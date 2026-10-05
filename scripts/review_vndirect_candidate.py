"""Hash-verified T010/T012 review; never write accepted dataset or split outputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from build_hose_calendar import build, verify_sources
from reconcile_hose_sessions import reconcile
from validate_vn30_sources import FIELDS, compare, parse

ROOT = Path(__file__).resolve().parents[1]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_audit(root: Path, config_path: str, audit_path: str) -> tuple[dict, dict, dict]:
    config_bytes = (root / config_path).read_bytes()
    config = yaml.safe_load(config_bytes)
    capture = root / audit_path
    manifest = json.loads((capture / "manifest.json").read_bytes())
    if sha(config_bytes) != manifest["config_sha256"]:
        raise ValueError("Audit config hash mismatch")
    if sha((root / "scripts/validate_vn30_sources.py").read_bytes()) != manifest["script_sha256"]:
        raise ValueError("Audit parser hash mismatch")
    if manifest["run_id"] != capture.name or set(manifest["providers"]) != set(config["providers"]):
        raise ValueError("Audit identity mismatch")
    frames = {}
    for name, record in manifest["providers"].items():
        raw = (capture / f"{name}.json").read_bytes()
        if sha(raw) != record["response_sha256"]:
            raise ValueError(f"Raw response hash mismatch: {name}")
        frames[name] = parse(raw, config)
    return config, manifest, frames


def unique_rows(frame: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    return frame.loc[frame.date.between(start, end) & ~frame.duplicate_date].set_index("date")


def capture_drift(old: pd.DataFrame, new: pd.DataFrame, start: str, end: str) -> dict:
    before, after = unique_rows(old, start, end), unique_rows(new, start, end)
    common = before.index.intersection(after.index).sort_values()
    differences = before.loc[common, list(FIELDS)].ne(after.loc[common, list(FIELDS)])
    old_dates = set(old.loc[old.date.between(start, end), "date"])
    new_dates = set(new.loc[new.date.between(start, end), "date"])
    encode = lambda dates: [day.strftime("%Y-%m-%d") for day in sorted(dates)]
    return {
        "interval_start": start, "interval_end": end,
        "common_unambiguous_dates": len(common),
        "changed_ohlc_dates": int(differences.any(axis=1).sum()),
        "changed_fields": {field: int(differences[field].sum()) for field in FIELDS},
        "old_duplicate_dates": encode(old.loc[old.date.between(start, end) & old.duplicate_date, "date"].unique()),
        "new_duplicate_dates": encode(new.loc[new.date.between(start, end) & new.duplicate_date, "date"].unique()),
        "dates_removed_from_response": encode(old_dates - new_dates),
        "dates_added_to_response": encode(new_dates - old_dates),
        "note": "Different request windows can affect responses; differences do not prove a provider revision or correction.",
    }


def sample_summary(crosscheck: pd.DataFrame, primary: str) -> list[dict]:
    selected = crosscheck.loc[(crosscheck.left_provider == primary) | (crosscheck.right_provider == primary)]
    results = []
    for (left, right), rows in selected.groupby(["left_provider", "right_provider"], sort=True):
        dates = rows.groupby("date").status.agg(list)
        stratified = rows.loc[rows.selection.str.contains("year_stratified")]
        results.append({
            "comparator": right if left == primary else left,
            "selected_dates": len(dates),
            "year_stratified_dates": int(stratified.date.nunique()),
            "years": sorted(int(year) for year in stratified.date.dt.year.unique()),
            "complete_ohlc_dates": sum("missing" not in statuses for statuses in dates),
            "all_fields_within_tolerance_dates": sum(all(status == "pass" for status in statuses) for statuses in dates),
            "discrepancy_fields": int(rows.status.eq("discrepancy").sum()),
            "missing_fields": int(rows.status.eq("missing").sum()),
            "upstream_independence": "unverified",
        })
    return results


def calendar_review(frame: pd.DataFrame, mappings: dict, start: str, end: str, root: Path) -> tuple[pd.DataFrame, list[dict]]:
    parts, results = [], []
    for year in range(pd.Timestamp(start).year, pd.Timestamp(end).year + 1):
        if str(year) not in mappings:
            raise ValueError(f"Missing calendar evidence mapping: {year}")
        path = root / mappings[str(year)]
        config = yaml.safe_load(path.read_bytes())
        # Existing builder verifies all retained primary and corroborating source bytes.
        verify_sources(config)
        first, last = max(start, f"{year}-01-01"), min(end, f"{year}-12-31")
        days = build(config, first, last)
        dates = frame.loc[frame.date.between(first, last)]
        days["calendar_config"] = mappings[str(year)]
        parts.append(days)
        results.append({
            "year": year, "start": first, "end": last,
            "evidence_status": config["status"], "calendar_config": mappings[str(year)],
            "calendar_config_sha256": sha(path.read_bytes()),
            "scheduled_sessions": int(days.is_session.sum()), "observed_rows": len(dates),
            "limitations": config["limitations"], **reconcile(dates, days),
        })
    return pd.concat(parts, ignore_index=True), results


def write_once(path: Path, raw: bytes) -> None:
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"Evidence changed; use a new output directory: {path}")
    else:
        with path.open("xb") as stream:
            stream.write(raw)


def execute(spec_path: Path, output: Path) -> dict:
    spec_bytes = spec_path.read_bytes()
    spec = yaml.safe_load(spec_bytes)
    primary = spec["primary_provider"]
    config, manifest, frames = load_audit(ROOT, spec["audit_config"], spec["audit"])
    old_config, old_manifest, old_frames = load_audit(ROOT, spec["previous_audit_config"], spec["previous_audit"])
    crosscheck = compare(frames, config)
    original = ROOT / "artifacts/source_audit" / manifest["run_id"] / "crosscheck.parquet"
    pd.testing.assert_frame_equal(pd.read_parquet(original), crosscheck)
    frame = frames[primary]
    start, end = config["start"], config["end"]
    days, calendar = calendar_review(frame, spec["calendar_configs"], start, end, ROOT)
    selected = crosscheck.loc[(crosscheck.left_provider == primary) | (crosscheck.right_provider == primary)]
    files = {
        "selected_crosscheck.csv": selected.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\n").encode(),
        "candidate_calendar.csv": days.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\n").encode(),
        "selected_raw_rows.csv": frame.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\n").encode(),
    }
    summary = {
        "classification": "candidate_review_not_phase1_acceptance", "gate_G1": "pending", "T012": "pending",
        "inference_allowed": False, "primary_provider": primary,
        "start": start, "end": end, "rows": len(frame),
        "quality_counts": {name: int(frame[name].sum()) for name in ("duplicate_date", "invalid_numeric", "invalid_ohlc", "outside_request")},
        "source_dates_strictly_increasing": bool(frame.date.is_monotonic_increasing and frame.date.is_unique),
        "crosscheck": sample_summary(crosscheck, primary), "calendar": calendar,
        "capture_drift": {name: capture_drift(old_frames[name], current, max(start, old_config["start"]), min(end, old_config["end"])) for name, current in frames.items()},
        "acceptance_blockers": ["material_OHLC_discrepancies_unresolved", "independent_upstream_lineage_unverified", "calendar_original_notices_and_exception_review_incomplete"],
        "bindings": {
            "review_spec": str(spec_path.relative_to(ROOT)).replace("\\", "/"), "review_spec_sha256": sha(spec_bytes),
            "review_script_sha256": sha(Path(__file__).read_bytes()),
            "audit_manifest_sha256": sha((ROOT / spec["audit"] / "manifest.json").read_bytes()),
            "previous_audit_manifest_sha256": sha((ROOT / spec["previous_audit"] / "manifest.json").read_bytes()),
            "audit_identity": manifest, "previous_audit_identity": old_manifest,
            "code_sha256": {name: sha((ROOT / "scripts" / name).read_bytes()) for name in ("validate_vn30_sources.py", "build_hose_calendar.py", "reconcile_hose_sessions.py")},
            "output_sha256": {name: sha(raw) for name, raw in files.items()},
        },
    }
    # Check every existing artifact before writing anything on a replay.
    files["summary.json"] = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    for name, raw in files.items():
        path = output / name
        if path.exists() and path.read_bytes() != raw:
            raise ValueError(f"Evidence changed; use a new output directory: {path}")
    output.mkdir(parents=True, exist_ok=True)
    for name, raw in files.items():
        write_once(output / name, raw)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=ROOT / "configs/vndirect_candidate_review.yaml")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.spec.resolve(), args.output.resolve())
    print(json.dumps({key: result[key] for key in ("gate_G1", "T012", "rows", "quality_counts", "crosscheck")}, indent=2))

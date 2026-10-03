"""Freeze Phase 1 outputs only from reviewed, hash-bound accepted inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path

import pandas as pd
import yaml

from phase1_pipeline import process, quality_report, session_dates, temporal_split

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = {"reproducible_download", "dates_and_units", "independent_crosscheck",
            "material_discrepancies_resolved", "session_reconciliation"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bound_file(root: Path, record: dict) -> Path:
    path = (root / record["path"]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Input evidence must be inside the project")
    if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) or sha(path) != record["sha256"]:
        raise ValueError(f"Input hash mismatch: {record['path']}")
    return path


def freeze(spec_path: Path, root: Path) -> dict:
    root = root.resolve()
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if spec.get("status") != "accepted_inputs":
        raise ValueError("Phase 1 inputs are pending; no accepted output may be written")
    acceptance_path = bound_file(root, spec["source_acceptance"])
    acceptance = yaml.safe_load(acceptance_path.read_text(encoding="utf-8"))
    if acceptance.get("status") != "accepted" or set(acceptance.get("criteria", {})) != CRITERIA:
        raise ValueError("G1 requires every source acceptance criterion")
    for name, criterion in acceptance["criteria"].items():
        if criterion.get("status") != "pass" or not criterion.get("review_note", "").strip():
            raise ValueError(f"G1 criterion unresolved: {name}")
        bound_file(root, criterion["evidence"])
    if (acceptance.get("crosschecked_dates", 0) < 30 or
            acceptance.get("extreme_return_dates_reviewed", 0) < 1 or
            acceptance.get("unresolved_material_discrepancies", 1) != 0):
        raise ValueError("G1 crosscheck/discrepancy requirements not met")
    provider = acceptance["provider"]
    if not re.fullmatch(r"[a-z0-9_]+", provider):
        raise ValueError("Invalid provider identifier")
    raw_path = bound_file(root, spec["raw_csv"])
    if acceptance.get("raw_csv_sha256") != sha(raw_path) or acceptance.get("units") != "index_points":
        raise ValueError("Accepted source does not match this exact snapshot/units")
    original_responses = [bound_file(root, item) for item in spec["original_responses"]]
    if not original_responses:
        raise ValueError("Unchanged original response evidence is required")
    calendar_path = bound_file(root, spec["calendar"])
    calendar_manifest_path = bound_file(root, spec["calendar_manifest"])
    calendar_manifest = yaml.safe_load(calendar_manifest_path.read_text(encoding="utf-8"))
    if (calendar_manifest.get("status") != "accepted" or
            calendar_manifest.get("calendar_sha256") != sha(calendar_path) or
            not calendar_manifest.get("exceptional_closures_reviewed") or
            not calendar_manifest.get("sources")):
        raise ValueError("Accepted calendar with exceptional-closure review is required")
    for source in calendar_manifest["sources"]:
        bound_file(root, source)
    days = pd.read_parquet(calendar_path)
    session_dates(days.date)
    if not days.date.equals(pd.Series(pd.date_range(days.date.min(), days.date.max()), name="date")):
        raise ValueError("Calendar must cover every date in its declared interval")
    if days.is_session.dtype != bool:
        raise ValueError("Calendar session flags must be boolean")
    sessions = pd.DatetimeIndex(days.loc[days.is_session, "date"])
    raw = pd.read_csv(raw_path, parse_dates=["date"])
    retrieved = pd.Timestamp(spec["retrieved_at_utc"])
    if retrieved.tz is None:
        raise ValueError("Retrieval timestamp requires timezone")
    freeze_date = pd.Timestamp(spec["freeze"])
    if raw.date.max() > freeze_date:
        raise ValueError("Snapshot includes dates after freeze; never trim silently")
    if freeze_date > retrieved.tz_convert("Asia/Ho_Chi_Minh").tz_localize(None).normalize():
        raise ValueError("Freeze cannot be later than retrieval")
    provenance_path = bound_file(root, spec["checkpoint_provenance"])
    provenance = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("status") != "accepted_for_phase_0":
        raise ValueError("G2 checkpoint provenance is not accepted")
    study_path = bound_file(root, spec["study"])
    study = yaml.safe_load(study_path.read_text(encoding="utf-8"))
    if study["forecast"]["path_length"] != 20 or study["forecast"]["primary_context_length"] != 128:
        raise ValueError("Research contract requires 128 context / 20 target sessions")
    annotations = None
    if "session_quality_flag" in days:
        if days.session_quality_flag.isna().any():
            raise ValueError("Calendar quality flags must not be null")
        annotations = days.loc[days.session_quality_flag.ne(""), ["date", "session_quality_flag"]]
        if not annotations.empty:
            if "event_source" not in days:
                raise ValueError("Annotated calendar sessions require event sources")
            event_sources = days.loc[annotations.index, "event_source"]
            if not event_sources.map(lambda value: isinstance(value, str) and bool(value.strip())).all():
                raise ValueError("Annotated calendar event sources must be nonempty strings")
    processed = process(raw, sessions, source=provider, g1_accepted=True,
                        calendar_accepted=True, session_annotations=annotations)
    origins, feasibility = temporal_split(raw.date, sessions,
        provenance["common_provenance_boundary"]["timestamp_utc"], spec["freeze"])
    classification = "confirmatory" if feasibility["size_gate"] == "pass" else "exploratory_pilot"
    if not feasibility["validation_origins"]:
        raise ValueError("No full-context validation origins; development cannot proceed")
    retrieval_day = str(retrieved.tz_convert("UTC").date())
    snapshot_rel = f"data/raw/vn30/{provider}/{retrieval_day}"
    snapshot_csv = f"{snapshot_rel}/vn30_daily.csv"
    paths = [snapshot_csv, f"{snapshot_rel}/manifest.yaml", "data/processed/vn30_daily.parquet",
             "data/manifests/hose_sessions.parquet", "data/manifests/hose_calendar.yaml",
             "data/manifests/dataset.yaml", "data/manifests/common_origins.parquet",
             "data/manifests/holdout_feasibility.json", "data/manifests/splits.yaml",
             "reports/data_quality.json", "data/manifests/phase1_freeze.yaml"]
    response_destinations = [f"{snapshot_rel}/response_{i:03d}.bin" for i in range(len(original_responses))]
    paths += response_destinations
    if any((root / relative).exists() for relative in paths):
        raise ValueError("Frozen outputs already exist; verify them instead of overwriting")
    stage_parent = root / "tmp" / "phase1_freeze"
    stage_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=stage_parent) as temporary:
        stage = Path(temporary).resolve()
        if not stage.is_relative_to(stage_parent.resolve()):
            raise ValueError("Invalid staging directory")
        for relative in paths:
            (stage / relative).parent.mkdir(parents=True, exist_ok=True)
        (stage / snapshot_csv).write_bytes(raw_path.read_bytes())
        for destination, response in zip(response_destinations, original_responses):
            (stage / destination).write_bytes(response.read_bytes())
        processed.to_parquet(stage / "data/processed/vn30_daily.parquet", index=False)
        days.to_parquet(stage / "data/manifests/hose_sessions.parquet", index=False)
        origins.to_parquet(stage / "data/manifests/common_origins.parquet", index=False)

        def save_yaml(relative, value):
            (stage / relative).write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

        save_yaml(f"{snapshot_rel}/manifest.yaml", {"provider": provider, "retrieved_at_utc": str(retrieved),
                  "kind": "unchanged_normalized_provider_csv_with_original_http_responses",
                  "sha256": sha(raw_path), "row_count": len(raw), "min_date": str(raw.date.min().date()),
                  "max_date": str(raw.date.max().date()), "column_schema": {c: str(d) for c, d in raw.dtypes.items()},
                  "original_responses": [{"path": p, "sha256": sha(r)} for p, r in zip(response_destinations, original_responses)],
                  "source_acceptance_sha256": sha(acceptance_path)})
        save_yaml("data/manifests/hose_calendar.yaml", calendar_manifest | {
            "calendar_sha256": sha(stage / "data/manifests/hose_sessions.parquet"),
            "input_calendar_sha256": sha(calendar_path), "input_manifest_sha256": sha(calendar_manifest_path)})
        save_yaml("data/manifests/dataset.yaml", {"status": "accepted", "provider": provider,
                  "raw_snapshot": snapshot_csv, "raw_sha256": sha(raw_path), "processed_path": "data/processed/vn30_daily.parquet",
                  "processed_sha256": sha(stage / "data/processed/vn30_daily.parquet"),
                  "row_count": len(processed), "schema": {c: str(d) for c, d in processed.dtypes.items()},
                  "units": "index_points", "derived_features": {
                      "log_close": "log(close)", "return_1d": "close / previous_close - 1",
                      "log_return_1d": "log_close - previous_log_close", "range_abs": "high - low",
                      "range_pct": "range_abs / close", "body_abs": "abs(close - open)",
                      "body_pct": "body_abs / open"},
                  "pipeline_sha256": sha(Path(__file__).with_name("phase1_pipeline.py")),
                  "freeze_script_sha256": sha(Path(__file__)), "input_spec_sha256": sha(spec_path)})
        feasibility.update({"classification": classification, "G1": "pass", "G2": "pass",
                            "calendar_sha256": sha(stage / "data/manifests/hose_sessions.parquet"),
                            "checkpoint_provenance": provenance, "contains_forecasts_or_metrics": False})
        (stage / "data/manifests/holdout_feasibility.json").write_text(json.dumps(feasibility, indent=2), encoding="utf-8")
        save_yaml("data/manifests/splits.yaml", {"classification": classification, "freeze": spec["freeze"],
                  "validation_targets": feasibility["validation_targets"], "test_targets": feasibility["test_targets"],
                  "train_end_exclusive": feasibility["validation_targets"]["start"],
                  "refit_end_inclusive": feasibility["validation_targets"]["end"],
                  "origin_manifest": "data/manifests/common_origins.parquet",
                  "origin_manifest_sha256": sha(stage / "data/manifests/common_origins.parquet"),
                  "study_sha256": sha(study_path), "checkpoint_provenance_sha256": sha(provenance_path)})
        quality = quality_report(raw, sessions)
        quality["flagged_observations"] = [
            {"date": str(row.date.date()), "quality_flags": row.quality_flags}
            for row in processed.loc[processed.quality_flags.ne(""), ["date", "quality_flags"]].itertuples()]
        (stage / "reports/data_quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
        receipt = {"status": "frozen", "classification": classification,
                   "g1_criteria": sorted(CRITERIA),
                   "research_use_criterion": "excluded_by_user_request_2026-10-02",
                   "artifacts": [{"path": p, "sha256": sha(stage / p)} for p in paths if p != "data/manifests/phase1_freeze.yaml"]}
        save_yaml("data/manifests/phase1_freeze.yaml", receipt)
        # Publish the receipt last. An interruption cannot masquerade as a complete freeze.
        for relative in [p for p in paths if p != "data/manifests/phase1_freeze.yaml"] + ["data/manifests/phase1_freeze.yaml"]:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError("Output appeared during freeze; refusing replacement")
            (stage / relative).rename(target)
    return receipt


def verify_freeze(root: Path) -> dict:
    root = root.resolve()
    receipt = yaml.safe_load((root / "data/manifests/phase1_freeze.yaml").read_text(encoding="utf-8"))
    if receipt.get("status") != "frozen" or not receipt.get("artifacts"):
        raise ValueError("Missing completed Phase 1 receipt")
    for record in receipt["artifacts"]:
        bound_file(root, record)
    return {"status": "verified", "classification": receipt["classification"], "artifacts": len(receipt["artifacts"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=ROOT / "configs/phase1_inputs.yaml")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(verify_freeze(ROOT) if args.verify else freeze(args.spec, ROOT), indent=2))
    except (ValueError, KeyError, FileNotFoundError) as exc:
        parser.exit(1, f"Phase 1 freeze refused: {exc}\n")


if __name__ == "__main__":
    main()

"""Immutable, replayable provider audit. This command never grants G1 automatically."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("open", "high", "low", "close")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def download(url: str) -> bytes:
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "vn30-research-audit/1.0"}), timeout=30) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code != 429 and exc.code < 500:
                raise
            if attempt == 2:
                raise
            time.sleep(min(30, int(exc.headers.get("Retry-After", 2 ** (attempt + 1)))))
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError("Unreachable retry state")


def parse(raw: bytes, config: dict) -> pd.DataFrame:
    payload = json.loads(raw)
    if payload.get("s") not in (None, "ok"):
        raise ValueError("Provider returned a non-success status")
    stamps = payload.get("t", [])
    if not stamps or any(len(payload.get(field[0], [])) != len(stamps) for field in FIELDS):
        raise ValueError("Empty or mismatched OHLC arrays")
    dates = pd.to_datetime(stamps, unit="s", utc=True).tz_convert(config["timezone"]).normalize().tz_localize(None)
    frame = pd.DataFrame({"date": dates, "timestamp": stamps} | {f: payload[f[0]] for f in FIELDS})
    for field in FIELDS:
        frame[field] = pd.to_numeric(frame[field], errors="raise")
    frame["duplicate_date"] = frame.date.duplicated(keep=False)
    values = frame[list(FIELDS)].to_numpy()
    frame["invalid_numeric"] = ~np.isfinite(values).all(axis=1) | (values <= 0).any(axis=1)
    frame["invalid_ohlc"] = (frame.high < frame[["open", "close", "low"]].max(axis=1)) | (frame.low > frame[["open", "close", "high"]].min(axis=1))
    frame["outside_request"] = (frame.date < pd.Timestamp(config["start"])) | (frame.date > pd.Timestamp(config["end"]))
    return frame


def compare(frames: dict[str, pd.DataFrame], config: dict) -> pd.DataFrame:
    rows = []
    for left, right in itertools.combinations(sorted(frames), 2):
        indexes = {name: frames[name].loc[~frames[name].duplicate_date & ~frames[name].outside_request].sort_values("date").set_index("date") for name in (left, right)}
        common = indexes[left].index.intersection(indexes[right].index).sort_values()
        rng = np.random.default_rng(config["seed"])
        selected: dict[pd.Timestamp, set[str]] = {}
        for year in sorted(set(common.year)):
            pool = common[common.year == year]
            for date in rng.choice(pool.to_numpy(), min(len(pool), config["samples_per_year"]), replace=False):
                selected.setdefault(pd.Timestamp(date), set()).add("year_stratified")
        # Extremes are calculated from consecutive observed dates of each source,
        # including every raw date; duplicated dates yield no return for selection.
        for name in (left, right):
            source = frames[name].sort_values("date", kind="stable").copy()
            source["abs_return"] = source.close.pct_change(fill_method=None).abs()
            source.loc[source.duplicate_date | source.duplicate_date.shift(fill_value=False), "abs_return"] = np.nan
            for date in source.loc[~source.outside_request].nlargest(config["extreme_return_count"], "abs_return").date:
                selected.setdefault(date, set()).add(f"extreme_{name}")
        for date, reasons in sorted(selected.items()):
            for field in FIELDS:
                a = float(indexes[left].at[date, field]) if date in indexes[left].index else None
                b = float(indexes[right].at[date, field]) if date in indexes[right].index else None
                diff = abs(a - b) if a is not None and b is not None else None
                threshold = config["tolerances"][field]
                passed = diff is not None and np.isfinite(diff) and diff <= threshold + 1e-9
                rows.append({"date": date, "selection": ";".join(sorted(reasons)), "left_provider": left, "right_provider": right, "field": field, "left_value": a, "right_value": b, "abs_difference": diff, "tolerance": threshold, "status": "pass" if passed else "missing" if diff is None else "discrepancy", "resolution": "not_required" if passed else "unresolved"})
    return pd.DataFrame(rows)


def execute(config_path: Path, replay: Path | None) -> Path:
    config_bytes = config_path.read_bytes()
    config = yaml.safe_load(config_bytes)
    if replay:
        manifest = json.loads((replay / "manifest.json").read_text(encoding="utf-8"))
        if digest(config_bytes) != manifest["config_sha256"]:
            raise ValueError("Replay config hash mismatch")
        run = replay
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run = ROOT / "data" / "raw" / "source_audit" / run_id
        run.mkdir(parents=True, exist_ok=False)
        manifest = {"run_id": run_id, "config_sha256": digest(config_bytes), "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "code_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()), "script_sha256": digest(Path(__file__).read_bytes()), "classification": "source_audit_not_accepted_dataset", "providers": {}}
    frames = {}
    for name, spec in config["providers"].items():
        path = run / f"{name}.json"
        if replay:
            raw = path.read_bytes()
            if digest(raw) != manifest["providers"][name]["response_sha256"]:
                raise ValueError(f"{name}: raw response hash mismatch")
        else:
            start = int(pd.Timestamp(config["start"], tz="UTC").timestamp())
            end = int((pd.Timestamp(config["end"], tz="UTC") + pd.Timedelta(days=1)).timestamp()) - 1
            url = spec["endpoint"] + "?" + urlencode({"symbol": config["symbol"], "resolution": spec["resolution"], "from": start, "to": end})
            raw = download(url)
            path.write_bytes(raw)
            manifest["providers"][name] = {"url": url, "response_sha256": digest(raw), "size_bytes": len(raw)}
            (run / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            time.sleep(1)
        frames[name] = parse(raw, config)
    evidence = ROOT / "artifacts" / "source_audit" / manifest["run_id"]
    comparison = compare(frames, config)
    if replay:
        original = pd.read_parquet(evidence / "crosscheck.parquet")
        pd.testing.assert_frame_equal(original, comparison)
        print("Replay matches persisted crosscheck; all raw response hashes verified")
        return evidence
    evidence.mkdir(parents=True, exist_ok=False)
    comparison.to_parquet(evidence / "crosscheck.parquet", index=False)
    anomalies = pd.concat([frame.assign(provider=name) for name, frame in frames.items()], ignore_index=True)
    anomalies = anomalies.loc[anomalies.duplicate_date | anomalies.invalid_numeric | anomalies.invalid_ohlc | anomalies.outside_request]
    anomalies.to_parquet(evidence / "anomalies.parquet", index=False)
    summary = {"gate_G1": "pending", "selected_provider": None, "raw_manifest": str(run.relative_to(ROOT)), "identity": manifest, "providers": {name: {"raw_rows": len(frame), "first_date": str(frame.date.min().date()), "last_date": str(frame.date.max().date()), "duplicate_rows": int(frame.duplicate_date.sum()), "invalid_ohlc_rows": int(frame.invalid_ohlc.sum()), "invalid_numeric_rows": int(frame.invalid_numeric.sum()), "outside_request_rows": int(frame.outside_request.sum())} for name, frame in frames.items()}, "comparisons": comparison.groupby(["left_provider", "right_provider", "status"]).size().reset_index(name="field_count").to_dict("records"), "unresolved_material_discrepancies": int((comparison.status == "discrepancy").sum()), "permission": {name: spec["permission_status"] for name, spec in config["providers"].items()}}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "data_source_acceptance.yaml")
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    execute(args.config, args.replay)

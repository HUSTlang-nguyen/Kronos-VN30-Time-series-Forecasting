"""Preserve narrow-window responses to investigate, never repair, raw anomalies."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import yaml

from validate_vn30_sources import download, parse

ROOT = Path(__file__).resolve().parents[1]


def duplicate_details(frame: pd.DataFrame) -> list[dict]:
    rows = []
    for day, group in frame[frame.date.duplicated(keep=False)].groupby("date"):
        rows.append({
            "date": str(day.date()), "rows": len(group),
            "timestamps": [int(x) for x in group.timestamp],
            "utc_times": [str(pd.Timestamp(x, unit="s", tz="UTC")) for x in group.timestamp],
            "identical_ohlc": len(group[["open", "high", "low", "close"]].drop_duplicates()) == 1,
            "ohlc": group[["open", "high", "low", "close"]].to_dict("records"),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--provider", choices=["dnse", "vps", "vndirect"])
    parser.add_argument("--start")
    parser.add_argument("--end", help="Exclusive UTC date boundary")
    args = parser.parse_args()
    custom = [args.provider, args.start, args.end]
    if any(custom) and (not all(custom) or args.replay):
        parser.error("Use --provider, --start and --end together, without --replay")
    windows = [("dnse", "2025-03-31", "2025-04-08"), ("vps", "2025-05-01", "2025-05-14")]
    if all(custom):
        start = pd.Timestamp(args.start, tz="UTC")
        end = pd.Timestamp(args.end, tz="UTC")
        if start >= end or start != start.normalize() or end != end.normalize():
            parser.error("Window boundaries must be midnight dates with start < end")
        windows = [(args.provider, args.start, args.end)]
    config_path = ROOT / "configs/data_source_acceptance.yaml"
    config = yaml.safe_load(config_path.read_text())
    audit_manifest = json.loads((args.audit / "manifest.json").read_text())
    if hashlib.sha256(config_path.read_bytes()).hexdigest() != audit_manifest["config_sha256"]:
        raise ValueError("Audit configuration changed")
    original = {}
    for provider, entry in audit_manifest["providers"].items():
        raw = (args.audit / f"{provider}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["response_sha256"]:
            raise ValueError("Audit bytes changed")
        original[provider] = parse(raw, config)
    if args.replay:
        raw_dir = args.replay
        manifest = json.loads((raw_dir / "manifest.json").read_text())
    else:
        run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        raw_dir = ROOT / "data/raw/source_investigation" / run
        raw_dir.mkdir(parents=True, exist_ok=False)
        manifest = {"run_id": run, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "requests": {}}
        for provider, start, end in windows:
            spec = config["providers"][provider]
            params = {"symbol": "VN30", "resolution": spec["resolution"],
                      "from": int(pd.Timestamp(start, tz="UTC").timestamp()),
                      "to": int(pd.Timestamp(end, tz="UTC").timestamp()) - 1}
            url = spec["endpoint"] + "?" + urlencode(params)
            raw = download(url)
            (raw_dir / f"{provider}.json").write_bytes(raw)
            manifest["requests"][provider] = {"url": url, "sha256": hashlib.sha256(raw).hexdigest()}
        (raw_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    result = {"classification": "investigation_only_no_dataset_patch", "capture": manifest,
              "original_audit_sha256": hashlib.sha256((args.audit / "manifest.json").read_bytes()).hexdigest(),
              "vps_original_duplicates": duplicate_details(original["vps"]), "narrow_windows": {}}
    for provider, entry in manifest["requests"].items():
        raw = (raw_dir / f"{provider}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError("Investigation bytes changed")
        frame = parse(raw, config)
        result["narrow_windows"][provider] = {
            "dates": [str(d.date()) for d in frame.date],
            "duplicates": duplicate_details(frame),
            "dnse_2025_04_03_present": (
                bool((frame.date == pd.Timestamp("2025-04-03")).any())
                if provider == "dnse" and not frame.empty
                and frame.date.min() <= pd.Timestamp("2025-04-03") <= frame.date.max()
                else None
            ),
        }
    evidence = ROOT / "artifacts/source_audit" / ("investigation_" + manifest["run_id"])
    evidence.mkdir(parents=True, exist_ok=True)
    path = evidence / "summary.json"
    serialized = json.dumps(result, indent=2) + "\n"
    if path.exists() and path.read_text() != serialized:
        raise ValueError("Replay result changed")
    path.write_text(serialized, encoding="utf-8")
    print(json.dumps({"evidence": str(evidence), "narrow_windows": result["narrow_windows"],
                      "duplicate_dates": len(result["vps_original_duplicates"]),
                      "identical_duplicate_dates": sum(r["identical_ohlc"] for r in result["vps_original_duplicates"])}, indent=2))


if __name__ == "__main__":
    main()

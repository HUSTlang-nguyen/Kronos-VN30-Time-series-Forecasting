"""Compare all raw candles on anomalous dates; never select or repair prices."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from validate_vn30_sources import parse
from verify_vnstock_capture import reconstruct

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--vnstock", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config_path = ROOT / "configs/data_source_acceptance.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    audit = json.loads((args.audit / "manifest.json").read_text())
    wrapper = json.loads((args.vnstock / "manifest.json").read_text())
    if sha(config_path) != audit["config_sha256"]:
        raise ValueError("Original audit configuration changed")
    frames, hashes = {}, {}
    for provider, record in audit["providers"].items():
        path = args.audit / f"{provider}.json"
        if sha(path) != record["response_sha256"]:
            raise ValueError(f"Original response changed: {provider}")
        frames[provider] = parse(path.read_bytes(), config)
        hashes[provider] = sha(path)
    wrapper_config = dict(config, start=wrapper["start"], end=wrapper["end"])
    for provider, record in wrapper["providers"].items():
        response = record["http_captures"]
        if len(response) != 1:
            raise ValueError("Expected one unchanged history response per provider")
        path = args.vnstock / response[0]["file"]
        if sha(path) != response[0]["sha256"]:
            raise ValueError(f"Original response changed: {provider}")
        frames[provider] = reconstruct(provider, path.read_bytes(), wrapper_config)
        hashes[provider] = sha(path)
    dates = pd.DatetimeIndex(sorted(set().union(*[
        set(frame.loc[frame.invalid_numeric | frame.invalid_ohlc | frame.duplicate_date, "date"])
        for frame in frames.values()
    ])))
    selected = []
    for provider, frame in sorted(frames.items()):
        rows = frame.loc[frame.date.isin(dates),
            ["date", "open", "high", "low", "close", "invalid_numeric", "invalid_ohlc", "duplicate_date"]].copy()
        rows["provider"] = provider
        selected.append(rows)
    review = pd.concat(selected, ignore_index=True).sort_values(["date", "provider"], kind="stable").reset_index(drop=True)
    summary = {
        "classification": "anomaly_review_only_no_source_selection_or_dataset_patch",
        "config_sha256": sha(config_path), "script_sha256": sha(Path(__file__)),
        "audit_manifest_sha256": sha(args.audit / "manifest.json"),
        "vnstock_manifest_sha256": sha(args.vnstock / "manifest.json"),
        "response_sha256": hashes, "anomalous_dates": len(dates), "review_rows": len(review),
        "providers": {name: {"invalid_ohlc_rows": int(frame.invalid_ohlc.sum()),
            "invalid_numeric_rows": int(frame.invalid_numeric.sum()),
            "duplicate_rows": int(frame.duplicate_date.sum())} for name, frame in sorted(frames.items())},
        "limitations": ["Absent provider rows remain absent; no imputation.",
            "All conflicting duplicate candles are retained.",
            "Source agreement does not identify correct OHLC or independent upstream lineage."]}
    args.output.mkdir(parents=True, exist_ok=True)
    table = args.output / "candles.parquet"
    receipt = args.output / "summary.json"
    if table.exists():
        pd.testing.assert_frame_equal(pd.read_parquet(table), review)
    else:
        review.to_parquet(table, index=False)
    summary["review_sha256"] = sha(table)
    serialized = json.dumps(summary, indent=2) + "\n"
    if receipt.exists() and receipt.read_text(encoding="utf-8") != serialized:
        raise ValueError("Anomaly review changed; preserve existing evidence")
    receipt.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()

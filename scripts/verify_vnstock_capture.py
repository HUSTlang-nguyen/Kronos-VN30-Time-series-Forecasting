"""Reconstruct daily OHLC directly from captured provider bytes, offline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from audit_vnstock_sources import normalize
from build_hose_calendar import build
from reconcile_hose_sessions import reconcile
from validate_vn30_sources import compare, parse

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["date", "open", "high", "low", "close"]


def reconstruct(provider: str, raw: bytes, config: dict) -> pd.DataFrame:
    payload = json.loads(raw)
    if provider == "kbs":
        if payload["symbol"] != "VN30":
            raise ValueError("Wrong index")
        frame = pd.DataFrame(payload["data_day"]).rename(columns={"t": "date", "o": "open", "h": "high", "l": "low", "c": "close"})
    elif provider == "vci":
        payload = payload[0]
        if payload["symbol"] != "VN30":
            raise ValueError("Wrong index")
        frame = pd.DataFrame({"date": pd.to_datetime([int(t) for t in payload["t"]], unit="s", utc=True),
                              **{f: payload[f[0]] for f in FIELDS[1:]}})
    else:
        raise ValueError("Unknown provider")
    return normalize(frame, config).sort_values("date", kind="stable").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--reference", type=Path, default=ROOT / "data/raw/source_audit/20261001T151513588605Z")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.capture / "manifest.json").read_text())
    config_path = ROOT / "configs/data_source_acceptance.yaml"
    config = yaml.safe_load(config_path.read_text())
    config["end"] = manifest["end"]
    calendar_config = yaml.safe_load((ROOT / "data/manifests/hose_calendar_evidence.yaml").read_text())
    calendar = build(calendar_config, "2025-01-01", config["end"])
    args.output.mkdir(parents=True, exist_ok=True)
    findings = {"classification": "offline_audit_not_G1_acceptance", "providers": {},
                "capture_manifest_sha256": hashlib.sha256((args.capture / "manifest.json").read_bytes()).hexdigest(),
                "calendar_status": calendar_config["status"]}
    frames = {}
    for provider, entry in manifest["providers"].items():
        if entry["status"] != "downloaded_pending_validation":
            continue
        if len(entry["http_captures"]) != 1:
            raise ValueError("This verifier requires one complete OHLC response per provider")
        response = entry["http_captures"][0]
        raw = (args.capture / response["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != response["sha256"]:
            raise ValueError("Raw response hash mismatch")
        frame = reconstruct(provider, raw, config)
        csv_path = args.capture / f"{provider}_normalized.csv"
        if hashlib.sha256(csv_path.read_bytes()).hexdigest() != entry["normalized_sha256"]:
            raise ValueError("Normalized snapshot hash mismatch")
        normalized = normalize(pd.read_csv(csv_path), config).sort_values("date", kind="stable").reset_index(drop=True)
        pd.testing.assert_frame_equal(frame[FIELDS], normalized[FIELDS], check_dtype=False, check_exact=False, rtol=0, atol=1e-9)
        anomalies = frame.loc[frame.invalid_numeric | frame.invalid_ohlc | frame.duplicate_date | frame.outside_request, FIELDS].reset_index(drop=True)
        path = args.output / f"{provider}_anomalies.parquet"
        if path.exists():
            pd.testing.assert_frame_equal(pd.read_parquet(path), anomalies)
        else:
            anomalies.to_parquet(path, index=False)
        findings["providers"][provider] = {
            "raw_to_normalized_ohlc_verified": True,
            "date_reconciliation": reconcile(frame, calendar),
            "invalid_ohlc_by_year": frame[frame.invalid_ohlc].groupby(frame.date.dt.year).size().to_dict(),
            "ohlc_2025_04_03": frame[frame.date.eq("2025-04-03")][FIELDS[1:]].to_dict("records"),
        }
        frames[provider] = frame
    reference_config = yaml.safe_load(config_path.read_text())
    reference_manifest = json.loads((args.reference / "manifest.json").read_text())
    if hashlib.sha256(config_path.read_bytes()).hexdigest() != reference_manifest["config_sha256"]:
        raise ValueError("Reference configuration changed")
    for provider, entry in reference_manifest["providers"].items():
        raw = (args.reference / f"{provider}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["response_sha256"]:
            raise ValueError("Reference bytes changed")
        frames[provider] = parse(raw, reference_config)
    # All reference captures end on 30 September: no artificial missing-date finding
    # against a source whose request deliberately excluded 1 October.
    crosscheck = compare({p: f[f.date <= pd.Timestamp(reference_config["end"])].copy() for p, f in frames.items()}, reference_config)
    crosscheck = crosscheck[crosscheck.left_provider.isin(["kbs", "vci"]) | crosscheck.right_provider.isin(["kbs", "vci"])]
    crosscheck = crosscheck.reset_index(drop=True)
    path = args.output / "crosscheck_common_interval.parquet"
    if path.exists():
        pd.testing.assert_frame_equal(pd.read_parquet(path), crosscheck)
    else:
        crosscheck.to_parquet(path, index=False)
    findings["crosscheck_end"] = reference_config["end"]
    findings["comparisons"] = crosscheck.groupby(["left_provider", "right_provider", "status"]).size().reset_index(name="field_count").to_dict("records")
    path = args.output / "summary.json"
    serialized = json.dumps(findings, indent=2)
    if path.exists() and path.read_text() != serialized:
        raise ValueError("Offline findings changed; preserve prior output and investigate")
    path.write_text(serialized, encoding="utf-8")
    print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()

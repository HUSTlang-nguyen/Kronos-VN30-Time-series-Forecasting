"""Audit vnstock KBS/VCI with immutable HTTP captures; no automatic acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import requests
import yaml

from validate_vn30_sources import compare, parse

ROOT = Path(__file__).resolve().parents[1]


def normalize(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    frame = frame.rename(columns={"time": "date"}).copy()
    if not {"date", "open", "high", "low", "close"}.issubset(frame):
        raise ValueError("Missing daily OHLC columns")
    dates = pd.to_datetime(frame.date, errors="raise")
    if dates.dt.tz is not None:
        dates = dates.dt.tz_convert(config["timezone"]).dt.tz_localize(None)
    frame["date"] = dates.dt.normalize()
    for field in ("open", "high", "low", "close"):
        frame[field] = pd.to_numeric(frame[field], errors="raise")
    frame["duplicate_date"] = frame.date.duplicated(keep=False)
    values = frame[["open", "high", "low", "close"]].to_numpy()
    frame["invalid_numeric"] = ~np.isfinite(values).all(axis=1) | (values <= 0).any(axis=1)
    frame["invalid_ohlc"] = (frame.high < frame[["open", "close", "low"]].max(axis=1)) | (frame.low > frame[["open", "close", "high"]].min(axis=1))
    frame["outside_request"] = (frame.date < pd.Timestamp(config["start"])) | (frame.date > pd.Timestamp(config["end"]))
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--end", default="2026-10-01")
    parser.add_argument("--reference", type=Path, default=ROOT / "data/raw/source_audit/20261001T151513588605Z")
    args = parser.parse_args()
    os.environ.setdefault("VNSTOCK_TELEMETRY", "off")
    base_config = ROOT / "configs/data_source_acceptance.yaml"
    config = yaml.safe_load(base_config.read_text())
    config["end"] = args.end
    if pd.Timestamp(args.end) > pd.Timestamp.now(tz=config["timezone"]).tz_localize(None).normalize():
        raise ValueError("End date is in the future")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    raw_dir = ROOT / "data/raw/vnstock_audit" / run_id
    evidence = ROOT / "artifacts/source_audit" / ("vnstock_" + run_id)
    raw_dir.mkdir(parents=True, exist_ok=False)
    evidence.mkdir(parents=True, exist_ok=False)
    packages = {dist.metadata["Name"]: dist.version for dist in importlib.metadata.distributions()}
    manifest = {"classification": "candidate_audit_not_accepted_dataset", "run_id": run_id,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "symbol": "VN30",
                "start": config["start"], "end": config["end"], "interval": "1D",
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "config_sha256": hashlib.sha256(base_config.read_bytes()).hexdigest(),
                "packages": packages, "providers": {}, "permission": "not_established_for_underlying_data"}
    frames = {}
    for provider in ("kbs", "vci"):
        records = []
        original_send = requests.Session.send

        def capture(session, request, **kwargs):
            response = original_send(session, request, **kwargs)
            # Capture only market-data hosts; never persist auth headers/telemetry.
            host = urlparse(request.url).hostname or ""
            if host.endswith("kbsec.com.vn") or host.endswith("vietcap.com.vn"):
                filename = f"{provider}_response_{len(records):03d}.bin"
                raw = response.content
                (raw_dir / filename).write_bytes(raw)
                body = request.body
                if isinstance(body, bytes):
                    body = body.decode("utf-8")
                records.append({"file": filename, "url": request.url, "method": request.method,
                                "request_body": body, "status": response.status_code,
                                "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)})
            return response

        entry = {"http_captures": records}
        try:
            with patch.object(requests.Session, "send", capture):
                if provider == "kbs":
                    from vnstock.explorer.kbs.quote import Quote
                else:
                    from vnstock.explorer.vci.quote import Quote
                frame = Quote(symbol="VN30", random_agent=False).history(
                    start=config["start"], end=args.end, interval="1D", floating=None)
            if not records:
                raise ValueError("No raw market response captured; cannot audit provenance")
            frame.to_csv(raw_dir / f"{provider}_normalized.csv", index=False)
            entry["normalized_sha256"] = hashlib.sha256((raw_dir / f"{provider}_normalized.csv").read_bytes()).hexdigest()
            normalized = normalize(frame, config)
            normalized.to_parquet(raw_dir / f"{provider}_normalized.parquet", index=False)
            frames[provider] = normalized
            entry.update({"status": "downloaded_pending_validation", "rows": len(frame),
                          "first_date": str(normalized.date.min().date()), "last_date": str(normalized.date.max().date()),
                          "duplicate_rows": int(normalized.duplicate_date.sum()),
                          "invalid_ohlc_rows": int(normalized.invalid_ohlc.sum()),
                          "invalid_numeric_rows": int(normalized.invalid_numeric.sum()),
                          "outside_request_rows": int(normalized.outside_request.sum())})
        except Exception as exc:
            entry.update({"status": "failed", "exception_type": type(exc).__name__, "error": str(exc)})
        manifest["providers"][provider] = entry
        (raw_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(provider, entry["status"], flush=True)
    reference_config = yaml.safe_load(base_config.read_text())
    reference_manifest = json.loads((args.reference / "manifest.json").read_text())
    if hashlib.sha256(base_config.read_bytes()).hexdigest() != reference_manifest["config_sha256"]:
        raise ValueError("Reference config hash changed")
    for provider, entry in reference_manifest["providers"].items():
        raw = (args.reference / f"{provider}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["response_sha256"]:
            raise ValueError("Reference response hash changed")
        frames[provider] = parse(raw, reference_config)
    if any(p in frames for p in ("kbs", "vci")):
        comparison_end = min(pd.Timestamp(config["end"]), pd.Timestamp(reference_config["end"]))
        comparison_config = config | {"end": str(comparison_end.date())}
        crosscheck = compare({p: f[f.date <= comparison_end].copy() for p, f in frames.items()}, comparison_config)
        manifest["crosscheck_end"] = str(comparison_end.date())
        crosscheck = crosscheck[crosscheck.left_provider.isin(["kbs", "vci"]) | crosscheck.right_provider.isin(["kbs", "vci"])]
        crosscheck.to_parquet(evidence / "crosscheck.parquet", index=False)
        manifest["comparisons"] = crosscheck.groupby(["left_provider", "right_provider", "status"]).size().reset_index(name="field_count").to_dict("records")
    (evidence / "summary.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"evidence": str(evidence), "providers": manifest["providers"]}, indent=2))


if __name__ == "__main__":
    main()

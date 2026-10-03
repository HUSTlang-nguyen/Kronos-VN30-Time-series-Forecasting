"""Compare immutable provider audit dates with a candidate exchange calendar."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from validate_vn30_sources import parse

ROOT = Path(__file__).resolve().parents[1]


def reconcile(frame: pd.DataFrame, calendar: pd.DataFrame) -> dict:
    expected = set(calendar.loc[calendar.is_session, "date"])
    observed = set(frame.date)
    covered = set(calendar.date)
    encode = lambda days: [day.strftime("%Y-%m-%d") for day in sorted(days)]
    return {
        "missing_scheduled_sessions": encode(expected - observed),
        "observed_non_sessions": encode((observed & covered) - expected),
        "duplicate_dates_in_coverage": encode(set(frame.loc[frame.date.duplicated(keep=False), "date"]) & covered),
        "observations_outside_calendar_coverage": int((~frame.date.isin(covered)).sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config_path = ROOT / "configs/data_source_acceptance.yaml"
    config = yaml.safe_load(config_path.read_text())
    if pd.Timestamp(args.end) > pd.Timestamp(config["end"]):
        raise ValueError("Reconciliation end exceeds the audit request")
    manifest = json.loads((args.audit / "manifest.json").read_text())
    if hashlib.sha256(config_path.read_bytes()).hexdigest() != manifest["config_sha256"]:
        raise ValueError("Source audit configuration changed")
    calendar = pd.read_parquet(args.calendar)
    calendar = calendar[calendar.date <= pd.Timestamp(args.end)]
    if calendar.empty:
        raise ValueError("No calendar coverage")
    result = {"classification": "candidate_calendar_reconciliation_not_G1_acceptance", "end": args.end,
              "calendar_sha256": hashlib.sha256(args.calendar.read_bytes()).hexdigest(),
              "audit_manifest_sha256": hashlib.sha256((args.audit / "manifest.json").read_bytes()).hexdigest(),
              "providers": {}}
    for provider, record in manifest["providers"].items():
        raw = (args.audit / f"{provider}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != record["response_sha256"]:
            raise ValueError(f"Raw hash changed: {provider}")
        result["providers"][provider] = reconcile(parse(raw, config), calendar)
    serialized = json.dumps(result, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and args.output.read_text() != serialized:
        raise ValueError("Reconciliation changed; use a new output path")
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()

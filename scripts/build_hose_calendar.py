"""Build an evidence-backed candidate calendar; never infer uncovered years."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]


def build(config: dict, start: str, end: str) -> pd.DataFrame:
    dates = pd.date_range(start, end)
    if dates.empty:
        raise ValueError("Empty calendar interval")
    covered = set(config["covered_years"])
    if not set(dates.year).issubset(covered):
        raise ValueError("Requested years lack calendar evidence")
    closures = {}
    for event in config["closures"]:
        if event["source"] not in config["sources"]:
            raise ValueError("Unknown closure source")
        span = pd.date_range(event["start"], event["end"])
        if span.empty or not set(span.year).issubset(covered):
            raise ValueError("Invalid closure interval")
        for day in span:
            if day in closures:
                raise ValueError("Overlapping closure declarations")
            closures[day] = event
    rows = []
    for day in dates:
        event = closures.get(day)
        weekend = day.dayofweek >= 5
        rows.append({
            "date": day, "is_session": not weekend and event is None,
            "reason": event["reason"] if event else ("weekend" if weekend else "scheduled_session"),
            "source": event["source"] if event else config["annual_sources"][str(day.year)],
            "calendar_status": config["status"],
        })
    frame = pd.DataFrame(rows)
    if "session_events" in config:
        frame["session_quality_flag"] = ""
        frame["event_source"] = ""
        seen = set()
        for event in config["session_events"]:
            day = pd.Timestamp(event["date"])
            if (day.tz is not None or pd.isna(day) or day != day.normalize()
                    or day.year not in covered or day in seen):
                raise ValueError("Invalid or duplicate session event date")
            if event["source"] not in config["sources"]:
                raise ValueError("Unknown session event source")
            if event["quality_flag"] != "shortened_session":
                raise ValueError("Unsupported session quality flag")
            if day.dayofweek >= 5 or day in closures:
                raise ValueError("Session event cannot annotate a closed day")
            seen.add(day)
            mask = frame.date.eq(day)
            frame.loc[mask, "session_quality_flag"] = event["quality_flag"]
            frame.loc[mask, "event_source"] = event["source"]
    return frame


def verify_sources(config: dict) -> None:
    for source in config["sources"].values():
        path = ROOT / source["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Calendar source hash mismatch: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "data/manifests/hose_calendar_evidence.yaml")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-12-31")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/source_audit/calendar_2025_2026")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    verify_sources(config)
    frame = build(config, args.start, args.end)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "candidate_days.parquet"
    if path.exists():
        pd.testing.assert_frame_equal(pd.read_parquet(path), frame)
    else:
        frame.to_parquet(path, index=False)
    summary = {
        "classification": config["status"], "start": args.start, "end": args.end,
        "config_sha256": hashlib.sha256(args.config.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "calendar_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "scheduled_sessions_by_year": frame[frame.is_session].groupby(frame.date.dt.year).size().to_dict(),
        "limitations": config["limitations"],
    }
    target = args.output / "summary.json"
    serialized = json.dumps(summary, indent=2) + "\n"
    if target.exists() and target.read_text() != serialized:
        raise ValueError("Output manifest changed; use a new output directory")
    target.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()

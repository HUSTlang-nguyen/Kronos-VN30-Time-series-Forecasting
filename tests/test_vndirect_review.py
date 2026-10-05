from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from review_vndirect_candidate import calendar_review, capture_drift, load_audit, sample_summary, sha, write_once
from validate_vn30_sources import compare, parse


CONFIG = {"start": "2021-06-01", "end": "2021-06-03", "timezone": "Asia/Ho_Chi_Minh",
          "seed": 42, "samples_per_year": 3, "extreme_return_count": 1,
          "tolerances": dict.fromkeys(("open", "high", "low", "close"), 0.02)}


def candles(dates, values):
    stamps = [int(pd.Timestamp(day, tz="UTC").timestamp()) for day in dates]
    return parse(json.dumps({"s": "ok", "t": stamps, "o": values, "h": [x + 1 for x in values],
                             "l": [x - 1 for x in values], "c": values}).encode(), CONFIG)


def test_duplicate_resolution_does_not_claim_removed_or_changed_prices():
    old = candles(["2021-06-01", "2021-06-01", "2021-06-02"], [100, 102, 101])
    new = candles(["2021-06-01", "2021-06-02"], [102, 101])
    drift = capture_drift(old, new, CONFIG["start"], CONFIG["end"])
    assert drift["old_duplicate_dates"] == ["2021-06-01"]
    assert drift["dates_removed_from_response"] == []
    assert drift["common_unambiguous_dates"] == 1
    assert drift["changed_ohlc_dates"] == 0
    reverse = capture_drift(new, old, CONFIG["start"], CONFIG["end"])
    assert reverse["dates_removed_from_response"] == []


def test_drift_only_uses_common_requested_dates_and_detects_changed_fields():
    old = candles(["2021-05-31", "2021-06-01", "2021-06-02"], [1, 100, 101])
    new = candles(["2021-06-01", "2021-06-03"], [100.5, 103])
    drift = capture_drift(old, new, CONFIG["start"], CONFIG["end"])
    assert drift["changed_ohlc_dates"] == 1
    assert drift["changed_fields"]["close"] == 1
    assert drift["dates_removed_from_response"] == ["2021-06-02"]
    assert drift["dates_added_to_response"] == ["2021-06-03"]


def test_sample_counts_distinguish_missing_discrepancies_and_passes():
    primary = candles(["2021-06-01", "2021-06-02", "2021-06-03"], [100, 150, 151])
    other = candles(["2021-06-01", "2021-06-03"], [100, 152])
    rows = sample_summary(compare({"vndirect": primary, "other": other}, CONFIG), "vndirect")[0]
    assert rows["selected_dates"] == 3
    assert rows["complete_ohlc_dates"] == 2
    assert rows["all_fields_within_tolerance_dates"] == 1
    assert rows["missing_fields"] == 4
    assert rows["discrepancy_fields"] == 4
    assert rows["upstream_independence"] == "unverified"


def test_calendar_is_scoped_to_provider_interval_and_retains_shortened_session(tmp_path):
    source = tmp_path / "notice.txt"
    source.write_bytes(b"synthetic fixture")
    config = {"covered_years": [2021], "status": "synthetic_pending", "annual_sources": {"2021": "a"},
              "sources": {"a": {"path": str(source), "sha256": sha(source.read_bytes())}},
              "limitations": ["synthetic"], "closures": [],
              "session_events": [{"date": "2021-06-01", "quality_flag": "shortened_session", "source": "a"}]}
    path = tmp_path / "calendar.yaml"
    path.write_text(yaml.safe_dump(config))
    frame = candles(["2021-06-01", "2021-06-02"], [100, 101])
    days, result = calendar_review(frame, {"2021": str(path)}, "2021-06-01", "2021-06-02", tmp_path)
    assert result[0]["missing_scheduled_sessions"] == []
    assert result[0]["scheduled_sessions"] == 2
    assert days.loc[0, "session_quality_flag"] == "shortened_session"
    assert days.is_session.all()
    with pytest.raises(ValueError, match="Missing calendar evidence"):
        calendar_review(frame, {}, "2021-06-01", "2021-06-02", tmp_path)


def test_audit_rejects_tampered_raw_response(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/validate_vn30_sources.py").write_bytes(b"synthetic parser identity")
    config = {**CONFIG, "providers": {"vndirect": {}}}
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    run = tmp_path / "capture"
    run.mkdir()
    (run / "manifest.json").write_text(json.dumps({"run_id": "capture", "config_sha256": sha(config_path.read_bytes()),
        "script_sha256": sha(b"synthetic parser identity"), "providers": {"vndirect": {"response_sha256": sha(b"original")}}}))
    (run / "vndirect.json").write_bytes(b"changed")
    with pytest.raises(ValueError, match="Raw response hash mismatch"):
        load_audit(tmp_path, "config.yaml", "capture")


def test_changed_evidence_cannot_overwrite_previous_output(tmp_path):
    path = tmp_path / "summary.json"
    write_once(path, b"original")
    write_once(path, b"original")
    with pytest.raises(ValueError, match="Evidence changed"):
        write_once(path, b"changed")
    assert path.read_bytes() == b"original"

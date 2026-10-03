import importlib.util
from pathlib import Path

import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hose_calendar", ROOT / "scripts/build_hose_calendar.py")
calendar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calendar)


def test_holiday_update_and_makeup_saturdays_remain_closed():
    config = yaml.safe_load((ROOT / "data/manifests/hose_calendar_evidence.yaml").read_text())
    days = calendar.build(config, "2026-01-01", "2026-08-24").set_index("date")
    for day in ["2026-01-02", "2026-01-10", "2026-08-22"]:
        assert not days.loc[day, "is_session"]
    assert days.loc["2026-01-05", "is_session"]
    assert days.loc["2026-08-24", "is_session"]


def test_uncovered_year_cannot_be_inferred_from_weekdays():
    config = yaml.safe_load((ROOT / "data/manifests/hose_calendar_evidence.yaml").read_text())
    with pytest.raises(ValueError, match="lack calendar evidence"):
        calendar.build(config, "2024-12-31", "2025-01-02")


def test_2023_updated_national_day_does_not_use_old_settlement_schedule():
    config = yaml.safe_load((ROOT / "data/manifests/hose_calendar_2023_evidence.yaml").read_text())
    days = calendar.build(config, "2023-09-01", "2023-09-05").set_index("date")
    assert not days.loc["2023-09-01", "is_session"]
    assert not days.loc["2023-09-04", "is_session"]
    assert days.loc["2023-09-05", "is_session"]


def test_tampered_source_is_rejected(tmp_path):
    path = tmp_path / "source.pdf"
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        calendar.verify_sources({"sources": {"s": {"path": str(path), "sha256": "0" * 64}}})


def test_2024_updated_holiday_and_makeup_saturday():
    config = yaml.safe_load((ROOT / "data/manifests/hose_calendar_2024_evidence.yaml").read_text())
    days = calendar.build(config, "2024-04-26", "2024-05-06").set_index("date")
    for day in ["2024-04-29", "2024-04-30", "2024-05-01", "2024-05-04"]:
        assert not days.loc[day, "is_session"]
        assert days.loc[day, "source"] == "hose_2024_update"
    for day in ["2024-04-26", "2024-05-02", "2024-05-03", "2024-05-06"]:
        assert days.loc[day, "is_session"]


def test_shortened_session_annotations_do_not_close_or_create_a_session():
    config = {"covered_years": [2021], "sources": {"annual": {}, "halt": {}},
              "annual_sources": {"2021": "annual"}, "status": "synthetic_fixture",
              "closures": [], "session_events": [
                  {"date": "2021-06-01", "quality_flag": "shortened_session", "source": "halt"}]}
    days = calendar.build(config, "2021-05-31", "2021-06-02").set_index("date")
    assert days.loc["2021-06-01", "is_session"]
    assert days.loc["2021-06-01", "session_quality_flag"] == "shortened_session"
    assert days.loc["2021-06-01", "event_source"] == "halt"
    config["closures"] = [{"start": "2021-06-01", "end": "2021-06-01", "reason": "synthetic", "source": "annual"}]
    with pytest.raises(ValueError, match="closed day"):
        calendar.build(config, "2021-05-31", "2021-06-02")


def test_2018_halt_retains_partial_session_and_cross_year_bridge():
    config = yaml.safe_load((ROOT / "data/manifests/hose_calendar_2018_evidence.yaml").read_text())
    days = calendar.build(config, "2018-01-01", "2018-12-31").set_index("date")
    assert days.loc["2018-01-22", "is_session"]
    assert days.loc["2018-01-22", "session_quality_flag"] == "shortened_session"
    assert days.loc["2018-01-25", "is_session"]
    for day in ["2018-01-23", "2018-01-24", "2018-12-31"]:
        assert not days.loc[day, "is_session"]

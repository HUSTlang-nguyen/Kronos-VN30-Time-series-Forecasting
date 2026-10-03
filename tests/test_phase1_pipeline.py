import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from phase1_pipeline import process, quality_report, temporal_split


def fixture():
    dates = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-08"])
    frame = pd.DataFrame({"date": dates, "open": [100, 100, 105], "high": [101, 112, 107],
                          "low": [99, 99, 104], "close": [100, 111, 106]})
    return dates, frame


def test_processing_blocks_unaccepted_inputs_and_does_not_mutate():
    dates, frame = fixture()
    before = frame.copy()
    with pytest.raises(ValueError, match="G1"):
        process(frame, dates, source="test", g1_accepted=False, calendar_accepted=True)
    result = process(frame, dates, source="test", g1_accepted=True, calendar_accepted=True)
    pd.testing.assert_frame_equal(frame, before)
    assert np.isnan(result.return_1d.iloc[0])
    assert result.quality_flags.iloc[1] == "abs_return_gt_10pct"
    assert len(result) == 3
    assert result.range_abs.iloc[1] == 13
    assert result.body_abs.iloc[1] == 11


def test_no_future_observation_changes_past_features():
    dates, frame = fixture()
    before = process(frame, dates, source="test", g1_accepted=True, calendar_accepted=True)
    frame.loc[2, ["open", "high", "low", "close"]] = [1000, 1100, 900, 1050]
    after = process(frame, dates, source="test", g1_accepted=True, calendar_accepted=True)
    pd.testing.assert_frame_equal(before.iloc[:2], after.iloc[:2])


def test_shortened_session_retains_prices_dates_and_existing_quality_flags():
    dates, frame = fixture()
    baseline = process(frame, dates, source="test", g1_accepted=True, calendar_accepted=True)
    annotations = pd.DataFrame({"date": dates[:2], "session_quality_flag": "shortened_session"})
    result = process(frame, dates, source="test", g1_accepted=True,
                     calendar_accepted=True, session_annotations=annotations)
    pd.testing.assert_frame_equal(result.drop(columns="quality_flags"), baseline.drop(columns="quality_flags"))
    assert result.quality_flags.tolist() == [
        "first_return_undefined;shortened_session", "abs_return_gt_10pct;shortened_session", ""]
    annotations.loc[0, "date"] = pd.Timestamp("2026-01-04")
    with pytest.raises(ValueError, match="non-session"):
        process(frame, dates, source="test", g1_accepted=True,
                calendar_accepted=True, session_annotations=annotations)


def test_missing_session_invalid_candle_and_unsorted_dates_rejected():
    dates, frame = fixture()
    report = quality_report(frame.iloc[[0, 2]], dates)
    assert report["missing_sessions"] == ["2026-01-06"]
    frame.loc[1, "high"] = 101
    with pytest.raises(ValueError, match="quality failures"):
        process(frame, dates, source="test", g1_accepted=True, calendar_accepted=True)
    with pytest.raises(ValueError, match="sorted"):
        quality_report(frame.iloc[::-1], dates)


def test_full_path_counts_and_projection_include_tail_sessions():
    # Synthetic dates are test fixtures, never a replacement exchange calendar.
    calendar = pd.date_range("2025-01-01", periods=250)
    boundary = "2025-01-02T12:00:00Z"
    origins, report = temporal_split(calendar[:210], calendar, boundary, str(calendar[209].date()), context=2)
    assert report["eligible_sessions"] == 208
    assert report["validation_origins"] == 44
    assert report["test_origins"] == 126
    assert report["size_gate"] == "pass"
    assert report["earliest_projected_freeze"] == str(calendar[209].date())
    test = origins[origins.partition.eq("test")]
    assert test.origin_date.iloc[0] == calendar[64]
    for row in origins.itertuples():
        targets = pd.to_datetime(row.target_dates)
        assert len(targets) == 20 and (targets > row.origin_date).all()
    _, shorter = temporal_split(calendar[:209], calendar, boundary, str(calendar[208].date()), context=2)
    assert shorter["test_origins"] == 125 and shorter["size_gate"] == "pilot"


def test_missing_observation_and_insufficient_context_never_create_origins():
    calendar = pd.date_range("2025-01-01", periods=20)
    with pytest.raises(ValueError, match="does not match"):
        temporal_split(calendar.delete(8), calendar, "2025-01-02T00:00:00Z", "2025-01-20")
    origins, report = temporal_split(calendar, calendar, "2025-01-02T00:00:00Z", "2025-01-20", context=128, path=2, validation=3, minimum_test_origins=2)
    assert origins.empty and report["earliest_projected_freeze"] is None

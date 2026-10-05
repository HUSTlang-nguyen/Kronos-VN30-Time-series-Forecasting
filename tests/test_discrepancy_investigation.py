from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from investigate_vndirect_discrepancies import published_verdict, row_at, usable


def candle(day, invalid=False):
    return {"date": pd.Timestamp(day), "open": 101, "high": 102, "low": 100, "close": 101,
            "duplicate_date": False, "invalid_numeric": False, "invalid_ohlc": invalid,
            "outside_request": False}


def test_ambiguous_date_cannot_be_selected_as_confirmation():
    rows = pd.DataFrame([candle("2020-08-13"), candle("2020-08-13")])
    assert row_at(rows, pd.Timestamp("2020-08-13")) is None
    assert not usable(row_at(rows, pd.Timestamp("2020-08-13")))


def test_invalid_or_missing_candle_cannot_confirm_provider():
    assert not usable(pd.Series(candle("2020-08-13", invalid=True)))
    assert not usable(None)
    assert usable(pd.Series(candle("2020-08-13")))


def test_public_close_does_not_resolve_high_or_root_cause():
    evidence = [{"field": "close", "value": 797.08}]
    assert published_verdict("close", 797.08, 799.53, .02, evidence) == "published_value_supports_vndirect"
    assert published_verdict("high", 797.08, 799.53, .02, evidence) == "unresolved"
    assert published_verdict("close", 799.53, 797.08, .02, evidence) == "published_value_supports_comparator"


def test_conflicting_publications_are_not_decided_by_majority():
    evidence = [{"field": "close", "value": v} for v in (797.08, 797.08, 799.53)]
    assert published_verdict("close", 797.08, 799.53, .02, evidence) == "conflicting_or_inconclusive_publications"

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from investigate_source_anomalies import duplicate_details
from reconcile_hose_sessions import reconcile


def test_conflicting_duplicate_values_are_not_treated_as_identical():
    frame = pd.DataFrame({"date": pd.to_datetime(["2025-05-05"] * 2),
                          "timestamp": [1746378000, 1746403200], "open": [1309.73, 1315.43],
                          "high": [1321.68] * 2, "low": [1309.43] * 2, "close": [1320.41] * 2})
    result = duplicate_details(frame)
    assert len(result) == 1
    assert result[0]["identical_ohlc"] is False
    assert result[0]["timestamps"] == [1746378000, 1746403200]
    assert len(frame) == 2


def test_reconciliation_separates_missing_closed_duplicate_and_uncovered_dates():
    calendar = pd.DataFrame({"date": pd.to_datetime(["2025-04-03", "2025-04-04", "2025-04-05"]),
                             "is_session": [True, True, False]})
    frame = pd.DataFrame({"date": pd.to_datetime(["2024-12-31", "2025-04-04", "2025-04-04", "2025-04-05"])})
    result = reconcile(frame, calendar)
    assert result["missing_scheduled_sessions"] == ["2025-04-03"]
    assert result["observed_non_sessions"] == ["2025-04-05"]
    assert result["duplicate_dates_in_coverage"] == ["2025-04-04"]
    assert result["observations_outside_calendar_coverage"] == 1

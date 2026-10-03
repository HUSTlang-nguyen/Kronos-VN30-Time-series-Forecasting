from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("source_audit", ROOT / "scripts" / "validate_vn30_sources.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

CONFIG = {
    "start": "2026-09-01", "end": "2026-09-30", "timezone": "Asia/Ho_Chi_Minh",
    "seed": 42, "samples_per_year": 5, "extreme_return_count": 1,
    "tolerances": dict.fromkeys(audit.FIELDS, 0.02),
}


def payload(stamps: list[int], closes: list[float]) -> bytes:
    return json.dumps({"s": "ok", "t": stamps, "o": closes, "h": [x + 1 for x in closes], "l": [x - 1 for x in closes], "c": closes}).encode()


def test_session_date_uses_local_timezone_and_retains_duplicates() -> None:
    stamp = int(pd.Timestamp("2026-09-01T18:00:00Z").timestamp())
    frame = audit.parse(payload([stamp, stamp], [100, 101]), CONFIG)
    assert frame.date.tolist() == [pd.Timestamp("2026-09-02")] * 2
    assert frame.duplicate_date.all()
    assert len(frame) == 2


def test_material_open_difference_is_not_hidden_by_equal_close() -> None:
    stamp = int(pd.Timestamp("2026-09-01T00:00:00Z").timestamp())
    left = audit.parse(payload([stamp], [100]), CONFIG)
    right = left.astype({"open": float}).copy()
    right.loc[0, "open"] = 100.5
    result = audit.compare({"left": left, "right": right}, CONFIG)
    assert result.loc[result.field == "open", "status"].tolist() == ["discrepancy"]
    assert result.loc[result.field == "close", "status"].tolist() == ["pass"]


def test_extreme_date_missing_from_other_source_is_reported() -> None:
    dates = [int(pd.Timestamp(f"2026-09-{d:02d}", tz="UTC").timestamp()) for d in (1, 2, 3)]
    left = audit.parse(payload(dates, [100, 150, 151]), CONFIG)
    right = audit.parse(payload([dates[0], dates[2]], [100, 151]), CONFIG)
    result = audit.compare({"left": left, "right": right}, CONFIG)
    missing = result.loc[result.date == pd.Timestamp("2026-09-02")]
    assert len(missing) == 4
    assert (missing.status == "missing").all()
    assert (missing.resolution == "unresolved").all()

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_vnstock_sources import normalize
from verify_vnstock_capture import reconstruct

CONFIG = {"timezone": "Asia/Ho_Chi_Minh", "start": "2012-02-06", "end": "2026-10-01"}


def test_vci_index_points_and_local_session_date_are_preserved():
    payload = [{"symbol": "VN30", "t": [str(int(pd.Timestamp("2025-04-02T17:00:00Z").timestamp()))],
                "o": [1342.46], "h": [1342.46], "l": [1282.99], "c": [1283.18]}]
    frame = reconstruct("vci", json.dumps(payload).encode(), CONFIG)
    assert frame.date.iloc[0] == pd.Timestamp("2025-04-03")
    assert frame.close.iloc[0] == 1283.18
    assert not frame.invalid_ohlc.iloc[0]


def test_kbs_invalid_candle_is_flagged_without_repair():
    payload = {"symbol": "VN30", "data_day": [{"t": "2012-07-12 07:00", "o": "479.88", "h": "483.68", "l": "481.57", "c": "483.12"}]}
    frame = reconstruct("kbs", json.dumps(payload).encode(), CONFIG)
    assert len(frame) == 1
    assert frame.open.iloc[0] == 479.88
    assert frame.invalid_ohlc.iloc[0]


def test_wrong_asset_cannot_be_used_as_index():
    with pytest.raises(ValueError, match="Wrong index"):
        reconstruct("vci", json.dumps([{"symbol": "VN30F1M"}]).encode(), CONFIG)


def test_normalization_retains_duplicate_and_out_of_range_rows():
    frame = pd.DataFrame({"time": ["2026-10-02", "2026-10-02"], "open": [100, 101],
                          "high": [105, 105], "low": [99, 99], "close": [103, 103]})
    result = normalize(frame, CONFIG)
    assert len(result) == 2
    assert result.duplicate_date.all() and result.outside_request.all()

import hashlib
import io
import json
import sqlite3
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from share_vndirect_snapshot import export_snapshot, verify_snapshot
from share_vndirect_sqlite import export_sqlite, verify_sqlite


def capture(tmp_path):
    run = "synthetic_test_only"
    directory = tmp_path / "data/raw/source_audit" / run
    directory.mkdir(parents=True)
    (tmp_path / "configs").mkdir()
    (tmp_path / "scripts").mkdir()
    config = b"start: '2026-09-01'\nend: '2026-09-30'\ntimezone: Asia/Ho_Chi_Minh\n"
    code = (ROOT / "scripts/validate_vn30_sources.py").read_bytes()
    # Duplicate dates, invalid candle and outside-request date are intentional.
    raw = json.dumps({"s": "ok", "t": [1788220800, 1788220800, 1790812800],
                      "o": [100, 110, 100], "h": [102, 102, 102],
                      "l": [99, 99, 99], "c": [101, 101, 101]}).encode()
    sha = lambda content: hashlib.sha256(content).hexdigest()
    audit = {"run_id": run, "config_sha256": sha(config), "script_sha256": sha(code),
             "retrieved_at_utc": "2026-10-01T16:00:00Z",
             "providers": {"vndirect": {"response_sha256": sha(raw),
                                        "url": "https://example.invalid/synthetic"}}}
    (directory / "manifest.json").write_text(json.dumps(audit))
    (directory / "vndirect.json").write_bytes(raw)
    (tmp_path / "configs/data_source_acceptance.yaml").write_bytes(config)
    (tmp_path / "scripts/validate_vn30_sources.py").write_bytes(code)
    return run, tmp_path / "bundle.zip", raw


def test_snapshot_retains_anomalies_and_original_response(tmp_path):
    run, output, raw = capture(tmp_path)
    result = export_snapshot(tmp_path, run, output)
    snapshot = result["snapshot"]
    assert snapshot["rows"] == 3
    assert snapshot["quality_counts"] == {"duplicate_date": 2, "invalid_numeric": 0,
                                          "invalid_ohlc": 1, "outside_request": 1}
    assert snapshot["gate_G1"] == "pending"
    assert not snapshot["includes_accepted_calendar_or_splits"]
    assert verify_snapshot(output, result["archive_sha256"]) == result
    with ZipFile(output) as archive:
        assert archive.read("original_response.json") == raw
    with pytest.raises(ValueError, match="overwrite"):
        export_snapshot(tmp_path, run, output)


def test_changed_file_rejected_even_with_matching_archive_checksum(tmp_path):
    run, output, _ = capture(tmp_path)
    export_snapshot(tmp_path, run, output)
    with ZipFile(output) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    files["vn30_daily.csv"] += b"altered\n"
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name, payload in files.items():
            archive.writestr(name, payload)
    output.write_bytes(buffer.getvalue())
    with pytest.raises(ValueError, match="Archive SHA256 mismatch"):
        verify_snapshot(output)
    with pytest.raises(ValueError, match="File integrity mismatch: vn30_daily.csv"):
        verify_snapshot(output, hashlib.sha256(buffer.getvalue()).hexdigest())


def test_export_rejects_changed_original_capture(tmp_path):
    run, output, raw = capture(tmp_path)
    (tmp_path / "data/raw/source_audit" / run / "vndirect.json").write_bytes(raw + b" ")
    with pytest.raises(ValueError, match="Captured input hash mismatch"):
        export_snapshot(tmp_path, run, output)
    assert not output.exists()


def test_sqlite_preserves_candidate_rows_and_original_bytes(tmp_path):
    run, archive, raw = capture(tmp_path)
    receipt = export_snapshot(tmp_path, run, archive)
    database = tmp_path / "snapshot.sqlite"
    result = export_sqlite(archive, database, receipt["archive_sha256"])
    assert result["snapshot"] == receipt["snapshot"]
    assert verify_sqlite(database) == result
    connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
    try:
        assert connection.execute("SELECT COUNT(*) FROM candles").fetchone() == (3,)
        assert connection.execute("SELECT SUM(duplicate_date), SUM(invalid_ohlc), "
                                  "SUM(outside_request) FROM candles").fetchone() == (2, 1, 1)
        assert connection.execute("SELECT content FROM source_files WHERE name = ?",
                                  ("original_response.json",)).fetchone()[0] == raw
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("DELETE FROM candles")
    finally:
        connection.close()
    with pytest.raises(ValueError, match="overwrite"):
        export_sqlite(archive, database, receipt["archive_sha256"])


def test_sqlite_rejects_modified_prices(tmp_path):
    run, archive, _ = capture(tmp_path)
    receipt = export_snapshot(tmp_path, run, archive)
    database = tmp_path / "snapshot.sqlite"
    export_sqlite(archive, database, receipt["archive_sha256"])
    connection = sqlite3.connect(database)
    try:
        connection.execute("UPDATE candles SET close = 1 WHERE row_id = 1")
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(ValueError, match="SQLite SHA256 mismatch"):
        verify_sqlite(database)
    with pytest.raises(ValueError, match="candles differ from original CSV"):
        verify_sqlite(database, hashlib.sha256(database.read_bytes()).hexdigest())

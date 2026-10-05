"""Create/verify a self-contained SQLite copy of a verified candidate snapshot."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sqlite3
import tempfile
from datetime import date
from pathlib import Path
from zipfile import ZipFile

from share_vndirect_snapshot import ROOT, RUN, sha, verify_snapshot

SCHEMA = """
CREATE TABLE candles (
    row_id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    provider TEXT NOT NULL,
    date TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL, high REAL, low REAL, close REAL,
    duplicate_date INTEGER NOT NULL CHECK (duplicate_date IN (0, 1)),
    invalid_numeric INTEGER NOT NULL CHECK (invalid_numeric IN (0, 1)),
    invalid_ohlc INTEGER NOT NULL CHECK (invalid_ohlc IN (0, 1)),
    outside_request INTEGER NOT NULL CHECK (outside_request IN (0, 1))
);
CREATE INDEX candles_by_date ON candles(symbol, date);
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE source_files (
    name TEXT PRIMARY KEY, sha256 TEXT NOT NULL,
    size_bytes INTEGER NOT NULL, content BLOB NOT NULL
);
"""


def candle_rows(raw: bytes, manifest: dict) -> list[tuple]:
    result = []
    for number, row in enumerate(csv.DictReader(io.StringIO(raw.decode("utf-8"))), 1):
        date.fromisoformat(row["date"])
        flags = [row[name] for name in
                 ("duplicate_date", "invalid_numeric", "invalid_ohlc", "outside_request")]
        if any(flag not in ("True", "False") for flag in flags):
            raise ValueError("Invalid CSV quality flag")
        prices = [float(row[name]) for name in ("open", "high", "low", "close")]
        if not all(math.isfinite(value) for value in prices):
            raise ValueError("Non-finite prices cannot round-trip through REAL; retain the ZIP snapshot")
        result.append((number, manifest["symbol"], manifest["provider"], row["date"],
                       int(row["timestamp"]),
                       *prices,
                       *(int(flag == "True") for flag in flags)))
    return result


def export_sqlite(source: Path, output: Path, expected_archive_sha256: str) -> dict:
    receipt = verify_snapshot(source, expected_archive_sha256)
    manifest = receipt["snapshot"]
    sidecar = output.with_suffix(output.suffix + ".sha256")
    if output.exists() or sidecar.exists():
        raise ValueError("Refusing to overwrite an existing SQLite snapshot/checksum")
    with ZipFile(source) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    rows = candle_rows(files["vn30_daily.csv"], manifest)
    if len(rows) != manifest["rows"]:
        raise ValueError("CSV row count differs from snapshot manifest")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sqlite-snapshot-", dir=output.parent) as staging:
        staged = Path(staging) / "snapshot.sqlite"
        connection = sqlite3.connect(staged)
        try:
            connection.executescript(SCHEMA)
            # row_id preserves source order and conflicting duplicate dates.
            connection.executemany("INSERT INTO candles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
            connection.executemany("INSERT INTO metadata VALUES (?,?)", [
                ("snapshot", json.dumps(manifest, sort_keys=True)),
                ("source_archive_sha256", receipt["archive_sha256"]),
                ("schema_version", "1"),
            ])
            connection.executemany("INSERT INTO source_files VALUES (?,?,?,?)",
                                   [(name, sha(raw), len(raw), raw) for name, raw in files.items()])
            connection.commit()
        finally:
            connection.close()
        content = staged.read_bytes()
        # Publish a closed database in default DELETE journal mode, without WAL files.
        with output.open("xb") as handle:
            handle.write(content)
    with sidecar.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{sha(content)}  {output.name}\n")
    return verify_sqlite(output, sha(content))


def verify_sqlite(path: Path, expected_sha256: str | None = None) -> dict:
    checksum = sha(path.read_bytes())
    expected = expected_sha256 or path.with_suffix(path.suffix + ".sha256").read_text().split()[0]
    if checksum != expected:
        raise ValueError("SQLite SHA256 mismatch")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity check failed")
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        manifest = json.loads(metadata["snapshot"])
        stored = {}
        for name, digest, size, content in connection.execute(
                "SELECT name, sha256, size_bytes, content FROM source_files"):
            _check_content(name, digest, size, content)
            stored[name] = content
        if set(stored) != set(manifest["files"]) | {"manifest.json"}:
            raise ValueError("SQLite source file list differs from manifest")
        if json.loads(stored["manifest.json"]) != manifest:
            raise ValueError("Embedded manifest mismatch")
        for name, record in manifest["files"].items():
            _check_content(name, record["sha256"], record["size_bytes"], stored[name])
        expected_rows = candle_rows(stored["vn30_daily.csv"], manifest)
        observed_rows = connection.execute("SELECT * FROM candles ORDER BY row_id").fetchall()
        if observed_rows != expected_rows or len(observed_rows) != manifest["rows"]:
            raise ValueError("SQLite candles differ from original CSV")
    finally:
        connection.close()
    return {"database": str(path), "database_sha256": checksum, "integrity": "verified",
            "source_archive_sha256": metadata["source_archive_sha256"], "snapshot": manifest}


def _check_content(name: str, digest: str, size: int, raw: bytes) -> None:
    if sha(raw) != digest or len(raw) != size:
        raise ValueError(f"SQLite source integrity mismatch: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data/share" / f"vn30_vndirect_{RUN}_candidate.zip")
    parser.add_argument("--receipt", type=Path, default=ROOT / "data/manifests/vndirect_contributor_snapshot.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/share" / f"vn30_vndirect_{RUN}_candidate.sqlite")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    if args.expected_sha256 and not args.verify:
        parser.error("--expected-sha256 requires --verify")
    try:
        result = (verify_sqlite(args.verify, args.expected_sha256) if args.verify else
                  export_sqlite(args.source, args.output,
                                json.loads(args.receipt.read_text())["archive_sha256"]))
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f"SQLite snapshot refused: {exc}\n")


if __name__ == "__main__":
    main()

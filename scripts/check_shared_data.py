"""Verify the contributor's local data file against the receipt in this checkout."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from share_vndirect_snapshot import ROOT, verify_snapshot
from share_vndirect_sqlite import verify_sqlite


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("sqlite", "zip"), default="sqlite")
    parser.add_argument("--path", type=Path, help="Override the local data file location")
    args = parser.parse_args()
    name = "vndirect_sqlite_snapshot.json" if args.format == "sqlite" else "vndirect_contributor_snapshot.json"
    try:
        receipt = json.loads((ROOT / "data/manifests" / name).read_text(encoding="utf-8"))
        file_key, hash_key = (("database", "database_sha256") if args.format == "sqlite"
                              else ("archive", "archive_sha256"))
        path = args.path or ROOT / receipt[file_key]
        result = (verify_sqlite(path, receipt[hash_key]) if args.format == "sqlite"
                  else verify_snapshot(path, receipt[hash_key]))
        snapshot = result["snapshot"]
        if snapshot != receipt["snapshot"]:
            raise ValueError("Local snapshot metadata differs from the tracked receipt")
        print(json.dumps({"integrity": result["integrity"], "format": args.format,
                          "rows": snapshot["rows"], "classification": snapshot["classification"],
                          "gate_G1": snapshot["gate_G1"]}, indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Shared data unavailable or invalid: {exc}\n"
                    "See docs/Contributor_Data_Guide.md for the matching snapshot.\n")


if __name__ == "__main__":
    main()

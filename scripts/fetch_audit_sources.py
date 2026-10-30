"""Fetch traceable independent provider evidence without editing the old audit."""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_protocol import atomic_json, file_hash


def main():
    import pandas as pd
    import yaml
    from validate_vn30_sources import download, parse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cfg = yaml.safe_load((ROOT / "configs/data_source_acceptance.yaml").read_bytes())
    failures = {}
    for name in ("vps", "dnse"):
        spec = cfg["providers"][name]
        url = (
            spec["endpoint"]
            + "?"
            + urlencode(
                {
                    "symbol": "VN30",
                    "resolution": spec["resolution"],
                    "from": int(pd.Timestamp("2017-08-24", tz="UTC").timestamp()),
                    "to": int(pd.Timestamp("2026-10-02", tz="UTC").timestamp()) - 1,
                }
            )
        )
        try:
            raw = download(url)
            (args.output / (name + "-raw.json")).write_bytes(raw)
            data = parse(raw, {**cfg, "start": "2017-08-24", "end": "2026-10-01"})
            data["date"] = data.date.dt.strftime("%Y-%m-%d")
            path = args.output / (name + ".csv")
            data.to_csv(path, index=False)
            atomic_json(
                path.with_suffix(".json"),
                {
                    "provider": name,
                    "symbol": "VN30",
                    "url": url,
                    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                    "raw_sha256": file_hash(args.output / (name + "-raw.json")),
                    "csv_sha256": file_hash(path),
                    "timezone": cfg["timezone"],
                },
            )
        except Exception as exc:
            failures[name] = type(exc).__name__ + ": " + str(exc)
    atomic_json(args.output / "fetch_status.json", {"failures": failures})
    print(json.dumps({"output": str(args.output), "failures": failures}, indent=2))


if __name__ == "__main__":
    main()

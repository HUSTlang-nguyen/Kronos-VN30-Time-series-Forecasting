"""Export/verify a candidate contributor snapshot; never accept or freeze Phase 1."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
RUN = "20261001T151513588605Z"
MEMBERS = {"vn30_daily.csv", "original_response.json", "audit_manifest.json",
           "audit_config.yaml", "parser.py", "manifest.json"}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def export_snapshot(root: Path, run: str, output: Path) -> dict:
    import yaml
    from validate_vn30_sources import parse

    if not run or Path(run).name != run or run in {".", ".."} or "\\" in run:
        raise ValueError("Expected one audit run directory name")
    capture = root / "data/raw/source_audit" / run
    audit_bytes = (capture / "manifest.json").read_bytes()
    audit = json.loads(audit_bytes)
    if audit["run_id"] != run:
        raise ValueError("Audit run identity mismatch")
    files = {
        "original_response.json": (capture / "vndirect.json").read_bytes(),
        "audit_manifest.json": audit_bytes,
        "audit_config.yaml": (root / "configs/data_source_acceptance.yaml").read_bytes(),
        "parser.py": (root / "scripts/validate_vn30_sources.py").read_bytes(),
    }
    bindings = {
        "original_response.json": audit["providers"]["vndirect"]["response_sha256"],
        "audit_config.yaml": audit["config_sha256"],
        "parser.py": audit["script_sha256"],
    }
    for name, expected in bindings.items():
        if sha(files[name]) != expected:
            raise ValueError(f"Captured input hash mismatch: {name}")
    config = yaml.safe_load(files["audit_config.yaml"])
    frame = parse(files["original_response.json"], config)
    # Preserve original order and every row, including outside-request flags.
    files["vn30_daily.csv"] = frame.to_csv(index=False, date_format="%Y-%m-%d",
                                           lineterminator="\n").encode("utf-8")
    manifest = {
        "schema_version": 1, "provider": "vndirect", "symbol": "VN30",
        "classification": "candidate_snapshot_not_accepted_dataset",
        "gate_G1": "pending", "run_id": run,
        "retrieved_at_utc": audit["retrieved_at_utc"],
        "request_url": audit["providers"]["vndirect"]["url"],
        "timezone": config["timezone"], "units": "index_points",
        "rows": len(frame), "first_date": str(frame.date.min().date()),
        "last_date": str(frame.date.max().date()),
        "quality_counts": {name: int(frame[name].sum()) for name in
                           ("duplicate_date", "invalid_numeric", "invalid_ohlc", "outside_request")},
        "csv_semantics": "normalized_provider_snapshot_all_rows_unmodified_prices",
        "includes_accepted_calendar_or_splits": False,
        "files": {name: {"sha256": sha(raw), "size_bytes": len(raw)}
                  for name, raw in files.items()},
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as bundle:
        for name, raw in sorted(files.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            bundle.writestr(info, raw)
    sidecar = output.with_suffix(output.suffix + ".sha256")
    if output.exists() or sidecar.exists():
        raise ValueError("Refusing to overwrite an existing snapshot/checksum")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        handle.write(buffer.getvalue())
    with sidecar.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{sha(buffer.getvalue())}  {output.name}\n")
    return verify_snapshot(output)


def verify_snapshot(path: Path, expected_sha256: str | None = None) -> dict:
    raw = path.read_bytes()
    expected = expected_sha256 or path.with_suffix(path.suffix + ".sha256").read_text().split()[0]
    if sha(raw) != expected:
        raise ValueError("Archive SHA256 mismatch")
    with ZipFile(io.BytesIO(raw)) as bundle:
        names = bundle.namelist()
        if set(names) != MEMBERS or len(names) != len(MEMBERS):
            raise ValueError("Unexpected or duplicate archive members")
        manifest = json.loads(bundle.read("manifest.json"))
        if set(manifest["files"]) != MEMBERS - {"manifest.json"}:
            raise ValueError("Incomplete file manifest")
        for name, record in manifest["files"].items():
            payload = bundle.read(name)
            if sha(payload) != record["sha256"] or len(payload) != record["size_bytes"]:
                raise ValueError(f"File integrity mismatch: {name}")
    return {"archive": str(path), "archive_sha256": sha(raw), "integrity": "verified",
            "snapshot": manifest}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=RUN)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256", help="Trusted archive hash from the tracked receipt")
    args = parser.parse_args()
    if args.expected_sha256 and not args.verify:
        parser.error("--expected-sha256 requires --verify")
    try:
        result = (verify_snapshot(args.verify, args.expected_sha256) if args.verify else
                  export_snapshot(ROOT, args.run, args.output or
                                  ROOT / "data/share" / f"vn30_vndirect_{args.run}_candidate.zip"))
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Snapshot refused: {exc}\n")


if __name__ == "__main__":
    main()

"""Restore content-addressed DVC objects downloaded through an authorized Drive UI."""

from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_protocol import atomic_json, file_hash


def md5(data):
    return hashlib.md5(data, usedforsecurity=False).hexdigest()


def restore(archive=None):
    import yaml

    cache = ROOT / ".dvc/cache/files/md5"
    if archive:
        # Only md5/xx/hex[-.dir] entries are accepted; no arbitrary ZIP paths.
        with ZipFile(archive) as bundle:
            for info in bundle.infolist():
                if info.is_dir():
                    continue
                parts = Path(info.filename.replace("\\", "/")).parts
                if (
                    len(parts) != 3
                    or parts[0] != "md5"
                    or not re.fullmatch(r"[0-9a-f]{2}", parts[1])
                    or not re.fullmatch(r"[0-9a-f]{30}(?:\.[A-Za-z0-9_-]+)*", parts[2])
                ):
                    raise ValueError("Unexpected archive member: " + info.filename)
                data = bundle.read(info)
                # Drive can append .html/.pdf/.zip while bundling extensionless
                # objects. The content hash, not a guessed file type, is identity.
                expected = parts[1] + parts[2][:30]
                if md5(data) != expected:
                    raise ValueError("DVC object checksum mismatch")
                canonical = parts[2][:30] + (
                    ".dir" if parts[2][30:].startswith(".dir") else ""
                )
                destination = cache / parts[1] / canonical
                if not destination.resolve().is_relative_to(cache.resolve()):
                    raise ValueError("Unsafe cache path")
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() and destination.read_bytes() != data:
                    raise ValueError("Existing cache object differs")
                if not destination.exists():
                    destination.write_bytes(data)

    def get(digest):
        value = (cache / digest[:2] / digest[2:]).read_bytes()
        if md5(value) != digest.removesuffix(".dir"):
            raise ValueError("Local DVC object corrupted")
        return value

    restored = []
    for pointer in [
        ROOT / "data/raw.dvc",
        *sorted((ROOT / "data/share").glob("*.dvc")),
    ]:
        info = yaml.safe_load(pointer.read_text())["outs"][0]
        target = (pointer.parent / info["path"]).resolve()
        if not target.is_relative_to((ROOT / "data").resolve()):
            raise ValueError("Unsafe DVC pointer")
        entries = (
            json.loads(get(info["md5"]))
            if info["md5"].endswith(".dir")
            else [{"relpath": None, "md5": info["md5"]}]
        )
        for entry in entries:
            path = (target / entry["relpath"]).resolve() if entry["relpath"] else target
            if entry["relpath"] and not path.is_relative_to(target):
                raise ValueError("Unsafe DVC directory path")
            value = get(entry["md5"])
            if path.exists() and path.read_bytes() != value:
                raise ValueError("Refusing to overwrite different data: " + str(path))
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(value)
            restored.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "md5": entry["md5"],
                    "sha256": file_hash(path),
                }
            )
    return {"classification": "original_dvc_objects_verified", "files": restored}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path)
    p.add_argument("--receipt", type=Path)
    args = p.parse_args()
    result = restore(args.archive)
    if args.receipt:
        atomic_json(args.receipt, result)
    print(
        json.dumps(
            {"classification": result["classification"], "files": len(result["files"])},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

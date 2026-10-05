"""Export the data/test dependency subset from uv.lock, including package hashes."""
from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_PACKAGES = ("numpy", "pandas", "pyarrow", "pyyaml", "pytest", "requests")


def render() -> str:
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    packages = {record["name"]: record for record in lock["package"]}
    pending = list(ROOT_PACKAGES)
    selected = set()
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        selected.add(name)
        pending.extend(item["name"] for item in packages[name].get("dependencies", []))
    lines = ["# Generated from uv.lock by scripts/export_data_requirements.py.",
             "# Data/audit/tests only; no PyTorch or model inference dependencies."]
    for name in sorted(selected):
        package = packages[name]
        hashes = sorted({item["hash"] for item in package.get("wheels", []) +
                         ([package["sdist"]] if "sdist" in package else [])})
        if not hashes:
            raise ValueError(f"No distribution hashes for {name}")
        lines.append(f"{name}=={package['version']} \\")
        lines.extend(f"    --hash={value}" + (" \\" if index < len(hashes) - 1 else "")
                     for index, value in enumerate(hashes))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = ROOT / "requirements/data.txt"
    expected = render()
    if args.check:
        if not destination.exists() or destination.read_text(encoding="utf-8") != expected:
            parser.exit(1, "requirements/data.txt differs from uv.lock; regenerate it\n")
        print("Data dependency lock matches uv.lock")
    else:
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(expected, encoding="utf-8", newline="\n")
        print("Wrote requirements/data.txt")


if __name__ == "__main__":
    main()

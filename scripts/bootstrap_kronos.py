"""Fetch the pinned Kronos implementation on Windows, Linux or in Docker."""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> None:
    manifest = yaml.safe_load((ROOT / "data/manifests/checkpoint_provenance.yaml").read_text(encoding="utf-8"))
    spec = manifest["implementation_code"]["kronos"]
    target = ROOT / ".vendor/Kronos"
    repository, revision = spec["repository"], spec["revision"]
    if target.exists():
        if not (target / ".git").exists():
            raise ValueError("Existing Kronos directory is not a checkout; refusing replacement")
        if Path(git("-C", str(target), "rev-parse", "--show-toplevel")).resolve() != target.resolve():
            raise ValueError("Kronos Git root mismatch")
        if git("-C", str(target), "status", "--porcelain"):
            raise ValueError("Kronos checkout contains local edits; refusing checkout")
        if git("-C", str(target), "remote", "get-url", "origin") != repository:
            raise ValueError("Kronos repository URL mismatch")
        if git("-C", str(target), "rev-parse", "HEAD") == revision:
            print(f"Kronos ready at {target} ({revision})")
            return
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "--filter=blob:none", "--no-checkout", repository, str(target))
    git("-C", str(target), "fetch", "--depth", "1", "origin", revision)
    git("-C", str(target), "checkout", "--detach", revision)
    if git("-C", str(target), "rev-parse", "HEAD") != revision:
        raise ValueError("Kronos revision mismatch")
    print(f"Kronos ready at {target} ({revision})")


if __name__ == "__main__":
    main()

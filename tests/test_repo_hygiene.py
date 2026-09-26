from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_gitlinks_in_repository() -> None:
    result = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    gitlinks = [line for line in result.stdout.splitlines() if line.startswith("160000")]
    assert not gitlinks, f"Found mode 160000 gitlink entries in git index: {gitlinks}"


def test_gitignore_ignores_disposable_and_large_artifacts() -> None:
    test_paths = [
        "tmp/foo.txt",
        "data/raw/test.parquet",
        "data/interim/test.parquet",
        "data/processed/test.parquet",
        "artifacts/forecasts/test.parquet",
        "artifacts/scored/test.parquet",
        "artifacts/checkpoints/model.bin",
        "artifacts/samples/test.parquet",
        "artifacts/cache/test.cache",
        ".vendor/test.py",
        ".cache/test.txt",
    ]
    for p in test_paths:
        res = subprocess.run(
            ["git", "check-ignore", "-q", p],
            cwd=str(ROOT),
        )
        assert res.returncode == 0, f"Expected {p} to be ignored by .gitignore"


def test_canonical_evidence_not_ignored() -> None:
    canonical_paths = [
        "artifacts/smoke/phase0_model_smoke.json",
        "artifacts/source_audit/retrieval.json",
        "data/manifests/checkpoint_provenance.yaml",
        "data/manifests/artifact_registry.yaml",
        "data/manifests/source_crosscheck.parquet",
        "references/zhang_2025/attribution.md",
        "docs/tmp/Kronos_VN30_Agent_Implementation_Plan.md",
    ]
    for p in canonical_paths:
        res = subprocess.run(
            ["git", "check-ignore", "-q", p],
            cwd=str(ROOT),
        )
        assert res.returncode != 0, f"Expected {p} NOT to be ignored by .gitignore"

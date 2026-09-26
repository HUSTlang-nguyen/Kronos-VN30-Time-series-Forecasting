# Phase 0 Completion Report

**Execution date:** 2026-09-26

**Result:** accepted

**Completed tasks:** T001, T002, T003, T004

**Passed gate:** G2

**Pending gates:** G1, G3, G4

## T001 — Research contract

- Output: `configs/study.yaml`
- Status: accepted.
- Evidence: primary endpoint, hypotheses, model scope, inference family and claim limits are machine-readable and match implementation plan v4.

## T002 — Zhang (2025) protocol extraction

- Outputs:
  - `data/manifests/zhang_2025_replication.yaml`
  - `reports/zhang_2025_discrepancies.md`
- Status: accepted as protocol extraction; experiment remains unrun.
- Evidence: all six publisher-PDF pages were visually inspected and text-extracted. The source PDF SHA256 is recorded in the manifest.
- Decision: exact replication is currently impossible; later work must be labeled approximate replication unless missing source/split/evaluation details are obtained.

## T003 — Checkpoint provenance

- Output: `data/manifests/checkpoint_provenance.yaml`
- Status: accepted; G2 passes.
- Common provenance boundary: `2025-12-03T11:57:35Z`.
- Decision basis: exact pinned Chronos-2-small revision availability because its exact training cutoff is not documented.
- Verification: downloaded Chronos-2-small, Kronos-small and Kronos-Tokenizer-base files match the manifest SHA256 and byte size.

## T004 — Environment and mandatory TSFM smoke tests

- Outputs:
  - `pyproject.toml`
  - `uv.lock`
  - `scripts/bootstrap_kronos.ps1`
  - `scripts/verify_checkpoint_provenance.py`
  - `scripts/smoke_models.py`
  - `reports/environment.md`
- Status: accepted.
- Chronos-2-small: 128-step, four-variate input produced finite 20-step quantile forecasts.
- Kronos-small: 128-step OHLC input with explicit zero volume/amount produced finite 20-step forecasts.
- CUDA verification: PyTorch 2.14.0+cu130 detected the NVIDIA GeForce GTX 1650 and both model smoke tests passed on `cuda:0`.
- Limitation: the GPU has 4 GiB VRAM; later training and batch-size decisions require task-specific memory profiling.

## Commands verified

```powershell
uv sync --frozen --group dev
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\bootstrap_kronos.ps1
uv run python scripts\verify_checkpoint_provenance.py
uv run python scripts\smoke_models.py --model all --device cuda:0
```

## Phase 1 entry condition

Phase 1 may begin with T010. It must select and cross-check a reproducible VN30 OHLC provider before G1 can pass. No primary holdout inference is authorized until G1-G4 all pass.

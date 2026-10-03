# Phase 0 Environment and Smoke-Test Record

## Status

Phase 0 environment lock and mandatory TSFM smoke tests passed on 2026-09-26.

## Host

| Item | Value |
|---|---|
| OS | Windows |
| Python | 3.11.6 |
| uv | 0.11.2 |
| GPU detected by driver | NVIDIA GeForce GTX 1650, 4096 MiB |
| NVIDIA driver | 616.56 |
| PyTorch | 2.14.0+cu130 |
| CUDA runtime bundled with PyTorch | 13.0 |
| CUDA available to PyTorch | true |
| Smoke-test device | `cuda:0` |

## Environment lock

| Item | Value |
|---|---|
| Project lock | `uv.lock` |
| uv.lock SHA256 | `33eb1cffdbf1e3528153ce574a5ff47d06cdb51d0b6c87e7a355201fb3fc6dd3` |
| Repository HEAD at execution | `05084894fc52fcf00874f338fa9965a1514c14cb` |
| Kronos code revision | `67b630e67f6a18c9e9be918d9b4337c960db1e9a` |

Key locked packages:

| Package | Version |
|---|---|
| chronos-forecasting | 2.3.2 |
| accelerate | 1.15.0 |
| huggingface-hub | 0.33.1 |
| transformers | 4.53.3 |
| torch | 2.14.0+cu130 |
| numpy | 2.4.6 |
| pandas | 2.2.2 |
| pyarrow | 23.0.1 |
| scipy | 1.17.1 |
| scikit-learn | 1.9.1 |
| statsmodels | 0.15.0 |

`uv.lock` is authoritative for the complete transitive package set.

## Pinned model assets

| Component | Immutable revision |
|---|---|
| Chronos-2-small | `ddec01313e50b6bc58ebaa92ede81bc24a3d9f9a` |
| Kronos-small | `901c26c1332695a2a8f243eb2f37243a37bea320` |
| Kronos-Tokenizer-base | `0e0117387f39004a9016484a186a908917e22426` |

Weight SHA256 values and provenance evidence are stored in `data/manifests/checkpoint_provenance.yaml`.

## Smoke-test results

Synthetic input contained 128 valid OHLC observations. Forecast length was 20.

| Model | Input shape | Output shape | Finite | Runtime after cache |
|---|---:|---:|---:|---:|
| Chronos-2-small | 1 x 4 x 128 | 4 x 13 quantiles x 20 | yes | 1.695 s |
| Kronos-small | 128 x 6 including zero volume/amount | 20 x 6 | yes | 1.206 s |

The generated machine-readable evidence is `artifacts/smoke/phase0_model_smoke.json`. This canonical smoke artifact is tracked by the repository; rerun it from the locked environment when verification is required.

## Reproduction commands

```powershell
uv sync --frozen --group dev
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\bootstrap_kronos.ps1
uv run python scripts\verify_checkpoint_provenance.py
uv run python scripts\smoke_models.py --model all --device cuda:0
```

## Re-verification on 2026-10-01

- `uv sync --frozen --group dev --offline` completed successfully from the existing lock/cache.
- `uv lock --check` passed.
- `pytest -q` passed: 3 tests.
- Checkpoint provenance verification passed for Chronos-2-small, Kronos-small and Kronos-Tokenizer-base with exact SHA256 and byte-size matches.
- Both mandatory TSFM smoke tests passed again on `cuda:0` with finite 20-step forecasts.
- The corrected `uv.lock` SHA256 above was recomputed from both the Phase 0 commit (`38ae7e6`) and the current file; they match. The previously recorded `3e4565...` value was an evidence-metadata error.

## Phase 0 limitations carried forward

- Chronos-2-small does not document the exact pretraining cutoff for the pinned checkpoint. The exact revision's public availability is used as the conservative provenance boundary.
- The GTX 1650 has 4 GiB VRAM. Training and larger checkpoints require separate memory profiling; Phase 0 only validates small-checkpoint inference.
- Synthetic business-day timestamps only validate adapter execution. The real benchmark must use the versioned HOSE session calendar.
- Statistical, DLinear and Ridge adapters are implemented after the common model interface and walk-forward engine exist; they are not part of this external-checkpoint smoke test.

# VN30 Time-Series Forecasting

Research planning repository for forecasting VN30 Index with traditional time-series baselines, generic time-series foundation models, and K-line tokenization models such as Kronos.

## Documents

- `docs/TSFM_VN30Index_Report.md`: research report outline.
- `docs/VN30_TSFMs_Kronos_Technical_Implementation_Plan.md`: technical implementation plan.
- `docs/VN30_TSFMs_Kronos_End_to_End_Tasks.md`: executable task checklist and acceptance criteria.

## Phase 0 setup

```powershell
uv sync --group dev
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\bootstrap_kronos.ps1
uv run python scripts\verify_checkpoint_provenance.py
uv run python scripts\smoke_models.py --model all --device auto
```

Research contract and provenance manifests are under `configs/` and `data/manifests/`. Phase 0 evidence is under `reports/`.

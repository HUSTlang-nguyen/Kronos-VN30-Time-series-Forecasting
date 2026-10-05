# Core benchmark implementation

The benchmark core is planned, not implemented yet. Task ownership and acceptance criteria are in `docs/VN30_TSFMs_Kronos_End_to_End_Tasks.md`.

| Planned module | Task | Contract |
|---|---|---|
| `models/base.py` | T021 | Shared fit/observe/state/predict interface |
| `models/` adapters | T031–T033, T040–T041 | Frozen revisions/configs and common input/origin contract |
| `evaluation/walk_forward.py` | T022 | Chronological, resumable execution without future labels |
| Forecast/scored artifact modules | T023 | Atomic label-free forecasts, validated label join |
| `evaluation/metrics.py` | T024 | Declared metrics and training-only scale |
| `evaluation/bootstrap.py` | T025 | Paired origin-level inference and frozen RNG |

Agree the T021 interface and T023 artifact schema in the relevant PR before implementing multiple adapters. Phase 1 scripts remain under `scripts/` so their hash-bound audit replay is preserved.

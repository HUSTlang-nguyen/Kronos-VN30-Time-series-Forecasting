# Phase 1 processing and holdout planning

Reviewed 2026-10-02. Phase 1 remains incomplete; this report documents implementation progress, not accepted T013/T014 outputs.

Current G1 policy (explicit user amendment, 2026-10-02): research-use permission is excluded. The five required criteria are reproducible download, dates/units, independent crosscheck, resolved material discrepancies and session reconciliation. Validation after the amendment: 34 tests passed. Remaining blockers in this report refer to quality/calendar evidence, not permission. Historical permission-related statements below describe the previous policy.

`scripts/freeze_phase1.py` now orchestrates immutable snapshot copies, processed data, calendar, split/origin/feasibility manifests and a final hash receipt. It requires reviewed hash-bound source/calendar acceptance, refuses pending inputs and existing outputs, and provides read-only `--verify`. The end-to-end test uses synthetic temporary inputs only. Actual project configuration remains pending. Input/output contract: `docs/Phase1_Freeze_Runbook.md`.

## Implemented primitives

`scripts/phase1_pipeline.py` validates explicit unique sorted local dates, finite positive OHLC, OHLC inequalities and exact observed-session coverage. Processing rejects unresolved failures and requires both source and calendar acceptance. It never sorts an invalid input, deletes a row, interpolates a missing session or combines providers.

Declared features are computed from current/past observations only:

- `log_close = log(close)`
- `return_1d = close / previous_close - 1`
- `log_return_1d = log_close - previous_log_close`
- `range_abs = high - low`, `range_pct = range_abs / close`
- `body_abs = abs(close - open)`, `body_pct = body_abs / open`

Here `pct` denotes a ratio, not a value multiplied by 100. The first return remains undefined and is flagged. Absolute daily returns over 10% are flagged for review, retained without correction; this is a quality-review threshold, not a selection rule. Provider identifiers and optional trade value are retained. No volume or technical indicators are fabricated.

Temporal splitting excludes the local day containing provenance boundary B, uses the first 63 subsequent sessions as validation targets and the remaining sessions as test targets. Every origin has 128 observed context rows and a full 20-session target path inside its partition. The first test origin is the last validation session. One full-path origin set is shared across h=1/5/20.

## Candidate feasibility, without model outcomes

`scripts/audit_holdout_feasibility.py` verified the captured VCI response hash and official calendar PDF hashes, then used the overlap with the candidate 2025-2026 calendar strictly for planning. It did not truncate or accept the full historical research dataset.

| Item | Candidate result |
|---|---|
| Provenance boundary B | 2025-12-03T11:57:35Z |
| Data freeze | 2026-10-01 |
| Eligible target sessions | 203 |
| Validation targets | 2025-12-04 through 2026-03-11; 63 sessions |
| Full-path validation origins | 44 |
| Test targets | 2026-03-12 through 2026-10-01; 140 sessions |
| Full-path test origins | 121 |
| First / last test origin | 2026-03-11 / 2026-09-03 |
| Required test origins | 126 |
| Earliest projected freeze | 2026-10-08 |

The count uses 63 validation targets + 126 origins + 19 trailing target sessions = 208 eligible sessions. The current 203 eligible sessions are five short. The projection assumes scheduled sessions occur and their valid data become available. It is not a commitment to complete on 8 October and must be recomputed from the accepted realized calendar and snapshot.

Tracked evidence: `artifacts/source_audit/vnstock_20261001T154235115506Z/candidate_holdout_feasibility.json`. This file records provenance/config/source hashes and explicitly sets `inference_allowed: false`. No forecasts, losses or test scores are included.

## Verification and outstanding work

Latest code verification: 29 tests passed. Complete signed annual evidence is captured separately for 2019 and 2022-2026. The 2018 candidate has 248 sessions and incomplete announcement/exception documentation; 2020 is a cross-exchange diagnostic and 2021 has partial evidence only. The 2018/2019 calendars reconcile cleanly with VPS/VNDIRECT; DNSE has no returned history in those years. The 2023 reconciliation identifies missing DNSE session 2023-04-07; the 2022 and updated 2024 calendars reconcile cleanly with all three original providers. Full historical calendar coverage and investigation remain incomplete.

Shortened-session annotations now propagate from `build_hose_calendar.py` through `process()` and the freeze into `quality_flags` and the quality report. They preserve existing flags, all prices, dates and derived features. Closed-day annotations, unknown flags and missing event-source identifiers are rejected. This implementation does not accept the incomplete real 2021 calendar; end-to-end validation uses synthetic inputs only. Earlier immutable candidate artifacts retain their original code hashes; create a new output directory when rebuilding under a changed script revision.

Tests cover gate refusal, invalid OHLC, missing/unsorted dates, preservation of suspicious observations, future-mutation invariance, exact 125/126-origin boundaries, full-path target ordering and insufficient context. Candidate planning replay reproduces the persisted artifact.

G1 remains pending; the calendar remains a candidate. No accepted `vn30_daily.parquet`, `dataset.yaml`, `splits.yaml`, `common_origins.parquet` or final `holdout_feasibility.json` has been generated. Source discrepancy resolution, historical calendar coverage and data-use evidence still precede accepted pipeline execution. The implemented orchestration can persist and verify final outputs once accepted inputs exist; implementation/tests alone do not complete T011-T014.

Commands:

```powershell
.venv/Scripts/python.exe scripts/audit_holdout_feasibility.py
.venv/Scripts/python.exe -m pytest -q
```

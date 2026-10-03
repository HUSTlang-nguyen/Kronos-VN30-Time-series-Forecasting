# Phase 1 freeze command

The implementation is ready for accepted inputs. Current project inputs are **pending**. This runbook does not accept a provider, clear G1, or replace the historical calendar review.

```powershell
.venv/Scripts/python.exe scripts/freeze_phase1.py
.venv/Scripts/python.exe scripts/freeze_phase1.py --verify
```

The first command reads `configs/phase1_inputs.yaml`. Its current pending status must cause exit code 1 before any accepted outputs are written. The second command verifies an existing completed freeze receipt; it cannot create or accept a dataset.

## Input contract

When evidence has actually passed review, provide a YAML spec with the following fields. Every file reference is `{path: <project-relative path>, sha256: <64-character SHA256>}`. Files outside the project are rejected.

| Field | Requirement |
|---|---|
| `status` | `accepted_inputs`, only after actual evidence review |
| `source_acceptance` | Hash-bound source acceptance YAML described below |
| `raw_csv` | Exact immutable daily CSV, explicit sorted local `date`, OHLC in index points |
| `original_responses` | Nonempty list of hash-bound unchanged original HTTP response captures |
| `calendar` | Hash-bound Parquet with every date in coverage and boolean `is_session` |
| `calendar_manifest` | Hash-bound accepted calendar manifest including exceptional closure review |
| `checkpoint_provenance` | Existing accepted Phase 0 provenance manifest |
| `study` | Frozen research contract, 128 context and 20 target sessions |
| `freeze` | Local date `YYYY-MM-DD`, covered by calendar and realized observations |
| `retrieved_at_utc` | Timezone-aware retrieval timestamp, no earlier than freeze date |

The source acceptance YAML needs `status: accepted`, a safe lowercase `provider` identifier, `units: index_points`, `raw_csv_sha256`, `crosschecked_dates >= 30`, `extreme_return_dates_reviewed >= 1`, and `unresolved_material_discrepancies: 0`. Its `criteria` must include exactly:

```text
reproducible_download
dates_and_units
independent_crosscheck
material_discrepancies_resolved
session_reconciliation
```

Each criterion requires `status: pass`, a nonempty `review_note`, and a hash-bound local `evidence` file. These records document actual review; changing a label is not proof that a criterion passed. The program verifies identities and mandatory fields, not the substantive truth of a research conclusion.

As requested by the user on 2026-10-02, `research_use` is excluded from G1 and must not appear in the five-criterion acceptance mapping. The freeze receipt records this policy amendment; it does not assert that permission was verified. Existing hash-bound audit configurations and captures retain their historical permission metadata for replay, which is no longer a gate requirement.

The calendar manifest requires `status: accepted`, `calendar_sha256`, `exceptional_closures_reviewed: true`, and a nonempty `sources` list of hash-bound captured official/reproducible source files. Missing years or exceptional closure checks must not be marked accepted to make the command run.

For reviewed shortened sessions, calendar-builder inputs can include `session_events` with `date`, `quality_flag: shortened_session` and a declared `source`. The builder emits `session_quality_flag` and `event_source`; the freeze requires nonempty event-source identifiers and carries the flag into processed observations and the quality report. A shortened session remains a trading date. An annotation does not change prices, derived features or origin eligibility, and is never a model input feature.

## Output and integrity

After all input/quality/split checks pass, the command stages and publishes:

- `data/raw/vn30/<provider>/<UTC retrieval day>/vn30_daily.csv`, unchanged byte copy, adjacent snapshot manifest and unchanged original response captures.
- `data/manifests/hose_sessions.parquet` and `hose_calendar.yaml`.
- `data/processed/vn30_daily.parquet`, `data/manifests/dataset.yaml` and `reports/data_quality.json`.
- `data/manifests/common_origins.parquet`, `splits.yaml` and `holdout_feasibility.json`.
- `data/manifests/phase1_freeze.yaml`, written last, binding every output hash.

The CSV is explicitly identified as an unchanged **normalized provider snapshot**, not falsely described as original HTTP bytes. Original HTTP bodies are retained separately. No row repair, deletion, sorting, data splice or interpolation occurs. Suspicious return flags remain attached to observations.

The freeze refuses existing target files. An interrupted publication may leave files without a completed receipt; that state is incomplete and requires investigation, not automatic overwrite. `--verify` checks every receipt-bound file and rejects hash mismatches. Snapshot, dataset and code hashes are recorded for reproducibility.

If fewer than 126 full-path test origins are available, the frozen split is labeled `exploratory_pilot`. This is allowed only after source/calendar acceptance and does not relax the confirmatory threshold. No model inference or metrics are part of this command. G4 and benchmark execution remain subsequent responsibilities.

## Current evidence

Source/calendar acceptance is unfinished. The candidate projection through 2026-10-01 has 121 full-path test origins and estimates 2026-10-08 for 126 origins. These dates come from unaccepted candidate inputs and must be recomputed after G1/T012 pass. See `reports/vnstock_source_audit.md`, `reports/hose_calendar_review.md` and `reports/phase1_pipeline_progress.md`.

Tests run the complete freeze only in pytest temporary directories with synthetic inputs. They do not produce or validate accepted project research artifacts.

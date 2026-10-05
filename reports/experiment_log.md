# Experiment log

## 2026-10-01: 2024 holiday evidence

Captured and visually inspected signed annual HOSE 1943 and update 905 from public mirrors. Preserved bytes/hashes in the 2024 calendar evidence manifest. Built 250-session candidate calendar; all three original providers have no missing, duplicate or non-session dates for 2024. Added regression coverage for 29 April closure and 4 May non-trading makeup Saturday; 25 tests pass. No G1 acceptance or model evaluation performed.

## 2026-10-01 - Historical calendar chronology

Retrieved and visually verified the complete mirrored signed HOSE 2208/TB-SGDHCM notice for 2023. Stored exact scan hash and declared holiday ranges separately from the existing 2025-2026 config. The older official VSD settlement page lists conflicting September dates; preserved its HTML and documented why it cannot define HOSE sessions. Found 2022/2024 annual PDF candidates and a 2024 calendar update, but direct mirror downloads returned 403; no full capture/visual verification or accepted coverage is claimed for those years. Report: `reports/historical_calendar_discovery.md`. T012 and G1 remain pending.

## 2026-10-01 - End-to-end freeze orchestration

Implemented `scripts/freeze_phase1.py` with input evidence hashes, G1/calendar checks, immutable snapshot copying, processed/calendar/split/origin manifests and a receipt published last. Read-only verification checks every output hash. The complete synthetic-input test verifies exact CSV preservation, 126 test origins, overwrite refusal and tamper detection. `configs/phase1_inputs.yaml` remains pending; actual execution must refuse before creating accepted project outputs. Runbook: `docs/Phase1_Freeze_Runbook.md`. G1/T012 acceptance and real deliverables remain incomplete.

## 2026-10-01 - Processing primitives and holdout feasibility

Added strict data-quality/feature and temporal-split primitives plus planning-only feasibility capture. Using the hash-verified VCI response and candidate calendar, data through 2026-10-01 yields 203 eligible target sessions, 44 validation origins and 121 full-path test origins. Scheduled projection reaches 126 origins on 2026-10-08. This is not G3 acceptance: G1/calendar remain pending and no benchmark inference is allowed. No accepted dataset/split/origin artifacts created. Report: `reports/phase1_pipeline_progress.md`.

## 2026-10-01 - vnstock KBS/VCI audit

Installed vnstock 4.0.9 and vnai 2.6.2 in `tmp/vnstock-env` from the documented Vnstock index after PyPI resolution failed. Main CUDA dependencies unchanged. Captured run `20261001T154235115506Z`: KBS 3575 rows, VCI 3656 rows. Full requested history not established: KBS starts June 2012; VCI reaches launch date but has 60 historical OHLC violations, KBS has 28. Direct offline reconstruction matches normalized OHLC. Candidate-calendar reconciliation passes for 2025 onward. Common-interval comparison ends 2026-09-30 to avoid treating the older requests' excluded 2026-10-01 as missing. Raw data retained without repair. Report: `reports/vnstock_source_audit.md`. G1 pending.

## 2026-10-01 - Narrow-window anomaly investigation

Captured independent narrow-window endpoint requests at `data/raw/source_investigation/20261001T153102558007Z/`; hashes and request URLs preserved. Offline replay verified all response hashes and reproduced the findings. DNSE still omits 2025-04-03, which the official HOSE trading summary confirms traded (VN30 close 1283.18). VPS reproduces conflicting duplicate OHLC; original audit has 26 duplicate dates, 25 conflicting and one identical. Evidence: `reports/source_anomaly_investigation.md` and matching tracked source-audit summary. No raw patch or G1 acceptance. Eleven tests pass.

## 2026-10-01 — T010 source audit continuation

Status: audit infrastructure and retrieval completed; source acceptance pending.

Code base: `411b830272ebf96579c134f72e2b23b1ebf1c443`; working tree dirty, including the earlier Phase 0 re-verification changes.

The previous VPS-primary audit remains exploratory. It is preserved at `data/manifests/source_crosscheck.parquet` and `artifacts/source_audit/retrieval.json`; it has not been relabeled as accepted evidence.

New criteria: `configs/data_source_acceptance.yaml`, SHA256 `9e3f4a865d35e9c0b35635f43d5891ba9baff45b5675c0d790a4f9bd0ba4f363`.

New evidence run: `20261001T151513588605Z`. Exact raw responses are retained under `data/raw/source_audit/`; comparison, anomaly and summary artifacts are under the matching `artifacts/source_audit/` run directory. Retrieval identities and script/config hashes are in `summary.json`.

Commands: `uv run --no-sync python scripts/validate_vn30_sources.py`, followed by the same command with `--replay data/raw/source_audit/20261001T151513588605Z`, then `uv run --no-sync pytest -q`.

Outcome: raw-hash verification and offline replay passed. No provider accepted: 55 field discrepancies, VPS duplicates/invalid candles, research permission and session reconciliation remain unresolved. `reports/data_source_acceptance.md` records criteria, observations and remaining requirements; `reports/source_discrepancies.md` lists material discrepancies.

No model forecasts or final-test metrics were generated. No T011–T014 acceptance or G1/G3/G4 pass is claimed.
# Calendar evidence review - 2026-10-01

## G1 policy amendment — 2026-10-02

The user explicitly requested removal of the research-use permission criterion and continuation of Phase 1. Updated implementation plan Section 5.4, T010 checklist, freeze runbook, pending input spec and freeze validator accordingly. G1 now requires five quality/reproducibility criteria. Future freeze receipts record the excluded criterion and required criteria. Historical hash-bound source-audit configs/captures remain unchanged for replay; their permission metadata is not a current acceptance requirement. No grant of permission is inferred.

Validation: 34 tests passed, including successful synthetic freeze without research-use evidence and rejection of each of the five remaining unresolved criteria. Real project G1 remains pending due to quality/discrepancy/calendar evidence; no accepted dataset is created solely by this amendment.

Visually inspected HOSE notices 2079 (2025), 2294 (2026 annual, mirrored signed scan) and 2410 (2026 New Year update). Stored local raw PDFs with SHA256 references in `data/manifests/hose_calendar_evidence.yaml`. Built `artifacts/source_audit/calendar_2025_2026/candidate_days.parquet`; candidate only, exceptional closures not yet reviewed. Reconciliation through 2026-09-30 found DNSE missing 2025-04-03, VPS with 25 duplicate dates, and VNDIRECT with no date discrepancies inside this interval. No accepted dataset, calendar or split was created. Details: `reports/hose_calendar_review.md`.

## Contributor setup update - 2026-10-05

Infrastructure evidence is recorded in reports/contributor_setup_validation.md. VNDIRECT candidate ZIP/SQLite receipts identify the contributor snapshot; G1 and accepted dataset/splits remain pending. No primary holdout run is introduced by this setup update.

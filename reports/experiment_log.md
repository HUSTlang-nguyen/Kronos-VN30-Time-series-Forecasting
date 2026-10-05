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

Infrastructure evidence is recorded in reports/collaborator_setup_validation.md. VNDIRECT candidate ZIP/SQLite receipts identify the contributor snapshot; G1 and accepted dataset/splits remain pending. No primary holdout run is introduced by this setup update.

## Selected-source T010/T012 execution — 2026-10-05

Fresh run `20261005T084027989272Z` uses `configs/vndirect_source_audit.yaml`, selected interval 2017-08-24–2026-10-02 and pre-rerun absolute 0.02-point OHLC tolerances. VNDIRECT has 2,272 strictly ordered unique rows, no structural/numeric/outside-request anomalies, and no date discrepancies against the combined candidate calendar. VPS comparisons cover 50 seeded year-stratified dates plus extremes (59 total); DNSE covers 35 seeded dates plus extremes (49 total). There are 39 selected-source material field discrepancies and 16 missing comparison fields; independent upstream lineage is unverified. Exact historical raw captures are retained without price repair or provider splicing.

New 2021 HOSE-attributed holiday-table capture corroborates the earlier diagnostic calendar but does not replace the missing original notice or exception review. Supplemental MBS/Pinetree evidence corroborates VNDIRECT's 2022-11-09 Close only. Combined review and source bindings: `artifacts/source_audit/vndirect_review_20261005_v2/`, `data/manifests/hose_calendar_2021_selected_evidence.yaml`, `data/manifests/vndirect_close_20221109_evidence.yaml`. Detailed outcomes and replay commands: `reports/vndirect_T010_T012_review.md`.

Validation: 45 tests passed in the isolated data environment, including six new tests for tamper rejection, immutable output, duplicate-safe capture drift, incomplete crosschecks and coverage-scoped calendar/shortened-session preservation. T009 now records successful remote CI run 37282168003 for the previous commit `6f0d6a7`; that CI result does not cover these new changes. G1/T012 and accepted Phase 1 outputs remain pending; no model inference or final-test metrics were generated.

## All 39 discrepancies and baseline review — 2026-10-05

Investigated all 39 fields on 30 dates from the registered rerun. Reconstructed hash-verified KBS/VCI raw and normalized captures; annual-window repeat requests to VNDIRECT/VPS/DNSE retained every disputed field. KBS repeat covered the latest case; VCI returned a retained HTTP 403 response. Independent publication review rendered full page 1 of four contemporary PDFs supporting VNDIRECT Close on 2020-06-18, 2020-07-15, 2021-03-05 and 2022-10-26. All 35 O/H/L fields remain unadjudicated and root causes remain unknown. Additional diagnosis: VNDIRECT Open equals previous Close on 71 consecutive observed sessions, 2025-05-05–2025-08-11; this is a feed/construction question, not permission to repair prices.

Artifacts: `artifacts/source_audit/vndirect_39_cases_20261005/`, `configs/vndirect_discrepancy_investigation.yaml`, `data/manifests/vndirect_39_publications_evidence.yaml`, `reports/vndirect_39_discrepancy_review.md`. Raw repeats are in `data/raw/source_investigation/20261005_39_repeat/`. Exact case/candle summary replay passed; hashes were verified. Supplemental monthly Open diagnosis is outside the registered comparison population. Raw old vnstock manifest lacks config hash and its historical capture-script hash differs from current code; current normalization config/code are pinned explicitly, and no complete historical-code identity claim is made.

Reviewed the four supplied references using primary publisher/author sources. Full PDFs read for Nguyen–Paientko and Do–Nguyen; only primary abstracts/metadata available for Dao and LSTM–Ichimoku. Proposed daily ARIMA E0 amendment and conditional KTPCA extension are recorded in `reports/vn30_baseline_literature_review.md` with source receipt `data/manifests/vn30_baseline_review_evidence.yaml`. Study v4 and baseline task contracts remain unchanged; no ranking/indexing claim or model score is inferred.

Validation: `tmp/ci-data-env/Scripts/python.exe -B -m pytest -q -p no:cacheprovider` — **49 passed**. Four new tests reject ambiguous/invalid corroborating candles, distinguish Close evidence from H/L evidence, and refuse majority decisions for conflicting publications. Offline replay passed. Remote CI still refers to the earlier pushed commit; no new commit/push or accepted dataset, calendar, split, inference or final-test score was produced.

## Documentation publication preparation — 2026-10-05

Synchronized README, contributor/data/Docker/freeze guides, shared-data notes, implementation-plan execution status, research report, task checklist and acceptance reports with the T010/T012 and complete 39-field investigation. Literature changes remain proposals; the v4 study and Zhang E0 contract are preserved. Shared snapshot bytes/receipts and historical raw/config/parser evidence remain unchanged. New reports/configs/scripts/tests and compact diagnostic artifacts are included for publication; raw/PDF/runtime directories remain ignored.

Pre-publication checks against the local working tree based on `6f0d6a7`: 49 tests passed; locked data dependency export matched; shared SQLite/ZIP verified; all three offline replays matched persisted artifacts. Remote CI for the publication must be identified by its actual pushed commit rather than attributed to the earlier run. Publication commit identities are available in Git history.

## T006 — DVC/Google Drive migration preparation — 2026-10-06

Working tree based on `e8527db`; no migration commit/push yet. Created three DVC pointers for all 87 raw files and the unchanged SQLite/ZIP candidate snapshots. Removed binary files only from the Git index; preserved local bytes and scientific receipts. Configured the user-provided team Drive folder, updated contributor/data/Docker/freeze documentation and added a synthetic DVC CI roundtrip check. DVC is an isolated uv tool, leaving research lock/CUDA dependencies unchanged.

Validation: 52 unit tests pass; synthetic upload, empty-cache download and two-version historical restore pass. Actual-data local remote upload/restoration also verified all 89 file SHA256 hashes and both scientific snapshot receipts with a fresh cache. Dependency export, Compose configuration, DVC status and diff checks pass. Initial pyOpenSSL incompatibility was resolved with the tool pin. The user reported default Google OAuth blocked; upload/Drive recovery remain pending the team's Desktop client. T006 remote sharing and CI for this revision remain unchecked. No G1/G3/G4 acceptance or research results are claimed. Details: `reports/dvc_migration_validation.md`.

## T006 — Google Drive upload and recovery verified — 2026-10-06

The user configured the custom Desktop OAuth client locally and completed Google sign-in. `dvc push -r team` exited 0: 89 files pushed. A separate temporary workspace/cache pulled all 89 files from the team Drive; each SHA256 matched the original, and both SQLite/ZIP receipts verified the unchanged 2,271-row candidate. Logical file size: 22,475,925 bytes. Evidence: `data/manifests/dvc_drive_verification.json`. Credentials remain excluded from Git; source bytes remain local and the temporary restore was cleaned up. Updated README/data/plan/checklist/validation documents to record successful Drive upload and recovery. Git migration publication, its CI and independent Viewer verification remain pending; no research gate or data acceptance changed.

## Research collaborator workflow clarification — 2026-10-06

Updated active documentation to describe peers collaborating on the research: shared GitHub repository with Write access and branch/PR review, task ownership/reviewer coordination, separate Drive/OAuth permissions, reproducible local processing and versioned output sharing. Collaborators responsible for data work can publish new DVC versions with Editor access after validation and review; this role is not restricted to a fixed maintainer. Canonical data guide: `docs/Collaborator_Data_Guide.md`; the previous URL redirects for historical links. Existing script/test/receipt names are retained for compatibility. No cloud permissions, dataset bytes, research gates or published Git state were changed by this documentation update.

## Collaborator filenames and public-data clarification — 2026-10-06

At the user's explicit request, renamed `CONTRIBUTING.md` to `COLLABORATING.md`, the setup report to `reports/collaborator_setup_validation.md`, the snapshot test to `tests/test_collaborator_snapshot.py`, and the ZIP receipt to `data/manifests/vndirect_collaborator_snapshot.json`; removed the old guide redirect now that `docs/Collaborator_Data_Guide.md` is canonical. Updated live links and executable receipt defaults. ZIP receipt contents and SQLite/ZIP/raw bytes remain unchanged.

Verified via GitHub API that the repository is public and its current `main` still contains the old SQLite/ZIP binaries. Documented that public DVC hashes/pointers do not grant private Drive access, while actual data already committed to public Git is directly downloadable and remains in history after a normal deletion commit. No visibility, Drive sharing or history rewrite was performed.

## DVC/collaborator migration publication — 2026-10-06

Publication revision is the commit containing this entry. Versions the three DVC pointers, verified Drive receipt, isolated tooling/CI check, renamed collaborator guides/report/test/ZIP receipt, and research collaboration workflow. Removes SQLite/ZIP bytes from the current Git tree while retaining local data and public Git history. Research gates, data prices and CUDA lock are unchanged. Pre-publication evidence: 52 unit tests, both snapshot formats verified, local DVC roundtrip, Drive roundtrip of 89 files, portable pointer hashes and local Markdown links. Actual remote CI must be recorded against this commit after push; another collaborator's account/access verification remains pending.

## Published migration CI verified — 2026-10-06

Migration commit `f56cfc8c2d2e6ada1995d0d5a8e136c16da00ff0` is on `origin/main`. Fresh local clone passes 52 tests and the dependency-lock check; credentials/data binaries are absent and all three pointer SHA256 values match the Drive verification receipt. GitHub run 37351516675 passed Windows tests, Ubuntu tests, Docker data build/tests and `dvc-local`. Updated T009 and validation reports with that exact commit/run evidence. T006's separate collaborator-account access verification remains pending; no research gate changed.

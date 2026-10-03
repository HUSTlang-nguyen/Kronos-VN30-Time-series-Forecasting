# VN30 TSFM/Kronos — End-to-End Task Checklist

**Source of truth:** `docs/VN30_TSFMs_Kronos_Technical_Implementation_Plan.md` v4  
**Scope:** VN30 daily OHLC, horizons 1/5/20, mandatory zero-shot benchmark  
**Primary endpoint:** pooled Close MAE at h=1  
**Primary comparison:** Kronos-small vs Naive and frozen generic multivariate TSFM  

## 1. Usage rules

- `[ ]` pending; `[x]` accepted; add `BLOCKED:` after the task title when blocked.
- A task is complete only when its output exists, its acceptance checks pass and the evidence path is recorded.
- Do not inspect final test metrics before G4 is frozen.
- Do not change data cleaning, origins, models, context, sampling or selection rules from test results.
- Keep mandatory, secondary and optional work separate. Optional work cannot delay the core benchmark.
- Record deviations in `reports/experiment_log.md`; never silently replace a model, dataset or configuration.

## 2. Required gates

| Gate | Requirement | Evidence | Status |
|---|---|---|---|
| G1 | Reproducible VN30 OHLC source passes the data-source acceptance checks | data-source report, cross-check table, calendar reconciliation | [ ] |
| G2 | Exact model/tokenizer revisions and provenance boundary are recorded | checkpoint provenance manifest with evidence URLs | [x] |
| G3 | At least 126 common full-path test origins exist after the provenance boundary | `data/manifests/holdout_feasibility.json` | [ ] |
| G4 | Configs, calendar and origin manifest are frozen before test inference | immutable hashes and freeze record | [ ] |

If G2 or G3 fails, outputs must be labeled `exploratory_pilot`. If G1 fails, stop the Kronos benchmark. G4 must pass before any primary holdout run.

## 3. Phase 0 — Research contract and environment

### T001 — Freeze the research contract

- [x] Copy the primary question, hypotheses, endpoint, mandatory models and point functional into a machine-readable study manifest.
- Depends on: none.
- Output: `configs/study.yaml`.
- Acceptance:
  - Primary metric is `close_mae_h1`.
  - Primary comparisons are Kronos-small vs Naive and Kronos-small vs the frozen generic multivariate TSFM.
  - Point functional is median for sampled/quantile TSFMs.
  - Mandatory/secondary/optional scopes match Sections 0.2 and 34 of the plan.
- Plan reference: Sections 0, 9, 34.

### T002 — Extract the Zhang (2025) replication protocol

- [x] Read the complete paper and fill every replication field; use `not reported` instead of guessing.
- [x] Record conflicts between abstract, tables and conclusion.
- Depends on: T001.
- Outputs:
  - `data/manifests/zhang_2025_replication.yaml`
  - `reports/zhang_2025_discrepancies.md`
- Acceptance: data period, source, split, ARIMA order, ETS specification, metric formulas and reported results are either sourced or marked `not reported`.
- Plan reference: Sections 3, 30 Phase 2.

### T003 — Audit checkpoint and tokenizer provenance

- [x] Resolve immutable revisions for Chronos-2-small, Kronos-small and Kronos-Tokenizer-base.
- [x] Record first public availability, documented training cutoff, evidence URL and eligibility status for each revision.
- [x] Select the latest acceptable common provenance boundary `B` without using model performance.
- Depends on: T001.
- Output: `data/manifests/checkpoint_provenance.yaml`.
- Acceptance: mutable branch names such as `main` are absent from executable configs; each checkpoint and tokenizer uses an immutable revision.
- Gate: G2.
- Plan reference: Sections 0.3, 8.2, 13, 14, 32 Gate D0.

### T004 — Lock the software environment and smoke-test adapters

- [x] Create `pyproject.toml` and an exact dependency lock.
- [x] Record Python, PyTorch, CUDA and required package versions.
- [x] Load both externally sourced mandatory TSFMs at immutable revisions.
- [x] Produce one valid 20-step dummy forecast from each mandatory TSFM adapter. Statistical and train-from-scratch adapters are implemented and validated in Phases 2-3.
- Depends on: T003.
- Outputs:
  - dependency lock
  - `reports/environment.md`
  - adapter smoke-test artifacts
- Acceptance: environment rebuild succeeds and both TSFM adapters return a 20-step finite multivariate forecast; remaining mandatory adapters follow the unified contract tests in T021 and their implementation tasks.
- Plan reference: Sections 23, 29, 30 Phase 0.

## 4. Phase 1 — Data acquisition and immutable manifests

### T010 — Select and validate a VN30 OHLC provider

Progress 2026-10-02 (complete anomaly review): hash-verified raw responses from all five tested providers; assembled 440 unchanged candles across all 119 dates with invalid OHLC or duplicate rows. All 100 invalid OHLC rows and 52 duplicate VPS rows remain retained. Immutable replay passed. This investigation table is not an accepted dataset or source-selection decision. Evidence: `artifacts/source_audit/anomaly_review_20261002/`, `scripts/build_anomaly_review.py`.

Policy amendment 2026-10-02: research-use permission excluded from G1 by explicit user request. Earlier permission-related progress notes describe the old policy. Source quality, discrepancy resolution and calendar reconciliation remain required; G1 is still pending.

Progress 2026-10-01 (vnstock): KBS and VCI retrieved in an isolated, version-frozen environment. VCI reaches 2012-02-06, KBS starts 2012-06-01. Unchanged HTTP bytes and normalized snapshots preserved; offline reconstruction verified. Both cover candidate calendar sessions in 2025-2026 but have unresolved historical OHLC violations (28 KBS, 60 VCI). See `reports/vnstock_source_audit.md`. G1 remains pending.

Progress 2026-10-01: replayable three-provider audit completed. Acceptance remains pending: material discrepancies, provider permission and exchange-session reconciliation require resolution. Evidence: `reports/data_source_acceptance.md`, `reports/source_discrepancies.md`, `data/manifests/source_investigation.yaml` and `artifacts/source_audit/20261001T151513588605Z/`. The earlier `source_crosscheck.parquet` remains exploratory; it has not been replaced or accepted as G1 evidence.

- [ ] Confirm reproducible daily OHLC download, explicit dates and consistent units.
- [ ] Cross-check at least 30 year-stratified observations plus extreme-return dates against an independent source.
- [ ] Define field-level numeric tolerances before cross-checking.
- [ ] Investigate every material discrepancy.
- Depends on: T001.
- Outputs:
  - `reports/data_source_acceptance.md`
  - `data/manifests/source_crosscheck.parquet`
- Acceptance: every criterion in Section 5.4 passes.
- Gate: G1.
- Plan reference: Sections 5.3–5.4, 32 Gate A.

### T011 — Freeze the raw data snapshot

Progress 2026-10-01: `scripts/freeze_phase1.py` implements byte-preserving snapshot/response copies and hash-bound metadata; end-to-end behavior verified using synthetic temporary inputs. Actual accepted snapshot remains pending G1. Runbook: `docs/Phase1_Freeze_Runbook.md`.

- [ ] Download VN30 daily OHLC without modifying the provider response.
- [ ] Save retrieval timestamp, source identifier, schema, row count, minimum/maximum date and SHA256.
- Depends on: T010.
- Outputs:
  - `data/raw/vn30/<provider>/<retrieval_date>/vn30_daily.csv`
  - adjacent raw-data manifest
- Acceptance: rerunning validation against the snapshot reproduces its hash and metadata; the raw file is never overwritten.
- Plan reference: Section 5.5.

### T012 — Build and version the HOSE session calendar

Progress 2026-10-02 (2014 partial): captured SHS/Asean broker notices and BMSC's earlier HNX table. Recorded conflicting holiday intervals, the SHS Friday date listed among Saturdays, and Asean's title/body year mismatch. No annual coverage inferred. Evidence: `data/manifests/hose_2014_partial_holiday_evidence.yaml`.

Progress 2026-10-02 (2015 partial): preserved and text-reviewed SHS New Year notice covering January 1-2, reopening January 5. This prevents a January-1-only assumption but does not establish annual HOSE coverage. Remaining holiday/exception evidence remains pending. Evidence: `data/manifests/hose_2015_partial_holiday_evidence.yaml`.

Progress 2026-10-02 (2016 diagnostic): captured and text-reviewed HNX annual notice. The 251-session hypothesis reconciles cleanly with VPS; VNDIRECT/DNSE have no returned history for 2016. Direct HOSE annual confirmation, exceptional-closure review and acceptance remain pending. Evidence: `data/manifests/calendar_2016_cross_exchange_evidence.yaml`, `artifacts/source_audit/calendar_2016_cross_exchange/`.

Progress 2026-10-02 (2017): captured and visually inspected complete HOSE update 1241, replacing notice 625. Tet closure is January 26-February 1; conflicting HNX January 27-February 2 dates are preserved but not applied. Candidate has 250 sessions; VPS reconciles cleanly, VNDIRECT lacks pre-August-24 coverage and DNSE has no history that year. The PDF has a typed signatory but no visible signature/stamp. Exceptional-closure review and acceptance remain pending. Evidence: `data/manifests/hose_calendar_2017_evidence.yaml`, `artifacts/source_audit/calendar_2017/`.

Progress 2026-10-02 (2021 diagnostic): captured and text-reviewed HNX annual notice; diagnostic calendar has 250 sessions and retains June 1 as shortened. VPS/VNDIRECT dates reconcile cleanly; DNSE lacks 15 diagnostic dates, eleven reproduced in a new January/February request. Direct HOSE annual/session confirmation remains pending. Evidence: `data/manifests/calendar_2021_cross_exchange_evidence.yaml`, `artifacts/source_audit/calendar_2021_cross_exchange/`, `artifacts/source_audit/investigation_20261001T173314028636Z/`.

Progress 2026-10-02 (2018 candidate): captured and visually inspected a cropped HOSE holiday table, combined with the signed 2019 notice's December 31 closure and an HNX retrospective of the January interruption. Candidate has 248 sessions; January 22 is retained with a shortened-session flag, January 23-24 are closed. VPS/VNDIRECT dates reconcile cleanly. Complete annual notice and primary HOSE exception documentation remain pending. Evidence: `data/manifests/hose_calendar_2018_evidence.yaml`, `artifacts/source_audit/calendar_2018/`. Latest regression suite: 29 tests passed.

Progress 2026-10-02 (2020 diagnostic): captured HNX annual and KIS/SSI holiday notices; a 252-session hypothesis identifies 16 DNSE omissions within returned history, five reproduced in a fresh May request. Direct HOSE annual/session confirmation remains pending; this diagnostic does not extend verified HOSE coverage. See `reports/historical_calendar_discovery.md` and `data/manifests/calendar_2020_cross_exchange_evidence.yaml`.

Progress 2026-10-02 (2019): signed HOSE annual notice 1108 captured and visually inspected. Candidate has 250 sessions; VPS/VNDIRECT reconcile cleanly, while DNSE has no history in 2019. Candidate annual coverage is 2019 plus 2022-2026; intervening years are not inferred. Evidence: `data/manifests/hose_calendar_2019_evidence.yaml`, `artifacts/source_audit/calendar_2019/`.

Progress 2026-10-02: investigated the 2021-06-01 afternoon halt. Preserve it as a shortened trading session, not a full-day closure; all original providers contain one agreeing candle. Captured HOSE director's statement and source limitations are in `data/manifests/hose_session_exceptions.yaml`. Full 2021 calendar and propagation of event flags into accepted artifacts remain pending.

Progress 2026-10-01 (2022): signed HOSE notice 2168 captured and visually inspected; signed issue date is December 21, 2021 despite mirror filename December 22. Candidate calendar has 249 sessions; all original providers reconcile without date anomalies. Candidate annual coverage is now 2022-2026; 2012-2021 and exceptional-closure review remain pending. Evidence: `data/manifests/hose_calendar_2022_evidence.yaml`, `artifacts/source_audit/calendar_2022/`.

Progress 2026-10-01 (2024): both signed HOSE annual/update notices captured, hash-bound and visually inspected. The updated candidate calendar has 250 sessions; all three original providers reconcile without date anomalies in 2024. Remaining historical years and exceptional closures still require review. Evidence: `data/manifests/hose_calendar_2024_evidence.yaml`, `artifacts/source_audit/calendar_2024/`.

Progress 2026-10-01 (historical evidence): captured and visually inspected the signed HOSE 2023 notice; candidate calendar has 249 sessions. VPS/VNDIRECT reconcile cleanly in that year; DNSE lacks 2023-04-07. The later HOSE notice supersedes conflicting dates in the older VSD settlement schedule. 2022/2024 captures and historical exceptional-closure review remain pending. See `reports/historical_calendar_discovery.md`.

Progress 2026-10-01: hash-verified, visually inspected 2025/2026 holiday evidence and a replayable candidate calendar are available. Reconciliation identifies DNSE missing 2025-04-03 and 25 VPS duplicate dates. Historical coverage, exceptional-closure review and G1 remain pending. Evidence: `reports/hose_calendar_review.md`, `data/manifests/hose_calendar_evidence.yaml`, `artifacts/source_audit/calendar_2025_2026/`.

- [ ] Create the session calendar from official/reproducible exchange information.
- [ ] Record holidays, exceptional closures, source and version.
- [ ] Do not substitute a weekday-only calendar.
- Depends on: T010.
- Output: `data/manifests/hose_sessions.parquet` plus calendar manifest.
- Acceptance: dataset dates map to sessions or carry an investigated exception; target dates never include non-sessions.
- Plan reference: Sections 6.2, 8.4.

### T013 — Validate and build the processed dataset

Progress 2026-10-01: strict validation and past/current-only feature primitives implemented and tested in `scripts/phase1_pipeline.py`. Accepted execution remains blocked by pending G1/calendar; no accepted processed dataset has been written. Details: `reports/phase1_pipeline_progress.md`.

- [ ] Reject duplicate/unsorted dates.
- [ ] Check positive OHLC and OHLC inequalities.
- [ ] Flag suspicious values without silently deleting them.
- [ ] Compute only the declared derived columns using past/current observations.
- [ ] Preserve source and quality flags.
- Depends on: T011, T012.
- Outputs:
  - `data/processed/vn30_daily.parquet`
  - `data/manifests/dataset.yaml`
  - data-quality report
- Acceptance: processed dataset, schema and code produce a stable dataset hash; no interpolation or boundary-crossing backfill occurs.
- Plan reference: Sections 5.2, 6.

### T014 — Build split, feasibility and common-origin manifests

Progress 2026-10-01: full-path split primitives and planning-only candidate feasibility implemented. Current candidate data has 121 test origins; projected 126-origin freeze is 2026-10-08, subject to accepted realized calendar/data. Inference is explicitly prohibited by the candidate artifact. No accepted split/origin manifests are generated before upstream gates pass. Details: `reports/phase1_pipeline_progress.md`.

- [ ] Calculate eligible sessions strictly after provenance boundary `B`.
- [ ] Allocate the first 63 eligible target sessions to validation and the remainder to test.
- [ ] Retain only origins whose full 20-step target path stays within its target interval.
- [ ] Project the earliest freeze date that can provide 126 test origins.
- [ ] Use one common ordered origin/target manifest for every mandatory model.
- Depends on: T003, T012, T013.
- Outputs:
  - `data/manifests/holdout_feasibility.json`
  - `data/manifests/splits.yaml`
  - `data/manifests/common_origins.parquet`
- Acceptance:
  - All validation/test targets obey their boundaries.
  - All target dates are later than their origin.
  - Test contains at least 126 full-path origins for a confirmatory run.
  - The feasibility artifact contains no forecasts or model metrics.
- Gate: G3 or explicit `exploratory_pilot` classification.
- Plan reference: Sections 0.3, 8.2, 28 split tests.

## 5. Phase 2 — Evaluation framework

### T020 — Implement and validate expanded configurations

- [ ] Define schemas for data, split, forecast, model and evaluation configs.
- [ ] Reject placeholders, mutable revisions, missing hashes and unresolved provenance fields.
- [ ] Include `selection_metric: close_mae_h1` and adapter temporal-encoding description.
- Depends on: T001, T003, T014.
- Outputs: config schemas, validators and model config files.
- Acceptance: invalid/unresolved configs fail before inference; the expanded config has a stable hash.
- Plan reference: Section 22.

### T021 — Implement the unified model interface

- [ ] Implement `fit`, `observe`, `snapshot_state`, `restore_state` and `predict`.
- [ ] Enforce output shapes, origin date, target dates and metadata invariants.
- [ ] Reject duplicate/non-monotonic observations.
- Depends on: T004.
- Outputs: `src/models/base.py` and interface tests.
- Acceptance: every mandatory adapter passes the same contract tests; state snapshot/restore round-trips exactly.
- Plan reference: Section 20.

### T022 — Implement the walk-forward engine

- [ ] Iterate the immutable manifest strictly by origin date.
- [ ] Expose only observations available through the current origin.
- [ ] Update ARIMA/ETS state without parameter re-estimation.
- [ ] Perform one identical technical retry after restoring pre-origin state.
- [ ] Write exactly 20 failure rows after an unresolved origin and replay unassimilated observations at later origins.
- Depends on: T014, T020, T021.
- Outputs: `src/evaluation/walk_forward.py` and integration tests.
- Acceptance: uninterrupted and resumed runs produce equivalent forecasts within the declared tolerance; no date is assimilated twice.
- Plan reference: Sections 8.3–8.4, 21.

### T023 — Implement forecast and scored artifacts

- [ ] Persist label-free forecasts atomically before loading outcomes.
- [ ] Validate run/config/data/split/checkpoint hashes and coverage before joining labels.
- [ ] Store sample paths separately from row-level point forecasts.
- [ ] Build scored artifacts only through the evaluation command.
- Depends on: T020, T022.
- Outputs:
  - `artifacts/forecasts/<run_id>.parquet`
  - `artifacts/scored/<run_id>.parquet`
- Acceptance: raw forecast artifacts contain no actual outcomes; paper outputs can be regenerated from scored artifacts without model inference.
- Plan reference: Sections 23–24.

### T024 — Implement metrics

- [ ] Implement MAE, RMSE, sMAPE, MASE, Return MAE, Return RMSE, DA and Naive-relative skill.
- [ ] Calculate the MASE scale from training history only.
- [ ] Define zero denominator and direction-tie behavior.
- [ ] Report pooled RMSE directly rather than averaging fold RMSE values.
- Depends on: T023.
- Outputs: `src/evaluation/metrics.py` and hand-computable unit tests.
- Acceptance: unit tests cover exact expected values, undefined cases and identical-origin model comparisons.
- Plan reference: Section 16.

### T025 — Implement registered statistical inference

- [ ] Implement paired moving-block bootstrap over origin-level loss vectors.
- [ ] Use 5,000 replicates, primary block length 20 and sensitivity lengths 10/40 where feasible.
- [ ] Produce uncentered percentile CIs and centered-null two-sided tests.
- [ ] Apply Holm correction over the two primary comparisons.
- [ ] Recompute ratio-based skill inside each replicate.
- Depends on: T024.
- Outputs: `src/evaluation/bootstrap.py` and statistical validation tests.
- Acceptance: pairing, chronological blocks, deterministic RNG and multiplicity correction are tested; seeds never count as market observations.
- Plan reference: Section 17.

### T026 — Complete leakage, state and artifact tests

- [ ] Implement every data, split, metric and model-adapter test from Section 28.
- [ ] Test that changing future outcomes cannot change forecasts.
- [ ] Test calendar boundaries, retry/replay, failure coverage and state restoration.
- [ ] Test Kronos optional-column preprocessing and point-summary semantics.
- Depends on: T021–T025.
- Output: complete `tests/` suite.
- Acceptance: all mandatory tests pass in the locked environment.
- Plan reference: Section 28.

### T027 — Run Naive end to end

- [ ] Run every common origin through config validation, forecast artifact, label join, scoring, metrics and table generation.
- Depends on: T014, T020–T026.
- Outputs: Naive forecast/scored artifacts and one generated metrics table.
- Acceptance: table regeneration uses only saved artifacts/manifests; coverage is exactly 100% of common origins.
- Plan reference: Sections 11.1, 30 Phase 3, 37.

## 6. Phase 3 — Mandatory baseline ladder

### T030 — Reproduce or approximate Zhang ARIMA/ETS

- [ ] Run the disclosed paper protocol where possible.
- [ ] Keep replication results separate from the new benchmark.
- [ ] Document every unresolved discrepancy.
- Depends on: T002, T013, T024.
- Outputs: replication artifacts, result table and discrepancy log.
- Acceptance: result is labeled exact replication or approximate replication with reasons.
- Plan reference: Sections 3, 10 E0, 30 Phase 2, 32 Gate B.

### T031 — Implement current-holdout statistical baselines

- [ ] Implement Naive, Drift, ETS and ARIMA for the new protocol.
- [ ] Select ARIMA/ETS specifications on development data only.
- [ ] Freeze parameters at the pre-test boundary and assimilate observed Close values per origin without re-estimation.
- Depends on: T014, T022, T027, T030.
- Outputs: baseline configs and artifacts.
- Acceptance: Naive, ARIMA and ETS have complete common-origin coverage; Drift is reported as a supporting baseline.
- Plan reference: Sections 8.3, 11, 34.

### T032 — Implement DLinear-C

- [ ] Use the declared development search space and exactly five preregistered final seeds.
- [ ] Select by validation Close MAE at h=1 and refit for the frozen epoch count.
- [ ] Average origin-level loss across seeds for model-level inference; report seed dispersion separately.
- Depends on: T014, T020–T026.
- Outputs: DLinear configs, checkpoints, artifacts and seed report.
- Acceptance: no validation label enters training windows or refit early stopping; test inference uses frozen learned parameters.
- Plan reference: Sections 8.3, 12, 23.

### T033 — Implement Ridge-OHLC

- [ ] Flatten the common 128-session OHLC context.
- [ ] Fit scaling on training windows only.
- [ ] Select regularization from the frozen development grid.
- [ ] Predict all 20 future Close values.
- Depends on: T014, T020–T026.
- Outputs: Ridge config and artifacts.
- Acceptance: O/H/L changes exercise the multivariate input path while test labels remain inaccessible.
- Plan reference: Sections 9, 10 E2, 12.2.

## 7. Phase 4 — Mandatory TSFM adapters and freeze

### T040 — Implement the generic multivariate TSFM adapter

- [ ] Use immutable `autogluon/chronos-2-small`, or execute Gate C before test if substitution is required.
- [ ] Supply only the same 128 observed OHLC rows and allowed timestamps.
- [ ] Never provide actual future OHLC as known covariates.
- [ ] Disable cross-learning across forecast origins.
- [ ] Extract the Close 0.5 quantile as the primary point forecast.
- Depends on: T003, T004, T014, T020–T026.
- Outputs: adapter, config, smoke-test and development artifacts.
- Acceptance: the adapter passes all contract/input-parity tests and records its temporal encoding.
- Plan reference: Sections 9.2, 13.2, 32 Gate C.

### T041 — Implement the Kronos-small adapter

- [ ] Load immutable Kronos-small and Kronos-Tokenizer-base revisions.
- [ ] Supply OHLC plus explicit zero `volume` and `amount` for the primary experiment.
- [ ] Use the same 128 observed OHLC rows and target dates as the generic TSFM.
- [ ] Tune sampling parameters only on validation data.
- [ ] Retain raw sample paths and use the sample median for primary MAE.
- [ ] Derive RNG seed from run seed and origin so resume/batching does not change forecasts.
- Depends on: T003, T004, T014, T020–T026.
- Outputs: adapter, config, smoke-test and development artifacts.
- Acceptance: sample mean reproduces official public aggregation within tolerance; median is independently verified; amount/volume preprocessing is tested.
- Plan reference: Sections 14, 28.

### T042 — Verify E2 input parity and document temporal encoding

- [ ] For Ridge-OHLC, generic TSFM and Kronos, compare origin IDs, context dates, OHLC values, target dates and context length before inference.
- [ ] Record each adapter's timestamp/session-position/temporal-embedding behavior.
- [ ] Generate a machine-readable parity report.
- Depends on: T033, T040, T041.
- Output: `artifacts/metrics/e2_input_parity.json`.
- Acceptance: all observed market inputs match exactly; remaining temporal-encoding differences are documented as limitations.
- Plan reference: Sections 0.5, 8.4, 10 E2.

### T043 — Freeze G4

- [ ] Freeze dataset, calendar, split, common origins, expanded configs, seeds, point functional, inference parameters and code commit.
- [ ] Store hashes and a signed/time-stamped freeze record.
- [ ] Confirm no final test metrics have been opened.
- Depends on: G1–G3, T020, T025, T031–T042.
- Output: `data/manifests/primary_freeze.yaml`.
- Acceptance: changing any frozen input changes a hash and invalidates cached forecasts.
- Gate: G4.
- Plan reference: Sections 0.3–0.4, 8.3, 23.

### T044 — Execute the mandatory holdout once

- [ ] Run Naive, ARIMA, ETS, DLinear-C, Ridge-OHLC, frozen generic multivariate TSFM and Kronos-small on the common manifest.
- [ ] Retain every origin, seed, retry and failure.
- [ ] Do not tune, replace or rerun selectively from test performance.
- Depends on: T043.
- Outputs: immutable forecast artifacts and run metadata for all mandatory models.
- Acceptance: every model has valid forecasts for every origin or a complete explicit failure table; incomplete models are excluded from superiority claims until resolved consistently.
- Plan reference: Sections 24, 34, 36 task 14.

## 8. Phase 5 — Scoring, inference and core paper artifacts

### T050 — Validate holdout coverage and join labels

- [ ] Validate run/config/data/split/checkpoint hashes.
- [ ] Verify identical origin and target coverage across mandatory models.
- [ ] Join immutable labels only after forecast validation.
- Depends on: T044.
- Outputs: scored artifacts and coverage report.
- Acceptance: no model is compared on a selectively successful subset.
- Plan reference: Sections 8.4, 24.

### T051 — Generate primary and secondary metric tables

- [ ] Calculate h=1/5/20 price, return and direction metrics from scored artifacts.
- [ ] Report always-up and previous-return-sign DA baselines.
- [ ] Include Naive-relative skill and sample count.
- Depends on: T024, T050.
- Outputs: Tables A and B plus machine-readable metrics.
- Acceptance: every displayed number traces to scored artifact rows and frozen hashes.
- Plan reference: Sections 16, 25 Tables A–B.

### T052 — Run registered primary inference

- [ ] Test Kronos-small vs Naive at h=1 absolute loss.
- [ ] Test Kronos-small vs generic multivariate TSFM at h=1 absolute loss.
- [ ] Report direction, mean loss difference, 95% CI, raw p-value and Holm-adjusted p-value.
- Depends on: T025, T050.
- Output: Table C and bootstrap replicate metadata.
- Acceptance: inference uses paired origin-level losses and the frozen two-comparison family.
- Plan reference: Section 17, Section 25 Table C.

### T053 — Generate core figures

- [ ] Plot the full VN30 history with split boundaries.
- [ ] Plot returns and rolling volatility.
- [ ] Plot representative forecasts selected by a frozen rule including typical and failure cases.
- [ ] Plot MASE by model/horizon and relative improvement over Naive.
- Depends on: T051, T052.
- Outputs: core figures under `reports/figures/`.
- Acceptance: figures are regenerated by scripts from manifests/scored artifacts; no favorable period is hand-picked.
- Plan reference: Section 26.

### T054 — Run error and failure analysis

- [ ] Generate case files for the largest preregistered Kronos errors.
- [ ] Report failure coverage, invalid predictions, retries and unresolved origins.
- [ ] Keep pattern labels descriptive and out of model training.
- Depends on: T050.
- Outputs: error case files and failure report.
- Acceptance: case selection is rule-based and includes adverse results.
- Plan reference: Sections 27, 35.

### T055 — Verify full reproducibility

- [ ] Rebuild the environment from the lock.
- [ ] Regenerate forecasts within numeric tolerance using the same revisions/seeds.
- [ ] Regenerate all metrics, tests, tables and figures from persisted artifacts.
- Depends on: T050–T054.
- Outputs: reproducibility report and commands.
- Acceptance: every final number maps to dataset hash, split/origin hash, config hash, checkpoint revision and code commit.
- Plan reference: Sections 23, 28, 30 Phase 8, 35.

## 9. Phase 6 — Secondary work

Secondary work starts only after T055 passes.

### T060 — Predictor-only Kronos adaptation

- [ ] Freeze tokenizer and fine-tune predictor on training windows only.
- [ ] Select settings on purged validation; use five preregistered seeds for confirmatory reporting.
- [ ] Compare adapted and zero-shot Kronos on identical frozen origins.
- Outputs: adaptation artifacts and Table E.
- Plan reference: Sections 15, 17.1, 30 Phase 6.

### T061 — DM robustness analysis

- [ ] Run DM tests with declared Newey-West/Bartlett bandwidth and finite-sample correction.
- [ ] Return undefined for zero/nonpositive variance.
- Output: secondary statistical table.
- Plan reference: Section 17.2.

### T062 — Volatility-regime analysis

- [ ] Calculate origin-time volatility from past data only.
- [ ] Set regime thresholds from training history only.
- [ ] Report regime sample sizes and descriptive results for sparse cells.
- Outputs: Table D and conditional regime figure.
- Plan reference: Section 18.

## 10. Phase 7 — Optional work

Optional tasks may be independently skipped with a recorded reason.

- [ ] **T070:** Chronos-T5-mini Close-only historical/general token baseline — Sections 9.2, 13.1.
- [ ] **T071:** VN30 validated trading-value ablation; verify semantics, latency and preprocessing — Sections 4, 10 E3.
- [ ] **T072:** Independently tuned context-length sensitivity; freeze selected setting before its separate OOS run — Sections 8.3, 14.3.
- [ ] **T073:** Full Kronos tokenizer plus predictor fine-tuning after predictor-only adaptation — Section 15 Stage C.
- [ ] **T074:** Adaptation data-efficiency study using feasible 1y/3y/5y/full cells — Section 10 E5.
- [ ] **T075:** Probabilistic scoring after retained-path validation — Sections 14.6, 16.3.
- [ ] **T076:** Kronos-base and other larger-checkpoint size sensitivity — Section 9.3.

## 11. Phase 8 — Final research package

### T080 — Audit claims against evidence

- [ ] Check every claim against the allowed/forbidden claim list.
- [ ] Describe association rather than claiming tokenization causality.
- [ ] Preserve negative results and limitations.
- [ ] Label pilot, exploratory, secondary and confirmatory outputs correctly.
- Depends on: T055 and any completed secondary/optional tasks.
- Output: `reports/claim_evidence_matrix.md`.
- Acceptance: every manuscript claim points to a table, figure or reproducible artifact.
- Plan reference: Sections 33, 35.

### T081 — Freeze the reproducibility package

- [ ] Freeze data/checkpoint/config/code references and final artifact hashes.
- [ ] Publish exact setup and regeneration commands.
- [ ] Generate final tables/figures automatically.
- [ ] Record deferred tasks and known limitations.
- Depends on: T080.
- Outputs: final report/paper package and `reports/reproducibility.md`.
- Acceptance: a clean environment can reproduce the reported package without undocumented manual steps.
- Plan reference: Sections 30 Phase 8, 36 task 17.

## 12. Core completion checklist

The primary study is complete only when all items below are checked:

- [ ] G1, G2, G3 and G4 pass.
- [ ] T001–T055 pass; the supporting Drift component inside T031 may be omitted with a recorded reason.
- [ ] Mandatory models use identical common full-path origins.
- [ ] Primary point forecasts use the declared median semantics.
- [ ] Primary h=1 model selection and inference rules remain frozen.
- [ ] Every origin has a valid forecast or an explicit failure record.
- [ ] Both registered bootstrap tests and Holm correction are reported.
- [ ] Tables and figures are generated from validated scored artifacts.
- [ ] No test-informed tuning or selective rerun occurred.
- [ ] Final numbers trace to immutable hashes and revisions.

## 13. Per-task evidence template

Copy this block into `reports/experiment_log.md` when closing a task:

```text
Task ID:
Status: accepted | blocked | exploratory
Completed at:
Code commit:
Config hash:
Dataset/split/origin hashes:
Checkpoint/tokenizer revisions:
Commands executed:
Outputs:
Checks/tests:
Deviations:
Reviewer:
```

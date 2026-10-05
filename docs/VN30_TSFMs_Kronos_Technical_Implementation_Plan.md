# Technical Implementation Plan — VN30 Index Forecasting with Classical Models, General TSFMs, and Kronos

**Research object:** VN30 Index  
**Primary task:** Daily multi-horizon forecasting  
**Core comparison:** Classical statistical forecasting → train-from-scratch neural forecasting → general-purpose TSFM → finance-specific K-line foundation model  
**Primary model of interest:** Kronos  
**Document status:** Reviewed implementation plan v4; G2 accepted, G1/G3/G4 pending
**Date:** 2026-09-26

**Data versioning update — 2026-10-06:** Raw captures and shared candidate SQLite/ZIP bytes are managed by DVC with the team's Google Drive remote; Git retains pointers, SHA256 and receipts. Custom Desktop OAuth and upload/fresh-cache restore verified all 89 files without SHA256 changes. Pointers/receipts are versioned in Git; another collaborator's independent download remains pending. This infrastructure migration does not alter dataset bytes, study v4 or G1/G3/G4. See [DVC workflow](DVC_Data_Versioning.md) and [validation](../reports/dvc_migration_validation.md).

**Execution update — 2026-10-05:** VNDIRECT remains the selected candidate. The fresh audit through 2026-10-02 has 2,272 rows; all 39 discrepant fields on 30 dates were investigated, with four publication-supported Close values and 35 unadjudicated O/H/L values. A 71-session Open/previous-Close pattern during 2025-05-05–2025-08-11 requires construction-rule clarification. Calendar agreement is diagnostic; original historical notices and exception review remain pending. See [T010/T012 review](../reports/vndirect_T010_T012_review.md) and [case-level review](../reports/vndirect_39_discrepancy_review.md). Existing shared snapshots remain unchanged through 2026-10-01.

**Literature amendment status:** [Four-paper review](../reports/vn30_baseline_literature_review.md) proposes daily ARIMA as a replacement E0 anchor and a conditional KTPCA extension. These proposals are not adopted by this update: study v4, Zhang replication protocol, core models and test contract remain unchanged. Any adoption must version the study, plan, task definitions and replication manifest together before execution. Latest task and CI acceptance evidence is in the [checklist](VN30_TSFMs_Kronos_End_to_End_Tasks.md).

---

## 0. Execution contract (read this first)

This document supports one paper claim: whether a finance-specific pretrained model transfers to VN30 better than simple baselines and a generic multivariate TSFM when all models receive the same information available at the same forecast origin.

### 0.1 Frozen primary question

```text
Data:          VN30 daily OHLC
Forecast:      one 20-session Close path from each origin
Primary score: pooled Close MAE at h=1
Primary model: Kronos-small, zero-shot, OHLC
Comparators:   Naive and one frozen generic multivariate TSFM, OHLC
Origin set:    the same provenance-qualified, full-path origins for every model
Point value:   predictive median for sampled/quantile TSFMs
Inference:     paired moving-block bootstrap; Holm correction over two tests
```

The two registered primary hypotheses are:

1. Kronos zero-shot has different h=1 absolute error from Naive.
2. Kronos zero-shot has different h=1 absolute error from the frozen generic multivariate TSFM.

Direction, effect size and confidence interval must be reported; the study does not assume Kronos wins.

### 0.2 Mandatory, secondary and optional work

| Priority | Required content | Paper role |
|---|---|---|
| Mandatory | accepted immutable VN30 OHLC snapshot; split/origin manifests; Naive, ARIMA, ETS, DLinear-C, Ridge-OHLC, generic multivariate TSFM and Kronos zero-shot; h=1/5/20 scores; primary bootstrap tests | complete core paper |
| Secondary | predictor-only Kronos adaptation; DM robustness; volatility regimes | strengthens the paper but cannot change the primary claim |
| Optional | Chronos-T5, trading-value ablation, full tokenizer fine-tuning, data-efficiency study, probabilistic scoring, larger checkpoints | appendix or later work |

Optional work must not delay or redefine the mandatory benchmark.

### 0.3 Non-negotiable gates

The primary benchmark may run only after all four conditions are true:

```text
G1  A reproducible VN30 OHLC source passes Section 5.4.
G2  Exact checkpoint/tokenizer revisions and provenance are recorded.
G3  The common clean test contains at least 126 full 20-step origins.
G4  Configuration, calendar and origin manifests are frozen before any test inference or inspection of test performance.
```

Before G3 can pass, generate a feasibility artifact containing the provenance boundary, eligible session count, validation target dates, candidate test-origin count and earliest projected dataset-freeze date that would produce 126 full-path origins. Compute it from the accepted versioned HOSE session calendar rather than weekdays. This artifact contains no model forecasts or test metrics.

If G1 fails, stop. If G2 or G3 fails, run only a clearly labeled exploratory pilot and begin prospective collection. Do not weaken the 126-origin rule or move the provenance boundary after viewing model results. Failure to reproduce Zhang (2025) exactly does not block the new benchmark if the missing information is documented.

### 0.4 One-way execution flow

```text
paper extraction + checkpoint audit
              ↓
raw data snapshot → data audit → frozen processed dataset
              ↓
calendar + split manifest → immutable common-origin manifest
              ↓
development tuning → frozen expanded configs → pre-test refit
              ↓
forecast-only artifacts → label join → scored artifacts
              ↓
registered statistics → tables/figures → paper claims
```

No decision may flow backward from final test metrics to data cleaning, model choice, context length, inference parameters or checkpoint selection.

### 0.5 Paper-to-experiment mapping

| Paper statement | Required evidence |
|---|---|
| Published VN30 baseline can/cannot be reproduced | E0 manifest, code, reproduced metrics and discrepancy log |
| Generic TSFM transfers to VN30 | generic multivariate TSFM versus Naive/ARIMA/ETS on the common holdout |
| Finance-specific transfer differs from generic transfer | Kronos versus the frozen generic multivariate TSFM in E2 |
| Adaptation helps Kronos | predictor-only adapted Kronos versus zero-shot on identical origins |
| Performance varies by horizon/regime | preregistered secondary h=5/20 and regime tables |

Controlling OHLC does not isolate tokenization causally because architectures, objectives, corpora and training compute also differ.

The controlled information claim applies to observed market variables and context dates: every E2 model receives the same 128 OHLC rows from the same origins and predicts the same target sessions. Native temporal encodings may still differ by architecture and must be recorded; therefore describe E2 as **OHLC/input-controlled**, not as controlling every internal source of information.

### 0.6 Review decisions retained in v4

VN30-only scope; replication separated from extension; immutable data; OHLC input control; checkpoint-aware dates; purged labels; state-current classical baselines; correct MASE interpretation; DLinear channel-independence; explicit Kronos amount handling; consistent median semantics; and preservation of negative results. No experiment result is claimed by this plan.

## 1. Research objective

### 1.1 Core question

The study will test whether a finance-specific pretrained representation, especially **K-line tokenization in Kronos**, transfers effectively to the **VN30 Index**, compared with:

1. simple forecasting baselines;
2. the published VN30 ARIMA/ETS baseline;
3. a train-from-scratch neural model;
4. general-purpose pretrained time-series foundation models.

The central question is not simply *“which model has the lowest RMSE?”*. The study is designed to separate several hypotheses:

- **H1 — Statistical sufficiency:** much of the predictable structure in VN30 can already be captured by simple/statistical models.
- **H2 — Generic transfer:** a general TSFM transfers reusable temporal patterns to VN30 in zero-shot mode.
- **H3 — Finance-domain transfer:** a finance-specific TSFM transfers better because its pretraining and representation better match financial K-lines.
- **H4 — Adaptation:** Kronos may not be optimal zero-shot, but VN30-specific adaptation may improve it.
- **H5 — Regime dependence:** relative model performance changes across volatility regimes and forecast horizons.

### 1.2 Research questions

- **RQ1:** Can general-purpose TSFMs outperform Naive, ARIMA and ETS on VN30 in strict out-of-sample forecasting?
- **RQ2:** Does Kronos outperform a generic TSFM when both are given comparable OHLC information?
- **RQ3:** How much does Kronos benefit from VN30-specific adaptation/fine-tuning?
- **RQ4:** Are gains stable at horizons of 1, 5 and 20 trading sessions?
- **RQ5:** Are gains stable across low-, medium- and high-volatility regimes?
- **RQ6:** Does adding VN30 aggregate trading value provide useful information beyond OHLC for Kronos?

---

## 2. Scope freeze

### 2.1 In scope

- VN30 **price index** only.
- Daily frequency.
- Forecast horizons: **1, 5, 20 trading sessions**.
- Primary inputs: **Open, High, Low, Close (OHLC)**.
- Optional ablation: VN30 aggregate trading value mapped only when its semantics and historical availability are validated.
- Point forecasting as the primary study.
- Probabilistic forecasting as an extension when comparable sample/quantile outputs are available.
- Strict chronological evaluation.
- Zero-shot and VN30-specific adaptation for pretrained models.

### 2.2 Out of scope for v1

- Intraday/high-frequency forecasting.
- Order-book or tick data.
- News/sentiment.
- Macroeconomic covariates.
- Constituent-level features.
- Trading execution/backtesting as the primary contribution.
- Portfolio optimization.
- Reinforcement learning.
- Automatic buy/sell recommendations.

These extensions can be added only after the core benchmark is stable.

---

## 3. Research baseline to reproduce first

A published VN30-specific baseline already exists:

> Zhang, H. (2025), *Vietnam V30 Closing Price Forecast Based on ARIMA and ETS*, Advances in Economics, Management and Political Sciences, 147, 29–34. DOI: 10.54254/2754-1169/2024.GA19104.

The public article page states that the study uses the VN30 index from **2016 to 2023** and compares ARIMA and ETS.

### Replication rule

Before any TSFM benchmark, create a **replication manifest** containing:

```yaml
paper: Zhang_2025_VN30_ARIMA_ETS
data_period: exact period extracted from paper
source: exact source if disclosed
frequency: daily
target: close
train_split: exact split if disclosed
validation_split: exact split if disclosed
test_split: exact split if disclosed
arima_order: exact order if disclosed
ets_specification: exact specification if disclosed
metrics: exact formulas used in paper
reported_results: extracted values
reproduced_results: null
notes: null
```

If the paper does not disclose enough detail to reproduce an item, mark it **not reported** rather than guessing.

Record conflicts between the article abstract, result tables and conclusion rather than selecting the most favorable claim. Verify the DOI against publisher metadata before citation export. Cap the initial replication investigation at two working days; unresolved items remain documented limitations.

This replication and the new TSFM experiment must remain separate. The new study must not silently alter the old methodology and still call it a replication.

---

## 4. VN30-specific facts that affect the implementation

The HOSE Index Ground Rule Version 4.0 describes VN30 as a **free-float-adjusted market-capitalization index with 30 constituents**. The rules include periodic constituent review and capping. The index itself is therefore a synthetic index rather than a directly traded stock.

Implications:

1. **OHLC is meaningful** for the index time series.
2. **Stock volume is not naturally defined for the index itself.**
3. HOSE publishes trading value associated with VN30 constituents/index summaries, but this must not automatically be treated as if it were a stock's own traded `volume`.
4. The primary Kronos experiment should therefore use **OHLC only**.
5. A trading-value feature should be introduced only as a clearly labeled ablation.

The inspected Kronos predictor requires OHLC. If `volume` is absent, it sets both `volume` and `amount` to zero, even when `amount` was supplied; if only `amount` is absent, it derives it from volume and mean OHLC [8]. For the primary adapter, explicitly supply both fields as zero. This makes an OHLC-only VN30 experiment technically possible, but the zero-filled dimensions should be documented as a potential distribution shift relative to Kronos pretraining.

---

## 5. Dataset design

### 5.1 Dataset periods

Use two dataset views.

#### Dataset A — replication slice

- VN30: **2016–2023**.
- Purpose: reproduce/approximate the published ARIMA/ETS study.
- Use the exact period and split from the paper whenever disclosed.

#### Dataset B — main research dataset

Target period:

```text
VN30 launch / earliest reliable daily OHLC
        →
latest complete trading day available at experiment freeze
```

VN30 was introduced by HOSE in 2012. Prefer observed post-launch data over reconstructed pre-launch values unless the provider clearly documents reconstruction methodology.

The exact experiment freeze date must be recorded in the dataset manifest.

### 5.2 Required raw schema

```text
date              trading date
open              VN30 opening index level
high              VN30 highest index level
low               VN30 lowest index level
close             VN30 closing index level
trade_value       optional aggregate VN30 trading value
source             data provider identifier
retrieved_at       retrieval timestamp
```

Processed schema:

```text
date
open
high
low
close
log_close
return_1d
log_return_1d
range_abs
range_pct
body_abs
body_pct
trade_value        optional
source
quality_flags
```

Do **not** add technical indicators to the primary benchmark. They would change the scientific question from representation/pretraining to feature engineering.

### 5.3 Source hierarchy

Use the following hierarchy:

1. **HOSE official material** for index rules and spot checks.
2. A reproducible historical-data provider/API for complete daily VN30 OHLC.
3. A second independent source for validation only.

Do not merge providers by default. Provider switching can introduce hidden discontinuities.

Source selection (2026-10-05, explicit user decision): **VNDIRECT** is the primary provider for Dataset B. The retained capture starts on 2017-08-24, so this source cannot cover the full Dataset A replication period. Use verified provider coverage without splicing earlier prices from another feed; disclose the final accepted period in the dataset manifest. Selection does not itself pass G1 or accept the calendar. The decision is recorded in `configs/primary_data_source.yaml`; collaborator snapshot exchange is documented in `docs/Collaborator_Data_Guide.md`.

### 5.4 Data-source acceptance gate

A source is accepted only if:

- daily OHLC history is reproducibly downloadable;
- dates are explicit and sorted;
- OHLC units are consistent;
- duplicate dates are absent or explainable;
- at least 30 seeded, year-stratified OHLC observations can be cross-checked against an independent source, supplemented by extreme-return dates; record precision-based tolerances and discrepancies;
- missing observations can be explained by the trading calendar rather than silently imputed;

Policy amendment (2026-10-02, explicit user request): research-use permission is excluded from G1. No permission evidence is required to pass this gate. This records the study's acceptance policy, not a verified grant of data rights. All quality, reproducibility, independent crosscheck and calendar requirements above remain mandatory.

### 5.5 Immutable data snapshots

Save raw data unchanged:

```text
data/raw/vn30/<provider>/<retrieval_date>/vn30_daily.csv
```

Generate:

```text
SHA256
row_count
min_date
max_date
column_schema
provider
retrieval_timestamp
```

Never overwrite raw snapshots.

---

## 6. Data validation and leakage prevention

### 6.1 OHLC integrity checks

For every trading day:

$$
L_t \le \min(O_t,C_t)
$$

$$
H_t \ge \max(O_t,C_t)
$$

and:

```text
open > 0
high > 0
low > 0
close > 0
high >= low
```

Flag rather than automatically delete suspicious observations.

### 6.2 Calendar handling

- Do not insert weekends.
- Do not blindly insert public holidays.
- Do not linearly interpolate price levels across missing trading days.
- If a trading session is unexpectedly missing, investigate the source first.

### 6.3 Leakage rules

Strict rules:

- No random train/test split.
- Dataset-level scalers fit only on the training partition. Native per-context normalization may use observations through the current origin, including previously observed test sessions; it must never use the forecast window.
- No centered rolling feature computed across the full dataset. DLinear decomposition within an already observed context is allowed; it must not access labels or future context.
- No `bfill()` across the train/test boundary.
- Volatility regime labels for time `t` must use only information available at or before `t`.
- Every supervised training window must have its entire 20-step label block inside training; validation context may include earlier training observations, but all validation targets must lie in validation. Purge boundary-crossing labels.
- Hyperparameters are selected on development data and frozen before final test evaluation.
- Test metrics must not be used to choose context length, learning rate, model size or sampling parameters.

---

## 7. Forecast targets

Use two evaluation views.

### 7.1 Price-level target

For horizon $h$:

$$
y^{price}_{t,h}=C_{t+h}
$$

This preserves direct comparability with the published VN30 close-price forecasting baseline.

### 7.2 Cumulative log-return target

$$
y^{return}_{t,h}=\log\left(\frac{C_{t+h}}{C_t}\right)
$$

Directional label:

$$
d_{t,h}=sign(y^{return}_{t,h})
$$

Why both are necessary:

- price levels are persistent and can make a Naive model look very strong;
- return evaluation tests whether the model actually predicts movement rather than merely tracking the current level.

---

## 8. Forecast protocol

### 8.1 One 20-step path per forecast origin

At every origin $t$, each model produces:

$$
\hat{C}_{t+1:t+20}
$$

Evaluate steps:

```text
h = 1
h = 5
h = 20
```

Do not invoke three independently tuned models for the three horizons unless the method intrinsically requires horizon-specific fitting.

This keeps the comparison closer to a real multi-step forecasting problem.

### 8.2 Separate retrospective diagnostics from the primary benchmark

**Do not label 2021-2024 forecasts from current foundation models as clean historical OOS.** Kronos describes a June 2024 pretraining cutoff [6]. Chronos-2 was released in October 2025 [3]; that date does not establish the release date or cutoff of the particular small checkpoint. A chronological downstream split alone does not remove pretraining contamination.

Maintain three evidence tracks:

1. **Historical diagnostic:** development through 2020, expanding annual folds 2021 onward. Useful for classical models, engine verification and exploratory regimes. TSFM results in overlapping/unknown pretraining periods are labeled `retrospective_contamination_unknown`; exclude them from primary significance claims.
2. **Primary retrospective benchmark:** choose dates only after checkpoint provenance is audited. Record immutable model/tokenizer revisions, first public availability of those exact weights, documented training cutoff and evidence URL. Use a common boundary after the latest verified cutoff for all models; if any cutoff is unknown, conservatively use the latest verified public availability of all exact weight revisions. A missing provenance record blocks the clean-comparison label, not exploratory work.
3. **Prospective follow-up:** freeze code, configuration and weights now, persist forecasts before outcomes exist, then score after labels mature. This is strongest when recent checkpoints leave too little historical holdout.

Default date-selection algorithm for track 2, fixed before reading model test scores:

```text
B = latest acceptable provenance boundary among all primary checkpoints
E = ordered VN30 sessions strictly after B and no later than the data freeze

validation_targets = E[0:63]
test_targets       = E[63:]

validation_origin is valid iff all of t+1 ... t+20 are validation_targets
test_origin is valid iff all of t+1 ... t+20 are test_targets

primary_origin_set = every valid full-path test origin in one immutable manifest
                     consumed unchanged by every mandatory model
minimum size       = 126 full-path test origins
```

All primary h=1, h=5 and h=20 results use this same full-path origin set. This avoids changing sample size across horizons. A separately labeled horizon-specific sensitivity table may use later h=1 or h=5 origins whose shorter targets are observed, but it cannot replace the primary table or tests.

Training initially contains all accepted history before the validation target interval. Development tuning uses only valid validation origins. After every hyperparameter and training duration is frozen, trainable models are refit once on all observations through the last validation session; the first test origin is that last validation session. Every test target is therefore strictly later than all refit observations.

Report `B`, validation dates, test dates, first/last origin and final origin count explicitly. If fewer than 126 full-path origins remain, report a pilot, continue prospective collection, or preregister a different eligible checkpoint before opening test results. Do not backdate the split merely to obtain more data. Additional checkpoint-specific historical tests are separate tables and are never pooled with the common test.

Before model execution, save `data/manifests/holdout_feasibility.json` with at least:

```text
checkpoint/tokenizer revisions and first-public-availability evidence
provenance boundary B
dataset freeze and calendar version
eligible session count
validation target start/end
candidate test origin start/end/count
required origin count = 126
earliest projected freeze date for 126 full-path origins
gate status: pass / pilot
```

The projected date is planning information and must be recomputed against the realized exchange calendar when data are frozen.

### 8.3 Hyperparameter selection and fitting policy

Use this exact sequence:

1. Declare the search space and search budget without test metrics.
2. Fit each candidate on development training data only.
3. Select context length, hyperparameters, inference settings and neural epoch count using valid validation origins only. The frozen selection metric is pooled Close MAE at h=1 on the common validation-origin set.
4. Freeze architecture, loss, point functional, seed list, aggregation, sampling and state-update policy in expanded configs.
5. Refit trainable models once on all pre-test observations for the selected fixed epoch count. Refit scalers on exactly that same partition.
6. Run the frozen test origin manifest once. Do not early-stop, retune or replace a model from test results.

For stochastic trainable models, compute the selection score by averaging origin-level absolute loss across the preregistered development seeds before pooling origins. If two configurations have identical validation MAE at the stored numerical precision, choose the one with lower h=1 validation RMSE; if still tied, choose the lexicographically smaller immutable config ID. Record every candidate score and the selected config. Multi-horizon selection is a separately labeled sensitivity analysis and cannot replace this rule.

E2 uses the same 128-session context for Ridge-OHLC, the generic multivariate TSFM and Kronos unless 128 is infeasible for a locked adapter. Independently tuned context lengths belong to a secondary best-configuration experiment. Primary evaluation keeps learned parameters fixed across the holdout.

Do not pass validation rows already used in training to early stopping. Later expanding folds may absorb earlier test observations only in a separately preregistered online-update experiment after their labels mature; they are not part of the primary fixed-model benchmark.

ARIMA/ETS are fit through the last validation session. At later origins, append only newly observed closes to their state without re-estimating parameters. Forecast from the state current at that origin. Naive uses the latest close; Drift uses all history available at that origin. Neural/TSFM adapters receive only the trailing context. Log the last assimilated timestamp. This prevents a stale fold-start statistical forecast from being compared with a TSFM that sees current data.

### 8.4 Origins, calendars and failure policy

Define origin t as **after the completed VN30 session t**; targets are sessions t+1 through t+20. Include the final pre-test session as the first eligible origin when its targets lie in test. Build one immutable origin/target-date manifest, shared by all models; do not silently lose the last 20 sessions of every calendar year. Annual summaries are grouped by origin within the common holdout, not separate truncating datasets.

Use a versioned HOSE session calendar. Known holidays can determine future timestamps; record exceptional closures and any hindsight use of the realized calendar. Do not use a weekday-only calendar as a substitute. Library tensor adapters operate on consecutive session positions and map back to true dates; Kronos receives the real calendar features.

For every E2 adapter, record whether timestamps are represented as session positions, explicit calendar features or native temporal embeddings. Kronos may consume its required native timestamp features, but this architectural difference must appear in the methods and limitations. Do not claim that E2 causally isolates tokenization. A calendar-covariate sensitivity is valid only if the same point-in-time calendar fields can be supplied consistently to every compared model.

Persist every attempted origin, status and error. Invalid/nonpositive Close predictions are failures, not silently clipped or removed. Predeclare one technical retry with identical configuration. A failed common-origin forecast blocks the complete-table label until fixed and rerun consistently; partial tables must show coverage and cannot claim superiority from selectively omitted origins.

---

## 9. Model matrix

### 9.1 Planned model registry

| ID | Model | Role | Input | Training mode |
|---|---|---|---|---|
| B0 | Naive / Random Walk | sanity baseline | Close | none |
| B1 | Drift | stronger simple baseline | Close | analytical |
| B2 | ETS | published baseline family | Close | pre-test fit; state update per origin |
| B3 | ARIMA | published baseline family | Close | pre-test fit; state update per origin |
| N1 | DLinear | channel-independent neural baseline | Close; OHLC optional | pre-test fit |
| B4 | Ridge-OHLC | lightweight channel-mixing baseline | flattened OHLC context | pre-test fit |
| T1 | Chronos-T5-mini | original generic token TSFM | Close | zero-shot |
| T2 | Chronos-2-small | input-controlled generic TSFM | OHLC | zero-shot |
| K1 | Kronos-small | finance-specific K-line TSFM | OHLC | zero-shot |
| K2 | Kronos-small adapted (secondary) | finance-specific + VN30 adaptation | OHLC | fine-tuned if feasible |

The mandatory core consists of B0, B2, B3, N1 as DLinear-C, B4, T2 and K1. B1 is a low-cost supporting baseline, T1 is optional, and K2 is secondary. Their presence in this registry does not make optional or secondary work an exit condition for the core study.

### 9.2 Why both original Chronos and Chronos-2?

The original Chronos is useful conceptually because it explicitly represents generic time series through scaling + quantization + language-model forecasting.

However, comparing univariate Chronos directly with multivariate Kronos conflates **input information** and **representation**.

Chronos-2 currently supports multivariate/covariate-informed forecasting and provides a better information-controlled generic TSFM comparator. Therefore:

- **Chronos-T5-mini:** historical/general tokenization baseline.
- **Chronos-2-small:** primary generic TSFM comparator for OHLC-controlled tests.
- **Kronos-small:** domain-specific comparator of similar practical scale.

If Chronos-2 introduces implementation instability, replace T2 with a stable multivariate Moirai checkpoint and document the substitution before final evaluation.

### 9.3 Optional robustness models

Only after the core matrix is complete:

- LSTM — continuity with the old project.
- Moirai — second general-purpose multivariate TSFM.
- Kronos-base — model-size sensitivity.
- Chronos-T5-base — model-size sensitivity.

Do not add models merely to make the benchmark table longer.

---

## 10. Input-control experiment design

This section controls observed market inputs, origin dates, target dates and context length, but does not isolate tokenization causally: temporal encoding, architecture, corpus, objective and compute still differ.

### Experiment E0 — Published baseline replication

```text
Input: Close
Models: ARIMA, ETS
Period: paper's 2016–2023 protocol
Goal: establish reproducibility
```

### Experiment E1 — Classical and generic univariate forecasting

```text
Input: Close only
Models:
- Naive
- Drift
- ETS
- ARIMA
- DLinear-univariate
- Chronos-T5-mini
Goal: benchmark generic close-price forecasting
```

### Experiment E2 — Information-controlled multivariate benchmark

```text
Input: identical OHLC history
Models:
- Ridge-OHLC (channel mixing)
- DLinear-OHLC (optional channel-independent reference)
- Chronos-2-small
- Kronos-small
Goal: compare generic vs finance-specific pretrained representation
      while controlling observed information
```

This should be the **primary experiment for the Kronos research claim**.

### Experiment E3 — Kronos input ablation

```text
Kronos-OHLC
vs
Kronos-OHLC + validated trading value
```

Do not fabricate stock-style volume for VN30. For E3 explicitly set `volume=0.0` and `amount=trade_value`; otherwise the inspected predictor overwrites amount when volume is absent [8]. Assert the supplied amount survives preprocessing. Record currency/unit, publication latency, historical constituent membership and whether the field is point-in-time. Keep E3 separate from the OHLC-controlled claim; skip it if semantics or history cannot be verified.

### Experiment E4 — Adaptation study

```text
Kronos zero-shot
vs
Kronos predictor-only fine-tuning
vs
Kronos official two-stage fine-tuning (tokenizer + predictor)
```

The full two-stage variant is optional because a single daily VN30 series is small and can easily overfit.

### Experiment E5 — Data-efficiency study

At each final fold, adapt using only the most recent:

```text
1 year  ≈ 252 sessions
3 years ≈ 756 sessions
5 years ≈ 1260 sessions
all available pre-test history
```

Use actual available sessions, not an assumption of 252 per year. A context of 512 cannot be trained from one year of approximately 252 observations. Require `N = max(0, T - context - 20 + 1)` after the validation holdout and purge; mark impossible or too-small cells unavailable instead of borrowing older data silently. Overlapping windows are not independent samples. Freeze the minimum usable-window rule on development.

This produces:

$$
Performance=f(\text{VN30 adaptation data})
$$

and tests whether the value of pretraining is strongest in the low-data regime.

---

## 11. Classical baselines

### 11.1 Naive / Random Walk

$$
\hat C_{t+h}=C_t
$$

This is mandatory.

Any complex model that cannot reliably beat this baseline on appropriate metrics has weak practical forecasting evidence.

### 11.2 Drift

$$
\hat C_{t+h}=C_t+h\frac{C_t-C_1}{t-1}
$$

Useful as a second low-complexity baseline.

### 11.3 ARIMA

Replication branch:

- use the paper's exact specification if disclosed.

Extension branch:

- difference/order search ranges selected on the development period only;
- use AIC/AICc as an internal selection criterion;
- optionally verify residual autocorrelation;
- freeze the search space before OOS evaluation.

Do not run an unconstrained Auto-ARIMA search separately on each test year after seeing test performance.

### 11.4 ETS

Replication branch:

- reproduce paper specification exactly if disclosed.

Extension branch:

- compare a small preregistered family of level/trend/damped-trend configurations on development data;
- do not invent seasonality without evidence.

---

## 12. DLinear baseline

DLinear is used because it provides a deliberately simple train-from-scratch neural comparator.

### 12.1 Config search on development only

Candidate context lengths:

```text
64
128
256
512
```

Original DLinear has temporal linear projections, not a generic hidden-width parameter. Tune only a small declared set of learning rates, decomposition settings and `individual` sharing choices. The official implementation processes channels independently at inference [9]; shared weights are not cross-channel mixing.

### 12.2 Two versions

```text
DLinear-C: close only
DLinear-OHLC: four channels, independently projected
```

Do not interpret DLinear-OHLC as proof that O/H/L inform the predicted Close. Add Ridge-OHLC: flatten the same observed OHLC context, train a regularized multi-output linear regression for the 20 future Close values, and select alpha from a small frozen development grid. Fit scaling only on its training windows. Use the same loss target and context in E2; retain DLinear-C as the simple neural comparator.

### 12.3 Training controls

- seed: run at least 5 seeds for train-from-scratch neural models;
- early stopping on a purged development validation partition; refit using the frozen epoch count as specified in Section 8.3;
- fit scaling parameters on training data only;
- save best checkpoint by validation MASE or validation MAE;
- report mean ± standard deviation across seeds.

---

## 13. Chronos implementation

### 13.1 Original Chronos

Use an official `amazon/chronos-t5-mini` checkpoint for the historical general-purpose TSFM baseline.

Primary use:

```text
Input = close-price context
Mode = zero-shot
Output = 20-step forecast distribution / samples
```

Do not fine-tune Chronos in the first paper version unless adaptation becomes a specific secondary research question.

### 13.2 Chronos-2

Use `autogluon/chronos-2-small`, confirmed in the official model listing and model card (28M parameters) [3, 7]. Resolve and freeze its exact revision; never silently substitute the latest checkpoint. Check the exact revision release history and training provenance before selecting evaluation dates.

Purpose:

```text
Input = OHLC multivariate history
Mode = zero-shot
Output = 20-step multivariate forecast
Evaluation = predicted Close component
```

Keep the exact model ID and package commit in the run metadata because the Chronos family is actively evolving.

Treat OHLC as jointly grouped targets, or Close as target with O/H/L as past-only covariates; freeze one choice before testing. Never provide actual future OHLC as known covariates. Prefer the tensor interface for irregular exchange sessions; the inspected DataFrame API expects a regular time grid [10]. Do not fill exchange holidays to satisfy that API. Disable cross-learning across different forecast origins, which could expose later contexts to earlier tasks.

The inspected `predict_quantiles` returns the 0.5 quantile in its variable named `mean` [10]. Record this as a median, not a predictive expectation. For MAE, use median-based point extraction for sampled TSFMs as well. Native-mean comparisons are a separate sensitivity table; do not silently mix mean and median estimands.

---

## 14. Kronos implementation

### 14.1 Primary checkpoint

Use:

```text
Tokenizer: NeoQuasar/Kronos-Tokenizer-base
Model:     NeoQuasar/Kronos-small
max_context: 512
```

The official repository reports Kronos-small at approximately 24.7M parameters with a maximum context of 512.

### 14.2 Primary input

```text
open
high
low
close
```

Do not synthesize volume.

### 14.3 Candidate context lengths

The primary E2 comparison uses 128 sessions for Ridge-OHLC, Chronos-2 and Kronos. Run the following development grid only for a separately labeled best-configuration sensitivity:

```text
64
128
256
512
```

Freeze the selected sensitivity setting before its OOS run; it does not replace the fixed-context E2 result.

### 14.4 Prediction call

Conceptually:

```python
pred_df = predictor.predict(
    df=context_ohlc,
    x_timestamp=context_dates,
    y_timestamp=future_dates,
    pred_len=20,
    T=T_FIXED,
    top_p=TOP_P_FIXED,
    sample_count=N_FIXED,
)
```

Sampling parameters must be tuned on the development validation period and then frozen.

### 14.5 Point forecast definition

Primary MAE uses the sample median at each horizon for Kronos and Chronos-T5, and quantile 0.5 for Chronos-2. Deterministic baselines retain their specified point outputs; describe their fitting loss. Preserve sample means as an optional sensitivity output, not an estimated mean for a quantile-only model.

Kronos public inference averages trajectories [8]. Therefore retain raw paths before aggregation and verify that their mean reproduces the public output within numerical tolerance. Median extraction is a requirement for the primary comparison, even if full probabilistic scoring is deferred. Freeze sample count and use a stable seed derived from run seed and origin date so batching/resume does not change results.

### 14.6 Probabilistic extension

Building on the retained paths required for primary median extraction, add CRPS or interval calibration only after the following checks:

1. instrument/wrap the sampling layer to retain all generated paths;
2. verify that retained paths exactly reproduce the public point forecast when averaged;
3. unit-test shapes and denormalization;
4. only then add probabilistic metrics.

Do not claim probabilistic evaluation based on a single averaged path.

---

## 15. Kronos fine-tuning strategy

The official repository provides a two-stage fine-tuning pipeline:

1. tokenizer fine-tuning;
2. predictor fine-tuning.

For VN30, use a conservative sequence because only one daily index series is available.

### Stage A — zero-shot first

No adaptation.

This establishes whether cross-market pretraining transfers at all.

### Stage B — predictor-only adaptation

Freeze tokenizer:

```text
K-line → pretrained tokenizer (frozen)
      → predictor (fine-tuned on VN30 windows)
```

This is the **primary adaptation experiment** because it reduces overfitting risk and preserves the financial representation learned during pretraining.

### Stage C — full official two-stage adaptation

Fine-tune tokenizer and predictor only after Stage B.

Treat this as an ablation, not the default expected winner.

### Fine-tuning data construction

From training history, generate windows:

```text
context_length = selected context
prediction_length = 20
stride = 1 during training
```

For a series of length $T$, approximate sample count:

$$
N=T-context-prediction+1
$$

Overlapping windows are allowed inside training data but must never cross into validation/test periods.

### Early stopping

Use the disjoint chronological validation partition described in Section 8.3. Hold the tokenizer in eval mode with no gradients for predictor-only adaptation; fit any external transforms only on training. Match normalization/clipping to the inference adapter and test that label/future values do not affect context scaling. Tokenizer and predictor revisions must remain compatible. Never reuse a fixed validation interval once those rows are included in a later training fold.

Never use final test-year loss for early stopping.

---

## 16. Evaluation metrics

### 16.1 Price metrics

#### MAE

$$
MAE=\frac{1}{N}\sum_{i=1}^{N}|y_i-\hat y_i|
$$

#### RMSE

$$
RMSE=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(y_i-\hat y_i)^2}
$$

#### sMAPE

Use one documented implementation and an epsilon guard for the denominator.

#### MASE — primary scale-free metric

Use the nonseasonal one-step in-sample Naive scale:

$$
MASE=\frac{\frac{1}{N}\sum_{i=1}^{N}|y_i-\hat y_i|}
{\frac{1}{T-1}\sum_{t=2}^{T}|y_t-y_{t-1}|}
$$

The denominator must be computed from the **training history only** for each fold.

Interpretation:

```text
MASE < 1 → error is below the training-period one-step Naive scale
This does NOT establish superiority over Naive on the test set or at h=5/20.
```

For actual OOS comparison, report `skill_h = 1 - MAE_model,h / MAE_naive,h` using identical test origins. Positive skill means improvement over the tested Naive forecast. Handle zero denominators explicitly as undefined. Report pooled MAE and origin-weighted MASE, with per-fold scales saved; do not average fold RMSE values to obtain pooled RMSE.

### 16.2 Return metrics

From a predicted close:

$$
\hat r_{t,h}=\log\left(\frac{\hat C_{t+h}}{C_t}\right)
$$

Evaluate:

```text
Return MAE
Return RMSE
Directional Accuracy
```

Directional Accuracy:

$$
DA=\frac{1}{N}\sum_{t=1}^{N}
1[sign(\hat r_{t,h})=sign(r_{t,h})]
$$

Report DA against always-up and previous-return-sign baselines. Define zero-return/prediction ties explicitly as a third class with counts; use the same rule everywhere. Return errors derived from price predictions are a transformed view of the same forecasts, not an independent replication. Do not describe DA > 50% as economically profitable without transaction-cost analysis.

### 16.3 Probabilistic metrics — extended study

Only when comparable forecast distributions are retained:

- pinball loss / WQL;
- CRPS;
- 50%, 80%, 90% interval coverage;
- average interval width.

---

## 17. Statistical significance

A metric table alone is insufficient.

### 17.1 Registered comparisons

Primary family: h=1 absolute-error differences for (a) Kronos zero-shot vs Naive, (b) Kronos zero-shot vs the frozen generic multivariate comparator. Apply Holm correction across these two comparisons. Report effect sizes and paired block-bootstrap 95% CIs with their unadjusted-CI label; infer significance from the adjusted tests, not from those intervals alone.

Secondary family: h=5/20 and adapted-vs-zero-shot, with its comparison list and correction scope frozen before test. All other pairwise/regime analyses are exploratory. A conditional adaptation study need not run to complete the primary benchmark.

### 17.2 Dependence-aware inference

Let `d_t = abs(error_Kronos,t) - abs(error_comparator,t)`; negative favors Kronos. Bootstrap paired vectors of origin-level losses, preserving model pairing and chronological blocks, never individual horizon rows or seeds. For repeated training seeds, average the per-seed loss at each origin before inference and separately report seed dispersion; seeds are not additional market observations or an implicit forecast ensemble.

Use 5,000 moving-block replicates, primary length 20 sessions and sensitivity lengths 10/40 where sample size permits. Construct a centered-null two-sided bootstrap test from resampled `d_t - mean(d)` and separately a percentile CI from resampled uncentered d. Save RNG seed and method. Resample within contiguous evaluation segments; do not join blocks across gaps or protocol changes. Recompute ratio-based skill inside each replicate. Report N and the approximate number of effective blocks; sparse regime cells receive descriptive results only, not strong significance claims.

DM is a secondary robustness check with Newey-West/Bartlett variance and a preregistered bandwidth, initially `max(h-1, floor(4*(N/100)**(2/9)))`. Document finite-sample correction; zero/nonpositive variance yields an undefined test, not an infinite statistic. For non-overlapping-origin sensitivity, report the fixed offset rule, not the offset with the best result.

---

## 18. Volatility-regime analysis

Regime labeling must not use future data.

### 18.1 Realized volatility feature

At forecast origin $t$:

$$
\sigma_t=\mathrm{Std}(r_{t-19},\ldots,r_t)
$$

### 18.2 Threshold calibration

For each fold:

1. calculate 20-day volatility on training history;
2. compute training-only 33rd and 66th percentile thresholds;
3. freeze thresholds;
4. classify test origins into low / medium / high volatility.

Do not calculate quantile thresholds using the full dataset.

### 18.3 Report

For every model and horizon:

```text
metric × low-vol regime
metric × medium-vol regime
metric × high-vol regime
sample count per regime
```

Avoid conclusions for very small regime subsets.

---

## 19. Repository architecture

Recommended repository:

```text
vn30-tsfm-research/
│
├── README.md
├── pyproject.toml
├── uv.lock / requirements-lock.txt
├── .env.example
├── .gitignore
│
├── configs/
│   ├── data.yaml
│   ├── splits.yaml
│   ├── eval.yaml
│   ├── arima.yaml
│   ├── ets.yaml
│   ├── dlinear.yaml
│   ├── chronos_t5.yaml
│   ├── chronos2.yaml
│   ├── kronos_zero_shot.yaml
│   └── kronos_finetune.yaml
│
├── data/
│   ├── raw/                 # immutable, gitignored
│   ├── interim/
│   ├── processed/
│   └── manifests/
│
├── src/
│   ├── data/
│   │   ├── download.py
│   │   ├── validate.py
│   │   ├── preprocess.py
│   │   ├── manifest.py
│   │   └── splits.py
│   │
│   ├── models/
│   │   ├── base.py
│   │   ├── naive.py
│   │   ├── drift.py
│   │   ├── arima.py
│   │   ├── ets.py
│   │   ├── dlinear.py
│   │   ├── ridge_ohlc.py
│   │   ├── chronos_t5.py
│   │   ├── chronos2.py
│   │   └── kronos.py
│   │
│   ├── training/
│   │   ├── dlinear_trainer.py
│   │   └── kronos_finetune.py
│   │
│   ├── evaluation/
│   │   ├── walk_forward.py
│   │   ├── metrics.py
│   │   ├── dm_test.py
│   │   ├── bootstrap.py
│   │   └── regimes.py
│   │
│   └── utils/
│       ├── seed.py
│       ├── logging.py
│       └── io.py
│
├── scripts/
│   ├── 01_fetch_data.py
│   ├── 02_validate_data.py
│   ├── 03_build_dataset.py
│   ├── 04_replicate_zhang2025.py
│   ├── 05_run_baselines.py
│   ├── 06_run_tsfm_zero_shot.py
│   ├── 07_run_kronos_finetune.py
│   ├── 08_run_statistics.py
│   └── 09_build_report_tables.py
│
├── notebooks/
│   ├── 00_data_audit.ipynb
│   ├── 01_replication.ipynb
│   └── 02_error_analysis.ipynb
│
├── tests/
│   ├── test_data_validation.py
│   ├── test_no_leakage.py
│   ├── test_metrics.py
│   ├── test_splits.py
│   └── test_model_io_shapes.py
│
├── artifacts/
│   ├── checkpoints/
│   ├── forecasts/
│   ├── scored/
│   ├── metrics/
│   └── figures/
│
└── reports/
    ├── tables/
    ├── figures/
    └── experiment_log.md
```

---

## 20. Unified model interface

All models should expose the same logical interface.

```python
class ForecastModel:
    def fit(self, train_df, val_df=None):
        ...

    def observe(self, new_rows_df):
        """Append rows not already assimilated; never refit parameters."""
        ...

    def snapshot_state(self):
        """Return restorable state before processing an origin."""
        ...

    def restore_state(self, state):
        """Restore state exactly for deterministic retry/replay."""
        ...

    def predict(self, context_df, future_dates) -> ForecastOutput:
        ...
```

Suggested output:

```python
@dataclass
class ForecastOutput:
    origin_date: pd.Timestamp
    horizon_dates: pd.DatetimeIndex
    point_close: np.ndarray
    point_open: np.ndarray | None = None
    point_high: np.ndarray | None = None
    point_low: np.ndarray | None = None
    samples_close: np.ndarray | None = None
    metadata: dict = field(default_factory=dict)
```

Required invariants:

```text
len(point_close) == len(horizon_dates) == 20
origin_date == max(context_df.date)
all(horizon_dates > origin_date)
metadata records last_assimilated_date and adapter/checkpoint revision
observe() rejects duplicate or non-monotonic rows
snapshot_state()/restore_state() round-trip exactly for stateful adapters
predict() has no access to outcomes or the scored-artifact table
```

This prevents evaluation code from being coupled to a specific library and makes state handling testable.

---

## 21. Walk-forward engine

Pseudo-code (helpers enforce the split manifest, not calendar-year slicing):

```python
config = load_frozen_config()
manifest = load_origin_manifest(config.split_manifest_hash)
model = build_model(config)
model.fit(pretest_refit_data, val_df=None)  # epoch count already frozen
last_assimilated = pretest_refit_data.date.max()

for origin_record in manifest:
    origin = origin_record.origin_date
    observed = data.loc[data.date <= origin]
    context = observed.tail(config.context_length).copy()
    new_rows = observed.loc[observed.date > last_assimilated]
    future_dates = origin_record.target_dates
    assert context.date.max() == origin
    assert min(future_dates) > origin

    state_before_origin = model.snapshot_state()
    forecast = None
    attempts = []
    for attempt in range(2):  # initial attempt + one identical technical retry
        try:
            model.restore_state(state_before_origin)
            model.observe(new_rows)  # no-op for fixed neural/TSFM adapters
            forecast = model.predict(context, future_dates=future_dates)
            validate_forecast(forecast, origin_record)
            attempts.append({"attempt": attempt + 1, "status": "ok"})
            break
        except Exception as exc:
            forecast = None
            attempts.append(capture_failure(attempt + 1, exc))

    if forecast is None:
        model.restore_state(state_before_origin)
        save_failure_rows(config, origin_record, attempts, horizon_count=20)
        continue

    save_forecast_atomic(config, origin_record, forecast, attempts)
    last_assimilated = origin

# Join labels only in evaluation after forecast artifacts are saved.
```

The manifest is iterated strictly by origin date. `new_rows` may be empty only at the first origin. A stateful adapter must assert that no date is assimilated twice and that its state ends at the current origin before forecasting. Retry restores the pre-origin state before replaying identical inputs. After a failed origin, later origins replay every row since `last_assimilated`; failure never advances model state. Forecast writes are atomic, and an unresolved origin writes exactly 20 null-valued failure rows with both attempt records.

Neither an adapter nor the sampling layer receives the outcome table. Resume keys include run ID, checkpoint revision, origin and seed; config mismatches must fail instead of reusing cached predictions. State restoration/replay must yield the same forecasts as an uninterrupted run.

---

## 22. Experiment configuration

Example YAML:

```yaml
experiment_id: E2_kronos_small_ohlc_zero_shot
seed: 42

data:
  asset: VN30
  frequency: 1D-trading
  features: [open, high, low, close]
  target: close

forecast:
  horizon: 20
  evaluate_steps: [1, 5, 20]
  context_length: 128
  point_functional: median
  selection_metric: close_mae_h1
  origin_manifest_hash: <required>

model:
  family: kronos
  checkpoint: NeoQuasar/Kronos-small
  tokenizer: NeoQuasar/Kronos-Tokenizer-base
  checkpoint_revision: <required_immutable_sha>
  tokenizer_revision: <required_immutable_sha>
  provenance_manifest: <required_path>
  max_context: 512
  mode: zero_shot
  temperature: <frozen_from_dev>
  top_p: <frozen_from_dev>
  sample_count: <frozen_from_dev>
  temporal_encoding: <required_adapter_description>

evaluation:
  metrics: [mae, rmse, smape, mase, return_mae, return_rmse, da]
  primary_endpoint: close_mae_h1
  evidence_track: primary_retrospective
  split_manifest: <required_path>
  dm_test: secondary
  block_bootstrap: true
  bootstrap_replicates: 5000
  primary_block_length: 20
  multiplicity: holm_two_primary_comparisons
```

Angle-bracket values are unresolved planning fields. A config validator must reject execution until all are resolved, provenance/split gates pass, and the expanded config is saved. Every results row must be reconstructible from config, dataset/split/checkpoint manifests and a code commit (plus a diff hash if the tree is dirty).

---

## 23. Experiment tracking and reproducibility

### Minimum stack

```text
Git
Python virtual environment / uv
PyTorch
pandas / numpy
statsmodels
scikit-learn
SciPy
official Chronos package
official Kronos code/checkpoints
pytest
MLflow or equivalent local experiment tracker
```

### Record per run

```text
git commit
python version
package lock hash
CUDA version
GPU name
model checkpoint ID
immutable model and tokenizer revisions (mandatory)
checkpoint provenance and eligibility status
calendar version and split/origin manifest hashes
point functional and normalization policy
dataset SHA256
config file
random seed
start/end time
runtime
peak GPU memory if measurable
forecast artifact
scored artifact
metrics file
```

### Seeds

- Deterministic statistical/zero-shot inference: fixed seed where sampling is involved.
- DLinear final result: exactly **5 preregistered seeds**; average origin-level loss across seeds for model-level inference and report seed dispersion separately.
- Fine-tuned Kronos: **5 preregistered seeds** if included as a confirmatory secondary result; otherwise label a smaller-seed run exploratory.
- Seeds never count as additional market observations.

---

## 24. Forecast and scored artifact formats

Keep label-free forecasts separate from evaluation outputs.

### 24.1 Forecast artifact

One row per attempted origin × horizon × model, written before labels are joined:

```text
run_id, model, fold, origin_date, target_date, horizon
predicted_close, predicted_log_return, predicted_direction
seed, status, failure_reason, point_functional
checkpoint_revision, dataset_hash, split_hash, config_hash
last_assimilated_date
```

Store as:

```text
artifacts/forecasts/<run_id>.parquet
```

For failed origins, retain all identity/status fields and null forecast values. Sample paths, when available, are stored in a separate run-keyed array artifact rather than duplicated across rows.

### 24.2 Scored artifact

The evaluation command validates forecast coverage and hashes, then joins immutable labels and training-only metadata to create:

```text
all forecast fields
actual_close, actual_log_return, actual_direction
absolute_error, squared_error, return_error
volatility_regime, training_mase_scale
```

Store as:

```text
artifacts/scored/<run_id>.parquet
```

Do not compute paper tables from in-memory outputs or raw model objects. Generate every metric, test, table and figure from validated scored artifacts.

---

## 25. Primary result tables

### Table A — Overall price forecasting

```text
Model | h | MAE | RMSE | sMAPE | MASE | 95% CI
```

### Table B — Return forecasting

```text
Model | h | Return MAE | Return RMSE | Directional Accuracy
```

### Table C — Statistical comparison

```text
Model A | Model B | h | loss | mean Δloss | 95% CI | test | raw p | adjusted p
```

### Table D — Regime analysis

```text
Model | h | regime | N | MASE | Return RMSE | DA
```

### Table E — Adaptation efficiency

```text
Model | adaptation data | h | MASE | Δ vs zero-shot
```

### Table F — Compute cost

```text
Model | parameters | train time | inference time/origin | peak VRAM
```

This prevents claiming an accuracy gain without showing its computational cost.

---

## 26. Figures

Core figures:

1. VN30 full historical close series with fold boundaries.
2. Return and rolling-volatility series.
3. Example 20-day forecasts for representative test origins.
4. MASE by model and horizon.
5. Relative improvement over Naive.

Conditional figures:

6. Kronos vs generic TSFM error by volatility regime, only if the secondary regime analysis runs.
7. Data-efficiency curve, only if the optional adaptation-data study runs.
8. Calibration/interval plot, only if probabilistic evaluation is implemented correctly.

Never choose only visually favorable forecast periods. Example origins must be selected by a preregistered rule or include both typical and failure cases.

---

## 27. Error analysis

For the largest Kronos errors, automatically generate a case file containing:

```text
origin date
20-day context OHLC
20-day true future
20-day predicted future
absolute errors
return errors
regime
recent volatility
recent drawdown
```

Then classify failure patterns such as:

- sudden regime shift;
- extreme gap;
- long directional trend;
- reversal;
- high-volatility transition;
- unusually narrow volatility period followed by breakout.

These labels are descriptive analysis, not training features in v1.

---

## 28. Unit and integration tests

### Data tests

- duplicate dates rejected;
- OHLC inequalities checked;
- sorted chronology enforced;
- test split never appears in scaler fitting;
- rolling features use only past values.

### Split tests

```text
max(train_window.target_dates) <= train_end
min(validation_window.target_dates) >= validation_start
max(validation_window.target_dates) <= validation_end
max(refit_window.target_dates) < min(test_target_dates)
all(context_dates <= origin_date < target_dates)
```

for every fold.

### Metric tests

Use small arrays with hand-computable expected MAE/RMSE/MASE.

### Model adapter tests

For each model:

```text
input context has expected schema
output length == 20
no NaN predictions
predicted target dates match expected trading dates
```

Additional adapter checks:

- changing future OHLC leaves earlier forecasts unchanged;
- changing O/H/L while holding Close fixed exercises the Ridge/TSFM multivariate input path; document DLinear's expected channel independence;
- Kronos amount survives preprocessing when explicit zero volume is supplied;
- returned mean/median labels match computed sample summaries;
- statistical state reaches each current origin; repeated observations are not applied twice;
- holidays/year boundaries preserve exact target session IDs;
- failure/retry/resume preserves origin coverage, RNG behavior and pre-origin state;
- an unresolved origin produces exactly 20 failure rows and later origins replay unassimilated observations correctly;
- raw forecast artifacts contain no actual outcomes;
- scored artifacts join labels only after run/config/hash and complete-origin validation;

### Reproducibility test

A zero-shot run with fixed seed and the same package/checkpoint revision should reproduce predictions within a documented numerical tolerance.

---

## 29. Compute plan

### Phase 1 — CPU-compatible work

- data acquisition;
- validation;
- EDA;
- Naive;
- ETS;
- ARIMA;
- metric/statistics pipeline.

### Phase 2 — single-GPU work

- DLinear;
- Chronos zero-shot;
- Chronos-2 zero-shot;
- Kronos-small zero-shot.

### Phase 3 — adaptation

- Kronos predictor-only fine-tuning;
- optional full tokenizer + predictor fine-tuning;
- optional base-size robustness models.

Actual GPU memory requirements should be measured in an initial smoke benchmark rather than assumed. Record batch size, precision and peak VRAM.

Use mixed precision only after confirming numerical stability.

---

## 30. Execution phases

### Phase 0 — research freeze and environment

**Tasks**

- create repository;
- lock research questions;
- retrieve baseline paper PDF;
- extract exact ARIMA/ETS protocol;
- test Chronos and Kronos official repositories;
- freeze initial package environment.

**Exit criteria**

- required core models load with immutable revisions; checkpoint-provenance manifest defines eligible dates;
- one dummy forecast works;
- replication manifest exists.

---

### Phase 1 — data acquisition and audit

**Tasks**

- collect VN30 daily OHLC;
- create immutable raw snapshot;
- cross-check dates/close levels;
- audit missing days and OHLC consistency;
- build dataset manifest.

**Exit criteria**

- data-source acceptance gate passes;
- no unexplained duplicate dates;
- sample source verification completed.

---

### Phase 2 — published baseline replication

**Tasks**

- reproduce the 2016–2023 close series;
- implement exact ARIMA/ETS specification where possible;
- compare reproduced and reported metrics;
- document every unresolved discrepancy.

**Exit criteria**

- either replication is successful, or non-reproducibility is explicitly documented with reasons.

Do not block the new study indefinitely if the original paper omits critical details.

---

### Phase 3 — evaluation framework

**Tasks**

- build walk-forward engine;
- implement metrics;
- implement MASE correctly;
- implement return transformation;
- implement the primary bootstrap/Holm pipeline;
- implement volatility regimes only for the secondary analysis;
- write leakage tests;
- persist label-free forecast and scored artifacts.

**Exit criteria**

- Naive forecasts can run end-to-end across all folds;
- tables can be regenerated from saved scored Parquet artifacts and the referenced frozen manifests, without running model inference again.

---

### Phase 4 — classical + neural baselines

**Tasks**

- Naive;
- Drift;
- ETS;
- ARIMA;
- DLinear;
- Ridge-OHLC.

**Exit criteria**

- baseline table complete;
- all hyperparameters frozen from development period.

---

### Phase 5 — zero-shot TSFM benchmark

**Tasks**

- mandatory: frozen generic multivariate TSFM OHLC;
- mandatory: Kronos-small OHLC;
- mandatory: freeze inference/sampling config and run the provenance-qualified common holdout;
- optional: Chronos-T5-mini close-only and E1;
- optional: best-configuration context-length sensitivity;
- keep historical diagnostics in a separate artifact namespace.

**Exit criteria**

- mandatory E2 and baseline ladder complete;
- zero-shot TSFM forecasts and scored artifacts persisted;
- no test-informed tuning.

This is the first complete main benchmark. Publication readiness still depends on sufficient holdout length, provenance, uncertainty and an updated related-work review.

---

### Phase 6 — Kronos ablations and adaptation

**Tasks**

- OHLC-only vs OHLC + validated trading value;
- zero-shot vs predictor-only fine-tuning;
- optional full two-stage fine-tuning;
- 1y / 3y / 5y / full adaptation-data study.

**Exit criteria**

- selected feasible adaptation cells complete, or optional study explicitly deferred with reason;
- any overfitting clearly reported;
- tokenizer fine-tuning is not presented as beneficial unless OOS evidence supports it.

---

### Phase 7 — statistical tests and robustness

**Tasks**

- mandatory: registered paired block-bootstrap tests/CIs and Holm correction;
- secondary: DM tests and regime analysis;
- optional: context-length and non-overlapping-origin sensitivities.

**Exit criteria**

- all major claims supported by uncertainty/statistical evidence.

---

### Phase 8 — paper artifacts

**Tasks**

- freeze dataset/model/code revisions;
- generate all tables automatically;
- generate figures automatically;
- write methodology from configs, not memory;
- publish reproducibility instructions.

---

## 31. Proposed 6–8 week schedule

| Week | Goal | Deliverable |
|---|---|---|
| 1 | environment + data source + baseline extraction | data/replication manifests |
| 2 | data audit + Zhang replication | replication report |
| 3 | walk-forward/evaluation + classical baselines | baseline table |
| 4 | DLinear-C + Ridge-OHLC + Chronos-2 + Kronos zero-shot | main zero-shot benchmark; Chronos-T5 optional in minimal scope |
| 5 | finish core QA; optional Kronos adaptation | verified main table; adaptation table if feasible |
| 6 | primary bootstrap/Holm inference; secondary DM/regime if feasible | statistical results |
| 7 | robustness + failure analysis | final figures/tables |
| 8 | paper/reproducibility cleanup | research package |

If resources are limited, finish the zero-shot core, uncertainty analysis and reproducibility package first. Adaptation, data-efficiency and probabilistic scoring may be deferred. A six-week schedule cannot manufacture a sufficiently long uncontaminated holdout; report a pilot if the date gate fails.

---

## 32. Decision gates

### Gate A — OHLC source quality

If reliable historical VN30 OHLC cannot be obtained reproducibly:

- do not invent OHLC from Close;
- do not proceed with Kronos as if data were genuine K-lines;
- resolve the source first.

### Gate B — baseline reproducibility

If Zhang (2025) cannot be exactly reproduced because the paper does not disclose enough detail:

- report it as an approximate replication;
- maintain the paper as literature baseline;
- use the new walk-forward protocol as the primary experimental protocol.

### Gate C — generic multivariate comparator

If Chronos-2 multivariate support is unstable in the locked environment:

- substitute Moirai as the preregistered generic multivariate TSFM;
- make the substitution before final test execution.

### Gate D0 — checkpoint chronology and sample size

If weight provenance is unknown or the common clean holdout is too short, retain exploratory results with that label and begin prospective collection. Do not claim clean OOS from the old 2021-2024 folds. Comparator substitution must pass both adapter and chronology gates before testing.

### Gate D — Kronos fine-tuning

If predictor-only adaptation overfits development validation:

- do not proceed automatically to full tokenizer fine-tuning;
- keep zero-shot Kronos as the main result.

---

## 33. Claims that the study may and may not make

### Allowed if supported by results

- Kronos has lower/higher OOS forecasting error than named baselines under the defined protocol.
- Domain-specific pretraining is associated with different transfer performance than generic TSFMs in this experiment.
- Performance changes across horizons/regimes.
- Fine-tuning requires a certain amount of VN30 data before helping under this protocol.

### Avoid without additional experiments

- “Kronos understands the Vietnamese market.”
- “K-line tokenization is the sole reason Kronos wins.”
- “The model is profitable.”
- “The model predicts market crashes.”
- “Kronos is universally superior to classical forecasting.”
- “A low price RMSE proves return predictability.”

The strongest causal claim about tokenization requires input control and ideally additional representation ablations.

---

## 34. Minimum complete experiment set

This is the definition of a complete core study. Anything below marked secondary may be omitted without making the primary paper incomplete.

```text
Data:
VN30 daily OHLC

Horizons:
1 / 5 / 20 sessions

Protocol:
checkpoint-qualified development/holdout from Section 8
historical 2021+ folds diagnostic only

Models:
Naive
ARIMA
ETS
DLinear-C
Ridge-OHLC
frozen generic multivariate TSFM OHLC (Chronos-2-small, or Gate C substitute)
Kronos-small OHLC

Mode:
zero-shot for both TSFMs

Metrics:
MAE
RMSE
MASE
Return RMSE
Directional Accuracy

Analysis:
paired block-bootstrap CI/test + Holm for primary family
```

Secondary additions, in order: predictor-only Kronos adaptation, DM robustness, volatility regimes. Chronos-T5, trading value, full tokenizer adaptation, data-efficiency curves and probabilistic scoring are optional.

The core study is complete only when every mandatory model has either valid forecasts for every common origin or an explicitly reported failure table. Models are never compared on different subsets of successful origins.

---

## 35. Success criteria

The project is considered technically successful even if Kronos does not win, provided that:

- the data pipeline is reproducible;
- no future-data leakage is found;
- a published VN30 baseline is reproduced or its reproducibility limitations are documented;
- all models are evaluated on identical OOS forecast origins;
- generic-vs-financial TSFM comparison controls input information;
- uncertainty/statistical significance is reported;
- negative results are preserved rather than tuned away;
- every final number can be traced to a dataset hash, config and code commit.

Research success is **knowledge about transfer**, not a predetermined winning model.

---

## 36. Immediate implementation backlog

Execute in this order:

```text
[ ] 01. Extract Zhang protocol into replication manifest; use `not reported` for missing fields
[ ] 02. Resolve exact TSFM/tokenizer revisions and provenance boundary B; generate holdout feasibility artifact
[ ] 03. Lock environment; prove each mandatory adapter can produce one 20-step forecast
[ ] 04. Select and cross-check a VN30 OHLC source; pass G1
[ ] 05. Freeze raw snapshot, processed dataset, calendar and hashes
[ ] 06. Build validation/test target intervals and the common full-path origin manifest
[ ] 07. Confirm at least 126 primary origins; otherwise classify the study as a pilot
[ ] 08. Implement label-free forecast artifacts, label join and leakage/metric tests
[ ] 09. Run Naive end-to-end and regenerate one scored table only from artifacts
[ ] 10. Reproduce/approximate ARIMA and ETS; preserve discrepancy log
[ ] 11. Add DLinear-C and Ridge-OHLC; select with development validation only
[ ] 12. Validate generic multivariate TSFM and Kronos OHLC adapters against identical inputs
[ ] 13. Freeze every expanded config, seed list and manifest hash
[ ] 14. Run mandatory zero-shot holdout once; retain every failure
[ ] 15. Run registered bootstrap tests and generate core tables/figures
[ ] 16. Add predictor-only adaptation and other secondary analyses only after core completion
[ ] 17. Freeze the reproducibility package and write paper claims from saved artifacts
```

---

## 37. Recommended first implementation milestone

Do **not** start by fine-tuning Kronos.

The first end-to-end milestone should be:

```text
VN30 raw OHLC
      ↓
validated immutable dataset
      ↓
provenance-qualified holdout/origin manifest
      ↓
Naive / ARIMA / ETS
      ↓
Chronos-2 zero-shot
      ↓
Kronos-small zero-shot
      ↓
MAE h=1 + Naive-relative skill + secondary metrics
      ↓
paired block-bootstrap uncertainty
```

Only after this works reproducibly should fine-tuning be introduced.

This sequencing separates implementation bugs from adaptation effects and gives the study a strong baseline before adding complexity.

---

## 38. References / implementation sources

1. **HOSE-INDEX Ground Rule, Version 4.0.** Ho Chi Minh Stock Exchange. VN30 is defined as a 30-constituent free-float-adjusted market-capitalization index with periodic review/capping rules.  
   https://staticfile.hsx.vn/Uploads/LocalFiles/ef15ff11e799483abd11677ad0443887/20250114_20241230_QD%20747%20HOSE%20Index%20Ground%20Rules.pdf

2. **Zhang, H. (2025).** *Vietnam V30 Closing Price Forecast Based on ARIMA and ETS.* Advances in Economics, Management and Political Sciences, 147, 29–34. DOI: 10.54254/2754-1169/2024.GA19104.  
   https://aemps.ewapub.com/article/view/19104

3. **Ansari et al. — Chronos.** Official Amazon Science implementation. The original Chronos family scales and quantizes time-series values into tokens; the current repository also contains Chronos-Bolt and Chronos-2.  
   https://github.com/amazon-science/chronos-forecasting

4. **Shi et al. — Kronos: A Foundation Model for the Language of Financial Markets.** Official implementation. Kronos uses a financial K-line tokenizer and autoregressive Transformer; the repository provides OHLC-only inference support and fine-tuning scripts.  
   https://github.com/shiyu-coder/Kronos

5. **Kronos AAAI 2026 paper.**  
   https://ojs.aaai.org/index.php/AAAI/article/view/39730

6. **Kronos extended paper, Appendix D.** Pretraining cutoff and forecasting setup.  
   https://arxiv.org/html/2508.02739v1

7. **Chronos-2-small model card.** Exact model ID and size; release/cutoff audit remains required per revision.  
   https://huggingface.co/autogluon/chronos-2-small

8. **Kronos predictor source.** Optional-column preprocessing and sample aggregation.  
   https://raw.githubusercontent.com/shiyu-coder/Kronos/master/model/kronos.py

9. **Official DLinear implementation.** Channel-independent temporal linear projections.  
   https://raw.githubusercontent.com/cure-lab/LTSF-Linear/main/models/DLinear.py

10. **Chronos-2 pipeline source.** Quantile/point semantics, covariates and timestamp constraints.  
    https://raw.githubusercontent.com/amazon-science/chronos-forecasting/main/src/chronos/chronos2/pipeline.py

11. **Huynh et al. (2024), Anomaly Detection For Vietnamese Financial Market.** ACOMPA, DOI 10.1109/ACOMPA64883.2024.00016. Prior Moirai/VN30 work must be discussed; this study must not claim the first VN30 TSFM application.  
    https://ieeexplore.ieee.org/document/10818343/

Sources 3 and 6-10 checked during the 2026-09-26 review. Mutable source URLs document the review only; implementation must record resolved commits. This review did not download weights, validate a VN30 provider or run model experiments.

---

# Final technical recommendation

Freeze the paper around one primary controlled experiment:

$$
\boxed{
\text{Chronos-2 (generic multivariate TSFM, OHLC)}
\quad vs \quad
\text{Kronos (finance-specific TSFM, OHLC)}
}
$$

with Naive, ARIMA, ETS, DLinear-C and Ridge-OHLC providing the historical/statistical/train-from-scratch ladder beneath them.

After the primary zero-shot benchmark, optionally use **predictor-only fine-tuning → full fine-tuning** to determine whether any Kronos advantage comes from pretrained transfer and whether VN30-specific adaptation improves it.

The key methodological principle is:

> **Control information, control time, freeze decisions before testing, and treat a negative Kronos result as a valid research result.**

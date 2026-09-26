# Agent Implementation Plan — VN30 Kronos Research Repository Hardening & Phase 1

**Target repository:** `HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting`  
**Reviewed baseline:** `main` @ `042854edc64156caea96a9a849b034c7c5c4bed5`  
**Plan status:** implementation-ready, revised after repository update on 2026-09-26  
**Primary goal:** remediate reproducibility/provenance gaps found in the repository review, then implement the Phase 1 data foundation without violating the frozen research contract.

---

## 0. Agent operating contract

This file is an execution plan, not a redesign proposal. The agent must preserve the scientific intent already frozen in `configs/study.yaml` and `docs/VN30_TSFMs_Kronos_Technical_Implementation_Plan.md`.

### 0.1 Do not do these things

The agent MUST NOT:

1. Run the primary VN30 holdout benchmark before G1–G4 pass.
2. Inspect final-test model metrics and then change:
   - the provenance boundary;
   - dataset cleaning rules;
   - forecast origins;
   - context length;
   - model choice;
   - inference/sampling parameters;
   - checkpoint revisions.
3. Replace the official HOSE session calendar with a weekday/business-day approximation.
4. Fabricate VN30 stock-style volume.
5. Treat zero `volume` / zero `amount` passed to Kronos as observed market data.
6. Change the two registered primary comparisons without explicitly versioning the study contract.
7. Fine-tune Kronos before the zero-shot evaluation pipeline works end-to-end.
8. Delete negative results, failed origins, retries, or data discrepancies.
9. Infer undocumented details from Zhang (2025) to make the replication fit.
10. Commit generated raw/processed market data unless licensing and repository policy explicitly permit it.

### 0.2 Scientific invariants that must remain true

The implementation must preserve:

```text
Primary object:          VN30 price index
Frequency:               HOSE exchange sessions
Primary observed input:  OHLC
Forecast path:           20 sessions
Evaluated horizons:      1 / 5 / 20
Primary endpoint:        pooled Close MAE at h=1
Primary model:           Kronos-small zero-shot
Primary comparisons:     Kronos vs Naive
                         Kronos vs generic multivariate TSFM
Primary TSFM comparator: Chronos-2-small unless Gate C is explicitly exercised
Common E2 context:       identical 128-session OHLC history
Point functional:        median for sampled/quantile TSFMs
Primary inference:       paired moving-block bootstrap
Multiplicity:            Holm over the two registered primary tests
```

### 0.3 Implementation principle

Every result used in a paper claim must be traceable through:

```text
code commit
   +
clean/dirty repository state
   +
dependency lock hash
   +
dataset hash
   +
calendar hash
   +
split/origin hash
   +
model/checkpoint revision
   +
expanded config hash
   +
forecast artifact hash
   +
scored artifact hash
```

If any link is missing, the result is not publication-grade evidence.

---

# 1. Current repository state

Phase 0 is implemented and reported as complete:

- T001 — study contract: complete.
- T002 — Zhang (2025) protocol extraction: complete.
- T003 — checkpoint/tokenizer provenance: complete.
- T004 — software environment + external-model smoke tests: complete.
- G2: passed.
- G1, G3, G4: pending.

Current repository strengths:

- immutable model revisions are recorded;
- model weights are SHA256-verified;
- Chronos-2 and Kronos can execute on the target CUDA environment;
- the research protocol explicitly addresses leakage, test-informed tuning, paired origins, uncertainty, and negative results;
- small Phase-0 evidence artifacts are now committed under `artifacts/smoke/`;
- a preliminary VN30 multi-provider audit exists in `scripts/audit_vn30_sources.py`;
- preliminary cross-check output exists at `data/manifests/source_crosscheck.parquet`;
- provider retrieval metadata and response hashes are recorded in `artifacts/source_audit/retrieval.json`.

Important findings from the newly pushed files:

- `VPS` currently has 3,676 raw rows, 24 duplicate entries covering 24 ambiguous dates, and 12 OHLC-inequality failures after duplicate-date exclusion. It must **not** be accepted as the primary source without investigation.
- `VNDIRECT` has no duplicate/OHLC-inequality failures in the current audit but begins at 2017-08-24.
- `DNSE` has no duplicate/OHLC-inequality failures in the current audit but begins at 2020-05-11.
- The current audit hardcodes `VPS` as the primary source and therefore is exploratory evidence, not yet a valid G1 acceptance decision.
- `tmp/official/*` and `tmp/hf-history/*` are tracked as Git gitlinks (`mode 160000`) while the repository has no `.gitmodules`; these are not reproducible submodules and should not remain in the tracked tree in their current form.
- `tmp/pdfs/` contains the Zhang paper and rendered page images. The PDF may be retained only under an intentional reference-data policy with license/attribution; rendered PNG pages are regenerable evidence and should not live under a tracked `tmp/` directory.
- `.gitignore` no longer protects `tmp/`, `data/raw/`, `data/interim/`, `data/processed/`, or large future experiment outputs, creating a high risk of accidentally committing raw datasets, caches, and large forecast artifacts.

Current implementation gaps that this plan must fix:

1. Repository hygiene must be restored before further implementation: remove/relocate tracked `tmp` gitlinks and regenerable temporary files, and restore selective ignore rules.
2. Phase-0 smoke execution was recorded against an earlier HEAD while the executed files were not yet committed.
3. The vendored Kronos checkout verifies HEAD revision but not working-tree cleanliness.
4. Model revisions are duplicated between manifest files and Python constants.
5. Artifact policy must distinguish **small canonical evidence committed to Git** from **large generated artifacts kept outside Git but hash-registered**.
6. `reports/experiment_log.md` is required by the protocol but missing.
7. README reproduction commands are less strict than the completion report.
8. No automated tests / CI currently protect the research invariants.
9. Research wording can overstate that *all* models receive identical information; the controlled-information claim actually applies to E2.
10. Zero-valued Kronos `volume`/`amount` placeholders need explicit semantics.
11. The preliminary source audit must be formalized before G1: acceptance criteria/config were not independently frozen before the already-produced audit results, provider choice is still unresolved, and exact raw audit responses are not preserved.
12. G3 cannot be declared passed until the official HOSE calendar and sufficient post-boundary sessions exist.
13. Phase 1 raw snapshot, calendar, processed dataset, and split/origin infrastructure still do not exist.

---

# 2. Required implementation order

Execute in this exact order unless a task explicitly says it may be parallelized:

```text
A0. Restore repository hygiene and classify newly pushed evidence
        ↓
A. Harden Phase-0 reproducibility
        ↓
B. Clarify machine-readable research contract
        ↓
C. Establish package/test/CI foundation
        ↓
D0. Formalize the existing exploratory source audit
        ↓
D. Complete Phase-1 data acquisition and manifests
        ↓
E. Compute holdout feasibility / Gate G3
        ↓
STOP before primary model evaluation
```

The agent must not jump directly to Chronos/Kronos benchmark code.

---

# 3. Phase A — Harden Phase-0 reproducibility

## A000 — Restore repository hygiene after the local-file push

### Problem

The latest commit intentionally exposed useful local evidence, but it also tracked files that should not remain as normal repository content:

```text
tmp/official/Kronos                  # gitlink, no .gitmodules entry
tmp/official/chronos-forecasting     # gitlink, no .gitmodules entry
tmp/hf-history/*                     # gitlinks, no .gitmodules entries
tmp/pdfs/*.png                       # regenerable render outputs
```

The current `.gitignore` also stopped ignoring future raw/processed datasets and large generated outputs.

### Required changes

1. Restore selective ignore rules:

```gitignore
# Disposable/local audit material
tmp/

# Local model/runtime caches
.vendor/
.cache/

# Market data bytes; manifests stay tracked
data/raw/
data/interim/
data/processed/

# Large generated experiment outputs
artifacts/forecasts/
artifacts/scored/
artifacts/checkpoints/
artifacts/samples/
artifacts/cache/
```

2. Keep small canonical evidence trackable, including:

```text
artifacts/smoke/*.json
artifacts/source_audit/*.json
data/manifests/*.yaml
data/manifests/*.json
data/manifests/source_crosscheck.parquet
```

3. Remove the current `tmp/*` gitlinks from the tracked tree. Do **not** rewrite public history unless there is a separate licensing/security reason; removing them in the next commit is sufficient.

4. Do not convert the current `tmp/*` gitlinks into submodules merely to preserve them. The project already records immutable revisions in manifests and has a bootstrap path for executable Kronos code. A submodule adds another dependency mechanism without adding scientific provenance.

5. Decide the Zhang paper policy explicitly:
   - preferred: keep only DOI/URL/SHA256 + extraction notes in manifests/reports; remove the local PDF/page PNGs from the tracked tree;
   - acceptable alternative: move the licensed source PDF to `references/zhang_2025/`, add attribution/license metadata, and remove the regenerable page PNGs.

6. Add a repository test that fails if an unregistered gitlink is introduced:

```text
all mode-160000 entries must have an intentional .gitmodules mapping
OR
no mode-160000 entries are allowed
```

For this repository, the simpler preferred invariant is: **no gitlinks/submodules in v1**.

### Acceptance criteria

- `tmp/` is absent from the tracked tree.
- `git ls-files -s` contains no mode `160000` entries.
- small Phase-0/source-audit evidence remains tracked.
- future raw/processed VN30 data and large forecast/scored artifacts cannot be accidentally added by a normal `git add .`.
- the repository still contains enough metadata to resolve every official source/checkpoint revision.

## A001 — Create a central provenance/config loader

### Problem

Checkpoint identifiers and revisions are currently duplicated in:

- `data/manifests/checkpoint_provenance.yaml`
- `scripts/smoke_models.py`
- potentially future model adapters.

This can create silent configuration drift.

### Required changes

Create:

```text
src/vn30_tsfm/
    __init__.py
    provenance.py
```

`provenance.py` must:

1. load `data/manifests/checkpoint_provenance.yaml`;
2. validate required fields;
3. expose immutable typed records for:
   - Chronos-2-small;
   - Kronos-small;
   - Kronos-Tokenizer-base;
   - pinned Kronos implementation revision;
4. reject:
   - missing revisions;
   - mutable branch names such as `main`, `master`, `latest`;
   - malformed SHA-like Git revisions where an immutable Git revision is expected;
   - missing weights SHA256 or size;
5. make the manifest the source of truth for scripts and future adapters.

Suggested public interface:

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class HFComponent:
    repository: str
    revision: str
    weights_file: str
    weights_sha256: str
    weights_size_bytes: int

@dataclass(frozen=True)
class KronosCodeRevision:
    repository: str
    revision: str

def load_checkpoint_provenance(
    path: Path | None = None,
) -> ...:
    ...
```

### Modify

- `scripts/smoke_models.py`
- `scripts/verify_checkpoint_provenance.py`

Remove duplicated hardcoded model/checkpoint revisions and load them through the new module.

### Acceptance criteria

- There is exactly one executable source of truth for model/tokenizer revisions.
- Changing a revision in the manifest changes what smoke scripts load.
- Invalid/mutable revisions fail before any model is downloaded.
- Unit tests cover valid and invalid provenance manifests.

---

## A002 — Harden `bootstrap_kronos.ps1`

### Problem

Current validation:

```powershell
git rev-parse HEAD
```

proves the checkout points at the pinned commit but does **not** prove that tracked files are unmodified.

A locally edited `model/kronos.py` could execute while HEAD still reports the official pinned SHA.

### Required behavior

`bootstrap_kronos.ps1` must establish:

```text
resolved HEAD == manifest revision
AND
tracked working tree clean
AND
no unexpected untracked executable files influence imports
```

### Required implementation

Refactor the script so the revision is read from the central manifest rather than duplicated.

Recommended behavior:

```text
if checkout missing:
    clone repository

fetch pinned revision
checkout --detach pinned revision
reset --hard pinned revision
clean generated/untracked repository files according to a safe policy
verify HEAD
verify git status --porcelain
fail if dirty
```

Preferred safety model:

- `.vendor/Kronos` is treated as disposable;
- no user-authored files should live under it;
- `git clean` must operate only inside `.vendor/Kronos`.

The script MUST NOT run a broad `git clean` against the research repository itself.

### Add a machine-readable verification output

Write:

```text
artifacts/smoke/kronos_source_verification.json
```

with at least:

```json
{
  "repository": "...",
  "expected_revision": "...",
  "resolved_revision": "...",
  "git_status_clean": true,
  "verified_at_utc": "...",
  "status": "pass"
}
```

### Acceptance criteria

- A modified tracked file in `.vendor/Kronos` is reset or causes a deterministic failure.
- After bootstrap, `git status --porcelain` inside `.vendor/Kronos` is empty.
- The resolved revision equals the manifest revision.
- Verification output is generated.
- Unit/integration test or documented manual test demonstrates dirty-tree handling.

---

## A003 — Record repository execution identity

### Problem

Phase-0 reports currently identify a Git commit, but the previous smoke execution occurred before the Phase-0 implementation files themselves were committed.

### Create

```text
src/vn30_tsfm/runtime_identity.py
```

It should collect:

```text
repository_commit
repository_is_dirty
dirty_paths                # optional but strongly recommended
uv_lock_sha256
study_config_sha256
checkpoint_manifest_sha256
python_version
platform
torch_version
cuda_available
cuda_device_name
execution_timestamp_utc
```

### Rules

For evidence-producing commands:

- dirty repository state must be recorded;
- publication-grade runs should fail by default when the repository is dirty;
- development/smoke commands may allow `--allow-dirty`, but the output must prominently record that status.

Suggested helper:

```python
def collect_runtime_identity(
    repo_root: Path,
    require_clean: bool = True,
) -> dict:
    ...
```

### Modify

Use this helper in:

- `scripts/verify_checkpoint_provenance.py`
- `scripts/smoke_models.py`
- all later data/evaluation commands.

### Acceptance criteria

- Every generated evidence JSON includes repository commit and clean/dirty state.
- Running with an uncommitted tracked change fails when `require_clean=True`.
- `uv.lock` hash is computed at runtime rather than copied manually into reports.

---

## A004 — Create artifact hashing and registry infrastructure

### Problem

The latest commit now tracks small evidence under `artifacts/`, which is useful. However, the future benchmark will create much larger forecast/scored/sample/checkpoint outputs that should not all be committed to Git. The repository therefore needs a **hybrid artifact policy**, not an all-tracked or all-ignored policy.

### Create

```text
src/vn30_tsfm/artifacts.py
data/manifests/artifact_registry.yaml
```

The registry should track metadata, not necessarily large artifact bytes.

Minimum entry:

```yaml
- artifact_id: phase0_model_smoke_<timestamp-or-run-id>
  kind: smoke_test
  path: artifacts/smoke/phase0_model_smoke.json
  sha256: ...
  size_bytes: ...
  created_at_utc: ...
  code_commit: ...
  code_dirty: false
  config_hash: ...
  checkpoint_manifest_hash: ...
  status: accepted
```

Provide utilities:

```python
sha256_file(path)
register_artifact(...)
verify_registered_artifact(...)
```

### Important rule

Never silently overwrite an accepted artifact.

If a path already exists:

- either use a new run ID/path;
- or fail unless the command is explicitly a development-only artifact.

Primary holdout artifacts later must be immutable by design.

### Acceptance criteria

- All Phase-0 evidence artifacts can be hashed and registered.
- Registry verification catches file modification.
- Re-registering a conflicting immutable artifact fails.
- Small canonical evidence may be committed directly; large generated artifacts remain ignored/external but their immutable hashes and locations are registered.
- The registry can also register committed evidence so one verification path covers both storage classes.

---

## A005 — Create `reports/experiment_log.md`

### Required format

Add one entry for each completed Phase-0 task using the protocol template.

Minimum entries:

```text
T001
T002
T003
T004
```

Each entry must include:

```text
Task ID
Status
Completed at
Code commit
Repository dirty state at original execution
Config hash
Dataset/split/origin hashes
Checkpoint/tokenizer revisions
Commands executed
Outputs
Checks/tests
Deviations
Reviewer
```

### Historical honesty rule

Do not rewrite history.

For the original Phase-0 execution, record that the smoke execution was performed with HEAD at the earlier commit and that Phase-0 files were subsequently committed.

Then add a new remediation/reverification entry after A001–A004 are implemented and rerun from a clean commit.

### Acceptance criteria

- The log documents the original provenance limitation.
- A new clean rerun is separately recorded.
- No historical evidence is silently replaced.

---

## A006 — Re-run Phase 0 from a clean committed revision

This task happens only after A001–A005 are committed.

### Required sequence

```text
1. ensure research repo working tree clean
2. uv sync --frozen --group dev
3. bootstrap pinned Kronos source
4. verify checkpoint hashes
5. run Chronos-2/Kronos smoke tests
6. register every evidence artifact
7. update Phase-0 remediation record
```

### Required commands

README must eventually expose equivalent commands such as:

```powershell
uv sync --frozen --group dev
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\bootstrap_kronos.ps1
uv run python scripts\verify_checkpoint_provenance.py
uv run python scripts\smoke_models.py --model all --device cuda:0
```

### Report update

Update:

```text
reports/environment.md
reports/phase0_completion.md
```

Add a clearly labeled **Reverification** section instead of deleting the original execution record.

Record:

```text
clean commit
artifact hashes
Kronos source verification hash
checkpoint verification hash
smoke output hash
```

### Acceptance criteria

- Current evidence maps to a committed clean repository state.
- All external weights pass hash verification.
- Kronos source checkout is clean at the pinned revision.
- Both mandatory external TSFMs produce finite 20-step outputs.
- Evidence artifacts are registered and hash-verifiable.

---

## A007 — Make README reproduction strict and explicit

### Modify

`README.md`

### Required changes

1. Use `uv sync --frozen --group dev`.
2. Explain that `.vendor/Kronos` is disposable and pinned.
3. Link:
   - `configs/study.yaml`
   - checkpoint provenance manifest
   - experiment log
   - Phase-0 report.
4. Add a short status table:

```text
G1 pending
G2 pass
G3 pending / blocked until official feasibility calculation
G4 pending
```

5. State that current repository contains Phase 0 and research planning, not the completed benchmark.

### Acceptance criteria

A new contributor can reproduce Phase 0 without reading the full technical plan.

---

# 4. Phase B — Clarify the research contract

## B001 — Correct the controlled-information wording

### Problem

`configs/study.yaml` currently risks implying that **all mandatory models** receive identical market information, but classical baselines and DLinear-C use Close-only input while E2 models receive OHLC.

### Modify

`configs/study.yaml`

Replace the broad research question with wording that distinguishes:

```text
baseline ladder
vs
OHLC-controlled E2 comparison
```

Required semantics:

- Naive / ARIMA / ETS / DLinear-C are legitimate baseline models and do not need the same feature set.
- The **generic-vs-financial TSFM transfer claim** is supported by the E2 controlled comparison where Ridge-OHLC, Chronos-2, and Kronos receive identical observed OHLC history, origins, and target dates.

### Acceptance criteria

No configuration or report states that all mandatory models receive identical input features.

---

## B002 — Encode Kronos placeholder semantics

### Problem

Current config says synthetic volume is prohibited, while the adapter intentionally passes zero-valued `volume` and `amount`.

This is technically valid but semantically ambiguous.

### Modify

`configs/study.yaml`

Add an explicit section similar to:

```yaml
kronos_primary_input:
  observed_features: [open, high, low, close]
  placeholder_features:
    volume:
      value: 0.0
      semantic: non_observed_placeholder
    amount:
      value: 0.0
      semantic: non_observed_placeholder
  synthetic_market_volume_allowed: false
```

### Rules

- zero fields are implementation placeholders;
- they are not reported as observed VN30 volume;
- downstream parity reports must compare only true observed OHLC as controlled market information.

### Acceptance criteria

Machine-readable config clearly separates observed features from required model placeholders.

---

## B003 — Represent gate state explicitly

### Modify or create

Prefer:

```text
data/manifests/gates.yaml
```

rather than overloading `configs/study.yaml`.

Suggested schema:

```yaml
G1:
  status: pending
  reason: vn30_ohlc_source_not_yet_accepted

G2:
  status: pass
  evidence:
    - data/manifests/checkpoint_provenance.yaml
    - ...

G3:
  status: blocked
  reason: requires_official_hose_calendar_and_sufficient_post_boundary_sessions
  evidence: null

G4:
  status: pending
  reason: dataset_calendar_origins_and_expanded_configs_not_frozen
```

Do not hardcode the projected G3 pass date until T012/T014 compute it from the official session calendar.

### Acceptance criteria

- Gate status is machine-readable.
- Gate transitions require evidence paths.
- G3 is not accidentally marked pass from weekday arithmetic.

---

# 5. Phase C — Package, tests, and CI foundation

## C001 — Convert the project to an importable package

### Target layout

```text
src/
└── vn30_tsfm/
    ├── __init__.py
    ├── provenance.py
    ├── runtime_identity.py
    ├── artifacts.py
    ├── config/
    ├── data/
    ├── models/
    ├── evaluation/
    └── utils/
```

### Modify

`pyproject.toml`

The project should no longer rely on `package = false` once reusable modules exist.

### Acceptance criteria

These commands work from a clean environment:

```text
uv run python -c "import vn30_tsfm"
uv run pytest
```

No script relies on modifying `sys.path` to import the research package.

Exception: importing the external vendored Kronos project may still require a controlled adapter-specific path mechanism until it is packaged differently.

---

## C002 — Add core unit tests

Create:

```text
tests/
    test_provenance.py
    test_runtime_identity.py
    test_artifacts.py
    test_study_contract.py
```

Minimum tests:

### Provenance

- valid manifest loads;
- mutable revision rejected;
- missing SHA rejected;
- revision mismatch caught.

### Runtime identity

- lock hash stable;
- dirty repository detected;
- clean requirement enforced.

### Artifacts

- hash verification passes;
- modified artifact fails;
- immutable overwrite rejected.

### Study contract

- primary endpoint = Close MAE h=1;
- path length = 20;
- evaluated horizons = 1/5/20;
- primary family size = 2;
- Kronos observed input = OHLC;
- zero volume/amount are placeholders only.

### Acceptance criteria

`uv run pytest` passes locally.

---

## C003 — Add CI

Create:

```text
.github/workflows/ci.yml
```

CI should be CPU-safe and should NOT download large checkpoints by default.

Required jobs:

```text
install locked environment
import package
run unit tests
validate YAML manifests
validate research-contract invariants
```

Optional:

- formatting/linting if a tool is explicitly added to the lock.

Do not make CUDA smoke tests a required cloud CI job unless an appropriate GPU runner is intentionally configured.

### Acceptance criteria

Every PR and push to `main` receives a CI result for the lightweight test suite.

---

# 6. Phase D — Implement Phase 1 data acquisition

This phase implements T010–T014. It must not run the primary model benchmark.

---

## D010 — Formalize the existing exploratory provider audit and complete provider selection

### Current status

Do **not** rebuild the audit from zero. The repository already contains:

```text
scripts/audit_vn30_sources.py
artifacts/source_audit/retrieval.json
data/manifests/source_crosscheck.parquet
```

Treat these as **exploratory source-discovery evidence**. They are useful, but they do not yet satisfy T010/G1.

Current observed source characteristics from the committed audit:

```text
VPS:
  first date: 2012-02-06
  last date:  2026-09-25
  raw rows:   3676
  duplicates: 24 entries / 24 ambiguous dates excluded
  OHLC inequality failures: 12

VNDIRECT:
  first date: 2017-08-24
  last date:  2026-09-25
  duplicates: 0
  OHLC inequality failures: 0

DNSE:
  first date: 2020-05-11
  last date:  2026-09-25
  duplicates: 0
  OHLC inequality failures: 0
```

The agent MUST NOT conclude that VPS is the accepted provider simply because the existing script names it `primary`.

### Why the current audit is not yet G1 evidence

1. `VPS` is hardcoded as the primary provider before its anomalies are resolved.
2. The tolerance and sampling rule live in Python constants rather than a frozen machine-readable acceptance config.
3. The produced result and the code declaring the tolerance were committed together; therefore do not retroactively describe the current audit as preregistered acceptance evidence.
4. Exact raw response bytes are not preserved, only SHA256 hashes. If a provider revises historical values, the current cross-check cannot be reconstructed exactly from Git alone.
5. License/research-use terms and field semantics are not yet represented in an acceptance report.
6. The current comparison is primary-vs-secondary rather than a provider-neutral pairwise audit over all useful overlap periods.

### Required refactor

Create:

```text
src/vn30_tsfm/data/
    providers/
        base.py
        vps.py
        vndirect.py
        dnse.py
    source_audit.py
configs/data_source_acceptance.yaml
```

Keep `scripts/audit_vn30_sources.py` as a thin CLI wrapper around the package implementation.

### Provider interface

```python
class VN30Provider(Protocol):
    provider_id: str

    def fetch_daily_ohlc(
        self,
        start: date,
        end: date,
    ) -> RawRetrieval:
        ...
```

`RawRetrieval` should preserve both normalized rows and retrieval identity:

```text
provider_id
request parameters
retrieved_at_utc
response_sha256
raw bytes location or external artifact ID
normalized frame
```

### Freeze acceptance criteria prospectively

Create `configs/data_source_acceptance.yaml` **after acknowledging that the existing audit is exploratory and before producing the acceptance rerun**.

Suggested schema:

```yaml
required_fields: [date, open, high, low, close]
date_uniqueness_required: true
strictly_positive_ohlc: true
ohlc_inequalities_required: true

crosscheck:
  minimum_observations: 30
  sampling_rule: year_stratified_plus_extreme_return_dates
  seed: 20260926
  tolerances:
    open_abs_points: 0.02
    high_abs_points: 0.02
    low_abs_points: 0.02
    close_abs_points: 0.02
  pairwise_comparison: true

source_acceptance:
  unresolved_duplicate_dates_allowed: false
  unresolved_ohlc_inequality_failures_allowed: false
  research_use_note_required: true
  field_semantics_note_required: true
```

If `0.02` index points is retained, document why this tolerance is appropriate. Because the exploratory result has already been seen, any changed threshold must be justified from data precision/source semantics, not chosen to maximize agreement.

### Preserve exact audit retrievals

For the acceptance rerun, exact source responses must be recoverable.

Preferred options, in order:

1. store content-addressed compressed raw responses outside Git and register their SHA256/location;
2. if licensing and size clearly permit, store compact content-addressed audit responses in a dedicated immutable evidence area;
3. if raw redistribution is prohibited, record enough request metadata + provider terms + SHA256 and archive the bytes in a private research artifact store.

A hash without recoverable bytes is evidence of identity, not a reproducible snapshot.

### Provider-neutral comparison

The acceptance rerun should compare available provider pairs on their overlap:

```text
VPS ↔ VNDIRECT
VPS ↔ DNSE
VNDIRECT ↔ DNSE
```

Do not require a secondary provider to cover the full primary history. Cross-check historical periods where overlap exists, and separately evaluate each candidate's usable historical coverage.

### Mandatory anomaly investigation

Before VPS can be selected, produce a case table for:

- all ambiguous/duplicate VPS dates;
- all 12 OHLC-inequality failure dates;
- agreement/disagreement with VNDIRECT/DNSE where those dates overlap;
- provider raw payload evidence for those dates;
- disposition: provider error, duplicate revision, timestamp issue, field-definition issue, or unresolved.

No silent row deletion may turn an invalid provider into an accepted provider.

### Deliverables

```text
configs/data_source_acceptance.yaml
reports/data_source_acceptance.md
data/manifests/source_crosscheck.parquet      # acceptance rerun, replacing/superseding exploratory result explicitly
data/manifests/source_crosscheck.yaml
artifacts/source_audit/<run_id>/retrieval.json
artifacts/source_audit/<run_id>/summary.json
```

If the existing parquet is superseded, preserve its provenance in `reports/experiment_log.md`; do not pretend it was the final acceptance run.

### G1 acceptance criteria

G1 may pass only if:

- a specific provider is selected by predeclared quality/coverage rules rather than model performance;
- daily OHLC is reproducibly obtainable;
- dates, units, timestamp semantics, and field meanings are understood;
- at least 30 year-stratified/extreme-date observations are cross-checked on independent overlapping sources;
- all material duplicate/OHLC discrepancies are investigated;
- exact acceptance-run retrieval identities are recoverable;
- research-use/licensing constraints are documented;
- `reports/data_source_acceptance.md` explicitly explains why the chosen provider is accepted despite any coverage trade-off.


## D011 — Implement immutable raw snapshot handling

### Create

```text
src/vn30_tsfm/data/raw_snapshot.py
```

Raw snapshots must use append-only paths:

```text
data/raw/vn30/<provider>/<retrieval_timestamp_or_date>/
    vn30_daily.<provider-format-or-csv>
    manifest.yaml
```

Manifest fields:

```yaml
provider:
provider_request:
retrieved_at_utc:
raw_path:
sha256:
size_bytes:
row_count:
min_date:
max_date:
columns:
timezone_or_date_semantics:
license_note:
code_commit:
```

### Rules

- Never overwrite a raw snapshot.
- Re-fetching creates a new snapshot.
- Validation must operate against an explicitly selected snapshot hash.
- Raw data remains gitignored unless policy explicitly changes.

### Acceptance criteria

Running snapshot verification reproduces SHA256 and metadata.

---

## D012 — Build the official HOSE session calendar

### Create

```text
src/vn30_tsfm/data/calendar.py
data/manifests/hose_sessions.parquet
data/manifests/hose_calendar.yaml
```

### Requirements

The calendar must represent actual exchange sessions, including:

- weekends excluded;
- official holidays excluded;
- exceptional exchange closures represented when applicable;
- source and calendar version recorded.

Each session row should minimally contain:

```text
session_date
is_session = true
calendar_version
source_reference
quality_flag
```

If the source is assembled from multiple official notices, record all source references in the manifest.

### Tests

- known holidays are absent;
- known ordinary trading dates are present;
- dates are unique and sorted;
- no weekday-only fallback is silently used;
- dataset dates missing from the calendar trigger an investigation record.

### Acceptance criteria

T012 passes only when the calendar is versioned and hashable.

---

## D013 — Build validation and processed-dataset pipeline

### Create

```text
src/vn30_tsfm/data/
    validate.py
    preprocess.py
    manifest.py
```

### Raw OHLC validations

Fail on:

```text
duplicate date
unsorted chronology after normalization
non-positive OHLC
high < max(open, close)
low > min(open, close)
high < low
missing required field
unparseable date
```

Flag rather than automatically delete:

```text
extreme daily move
suspicious flat OHLC
provider disagreement
calendar mismatch
potential data correction
```

### Processed dataset

Create:

```text
data/processed/vn30_daily.parquet
data/manifests/dataset.yaml
```

Derived columns allowed by the current plan:

```text
log_close
return_1d
log_return_1d
range_abs
range_pct
body_abs
body_pct
```

All derived values must use only current/past observations.

Do not add technical indicators to the primary dataset.

### Dataset manifest

Include:

```yaml
source_snapshot_sha256:
calendar_sha256:
processing_code_commit:
processing_config_hash:
row_count:
min_date:
max_date:
schema:
quality_summary:
processed_sha256:
```

### Acceptance criteria

- Processing is deterministic.
- Same raw snapshot + same code/config produces the same processed hash.
- No interpolation/backfill crosses missing-session boundaries.
- No future-derived feature exists.

---

## D014 — Build split, origin, and feasibility manifests

### Create

```text
src/vn30_tsfm/data/splits.py
scripts/build_holdout_feasibility.py

data/manifests/
    holdout_feasibility.json
    splits.yaml
    common_origins.parquet
```

### Provenance boundary

Read the common boundary from:

```text
data/manifests/checkpoint_provenance.yaml
```

Do not duplicate it.

### Required logic

1. Load the accepted HOSE session calendar.
2. Identify sessions strictly after the provenance boundary.
3. Allocate the first 63 eligible target sessions to validation.
4. Remaining eligible target interval is candidate test.
5. An origin is valid only if:
   - context is available through the origin;
   - all 20 target sessions exist;
   - the full target path lies inside its assigned validation/test interval.
6. Build one ordered origin/target manifest shared by every mandatory model.

### Feasibility artifact

Must contain **no forecasts or model metrics**.

Include at least:

```json
{
  "provenance_boundary": "...",
  "calendar_hash": "...",
  "first_eligible_session": "...",
  "eligible_session_count": 0,
  "validation_target_count": 63,
  "candidate_test_target_count": 0,
  "full_path_test_origin_count": 0,
  "required_full_path_test_origins": 126,
  "gate_G3": "pass|blocked",
  "earliest_projected_freeze_date": "...|null"
}
```

The projected freeze date must come from the official calendar logic, not weekday arithmetic.

### Mathematical invariant

For a contiguous test interval, 126 origins with 20-step full paths require at least:

\[
126 + 20 - 1 = 145
\]

test target sessions after the validation allocation.

The implementation should test the actual manifest rather than rely solely on this arithmetic.

### Acceptance criteria

- every target date is later than its origin;
- every target date is an exchange session;
- no origin crosses validation/test boundaries;
- all mandatory models will receive the same origin IDs;
- G3 passes only if at least 126 valid full-path test origins exist;
- otherwise the artifact explicitly says blocked/pilot.

---

# 7. Phase E — Test the Phase 1 research invariants

Create additional tests:

```text
tests/data/
    test_raw_snapshot.py
    test_calendar.py
    test_validate.py
    test_preprocess.py
    test_splits.py
```

Required cases:

## E001 — Calendar integrity

- duplicate session rejected;
- unsorted session rejected;
- configured official holiday absent;
- target generation never uses non-session dates.

## E002 — OHLC integrity

Hand-crafted invalid rows must fail:

```text
high < close
high < open
low > close
low > open
high < low
negative close
duplicate date
```

## E003 — Causality

Changing a future row must not change processed features for earlier rows.

## E004 — Split boundaries

For every fold/origin:

```text
context_date <= origin_date < target_date
```

and the full target path remains inside its declared interval.

## E005 — Deterministic hashes

The same fixture data must produce the same:

```text
dataset hash
calendar hash
split hash
origin hash
```

## E006 — G3 classification

Fixtures must cover:

```text
125 origins -> blocked
126 origins -> pass
```

---

# 8. Artifact policy for future benchmark code

Implement this policy before T020/T023 even if model evaluation is deferred.

## 8.1 Raw forecast artifact

Future model adapters must write label-free rows only:

```text
run_id
model_id
origin_id
origin_date
target_date
horizon
prediction
status
failure_reason
seed
point_functional
checkpoint_revision
dataset_hash
calendar_hash
split_hash
origin_manifest_hash
config_hash
code_commit
```

No actual outcome values may appear here.

## 8.2 Scored artifact

Only a dedicated evaluation command may join labels to create:

```text
actual_close
actual_log_return
actual_direction
absolute_error
squared_error
...
```

## 8.3 Immutable run behavior

Primary holdout run IDs are immutable.

A rerun must get a new run ID and must not replace the previous accepted artifact.

---

# 9. Recommended commit sequence

Use small auditable commits.

## Commit 0 — repository hygiene

```text
chore: clean tracked temp material and restore data artifact ignores
```

Contains:

- remove tracked `tmp/` gitlinks/regenerable temp files;
- restore selective `.gitignore`;
- optional explicit reference-PDF relocation/attribution if retained;
- test/invariant preventing accidental gitlinks.

## Commit 1 — provenance centralization

```text
refactor: centralize checkpoint and source provenance
```

Contains:

- package bootstrap;
- `provenance.py`;
- manifest validation;
- tests.

## Commit 2 — harden external source checkout

```text
fix: enforce clean pinned Kronos source checkout
```

Contains:

- bootstrap hardening;
- source verification JSON;
- tests/manual verification notes.

## Commit 3 — runtime identity and artifacts

```text
feat: add runtime identity and immutable artifact registry
```

Contains:

- runtime identity;
- artifact hashing;
- artifact registry;
- tests.

## Commit 4 — research contract clarification

```text
docs(config): clarify E2 input parity and Kronos placeholders
```

Contains:

- study YAML wording;
- placeholder semantics;
- gate manifest;
- experiment log.

## Commit 5 — clean Phase-0 reverification

```text
chore: reverify phase 0 from clean committed state
```

Contains only regenerated metadata/reports/registry entries that are intended to be committed.

## Commit 6 — package and CI foundation

```text
build: enable package tests and lightweight CI
```

## Commit 7 — formalize VN30 source acceptance

```text
feat: formalize VN30 source audit and provider acceptance
```

Contains:

- refactor the existing audit into provider modules;
- freeze prospective acceptance config;
- archive/register exact audit retrievals;
- investigate VPS duplicate/OHLC anomalies;
- rerun provider-neutral pairwise cross-check;
- generate G1 acceptance report.

## Commit 8 — immutable raw snapshot + calendar

```text
feat: add raw snapshot and HOSE session calendar pipeline
```

## Commit 9 — processed dataset

```text
feat: add deterministic VN30 validation and preprocessing
```

## Commit 10 — split and feasibility manifests

```text
feat: add provenance-qualified split and G3 feasibility builder
```

Do not mix benchmark model results into these commits.

---

# 10. Definition of done for this remediation plan

The remediation + Phase 1 foundation is complete when all of the following are true:

- [ ] tracked `tmp/` gitlinks/regenerable temporary material are removed or intentionally relocated;
- [ ] `.gitignore` protects raw/processed market data and large experiment outputs while allowing small canonical evidence;
- [ ] model/tokenizer revisions have one executable source of truth;
- [ ] Kronos source checkout is verified clean at the pinned commit;
- [ ] Phase-0 evidence has been rerun from a clean committed research revision;
- [ ] runtime identity is attached to evidence-producing commands;
- [ ] hybrid artifact policy is implemented: small canonical evidence tracked; large outputs ignored/external and hash-registered;
- [ ] artifact hashes and registry entries exist;
- [ ] original Phase-0 provenance limitation is documented rather than erased;
- [ ] `reports/experiment_log.md` exists and contains T001–T004 plus remediation evidence;
- [ ] README uses frozen environment reproduction commands;
- [ ] E2 controlled-information wording is precise;
- [ ] Kronos zero volume/amount semantics are explicit placeholders;
- [ ] gate state is machine-readable;
- [ ] repository is an importable package;
- [ ] lightweight CI passes;
- [ ] the currently committed provider audit is explicitly labeled exploratory;
- [ ] provider acceptance criteria are prospectively frozen before the acceptance rerun;
- [ ] VPS duplicate/OHLC anomalies are investigated rather than silently excluded;
- [ ] exact acceptance-audit retrieval bytes are recoverable or registered in an immutable external store;
- [ ] one VN30 OHLC provider passes G1 or G1 remains explicitly blocked;
- [ ] an immutable raw data snapshot exists;
- [ ] official/versioned HOSE session calendar exists;
- [ ] deterministic processed dataset + manifest exist;
- [ ] holdout feasibility artifact exists;
- [ ] common origin manifest exists;
- [ ] G3 is computed from the official calendar;
- [ ] no primary holdout forecast has been executed before G4.

---

# 11. Stop condition before Phase 2

After T014, stop and review the repository before implementing T020–T027.

The next review must answer:

```text
1. Did G1 pass?
2. Is the raw snapshot reproducible?
3. Is the HOSE calendar authoritative/versioned?
4. Are processed-data transformations causal?
5. How many provenance-qualified validation/test sessions exist?
6. Does G3 pass?
7. Is the common-origin manifest immutable?
8. Are all hashes reproducible?
9. Are CI/tests green?
10. Is the research repository clean and auditable?
```

Only after these questions are resolved should the agent proceed to:

```text
unified model interface
walk-forward engine
forecast/scored artifact separation
metrics
bootstrap
Naive end-to-end
```

---

# 12. Guidance for the next implementation plan

The next agent plan (Phase 2/3) should begin with:

```text
T020 config schemas
T021 unified model interface
T022 walk-forward state machine
T023 label-free forecast artifacts
T024 metrics
T025 paired moving-block bootstrap
T026 leakage/state tests
T027 Naive end-to-end
```

Then implement:

```text
ARIMA / ETS
DLinear-C
Ridge-OHLC
Chronos-2 adapter
Kronos adapter
E2 parity verification
G4 freeze
```

Do **not** implement adaptation/fine-tuning until the mandatory zero-shot benchmark is reproducible.

---

# 13. Agent handoff summary

If an implementation agent only reads one section, use this:

```text
FIRST:
- remove/relocate tracked tmp gitlinks and restore selective ignores;
- preserve small evidence but separate it from large future artifacts;
- centralize revisions;
- guarantee clean pinned Kronos code;
- add runtime identity + artifact registry;
- document original Phase-0 dirty/uncommitted execution;
- commit;
- rerun Phase 0 cleanly.

THEN:
- clarify E2 vs baseline feature parity;
- mark zero volume/amount as non-observed placeholders;
- add gate state;
- package project + tests + CI.

THEN:
- treat the existing VPS/VNDIRECT/DNSE audit as exploratory;
- freeze provider acceptance criteria prospectively;
- investigate VPS duplicate/OHLC failures;
- rerun provider-neutral cross-check with recoverable raw audit responses;
- accept one VN30 provider or keep G1 blocked;
- snapshot raw data immutably;
- build official HOSE session calendar;
- validate/process deterministically;
- build provenance-qualified validation/test origins;
- compute G3.

STOP:
- do not run the primary benchmark;
- do not tune models from final-test results;
- do not fine-tune Kronos.
```

The success criterion of this implementation is not “Kronos runs.”  
The success criterion is that the repository becomes a **reproducible research system whose future benchmark results can be audited from source data to final statistical claims**.

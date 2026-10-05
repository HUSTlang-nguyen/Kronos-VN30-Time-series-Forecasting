# T010/T012 — VNDIRECT review, 2026-10-05

Status: **in progress; G1 and T012 pending**. This review records source-quality evidence, not forecasts or an accepted dataset. Research-use permission remains excluded from G1 under the user's existing decision.

Follow-up: `reports/vndirect_39_discrepancy_review.md` investigates all 39 fields on 30 dates. Four Close values are corroborated by contemporaneous publications; 35 O/H/L values remain unadjudicated. Repeated requests reproduce the differences. A supplemental diagnosis finds 71 consecutive VNDIRECT sessions with Open equal to previous Close during 2025-05-05–2025-08-11. This does not explain the construction rules or accept G1. Baseline proposals: `reports/vn30_baseline_literature_review.md`; study v4 remains unchanged.

## T010 — Fresh capture and source comparison

An unchanged three-provider capture was saved under `data/raw/source_audit/20261005T084027989272Z`. The requested interval is **2017-08-24 through 2026-10-02**, with 2 October chosen as an explicit cutoff before the analysis date. This review does not establish the latest available session; refresh through the latest verified complete session when preparing the eventual accepted freeze. Config: `configs/vndirect_source_audit.yaml`. The 0.02-point absolute tolerance for each OHLC field, seed 20261005, five samples per year and ten extreme returns per provider were recorded before this rerun. This is a prospective rerun after earlier exploratory discrepancies, not a blind initial audit.

VNDIRECT returns **2,272 rows**, with strictly increasing unique local session dates and zero invalid numeric values, nonpositive prices, invalid OHLC inequalities or outside-request dates. Date conversion uses `Asia/Ho_Chi_Minh`. The new capture includes 2 October; the old shared contributor snapshot remains unchanged at 2,271 rows through 1 October.

| Comparator | Seeded year-stratified dates | All selected dates including extremes | Dates with complete OHLC | Dates with all four fields within tolerance | Discrepant fields | Missing fields |
|---|---:|---:|---:|---:|---:|---:|
| VPS | 50, spanning 2017–2026 | 59 | 59 | 48 | 12 | 0 |
| DNSE | 35, spanning 2020–2026 | 49 | 45 | 26 | 27 | 16 |

There are **39 material field discrepancies** across the two VNDIRECT comparisons. Counts are field comparisons, not unique dates or independent observations. Different endpoints alone do not establish independent upstream data lineage. Four selected extreme dates are absent from DNSE: 2020-03-09, 2020-03-23, 2021-01-28 and 2025-04-03; the first two predate its observed coverage. No missing candle was filled.

The current VPS capture contains one structurally invalid candle on 2020-08-13: Open 788.42 is below Low 789.26. Comparator problems are not automatically attributed to VNDIRECT. Discrepancies could reflect errors or differing candle construction; neither mechanism is assumed without documentation.

Artifacts: `artifacts/source_audit/20261005T084027989272Z/` and `artifacts/source_audit/vndirect_review_20261005_v2/`. The latter includes selected crosschecks, every unchanged selected-source row, combined candidate calendar and a hash-bound summary. No accepted Phase 1 files are written.

### Comparison with the old capture

Within the common requested interval ending 2026-09-30, all four VNDIRECT fields are exactly unchanged on **2,270 common dates**. DNSE is unchanged on 1,564 common dates. VPS is unchanged on 2,243 dates that are unambiguous in both captures; its 26 formerly duplicated dates now return single rows, and 2017-08-24 is absent from the new response. Request windows differ, so this establishes response differences rather than proving a historical correction or its cause. Ambiguous older candles are not selected or overwritten.

### Supplemental close-value investigation

The previously recorded discrepancy for 2022-11-09 is still present: DNSE Close 974.17 versus VNDIRECT/VPS 979.68. Two contemporaneous publications report VN30 at **979.68**: [MBS daily report](https://www.mbs.com.vn/media/4zihijhi/mbs-market-strategy-daily-09-11-2022.pdf) and [Pinetree market brief](https://pinetree.vn/post/20221109/ban-tin-thi-truong-ngay-09-11-2022/). The complete relevant MBS page was rendered and visually inspected; original PDF/HTML bytes are retained with SHA256 in `data/manifests/vndirect_close_20221109_evidence.yaml`.

This corroborates VNDIRECT's **Close for one day**. It does not establish O/H/L, explain DNSE's construction, verify independent upstream lineage or satisfy the 30-date OHLC requirement. No provider price is patched and the registered rerun sample is unchanged.

## T012 — Selected-interval calendar reconciliation

Every retained calendar source was hash-verified before rebuilding. Config-to-year bindings are in `configs/vndirect_candidate_review.yaml`. Only dates inside the selected request are compared; pre-24-August-2017 absence is not called missing data.

| Year / selected interval | Candidate sessions | VNDIRECT rows | Missing / non-session / duplicate dates |
|---|---:|---:|---|
| 2017, from 24 August | 91 | 91 | 0 / 0 / 0 |
| 2018 | 248 | 248 | 0 / 0 / 0 |
| 2019 | 250 | 250 | 0 / 0 / 0 |
| 2020 | 252 | 252 | 0 / 0 / 0 |
| 2021 | 250 | 250 | 0 / 0 / 0 |
| 2022 | 249 | 249 | 0 / 0 / 0 |
| 2023 | 249 | 249 | 0 / 0 / 0 |
| 2024 | 250 | 250 | 0 / 0 / 0 |
| 2025 | 249 | 249 | 0 / 0 / 0 |
| 2026, through 2 October | 184 | 184 | 0 / 0 / 0 |
| **Total** | **2,272** | **2,272** | **0 / 0 / 0** |

New 2021 evidence: a captured [Vietstock table attributed to HOSE](https://en.vietstock.vn/2020/12/hose-notice-of-holiday-schedule-2021-36-430999.htm) explicitly provides all holiday categories. It agrees with the previous HNX-based diagnostic schedule, but is a mirrored transcription, not the original exchange notice. Its bytes, attribution and limitations are recorded in `data/manifests/hose_calendar_2021_selected_evidence.yaml`. The older hash-bound diagnostic manifest is preserved.

The combined candidate retains **2018-01-22 and 2021-06-01 as shortened sessions**, and closes 2018-01-23/24. Provider agreement does not prove the completeness of exchange holiday/exception evidence.

Remaining evidence:

- 2018: complete annual HOSE notice and original halt/update notices; current holiday table is cropped.
- 2020: direct HOSE annual notice; the current calendar remains an HNX/broker-supported diagnostic.
- 2021: original HOSE annual notice and original halt documentation; new mirrored corroboration improves attribution without accepting it.
- All selected years: finish and record the review of later updates and exceptional full-day closures. Preserve shortened-session flags.

## Replay and acceptance boundary

```powershell
.venv/Scripts/python.exe -B scripts/validate_vn30_sources.py --config configs/vndirect_source_audit.yaml --replay data/raw/source_audit/20261005T084027989272Z
.venv/Scripts/python.exe -B scripts/review_vndirect_candidate.py --output artifacts/source_audit/vndirect_review_20261005_v2
tmp/ci-data-env/Scripts/python.exe -B -m pytest -q -p no:cacheprovider
```

Replay requires the original local raw captures and calendar sources; their working directories remain ignored by Git. The committed configs, receipts and source URLs identify them, but contributors without these bytes cannot run offline replay merely by cloning the repository. Existing `data/share/` snapshots continue to verify independently.

G1 remains pending until material differences and independent-source evidence are resolved and the calendar is accepted. T012 remains pending until the historical evidence above is complete. No processed dataset, accepted calendar, split/origin manifest, G4 freeze, model inference or holdout metrics were generated.

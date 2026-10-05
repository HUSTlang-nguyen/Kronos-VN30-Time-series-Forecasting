# Phase 1 readiness review

Update 2026-10-05: the user selected VNDIRECT as the primary provider. Current candidate sharing receipts are `data/manifests/vndirect_contributor_snapshot.json` and `data/manifests/vndirect_sqlite_snapshot.json`. Calendar/quality work should target the eventual accepted VNDIRECT interval starting no earlier than the captured 2017-08-24 coverage. The historical review below predates this selection; it does not require repairing rejected providers to accept VNDIRECT. G1 and accepted dataset/splits remain pending.

Reviewed 2026-10-02 against the implementation plan, Section 5 and T010-T014. Phase 1 remains incomplete. Research-use permission is excluded by the user's amendment. No source, processed dataset, calendar or split has been accepted.

Execution status: blocked on external data evidence. The same source-quality blocker persisted across the 2014 calendar investigation, repeated DNSE close check and complete structural-anomaly review. These investigations produced evidence but did not establish a valid accepted source. No authorization to replace unknown prices with guesses, remove failed rows or weaken G1 has been given. Additional identical requests or audit tables cannot resolve the correct OHLC values.

Final local check: `freeze_phase1.py --spec configs/phase1_inputs.yaml` exited with code 1 and `Phase 1 inputs are pending; no accepted output may be written`. Verified absent: processed dataset, dataset manifest, accepted session calendar, common-origin manifest, split manifest and freeze receipt. The goal is not complete. Resume when provider correction/clarification or an independently verifiable alternative becomes available; historical calendar acceptance remains required as well.

| Requirement | Current evidence | Remaining work |
|---|---|---|
| T010 reproducible acquisition and units | Hash-verified response replay for VPS/VNDIRECT/DNSE and offline raw reconstruction for KBS/VCI | Select a source only after the remaining quality checks pass |
| T010 OHLC correctness and uniqueness | VPS: 12 invalid OHLC rows and 52 duplicate rows; KBS: 28 invalid OHLC rows; VCI: 60 invalid OHLC rows | Provider explanation or independently verified resolution; retain original values |
| T010 independent seeded crosscheck and extremes | Pairwise audit artifacts include year-stratified and extreme-return observations with fixed 0.02-point tolerances | Material differences and independent upstream lineage remain unresolved |
| T011 immutable accepted snapshot | Freeze implementation exists; original exploratory captures retained and replayable | G1 acceptance and an exact accepted snapshot are missing |
| T012 historical session calendar | HOSE annual candidate evidence for 2017, 2019 and 2022-2026; partial/cross-exchange evidence for other years | Complete evidence over the selected research period and review exceptional closures |
| T013 processed data and quality report | Strict date/OHLC/session validation and past/current-only features implemented | Execute on accepted T011/T012 inputs; accepted output files are absent |
| T014 splits, feasibility and common origins | Candidate planning: 63 validation targets and 121 full-path test origins through 2026-10-01 | Generate manifests from accepted realized data/calendar; 126 origins required for confirmatory classification, otherwise explicit pilot |

The research period remains the launch/earliest reliable daily OHLC through the latest complete session at freeze. Dataset A remains the 2016-2023 replication slice. This review does not authorize choosing a later start just to remove known anomalies, dropping sessions, enlarging tolerances, deduplicating conflicting rows, mixing providers or fabricating missing candles.

## Complete structural-anomaly review

`scripts/build_anomaly_review.py` assembles every returned candle from all five providers on the union of dates with invalid numeric/OHLC values or duplicate daily dates. The table has **119 dates and 440 rows**, retaining **100 invalid OHLC rows and all 52 duplicate VPS rows**. Missing provider observations remain absent. These totals overlap by date and must not be added as counts of independent failed sessions. Numerical disagreements on otherwise valid dates and missing-session checks are separate audits.

Each original response hash is verified before reading. The receipt records config/script/manifest/response hashes and the resulting table hash. Re-execution verifies exact equality and refuses changed results. It makes no source-selection or price-correction decision.

```powershell
.venv/Scripts/python.exe scripts/build_anomaly_review.py --audit data/raw/source_audit/20261001T151513588605Z --vnstock data/raw/vnstock_audit/20261001T154235115506Z --output artifacts/source_audit/anomaly_review_20261002
```

Verified in this review: both original source-audit replays, raw-to-normalized KBS/VCI reconstruction and exact anomaly-table replay. The duplicate/invalid rows are retained, not repaired. Earlier pipeline unit verification: 34 tests passed; unit tests do not establish actual data acceptance.

## Evidence needed to unblock acceptance

A provider's corrected/clarified daily VN30 OHLC history or an independently verifiable alternative source is needed to resolve the known structural and price discrepancies. Historical exchange notices and exception evidence are also still required for the selected interval. A further identical request can reproduce an error but cannot establish its correct value or explain its construction. No inference run or benchmark scores can be produced while G1 remains pending.

Supporting investigations: `reports/source_discrepancies.md`, `reports/source_anomaly_investigation.md`, `reports/vnstock_source_audit.md` and `reports/historical_calendar_discovery.md`. Executable acceptance/output contract: `docs/Phase1_Freeze_Runbook.md`.

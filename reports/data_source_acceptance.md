# T010 — VN30 source acceptance audit

Case-level update 2026-10-05: `reports/vndirect_39_discrepancy_review.md` checks all 39 selected-source field discrepancies. Four Close values are publication-supported, 35 O/H/L values remain unadjudicated, and VNDIRECT has a 71-session Open/previous-Close pattern requiring clarification. G1 remains pending. Baseline recommendations in `reports/vn30_baseline_literature_review.md` do not change data acceptance or the canonical study.

Audit date: 2026-10-01. Status: **pending — G1 has not passed**.

Selected-source review update (2026-10-05): a fresh VNDIRECT capture has 2,272 valid, unique daily candles through 2026-10-02. All dates match the combined year-specific candidate calendars over 2017-08-24–2026-10-02. Seeded rerun comparisons still contain 39 material OHLC field discrepancies involving VNDIRECT. Original annual calendar documents/exception review and independent upstream lineage remain pending; no G1 acceptance is claimed. Current evidence and replay commands: `reports/vndirect_T010_T012_review.md`. The findings below retain the earlier audit's scope.

Decision update (2026-10-05): the user selected VNDIRECT as the primary provider for the main dataset. See `configs/primary_data_source.yaml`. Selection is distinct from quality acceptance: G1 remains pending. The older multi-provider audit configuration and its hashes are unchanged for replay.

Additional sources tested through vnstock 4.0.9: KBS and VCI. VCI reaches the requested launch date; KBS begins June 2012. Both have unresolved historical OHLC violations. Captured bytes, offline verification, common-interval crosscheck and isolated dependency freeze are documented in `reports/vnstock_source_audit.md`. No source is automatically preferred or accepted.

No provider has been accepted. This prevents acceptance of the downstream T011–T014 deliverables under the current plan. The full Phase 1 objective remains open.

## Evidence and reproducibility

The previous `scripts/audit_vn30_sources.py` / `data/manifests/source_crosscheck.parquet` audit is exploratory. Its raw responses were not retained and its VPS-primary assumption was not an accepted selection decision. Those artifacts remain preserved as historical evidence.

The new audit uses `configs/data_source_acceptance.yaml`, written before the new retrieval. Its rules acknowledge the already observed exploratory results; this is not an independent preregistration made before any source inspection.

- Run: `20261001T151513588605Z`.
- Requested dates: 2012-02-06 through 2026-09-30 inclusive.
- All three provider pairs compared; no automatic primary provider selection.
- Seed: 20261001. Five common dates sampled per available year, supplemented by the ten largest absolute one-session Close returns from each provider. Extreme dates absent from the other provider remain missing records.
- Each OHLC field uses an absolute tolerance of 0.02 index points, relative tolerance zero. The threshold reflects two-decimal reporting; discrepancies are not justified by enlarging it after inspection.
- Raw bytes, request URL, retrieval time, SHA256 and size: `data/raw/source_audit/20261001T151513588605Z/manifest.json` and the adjacent provider JSON files.
- Raw-response files are local and gitignored. Replaying requires these retained files; hashes alone cannot reconstruct bytes.
- Committed audit evidence: `artifacts/source_audit/20261001T151513588605Z/summary.json`, `crosscheck.parquet`, `anomalies.parquet`.
- Run records the current code commit, dirty state, script hash and config hash. This is development audit evidence.

```powershell
uv run --no-sync python scripts\validate_vn30_sources.py
uv run --no-sync python scripts\validate_vn30_sources.py --replay data\raw\source_audit\20261001T151513588605Z
uv run --no-sync pytest -q
```

The online command creates a new run; it never overwrites the preceding run. Offline replay verifies all raw hashes and exact equality of regenerated comparison rows.

## Provider assessment

| Provider | Returned rows | First returned date | Last returned date | Duplicate rows | Invalid OHLC rows | Outside requested dates |
|---|---:|---|---|---:|---:|---:|
| VPS | 3679 | 2012-02-07 | 2026-10-01 | 52 | 12 | 1 |
| VNDIRECT | 2271 | 2017-08-24 | 2026-10-01 | 0 | 0 | 1 |
| DNSE | 1564 | 2020-05-11 | 2026-09-30 | 0 | 0 | 0 |

Numbers count raw rows, including every duplicate and out-of-range response row. Duplicate rows are retained in raw and anomalies artifacts and explicitly excluded from pairwise numeric comparison. They are not silently removed from an accepted dataset.

VPS provides the longest observed coverage, but duplicated candles and invalid OHLC prevent accepting it. VNDIRECT and DNSE satisfy basic numeric checks on the retrieved observations, but have shorter coverage and material cross-source disagreements. Numeric plausibility does not establish a correct source.

Daily timestamps are mapped to `Asia/Ho_Chi_Minh` session dates. Sources have different timestamp conventions; equal epoch times are not required. VPS and VNDIRECT return one session beyond the requested end; it is flagged and excluded from comparisons. VPS did not return the requested first launch date in this request. Start-boundary inclusivity and full-history availability need investigation before dataset freezing.

## Cross-check results

| Pair | Fields within tolerance | Material discrepancies | Missing fields |
|---|---:|---:|---:|
| DNSE / VNDIRECT | 156 | 24 | 16 |
| DNSE / VPS | 160 | 20 | 20 |
| VNDIRECT / VPS | 229 | 11 | 4 |

These are field counts, not counts of days. The detailed investigation register is `reports/source_discrepancies.md`. All 55 material field discrepancies remain unresolved. Agreement between two broker feeds is corroboration but does not establish independent upstream lineage or identify which candle definition is correct.

An investigation of 2022-11-09 found DNSE Close 974.17 versus VNDIRECT/VPS 979.68. [Pinetree's dated market brief](https://pinetree.vn/en/post/20221109/market-brief-09-11-2022/) reports VN30 979.68, supporting VNDIRECT/VPS on this field. Root cause and exchange confirmation remain pending; no raw candle was patched. `data/manifests/source_investigation.yaml` records this finding and an official HOSE calendar-notice candidate for T012.

## Research-use permission — historical review, excluded from G1

Policy amendment 2026-10-02: the user explicitly instructed proceeding without the research-use criterion. It is no longer required by the plan or freeze validator. The historical observations below are retained for provenance, not as current blockers. Permission has not been independently verified or relabeled as granted.

- [VPS website terms](https://www.vps.com.vn/dieu-khoan-su-dung) allow personal downloads with attribution, while restricting other copying/distribution. Applicability to the chart endpoint and academic publication has not been established. Personal download permission is not recorded as blanket research/publication permission.
- [VNDIRECT Datafeed terms](https://datafeed.vndirect.com.vn/term-full) describe a registered product for personal technical analysis. They do not establish permission for this separate public dchart endpoint.
- [DNSE terms](https://www.dnse.com.vn/dieu-khoan-dich-vu) and its API documentation do not yet provide recorded permission for the chart endpoint and intended research use.
- An open-source wrapper's software license is not a license for the underlying market data.

This audit does not establish data redistribution rights. Under the amended study policy, permission evidence is not required for G1; historical endpoint/terms observations above remain informational.

## Remaining G1 requirements

Current consolidated readiness review: `reports/phase1_readiness_review.md`. The all-provider anomaly table at `artifacts/source_audit/anomaly_review_20261002/candles.parquet` preserves 440 raw candles on the union of 119 invalid/duplicate dates, including every conflicting VPS row. Its receipt binds all original response hashes. This table covers structural anomalies, not all sampled numerical disagreements or missing-session dates.

1. Resolve duplicated/invalid VPS rows and all material discrepancies using official HOSE observations or provider clarification, recording evidence for every disposition. Investigate OHLC construction and any auction/session differences without guessing.
2. Research-use permission requirement removed by explicit user request on 2026-10-02.
3. Reconcile missing dates and source boundaries against reproducible HOSE sessions, including exceptional closures. Weekday-only approximation is insufficient.
4. Choose one provider from documented quality and coverage evidence; preserve coverage limitations and never splice feeds silently.
5. Only then accept G1 and freeze the benchmark dataset under T011. This audit raw capture is not the accepted T011 dataset.

## Validation

Offline replay reproduced the stored comparison exactly and verified response hashes. Tests cover local date conversion, duplicate retention, differing Open with equal Close, and missing extreme-date observations. Existing repository hygiene tests also pass.
# Additional anomaly evidence (2026-10-01)

Narrow-window queries reproduced DNSE's missing 2025-04-03 and conflicting VPS duplicate daily observations. The official HOSE trading summary confirms 2025-04-03 traded with VN30 close 1283.18. DNSE fails completeness for this captured session; VPS fails daily uniqueness without an explicit resolution rule. VNDIRECT remains an unaccepted candidate. Full evidence and replay command: `reports/source_anomaly_investigation.md`. This does not resolve the 55 material field discrepancies or grant G1.

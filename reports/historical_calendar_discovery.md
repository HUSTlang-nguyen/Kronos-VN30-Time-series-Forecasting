# Historical calendar review

## 2026-10-02: partial 2014 evidence and schedule conflicts

Preserved and text-reviewed SHS's schedule, Asean Securities' National Day notice and BMSC's republication of an earlier HNX annual table. Exact URLs, unchanged-byte SHA256 hashes and limitations are recorded in `data/manifests/hose_2014_partial_holiday_evidence.yaml`.

SHS records January 1, April 9, April 30-May 2 and September 1-2, but its table does not specify Tet. It lists `25/4/2014` among Saturdays without trading even though that date is a Friday. Preserve the original ambiguity; do not close April 25 or silently change it to April 26. Asean's article body explicitly concerns 2014 despite the 2013 title/URL, cites HOSE notice 789 dated August 13 and corroborates September 1-2 closure, September 3 reopening and no trading on makeup Saturday September 6.

The earlier HNX table instead gives Tet January 30-February 5, April 30-May 1 and September 2 only. MBS's web-visible later Tet announcement describes January 28-February 5, reopening February 6, but local capture returned HTTP 403. These records demonstrate why the earlier table must not be treated as the final HOSE calendar. No annual 2014 coverage or accepted calendar has been generated; original exchange updates and the date ambiguity remain evidence targets.

## 2026-10-02: partial 2015 New Year evidence

Captured the SHS notice published 31 December 2014 and reviewed its visible text: trading is closed 1-2 January 2015 and resumes 5 January. The unchanged HTML is hash-bound in `data/manifests/hose_2015_partial_holiday_evidence.yaml`. This identifies January 2 as a date requiring explicit closure evidence; a January-1-only holiday assumption is insufficient. Broker evidence is not presented as a HOSE annual notice, and 2015 remains outside annual coverage.

SSI's historical disclosure index links a separate 2015 holiday notice. Its target/attachment content has not been verified; it is recorded as a discovery follow-up rather than accepted evidence. The complete annual notice and historical exception review remain pending.

Follow-up: the SSI target page was captured unchanged (SHA256 `e5685c2d4f56abab0348e8b0cfdfecd80104f459e7dbc660c5a998ba746fa7ee`). Its holiday content is an image attachment; downloading that attachment returned HTTP 403. No image capture or extracted dates are claimed. VNDIRECT's 2015 Tet article was found, but local retrieval also returned HTTP 403. No access-control bypass was attempted. Discovery identified HOSE notice 1157/TB-SGDHCM, reportedly issued 19 December 2014 and replacing notice 596 dated 30 May; the original document remains the next evidence target. These failures and identities are recorded in the partial manifest to prevent treating a page title as verified annual content.

## 2026-10-02: 2016 cross-exchange diagnostic

Captured the unchanged HNX annual notice and reviewed its visible holiday table, citing regulator letter 2648/UBCK-PTTT dated 28 May 2015. SHA256: `685a07acaec24ed19d4a2472e0cf03df23f28a6a1520bbfe21aac15ff4bed0bf`. Source: https://www.hnx.vn/vi-vn/chi-tiet-lich-nghi-gd-194376.html?_page=1 . This is HNX evidence; direct HOSE annual confirmation, later updates and exceptional-closure review remain pending.

The diagnostic calendar contains 251 sessions. VPS has no missing, duplicate or non-session dates. VNDIRECT and DNSE each lack all 251 dates because their preserved histories begin after 2016; this is a coverage limitation, not an isolated omission within returned history. Evidence: `data/manifests/calendar_2016_cross_exchange_evidence.yaml` and `artifacts/source_audit/calendar_2016_cross_exchange/`. No accepted calendar, dataset patch or G1 acceptance was generated.

## 2026-10-02: updated HOSE 2017 annual notice captured

Captured and visually inspected the complete one-page HOSE notice 1241/TB-SGDHCM dated 7 December 2016. It explicitly replaces notice 625 dated 26 May 2016 and fixes Tet closure to 26 January-1 February 2017. The PDF includes a typed signatory name but no visible handwritten signature or stamp; its filename date is 8 December. Preserve these limitations rather than calling it a signed scan. Source: https://static2.vietstock.vn/vietstock/2016/12/8/20161208_20161208%20Cong%20bo%20lich%20nghi%20giao%20dich%202017.pdf . SHA256: `2db1b5b67cf48464123769b1769653dc29ab9ba79cff5f9fa29e5bc6b6052748`.

The captured HNX annual page still gives 27 January-2 February. Its visible text was reviewed and preserved as conflicting discovery evidence, not input to the HOSE calendar. The updated exchange-specific document determines the candidate dates; provider agreement is not used to select the holiday interval.

The 2017 candidate has 250 sessions. VPS reconciles without missing, duplicate or non-session dates. VNDIRECT is absent on 159 sessions before its first returned observation on 24 August; dates within its returned 2017 coverage reconcile cleanly. DNSE has no returned 2017 history. Evidence: `data/manifests/hose_calendar_2017_evidence.yaml` and `artifacts/source_audit/calendar_2017/`. Exceptional-closure review and G1 remain pending.

## 2026-10-02: 2021 diagnostic and reproduced DNSE omissions

Captured unchanged HNX annual HTML published 4 December 2020 and reviewed the visible holiday table. Source: https://hnx.vn/vi-vn/chi-tiet-lich-nghi-gd-60010564.html?_page=1 . SHA256: `09c4062b6ab7a5632797ea1efacaaa3d66504606db4ba58267197b3838c077a9`. Together with the preserved BMSC Tet notice and HOSE director interview, it supports a diagnostic 250-session calendar retaining 1 June with a shortened-session flag. It does not establish a verified HOSE annual calendar.

VPS/VNDIRECT reconcile without missing, duplicate or non-session dates. DNSE is absent on 15 diagnostic dates: 21-22 and 25-29 January; 1-4 February; 12-14 and 23 July. A fresh request for 18 January through 5 February returns only 18-20 January and 5 February, reproducing all eleven January/February omissions. This changes the source investigation from a single broad-capture observation to a repeated narrow-window observation; root cause and direct HOSE session confirmation remain pending. No rows were patched or imputed.

Evidence: `data/manifests/calendar_2021_cross_exchange_evidence.yaml`, `artifacts/source_audit/calendar_2021_cross_exchange/` and `artifacts/source_audit/investigation_20261001T173314028636Z/summary.json`. Original response SHA256: `e7acb53d7973c28f92757a8bbf22b1e12a3fbc70f13b6cb3ab3c5e50f5b16ef1`.

## Current evidence status — 2026-10-02

Complete signed annual notices are captured for 2019 and 2022-2026. The 2018 calendar is a candidate supported by a cropped HOSE holiday table and separate event evidence. The 2020 and 2021 calendars are cross-exchange diagnostics; direct HOSE annual confirmation remains pending. None is an accepted complete 2012-present calendar.

The 2018 candidate contains 248 sessions. The visually inspected holiday-table image has SHA256 `9ea8244df18b5431e2baa0d32b27ffa44ef175e08f69cc2af9fd40181ae06fc6`; its crop lacks a signature and issue date. The signed 2019 notice independently documents the 31 December 2018 closure. The captured HNX retrospective describes the interrupted closing auction on 22 January and full-day HOSE closures on 23-24 January. Keep 22 January as a session with `shortened_session`; primary HOSE exception documentation remains pending.

VPS and VNDIRECT reconcile without missing, duplicate or non-session dates in 2018. DNSE has no returned history for this year. Date agreement does not validate OHLC values or usage rights. Configuration and replayable results: `data/manifests/hose_calendar_2018_evidence.yaml`, `artifacts/source_audit/calendar_2018/`.

## 2026-10-02: 2020 diagnostic cross-exchange reconciliation

Captured the official HNX annual trading notice and KIS/SSI notices for each holiday category as unchanged HTML. Their reviewed text supports a 252-session diagnostic calendar. The HNX annual source is explicitly identified as HNX, and broker notices are not presented as a HOSE annual notice. Consequently this does **not** extend verified HOSE annual coverage to 2020. Direct HOSE confirmation and exceptional-closure review remain pending. Source identities, hashes and the KIS National Day reopening-year typo are preserved in `data/manifests/calendar_2020_cross_exchange_evidence.yaml`.

Reconciliation finds no missing or non-session dates for VPS/VNDIRECT; VPS has the previously investigated duplicate date 25 December. DNSE is absent on 100 diagnostic sessions: 84 before its first observation on 11 May and 16 within returned history. The latter dates are 12, 15, 22, 27 and 29 May; 16, 17 and 20 July; 20, 21, 24 and 25 August; 14, 15, 18 and 28 September. These are candidate calendar discrepancies pending direct HOSE session evidence, not permission to add rows.

A new DNSE request for 11-31 May returns only ten observations and reproduces all five May omissions. Exact bytes and request identity are saved under `data/raw/source_investigation/20261001T172147744349Z`; replayable evidence is `artifacts/source_audit/investigation_20261001T172147744349Z/summary.json`. Root cause remains unresolved; no imputation, candle repair or provider splice was performed.

```powershell
.venv/Scripts/python.exe scripts/build_hose_calendar.py --config data/manifests/calendar_2020_cross_exchange_evidence.yaml --start 2020-01-01 --end 2020-12-31 --output artifacts/source_audit/calendar_2020_cross_exchange
.venv/Scripts/python.exe scripts/investigate_source_anomalies.py --audit data/raw/source_audit/20261001T151513588605Z --replay data/raw/source_investigation/20261001T172147744349Z
```

## 2026-10-02: 2019 annual notice captured

The complete signed HOSE notice 1108/TB-SGDHCM, dated 29 August 2018, was retrieved from the Fiingroup mirror and visually inspected after rendering. Discovery used the KIS page's Stoxplus attachment path; the old host failed TLS negotiation, while the same path on Fiingroup downloaded successfully with ordinary verified TLS. The exact retrieval URL and unchanged PDF SHA256 `cf69c0ebb5c4315978c6452786b8c7b9769e5d0c7cbbed5cf5bd94f73cb15a1b` are recorded in `data/manifests/hose_calendar_2019_evidence.yaml`.

The notice includes a cross-year New Year closure on 31 December 2018-1 January 2019 and a 29 April-1 May 2019 closure. The 2019 candidate includes only the 2019 part of the cross-year holiday; it does not claim annual coverage for 2018. The captured notice remains available to support that individual 2018 date when reviewing the 2018 calendar.

The resulting calendar has 250 scheduled sessions. VPS and VNDIRECT have zero missing, duplicate or non-session dates in 2019. DNSE has no observations for this year: its preserved response begins in May 2020, so the reconciliation lists all 250 sessions as absent. This is a historical coverage limitation, distinct from an isolated missing date within returned history. Evidence: `artifacts/source_audit/calendar_2019/`.

Candidate annual coverage is **2019 and 2022-2026**, not a continuous 2019-2026 calendar. 2012-2018, 2020 and 2021 remain unverified annually; exceptional-closure review and G1 remain pending.

```powershell
.venv/Scripts/python.exe scripts/build_hose_calendar.py --config data/manifests/hose_calendar_2019_evidence.yaml --start 2019-01-01 --end 2019-12-31 --output artifacts/source_audit/calendar_2019
.venv/Scripts/python.exe scripts/reconcile_hose_sessions.py --audit data/raw/source_audit/20261001T151513588605Z --calendar artifacts/source_audit/calendar_2019/candidate_days.parquet --end 2019-12-31 --output artifacts/source_audit/calendar_2019/reconciliation.json
```

Reviewed 2026-10-01. No historical calendar has been promoted to accepted T012 status.

## 2026-10-02: 2021 shortened-session investigation

The 1 June 2021 interruption stopped afternoon trading after the morning session completed. It must not be treated as a full-day closure or removed from daily observations. A captured VTV interview with HOSE's general director confirms the closing price convention was the last morning matched price; source URL, unchanged HTML hash and pending exchange-document limitations are recorded in `data/manifests/hose_session_exceptions.yaml`.

All three preserved original providers contain exactly one candle on that date, agreeing on O/H/L/C = 1473.28 / 1496.55 / 1473.28 / 1482.92. This is source agreement, not independent validation of all fields. Preserve the candle and carry a shortened-session quality flag when the accepted historical calendar is built; do not synthesize afternoon prices or filter the day.

VNDIRECT's contemporaneous notice corroborates the event, but local capture met an HTTP challenge; its linked exchange PDF returns 404. No bypass or local-capture claim is made. The complete 2021 holiday notice has not yet been captured, so 2021 remains outside candidate annual coverage.

## 2023 captured and visually verified

The complete signed scan of HOSE 2208/TB-SGDHCM, issued 13 December 2022, was retrieved from a third-party mirror and visually inspected. Exact local image bytes: `data/raw/calendar/20261001_historical/hose_2023_mirror.jpg`; SHA256 `81b5e5914da3e720e83486ebb4c59aff2ec1b1a95a1ca5124c5d21929107523d`.

Source: https://cdn.thuvienphapluat.vn/phap-luat/2022-2/HQ/lich-nghi-hose.jpg

Its holiday schedule is recorded in `data/manifests/hose_calendar_2023_evidence.yaml`. National Day closure is 1-4 September, including the weekend. Thus 1 September is closed and 5 September is a scheduled trading day. The notice cites regulator letter 8235/UBCK-PTTT dated 12 December 2022.

The original VSD settlement-calendar page published 26 July 2022 still records National Day closures on 4-5 September 2023. Exact HTML was preserved at `data/raw/calendar/20261001_historical/vsd_2023_original_schedule.html`; SHA256 `b52eddf981b614d0d5d4761899a99ad45085c000d28b672297e1e9918ffceffe`. Source: https://vsdc.vn/vi/ad/152241

Disposition: do not use that older settlement page to define HOSE trading dates. The later HOSE trading notice supplies the applicable candidate holiday dates. A settlement calendar also describes a different operation from spot-index trading. Record chronology and subject matter instead of merging conflicting dates or using whichever source agrees with the price feed.

## Initial discovery limitations

The captured 2023 notice produces 249 scheduled sessions. Reconciliation against the preserved provider responses finds no missing, duplicate or non-session dates for VPS and VNDIRECT in 2023. DNSE is missing the scheduled session 2023-04-07. This remains an unresolved source anomaly; no row has been imputed or copied from another provider. Evidence: `artifacts/source_audit/calendar_2023/reconciliation.json`.

HOSE-authored 2022 and 2024 annual PDFs were found on a Vietstock mirror and their extracted text was reviewed. Direct downloads from that host returned HTTP 403; no unchanged PDF capture or full visual verification is claimed. They have not been added as covered years.

- 2022 candidate: https://static2.vietstock.vn/vietstock/2021/12/22/20211222_TB%20lich%20nghi%20giao%20dich%20trong%20nam%202022.pdf
- 2024 candidate: https://static2.vietstock.vn/vietstock/2023/12/7/20231207_lich_nghi_giao_dich_2024.pdf
- A HOSE 2024 update was announced on 19 April 2024: https://www.phs.vn/tin-tuc/hose-cap-nhat-lich-nghi-giao-dich-nam-2024/6167965

The 2024 annual schedule must be reconciled with that update before use. An official HNX update records 29 April-1 May closure and no trading on makeup Saturday 4 May, citing regulator letter 2421/UBCK-PTTT. This corroborates a change but is not silently substituted for HOSE evidence: https://www.hnx.vn/vi-vn/chi-tiet-lich-nghi-gd-60018631.html?_page=1

## 2024 capture and reconciliation completed subsequently

Both complete signed HOSE notices were subsequently downloaded using PowerShell's standard TLS client and visually inspected after rendering. No TLS verification was disabled. The annual notice 1943/TB-SGDHCM (7 December 2023) is preserved from the Thuvienphapluat mirror; update 905/TB-SGDHCM (19 April 2024) is preserved from the exact Vietstock attachment linked by PHS. URLs, unchanged-byte hashes and local paths are recorded in `data/manifests/hose_calendar_2024_evidence.yaml`.

The update replaces the annual 30 April-1 May closure with 29 April-1 May and explicitly excludes trading on makeup Saturday 4 May. Other annual holidays remain unchanged. The resulting candidate calendar has 250 scheduled sessions. VPS, VNDIRECT and DNSE each have zero missing, duplicate or non-session dates in 2024. Evidence: `artifacts/source_audit/calendar_2024/{summary,reconciliation}.json`. Matching dates do not establish OHLC accuracy or source-use permission.

2024 is now covered as a candidate year; exceptional-closure review remains pending. The earlier failed-download observations above describe discovery history, not the final capture state.

```powershell
.venv/Scripts/python.exe scripts/build_hose_calendar.py --config data/manifests/hose_calendar_2024_evidence.yaml --start 2024-01-01 --end 2024-12-31 --output artifacts/source_audit/calendar_2024
.venv/Scripts/python.exe scripts/reconcile_hose_sessions.py --audit data/raw/source_audit/20261001T151513588605Z --calendar artifacts/source_audit/calendar_2024/candidate_days.parquet --end 2024-12-31 --output artifacts/source_audit/calendar_2024/reconciliation.json
```

## Reproduce the 2023 candidate

The DNSE omission on 7 April 2023 reproduces in a fresh narrow-window request covering 3-11 April. Preserved response SHA256: `7225236544ec915483530aa58c953c3035f6c5d3c5c4cf5f95492ab3de6d8659`; evidence: `artifacts/source_audit/investigation_20261001T161635909230Z/summary.json`. DNSE's own [market report](https://www.dnse.com.vn/hoc/ban-tin-thi-truong-07-04-2023) describes completed HOSE trading and VN30 gaining 0.02 points that day. Its HTML is captured and hash-bound in `data/manifests/source_investigation.yaml`. This corroborates session existence, not all OHLC fields or the missing-data root cause.

`scripts/investigate_source_anomalies.py` now accepts an explicit provider and UTC date window, preserving existing default and offline replay behavior. Reproduce this investigation with `--provider dnse --start 2023-04-03 --end 2023-04-12`, or replay the captured request with `--replay data/raw/source_investigation/20261001T161635909230Z` alongside the original `--audit` path.

```powershell
.venv/Scripts/python.exe scripts/build_hose_calendar.py --config data/manifests/hose_calendar_2023_evidence.yaml --start 2023-01-01 --end 2023-12-31 --output artifacts/source_audit/calendar_2023
.venv/Scripts/python.exe scripts/reconcile_hose_sessions.py --audit data/raw/source_audit/20261001T151513588605Z --calendar artifacts/source_audit/calendar_2023/candidate_days.parquet --end 2023-12-31 --output artifacts/source_audit/calendar_2023/reconciliation.json
```

Review exceptional closures, locate official-host captures and cover remaining historical years before claiming a complete exchange calendar. The existing 2025-2026 evidence/configuration and planning artifact remain unchanged.

## 2022 capture and reconciliation completed subsequently

The full one-page signed HOSE notice 2168/TB-SGDHCM was subsequently captured using PowerShell's standard TLS client, rendered and visually inspected. Its handwritten issue date is **21 December 2021**; the mirror filename uses 22 December. The manifest records the signed date rather than deriving it from the URL. Unchanged PDF SHA256: `1d431fe8656b74482753dd87d9354a5ffd20ed99a8b249f5dc77ebf0ae43b528`.

The candidate calendar has 249 scheduled sessions. VPS, VNDIRECT and DNSE each have zero missing, duplicate or non-session dates for 2022. Evidence: `data/manifests/hose_calendar_2022_evidence.yaml` and `artifacts/source_audit/calendar_2022/`. This checks dates only; the previously recorded 9 November close disagreement remains unresolved. Candidate annual coverage now extends through 2022-2026; 2012-2021 and historical exceptional-closure review remain pending.

```powershell
.venv/Scripts/python.exe scripts/build_hose_calendar.py --config data/manifests/hose_calendar_2022_evidence.yaml --start 2022-01-01 --end 2022-12-31 --output artifacts/source_audit/calendar_2022
.venv/Scripts/python.exe scripts/reconcile_hose_sessions.py --audit data/raw/source_audit/20261001T151513588605Z --calendar artifacts/source_audit/calendar_2022/candidate_days.parquet --end 2022-12-31 --output artifacts/source_audit/calendar_2022/reconciliation.json
```

# Provider anomaly investigation

## 2026-10-02: reproduced DNSE close discrepancy, 9 November 2022

A new DNSE request covering November 7-10 returns the same close of 974.17 as the preserved broad-history response. Open/high/low agree with VPS/VNDIRECT at 980.92 / 993.28 / 969.19, while their close is 979.68. The 5.51-point close difference exceeds the predetermined 0.02-point tolerance; it is not a missing-date or duplicate-row artifact. Repeated requests establish reproducibility, not the underlying cause.

The unchanged [Pinetree market brief](https://pinetree.vn/en/post/20221109/market-brief-09-11-2022/) was captured and its visible VN30 value of 979.68 reviewed. Its SHA256 is `497efae807e4c23325ad3f4505d361d5b4b3798fe55fccba0549f54b6bd7d55a`. This corroborates the VPS/VNDIRECT close only; exchange confirmation and upstream lineage remain unverified. DNSE remains ineligible for acceptance on this evidence. No raw values were patched and no alternative source was automatically accepted.

Hash-bound evidence: `artifacts/source_audit/investigation_20261001T180030479867Z/price_recheck.json` and `data/manifests/source_investigation.yaml`. Replay the unchanged chart capture with:

```powershell
.venv/Scripts/python.exe scripts/investigate_source_anomalies.py --audit data/raw/source_audit/20261001T151513588605Z --replay data/raw/source_investigation/20261001T180030479867Z
```

Reviewed 2026-10-01. No dataset patches or provider acceptance.

## DNSE missing session: 2025-04-03

The original full-history response omits this date. A separate request for 31 March through 7 April also omits it. Thus the absence was reproduced without using the same broad request.

HOSE's official trading summary dated 3 April 2025, page 1, was downloaded and visually inspected. It records VN30 close **1283.18**, change **-93.76** points (**-6.81%**). VPS and VNDIRECT both report close 1283.18 for that date. This establishes that the missing date was a trading session, not a holiday. It does not independently verify their open/high/low.

Official source: https://staticfile.hsx.vn/Uploads/News/de2bfaf00509454ab519d44c8ccad1f7/20250403_20250403%20T%E1%BB%95ng%20h%E1%BB%A3p%20th%C3%B4ng%20tin%20giao%20d%E1%BB%8Bch.pdf

Local unchanged capture: `data/raw/source_investigation/20261001T153102558007Z/hose_20250403.pdf`. SHA256: `1b38f68892f5c06c3db22a766a615695e0581a5ec17934d61760445d1818cfdf`.

Disposition: DNSE's captured endpoint response fails completeness for this session. Root cause requires provider clarification. Do not fill it from another provider or silently omit this extreme-return date.

## VPS duplicates

The original response has **26 duplicate dates**: one on 25 December 2020 and 25 in May/June 2025. This distinction explains the earlier calendar finding of 25 dates: that calendar only covers 2025-2026.

The 2020 duplicate has identical OHLC but different timestamps. All 25 duplicates in 2025 have conflicting OHLC. A separate May request reproduces six conflicting duplicate dates. For example, 5 May 2025 has timestamps 4 May 17:00 UTC and 5 May 00:00 UTC, both mapping to 5 May in Vietnam. Their opens are respectively 1309.73 and 1315.43. Therefore simple duplicate removal would select between different observations; it is not a justified cleanup.

Disposition: VPS's captured endpoint response fails unique daily OHLC requirements. Timestamp interpretation/data semantics require clarification. No automatic row selection, timezone shift or deduplication is authorized by this evidence.

## Captures and replay

Exact narrow-window responses and request URLs/hashes are stored under `data/raw/source_investigation/20261001T153102558007Z/`. Tracked detailed findings: `artifacts/source_audit/investigation_20261001T153102558007Z/summary.json`.

```powershell
.venv/Scripts/python.exe scripts/investigate_source_anomalies.py --audit data/raw/source_audit/20261001T151513588605Z --replay data/raw/source_investigation/20261001T153102558007Z
```

VNDIRECT remains a candidate, not accepted: all OHLC discrepancies, historical calendar coverage and research-use permission still require assessment. These findings do not establish that another provider is correct on all dates.

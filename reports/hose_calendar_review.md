# HOSE calendar evidence and source reconciliation

Reviewed: 2026-10-01. Status: candidate, T012 and G1 remain pending.

## Evidence

All relevant pages were rendered and inspected. Exact PDF bytes are preserved locally under `data/raw/calendar/20261001/`; URLs, paths and SHA256 hashes are recorded in `data/manifests/hose_calendar_evidence.yaml`.

- HOSE 2079/TB-SGDHCM, 26 December 2024: annual 2025 holidays, including 2 May closure and no trading on makeup Saturday 26 April. Retrieved from the official HOSE host.
- HOSE 2294/TB-SGDHCM, 9 December 2025: annual 2026 holidays, including 31 August closure and no trading on makeup Saturday 22 August. Exchange-authored signed scan retrieved from a third-party mirror; official-host copy still needed.
- HOSE 2410/TB-SGDHCM, 25 December 2025: replaces the annual New Year entry with 1-2 January 2026 closures; makeup Saturday 10 January remains closed. Retrieved from the official HOSE host.

The versioned candidate contains every calendar date, a session flag, closure reason and source identifier. Scheduled session counts are 249 for 2025 and 248 for 2026. These counts assume no additional exceptional closures and are not an accepted final calendar.

## Reconciliation

Audit: `20261001T151513588605Z`. Comparison interval: 2025-01-01 through 2026-09-30. Input PDF and provider-response hashes were verified before processing.

| Provider | Missing scheduled sessions | Observed non-sessions | Duplicate dates |
|---|---|---|---|
| VPS | None | None | 25 dates; listed in reconciliation JSON |
| VNDIRECT | None | None | None |
| DNSE | 2025-04-03 | None | None |

These are date-coverage findings, not OHLC acceptance. No raw rows were deleted, filled or patched. DNSE's missing date and VPS duplicates require investigation. Provider observations before 2025 and after the comparison end are counted outside coverage, not classified as invalid sessions.

## Reproduce

```powershell
.venv/Scripts/python.exe scripts/build_hose_calendar.py
.venv/Scripts/python.exe scripts/reconcile_hose_sessions.py --audit data/raw/source_audit/20261001T151513588605Z --calendar artifacts/source_audit/calendar_2025_2026/candidate_days.parquet --end 2026-09-30 --output artifacts/source_audit/calendar_2025_2026/reconciliation.json
```

The builder rejects years without evidence and verifies captured PDF hashes. Existing output is checked rather than silently replaced. Replay requires the locally preserved raw bytes, which are excluded from Git.

## Outstanding requirements

Obtain annual calendar evidence for the selected historical dataset period, investigate exceptional exchange closures, locate the official-host 2026 annual notice, resolve source discrepancies and confirm research-use permission. Do not promote the candidate to `data/manifests/hose_sessions.parquet` or generate an accepted dataset/split until the required gates pass.

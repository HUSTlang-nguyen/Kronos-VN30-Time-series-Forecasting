# VN30 history through vnstock

Audit date: 2026-10-01. T010/G1 status: pending.

## Actual retrieval

Requested daily VN30 price-index OHLC from 2012-02-06 through 2026-10-01 using `vnstock==4.0.9`, `vnai==2.6.2`, provider-specific Quote adapters and no random user agent. The main project/CUDA environment was not modified. Dependencies for the separate audit environment are frozen in `requirements/vnstock-audit.txt`.

| Provider | Rows | First returned date | Last returned date | Duplicate rows | Invalid OHLC rows |
|---|---:|---|---|---:|---:|
| KBS | 3575 | 2012-06-01 | 2026-10-01 | 0 | 28 |
| VCI | 3656 | 2012-02-06 | 2026-10-01 | 0 | 60 |

No nonpositive/nonfinite OHLC or out-of-request dates were found. An invalid candle means High is below Open/Close/Low or Low is above Open/Close/High, using the raw reported values. Example KBS 2012-07-12: Open 479.88, High 483.68, Low 481.57, Close 483.12; Open is below Low. VCI 2012-02-21: Open 459.71, High 475.54, Low 460.72, Close 462.27. These are not tiny float-rounding differences.

VCI reaches the requested start date, but that does not prove complete historical coverage. KBS did not return the requested February-May 2012 period. Neither source is accepted for a full-history benchmark while these issues remain unresolved. Do not silently truncate the study, drop invalid candles, clamp prices, splice sources or interpolate.

## Independent verification

HTTP response bodies were captured unchanged before vnstock normalization, with URL, method, OHLC request body, status and SHA256. Authentication headers and telemetry traffic were not captured. Exact local raw material: `data/raw/vnstock_audit/20261001T154235115506Z/`. The initial library execution displayed its optional telemetry notice; subsequent audit executions explicitly disable telemetry via its documented environment setting.

An offline verifier reconstructs OHLC directly from KBS/VCI JSON, verifies response and normalized CSV hashes, and checks agreement with the library-normalized data to absolute tolerance 1e-9. No price scaling is applied to index points. All captured candles, including invalid ones, are retained.

Both sources contain 2025-04-03 with Close 1283.18, agreeing with the previously inspected HOSE trading summary. Both also match scheduled session dates from 2025-01-01 through 2026-10-01, with no missing/extra dates in the candidate calendar. Historical coverage and exceptional closures remain unverified.

The original acquisition crosscheck included 2026-10-01, beyond the older reference request's end. Use `offline_verification/crosscheck_common_interval.parquet` for comparisons: it restricts all sources to the common end 2026-09-30. Its seeded sampling may select different dates than the acquisition sample. Old outputs are preserved for traceability.

| Pair | Pass fields | Discrepant fields | Missing fields |
|---|---:|---:|---:|
| KBS / VCI | 287 | 53 | 0 |
| KBS / VNDIRECT | 218 | 22 | 4 |
| VCI / VNDIRECT | 207 | 33 | 4 |
| DNSE / KBS | 155 | 25 | 20 |
| DNSE / VCI | 161 | 19 | 20 |
| KBS / VPS | 315 | 25 | 0 |
| VCI / VPS | 299 | 41 | 0 |

These are sampled field counts, not complete-history accuracy rates. Dispositions remain unresolved. Agreement between feeds does not prove independent upstream lineage.

## Reproduce

```powershell
uv venv tmp/vnstock-env --python .venv/Scripts/python.exe
uv pip install --python tmp/vnstock-env/Scripts/python.exe -r requirements/vnstock-audit.txt
tmp/vnstock-env/Scripts/python.exe scripts/audit_vnstock_sources.py --end 2026-10-01
.venv/Scripts/python.exe scripts/verify_vnstock_capture.py --capture data/raw/vnstock_audit/20261001T154235115506Z --output artifacts/source_audit/vnstock_20261001T154235115506Z/offline_verification
```

Live acquisition always creates a new immutable run; provider values can change. The offline command verifies the captured run without network access and checks existing output rather than overwriting changed findings. Local raw captures are excluded from Git.

## Permission and remaining work

Policy amendment, 2026-10-02: the user excluded research-use permission from G1. The following licence observation is historical context and no longer an acceptance requirement.

The current [vnstock software licence](https://github.com/thinh-vu/vnstock/blob/main/LICENSE.md) explicitly separates software rights from third-party data rights. Using the wrapper therefore does not establish research-use permission for KBS or VCI data. No data redistribution is authorized by this audit.

Resolve historical OHLC anomalies and material discrepancies with official observations or provider documentation; complete historical HOSE calendars; then select a source, pass G1 and freeze T011. T013/T014 accepted deliverables remain pending.

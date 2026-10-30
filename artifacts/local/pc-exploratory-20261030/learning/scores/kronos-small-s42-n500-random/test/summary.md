**THĂM DÒ — dataset unverified; chưa phải kết luận Q3 chính.**

# VN30 snapshot experiment

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Open is VNDIRECT provider data; its construction on some sessions is uncertain. The actual future trading calendar is supplied to Kronos. VN30 is an index, so these metrics do not imply tradable profit.

| Model | Target | h | N | MAE | RMSE | MAE vs naive |
|---|---|---:|---:|---:|---:|---:|
| naive | open | 1 | 323 | 5.95926 | 9.20026 | 0.00000 |
| naive | close | 1 | 323 | 17.72232 | 24.52345 | 0.00000 |
| naive | open | 5 | 323 | 40.84591 | 51.06532 | 0.00000 |
| naive | close | 5 | 323 | 45.16461 | 55.73607 | 0.00000 |
| naive | open | 20 | 323 | 91.95071 | 113.74891 | 0.00000 |
| naive | close | 20 | 323 | 93.82563 | 115.25833 | 0.00000 |
| naive | gap | 1 | 323 | 0.00310 | 0.00483 | 0.00000 |
| naive | intraday | 1 | 323 | 0.00895 | 0.01231 | 0.00000 |
| kronos-small-ft | open | 1 | 323 | 20.79626 | 37.46504 | 14.83700 |
| kronos-small-ft | close | 1 | 323 | 31.41600 | 47.96952 | 13.69367 |
| kronos-small-ft | open | 5 | 323 | 85.87318 | 122.66825 | 45.02726 |
| kronos-small-ft | close | 5 | 323 | 85.11924 | 118.24710 | 39.95463 |
| kronos-small-ft | open | 20 | 323 | 148.11027 | 184.09069 | 56.15956 |
| kronos-small-ft | close | 20 | 323 | 146.39881 | 181.31310 | 52.57318 |
| kronos-small-ft | gap | 1 | 323 | 0.01120 | 0.02009 | 0.00810 |
| kronos-small-ft | intraday | 1 | 323 | 0.01163 | 0.01611 | 0.00269 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

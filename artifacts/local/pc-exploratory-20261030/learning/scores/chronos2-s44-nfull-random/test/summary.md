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
| chronos2-ft | open | 1 | 323 | 153.38447 | 192.13540 | 147.42521 |
| chronos2-ft | close | 1 | 323 | 152.75351 | 190.79289 | 135.03119 |
| chronos2-ft | open | 5 | 323 | 162.74095 | 203.95018 | 121.89503 |
| chronos2-ft | close | 5 | 323 | 162.04917 | 202.52405 | 116.88456 |
| chronos2-ft | open | 20 | 323 | 188.96105 | 239.26269 | 97.01034 |
| chronos2-ft | close | 20 | 323 | 188.08878 | 237.69193 | 94.26315 |
| chronos2-ft | gap | 1 | 323 | 0.08894 | 0.11298 | 0.08584 |
| chronos2-ft | intraday | 1 | 323 | 0.00899 | 0.01235 | 0.00004 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

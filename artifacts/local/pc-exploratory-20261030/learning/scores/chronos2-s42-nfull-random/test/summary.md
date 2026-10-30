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
| chronos2-ft | open | 1 | 323 | 153.52978 | 192.32270 | 147.57053 |
| chronos2-ft | close | 1 | 323 | 152.89970 | 190.97970 | 135.17738 |
| chronos2-ft | open | 5 | 323 | 160.07031 | 200.52615 | 119.22440 |
| chronos2-ft | close | 5 | 323 | 159.37846 | 199.11200 | 114.21384 |
| chronos2-ft | open | 20 | 323 | 186.87235 | 236.65122 | 94.92164 |
| chronos2-ft | close | 20 | 323 | 185.99850 | 235.08958 | 92.17287 |
| chronos2-ft | gap | 1 | 323 | 0.08903 | 0.11310 | 0.08593 |
| chronos2-ft | intraday | 1 | 323 | 0.00899 | 0.01235 | 0.00004 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

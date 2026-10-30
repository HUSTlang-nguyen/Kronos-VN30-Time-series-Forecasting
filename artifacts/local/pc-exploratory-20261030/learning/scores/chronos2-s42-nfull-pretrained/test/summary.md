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
| chronos2-ft | open | 1 | 323 | 20.22070 | 26.53226 | 14.26144 |
| chronos2-ft | close | 1 | 323 | 19.65774 | 26.35277 | 1.93542 |
| chronos2-ft | open | 5 | 323 | 48.46909 | 59.40705 | 7.62318 |
| chronos2-ft | close | 5 | 323 | 47.93681 | 58.61035 | 2.77219 |
| chronos2-ft | open | 20 | 323 | 100.48656 | 121.24932 | 8.53585 |
| chronos2-ft | close | 20 | 323 | 99.49192 | 120.57895 | 5.66629 |
| chronos2-ft | gap | 1 | 323 | 0.01083 | 0.01414 | 0.00773 |
| chronos2-ft | intraday | 1 | 323 | 0.01220 | 0.01675 | 0.00326 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

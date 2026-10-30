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
| kronos-small-ft | open | 1 | 323 | 20.33242 | 35.18597 | 14.37316 |
| kronos-small-ft | close | 1 | 323 | 36.62629 | 63.73561 | 18.90397 |
| kronos-small-ft | open | 5 | 323 | 95.35770 | 147.01352 | 54.51179 |
| kronos-small-ft | close | 5 | 323 | 98.92498 | 150.79366 | 53.76036 |
| kronos-small-ft | open | 20 | 323 | 170.36246 | 221.53930 | 78.41175 |
| kronos-small-ft | close | 20 | 323 | 170.21577 | 221.24705 | 76.39013 |
| kronos-small-ft | gap | 1 | 323 | 0.01090 | 0.01882 | 0.00780 |
| kronos-small-ft | intraday | 1 | 323 | 0.01359 | 0.02265 | 0.00464 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

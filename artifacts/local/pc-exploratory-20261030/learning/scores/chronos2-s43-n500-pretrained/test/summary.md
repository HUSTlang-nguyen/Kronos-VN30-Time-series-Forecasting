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
| chronos2-ft | open | 1 | 323 | 20.54591 | 27.55530 | 14.58665 |
| chronos2-ft | close | 1 | 323 | 19.73830 | 26.89153 | 2.01598 |
| chronos2-ft | open | 5 | 323 | 48.42997 | 60.61571 | 7.58406 |
| chronos2-ft | close | 5 | 323 | 47.46512 | 58.98798 | 2.30050 |
| chronos2-ft | open | 20 | 323 | 100.74717 | 123.02612 | 8.79646 |
| chronos2-ft | close | 20 | 323 | 98.57987 | 120.50369 | 4.75423 |
| chronos2-ft | gap | 1 | 323 | 0.01096 | 0.01465 | 0.00786 |
| chronos2-ft | intraday | 1 | 323 | 0.01317 | 0.01817 | 0.00422 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

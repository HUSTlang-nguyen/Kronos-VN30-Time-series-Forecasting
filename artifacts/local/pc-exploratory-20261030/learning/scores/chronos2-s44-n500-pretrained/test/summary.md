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
| chronos2-ft | open | 1 | 323 | 20.66781 | 27.58757 | 14.70856 |
| chronos2-ft | close | 1 | 323 | 19.79599 | 26.92182 | 2.07367 |
| chronos2-ft | open | 5 | 323 | 48.34110 | 60.54277 | 7.49519 |
| chronos2-ft | close | 5 | 323 | 47.33883 | 58.84828 | 2.17421 |
| chronos2-ft | open | 20 | 323 | 100.60815 | 122.84150 | 8.65744 |
| chronos2-ft | close | 20 | 323 | 98.30238 | 120.05751 | 4.47674 |
| chronos2-ft | gap | 1 | 323 | 0.01103 | 0.01466 | 0.00793 |
| chronos2-ft | intraday | 1 | 323 | 0.01336 | 0.01845 | 0.00441 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

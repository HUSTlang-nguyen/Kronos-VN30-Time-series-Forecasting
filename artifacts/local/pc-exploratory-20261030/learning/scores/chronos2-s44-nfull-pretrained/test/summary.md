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
| chronos2-ft | open | 1 | 323 | 21.29097 | 27.76344 | 15.33171 |
| chronos2-ft | close | 1 | 323 | 20.49374 | 27.56458 | 2.77142 |
| chronos2-ft | open | 5 | 323 | 49.33786 | 60.64952 | 8.49195 |
| chronos2-ft | close | 5 | 323 | 48.69265 | 59.68324 | 3.52804 |
| chronos2-ft | open | 20 | 323 | 102.19184 | 122.76004 | 10.24113 |
| chronos2-ft | close | 20 | 323 | 101.39012 | 122.26067 | 7.56448 |
| chronos2-ft | gap | 1 | 323 | 0.01140 | 0.01483 | 0.00830 |
| chronos2-ft | intraday | 1 | 323 | 0.01289 | 0.01789 | 0.00394 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

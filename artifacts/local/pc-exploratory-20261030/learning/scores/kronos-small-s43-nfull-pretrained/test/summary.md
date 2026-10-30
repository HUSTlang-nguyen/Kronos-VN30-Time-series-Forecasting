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
| kronos-small-ft | open | 1 | 323 | 10.35944 | 13.91418 | 4.40018 |
| kronos-small-ft | close | 1 | 323 | 20.59497 | 28.12742 | 2.87264 |
| kronos-small-ft | open | 5 | 323 | 51.68584 | 68.17102 | 10.83993 |
| kronos-small-ft | close | 5 | 323 | 55.45474 | 72.51057 | 10.29013 |
| kronos-small-ft | open | 20 | 323 | 133.46771 | 171.28028 | 41.51700 |
| kronos-small-ft | close | 20 | 323 | 138.43443 | 175.74736 | 44.60880 |
| kronos-small-ft | gap | 1 | 323 | 0.00554 | 0.00743 | 0.00244 |
| kronos-small-ft | intraday | 1 | 323 | 0.01013 | 0.01344 | 0.00118 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

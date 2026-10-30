**THĂM DÒ — dataset unverified; chưa phải kết luận Q3 chính.**

# VN30 snapshot experiment

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Open is VNDIRECT provider data; its construction on some sessions is uncertain. The actual future trading calendar is supplied to Kronos. VN30 is an index, so these metrics do not imply tradable profit.

| Model | Target | h | N | MAE | RMSE | MAE vs naive |
|---|---|---:|---:|---:|---:|---:|
| naive | open | 1 | 321 | 3.25981 | 6.71894 | 0.00000 |
| naive | close | 1 | 321 | 8.80112 | 14.22747 | 0.00000 |
| naive | open | 5 | 321 | 20.20508 | 29.04893 | 0.00000 |
| naive | close | 5 | 321 | 21.84221 | 31.35171 | 0.00000 |
| naive | open | 20 | 321 | 40.02751 | 50.59546 | 0.00000 |
| naive | close | 20 | 321 | 40.48723 | 51.55992 | 0.00000 |
| naive | gap | 1 | 321 | 0.00254 | 0.00537 | 0.00000 |
| naive | intraday | 1 | 321 | 0.00589 | 0.00863 | 0.00000 |
| kronos-small-ft | open | 1 | 321 | 4.60233 | 7.48441 | 1.34252 |
| kronos-small-ft | close | 1 | 321 | 10.67381 | 15.80167 | 1.87269 |
| kronos-small-ft | open | 5 | 321 | 23.25575 | 32.97714 | 3.05067 |
| kronos-small-ft | close | 5 | 321 | 25.32639 | 35.98325 | 3.48418 |
| kronos-small-ft | open | 20 | 321 | 38.01908 | 45.88043 | -2.00843 |
| kronos-small-ft | close | 20 | 321 | 38.08938 | 46.59948 | -2.39785 |
| kronos-small-ft | gap | 1 | 321 | 0.00359 | 0.00592 | 0.00105 |
| kronos-small-ft | intraday | 1 | 321 | 0.00681 | 0.00964 | 0.00093 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

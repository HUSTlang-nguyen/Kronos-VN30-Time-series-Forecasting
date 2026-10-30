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
| kronos-small-ft | open | 1 | 321 | 4.61697 | 6.86179 | 1.35716 |
| kronos-small-ft | close | 1 | 321 | 11.01694 | 16.05853 | 2.21581 |
| kronos-small-ft | open | 5 | 321 | 25.51223 | 34.74217 | 5.30715 |
| kronos-small-ft | close | 5 | 321 | 27.26900 | 37.52131 | 5.42679 |
| kronos-small-ft | open | 20 | 321 | 61.69515 | 74.89074 | 21.66764 |
| kronos-small-ft | close | 20 | 321 | 63.95720 | 77.53671 | 23.46998 |
| kronos-small-ft | gap | 1 | 321 | 0.00361 | 0.00544 | 0.00107 |
| kronos-small-ft | intraday | 1 | 321 | 0.00738 | 0.01042 | 0.00149 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

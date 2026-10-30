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
| chronos2-ft | open | 1 | 321 | 44.37378 | 55.59241 | 41.11396 |
| chronos2-ft | close | 1 | 321 | 44.39887 | 55.73706 | 35.59775 |
| chronos2-ft | open | 5 | 321 | 47.13685 | 58.57959 | 26.93178 |
| chronos2-ft | close | 5 | 321 | 47.24442 | 58.71068 | 25.40220 |
| chronos2-ft | open | 20 | 321 | 53.97783 | 65.40310 | 13.95033 |
| chronos2-ft | close | 20 | 321 | 54.24316 | 65.56884 | 13.75594 |
| chronos2-ft | gap | 1 | 321 | 0.03509 | 0.04438 | 0.03255 |
| chronos2-ft | intraday | 1 | 321 | 0.00593 | 0.00867 | 0.00004 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

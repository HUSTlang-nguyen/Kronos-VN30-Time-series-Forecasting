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
| chronos2-ft | open | 1 | 321 | 9.44549 | 13.94808 | 6.18568 |
| chronos2-ft | close | 1 | 321 | 9.76917 | 15.29704 | 0.96805 |
| chronos2-ft | open | 5 | 321 | 21.77871 | 30.07682 | 1.57363 |
| chronos2-ft | close | 5 | 321 | 22.17231 | 31.74796 | 0.33010 |
| chronos2-ft | open | 20 | 321 | 41.15907 | 49.90238 | 1.13156 |
| chronos2-ft | close | 20 | 321 | 41.79388 | 51.23347 | 1.30666 |
| chronos2-ft | gap | 1 | 321 | 0.00736 | 0.01097 | 0.00482 |
| chronos2-ft | intraday | 1 | 321 | 0.00965 | 0.01334 | 0.00376 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

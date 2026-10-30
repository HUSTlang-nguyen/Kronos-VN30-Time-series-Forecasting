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
| chronos2-ft | open | 1 | 321 | 48.63416 | 60.41930 | 45.37435 |
| chronos2-ft | close | 1 | 321 | 48.70595 | 60.52673 | 39.90483 |
| chronos2-ft | open | 5 | 321 | 51.75995 | 63.71294 | 31.55487 |
| chronos2-ft | close | 5 | 321 | 51.88586 | 63.79681 | 30.04365 |
| chronos2-ft | open | 20 | 321 | 60.05153 | 72.27599 | 20.02402 |
| chronos2-ft | close | 20 | 321 | 60.34570 | 72.41176 | 19.85847 |
| chronos2-ft | gap | 1 | 321 | 0.03860 | 0.04842 | 0.03606 |
| chronos2-ft | intraday | 1 | 321 | 0.00592 | 0.00867 | 0.00004 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

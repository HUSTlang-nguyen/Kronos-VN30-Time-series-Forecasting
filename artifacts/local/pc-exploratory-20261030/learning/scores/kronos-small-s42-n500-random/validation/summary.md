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
| kronos-small-ft | open | 1 | 321 | 8.41136 | 13.61833 | 5.15155 |
| kronos-small-ft | close | 1 | 321 | 16.00315 | 26.28706 | 7.20203 |
| kronos-small-ft | open | 5 | 321 | 43.44669 | 59.43631 | 23.24161 |
| kronos-small-ft | close | 5 | 321 | 45.50645 | 61.36479 | 23.66424 |
| kronos-small-ft | open | 20 | 321 | 59.50026 | 77.94135 | 19.47275 |
| kronos-small-ft | close | 20 | 321 | 59.44529 | 78.12738 | 18.95806 |
| kronos-small-ft | gap | 1 | 321 | 0.00661 | 0.01081 | 0.00407 |
| kronos-small-ft | intraday | 1 | 321 | 0.00961 | 0.01533 | 0.00372 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

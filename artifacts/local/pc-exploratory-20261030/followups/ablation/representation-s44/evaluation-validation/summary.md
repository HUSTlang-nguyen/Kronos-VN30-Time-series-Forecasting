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
| representation-continuous | open | 1 | 321 | 6.01296 | 9.32838 | 2.75315 |
| representation-continuous | close | 1 | 321 | 10.41542 | 15.83795 | 1.61430 |
| representation-continuous | open | 5 | 321 | 33.94612 | 46.46704 | 13.74105 |
| representation-continuous | close | 5 | 321 | 36.02561 | 48.64087 | 14.18340 |
| representation-continuous | open | 20 | 321 | 92.29731 | 114.32002 | 52.26980 |
| representation-continuous | close | 20 | 321 | 91.52716 | 112.43248 | 51.03993 |
| representation-continuous | gap | 1 | 321 | 0.00466 | 0.00734 | 0.00212 |
| representation-continuous | intraday | 1 | 321 | 0.00621 | 0.00894 | 0.00032 |
| representation-quantized | open | 1 | 321 | 5.71986 | 8.68692 | 2.46005 |
| representation-quantized | close | 1 | 321 | 10.05073 | 15.07481 | 1.24961 |
| representation-quantized | open | 5 | 321 | 26.30324 | 37.78658 | 6.09816 |
| representation-quantized | close | 5 | 321 | 28.18971 | 40.35523 | 6.34750 |
| representation-quantized | open | 20 | 321 | 46.63046 | 60.96364 | 6.60296 |
| representation-quantized | close | 20 | 321 | 47.29462 | 61.84140 | 6.80739 |
| representation-quantized | gap | 1 | 321 | 0.00445 | 0.00690 | 0.00191 |
| representation-quantized | intraday | 1 | 321 | 0.00639 | 0.00916 | 0.00050 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

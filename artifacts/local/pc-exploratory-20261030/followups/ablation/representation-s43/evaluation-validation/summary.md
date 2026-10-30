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
| representation-continuous | open | 1 | 321 | 5.69354 | 8.40208 | 2.43372 |
| representation-continuous | close | 1 | 321 | 10.49710 | 15.14184 | 1.69597 |
| representation-continuous | open | 5 | 321 | 29.41464 | 38.70406 | 9.20956 |
| representation-continuous | close | 5 | 321 | 31.27772 | 41.13148 | 9.43550 |
| representation-continuous | open | 20 | 321 | 79.27237 | 96.17329 | 39.24486 |
| representation-continuous | close | 20 | 321 | 80.17944 | 96.68148 | 39.69222 |
| representation-continuous | gap | 1 | 321 | 0.00443 | 0.00665 | 0.00190 |
| representation-continuous | intraday | 1 | 321 | 0.00640 | 0.00914 | 0.00051 |
| representation-quantized | open | 1 | 321 | 4.91013 | 7.66944 | 1.65031 |
| representation-quantized | close | 1 | 321 | 10.23161 | 15.32350 | 1.43048 |
| representation-quantized | open | 5 | 321 | 28.28777 | 39.11552 | 8.08269 |
| representation-quantized | close | 5 | 321 | 30.26730 | 42.14598 | 8.42509 |
| representation-quantized | open | 20 | 321 | 79.17866 | 102.07675 | 39.15115 |
| representation-quantized | close | 20 | 321 | 79.31835 | 102.68791 | 38.83112 |
| representation-quantized | gap | 1 | 321 | 0.00383 | 0.00609 | 0.00129 |
| representation-quantized | intraday | 1 | 321 | 0.00621 | 0.00892 | 0.00032 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

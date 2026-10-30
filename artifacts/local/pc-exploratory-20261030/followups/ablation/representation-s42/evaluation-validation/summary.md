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
| representation-continuous | open | 1 | 321 | 5.11845 | 7.71491 | 1.85864 |
| representation-continuous | close | 1 | 321 | 10.11470 | 15.33175 | 1.31358 |
| representation-continuous | open | 5 | 321 | 26.96220 | 37.74202 | 6.75712 |
| representation-continuous | close | 5 | 321 | 29.44425 | 41.19202 | 7.60204 |
| representation-continuous | open | 20 | 321 | 79.30078 | 97.76350 | 39.27327 |
| representation-continuous | close | 20 | 321 | 78.83702 | 97.96175 | 38.34979 |
| representation-continuous | gap | 1 | 321 | 0.00399 | 0.00609 | 0.00145 |
| representation-continuous | intraday | 1 | 321 | 0.00664 | 0.00945 | 0.00075 |
| representation-quantized | open | 1 | 321 | 5.08368 | 7.94142 | 1.82387 |
| representation-quantized | close | 1 | 321 | 10.32866 | 15.16773 | 1.52754 |
| representation-quantized | open | 5 | 321 | 28.74825 | 38.02733 | 8.54317 |
| representation-quantized | close | 5 | 321 | 31.19278 | 40.88058 | 9.35057 |
| representation-quantized | open | 20 | 321 | 75.07435 | 105.42921 | 35.04684 |
| representation-quantized | close | 20 | 321 | 75.57815 | 103.94773 | 35.09092 |
| representation-quantized | gap | 1 | 321 | 0.00395 | 0.00631 | 0.00142 |
| representation-quantized | intraday | 1 | 321 | 0.00622 | 0.00896 | 0.00033 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

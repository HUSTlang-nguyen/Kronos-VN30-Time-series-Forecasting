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
| representation-continuous | open | 1 | 323 | 17.25774 | 22.92577 | 11.29849 |
| representation-continuous | close | 1 | 323 | 24.07455 | 32.70870 | 6.35223 |
| representation-continuous | open | 5 | 323 | 75.62894 | 98.65412 | 34.78303 |
| representation-continuous | close | 5 | 323 | 76.44634 | 98.57418 | 31.28172 |
| representation-continuous | open | 20 | 323 | 165.85380 | 216.13942 | 73.90309 |
| representation-continuous | close | 20 | 323 | 161.14293 | 206.77786 | 67.31730 |
| representation-continuous | gap | 1 | 323 | 0.00912 | 0.01201 | 0.00602 |
| representation-continuous | intraday | 1 | 323 | 0.00928 | 0.01264 | 0.00034 |
| representation-quantized | open | 1 | 323 | 15.24827 | 19.55398 | 9.28901 |
| representation-quantized | close | 1 | 323 | 22.96519 | 30.45785 | 5.24287 |
| representation-quantized | open | 5 | 323 | 64.53268 | 87.76378 | 23.68677 |
| representation-quantized | close | 5 | 323 | 66.29874 | 89.54775 | 21.13412 |
| representation-quantized | open | 20 | 323 | 148.46486 | 205.12357 | 56.51415 |
| representation-quantized | close | 20 | 323 | 148.39696 | 202.76736 | 54.57132 |
| representation-quantized | gap | 1 | 323 | 0.00832 | 0.01064 | 0.00522 |
| representation-quantized | intraday | 1 | 323 | 0.00959 | 0.01320 | 0.00064 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

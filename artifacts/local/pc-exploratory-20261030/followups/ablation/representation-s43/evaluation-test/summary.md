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
| representation-continuous | open | 1 | 323 | 14.32426 | 18.42029 | 8.36500 |
| representation-continuous | close | 1 | 323 | 22.85732 | 30.56288 | 5.13500 |
| representation-continuous | open | 5 | 323 | 59.65658 | 74.78514 | 18.81067 |
| representation-continuous | close | 5 | 323 | 61.49075 | 77.75886 | 16.32614 |
| representation-continuous | open | 20 | 323 | 127.48747 | 168.61306 | 35.53676 |
| representation-continuous | close | 20 | 323 | 128.45598 | 168.29541 | 34.63035 |
| representation-continuous | gap | 1 | 323 | 0.00776 | 0.00987 | 0.00466 |
| representation-continuous | intraday | 1 | 323 | 0.00990 | 0.01355 | 0.00096 |
| representation-quantized | open | 1 | 323 | 13.62360 | 17.84750 | 7.66434 |
| representation-quantized | close | 1 | 323 | 22.69657 | 29.66163 | 4.97424 |
| representation-quantized | open | 5 | 323 | 61.11162 | 76.36959 | 20.26571 |
| representation-quantized | close | 5 | 323 | 63.98253 | 79.93675 | 18.81791 |
| representation-quantized | open | 20 | 323 | 147.32100 | 195.16392 | 55.37028 |
| representation-quantized | close | 20 | 323 | 147.55274 | 194.10449 | 53.72710 |
| representation-quantized | gap | 1 | 323 | 0.00742 | 0.00972 | 0.00432 |
| representation-quantized | intraday | 1 | 323 | 0.00923 | 0.01278 | 0.00028 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

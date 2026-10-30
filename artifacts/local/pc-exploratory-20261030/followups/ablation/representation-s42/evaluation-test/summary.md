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
| representation-continuous | open | 1 | 323 | 13.88124 | 17.57711 | 7.92198 |
| representation-continuous | close | 1 | 323 | 21.56406 | 29.89882 | 3.84174 |
| representation-continuous | open | 5 | 323 | 56.73858 | 71.73827 | 15.89266 |
| representation-continuous | close | 5 | 323 | 60.10708 | 76.16338 | 14.94247 |
| representation-continuous | open | 20 | 323 | 140.00313 | 174.35672 | 48.05242 |
| representation-continuous | close | 20 | 323 | 143.52691 | 177.42917 | 49.70127 |
| representation-continuous | gap | 1 | 323 | 0.00747 | 0.00938 | 0.00437 |
| representation-continuous | intraday | 1 | 323 | 0.01019 | 0.01400 | 0.00125 |
| representation-quantized | open | 1 | 323 | 12.64427 | 16.31535 | 6.68502 |
| representation-quantized | close | 1 | 323 | 22.83274 | 30.48697 | 5.11042 |
| representation-quantized | open | 5 | 323 | 67.12833 | 88.23627 | 26.28242 |
| representation-quantized | close | 5 | 323 | 72.43048 | 92.71413 | 27.26587 |
| representation-quantized | open | 20 | 323 | 155.20261 | 204.47232 | 63.25190 |
| representation-quantized | close | 20 | 323 | 156.83231 | 201.62077 | 63.00667 |
| representation-quantized | gap | 1 | 323 | 0.00680 | 0.00870 | 0.00370 |
| representation-quantized | intraday | 1 | 323 | 0.00934 | 0.01279 | 0.00039 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

# VN30 snapshot experiment

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Open is VNDIRECT provider data; its construction on some sessions is uncertain. The actual future trading calendar is supplied to Kronos. VN30 is an index, so these metrics do not imply tradable profit.

| Model | Target | h | N | MAE | RMSE | MAE vs naive |
|---|---|---:|---:|---:|---:|---:|
| naive | open | 1 | 1442 | 2.11616 | 4.12994 | 0.00000 |
| naive | close | 1 | 1442 | 10.12086 | 14.86033 | 0.00000 |
| naive | open | 5 | 1442 | 22.28350 | 30.34175 | 0.00000 |
| naive | close | 5 | 1442 | 24.96063 | 33.58557 | 0.00000 |
| naive | open | 20 | 1442 | 50.14716 | 66.70904 | 0.00000 |
| naive | close | 20 | 1442 | 50.91420 | 68.04594 | 0.00000 |
| naive | gap | 1 | 1442 | 0.00180 | 0.00342 | 0.00000 |
| naive | intraday | 1 | 1442 | 0.00905 | 0.01315 | 0.00000 |
| ridge | open | 1 | 1442 | 10.59627 | 14.85757 | 8.48012 |
| ridge | close | 1 | 1442 | 14.60105 | 20.26352 | 4.48019 |
| ridge | open | 5 | 1442 | 24.14662 | 32.53167 | 1.86311 |
| ridge | close | 5 | 1442 | 26.43579 | 35.43048 | 1.47516 |
| ridge | open | 20 | 1442 | 47.25193 | 63.13420 | -2.89523 |
| ridge | close | 20 | 1442 | 47.96736 | 64.26653 | -2.94684 |
| ridge | gap | 1 | 1442 | 0.00994 | 0.01407 | 0.00814 |
| ridge | intraday | 1 | 1442 | 0.00892 | 0.01297 | -0.00013 |
| chronos2 | open | 1 | 1442 | 11.24378 | 16.01707 | 9.12762 |
| chronos2 | close | 1 | 1442 | 11.32246 | 16.32973 | 1.20160 |
| chronos2 | open | 5 | 1442 | 26.40280 | 35.71309 | 4.11930 |
| chronos2 | close | 5 | 1442 | 26.64326 | 36.07848 | 1.68263 |
| chronos2 | open | 20 | 1442 | 51.26080 | 70.14971 | 1.11364 |
| chronos2 | close | 20 | 1442 | 49.88039 | 67.66855 | -1.03382 |
| chronos2 | gap | 1 | 1442 | 0.01039 | 0.01468 | 0.00859 |
| chronos2 | intraday | 1 | 1442 | 0.01396 | 0.01984 | 0.00491 |
| kronos | open | 1 | 1442 | 5.42627 | 7.94089 | 3.31011 |
| kronos | close | 1 | 1442 | 11.79093 | 17.03604 | 1.67007 |
| kronos | open | 5 | 1442 | 27.04939 | 36.92125 | 4.76589 |
| kronos | close | 5 | 1442 | 30.40994 | 41.56811 | 5.44931 |
| kronos | open | 20 | 1442 | 79.00106 | 109.95034 | 28.85390 |
| kronos | close | 20 | 1442 | 80.34573 | 112.03804 | 29.43153 |
| kronos | gap | 1 | 1442 | 0.00501 | 0.00736 | 0.00321 |
| kronos | intraday | 1 | 1442 | 0.01047 | 0.01477 | 0.00142 |

Diagnostic high-volatility threshold: absolute Close return >= 0.020919 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

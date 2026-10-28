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
| ridge | open | 1 | 323 | 22.02059 | 27.82475 | 16.06133 |
| ridge | close | 1 | 323 | 28.80364 | 36.32526 | 11.08132 |
| ridge | open | 5 | 323 | 50.24313 | 60.49777 | 9.39722 |
| ridge | close | 5 | 323 | 54.01998 | 64.78414 | 8.85537 |
| ridge | open | 20 | 323 | 106.46529 | 129.03212 | 14.51458 |
| ridge | close | 20 | 323 | 108.39992 | 131.02727 | 14.57429 |
| ridge | gap | 1 | 323 | 0.01183 | 0.01487 | 0.00873 |
| ridge | intraday | 1 | 323 | 0.00918 | 0.01238 | 0.00023 |
| chronos2 | open | 1 | 323 | 21.04466 | 27.32574 | 15.08540 |
| chronos2 | close | 1 | 323 | 19.99463 | 26.48667 | 2.27230 |
| chronos2 | open | 5 | 323 | 48.65085 | 61.77541 | 7.80493 |
| chronos2 | close | 5 | 323 | 47.69938 | 59.96893 | 2.53477 |
| chronos2 | open | 20 | 323 | 103.22858 | 126.92427 | 11.27787 |
| chronos2 | close | 20 | 323 | 102.07242 | 125.48654 | 8.24679 |
| chronos2 | gap | 1 | 323 | 0.01130 | 0.01461 | 0.00820 |
| chronos2 | intraday | 1 | 323 | 0.01310 | 0.01808 | 0.00416 |
| kronos | open | 1 | 323 | 10.64439 | 14.28488 | 4.68513 |
| kronos | close | 1 | 323 | 19.75008 | 27.13198 | 2.02776 |
| kronos | open | 5 | 323 | 48.09212 | 60.30912 | 7.24621 |
| kronos | close | 5 | 323 | 53.29650 | 66.70679 | 8.13189 |
| kronos | open | 20 | 323 | 153.23669 | 192.83536 | 61.28598 |
| kronos | close | 20 | 323 | 155.23880 | 194.18955 | 61.41317 |
| kronos | gap | 1 | 323 | 0.00570 | 0.00764 | 0.00260 |
| kronos | intraday | 1 | 323 | 0.00929 | 0.01288 | 0.00034 |
| chronos2-ft | open | 1 | 323 | 20.25860 | 26.60980 | 14.29934 |
| chronos2-ft | close | 1 | 323 | 19.62304 | 26.34054 | 1.90072 |
| chronos2-ft | open | 5 | 323 | 48.45112 | 59.44100 | 7.60521 |
| chronos2-ft | close | 5 | 323 | 47.72128 | 58.54257 | 2.55667 |
| chronos2-ft | open | 20 | 323 | 100.42683 | 121.18264 | 8.47612 |
| chronos2-ft | close | 20 | 323 | 99.41115 | 120.38236 | 5.58552 |
| chronos2-ft | gap | 1 | 323 | 0.01085 | 0.01419 | 0.00775 |
| chronos2-ft | intraday | 1 | 323 | 0.01229 | 0.01692 | 0.00335 |
| kronos-ft | open | 1 | 323 | 9.88940 | 13.48648 | 3.93015 |
| kronos-ft | close | 1 | 323 | 19.59659 | 26.74760 | 1.87427 |
| kronos-ft | open | 5 | 323 | 52.16827 | 67.30134 | 11.32236 |
| kronos-ft | close | 5 | 323 | 55.37658 | 71.77460 | 10.21196 |
| kronos-ft | open | 20 | 323 | 130.78485 | 167.85099 | 38.83413 |
| kronos-ft | close | 20 | 323 | 138.30330 | 175.47473 | 44.47767 |
| kronos-ft | gap | 1 | 323 | 0.00531 | 0.00722 | 0.00221 |
| kronos-ft | intraday | 1 | 323 | 0.00961 | 0.01309 | 0.00066 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

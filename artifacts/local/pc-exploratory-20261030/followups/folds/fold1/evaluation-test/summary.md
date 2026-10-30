**THĂM DÒ — expanding fold, dataset unverified.**

# VN30 snapshot experiment

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Open is VNDIRECT provider data; its construction on some sessions is uncertain. The actual future trading calendar is supplied to Kronos. VN30 is an index, so these metrics do not imply tradable profit.

| Model | Target | h | N | MAE | RMSE | MAE vs naive |
|---|---|---:|---:|---:|---:|---:|
| naive | open | 1 | 208 | 2.79428 | 4.13173 | 0.00000 |
| naive | close | 1 | 208 | 9.47192 | 12.93167 | 0.00000 |
| naive | open | 5 | 208 | 20.26683 | 25.91719 | 0.00000 |
| naive | close | 5 | 208 | 22.36255 | 28.23607 | 0.00000 |
| naive | open | 20 | 208 | 40.01466 | 49.54619 | 0.00000 |
| naive | close | 20 | 208 | 40.00875 | 50.14990 | 0.00000 |
| naive | gap | 1 | 208 | 0.00251 | 0.00372 | 0.00000 |
| naive | intraday | 1 | 208 | 0.00780 | 0.01059 | 0.00000 |
| kronos-mini | open | 1 | 208 | 4.74380 | 6.26183 | 1.94952 |
| kronos-mini | close | 1 | 208 | 10.54142 | 14.42056 | 1.06950 |
| kronos-mini | open | 5 | 208 | 22.98152 | 28.60498 | 2.71470 |
| kronos-mini | close | 5 | 208 | 25.60031 | 31.50336 | 3.23776 |
| kronos-mini | open | 20 | 208 | 49.55173 | 60.89561 | 9.53706 |
| kronos-mini | close | 20 | 208 | 50.09812 | 61.61792 | 10.08937 |
| kronos-mini | gap | 1 | 208 | 0.00424 | 0.00560 | 0.00172 |
| kronos-mini | intraday | 1 | 208 | 0.00852 | 0.01164 | 0.00072 |
| kronos-mini-ft | open | 1 | 208 | 4.71415 | 6.22989 | 1.91987 |
| kronos-mini-ft | close | 1 | 208 | 10.47367 | 14.41621 | 1.00174 |
| kronos-mini-ft | open | 5 | 208 | 21.05920 | 26.81889 | 0.79237 |
| kronos-mini-ft | close | 5 | 208 | 23.65460 | 29.41738 | 1.29205 |
| kronos-mini-ft | open | 20 | 208 | 48.96435 | 58.58582 | 8.94969 |
| kronos-mini-ft | close | 20 | 208 | 49.68220 | 59.41957 | 9.67345 |
| kronos-mini-ft | gap | 1 | 208 | 0.00421 | 0.00557 | 0.00170 |
| kronos-mini-ft | intraday | 1 | 208 | 0.00843 | 0.01157 | 0.00063 |
| kronos-small | open | 1 | 208 | 4.82878 | 6.45523 | 2.03450 |
| kronos-small | close | 1 | 208 | 11.03858 | 15.29876 | 1.56666 |
| kronos-small | open | 5 | 208 | 24.84360 | 32.86110 | 4.57677 |
| kronos-small | close | 5 | 208 | 27.52572 | 35.37212 | 5.16317 |
| kronos-small | open | 20 | 208 | 57.67573 | 74.29738 | 17.66107 |
| kronos-small | close | 20 | 208 | 57.83108 | 74.21397 | 17.82233 |
| kronos-small | gap | 1 | 208 | 0.00433 | 0.00579 | 0.00181 |
| kronos-small | intraday | 1 | 208 | 0.00914 | 0.01255 | 0.00134 |
| kronos-small-ft | open | 1 | 208 | 4.86791 | 6.41072 | 2.07363 |
| kronos-small-ft | close | 1 | 208 | 10.98963 | 15.44102 | 1.51770 |
| kronos-small-ft | open | 5 | 208 | 25.69202 | 34.81069 | 5.42519 |
| kronos-small-ft | close | 5 | 208 | 27.70818 | 37.11762 | 5.34563 |
| kronos-small-ft | open | 20 | 208 | 59.56684 | 76.56161 | 19.55218 |
| kronos-small-ft | close | 20 | 208 | 59.61059 | 76.50765 | 19.60184 |
| kronos-small-ft | gap | 1 | 208 | 0.00435 | 0.00574 | 0.00184 |
| kronos-small-ft | intraday | 1 | 208 | 0.00908 | 0.01250 | 0.00128 |
| kronos-base | open | 1 | 208 | 4.61162 | 6.16627 | 1.81734 |
| kronos-base | close | 1 | 208 | 10.68296 | 15.01899 | 1.21104 |
| kronos-base | open | 5 | 208 | 24.00151 | 31.66617 | 3.73468 |
| kronos-base | close | 5 | 208 | 26.39532 | 34.55289 | 4.03277 |
| kronos-base | open | 20 | 208 | 67.02818 | 85.88227 | 27.01352 |
| kronos-base | close | 20 | 208 | 66.88535 | 85.32141 | 26.87660 |
| kronos-base | gap | 1 | 208 | 0.00411 | 0.00548 | 0.00160 |
| kronos-base | intraday | 1 | 208 | 0.00862 | 0.01184 | 0.00082 |
| kronos-base-ft | open | 1 | 208 | 5.01584 | 6.64082 | 2.22156 |
| kronos-base-ft | close | 1 | 208 | 11.52371 | 15.84234 | 2.05179 |
| kronos-base-ft | open | 5 | 208 | 24.66240 | 32.95193 | 4.39557 |
| kronos-base-ft | close | 5 | 208 | 25.39156 | 34.34331 | 3.02901 |
| kronos-base-ft | open | 20 | 208 | 56.70854 | 72.03250 | 16.69388 |
| kronos-base-ft | close | 20 | 208 | 56.35820 | 72.44252 | 16.34945 |
| kronos-base-ft | gap | 1 | 208 | 0.00448 | 0.00592 | 0.00197 |
| kronos-base-ft | intraday | 1 | 208 | 0.00915 | 0.01253 | 0.00136 |
| chronos2 | open | 1 | 208 | 10.33689 | 13.60026 | 7.54261 |
| chronos2 | close | 1 | 208 | 10.82938 | 14.25201 | 1.35746 |
| chronos2 | open | 5 | 208 | 24.27926 | 30.88407 | 4.01243 |
| chronos2 | close | 5 | 208 | 24.04614 | 30.98884 | 1.68359 |
| chronos2 | open | 20 | 208 | 44.51834 | 55.00509 | 4.50368 |
| chronos2 | close | 20 | 208 | 44.16514 | 54.17658 | 4.15639 |
| chronos2 | gap | 1 | 208 | 0.00921 | 0.01210 | 0.00670 |
| chronos2 | intraday | 1 | 208 | 0.01253 | 0.01621 | 0.00473 |
| chronos2-ft | open | 1 | 208 | 9.95115 | 13.01109 | 7.15687 |
| chronos2-ft | close | 1 | 208 | 10.41750 | 13.83104 | 0.94558 |
| chronos2-ft | open | 5 | 208 | 21.99667 | 28.04724 | 1.72984 |
| chronos2-ft | close | 5 | 208 | 22.21298 | 28.50057 | -0.14956 |
| chronos2-ft | open | 20 | 208 | 41.16685 | 49.71139 | 1.15219 |
| chronos2-ft | close | 20 | 208 | 40.95840 | 49.51347 | 0.94965 |
| chronos2-ft | gap | 1 | 208 | 0.00888 | 0.01158 | 0.00637 |
| chronos2-ft | intraday | 1 | 208 | 0.01149 | 0.01476 | 0.00370 |

Diagnostic high-volatility threshold: absolute Close return >= 0.016876 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

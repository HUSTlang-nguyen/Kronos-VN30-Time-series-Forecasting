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
| kronos-mini-ft | open | 1 | 208 | 4.72761 | 6.25683 | 1.93333 |
| kronos-mini-ft | close | 1 | 208 | 10.53659 | 14.47807 | 1.06467 |
| kronos-mini-ft | open | 5 | 208 | 20.99047 | 26.72889 | 0.72365 |
| kronos-mini-ft | close | 5 | 208 | 23.56801 | 29.31946 | 1.20547 |
| kronos-mini-ft | open | 20 | 208 | 48.87861 | 58.42130 | 8.86395 |
| kronos-mini-ft | close | 20 | 208 | 49.72858 | 59.38463 | 9.71983 |
| kronos-mini-ft | gap | 1 | 208 | 0.00422 | 0.00559 | 0.00171 |
| kronos-mini-ft | intraday | 1 | 208 | 0.00847 | 0.01161 | 0.00068 |
| kronos-small | open | 1 | 208 | 4.82878 | 6.45523 | 2.03450 |
| kronos-small | close | 1 | 208 | 11.03858 | 15.29876 | 1.56666 |
| kronos-small | open | 5 | 208 | 24.84360 | 32.86110 | 4.57677 |
| kronos-small | close | 5 | 208 | 27.52572 | 35.37212 | 5.16317 |
| kronos-small | open | 20 | 208 | 57.67573 | 74.29738 | 17.66107 |
| kronos-small | close | 20 | 208 | 57.83108 | 74.21397 | 17.82233 |
| kronos-small | gap | 1 | 208 | 0.00433 | 0.00579 | 0.00181 |
| kronos-small | intraday | 1 | 208 | 0.00914 | 0.01255 | 0.00134 |
| kronos-small-ft | open | 1 | 208 | 4.82508 | 6.38578 | 2.03080 |
| kronos-small-ft | close | 1 | 208 | 11.17710 | 15.66321 | 1.70517 |
| kronos-small-ft | open | 5 | 208 | 25.63849 | 34.99519 | 5.37166 |
| kronos-small-ft | close | 5 | 208 | 27.36352 | 37.18376 | 5.00097 |
| kronos-small-ft | open | 20 | 208 | 58.83770 | 75.50607 | 18.82304 |
| kronos-small-ft | close | 20 | 208 | 58.69074 | 75.37363 | 18.68199 |
| kronos-small-ft | gap | 1 | 208 | 0.00432 | 0.00572 | 0.00180 |
| kronos-small-ft | intraday | 1 | 208 | 0.00925 | 0.01270 | 0.00145 |
| kronos-base | open | 1 | 208 | 4.61162 | 6.16627 | 1.81734 |
| kronos-base | close | 1 | 208 | 10.68296 | 15.01899 | 1.21104 |
| kronos-base | open | 5 | 208 | 24.00151 | 31.66617 | 3.73468 |
| kronos-base | close | 5 | 208 | 26.39532 | 34.55289 | 4.03277 |
| kronos-base | open | 20 | 208 | 67.02818 | 85.88227 | 27.01352 |
| kronos-base | close | 20 | 208 | 66.88535 | 85.32141 | 26.87660 |
| kronos-base | gap | 1 | 208 | 0.00411 | 0.00548 | 0.00160 |
| kronos-base | intraday | 1 | 208 | 0.00862 | 0.01184 | 0.00082 |
| kronos-base-ft | open | 1 | 208 | 5.14947 | 6.78417 | 2.35519 |
| kronos-base-ft | close | 1 | 208 | 11.54216 | 15.89276 | 2.07024 |
| kronos-base-ft | open | 5 | 208 | 24.39773 | 32.84132 | 4.13090 |
| kronos-base-ft | close | 5 | 208 | 25.29715 | 34.50703 | 2.93460 |
| kronos-base-ft | open | 20 | 208 | 56.53969 | 69.89875 | 16.52502 |
| kronos-base-ft | close | 20 | 208 | 56.14894 | 70.43507 | 16.14019 |
| kronos-base-ft | gap | 1 | 208 | 0.00460 | 0.00605 | 0.00209 |
| kronos-base-ft | intraday | 1 | 208 | 0.00907 | 0.01252 | 0.00128 |
| chronos2 | open | 1 | 208 | 10.33689 | 13.60026 | 7.54261 |
| chronos2 | close | 1 | 208 | 10.82938 | 14.25201 | 1.35746 |
| chronos2 | open | 5 | 208 | 24.27926 | 30.88407 | 4.01243 |
| chronos2 | close | 5 | 208 | 24.04614 | 30.98884 | 1.68359 |
| chronos2 | open | 20 | 208 | 44.51834 | 55.00509 | 4.50368 |
| chronos2 | close | 20 | 208 | 44.16514 | 54.17658 | 4.15639 |
| chronos2 | gap | 1 | 208 | 0.00921 | 0.01210 | 0.00670 |
| chronos2 | intraday | 1 | 208 | 0.01253 | 0.01621 | 0.00473 |
| chronos2-ft | open | 1 | 208 | 9.87302 | 12.88048 | 7.07874 |
| chronos2-ft | close | 1 | 208 | 10.27875 | 13.75096 | 0.80682 |
| chronos2-ft | open | 5 | 208 | 21.44247 | 27.80353 | 1.17565 |
| chronos2-ft | close | 5 | 208 | 21.61516 | 28.28885 | -0.74739 |
| chronos2-ft | open | 20 | 208 | 41.63046 | 49.89441 | 1.61580 |
| chronos2-ft | close | 20 | 208 | 41.54180 | 49.91656 | 1.53305 |
| chronos2-ft | gap | 1 | 208 | 0.00881 | 0.01146 | 0.00630 |
| chronos2-ft | intraday | 1 | 208 | 0.01153 | 0.01477 | 0.00373 |

Diagnostic high-volatility threshold: absolute Close return >= 0.016876 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

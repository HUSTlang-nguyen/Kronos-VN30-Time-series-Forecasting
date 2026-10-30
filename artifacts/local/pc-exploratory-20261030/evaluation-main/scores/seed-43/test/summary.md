**THĂM DÒ — dataset unverified; không phải kết luận chính Q1–Q4.**

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
| ridge | open | 1 | 323 | 12.39224 | 16.25944 | 6.43298 |
| ridge | close | 1 | 323 | 21.59700 | 28.63462 | 3.87468 |
| ridge | open | 5 | 323 | 45.36805 | 55.66373 | 4.52214 |
| ridge | close | 5 | 323 | 49.59769 | 60.45875 | 4.43308 |
| ridge | open | 20 | 323 | 103.68281 | 124.11875 | 11.73210 |
| ridge | close | 20 | 323 | 105.21073 | 126.26861 | 11.38509 |
| ridge | gap | 1 | 323 | 0.00661 | 0.00859 | 0.00351 |
| ridge | intraday | 1 | 323 | 0.00933 | 0.01247 | 0.00038 |
| ets | open | 1 | 323 | 19.01664 | 25.37199 | 13.05738 |
| ets | close | 1 | 323 | 17.72232 | 24.52345 | 0.00000 |
| ets | open | 5 | 323 | 46.28804 | 56.75177 | 5.44212 |
| ets | close | 5 | 323 | 45.16461 | 55.73607 | 0.00000 |
| ets | open | 20 | 323 | 94.70040 | 116.31405 | 2.74969 |
| ets | close | 20 | 323 | 93.82563 | 115.25833 | 0.00000 |
| ets | gap | 1 | 323 | 0.01016 | 0.01350 | 0.00706 |
| ets | intraday | 1 | 323 | 0.01242 | 0.01718 | 0.00348 |
| arima | open | 1 | 323 | 18.99876 | 25.33499 | 13.03950 |
| arima | close | 1 | 323 | 17.72232 | 24.52345 | 0.00000 |
| arima | open | 5 | 323 | 46.26981 | 56.75029 | 5.42390 |
| arima | close | 5 | 323 | 45.16461 | 55.73607 | 0.00000 |
| arima | open | 20 | 323 | 94.71957 | 116.32868 | 2.76885 |
| arima | close | 20 | 323 | 93.82563 | 115.25833 | 0.00000 |
| arima | gap | 1 | 323 | 0.01015 | 0.01348 | 0.00705 |
| arima | intraday | 1 | 323 | 0.01239 | 0.01716 | 0.00345 |
| kronos-mini | open | 1 | 323 | 9.85111 | 12.82936 | 3.89185 |
| kronos-mini | close | 1 | 323 | 20.52904 | 27.76578 | 2.80672 |
| kronos-mini | open | 5 | 323 | 50.47060 | 61.96088 | 9.62469 |
| kronos-mini | close | 5 | 323 | 53.77584 | 65.84846 | 8.61123 |
| kronos-mini | open | 20 | 323 | 121.45704 | 153.51266 | 29.50633 |
| kronos-mini | close | 20 | 323 | 122.07889 | 153.12056 | 28.25325 |
| kronos-mini | gap | 1 | 323 | 0.00524 | 0.00677 | 0.00214 |
| kronos-mini | intraday | 1 | 323 | 0.00984 | 0.01316 | 0.00089 |
| kronos-mini-ft | open | 1 | 323 | 9.85958 | 12.82580 | 3.90033 |
| kronos-mini-ft | close | 1 | 323 | 19.84726 | 27.29183 | 2.12494 |
| kronos-mini-ft | open | 5 | 323 | 46.32649 | 57.03301 | 5.48058 |
| kronos-mini-ft | close | 5 | 323 | 50.25464 | 61.37717 | 5.09003 |
| kronos-mini-ft | open | 20 | 323 | 108.22855 | 133.74176 | 16.27784 |
| kronos-mini-ft | close | 20 | 323 | 109.09237 | 134.34082 | 15.26673 |
| kronos-mini-ft | gap | 1 | 323 | 0.00523 | 0.00675 | 0.00213 |
| kronos-mini-ft | intraday | 1 | 323 | 0.00960 | 0.01300 | 0.00065 |
| kronos-small | open | 1 | 323 | 10.40685 | 14.02436 | 4.44759 |
| kronos-small | close | 1 | 323 | 20.40287 | 27.47890 | 2.68055 |
| kronos-small | open | 5 | 323 | 48.41498 | 60.00802 | 7.56906 |
| kronos-small | close | 5 | 323 | 52.24570 | 64.89386 | 7.08109 |
| kronos-small | open | 20 | 323 | 152.53022 | 190.75028 | 60.57951 |
| kronos-small | close | 20 | 323 | 155.45122 | 193.27101 | 61.62558 |
| kronos-small | gap | 1 | 323 | 0.00559 | 0.00754 | 0.00249 |
| kronos-small | intraday | 1 | 323 | 0.00989 | 0.01308 | 0.00094 |
| kronos-small-ft | open | 1 | 323 | 10.35944 | 13.91418 | 4.40018 |
| kronos-small-ft | close | 1 | 323 | 20.59497 | 28.12742 | 2.87264 |
| kronos-small-ft | open | 5 | 323 | 51.68584 | 68.17102 | 10.83993 |
| kronos-small-ft | close | 5 | 323 | 55.45474 | 72.51057 | 10.29013 |
| kronos-small-ft | open | 20 | 323 | 133.46771 | 171.28028 | 41.51700 |
| kronos-small-ft | close | 20 | 323 | 138.43443 | 175.74736 | 44.60880 |
| kronos-small-ft | gap | 1 | 323 | 0.00554 | 0.00743 | 0.00244 |
| kronos-small-ft | intraday | 1 | 323 | 0.01013 | 0.01344 | 0.00118 |
| kronos-base | open | 1 | 323 | 10.59346 | 14.29369 | 4.63421 |
| kronos-base | close | 1 | 323 | 21.03912 | 28.26925 | 3.31680 |
| kronos-base | open | 5 | 323 | 50.80349 | 62.27481 | 9.95758 |
| kronos-base | close | 5 | 323 | 54.49211 | 68.34325 | 9.32750 |
| kronos-base | open | 20 | 323 | 164.08237 | 211.08441 | 72.13166 |
| kronos-base | close | 20 | 323 | 165.96114 | 212.58240 | 72.13550 |
| kronos-base | gap | 1 | 323 | 0.00567 | 0.00764 | 0.00257 |
| kronos-base | intraday | 1 | 323 | 0.00987 | 0.01334 | 0.00092 |
| kronos-base-ft | open | 1 | 323 | 10.68102 | 14.32745 | 4.72177 |
| kronos-base-ft | close | 1 | 323 | 21.49370 | 28.97303 | 3.77138 |
| kronos-base-ft | open | 5 | 323 | 49.96166 | 64.94521 | 9.11575 |
| kronos-base-ft | close | 5 | 323 | 54.36812 | 69.41233 | 9.20350 |
| kronos-base-ft | open | 20 | 323 | 97.69590 | 121.82508 | 5.74519 |
| kronos-base-ft | close | 20 | 323 | 98.87152 | 124.22642 | 5.04589 |
| kronos-base-ft | gap | 1 | 323 | 0.00573 | 0.00768 | 0.00263 |
| kronos-base-ft | intraday | 1 | 323 | 0.01040 | 0.01384 | 0.00146 |
| chronos2 | open | 1 | 323 | 21.04466 | 27.32574 | 15.08540 |
| chronos2 | close | 1 | 323 | 19.99462 | 26.48667 | 2.27230 |
| chronos2 | open | 5 | 323 | 48.65084 | 61.77541 | 7.80493 |
| chronos2 | close | 5 | 323 | 47.69938 | 59.96892 | 2.53477 |
| chronos2 | open | 20 | 323 | 103.22860 | 126.92429 | 11.27788 |
| chronos2 | close | 20 | 323 | 102.07243 | 125.48655 | 8.24680 |
| chronos2 | gap | 1 | 323 | 0.01130 | 0.01461 | 0.00820 |
| chronos2 | intraday | 1 | 323 | 0.01310 | 0.01808 | 0.00416 |
| chronos2-ft | open | 1 | 323 | 20.50205 | 27.84184 | 14.54279 |
| chronos2-ft | close | 1 | 323 | 20.16123 | 27.61161 | 2.43890 |
| chronos2-ft | open | 5 | 323 | 48.41340 | 60.78954 | 7.56749 |
| chronos2-ft | close | 5 | 323 | 47.96552 | 59.84043 | 2.80090 |
| chronos2-ft | open | 20 | 323 | 99.75261 | 121.44414 | 7.80190 |
| chronos2-ft | close | 20 | 323 | 99.04694 | 120.98824 | 5.22131 |
| chronos2-ft | gap | 1 | 323 | 0.01089 | 0.01472 | 0.00779 |
| chronos2-ft | intraday | 1 | 323 | 0.01258 | 0.01739 | 0.00363 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

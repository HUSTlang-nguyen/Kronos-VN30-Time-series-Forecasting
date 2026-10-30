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
| kronos-mini | open | 1 | 323 | 9.68332 | 12.64979 | 3.72406 |
| kronos-mini | close | 1 | 323 | 20.23718 | 27.44024 | 2.51486 |
| kronos-mini | open | 5 | 323 | 50.68966 | 61.90007 | 9.84375 |
| kronos-mini | close | 5 | 323 | 53.90409 | 66.41300 | 8.73947 |
| kronos-mini | open | 20 | 323 | 119.75848 | 151.94155 | 27.80777 |
| kronos-mini | close | 20 | 323 | 120.59567 | 152.26547 | 26.77003 |
| kronos-mini | gap | 1 | 323 | 0.00516 | 0.00669 | 0.00206 |
| kronos-mini | intraday | 1 | 323 | 0.00991 | 0.01331 | 0.00096 |
| kronos-mini-ft | open | 1 | 323 | 9.69080 | 12.61884 | 3.73155 |
| kronos-mini-ft | close | 1 | 323 | 19.37956 | 26.67171 | 1.65724 |
| kronos-mini-ft | open | 5 | 323 | 46.93123 | 57.73133 | 6.08532 |
| kronos-mini-ft | close | 5 | 323 | 49.94351 | 61.59618 | 4.77890 |
| kronos-mini-ft | open | 20 | 323 | 106.11554 | 131.13949 | 14.16483 |
| kronos-mini-ft | close | 20 | 323 | 106.56385 | 131.34225 | 12.73821 |
| kronos-mini-ft | gap | 1 | 323 | 0.00515 | 0.00666 | 0.00205 |
| kronos-mini-ft | intraday | 1 | 323 | 0.00953 | 0.01292 | 0.00059 |
| kronos-small | open | 1 | 323 | 10.23418 | 13.91321 | 4.27493 |
| kronos-small | close | 1 | 323 | 19.28950 | 26.42411 | 1.56718 |
| kronos-small | open | 5 | 323 | 49.51973 | 61.06359 | 8.67382 |
| kronos-small | close | 5 | 323 | 52.89691 | 65.35595 | 7.73230 |
| kronos-small | open | 20 | 323 | 150.59720 | 188.36571 | 58.64649 |
| kronos-small | close | 20 | 323 | 153.56796 | 190.36513 | 59.74233 |
| kronos-small | gap | 1 | 323 | 0.00552 | 0.00750 | 0.00242 |
| kronos-small | intraday | 1 | 323 | 0.00918 | 0.01257 | 0.00024 |
| kronos-small-ft | open | 1 | 323 | 9.90582 | 13.50037 | 3.94656 |
| kronos-small-ft | close | 1 | 323 | 19.64536 | 26.77614 | 1.92303 |
| kronos-small-ft | open | 5 | 323 | 52.29258 | 67.47761 | 11.44666 |
| kronos-small-ft | close | 5 | 323 | 55.60810 | 72.17550 | 10.44349 |
| kronos-small-ft | open | 20 | 323 | 131.05356 | 167.96626 | 39.10284 |
| kronos-small-ft | close | 20 | 323 | 138.72199 | 175.85511 | 44.89635 |
| kronos-small-ft | gap | 1 | 323 | 0.00531 | 0.00723 | 0.00221 |
| kronos-small-ft | intraday | 1 | 323 | 0.00962 | 0.01309 | 0.00067 |
| kronos-base | open | 1 | 323 | 10.23877 | 14.02753 | 4.27952 |
| kronos-base | close | 1 | 323 | 20.83493 | 28.12128 | 3.11260 |
| kronos-base | open | 5 | 323 | 50.06519 | 61.81890 | 9.21927 |
| kronos-base | close | 5 | 323 | 55.55627 | 69.51079 | 10.39166 |
| kronos-base | open | 20 | 323 | 164.95630 | 212.31984 | 73.00559 |
| kronos-base | close | 20 | 323 | 167.24379 | 214.90463 | 73.41815 |
| kronos-base | gap | 1 | 323 | 0.00548 | 0.00749 | 0.00238 |
| kronos-base | intraday | 1 | 323 | 0.00944 | 0.01296 | 0.00049 |
| kronos-base-ft | open | 1 | 323 | 10.10675 | 13.94615 | 4.14749 |
| kronos-base-ft | close | 1 | 323 | 20.75315 | 28.42244 | 3.03083 |
| kronos-base-ft | open | 5 | 323 | 48.97890 | 62.25066 | 8.13299 |
| kronos-base-ft | close | 5 | 323 | 54.40106 | 68.04672 | 9.23644 |
| kronos-base-ft | open | 20 | 323 | 96.10256 | 121.93950 | 4.15185 |
| kronos-base-ft | close | 20 | 323 | 97.31352 | 124.18143 | 3.48788 |
| kronos-base-ft | gap | 1 | 323 | 0.00541 | 0.00745 | 0.00231 |
| kronos-base-ft | intraday | 1 | 323 | 0.00960 | 0.01320 | 0.00066 |
| chronos2 | open | 1 | 323 | 21.04466 | 27.32574 | 15.08540 |
| chronos2 | close | 1 | 323 | 19.99462 | 26.48667 | 2.27230 |
| chronos2 | open | 5 | 323 | 48.65084 | 61.77541 | 7.80493 |
| chronos2 | close | 5 | 323 | 47.69938 | 59.96892 | 2.53477 |
| chronos2 | open | 20 | 323 | 103.22860 | 126.92429 | 11.27788 |
| chronos2 | close | 20 | 323 | 102.07243 | 125.48655 | 8.24680 |
| chronos2 | gap | 1 | 323 | 0.01130 | 0.01461 | 0.00820 |
| chronos2 | intraday | 1 | 323 | 0.01310 | 0.01808 | 0.00416 |
| chronos2-ft | open | 1 | 323 | 20.22070 | 26.53226 | 14.26144 |
| chronos2-ft | close | 1 | 323 | 19.65774 | 26.35277 | 1.93542 |
| chronos2-ft | open | 5 | 323 | 48.46909 | 59.40705 | 7.62318 |
| chronos2-ft | close | 5 | 323 | 47.93681 | 58.61035 | 2.77219 |
| chronos2-ft | open | 20 | 323 | 100.48656 | 121.24932 | 8.53585 |
| chronos2-ft | close | 20 | 323 | 99.49192 | 120.57895 | 5.66629 |
| chronos2-ft | gap | 1 | 323 | 0.01083 | 0.01414 | 0.00773 |
| chronos2-ft | intraday | 1 | 323 | 0.01220 | 0.01675 | 0.00326 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

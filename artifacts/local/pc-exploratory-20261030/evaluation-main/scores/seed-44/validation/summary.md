**THĂM DÒ — dataset unverified; không phải kết luận chính Q1–Q4.**

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
| ridge | open | 1 | 321 | 6.10887 | 9.35566 | 2.84906 |
| ridge | close | 1 | 321 | 10.64603 | 15.51241 | 1.84490 |
| ridge | open | 5 | 321 | 22.33645 | 30.28986 | 2.13137 |
| ridge | close | 5 | 321 | 24.77656 | 32.96773 | 2.93435 |
| ridge | open | 20 | 321 | 51.36215 | 62.10741 | 11.33464 |
| ridge | close | 20 | 321 | 52.35130 | 63.88536 | 11.86407 |
| ridge | gap | 1 | 321 | 0.00476 | 0.00737 | 0.00222 |
| ridge | intraday | 1 | 321 | 0.00606 | 0.00870 | 0.00017 |
| ets | open | 1 | 321 | 9.00389 | 13.39397 | 5.74408 |
| ets | close | 1 | 321 | 8.87316 | 14.24619 | 0.07204 |
| ets | open | 5 | 321 | 21.72235 | 30.06525 | 1.51727 |
| ets | close | 5 | 321 | 21.90707 | 31.38737 | 0.06486 |
| ets | open | 20 | 321 | 40.28819 | 50.28962 | 0.26068 |
| ets | close | 20 | 321 | 40.48951 | 51.53644 | 0.00228 |
| ets | gap | 1 | 321 | 0.00701 | 0.01050 | 0.00447 |
| ets | intraday | 1 | 321 | 0.00903 | 0.01265 | 0.00314 |
| arima | open | 1 | 321 | 8.96981 | 13.32711 | 5.71000 |
| arima | close | 1 | 321 | 8.80112 | 14.22747 | 0.00000 |
| arima | open | 5 | 321 | 21.66829 | 30.01557 | 1.46321 |
| arima | close | 5 | 321 | 21.84221 | 31.35171 | 0.00000 |
| arima | open | 20 | 321 | 40.27863 | 50.30683 | 0.25112 |
| arima | close | 20 | 321 | 40.48723 | 51.55992 | 0.00000 |
| arima | gap | 1 | 321 | 0.00698 | 0.01045 | 0.00444 |
| arima | intraday | 1 | 321 | 0.00915 | 0.01279 | 0.00326 |
| kronos-mini | open | 1 | 321 | 4.56631 | 7.51444 | 1.30650 |
| kronos-mini | close | 1 | 321 | 10.17542 | 14.87148 | 1.37430 |
| kronos-mini | open | 5 | 321 | 21.78176 | 29.91096 | 1.57668 |
| kronos-mini | close | 5 | 321 | 23.68675 | 32.28536 | 1.84454 |
| kronos-mini | open | 20 | 321 | 45.24206 | 53.12734 | 5.21456 |
| kronos-mini | close | 20 | 321 | 45.85721 | 53.79787 | 5.36998 |
| kronos-mini | gap | 1 | 321 | 0.00355 | 0.00595 | 0.00101 |
| kronos-mini | intraday | 1 | 321 | 0.00683 | 0.00933 | 0.00094 |
| kronos-mini-ft | open | 1 | 321 | 4.61457 | 7.55953 | 1.35476 |
| kronos-mini-ft | close | 1 | 321 | 10.22160 | 14.99567 | 1.42048 |
| kronos-mini-ft | open | 5 | 321 | 21.95590 | 30.61406 | 1.75082 |
| kronos-mini-ft | close | 5 | 321 | 24.09033 | 33.33170 | 2.24812 |
| kronos-mini-ft | open | 20 | 321 | 43.69491 | 52.26769 | 3.66741 |
| kronos-mini-ft | close | 20 | 321 | 43.71499 | 53.04395 | 3.22777 |
| kronos-mini-ft | gap | 1 | 321 | 0.00359 | 0.00598 | 0.00105 |
| kronos-mini-ft | intraday | 1 | 321 | 0.00672 | 0.00926 | 0.00083 |
| kronos-small | open | 1 | 321 | 4.64367 | 7.69213 | 1.38386 |
| kronos-small | close | 1 | 321 | 10.27605 | 15.78930 | 1.47493 |
| kronos-small | open | 5 | 321 | 21.19544 | 29.92681 | 0.99037 |
| kronos-small | close | 5 | 321 | 22.71834 | 32.21132 | 0.87613 |
| kronos-small | open | 20 | 321 | 40.69664 | 48.75805 | 0.66913 |
| kronos-small | close | 20 | 321 | 41.18090 | 49.72680 | 0.69368 |
| kronos-small | gap | 1 | 321 | 0.00362 | 0.00610 | 0.00108 |
| kronos-small | intraday | 1 | 321 | 0.00661 | 0.00946 | 0.00072 |
| kronos-small-ft | open | 1 | 321 | 4.66013 | 7.48670 | 1.40032 |
| kronos-small-ft | close | 1 | 321 | 10.72185 | 15.93601 | 1.92073 |
| kronos-small-ft | open | 5 | 321 | 24.86146 | 34.68728 | 4.65638 |
| kronos-small-ft | close | 5 | 321 | 27.27380 | 38.14483 | 5.43159 |
| kronos-small-ft | open | 20 | 321 | 38.41763 | 46.87312 | -1.60988 |
| kronos-small-ft | close | 20 | 321 | 38.78288 | 47.66495 | -1.70435 |
| kronos-small-ft | gap | 1 | 321 | 0.00363 | 0.00592 | 0.00109 |
| kronos-small-ft | intraday | 1 | 321 | 0.00679 | 0.00965 | 0.00090 |
| kronos-base | open | 1 | 321 | 4.78942 | 8.22872 | 1.52960 |
| kronos-base | close | 1 | 321 | 10.46208 | 15.71077 | 1.66096 |
| kronos-base | open | 5 | 321 | 21.88372 | 30.57113 | 1.67865 |
| kronos-base | close | 5 | 321 | 23.77062 | 32.96266 | 1.92840 |
| kronos-base | open | 20 | 321 | 45.55194 | 54.86185 | 5.52443 |
| kronos-base | close | 20 | 321 | 45.82342 | 55.64701 | 5.33620 |
| kronos-base | gap | 1 | 321 | 0.00373 | 0.00651 | 0.00119 |
| kronos-base | intraday | 1 | 321 | 0.00685 | 0.00953 | 0.00096 |
| kronos-base-ft | open | 1 | 321 | 4.67956 | 7.77823 | 1.41975 |
| kronos-base-ft | close | 1 | 321 | 10.52517 | 15.76527 | 1.72405 |
| kronos-base-ft | open | 5 | 321 | 25.45778 | 35.08068 | 5.25270 |
| kronos-base-ft | close | 5 | 321 | 27.81016 | 38.33138 | 5.96795 |
| kronos-base-ft | open | 20 | 321 | 43.55790 | 52.40114 | 3.53039 |
| kronos-base-ft | close | 20 | 321 | 44.33086 | 53.40320 | 3.84363 |
| kronos-base-ft | gap | 1 | 321 | 0.00364 | 0.00613 | 0.00110 |
| kronos-base-ft | intraday | 1 | 321 | 0.00677 | 0.00942 | 0.00088 |
| chronos2 | open | 1 | 321 | 9.38486 | 13.71403 | 6.12504 |
| chronos2 | close | 1 | 321 | 9.47971 | 14.99766 | 0.67859 |
| chronos2 | open | 5 | 321 | 21.48382 | 29.61195 | 1.27874 |
| chronos2 | close | 5 | 321 | 21.92711 | 31.10038 | 0.08490 |
| chronos2 | open | 20 | 321 | 40.05295 | 47.75902 | 0.02544 |
| chronos2 | close | 20 | 321 | 40.55627 | 48.79385 | 0.06904 |
| chronos2 | gap | 1 | 321 | 0.00731 | 0.01077 | 0.00477 |
| chronos2 | intraday | 1 | 321 | 0.00967 | 0.01340 | 0.00378 |
| chronos2-ft | open | 1 | 321 | 10.26863 | 16.11017 | 7.00882 |
| chronos2-ft | close | 1 | 321 | 10.70864 | 17.38240 | 1.90751 |
| chronos2-ft | open | 5 | 321 | 23.37386 | 33.47734 | 3.16878 |
| chronos2-ft | close | 5 | 321 | 23.74336 | 35.04536 | 1.90114 |
| chronos2-ft | open | 20 | 321 | 44.16563 | 54.70501 | 4.13813 |
| chronos2-ft | close | 20 | 321 | 44.55079 | 56.24144 | 4.06356 |
| chronos2-ft | gap | 1 | 321 | 0.00804 | 0.01293 | 0.00550 |
| chronos2-ft | intraday | 1 | 321 | 0.00928 | 0.01302 | 0.00339 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

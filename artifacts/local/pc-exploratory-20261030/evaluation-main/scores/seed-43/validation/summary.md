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
| kronos-mini | open | 1 | 321 | 4.60867 | 7.51871 | 1.34886 |
| kronos-mini | close | 1 | 321 | 10.06073 | 14.91836 | 1.25960 |
| kronos-mini | open | 5 | 321 | 21.48966 | 29.59147 | 1.28458 |
| kronos-mini | close | 5 | 321 | 23.40528 | 32.02793 | 1.56306 |
| kronos-mini | open | 20 | 321 | 44.52878 | 52.65403 | 4.50127 |
| kronos-mini | close | 20 | 321 | 44.93366 | 53.85865 | 4.44643 |
| kronos-mini | gap | 1 | 321 | 0.00358 | 0.00594 | 0.00104 |
| kronos-mini | intraday | 1 | 321 | 0.00651 | 0.00925 | 0.00062 |
| kronos-mini-ft | open | 1 | 321 | 4.67432 | 7.54573 | 1.41451 |
| kronos-mini-ft | close | 1 | 321 | 10.09927 | 14.90406 | 1.29815 |
| kronos-mini-ft | open | 5 | 321 | 22.49617 | 31.34266 | 2.29109 |
| kronos-mini-ft | close | 5 | 321 | 24.10545 | 33.70765 | 2.26324 |
| kronos-mini-ft | open | 20 | 321 | 43.62815 | 52.58505 | 3.60064 |
| kronos-mini-ft | close | 20 | 321 | 44.09463 | 53.64234 | 3.60741 |
| kronos-mini-ft | gap | 1 | 321 | 0.00363 | 0.00596 | 0.00110 |
| kronos-mini-ft | intraday | 1 | 321 | 0.00644 | 0.00911 | 0.00055 |
| kronos-small | open | 1 | 321 | 4.72445 | 7.77125 | 1.46463 |
| kronos-small | close | 1 | 321 | 10.18799 | 15.98369 | 1.38686 |
| kronos-small | open | 5 | 321 | 21.20244 | 29.80497 | 0.99737 |
| kronos-small | close | 5 | 321 | 22.15872 | 31.96390 | 0.31651 |
| kronos-small | open | 20 | 321 | 41.07400 | 49.05323 | 1.04649 |
| kronos-small | close | 20 | 321 | 41.52891 | 49.64371 | 1.04168 |
| kronos-small | gap | 1 | 321 | 0.00368 | 0.00615 | 0.00114 |
| kronos-small | intraday | 1 | 321 | 0.00639 | 0.00946 | 0.00050 |
| kronos-small-ft | open | 1 | 321 | 4.71067 | 7.71130 | 1.45086 |
| kronos-small-ft | close | 1 | 321 | 10.51740 | 16.05896 | 1.71627 |
| kronos-small-ft | open | 5 | 321 | 24.22791 | 34.22447 | 4.02284 |
| kronos-small-ft | close | 5 | 321 | 26.68580 | 37.95887 | 4.84358 |
| kronos-small-ft | open | 20 | 321 | 38.29794 | 45.93346 | -1.72957 |
| kronos-small-ft | close | 20 | 321 | 38.61415 | 46.75012 | -1.87307 |
| kronos-small-ft | gap | 1 | 321 | 0.00367 | 0.00610 | 0.00113 |
| kronos-small-ft | intraday | 1 | 321 | 0.00665 | 0.00978 | 0.00076 |
| kronos-base | open | 1 | 321 | 4.76047 | 7.77948 | 1.50065 |
| kronos-base | close | 1 | 321 | 10.29563 | 15.39232 | 1.49451 |
| kronos-base | open | 5 | 321 | 21.91715 | 30.24372 | 1.71207 |
| kronos-base | close | 5 | 321 | 23.48697 | 32.64922 | 1.64476 |
| kronos-base | open | 20 | 321 | 45.78724 | 54.94303 | 5.75973 |
| kronos-base | close | 20 | 321 | 46.01666 | 55.49863 | 5.52944 |
| kronos-base | gap | 1 | 321 | 0.00370 | 0.00613 | 0.00116 |
| kronos-base | intraday | 1 | 321 | 0.00632 | 0.00921 | 0.00043 |
| kronos-base-ft | open | 1 | 321 | 4.61962 | 7.80856 | 1.35980 |
| kronos-base-ft | close | 1 | 321 | 10.36179 | 15.73961 | 1.56067 |
| kronos-base-ft | open | 5 | 321 | 24.85961 | 34.59564 | 4.65453 |
| kronos-base-ft | close | 5 | 321 | 27.31593 | 37.90920 | 5.47372 |
| kronos-base-ft | open | 20 | 321 | 45.43362 | 54.18264 | 5.40611 |
| kronos-base-ft | close | 20 | 321 | 45.20212 | 54.43210 | 4.71489 |
| kronos-base-ft | gap | 1 | 321 | 0.00359 | 0.00617 | 0.00106 |
| kronos-base-ft | intraday | 1 | 321 | 0.00665 | 0.00962 | 0.00076 |
| chronos2 | open | 1 | 321 | 9.38486 | 13.71403 | 6.12504 |
| chronos2 | close | 1 | 321 | 9.47971 | 14.99766 | 0.67859 |
| chronos2 | open | 5 | 321 | 21.48382 | 29.61195 | 1.27874 |
| chronos2 | close | 5 | 321 | 21.92711 | 31.10038 | 0.08490 |
| chronos2 | open | 20 | 321 | 40.05295 | 47.75902 | 0.02544 |
| chronos2 | close | 20 | 321 | 40.55627 | 48.79385 | 0.06904 |
| chronos2 | gap | 1 | 321 | 0.00731 | 0.01077 | 0.00477 |
| chronos2 | intraday | 1 | 321 | 0.00967 | 0.01340 | 0.00378 |
| chronos2-ft | open | 1 | 321 | 9.91148 | 15.81053 | 6.65167 |
| chronos2-ft | close | 1 | 321 | 10.34056 | 17.24208 | 1.53944 |
| chronos2-ft | open | 5 | 321 | 23.01397 | 33.26485 | 2.80889 |
| chronos2-ft | close | 5 | 321 | 23.43763 | 34.94504 | 1.59541 |
| chronos2-ft | open | 20 | 321 | 43.43653 | 53.88073 | 3.40902 |
| chronos2-ft | close | 20 | 321 | 43.89970 | 55.46508 | 3.41247 |
| chronos2-ft | gap | 1 | 321 | 0.00773 | 0.01264 | 0.00519 |
| chronos2-ft | intraday | 1 | 321 | 0.00910 | 0.01283 | 0.00321 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

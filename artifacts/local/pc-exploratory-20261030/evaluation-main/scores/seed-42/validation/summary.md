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
| kronos-mini | open | 1 | 321 | 4.53747 | 7.59429 | 1.27765 |
| kronos-mini | close | 1 | 321 | 10.06310 | 15.04605 | 1.26198 |
| kronos-mini | open | 5 | 321 | 21.98271 | 29.71785 | 1.77763 |
| kronos-mini | close | 5 | 321 | 23.58608 | 31.87953 | 1.74387 |
| kronos-mini | open | 20 | 321 | 44.49451 | 52.25124 | 4.46700 |
| kronos-mini | close | 20 | 321 | 44.71595 | 52.71060 | 4.22872 |
| kronos-mini | gap | 1 | 321 | 0.00353 | 0.00602 | 0.00099 |
| kronos-mini | intraday | 1 | 321 | 0.00669 | 0.00939 | 0.00081 |
| kronos-mini-ft | open | 1 | 321 | 4.70351 | 7.72919 | 1.44370 |
| kronos-mini-ft | close | 1 | 321 | 10.27859 | 15.53136 | 1.47747 |
| kronos-mini-ft | open | 5 | 321 | 22.33571 | 31.19410 | 2.13064 |
| kronos-mini-ft | close | 5 | 321 | 23.98195 | 33.38646 | 2.13973 |
| kronos-mini-ft | open | 20 | 321 | 44.08084 | 52.85534 | 4.05333 |
| kronos-mini-ft | close | 20 | 321 | 43.92879 | 53.45676 | 3.44156 |
| kronos-mini-ft | gap | 1 | 321 | 0.00366 | 0.00612 | 0.00112 |
| kronos-mini-ft | intraday | 1 | 321 | 0.00675 | 0.00959 | 0.00086 |
| kronos-small | open | 1 | 321 | 4.66347 | 7.64300 | 1.40366 |
| kronos-small | close | 1 | 321 | 9.72625 | 15.33139 | 0.92513 |
| kronos-small | open | 5 | 321 | 20.64724 | 29.61120 | 0.44216 |
| kronos-small | close | 5 | 321 | 22.29947 | 32.32570 | 0.45726 |
| kronos-small | open | 20 | 321 | 39.83722 | 47.45547 | -0.19029 |
| kronos-small | close | 20 | 321 | 40.44763 | 48.58545 | -0.03959 |
| kronos-small | gap | 1 | 321 | 0.00364 | 0.00605 | 0.00110 |
| kronos-small | intraday | 1 | 321 | 0.00634 | 0.00919 | 0.00045 |
| kronos-small-ft | open | 1 | 321 | 4.65585 | 7.68924 | 1.39604 |
| kronos-small-ft | close | 1 | 321 | 10.33127 | 16.14467 | 1.53015 |
| kronos-small-ft | open | 5 | 321 | 24.19769 | 34.55904 | 3.99261 |
| kronos-small-ft | close | 5 | 321 | 26.73604 | 38.11325 | 4.89383 |
| kronos-small-ft | open | 20 | 321 | 38.01437 | 46.16324 | -2.01314 |
| kronos-small-ft | close | 20 | 321 | 38.65561 | 47.08700 | -1.83162 |
| kronos-small-ft | gap | 1 | 321 | 0.00362 | 0.00609 | 0.00109 |
| kronos-small-ft | intraday | 1 | 321 | 0.00669 | 0.00983 | 0.00081 |
| kronos-base | open | 1 | 321 | 4.66028 | 7.49955 | 1.40047 |
| kronos-base | close | 1 | 321 | 10.07209 | 15.48177 | 1.27097 |
| kronos-base | open | 5 | 321 | 21.71459 | 30.26485 | 1.50951 |
| kronos-base | close | 5 | 321 | 23.30180 | 32.70593 | 1.45959 |
| kronos-base | open | 20 | 321 | 45.60416 | 54.44758 | 5.57665 |
| kronos-base | close | 20 | 321 | 45.78840 | 55.41919 | 5.30118 |
| kronos-base | gap | 1 | 321 | 0.00363 | 0.00591 | 0.00109 |
| kronos-base | intraday | 1 | 321 | 0.00649 | 0.00938 | 0.00060 |
| kronos-base-ft | open | 1 | 321 | 4.46021 | 7.34283 | 1.20040 |
| kronos-base-ft | close | 1 | 321 | 10.02004 | 15.46415 | 1.21892 |
| kronos-base-ft | open | 5 | 321 | 24.49021 | 33.98570 | 4.28513 |
| kronos-base-ft | close | 5 | 321 | 27.02774 | 37.47165 | 5.18553 |
| kronos-base-ft | open | 20 | 321 | 42.75977 | 52.14513 | 2.73226 |
| kronos-base-ft | close | 20 | 321 | 43.55094 | 53.48757 | 3.06371 |
| kronos-base-ft | gap | 1 | 321 | 0.00347 | 0.00578 | 0.00093 |
| kronos-base-ft | intraday | 1 | 321 | 0.00667 | 0.00951 | 0.00079 |
| chronos2 | open | 1 | 321 | 9.38486 | 13.71403 | 6.12504 |
| chronos2 | close | 1 | 321 | 9.47971 | 14.99766 | 0.67859 |
| chronos2 | open | 5 | 321 | 21.48382 | 29.61195 | 1.27874 |
| chronos2 | close | 5 | 321 | 21.92711 | 31.10038 | 0.08490 |
| chronos2 | open | 20 | 321 | 40.05295 | 47.75902 | 0.02544 |
| chronos2 | close | 20 | 321 | 40.55627 | 48.79385 | 0.06904 |
| chronos2 | gap | 1 | 321 | 0.00731 | 0.01077 | 0.00477 |
| chronos2 | intraday | 1 | 321 | 0.00967 | 0.01340 | 0.00378 |
| chronos2-ft | open | 1 | 321 | 9.96498 | 15.51759 | 6.70517 |
| chronos2-ft | close | 1 | 321 | 10.29497 | 16.81609 | 1.49384 |
| chronos2-ft | open | 5 | 321 | 22.64067 | 32.44020 | 2.43559 |
| chronos2-ft | close | 5 | 321 | 23.05144 | 34.14783 | 1.20923 |
| chronos2-ft | open | 20 | 321 | 42.92710 | 52.80646 | 2.89959 |
| chronos2-ft | close | 20 | 321 | 43.46929 | 54.55238 | 2.98206 |
| chronos2-ft | gap | 1 | 321 | 0.00779 | 0.01238 | 0.00525 |
| chronos2-ft | intraday | 1 | 321 | 0.00885 | 0.01246 | 0.00296 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

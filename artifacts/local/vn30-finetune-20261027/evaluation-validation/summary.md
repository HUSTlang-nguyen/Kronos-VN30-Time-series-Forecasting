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
| ridge | open | 1 | 321 | 10.49612 | 14.75789 | 7.23631 |
| ridge | close | 1 | 321 | 13.97730 | 19.41530 | 5.17618 |
| ridge | open | 5 | 321 | 23.47520 | 30.48798 | 3.27013 |
| ridge | close | 5 | 321 | 25.32509 | 32.88327 | 3.48288 |
| ridge | open | 20 | 321 | 48.12889 | 57.59356 | 8.10138 |
| ridge | close | 20 | 321 | 48.93917 | 58.98097 | 8.45194 |
| ridge | gap | 1 | 321 | 0.00817 | 0.01157 | 0.00564 |
| ridge | intraday | 1 | 321 | 0.00594 | 0.00864 | 0.00005 |
| chronos2 | open | 1 | 321 | 9.38485 | 13.71403 | 6.12504 |
| chronos2 | close | 1 | 321 | 9.47971 | 14.99766 | 0.67859 |
| chronos2 | open | 5 | 321 | 21.48382 | 29.61195 | 1.27874 |
| chronos2 | close | 5 | 321 | 21.92711 | 31.10038 | 0.08490 |
| chronos2 | open | 20 | 321 | 40.05295 | 47.75902 | 0.02544 |
| chronos2 | close | 20 | 321 | 40.55626 | 48.79384 | 0.06903 |
| chronos2 | gap | 1 | 321 | 0.00731 | 0.01077 | 0.00477 |
| chronos2 | intraday | 1 | 321 | 0.00967 | 0.01340 | 0.00378 |
| kronos | open | 1 | 321 | 4.70205 | 7.70776 | 1.44224 |
| kronos | close | 1 | 321 | 10.19676 | 15.29722 | 1.39564 |
| kronos | open | 5 | 321 | 22.04774 | 30.40852 | 1.84267 |
| kronos | close | 5 | 321 | 22.92668 | 32.15319 | 1.08447 |
| kronos | open | 20 | 321 | 41.38412 | 49.68400 | 1.35662 |
| kronos | close | 20 | 321 | 41.54634 | 50.80746 | 1.05911 |
| kronos | gap | 1 | 321 | 0.00366 | 0.00608 | 0.00112 |
| kronos | intraday | 1 | 321 | 0.00636 | 0.00915 | 0.00047 |
| chronos2-ft | open | 1 | 321 | 9.91997 | 15.53499 | 6.66016 |
| chronos2-ft | close | 1 | 321 | 10.24471 | 16.76633 | 1.44359 |
| chronos2-ft | open | 5 | 321 | 22.64892 | 32.46575 | 2.44384 |
| chronos2-ft | close | 5 | 321 | 23.02263 | 34.12020 | 1.18042 |
| chronos2-ft | open | 20 | 321 | 42.91619 | 52.84750 | 2.88868 |
| chronos2-ft | close | 20 | 321 | 43.43149 | 54.40872 | 2.94427 |
| chronos2-ft | gap | 1 | 321 | 0.00776 | 0.01240 | 0.00522 |
| chronos2-ft | intraday | 1 | 321 | 0.00894 | 0.01259 | 0.00305 |
| kronos-ft | open | 1 | 321 | 4.65227 | 7.68600 | 1.39245 |
| kronos-ft | close | 1 | 321 | 10.33676 | 16.14877 | 1.53564 |
| kronos-ft | open | 5 | 321 | 24.19721 | 34.57834 | 3.99213 |
| kronos-ft | close | 5 | 321 | 26.73342 | 38.12996 | 4.89121 |
| kronos-ft | open | 20 | 321 | 37.96288 | 46.06384 | -2.06462 |
| kronos-ft | close | 20 | 321 | 38.57375 | 46.91183 | -1.91347 |
| kronos-ft | gap | 1 | 321 | 0.00362 | 0.00608 | 0.00108 |
| kronos-ft | intraday | 1 | 321 | 0.00670 | 0.00984 | 0.00081 |

Diagnostic high-volatility threshold: absolute Close return >= 0.014413 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

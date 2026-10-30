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
| kronos-mini | open | 1 | 323 | 9.64208 | 12.73544 | 3.68282 |
| kronos-mini | close | 1 | 323 | 20.99409 | 27.78905 | 3.27177 |
| kronos-mini | open | 5 | 323 | 48.49706 | 60.58021 | 7.65114 |
| kronos-mini | close | 5 | 323 | 52.35551 | 64.84345 | 7.19089 |
| kronos-mini | open | 20 | 323 | 120.90263 | 152.35767 | 28.95191 |
| kronos-mini | close | 20 | 323 | 122.03761 | 152.45400 | 28.21197 |
| kronos-mini | gap | 1 | 323 | 0.00512 | 0.00673 | 0.00203 |
| kronos-mini | intraday | 1 | 323 | 0.01016 | 0.01343 | 0.00121 |
| kronos-mini-ft | open | 1 | 323 | 9.86657 | 13.01297 | 3.90731 |
| kronos-mini-ft | close | 1 | 323 | 21.15456 | 27.91357 | 3.43224 |
| kronos-mini-ft | open | 5 | 323 | 47.37735 | 58.25666 | 6.53144 |
| kronos-mini-ft | close | 5 | 323 | 50.36685 | 62.12672 | 5.20224 |
| kronos-mini-ft | open | 20 | 323 | 109.21172 | 132.96435 | 17.26101 |
| kronos-mini-ft | close | 20 | 323 | 109.81299 | 133.87275 | 15.98735 |
| kronos-mini-ft | gap | 1 | 323 | 0.00525 | 0.00687 | 0.00215 |
| kronos-mini-ft | intraday | 1 | 323 | 0.01006 | 0.01330 | 0.00111 |
| kronos-small | open | 1 | 323 | 10.64394 | 14.21645 | 4.68468 |
| kronos-small | close | 1 | 323 | 20.02611 | 27.11859 | 2.30379 |
| kronos-small | open | 5 | 323 | 48.48803 | 60.57808 | 7.64212 |
| kronos-small | close | 5 | 323 | 52.61643 | 65.81699 | 7.45181 |
| kronos-small | open | 20 | 323 | 150.76621 | 189.27393 | 58.81549 |
| kronos-small | close | 20 | 323 | 153.40916 | 191.01198 | 59.58352 |
| kronos-small | gap | 1 | 323 | 0.00571 | 0.00763 | 0.00261 |
| kronos-small | intraday | 1 | 323 | 0.00954 | 0.01289 | 0.00060 |
| kronos-small-ft | open | 1 | 323 | 10.35807 | 13.99809 | 4.39881 |
| kronos-small-ft | close | 1 | 323 | 20.73859 | 28.34712 | 3.01627 |
| kronos-small-ft | open | 5 | 323 | 52.55358 | 67.68481 | 11.70766 |
| kronos-small-ft | close | 5 | 323 | 56.00714 | 72.55347 | 10.84253 |
| kronos-small-ft | open | 20 | 323 | 130.03491 | 167.84453 | 38.08420 |
| kronos-small-ft | close | 20 | 323 | 138.99271 | 177.37399 | 45.16708 |
| kronos-small-ft | gap | 1 | 323 | 0.00553 | 0.00745 | 0.00243 |
| kronos-small-ft | intraday | 1 | 323 | 0.01007 | 0.01363 | 0.00112 |
| kronos-base | open | 1 | 323 | 10.39095 | 14.13248 | 4.43169 |
| kronos-base | close | 1 | 323 | 20.79198 | 27.74704 | 3.06966 |
| kronos-base | open | 5 | 323 | 50.56305 | 62.82753 | 9.71714 |
| kronos-base | close | 5 | 323 | 55.39501 | 70.38044 | 10.23040 |
| kronos-base | open | 20 | 323 | 164.59452 | 210.83453 | 72.64381 |
| kronos-base | close | 20 | 323 | 167.13762 | 213.24948 | 73.31198 |
| kronos-base | gap | 1 | 323 | 0.00555 | 0.00754 | 0.00245 |
| kronos-base | intraday | 1 | 323 | 0.00968 | 0.01296 | 0.00073 |
| kronos-base-ft | open | 1 | 323 | 10.60922 | 14.44020 | 4.64997 |
| kronos-base-ft | close | 1 | 323 | 21.45386 | 29.04095 | 3.73153 |
| kronos-base-ft | open | 5 | 323 | 50.36864 | 64.73521 | 9.52273 |
| kronos-base-ft | close | 5 | 323 | 55.35818 | 70.23920 | 10.19356 |
| kronos-base-ft | open | 20 | 323 | 98.83578 | 123.39773 | 6.88506 |
| kronos-base-ft | close | 20 | 323 | 100.36294 | 123.95740 | 6.53730 |
| kronos-base-ft | gap | 1 | 323 | 0.00567 | 0.00770 | 0.00257 |
| kronos-base-ft | intraday | 1 | 323 | 0.01001 | 0.01360 | 0.00107 |
| chronos2 | open | 1 | 323 | 21.04466 | 27.32574 | 15.08540 |
| chronos2 | close | 1 | 323 | 19.99462 | 26.48667 | 2.27230 |
| chronos2 | open | 5 | 323 | 48.65084 | 61.77541 | 7.80493 |
| chronos2 | close | 5 | 323 | 47.69938 | 59.96892 | 2.53477 |
| chronos2 | open | 20 | 323 | 103.22860 | 126.92429 | 11.27788 |
| chronos2 | close | 20 | 323 | 102.07243 | 125.48655 | 8.24680 |
| chronos2 | gap | 1 | 323 | 0.01130 | 0.01461 | 0.00820 |
| chronos2 | intraday | 1 | 323 | 0.01310 | 0.01808 | 0.00416 |
| chronos2-ft | open | 1 | 323 | 21.29097 | 27.76344 | 15.33171 |
| chronos2-ft | close | 1 | 323 | 20.49374 | 27.56458 | 2.77142 |
| chronos2-ft | open | 5 | 323 | 49.33786 | 60.64952 | 8.49195 |
| chronos2-ft | close | 5 | 323 | 48.69265 | 59.68324 | 3.52804 |
| chronos2-ft | open | 20 | 323 | 102.19184 | 122.76004 | 10.24113 |
| chronos2-ft | close | 20 | 323 | 101.39012 | 122.26067 | 7.56448 |
| chronos2-ft | gap | 1 | 323 | 0.01140 | 0.01483 | 0.00830 |
| chronos2-ft | intraday | 1 | 323 | 0.01289 | 0.01789 | 0.00394 |

Diagnostic high-volatility threshold: absolute Close return >= 0.022047 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

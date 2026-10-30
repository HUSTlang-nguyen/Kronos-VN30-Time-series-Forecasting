**THĂM DÒ — expanding fold, dataset unverified.**

# VN30 snapshot experiment

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Open is VNDIRECT provider data; its construction on some sessions is uncertain. The actual future trading calendar is supplied to Kronos. VN30 is an index, so these metrics do not imply tradable profit.

| Model | Target | h | N | MAE | RMSE | MAE vs naive |
|---|---|---:|---:|---:|---:|---:|
| naive | open | 1 | 208 | 5.28649 | 7.78438 | 0.00000 |
| naive | close | 1 | 208 | 14.80288 | 20.92229 | 0.00000 |
| naive | open | 5 | 208 | 33.43736 | 42.79603 | 0.00000 |
| naive | close | 5 | 208 | 36.67966 | 46.64452 | 0.00000 |
| naive | open | 20 | 208 | 82.27894 | 102.04516 | 0.00000 |
| naive | close | 20 | 208 | 82.75957 | 103.92318 | 0.00000 |
| naive | gap | 1 | 208 | 0.00448 | 0.00670 | 0.00000 |
| naive | intraday | 1 | 208 | 0.01205 | 0.01713 | 0.00000 |
| kronos-mini | open | 1 | 208 | 9.88815 | 13.72197 | 4.60166 |
| kronos-mini | close | 1 | 208 | 17.97736 | 25.63351 | 3.17447 |
| kronos-mini | open | 5 | 208 | 40.83281 | 55.11770 | 7.39545 |
| kronos-mini | close | 5 | 208 | 43.01672 | 58.37763 | 6.33705 |
| kronos-mini | open | 20 | 208 | 106.65929 | 132.02500 | 24.38035 |
| kronos-mini | close | 20 | 208 | 109.32871 | 133.83692 | 26.56914 |
| kronos-mini | gap | 1 | 208 | 0.00847 | 0.01202 | 0.00399 |
| kronos-mini | intraday | 1 | 208 | 0.01426 | 0.02017 | 0.00221 |
| kronos-mini-ft | open | 1 | 208 | 9.68957 | 13.30559 | 4.40307 |
| kronos-mini-ft | close | 1 | 208 | 17.43454 | 24.31893 | 2.63165 |
| kronos-mini-ft | open | 5 | 208 | 36.30881 | 49.05121 | 2.87145 |
| kronos-mini-ft | close | 5 | 208 | 38.07818 | 52.03498 | 1.39851 |
| kronos-mini-ft | open | 20 | 208 | 94.02757 | 118.27488 | 11.74863 |
| kronos-mini-ft | close | 20 | 208 | 95.49001 | 119.09142 | 12.73044 |
| kronos-mini-ft | gap | 1 | 208 | 0.00831 | 0.01170 | 0.00383 |
| kronos-mini-ft | intraday | 1 | 208 | 0.01402 | 0.01959 | 0.00197 |
| kronos-small | open | 1 | 208 | 8.52194 | 11.43796 | 3.23544 |
| kronos-small | close | 1 | 208 | 16.59205 | 22.70557 | 1.78917 |
| kronos-small | open | 5 | 208 | 39.42974 | 51.62667 | 5.99238 |
| kronos-small | close | 5 | 208 | 43.60814 | 56.55372 | 6.92848 |
| kronos-small | open | 20 | 208 | 116.90322 | 142.79713 | 34.62428 |
| kronos-small | close | 20 | 208 | 120.19515 | 146.45092 | 37.43558 |
| kronos-small | gap | 1 | 208 | 0.00723 | 0.00976 | 0.00275 |
| kronos-small | intraday | 1 | 208 | 0.01322 | 0.01892 | 0.00117 |
| kronos-small-ft | open | 1 | 208 | 8.33135 | 11.06726 | 3.04486 |
| kronos-small-ft | close | 1 | 208 | 16.39680 | 22.11673 | 1.59392 |
| kronos-small-ft | open | 5 | 208 | 36.33084 | 47.96477 | 2.89349 |
| kronos-small-ft | close | 5 | 208 | 40.97693 | 52.76602 | 4.29726 |
| kronos-small-ft | open | 20 | 208 | 110.75635 | 133.51320 | 28.47741 |
| kronos-small-ft | close | 20 | 208 | 112.27055 | 136.57444 | 29.51098 |
| kronos-small-ft | gap | 1 | 208 | 0.00708 | 0.00949 | 0.00260 |
| kronos-small-ft | intraday | 1 | 208 | 0.01323 | 0.01881 | 0.00118 |
| kronos-base | open | 1 | 208 | 8.59850 | 11.96032 | 3.31201 |
| kronos-base | close | 1 | 208 | 16.49966 | 22.67292 | 1.69678 |
| kronos-base | open | 5 | 208 | 47.59479 | 63.62697 | 14.15744 |
| kronos-base | close | 5 | 208 | 54.94678 | 73.14738 | 18.26712 |
| kronos-base | open | 20 | 208 | 148.48414 | 181.32181 | 66.20520 |
| kronos-base | close | 20 | 208 | 152.03825 | 184.66036 | 69.27868 |
| kronos-base | gap | 1 | 208 | 0.00726 | 0.00998 | 0.00278 |
| kronos-base | intraday | 1 | 208 | 0.01301 | 0.01852 | 0.00096 |
| kronos-base-ft | open | 1 | 208 | 8.57152 | 11.03035 | 3.28503 |
| kronos-base-ft | close | 1 | 208 | 17.11414 | 23.05620 | 2.31126 |
| kronos-base-ft | open | 5 | 208 | 37.92350 | 48.56374 | 4.48614 |
| kronos-base-ft | close | 5 | 208 | 43.48197 | 55.16699 | 6.80231 |
| kronos-base-ft | open | 20 | 208 | 129.37567 | 159.24683 | 47.09673 |
| kronos-base-ft | close | 20 | 208 | 131.64422 | 162.46426 | 48.88466 |
| kronos-base-ft | gap | 1 | 208 | 0.00724 | 0.00936 | 0.00276 |
| kronos-base-ft | intraday | 1 | 208 | 0.01352 | 0.01949 | 0.00147 |
| chronos2 | open | 1 | 208 | 16.47011 | 23.05980 | 11.18362 |
| chronos2 | close | 1 | 208 | 15.96101 | 22.76597 | 1.15813 |
| chronos2 | open | 5 | 208 | 38.86993 | 49.54429 | 5.43257 |
| chronos2 | close | 5 | 208 | 39.91744 | 50.33842 | 3.23778 |
| chronos2 | open | 20 | 208 | 87.94736 | 111.84432 | 5.66842 |
| chronos2 | close | 20 | 208 | 79.66441 | 101.35290 | -3.09515 |
| chronos2 | gap | 1 | 208 | 0.01395 | 0.01972 | 0.00947 |
| chronos2 | intraday | 1 | 208 | 0.01800 | 0.02486 | 0.00595 |
| chronos2-ft | open | 1 | 208 | 16.98924 | 23.19284 | 11.70274 |
| chronos2-ft | close | 1 | 208 | 16.91449 | 22.91703 | 2.11161 |
| chronos2-ft | open | 5 | 208 | 38.24988 | 48.19400 | 4.81253 |
| chronos2-ft | close | 5 | 208 | 38.52051 | 48.28675 | 1.84085 |
| chronos2-ft | open | 20 | 208 | 78.98651 | 102.09614 | -3.29244 |
| chronos2-ft | close | 20 | 208 | 77.79471 | 100.32996 | -4.96486 |
| chronos2-ft | gap | 1 | 208 | 0.01437 | 0.01984 | 0.00990 |
| chronos2-ft | intraday | 1 | 208 | 0.01717 | 0.02401 | 0.00512 |

Diagnostic high-volatility threshold: absolute Close return >= 0.032689 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

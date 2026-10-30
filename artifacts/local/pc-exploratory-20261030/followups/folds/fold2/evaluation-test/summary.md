**THĂM DÒ — expanding fold, dataset unverified.**

# VN30 snapshot experiment

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Open is VNDIRECT provider data; its construction on some sessions is uncertain. The actual future trading calendar is supplied to Kronos. VN30 is an index, so these metrics do not imply tradable profit.

| Model | Target | h | N | MAE | RMSE | MAE vs naive |
|---|---|---:|---:|---:|---:|---:|
| naive | open | 1 | 208 | 2.79745 | 3.92283 | 0.00000 |
| naive | close | 1 | 208 | 8.39548 | 11.77011 | 0.00000 |
| naive | open | 5 | 208 | 19.51764 | 23.88753 | 0.00000 |
| naive | close | 5 | 208 | 20.58029 | 25.39085 | 0.00000 |
| naive | open | 20 | 208 | 36.06399 | 44.63198 | 0.00000 |
| naive | close | 20 | 208 | 36.07216 | 44.37733 | 0.00000 |
| naive | gap | 1 | 208 | 0.00219 | 0.00308 | 0.00000 |
| naive | intraday | 1 | 208 | 0.00593 | 0.00836 | 0.00000 |
| kronos-mini | open | 1 | 208 | 4.23940 | 5.36765 | 1.44195 |
| kronos-mini | close | 1 | 208 | 9.59155 | 12.91974 | 1.19607 |
| kronos-mini | open | 5 | 208 | 21.97087 | 26.06327 | 2.45322 |
| kronos-mini | close | 5 | 208 | 22.94951 | 27.46316 | 2.36923 |
| kronos-mini | open | 20 | 208 | 45.64790 | 53.16003 | 9.58391 |
| kronos-mini | close | 20 | 208 | 45.26478 | 52.72536 | 9.19261 |
| kronos-mini | gap | 1 | 208 | 0.00332 | 0.00421 | 0.00113 |
| kronos-mini | intraday | 1 | 208 | 0.00665 | 0.00915 | 0.00072 |
| kronos-mini-ft | open | 1 | 208 | 4.44046 | 5.53242 | 1.64300 |
| kronos-mini-ft | close | 1 | 208 | 9.77890 | 13.22730 | 1.38342 |
| kronos-mini-ft | open | 5 | 208 | 21.14500 | 25.86448 | 1.62736 |
| kronos-mini-ft | close | 5 | 208 | 22.36219 | 27.29215 | 1.78190 |
| kronos-mini-ft | open | 20 | 208 | 42.11747 | 49.78352 | 6.05348 |
| kronos-mini-ft | close | 20 | 208 | 41.48377 | 49.51454 | 5.41161 |
| kronos-mini-ft | gap | 1 | 208 | 0.00348 | 0.00434 | 0.00129 |
| kronos-mini-ft | intraday | 1 | 208 | 0.00665 | 0.00914 | 0.00072 |
| kronos-small | open | 1 | 208 | 4.34325 | 5.64024 | 1.54580 |
| kronos-small | close | 1 | 208 | 9.51547 | 12.96671 | 1.11999 |
| kronos-small | open | 5 | 208 | 20.11471 | 25.40720 | 0.59707 |
| kronos-small | close | 5 | 208 | 21.45634 | 27.22654 | 0.87606 |
| kronos-small | open | 20 | 208 | 42.92174 | 50.36688 | 6.85775 |
| kronos-small | close | 20 | 208 | 43.45645 | 51.15949 | 7.38428 |
| kronos-small | gap | 1 | 208 | 0.00342 | 0.00447 | 0.00123 |
| kronos-small | intraday | 1 | 208 | 0.00645 | 0.00892 | 0.00052 |
| kronos-small-ft | open | 1 | 208 | 4.22221 | 5.41711 | 1.42476 |
| kronos-small-ft | close | 1 | 208 | 10.21621 | 14.02004 | 1.82073 |
| kronos-small-ft | open | 5 | 208 | 22.58084 | 29.23204 | 3.06319 |
| kronos-small-ft | close | 5 | 208 | 24.61365 | 32.00497 | 4.03336 |
| kronos-small-ft | open | 20 | 208 | 40.09571 | 48.17440 | 4.03172 |
| kronos-small-ft | close | 20 | 208 | 40.31532 | 48.13341 | 4.24316 |
| kronos-small-ft | gap | 1 | 208 | 0.00332 | 0.00428 | 0.00112 |
| kronos-small-ft | intraday | 1 | 208 | 0.00694 | 0.00977 | 0.00101 |
| kronos-base | open | 1 | 208 | 4.27429 | 5.44960 | 1.47683 |
| kronos-base | close | 1 | 208 | 9.96535 | 13.60444 | 1.56987 |
| kronos-base | open | 5 | 208 | 20.66417 | 25.97579 | 1.14652 |
| kronos-base | close | 5 | 208 | 21.52561 | 27.48454 | 0.94533 |
| kronos-base | open | 20 | 208 | 52.78512 | 60.71258 | 16.72113 |
| kronos-base | close | 20 | 208 | 53.02939 | 61.72572 | 16.95722 |
| kronos-base | gap | 1 | 208 | 0.00336 | 0.00430 | 0.00117 |
| kronos-base | intraday | 1 | 208 | 0.00673 | 0.00938 | 0.00080 |
| kronos-base-ft | open | 1 | 208 | 4.09742 | 5.24033 | 1.29997 |
| kronos-base-ft | close | 1 | 208 | 10.08712 | 13.89231 | 1.69164 |
| kronos-base-ft | open | 5 | 208 | 24.04532 | 29.95189 | 4.52768 |
| kronos-base-ft | close | 5 | 208 | 26.40422 | 32.64879 | 5.82393 |
| kronos-base-ft | open | 20 | 208 | 41.49074 | 49.69396 | 5.42675 |
| kronos-base-ft | close | 20 | 208 | 42.15074 | 50.73765 | 6.07858 |
| kronos-base-ft | gap | 1 | 208 | 0.00322 | 0.00413 | 0.00102 |
| kronos-base-ft | intraday | 1 | 208 | 0.00711 | 0.00985 | 0.00118 |
| chronos2 | open | 1 | 208 | 9.15414 | 12.09247 | 6.35668 |
| chronos2 | close | 1 | 208 | 9.24126 | 12.82720 | 0.84578 |
| chronos2 | open | 5 | 208 | 20.75227 | 25.61384 | 1.23463 |
| chronos2 | close | 5 | 208 | 21.01971 | 25.92573 | 0.43942 |
| chronos2 | open | 20 | 208 | 37.39819 | 44.47493 | 1.33420 |
| chronos2 | close | 20 | 208 | 37.36873 | 44.06323 | 1.29657 |
| chronos2 | gap | 1 | 208 | 0.00721 | 0.00954 | 0.00501 |
| chronos2 | intraday | 1 | 208 | 0.00993 | 0.01357 | 0.00400 |
| chronos2-ft | open | 1 | 208 | 10.20945 | 12.86425 | 7.41200 |
| chronos2-ft | close | 1 | 208 | 10.44887 | 13.69063 | 2.05339 |
| chronos2-ft | open | 5 | 208 | 21.88588 | 26.47157 | 2.36824 |
| chronos2-ft | close | 5 | 208 | 21.97780 | 26.92765 | 1.39751 |
| chronos2-ft | open | 20 | 208 | 42.81024 | 50.48961 | 6.74624 |
| chronos2-ft | close | 20 | 208 | 42.64256 | 50.41628 | 6.57040 |
| chronos2-ft | gap | 1 | 208 | 0.00804 | 0.01015 | 0.00584 |
| chronos2-ft | intraday | 1 | 208 | 0.00916 | 0.01257 | 0.00323 |

Diagnostic high-volatility threshold: absolute Close return >= 0.015317 (90th percentile of this test set; descriptive only).
See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.

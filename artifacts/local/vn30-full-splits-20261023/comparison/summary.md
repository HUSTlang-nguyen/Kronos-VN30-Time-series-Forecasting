# VN30 full-split experiment

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`; 2271 chronological sessions.

| Split | Dates | Rows | Forecast origins |
|---|---|---:|---:|
| train | 2017-08-24 to 2023-12-29 | 1589 | 1442 |
| validation | 2024-01-02 to 2025-05-20 | 340 | 321 |
| test | 2025-05-21 to 2026-10-01 | 342 | 323 |

MAE is in VN30 index points; lower is better. Each forecast origin has a complete 20-session target path within its split.

| Split | Model | Open h1 | Close h1 | Open h5 | Close h5 | Open h20 | Close h20 |
|---|---|---:|---:|---:|---:|---:|---:|
| train | chronos2 | 11.24 | 11.32 | 26.40 | 26.64 | 51.26 | 49.88 |
| train | kronos | 5.43 | 11.79 | 27.05 | 30.41 | 79.00 | 80.35 |
| train | naive | 2.12 | 10.12 | 22.28 | 24.96 | 50.15 | 50.91 |
| train | ridge | 10.60 | 14.60 | 24.15 | 26.44 | 47.25 | 47.97 |
| validation | chronos2 | 9.38 | 9.48 | 21.48 | 21.93 | 40.05 | 40.56 |
| validation | kronos | 4.70 | 10.20 | 22.05 | 22.93 | 41.38 | 41.55 |
| validation | naive | 3.26 | 8.80 | 20.21 | 21.84 | 40.03 | 40.49 |
| validation | ridge | 10.50 | 13.98 | 23.48 | 25.33 | 48.13 | 48.94 |
| test | chronos2 | 21.04 | 19.99 | 48.65 | 47.70 | 103.23 | 102.07 |
| test | kronos | 10.64 | 19.75 | 48.09 | 53.30 | 153.24 | 155.24 |
| test | naive | 5.96 | 17.72 | 40.85 | 45.16 | 91.95 | 93.83 |
| test | ridge | 22.02 | 28.80 | 50.24 | 54.02 | 106.47 | 108.40 |

Ridge is fitted on train, so its train score is in-sample. Naive requires no fit; Chronos-2 and Kronos use pretrained checkpoints without VN30 fine-tuning.
Validation is for model/configuration comparison; test is the final historical holdout. This test period was already inspected in an earlier experiment, so it is not a newly untouched holdout.
Absolute MAE across different time periods also reflects changes in VN30 index level and market volatility; compare models primarily within the same split.
VNDIRECT Open construction is uncertain on some sessions. Kronos uses realized historical target-session dates as calendar features. These index errors do not establish trading performance.
Full MAE/RMSE, gap and intraday scores are in `scores_all_splits.csv`; per-split diagnostics are in the evaluation folders.

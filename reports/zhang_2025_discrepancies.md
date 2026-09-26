# Zhang (2025) Replication Discrepancy Log

## Source reviewed

- Hongyu Zhang, *Vietnam V30 Closing Price Forecast Based on ARIMA and ETS*.
- DOI landing page: <https://doi.org/10.54254/2754-1169/2024.GA19104>
- Publisher PDF: <https://aemps.ewapub.com/article/view/19104.pdf>
- Complete PDF pages reviewed: 29-34.

## Extracted protocol

| Item | Extracted value |
|---|---|
| Target | VN30 closing price |
| Raw frequency | Daily |
| Modeled frequency | Monthly |
| Aggregation | Daily observations averaged into monthly data |
| Exact data period | August 2016-March 2023 |
| Training statement | 2016-2023 |
| Test statement | 2023-2024 |
| ARIMA | ARIMA(2,2,1) |
| ETS | ETS(M,A,N) |
| Metric | RMSE; formula and evaluated dates not reported |
| ARIMA RMSE | 110.9214 |
| ETS RMSE | 68.6134 |

## Material discrepancies

1. The abstract and introduction state that ARIMA has lower RMSE and outperforms ETS. Table 2 reports ARIMA = 110.9214 and ETS = 68.6134, so the table implies the opposite.
2. The text directly below Table 2 and the conclusion state that ETS outperforms ARIMA. This agrees with the numeric table and conflicts with the abstract/introduction.
3. The data section states that observations end in March 2023, while the method/results describe 2023-2024 as a test set. The paper does not identify test actuals or explain how RMSE was calculated for dates beyond the reported sample.
4. The training interval is described as 2016-2023 and the test interval as 2023-2024. The exact cutoff and whether 2023 overlaps are not reported.
5. Figure 1 appears monthly and ends at March 2023, while forecast figures extend through 2024 and visually toward 2025. Exact forecast origins, horizons and evaluated points are absent.
6. The source of VN30 data is not reported. The publisher page states that data are available from the author upon reasonable request.
7. The daily-to-monthly averaging formula, treatment of incomplete months, missing sessions and adjustment policy are not reported.
8. ARIMA/ETS order-selection procedure, fitting software, constant/drift choice and interval construction are not reported.
9. RMSE is named but its formula, evaluation unit and sample size are not reported.
10. The title uses "V30" while the paper body describes VN30.

## Replication decision

An exact replication is currently impossible. The project will retain the reported ARIMA(2,2,1), ETS(M,A,N), monthly averaging and numeric RMSE values as a literature benchmark, then perform an explicitly labeled approximate replication after a VN30 source passes G1. Missing details will remain `not reported`; they will not be inferred from favorable results.

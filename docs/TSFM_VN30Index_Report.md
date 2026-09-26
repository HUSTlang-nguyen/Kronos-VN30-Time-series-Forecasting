**ĐỊNH HƯỚNG NGHIÊN CỨU  
Dự báo VN30 bằng Time-Series Foundation Models**

_Từ baseline ARIMA/ETS đến General TSFM và Financial K-line Foundation Model_

Mục tiêu của báo cáo này là thu hẹp project cũ từ một hệ thống dự báo nhiều tài sản (VN30, TSLA, MSTR; Naive/Moving Average/LSTM/Transformer) thành một nghiên cứu có câu hỏi khoa học rõ ràng, tập trung vào VN30 Index và khả năng chuyển giao của các mô hình nền tảng chuỗi thời gian.

# 1\. Quyết định phạm vi

Đề xuất chính: chọn VN30 Index làm đối tượng nghiên cứu duy nhất ở giai đoạn đầu. Lý do là VN30 có baseline công bố trực tiếp, ít bão hòa hơn TSLA và cho phép xây dựng một bài nghiên cứu theo hướng replication → extension thay vì chỉ benchmark nhiều model trên nhiều tài sản.

| Lựa chọn        | Novelty         | Dữ liệu/K-line                      | Vai trò phù hợp               |
| --------------- | --------------- | ----------------------------------- | ----------------------------- |
| TSLA            | Thấp–trung bình | Rất thuận lợi                       | Reproducibility / testbed     |
| VN30 Index      | Cao hơn         | OHLC khả thi; volume cần thận trọng | Replication + TSFM transfer   |
| 1 cổ phiếu VN30 | Cao             | OHLCV tự nhiên                      | K-line tokenization sạch nhất |

# 2\. Baseline và research gap

Baseline công bố trực tiếp: Zhang (2025) sử dụng dữ liệu VN30 giai đoạn 2016–2023 và so sánh ARIMA với ETS. Nghiên cứu mới nên trước hết tái lập protocol/baseline này càng sát càng tốt, sau đó mở rộng sang deep learning và pretrained TSFMs.

Research gap đề xuất: các nghiên cứu VN30 hiện có chủ yếu tập trung vào mô hình thống kê hoặc supervised learning; khả năng generalize/transfer của pretrained time-series foundation models, đặc biệt mô hình được pretrain chuyên biệt cho financial K-line, trên thị trường Việt Nam vẫn chưa được khảo sát đầy đủ.

# 3\. Câu hỏi nghiên cứu

- RQ1 — General-purpose TSFM có thể zero-shot forecast VN30 tốt hơn các baseline đơn giản và mô hình thống kê hay không?
- RQ2 — Financial K-line representation của Kronos có đem lại lợi thế so với general-purpose TSFM như Chronos hay không?
- RQ3 — Lợi ích của pretrained model thay đổi thế nào khi có ít dữ liệu VN30 để adaptation/fine-tuning?
- RQ4 — Kết quả có ổn định qua nhiều forecast horizon và volatility regime hay không?

# 4\. Bộ model tối giản

| Nhóm               | Model               | Mục đích                                                       |
| ------------------ | ------------------- | -------------------------------------------------------------- |
| Sanity baseline    | Naive / Random Walk | Kiểm tra model phức tạp có thực sự tạo giá trị dự báo.         |
| Published baseline | ARIMA + ETS         | Tái lập và mở rộng nghiên cứu VN30 đã công bố.                 |
| Train-from-scratch | DLinear hoặc LSTM   | Đại diện supervised deep learning không pretrain.              |
| General TSFM       | Chronos             | Đo transfer từ pretraining tổng quát.                          |
| Finance TSFM       | Kronos              | Đo lợi ích của pretraining và K-line tokenization chuyên biệt. |

# 5\. Dữ liệu và thiết kế thí nghiệm

Dữ liệu chính: VN30 daily OHLC từ nguồn đáng tin cậy; bổ sung volume/turnover chỉ khi định nghĩa và chất lượng dữ liệu phù hợp. Không tạo volume giả cho index. Kronos có thể được kiểm thử trước trên OHLC.

Evaluation nên dùng rolling-origin / walk-forward thay vì random split. Forecast horizons: 1, 5 và 20 phiên, tương ứng gần đúng với ngày, tuần và tháng giao dịch.

Hai target song song: (A) price level C(t+h); (B) return/log-return. Việc đánh giá return giúp tránh kết luận sai rằng model tốt chỉ vì mức giá có tính persistence cao.

# 6\. Evaluation

- Price: MAE, RMSE, sMAPE, MASE. MASE < 1 cho biết model tốt hơn Naive theo cùng protocol.
- Return: MAE/RMSE trên return và Directional Accuracy.
- Probabilistic forecast (nếu hỗ trợ): pinball loss/CRPS và interval coverage.
- Robustness: đánh giá theo volatility regime.
- Statistical significance: Diebold–Mariano test và/hoặc block bootstrap confidence intervals.

# 7\. Experiment quan trọng nhất

Đối với Chronos/Kronos, không chỉ chạy một cấu hình. Nghiên cứu nên tách: zero-shot → data-limited adaptation/few-shot → full fine-tuning. Như vậy có thể phân biệt lợi ích đến từ kiến thức pretraining với lợi ích do adaptation trên VN30.

# 8\. Contribution dự kiến

- Replication có kiểm soát của baseline ARIMA/ETS trên VN30.
- Benchmark thống nhất giữa classical, train-from-scratch, general TSFM và finance-specific TSFM.
- Đánh giá khả năng cross-market transfer sang một emerging market.
- Phân tích zero-shot/fine-tuning, nhiều horizon và volatility regime.
- Kết quả âm vẫn có giá trị: nếu ARIMA/Naive thắng Kronos, điều đó là bằng chứng về giới hạn transfer chứ không phải thất bại của nghiên cứu.

# 9\. Điểm cần quyết định trước khi triển khai

Decision gate: sau khi kiểm tra nguồn dữ liệu VN30 OHLC lịch sử và khả năng tái lập baseline 2016–2023, nếu dữ liệu index đủ sạch thì tiếp tục với VN30 Index. Nếu K-line/volume của index gây hạn chế đáng kể cho Kronos, chuyển sang một cổ phiếu thuộc VN30 có lịch sử dài và thanh khoản cao, nhưng giữ nguyên research questions và protocol.

# 10\. Tài liệu nền tảng đã xác minh

1. Zhang, H. (2025). Vietnam V30 Closing Price Forecast Based on ARIMA and ETS. Advances in Economics, Management and Political Sciences, 147, 29–34. DOI: 10.54254/2754-1169/2024.GA19104.
2. Ansari, A. F., et al. (2024). Chronos: Learning the Language of Time Series. Transactions on Machine Learning Research (TMLR). OpenReview: gerNCVqqtR.
3. Shi, Y., Fu, Z., Chen, S., et al. (2026). Kronos: A Foundation Model for the Language of Financial Markets. AAAI 2026, 40(30), 25366–25373. DOI: 10.1609/aaai.v40i30.39730.
4. Ho Chi Minh Stock Exchange (HOSE). HOSE-Index Ground Rule – Version 4.0, effective from March 2025; VN30 capping includes 10% per stock, 15% for related-stock groups and 40% per sector.

**Kết luận: ưu tiên VN30 Index cho replication + TSFM transfer; giữ phương án 1 cổ phiếu VN30 làm fallback nếu representation của index hạn chế thí nghiệm K-line.**
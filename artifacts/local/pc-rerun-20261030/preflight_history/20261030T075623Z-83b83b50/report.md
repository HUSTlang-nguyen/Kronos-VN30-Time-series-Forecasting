# VN30 — kết quả làm lại trên PC

Trạng thái: **chưa hoàn thành**.

Kết quả dưới đây chỉ từ lượt chạy PC này. Không dùng forecast/checkpoint fine-tune của môi trường cũ.

Công việc hoàn thành: 5/288. Ngân sách tổng: 24 giờ; không reset khi resume.

Kiểm toán dữ liệu: **unverified**; dataset SHA256 `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.

Xem [kiểm toán](audit/summary.md).

| Câu hỏi | Bằng chứng đã chạy |
|---|---|
| Q1 — zero-shot và baseline | 0/83 công việc; chưa đủ |
| Q2 — kích thước và lượng tử hóa | 0/3 công việc; chưa đủ |
| Q3 — lượng dữ liệu và pretraining | 0/138 công việc; chưa đủ |
| Q4 — seed, horizon, volatility và fold | 0/135 công việc; chưa đủ |

## Giới hạn diễn giải

- Test là lịch sử đã được xem. Cutoff pretraining chưa xác minh đầy đủ; không tuyên bố backtest triển khai lịch sử sạch.
- Mini khác tokenizer; chênh lệch không chỉ do số tham số.
- Quantization ablation chỉ kiểm tra can thiệp đó với encoder cố định, không chứng minh toàn bộ lợi ích K-line.
- Kronos random control vẫn dùng tokenizer pretrained; đối chứng chỉ tách predictor pretraining.
- Origin chồng lấn; bootstrap dùng block 20. Seed không phải mẫu thị trường độc lập.
- Open phụ thuộc kiểm toán nguồn; không suy ra lợi nhuận giao dịch từ sai số chỉ số.

## Phần còn thiếu

Xem [danh sách công việc còn thiếu](remaining.json) và logs tương ứng.

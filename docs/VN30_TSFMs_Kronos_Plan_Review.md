# Review kế hoạch triển khai VN30 TSFMs / Kronos

Ngày: 26/09/2026. Đã chỉnh trực tiếp `VN30_TSFMs_Kronos_Technical_Implementation_Plan.md` thành bản v2. Đây là review thiết kế và mã nguồn thư viện công khai, chưa phải xác nhận mô hình đã chạy.

## Nhận xét chung

Kế hoạch có nền tảng tốt, nhưng bản ban đầu chưa nên dùng ngay để chạy benchmark chính. Vấn đề quan trọng nhất là giai đoạn test có thể nằm trong dữ liệu tiền huấn luyện của foundation model. Nếu không sửa, kết quả tốt vẫn khó bảo vệ trước phản biện.

## Điểm mạnh được giữ lại

- Phạm vi một chỉ số, dữ liệu ngày và câu hỏi chuyển giao rõ ràng.
- Có Naive, ARIMA/ETS và mô hình học từ đầu làm đối chứng.
- Tách replication bài cũ khỏi thí nghiệm mới; không đoán thông số thiếu.
- Kiểm soát OHLC, không giả tạo volume cho VN30.
- Có snapshot, hash, prediction artifacts và kiểm tra rò rỉ dữ liệu.
- Chấp nhận kết quả âm; không mặc định Kronos phải thắng.

## Các điểm yếu và chỉnh sửa chính

| Mức độ | Vấn đề trong bản cũ | Chỉnh sửa trong v2 |
|---|---|---|
| Nghiêm trọng | Test 2021-2024 nhưng dùng checkpoint ra đời sau đó; chronological split chưa đủ loại trừ pretraining contamination | Tách historical diagnostic, benchmark có provenance và kiểm chứng tiến cứu. Chọn mốc theo đúng revision của từng checkpoint; thiếu dữ liệu sạch thì báo pilot |
| Cao | Chưa khóa rõ cửa sổ nhãn, early stopping và tái huấn luyện | Purge nhãn 20 phiên vượt ranh giới; validation tách biệt; chọn số epoch rồi refit trước test |
| Cao | ARIMA/ETS có thể dùng trạng thái từ đầu fold, còn TSFM dùng context mới nhất | Cập nhật trạng thái thống kê bằng các quan sát đã đến, giữ tham số cố định trong holdout chính |
| Cao | DLinear-OHLC được hiểu như mô hình kết hợp các kênh | DLinear gốc chiếu từng kênh riêng; giữ làm baseline và thêm Ridge-OHLC có trộn kênh |
| Cao | `MASE < 1` bị diễn giải thành thắng Naive trên test | Sửa thành so với thang sai số Naive trong train; bổ sung skill trực tiếp so với Naive trên cùng test |
| Cao | Point forecast chưa thống nhất mean/median | Dùng median cho các TSFM trong so sánh MAE chính; giữ mean làm phân tích phụ |
| Cao | Trading value có thể bị mất khi đưa vào Kronos | Truyền rõ `volume=0`, `amount=trade_value`; kiểm tra không bị ghi đè; chỉ chạy khi ngữ nghĩa dữ liệu được xác minh |
| Cao | API DataFrame có thể tự tạo ngày không đúng lịch HOSE hoặc vô tình nhận OHLC tương lai | Dùng tensor theo thứ tự phiên; map về lịch thật; cấm future OHLC và cross-learning giữa origin khác thời điểm |
| Trung bình | Quá nhiều model, horizon, fine-tuning, regime và kiểm định cho 6-8 tuần | Chốt MAE h=1 và hai so sánh chính; adaptation/data-efficiency là phần mở rộng |
| Trung bình | Cửa sổ 512 với dữ liệu một năm không đủ tạo mẫu | Tính số cửa sổ thực sau holdout/purge; đánh dấu cấu hình không khả thi |
| Trung bình | Chưa rõ lỗi dự báo, resume, ghép năm và ý nghĩa các seed | Lưu origin manifest, failure status và seed ổn định; không coi seed là quan sát thị trường độc lập |

## Những giới hạn vẫn cần giải quyết khi triển khai

1. Chưa xác minh nguồn OHLC VN30 đủ dài và quyền sử dụng; cần pilot tải dữ liệu và đối chiếu nguồn thứ hai.
2. Chưa xác định ngày phát hành/cutoff của chính xác revision Chronos-2-small sẽ dùng. Ngày phát hành cả họ mô hình không thay thế được bằng chứng này.
3. Mốc 63 phiên validation và tối thiểu 126 origin test là quy tắc lập kế hoạch, không bảo đảm đủ lực thống kê, nhất là h=20 và phân tích regime.
4. Kiểm soát cùng OHLC chưa chứng minh tokenization là nguyên nhân của chênh lệch: corpus, kiến trúc và cách huấn luyện vẫn khác nhau.
5. Chưa đo GPU, latency hay khả năng fine-tuning. Chạy pilot trước khi chốt khối lượng thí nghiệm.

## Thứ tự thực hiện đề nghị

**Dev:** xác minh checkpoint và nguồn dữ liệu → khóa split/origin → Naive/ARIMA/ETS → DLinear-C/Ridge-OHLC → Chronos-2/Kronos zero-shot → adaptation nếu còn nguồn lực.

**Test:** kiểm tra lịch phiên, nhãn không vượt split, cập nhật trạng thái ARIMA, median/mean, zero-volume/amount và dự báo không đổi khi thay dữ liệu tương lai.

**Checklist:** chỉ chạy test chính sau khi khóa config; giữ toàn bộ lỗi/coverage; xuất kết quả từ artifacts; ghi rõ pilot nếu chưa đủ holdout sạch.

## Nguồn đối chiếu trực tiếp

- [Kronos Appendix D](https://arxiv.org/html/2508.02739v1): cutoff tiền huấn luyện tới tháng 6/2024.
- [Chronos repository](https://github.com/amazon-science/chronos-forecasting) và [Chronos-2-small model card](https://huggingface.co/autogluon/chronos-2-small): model ID, multivariate support và thông tin phát hành.
- [Kronos predictor](https://raw.githubusercontent.com/shiyu-coder/Kronos/master/model/kronos.py): volume/amount và tổng hợp đường mẫu.
- [DLinear gốc](https://raw.githubusercontent.com/cure-lab/LTSF-Linear/main/models/DLinear.py): phép chiếu theo từng kênh.
- [Chronos-2 pipeline](https://raw.githubusercontent.com/amazon-science/chronos-forecasting/main/src/chronos/chronos2/pipeline.py): median, covariate và điều kiện timestamp.

Các URL mã nguồn có thể thay đổi; cần pin commit khi thực hiện.

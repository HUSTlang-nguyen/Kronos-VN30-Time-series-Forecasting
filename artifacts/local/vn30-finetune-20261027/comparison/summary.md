# VN30 — fine-tune và so sánh zero-shot

Dataset SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`. Giữ nguyên snapshot 2.271 phiên và split 70/15/15.

Train: 1.589 phiên/1.442 cửa sổ; validation: 340/321; test: 342/323. Context 128, horizon 20.

Fine-tune toàn bộ trọng số mô hình; Kronos giữ tokenizer pretrained cố định. Dùng AdamW và FP32. Mọi cửa sổ train được dùng một lần mỗi epoch. Checkpoint được chọn bằng validation loss trong các epoch đã huấn luyện; test không tham gia cập nhật trọng số hoặc chọn checkpoint.

| Model | Epoch chọn | Validation loss trước | Validation loss sau | Train + validation (giây) | PyTorch allocated peak (MiB) |
|---|---:|---:|---:|---:|---:|
| chronos2 | 1 | 2.5728 | 2.7766 | 116.5 | 577.5 |
| kronos | 5 | 2.1583 | 1.9646 | 170.5 | 796.1 |

- chronos2: 5 epoch, learning rate 1e-06, batch 8 cửa sổ × accumulation 2, seed 42, device cuda:0.
- kronos: 5 epoch, learning rate 1e-06, batch 8 cửa sổ × accumulation 2, seed 42, device cuda:0.

Validation loss chỉ so sánh trước/sau trong cùng model: Chronos dùng quantile loss, Kronos dùng token cross-entropy cho 20 phiên đích với teacher forcing. Đây không phải sai số giá.

MAE bên dưới tính bằng điểm VN30. Thay đổi âm nghĩa là fine-tune giảm lỗi so với zero-shot.

| Tập | Model | Target | h | Zero-shot MAE | Fine-tune MAE | Thay đổi | Naive MAE |
|---|---|---|---:|---:|---:|---:|---:|
| validation | chronos2 | open | 1 | 9.38 | 9.92 | +5.7% | 3.26 |
| validation | chronos2 | close | 1 | 9.48 | 10.24 | +8.1% | 8.80 |
| validation | chronos2 | open | 5 | 21.48 | 22.65 | +5.4% | 20.21 |
| validation | chronos2 | close | 5 | 21.93 | 23.02 | +5.0% | 21.84 |
| validation | chronos2 | open | 20 | 40.05 | 42.92 | +7.1% | 40.03 |
| validation | chronos2 | close | 20 | 40.56 | 43.43 | +7.1% | 40.49 |
| validation | kronos | open | 1 | 4.70 | 4.65 | -1.1% | 3.26 |
| validation | kronos | close | 1 | 10.20 | 10.34 | +1.4% | 8.80 |
| validation | kronos | open | 5 | 22.05 | 24.20 | +9.7% | 20.21 |
| validation | kronos | close | 5 | 22.93 | 26.73 | +16.6% | 21.84 |
| validation | kronos | open | 20 | 41.38 | 37.96 | -8.3% | 40.03 |
| validation | kronos | close | 20 | 41.55 | 38.57 | -7.2% | 40.49 |
| test | chronos2 | open | 1 | 21.04 | 20.26 | -3.7% | 5.96 |
| test | chronos2 | close | 1 | 19.99 | 19.62 | -1.9% | 17.72 |
| test | chronos2 | open | 5 | 48.65 | 48.45 | -0.4% | 40.85 |
| test | chronos2 | close | 5 | 47.70 | 47.72 | +0.0% | 45.16 |
| test | chronos2 | open | 20 | 103.23 | 100.43 | -2.7% | 91.95 |
| test | chronos2 | close | 20 | 102.07 | 99.41 | -2.6% | 93.83 |
| test | kronos | open | 1 | 10.64 | 9.89 | -7.1% | 5.96 |
| test | kronos | close | 1 | 19.75 | 19.60 | -0.8% | 17.72 |
| test | kronos | open | 5 | 48.09 | 52.17 | +8.5% | 40.85 |
| test | kronos | close | 5 | 53.30 | 55.38 | +3.9% | 45.16 |
| test | kronos | open | 20 | 153.24 | 130.78 | -14.7% | 91.95 |
| test | kronos | close | 20 | 155.24 | 138.30 | -10.9% | 93.83 |

## Diễn giải

- chronos2: fine-tune giảm MAE ở 5/6 chỉ tiêu test so với zero-shot; thấp hơn Naive ở 0/6 chỉ tiêu.
- kronos: fine-tune giảm MAE ở 4/6 chỉ tiêu test so với zero-shot; thấp hơn Naive ở 0/6 chỉ tiêu.

Đây là một cấu hình và một seed, không phải tìm kiếm siêu tham số đầy đủ. Test đã được xem trong các vòng thử trước, nên kết quả không phải đánh giá trên holdout hoàn toàn mới. Checkpoint của Chronos có thời điểm kết thúc pretraining chưa được xác minh; không thể loại trừ overlap với lịch sử VN30.

Kronos giữ causal mask trong teacher-forced validation: thay token tương lai không làm đổi logits ở các vị trí quá khứ. Khác biệt MAE chưa được kiểm định ý nghĩa thống kê; các cửa sổ dự báo chồng lấn nhau.

Chronos trả 13 quantile, không phải 13 mẫu ngẫu nhiên. Giữ trung bình đều 13 quantile như vòng zero-shot cũ để so sánh; metadata mới được sửa thành quantile_mean. Kronos dùng trung bình 3 path với cùng seed theo origin, temperature 1 và top_p 0.9.

Giá Open vẫn là giá do VNDIRECT cung cấp với một số phiên có cách dựng chưa rõ. Kronos nhận lịch phiên đích lịch sử thực tế. Các metric trên chỉ số không chứng minh lợi nhuận giao dịch.

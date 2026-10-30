# Trạng thái sau khi hoàn tất hàng đợi PC

**Tính toán thăm dò đã xong; bài nghiên cứu chưa hoàn thiện.** Dataset vẫn `unverified`, mọi kết quả giữ scope `exploratory_only`.

Supervisor kết thúc lúc **30/10/2026 18:22:28 +07**. Kiểm process thật sau đó không còn supervisor, Q3 hoặc Q2/Q4 worker sống; không cần chạy lại vì đã thấy `complete`.

| Nhóm | Hàng đợi đã thực hiện |
|---|---|
| SFT chính thăm dò | Bốn model × ba seed × năm epoch; giữ best-trained và selected có tính epoch 0 |
| Neural zero-shot/SFT | 48 forecast validation/test, đủ ba seed |
| Baseline | 11 jobs, gồm tuning validation và forecast; Naive, Ridge, ARIMA, ETS |
| Q3 | 36 so sánh hai model, ba budget, hai khởi tạo, ba seed; random LR trials riêng |
| Q2/Q4 | Ba seed ablation continuous/quantized và hai expanding folds |

Kiểm định độc lập sau chạy: **88 nhóm score, 182 file forecast, 2.160 dòng metric** đều khớp khi tính trực tiếp với nhãn SQLite. Kiểm đầy đủ path 20 phiên, thứ tự/ngày origin, ngày nhãn, ranh giới split, finite values, MAE/RMSE và chênh lệch so Naive. Ca cố tình đổi target date bị từ chối. **85 output receipts** còn khớp hash và **90 cặp training/selection receipts** khớp bytes checkpoint. Số 90 bao gồm benchmark và các LR trial, không phải 90 cấu hình độc lập của bảng chính.

- Receipt: [numerical_validation.json](numerical_validation.json).
- Metric tính lại: [recomputed_metrics.csv](recomputed_metrics.csv).
- Bảng chính theo seed: [seed_summary.csv](../evaluation-main/seed_summary.csv).
- Learning curve: [learning_curve.csv](../learning/learning_curve.csv).
- Ablation và fold: [followups](../followups/).

Quan sát có giới hạn: ở bảng chính, MAE Close trung bình ba seed của Naive thấp hơn mọi neural model tại h=1/5/20. Kronos-base best-trained SFT cải thiện mạnh h=20 so với zero-shot nhưng chưa vượt Naive ở trung bình này. Bảng `-ft` đang chấm **best-trained** để đo tác động cập nhật; Chronos chọn epoch 0 theo native validation ở cả ba seed, nên kết quả best-trained không được gọi là lựa chọn triển khai tốt nhất. Native loss giữa các model không so trực tiếp.

Còn phải hoàn tất:

1. Phân xử nghi vấn Open/OHLC và các ngày Close khác nguồn; không suy chất lượng giá từ checksum hay metric khớp.
2. Tổng hợp báo cáo Q1–Q4, bảng Open/Close, seed/period/regime, learning curve, ablation, folds và CI với diễn giải đúng phạm vi. Kiểm định số học ở trên chưa tự chứng minh bootstrap/selection hay causal attribution.
3. Đối chiếu lại toàn bộ yêu cầu trước khi chốt hoàn thiện. Không tự chuyển checkpoint thăm dò thành bằng chứng chính; không tuning theo test đã xem.

Lệnh kiểm lại số học: `.venv/Scripts/python.exe experiments/verify_completed_candidate.py` từ repo root. Không sửa các artifact cũ. Đồng hồ 24 giờ gốc vẫn kết thúc **31/10/2026 14:09:17 +07**.

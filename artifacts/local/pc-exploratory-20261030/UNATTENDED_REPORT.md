# VN30 — chạy tự động trên PC

**Dataset vẫn unverified; kết quả mang nhãn thăm dò.**

Cập nhật UTC: 2026-10-30T09:16:53.048746+00:00. Hạn gốc Unix: 1793430557.9180253.

| Phần | Hoàn tất | Trạng thái | PID đang sống | Lần khởi động lại |
|---|---:|---|---|---:|
| baselines | 11/11 | complete |  | 0 |
| neural | 40/48 | running | 6692, 22028 | 0 |
| score | 0/1 | pending |  | 0 |
| learning | 0/36 | waiting_for_sequential_gpu_slot | 33968, 34520 | 0 |
| followups | 0/5 | waiting_for_learning | 19948, 32932 | 0 |

GPU tuần tự; không đổi learning rate, precision, seed, origin hoặc trạng thái kiểm toán để vượt lỗi.
Các lượt còn sống không bị khởi động lại chỉ vì chậm. Lỗi protocol/hash phải chờ kiểm tra; lỗi tiến trình có tối đa hai lần tiếp tục.

## MAE Close từ các seed đã chấm

Số seed đang có: [1]. Không coi seed là các tập thị trường độc lập.

| Model | h=1 | h=5 | h=20 |
|---|---:|---:|---:|
| arima | 17.722 | 45.165 | 93.826 |
| chronos2 | 19.995 | 47.699 | 102.072 |
| chronos2-ft | 19.658 | 47.937 | 99.492 |
| ets | 17.722 | 45.165 | 93.826 |
| kronos-base | 20.835 | 55.556 | 167.244 |
| kronos-base-ft | 20.753 | 54.401 | 97.314 |
| kronos-mini | 20.237 | 53.904 | 120.596 |
| kronos-mini-ft | 19.380 | 49.944 | 106.564 |
| kronos-small | 19.289 | 52.897 | 153.568 |
| kronos-small-ft | 19.645 | 55.608 | 138.722 |
| naive | 17.722 | 45.165 | 93.826 |
| ridge | 21.597 | 49.598 | 105.211 |

## Giới hạn còn lại

- Chưa phân xử đủ chênh lệch OHLC và chưa xác nhận Open chính thức.
- Không tự chuyển checkpoint thăm dò thành bằng chứng chính hoặc đánh dấu bài hoàn thiện.
- Bảng chi tiết: evaluation-main/, learning/, followups/. Nhật ký: supervision/events.jsonl.

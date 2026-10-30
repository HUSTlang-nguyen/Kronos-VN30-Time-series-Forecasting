# VN30 — chạy tự động trên PC

**Dataset vẫn unverified; kết quả mang nhãn thăm dò.**

Cập nhật UTC: 2026-10-30T11:22:28.202256+00:00. Hạn gốc Unix: 1793430557.9180253.

| Phần | Hoàn tất | Trạng thái | PID đang sống | Lần khởi động lại |
|---|---:|---|---|---:|
| baselines | 11/11 | complete |  | 0 |
| neural | 48/48 | complete |  | 0 |
| score | 1/1 | complete |  | 0 |
| learning | 36/36 | complete |  | 0 |
| followups | 5/5 | complete |  | 0 |

GPU tuần tự; không đổi learning rate, precision, seed, origin hoặc trạng thái kiểm toán để vượt lỗi.
Các lượt còn sống không bị khởi động lại chỉ vì chậm. Lỗi protocol/hash phải chờ kiểm tra; lỗi tiến trình có tối đa hai lần tiếp tục.

## MAE Close từ các seed đã chấm

Số seed đang có: [3]. Không coi seed là các tập thị trường độc lập.

| Model | h=1 | h=5 | h=20 |
|---|---:|---:|---:|
| arima | 17.722 | 45.165 | 93.826 |
| chronos2 | 19.995 | 47.699 | 102.072 |
| chronos2-ft | 20.104 | 48.198 | 99.976 |
| ets | 17.722 | 45.165 | 93.826 |
| kronos-base | 20.889 | 55.148 | 166.781 |
| kronos-base-ft | 21.234 | 54.709 | 98.849 |
| kronos-mini | 20.587 | 53.345 | 121.571 |
| kronos-mini-ft | 20.127 | 50.188 | 108.490 |
| kronos-small | 19.906 | 52.586 | 154.143 |
| kronos-small-ft | 20.326 | 55.690 | 138.716 |
| naive | 17.722 | 45.165 | 93.826 |
| ridge | 21.597 | 49.598 | 105.211 |

## Giới hạn còn lại

- Chưa phân xử đủ chênh lệch OHLC và chưa xác nhận Open chính thức.
- Không tự chuyển checkpoint thăm dò thành bằng chứng chính hoặc đánh dấu bài hoàn thiện.
- Bảng chi tiết: evaluation-main/, learning/, followups/. Nhật ký: supervision/events.jsonl.

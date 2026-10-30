# Ghi nhớ công việc VN30

## Yêu cầu và quyết định của người dùng

Người dùng yêu cầu làm lại bài trên **PC hiện tại**, với **Kronos-mini, Kronos-small, Kronos-base**, và hoàn thiện những phần thiếu của Q1–Q4. Checkpoint Kronos-small SFT cũ được tạo trên môi trường khác. Không dùng checkpoint/forecast cũ làm kết quả mới.

Các quyết định đã được người dùng chốt:

- Khôi phục và kiểm toán snapshot cũ trước; chỉ tạo bản hiệu chỉnh riêng khi có bằng chứng.
- Phạm vi mục tiêu: đủ Q1–Q4, gồm baseline thống kê, nhiều seed, learning curve, đối chứng khởi tạo ngẫu nhiên và representation ablation.
- Giữ **Chronos-2-small zero-shot và SFT** làm đối chứng general-purpose TSFM.
- **Tổng ngân sách chạy tối đa 24 giờ**, không tự chuyển thành nhiều đợt hoặc cấp thêm thời gian. Nếu chưa đủ thí nghiệm, phải công khai phần thiếu.
- Tài khoản của người dùng đã có quyền vào Drive DVC nhóm. Người dùng đã cho link thư mục; bộ dữ liệu đã được tải thành công bằng trình duyệt đăng nhập và khôi phục theo hash DVC.
- Người dùng muốn agent chủ động tìm hướng tốt hơn khi phát hiện flaw; phải ghi phát hiện, giải pháp, lý do, kiểm thử và phần chưa xong vào implementation plan/log.
- Người dùng yêu cầu nhánh `neikhn/lam-lai-vn30-pc`, định kỳ lưu checkpoint commit/push sau mốc công việc, nội dung ngắn gọn; stash khi cần giữ thay đổi tạm.
- Mỗi lần phục hồi ngữ cảnh, đọc lại các file ghi nhớ trong repo, không dựa vào trí nhớ hội thoại.

## Hiện trạng quan trọng

**Phần mềm đã triển khai; nghiên cứu mới chưa được huấn luyện do dữ liệu chưa qua kiểm toán.**

PC: Windows/PowerShell, RTX 4070 SUPER 12 GB, RAM khoảng 32 GB. Python 3.11.9. Môi trường `.venv` đã cài đúng `uv.lock`, torch `2.14.0+cu130`, CUDA thực tế dùng được. `.venv-data` chứa uv và DVC riêng; `.vendor/Kronos` đã checkout revision đã khóa.

Dataset gốc:

- `data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite`.
- SHA256 `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.
- 2.271 phiên, 24/08/2017–01/10/2026. Đã khôi phục raw/SQLite/ZIP, xác minh đối tượng DVC và replay raw/timestamp/quality flags.
- Audit mới: **unverified**. Có 1.230 chênh lệch OHLC so với VPS/DNSE trên ngày giao nhau; đây là số phép so sánh khác nhau, không phải số nến đã chứng minh sai.
- Close: 54 chênh lệch với DNSE, 6 với VPS, tổng 60 ngày khác nhau. Chưa có căn cứ kết luận nhà cung cấp nào đúng trong mọi trường hợp.
- Có 78 phiên Open bằng Close trước; trong đó 71 phiên liên tiếp từ 05/05 đến 11/08/2025. Bảy trường hợp còn lại rải rác; không nhầm 71 của giai đoạn đặc biệt với tổng toàn bộ dữ liệu.
- Một hàng ngoài request, chưa đối chiếu lịch phiên đầy đủ. Không điền ngày nghỉ theo suy đoán, không sửa giá bằng đa số phiếu nhà cung cấp.

## Trạng thái lượt chạy PC

- Config: `configs/pc_rerun.json`.
- Output: `artifacts/local/pc-rerun-20261030/`.
- State: **5/288 công việc hoàn thành, 283 blocked**, không có huấn luyện VN30 mới.
- Các việc hoàn thành: recover, independent source fetch, audit, pretrained weights verification, Kronos bootstrap.
- `prepare` blocked với lý do `dataset_unverified`; các bước phụ thuộc bị chặn theo đúng kế hoạch.
- Đồng hồ được lưu trong `state.json`, không reset khi resume.
- Mốc được lưu theo Asia/Bangkok: bắt đầu **30/10/2026 14:09:17 +07:00**, hạn **31/10/2026 14:09:17 +07:00**. Khi tiếp tục, đọc timestamp từ state; không suy ra ngân sách còn lại từ ghi chú này.
- Source code đã được khóa bằng hash trong state. Sửa file Python sẽ khiến resume từ chối; không sửa state để che khác biệt. Có lệnh `refresh-preflight --reason` dành riêng cho sửa lỗi trước khi có bất kỳ artifact nghiên cứu nào: lưu lịch sử cũ, kiểm evidence/config/provenance và giữ nguyên started/deadline. Không dùng sau khi đã huấn luyện/dự báo. File Markdown ghi nhớ không thuộc bộ hash Python hiện tại.

## Quy tắc nghiên cứu cần giữ

- Không trộn score/checkpoint từ các lượt cũ. Không dùng dữ liệu giả để đưa ra kết luận VN30.
- Không gọi hash đúng là dữ liệu thị trường đúng. Không tự chấp nhận dataset để vượt cổng kiểm toán.
- Chọn cấu hình/checkpoint bằng validation, không bằng test. Test cũ đã được xem, phải gọi là hồi cứu.
- Context 128, path 20, score h=1/5/20, seed 42/43/44; cùng origin trong từng bảng.
- Tokenizer mini là `Kronos-Tokenizer-2k`; small/base là `Kronos-Tokenizer-base`.
- Giữ riêng checkpoint tốt nhất sau cập nhật và lựa chọn có tính epoch 0 pretrained. Không bắt buộc chọn SFT nếu validation kém đi.
- Volume/amount hiện bằng 0 vì thiếu dữ liệu; đó là giới hạn input, không phải volume thực của VN30.
- Nhiều seed không thay cho nhiều chu kỳ thị trường; cửa sổ dự báo chồng lấn không phải mẫu độc lập.
- Không suy lợi nhuận giao dịch trực tiếp từ sai số chỉ số.
- Không xóa hoặc ghi đè checkpoint cũ. Working tree ban đầu đã báo hai file Chronos LFS là modified khi tắt filter; các file này không được sửa trong công việc mới.

## Cách tiếp tục

Đọc `AGENT_LOG.md` rồi `IMPLEMENTATION_PLAN.md`. Kiểm tra `state.json`, audit và Git trước khi sửa. Hồ sơ điều tra bổ sung nằm ở `artifacts/local/pc-preflight-20261030/evidence_review.md`; đây chưa phải biên bản chấp nhận dataset. Tiếp tục điều tra nguồn giá/lịch phiên bằng bằng chứng truy vết được. Chỉ chạy nghiên cứu mới khi điều kiện dữ liệu thật sự đạt; không hỏi lại các lựa chọn người dùng đã chốt ở trên.

Lệnh, cấu trúc artifact và hướng dẫn chi tiết: `docs/PC_Rerun.md`.

# Điểm vào cho agent làm việc trong repo

Đọc các file sau trước khi phân tích, sửa code hoặc tiếp tục công việc sau khi mất ngữ cảnh:

1. `AGENT.md` — mục tiêu, quyết định của người dùng, quy tắc và hiện trạng cần nhớ.
2. `IMPLEMENTATION_PLAN.md` — kế hoạch đang thực hiện, tiêu chí hoàn thành và các flaw cần giải quyết.
3. `AGENT_LOG.md` — trạng thái mới nhất, thay đổi đã làm, bằng chứng kiểm thử và việc tiếp theo.

Đối chiếu trạng thái thực tế với `artifacts/local/pc-rerun-20261030/state.json`, báo cáo audit và working tree; không chỉ tin dấu tick hoặc đoạn tóm tắt hội thoại.

Sau mỗi mốc công việc có ý nghĩa, cập nhật log và trạng thái trong plan. Ghi phát hiện mới, giải pháp, lý do lựa chọn, bằng chứng kiểm tra, hạn chế và việc còn lại. Trước khi kết thúc lượt hoặc chuyển giao, ghi rõ điểm tiếp tục. Không lưu secrets, token, mật khẩu hoặc nội dung OAuth vào các file này.

Theo yêu cầu người dùng, làm trên nhánh `neikhn/lam-lai-vn30-pc`. Sau các mốc công việc có ý nghĩa, lưu commit checkpoint và push nhánh; thông điệp ngắn gọn. Dùng stash khi cần giữ tạm thay đổi để chuyển ngữ cảnh/nhánh, không bỏ thay đổi. Kiểm nội dung staged trước mỗi commit; không đưa credential, cache/môi trường hoặc checkpoint cũ ngoài phạm vi vào commit.

Tuân thủ chỉ dẫn trực tiếp mới nhất của người dùng và chỉ dẫn cấp cao hơn. Các file ghi nhớ không tự cấp quyền cho hành động ngoài phạm vi đã được người dùng đồng ý.

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

**Cập nhật sau lệnh `proceed`:** đang hoàn thiện báo cáo mới `docs/VN30_PC_Research_Report.md` bằng postprocessor riêng, không sửa frozen src/scripts. Đã kiểm độc lập **378 CI bootstrap, 1.782 metric regime/period**, ba baseline validation locks, 18 lựa chọn random LR, 12 selected checkpoint có xét epoch 0. Báo cáo và bảng nằm ở `artifacts/local/pc-exploratory-20261030/final-report/`; đọc `verification.json`, `completion_matrix.csv` và `report_sources.json` thay vì các trạng thái lịch sử bên dưới. Dataset vẫn unverified; không đánh dấu nghiên cứu chính hoàn thiện.

Phát hiện cần giữ: Chronos selected epoch 0 cả ba seed; Kronos-small random thắng pretrained ở Close h=5/20 tại budget 1.000/full trong ngân sách đã thử; lượng tử hóa không cải thiện đồng nhất; hai fold đều không có origin volatility cao theo train p90, test chính chỉ 17 origin cao trong hai cụm. Test h=1 có 59 nhãn trong đoạn Open bất thường khiến Naive Open error bằng 0; không coi đó là chứng minh dự báo Open chính thức tốt.

Verifier hậu kiểm đã hỗ trợ ánh xạ receipt tuyệt đối của Windows/Linux về chính repo và chặn traversal. Lưu lịch sử numerical receipt khi đổi phiên bản verifier; metric CSV tính lại không đổi. `.gitattributes` giữ byte report và LF của postprocessor để hash ổn định qua checkout. Raw công bố bổ sung vẫn local; source catalog chứa URL/hash, không hứa tải lại HTML động cho cùng bytes.

**Cập nhật bàn giao 30/10/2026 21:17 +07:** hàng đợi thăm dò đã kết thúc lúc **18:22:28 +07**, supervisor tự thoát sau khi đủ 11 baseline jobs, 48 neural forecasts, score ba seed, 36 learning comparisons và 5 followup jobs (ba ablation seed, hai fold). Kiểm tra process thật bằng psutil không còn supervisor/Q3/followup sống. Không khởi động lại các job đã xong. Các mô tả “đang chạy/xếp hàng” bên dưới là lịch sử trước mốc này. Đây mới là hoàn tất hàng đợi phần mềm; cần kiểm định đầu ra từ forecast/nhãn và tổng hợp báo cáo, chưa hoàn tất nghiên cứu. Dataset vẫn unverified.

Người dùng từng yêu cầu pause agent ba giờ; chưa tạo được lịch tự gọi lại agent. Không hứa tự thức dậy: cấu hình hai lần gọi đã bị bộ duyệt tự động từ chối và không được thực hiện. PC đã tự hoàn tất công việc trong lúc chờ, không cần giữ GPU chạy vô ích. **Người dùng đã quay lại, thông báo quota đầy và hỏi trạng thái; tiếp tục kiểm định đầu ra và báo cáo, không pause theo yêu cầu cũ.** Goal tự động trong chat đã được người dùng xóa; không tự tạo goal mới. Deadline gốc vẫn giữ.

**Đã bắt đầu huấn luyện thăm dò trên PC. Dataset vẫn unverified; thí nghiệm chính chưa được phép dùng làm kết luận.**

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
- State chính: **5/288 công việc hoàn thành, 283 blocked**, chưa có huấn luyện thuộc bằng chứng chính.
- Các việc hoàn thành: recover, independent source fetch, audit, pretrained weights verification, Kronos bootstrap.
- `prepare` blocked với lý do `dataset_unverified`; các bước phụ thuộc bị chặn theo đúng kế hoạch.
- Đồng hồ được lưu trong `state.json`, không reset khi resume.
- Mốc được lưu theo Asia/Bangkok: bắt đầu **30/10/2026 14:09:17 +07:00**, hạn **31/10/2026 14:09:17 +07:00**. Khi tiếp tục, đọc timestamp từ state; không suy ra ngân sách còn lại từ ghi chú này.
- Source code đã được khóa bằng hash trong state. Sửa file Python sẽ khiến resume từ chối; không sửa state để che khác biệt. Có lệnh `refresh-preflight --reason` dành riêng cho sửa lỗi trước khi có bất kỳ artifact nghiên cứu nào: lưu lịch sử cũ, kiểm evidence/config/provenance và giữ nguyên started/deadline. Không dùng sau khi đã huấn luyện/dự báo. File Markdown ghi nhớ không thuộc bộ hash Python hiện tại.

Nhánh thăm dò: `artifacts/local/pc-exploratory-20261030/`, chạy bằng `scripts/run_candidate_training.py`. Manifest và mọi checkpoint/forecast có scope `exploratory_only`, audit vẫn unverified; loader mặc định và scorer chính từ chối. Đồng hồ dùng chung deadline gốc. **Đã hoàn tất 16 job:** benchmark một epoch + 32 origin validation của cả bốn model và **12 lượt SFT năm epoch, ba seed 42/43/44**. Checksum/history/deadline đã xác minh trong `verification.json`; không còn GPU job của nhánh này chạy nền. Ba Kronos chọn epoch 5, Chronos chọn epoch 0 ở cả ba seed. Loss native không so xếp hạng giữa model. Weights/optimizer thăm dò giữ local; code, loss và hash receipts được lưu Git.

Đối chiếu lịch mới: ngày VN30 khớp toàn bộ ngày quan sát được của **VNINDEX từ VPS**, DNSE VNINDEX thiếu 33 ngày. Đây là lịch quan sát nguồn độc lập, chưa phải chứng nhận calendar chính thức. Audit bổ sung trong `artifacts/local/pc-preflight-20261030/calendar_crosscheck/audit/`; trạng thái dataset vẫn unverified.

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

### Lịch sử bàn giao chạy cục bộ khi agent tạm dừng 3 giờ

Người dùng đã yêu cầu sau khi kiểm tra bàn giao thì **tạm dừng agent theo dõi 3 giờ, PC tiếp tục chạy** để dành quota. Pipeline cục bộ không dùng LLM. Không dừng các tiến trình tính toán khi tạm dừng goal trong chat.

- `experiments/unattended_supervisor.py`: nhận các worker đang sống bằng đúng command/PID, GPU tuần tự, tối đa hai lần tiếp tục tiến trình đã chết, không sửa cấu hình/kết quả khi lỗi hash/protocol. Giữ máy khỏi tự sleep trong thời gian supervisor sống; màn hình vẫn có thể tắt.
- Thứ tự: main neural + baseline → chấm đủ ba seed; GPU chuyển Q3 → ba ablation seed → hai expanding folds. Mọi bước dùng deadline gốc hoặc stage cap sớm hơn.
- Báo cáo tự cập nhật: `artifacts/local/pc-exploratory-20261030/UNATTENDED_REPORT.md`; PID/heartbeat/events trong `supervision/`. Đọc file này và kiểm process thật trước khi khởi động bất kỳ worker nào. Không chạy thêm supervisor nếu PID lock còn sống.
- Main: `scripts/evaluate_candidate.py`; snapshot cũ không thay đổi, chỉ thêm entry point đánh giá và ghi proof tất cả file đã khóa giữ nguyên. Primary coordinator vẫn bị chặn dữ liệu; không âm thầm sửa source identity của primary state.
- Q3: `experiments/candidate_learning.py`, 36 so sánh, 66 lượt train mới gồm random LR trials, tái dùng 6 full-budget pretrained checkpoint PC. Dùng trực tiếp trial LR thắng validation, không train trùng. Hash riêng của orchestrator được ghi bên cạnh hash src/scripts đã khóa.
- Q2/Q4: `experiments/candidate_stability.py` và `candidate_ablation.py`. Ablation là specialization có scope/provenance của mã frozen, giữ nguyên predictor/loss/feature transforms/vòng lặp số học. Chỉ dùng loader thăm dò rõ ràng; không giả audit accepted.
- Các process đã được kiểm sống trước bàn giao: main neural exec session `49384`; watcher chấm điểm `53801`; Q3 chờ GPU `34839`; Q2/Q4 chờ Q3 `7939`. Các session có thể terminal sau khi xong; ưu tiên supervisor status và native PID/command thực tế. CPU baseline session `60966` đã terminal thành công.
- Có bảng tạm seed 42 (1/3, không đánh dấu hoàn thành); Naive đang mạnh, không đổi HP vì đã thấy test. Cấu hình baseline validation: Ridge alpha 10, ETS level, ARIMA(0,1,0).
- Vai trò model: trọng tâm ba Kronos; Chronos-2-small là đối chứng đã có trong báo cáo VN30 cũ, không phải model thay Kronos.

Đọc `AGENT_LOG.md` rồi `IMPLEMENTATION_PLAN.md`. Kiểm tra `state.json`, audit và Git trước khi sửa. Hồ sơ điều tra bổ sung nằm ở `artifacts/local/pc-preflight-20261030/evidence_review.md`; đây chưa phải biên bản chấp nhận dataset. Tiếp tục điều tra nguồn giá/lịch phiên bằng bằng chứng truy vết được. Chỉ chạy nghiên cứu mới khi điều kiện dữ liệu thật sự đạt; không hỏi lại các lựa chọn người dùng đã chốt ở trên.

Lệnh, cấu trúc artifact và hướng dẫn chi tiết: `docs/PC_Rerun.md`.

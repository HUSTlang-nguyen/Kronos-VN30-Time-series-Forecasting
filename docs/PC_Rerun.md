# VN30 — chạy lại trên PC

Đây là quy trình mới cho Kronos mini/small/base và Chronos-2-small. Các kết quả năm 2026 trong thư mục chạy cũ là lịch sử từ môi trường khác; không được dùng để lấp bảng điểm của lượt PC.

## Hiện trạng PC ngày 30/10/2026

- Python 3.11.9; môi trường `.venv` đã cài theo `uv.lock`, PyTorch `2.14.0+cu130` nhận RTX 4070 SUPER 12 GB.
- `.venv-data` chứa uv/DVC riêng. Đã khôi phục đủ 89 file từ các đối tượng DVC trong Drive được chia sẻ; kiểm MD5 từng đối tượng và SHA256 SQLite/ZIP.
- Đã tải và kiểm checksum bốn predictor và hai tokenizer pretrained. Kiểm thử GPU bằng dữ liệu giả đã chạy đủ bốn model, gồm dự báo, gradient, tokenizer và causal mask. Đây không phải score VN30.
- Kiểm toán ban đầu: raw/timestamp/flags replay khớp; 2.271 phiên, một hàng ngoài request; 78 phiên Open bằng Close trước, trong đó có chuỗi 71 phiên 05/05–11/08/2025. Có chênh lệch OHLC với VPS/DNSE và chưa đối chiếu xong lịch phiên. Dữ liệu chưa được chấp nhận để chạy thí nghiệm chính.

Xem `artifacts/local/pc-preflight-20261030/audit/summary.md` để đọc chi tiết. Chênh lệch nhà cung cấp không tự chứng minh VNDIRECT sai. Không sửa giá hoặc đổi nguồn dựa trên score model.

## Các lệnh

Chạy từ gốc repo bằng PowerShell:

```powershell
.venv/Scripts/python.exe scripts/run_experiment.py plan --config configs/pc_rerun.json
.venv/Scripts/python.exe scripts/run_experiment.py run --config configs/pc_rerun.json
.venv/Scripts/python.exe scripts/run_experiment.py status --config configs/pc_rerun.json
.venv/Scripts/python.exe scripts/run_experiment.py resume --config configs/pc_rerun.json
.venv/Scripts/python.exe scripts/run_experiment.py report --config configs/pc_rerun.json
```

`run` tạo một đồng hồ 24 giờ duy nhất; `resume` không cấp thêm 24 giờ. Các mốc tính từ lúc bắt đầu: setup 3 giờ, main 11 giờ, learning 16 giờ, ablation/folds 20 giờ; phần cuối dành cho báo cáo. Không mở thêm job sau mốc của giai đoạn. Job bị hết giờ giữ epoch hoàn tất gần nhất hoặc progress forecast để tiếp tục trong ngân sách còn lại.

Không thay config/code/provenance rồi gọi resume. Không xóa `state.json` để reset thời gian. Nếu tiến trình bị tắt cưỡng bức, kiểm PID trong `coordinator.lock`; chỉ bỏ lock sau khi xác nhận tiến trình cũ đã dừng.

Nếu cần sửa code trong preflight và **chưa có artifact nghiên cứu**, có một ngoại lệ được ghi lịch sử rõ ràng:

```powershell
.venv/Scripts/python.exe scripts/run_experiment.py refresh-preflight --config configs/pc_rerun.json --reason "Mô tả sửa lỗi và bằng chứng kiểm thử"
.venv/Scripts/python.exe scripts/run_experiment.py resume --config configs/pc_rerun.json
```

Lệnh này từ chối config/provenance thay đổi, evidence cũ không khớp, job đang chạy/bị ngắt hoặc artifact checkpoint/forecast/benchmark đã tồn tại. Nó lưu state và báo cáo cũ trong `preflight_history`, ghi identity trước/sau, rồi kiểm lại preflight. **Started và deadline gốc được giữ nguyên.** Đây không phải cách tiếp tục nghiên cứu dưới code mới sau khi đã tạo kết quả.

Trên Linux, dùng Python của môi trường tương ứng và chỉnh `dvc_executable` trước khi khởi tạo lượt chạy. Artifact mới dùng đường dẫn tương đối; các bộ đọc cũng hiểu dấu `\\` trong receipt Windows cũ.

## Cổng kiểm toán dữ liệu

```powershell
.venv/Scripts/python.exe scripts/audit_vn30_data.py --output artifacts/local/audit-new --independent <vps.csv> <dnse.csv> --calendar <calendar.csv>
```

Nguồn độc lập là CSV có `date,open,high,low,close`, kèm JSON cùng tên chứa `provider`, `symbol: VN30`, URL và `csv_sha256`. Calendar là CSV `date`, kèm JSON có URL nguồn và `csv_sha256`. `fetch_audit_sources.py` tải và lưu raw/CSV/metadata VPS/DNSE; không tạo một lịch sàn giả từ chính ngày có trong dataset.

Chỉ trạng thái `accepted_provider_scope` cho phép tạo manifest chạy chính. Byte integrity, replay, mẫu kiểm chứng, chênh lệch giá và lịch phiên được báo riêng. Khi chưa kiểm chứng, coordinator hoàn tất báo cáo kiểm toán rồi đánh dấu toàn bộ công việc phụ thuộc là blocked. Không có cờ bỏ qua kiểm toán cho kết quả chính.

Nếu có bằng chứng hiệu chỉnh, tạo dataset/receipt riêng và giữ bản gốc. Loader hỗ trợ manifest v2 với dataset, receipt và hash báo cáo audit; không hardcode 2.271 hàng. Không ghép nhiều nguồn theo ô, tự điền ngày hoặc sửa Open thành Close trước. Cấu hình một lượt mới phải phản ánh dataset mới; lượt cũ vẫn bất biến và việc cấp ngân sách mới cần được quyết định riêng.

Nếu DVC OAuth không dùng được nhưng tài khoản đã có quyền Drive, có thể tải thư mục `files/md5` bằng trình duyệt và phục hồi cục bộ:

```powershell
.venv/Scripts/python.exe scripts/restore_pc_data.py --archive <zip-downloaded-from-drive> --receipt artifacts/local/recovery.json
```

Helper chỉ nhận các đối tượng có tên hash hợp lệ, xác minh nội dung, khôi phục theo pointer và từ chối ghi đè dữ liệu khác. ZIP Drive có thể thêm đuôi kiểu tệp; identity vẫn do hash quyết định. Không thực thi parser nhúng trong dữ liệu tải về.

## Ma trận thí nghiệm

- Q1: Naive, Ridge (alpha 1/10/100/1000), ARIMA (p/q 0–2, d 0–1) và ETS (level/additive/damped additive). Cấu hình chọn trên toàn bộ validation; ứng viên lỗi không được xem như đã phủ đủ mẫu. Không thay lỗi dự báo bằng Naive.
- Main: bốn neural model, zero-shot và SFT, seed 42/43/44; validation/test cùng origin. Kronos-mini dùng Tokenizer-2k; small/base dùng Tokenizer-base. Không suy tác động kích thước thuần túy từ khác biệt mini.
- SFT: FP32, AdamW, 5 epoch, effective batch 16, gradient clipping 1.0, LR 1e-6. `best/` là checkpoint tốt nhất sau cập nhật; `selected/` xét cả epoch 0. `training.json` và `selection.json` ghi lựa chọn riêng.
- Q3: Kronos-small và Chronos-2-small, 500/1.000/full phiên train, cùng ngày kết thúc; predictor pretrained so với random, ba seed. Random LR chọn trong 1e-6/1e-5/1e-4 trên validation. Tokenizer Kronos vẫn pretrained nên đối chứng chỉ tách predictor pretraining.
- Q2: một encoder tokenizer small cố định, đặc trưng liên tục chuẩn hóa L2 so với BSQ lượng tử hóa; cùng backbone small khởi tạo, cùng numeric head/MSE, cùng train/validation/test và ba seed. Không gộp kết quả này thành bằng chứng cho mọi thành phần của K-line representation.
- Q4: ba đoạn test, volatility tại origin (sigma20, ngưỡng train p90), paired moving-block bootstrap block 20 với 2.000 mẫu, hai fold lịch sử bổ sung với seed 42. Lịch sử trước thời điểm công bố checkpoint chỉ là hồi cứu, không phải triển khai lịch sử sạch.

Đọc lựa chọn có xét epoch 0 khi inference:

```powershell
.venv/Scripts/python.exe scripts/forecast_vn30.py run --manifest <primary.json> --model kronos-base-ft --checkpoint <training-directory> --checkpoint-choice selected --split test --device cuda:0 --output <new-forecast.csv>
```

Mặc định `--checkpoint-choice best-trained` giữ đúng ý nghĩa so sánh SFT. Khi `selected` chọn epoch 0, metadata revision ghi `selected-pretrained`.

## Kiểm thử và đầu ra

### Báo cáo kết quả PC và kiểm định sau chạy

Đọc [báo cáo PC mới](VN30_PC_Research_Report.md). Hàng đợi thăm dò đã xong; không cần mở lại supervisor hoặc chạy GPU thêm để dựng báo cáo. Dataset vẫn unverified, primary run vẫn blocked; trạng thái complete của candidate không tự mở cổng nghiên cứu chính.

```powershell
.venv/Scripts/python.exe experiments/verify_completed_candidate.py
.venv/Scripts/python.exe experiments/finalize_pc_report.py
```

Lệnh kiểm định đọc forecast và SQLite trực tiếp, kiểm 90 cặp best/selected checkpoint local. Postprocessor kiểm lại lựa chọn validation, bootstrap/regime/period, sinh bảng CSV/PNG và báo cáo Markdown. Cả hai không sửa checkpoint/forecast cũ; receipt numerical cũ được lưu vào history khi đổi phiên bản verifier. Các đường dẫn absolute trong receipt lịch sử được đọc bằng cách ánh xạ lại phần nằm trong chính repository, không cho traversal ra ngoài; output mới dùng đường dẫn tương đối.

Các tham số postprocessor: `--candidate <candidate-directory>`, `--output <new-table-directory>`, `--report <new-report.md>`. Báo cáo mặc định ở `docs/VN30_PC_Research_Report.md`, bảng/hình và hồ sơ nguồn ở `artifacts/local/pc-exploratory-20261030/final-report/`. `selected_scores.csv` tách lựa chọn có xét epoch 0 khỏi best-trained; `completion_matrix.csv` ghi yêu cầu đã đạt và chưa đạt. Không lấy CSV mô tả volatility theo return thực hiện tương lai làm nhóm volatility của Q4.

### Huấn luyện thăm dò khi dataset vẫn unverified

```powershell
.venv/Scripts/python.exe scripts/run_candidate_training.py --phase both
```

Đây là nhánh thăm dò đã tách riêng, không phải cờ bỏ qua cổng chính. Runner chỉ nhận snapshot đã có audit hoàn tất với replay/flags đạt và đủ ngày mẫu có nguồn đối chiếu, giữ giá gốc, sao chép receipt audit có hash, và dùng **deadline gốc** từ lượt PC. Output mặc định `artifacts/local/pc-exploratory-20261030/`.

`benchmark` chạy một epoch và 32 origin validation/model; `train` chạy SFT năm epoch seed 42; `both` làm tuần tự hai phần. Có thể dùng `--models` hoặc `--seed` khi tiếp tục các lượt đã định. Chạy lại cùng lệnh sẽ xác minh receipt/checksum rồi bỏ qua job hoàn tất hoặc resume checkpoint epoch. Có lock GPU riêng; không mở song song với GPU job khác.

Manifest, checkpoint và forecast mang scope `exploratory_only`; trainer yêu cầu `--exploratory` cho manifest này. Loader mặc định và bộ so sánh chính từ chối nó. Không tự nâng trạng thái dataset hoặc chuyển số liệu vào bảng Q1–Q4. Chỉ có kiểm toán đầy đủ mới cho phép kết luận chính.

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe scripts/smoke_pc_models.py --output <new-smoke-receipt.json>
```

CI chạy các kiểm thử dữ liệu/thời gian/điều phối. Các kiểm thử cần torch/sklearn được bỏ qua nếu môi trường data-only không cài các dependency đó; trên PC cần chạy đủ. Kiểm thử GPU không chạy trong CI.

Mỗi lượt có `state.json`, `matrix.json`, `logs/`, `audit/`, benchmark, cấu hình baseline đã khóa, checkpoint, forecast, score, chẩn đoán, và `remaining.json`. Báo cáo chỉ lấy nhóm đã phủ đủ origin và qua kiểm tra metric độc lập. Có bảng seed, learning curve, selected-score tính epoch 0, đồ thị loss và MAE khi thực sự có dữ liệu đầu ra. Không đủ lượt thì không đánh dấu hoàn thành.

Resume model lưu cả optimizer, RNG CPU/CUDA/Python/NumPy, thứ tự shuffle và epoch. Snapshot optimizer/RNG `.pt` là dữ liệu local; weights xuất bản dùng Git LFS. Các artifact cũ vẫn giữ nguyên.

## Chạy không cần theo dõi bằng agent

Các worker thăm dò được tách theo giai đoạn để GPU chạy tuần tự:

```powershell
.venv/Scripts/python.exe scripts/evaluate_candidate.py init
.venv/Scripts/python.exe scripts/evaluate_candidate.py neural
.venv/Scripts/python.exe scripts/evaluate_candidate.py baselines
.venv/Scripts/python.exe experiments/candidate_learning.py --wait-for-gpu
.venv/Scripts/python.exe experiments/candidate_stability.py --wait-for-learning
```

Supervisor `experiments/unattended_supervisor.py` nhận các worker đang sống trước khi mở worker còn thiếu; không chạy lại các lệnh trên nếu chúng đang sống. Nó không dùng quota chat, không đổi cấu hình khoa học, không tự chấp nhận dữ liệu. Giữ nguyên deadline/stage caps của lượt PC gốc, lưu báo cáo `UNATTENDED_REPORT.md` và nhật ký `supervision/events.jsonl`. Trên Windows, chạy nền bằng `Start-Process -WindowStyle Hidden`; kiểm `supervision/supervisor.lock` trước để tránh mở trùng.

Lỗi tiến trình có thể tiếp tục tối đa hai lần từ checkpoint/progress. Process còn sống không bị xem là đã chết chỉ vì chậm. Lỗi protocol/hash hoặc hết giới hạn retry được ghi rõ để agent kiểm tra sau; không dùng Naive lấp dự báo lỗi. Checkpoint/push tự động chỉ stage artifact trong thư mục candidate đã được người dùng cho phép công bố; weights/optimizer vẫn giữ local, lỗi Git không dừng tính toán.

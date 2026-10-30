# Agent log — VN30 PC rerun

## Trạng thái bàn giao hiện tại — 30/10/2026, Asia/Bangkok

**Đang triển khai yêu cầu làm lại bài; chưa hoàn thiện nghiên cứu.** Đã có code cho ma trận ba Kronos + Chronos và các đối chứng. Lượt PC dừng hợp lệ ở kiểm toán dữ liệu: 5/288 complete, 283 blocked. Không có huấn luyện VN30 mới hoặc score mới trên dữ liệu thật.

Nguồn trạng thái: `artifacts/local/pc-rerun-20261030/state.json`.
Nguồn kết luận dữ liệu: `artifacts/local/pc-rerun-20261030/audit/audit.json` và `summary.md`.
Hướng dẫn chạy: `docs/PC_Rerun.md`.

### Tiếp tục từ đây

1. Đọc AGENTS.md → AGENT.md → IMPLEMENTATION_PLAN.md → file log này.
2. Kiểm tra working tree, source hash và đồng hồ trong state. Không reset budget.
3. F12 đã sửa và kiểm thử; tiếp tục bằng chứng giá/calendar. Code đã thay đổi sau preflight cũ; dùng quy trình refresh-preflight có lưu lịch sử và giữ deadline, không sửa identity thủ công.
4. Không mở SFT VN30 trên dataset `unverified`. Không coi việc thực thi code trên dữ liệu giả là nghiên cứu hoàn thành.

### Kiểm thử đã có bằng chứng

- 17 unit tests đạt trên môi trường model: raw replay/hash, audit không tự accept, nguồn/calendar fixture, split/budget/coverage, Ridge và normalization isolation, portable paths, checkpoint variant, ma trận dependencies, CPU resume bằng uninterrupted, hết hạn resume không reset clock.
- GPU smoke đủ Kronos-mini/small/base và Chronos-2-small: shape 20×4, hữu hạn, replay cùng seed, native loss/backward. Kronos có tokenizer prefix invariance và causal logits đạt. Receipt: `artifacts/local/pc-preflight-20261030/synthetic_smoke.json`.
- Random-init GPU smoke cho Kronos-small và Chronos: loss/gradient hữu hạn. Receipt: `artifacts/local/pc-preflight-20261030/random_initialization_smoke.json`.
- Ablation integration synthetic đã chạy hai nhánh, huấn luyện một epoch, validation/test forecast và score, paired bootstrap; initial backbone hashes bằng nhau. Output chỉ để kiểm thử ở `.cache/ablation-integration-6fy1em40/ablation/representation-s42/result.json`, không đưa vào bảng VN30.
- Positive scorer/report integration synthetic đã chạy đủ validation/test coverage cho một nhóm so sánh, tính lại metric, chẩn đoán, seed summary, learning curve và đồ thị. Receipt: `artifacts/local/pc-preflight-20261030/report_integration.json`; output `.cache/report-integration-c8taigpn/`. Không phải kết quả VN30.
- Syntax 26 file Python đạt; dependency data export khớp uv.lock; Ruff kiểm nhóm lỗi F đã đạt trước các thay đổi nhỏ cuối, cần kiểm lại khi sửa code thêm.
- Coordinator đã chạy và resume thật; audit gate giữ nguyên trạng thái incomplete và không đổi deadline.

### Mốc budget đã lưu

- Bắt đầu: 30/10/2026 14:09:17 +07:00.
- Deadline: 31/10/2026 14:09:17 +07:00.
- Đọc lại số thực từ state khi tiếp tục. Không kết luận còn thời gian chỉ từ ngày trong log.

## Nhật ký quyết định và thực hiện

### 01 — Khảo sát bài cũ

- Đọc README, checklist, báo cáo Q1–Q4, adapter/trainer và artifact đang active.
- Tính lại 72 dòng metric validation/test và kiểm 36 ô MAE trong báo cáo cũ: khớp. Hai checkpoint active cũ khớp SHA256.
- Nhận diện các thiếu sót nghiên cứu: chưa ARIMA/ETS, một seed/một mức train, thiếu đối chứng/ablation, nhóm volatility cao nhỏ, test đã xem, Open chưa rõ semantics.
- Không kết luận bài cũ sai toàn bộ: số liệu nội bộ khớp, nhưng phạm vi kết luận còn hạn chế.

### 02 — Chốt phạm vi với người dùng

- Người dùng sửa rõ muốn **Kronos**, không phải thêm kích thước Chronos.
- Chọn audit bản cũ + bản hiệu chỉnh có bằng chứng; đủ Q1–Q4; tổng 24 giờ; giữ Chronos ZS/SFT.
- Không dùng checkpoint SFT cũ của môi trường khác cho kết quả mới.

### 03 — Chuẩn bị PC và model

- Tạo `.venv-data` cho uv/DVC; `.venv` được sync frozen từ lock CUDA.
- CUDA kiểm thực tế: torch 2.14.0+cu130 nhận RTX 4070 SUPER.
- Bootstrap `.vendor/Kronos` đúng revision `67b630e67f6a18c9e9be918d9b4337c960db1e9a`.
- Bổ sung provenance mini/base/tokenizer-2k bằng revision và SHA256 từ model repository công khai. Đã tải/kiểm checksum cả bốn predictor và hai tokenizer.

### 04 — Thay đổi phần mềm

- `src/research_protocol.py`: model registry, portable paths, code identity, budget origins, coverage và folds.
- `src/vn30_forecast.py`: dataset theo manifest/audit, variant/tokenizer phù hợp, baseline adapter, checkpoint validation và chọn epoch 0.
- `scripts/finetune_vn30.py`: variant, random initialization, budget, resume optimizer/RNG/epoch, best-trained/selected riêng, OOM microbatch replay.
- `scripts/run_experiment.py` + `experiment_tasks.py`: ma trận/dependencies, stage caps, clock bất biến, state/log/evidence và report.
- `src/statistical_baselines.py`: grid validation, refit past-only, không silent fallback.
- `scripts/representation_ablation.py`: continuous-vs-quantized fixed encoder, matched random backbone.
- `src/research_statistics.py`: origin-known volatility, periods và paired block bootstrap.
- Thêm kiểm toán/fetch/restore/smoke scripts; cập nhật CLI, kiểm thử CI, tài liệu và Git ignore/LFS cho checkpoint.

### 05 — Lấy dữ liệu gốc từ Drive

- DVC mở OAuth nhưng chờ đăng nhập; người dùng cung cấp link thư mục được mời qua Gmail.
- Dùng computer-use đọc đúng Drive tab đang đăng nhập và tải thư mục `files/md5`; không thay quyền chia sẻ hoặc đọc email ngoài nhiệm vụ.
- ZIP tải về: `C:/Users/neikh/Downloads/md5-20261030T022826Z-1-001.zip`.
- Importer phát hiện Drive thêm đuôi kiểu file; sửa cách canonicalize bằng 32 ký tự hash và xác minh MD5 nội dung trước khi ghi.
- Khôi phục đúng 89 file. Kiểm SQLite/ZIP SHA256, raw replay và flags đạt. Dừng tiến trình DVC OAuth do agent mở sau khi không còn cần.
- Không lưu token hoặc OAuth credential vào repo/log.

### 06 — Kết luận kiểm toán hiện tại

- Fetch mới VPS: 2.271 hàng, 25/08/2017–02/10/2026; 2.270 ngày giao với snapshot.
- Fetch mới DNSE: 1.565 hàng, 11/05/2020–01/10/2026; 1.565 ngày giao.
- Ngưỡng phát hiện khác biệt: 0,02 điểm, không phải quy tắc chọn nguồn đúng.

| Nguồn | Trường | Phép so sánh lệch | Chênh lệch lớn nhất |
|---|---|---:|---:|
| DNSE | Close | 54 | 16,35 |
| DNSE | High | 114 | 36,81 |
| DNSE | Low | 237 | 34,96 |
| DNSE | Open | 448 | 47,91 |
| VPS | Close | 6 | 2,47 |
| VPS | High | 55 | 36,81 |
| VPS | Low | 169 | 34,96 |
| VPS | Open | 147 | 27,96 |

- Tổng 1.230 phép so sánh lệch, 60 ngày Close khác nhau. Chưa xác định nguồn nào đúng cho mọi trường hợp.
- Có 78 phiên Open bằng Close trước, gồm chuỗi 71 phiên đã được báo trong giai đoạn 2025; không coi cả 78 là cùng một bất thường đã chứng minh.
- Chưa có calendar độc lập đầy đủ. Trạng thái **unverified**, không có sửa giá, không tạo dataset hiệu chỉnh thiếu căn cứ.
- Raw cũ còn có các lần điều tra VCI/KBS và một số publication. Metadata VCI/KBS cũ cũng ghi pending validation và invalid OHLC. Chưa coi các file đó là lời giải cho toàn bộ khác biệt.

### 07 — Sửa lỗi phát hiện khi kiểm thử

- Temporary files ban đầu ở vùng tạm Windows không cho atomic rename trong môi trường chạy: chuyển fixture temp vào `.cache/test-runs` trong workspace.
- SQLite audit dùng context manager connection nhưng chưa đóng connection thật: đổi sang `contextlib.closing`, xác minh test cleanup/locks đạt.
- Audit không có nguồn đối chiếu làm `nlargest` lỗi dtype object: đổi sang sort/head để báo unverified bình thường, không crash.
- Lint ablation phát hiện biến closure bị xóa cuối vòng: giữ binding bằng gán None sau khi dùng, kiểm tra lại và chạy integration GPU đạt.
- Các sửa đổi là sửa phần mềm mới; không thay dữ liệu thị trường để làm test pass.

### 08 — Chạy pipeline chính

- Thực thi `run_experiment.py run --config configs/pc_rerun.json`, rồi `resume`/`status`.
- Đạt recover/fetch/audit/weights/bootstrap; `prepare` blocked vì dataset chưa được kiểm chứng. Toàn bộ bước phụ thuộc giữ blocked.
- Kết quả thực tế: 5 complete / 283 blocked / tổng 288. Không có GPU job VN30 chạy nền cần chờ.
- Báo cáo: `artifacts/local/pc-rerun-20261030/report.md`; chi tiết audit trong `audit/summary.md`; việc còn thiếu trong `remaining.json`.

### 09 — Yêu cầu ghi nhớ của người dùng

- Tạo `AGENTS.md`, `AGENT.md`, `IMPLEMENTATION_PLAN.md`, `AGENT_LOG.md` để phục hồi mục tiêu, quyết định, artifact, flaw, cách xử lý và điểm tiếp tục sau compaction.
- Không chỉ ghi checklist. Mỗi hướng tối ưu mới phải có lý do và bằng chứng; giải pháp chưa chạy đủ phải giữ trạng thái pending.

### 10 — Kiểm tra đường đi có kết quả và điểm cần siết tiếp

- Chạy scorer/report end-to-end với forecast synthetic đủ origin cho ZS/FT và các baseline; metric recomputation, bootstrap, bảng seed, learning curve và plot đều xuất được. Không thêm số liệu này vào main report VN30.
- Trong lần rà soát, nhận diện F12: score worker cần thêm test âm cho seed/device/aggregation và receipt checkpoint; hiện chưa đánh dấu phần kiểm tra này hoàn thiện.
- Hiện có cảnh báo Matplotlib về cache ở vùng user không ghi được trong môi trường giới hạn (đã tự dùng temp trong workspace) và pandas future warning về fillna. Không làm test fail; không đổi dependency lock chỉ để tắt cảnh báo. Khi tối ưu tiếp, cấu hình cache workspace và đổi cách ép dtype có kiểm thử.

### 11 — Tiếp tục goal: siết protocol và xác minh resume GPU

- Đọc lại bốn file ghi nhớ và working tree trước khi tiếp tục.
- Thêm `src/forecast_protocol.py`, đối chiếu forecast với task/config/model provenance và receipt SFT. Kiểm seed/device/context/horizon/sampling/aggregation, baseline validation lock, budget/init/LR/epoch, tokenizer và hash weights; hash CSV cùng metadata vào receipt score.
- Tái sử dụng score chỉ khi input/output hash vẫn khớp. Các ca sửa sai metadata hoặc weights bị từ chối. Kiểm thử integration xác nhận score đầy đủ chạy được rồi từ chối score/forecast bị thay.
- Thêm refresh-preflight có lưu snapshot cũ, chỉ cho phép trước bất kỳ research artifact nào, config/provenance không đổi và evidence còn khớp; không đổi started/deadline. Chưa áp dụng lên lượt thật ở thời điểm ghi mục này.
- Kiểm thử native Kronos-mini trên RTX 4070 SUPER bằng dữ liệu giả: interrupted sau epoch 1 rồi resume tới epoch 2 khớp uninterrupted. Receipt `artifacts/local/pc-preflight-20261030/native_resume_smoke.json`; không phải SFT VN30.
- Bộ test đã đạt 31 tests trước integration bổ sung. Sau integration, lượt test đạt nhưng bị đếm lặp do import TestCase; đã sửa import sang module để tránh đếm trùng, cần kiểm lại số cuối.
- Đã tải bản tin mới từ CSI (09/04/2020), Phú Hưng (bản tin 23/09 cho phiên 22/09/2020), và Pinetree (26/10/2022, 09/11/2022). Text và hình trang đầu hai PDF xác nhận các giá 697,85 và 852,72 khớp VNDIRECT, không khớp VPS ở hai ngày đó. Pinetree công bố 990,41 và 979,68 khớp VNDIRECT, khác DNSE. Đây là bằng chứng từng trường hợp, chưa chấp nhận cả dataset.
- Raw mới lưu `data/raw/source_evidence/pc-20261030/manifest.json` cùng URL/hash. Không sửa giá gốc.

### 12 — Chốt kiểm thử, lưu điều tra mới và refresh preflight có lịch sử

- Bộ test cuối: **39 tests, OK, skipped=1**. Một ca bị bỏ qua mặc định là native GPU resume, đã bật và chạy riêng đạt. Sai khác tham số mini lớn nhất 5,96e-8; validation loss 0,7652203063 so với 0,7652203048. Receipt `artifacts/local/pc-preflight-20261030/test_summary.json` và `native_resume_smoke.json`.
- `review_close_publications.py` đã thử 60 ngày Close tranh chấp: 46 URL không tải được, 14 bản tin có raw/hash. Lượt đầu 6 hỗ trợ giá gốc, 8 chưa đủ ngữ nghĩa Close. Bổ sung cụm “khép phiên” rồi phân tích lại raw đã tải, không gọi lại 46 URL lỗi: 7 hỗ trợ giá gốc, 7 còn là ứng viên. Giữ cả `review.json` và `cached_reparse.json`, không ghi đè lịch sử.
- Hai bản tin 05/03 và 24/03/2021 có bảng chỉ số gần VPS; bản CSI cũ lại hỗ trợ VNDIRECT nhưng có nhãn hợp đồng cũ. Không coi giá ứng viên hoặc bản tin có dấu hiệu cũ là xác nhận tự động. Ghi F13: cần sổ adjudication có nguồn/semantics thay vì chờ mọi nhà cung cấp đồng thuận.
- Ghi F14: chuỗi Open bất thường bắt đầu cùng ngày KRX vận hành; VNDIRECT 71/71, VPS 0/71, DNSE 5/71 trong đoạn. Đây chỉ là giả thuyết nguyên nhân để điều tra. Không chỉnh giá theo giả thuyết.
- Hồ sơ đọc lại: `artifacts/local/pc-preflight-20261030/evidence_review.md`, dẫn raw/URL/hash và phạm vi chưa xác minh. Chưa tích hợp adjudication vào cổng audit, dataset vẫn unverified.
- Áp dụng `refresh-preflight --reason` sau kiểm thử: lưu state/audit/log/report cũ tại `artifacts/local/pc-rerun-20261030/preflight_history/20261030T075623Z-83b83b50`; ghi source identity trước/sau, không thay config/provenance, không có artifact nghiên cứu. Sau đó resume thành công: **5 complete / 283 blocked / 288**. Không có training VN30 chạy nền.
- Kiểm bằng assertion: started vẫn `2026-10-30T07:09:17.918025+00:00`, deadline Unix `1793430557.9180253`, chênh đúng 86.400 giây. Không cấp thêm thời gian. Git diff whitespace check đạt; hai Chronos LFS modified ban đầu vẫn được giữ nguyên.
- Điểm tiếp tục: xử lý bằng chứng giá và calendar độc lập, thiết kế adjudication có kiểm thử nếu đủ nguồn; không lách audit để tạo bảng Q1–Q4. Code identity hiện đã khớp state sau refresh. Sửa Python tiếp sẽ lại làm resume từ chối; đọc điều kiện refresh trong tài liệu trước khi thay đổi.

### 13 — Quy ước lưu Git theo yêu cầu người dùng

- Nhánh làm lại: `neikhn/lam-lai-vn30-pc`; lưu checkpoint commit/push sau mỗi mốc đáng kể, message ngắn gọn. Stash khi cần giữ tạm để chuyển nhánh/ngữ cảnh.
- Checkpoint đầu gồm code PC rerun, kiểm thử, plan/log và audit receipts hiện có; dữ liệu vẫn unverified. Đã rà danh sách file và mẫu credential trước khi stage.
- Giữ ngoài commit hai weights Chronos LFS cũ đã hiện modified từ đầu; không đưa môi trường/cache/credential lên Git.
- Đã tạo commit `3cfb7b0` — `feat: rebuild VN30 pipeline on PC`. Push đầu bị bộ duyệt tự động chặn vì có CSV/artifact trong kho public. Đã xác minh visibility và hỏi đúng phạm vi; người dùng xác nhận **“Push toàn bộ commit”**. Push lại thành công lên `origin/neikhn/lam-lai-vn30-pc`, có upstream. Không tạo PR vì chưa được yêu cầu.

### 14 — Bắt đầu và hoàn tất SFT thăm dò trên PC, giữ cổng chính

- F15: chỉ chặn huấn luyện chính đã bỏ sót nhánh thăm dò được kế hoạch cho phép khi OHLC còn nghi vấn. Thêm scope `exploratory_only` và opt-in trainer; loader mặc định, inference checkpoint chính và scorer chính từ chối scope này. Không đổi dataset thành accepted, không sửa giá. Đã kiểm các ca opt-in/budget/integrity/audit receipt/primary rejection; **46 tests OK, skipped=1**, static checks đạt.
- Refresh preflight trước khi có training artifact ở lượt chính, lưu lịch sử `preflight_history/20261030T080938Z-6f47fbe3`, rồi resume 5 complete/283 blocked. Config/provenance và started/deadline vẫn nguyên. Nhánh thăm dò có output/manifest/receipt riêng, deadline lấy từ state gốc.
- **Đã chạy thật trên RTX 4070 SUPER:** bốn benchmark (một epoch và 32 origin validation/model), rồi 12 SFT (mini/small/base/Chronos × seed 42/43/44 × đủ năm epoch), 1.442 cửa sổ train và 321 validation/lượt. GPU tuần tự; không dùng test để train/chọn epoch. Tất cả job terminal complete; lock được dọn, không còn lượt này chạy nền.
- Receipt `artifacts/local/pc-exploratory-20261030/verification.json` kiểm checksum best/selected, model/scope/protocol, đủ năm epoch trong history, source identity và deadline gốc. `training_summary.csv`, `native_loss_history.csv`, `native_validation_loss.png` sinh trực tiếp từ receipts/history; đã xem hình. Loss native khác tokenizer/objective, không dùng để xếp hạng model.
- Ba Kronos chọn epoch 5 theo native validation; Chronos chọn epoch 0 ở cả ba seed vì best-trained (epoch 1) vẫn kém pretrained. Giữ cả best-trained và selected. Chưa biết tác động tới MAE/RMSE vì chưa có chấm dự báo test mới.
- Thời gian một epoch: mini 4,19s, small 7,98s, base 18,45s, Chronos 12,23s; 32 origin validation lần lượt 7,34/7,55/13,66/7,36s. Peak allocated cao nhất base ~2,73GB (không phải tổng VRAM tiến trình). Ước lượng phần neural ma trận ~4,73h, **chưa tính** CPU baseline, ablation, setup và giải quyết dữ liệu; không tuyên bố toàn bộ chắc chắn vừa ngân sách.
- CPU probe trên ba origin validation cố định: ARIMA 54 lượt cấu hình/origin có 3 lỗi convergence, ETS 9 lượt không lỗi. Lưu nguyên lỗi, không thay bằng Naive; chưa chọn cấu hình từ probe. Ngoại suy sơ bộ toàn grid validation ~21 phút ARIMA/~49s ETS, không phải benchmark bảo đảm cho mọi origin.
- Calendar: tải VNINDEX từ VPS và DNSE, lưu raw/URL/hash. Tập ngày VPS VNINDEX khớp toàn bộ VN30; DNSE VNINDEX thiếu 33 ngày. Audit bổ sung `pc-preflight-20261030/calendar_crosscheck/audit/` ghi pass trong phạm vi lịch quan sát, metadata `official_exchange_calendar: false`; dataset vẫn unverified do giá. Không thay audit đang khóa.
- Đọc và xem ảnh hai PDF Pinetree 05/03 và 24/03/2021, bảng VN30 riêng với futures hỗ trợ các giá ứng viên đã thấy; vẫn giữ mâu thuẫn chưa phân xử. BSC endpoint thử trả nội dung không phải PDF, không dùng làm bằng chứng. Cập nhật `evidence_review.md`.
- Điểm tiếp tục: cần forecast/chấm giá ZS/SFT và baseline dưới scope rõ ràng, tiếp tục nguồn O/H/L/Close và calendar chính thức. Cần Q3 random/learning, Q2 ablation, Q4 folds/bootstrap mới. Không tự chuyển 12 checkpoint thăm dò thành bằng chứng chính. Mục tiêu đầy đủ và deadline gốc vẫn giữ.
- Đã commit/push checkpoint tiến độ `afc33df` — `feat: run exploratory PC fine-tuning` lên nhánh `neikhn/lam-lai-vn30-pc`; local HEAD và remote-tracking đã khớp. Payload chỉ gồm code/tài liệu/CSV/đồ thị/receipts; weights và optimizer thăm dò giữ PC theo ignore.

### 15 — Main forecast/baseline, Q3 và Q2/Q4 xếp hàng

- Thêm `scripts/evaluate_candidate.py` như entry point mới duy nhất trong src/scripts: kiểm mọi hash file cũ giữ nguyên trước khi dùng checkpoint SFT PC, không sửa receipt training. Có identity riêng cho inference. Primary coordinator vẫn giữ identity cũ và audit gate; không âm thầm resume nó dưới code mới.
- Baseline hoàn tất 11/11 job gồm ba validation lock và tám forecast validation/test. Chọn Ridge alpha 10, ETS level, ARIMA(0,1,0); không dùng test để chọn. Lỗi hội tụ của ứng viên được lưu, không có Naive fallback.
- Neural có 48 forecast dự kiến, seed 42/43/44. Seed 42 đủ 16 forecast đã chấm tạm cả validation/test và kiểm metric/coverage/receipt; có paired block CI, volatility và periods. `interim_view.json` ghi rõ 1/3 seed, không hoàn thành main. Naive đang mạnh ở Close; giữ cấu hình đã khóa, không tuning theo test.
- Q3 xếp hàng qua `experiments/candidate_learning.py`: 36 so sánh; 12 pretrained budget nhỏ và 54 random-LR trials mới, tái dùng sáu full-budget pretrained PC. Giữ cùng holdout/origin; hash riêng orchestrator cùng frozen core identity. Chọn và dùng thẳng trial thắng validation; không train lại để tiết kiệm chi phí. Trial process lỗi được ghi, lỗi protocol/hash dừng.
- Q2/Q4 xếp sau Q3 qua `candidate_stability.py`: ba paired continuous/quantized ablation seed, hai expanding folds cho bốn neural model seed 42. `candidate_ablation.py` là specialization của mã frozen, thay loader opt-in và scope/provenance, giữ nguyên số học. Không giả audit accepted. Tất cả có deadline/stage cap gốc và GPU lock.
- Điều tra bổ sung: bảng lịch sử Investing bị modal đăng ký/cookie chặn, chưa lấy được giai đoạn mục tiêu; không đăng nhập bằng tài khoản người dùng. Probe nến phút VNDIRECT/VPS ở 05/05, 11/08, 12/08/2025 đều trả không có bar; đây không phải bằng chứng không có giao dịch, chỉ chưa lấy được dữ liệu phút để phân xử Open. Raw/URL/hash ở `data/raw/source_evidence/intraday-open-probe-20261030/manifest.json`.
- Người dùng hỏi Chronos-2: đã đối chiếu `git show main` báo cáo lịch sử và checkpoint cũ. VN30 cũ đã dùng `autogluon/chronos-2-small` ZS/SFT; trọng tâm lần làm lại vẫn là ba Kronos, Chronos là đối chứng. Không thay scope model khi chỉ được hỏi giải thích.

### 16 — Bàn giao 3 giờ không cần agent theo dõi

- Người dùng xác nhận rõ **“Tạm dừng agent 3 giờ, PC tiếp tục chạy”** sau khi kiểm tra bàn giao. Không dừng computation khi pause goal chat. Quota kiểm thực tế 84% used của cửa sổ 5h, reset 19:01:09 +07 ngày 30/10; không ghi account id/token.
- Thêm `experiments/unattended_supervisor.py`: nhận worker theo command/PID thực, GPU tuần tự, tối đa hai lần tiếp tục worker đã chết, không xem chậm là đã chết. Source/hash/protocol sai thì lưu needs_attention, không tự sửa khoa học. Lưu PID/status/events và `UNATTENDED_REPORT.md`; Git checkpoint artifact có whitelist, không interactive login, lỗi Git không dừng GPU.
- Giữ máy khỏi tự sleep bằng API theo tuổi thọ supervisor; không đổi thiết lập power vĩnh viễn. Có lock ngăn supervisor trùng. Khôi phục lock chết có archive, không lấy lock của process sống hoặc orphan training worker.
- Kiểm thử cuối **58 tests OK, skipped=1**. Self-test thật dùng process dùng một lần exit 7, chạy tiếp thành công exit 0, checkpoint từ epoch 1 tới 2 được giữ; không chạm worker nghiên cứu. Receipt `pc-preflight-20261030/supervisor_recovery_test.json`.
- Snapshot health trước khi chạy nền: 11/11 baseline, 40/48 neural, Q3 và followups đang có PID sống và đúng hàng chờ. Trạng thái thực tế tiếp tục cập nhật; không dựa vào số snapshot này khi quay lại.
- Điểm tiếp tục sau 3h: đọc `supervision/status.json`, `events.jsonl`, `UNATTENDED_REPORT.md`, kiểm PID/command thật; kiểm queued phases/output/metric từ CSV. Chưa đủ dữ liệu để kết luận chính. Không sửa các file Python đã khóa khi worker còn sống. Cần hoàn thiện báo cáo nghiên cứu và kiểm tra metric trực tiếp từ forecast/nhãn, không chỉ từ details.csv.

## Việc chưa hoàn thành / rủi ro cần giữ nguyên trong bàn giao

### 17 — Xác minh hàng đợi đã tự hoàn tất, bàn giao pause

- Thời điểm kiểm tra lại thực tế: 30/10/2026 21:17 +07. `supervision/events.jsonl` ghi supervisor PID 30948 chạy từ 16:27:44 và tự kết thúc **18:22:28 +07** với pipeline_complete=true, chưa chạm deadline gốc. `psutil.process_iter` không còn process supervisor/learning/stability khớp command thật; không restart.
- State đối chiếu: baseline 11/11, neural 48/48, score ba seed xong; learning 36/36; followups ablation seed 42/43/44 và fold1/fold2 đều terminal complete. Ba ablation có verified.json. Đây là bằng chứng hoàn tất hàng đợi, chưa thay cho kiểm định nghiên cứu toàn diện hoặc chấp nhận dataset.
- Supervisor được chuyển sang Windows Task Scheduler `VN30-PC-Supervisor-20261030` để độc lập vòng đời tool. Truy vấn CIM Task Scheduler ở lần kiểm tra mới bị hạn chế quyền; dùng process thật và events để xác minh kết thúc, không suy từ lỗi truy vấn là worker lỗi.
- Phát hiện Git checkpoint tự động bị bỏ qua vì index còn staged. Nguyên nhân ban đầu là supervisor.lock nằm trong payload; đã bỏ stage lock và thêm ignore `supervision/*.lock`, giữ dữ liệu khác nguyên vẹn. Bàn giao bằng commit/push thủ công sau kiểm staged; toàn bộ 1.683 file mới đều CSV/JSON/PNG/Markdown, không weights/optimizer.
- Không tạo thành công lịch gọi agent một lần sau ba giờ: cấu hình COUNT=1 ban đầu không có future run; cấu hình có DTSTART chỉ được phép ở chế độ đề xuất; lần thử COUNT=2 bị **automatic approval review từ chối** vì có thể tạo hai lượt gọi và dùng thêm quota ngoài phạm vi. Không lách bằng cron hay lịch khác; không có automation được tạo. Cần nói rõ với người dùng không có tự thức dậy.
- Người dùng đã xác nhận pause agent ba giờ, PC tiếp tục. Pipeline thực tế đã tự xong trước bàn giao; không khởi chạy công việc thừa. Pause goal chat sau khi lưu checkpoint, không đánh dấu mục tiêu nghiên cứu complete.
- Điểm tiếp tục: kiểm trực tiếp metric từ forecast/SQLite và đầy đủ hash/origin/receipt; kiểm learning/folds/ablation rồi dựng báo cáo mới. Tiếp tục bằng chứng OHLC/calendar, không tự nâng scope exploratory_only. Deadline 31/10/2026 14:09:17 +07 giữ nguyên.
- Người dùng đã quay lại, thông báo quota đầy và hỏi complete đã xong chưa. Yêu cầu pause cũ không còn áp dụng cho phần kiểm định đang tiếp tục; goal tự động đã được người dùng xóa, không tự tạo mới. Đã giải thích complete là hàng đợi thăm dò xong, chưa phải bài hoàn thiện.
- Thêm post-run verifier riêng `experiments/verify_completed_candidate.py`, không sửa frozen src/scripts hoặc artifact cũ. Đọc forecast CSV và SQLite read-only, không dùng scorer/details.csv để tính metric. **Đạt:** 88 nhóm score, 182 forecast files, 2.160 dòng metric (cả Open/Close và gap/intraday); kiểm full path/ngày/split/finite/n/MAE/RMSE/Naive delta. Negative check đổi ngày nhãn bị từ chối. 85 output receipts và 90 cặp training/selection khớp hash bytes checkpoint (90 gồm benchmark và LR trials). Receipt `review/numerical_validation.json`, CSV tính lại và trạng thái tự chứa ở `review/STATUS.md`.
- F12 phần kiểm metric trực tiếp forecast/nhãn đã có bằng chứng mới; không còn chỉ tính từ details.csv. Giới hạn: verifier này chưa độc lập chạy lại bootstrap/tuning hoặc chứng minh giá thị trường đúng. Bảng -ft hiện dùng best-trained; Chronos selected epoch 0 phải được giải thích riêng trong báo cáo.

- Chưa giải quyết bằng chứng giá O/H/L/Close giữa các nhà cung cấp và chưa có calendar độc lập đầy đủ.
- Đã có SFT và forecast/score tạm seed 42; main đủ ba seed và Q2/Q3/Q4 đang chạy/xếp hàng. Chưa đủ bằng chứng chính Q1–Q4.
- Đã có benchmark dữ liệu thật nhưng chưa chứng minh toàn bộ ma trận, kiểm toán và báo cáo vừa 24 giờ.
- Native GPU resume Kronos-mini đã đạt; các variant khác và forced-OOM stress chưa thử đầy đủ.
- F12 đã có kiểm thử âm và integration; bộ test cuối 58 ca đạt như mục 16. Cần thêm bước đối chiếu metric trực tiếp từ forecast/nhãn trong lần tổng hợp cuối; hiện recomputation chủ yếu từ details.csv. Chỉ chạy lại test khi có thay đổi hoặc nghi vấn mới cần kiểm chứng.
- Không sửa code Python rồi giả vờ resume cùng identity. Ghi rõ thay đổi và xử lý tương thích/budget trước khi tiếp tục.
- Một số lệnh Git trong môi trường giới hạn lỗi git-lfs filter. Dùng `git -c filter.lfs.required=false -c filter.lfs.process= -c filter.lfs.clean= ...` để đọc trạng thái/diff; không dùng kết quả modified của hai weights Chronos cũ để kết luận agent đã sửa chúng.

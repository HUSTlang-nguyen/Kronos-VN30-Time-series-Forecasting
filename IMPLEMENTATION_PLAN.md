# Implementation plan — VN30 PC rerun

## 1. Mục tiêu và định nghĩa hoàn thành

Làm lại trên PC hiện tại với Kronos mini/small/base, Chronos-2-small ZS/SFT, Naive/Ridge/ARIMA/ETS. Hoàn thiện bằng chứng Q1–Q4 trong tổng ngân sách chạy 24 giờ. Artifact cũ chỉ dùng làm đối chiếu lịch sử.

Phân biệt ba mức:

1. **Đã triển khai:** có code và giao diện thực thi.
2. **Đã kiểm thử phần mềm:** có kiểm thử unit/integration/smoke chứng minh nhánh code hoạt động.
3. **Đã có bằng chứng nghiên cứu:** đã chạy trên dữ liệu được kiểm toán, đủ mẫu/seed/fold và có output được xác minh.

Không dùng mức 1 hoặc 2 để đánh dấu mức 3. Hiện chưa hoàn thành nghiên cứu.

## 2. Kế hoạch triển khai và trạng thái

| Hạng mục | Triển khai/kiểm thử | Thí nghiệm dữ liệu thật |
|---|---|---|
| Môi trường PC/CUDA, pinned code/model/tokenizer | Đã cài, checksum và GPU smoke đạt | Sẵn sàng về phần mềm |
| Khôi phục dữ liệu, raw replay và đối chiếu nguồn | Đã chạy; có CSV và audit report | Chưa chấp nhận dataset |
| Loader theo manifest, hash và điều kiện audit | Đã triển khai, có kiểm thử | Chặn dataset unverified |
| Adapter mini/small/base/Chronos, alias tương thích | Đã triển khai; bốn model qua GPU smoke | Đủ 48 forecast validation/test thăm dò, ba seed |
| SFT, epoch 0, checkpoint optimizer/RNG, resume | Đã triển khai; CPU/native mini GPU resume đạt | Đã đủ 12 SFT thăm dò × 5 epoch; chưa bằng chứng chính |
| Ridge/ARIMA/ETS tuning validation, không fallback âm thầm | Đã triển khai; grid/lock kiểm lại | Đã có kết quả thăm dò; ARIMA 6/18 cấu hình không đủ coverage, không được chọn |
| Q3: 500/1.000/full, pretrained/random, ba seed | Đã triển khai; kiểm 18 LR selection | Đủ 36 so sánh thăm dò và learning curve |
| Q2: continuous/quantized, cùng encoder/backbone | Đã triển khai; hash khởi tạo hai nhánh khớp | Đủ ba seed thăm dò; không có lợi ích đồng nhất |
| Q4: seed/horizon/volatility/fold/bootstrap | Đã kiểm lại trực tiếp 378 CI và 1.782 metric subgroup | Có bảng thăm dò, hai fold; hai fold không có high-vol origin |
| Điều phối 24h, plan/run/resume/status/report | Đã chạy; clock không reset, audit gate chặn đúng | 5/288 hoàn thành; 283 blocked |
| Báo cáo, seed summary, learning/loss plots, selected-score | Postprocessor riêng kiểm input/selection và sinh từ CSV | Báo cáo PC Q1–Q4 thăm dò đã dựng; không đủ điều kiện nghiên cứu chính |
| Tài liệu và ghi nhớ repo | Đang duy trì | Không thay thế artifact |

## 3. Đăng ký flaw và quyết định xử lý

### F01 — Nhầm độ nguyên vẹn file với chất lượng dữ liệu

- **Bằng chứng:** raw và checksum đúng nhưng có 1.230 phép so sánh OHLC lệch hơn 0,02 điểm với nguồn khác; lịch phiên chưa hoàn tất.
- **Giải pháp:** tách integrity/replay/market crosscheck/calendar; chỉ trạng thái `accepted_provider_scope` mới cho phép tạo manifest chạy chính.
- **Vì sao:** huấn luyện thêm trên nhãn chưa giải thích được sẽ tạo thêm số liệu mà không giải quyết điểm yếu gốc.
- **Trạng thái:** cổng phần mềm đã kiểm thử; chất lượng thị trường **chưa giải quyết**. Không có chỉnh giá nào được thực hiện.

### F02 — Dataset và adapter khóa cứng một snapshot/một bản small

- **Giải pháp:** manifest v2 xác định dataset/receipt/audit/hash; registry chọn mini/small/base và tokenizer tương ứng, giữ alias `kronos` cho small.
- **Kiểm chứng:** test manifest, split, coverage và GPU smoke bốn model.
- **Giới hạn:** chưa có dataset hiệu chỉnh được xác nhận; loader linh hoạt không đồng nghĩa đã có dữ liệu mới hợp lệ.

### F03 — Chọn checkpoint đã cập nhật dù pretrained có validation tốt hơn

- **Bằng chứng:** Chronos cũ có pretrained validation loss thấp hơn mọi epoch SFT.
- **Giải pháp:** giữ `best/` trong các epoch cập nhật và `selected/` xét cả epoch 0; xuất `training.json`, `selection.json`; CLI có `--checkpoint-choice`.
- **Vì sao:** đo tác động SFT vẫn cần checkpoint sau cập nhật, nhưng lựa chọn sử dụng phải được phép giữ pretrained.
- **Trạng thái:** đã triển khai; cần giữ rõ hai loại điểm trong báo cáo thật. Không chọn theo test.

### F04 — Thiếu baseline thống kê và tuning công bằng

- **Giải pháp:** Ridge alpha 1/10/100/1000; ARIMA p/q 0–2, d 0–1; ETS level/additive/damped; chọn trên validation với MAE chuẩn hóa bằng train.
- **Chính sách:** ứng viên lỗi phải ghi lỗi/mẫu thiếu; không thay bằng Naive hoặc bỏ origin rồi so như đủ mẫu.
- **Trạng thái:** code có; chưa có kết quả baseline mới do dữ liệu bị chặn.

### F05 — Một mức dữ liệu không trả lời được lợi ích khi ít dữ liệu

- **Giải pháp:** 500/1.000/full phiên train lồng nhau, cùng ngày kết thúc, cùng validation/test; so pretrained và predictor random trên Kronos-small/Chronos.
- **Tối ưu chi phí:** hai model đại diện; dùng lại full-budget pretrained job của main, không chạy lại nhánh trùng trong ma trận.
- **Giới hạn:** tokenizer Kronos vẫn pretrained; chỉ đo lợi ích predictor pretraining. Ngân sách 5 epoch không chứng minh hiệu quả tối đa khi huấn luyện đến hội tụ.
- **Trạng thái:** random-init native GPU smoke đạt; thí nghiệm VN30 chưa chạy.

### F06 — Gán lợi thế Kronos cho representation từ so sánh hai họ model

- **Giải pháp:** ablation riêng continuous normalized feature so với BSQ feature từ cùng encoder frozen; cùng backbone small random, head/loss và điều kiện huấn luyện.
- **Kiểm chứng:** integration synthetic đã huấn luyện hai nhánh, forecast, score và bootstrap thành công; initial backbone hash bằng nhau.
- **Giới hạn:** đây là can thiệp lượng tử hóa trong thiết lập này, không chứng minh mọi thành phần của financial K-line representation.
- **Trạng thái:** code/integration đạt; nghiên cứu chưa chạy.

### F07 — Suy độ ổn định từ một seed hoặc một cụm biến động

- **Giải pháp:** ba seed; horizon 1/5/20; ba đoạn test; sigma20 chỉ dùng quá khứ, ngưỡng train p90; hai expanding folds; paired moving-block bootstrap block 20, 2.000 lần.
- **Giới hạn:** chưa tạo thêm chu kỳ thị trường độc lập bằng việc đổi seed. Fold lịch sử trước khi checkpoint được công bố chỉ là hồi cứu.
- **Trạng thái:** code và bootstrap integration có; chưa có bảng VN30 mới.

### F08 — Tiếp tục sau gián đoạn và giới hạn tài nguyên

- **Giải pháp:** checkpoint epoch lưu model/optimizer/RNG/shuffle; progress forecast theo origin; một deadline được lưu cố định qua resume; GPU tuần tự.
- **Tối ưu:** tokenizer feature cache trong mỗi setup, effective batch 16; khi OOM giảm microbatch và replay epoch từ checkpoint, không bỏ mẫu/đổi precision.
- **Kiểm chứng:** CPU interrupted/resumed training khớp uninterrupted; native Kronos-mini GPU resume sau epoch 1 tới epoch 2 đạt, sai khác tham số lớn nhất 5,96e-8; test hết hạn không reset clock; bốn model chạy được FP32 trên PC.
- **Cần phân biệt:** GPU resume mới kiểm thử mini bằng dữ liệu giả; chưa kiểm mọi variant hoặc stress-test đầy đủ nhánh OOM cưỡng bức.

### F09 — Receipt Windows và khác biệt newline làm khó tái lập

- **Giải pháp:** đường dẫn tương đối chuẩn hóa, bộ đọc chấp nhận backslash cũ; giữ hash byte cho dữ liệu/weights, hash mã nguồn chuẩn hóa newline cho resume.
- **Kiểm chứng:** test portable path; kiểm tra source/provenance/evidence trước resume.
- **Giới hạn:** không tự đổi code rồi sửa receipt/state cho khớp; cần lưu lịch sử thay đổi và quyết định ngân sách rõ ràng.

### F10 — Token tương lai và nhãn test có thể rò vào quy trình

- **Giải pháp:** cửa sổ nhãn nằm trọn trong tập; scaler context-only; causal teacher forcing; tokenizer/model đúng vocabulary; thử thay token/giá tương lai.
- **Kiểm chứng:** unit tests isolation và native GPU causal/tokenizer checks cho ba Kronos đạt.
- **Giới hạn:** cutoff pretraining chưa xác minh đầy đủ; kiểm thử không chứng minh pretrained model chưa từng thấy VN30.

### F11 — Dữ liệu qua Drive có quyền nhưng OAuth DVC chờ

- **Giải pháp đã dùng:** tải thư mục `files/md5` bằng trình duyệt người dùng đã đăng nhập; kiểm content hash rồi phục hồi theo pointer vào cache/data.
- **Kiểm chứng:** khôi phục 89 file; SQLite và ZIP đều khớp receipt. Google Drive tự thêm `.html/.pdf/.zip` cho một số object; importer xác định bằng hash thay vì tin đuôi tệp.
- **Trạng thái:** đã giải quyết việc lấy dữ liệu. Không nhầm với việc chất lượng giá đã được giải quyết. Tiến trình OAuth chờ do agent mở đã dừng sau khi phục hồi thành công.

### F12 — Cần siết kiểm tra protocol của bộ so sánh mới

- **Phát hiện khi rà soát:** worker score hiện kiểm dataset/split/source identity/coverage và tính lại metric; vẫn cần kiểm thử âm riêng cho seed/device/aggregation và liên kết revision của forecast SFT với đúng receipt checkpoint.
- **Hướng xử lý:** đối chiếu metadata với task/config đã khóa và training receipt trước khi chấm; baseline deterministic được phép dùng chung giữa các seed, nhưng neural ZS/SFT phải khớp protocol đã định. Thử sửa một trường để chứng minh bị từ chối.
- **Trạng thái 30/10:** đã bổ sung bộ kiểm tra theo task/config/provenance, hash CSV, metadata và checkpoint. Ca sửa seed/device/aggregation/LR/budget/tokenizer/revision/weights bị từ chối; baseline deterministic dùng seed của task riêng. Integration kiểm cả tái dùng score hợp lệ và từ chối artifact bị sửa. Đã kiểm thử phần mềm, chưa có kết quả VN30 mới.

### F13 — Đồng thuận giữa nguồn không thay cho giải quyết bằng chứng

- **Phát hiện:** cổng audit hiện coi tất cả chênh lệch chưa có adjudication là unresolved. Bản tin độc lập đã hỗ trợ một số giá VNDIRECT dù VPS/DNSE khác; đồng thời bảng bản tin ở hai ngày khác lại gần VPS. Yêu cầu mọi nhà cung cấp giống nhau có thể không giải quyết được bằng cách thêm nguồn.
- **Hướng tốt hơn:** lập sổ bằng chứng theo ngày/trường, phân biệt ngày công bố với phiên được mô tả, VN30 cơ sở với hợp đồng tương lai, bảng chỉ số với giá đóng cửa được xác nhận. Nếu thêm cơ chế adjudication, phải khóa hash nguồn và lý do; không có cờ chấp nhận hàng loạt.
- **Trạng thái:** đã có helper trích xuất và hồ sơ từng trường hợp; **chưa triển khai adjudication vào audit**, chưa đổi trạng thái dataset. Có thể cân nhắc chuỗi Close riêng hoặc phạm vi thăm dò chỉ sau khi xác minh đủ phạm vi và sửa protocol công khai, không tự bỏ Open rồi coi là hoàn thành thiết kế gốc.

### F14 — Open bất thường trùng giai đoạn thay hệ thống giao dịch

- **Bằng chứng quan sát:** chuỗi 71 phiên Open bằng Close trước bắt đầu ngày 05/05/2025, cũng là ngày KRX vận hành. Trong đoạn này VNDIRECT có 71/71 trường hợp, VPS 0/71, DNSE 5/71.
- **Hướng điều tra:** truy vết định nghĩa Open và cách dựng nến của từng nhà cung cấp, kiểm thông báo chuyển hệ thống, kiểm mốc kết thúc 11/08 và trở lại bình thường 12/08.
- **Giới hạn:** trùng thời điểm chỉ là giả thuyết điều tra, chưa chứng minh nguyên nhân hoặc chứng minh tất cả giá Open sai. Không sửa Open thành nguồn khác dựa trên giả thuyết này.

## 4. Việc tiếp theo theo thứ tự ưu tiên

### Điều chỉnh thực thi — huấn luyện thăm dò song song với xác minh nguồn

- **Flaw F15:** cổng chính chặn mọi huấn luyện, kể cả thăm dò, trong lúc chờ giải thích khác biệt nhà cung cấp. Điều này chưa thực hiện nhánh thăm dò đã có trong kế hoạch và làm chậm benchmark trên PC.
- **Cách xử lý:** giữ nguyên cổng accepted cho bằng chứng chính; thêm manifest `usage: exploratory_only`, opt-in rõ ở trainer, receipt/checkpoint/forecast có scope, và bộ so sánh chính từ chối scope này. Chỉ chạy khi integrity/replay/flags đạt, không có giá sửa hoặc ngày mẫu thiếu nguồn đối chiếu. Dataset vẫn unverified.
- **Chi phí và tính công bằng:** chạy một epoch + 32 origin validation/model để benchmark, rồi SFT năm epoch seed 42 trên snapshot gốc trong output riêng. Không xem test để chọn cấu hình; không dùng nhánh này để đánh dấu Q1–Q4 hoàn thành. Không tự chuyển checkpoint sang main. Đồng hồ giữ deadline 24 giờ gốc.
- **Điểm cần giữ:** thăm dò không thay thế mục tiêu chính. Tiếp tục kiểm toán và calendar; khi dữ liệu được xác minh mới xem xét khả năng dùng lại bằng kiểm tra protocol đầy đủ hoặc chạy lại. Nếu dữ liệu đổi, checkpoint thăm dò không được gọi là checkpoint của dữ liệu mới.
- **Kiểm chứng hiện tại:** 46 unit/integration tests đạt, một native GPU opt-in đã chạy riêng trước đó. Benchmark bốn model đủ một epoch/32 origin và 12 SFT năm epoch (seed 42/43/44) đã xong; checksum và đủ năm dòng history đã xác minh. Không có score test chính từ nhánh này. Chronos chọn epoch 0 theo validation ở cả ba seed; Kronos chọn epoch 5. Đây là lựa chọn theo native loss, chưa chứng minh MAE/RMSE giá tốt hơn.

1. F12 đã được xử lý bằng kiểm thử âm và integration. Native GPU resume mini đã đạt; tiếp tục điều tra bằng chứng giá/calendar và chỉ mở nghiên cứu khi đủ căn cứ.
2. Đọc audit chính và lập bằng chứng giải quyết các ngày giá lệch; đối chiếu công bố truy vết được, không chấp nhận chỉ vì nhiều nhà cung cấp đồng ý.
3. Hoàn tất lịch phiên độc lập cho giai đoạn dataset. Không dựng calendar từ chính bảng giá đang kiểm toán.
4. Chỉ khi đủ căn cứ mới khóa dataset cho main; nếu cần hiệu chỉnh, tạo bản riêng, lưu thay đổi và nguồn. Không ghép giá từng ô hoặc cập nhật đến hiện tại ngoài phạm vi đã chọn.
5. Khi đầu vào đạt: benchmark một epoch và 32 origin/model; main ba seed trước, Q3 sau, Q2/folds tiếp theo, chừa thời gian tổng hợp báo cáo.
6. Nếu không đủ dữ liệu hoặc thời gian: bàn giao báo cáo incomplete, danh sách công việc và lý do; không dùng kết quả cũ/giả để lấp.

Mốc budget lấy từ `state.json`. Việc chỉnh Markdown không reset hay thay đổi budget. Không tạo lại state hoặc âm thầm cấp thêm 24 giờ.

## 5. Cập nhật kế hoạch khi phát hiện hướng tốt hơn

### F16 — Hậu kiểm và báo cáo chưa phản ánh kết quả mới

- **Xử lý:** `experiments/finalize_pc_report.py` tách khỏi frozen core; không cần GPU lại. Kiểm input hashes, chọn baseline/random LR/epoch 0, tính lại CI/regime/period trực tiếp từ forecast/SQLite, xuất bảng/hình/nguồn và ma trận nghiệm thu.
- **Bằng chứng:** numerical verifier vẫn đạt 88 nhóm/182 forecast/2.160 metric, CSV không đổi; kiểm thống kê 378 CI/1.782 subgroup rows khớp. Report mới tách best-trained/selected, giữ báo cáo lịch sử và chuyển README sang báo cáo PC.
- **Giới hạn:** 1.230 sai khác OHLC vẫn chưa phân xử đầy đủ; sổ bằng chứng chỉ bổ sung hỗ trợ từng trường hợp, không mở audit gate. Source catalog có raw hash/URL; raw công bố local cần được giữ để tái kiểm byte.
- **Nghiệm thu phần báo cáo:** full suite 64 ca đạt, skipped=1; hash các output khớp, local links không hỏng, đã xem hình main/ablation/hai learning curves. Kiểm ba orchestrator frozen cùng core; report_sources.json khóa đầu vào/đầu ra. Giá gốc vẫn không đổi. Giả thuyết High/Low bao gồm Close trước chỉ khớp 24/575 sai khác, đã ghi rõ không dùng để hiệu chỉnh đồng loạt.

### F17 — Đường dẫn host và newline làm báo cáo khó kiểm lại

- **Xử lý:** chỉ trong post-run reader, ánh xạ absolute receipt theo đúng tên repository sang root hiện tại, từ chối đường dẫn không nhận diện hoặc traversal. Không sửa các receipt forecast đã khóa. Giữ LF cho hai postprocessor và bytes của report sinh tự động bằng attributes.
- **Kiểm chứng:** kiểm thử Windows/Linux path, traversal; numerical receipt cũ được archive khi thay verifier; metrics hash không đổi. Các source Python core vẫn đúng normalized hash đã khóa.
- **Không khái quát:** chưa chạy toàn bộ pipeline huấn luyện trên Linux; đây là tương thích đọc lại artifact, không phải chứng nhận mọi environment.

Mỗi thay đổi hướng làm cần ghi trong `AGENT_LOG.md`: flaw/bằng chứng, lựa chọn mới, lợi ích dự kiến, tác động tới tính công bằng/tái lập/chi phí, kiểm thử thực tế và trạng thái. Ghi ngắn gọn lý do kỹ thuật có thể kiểm chứng; không biến giả thuyết thành kết quả.

Các tối ưu đang để xem xét, **chưa được tuyên bố đã làm**:

- Dùng trực tiếp checkpoint thắng vòng random-LR thay vì train lại cùng cấu hình/seed, sau khi có kiểm thử identity và tính tương đương. Hiện worker chọn LR rồi chạy job train riêng.
- Đánh giá batching inference chỉ khi giữ được seed/origin và phép lấy point forecast. Không đổi thứ tự RNG để tăng tốc rồi gọi là replay tương đương.
- Tối ưu thêm phạm vi chạy chỉ theo ngân sách đã chốt và validation, không theo điểm test.

## 6. Thực thi không cần agent theo dõi trong 3 giờ

**Trạng thái mới nhất (30/10/2026 21:17 +07):** hàng đợi đã kết thúc 18:22:28 +07; 11/11 baseline jobs, 48/48 neural forecasts, chấm đủ ba seed, 36/36 Q3 comparisons, 3/3 ablation seed và 2/2 folds. Đối chiếu state/events và process thật: không còn worker sống, không cần restart. Các dòng đang chạy/xếp hàng bên dưới là lịch sử. Chưa coi Q1–Q4 chính hoàn thành: dữ liệu còn unverified, cần kiểm định trực tiếp forecast/nhãn và dựng báo cáo nghiên cứu đầy đủ.

**Bổ sung kiểm định sau khi người dùng quay lại:** verifier độc lập đã tính lại trực tiếp 2.160 dòng metric của 88 nhóm score từ 182 forecast CSV và SQLite; đủ path/ngày/split/finite, MAE/RMSE/Naive delta đều khớp. 85 output receipts và 90 cặp training/selection khớp bytes checkpoint. Xem `review/numerical_validation.json` và `review/STATUS.md`; chưa thay thế kiểm định bootstrap/selection hoặc chất lượng giá. Người dùng đã quay lại với quota đầy, không pause theo yêu cầu cũ; goal tự động đã được xóa.

- Supervisor chạy độc lập qua Windows Task Scheduler, task `VN30-PC-Supervisor-20261030`, không có trigger định kỳ; tự thoát khi hết hàng đợi. API chống sleep được nhả lúc thoát.
- Auto Git đã bỏ qua vì index đang có staged changes; hoàn tất checkpoint thủ công khi bàn giao. Đã thêm ignore PID lock để tránh đưa lock vào commit. Không có checkpoint/optimizer weights được push.
- Không có lịch tự gọi agent đã tạo thành công. Lần thử cấu hình hai lượt bị bộ duyệt từ chối do vượt yêu cầu một lần sau ba giờ; giữ pause theo yêu cầu, người dùng tiếp tục chat khi quay lại.
- Bước tiếp tục: kiểm đủ forecast/hash/origin/checkpoint receipts, tính lại MAE/RMSE trực tiếp từ forecast và SQLite, kiểm folds/learning/ablation, tiếp tục adjudication nguồn giá rồi tổng hợp báo cáo với giới hạn rõ ràng. Không chạy lại để đổi kết quả sau khi đã xem test.

- Main đã có baseline đủ validation/test; 48 forecast neural đang chạy. Chấm tự động khi đủ mọi file, không giảm seed hoặc origin. Bảng seed 42 chỉ là bản tạm 1/3.
- Q3 đã xếp hàng GPU, sau main; giữ 500/1.000/full, pretrained/random, 42/43/44. Nhánh candidate mới dùng trực tiếp checkpoint LR thắng validation và tái dùng full-budget SFT PC đã khớp protocol. Worker primary cũ chưa đổi tối ưu này.
- Q2/Q4 đã xếp sau Q3: ba ablation seed rồi hai fold, bốn neural model, seed 42; CI block 20, 2.000 bootstrap như protocol. Chưa được đánh dấu hoàn thành trước khi worker thực sự chạy và output được kiểm.
- Supervisor cục bộ tiếp tục kể cả khi agent tạm dừng, kiểm process thật, giữ GPU tuần tự, checkpoint/report tự động, commit/push artifact theo mốc. Không đổi precision/LR/seed/mẫu để vượt lỗi; không tự nhận dữ liệu accepted.
- Kiểm thử: **58 tests đạt, skipped=1** (native GPU opt-in đã chạy riêng trước đó); có kiểm thử tiến trình dùng một lần lỗi rồi resume giữ checkpoint. Supervisor kiểm nhận diện worker chính xác và bảo toàn lock của process sống.
- Agent được người dùng yêu cầu tạm dừng theo dõi 3 giờ sau bàn giao, có hẹn kiểm tra lại sau cửa sổ đó. Dữ liệu, kết luận chính và các đầu ra chưa đủ vẫn giữ trạng thái chưa hoàn thành.

## 7. Dashboard phụ — hoàn tất 30/10/2026

- Kế hoạch riêng: DASHBOARD_PLAN.md. Không thuộc tiêu chí chấp nhận dữ liệu hay ngân sách nghiên cứu 24 giờ.
- Đã triển khai frontend đúng preset shadcn b3DpibPrn6, dark/VI mặc định và hai toggle, sample VN30/chọn lịch sử; FastAPI inference thật mini/small/base SFT, một model/job, CPU fallback, bảng/CSV/đối chiếu actual riêng.
- Ba model đã public ở neikhn/kronos-{mini,small,base}-vn30-sft; registry lưu revision/hash. Tải lại ẩn danh và chạy offline cả ba đạt.
- Sáu tests, native GPU ba model/CPU mini, Chrome E2E bốn tổ hợp theme-language/mobile và portable ZIP offline đạt. Receipts: demo/checks/. Người dùng bỏ benchmark laptop; không để đó thành việc bắt buộc còn thiếu.
- Gói bàn giao local: demo/bundle/VN30-Inference-Studio.zip, 518.705.873 bytes; SHA256 075023c229fe6c9c353c763f66376797cf2dec166bd143145625cc7f30d21295. ZIP/weights/env/cache được Git bỏ qua; code/docs/receipts/screenshot được lưu nhánh hiện tại, model weights trên HF.
- Điểm tiếp tục: dashboard v1 đã xong, không chạy lại training hoặc publish lại model trùng. Dùng Start-Dashboard.cmd để mở; hướng dẫn ở demo/README.md. Nghiên cứu chính vẫn chưa hoàn thiện vì nguồn dữ liệu unverified.

## 8. Slide nghiên cứu theo Paper & Ink — chờ duyệt dàn ý

- Yêu cầu mới 31/10/2026: dùng paper-ink-slides.zip, viết file Markdown cấu trúc trước để người dùng duyệt, tối đa 20 slide kể cả bìa/kết luận/phụ lục.
- Đã đọc mẫu thiết kế và khung HTML trong ZIP, không cài vào hệ thống, không chạy mã trong ZIP. Đã đọc báo cáo PC, audit, CSV và state thực tế; nghiên cứu chính vẫn incomplete (5 complete/283 blocked), dataset unverified.
- Đã hoàn thành docs/slides/slide-outline.md với 20 slide. Mỗi slide có vai trò, nội dung, visualize, nguồn và REVIEW. Nội dung gồm thiết kế/Kronos, dữ liệu/audit, Q1–Q4, chi phí, kiểm định, giới hạn/kết luận; dashboard giữ riêng.
- Kiểm tra: số thứ tự 01–20 và 20 REVIEW đúng; 20 nguồn local tồn tại; 15 giá trị MAE Close chính khớp CSV làm tròn ba chữ số. Chưa tạo HTML/PPTX/PDF hoặc chạy lại thí nghiệm.
- Điểm tiếp tục: chờ người dùng duyệt dàn ý. Khi nhận góp ý, đọc lại file mới nhất và REVIEW, giữ chỉnh sửa trực tiếp, sau đó dựng bằng khung Paper & Ink theo phạm vi được duyệt. Không tự lấy quy trình 5-slide mặc định trong template để vượt yêu cầu dừng ở Markdown.

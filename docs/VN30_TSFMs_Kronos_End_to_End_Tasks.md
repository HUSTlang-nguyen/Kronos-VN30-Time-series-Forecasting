# VN30 — checklist thử nghiệm dự báo

Mục tiêu: chạy Kronos-small, Chronos-2-small và baseline **trực tiếp trên snapshot VN30 hiện có**, cùng thời điểm dự báo và cùng phiên đích. Đánh giá Close và thêm Open phiên kế tiếp. Đây là checklist thử nghiệm model, không dùng để viết bài báo.

**Trạng thái:** `[x]` đã có và kiểm tra được; `[ ]` chưa hoàn thành. Đánh dấu xong sau khi có code, lệnh chạy và kết quả kiểm tra tương ứng. Đường dẫn file trong các task chưa hoàn thành là đầu ra dự kiến, không phải file đã tồn tại.

**Dataset cố định cho vòng thử này:** `data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite` (DVC), SHA256 `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`. Snapshot VNDIRECT chứa **2.271 hàng từ 24/08/2017 đến 01/10/2026**, gồm Open/High/Low/Close theo điểm chỉ số và cờ chất lượng. Receipt ghi 0 ngày trùng, 0 giá trị số/OHLC không hợp lệ, **1 hàng `outside_request`**. Giữ cả 2.271 hàng trong dữ liệu mặc định; không tự loại hàng cờ này hoặc thay giá. Mọi score của vòng này phản ánh **giá Open/Close do VNDIRECT cung cấp**, cùng giới hạn về cách dựng Open. Không cần lấy thêm nguồn hoặc giải quyết chênh lệch với VPS/DNSE trước khi chạy model. Thay dataset là một vòng thử khác, có hash và kết quả riêng.

## Hiện trạng

- [x] **T001 — Môi trường model.** `pyproject.toml`/`uv.lock` giữ PyTorch CUDA; `scripts/bootstrap_kronos.py` lấy đúng revision Kronos. `scripts/verify_checkpoint_provenance.py` kiểm tra hash weights; `scripts/smoke_models.py` đã chạy Kronos-small và Chronos-2-small với OHLC giả trên CUDA. Lệnh: `uv sync --frozen`, `uv run --no-sync python scripts/bootstrap_kronos.py`, `uv run --no-sync python scripts/smoke_models.py --model all --device cuda:0`.
- [x] **T002 — Dữ liệu chia sẻ có phiên bản.** DVC giữ raw, SQLite và ZIP trên Drive của nhóm; Git giữ pointers và checksum. `scripts/check_shared_data.py` xác minh snapshot SQLite/ZIP hiện tại. Hướng dẫn tải và cấu hình OAuth ở [README](../README.md#tải-dữ-liệu-bằng-dvc). Lệnh kiểm tra vòng này: `uv run --no-sync python scripts/check_shared_data.py`.

## Dữ liệu đầu vào

- [x] **T003 — Khóa input cho vòng thử.** Dùng duy nhất SQLite và SHA256 nêu trên; `configs/primary_data_source.yaml` và `data/manifests/vndirect_sqlite_snapshot.json` ghi nguồn, mốc thời gian, receipt. Giữ nguyên giá/cờ và toàn bộ hàng theo thứ tự ngày. Có 71 phiên Open bằng Close trước đó được ghi nhận trong nguồn; xem đây là giới hạn khi giải thích metric Open/gap, chưa sửa hoặc tự xác nhận giá mở cửa của sàn.
- [x] **T004 — Loader VN30.** Viết loader đọc **đúng SQLite đã khóa** ở chế độ chỉ đọc và gọi `scripts/check_shared_data.py` hoặc kiểm SHA256/receipt tương đương trước khi dùng. Xuất OHLC, ngày phiên và bốn cờ chất lượng; kiểm 2.271 hàng, một ngày mỗi hàng, ngày tăng dần, số dương và quan hệ OHLC. Mặc định giữ hàng `outside_request`; nếu làm phân tích loại hàng này, ghi là một nhánh sensitivity riêng. Lỗi rõ ràng khi file thiếu hoặc hash sai. Loader không phụ thuộc đường dẫn cá nhân.
  - Kiểm tra local 22/10/2026: `src/vn30_forecast.py:load`; kiểm SHA256/receipt, 2.271 hàng và bốn cờ; thử sửa 1 byte SQLite cho thấy loader từ chối.
- [x] **T005 — Chia tập theo thời gian.** Từ 2.271 hàng của T004, chia theo thứ tự phiên: **70% train, 15% validation, 15% test** (phần dư cuối thuộc test); xuất chính xác ngày biên và số hàng vào manifest. Origin dự báo là sau Close phiên `t`; context 128 phiên và path 20 phiên, đánh giá h=1/5/20. Mọi model dùng cùng danh sách origin/target dates; nhãn của mỗi tập nằm trọn trong tập đó, context được phép nhìn lại các phiên đã quan sát. Fit scaler/ARIMA/ETS bằng quá khứ, chọn tham số chỉ bằng validation; không đưa OHLC thật tương lai vào input. Kiểm thử ranh giới và số origin trước khi chạy model.
  - Kiểm tra local 22/10/2026: `artifacts/local/vn30-experiment/split.json`; train 1.589 phiên, validation 340, test 342; 323 origin test có toàn bộ 20 nhãn trong test.

## Model và dự báo

- [x] **T006 — Baseline đơn giản.** Với thông tin sau Close phiên `t`, dự báo `Close_{t+1}=Close_t` và `Open_{t+1}=Close_t`; mở rộng thành path 20 phiên khi cần. Viết chung interface dự báo với các model bên dưới. Đây là mốc tối thiểu để đánh giá lợi ích của Kronos/Chronos.
  - Kiểm tra local 22/10/2026: `artifacts/local/vn30-experiment/naive.csv`; đủ 6.460 hàng dự báo (323 origin × 20 bước).
- [x] **T007 — Adapter Kronos và Chronos.** Nạp checkpoint/revision đã ghi trong `data/manifests/checkpoint_provenance.yaml`. Cùng nhận context OHLC và các origin từ T005. Kronos trả path OHLC; Chronos-2 trả các kênh Open/High/Low/Close tương ứng. Xử lý thiếu volume/amount của chỉ số VN30 theo quy tắc đã ghi trong adapter; không tạo volume giả. Lưu seed, số mẫu, thiết bị và cách lấy point forecast. Kết quả chỉ hợp lệ khi số bước, ngày đích và giá trị hữu hạn khớp.
  - Kiểm tra local 22/10/2026: `artifacts/local/vn30-experiment/chronos2.csv` và `kronos.csv`; cả hai chạy CUDA đủ 323 origin. Lặp lại 2 origin Kronos cùng seed cho CSV giống byte.
- [x] **T008 — Baseline bổ sung.** Thêm ARIMA/ETS hoặc Ridge/DLinear khi muốn so sánh rộng hơn. Mỗi model dùng cùng tập origin và dữ liệu quá khứ; ghi rõ kênh đầu vào, cách fit/refit và chi phí chạy. Baseline bổ sung không chặn việc hoàn thành vòng thử nghiệm đầu tiên T006–T007.
  - Kiểm tra local 22/10/2026: `artifacts/local/vn30-experiment/ridge.csv`; Ridge fit trên train, đủ 323 origin test.
- [x] **T009 — Runner tái lập.** Tạo CLI nhận `--model`, `--device`, `--seed`, `--output` và split/origin manifest T005; đường dẫn dataset mặc định là SQLite đã khóa. Nếu cho phép `--data`, chỉ nhận file có cùng SHA256 trong vòng thử này. Dự báo từ một origin hoặc chạy walk-forward. Lưu forecast **trước khi ghép nhãn thật**, cùng ngày tạo dự báo, ngày đích, model, revision, hash dữ liệu và cấu hình. Chạy lại cùng cấu hình cho cùng danh sách origin; không ghi đè output cũ âm thầm.
  - Kiểm tra local 22/10/2026: `scripts/forecast_vn30.py`; `prepare`, `run`, `score`, `report` chạy thành công. Bốn forecast CSV được lưu trước bước score và khớp cùng origin.

## Đánh giá và sử dụng kết quả

- [x] **T010 — Metrics.** Ghép nhãn thật theo `target_date` sau khi forecast đã lưu. Tính MAE/RMSE cho Close và Open theo từng horizon; so với T006 bằng cùng mẫu. Với h=1, báo cáo thêm gap `log(Open_{t+1}/Close_t)` và biến động trong phiên `log(Close_{t+1}/Open_{t+1})` khi Open hợp lệ. Nếu dùng directional accuracy, quy định trước cách xử lý return bằng 0. Báo số mẫu và cả lỗi dự báo, không loại riêng những origin model làm kém.
  - Kiểm tra local 22/10/2026: `artifacts/local/vn30-experiment/evaluation/scores.csv`, `details.csv`; đủ MAE/RMSE Open/Close h=1/5/20 và gap/intraday h=1 trên 323 origin.
- [x] **T011 — Chẩn đoán dữ liệu và thời điểm dự báo.** Tách tín hiệu được tạo sau Close `t` khỏi tín hiệu chỉ có sau Open `t+1`; không giả định khớp lệnh tại giá đã dùng để tạo tín hiệu. Báo riêng lỗi tại 71 phiên Open bằng Close trước đó, phiên `outside_request` nếu nằm trong tập đánh giá, và những ngày biến động mạnh. Giữ nguyên nhãn của vòng thử; mọi nhánh loại/lọc đều có score riêng. VN30 là chỉ số, vì vậy không suy ra lợi nhuận giao dịch trực tiếp từ lỗi dự báo giá chỉ số.
  - Kiểm tra local 22/10/2026: `open_pattern_diagnostic.csv`, `volatility_diagnostic.csv`, `outside_request_diagnostic.csv`; 59 phiên thuộc giai đoạn Open đặc biệt trong test; một hàng outside_request chỉ xuất hiện tại h=20.
- [x] **T012 — Bảng kết quả và demo.** Xuất bảng model × target × horizon gồm MAE, RMSE, số origin và chênh lệch với baseline; vài đồ thị actual/forecast, lỗi theo thời gian và gap. Ghi rõ **file SQLite, SHA256 cố định**, split, revision model, seed, CUDA/CPU và lệnh tái chạy. Đặt nhãn kết quả là **thử nghiệm trên snapshot VNDIRECT 01/10/2026**; không trình bày đó là dự báo đã kiểm chứng trên dữ liệu mới hơn hoặc giá Open chính thức của sàn.
  - Kiểm tra local 22/10/2026: `artifacts/local/vn30-experiment/evaluation/summary.md` và bốn đồ thị; kèm hash, split, revision, seed và lệnh tái chạy trong README.
- [x] **T013 — Đánh giá đầy đủ theo train/validation/test.** Chạy cùng bốn model trên mọi origin có đủ context 128 phiên và toàn bộ path 20 phiên nằm trong tập nhãn. Chấm điểm, vẽ chẩn đoán cho từng tập và tổng hợp kết quả. Train: 1.589 hàng/1.442 origin; validation: 340/321; test: 342/323. Ridge fit trên train, nên điểm train là in-sample; Kronos/Chronos là zero-shot trên VN30, không gọi là fine-tune. Kết quả test cũ được chấm lại trên cùng manifest/hash thay vì chạy lại inference.
  - Kiểm tra local 23/10/2026: `artifacts/local/vn30-full-splits-20261023/comparison/summary.md`, `scores_all_splits.csv`, các thư mục `evaluation-{train,validation,test}/`. Lệnh tái chạy đủ ba tập ở [README](../README.md#chạy-dự-báo-vn30).

## Trình tự và cách đối chiếu

T001–T013 đã có bản chạy end-to-end trên snapshot cố định. Thứ tự để tái chạy: T004 → T005 → (T006, T007, T008) → T009 → T010 → T011 → T012 → T013. Lệnh cụ thể ở [README](../README.md#chạy-dự-báo-vn30); kết quả local nằm trong `artifacts/local/` và không được Git theo dõi.

**Kết quả tham chiếu h=1 trên 323 origin test (MAE, điểm chỉ số):** Naive Open 5,96 / Close 17,72; Kronos Open 10,64 / Close 19,75; Chronos-2 Open 21,04 / Close 19,99; Ridge Open 22,02 / Close 28,80. Đây là phép thử trên snapshot VNDIRECT cũ; không suy ra lợi nhuận giao dịch hay kết quả trên phiên mới.

Mỗi collaborator nhận một task/nhánh, ghi lệnh chạy và file đầu ra trong PR. Khi đánh dấu `[x]`, ghi đường dẫn artifact và lệnh kiểm tra; nếu đã publish thì thêm commit hoặc PR. Cùng checkout pointer/receipt của dataset đã khóa; không thay SQLite giữa các model hoặc âm thầm cập nhật dữ liệu trong vòng này. Không commit raw/SQLite/ZIP, weights hoặc credential. CI hiện chỉ kiểm tra cú pháp và công cụ dữ liệu; chạy model/CUDA cần xác minh trên máy có GPU.

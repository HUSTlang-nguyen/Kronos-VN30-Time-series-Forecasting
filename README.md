# VN30 Forecasting

Thử nghiệm dự báo VN30 bằng **Kronos mini/small/base**, **Chronos-2-small**, Naive, Ridge, ARIMA và ETS. Kết quả cũ chỉ gồm các model đã được ghi trong báo cáo lịch sử; có runner không đồng nghĩa mọi thí nghiệm mới đã chạy xong.

**Làm lại trên PC:** xem [quy trình và trạng thái kiểm toán dữ liệu](docs/PC_Rerun.md). Lượt mới tách hoàn toàn kết quả khỏi môi trường cũ, có giới hạn 24 giờ và giữ cổng kiểm toán cho bằng chứng chính. Đã hoàn tất [12 lượt SFT thăm dò](artifacts/local/pc-exploratory-20261030/report.md) trên PC (bốn model × ba seed, năm epoch); dataset vẫn chưa được chấp nhận, chưa có kết luận Q1–Q4 mới.

Repo có loader cho snapshot VN30 cố định, runner dự báo và đánh giá Open/Close trên cùng các phiên. Context là 128 phiên, path dự báo 20 phiên; score tại h=1/5/20. Dữ liệu VNDIRECT là một snapshot lịch sử, vì vậy kết quả chỉ áp dụng cho snapshot này.

Các bước triển khai và điều kiện hoàn thành nằm trong [checklist end-to-end](docs/VN30_TSFMs_Kronos_End_to_End_Tasks.md).

[Báo cáo kết quả Q1–Q4](docs/VN30_Experimental_Results_Q1_Q4.md) tổng hợp bằng chứng về zero-shot, K-line representation, fine-tuning với dữ liệu hiện có và độ ổn định theo horizon/volatility.

## Cài môi trường CUDA

Cần Python 3.11, Git, uv và NVIDIA GPU/driver hỗ trợ CUDA 13.0. Giữ phiên bản PyTorch đã khóa, không cài đè bằng bản CPU.

```sh
uv sync --frozen
uv run --no-sync python scripts/bootstrap_kronos.py
uv run --no-sync python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
uv run --no-sync python scripts/smoke_models.py --model all --device cuda:0
```

Smoke dùng dữ liệu giả, chỉ kiểm tra model chạy được. Có thể chọn `--model kronos` hoặc `--model chronos2`; dùng `--device cpu` khi cần. `scripts/smoke_pc_models.py` kiểm tra đủ ba bản Kronos và Chronos trên GPU. Weights pretrained được tải và cache khi chạy lần đầu; artifact kiểm thử được ghi rõ khác với kết quả VN30.

Kiểm tra hash checkpoint nếu cần:

```sh
uv run --no-sync python scripts/verify_checkpoint_provenance.py
```

## Tải dữ liệu bằng DVC

Git giữ pointers/checksum; dữ liệu nằm trên Google Drive của nhóm. Chủ Drive cấp **Viewer** để tải, **Editor** để upload. Nhóm dùng chung một Desktop OAuth client JSON gửi riêng ngoài repo; mỗi collaborator đăng nhập tài khoản Google của mình. Thêm email vào Test users nếu OAuth app đang ở Testing. Không chia sẻ token đăng nhập hoặc commit credentials.

```sh
uv tool install --with-requirements requirements/dvc.txt dvc
```

Thay đường dẫn JSON bằng file trên máy bạn:

```sh
uv run --no-sync python scripts/configure_dvc_drive.py --client-json "C:/Users/<user>/Downloads/dvc-client.json"
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite.dvc
uv run --no-sync python scripts/check_shared_data.py
```

Helper ghi client ID/secret vào `.dvc/config.local` đã được gitignore. Khi DVC yêu cầu, hoàn tất đăng nhập Google bằng tài khoản có quyền thư mục Drive.

SQLite hiện có **2.271 hàng, 24/08/2017–01/10/2026**, nguồn VNDIRECT. Snapshot là phiên bản cố định để cả nhóm dùng cùng dữ liệu; không có nghĩa đã làm sạch. Các cờ `duplicate_date`, `invalid_numeric`, `invalid_ohlc`, `outside_request` vẫn được giữ. Đặc biệt, từng ghi nhận 71 phiên Open bằng Close phiên trước trong 05/05–11/08/2025; cần hiểu cách nguồn định nghĩa Open trước khi đánh giá gap. Dữ liệu chưa được cập nhật tới hôm nay.

Đọc SQLite ở chế độ chỉ đọc; ghi dữ liệu xử lý vào `data/processed/`:

```python
from pathlib import Path
import sqlite3
import pandas as pd

path = Path("data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite")
with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
    candles = pd.read_sql_query(
        "SELECT date, open, high, low, close, duplicate_date, invalid_numeric, "
        "invalid_ohlc, outside_request FROM candles ORDER BY date, row_id",
        connection,
    )
```

Raw là phản hồi gốc để kiểm tra hoặc xử lý lại; ZIP là bản đóng gói kèm CSV và nguồn gốc:

```sh
dvc pull data/raw.dvc
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.zip.dvc
uv run --no-sync python scripts/check_shared_data.py --format zip
```

`scripts/share_vndirect_snapshot.py` và `scripts/share_vndirect_sqlite.py` giữ khả năng đóng gói snapshot cũ. `configs/data_source_acceptance.yaml` và `scripts/validate_vn30_sources.py` được giữ nguyên byte để khớp hash của bản dữ liệu đó; các trường gate trong metadata chỉ là thông tin lịch sử.

Sau khi cập nhật dữ liệu, kiểm tra nội dung rồi chạy `dvc add <đường-dẫn-dữ-liệu>` và `dvc push`. Commit các pointer `.dvc`, checksum và receipts tương ứng cùng code/config. Không commit raw, SQLite/ZIP, weights hoặc credentials. Hash công khai trong Git không cấp quyền truy cập Drive.

## Chạy dự báo VN30

Sau khi tải SQLite và cài môi trường CUDA, chạy từng model trên cùng `split.json` (Windows PowerShell hoặc shell):

```sh
uv run --no-sync python scripts/forecast_vn30.py prepare --output artifacts/local/vn30-run/split.json
uv run --no-sync python scripts/forecast_vn30.py run --manifest artifacts/local/vn30-run/split.json --model naive --device cpu --output artifacts/local/vn30-run/naive.csv
uv run --no-sync python scripts/forecast_vn30.py run --manifest artifacts/local/vn30-run/split.json --model ridge --device cpu --output artifacts/local/vn30-run/ridge.csv
uv run --no-sync python scripts/forecast_vn30.py run --manifest artifacts/local/vn30-run/split.json --model chronos2 --device cuda:0 --output artifacts/local/vn30-run/chronos2.csv
uv run --no-sync python scripts/forecast_vn30.py run --manifest artifacts/local/vn30-run/split.json --model kronos --device cuda:0 --output artifacts/local/vn30-run/kronos.csv
uv run --no-sync python scripts/forecast_vn30.py score --manifest artifacts/local/vn30-run/split.json --forecasts artifacts/local/vn30-run/naive.csv artifacts/local/vn30-run/ridge.csv artifacts/local/vn30-run/chronos2.csv artifacts/local/vn30-run/kronos.csv --output artifacts/local/vn30-run/evaluation
uv run --no-sync python scripts/forecast_vn30.py report --scores artifacts/local/vn30-run/evaluation
```

`run --limit 2` chỉ là kiểm tra nhanh; không dùng score đó thay kết quả toàn tập. Runner từ chối ghi đè output cũ: dùng thư mục chạy mới cho mỗi lần thử. `prepare` tạo split theo thời gian 70/15/15, giữ đủ 2.271 hàng và lưu hash dataset; mỗi model dùng cùng 323 origin test. Dự báo được lưu trước khi ghép nhãn thật trong `score`. `ridge` chỉ fit trên train; Kronos dùng trung bình 3 path. Chronos trả **13 quantile**, lấy trung bình đều các quantile để giữ quy tắc so sánh cũ; đây không phải 13 mẫu ngẫu nhiên. Metadata cũ ghi `sample_mean` cho Chronos chưa chính xác; metadata mới ghi `quantile_mean`, không đổi phép tính giá dự báo. Kronos nhận lịch phiên đích thực tế dưới dạng thông tin ngày; đây là giới hạn cần nhớ khi diễn giải kết quả. `artifacts/local/` được lưu trong Git; trọng số model dùng Git LFS.

Để chạy **đủ train/validation/test** bằng PowerShell, dùng một thư mục output mới:

```powershell
$base = "artifacts/local/vn30-full-splits"
uv run --no-sync python scripts/forecast_vn30.py prepare --output "$base/split.json"
foreach ($split in @("train", "validation", "test")) {
  foreach ($model in @("naive", "ridge", "chronos2", "kronos")) {
    $device = if ($model -in @("chronos2", "kronos")) { "cuda:0" } else { "cpu" }
    uv run --no-sync python scripts/forecast_vn30.py run --manifest "$base/split.json" --model $model --split $split --device $device --output "$base/$model-$split.csv"
    if ($LASTEXITCODE -ne 0) { throw "Forecast failed: $split/$model" }
  }
  uv run --no-sync python scripts/forecast_vn30.py score --manifest "$base/split.json" --forecasts "$base/naive-$split.csv" "$base/ridge-$split.csv" "$base/chronos2-$split.csv" "$base/kronos-$split.csv" --output "$base/evaluation-$split"
  if ($LASTEXITCODE -ne 0) { throw "Scoring failed: $split" }
  uv run --no-sync python scripts/forecast_vn30.py report --scores "$base/evaluation-$split"
}
uv run --no-sync python scripts/compare_vn30_splits.py --manifest "$base/split.json" --train "$base/evaluation-train" --validation "$base/evaluation-validation" --test "$base/evaluation-test" --output "$base/comparison"
```

Train có 1.589 phiên và 1.442 origin đủ context/path; validation có 340 phiên/321 origin; test có 342 phiên/323 origin. Cả 2.271 phiên đều thuộc đúng một tập. 128 phiên context được phép nhìn về quá khứ qua ranh giới tập, nhưng toàn bộ 20 nhãn của một origin phải nằm trong tập của nó. Naive không cần fit; Ridge fit trên train nên điểm train là **in-sample**; Chronos/Kronos dùng checkpoint pretrained và chưa fine-tune bằng train VN30. Validation dùng so sánh cấu hình, test là holdout lịch sử. Giai đoạn test này đã được xem trong lần thử trước, nên không còn là holdout hoàn toàn chưa từng xem.

Lần chạy local 23/10/2026 lưu bảng ba tập tại `artifacts/local/vn30-full-splits-20261023/comparison/summary.md` và toàn bộ MAE/RMSE tại `scores_all_splits.csv` cùng thư mục; output được lưu trong Git. Test của lần này được chấm lại từ forecast đã lưu của lần chạy cùng snapshot/hash, không chạy lại inference.

Xem [checklist](docs/VN30_TSFMs_Kronos_End_to_End_Tasks.md) để đối chiếu từng bước. Giá Open trong score là giá từ VNDIRECT; cách nguồn dựng Open ở một số phiên chưa được xác nhận.

## Fine-tune trên VN30

`scripts/finetune_vn30.py` cập nhật toàn bộ trọng số Chronos-2-small hoặc Kronos-small; tokenizer Kronos được giữ cố định. Dùng nguyên split đã khóa, 1.442 cửa sổ train/321 validation, context 128 và 20 nhãn tương lai. Chuẩn hóa chỉ bằng context, mọi cửa sổ train được dùng một lần mỗi epoch. Checkpoint tốt nhất được chọn bằng validation loss trong các epoch đã huấn luyện; có ghi loss pretrained để biết fine-tune có làm validation kém đi hay không. Test không được dùng để cập nhật trọng số hoặc chọn checkpoint.

Mặc định: FP32/CUDA, 5 epoch, learning rate `1e-6`, batch 8 cửa sổ và accumulation 2, AdamW/weight decay `0.01`, seed 42. Chronos tối ưu quantile loss gốc; Kronos tối ưu token cross-entropy trên 20 phiên đích với teacher forcing. `history.csv` ghi train/validation loss; `training.json` giữ epoch chọn, cấu hình, hash tham số trước/sau và SHA256 checkpoint. Runner kiểm hash/checkpoint/split trước khi dự báo.

Teacher-forced validation của Kronos giữ causal mask ở dependency cross-attention; chỉ riêng attention có dropout bằng 0 được đặt cờ cần thiết, các dropout còn lại vẫn ở eval. `scripts/check_finetune_protocol.py` kiểm bằng cách thay token tương lai và xác nhận logits quá khứ không đổi, đồng thời kiểm tra test không đi vào cửa sổ train/validation và chuẩn hóa chỉ dùng context.

Ví dụ PowerShell, dùng thư mục mới cho mỗi lần thử:

```powershell
$base = "artifacts/local/vn30-finetune-new"
uv run --no-sync python scripts/forecast_vn30.py prepare --output "$base/split.json"
uv run --no-sync python scripts/check_finetune_protocol.py --manifest "$base/split.json" --output "$base/protocol_checks.json"
if ($LASTEXITCODE -ne 0) { throw "Fine-tuning protocol check failed" }
foreach ($model in @("chronos2", "kronos")) {
  uv run --no-sync python scripts/finetune_vn30.py --manifest "$base/split.json" --model $model --output "$base/$model"
  if ($LASTEXITCODE -ne 0) { throw "Training failed: $model" }
}
foreach ($split in @("validation", "test")) {
  foreach ($model in @("naive", "ridge", "chronos2", "kronos", "chronos2-ft", "kronos-ft")) {
    $device = if ($model -in @("naive", "ridge")) { "cpu" } else { "cuda:0" }
    $checkpointArgs = @()
    if ($model.EndsWith("-ft")) { $checkpointArgs = @("--checkpoint", "$base/$($model.Replace('-ft',''))") }
    uv run --no-sync python scripts/forecast_vn30.py run --manifest "$base/split.json" --model $model --split $split --device $device --output "$base/$model-$split.csv" @checkpointArgs
    if ($LASTEXITCODE -ne 0) { throw "Forecast failed: $split/$model" }
  }
  uv run --no-sync python scripts/forecast_vn30.py score --manifest "$base/split.json" --forecasts "$base/naive-$split.csv" "$base/ridge-$split.csv" "$base/chronos2-$split.csv" "$base/kronos-$split.csv" "$base/chronos2-ft-$split.csv" "$base/kronos-ft-$split.csv" --output "$base/evaluation-$split"
  if ($LASTEXITCODE -ne 0) { throw "Scoring failed: $split" }
  uv run --no-sync python scripts/forecast_vn30.py report --scores "$base/evaluation-$split"
}
uv run --no-sync python scripts/compare_vn30_finetuning.py --validation "$base/evaluation-validation" --test "$base/evaluation-test" --chronos-checkpoint "$base/chronos2" --kronos-checkpoint "$base/kronos" --output "$base/comparison"
```

Trainer dùng lớp dataset/loss của [Chronos](https://github.com/amazon-science/chronos-forecasting/blob/10afa9ebe016e514f9d7dc1aa873f66af57e116b/src/chronos/chronos2/pipeline.py) và kiến trúc/tokenizer của [Kronos](https://github.com/shiyu-coder/Kronos/tree/67b630e67f6a18c9e9be918d9b4337c960db1e9a/finetune_csv). Vòng này cố định tokenizer, chuẩn hóa bằng context và giới hạn loss vào phần dự báo để bám đúng tác vụ đang đánh giá. Không có thêm dependency ngoài môi trường đã khóa.

Lần chạy 27/10/2026: báo cáo tại `artifacts/local/vn30-finetune-20261027/comparison-final/summary.md`; checkpoint hợp lệ trong `chronos2/` và `kronos-causal/` của cùng thư mục chạy. Fine-tune cải thiện một phần sai số test, nhưng Naive vẫn có MAE thấp nhất ở cả Open/Close h=1/5/20. Xem [bảng kết quả và giới hạn](docs/VN30_TSFMs_Kronos_End_to_End_Tasks.md#fine-tune--kết-quả-test-27102026).

### Tải checkpoint đã fine-tune

Hai checkpoint được lưu trên GitHub bằng Git LFS. Cài [Git LFS](https://git-lfs.com/), rồi chạy trong repo:

```sh
git lfs install
git lfs pull
```

Checkpoint nằm tại `artifacts/local/vn30-finetune-20261027/chronos2/` (~112 MB) và `artifacts/local/vn30-finetune-20261027/kronos-causal/` (~99 MB). Mỗi thư mục có `best/model.safetensors`, config, `training.json` và `history.csv`. Dùng trực tiếp để inference, không cần train lại:

```powershell
uv run --no-sync python scripts/forecast_vn30.py run --manifest artifacts/local/vn30-finetune-20261027/split.json --model kronos-ft --checkpoint artifacts/local/vn30-finetune-20261027/kronos-causal --split test --device cuda:0 --output artifacts/local/kronos-ft-test-rerun.csv
```

Với Chronos, đổi `--model` thành `chronos2-ft` và `--checkpoint` thành `artifacts/local/vn30-finetune-20261027/chronos2`. Cần tải dataset bằng DVC và chuẩn bị môi trường theo hướng dẫn phía trên; tokenizer Kronos pretrained được tải riêng từ Hugging Face khi chạy lần đầu. Manifest split được lưu cùng checkpoint; toàn bộ kết quả đã lưu trong `artifacts/` cũng được theo dõi trong Git. Xem [ghi chú phiên bản kết quả](artifacts/README.md) để phân biệt lần chạy cuối và các lần thử cũ.

## Docker

```sh
docker compose build data
docker compose run --rm data
```

Lệnh mặc định xác minh SQLite đã tải bằng DVC. Container data không cần PyTorch; tải DVC trên host trước. Compose mount thư mục dự án nên output nằm trên máy bạn.

Chạy model bằng GPU cần Docker có hỗ trợ NVIDIA GPU (Windows: Docker Desktop/WSL2):

```sh
docker compose --profile cuda build cuda
docker compose --profile cuda run --rm cuda
docker compose --profile cuda run --rm cuda python scripts/bootstrap_kronos.py
docker compose --profile cuda run --rm cuda python scripts/smoke_models.py --model all --device cuda:0
```

## Cấu trúc

```text
configs/          Cấu hình nguồn và cấu hình gốc để đóng gói dữ liệu
scripts/          Bootstrap, model smoke, dữ liệu và DVC
requirements/     Dependencies data và DVC riêng
data/manifests/   Phiên bản checkpoint và receipts snapshot
data/raw/         Phản hồi gốc, quản lý bằng DVC
data/share/       SQLite/ZIP, pointers và checksum
data/processed/   Dữ liệu xử lý, không commit
artifacts/        Kết quả, receipts và đồ thị theo phiên bản; weights dùng Git LFS
```

Collaborator làm trên branch riêng, mở PR vào `main`; ghi model, phiên bản dữ liệu và lệnh chạy để người khác lặp lại. CI kiểm tra cú pháp, CLI dữ liệu, dependencies và Docker; không chạy GPU hoặc truy cập Drive riêng.

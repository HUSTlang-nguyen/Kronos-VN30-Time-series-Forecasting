# VN30 Time-Series Forecasting

Nghiên cứu dự báo VN30 bằng mô hình thống kê, mô hình nền tảng chuỗi thời gian và Kronos. Benchmark chính so sánh **Kronos-small**, **Chronos-2-small** và các baseline với cùng lịch giao dịch, dữ liệu quan sát và forecast origins.

Repo đang triển khai; chưa có kết quả benchmark chính thức. Script smoke test dùng dữ liệu giả để kiểm tra môi trường.

## Trạng thái và phạm vi

| Thành phần | Trạng thái |
|---|---|
| Phase 0: hợp đồng nghiên cứu, provenance, môi trường CUDA, smoke tests | Đã có bằng chứng kiểm tra |
| Nguồn chính VN30 | VNDIRECT, chọn ngày 05/10/2026 |
| Snapshot cho collaborator | SQLite/ZIP candidate; 2.271 hàng, 24/08/2017–01/10/2026 |
| Data versioning | DVC + Google Drive; đã upload/restore 89 file, SHA256 không đổi; pointers và receipts được version trong Git |
| Audit mới, chưa thay snapshot | 2.272 hàng, 24/08/2017–02/10/2026; 39 trường trên 30 ngày đã kiểm tra |
| Phase 1: chất lượng nguồn, calendar, accepted dataset/splits | Chưa hoàn tất; G1 pending |
| Phase 2–5: framework, baseline, adapters, holdout và thống kê | Chưa triển khai đầy đủ |
| Phase 6–8 | Secondary/optional và bộ báo cáo cuối |

- Asset chính: VN30 price index; OHLC theo điểm chỉ số, ngày theo `Asia/Ho_Chi_Minh`.
- Context chính: 128 phiên; dự báo path 20 phiên, đánh giá h=1/5/20.
- Endpoint chính: Close MAE tại h=1; point forecast của TSFM là median.
- Mandatory models: Naive, ARIMA, ETS, DLinear-C, Ridge-OHLC, Chronos-2-small, Kronos-small.
- Dataset chính dùng phạm vi VNDIRECT đã được xác minh. Capture hiện có chưa đủ giai đoạn replication 2016–2023.
- TSLA/MSTR không thuộc phạm vi triển khai hiện tại.

Snapshot candidate và tests đạt không tự xác nhận G1. Chưa chạy benchmark chính thức trước khi source/calendar/splits được chấp nhận và G4 được freeze. [Checklist end-to-end](docs/VN30_TSFMs_Kronos_End_to_End_Tasks.md) ghi task, phụ thuộc và điều kiện hoàn thành.

Cập nhật kiểm định 05/10/2026: bốn Close được bản tin cùng ngày hỗ trợ theo giá VNDIRECT; 35 O/H/L chưa phân xử. VNDIRECT có 71 phiên liên tiếp Open bằng Close phiên trước (05/05–11/08/2025), cần làm rõ cách dựng nến. Calendar candidate khớp ngày nhưng còn thiếu bằng chứng lịch sử/exception. [Review T010/T012](reports/vndirect_T010_T012_review.md), [bảng đủ 39 sai khác](reports/vndirect_39_discrepancy_review.md).

[Review bốn bài nghiên cứu](reports/vn30_baseline_literature_review.md) đề xuất daily ARIMA cho supporting replication và KTPCA ở nhánh mở rộng. Đây là đề xuất; study v4, E0/T030 và core baseline vẫn giữ nguyên. Local tests hiện có 52 tests pass; CI remote phải đối chiếu đúng commit, không dùng run cũ để chứng nhận thay đổi mới.

## Bắt đầu bằng Docker

Cần Git và Docker có Linux containers/Compose. Chạy từ thư mục gốc repo; các lệnh dùng được trên PowerShell và shell Linux.

```sh
git clone https://github.com/HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting.git
cd Kronos-VN30-Time-series-Forecasting
docker compose build data
docker compose run --rm data
```

Service `data` chạy tests hiện có. Image chứa NumPy, pandas, PyArrow, PyYAML, requests và pytest; collaborator làm dữ liệu/tests không cần tải PyTorch hoặc weights. Dependencies và distribution hashes được xuất từ `uv.lock` vào `requirements/data.txt`.

Dữ liệu được quản lý bằng **DVC + Google Drive**. Git chỉ giữ pointers, checksum và receipts; clone không tải dữ liệu. Upload và phục hồi 89 file từ Drive đã được xác minh; checkout Git chứa pointers/tài liệu của migration. [Hướng dẫn DVC](docs/DVC_Data_Versioning.md) có quyền truy cập và cách xác thực. Với checkout chứa pointers, cài DVC trên host và tải SQLite:

```sh
uv tool install --with-requirements requirements/dvc.txt dvc
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite.dvc
```

Kiểm tra snapshot bằng container:

```sh
docker compose run --rm data python scripts/check_shared_data.py
```

Lệnh kiểm tra checksum từ receipt trong checkout, SQLite integrity, dữ liệu gốc và nến so với CSV. Nếu thiếu dữ liệu, chạy `dvc pull` với pointer của cùng checkout; unit tests vẫn chạy độc lập với dữ liệu thật. Nếu cần ZIP, tải trước rồi kiểm tra:

```sh
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.zip.dvc
docker compose run --rm data python scripts/check_shared_data.py --format zip
```

Docker không chứa dataset/weights trong image và không tự tải VN30. Compose mount checkout vào `/workspace`: code sửa trên máy được dùng ngay; rebuild khi dependencies hoặc Dockerfile thay đổi. [Docker runbook](docs/Docker_Runbook.md) có lệnh kiểm tra và xử lý lỗi.

## Docker CUDA cho mô hình

Cần NVIDIA GPU và driver tương thích PyTorch CUDA 13.0. Windows dùng Docker Desktop với WSL2 backend; Linux cần NVIDIA Container Toolkit. Tham khảo [Compose GPU](https://docs.docker.com/compose/how-tos/gpu-support/) và [Windows GPU prerequisites](https://docs.docker.com/desktop/features/gpu/).

```sh
docker compose --profile cuda build cuda
docker compose --profile cuda run --rm cuda
docker compose --profile cuda run --rm cuda python scripts/bootstrap_kronos.py
docker compose --profile cuda run --rm cuda python scripts/verify_checkpoint_provenance.py --output artifacts/local/checkpoint_verification.json
docker compose --profile cuda run --rm cuda python scripts/smoke_models.py --model all --device cuda:0 --output artifacts/local/model_smoke.json
```

Service `cuda` cài toàn bộ môi trường từ `pyproject.toml`/`uv.lock` bằng `uv sync --frozen`, không đổi torch trên host. Lệnh mặc định kiểm tra PyTorch nhận GPU. Hai lệnh cuối có thể tải weights từ Hugging Face ở revision cố định; cache nằm trong Docker volume `hf-cache`.

Smoke test dùng OHLC giả, không phải kết quả nghiên cứu. Output tại `artifacts/local/` tránh sửa bằng chứng Phase 0 đã lưu. Hiện chưa có CLI chạy benchmark Phase 2–5; các task đó còn pending.

## Python trực tiếp

Cần Python 3.11 và `uv`. collaborator dữ liệu dùng môi trường riêng.

Windows PowerShell:

```powershell
uv venv .venv-data --python 3.11
uv pip install --python .venv-data/Scripts/python.exe --require-hashes -r requirements/data.txt
.venv-data/Scripts/python.exe -m pytest -q
.venv-data/Scripts/python.exe scripts/check_shared_data.py
```

Linux:

```sh
uv venv .venv-data --python 3.11
uv pip install --python .venv-data/bin/python --require-hashes -r requirements/data.txt
.venv-data/bin/python -m pytest -q
.venv-data/bin/python scripts/check_shared_data.py
```

Môi trường nghiên cứu đầy đủ, giữ torch CUDA đã khóa:

```sh
uv sync --frozen --group dev
uv run --no-sync python scripts/bootstrap_kronos.py
uv run --no-sync python scripts/verify_checkpoint_provenance.py --output artifacts/local/checkpoint_verification.json
uv run --no-sync python scripts/smoke_models.py --model all --device auto --output artifacts/local/model_smoke.json
```

`--device auto` có thể chọn CPU; thí nghiệm CUDA dùng `--device cuda:0` và ghi lại thiết bị. Không thay torch bằng `pip install torch` trong `.venv` đã khóa.

## Dữ liệu và Phase 1

Người quản lý dữ liệu tạo ZIP từ phản hồi gốc đã giữ tại máy, sau đó tạo SQLite từ ZIP đã xác minh:

```sh
python scripts/share_vndirect_snapshot.py
python scripts/share_vndirect_sqlite.py
```

Xuất ZIP cần môi trường `data` hoặc `.venv-data`; xuất/kiểm tra SQLite chỉ cần thư viện chuẩn Python. Raw captures có pointer `data/raw.dvc`; tải khi cần replay. collaborator chỉ cần SQLite cho truy vấn thông thường. Quy trình upload trước rồi commit pointers/receipts nằm trong hướng dẫn DVC. Mọi người dùng cùng commit và receipt, không tự nối nguồn hoặc sửa giá. [Hướng dẫn dữ liệu](docs/Collaborator_Data_Guide.md) có schema, SQL/pandas và quy trình cập nhật snapshot.

Freeze dữ liệu nghiên cứu sau khi có accepted inputs:

```sh
docker compose run --rm data python scripts/freeze_phase1.py
docker compose run --rm data python scripts/freeze_phase1.py --verify
```

Với cấu hình hiện tại, lệnh đầu **phải exit 1** vì `status: pending`; `--verify` chỉ có ý nghĩa sau freeze hoàn tất. Không đổi status sang accepted chỉ để lệnh chạy. Hợp đồng input/output ở [Phase 1 freeze runbook](docs/Phase1_Freeze_Runbook.md).

## Làm việc cùng nhau

1. Chọn một task pending trong checklist, ghi Task ID/phạm vi vào issue và trao đổi owner trước khi làm. Không nhận trùng task đang có người làm.
2. Chủ repo mời collaborator với quyền GitHub Write; cả nhóm clone repo chung và push branch riêng vào `origin`. Thành viên cùng upload dữ liệu cần Drive Editor và được thêm OAuth Test users khi app ở Testing. Xem [quy trình nhóm](COLLABORATING.md).
3. Đồng bộ main, tạo branch riêng. Ví dụ T021:

```sh
git switch main
git pull --ff-only
git switch -c codex/t021-model-interface
```

4. Sửa code/docs và tests liên quan. Output thử nghiệm đặt tại `artifacts/local/<task-or-name>/` hoặc `reports/local/`. Cập nhật evidence/checklist khi đủ acceptance criteria; không đánh dấu done chỉ vì có script.
5. Chạy checks, stage đúng file đã sửa, xem diff rồi commit/push branch. Thay tên file ví dụ bằng các file thuộc task của bạn:

```sh
docker compose run --rm data
git diff --check
git status --short
git add src/models/base.py tests/test_model_interface.py
git diff --cached
git commit -m "Implement T021 model interface"
git push -u origin codex/t021-model-interface
```

Các file T021 trên là ví dụ cho task chưa triển khai; không chạy `git add` với tên chưa tồn tại. PR docs/data có thể chạy tests bằng `.venv-data` thay Docker.

6. Mở Pull Request trên GitHub từ branch của bạn về `main` của repo chính. Điền template: Task ID/issue, vấn đề và hành vi mới, lệnh kiểm tra, evidence và tác động tới nghiên cứu. Đợi CI/reviewer; cập nhật cùng branch để xử lý feedback. Đóng issue/đánh dấu task accepted sau khi đủ nghiệm thu; không push trực tiếp lên main.

Git giữ `data/share/*.dvc`, `data/raw.dvc`, checksum và receipts; DVC giữ binary/raw bytes trên Drive. Không commit SQLite/ZIP, dữ liệu làm việc ở `data/raw/`, `data/interim/`, `data/processed/`, weights, credentials hoặc `.venv`. Snapshot SHA256 xác nhận cùng phiên bản, không thay cho kiểm định chất lượng.

Repo public không làm hash DVC thành quyền tải Drive. Remote cần được chia sẻ theo tài khoản; hash/pointers chỉ là metadata. SQLite/ZIP cũ đã được gỡ khỏi cây file hiện tại nhưng vẫn còn trong lịch sử GitHub public. Chi tiết phạm vi truy cập ở [DVC guide](docs/DVC_Data_Versioning.md).

## Cấu trúc repo

```text
configs/                 Hợp đồng nghiên cứu, nguồn, pending freeze inputs
data/manifests/          Provenance, receipts, calendar/source evidence
data/raw/                Phản hồi gốc, DVC qua data/raw.dvc
data/share/              DVC snapshots; Git giữ pointers/checksums
data/interim/            Dữ liệu làm việc, gitignored
data/processed/          Accepted dataset khi hoàn tất Phase 1
scripts/                 Audit, calendar, freeze, môi trường và chia sẻ dữ liệu
src/                     Chỗ triển khai framework/models; core benchmark chưa có
tests/                   Tests dữ liệu, calendar, freeze, snapshot integrity
artifacts/               Bằng chứng và output thí nghiệm theo loại
docs/                    Plan, tasks, runbooks; plan cũ ở archive/
reports/                 Báo cáo kiểm định và nghiên cứu
requirements/data.txt    Dependency subset xuất từ uv.lock
requirements/dvc.txt     DVC/Drive tool pins, môi trường riêng
Dockerfile               Targets data và cuda
compose.yaml             Bind mount và model cache cho collaborator
```

## File cần giữ và file có thể dọn

| Nhóm | Chính sách |
|---|---|
| DVC pointers, checksum và receipts | Giữ trong Git; tải binary bằng `dvc pull` |
| SQLite/ZIP/raw bytes và DVC cache | Chỉ dọn local sau khi upload và phục hồi remote đã được kiểm tra |
| `docs/archive/` | Plan cũ để tham khảo; dùng technical plan/checklist hiện tại khi làm task |
| `.pytest_cache/`, `__pycache__/`, ảnh PNG render tạm | Có thể xóa và tạo lại; không commit |
| `tmp/vnstock-env/` | Môi trường audit riêng có thể tạo lại từ requirements; giữ khi còn cần replay |
| `.venv/`, `.vendor/`, model cache | Runtime local đang dùng; không là rác và không commit |
| `data/raw/`, audit manifests/reports/artifacts, PDF tham khảo | Giữ bằng chứng tái lập; không xóa chỉ vì không dùng cho benchmark chính |

Chi tiết lượt dọn hiện tại: [repository cleanup](reports/repository_cleanup.md).

## Tài liệu chính

| Tài liệu | Mục đích |
|---|---|
| [Technical plan](docs/VN30_TSFMs_Kronos_Technical_Implementation_Plan.md) | Quy trình và lựa chọn nghiên cứu |
| [End-to-end tasks](docs/VN30_TSFMs_Kronos_End_to_End_Tasks.md) | Task ID, phụ thuộc, đầu ra, nghiệm thu |
| [collaborator guide](COLLABORATING.md) | Nhận task, branch/PR, tests, evidence |
| [Data guide](docs/Collaborator_Data_Guide.md) | Cùng phiên bản SQLite/ZIP |
| [DVC guide](docs/DVC_Data_Versioning.md) | Drive access, OAuth, tải/phát hành dữ liệu |
| [Docker runbook](docs/Docker_Runbook.md) | Build, chạy CPU/CUDA, xử lý lỗi |
| [Freeze runbook](docs/Phase1_Freeze_Runbook.md) | Accepted inputs và immutable outputs |
| [Phase 1 readiness](reports/phase1_readiness_review.md) | Điều kiện dữ liệu còn pending |
| [T010/T012 review](reports/vndirect_T010_T012_review.md) | Audit mới, calendar candidate và acceptance boundary |
| [39-field review](reports/vndirect_39_discrepancy_review.md) | Từng sai khác, bằng chứng và vấn đề Open |
| [Baseline literature review](reports/vn30_baseline_literature_review.md) | Bốn tài liệu, giới hạn và đề xuất thay đổi chưa áp dụng |
| [Research report](docs/TSFM_VN30Index_Report.md) | Nội dung trình bày nghiên cứu |

# Docker cho collaborator

## Hai môi trường

| Service | Dependencies | Công việc |
|---|---|---|
| `data` | Python 3.11 và subset có hashes từ uv.lock | Audit, calendar, tests, SQLite/ZIP, freeze khi đủ inputs |
| `cuda` | Toàn bộ uv.lock, torch 2.14.0+cu130 | Bootstrap, provenance và model smoke trên NVIDIA |

Base Python/uv image pin bằng digest. Python packages được khóa; apt packages lấy từ Debian repository nên rebuild vẫn có thể nhận cập nhật hệ thống. Freeze thí nghiệm cần ghi image ID/digest và package/device versions thực tế; không khẳng định rebuild byte-identical.

## CPU/data

```sh
docker compose --profile cuda config --quiet
docker compose build data
docker compose run --rm data
docker compose run --rm data python scripts/check_shared_data.py
docker compose run --rm data python scripts/export_data_requirements.py --check
```

Default command là pytest. Tests dùng synthetic inputs. Cài/xác thực DVC trên host theo [DVC guide](DVC_Data_Versioning.md), chạy `dvc pull` trước khi dùng SQLite/ZIP; Git chỉ giữ pointers/receipts. Build không gọi API VN30 và vẫn loại dữ liệu khỏi image; Compose đọc snapshot từ checkout.

Replay T010/T012 và 39 sai khác dùng các lệnh ở [freeze runbook](Phase1_Freeze_Runbook.md), thêm prefix `docker compose run --rm data`. Chạy `dvc pull data/raw.dvc` trên host để lấy đúng raw captures/calendar/PDF đã ghi trong manifests; clone Git riêng không đủ bytes cho replay. Snapshot chia sẻ vẫn là candidate cũ, không phải audit mới hoặc accepted dataset. CUDA/model inference tiếp tục chờ các gate tương ứng.

Compose mount checkout vào `/workspace`, gồm Git metadata phục vụ repository hygiene tests. Dùng `docker run` trực tiếp phải mount checkout; image không chứa `.git`:

```sh
docker run --rm --mount "type=bind,source=<absolute-repo-path>,target=/workspace" vn30-research-data:local python -m pytest -q -p no:cacheprovider
```

Thay placeholder bằng đường dẫn thật. Compose thuận tiện hơn với đường dẫn Windows có khoảng trắng.

## CUDA

Windows cần Docker Desktop Linux containers với WSL2 backend và NVIDIA driver tương thích. Linux cần NVIDIA Container Toolkit. Container không cài/đổi driver host. Tham khảo [Windows GPU prerequisites](https://docs.docker.com/desktop/features/gpu/) và [Compose GPU reservations](https://docs.docker.com/compose/how-tos/gpu-support/).

```sh
docker compose --profile cuda build cuda
docker compose --profile cuda run --rm cuda
docker compose --profile cuda run --rm cuda python scripts/bootstrap_kronos.py
docker compose --profile cuda run --rm cuda python scripts/verify_checkpoint_provenance.py --output artifacts/local/docker/checkpoints.json
docker compose --profile cuda run --rm cuda python scripts/smoke_models.py --model all --device cuda:0 --output artifacts/local/docker/smoke.json
```

Default CUDA command in torch/CUDA versions và GPU availability, exit nonzero nếu không có GPU. Weights chỉ tải khi chạy provenance/smoke, ở revision trong manifest. Bootstrap đọc pinned Kronos code revision từ manifest và từ chối checkout có local edits. `.vendor/Kronos` không là Git submodule.

Cache weights ở volume `hf-cache`; dataset/output ở checkout bind mount. Môi trường `/opt/venv` cài lúc build; rebuild sau khi sửa lock, không chạy `uv sync` để sửa môi trường bằng quyền collaborator. [uv Docker guide](https://docs.astral.sh/uv/guides/integration/docker/) là tài liệu tham chiếu.

## Snapshot và outputs

```sh
docker compose run --rm data python scripts/check_shared_data.py --format sqlite
docker compose run --rm data python scripts/check_shared_data.py --format zip
docker compose run --rm data python scripts/share_vndirect_snapshot.py
docker compose run --rm data python scripts/share_vndirect_sqlite.py
```

Hai lệnh export chỉ dành cho người có raw/ZIP input; từ chối ghi đè gói cũ. collaborator chỉ cần nhận đúng snapshot để làm code/tests. Output riêng đặt trong `artifacts/local/` hoặc `reports/local/`. Candidate data chưa có accepted calendar/splits; Docker không thay đổi trạng thái gate.

## Xử lý lỗi

| Lỗi | Cách xử lý |
|---|---|
| Cannot connect to daemon | Khởi động Docker Desktop/daemon; kiểm tra `docker info` |
| Image data thiếu torch/chronos | Dùng service `cuda` cho model |
| CUDA unavailable/device driver error | Kiểm tra driver, WSL2/Container Toolkit và GPU reservations |
| Snapshot thiếu/hash mismatch | `dvc pull` pointer của checkout trên host, kiểm tra lại; không ghi lại hash theo file không rõ nguồn |
| Freeze refused với pending inputs | Hành vi đúng; hoàn tất G1/calendar và review input spec |
| Permission denied ở bind mount Linux | Container UID 1000; dùng `docker compose run --rm --user <uid>:<gid> data ...` với UID/GID của bạn cho data |
| Tests không tìm thấy Git repository | Dùng Compose từ root checkout hoặc mount checkout khi docker run |
| Requirements khác uv.lock | Chạy `python scripts/export_data_requirements.py`, review và rebuild |

Không thêm token vào Dockerfile/Compose/build args. Drive OAuth chạy trên host; `.dvc/cache`, `.dvc/tmp` và `.dvc/config.local` bị loại khỏi build context. Không cần thêm DVC vào image data/CUDA. Image không mở cổng hoặc chạy database server; SQLite là snapshot file.

## Bằng chứng

Build/run thực tế ghi tại `reports/collaborator_setup_validation.md`. `.github/workflows/ci.yml` cấu hình CI; chỉ coi GitHub CI đạt sau khi run thật hoàn tất.

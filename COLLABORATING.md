# Hướng dẫn collaborator

## Quyền và trách nhiệm trong nhóm

| Thành phần | Quyền/thiết lập cho collaborator |
|---|---|
| GitHub | Write để push branch và mở PR trong repo chung |
| Google Drive | Editor khi cùng tạo/upload phiên bản DVC; Viewer đủ cho thành viên chỉ kiểm tra/tải |
| OAuth | Thêm email vào Audience → Test users khi app đang Testing; mỗi người đăng nhập bằng tài khoản riêng |
| Nghiên cứu | Thống nhất task, owner/reviewer, dữ liệu, interfaces và tiêu chí nghiệm thu trước khi chạy |

Quyền GitHub, Drive và OAuth được cấp riêng. Có quyền upload không tự chấp nhận dữ liệu hoặc thay hợp đồng nghiên cứu. Collaborator có thể làm nguồn/calendar, xử lý dữ liệu, xây model, đánh giá và viết báo cáo theo task đã thống nhất.

## Nhận task và phối hợp

Đọc README, technical plan và checklist trước khi nhận task. Task ID là đơn vị theo dõi chung; dùng issue/PR ghi owner, reviewer, phụ thuộc, phạm vi file và evidence. Không tự nhận thay một task đang có owner.

Trước khi làm T010–T014 hoặc T030, đọc [39-field review](reports/vndirect_39_discrepancy_review.md) và [baseline review](reports/vn30_baseline_literature_review.md). Bốn Close được corroborate không có nghĩa G1 đạt; 35 O/H/L và cách dựng Open còn pending. Đề xuất đổi E0/KTPCA chưa thay hợp đồng v4. Không sửa giá, tăng tolerance hoặc thay baseline chỉ để task đạt.

| Nhóm công việc | Phạm vi | Điểm phối hợp |
|---|---|---|
| Data/source | T010–T014 | Collaborator phụ trách task phát hành phiên bản; người khác review nguồn/calendar và hashes |
| Framework/evaluation | T020–T027 | Chốt interface/artifact schema trước khi chia adapter |
| Baselines | T030–T033 | Phụ thuộc engine/metrics và accepted origins |
| TSFM/adapters | T040–T042 | Revision cố định và cùng dữ liệu quan sát |
| Freeze/holdout | T043–T044 | Một người điều phối run; reviewer xác nhận G4 |
| Results/paper | T050–T055, T080–T081 | Sinh từ persisted artifacts và hashes |
| Secondary/optional | T060–T076 | Không trì hoãn core benchmark; ghi lý do deferred |

Có thể viết interface, metrics và tests với fixtures giả khi dữ liệu thật chưa accepted. Điều này không cho phép chạy primary holdout hoặc đóng task phụ thuộc dữ liệu.

## Branch và PR

Collaborator là thành viên cùng nghiên cứu, được chủ repo mời với quyền Write. Mọi người clone cùng repo và push branch của mình vào `origin`; quy trình nhóm dùng branch/PR trong repo chung.

```sh
git clone https://github.com/HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting.git
cd Kronos-VN30-Time-series-Forecasting
```

```sh
git switch main
git pull --ff-only
git switch -c codex/t021-model-interface
```

Thay ID/mô tả theo task. Giữ working tree hiện có trước khi switch; không reset/clean để bỏ sửa đổi của người khác.

Sau khi sửa và kiểm tra:

```sh
git status --short
git add <files-for-your-task>
git diff --cached
git commit -m "Implement T021 model interface"
git push -u origin codex/t021-model-interface
```

Thay `<files-for-your-task>` bằng file thật thuộc task; tránh `git add .` khi working tree chứa thay đổi của task khác. Mở PR trên GitHub với base `HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting:main`, compare branch của bạn trong repo chung. Đợi CI và reviewer, sửa feedback trên cùng branch. Sau merge, đồng bộ main rồi nhận task tiếp theo.

PR ghi task/issue, vấn đề và hành vi mới, lệnh kiểm tra đã chạy, evidence, thay đổi data/config/split và checklist liên quan. Dùng `.github/pull_request_template.md`. Task accepted cần đầu ra, mọi acceptance criteria đạt và reviewer kiểm tra bằng chứng.

Thay đổi nghiên cứu đã freeze phải ghi vào `reports/experiment_log.md`, tạo phiên bản/hashes mới và xác định lại phạm vi run. Không dùng kết quả test để đổi cấu hình hoặc dữ liệu.

## Môi trường và checks

```sh
docker compose build data
docker compose run --rm data python scripts/export_data_requirements.py --check
docker compose run --rm data
```

Collaborator docs/data không cần tải weights/CUDA. Model collaborators dùng service `cuda` hoặc `.venv` khóa bởi `uv.lock`; các lệnh nằm trong README.

Checks cho PR:

```sh
git diff --check
docker compose --profile cuda config --quiet
docker compose run --rm data
```

Sửa dependencies có chủ đích trong `pyproject.toml`, cập nhật `uv.lock`, rồi chạy `python scripts/export_data_requirements.py`. Commit cả lock và requirements đã sinh; không sửa thủ công `requirements/data.txt`. Adapter/model cần contract/leakage tests và smoke test phù hợp; ghi GPU, torch, CUDA và revision. CI data không xác minh adapter/model chưa triển khai.

## Dữ liệu và output

- Tải SQLite/ZIP bằng `dvc pull` với pointer của checkout; xem [DVC guide](docs/DVC_Data_Versioning.md) để cài tool và xác thực Drive. Dùng đúng receipt; chạy `python scripts/check_shared_data.py` trước khi dùng.
- Giữ dữ liệu nguồn, thứ tự và quality flags. Không splice, impute, sửa OHLC hoặc bỏ duplicate để qua kiểm tra.
- SQLite là snapshot: mỗi collaborator dùng bản local chỉ đọc; kết quả riêng đặt ở file khác.
- Output thử nghiệm đặt tại `artifacts/local/<task-or-name>/` hoặc `reports/local/`, được gitignore. Smoke/provenance nhận `--output` để tránh sửa bằng chứng chung.
- File đã hash-bound không được sửa chỉ để đổi kết luận; tạo evidence/manifest mới và liên kết bản cũ.
- Git quản lý DVC pointers, checksum/receipts; SQLite/ZIP và raw bytes ở DVC/Drive. Interim/processed chưa có pointer, weights và outputs lớn vẫn gitignore. Không đưa dữ liệu/weights vào Docker image hoặc tự upload từ CI.

Collaborator phụ trách task dữ liệu xuất phiên bản mới bằng `share_vndirect_*`, cập nhật receipt theo bytes thực tế, chạy checks, `dvc add` rồi `dvc push`. Kiểm tra tải từ checkout/cache trống trước khi publish pointers/checksum/receipts trong cùng PR. collaborator nhận code bằng Git và dữ liệu bằng `dvc pull`; không sửa DB trong repo để lưu kết quả riêng. Journal/WAL/SHM không được commit. Người phát hành ghi task, nguồn/biến đổi, hashes và reviewer; cả nhóm dùng phiên bản đã review. Việc cập nhật Git không tự làm G1 pass.

DVC tool dùng `requirements/dvc.txt`, tách khỏi dependency graph CUDA. Sau thay đổi quy trình versioning, chạy `python scripts/check_dvc_roundtrip.py`; CI kiểm tra local remote với fixtures giả, không kiểm tra Drive.

## Nghiệm thu task

Ghi entry trong `reports/experiment_log.md` theo template cuối checklist: Task ID, owner/reviewer, status, code commit, hashes, commands, outputs, checks và deviations. Với PR đang review, ghi commit thực thi kiểm tra; sau merge bổ sung commit chứa thay đổi nếu cần. Không bịa reviewer, kết quả hoặc hashes.

`implemented` nghĩa là có code; `accepted` nghĩa là có bằng chứng nghiệm thu. `blocked` cần điều kiện cụ thể còn thiếu. Optional work không thay thế gate bắt buộc.

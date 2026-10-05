# Hướng dẫn contributor

## Nhận task và phối hợp

Đọc README, technical plan và checklist trước khi nhận task. Task ID là đơn vị theo dõi chung; dùng issue/PR ghi owner, reviewer, phụ thuộc, phạm vi file và evidence. Không tự nhận thay một task đang có owner.

| Nhóm công việc | Phạm vi | Điểm phối hợp |
|---|---|---|
| Data/source | T010–T014 | Một người quản lý phiên bản snapshot; người khác kiểm tra nguồn/calendar |
| Framework/evaluation | T020–T027 | Chốt interface/artifact schema trước khi chia adapter |
| Baselines | T030–T033 | Phụ thuộc engine/metrics và accepted origins |
| TSFM/adapters | T040–T042 | Revision cố định và cùng dữ liệu quan sát |
| Freeze/holdout | T043–T044 | Một người điều phối run; reviewer xác nhận G4 |
| Results/paper | T050–T055, T080–T081 | Sinh từ persisted artifacts và hashes |
| Secondary/optional | T060–T076 | Không trì hoãn core benchmark; ghi lý do deferred |

Có thể viết interface, metrics và tests với fixtures giả khi dữ liệu thật chưa accepted. Điều này không cho phép chạy primary holdout hoặc đóng task phụ thuộc dữ liệu.

## Branch và PR

Có quyền push: `origin` là repo chính. Chưa có quyền push: fork repo trên GitHub, clone fork, thêm repo chính làm upstream:

```sh
git clone https://github.com/<your-account>/Kronos-VN30-Time-series-Forecasting.git
cd Kronos-VN30-Time-series-Forecasting
git remote add upstream https://github.com/HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting.git
git fetch upstream
git switch main
git merge --ff-only upstream/main
```

Thay `<your-account>` bằng tài khoản GitHub của bạn. Với fork, đồng bộ qua `upstream/main`; với clone repo chính, dùng `git pull --ff-only` như bên dưới. Không cố force/reset nếu branch đã diverge: xử lý commits của bạn trước.

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

Thay `<files-for-your-task>` bằng file thật thuộc task; tránh `git add .` khi working tree chứa thay đổi của task khác. Mở PR trên GitHub với base `HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting:main`, compare branch của bạn trong repo chính/fork. Đợi CI và reviewer, sửa feedback trên cùng branch. Sau merge, đồng bộ main rồi nhận task tiếp theo.

PR ghi task/issue, vấn đề và hành vi mới, lệnh kiểm tra đã chạy, evidence, thay đổi data/config/split và checklist liên quan. Dùng `.github/pull_request_template.md`. Task accepted cần đầu ra, mọi acceptance criteria đạt và reviewer kiểm tra bằng chứng.

Thay đổi nghiên cứu đã freeze phải ghi vào `reports/experiment_log.md`, tạo phiên bản/hashes mới và xác định lại phạm vi run. Không dùng kết quả test để đổi cấu hình hoặc dữ liệu.

## Môi trường và checks

```sh
docker compose build data
docker compose run --rm data python scripts/export_data_requirements.py --check
docker compose run --rm data
```

Contributor docs/data không cần tải weights/CUDA. Model contributors dùng service `cuda` hoặc `.venv` khóa bởi `uv.lock`; các lệnh nằm trong README.

Checks cho PR:

```sh
git diff --check
docker compose --profile cuda config --quiet
docker compose run --rm data
```

Sửa dependencies có chủ đích trong `pyproject.toml`, cập nhật `uv.lock`, rồi chạy `python scripts/export_data_requirements.py`. Commit cả lock và requirements đã sinh; không sửa thủ công `requirements/data.txt`. Adapter/model cần contract/leakage tests và smoke test phù hợp; ghi GPU, torch, CUDA và revision. CI data không xác minh adapter/model chưa triển khai.

## Dữ liệu và output

- Dùng đúng SQLite/ZIP theo receipt; chạy `python scripts/check_shared_data.py` trước khi dùng.
- Giữ dữ liệu nguồn, thứ tự và quality flags. Không splice, impute, sửa OHLC hoặc bỏ duplicate để qua kiểm tra.
- SQLite là snapshot: mỗi contributor dùng bản local chỉ đọc; kết quả riêng đặt ở file khác.
- Output thử nghiệm đặt tại `artifacts/local/<task-or-name>/` hoặc `reports/local/`, được gitignore. Smoke/provenance nhận `--output` để tránh sửa bằng chứng chung.
- File đã hash-bound không được sửa chỉ để đổi kết luận; tạo evidence/manifest mới và liên kết bản cũ.
- Snapshot SQLite/ZIP nhỏ trong `data/share/` được quản lý bằng Git cùng checksum/receipts. Working raw data, weights và outputs lớn vẫn gitignore. Không đưa dữ liệu/weights vào Docker image hoặc tự upload từ CI.

Người quản lý dữ liệu xuất phiên bản mới bằng `share_vndirect_*`, cập nhật receipt theo bytes thực tế, chạy checks và đưa snapshot/checksum/receipts vào cùng PR. Contributor nhận qua clone/pull commit đó; không sửa DB trong repo để lưu kết quả riêng. Journal/WAL/SHM không được commit. Việc cập nhật Git không tự làm G1 pass.

## Nghiệm thu task

Ghi entry trong `reports/experiment_log.md` theo template cuối checklist: Task ID, owner/reviewer, status, code commit, hashes, commands, outputs, checks và deviations. Với PR đang review, ghi commit thực thi kiểm tra; sau merge bổ sung commit chứa thay đổi nếu cần. Không bịa reviewer, kết quả hoặc hashes.

`implemented` nghĩa là có code; `accepted` nghĩa là có bằng chứng nghiệm thu. `blocked` cần điều kiện cụ thể còn thiếu. Optional work không thay thế gate bắt buộc.

# Dữ liệu VN30 cho collaborator

VNDIRECT là nguồn chính được chọn ngày 05/10/2026. Dữ liệu dùng một snapshot cố định; gọi API riêng từng người có thể nhận phiên bản khác. Snapshot **candidate** có 2.271 hàng, 24/08/2017–01/10/2026; G1/calendar/splits chưa accepted. Audit mới có 2.272 hàng đến 02/10/2026, chưa thay snapshot chia sẻ.

[Review 39 trường](../reports/vndirect_39_discrepancy_review.md) ghi bốn Close được bản tin hỗ trợ, 35 O/H/L chưa phân xử và 71 phiên Open bằng Close trước. Không sửa giá, tự loại hàng hoặc chạy benchmark chính/fine-tune trước khi acceptance hoàn tất.

## Làm việc cùng nghiên cứu

Collaborator có quyền GitHub Write để làm branch/PR trong repo chung; nếu cùng phát hành dữ liệu, dùng Drive Editor. Viewer đủ khi chỉ tải/kiểm tra. Khi OAuth app ở Testing, thêm email vào Test users và đăng nhập riêng; không dùng chung user tokens.

Thống nhất task và phiên bản đầu vào trước khi xử lý. Mỗi người có dataset local; code, nghiên cứu nguồn/calendar, mô hình và đánh giá được review qua PR. Dữ liệu mới có thể do bất kỳ collaborator phụ trách task đó phát hành sau kiểm tra, upload DVC và review; không giới hạn vào một người cố định.

## Nhận dữ liệu

Git chứa code, DVC pointers, checksums và audit receipts. Raw/PDF và SQLite/ZIP lưu bằng **DVC trên Google Drive**; clone Git không tự tải dữ liệu. Đã xác minh upload và phục hồi 89 file; pointers và receipts được version cùng code trong Git. Xem [DVC guide](DVC_Data_Versioning.md) cho trạng thái, quyền Viewer/Editor, cài tool và đăng nhập.

Sau khi remote đã được upload, tải SQLite của checkout:

```sh
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite.dvc
python scripts/check_shared_data.py
```

Kiểm tra chỉ dùng Python chuẩn, không cần CUDA. Trong Docker, tải bằng DVC trên host trước rồi chạy `docker compose run --rm data python scripts/check_shared_data.py`. Nếu cần ZIP hoặc replay audit:

```sh
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.zip.dvc
python scripts/check_shared_data.py --format zip
dvc pull data/raw.dvc
```

DVC kiểm tra content hash; script kiểm tra SHA256 từ receipt của checkout, SQLite integrity, original bytes, metadata và nến. Hash đúng chỉ xác nhận cùng phiên bản, không chứng minh chất lượng/G1. Replay dùng đúng paths trong manifests và [freeze runbook](Phase1_Freeze_Runbook.md), không thay bằng lần gọi API mới.

## SQLite và schema

SQLite là file tự chứa, có `candles`, `metadata` và `source_files` giữ các file nguồn nguyên vẹn. Không cần database server. ZIP là gói đối chiếu/export, chứa CSV, original response, parser/config/audit manifest và hashes. Snapshot giữ một hàng `outside_request` sau ngày yêu cầu 30/09/2026; không tự xem hàng đó thuộc accepted dataset. Không tạo volume giả cho chỉ số.

Đọc SQLite với kết nối chỉ đọc, trong môi trường data có pandas:

```python
import sqlite3
from pathlib import Path

import pandas as pd

db = Path('data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite').resolve()
connection = sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)
try:
    data = pd.read_sql_query(
        'SELECT date, open, high, low, close FROM candles '
        'WHERE symbol = ? ORDER BY date, row_id',
        connection,
        params=['VN30'],
        parse_dates=['date'],
    )
finally:
    connection.close()
```

`row_id` giữ thứ tự gốc; ngày không có ràng buộc unique để tránh làm mất nến trùng nếu có trong capture tương lai. Các cờ chất lượng được giữ trong bảng `candles`; truy vấn ví dụ không tự loại phiên hoặc sửa giá. Metadata tiếp tục ghi G1 pending, chưa có calendar/split chính thức.

Mỗi người đọc file trong checkout của mình bằng kết nối chỉ đọc; kết quả riêng ghi vào file khác dưới `data/interim/` hoặc `artifacts/local/`. Collaborator phụ trách task dữ liệu phát hành phiên bản mới sau review; tránh merge chỉnh sửa trực tiếp SQLite binary. Nếu nhóm cần truy vấn/cập nhật tập trung qua mạng, chọn PostgreSQL hoặc API. [Tài liệu SQLite](https://www.sqlite.org/whentouse.html) mô tả trao đổi dữ liệu bằng một file và khuyến nghị database client/server cho nhiều máy truy cập trực tiếp qua mạng.

## Xử lý và chia sẻ kết quả

1. Tạo branch `codex/<task-id>-<description>`, tải dữ liệu của cùng checkout và xác minh receipt.
2. Đọc SQLite ở chế độ read-only. Đặt dữ liệu dẫn xuất tại `data/interim/<task-id>/`, kết quả thí nghiệm tại `artifacts/local/<task-id>/`; ghi rõ các biến đổi và quality flags.
3. Commit code xử lý, tests, cấu hình và báo cáo vào branch; PR ghi input commit/hash, lệnh chạy, output/hash và reviewer để người cùng nghiên cứu tái lập được.
4. Nếu cả nhóm cần dữ liệu dẫn xuất, thống nhất đường dẫn/version và tạo DVC pointer ở vị trí Git không ignore, upload trước rồi review pointer/manifest trong cùng PR. Không đưa output lớn vào Git hoặc tự đánh dấu dữ liệu dẫn xuất thành accepted dataset.

Các biến đổi phục vụ nghiên cứu phải được ghi thành pipeline/config tái lập; không sửa bytes nguồn. Chấp nhận dataset/calendar/splits và thay đổi hợp đồng nghiên cứu vẫn cần evidence theo checklist. Snapshot hiện tại chưa cho phép benchmark chính/fine-tune.

## Phát hành và đối chiếu

Collaborator phụ trách task dữ liệu tải raw đúng phiên bản rồi tạo tên mới bằng `python scripts/share_vndirect_snapshot.py` và `python scripts/share_vndirect_sqlite.py`. Hai scripts dùng input local, không gọi API, không sửa giá và từ chối ghi đè. Tham số input/output ở `--help`.

Kiểm tra receipt, `dvc add` và upload trước; xác minh tải lại từ cache trống rồi mới commit/publish pointers, checksums và receipts trong cùng PR. Quy trình đầy đủ nằm trong [DVC guide](DVC_Data_Versioning.md). Giữ cùng commit code/data receipts; phiên bản accepted tương lai cần calendar, splits và freeze receipt mới.

DVC thay cách lưu/chia sẻ bytes, không thay chính sách G1. Tiêu chí quyền nghiên cứu tiếp tục được loại khỏi G1 theo quyết định trước đó. Không ghi lại quyền nguồn thành đã xác minh.

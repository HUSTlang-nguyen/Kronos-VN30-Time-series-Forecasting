# Chia sẻ dữ liệu VN30 cho contributor

VNDIRECT là nguồn chính được chọn ngày 05/10/2026. Nhóm dùng một snapshot có phiên bản: tải lại API riêng từng người có thể nhận dữ liệu đã được nhà cung cấp sửa đổi. Gói hiện tại là **candidate**, chưa phải dataset đã qua G1 và chưa có calendar/split được chấp nhận.

Audit mới có 2.272 hàng đến 02/10/2026, nhưng **SQLite/ZIP chia sẻ vẫn có 2.271 hàng đến 01/10/2026**. [Kiểm tra 39 trường](../reports/vndirect_39_discrepancy_review.md) ghi bốn Close được bản tin hỗ trợ, 35 O/H/L chưa phân xử và đoạn 71 phiên Open bằng Close trước. Contributor dùng snapshot cho phát triển/kiểm tra dữ liệu, không fine-tune hoặc chạy benchmark chính trước acceptance.

Các CSV/Parquet và biên nhận audit được quản lý trong Git; raw/PDF để replay nằm ngoài Git. Clone có snapshot cũ và kết quả audit mới, không có toàn bộ raw của audit mới. Muốn replay, nhận đúng raw paths ghi trong configs/manifests từ người quản lý dữ liệu và kiểm tra hashes; không thay raw bằng một lần gọi API mới. Các lệnh replay ở [freeze runbook](Phase1_Freeze_Runbook.md).

## Cách chia sẻ

1. Người quản lý dữ liệu tạo ZIP và checksum bằng lệnh bên dưới.
2. Đặt SQLite/ZIP và checksums trong `data/share/`, cập nhật receipts trong `data/manifests/`, review và commit các file đó trong cùng PR. Không ghi đè bản cũ để cập nhật dữ liệu; dùng phiên bản/tên mới.
3. Contributor clone/pull commit chứa snapshot, rồi kiểm tra trước khi dùng. Đối chiếu checksum với receipt trong Git, không chỉ checksum nhận cùng ZIP.
4. Dùng cùng snapshot và cùng commit code. Khi có dataset được chấp nhận, phân phối phiên bản mới kèm calendar, split và freeze receipt; không sửa đè bản candidate.

Các gói hiện tại tổng khoảng 672 KB nên quản lý trực tiếp bằng Git, chưa cần Git LFS/DVC. `data/share/` không gitignore; working raw/interim/processed và SQLite journal/WAL/SHM vẫn bị ignore. Git attributes giữ nguyên bytes của snapshot/checksum trên Windows/Linux. Docker build vẫn loại `data/share/` khỏi image; Compose truy cập qua mount checkout.

## Tạo gói tại máy quản lý dữ liệu

```powershell
.venv\Scripts\python.exe scripts\share_vndirect_snapshot.py
```

Lệnh dùng phản hồi gốc đã lưu tại `data/raw/source_audit/20261001T151513588605Z`; clone repo mới không có các byte này. Lệnh không gọi API, không sửa giá, không bỏ hàng và từ chối ghi đè gói đã có.

Gói nằm tại `data/share/vn30_vndirect_20261001T151513588605Z_candidate.zip`, cùng file checksum. Gói gồm:

- `vn30_daily.csv`: ngày theo Asia/Ho_Chi_Minh, OHLC theo điểm chỉ số, timestamp và cờ chất lượng.
- `original_response.json`: nguyên vẹn phản hồi VNDIRECT.
- `audit_manifest.json`, `audit_config.yaml`, `parser.py`: bằng chứng nguồn và cách chuyển đổi.
- `manifest.json`: thời điểm tải, phạm vi, số hàng, trạng thái và SHA256 từng file.

Snapshot tải ngày 01/10/2026 chứa 2.271 hàng từ 24/08/2017 đến 01/10/2026. Có một hàng ngoài khoảng yêu cầu ban đầu kết thúc 30/09/2026: được giữ và đánh dấu `outside_request`, không tự xem là thuộc dataset chính thức. Không tạo volume giả cho chỉ số.

## Contributor kiểm tra và sử dụng

Kiểm tra nhanh với receipt của checkout, không cần tự truyền checksum:

```sh
python scripts/check_shared_data.py --format zip
python scripts/check_shared_data.py --format sqlite
```

Trong Docker, thêm `docker compose run --rm data` trước `python`. Các lệnh chi tiết bên dưới giúp kiểm tra một file cụ thể; [README](../README.md) và [CONTRIBUTING](../CONTRIBUTING.md) có setup và quy trình PR.

Chạy từ thư mục repo với Python 3.11+. Chế độ kiểm tra chỉ dùng thư viện chuẩn Python, không cần CUDA hoặc cài dependencies nghiên cứu.

```powershell
$snapshotZip = 'data/share/vn30_vndirect_20261001T151513588605Z_candidate.zip'
$snapshotReceipt = Get-Content -Raw data/manifests/vndirect_contributor_snapshot.json | ConvertFrom-Json
python scripts/share_vndirect_snapshot.py --verify $snapshotZip --expected-sha256 $snapshotReceipt.archive_sha256
if ($LASTEXITCODE -ne 0) { throw 'Snapshot verification failed' }
Expand-Archive -LiteralPath $snapshotZip -DestinationPath 'data/interim/contributor/vndirect_20261001T151513588605Z'
```

Giải nén vào thư mục mới, không dùng `-Force`. Python kiểm tra SHA256 của ZIP, từng file bên trong và danh sách file; không thực thi `parser.py` trong gói. SHA256 xác nhận tính toàn vẹn và cùng phiên bản, không chứng minh dữ liệu đúng hoặc G1 đã đạt.

Đọc bằng pandas sau khi kiểm tra:

```python
import pandas as pd

data = pd.read_csv(
    'data/interim/contributor/vndirect_20261001T151513588605Z/vn30_daily.csv',
    parse_dates=['date'],
)
```

Chưa tự chia train/validation/test hoặc công bố kết quả benchmark chính thức từ bản candidate. Đợi freeze receipt để mọi contributor dùng cùng ngày và origins.

## Dùng SQLite thay cho giải nén CSV

SQLite phù hợp để chia sẻ một snapshot tự chứa: một file `.sqlite` gồm bảng `candles`, bảng `metadata` và bảng `source_files` chứa nguyên vẹn các file nguồn. Không cần cài database server hoặc thư viện Python bổ sung. CSV/ZIP gốc vẫn được giữ để đối chiếu.

Tạo từ ZIP đã xác minh với checksum trong receipt của repo:

```powershell
python scripts/share_vndirect_sqlite.py
```

SQLite và `.sqlite.sha256` trong `data/share/` đi cùng commit; contributor clone/pull rồi kiểm tra với receipt trong repo:

```powershell
$sqlitePath = 'data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite'
$sqliteReceipt = Get-Content -Raw data/manifests/vndirect_sqlite_snapshot.json | ConvertFrom-Json
python scripts/share_vndirect_sqlite.py --verify $sqlitePath --expected-sha256 $sqliteReceipt.database_sha256
if ($LASTEXITCODE -ne 0) { throw 'SQLite verification failed' }
```

Sau khi kiểm tra, đọc bằng pandas với kết nối chỉ đọc:

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

Mỗi người đọc file trong checkout của mình bằng kết nối chỉ đọc; kết quả riêng ghi vào file khác dưới `data/interim/` hoặc `artifacts/local/`. Người quản lý phát hành phiên bản mới khi cập nhật; tránh merge chỉnh sửa trực tiếp SQLite binary. Nếu nhóm cần truy vấn/cập nhật tập trung qua mạng, chọn PostgreSQL hoặc API. [Tài liệu SQLite](https://www.sqlite.org/whentouse.html) mô tả trao đổi dữ liệu bằng một file và khuyến nghị database client/server cho nhiều máy truy cập trực tiếp qua mạng.

## Phạm vi chia sẻ

Theo yêu cầu ngày 05/10/2026, dự án quản lý snapshot chia sẻ trực tiếp trong Git. Quyết định này thay hướng dẫn dùng thư mục riêng trước đó, không làm thay đổi dữ liệu hoặc chất lượng nghiệm thu. Tiêu chí quyền nghiên cứu vẫn được loại khỏi G1 theo quyết định trước đó; không ghi lại quyền nguồn thành đã xác minh.

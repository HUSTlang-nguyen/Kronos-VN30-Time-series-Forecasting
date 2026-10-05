# DVC và Google Drive

Git lưu code, `.dvc`, checksum SHA256 và receipts. DVC lưu raw captures và SQLite/ZIP trên [thư mục Drive của nhóm](https://drive.google.com/drive/folders/1FDP-QGk_-UdcZsjaEuYjXgEu_1Nd62ur). Không cần DVC Studio hay dịch vụ lưu trữ trả phí; dữ liệu dùng dung lượng Drive hiện có.

**Trạng thái triển khai — 06/10/2026:** đã upload và phục hồi đủ **89 file** từ Drive trong workspace/cache riêng, SHA256 của từng file không đổi; SQLite/ZIP xác minh đúng receipts. Đã dùng OAuth client riêng sau khi Google chặn ứng dụng mặc định. Pointers/tài liệu và receipts được version cùng code trong Git. Một collaborator khác chưa kiểm tra tải độc lập bằng tài khoản riêng. Bằng chứng: [receipt](../data/manifests/dvc_drive_verification.json), [validation](../reports/dvc_migration_validation.md).

## Quyền truy cập

Chủ thư mục chọn Share và thêm email Google của từng collaborator: Editor cho thành viên cùng quản lý/phát hành dữ liệu bằng DVC; Viewer đủ khi chỉ tải/kiểm tra. Đồng thời cấp GitHub Write cho branch/PR trong repo chung và OAuth Test users khi app ở Testing. Ba quyền này được thiết lập riêng. Không cần bật public. DVC khuyến nghị chia sẻ cho tài khoản/nhóm cụ thể; “Anyone with the link” không đảm bảo hoạt động qua API. [DVC Google Drive](https://doc.dvc.org/user-guide/data-management/remote-storage/google-drive).

Drive lưu các object theo hash, không phải thư mục SQLite có thể chỉnh sửa trực tiếp. Không đổi tên/xóa object bằng Drive UI. SQLite được tải về từng máy để đọc; không dùng Drive như database server.

## Repo public và quyền dữ liệu

Repo public làm công khai pointers `.dvc`, hashes, đường dẫn và metadata đã commit. Hash nhận diện/xác minh phiên bản, không phải token hay quyền truy cập Drive. Người biết hash và folder ID vẫn phải được Drive cấp quyền để lấy object từ remote Restricted. [DVC pointers](https://doc.dvc.org/user-guide/project-structure/dvc-files), [Drive authorization](https://doc.dvc.org/user-guide/data-management/remote-storage/google-drive).

Để giới hạn remote cho nhóm, chủ thư mục đặt General access → Restricted và chia sẻ theo email. Audience/Test users chỉ kiểm soát đăng nhập qua OAuth client đang Testing; không thay quyền thư mục Drive. Client secret, user tokens và `.dvc/config.local` không được commit; mỗi collaborator đăng nhập tài khoản riêng.

**Cập nhật migration 06/10/2026:** repo GitHub public; SQLite/ZIP đã được thay bằng DVC pointers trong cây file hiện tại. Binary cũ vẫn tồn tại trong lịch sử Git và có thể tải mà không cần quyền Drive. Xóa khỏi commit mới không thu hồi bản đã clone/fork/tải; muốn hạn chế những bản này cần quyết định riêng về visibility/lịch sử, không chỉ đổi DVC hash. [GitHub data removal](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Cài công cụ riêng

Chạy ở root checkout với Git và uv đã cài:

```sh
uv tool install --with-requirements requirements/dvc.txt dvc
dvc version
dvc remote list
```

Tool tách khỏi `.venv` CUDA và `.venv-data`. Nếu shell chưa nhận `dvc`, chạy `uv tool update-shell` rồi mở terminal mới. `requirements/dvc.txt` pin DVC/plugin/pyOpenSSL để tránh lỗi `GEN_EMAIL` đã gặp khi resolver chọn pyOpenSSL 22.0.0 với cryptography không tương thích; đây không phải lock toàn bộ dependency graph.

Repo đã cấu hình remote `team` trong `.dvc/config`:

```text
gdrive://1FDP-QGk_-UdcZsjaEuYjXgEu_1Nd62ur
```

Không chạy lại `dvc init` hoặc thay remote bằng `gdrive://root` trên máy collaborator.

## OAuth riêng khi ứng dụng mặc định bị chặn

Người quản lý nhóm tạo client theo [Google Drive desktop OAuth setup](https://developers.google.com/workspace/drive/api/quickstart/python):

1. Vào Google Cloud Console, chọn/tạo project và bật **Google Drive API**.
2. Cấu hình **Google Auth Platform → Branding / Audience**. Với tài khoản Gmail cá nhân, chọn External; khi app ở Testing, thêm email người upload và collaborators vào Test users.
3. Vào **Clients → Create client**, chọn **Desktop app**, tải JSON. Giữ file ngoài repository; không gửi token hoặc mật khẩu qua chat/PR.
4. Mỗi thành viên cấu hình client JSON tại máy mình rồi đăng nhập Google bằng tài khoản đã được chia sẻ thư mục. Việc thêm Test user không tự cấp quyền thư mục Drive.

Ví dụ PowerShell; thay đường dẫn bằng JSON thực tế:

```powershell
python scripts/configure_dvc_drive.py --client-json "C:/Users/admin/Downloads/dvc-desktop-client.json"
dvc push -r team
```

Helper chỉ lưu client ID/secret trong `.dvc/config.local` đã gitignore, không in giá trị. Collaborator tải bằng `dvc pull`; collaborator phụ trách dữ liệu có Drive Editor có thể phát hành phiên bản bằng `dvc push` theo quy trình review bên dưới. OAuth user tokens được DVC lưu ngoài Git trên từng máy; không chia sẻ tokens. Nếu vẫn bị chặn, kiểm tra đúng client Desktop, đúng Test user và chính sách tài khoản trong Google Console trước khi thử lại.

## Tải đúng dữ liệu của checkout

Sau khi có quyền Drive/OAuth và người quản lý đã upload:

```sh
git pull --ff-only
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite.dvc
python scripts/check_shared_data.py
```

SQLite là lựa chọn thông thường. ZIP dùng để đối chiếu/export:

```sh
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.zip.dvc
python scripts/check_shared_data.py --format zip
```

Replay source/calendar/audit cần toàn bộ raw captures:

```sh
dvc pull data/raw.dvc
```

`dvc pull` không có target tải tất cả ba pointers. DVC kiểm tra content hash; script dự án kiểm tra thêm SHA256 receipt, cấu trúc và metadata. Cùng hash không có nghĩa G1 đã pass.

## Phát hành phiên bản mới

Collaborator phụ trách task dữ liệu tạo tên snapshot mới bằng scripts export hiện có; giữ bytes gốc và không ghi đè phiên bản cũ. Sau khi kiểm tra cả hai định dạng:

```sh
dvc add data/raw data/share/<new-snapshot>.sqlite data/share/<new-snapshot>.zip
dvc status
dvc push -r team
```

Thay placeholders bằng đường dẫn mới thực tế. Upload phải thành công trước khi publish Git pointers. Kiểm tra bằng checkout riêng có cache trống: `dvc pull`, rồi chạy `check_shared_data.py` đối chiếu receipts của cùng commit. Stage `.dvc`, `.gitignore` liên quan, `.sha256`, receipts và tài liệu trong cùng PR; không stage SQLite/ZIP/raw bytes. Không upload từ CI tự động.

## Đổi phiên bản và dọn local

Sau khi giữ/commit các thay đổi đang làm, chuyển sang Git branch/tag/commit cần tái lập rồi chạy `dvc pull`. Không lấy pointer của một commit ghép với receipt của commit khác. `dvc checkout` chỉ phục hồi từ cache local; `dvc pull` lấy thêm dữ liệu từ remote nếu thiếu.

Có thể xóa bản SQLite/ZIP local đã upload và kiểm tra phục hồi thành công, rồi tải lại bằng pointer tương ứng. Raw captures và cache cũng chỉ dọn sau khi đã có bản remote được xác minh. Không chạy `dvc gc --cloud` trong thư mục dùng chung: lịch sử Git vẫn có thể cần những object đó. Việc bỏ binary khỏi commit hiện tại không xóa binary trong lịch sử Git cũ.

## Kiểm tra không cần Google

```sh
python scripts/check_dvc_roundtrip.py
```

Script tạo repo/cache/remote tạm với bytes giả, kiểm tra upload, clone trống, tải hai phiên bản và khôi phục lịch sử. CI job `dvc-local` chạy cùng kiểm tra trên Linux; tests dữ liệu và Docker không cần Google credentials. Docker dùng dữ liệu host đã `dvc pull`, xem [runbook](Docker_Runbook.md).

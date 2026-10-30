# VN30 Inference Studio

Dashboard local cho **Kronos-mini/small/base SFT**. Dark theme và tiếng Việt mặc định; có light/dark và VI/EN toggle. Dùng shadcn/ui preset **`b3DpibPrn6`** (Radix Lyra, neutral, Inter, JetBrains Mono).

Demo dùng dữ liệu lịch sử VN30 và các checkpoint selected epoch 5/seed 42 của lượt PC. Không có dữ liệu live, upload CSV, training hoặc dịch vụ inference trả phí. Dữ liệu mẫu VNDIRECT vẫn có giới hạn kiểm toán; dashboard là công cụ thử model, không phải bằng chứng mới trong báo cáo nghiên cứu.

## Chạy trên Windows

### Dùng gói ZIP đã đóng sẵn

1. Giải nén `VN30-Inference-Studio.zip` vào một thư mục riêng; giữ toàn bộ cấu trúc bên trong.
2. Cài Python **3.11** nếu máy chưa có.
3. Lần đầu, mở PowerShell tại thư mục đã giải nén:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\demo\setup.ps1
```

Setup tạo `.venv-demo` riêng. Nó kiểm CUDA driver để chọn PyTorch CUDA 13.0 hoặc CPU; không thay driver. Cần internet tải thư viện một lần. Có thể chọn rõ `-Compute cpu` hoặc `-Compute cu130`. Bản CUDA đã dùng trên PC hỗ trợ kiến trúc RTX 3050; chưa có phép đo trên laptop thực tế, và benchmark laptop được bỏ theo yêu cầu người dùng.

4. Nhấp đúp **Start-Dashboard.cmd**. Trình duyệt mở khi server sẵn sàng tại `http://127.0.0.1:8000`.
5. Chọn model/mốc lịch sử, nhấn **Chạy dự báo**. Đóng cửa sổ server hoặc nhấn Ctrl+C để dừng.

Nếu cổng 8000 đã dùng hoặc muốn ép CPU:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\demo\start.ps1 -Port 8001 -Cpu
```

Gói đầy đủ chứa ba predictor và hai tokenizer nên không cần đăng nhập HF để chạy, không cần Node/Docker, và có thể chạy offline sau khi cài dependencies. Một model/job dùng GPU tại một thời điểm. CUDA không có hoặc OOM thì replay cả lượt trên CPU; UI hiển thị thiết bị thực tế. Tốc độ phụ thuộc máy, không giả lập forecast khi lỗi.

## Dùng từ Git checkout trên PC phát triển

Weights, môi trường, node_modules và frontend build không được commit. Chuẩn bị từ artifact PC hiện có:

```powershell
.venv-demo/Scripts/python.exe -m demo.prepare
pnpm --dir demo/frontend install --frozen-lockfile
pnpm --dir demo/frontend build
.venv-demo/Scripts/python.exe -m demo.run --open-browser
```

Sau khi model được đăng HF, registry khóa repo/revision để runtime có thể tải weights còn thiếu, xác minh SHA256 và cache vào `demo/cache/hub`. Tokenizer luôn có ID/revision/hash riêng. Không tải model hoặc code theo URL do browser cung cấp.

## Dữ liệu và đầu ra

- Mẫu CSV gồm 470 phiên trích nguyên giá/ngày từ snapshot gốc, đủ 323 origin test. Manifest giữ hash nguồn và hash CSV mẫu. Không mang SQLite/raw hoặc source files nhúng vào app.
- Mỗi origin chỉ gửi **128 phiên OHLC đã biết** và **20 ngày phiên đích đã quan sát** vào predictor. Không có giá tương lai trong model input.
- Giá thực tế sau origin được lấy bằng endpoint đối chiếu riêng khi bật toggle, mặc định tắt.
- Inference: FP32, seed 42, mean ba path, temperature 1, top-p 0,9. Chọn 1/5/20 phiên trên biểu đồ chỉ thay phần hiển thị, không đổi lượt sinh path 20.
- CSV tải xuống chứa model, origin, ngày đích, bước, OHLC dự báo, seed và thiết bị. Ngày ISO, số thập phân dùng dấu chấm; UI định dạng theo VI/EN.
- Không sửa output High/Low để tạo nến có vẻ hợp lệ; biểu đồ chính là các đường Open/Close. Không suy lợi nhuận giao dịch từ demo.

## Hugging Face

Ba model repo công khai được người dùng chọn dưới namespace **neikhn**:

- `neikhn/kronos-mini-vn30-sft`
- `neikhn/kronos-small-vn30-sft`
- `neikhn/kronos-base-vn30-sft`

Không tạo Space, không gọi hosted Inference API. Upload chỉ gồm weights/config/card/license/provenance/spec đã chuẩn bị; không có raw dữ liệu, optimizer hoặc token.

```powershell
# Review-only, không upload:
.venv-demo/Scripts/python.exe -m demo.publish_models
# Chỉ thực hiện sau đăng nhập HF cục bộ:
.venv-demo/Scripts/python.exe -m demo.publish_models --namespace neikhn --visibility public --upload
```

Token đăng nhập chỉ cần quyền Write; không nhập token vào source code hay chat. Registry lưu revision do upload trả về. Model card ghi rõ nguồn pretrained, tokenizer, lựa chọn validation và phạm vi thăm dò.

## Kiểm thử và đóng gói

```powershell
.venv-demo/Scripts/python.exe -m unittest discover -s demo/tests -v
.venv-demo/Scripts/python.exe -m demo.smoke
# Cần server local đang chạy và Chrome:
pnpm --dir demo/frontend exec playwright test
.venv-demo/Scripts/python.exe -m demo.build_bundle
```

Kiểm API bao gồm hash, slicing, queue tuần tự, replay OOM sang CPU và CSV. Native smoke chạy thật ba model trên PC hiện tại, kiểm đủ path/hữu hạn/lặp seed; CPU mini có kiểm riêng. Browser test kiểm bốn tổ hợp theme/language, persistence, inference thật, actual toggle, CSV và mobile không tràn ngang. Đây là functional checks trên PC; **không phải benchmark RTX 3050**.

Gói nằm tại `demo/bundle/VN30-Inference-Studio.zip`, có manifest SHA256; không chứa venv/node_modules, credentials hoặc dữ liệu nghiên cứu cũ. Code Kronos MIT có revision và normalized source hashes; license của thư viện/font frontend nằm trong `licenses/`.

# Dashboard inference VN30 — kế hoạch triển khai

## 1. Quyết định đã chốt

- Đây là phần demo phụ; không đưa dashboard hoặc kết quả benchmark demo vào báo cáo nghiên cứu.
- Dashboard inference chạy **local**. Hugging Face chỉ lưu ba model; không tạo Space, không dùng hosted Inference API, không mua PRO hay compute.
- Chỉ dùng snapshot VN30 mẫu và chọn origin lịch sử; không upload CSV, không gọi nguồn giá live trong v1.
- Dark theme mặc định, có light/dark toggle. Tiếng Việt mặc định, có VI/EN toggle. Lưu hai lựa chọn riêng trong localStorage; lần đầu dùng dark/VI, không tự theo hệ điều hành.
- React + TypeScript + Vite, shadcn/ui đúng **preset `b3DpibPrn6`**. Dùng CLI chính thức để decode và init preset; giữ cấu hình/component tokens được tạo, không đoán lại palette. Khóa phiên bản dependencies sau khi build đạt.
- Scope model v1: **Kronos-mini/small/base SFT**, selected checkpoint full-budget seed 42 từ lượt PC. Cả ba selected hiện là epoch 5. Small mặc định; không chọn seed/checkpoint bằng điểm test. Không thêm Chronos hoặc training vào dashboard.
- Làm trong thư mục `demo/`, commit riêng trên nhánh hiện tại theo quy ước repo. Không thêm/sửa Python trong frozen `src/` và `scripts/`, không sửa artifact nghiên cứu hoặc reset đồng hồ nghiên cứu.

## 2. Khả thi trên laptop RTX 3050

ASUS công bố biến thể G513QC có RTX 3050 Laptop **4GB GDDR6**. Người dùng đã yêu cầu **bỏ benchmark laptop**, tiến hành hoàn thiện demo và chỉ kiểm chức năng trên PC hiện tại. Không cần log laptop để bàn giao; không tuyên bố đã đo RTX 3050. Chưa kiểm RAM/driver/cấu hình thực tế của laptop.

Ba predictor FP32 hiện khoảng **500 MiB** weights; hai tokenizer khoảng **30 MiB** nữa. Dung lượng weights không bằng peak VRAM hoặc thời gian inference. Lượt benchmark training base trên PC ghi peak tensor allocated khoảng 2,54 GiB, không phải phép đo inference trên RTX 3050.

- Một model và một job hoạt động tại một thời điểm; khi đổi model, giải phóng model cũ trên GPU trước khi đưa model mới lên.
- Giữ context 128, path 20, FP32, mean ba path, temperature 1, top-p 0,9 và seed 42. Chưa thêm thanh chỉnh sampling/precision.
- Tự phát hiện CUDA bằng PyTorch thực tế. Khi CUDA không có hoặc OOM, chuyển toàn bộ job sang CPU một lần, hiển thị thiết bị thực tế; không trả forecast một phần hoặc âm thầm đổi số path/model.
- Môi trường demo riêng, wheel PyTorch tương thích driver laptop; không ép dùng CUDA wheel của PC nghiên cứu và không sửa driver tự động.
- Chỉ chạy functional checks trên PC: đủ 20 output hữu hạn, lặp seed, model switching, CPU fallback và UI. Không thực hiện chiến dịch benchmark laptop.
- Không ghi “đã chạy trên RTX 3050” hoặc cam kết số giây. Kiểm trên RTX 4070 không thay cho phép đo laptop đã được người dùng bỏ qua.

## 3. Giao diện và luồng sử dụng

Một trang gọn, responsive, gồm:

1. Header tên demo, nhãn “Thử nghiệm”, VI/EN toggle và light/dark toggle.
2. Bộ chọn mini/small/base SFT và origin trong danh sách test đủ context/path của snapshot. Mặc định small và origin hợp lệ mới nhất.
3. Tóm tắt mốc lịch sử và nút **Chạy dự báo / Run forecast**. Trạng thái thật: đang tải model, đang tính, hoàn tất hoặc lỗi; không dùng tiến độ giả.
4. Biểu đồ Open/Close bằng shadcn Chart/Recharts: lịch sử nét liền, dự báo nét đứt, vạch chia tại origin. Close mặc định; chọn h=1/5/20 chỉ thay phạm vi hiển thị của path 20 đã tính.
5. Toggle xem giá thực tế sau origin, mặc định tắt. Nhãn “Demo lịch sử”, ngày mốc và snapshot kết thúc 01/10/2026 luôn rõ ràng; không gọi đây là dự báo giá hôm nay.
6. Ba ô giá dự báo h=1/5/20, thời gian tính, thiết bị thực tế; bảng kết quả và nút tải forecast CSV. CSV giữ số/date máy đọc được; UI dùng Intl theo ngôn ngữ.

Dùng component có sẵn: Card, Select/Combobox, Button, Tabs, Toggle/Switch, Tooltip, Skeleton, Alert và Table. Tất cả nhãn, lỗi, tooltip, trạng thái rỗng và định dạng ngày/số đều đổi ngôn ngữ. Không thêm login, backtest, PnL, news hoặc dashboard quản trị.

## 4. Backend, dữ liệu và model packaging

- FastAPI phục vụ API và frontend đã build trên `127.0.0.1:8000`. Development dùng Vite proxy; bản laptop không cần Node/Docker để chạy giao diện đã build.
- Một inference worker tuần tự; UI khóa gửi lặp trong lúc job của nó đang chạy. Hàng chờ tối đa ba job; quá tải trả lỗi bận có thể thử lại. Chạy backend một worker để tránh nhân bản model trong VRAM.
- API tối thiểu: danh sách model/origin, tạo job dự báo, đọc trạng thái/kết quả job, lấy giá thực tế để đối chiếu, health/device. Đầu vào inference chỉ gồm model ID trong registry và origin ID hợp lệ, không nhận đường dẫn checkpoint hoặc URL tùy ý từ trình duyệt.
- Registry khóa model repo/revision, weight SHA256, tokenizer ID/revision, source revision, epoch/seed và cấu hình inference. Hỗ trợ weights local trước khi xuất bản và tải từ Hub sau khi có repo ID; cache trên đĩa để lần sau chạy offline.
- Lấy 128 OHLC phiên tới origin và 20 ngày phiên kế tiếp từ lịch đã quan sát của snapshot. Model không nhận giá tương lai; giá thật được lấy qua luồng đối chiếu riêng. Không tự dựng ngày nghỉ hoặc dự báo ra ngoài dữ liệu lịch sử trong v1.
- Demo dùng bản mẫu tối thiểu cần thiết, có manifest/hash/nguồn và nhãn dữ liệu còn chưa xác minh. Không đọc checkpoint cũ ở môi trường khác; không tự sửa OHLC để vẽ nến đẹp. Biểu đồ chính dùng Open/Close lines.
- Nếu đóng gói lại CSV mẫu từ SQLite, xác minh từng giá và ngày với snapshot; không đóng gói raw ZIP, SQLite nhúng source files, credentials hoặc optimizer/RNG vào app.
- Khi chạy, model được gọi qua Kronos code đã khóa và loader demo riêng; không sửa adapter nghiên cứu vốn ràng buộc dataset/split. Giữ MIT attribution.

## 5. Hugging Face chỉ lưu model

Chuẩn bị ba model repo độc lập, tên dự kiến `<HF_USER>/kronos-{mini,small,base}-vn30-sft`; có thể gom bằng Collection. Đây là lựa chọn để mỗi variant có model card/revision/tokenizer riêng, không phải vì Hub cấm nhiều model trong subfolder.

Mỗi gói gồm `model.safetensors`, config, model card, inference specification và provenance đã loại đường dẫn host không cần thiết. Card ghi base revision, tokenizer, snapshot hash, seed 42/epoch 5, giới hạn dữ liệu và trạng thái thăm dò; không quảng bá vượt Naive hoặc model tốt nhất thị trường.

Kiểm export/import local và hash trước; giữ HF repo/revision do upload trả về vào registry. Chỉ upload weights đã chọn, không đưa toàn bộ ba seed, optimizer, raw dữ liệu hoặc môi trường lên Hub. Token chỉ dùng qua đăng nhập cục bộ, không vào Git/browser bundle.

Người dùng đã chốt namespace **neikhn**, **public**, cả ba mini/small/base. Danh sách payload/model cards đã chuẩn bị, không cần hỏi lại quyền xuất bản các model này. Công cụ đăng nhập cũ gặp lỗi whoami 400; đã chuyển sang HF CLI mới trong môi trường riêng và đăng nhập browser thành công. Không lưu token/OAuth vào repo/log. Không thực hiện đăng ký hay dịch vụ trả phí. Lưu model trên Hub không tự tạo API inference cho Kronos.

## 6. Thứ tự triển khai và nghiệm thu

1. **Chuẩn bị:** decode preset bằng CLI; chốt frontend lock, demo dependencies, registry và export ba selected checkpoint. Kiểm GPU/CPU trên PC, không chạy lại training.
2. **Luồng inference local:** slicing dữ liệu, job API, model switching và cache; đối chiếu output trực tiếp với lời gọi Kronos cùng cấu hình/thiết bị.
3. **Giao diện:** xây một trang, bốn tổ hợp theme/language, chart, bảng, CSV và trạng thái load/lỗi/thiết bị.
4. **Kiểm thử/đóng gói:** script PowerShell khởi động một lệnh, frontend build sẵn, hướng dẫn cài môi trường/download model; kiểm native GPU/CPU, model switching, cache và giao diện trên PC hiện tại. Bỏ benchmark laptop theo chỉ dẫn mới nhất; không để đây là việc pending bắt buộc.
5. **Xuất bản model:** review gói cụ thể, chốt namespace/visibility rồi upload Hub; thử tải sạch bằng revision mới và chạy offline từ cache. Dashboard vẫn local, không deploy Space.

Kiểm thử trọng tâm:

- Thay OHLC sau origin không đổi tensor đầu vào/forecast với cùng cấu hình, thiết bị và seed; đúng 128 context/20 output/ngày phiên, không NaN/Inf.
- Từ chối hash/tokenizer/variant sai; không nhận origin thiếu path; model switch không để hai predictor trên GPU.
- Job bận/lỗi tải model/OOM không giả forecast thành công; CPU fallback ghi thiết bị và lý do.
- Dark/VI mặc định ngay lần render đầu; toggle tồn tại sau reload, dịch đủ nhãn/lỗi và không làm mất kết quả.
- Chart nối đúng origin, phân biệt dự báo với thực tế; CSV khớp API; kiểm desktop và màn hình nhỏ.
- Không cam kết bit-identical giữa các kiến trúc GPU. Không đưa kết quả demo vào bảng nghiên cứu.

## Nguồn đã kiểm tra ngày 30/10/2026

- [ASUS G513QC/RTX 3050 4GB](https://rog.asus.com/ec/laptops/rog-strix/2021-rog-strix-g15-series/spec/?config=90NR0501-M01220).
- [shadcn CLI/preset](https://ui.shadcn.com/docs/cli).
- [HF storage: quota tài khoản, không có giới hạn 50GB/repo chung](https://huggingface.co/docs/hub/storage-limits).
- [HF Spaces: điều kiện gói trả phí cho Docker/Gradio và tài nguyên CPU Basic](https://huggingface.co/docs/hub/spaces-overview).
- [Kronos-base hiện không được Inference Provider triển khai](https://huggingface.co/NeoQuasar/Kronos-base).

Dashboard là công việc phụ mới, không reset hoặc gia hạn ngân sách 24 giờ của pipeline nghiên cứu.

## Trạng thái triển khai

- Đã decode/init đúng preset qua CLI, lưu components/theme/font chính thức và khóa pnpm dependencies.
- Đã xuất ba selected checkpoint, hai tokenizer, vendored code MIT và 470 phiên mẫu/323 origin; weights giữ local, không đưa vào Git.
- Backend đã chạy inference thật mini/small/base trên RTX 4070 SUPER, đủ 20 phiên; lặp seed sai khác 0 trên cùng PC; CPU mini đạt. Sáu unit/integration tests API/slicing/hash/queue/OOM/CSV đạt.
- Frontend build cuối đạt; Chrome E2E đã qua bốn theme/language, inference thật small/mini, actual toggle, CSV, persistence và mobile không tràn ngang. Đã xem ảnh desktop/mobile cuối; nhãn origin không bị cắt. Badge thử nghiệm có cả trên mobile.
- **Đã xuất bản:** `neikhn/kronos-mini-vn30-sft` revision `61d1824286f98bffa4cb63a88142d90b007b3328`; small revision `d7093271e98c939dcd30a0fec1cc87906d110844`; base revision `cb4301198abc5cbfa9ecb0ff2064e7c7ac410a2a`. Registry khóa cả ba; tải sạch không đăng nhập và xác minh hash config/weights đạt, chạy offline từ cache mới cả ba đạt (`demo/checks/hub_models.json`). Chuẩn bị lại export giữ repo/revision cũ khi weights không đổi.
- **ZIP đã đóng và thử:** `demo/bundle/VN30-Inference-Studio.zip`, 518.705.873 bytes, SHA256 `075023c229fe6c9c353c763f66376797cf2dec166bd143145625cc7f30d21295`. Có frontend build, ba predictor, hai tokenizer, license và bộ cài/chạy; không venv/node_modules/credentials/raw/optimizer. Kiểm đủ 66 member hashes, giải nén sang thư mục riêng, chạy API/frontend/mini inference/CSV khi tắt mạng đạt (`demo/checks/portable.json`).
- PowerShell syntax và nhận diện server đang chạy đạt. Preview local 127.0.0.1:8000; sau reboot chạy `Start-Dashboard.cmd`. Sáu test cuối sau khi registry public đạt; ca thiếu weights được thiết lập rõ là unpublished để không vô tình tải mạng.
- **Nghiệm thu dashboard v1: hoàn thành trên PC.** Benchmark laptop được bỏ theo yêu cầu, không phải việc pending. Nghiên cứu vẫn giữ audit unverified; không chuyển kết quả demo vào báo cáo hoặc gia hạn ngân sách nghiên cứu.

# Slide nghiên cứu VN30

Bài trình bày **20 slide** theo mẫu Paper & Ink, nhóm **1nsider**: Vi Nguyễn Ngọc Châu và Nguyễn Hoàng Kiên.

## Mở và trình chiếu

- Mở **vn30-paper-ink.html** bằng Chrome hoặc Edge. File đã nhúng thư viện, font và biểu đồ, dùng được offline, không cần cài Python/Node hay chạy server.
- Cuộn chuột/trackpad để đọc. **Tab** chuyển slide tiếp theo, **Shift+Tab** quay lại. **F** bật toàn màn hình, **S** mở ghi chú cho người thuyết trình.
- Có thể mở thẳng một trang, ví dụ thêm `#/q1-close` để tới slide 11 hoặc `#/ket-luan` để tới kết luận. Bỏ hash để mở lại từ đầu.
- **vn30-paper-ink.pdf** là bản tĩnh 20 trang, tỷ lệ 16:9, tiện gửi và xem trên máy khác. Ghi chú thuyết trình chỉ nằm trong HTML.

HTML giữ nền giấy có hạt nhẹ và bóng của mẫu. PDF bỏ hiệu ứng hạt/bóng để chữ, bảng và biểu đồ sắc nét, dung lượng nhỏ. Nội dung và số liệu của hai bản giống nhau.

## Nội dung và góp ý

Nguồn là báo cáo thực nghiệm và CSV đã kiểm định. Bìa giữ đúng project và thành viên trong dàn ý. Bản V2 giải thích baseline, kiến trúc Kronos, forecast origin, sampling/quantile, epoch, quantize, p90 và fold trước khi đọc kết quả. Source boundary giữ trong notes. Dashboard là phần riêng.

Thuật ngữ thống nhất: **pre-trained, encode, decode, weight, train, inference, predict, tokenizer, quantize**. Tokenization là toàn bộ quá trình tạo token, quantize là một bước trong đó. Ví dụ giải thích có nhãn minh họa; ví dụ Open ngày 21/05/2025 là dữ liệu thật đã đối chiếu prediction CSV.

Bạn có thể ghi số slide và cụm từ muốn giải thích hoặc sửa trong `slide-outline.md`. Các REVIEW gốc được giữ cùng ghi nhận đã xử lý. Khi chỉnh, cần cập nhật nguồn dựng và xuất lại hai bản để tránh lệch nội dung.

## Dựng lại

`build_deck.py` chỉ đọc CSV/Markdown đã có, không train hoặc chạy inference. Bảng là HTML, biểu đồ dữ liệu là SVG sửa được, font/thư viện đã khóa trong `vendor/`. `build_manifest.json` ghi hash nguồn và HTML.

```powershell
.venv-demo/Scripts/python.exe docs/slides/build_deck.py
# Chrome và package Playwright từ môi trường frontend có sẵn:
node docs/slides/check_deck.mjs --pdf
```

Script kiểm tra HTML, điều hướng và xuất PDF khi có `--pdf`. Ảnh/receipt kiểm tra nằm trong `.cache/slides-qa/`, không phải tài liệu thuyết trình. Mọi sửa chữa phải giữ giới hạn 20 slide, tên nhóm/thành viên và phân biệt SFT best-trained với lựa chọn có xét epoch 0.

Thư viện: reveal.js 5.1.0, MIT. Font Be Vietnam Pro và IBM Plex Mono, SIL Open Font License. Giấy phép có trong `vendor/` và file HTML.

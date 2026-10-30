# Điều tra bổ sung dữ liệu VN30 — 30/10/2026

Trạng thái: **bằng chứng từng phần; dataset vẫn unverified**. Không có giá nào được sửa. Tài liệu này bổ sung audit tự động, không thay biên bản chấp nhận dữ liệu.

## Close và bản tin độc lập

Audit phát hiện 60 ngày Close khác giữa VNDIRECT và ít nhất một trong VPS/DNSE. Helper đã thử tìm bản tin Pinetree cho cả 60 ngày: 46 URL không tải được ở lượt kiểm tra, 14 có raw HTML. Lỗi tải không chứng minh bản tin không tồn tại ở URL khác.

- Kết quả lần đầu: 6 bản tin hỗ trợ giá gốc, 8 chưa xác nhận rõ ngữ nghĩa Close.
- Sau khi bổ sung cách nhận diện cụm “khép phiên”, phân tích lại 14 raw đã lưu, không tải lại: 7 bản tin hỗ trợ giá gốc, 7 chỉ có giá ứng viên chưa đủ ngữ nghĩa Close.
- Giữ nguyên kết quả lượt đầu ở `publisher_close_review/review.json`; lượt phân tích bổ sung ở `publisher_close_review/cached_reparse.json`. Mỗi trường hợp có ngày, URL, raw path và SHA256.
- Giá ứng viên trong bản tin 05/03/2021 là 1174,16, trùng VPS thay vì VNDIRECT 1173,83; ngày 24/03/2021 là 1167,49, trùng VPS thay vì 1165,61. Hai bảng này chưa tự động được coi là xác nhận Close. PDF CSI cũ ngày 05/03 ghi 1173,83 nhưng có nhãn hợp đồng tương lai cũ; cần kiểm tính cập nhật của từng bảng trước khi dùng để phân xử.

Hai PDF tải mới đã được đọc text và xem ảnh trang đầu:

| Phiên được mô tả | Nhà công bố | VN30 | Ý nghĩa |
|---|---|---:|---|
| 09/04/2020 | CSI | 697,85 | Hỗ trợ VNDIRECT; khác VPS 700,32 |
| 22/09/2020 | Phú Hưng, bản tin phát hành 23/09 | 852,72 | Hỗ trợ VNDIRECT; khác VPS 853,68 |

URL, hash và thời gian tải của hai PDF cùng hai bản tin Pinetree bổ sung nằm trong `data/raw/source_evidence/pc-20261030/manifest.json`. Không đếm ngày phát hành PDF là ngày giao dịch nếu nội dung mô tả phiên trước.

Các trường hợp được hỗ trợ không chứng minh toàn bộ chuỗi Close đúng. Không chọn nguồn bằng đa số phiếu và không ghép từng ô giữa nhà cung cấp.

## Open và mốc chuyển hệ thống

Đoạn 05/05–11/08/2025 có 71 phiên liên tiếp Open VNDIRECT bằng Close phiên trước. Cùng đoạn: VPS 0/71, DNSE 5/71. Ngày bắt đầu trùng ngày hệ thống KRX vận hành. Đây là tương quan thời gian, **chưa phải nguyên nhân đã xác minh**.

Nguồn để tiếp tục truy vết:

- [Ủy ban Chứng khoán Nhà nước — vận hành hệ thống mới](https://ssc.gov.vn/webcenter/portal/ubck/pages_r/l/chitit?dDocName=APPSSCGOVVN1620154578).
- [VNDIRECT — phiên 05/05/2025](https://www.vndirect.com.vn/la-ban-thi-truong-05-05-2025-krx-chinh-thuc-van-hanh/).

Chưa dùng các thông báo này để sửa giá, gán lỗi parser hoặc kết luận nguồn nào phản ánh đúng Open. Cần xác minh định nghĩa nến và vì sao hiện tượng kết thúc sau 11/08.

## Điều kiện chưa giải quyết

1. Ngữ nghĩa và bằng chứng cho các chênh lệch O/H/L/Close còn lại.
2. Calendar độc lập đầy đủ; không lấy tập ngày trong chính bảng VN30 để làm chuẩn.
3. Cơ chế adjudication truy vết được trước khi chấp nhận có giới hạn; cổng audit hiện chưa tích hợp sổ phân xử.
4. Không có forecast, SFT hay kết luận Q1–Q4 mới trên dữ liệu này.

## Bổ sung sau khi bắt đầu nhánh thăm dò

Nhánh thăm dò đã bắt đầu SFT trên PC, có scope và output riêng; mục 4 ở trên mô tả thời điểm trước nhánh này. Vẫn chưa có kết luận Q1–Q4 chính thức.

Đã tải **VNINDEX**, không phải lấy lại tập ngày VN30, từ VPS và DNSE cho cùng giai đoạn. Ngày VN30 khớp toàn bộ ngày quan sát được của VNINDEX VPS. DNSE VNINDEX thiếu 33 ngày so với snapshot. Raw/CSV/URL/hash lưu ở `data/raw/source_evidence/calendar-vnindex-20261030/summary.json`.

Audit bổ sung nằm ở `calendar_crosscheck/audit/`: calendar ghi `pass` trong phạm vi khớp lịch quan sát từ VNINDEX VPS, không có ngày thiếu/thừa; metadata ghi rõ `official_exchange_calendar: false`. Đây chưa phải xác nhận lịch chính thức của sàn. Tổng 1.230 chênh lệch giá vẫn chưa phân xử, nên dataset vẫn `unverified`. Không thay audit đã khóa của lượt chính hoặc manifest thăm dò đang chạy.

Hai PDF Pinetree mới đã được đọc text và xem ảnh trang đầu: [05/03/2021](https://pinetree.vn/wp-content/uploads/2021/03/Market-brief_05032021_V.pdf) ghi VN30 1.174,16; [24/03/2021](https://pinetree.vn/wp-content/uploads/2021/03/Market-brief_24032021_V.pdf) ghi 1.167,49 trong bảng TTCK Việt Nam, tách với bảng hợp đồng tương lai. Các giá này hỗ trợ bảng HTML đã lưu, vẫn chưa giải quyết mâu thuẫn với nguồn khác. Manifest tải ở `data/raw/source_evidence/close-disputes-20261030/manifest.json`. Endpoint BSC đã thử trả nội dung không phải PDF; không dùng phản hồi đó như bằng chứng giá.

Kiểm thêm VPS cho thấy một phần chênh lệch O/H/L trùng Close phiên trước: trong 147 chênh Open, 73 giá VNDIRECT và 51 giá VPS bằng Close trước; trong 55 chênh High, các số tương ứng là 1 và 18; trong 169 chênh Low là 4 và 59. Đây là dấu hiệu cách dựng nến khác nhau để tiếp tục xác minh, chưa đủ để tự động phân xử hoặc sửa giá.

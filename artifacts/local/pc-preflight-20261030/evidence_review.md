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

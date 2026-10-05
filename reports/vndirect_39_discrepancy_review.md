# Kiểm tra đủ 39 sai khác OHLC — 05/10/2026

**Đã kiểm tra 39/39 trường trên 30 ngày. Bốn Close được bản tin cùng ngày hỗ trợ theo giá VNDIRECT; 35 Open/High/Low vẫn chưa có ground truth. G1 tiếp tục pending.** Đây là sai khác giữa nguồn, không phải 39 lỗi đã chứng minh của VNDIRECT.

## Cách kiểm tra và giới hạn

- Tái dựng từ raw đã kiểm tra SHA256; không sửa dữ liệu hoặc loại ngày bất lợi.
- Tải lại VNDIRECT/VPS/DNSE theo từng năm 2020, 2021, 2022, 2025, 2026, cắt ở 02/10/2026. Cả ba nguồn giữ nguyên giá tại mọi trường trong 39 trường. Điều này chứng minh tính lặp lại trong các cửa sổ đã thử, không chứng minh giá đúng.
- Đối chiếu raw KBS/VCI ngày 01/10/2026: có 38/39 trường. KBS tải mới bổ sung 02/10/2026 và giữ nguyên các trường 2026 đã có. VCI tải mới bị HTTP 403; đã lưu response lỗi, không giả định có dữ liệu mới.
- Nến có Open/Close ngoài [Low, High], số không hợp lệ hoặc ngày trùng không được coi là bằng chứng xác nhận. Không quyết định theo đa số; upstream của các nguồn chưa được chứng minh độc lập.
- Raw, normalized CSV của KBS/VCI cũ khớp khi tái dựng. Manifest cũ không có config hash và script capture hash khác script hiện tại; lần kiểm tra này ghim config/normalizer hiện tại, giữ hash gốc, không tuyên bố đã xác minh toàn bộ mã capture lịch sử.
- Các raw/PDF nằm trong `data/raw/` bị gitignore. Clone repo chỉ có biên nhận và bảng kết quả; replay offline cần nhận thêm đúng raw bytes từ người thực hiện.

## Giá Close đối chiếu được

| Case | Ngày | VNDIRECT | Comparator | Bản tin gốc, trang 1 |
|---|---|---:|---:|---|
| C01 | 2020-06-18 | 797.08 | DNSE 799.53 | [CSI/VNCS](https://vncsi.com.vn/data/data/anhpnh/files/ban-tin-thi-truong-ngay-18_06_2020.pdf) |
| C02 | 2020-07-15 | 810.16 | DNSE 812.62 | [CSI/VNCS](https://vncsi.com.vn/data/data/anhpnh/files/ban-tin-thi-truong-ngay-15_07_2020.pdf) |
| C14 | 2022-10-26 | 990.41 | DNSE 988.69 | [Pinetree](https://pinetree.vn/wp-content/uploads/2022/10/Market-brief_26102022_V-2.pdf) |
| C32 | 2021-03-05 | 1173.83 | VPS 1174.16 | [CSI](https://vncsi.com.vn/data/data/anhpnh/files/ban-tin-thi-truong-tuan-05_03_2021.pdf) |

Đã render và xem đầy đủ trang 1 của cả bốn PDF, kiểm tra nhãn VN30-Index/VN30 và ngày trên trang. Bản CSI 05/03/2021 có nhãn hợp đồng phái sinh cũ và dấu thay đổi cần thận trọng; chỉ dùng số Close VN30, không dùng bảng phái sinh hay dấu thay đổi. Đây là corroboration từ tài liệu công bố, chưa phải xác nhận của HOSE hoặc giải thích nguyên nhân sai khác. Kết quả 09/11/2022 trước đó là bổ sung ngoài mẫu 39 này.

## Bảng từng trường

Giá đơn vị điểm chỉ số. `!` = toàn bộ nến nguồn đó không hợp lệ, dù trường đang xem có thể trùng. `*` = KBS tải mới 05/10, không có trong capture 01/10. `—` = không có bằng chứng dùng được. Tất cả sai khác giữ nguyên sau truy vấn lại ba nguồn; tolerance vẫn 0.02.

| Case | Ngày | Trường | VNDIRECT | Nguồn so sánh | Giá so sánh | KBS | VCI | Kết luận / ghi chú |
|---|---|---|---:|---|---:|---:|---:|---|
| C01 | 2020-06-18 | close | 797.08 | DNSE | 799.53 | 797.08 | 797.08 | Bản tin cùng ngày hỗ trợ VNDIRECT Close; nguyên nhân sai khác chưa rõ. |
| C02 | 2020-07-15 | close | 810.16 | DNSE | 812.62 | 810.16 | 810.16 | Bản tin cùng ngày hỗ trợ VNDIRECT Close; nguyên nhân sai khác chưa rõ. |
| C03 | 2020-07-30 | open | 735.30 | DNSE | 735.16 | 735.16 | 735.30 | Chưa phân xử. DNSE/KBS Open bằng Close phiên trước; VNDIRECT/VPS/VCI khác. |
| C04 | 2020-07-30 | low | 735.30 | DNSE | 735.16 | 735.16 | 735.16 | Chưa phân xử. VNDIRECT Low cao hơn bốn nguồn khác; cần chuỗi intraday. |
| C05 | 2020-08-13 | open | 789.26 | DNSE | 788.42 | 788.42 | 788.42! | Chưa phân xử. DNSE/KBS hợp lệ; VPS/VCI Open < Low nên không được dùng để xác nhận. |
| C06 | 2020-08-13 | low | 789.26 | DNSE | 788.42 | 788.42 | 789.26! | Chưa phân xử. Low chia thành hai nhóm; VPS/VCI cùng ngày có nến không hợp lệ. |
| C07 | 2021-01-19 | open | 1173.27 | DNSE | 1173.34 | 1173.34 | 1173.27 | Chưa phân xử. DNSE/KBS Open bằng Close phiên trước; chưa xác định quy tắc Open. |
| C08 | 2021-06-17 | open | 1463.98 | DNSE | 1465.58 | 1463.98 | 1463.98 | Chưa phân xử. DNSE Open bằng Close phiên trước; các nguồn còn lại khác. |
| C09 | 2021-07-26 | open | 1397.01 | DNSE | 1396.45 | 1397.01 | 1397.01 | Chưa phân xử. DNSE Open khác các nguồn khác; chưa có giá mở cửa độc lập. |
| C10 | 2021-08-26 | open | 1432.37 | DNSE | 1432.02 | 1432.37 | 1432.37 | Chưa phân xử. DNSE Open khác các nguồn khác; chưa có giá mở cửa độc lập. |
| C11 | 2021-10-13 | open | 1512.73 | DNSE | 1512.70 | 1512.73 | 1512.73 | Chưa phân xử. Chênh 0.03, vẫn vượt tolerance 0.02; không tăng tolerance sau khi xem dữ liệu. |
| C12 | 2021-10-19 | open | 1512.10 | DNSE | 1510.78 | 1512.10 | 1512.10 | Chưa phân xử. DNSE Open khác các nguồn khác; chưa có giá mở cửa độc lập. |
| C13 | 2022-05-12 | high | 1339.25 | DNSE | 1349.82 | 1339.25 | 1339.25 | Chưa phân xử. DNSE High cao hơn 10.57; không thể giải thích bằng làm tròn hai chữ số. |
| C14 | 2022-10-26 | close | 990.41 | DNSE | 988.69 | 990.41 | 990.41 | Bản tin cùng ngày hỗ trợ VNDIRECT Close; nguyên nhân sai khác chưa rõ. |
| C15 | 2025-04-04 | open | 1269.06 | DNSE | 1221.15 | 1269.06 | 1269.06 | Chưa phân xử. DNSE thiếu 03/04/2025; không gán sai khác Open cho gap hay dịch ngày khi chưa có bằng chứng. |
| C16 | 2025-04-04 | low | 1208.42 | DNSE | 1216.27 | 1208.42 | 1208.42 | Chưa phân xử. DNSE Low khác các nguồn khác; cần intraday hoặc bảng OHLC chính thức. |
| C17 | 2025-05-13 | open | 1372.04 | DNSE | 1382.14 | 1372.04 | 1382.14 | Chưa phân xử. VNDIRECT/KBS Open bằng Close phiên trước; VPS/DNSE/VCI có Open khác. |
| C18 | 2025-05-13 | high | 1384.01 | DNSE | 1382.88 | 1384.01 | 1384.01 | Chưa phân xử. DNSE High thấp hơn các nguồn khác; chưa xác định cực đại đúng. |
| C19 | 2025-05-13 | low | 1370.29 | DNSE | 1371.11 | 1370.29 | 1370.29 | Chưa phân xử. DNSE Low cao hơn các nguồn khác; chưa xác định cực tiểu đúng. |
| C20 | 2025-06-20 | open | 1439.30 | DNSE | 1442.13 | 1439.30 | 1442.13 | Chưa phân xử. VNDIRECT/KBS Open bằng Close phiên trước; VPS/DNSE/VCI có Open khác. |
| C21 | 2025-06-20 | low | 1423.77 | DNSE | 1432.44 | 1423.77 | 1423.77 | Chưa phân xử. DNSE Low cao hơn 8.67; không suy ra từ gap/ATC. |
| C22 | 2025-09-18 | low | 1833.16 | DNSE | 1849.10 | 1849.10 | 1845.46 | Chưa phân xử. Có ba mức Low: 1833.16, 1845.46, 1849.10; không chọn theo đa số. |
| C23 | 2025-10-20 | open | 1968.92 | DNSE | 1966.80 | 1968.92 | 1968.92 | Chưa phân xử. DNSE Open khác các nguồn khác; chưa có giá mở cửa độc lập. |
| C24 | 2025-10-20 | high | 1977.14 | DNSE | 1972.81 | 1977.14 | 1972.81 | Chưa phân xử. VNDIRECT/KBS High khác VPS/DNSE/VCI; hai nhóm nguồn. |
| C25 | 2025-10-20 | low | 1868.69 | DNSE | 1870.86 | 1870.86 | 1870.86 | Chưa phân xử. VNDIRECT Low thấp hơn bốn nguồn khác; cần kiểm chứng ưu tiên. |
| C26 | 2026-04-16 | open | 1966.13 | DNSE | 1966.27 | 1966.13 | 1966.13 | Chưa phân xử. DNSE Open khác các nguồn khác; KBS tải mới vẫn giữ giá cũ. |
| C27 | 2026-07-29 | high | 1850.93 | DNSE | 1849.12 | 1849.12 | 1849.12 | Chưa phân xử. VNDIRECT High cao hơn bốn nguồn khác; cần kiểm chứng ưu tiên. |
| C28 | 2020-07-27 | high | 767.30 | VPS | 772.29 | 772.29 | 772.29 | Chưa phân xử. VNDIRECT/DNSE High 767.30; VPS/KBS/VCI 772.29. |
| C29 | 2020-11-02 | high | 900.03 | VPS | 899.94 | 900.03 | 899.94 | Chưa phân xử. VNDIRECT/DNSE/KBS High 900.03; VPS/VCI 899.94. |
| C30 | 2020-12-18 | open | 1017.99 | VPS | 1016.95 | 1016.95 | 1016.95 | Chưa phân xử. Bốn nguồn khác Open bằng Close trước; VNDIRECT có gap. Cả hai cách vẫn có nến hợp lệ. |
| C31 | 2020-12-18 | low | 1017.99 | VPS | 1016.95 | 1016.95 | 1016.95 | Chưa phân xử. VNDIRECT Low cao hơn bốn nguồn khác; cần chuỗi intraday. |
| C32 | 2021-03-05 | close | 1173.83 | VPS | 1174.16 | 1173.83 | 1174.16 | Bản tin cùng ngày hỗ trợ VNDIRECT Close; nguyên nhân sai khác chưa rõ. |
| C33 | 2025-06-16 | open | 1401.20 | VPS | 1394.58 | 1401.20 | 1394.58 | Chưa phân xử. VNDIRECT/KBS Open bằng Close trước; DNSE 1395.01, VPS/VCI 1394.58. |
| C34 | 2025-07-10 | open | 1543.27 | VPS | 1550.99 | 1550.99 | 1550.99 | Chưa phân xử. VNDIRECT Open bằng Close trước; bốn nguồn khác 1550.99. |
| C35 | 2025-08-05 | open | 1653.22 | VPS | 1676.20 | 1676.20 | 1676.20 | Chưa phân xử. VNDIRECT Open bằng Close trước; DNSE 1676.09, VPS/KBS/VCI 1676.20. |
| C36 | 2026-03-02 | low | 2009.13 | VPS | 2010.75 | 2010.75 | 2010.75 | Chưa phân xử. VNDIRECT Low thấp hơn bốn nguồn khác; cần kiểm chứng ưu tiên. |
| C37 | 2026-04-10 | low | 1921.38 | VPS | 1926.09 | 1915.01 | 1923.84 | Chưa phân xử. Bốn mức Low: VNDIRECT 1921.38, VPS/DNSE 1926.09, KBS 1915.01, VCI 1923.84. |
| C38 | 2026-06-05 | low | 1976.25 | VPS | 1976.85 | 1976.85 | 1976.62 | Chưa phân xử. Ba mức Low: VNDIRECT 1976.25, VPS/DNSE/KBS 1976.85, VCI 1976.62. |
| C39 | 2026-10-02 | low | 1865.78 | VPS | 1871.33 | 1871.33* | — | Chưa phân xử. KBS mới/VPS/DNSE Low 1871.33; VCI cũ chưa có ngày này, truy vấn mới HTTP 403. |

## Vấn đề cần ưu tiên

VNDIRECT Open bằng Close phiên trước tại **5/17 trường Open** đang tranh luận: C17, C20, C33, C34, C35. Kiểm tra toàn bộ capture phát hiện **71 phiên liên tiếp từ 05/05/2025 đến 11/08/2025** có Open bằng Close phiên trước: tháng 5 là 20/20, tháng 6 là 21/21, tháng 7 là 23/23 và tháng 8 thêm bảy phiên. Đây là dấu hiệu mạnh của việc carry-forward/quy ước dựng Open hoặc thay đổi feed theo giai đoạn, cần nhà cung cấp giải thích; chưa chứng minh nguyên nhân. Gap thực tế vẫn có thể bằng 0 nhưng không đủ để giải thích mặc định cả đoạn này. Không dùng quan sát này để sửa Open. Các thống kê theo tháng cho toàn bộ capture nằm ở `vndirect_monthly_open_diagnostic.csv`; đây là phân tích chẩn đoán thêm sau khi thấy sai khác, không thay mẫu đã đăng ký.

VNDIRECT cần được kiểm tra nghiêm túc ở C04, C25, C27, C31, C34–C39: giá khác nhiều nguồn, có trường High/Low và nhiều giá trị thay thế. C37 có bốn mức Low nên càng không thể coi một platform là chân lý.

Nến VPS/VCI 13/08/2020 có **Open 788.42 < Low 789.26**. Đây là bất nhất nội tại; gap, ATC hay đáo hạn không làm bất đẳng thức của cùng một nến trở nên hợp lệ. DNSE/KBS cùng ngày có Low 788.42 nên nến hợp lệ; sự hợp lệ đó vẫn chưa chứng minh quy tắc mở cửa đúng.

## Quyết định và việc tiếp theo

1. Giữ VNDIRECT là nguồn candidate; không chắp vá OHLC từ nhiều platform hoặc tăng tolerance sau khi xem mẫu.
2. Xin tài liệu định nghĩa Open/High/Low/Close của index và nguồn upstream; ưu tiên dữ liệu intraday/bảng OHLC chính thức cho 26 ngày còn vướng O/H/L. Có 30 ngày tổng, bốn ngày chỉ vướng Close đã được corroborate.
3. Nếu dùng một quy ước OHLC nhất quán của nhà cung cấp thay cho ground truth HOSE, phải ghi quyết định chất lượng dữ liệu và sửa tiêu chí G1 **trước freeze**, báo cáo sensitivity theo nguồn trên tập development. Không tự đánh dấu đạt theo đa số.
4. Đổi bài tham khảo/baseline không xử lý chất lượng dữ liệu. Không so trực tiếp điểm số giữa nguồn, tần suất, giai đoạn hoặc bộ biến khác nhau.

## Artifacts và replay

- `artifacts/source_audit/vndirect_39_cases_20261005/cases.csv`: 39 trường, giá của năm nguồn, flags hợp lệ, giá truy vấn lại, trạng thái bằng chứng.
- `candles.csv`: nến đầy đủ và phiên trước của các nguồn có trong captures gốc.
- `summary.json`: hashes, lỗi HTTP, số case và phân loại.
- `data/manifests/vndirect_39_publications_evidence.yaml`: URL, SHA256, giá/trang đã xem.

```powershell
tmp/ci-data-env/Scripts/python.exe -B scripts/investigate_vndirect_discrepancies.py --capture data/raw/source_investigation/20261005_39_repeat --output artifacts/source_audit/vndirect_39_cases_20261005
```

Không thêm `--fetch` khi replay. Capture mới cần thư mục mới; outputs đã ghi được bảo vệ khỏi ghi đè nội dung khác. Không có training, inference, test score hay accepted dataset được tạo ở bước này.

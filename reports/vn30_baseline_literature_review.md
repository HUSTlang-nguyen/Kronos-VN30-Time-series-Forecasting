# Review bốn tài liệu và đề xuất baseline — 05/10/2026

**Giữ Naive/ARIMA/ETS trong benchmark chung. Dùng Do–Nguyen làm related work chính về dự báo index hằng ngày; xem xét KTPCA ở nhánh mở rộng. Nguyen–Paientko phù hợp hơn Zhang để xây dựng một bài tái chạy ARIMA hằng ngày, nhưng chưa có căn cứ gọi venue của bài này uy tín hơn.** Đề xuất này chưa thay đổi study v4 hoặc các task đã chốt.

Đổi bài tham khảo không giải quyết 35 sai khác O/H/L còn chưa phân xử. Xem `reports/vndirect_39_discrepancy_review.md` trước khi freeze dataset.

## Phạm vi đã đọc

| Tài liệu | Bản đã kiểm tra | Vai trò đề xuất |
|---|---|---|
| Nguyen, Hung Long & Paientko, Tetiana (2024), *Forecasting the VN30 Index: Insights into Vietnam’s Stock Market Trends* | Full text và PDF nhà xuất bản; trang code/kết quả đã render | Daily ARIMA supporting replication |
| Dao, Thi Thanh Binh (2013), *VN30 Index: An Overview and Default Probability Analysis* | Metadata và abstract SSRN; chưa có PDF truy cập trực tiếp dùng được | Bối cảnh chỉ số |
| Pham Ngoc Hai, Hoang Trung Hieu & Phan Duy Hung (2022), *An Empirical Examination on Forecasting VN30 Short-Term Uptrend Stocks Using LSTM along with the Ichimoku Cloud Trading Strategy* | Abstract và metadata Springer; full chapter cần subscription | Related work về giao dịch cổ phiếu |
| Thanh Do Van & Hai Nguyen Minh (2021), *Forecast of the VN30 Index by Day Using a Variable Dimension Reduction Method Based on Kernel Tricks* | Full PDF EUDL; đối chiếu metadata Springer; trang 85/86/91 đã render | Daily-index method reference |

Biên nhận nguồn: `data/manifests/vn30_baseline_review_evidence.yaml`. Các PDF gốc được giữ ở raw và không đưa vào Git. Tên tác giả giữ theo publisher; tránh suy đoán họ/tên từ thứ tự viết tắt.

## 1. Nguyen–Paientko: phù hợp để tái chạy ARIMA

Journal *Strategies in Accounting and Management* 4(5), công bố 27/05/2024, DOI `10.31031/SIAM.2024.04.000598`. Dữ liệu Bloomberg; daily train 04/01/2022–07/07/2023 hoặc 18/06/2018–07/07/2023, test 10–14/07/2023. Daily ARIMA(0,1,0), Box–Cox, không constant; code R/fpp2. [Full text](https://crimsonpublishers.com/siam/fulltext/SIAM.000598.php).

Mạnh: ghi nguồn, ngày, code và prediction intervals. Yếu: chỉ một origin, năm phiên test; metric trong hình là training error. Coverage của khoảng rộng không chứng minh ưu thế point forecast. Mô hình random walk là đối chứng cần thiết, không phải baseline khó đánh bại mặc định. Monthly phần mô tả và code không hoàn toàn đồng nhất; code Figure 2 cắt train ở 12/2022. Không suy luận leakage từ mô tả monthly đơn thuần. [PDF, trang 5, 8–12](https://crimsonpublishers.com/siam/pdf/SIAM.000598.pdf).

Thay Bloomberg bằng VNDIRECT phải ghi **adaptation/approximate replication**. Không dùng bảng số gốc làm score so sánh cho nghiên cứu hiện tại.

## 2. Dao: không phải forecasting baseline

SSRN ghi bài viết 12/12/2013, đăng 28/12/2014. Nội dung bàn cấu trúc VN30 và xác suất vỡ nợ của doanh nghiệp bằng Z-score; không đưa mô hình dự báo giá index theo ngày. SSRN entry không đủ chứng minh công bố journal/conference qua phản biện. Chỉ dùng cho background; kết luận dựa trên abstract, không tuyên bố đã đọc full text. [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2543084).

## 3. Pham và cộng sự: khác target và metric

Conference chapter, *Communication and Intelligent Systems*, LNNS 461, trang 235–244, online 19/08/2022. LSTM dự báo khả năng outperform của **cổ phiếu thành phần**; mua ba cổ phiếu, giữ mười ngày. Abstract đánh giá lợi nhuận năm giai đoạn 2012–2020. Không phải VN30 Close MAE. [Springer](https://link.springer.com/chapter/10.1007/978-981-19-2130-8_19).

Muốn tái lập phải có full text, universe theo thời điểm, giá điều chỉnh, corporate actions, phí và timing khả dụng của feature. Không khẳng định bài mắc survivorship bias/leakage khi chưa đọc phương pháp. Nếu chuyển LSTM sang dự báo VN30 index thì đó là mô hình mới lấy cảm hứng, không phải reproduction bài này.

## 4. Do–Nguyen: khớp bài toán nhưng cần sửa protocol khi áp dụng

ICTCC 2021, LNICST 408, trang 83–94; Springer ghi first online 03/01/2022. [Metadata](https://link.springer.com/chapter/10.1007/978-3-030-92942-8_8).

Dataset 390 ngày, 25/01/2016–21/07/2017: VN30/cổ phiếu từ HSC, vàng/dầu/chỉ số quốc tế từ Yahoo. Train 385 ngày, test năm ngày. Phương pháp Pearson selection → KTPCA → dynamic factor regression → forecast factors. **KTPCA không đồng nhất với sklearn KernelPCA.** R² 0.993 và RMSE 4.328 mô tả fitted model, không phải rolling test score. [PDF, trang 85–91](https://eudl.eu/pdf/10.1007/978-3-030-92942-8_8).

Hạn chế: điền ngày nghỉ nước ngoài bằng trung bình ngày trước và ngày sau, tạo look-ahead nếu áp dụng online. Chỉ năm test points; lịch sử hiện có bắt đầu sau test của bài. Chưa đủ chi tiết để chứng minh PCA/selection chỉ fit train. Cần causal alignment, validation riêng và kiểm tra code gốc; không khẳng định bài tune trên test khi chưa có bằng chứng.

## Quyết định cho implementation plan

Các đề xuất dưới đây là thiết kế của dự án, không phải kết quả do các bài đã chứng minh.

| Phần | Đề xuất | Điều kiện |
|---|---|---|
| Core benchmark | Giữ Kronos-small, Chronos-2-small, Naive, ARIMA, ETS, DLinear-C, Ridge-OHLC như study v4 | Chạy cùng nguồn, origins và targets |
| E0 / T030 | Đề xuất chuyển anchor từ Zhang monthly sang daily ARIMA của Nguyen–Paientko | Sửa study/plan/checklist/protocol đồng bộ trước chạy; giữ bản Zhang cũ làm evidence |
| Daily-index related work | Đặt Do–Nguyen là tham chiếu phương pháp phù hợp | Nêu rõ information budget và hạn chế protocol |
| Kernel baseline | Optional extension sau core; triển khai đúng KTPCA nếu có mô tả/code đủ | Không gắn nhãn reproduction cho KernelPCA+Ridge |
| Dao / LSTM–Ichimoku | Background và adjacent research | Không lấy default-risk/portfolio return làm metric forecast index |

Thay E0 cần ghi model specification, phiên bản thư viện, Box–Cox và inverse transform, constant/drift, cách fit và evaluation dates. Có thể dùng đoạn lịch sử 2018–2023 tương ứng khi G1 đạt; nguồn khác Bloomberg đồng nghĩa approximate replication. Bài tái chạy này cần tách khỏi holdout phục vụ TSFM, xét provenance theo từng model, không dùng làm bằng chứng zero-shot ngoài training boundary.

Nếu thêm kernel baseline chỉ dùng OHLC128, đặt tên **adapted kernel/lag baseline**, công bố rằng nó khác bài gốc về input. Nếu tái lập phương pháp với dữ liệu ngoại sinh thì phải có thêm track exogenous cùng information budget cho mọi đối chứng. Không so một mô hình có thêm dữ liệu vĩ mô với model chỉ có OHLC rồi quy chênh lệch cho kiến trúc.

Protocol mọi mở rộng: fit scaler/feature selection/reduction trên train; chọn hyperparameters bằng validation theo thời gian; chỉ dùng dữ liệu thực sự có tại forecast origin. Với thị trường nước ngoài phải xét timestamp đóng cửa và múi giờ; dùng giá đã công bố gần nhất, không nội suy qua tương lai. Khóa quyết định trước test.

Các published scores chỉ ghi ở related work. MAE/RMSE/return errors/DA hiện tại phải tính lại trên common origins; R² fitted, portfolio annual return và coverage interval không thay thế primary Close MAE h=1. Nếu nghiên cứu intervals, báo cả coverage lẫn độ rộng/interval score theo một protocol riêng.

## Checklist đề xuất, chưa thay đổi hợp đồng nghiên cứu

- [x] Kiểm tra bốn tài liệu bằng nguồn publisher/author, ghi phạm vi full-text/abstract.
- [x] Tách target index, cổ phiếu thành phần và default probability.
- [x] Ghi nguồn Bloomberg/HSC/Yahoo được báo cáo; không suy ra dữ liệu của chúng ta tương đương.
- [x] Ghi caveat look-ahead, fitted/test metrics và reproducibility.
- [ ] Nếu chấp nhận đổi E0: version study mới, implementation plan, T002/T030 và manifest replication; bảo toàn v4.
- [ ] Trích protocol daily ARIMA mới và xác định vai trò supporting replication trước chạy.
- [ ] Chỉ thêm KTPCA sau khi có dữ liệu/phương pháp đủ và quyết định scope rõ.

Không có bằng chứng indexing/ranking đã được kiểm tra trong review này. Kết luận chọn baseline dựa trên độ khớp bài toán, protocol và khả năng tái lập; DOI hoặc tên publisher riêng lẻ không đảm bảo chất lượng nghiên cứu.

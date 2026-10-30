# Dự báo VN30 với Kronos mini, small và base

**Dàn ý để duyệt · 20 slide, gồm bìa và kết luận · 31/10/2026**

- **Người nghe dự kiến:** giảng viên hoặc nhóm nghiên cứu có kiến thức cơ bản về học máy và chuỗi thời gian. Đây là giả định để soạn dàn ý, có thể chỉnh khi duyệt.
- **Mục tiêu:** trình bày cách làm lại nghiên cứu trên PC, trả lời Q1–Q4 bằng kết quả đã kiểm định và nêu đúng giới hạn của bằng chứng.
- **Thời lượng đề xuất:** khoảng 20–25 phút, chưa chốt.
- **Ngôn ngữ:** tiếng Việt, giữ tên model và thuật ngữ cần thiết.
- **Định dạng theo mẫu:** slide HTML Paper & Ink, 16:9. Nền giấy ngà, chữ đen, Be Vietnam Pro và IBM Plex Mono, đường kẻ mảnh, bố cục thoáng. Cuộn dọc và Tab/Shift+Tab theo khung được cung cấp. Có thể xuất PDF sau khi dựng và kiểm tra.
- **Phạm vi bản này:** chỉ dàn ý Markdown để bạn duyệt. Chưa dựng slide HTML, PPTX hay PDF. Tổng số giữ tối đa 20, kể cả nếu bổ sung trang tài liệu hoặc phụ lục.
- **Nguồn chính:** [báo cáo PC ngày 30/10][R] và CSV/receipt của chính lượt PC. Dashboard là sản phẩm phụ riêng, không đưa vào nội dung nghiên cứu này.

**Thông điệp xuyên suốt:** các thí nghiệm thăm dò đã chạy và được kiểm định số học. Trong thiết lập này, neural model chưa vượt Naive một cách ổn định. Dữ liệu còn chưa được chấp nhận cho kết luận nghiên cứu chính.

**Quy ước khi dựng:** `-ft` là checkpoint tốt nhất **sau cập nhật**, còn `selected` cho phép chọn cả pretrained ở epoch 0 bằng validation. Điểm chính dùng MAE, đơn vị điểm chỉ số. Trung bình và SD giữa ba seed không phải khoảng tin cậy theo thị trường. Số liệu dưới đây dùng dấu phẩy thập phân.

## Slide 01 — Dự báo VN30 với Kronos mini, small và base

**Vai trò:** giới thiệu đề tài và phạm vi đánh giá.

**Nội dung:**

- Tiêu đề như trên, dòng phụ ngắn: “Đánh giá trên PC với baseline và Chronos-2-small”.
- Không tự thêm tên tác giả, trường, người hướng dẫn hoặc logo chưa được cung cấp.

**Visualize:** bìa chữ lớn theo mẫu, nền giấy ngà và một câu phụ, không có bảng hoặc hình dashboard.

**Nguồn và lưu ý:** [R]. Nêu phạm vi thăm dò ngay ở lời dẫn và slide 02, không biến bìa thành bảng trạng thái kỹ thuật.

> REVIEW:

## Slide 02 — Bốn câu hỏi nghiên cứu

**Vai trò:** giúp người nghe biết mỗi nhóm thí nghiệm trả lời vấn đề gì.

**Nội dung:**

- **Q1:** Kronos và Chronos so với Naive, Ridge, ARIMA, ETS như thế nào?
- **Q2:** kích thước model và lượng tử hóa representation ảnh hưởng ra sao?
- **Q3:** lượng dữ liệu và pretraining của predictor đóng góp như thế nào?
- **Q4:** kết quả ổn định đến đâu theo seed, horizon và giai đoạn thị trường?
- Một câu xác định phạm vi: “Kết quả thăm dò trên snapshot VN30 chưa được xác minh đầy đủ”.

**Visualize:** bảng bốn hàng, hai cột “Câu hỏi” và “Bằng chứng sử dụng”. Mỗi hàng gắn với nhóm slide kết quả tương ứng.

**Nguồn và lưu ý:** [R], [C]. Không đặt mục tiêu chứng minh model lớn hoặc SFT chắc chắn tốt hơn.

> REVIEW:

## Slide 03 — Cách Kronos xử lý chuỗi giá

**Vai trò:** giải thích representation trước khi nói về model và ablation.

**Nội dung:**

- Tokenizer mã hóa chuỗi nến thành biểu diễn rời rạc, predictor dự báo token, decoder khôi phục chuỗi giá.
- Zero-shot dùng trọng số có sẵn, SFT cập nhật predictor bằng tập train VN30 và giữ tokenizer cố định.
- Snapshot thiếu volume/amount, adapter điền 0. Đây là giới hạn đầu vào.

**Visualize:** sơ đồ một hàng có nhãn rõ: context OHLC và kênh phụ, encoder, lượng tử hóa, predictor, decoder, path giá. Đánh dấu phần cố định và phần cập nhật trong SFT bằng nét/nhãn, không dùng màu trang trí.

**Nguồn và lưu ý:** [R] mục 2 và 5, [K]. Sơ đồ mô tả luồng xử lý, không suy ra lợi thế dự báo từ kiến trúc.

> REVIEW:

## Slide 04 — Các model trong thực nghiệm

**Vai trò:** xác định ba Kronos và vai trò đối chứng của Chronos.

**Nội dung:**

- Kronos-mini khoảng 4,1M, small 24,7M, base 102,3M tham số.
- Mini dùng Tokenizer-2k, small/base dùng Tokenizer-base.
- Chronos-2-small khoảng 27,9M là model đối chứng tổng quát cho chuỗi thời gian, đã có trong bài VN30 cũ.
- Cả bốn có zero-shot và SFT. Toàn bộ checkpoint và kết quả trình bày lấy từ lượt PC mới.

**Visualize:** bảng bốn hàng với cột model, số tham số, tokenizer/cách biểu diễn và chế độ đánh giá.

**Nguồn và lưu ý:** [R], [P], [U]. Khác tokenizer khiến so mini với small/base không đo riêng tác động số tham số. Không so trực tiếp native loss giữa các họ model.

> REVIEW:

## Slide 05 — Snapshot VN30 và phân chia thời gian

**Vai trò:** giới thiệu dữ liệu và quy mô thực tế của tập đánh giá.

**Nội dung:**

- VNDIRECT, 2.271 phiên từ 24/08/2017 đến 01/10/2026, đơn vị điểm chỉ số.
- Train: 1.589 phiên, kết thúc 29/12/2023. Validation: 340 phiên, 02/01/2024–20/05/2025. Test: 342 phiên, 21/05/2025–01/10/2026.
- Số origin hợp lệ: train 1.442, validation 321, test 323. Origin là thời điểm phát dự báo sau Close của phiên t.

**Visualize:** timeline ba đoạn và bảng nhỏ “Số phiên / Số origin”. Hiện ngày biên, không chỉ ghi tỷ lệ 70/15/15.

**Nguồn và lưu ý:** [R] mục 1–2. Request từ 2012 nhưng nguồn chỉ trả từ 2017. Hàng 01/10/2026 ngoài request vẫn nằm trong snapshot được giữ để đối chiếu, không gọi là đã đạt phạm vi thu thập mong muốn.

> REVIEW:

## Slide 06 — Kiểm toán dữ liệu và điểm còn nghi vấn

**Vai trò:** đặt điều kiện diễn giải kết quả trước khi trình bày điểm số.

**Nội dung:**

- Raw replay, timestamp và SQLite integrity đã qua kiểm tra.
- Có 1.230 phép so sánh OHLC lệch hơn 0,02 điểm so với VPS/DNSE, gồm 60 ngày Close khác nguồn.
- Có 78 phiên Open bằng Close trước, trong đó 71 phiên liên tiếp từ 05/05 đến 11/08/2025.
- Chưa có đủ bằng chứng phân xử OHLC và lịch sàn chính thức. Dataset giữ trạng thái **unverified**, không sửa giá hoặc ghép nguồn theo từng ô.

**Visualize:** bảng “Đã xác minh / Còn thiếu bằng chứng” và một dải thời gian đánh dấu đoạn Open bất thường. Chi tiết từng trường chuyển vào notes.

**Nguồn và lưu ý:** [A], [D], [R] mục 1. 1.230 là số phép so sánh khác nhau, không phải số lỗi VNDIRECT đã chứng minh. Việc trùng mốc KRX chỉ là giả thuyết điều tra.

> REVIEW:

## Slide 07 — Quy trình dự báo và đánh giá chung

**Vai trò:** giải thích tính công bằng và cách tránh sử dụng nhãn tương lai.

**Nội dung:**

- Context 128 phiên, sinh path 20 phiên, chấm Open/Close tại h=1/5/20 bằng MAE và RMSE.
- Toàn bộ 20 nhãn của một origin phải nằm trong split tương ứng. Các model trong cùng bảng dùng cùng origin.
- Seed 42/43/44. Scaler và lựa chọn cấu hình không học từ test. Forecast được lưu trước khi ghép nhãn thật.
- Kronos lấy trung bình ba path, T=1 và top-p=0,9. Chronos lấy trung bình đều 13 quantile.

**Visualize:** một cửa sổ thời gian có 128 phiên quá khứ và 20 phiên đích, đánh dấu h=1/5/20. Bên dưới là quy trình train, chọn trên validation, chấm test đã khóa.

**Nguồn và lưu ý:** [R] mục 2. Quantile không phải mẫu ngẫu nhiên. Đây là đánh giá hồi cứu, dùng ngày phiên đích lịch sử đã biết, chưa chứng minh loại bỏ rò rỉ từ pretraining.

> REVIEW:

## Slide 08 — SFT và lựa chọn checkpoint

**Vai trò:** tách tác động fine-tuning khỏi quyết định chọn model sử dụng.

**Nội dung:**

- FP32, AdamW, LR chính 1e-6, tối đa năm epoch, effective batch 16, clipping 1,0. Tokenizer Kronos giữ cố định.
- Lưu checkpoint tốt nhất sau cập nhật và lựa chọn tốt nhất có xét epoch 0 pretrained.
- Ba Kronos chọn epoch 5 ở cả ba seed. Chronos chọn epoch 0 ở cả ba seed theo native validation.

**Visualize:** bảng bốn hàng “Model / Best-trained epoch / Selected epoch” và một chú giải ngắn về hai loại checkpoint. Không đặt native loss khác hệ lên cùng trục để xếp hạng.

**Nguồn và lưu ý:** [E], [S], [R] mục 4. Các bảng mang hậu tố `-ft` phía sau dùng best-trained; selected Chronos quay về zero-shot. Năm epoch không chứng minh hội tụ.

> REVIEW:

## Slide 09 — Baseline và lựa chọn trên validation

**Vai trò:** cho thấy baseline thống kê được triển khai và chọn cấu hình rõ ràng.

**Nội dung:**

- Naive giữ Close tại origin cho cả Open và Close tương lai.
- Ridge chọn alpha=10 trong lưới bốn giá trị. ARIMA chọn (0,1,0) trong 18 cấu hình, ETS chọn level trong ba cấu hình.
- ARIMA/ETS refit trên 128 phiên ở từng origin. Cấu hình lỗi hoặc thiếu coverage không được thắng lựa chọn, không thay ngầm bằng Naive.
- Tiêu chí validation tổng hợp MAE Open/Close tại ba horizon, chuẩn hóa bằng SD từng kênh trên train.

**Visualize:** bảng bốn baseline, quy tắc dự báo, lưới đã thử và cấu hình được chọn. Đưa 491 failed-origin fits của lưới ARIMA vào notes với đúng ngữ nghĩa.

**Nguồn và lưu ý:** [B], [R] mục 3. ARIMA và ETS đã chọn cho Close trùng forecast Naive, không tính ba nhãn thành ba bằng chứng độc lập.

> REVIEW:

## Slide 10 — Q1: Sai số Close trên test

**Vai trò:** trình bày kết quả chính để trả lời Q1.

**Nội dung:**

- Naive đạt MAE h=1/5/20 lần lượt 17,722 / 45,165 / 93,826 điểm.
- Kronos-base SFT đạt 21,234 / 54,709 / 98,849. Mini SFT đạt 20,127 / 50,188 / 108,490. Small SFT đạt 20,326 / 55,690 / 138,716.
- Chronos best-trained SFT đạt 20,104 / 48,198 / 99,976.
- Neural model chưa vượt Naive ở cả ba horizon xét trung bình ba seed trong bảng chính.

**Visualize:** bảng sáu hàng gồm Naive, Ridge, ba Kronos SFT và Chronos SFT, ba cột horizon. Giữ mean ± SD cho neural. Ghi chú ARIMA/ETS trùng Naive Close. Zero-shot được phân tích tiếp ở slide 12, đủ số liệu gốc trong notes.

**Nguồn và lưu ý:** [M], [R] mục 3. Nhãn `-ft` dùng best-trained theo slide 08, không gọi Chronos SFT là lựa chọn validation cuối cùng. Đây là kết luận trên snapshot và protocol đã thử.

> REVIEW:

## Slide 11 — Q1: Open và ảnh hưởng của đoạn bất thường

**Vai trò:** cho thấy lỗi dữ liệu có thể ảnh hưởng cách đọc một kết quả tốt.

**Nội dung:**

- Open h=1: Naive 5,959 điểm, ba Kronos SFT khoảng 9,806–10,466, Chronos SFT 20,671.
- Trong 323 origin h=1, có 59 nhãn đích nằm trong đoạn Open bất thường.
- Naive có Open MAE bằng 0 trên 59 nhãn đó, so với 7,291 trên 264 origin còn lại.
- Kết quả Open chưa đủ cơ sở đánh giá khả năng dự báo giá mở cửa chính thức.

**Visualize:** bảng Open h=1/5/20 cho Naive và bốn neural SFT, kèm một phần chú giải hai nhóm 59/264 origin và MAE tương ứng. Không thu nhỏ chữ để nhồi bảng toàn bộ 12 model.

**Nguồn và lưu ý:** [M], [R] mục 1 và 3. Đây là chẩn đoán theo đoạn bất thường đã phát hiện, không tạo một tập test mới để chọn model. Không diễn giải mọi trường hợp Open bằng Close trước là lỗi đã xác nhận.

> REVIEW:

## Slide 12 — Q2: Kích thước, tác động SFT và chi phí

**Vai trò:** so sánh ba Kronos mà vẫn giữ điều kiện diễn giải.

**Nội dung:**

- Close h=20 của base giảm từ 166,781 zero-shot xuống 98,849 sau SFT, cải thiện 67,932 điểm nhưng vẫn cao hơn Naive 93,826.
- Mini SFT có Close MAE thấp hơn small SFT tại cả ba horizon. Base SFT tốt hơn mini tại h=20 nhưng không tại h=1/5.
- Chi phí huấn luyện và peak tensor allocated tăng theo kích thước trong phép đo PC: mini khoảng 0,198 GiB, small 0,780 GiB, base 2,543 GiB.

**Visualize:** biểu đồ cặp zero-shot/SFT tại Close h=20 cho mini/small/base, đường tham chiếu Naive. Bảng chi phí ba hàng dùng số tham số, thời gian SFT đo được và peak tensor allocated.

**Nguồn và lưu ý:** [M], [U], [R] mục 5 và 8. Không gọi đây là quan hệ nhân quả thuần túy của số tham số vì mini khác tokenizer. Thời gian là đo trên RTX 4070 SUPER; VRAM tensor không phải tổng VRAM và không phải phép đo laptop hay inference.

> REVIEW:

## Slide 13 — Q2: Ablation lượng tử hóa có kiểm soát

**Vai trò:** cung cấp bằng chứng riêng về một thành phần representation.

**Nội dung:**

- Cùng encoder tokenizer small cố định, cùng backbone random, numeric head/MSE, dữ liệu, ngân sách và ba seed.
- So đặc trưng liên tục L2-normalized với đặc trưng sau lượng tử hóa BSQ.
- Close MAE h=1 gần bằng nhau ở mức 22,832. Tại h=5: continuous 66,015 và quantized 67,571. Tại h=20: 144,375 và 150,927.
- Chưa quan sát lợi ích đồng nhất của lượng tử hóa trong thiết lập này.

**Visualize:** sơ đồ hai nhánh chỉ khác bước lượng tử hóa, bên cạnh biểu đồ MAE ± SD theo ba horizon. Nhãn trục nêu rõ điểm chỉ số.

**Nguồn và lưu ý:** [Q], [R] mục 5. Chênh lệch mean chưa tự chứng minh ý nghĩa thống kê. Ablation này không tách mọi thành phần của K-line representation và không thay thế toàn bộ mô hình pretrained.

> REVIEW:

## Slide 14 — Q3: Lượng dữ liệu và predictor pretraining

**Vai trò:** trình bày learning curve và đối chứng khởi tạo ngẫu nhiên.

**Nội dung:**

- Train 500 / 1.000 / 1.589 phiên, các đoạn lồng nhau cùng ngày kết thúc, tương ứng 353 / 853 / 1.442 cửa sổ. Giữ validation và test cố định.
- Chronos pretrained có Close MAE thấp hơn random ở cả chín ô budget/horizon.
- Kronos-small cho kết quả không đồng nhất: random tốt hơn pretrained tại h=5/20 ở budget 1.000 và full.
- Ví dụ h=20 full: Kronos pretrained 138,716 so với random 117,220. Thêm dữ liệu không bảo đảm mọi horizon cùng cải thiện.

**Visualize:** hai learning curve cạnh nhau, một cho Kronos-small, một cho Chronos, cùng thang MAE Close h=20 nếu đọc được. Mỗi hình có hai đường pretrained/random, SD giữa seed và số cửa sổ tại từng mốc. h=1/5 đầy đủ trong notes.

**Nguồn và lưu ý:** [L], [LR], [R] mục 6. Random Kronos vẫn dùng tokenizer pretrained. Random chọn LR từ ba giá trị trên validation, pretrained dùng LR chính, nên tổng chi phí tìm cấu hình khác nhau. Kết luận trong ngân sách đã thử, không khẳng định random đã tối ưu đến hội tụ.

> REVIEW:

## Slide 15 — Q4: Khoảng bất định so với Naive

**Vai trò:** phân biệt chênh lệch điểm số với mức độ chắc chắn của kết luận.

**Nội dung:**

- Paired moving-block bootstrap trên chênh lệch absolute error cùng origin: block 20 origin, 2.000 lần lấy mẫu, CI percentile 95%.
- Chênh lệch âm nghĩa là MAE thấp hơn Naive. Khoảng cắt 0 chưa cho thấy khác biệt rõ trong phép kiểm này.
- Ví dụ seed 42, Close h=20: base SFT chênh 3,488, CI [−18,439; 26,387]; small SFT chênh 44,896, CI [13,737; 85,757].

**Visualize:** forest plot bốn model SFT ở h=1/5/20, đường dọc tại 0. Ghi rõ đây là **seed 42**, không giả CI tổng hợp ba seed. SD ba seed đã xuất hiện ở bảng điểm chính.

**Nguồn và lưu ý:** [I], [R] mục 7. Không bootstrap ba seed như ba thị trường, không lấy trung bình hai đầu CI để tạo CI chung. CI chưa điều chỉnh multiple comparisons và phụ thuộc lựa chọn block.

> REVIEW:

## Slide 16 — Q4: Giai đoạn test và mức biến động

**Vai trò:** kiểm tra tính ổn định theo thời gian và phạm vi các nhóm quan sát.

**Nội dung:**

- Chia test thành ba đoạn liên tiếp, 108 / 108 / 107 origin.
- Volatility là SD của 20 log-return đã biết tại origin, ngưỡng p90 chỉ lấy từ train.
- Có 17/323 origin volatility cao trong hai cụm, còn lại 306 origin bình thường.
- Thứ hạng và chênh lệch thay đổi theo giai đoạn, không có ưu thế chung ổn định trước Naive.

**Visualize:** timeline test có ba đoạn và đánh dấu hai cụm volatility, kèm biểu đồ chênh lệch MAE Close h=20 so với Naive theo từng đoạn cho bốn neural SFT. Số mẫu hiện ngay trên hình.

**Nguồn và lưu ý:** [V], [G], [R] mục 7. Regime dùng thông tin quá khứ tại origin, không dùng volatility tương lai. Hai cụm không đại diện nhiều khủng hoảng độc lập.

> REVIEW:

## Slide 17 — Q4: Hai expanding-window folds

**Vai trò:** kiểm tra khả năng giữ kết quả ở các giai đoạn hồi cứu khác nhau.

**Nội dung:**

- Fold 1 test 09/02–29/12/2023, fold 2 test 02/01–28/11/2024. Mỗi fold 208 origin, neural seed 42, train/validation riêng.
- Naive Close h=20: 40,009 ở fold 1 và 36,072 ở fold 2. Chưa có neural model thắng nhất quán qua horizon và hai fold.
- Chronos SFT nhỉnh hơn Naive ở fold 1 h=5: 22,213 so với 22,363, nhưng không giữ lợi thế ở fold 2.
- Cả hai fold có 0 origin volatility cao theo ngưỡng train riêng.

**Visualize:** timeline train/validation/test của hai fold, bên cạnh bảng chênh lệch MAE với Naive cho bốn model SFT tại h=1/5/20. Nhấn giới hạn coverage volatility bằng câu ngắn.

**Nguồn và lưu ý:** [F], [R] mục 7. Fold hồi cứu không chứng minh model pretrained chưa từng thấy giai đoạn đó. Các hàng `-ft` vẫn là best-trained như quy ước chung.

> REVIEW:

## Slide 18 — Khả năng tái lập và kiểm định kết quả

**Vai trò:** cho biết các con số dựa trên artifact nào và đã được kiểm tra đến đâu.

**Nội dung:**

- Khóa dataset/model/tokenizer/code revision và hash, lưu forecast trước khi chấm nhãn.
- Tính lại độc lập 2.160 dòng metric từ 182 forecast CSV và nhãn SQLite, kiểm 88 nhóm score.
- Kiểm lại 378 khoảng bootstrap, 1.782 metric theo nhóm/giai đoạn và checkpoint selection, không chỉ tin status “complete”.
- Giữ báo cáo, CSV, hình, receipts và lệnh tái lập. Kết quả cũ không đi vào bảng PC mới.

**Visualize:** chuỗi truy vết dữ liệu, checkpoint, forecast, metric, bảng/hình, báo cáo. Hai số kiểm định chính đặt nổi bật, không biến slide thành ảnh log hoặc danh sách lệnh dài.

**Nguồn và lưu ý:** [N], [T], [C], [R] mục 8 và 10. Kiểm đúng phép tính không chứng minh giá thị trường đúng. Resume GPU đã kiểm native mini; không mở rộng thành bảo đảm mọi variant. Chi tiết software tests đưa vào notes.

> REVIEW:

## Slide 19 — Giới hạn và việc còn thiếu

**Vai trò:** xác định phạm vi sử dụng kết quả và điều kiện cần để nâng mức bằng chứng.

**Nội dung:**

- Dữ liệu: tiếp tục phân xử OHLC/Open và lịch sàn chính thức, lập phiên bản riêng nếu có căn cứ hiệu chỉnh.
- Thiết kế: test đã được xem trước, cutoff/exclusions pretraining chưa xác minh đầy đủ, số cụm volatility cao ít.
- Ngân sách: tối đa năm epoch trong lượt chạy đã chốt, chưa chứng minh tối ưu/hội tụ của mọi đối chứng.
- Đánh giá: chưa có backtest giao dịch, phí giao dịch hoặc bằng chứng lợi nhuận từ sai số dự báo.

**Visualize:** bảng ba cột “Giới hạn / Ảnh hưởng kết luận / Việc cần làm”, tối đa bốn hàng. Không hứa có thêm dữ liệu hoặc nâng trạng thái audit khi chưa có bằng chứng.

**Nguồn và lưu ý:** [C], [P], [R] mục 9. Nếu dữ liệu thay đổi, phải kiểm lại các thí nghiệm phụ thuộc, không đổi nhãn checkpoint cũ thành model của dữ liệu mới.

> REVIEW:

## Slide 20 — Kết luận Q1–Q4

**Vai trò:** kết thúc bằng câu trả lời trực tiếp và bước ưu tiên tiếp theo.

**Nội dung:**

- **Q1:** chưa có lợi thế ổn định của neural model trước Naive trong thiết lập này.
- **Q2:** kích thước lớn và lượng tử hóa chưa cho lợi ích đồng nhất, SFT cải thiện rõ base tại Close h=20.
- **Q3:** lợi ích predictor pretraining phụ thuộc model và ngân sách, lượng dữ liệu thêm không cải thiện đồng đều.
- **Q4:** kết quả thay đổi theo horizon/giai đoạn, bằng chứng về volatility cao còn hạn chế.
- Ưu tiên tiếp theo: giải quyết bằng chứng dữ liệu trước khi chốt kết luận nghiên cứu chính.

**Visualize:** bốn dòng kết luận theo Q1–Q4 và một câu cuối trên thanh nhấn đen của mẫu. Chân trang có nguồn báo cáo/repo. Trang này cũng là điểm dừng trao đổi, không thêm slide Q&A thứ 21.

**Nguồn và lưu ý:** [R], [C]. Câu chốt: “Đã kiểm định kết quả thăm dò trên snapshot. Nghiên cứu chính còn chờ xác minh dữ liệu”. Không dùng dashboard hoặc việc upload HF làm bằng chứng chất lượng dự báo.

> REVIEW:

## Nguồn dùng khi dựng slide

Đây là danh mục trong file dàn ý, không phải slide bổ sung. Khi dựng, mỗi slide có nguồn ngắn ở chân trang, đường dẫn và giải thích đầy đủ trong speaker notes. Bảng/hình sinh từ CSV đã kiểm, không vẽ dữ liệu minh họa giả hoặc bê ảnh bảng chữ nhỏ từ báo cáo.

- [R] Báo cáo tổng hợp PC, nguồn diễn giải và giới hạn.
- [A] Audit snapshot, trạng thái dữ liệu.
- [D] Sổ chênh lệch và bằng chứng theo ngày/trường.
- [M] Bảng điểm chính Open/Close, validation/test, mean/SD/RMSE.
- [B] Lựa chọn baseline trên validation.
- [E] Lựa chọn epoch và checkpoint.
- [S] Điểm checkpoint selected có xét epoch 0.
- [Q] Ablation continuous/quantized.
- [L] Learning curve pretrained/random.
- [LR] Lựa chọn LR random trên validation.
- [I] Paired block bootstrap intervals.
- [V] Origin, giai đoạn và regime volatility.
- [G] Điểm tổng hợp theo giai đoạn/regime.
- [F] Kết quả hai expanding folds.
- [U] Số tham số và chi phí PC đo được.
- [N] Kiểm định độc lập forecast/nhãn.
- [T] Receipt kiểm định báo cáo cuối.
- [C] Ma trận nghiệm thu và phần còn thiếu.
- [P] Revision và provenance model/tokenizer.
- [K] Mã Kronos vendored đã pin, dùng giải thích luồng xử lý.

[R]: ../VN30_PC_Research_Report.md
[A]: ../../artifacts/local/pc-rerun-20261030/audit/summary.md
[D]: ../../artifacts/local/pc-exploratory-20261030/final-report/data_adjudication.csv
[M]: ../../artifacts/local/pc-exploratory-20261030/final-report/main_summary.csv
[B]: ../../artifacts/local/pc-exploratory-20261030/final-report/baseline_selection.csv
[E]: ../../artifacts/local/pc-exploratory-20261030/final-report/checkpoint_selection.csv
[S]: ../../artifacts/local/pc-exploratory-20261030/final-report/selected_scores.csv
[Q]: ../../artifacts/local/pc-exploratory-20261030/final-report/ablation_summary.csv
[L]: ../../artifacts/local/pc-exploratory-20261030/final-report/learning_curve.csv
[LR]: ../../artifacts/local/pc-exploratory-20261030/final-report/random_lr_selection.csv
[I]: ../../artifacts/local/pc-exploratory-20261030/final-report/paired_intervals.csv
[V]: ../../artifacts/local/pc-exploratory-20261030/final-report/origin_regimes.csv
[G]: ../../artifacts/local/pc-exploratory-20261030/final-report/regime_period_summary.csv
[F]: ../../artifacts/local/pc-exploratory-20261030/final-report/fold_scores.csv
[U]: ../../artifacts/local/pc-exploratory-20261030/final-report/resources.csv
[N]: ../../artifacts/local/pc-exploratory-20261030/review/numerical_validation.json
[T]: ../../artifacts/local/pc-exploratory-20261030/final-report/verification.json
[C]: ../../artifacts/local/pc-exploratory-20261030/final-report/completion_matrix.csv
[P]: ../../data/manifests/checkpoint_provenance.yaml
[K]: ../../demo/vendor/kronos/model/kronos.py

## Ghi nhớ mẫu và bước sau khi duyệt

- Mẫu gốc: `C:/Users/neikh/Downloads/paper-ink-slides.zip`, SHA256 `96e060255dddadaaf8c564757964d16dd123895a3fd3264bc4530b396e1a7264`.
- Dùng `paper-ink-slides/assets/deck.html` làm khung, cùng các mô tả design/outline/verification trong ZIP. Placeholder của mẫu không cung cấp dữ kiện nghiên cứu. Không cài skill hoặc chạy mã trong ZIP ở bước lập dàn ý.
- Nền `#f2f0e9`, chữ `#151610`, canvas 1920×1080. Giữ chữ đọc được, nguồn rõ, bảng/biểu đồ có thể chỉnh sửa. Không chuyển sang thiết kế dashboard hoặc thêm trang ngoài giới hạn 20.
- Khung hiện tham chiếu reveal.js/font qua CDN, cần Internet khi dùng nguyên bản. Quyết định đóng gói offline được xử lý ở bước dựng, không gọi bản CDN là tự chứa.
- Chờ bạn duyệt/chỉnh file này trước khi dựng. Đọc lại toàn bộ REVIEW và mọi chỉnh sửa trực tiếp của bạn ở lượt tiếp theo, giữ lịch sử góp ý cần thiết.

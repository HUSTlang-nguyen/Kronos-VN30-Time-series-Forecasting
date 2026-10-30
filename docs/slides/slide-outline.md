# Kronos-VN30-Time-series-Forecasting

**Dàn ý hiện tại · 19 slide · 31/10/2026**

Đã xóa slide 12 cũ (Q1 Open) theo yêu cầu và đánh lại số trang; BSQ ở slide 13, quantize ablation ở slide 14.

- Giữ Paper & Ink, nhóm **1nsider**, **Vi Nguyễn Ngọc Châu** và **Nguyễn Hoàng Kiên**.

- Thuật ngữ: **pre-trained, encode, decode, weight, train, inference, predict, tokenizer, quantize, baseline, validation, test, epoch**. Tokenization và quantize không đồng nghĩa.

- HTML offline và PDF cùng 19 slide. Chỉ sửa trình bày, không train thêm hoặc thay data/checkpoint/report/score. Q3 giữ small/Chronos.

- Source boundary và assumptions cần thiết trong notes; bỏ nhãn trạng thái, câu chuyện môi trường mới và hai trang kiểm định/giới hạn riêng khỏi phần trình chiếu.

- Giữ REVIEW gốc bên dưới, dùng các REVIEW theo số trang mới để góp ý tiếp.

## Slide 01 — Bìa

**Vai trò:** Nhận diện project và nhóm.

**Nội dung:** Kronos-VN30-Time-series-Forecasting. Nhóm 1nsider. Thành viên Vi Nguyễn Ngọc Châu, Nguyễn Hoàng Kiên.

**Visualize:** Bìa giữ nguyên tên project, nhóm và hai thành viên.

**Nguồn và lưu ý:** Thông tin người dùng cung cấp.

> REVIEW:

## Slide 02 — Bốn câu hỏi nghiên cứu

**Vai trò:** Nêu bốn câu hỏi bằng lời trực tiếp.

**Nội dung:** Baseline là phương pháp làm chuẩn so sánh. Q2 kiểm tra hai việc: so các hệ thống mini/small/base và thay riêng bước quantize trong ablation. Q4 kiểm tra MAE khi đổi seed, prediction horizon và giai đoạn test. Một model tốt ở một giai đoạn chưa chắc tiếp tục tốt ở giai đoạn khác.

**Visualize:** Bảng Q1–Q4 và experiment tương ứng, giải thích MAE ngắn.

**Nguồn và lưu ý:** Nguồn: Báo cáo thực nghiệm · Bảng kết quả Q1–Q4. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 03 — Baseline · Naive và Ridge

**Vai trò:** Giải thích Naive và Ridge trước cấu hình.

**Nội dung:** Naive không train và không nhìn target Open tương lai. Ridge thực tế dùng 128 × 4 OHLC features; scaler input và target chỉ fit trên train, output gồm 20 × 4 giá trị. Công thức Ridge: prediction = bias + tổng weight_i × feature_i. Alpha điều khiển regularization, tức hạn chế weight quá lớn; alpha = 10 được chọn trên validation từ 1/10/100/1000. Ví dụ giá 100/102 và weight 0,3/0,7 trên slide chỉ minh họa, không phải weight đã fit.

**Visualize:** Bảng Naive/Ridge, cách predict và ví dụ số có nhãn minh họa.

**Nguồn và lưu ý:** Nguồn: Adapter Ridge / Naive · baseline_selection.csv. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 04 — Baseline · ARIMA và ETS

**Vai trò:** Giải thích ARIMA và ETS.

**Nội dung:** ARIMA là AutoRegressive Integrated Moving Average. AR dùng lag của chuỗi, I là differencing, MA dùng error quá khứ. Trong cấu hình (0,1,0) không drift, prediction bằng giá trị cuối của kênh. ETS ở đây dùng exponential smoothing, thử level, additive trend và damped trend, không seasonal. Cấu hình level được chọn cho Close prediction trùng Naive trong experiment này. ARIMA/ETS fit Open riêng với Close; Naive dùng Close cho cả hai nên Open error không trùng. Lỗi convergence được ghi, không có fallback thay bằng Naive.

**Visualize:** Bảng ARIMA/ETS, thông tin dùng và cấu hình; giải thích Close trùng Naive.

**Nguồn và lưu ý:** Nguồn: statistical_baselines.py · baseline_selection.csv. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 05 — Kiến trúc Kronos

**Vai trò:** Giải thích kiến trúc và phần cập nhật khi SFT.

**Nội dung:** KronosTokenizer gồm encoder/decoder Transformer và Binary Spherical Quantization (BSQ). API encode thực tế gồm embed, encoder, quant_embed và quantizer rồi trả token IDs. Sơ đồ tách encode features và quantize để giải thích rõ vai trò. Predictor có hierarchical token embedding, temporal embedding, causal Transformer, s1 head và conditional s2 head. S2 phụ thuộc s1 trong cùng bước. Causal nghĩa là chỉ nhìn token quá khứ để predict token tiếp theo. Decode chuyển token về OHLC rồi khôi phục thang giá. Khi SFT, tokenizer giữ nguyên weight, predictor được cập nhật weight. Volume/amount thiếu được điền 0, không phải khối lượng giao dịch thực.

**Visualize:** Sơ đồ input, tokenization, Transformer, decode, output; bảng tokenizer/predictor và phần trainable.

**Nguồn và lưu ý:** Nguồn: KronosTokenizer / Kronos · Source revision đã khóa. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 06 — Kronos và các model còn lại

**Vai trò:** So model theo input, cách học, output và số tham số.

**Nội dung:** M là triệu tham số. Các baseline trong thiết lập này không dùng weight pre-trained từ tập dữ liệu lớn bên ngoài: Naive dùng quy tắc, Ridge/ARIMA/ETS fit theo dữ liệu VN30. Kronos được pre-trained cho chuỗi OHLC với tokenization. Chronos là đối chứng chuỗi thời gian tổng quát và trả quantile predictions. Mini dùng tokenizer khác small/base nên so mini với small/base không đo riêng tác động của số tham số. SFT trong bảng kết quả là best-trained; selected có thể giữ epoch 0. Không so native loss giữa các họ model khác nhau.

**Visualize:** Bảng baseline, ba Kronos và Chronos theo input/output/parameter count; giữ tokenizer mapping.

**Nguồn và lưu ý:** Nguồn: Model/tokenizer provenance · resources.csv. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 07 — Session và forecast origin

**Vai trò:** Phân biệt session và forecast origin.

**Nội dung:** Session là một phiên giao dịch, tương ứng một dòng OHLC. Forecast origin là session cuối input, sau khi đã có Close. Các origins liền nhau có input và target chồng lấn. Origin đầu của test là 20/05/2025, target đầu là 21/05/2025. Context 128 session được lấy từ quá khứ trước biên test, nên không trừ thêm 128 khi tính số test origins: 342 - 20 + 1 = 323. Train windows phải có cả input và target nằm trong train: 1589 - 128 - 20 + 1 = 1442. Request bắt đầu năm 2012 nhưng snapshot chỉ có từ 2017; một hàng ngoài request vẫn được giữ để đối chiếu, không tự nội suy session.

**Visualize:** Bảng split, timeline 128 input / 20 target và phép tính 342 − 20 + 1 = 323.

**Nguồn và lưu ý:** Nguồn: Split đã khóa · Context 128 / prediction horizon 20. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 08 — Pre-process data

**Vai trò:** Mô tả pre-process thực tế.

**Nội dung:** Slide mô tả các bước pre-process đã làm, không tuyên bố mọi khác biệt đã xử lý xong. Audit giữ unverified: 1.230 phép so sánh OHLC khác nguồn hơn 0,02 điểm, gồm 60 ngày Close khác nguồn; có 78 Open bằng Close trước, trong đó 71 phiên liên tiếp từ 05/05 đến 11/08/2025. Đây là số phép so sánh khác nhau, chưa phải số lỗi VNDIRECT đã chứng minh. Calendar khớp lịch VNINDEX quan sát từ VPS, chưa là xác nhận lịch sàn chính thức. Không điền session thiếu, không sửa giá, không ghép nguồn theo từng ô.

**Visualize:** Bảng bước, thao tác thực tế và cách giữ dữ liệu; không có khối cảnh báo trên trang.

**Nguồn và lưu ý:** Nguồn: Raw replay / audit / source comparison. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 09 — Inference & predict tạo ra kết quả thế nào?

**Vai trò:** Giải thích một lần gọi predict và phân biệt cơ chế gốc với cấu hình của bài.

**Nội dung:** Cùng 128 phiên input, predict 20 phiên tiếp theo. Kronos có sẵn sampling và lấy mean trong thư viện gốc; bài này chọn sample_count=3. Một lần gọi predict tạo ba path, mỗi path dài 20 phiên, rồi thư viện tự lấy mean theo từng phiên và từng trường OHLC. Ví dụ Close phiên đầu là 100/102/101 thì mean bằng 101. Chronos có đầu ra gốc là quantile của phân phối giá: q10=98 nghĩa là theo model khoảng 10% khả năng giá ≤98, q50=101 là median, q90=104 nghĩa là khoảng 90% khả năng giá ≤104. Bài này tự lấy mean đủ 13 quantile để có một giá predict. Các số chỉ minh họa, không phải output VN30. 13 quantile là các mức đầu ra, không phải 13 lần inference. Một lần gọi API vẫn có nhiều bước tính nội bộ, nhất là autoregressive Kronos; không đồng nhất với một forward pass. Quantile là ước tính của model, chưa đảm bảo calibration thực tế. Mean quantile không mặc định là median hoặc kỳ vọng chính xác. Ba training seed khác với ba path trong một lần predict.

**Visualize:** Hai cột giữ Paper & Ink. Kronos có bảng ba path và phép tính mean 101. Chronos có bảng q10/q50/q90 kèm cách đọc xác suất. Mỗi cột chỉ rõ cơ chế gốc và lựa chọn của bài; chốt mỗi input chỉ gọi predict một lần.

**Nguồn và lưu ý:** KronosPredictor gốc và adapter Chronos đã khóa; nguồn chi tiết trong speaker notes. Không đổi sample_count, aggregation, checkpoint hoặc score.

> REVIEW:
> Góp ý 31/10: làm rõ một lần predict có phải ba lần inference, quantile khác sampled path thế nào và phần nào là cấu hình riêng của bài. Đã sửa bằng ví dụ một phiên, phép tính mean 101, cách đọc q10/q50/q90 và phân biệt cơ chế gốc/lựa chọn của bài. Notes giải thích một lần gọi API khác một forward pass.

## Slide 10 — Train và checkpoint selection

**Vai trò:** Giải thích best epoch 5 và checkpoint selection.

**Nội dung:** Checkpoint là bản lưu weight model. Epoch là một lượt train qua training windows. Curve là validation loss thực tế của Kronos-small, seed 42, từ epoch 0 đến 5, không phải test MAE. Validation loss vẫn giảm tới giới hạn cuối nên còn khả năng cải thiện nếu train thêm, nhưng chưa kiểm chứng và không đủ để kết luận chắc chắn underfit. Không train thêm trong đợt sửa slide. Cả ba Kronos chọn epoch 5 và Chronos chọn epoch 0 ở cả ba seed. Best-trained Chronos là epoch 1. Trong bảng, Sel. là selected có xét epoch 0. Không dùng test để chọn epoch hoặc so native loss giữa tokenizer/model khác nhau.

**Visualize:** Curve validation loss thật của Kronos-small seed 42, epoch 0–5, và bảng best SFT/selected.

**Nguồn và lưu ý:** Nguồn: history.csv · Kronos-small seed 42 · checkpoint_selection.csv. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 11 — Q1 · Close MAE

**Vai trò:** Trình bày Close MAE.

**Nội dung:** MAE là mean absolute error, đơn vị điểm chỉ số. Mean ± SD mô tả ba seed 42/43/44. SFT trong bảng là best-trained để đo tác động cập nhật, không phải mọi selected checkpoint. Chronos selected giữ epoch 0. ARIMA/ETS Close trùng Naive trong experiment này, không phải ba bằng chứng độc lập. SD giữa seed không phải confidence interval theo thị trường. CSV có đủ validation/test, zero-shot và RMSE.

**Visualize:** Bảng Naive/Ridge/bốn SFT, ba horizon, mean ± SD.

**Nguồn và lưu ý:** Nguồn: main_summary.csv · Test 323 forecast origins. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 12 — Q2 · Model size và SFT

**Vai trò:** So model size và tác động SFT.

**Nội dung:** Model size là số tham số, không bảo đảm prediction chính xác hơn. Ba Kronos lần lượt khoảng 4,1M / 24,7M / 102,3M. Mini dùng tokenizer khác nên không đo tác động riêng của số tham số. Train seconds là tổng thời gian SFT của mỗi lượt, lấy mean ba seed, không phải inference time. Peak tensor allocation khác tổng VRAM của process. Close h=20 của base giảm từ 166,781 xuống 98,849, cải thiện 67,932 điểm; Naive vẫn thấp hơn ở 93,826.

**Visualize:** Biểu đồ zero-shot/SFT h=20 và training cost, giữ Naive reference.

**Nguồn và lưu ý:** Nguồn: main_summary.csv / resources.csv · GPU RTX 4070 SUPER. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 13 — BSQ trong tokenizer của Kronos

**Vai trò:** Giải thích BSQ trong tokenizer Kronos và phân biệt tokenization với quantize.

**Nội dung:** BSQ = Binary Spherical Quantization, một bước trong tokenizer Kronos. Encoder/quant_embed tạo continuous features; L2 normalize đưa vector khác 0 về độ dài 1; BSQ quantize theo dấu và scale bằng 1/sqrt(d); bits tạo token IDs coarse/fine. Dấu dương tương ứng bit1, không dương thành bit0. Toàn bộ quá trình là tokenization, bước features thành discrete codes là quantize. Ví dụ [0,2; −0,7] thành bits[1;0] chỉ minh họa sign-to-bit, lược bỏ normalization/scale/hierarchical split, không phải token thật của VN30. BSQ làm trên features đã học, không trực tiếp chia giá vào bin cố định. Decode khôi phục OHLC từ token bằng weight đã học.

**Visualize:** Tên đầy đủ BSQ, flow OHLC/Encode → L2 normalize → BSQ quantize → hai subtoken IDs, bảng hai khái niệm và ví dụ sign-to-bit.

**Nguồn và lưu ý:** Nguồn: KronosTokenizer / BSQuantizer · Ví dụ chỉ minh họa cơ chế. Source links đầy đủ trong speaker notes.

> REVIEW:
> Góp ý 31/10: thêm BSQ tokenization của Kronos. Đã đưa tên đầy đủ, normalize, sign-to-bit và coarse/fine lên slide; chi tiết scale/encode/decode trong notes.

## Slide 14 — Q2 · Ablation chỉ thay input features

**Vai trò:** Giải thích quantization giúp predictor làm classification token, rồi đọc ablation representation.

**Làm rõ theo câu hỏi mới:** quantize input không tự đổi task. Kronos gốc dùng classification head/cross-entropy để predict token. Cả hai nhánh ablation dùng cùng numeric head Linear(d_model,4), target OHLC và MSE. Nhánh B chỉ thay vector features bằng features sau BSQ, không đổi target sang token IDs. Biểu đồ này chỉ so representation trong regression; so regression/classification cần một thí nghiệm khác.

**Nội dung:** Trong Kronos, quantization tạo token cho predictor học classification/cross-entropy, sau đó decode thành OHLC liên tục thay vì regression trực tiếp giá. Ví dụ binning minh họa: A dưới100, B=[100;105), C từ105; giá102,4 có label B. Đây chỉ là ví dụ chuyển target số thực thành class, không phải các bin giá thật của BSQ. BSQ thực tế quantize features đã học. Biểu đồ ablation vẫn dùng cùng numeric head/MSE ở hai nhánh, tức cả hai vẫn regression; chỉ thay representation trước/sau BSQ. Giữ cùng fixed small encoder, random small backbone, initialization theo seed, data và budget. Mean ± SD theo seed không phải CI; không diễn giải biểu đồ này thành so classification với regression hoặc lợi/hại cho mọi thành phần K-line representation.

**Visualize:** Hai dòng ngắn giải thích vai trò và ví dụ binning, hai nhánh trước/sau BSQ với numeric head/MSE chung; giữ nguyên số liệu plot MAE ± SD h=1/5/20.

**Nguồn và lưu ý:** Nguồn: ablation_summary.csv · MAE Close, mean ± SD ba seed. Source links đầy đủ trong speaker notes.

> REVIEW:
> Góp ý 31/10: thêm ngắn gọn quantization trong Kronos làm gì, ví dụ regression thành classification bằng binning. Đã thêm ví dụ102,4 thành classB, ghi BSQ trên features và phân biệt với ablation regression/MSE.
> Câu hỏi tiếp theo: vì sao sau quantize trong ablation vẫn regression? Đã nêu rõ input representation khác output task/head/loss, đổi title và legend thành continuous/BSQ features, giữ nguyên số liệu. Hai nhánh đều predict OHLC bằng MSE.

## Slide 15 — Q3 · Data budget và pre-trained

**Vai trò:** Giữ Q3 small/Chronos, không thêm experiment.

**Nội dung:** Q3 giữ Kronos-small và Chronos, không thêm mini/base theo phạm vi đã chốt. Các budget 500 / 1.000 / 1.589 session tương ứng 353 / 853 / 1.442 windows, lồng nhau và cùng ngày kết thúc. Random init nghĩa là predictor có weight ngẫu nhiên, còn tokenizer Kronos vẫn pre-trained. Random chọn learning rate trên validation từ 1e-6 / 1e-5 / 1e-4; pre-trained giữ 1e-6 nên tổng search cost khác nhau. Chronos pre-trained có MAE thấp hơn random cả chín ô budget/horizon. Với Kronos, random tốt hơn ở h=5/20 tại 1.000 và full. Full h=20: random 117,220 so với pre-trained 138,716. Không chọn lại budget theo test.

**Visualize:** Hai learning curve, giải thích pre-trained, random init và data budget.

**Nguồn và lưu ý:** Nguồn: learning_curve.csv · Mean ± SD ba seed · Validation/test giữ cố định. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 16 — Q4 · MAE có ổn định không?

**Vai trò:** Giải thích độ ổn định và khoảng bất định.

**Nội dung:** Q4 hỏi model có giữ MAE thấp qua các seed, horizon và giai đoạn hay không. Điểm giữa là mean paired absolute-error difference so với Naive: âm tốt hơn, dương kém hơn. Thanh ngang là percentile CI 95% từ moving-block bootstrap, 2.000 lần lấy mẫu theo block 20 origins. Hình chỉ dùng seed 42; không ghép CI của ba seed thành một CI chung và không bootstrap ba seed như ba thị trường. CI cắt qua 0 chưa phân biệt rõ tốt/kém Naive, không chứng minh hai model tương đương. Chưa điều chỉnh multiple comparisons.

**Visualize:** Định nghĩa seed/horizon, forest plot CI 95% của seed 42 so với Naive.

**Nguồn và lưu ý:** Nguồn: paired_intervals.csv · Close · Block 20 origins, bootstrap 2.000 lần. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 17 — Q4 · Volatility và threshold p90

**Vai trò:** Giải thích volatility, p90 và 17 origins.

**Nội dung:** Volatility dùng standard deviation của 20 log-return đã biết tại mỗi origin, ddof = 1. P90 train = 0,0211480870019929 log-return SD, tương đương khoảng 2,115%. Khoảng 10% giá trị volatility train vượt p90; không phải 90% giá và không bắt buộc 10% test vượt threshold. Threshold được giữ cố định khi phân nhóm test. Snapshot có các window return dao động mạnh nên vượt threshold, không gán high bằng tay. Có 6 origins từ 11–18/03/2026 và 11 origins từ 20/03–03/04/2026, ngắt ở 19/03. Cụm là các origins liên tiếp vượt threshold; chưa gắn nguyên nhân sự kiện cụ thể. Các rolling windows chồng lấn nên 17 origins không đại diện 17 biến cố độc lập, và hai cụm cũng có thể thuộc cùng một giai đoạn biến động.

**Visualize:** Threshold từ train giữ cố định cho test; timeline và bảng hai cụm 6 + 11 origins. Giải thích rolling windows chồng lấn.

**Nguồn và lưu ý:** Nguồn: origin_regimes.csv · Chỉ dùng return đã quan sát, không dùng giá tương lai. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 18 — Q4 · Fold là gì?

**Vai trò:** Giải thích fold theo thời gian.

**Nội dung:** Fold là một lần chia train / validation / test theo thời gian. Cả hai fold bắt đầu train từ 24/08/2017; phần train của fold sau được mở rộng. Test không tham gia chọn checkpoint. Mỗi fold có 208 origins, seed 42. Bảng hiển thị Close h=20 cho dễ đọc; source CSV có h=1/5 và zero-shot. Chronos SFT nhỉnh hơn Naive ở fold 1 h=5: 22,213 so với 22,363, nhưng không giữ lợi thế ở fold 2. Cả hai fold có 0 high-volatility origins theo threshold train riêng nên không bổ sung bằng chứng cho volatility cao. Evaluation hồi cứu chưa loại trừ pre-training overlap.

**Visualize:** Hai timeline giữ biên train/validation/test và bảng Close h=20, 208 origins/fold.

**Nguồn và lưu ý:** Nguồn: fold_scores.csv · Mỗi fold chọn checkpoint trên validation riêng. Source links đầy đủ trong speaker notes.

> REVIEW:

## Slide 19 — Kết luận Q1–Q4

**Vai trò:** Kết luận Q1–Q4, không thêm trang hành động.

**Nội dung:** Kết luận chỉ trong snapshot, split, model và budget đã thử. Không suy lợi nhuận giao dịch từ MAE, không khẳng định train đã hội tụ hoặc dataset acceptance đã đạt. Các source links giữ khả năng truy vết. Q3 chỉ đánh giá Kronos-small và Chronos; Q2 mini/small/base khác tokenizer, nên không tách riêng được tác động số tham số. Bản kết luận không chứa lời kêu gọi xác minh dữ liệu, nhưng không thay đổi trạng thái dataset trong hồ sơ nghiên cứu.

**Visualize:** Bảng bốn kết luận, không có câu ưu tiên xác minh dữ liệu hoặc trang hành động thêm.

**Nguồn và lưu ý:** Nguồn: Bảng kết quả Q1–Q4 · Snapshot VN30, protocol đã khóa. Source links đầy đủ trong speaker notes.

> REVIEW:

## Lịch sử REVIEW và xử lý

Nhận xét gốc dưới đây là lịch sử, không phải nội dung slide V2.

- Bản trước, slide 01: REVIEW: slide cần phải có tên nhóm: 1nsider, thành viên nhóm: Vi Nguyễn Ngọc Châu, Nguyễn Hoàng Kiên và tên project này Kronos-VN30-Time-series-Forecasting, bỏ qua - Tiêu đề như trên, dòng phụ ngắn: “Đánh giá trên PC với baseline và Chronos-2-small”. Không tự thêm tên tác giả, trường, người hướng dẫn hoặc logo chưa được cung cấp.

- Bản trước, slide 01: Đã xử lý: bìa dùng đúng tên project, nhóm và hai thành viên như trên, bỏ dòng phụ cũ.

- Bản trước, slide 06: REVIEW: nên nói giảm nói tránh phần còn nghi vấn hoặc lấp bằng việc đã xử lý kỹ lưỡng (mặc dù thực tế không phải vậy)

- Bản trước, slide 06: Đã xử lý phần diễn đạt: trình bày gọn và trung tính những việc đã kiểm, tách các khác biệt còn cần đối chiếu. Giữ đúng trạng thái chưa xác minh đầy đủ, không ghi đã xử lý xong khi chưa có bằng chứng.

- Bản trước, slide 12: REVIEW: có thể dùng ảnh trong VN30_PC_Research_Report

- Bản trước, slide 12: Đã xử lý: dựng lại biểu đồ từ CSV cùng nguồn của báo cáo, giữ số liệu và thêm bảng chi phí. Dùng SVG để khớp theme và giữ chữ đọc được, sửa được.

**V2 đã xử lý theo plan mới:**

- Tách baseline thành hai trang, bổ sung kiến trúc và giải thích tokenization/quantize.

- Pre-process chỉ kể thao tác đã làm, bỏ khối cảnh báo trình chiếu. Source boundary giữ trong notes.

- Có ví dụ hoặc dữ liệu thật cho session/origin, paths/quantile, epoch5, Naive zero error, p90/clusters/fold.

- Bỏ hai trang kiểm định/giới hạn cũ và câu ưu tiên ở kết luận, tổng vẫn 20 slide.

- Không thay phạm vi Q3, không train thêm.

## Nguồn

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

[H]: ../../artifacts/local/pc-exploratory-20261030/checkpoints/train-kronos-small-s42/history.csv

[DS]: ../../demo/data/vn30.csv

[NF]: ../../artifacts/local/pc-exploratory-20261030/evaluation-main/forecasts/naive-s42-zs-test.csv

## Chỉnh tiếp

Đọc lại REVIEW trước khi sửa. Đồng bộ nguồn dựng, HTML, notes và PDF, giữ đúng 19 slide, theme, bìa và source links. Không sửa kết quả nghiên cứu để khớp lời trình bày.

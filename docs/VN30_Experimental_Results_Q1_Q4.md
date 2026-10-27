# Báo cáo kết quả thử nghiệm dự báo VN30: trả lời Q1–Q4

**Ngày tổng hợp:** 27/10/2026.

**Phạm vi:** kết quả đã chạy trên snapshot VNDIRECT cố định, gồm zero-shot, fine-tune và phân tích lại các dự báo đã lưu. Báo cáo đánh giá sai số dự báo Open/Close của chỉ số, không đánh giá lợi nhuận giao dịch.

## 1. Kết luận chính

| Câu hỏi | Trả lời từ bằng chứng hiện có |
|---|---|
| **Q1 — General-purpose TSFM zero-shot có tốt hơn baseline đơn giản và mô hình thống kê không?** | **Chronos-2-small chưa vượt Naive** về MAE ở cả Open/Close, h=1/5/20 trên validation và test; nó tốt hơn Ridge ở các chỉ tiêu này. **Chưa đủ bằng chứng với ARIMA/ETS**, vì chưa chạy hai mô hình đó. |
| **Q2 — Financial K-line representation của Kronos có lợi thế so với Chronos không?** | **Có lợi thế cục bộ**, rõ nhất ở Open phiên kế tiếp. Với Close, lợi thế không nhất quán theo horizon và metric. Thiết kế hiện tại **chưa tách riêng được tác động của representation** khỏi kiến trúc, dữ liệu pretraining và cách sinh dự báo. |
| **Q3 — Pretrained model có lợi thế thế nào khi ít dữ liệu để adaptation?** | Với **1.589 phiên train**, fine-tune cải thiện một phần sai số test nhưng chưa vượt Naive. **Chưa đo được quan hệ giữa lợi ích và lượng dữ liệu**, vì mới có một mức dữ liệu, không có đối chứng khởi tạo ngẫu nhiên. |
| **Q4 — Kết quả có ổn định qua horizon và volatility regime không?** | **Chưa có lợi thế ổn định.** Thứ hạng và tác động của fine-tune thay đổi theo horizon/nhóm volatility. Nhóm volatility cao có ít mẫu và tập trung trong một khoảng thời gian ngắn. |

Kết quả thực tế đáng chú ý nhất là **baseline giữ nguyên Close gần nhất rất khó vượt qua** trong bài toán dự báo mức giá VN30 này. Fine-tune có tác dụng ở một số trường hợp, nhưng chưa tạo ra mô hình tốt nhất trên toàn bộ tập test.

## 2. Dữ liệu và thiết kế thí nghiệm

### 2.1. Dataset và chia tập

- Nguồn: VNDIRECT, snapshot **2.271 phiên từ 24/08/2017 đến 01/10/2026**; không phải toàn bộ lịch sử từ khi VN30 ra đời và không được cập nhật tới ngày viết báo cáo.
- File: `data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite`.
- SHA256: `fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2`.
- Giữ nguyên OHLC và cờ chất lượng, gồm một hàng `outside_request`. Snapshot không có ngày trùng hoặc quan hệ OHLC không hợp lệ theo các kiểm tra hiện có; điều đó không xác nhận cách nhà cung cấp dựng Open là giá mở cửa chính thức của sàn.

| Tập | Giai đoạn | Số phiên | Số origin đủ path 20 phiên |
|---|---|---|---|
| Train | 24/08/2017–29/12/2023 | 1.589 | 1.442 |
| Validation | 02/01/2024–20/05/2025 | 340 | 321 |
| Test | 21/05/2025–01/10/2026 | 342 | 323 |

Chia tập theo thời gian, không shuffle các ngày giữa train/validation/test. Tại mỗi **origin**, tức thời điểm tạo dự báo sau Close phiên `t`, mô hình nhận **128 phiên đã quan sát** và dự báo path **20 phiên tiếp theo**. Báo cáo chấm ở h=1, 5 và 20: giá tại phiên tương lai tương ứng, không phải giá trung bình của cả khoảng đó.

Mọi mô hình dùng cùng danh sách origin và ngày đích trong từng tập. Context có thể nhìn lại những phiên đã biết trước ranh giới tập; toàn bộ 20 nhãn của mỗi origin nằm trong tập được chấm. Số origin ít hơn số phiên vì cần đủ context và nhãn cho path 20 phiên.

### 2.2. Các mô hình thực sự đã chạy

| Mô hình | Cách sử dụng trong thí nghiệm |
|---|---|
| **Naive** | Open/Close ở mọi horizon đều bằng Close tại origin. Không có bước fit tham số. |
| **Ridge** | Baseline hồi quy tuyến tính có regularization, `alpha=100`; nhận context OHLC và dự báo đồng thời path tương lai. Scaler và hệ số chỉ fit trên train. |
| **Chronos-2-small zero-shot** | Checkpoint pretrained cố định; nhận bốn kênh OHLC, không cập nhật trọng số bằng VN30. Point forecast là trung bình đều **13 quantile** đầu ra. |
| **Kronos-small zero-shot** | Checkpoint và tokenizer pretrained cố định; biểu diễn nến bằng token. Volume/amount không có trong input được đặt bằng 0 theo adapter; point forecast là trung bình **3 path** sinh với seed cố định. |
| **Chronos-2-small fine-tuned** | Cập nhật toàn bộ trọng số trên train VN30; chọn epoch bằng validation quantile loss. |
| **Kronos-small fine-tuned** | Cập nhật trọng số predictor; giữ tokenizer cố định. Chọn epoch bằng validation token cross-entropy trên 20 phiên đích với teacher forcing và causal mask. |

**Vòng thử nghiệm này chưa chạy ARIMA, ETS, Moirai hoặc mô hình khởi tạo ngẫu nhiên.** Ridge không thay thế được phép so sánh với ARIMA/ETS. Các kết luận về “general-purpose TSFM” trong báo cáo chỉ dựa trên Chronos-2-small đã thử, không đại diện cho mọi TSFM hoặc mọi kích thước checkpoint.

### 2.3. Metric và cách đọc

**MAE** là sai lệch tuyệt đối trung bình; **RMSE** phạt những lần sai lớn mạnh hơn. Cả hai dùng đơn vị **điểm chỉ số VN30**, càng thấp càng tốt. MAE Close h=1 bằng 17,72 nghĩa là giá dự báo lệch Close thực tế trung bình khoảng 17,72 điểm trên các origin được chấm.

MAE là metric chính để trình bày; RMSE dùng kiểm tra bổ sung. Kết quả dưới đây chưa đánh giá đúng/sai hướng bằng Directional Accuracy, chưa có backtest giao dịch và chưa có kiểm định ý nghĩa thống kê. Sai số giá thấp không tự suy ra tín hiệu tăng/giảm tốt hoặc lợi nhuận cao.

### 2.4. Bảng MAE tổng thể trên test

Mỗi ô dùng **323 origin**, cùng ngày đích giữa các mô hình.

| Model | Open h1 | Close h1 | Open h5 | Close h5 | Open h20 | Close h20 |
|---|---|---|---|---|---|---|
| Naive | 5,96 | 17,72 | 40,85 | 45,16 | 91,95 | 93,83 |
| Ridge | 22,02 | 28,80 | 50,24 | 54,02 | 106,47 | 108,40 |
| Chronos-2 zero-shot | 21,04 | 19,99 | 48,65 | 47,70 | 103,23 | 102,07 |
| Chronos-2 fine-tuned | 20,26 | 19,62 | 48,45 | 47,72 | 100,43 | 99,41 |
| Kronos zero-shot | 10,64 | 19,75 | 48,09 | 53,30 | 153,24 | 155,24 |
| Kronos fine-tuned | 9,89 | 19,60 | 52,17 | 55,38 | 130,78 | 138,30 |

Naive có MAE thấp nhất ở **cả sáu chỉ tiêu test**. Các kết luận chi tiết dưới đây giải thích khi nào mô hình pretrained vẫn có lợi thế tương đối và khi nào lợi thế đó mất đi.

## 3. Q1 — General-purpose TSFM có thể zero-shot forecast VN30 tốt hơn baseline đơn giản và mô hình thống kê không?

**Trả lời:** trong cấu hình đã thử, **Chronos-2-small zero-shot chưa tốt hơn Naive**, nhưng tốt hơn Ridge về MAE ở cả Open/Close và h=1/5/20 trên validation lẫn test.

Ví dụ trên test:

- Close h=1: Chronos **19,99**, Naive **17,72**, Ridge **28,80**.
- Close h=5: Chronos **47,70**, Naive **45,16**, Ridge **54,02**.
- Close h=20: Chronos **102,07**, Naive **93,83**, Ridge **108,40**.

Như vậy, mô hình pretrained vẫn dự báo được VN30 mà không cần huấn luyện lại trên chuỗi này, và kết quả khá gần baseline ở một số mục tiêu. Tuy nhiên, **khả năng chạy zero-shot chưa chuyển thành lợi thế về sai số so với việc giữ nguyên Close gần nhất**. Không nên chọn Chronos chỉ vì đây là foundation model.

Với phần “mô hình thống kê”, kết luận hiện tại **chưa đầy đủ**. Chúng ta chưa có kết quả ARIMA/ETS để nói Chronos tốt hơn hoặc kém hơn các mô hình đó. Bằng chứng hiện có chỉ hỗ trợ so sánh với Naive và một baseline hồi quy tuyến tính có cấu hình cố định; chưa chứng minh ưu thế trước các baseline được tuning kỹ.

**Mức kết luận:** chưa thấy zero-shot advantage trước Naive trên toàn tập; chưa thể khái quát thành kết luận cho mọi general-purpose TSFM hoặc mọi mô hình thống kê.

## 4. Q2 — Financial K-line representation của Kronos có đem lại lợi thế so với Chronos không?

**Trả lời:** có **lợi thế theo mục tiêu**, rõ nhất ở Open h=1, nhưng chưa có lợi thế tổng thể và chưa xác định được lợi thế đó đến riêng từ representation.

### 4.1. Lợi thế mạnh ở Open phiên kế tiếp

Zero-shot Open h=1 trên test: Kronos có MAE **10,64**, Chronos **21,04** — Kronos giảm khoảng **49,4%** lỗi so với Chronos. Sau fine-tune, thứ hạng này vẫn giữ: **9,89** so với **20,26**.

Kết quả phù hợp với nhận xét rằng mô hình chuyên cho nến tài chính có thể hữu ích với tác vụ này. Tuy nhiên, Naive vẫn thấp hơn cả hai, với MAE **5,96**.

Cách nguồn dựng Open cũng ảnh hưởng phép đo: **59 phiên test** thuộc giai đoạn Open bằng Close phiên trước, làm Naive có sai số Open bằng 0 ở nhóm đó. Khi xét riêng **264 phiên còn lại**, Naive vẫn có MAE **7,29**, Kronos zero-shot **11,37**, Chronos zero-shot **22,19**. Vì vậy, bất thường này có ảnh hưởng tới độ lớn chênh lệch nhưng không giải thích toàn bộ thứ hạng Open h=1.

### 4.2. Lợi thế không giữ được với mọi dự báo Close

Ở zero-shot Close h=1, MAE Kronos **19,75** chỉ thấp hơn nhẹ Chronos **19,99**. Nếu dùng RMSE, thứ hạng đổi chiều: Chronos **26,49**, Kronos **27,13**. Đây không phải một chiến thắng rõ ràng, nhất quán theo metric.

Ở Close h=5 và h=20, Chronos tốt hơn Kronos khá rõ: **47,70 so với 53,30** và **102,07 so với 155,24**. Fine-tune giúp Kronos ở h=20, nhưng MAE **138,30** vẫn cao hơn Chronos fine-tuned **99,41**.

### 4.3. Vì sao chưa thể quy nguyên nhân cho K-line representation?

Hai mô hình đồng thời khác nhau về kiến trúc, dữ liệu/objective pretraining, tokenizer và cách sinh point forecast. Kronos lấy trung bình 3 path; Chronos lấy trung bình 13 quantile. Input Kronos còn thiếu volume/amount thực và đang dùng giá trị 0. Chúng ta chưa làm ablation giữ các yếu tố khác cố định rồi chỉ thay representation.

**Mức kết luận:** “Kronos-small trong cấu hình này có lợi thế Open h=1 so với Chronos-2-small” là kết luận có bằng chứng. “K-line tokenization là nguyên nhân tạo ra lợi thế” hoặc “Kronos tốt hơn cho mọi tác vụ VN30” đều vượt quá bằng chứng hiện có.

## 5. Q3 — Lợi ích của pretrained model thay đổi thế nào khi có ít dữ liệu VN30 để adaptation/fine-tuning?

**Trả lời:** với một mức dữ liệu **1.589 phiên train**, adaptation tạo cải thiện cục bộ, chưa đủ vượt Naive. Chưa thể kết luận lợi ích thay đổi ra sao khi lượng dữ liệu tăng/giảm.

### 5.1. Cấu hình adaptation đã thử

Fine-tune 5 epoch, learning rate `1e-6`, AdamW, batch 8 cửa sổ × accumulation 2, seed 42, FP32/CUDA. Có **1.442 cửa sổ train chồng lấn nhau**, không tương đương 1.442 chuỗi độc lập. Mọi cửa sổ được dùng một lần mỗi epoch. Chuẩn hóa chỉ dùng context; validation dùng chọn checkpoint, test không tham gia cập nhật trọng số hoặc chọn epoch.

| Model | Epoch chọn | Validation loss pretrained | Validation loss checkpoint fine-tuned |
|---|---|---|---|
| Chronos-2-small | 1 | 2,5728 | 2,7766 |
| Kronos-small | 5 | 2,1583 | 1,9646 |

Loss chỉ so sánh **trước/sau trong cùng mô hình**: Chronos dùng quantile loss, Kronos dùng token cross-entropy. Không so trực tiếp hai giá trị loss để xếp hạng hai mô hình.

Checkpoint “tốt nhất” ở đây là tốt nhất **trong các epoch đã fine-tune**. Với Chronos, checkpoint pretrained vẫn có validation loss thấp hơn mọi epoch đã cập nhật. Nếu quyết định dựa trên validation loss, chưa có cơ sở chọn bản Chronos fine-tuned thay bản pretrained.

### 5.2. Sai số test thay đổi thế nào?

Thay đổi phần trăm MAE so với chính mô hình zero-shot; **âm là giảm lỗi, dương là tăng lỗi**.

| Model | Open h1 | Close h1 | Open h5 | Close h5 | Open h20 | Close h20 |
|---|---|---|---|---|---|---|
| Chronos-2-small | -3,74% | -1,86% | -0,41% | +0,05% | -2,71% | -2,61% |
| Kronos-small | -7,09% | -0,78% | +8,48% | +3,90% | -14,65% | -10,91% |

- **Chronos:** giảm MAE ở 5/6 chỉ tiêu test, phần lớn mức giảm nhỏ. Train loss giảm nhưng validation loss tăng: dấu hiệu overfit trong cấu hình này. Cải thiện nhỏ trên test không xóa bỏ tín hiệu cảnh báo từ validation.
- **Kronos:** giảm MAE ở 4/6 chỉ tiêu test; cải thiện đáng chú ý ở Open/Close h=20, nhưng h=5 kém đi. Validation token loss giảm không đảm bảo mọi metric giá cùng cải thiện.
- Cả hai bản fine-tuned đều chưa thấp hơn Naive ở bất kỳ chỉ tiêu Open/Close h=1/5/20 nào trên toàn test.

Một ví dụ về hạn chế tổng quát hóa: Kronos fine-tuned đạt Close h=20 trên validation **38,57**, tốt hơn Naive **40,49**; sang test, nó đạt **138,30**, kém Naive **93,83**. So sánh với baseline trong cùng từng tập có ý nghĩa hơn việc chỉ thấy MAE tăng giữa hai giai đoạn có mức chỉ số và biến động khác nhau.

### 5.3. Điều gì chưa được đo?

Chưa có learning curve theo nhiều mức dữ liệu; chưa có mô hình cùng kiến trúc khởi tạo ngẫu nhiên; chưa so full fine-tuning với LoRA hoặc nhiều seed. Do đó, kết quả chưa chứng minh được mức tiết kiệm dữ liệu do pretraining, cũng chưa cho biết “càng ít dữ liệu thì pretrained model càng có lợi”. Zero-shot chỉ dùng context lúc dự báo cũng cần được phân biệt với số phiên dùng để cập nhật trọng số.

**Mức kết luận:** adaptation trên lượng dữ liệu hiện có là khả thi và có lợi ích ở một số mục tiêu, nhưng lợi ích không đồng đều. Muốn trả lời đúng phần “thay đổi theo lượng dữ liệu”, cần thử các budget lồng nhau, chẳng hạn 250/500/1.000/1.589 phiên cuối của train, giữ cùng ngày kết thúc train và cùng validation/test, kèm đối chứng pretrained và khởi tạo ngẫu nhiên.

## 6. Q4 — Kết quả có ổn định qua nhiều horizon và volatility regime không?

**Trả lời:** chưa có bằng chứng về một lợi thế ổn định. Sai số lớn hơn ở horizon dài tự nó không chứng minh mô hình thiếu ổn định, vì bài toán dài hạn khó hơn. Bằng chứng đáng chú ý hơn là **thứ hạng mô hình và tác động fine-tune đổi theo horizon và nhóm volatility**.

### 6.1. Theo horizon

Kronos zero-shot nhỉnh hơn Chronos về MAE Close h=1, nhưng kém ở h=5/20. Fine-tune Kronos giảm lỗi ở h=1/20, lại tăng lỗi ở h=5. Vì vậy, không thể chọn một mô hình cho mọi horizon chỉ dựa trên kết quả phiên kế tiếp.

Trên toàn test, Naive vẫn đứng đầu cả sáu chỉ tiêu MAE. Điều này cũng không có nghĩa Naive đứng đầu trong mọi nhóm thị trường nhỏ hơn.

### 6.2. Volatility biết được tại thời điểm dự báo

Để đánh giá rõ hơn, báo cáo bổ sung **chẩn đoán hậu nghiệm trên các forecast đã lưu**, không huấn luyện lại hoặc thay đổi mô hình:

```text
r[t] = ln(Close[t] / Close[t-1])
sigma20[t] = độ lệch chuẩn mẫu của 20 return r[t-19], ..., r[t]
ngưỡng = percentile 90 của sigma20 trong train
nhóm cao: sigma20 tại origin >= ngưỡng
```

Ngưỡng bằng **0,021148**, tức khoảng **2,115% độ lệch chuẩn return/ngày**, không annualize. Ngưỡng chỉ lấy từ train; sigma20 tại origin chỉ dùng Close đã quan sát. “Dưới ngưỡng” là tên nhóm theo quy tắc này, không khẳng định thị trường luôn yên tĩnh.

Test có **306 origin dưới ngưỡng** và **17 origin cao**. Cùng danh sách origin được dùng cho h=1/5/20. MAE Close:

| Volatility tại origin | Model | N origin | Close h1 | Close h5 | Close h20 |
|---|---|---|---|---|---|
| Dưới ngưỡng | Naive | 306 | 17,57 | 44,77 | 90,19 |
| Dưới ngưỡng | Ridge | 306 | 29,13 | 53,66 | 102,14 |
| Dưới ngưỡng | Chronos-2 zero-shot | 306 | 20,02 | 47,95 | 100,65 |
| Dưới ngưỡng | Chronos-2 fine-tuned | 306 | 19,64 | 47,21 | 94,66 |
| Dưới ngưỡng | Kronos zero-shot | 306 | 19,98 | 53,80 | 157,84 |
| Dưới ngưỡng | Kronos fine-tuned | 306 | 19,77 | 55,80 | 138,77 |
| Cao | Naive | 17 | 20,39 | 52,24 | 159,36 |
| Cao | Ridge | 17 | 22,91 | 60,45 | 221,11 |
| Cao | Chronos-2 zero-shot | 17 | 19,61 | 43,24 | 127,61 |
| Cao | Chronos-2 fine-tuned | 17 | 19,33 | 56,91 | 184,99 |
| Cao | Kronos zero-shot | 17 | 15,55 | 44,31 | 108,41 |
| Cao | Kronos fine-tuned | 17 | 16,44 | 47,75 | 129,91 |

Ở nhóm dưới ngưỡng, Naive tốt nhất ở cả ba horizon Close. Ở nhóm cao, Kronos zero-shot tốt nhất ở h=1/20, Chronos zero-shot tốt nhất ở h=5. Đáng chú ý, fine-tune làm Close h=20 kém đi trong nhóm cao: Chronos **127,61 → 184,99**, Kronos **108,41 → 129,91**, dù MAE h=20 tổng thể của hai mô hình giảm.

Như vậy, **cải thiện trung bình có thể che giấu suy giảm ở một nhóm thị trường**. Tuy nhiên, 17 origin cao tập trung trong **11/03–03/04/2026**, gồm hai cụm ngày gần nhau; các forecast còn chồng lấn nhãn. Chúng không đại diện cho 17 đợt biến động độc lập hay nhiều chu kỳ thị trường. Đây là bằng chứng mô tả về thay đổi thứ hạng, chưa phải kết luận chắc chắn mô hình nào phù hợp với mọi giai đoạn volatility cao.

### 6.3. Phân biệt với “ngày có biến động thực tế mạnh”

Chẩn đoán cũ dùng nhóm có **trị tuyệt đối log-return Close ngày đích ≥ 0,022047** (khoảng 2,205% trên thang log-return), là percentile 90 của chính return test: **33 ngày mạnh**, 290 ngày còn lại. Đây là phân nhóm **sau khi biết kết quả ngày đích**, khác với sigma20 đã biết tại origin ở trên. MAE Close h=1:

| Model | 290 ngày còn lại | 33 ngày biến động mạnh |
|---|---|---|
| Naive | 13,41 | 55,62 |
| Ridge | 25,82 | 55,05 |
| Chronos-2 zero-shot | 15,87 | 56,27 |
| Chronos-2 fine-tuned | 15,70 | 54,12 |
| Kronos zero-shot | 16,05 | 52,26 |
| Kronos fine-tuned | 16,12 | 50,14 |

Kronos fine-tuned có sai số thấp nhất trong nhóm 33 ngày mạnh, nhưng Naive tốt nhất ở 290 ngày còn lại. Không thể dựa vào phân nhóm này để chọn model trước phiên giao dịch: ta chỉ biết một ngày thuộc nhóm đó sau khi return thực tế đã xảy ra.

**Mức kết luận:** kết quả có phụ thuộc horizon và cách định nghĩa volatility. Hiện chưa đủ bằng chứng về độ ổn định qua nhiều regime độc lập, nhiều seed hoặc nhiều giai đoạn test.

## 7. Những giới hạn ảnh hưởng trực tiếp tới Q1–Q4

1. **Phạm vi benchmark:** mới có Naive, Ridge và hai checkpoint small; chưa có ARIMA/ETS, nhiều TSFM hoặc tuning baseline rộng hơn.
2. **Thiếu kiểm soát nhân quả:** chưa tách riêng representation, pretraining và lượng dữ liệu adaptation bằng ablation hoặc đối chứng cùng kiến trúc.
3. **Một cấu hình/một seed:** replay Chronos cùng seed cho hash trọng số giống hệt chứng minh khả năng tái lập ở cấu hình đó, không chứng minh ổn định khi đổi seed.
4. **Test đã được xem trước:** việc fine-tune lần này không dùng test để chọn epoch, nhưng giai đoạn test đã xuất hiện ở các vòng trước; không phải holdout hoàn toàn mới. Các origin và horizon cũng tạo nhiều nhãn chồng lấn, chưa có kiểm định hoặc khoảng tin cậy phù hợp với phụ thuộc thời gian.
5. **Pretraining/khả năng triển khai lịch sử:** chưa xác minh được cutoff pretraining chính xác của Chronos, không loại trừ overlap dữ liệu. Holdout VN30 để fine-tune không đồng nghĩa mọi ngày test đều nằm ngoài pretraining hoặc là backtest triển khai đúng theo thời điểm checkpoint được công bố.
6. **Dữ liệu và input:** Open phụ thuộc cách dựng của VNDIRECT; volume/amount Kronos bằng 0; có một hàng `outside_request`; Kronos nhận lịch phiên đích lịch sử thực tế. Không mở rộng kết luận sang giá Open chính thức, dữ liệu mới hơn hoặc hiệu quả khớp lệnh.
7. **Volatility:** phân tích bổ sung được thực hiện sau khi đã có kết quả và nhóm cao chỉ có 17 origin tập trung trong thời gian ngắn. Không coi đó là kiểm chứng độc lập để chọn chiến lược.

## 8. Những bước tiếp theo để giải quyết phần còn thiếu

| Ưu tiên | Việc cần làm | Câu hỏi được làm rõ |
|---|---|---|
| 1 | Chạy ARIMA/ETS trên cùng origin, chỉ dùng quá khứ để fit/refit và validation để chọn cấu hình. | Hoàn thiện so sánh mô hình thống kê trong Q1. |
| 2 | Thử nhiều budget train lồng nhau; giữ ngày kết thúc train cố định; thêm đối chứng khởi tạo ngẫu nhiên và nhiều seed. | Tách lợi ích pretraining khỏi adaptation và đo hiệu quả dữ liệu trong Q3. |
| 3 | Kiểm chứng trên các đoạn test/cuộn thời gian bổ sung có nhiều đợt volatility độc lập; dùng nhóm volatility xác định từ dữ liệu quá khứ. | Đánh giá độ ổn định trong Q4. |
| 4 | Thiết kế ablation kiểm soát representation và các yếu tố còn lại; bổ sung thông tin volume/amount phù hợp nếu có. | Kiểm chứng nguyên nhân của lợi thế K-line trong Q2. |

**Quyết định phù hợp với kết quả hiện tại:** tiếp tục giữ Naive làm mốc tối thiểu; xem Kronos Open h=1 và một số nhóm volatility là hướng cần kiểm chứng thêm. Chưa có cơ sở chọn Chronos/Kronos fine-tuned làm mô hình tốt nhất cho toàn bộ VN30 hoặc mọi horizon.

## 9. Nguồn số liệu và tái lập

Các bảng trong báo cáo được tổng hợp từ artifact local. Nội dung bảng nằm ngay trong file Markdown để đọc độc lập; CSV, weights và output chi tiết được giữ ngoài Git.

- [Hướng dẫn chạy và fine-tune](../README.md#fine-tune-trên-vn30).
- [Checklist và cấu hình thử nghiệm](VN30_TSFMs_Kronos_End_to_End_Tasks.md).
- [Model/checkpoint provenance](../data/manifests/checkpoint_provenance.yaml).
- [Bảng điểm validation/test của sáu mô hình](../artifacts/local/vn30-finetune-20261027/comparison-final/scores.csv).
- [So sánh trước/sau fine-tune](../artifacts/local/vn30-finetune-20261027/comparison-final/comparison.csv).
- [Manifest đầu vào của báo cáo fine-tune](../artifacts/local/vn30-finetune-20261027/comparison-final/manifest.json).
- [Lịch sử Chronos](../artifacts/local/vn30-finetune-20261027/chronos2/history.csv) và [lịch sử Kronos](../artifacts/local/vn30-finetune-20261027/kronos-causal/history.csv).
- [Chẩn đoán ngày biến động mạnh](../artifacts/local/vn30-finetune-20261027/evaluation-test/volatility_diagnostic.csv) và [chẩn đoán Open](../artifacts/local/vn30-finetune-20261027/evaluation-test/open_pattern_diagnostic.csv).
- [Điểm theo rolling volatility](../artifacts/local/vn30-finetune-20261027/report-q1-q4/rolling_volatility_scores.csv), [origin và volatility](../artifacts/local/vn30-finetune-20261027/report-q1-q4/origin_volatility_regimes.csv), [định nghĩa/ngưỡng/kiểm tra](../artifacts/local/vn30-finetune-20261027/report-q1-q4/regime_manifest.json).

Phân tích rolling volatility không chạy lại model. Kiểm tra tổng hợp xác nhận MAE trung bình có trọng số và RMSE suy ra từ MSE của hai nhóm khớp điểm toàn test; không có origin bị bỏ khi phân nhóm.

"""Build the approved Paper & Ink HTML from verified PC CSVs, without model runs.

Run from the repository root: python docs/slides/build_deck.py
All browser dependencies and Vietnamese fonts are embedded for offline use.
"""
from pathlib import Path
import csv
import hashlib
import html
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "artifacts/local/pc-exploratory-20261030/final-report"
VENDOR = HERE / "vendor"
OUT = HERE / "vn30-paper-ink.html"
REV = "10180073ec60ff7cdb1f67009398f1b1ae9b8563"
GITHUB = f"https://github.com/HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting/blob/{REV}/"
inputs = set()


def esc(value):
    return html.escape(str(value), quote=True)


def read_csv(name):
    path = DATA / name
    inputs.add(path)
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(value, digits=3):
    return f"{float(value):,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def table(headers, rows, widths=None, cls="", highlight=()):
    cols = "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in widths) + "</colgroup>" if widths else ""
    head = "<thead><tr>" + "".join(f'<th scope="col">{x}</th>' for x in headers) + "</tr></thead>"
    body = "<tbody>" + "".join('<tr' + (' class="key-row"' if i in highlight else '') + '>' + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for i, row in enumerate(rows)) + "</tbody>"
    return f'<table class="deck-table {cls}">{cols}{head}{body}</table>'


def statement(text):
    return f'<div class="statement">{text}</div>'


def brief(text):
    return f'<p class="brief">{text}</p>'


def flow(items):
    return '<div class="flow">' + "".join(f'<div class="flow-step"><strong>{a}</strong><span>{b}</span></div>' for a, b in items) + '</div>'


def svg_text(x, y, text, size=28, anchor="start", color="#151610", weight=400):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{esc(text)}</text>'


def line(x1, y1, x2, y2, color="#c8c7bd", width=1.5, dash=""):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'


def svg_start(w, h, label):
    return f'<svg class="data-chart" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" xmlns="http://www.w3.org/2000/svg"><title>{esc(label)}</title>'


def grouped_bars(labels, series, ymax, width=1100, height=430, reference=None):
    # Editable data chart; no rasterized text or illustrative values.
    left, right, top, bottom = 88, 35, 66, 70
    pw, ph = width - left - right, height - top - bottom
    y = lambda v: top + ph * (1 - v / ymax)
    parts = [svg_start(width, height, "MAE theo nhóm, đơn vị điểm chỉ số, thấp hơn tốt hơn")]
    for tick in range(5):
        val = ymax * tick / 4
        yy = y(val)
        parts += [line(left, yy, width - right, yy), svg_text(left - 15, yy + 9, num(val, 0), 25, "end", "#65665e")]
    for j, (name, values, deviations, color) in enumerate(series):
        xx = left + j * (pw / len(series))
        parts += [f'<rect x="{xx}" y="12" width="21" height="21" fill="{color}"/>', svg_text(xx + 33, 31, name, 25)]
        for i, value in enumerate(values):
            group = pw / len(labels)
            bw = min(90, group / (len(series) + 1))
            xx = left + group * (i + .5) + (j - (len(series) - 1) / 2) * (bw + 13) - bw / 2
            parts += [f'<rect x="{xx:.2f}" y="{y(value):.2f}" width="{bw:.2f}" height="{y(0)-y(value):.2f}" fill="{color}"/>']
            if deviations is not None:
                sd = deviations[i]
                cx = xx + bw / 2
                parts += [line(cx, y(value - sd), cx, y(value + sd), "#151610", 2), line(cx - 9, y(value + sd), cx + 9, y(value + sd), "#151610", 2), line(cx - 9, y(value - sd), cx + 9, y(value - sd), "#151610", 2)]
            parts.append(svg_text(xx + bw / 2, y(value + (deviations[i] if deviations is not None else 0)) - 12, num(value, 1), 25, "middle"))
    if reference is not None:
        parts += [line(left, y(reference), width - right, y(reference), "#65665e", 2.5, "8 8"), svg_text(width - right, 57, "Nét đứt: Naive " + num(reference), 23, "end")]
    for i, label in enumerate(labels):
        parts.append(svg_text(left + pw / len(labels) * (i + .5), height - 22, label, 28, "middle"))
    return "".join(parts) + '</svg>'


MAIN = read_csv("main_summary.csv")


def main_score(model, target, horizon):
    return next(r for r in MAIN if (r["model"], r["split"], r["target"], int(r["horizon"])) == (model, "test", target, horizon))


def score_table(target, ridge=False):
    models = [("naive", "Naive")]
    if ridge:
        models.append(("ridge", "Ridge"))
    models += [("kronos-mini-ft", "Kronos-mini SFT"), ("kronos-small-ft", "Kronos-small SFT"), ("kronos-base-ft", "Kronos-base SFT"), ("chronos2-ft", "Chronos-2-small SFT")]
    rows = []
    for model, label in models:
        values = []
        for h in (1, 5, 20):
            r = main_score(model, target, h)
            value = num(r["mae"])
            if model.endswith("-ft"):
                value += f'<span class="sd"> ± {num(r["mae_sd"])}</span>'
            values.append(value)
        rows.append([label] + values)
    return table(["Model", "Sau 1 phiên", "Sau 5 phiên", "Sau 20 phiên"], rows, [31, 23, 23, 23], "dense scores", highlight=(0,))


def learning_chart(model, title):
    rows = [r for r in read_csv("learning_curve.csv") if r["model"] == model and r["split"] == "test" and r["target"] == "close" and r["horizon"] == "20"]
    w, h, left, right, top, bottom = 815, 355, 78, 32, 85, 63
    pw, ph = w - left - right, h - top - bottom
    xx = lambda n: left + (n - 500) / 1089 * pw
    yy = lambda n: top + ph * (1 - n / 210)
    parts = [svg_start(w, h, title + ": MAE Close sau 20 phiên"), svg_text(left, 32, title, 31, weight=600)]
    for tick in (0, 50, 100, 150, 200):
        parts += [line(left, yy(tick), w - right, yy(tick)), svg_text(left - 12, yy(tick) + 8, str(tick), 24, "end", "#65665e")]
    for j, (init, label, color, dash) in enumerate((("pretrained", "Pre-trained", "#151610", ""), ("random", "Random init", "#83847a", "9 6"))):
        xlegend = left + j * 270
        parts += [line(xlegend, 58, xlegend + 38, 58, color, 4, dash), svg_text(xlegend + 48, 67, label, 23)]
        values = sorted([r for r in rows if r["initialization"] == init], key=lambda r: int(r["train_rows"]))
        points = " ".join(f'{xx(int(r["train_rows"])):.2f},{yy(float(r["mae"])):.2f}' for r in values)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="4" stroke-dasharray="{dash}"/>')
        for r in values:
            x, y, sd = xx(int(r["train_rows"])), yy(float(r["mae"])), float(r["mae_sd"])
            parts += [line(x, yy(float(r["mae"]) - sd), x, yy(float(r["mae"]) + sd), color, 2), f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{color}"/>']
    for n in (500, 1000, 1589):
        parts.append(svg_text(xx(n), h - 25, num(n, 0), 25, "middle"))
    return ''.join(parts) + '</svg>'


def forest():
    rows = [r for r in read_csv("paired_intervals.csv") if r["group"] == "evaluation-main/scores/seed-42/test" and r["target"] == "close"]
    parts = [svg_start(1698, 430, "Khoảng tin cậy 95% cho chênh lệch MAE với Naive, seed 42")]
    models = [("kronos-mini-ft", "Mini"), ("kronos-small-ft", "Small"), ("kronos-base-ft", "Base"), ("chronos2-ft", "Chronos")]
    for panel, horizon in enumerate((1, 5, 20)):
        values = [next(r for r in rows if r["model"] == m and int(r["horizon"]) == horizon) for m, _ in models]
        low = min(-.5, min(float(r["ci_low"]) for r in values))
        high = max(float(r["ci_high"]) for r in values)
        span = high - low
        low, high = low - span * .12, high + span * .12
        offset, left, right = panel * 566, 110, 520
        x = lambda v: offset + left + (v - low) / (high - low) * (right - left)
        parts += [svg_text(offset + 290, 40, f"Sau {horizon} phiên", 30, "middle", weight=600), line(x(0), 68, x(0), 350, "#65665e", 2, "7 7")]
        for i, ((model, label), row) in enumerate(zip(models, values)):
            y = 105 + i * 73
            a, b, point = [float(row[k]) for k in ("ci_low", "ci_high", "difference")]
            parts += [svg_text(offset + 90, y + 9, label, 27, "end"), line(x(a), y, x(b), y, "#151610", 4), line(x(a), y - 9, x(a), y + 9, "#151610", 2), line(x(b), y - 9, x(b), y + 9, "#151610", 2), f'<circle cx="{x(point):.2f}" cy="{y}" r="7" fill="#151610"/>']
        for tick in (math.ceil(low), 0, math.floor(high)):
            parts += [line(x(tick), 358, x(tick), 367, "#65665e", 2), svg_text(x(tick), 402, num(tick, 0), 25, "middle", "#65665e")]
    return ''.join(parts) + '</svg>'


def volatility_chart():
    rows = [r for r in read_csv("origin_regimes.csv") if r["group"] == "evaluation-main/scores/seed-42/test"]
    assert len(rows) == 323
    parts = [svg_start(1698, 170, "Volatility từ 20 log-return đã biết tại 323 forecast origins")]
    x = lambda i: 15 + i / (len(rows) - 1) * 1668
    y = lambda v: 132 - v / .045 * 90
    threshold = float(rows[0]["train_p90"])
    for i, row in enumerate(rows):
        if row["regime"] == "high":
            parts.append(f'<rect x="{x(i)-2.8:.2f}" y="26" width="5.6" height="110" fill="#d1cfc5"/>')
    parts.append(line(15, y(threshold), 1683, y(threshold), "#83847a", 2, "8 8"))
    points = ' '.join(f'{x(i):.2f},{y(float(r["sigma20"])):.2f}' for i, r in enumerate(rows))
    parts.append(f'<polyline points="{points}" fill="none" stroke="#151610" stroke-width="2.5"/>')
    for n, indices in enumerate((range(0,108),range(108,216),range(216,323)),1):
        a,b=indices.start,indices.stop-1
        parts += [line(x(a), 146, x(b), 146, "#c8c7bd", 2),svg_text((x(a)+x(b))/2, 168, f"Đoạn {n} · {len(indices)} origins", 23, "middle")]
    parts += [svg_text(20, 20, "Vùng tô: 17 forecast origins vượt threshold", 24),svg_text(1680, 20, "Nét đứt: train volatility p90", 24, "end")]
    return ''.join(parts) + '</svg>'


slides = []


def add(identifier, title, section, body, takeaway, source, notes, files=()):
    idx = len(slides) + 1
    full_files = ["docs/VN30_PC_Research_Report.md"] + [f[5:] if f.startswith("repo:") else "artifacts/local/pc-exploratory-20261030/final-report/" + f for f in files]
    links = ''.join(f'<li><a href="{GITHUB + esc(f)}">{esc(f)}</a></li>' for f in full_files)
    for f in full_files:
        assert (ROOT / f).is_file(), f
        inputs.add(ROOT / f)
    notes_html = f'<p>{notes}</p><p>Source boundary: snapshot VNDIRECT. Dataset acceptance vẫn chưa đạt; kết quả mô tả prediction so với các label của snapshot. Evaluation hồi cứu, chưa xác minh đầy đủ pre-training exclusions.</p><ul>{links}</ul>'
    html_body = body + (statement(takeaway) if takeaway else '')
    slides.append(f'''<section id="{identifier}" aria-label="{esc(title)}">
<div class="frame content-slide">
<p class="eyebrow">VN30 / {esc(section)}</p>
<div class="heading"><span class="section-number" data-section></span><h2 class="action-title">{title}</h2></div>
<div class="body compact-body">{html_body}</div>
<footer class="chrome-foot"><p class="source">{source}</p><span data-page></span></footer><div class="bottom-rule" aria-hidden="true"></div>
</div><aside class="notes">{notes_html}</aside></section>''')


# Content revision 2: approved 20-slide structure, unchanged experiment results.
resources = read_csv('resources.csv')
selection = read_csv('checkpoint_selection.csv')
history_path = ROOT / 'artifacts/local/pc-exploratory-20261030/checkpoints/train-kronos-small-s42/history.csv'
inputs.add(history_path)
with history_path.open(encoding='utf-8', newline='') as stream:
    loss_history = list(csv.DictReader(stream))
initial_loss = float(next(r for r in selection if r['model']=='kronos-small' and r['seed']=='42')['initial_validation_loss'])
validation_losses = [initial_loss] + [float(r['validation_loss']) for r in loss_history]
assert len(validation_losses)==6 and validation_losses.index(min(validation_losses))==5


def validation_chart():
    w,h,left,right,top,bottom = 960,300,110,40,55,60
    x=lambda i:left+i/5*(w-left-right)
    y=lambda v:top+(2.18-v)/.24*(h-top-bottom)
    parts=[svg_start(w,h,'Kronos-small seed 42, validation loss thực tế từ epoch 0 đến 5'),
           svg_text(left,30,'Kronos-small · seed 42 · validation loss',26,weight=600)]
    for tick in (1.95,2.00,2.05,2.10,2.15):
        parts += [line(left,y(tick),w-right,y(tick)),svg_text(left-14,y(tick)+8,num(tick,2),24,'end','#65665e')]
    points=' '.join(f'{x(i):.2f},{y(v):.2f}' for i,v in enumerate(validation_losses))
    parts.append(f'<polyline points="{points}" fill="none" stroke="#151610" stroke-width="4"/>')
    for i,v in enumerate(validation_losses):
        parts += [f'<circle cx="{x(i):.2f}" cy="{y(v):.2f}" r="6" fill="#151610"/>',
                  svg_text(x(i),h-20,str(i),25,'middle')]
    parts += [svg_text(x(0)+12,y(validation_losses[0])-14,num(validation_losses[0]),24),
              svg_text(x(5),y(validation_losses[-1])-15,num(validation_losses[-1]),24,'end')]
    return ''.join(parts)+'</svg>'


sample_path = ROOT/'demo/data/vn30.csv'
forecast_path = ROOT/'artifacts/local/pc-exploratory-20261030/evaluation-main/forecasts/naive-s42-zs-test.csv'
inputs.update((sample_path,forecast_path))
with sample_path.open(encoding='utf-8',newline='') as stream:
    sample={r['date']:r for r in csv.DictReader(stream)}
with forecast_path.open(encoding='utf-8',newline='') as stream:
    naive_rows=[r for r in csv.DictReader(stream) if r['horizon']=='1']
example=next(r for r in naive_rows if r['target_date']=='2025-05-21')
origin_close=float(sample[example['origin_date']]['close'])
actual_open=float(sample[example['target_date']]['open'])
naive_open=float(example['pred_open'])
assert origin_close==actual_open==naive_open==1407.52
anomalous=[r for r in naive_rows if '2025-05-05'<=r['target_date']<='2025-08-11']
assert len(anomalous)==59 and all(float(r['pred_open'])==float(sample[r['target_date']]['open']) for r in anomalous)

slides.append('''<section id="mo-dau" aria-label="Kronos-VN30-Time-series-Forecasting"><div class="frame title-slide">
<p class="eyebrow">1NSIDER</p><div class="heading"><span class="section-number" data-section></span>
<h1 class="title">Kronos-VN30-<br>Time-series-Forecasting</h1></div>
<div class="body hero"><div class="statement cover-team">Nhóm <strong>1nsider</strong></div>
<div class="members"><p>Vi Nguyễn Ngọc Châu</p><p>Nguyễn Hoàng Kiên</p></div></div>
<footer class="chrome-foot"><span data-page></span></footer><div class="bottom-rule" aria-hidden="true"></div></div>
<aside class="notes"><p>Nhóm 1nsider. Thành viên: Vi Nguyễn Ngọc Châu, Nguyễn Hoàng Kiên. Project Kronos-VN30-Time-series-Forecasting. Nghiên cứu so sánh Kronos mini/small/base, Chronos-2-small và bốn baseline trên cùng snapshot VN30.</p></aside></section>''')

add('cau-hoi','Bốn câu hỏi nghiên cứu','MỤC TIÊU',
    table(['Câu hỏi','Điều cần kiểm tra','Experiment'],[
        ['<strong>Q1</strong>','Pre-trained model có MAE thấp hơn baseline?','Naive / Ridge / ARIMA / ETS'],
        ['<strong>Q2</strong>','Model lớn hơn và quantize có giúp MAE giảm?','Model size và quantize ablation'],
        ['<strong>Q3</strong>','Data budget và pre-training giúp đến đâu?','Learning curve, pre-trained / random'],
        ['<strong>Q4</strong>','MAE có ổn định qua lần chạy và giai đoạn khác?','Seed / horizon / volatility / fold'],
    ],[10,52,38]),
    'MAE là error tuyệt đối trung bình. <strong>MAE thấp hơn nghĩa là prediction sát label hơn.</strong>',
    'Nguồn: Báo cáo thực nghiệm · Bảng kết quả Q1–Q4',
    'Baseline là phương pháp làm chuẩn so sánh. Q2 kiểm tra hai việc: so các hệ thống mini/small/base và thay riêng bước quantize trong ablation. Q4 kiểm tra MAE khi đổi seed, prediction horizon và giai đoạn test. Một model tốt ở một giai đoạn chưa chắc tiếp tục tốt ở giai đoạn khác.',['main_summary.csv'])

add('baseline-naive-ridge','Baseline · Naive và Ridge','NỀN TẢNG',
    brief('Baseline là phương pháp dùng làm chuẩn để kiểm tra model phức tạp có thực sự tốt hơn không.')
    + table(['Model','Cách predict','Ví dụ minh họa'],[
        ['<strong>Naive</strong>','Không train. Dùng Close cuối input cho mọi target session.','Close gần nhất = 102<br>Prediction = <strong>102</strong>'],
        ['<strong>Ridge</strong>','Fit quan hệ tuyến tính giữa input quá khứ và target. Regularization hạn chế weight quá lớn.','Minh họa 2 features:<br>0,3 × 100 + 0,7 × 102 = <strong>101,4</strong>'],
    ],[16,44,40]),
    'Weight của Ridge được fit từ train. Ví dụ 0,3 / 0,7 chỉ để giải thích, không phải weight đã fit.',
    'Nguồn: Adapter Ridge / Naive · baseline_selection.csv',
    'Naive không train và không nhìn target Open tương lai. Ridge thực tế dùng 128 × 4 OHLC features; scaler input và target chỉ fit trên train, output gồm 20 × 4 giá trị. Công thức Ridge: prediction = bias + tổng weight_i × feature_i. Alpha điều khiển regularization, tức hạn chế weight quá lớn; alpha = 10 được chọn trên validation từ 1/10/100/1000. Ví dụ giá 100/102 và weight 0,3/0,7 trên slide chỉ minh họa, không phải weight đã fit.',['baseline_selection.csv','repo:src/vn30_forecast.py'])

add('baseline-arima-ets','Baseline · ARIMA và ETS','NỀN TẢNG',
    table(['Model','Thông tin dùng để predict','Cấu hình trong experiment'],[
        ['<strong>ARIMA</strong>','Lag của chuỗi, differencing (chênh lệch giữa phiên) và error quá khứ.','ARIMA(0,1,0)<br>Close tương lai giữ bằng Close cuối.'],
        ['<strong>ETS</strong>','Exponential smoothing: cập nhật level từ quan sát mới; có thể thêm trend.','Chỉ level, không trend / seasonal.<br>Close fit được trùng Naive trong kết quả này.'],
    ],[17,46,37])
    + brief('ARIMA/ETS fit lại từng kênh trên 128 session tại mỗi forecast origin. Cấu hình chọn bằng validation, không chọn bằng test.'),
    'ARIMA/ETS và Naive trùng Close prediction trong experiment này. Open prediction có thể khác.',
    'Nguồn: statistical_baselines.py · baseline_selection.csv',
    'ARIMA là AutoRegressive Integrated Moving Average. AR dùng lag của chuỗi, I là differencing, MA dùng error quá khứ. Trong cấu hình (0,1,0) không drift, prediction bằng giá trị cuối của kênh. ETS ở đây dùng exponential smoothing, thử level, additive trend và damped trend, không seasonal. Cấu hình level được chọn cho Close prediction trùng Naive trong experiment này. ARIMA/ETS fit Open riêng với Close; Naive dùng Close cho cả hai nên Open error không trùng. Lỗi convergence được ghi, không có fallback thay bằng Naive.',['baseline_selection.csv','repo:src/statistical_baselines.py'])

add('cach-kronos-du-bao','Kiến trúc Kronos','KIẾN TRÚC',
    flow([('Input','128 session OHLC'),('Tokenization','Encode + quantize'),('Predictor','Causal Transformer'),('Decode','Token thành OHLC'),('Output','20 target session')])
    + table(['Thành phần','Vai trò','Khi SFT'],[
        ['<strong>Tokenizer</strong>','Encoder tạo features, quantize thành token, decoder khôi phục OHLC.','Giữ nguyên weight'],
        ['<strong>Predictor</strong>','Dùng token quá khứ để predict token tiếp theo, lặp cho các session đích.','Cập nhật weight'],
    ],[23,55,22],'dense')
    + brief('OHLC: Open, High, Low, Close. Snapshot thiếu volume/amount, adapter điền 0.'),
    '', 'Nguồn: KronosTokenizer / Kronos · Source revision đã khóa',
    'KronosTokenizer gồm encoder/decoder Transformer và Binary Spherical Quantization (BSQ). API encode thực tế gồm embed, encoder, quant_embed và quantizer rồi trả token IDs. Sơ đồ tách encode features và quantize để giải thích rõ vai trò. Predictor có hierarchical token embedding, temporal embedding, causal Transformer, s1 head và conditional s2 head. S2 phụ thuộc s1 trong cùng bước. Causal nghĩa là chỉ nhìn token quá khứ để predict token tiếp theo. Decode chuyển token về OHLC rồi khôi phục thang giá. Khi SFT, tokenizer giữ nguyên weight, predictor được cập nhật weight. Volume/amount thiếu được điền 0, không phải khối lượng giao dịch thực.',['repo:demo/vendor/kronos/model/kronos.py'])

add('cac-model','Kronos và các model còn lại','SO SÁNH',
    table(['Model / tham số','Cách xử lý input','Output'],[
        ['Naive / Ridge / ARIMA / ETS','Quy tắc hoặc fit trực tiếp trên dữ liệu VN30.','Numeric prediction'],
        ['Kronos-mini · 4,1M','Pre-trained Transformer, Tokenizer-2k.','Predict token, decode OHLC'],
        ['Kronos-small · 24,7M','Pre-trained Transformer, Tokenizer-base.','Predict token, decode OHLC'],
        ['Kronos-base · 102,3M','Pre-trained Transformer, Tokenizer-base.','Predict token, decode OHLC'],
        ['Chronos-2-small · 27,9M','Pre-trained cho chuỗi thời gian tổng quát.','Numeric quantile predictions'],
    ],[33,41,26],'dense')
    + brief('Cả ba Kronos và Chronos có zero-shot (dùng weight pre-trained) và SFT (train thêm trên VN30). Mini khác tokenizer nên không tách riêng được tác động số tham số.'),
    '', 'Nguồn: Model/tokenizer provenance · resources.csv',
    'M là triệu tham số. Các baseline trong thiết lập này không dùng weight pre-trained từ tập dữ liệu lớn bên ngoài: Naive dùng quy tắc, Ridge/ARIMA/ETS fit theo dữ liệu VN30. Kronos được pre-trained cho chuỗi OHLC với tokenization. Chronos là đối chứng chuỗi thời gian tổng quát và trả quantile predictions. Mini dùng tokenizer khác small/base nên so mini với small/base không đo riêng tác động của số tham số. SFT trong bảng kết quả là best-trained; selected có thể giữ epoch 0. Không so native loss giữa các họ model khác nhau.',['resources.csv'])

add('du-lieu','Session và forecast origin','DATASET',
    '<p class="lead"><strong>2.271 session</strong> · VN30 · 24/08/2017–01/10/2026</p>'
    + table(['Split','Thời gian','Session','Forecast origins'],[
        ['Train','24/08/2017–29/12/2023','1.589','1.442'],
        ['Validation','02/01/2024–20/05/2025','340','321'],
        ['Test','21/05/2025–01/10/2026','342','323'],
    ],[17,43,16,24],'dense')
    + '<div class="window-strip small-window"><div class="context"><b>128 input session</b><span>Forecast origin = thời điểm chốt input</span></div><div class="future"><b>20 target session</b><span>Chỉ giữ origin đủ 20 target trong split</span></div></div>',
    'Session là một phiên giao dịch. Test có <strong>342 − 20 + 1 = 323</strong> lần inference đủ target.',
    'Nguồn: Split đã khóa · Context 128 / prediction horizon 20',
    'Session là một phiên giao dịch, tương ứng một dòng OHLC. Forecast origin là session cuối input, sau khi đã có Close. Các origins liền nhau có input và target chồng lấn. Origin đầu của test là 20/05/2025, target đầu là 21/05/2025. Context 128 session được lấy từ quá khứ trước biên test, nên không trừ thêm 128 khi tính số test origins: 342 - 20 + 1 = 323. Train windows phải có cả input và target nằm trong train: 1589 - 128 - 20 + 1 = 1442. Request bắt đầu năm 2012 nhưng snapshot chỉ có từ 2017; một hàng ngoài request vẫn được giữ để đối chiếu, không tự nội suy session.')

add('kiem-tra-du-lieu','Pre-process data','DATASET',
    table(['Bước','Thao tác thực tế','Cách giữ dữ liệu'],[
        ['Khôi phục','Kiểm hash, SQLite integrity và raw replay.','Giữ snapshot gốc.'],
        ['Timestamp / session','Kiểm timestamp, duplicate, missing session và ngày ngoài request.','Đối chiếu lịch nguồn, không tự điền phiên.'],
        ['OHLC','Kiểm giá hữu hạn, quan hệ O/H/L/C và Open bằng Close trước.','Lưu các trường hợp cần phân tích.'],
        ['Cross-source check','So từng trường với VPS/DNSE, lưu chênh lệch theo ngày.','Không ghép hoặc sửa giá theo từng ô.'],
    ],[22,48,30],'dense'),
    '', 'Nguồn: Raw replay / audit / source comparison',
    'Slide mô tả các bước pre-process đã làm, không tuyên bố mọi khác biệt đã xử lý xong. Audit giữ unverified: 1.230 phép so sánh OHLC khác nguồn hơn 0,02 điểm, gồm 60 ngày Close khác nguồn; có 78 Open bằng Close trước, trong đó 71 phiên liên tiếp từ 05/05 đến 11/08/2025. Đây là số phép so sánh khác nhau, chưa phải số lỗi VNDIRECT đã chứng minh. Calendar khớp lịch VNINDEX quan sát từ VPS, chưa là xác nhận lịch sàn chính thức. Không điền session thiếu, không sửa giá, không ghép nguồn theo từng ô.',['data_adjudication.csv'])

add('quy-trinh','Inference và prediction cuối','INFERENCE',
    brief('<strong>Ví dụ minh họa</strong> tại hai target session. Số trong hai bảng không phải output thực nghiệm.')
    + '<div class="two-col aligned"><div><h3>Kronos · sample 3 paths</h3>'
    + table(['Path','t+1','t+2'],[['A','100','102'],['B','102','100'],['C','101','101'],['<strong>Mean</strong>','<strong>101</strong>','<strong>101</strong>']],[46,27,27],'extra-dense scores',highlight=(3,))
    + brief('Cùng input, sample 3 paths dài 20 session. Lấy mean tại từng target session.')
    + '</div><div><h3>Chronos · quantile output</h3>'
    + table(['Quantile minh họa','t+1','t+2'],[['q10 · mức thấp','98','99'],['q50 · median','101','102'],['q90 · mức cao','104','105']],[54,23,23],'extra-dense scores')
    + brief('Trong experiment, lấy mean của đủ <strong>13 quantile</strong> tại từng target session.')
    + '</div></div>',
    'Sampled paths và quantile là hai loại output khác nhau. Ba paths không phải ba model hay ba training seed.',
    'Nguồn: Adapter Kronos / Chronos · Aggregation đã khóa',
    'Inference là chạy model với input để tạo prediction. Kronos sample 3 paths, mỗi path dài 20 session, dùng T = 1 và top-p = 0,9; cuối cùng lấy mean theo từng target session và từng kênh. Chronos trả 13 quantile levels. Q50 là median; q10/q90 là vị trí thấp/cao trong phân phối prediction. Ví dụ trên slide chỉ hiện 3 mức để giải thích, không phải experiment chỉ dùng 3 quantile. Implementation lấy mean của đủ 13 quantile, không gọi đó là median hoặc kỳ vọng chính xác, cũng không phải 13 random paths. Ba seed 42/43/44 là ba lần chạy experiment, khác với 3 sampled paths trong mỗi lần.',['repo:src/vn30_forecast.py'])

epoch_rows=[['Kronos mini / small / base','5','5'],['Chronos-2-small','1','0']]
add('chon-checkpoint','Train và checkpoint selection','TRAIN',
    '<div class="two-col chart-cost"><div>'+validation_chart()+'</div><div>'
    + table(['Model','SFT','Sel.¹'],epoch_rows,[58,20,22],'dense')
    + brief('¹ Selected được xét cả epoch 0, tức weight pre-trained trước khi train thêm.')
    + '</div></div>'
    + brief('Epoch = một lượt train qua training windows. Budget: 5 epoch, AdamW, LR 1e-6, batch 16.'),
    'Best epoch 5 là tốt nhất <strong>đã thử</strong>. Chưa khẳng định train đã hội tụ.',
    'Nguồn: history.csv · Kronos-small seed 42 · checkpoint_selection.csv',
    'Checkpoint là bản lưu weight model. Epoch là một lượt train qua training windows. Curve là validation loss thực tế của Kronos-small, seed 42, từ epoch 0 đến 5, không phải test MAE. Validation loss vẫn giảm tới giới hạn cuối nên còn khả năng cải thiện nếu train thêm, nhưng chưa kiểm chứng và không đủ để kết luận chắc chắn underfit. Không train thêm trong đợt sửa slide. Cả ba Kronos chọn epoch 5 và Chronos chọn epoch 0 ở cả ba seed. Best-trained Chronos là epoch 1. Trong bảng, Sel. là selected có xét epoch 0. Không dùng test để chọn epoch hoặc so native loss giữa tokenizer/model khác nhau.',['checkpoint_selection.csv','repo:artifacts/local/pc-exploratory-20261030/checkpoints/train-kronos-small-s42/history.csv'])

add('q1-close','Q1 · Close MAE','KẾT QUẢ',
    brief('Đơn vị: điểm chỉ số. <strong>Thấp hơn là tốt hơn.</strong> Mean ± SD từ seed 42 / 43 / 44.')
    + score_table('close',True),
    'Trong bảng chính, neural model chưa có MAE thấp hơn Naive khi lấy mean ba seed.',
    'Nguồn: main_summary.csv · Test 323 forecast origins',
    'MAE là mean absolute error, đơn vị điểm chỉ số. Mean ± SD mô tả ba seed 42/43/44. SFT trong bảng là best-trained để đo tác động cập nhật, không phải mọi selected checkpoint. Chronos selected giữ epoch 0. ARIMA/ETS Close trùng Naive trong experiment này, không phải ba bằng chứng độc lập. SD giữa seed không phải confidence interval theo thị trường. CSV có đủ validation/test, zero-shot và RMSE.',['main_summary.csv'])

open_one=[num(main_score(m,'open',1)['mae']) for m in ['naive','kronos-mini-ft','kronos-small-ft','kronos-base-ft','chronos2-ft']]
add('q1-open','Q1 · Vì sao Naive Open error = 0?','KẾT QUẢ',
    brief('Naive: Open prediction[t+1] = Close[t]. Ngày 20/05/2025: Close = <strong>1.407,52</strong>.')
    + table(['Origin','Target','Naive predict','Actual Open','Abs. error'],[
        ['20/05/2025','21/05/2025',num(naive_open,2),num(actual_open,2),'<strong>0,00</strong>']
    ],[20,20,22,22,16],'dense scores')
    + '<div class="diagnosis"><p><strong>59 origins trong đoạn Open đặc biệt</strong><br><span>Naive Open MAE = 0,000</span></p><p><strong>264 origins còn lại</strong><br><span>Naive Open MAE = 7,291</span></p></div>'
    + table(['Open h=1 MAE','Naive','Mini SFT','Small SFT','Base SFT','Chronos SFT'],[['Mean']+open_one],[17,14,17,17,17,18],'extra-dense scores'),
    'Trong snapshot: Open[t+1] = Close[t] nên error = 0. <strong>Naive không có rule riêng cho 59 origins.</strong>',
    'Nguồn: Snapshot VN30 + prediction CSV của Naive · Ví dụ dữ liệu thật',
    'Dữ liệu thật: Close ngày 20/05/2025 = 1407,52; Open ngày 21/05/2025 = 1407,52; Naive Open prediction = 1407,52. Absolute error = |1407,52 - 1407,52| = 0. Hàng này đã đối chiếu SQLite gốc, CSV sample và naive-s42-zs-test.csv. Có 59 origins h=1 có target trong đoạn Open 05/05–11/08/2025, đều cho error bằng 0. Naive không có rule riêng cho nhóm này, không sửa forecast và không nhìn target. Nhãn Open bằng Close trước làm Naive được lợi trên metric, không chứng minh predict giá mở cửa chính thức hoàn hảo. Trên 264 origins còn lại, MAE = 7,291; toàn bộ 323 origins, MAE = 5,959. Full Open h=5/20 và SD có trong CSV nguồn.',['main_summary.csv','repo:demo/data/vn30.csv','repo:artifacts/local/pc-exploratory-20261030/evaluation-main/forecasts/naive-s42-zs-test.csv'])

zero=[float(main_score('kronos-'+v,'close',20)['mae']) for v in ('mini','small','base')]
ft=[float(main_score('kronos-'+v+'-ft','close',20)['mae']) for v in ('mini','small','base')]
costs=[next(r for r in resources if r['model']=='kronos-'+v) for v in ('mini','small','base')]
chart13=grouped_bars(['Mini','Small','Base'],[('Zero-shot',zero,None,'#aaa99f'),('SFT',ft,None,'#151610')],200,width=1000,reference=float(main_score('naive','close',20)['mae']))
add('q2-kich-thuoc','Q2 · Model size và SFT','KẾT QUẢ',
    '<div class="two-col chart-cost"><div>'+chart13+'</div><div>'
    + table(['Model','Train (giây)','GiB¹'],[[r['model'].replace('kronos-','').title(),num(r['train_seconds_mean'],1),num(r['peak_allocated_GiB'])] for r in costs],[30,38,32],'dense')
    + brief('¹ Peak tensor memory khi train, không phải tổng VRAM hoặc inference cost.')
    + '</div></div>'
    + brief('Close h=20. Mini SFT tốt hơn small SFT tại cả ba horizon. Base SFT tốt hơn mini tại h=20, chưa tốt hơn tại h=1/5.'),
    f'Base: SFT giảm Close h=20 MAE <strong>{num(zero[2]-ft[2])} điểm</strong>, vẫn cao hơn Naive.',
    'Nguồn: main_summary.csv / resources.csv · GPU RTX 4070 SUPER',
    'Model size là số tham số, không bảo đảm prediction chính xác hơn. Ba Kronos lần lượt khoảng 4,1M / 24,7M / 102,3M. Mini dùng tokenizer khác nên không đo tác động riêng của số tham số. Train seconds là tổng thời gian SFT của mỗi lượt, lấy mean ba seed, không phải inference time. Peak tensor allocation khác tổng VRAM của process. Close h=20 của base giảm từ 166,781 xuống 98,849, cải thiện 67,932 điểm; Naive vẫn thấp hơn ở 93,826.',['main_summary.csv','resources.csv'])

add('tokenization-quantize','Tokenization và quantize','GIẢI THÍCH',
    flow([('OHLC','Numeric input'),('Encode','Continuous features'),('Quantize','Features thành mã hữu hạn'),('Token IDs','Input cho predictor')])
    + table(['Khái niệm','Ý nghĩa'],[
        ['<strong>Tokenization</strong>','Toàn bộ quá trình chuyển input thành token mà predictor xử lý.'],
        ['<strong>Quantize</strong>','Một bước trong tokenization: chuyển continuous features thành discrete codes (mã hữu hạn).'],
    ],[24,76],'dense')
    + '<div class="formula">Ví dụ minh họa theo dấu: [0,2; −0,7] → bits [1; 0]</div>',
    '',
    'Nguồn: KronosTokenizer / BSQuantizer · Ví dụ chỉ minh họa cơ chế',
    'Tokenization là toàn bộ quá trình chuyển input thành token; quantize là một bước trong đó. BSQ là Binary Spherical Quantization: latent vector được chuẩn hóa rồi quantize theo dấu; các bits tạo token IDs. Ví dụ hai chiều trên slide chỉ minh họa positive thành bit 1, negative thành bit 0, lược bỏ normalization, scale và hierarchical split. Không phải token thật của một session VN30. Encode API thực tế đã gồm quantize, sơ đồ tách ra để giải thích. Decode dùng weight đã học để khôi phục OHLC, không phải đảo bit thành giá bằng một công thức đơn giản.',['repo:demo/vendor/kronos/model/kronos.py','repo:demo/vendor/kronos/model/module.py'])

ablation=read_csv('ablation_summary.csv')
bar_values=[]
for model,label,color in [('representation-continuous','Trước quantize','#aaa99f'),('representation-quantized','Sau quantize','#151610')]:
    rr=[next(r for r in ablation if r['model']==model and r['split']=='test' and r['target']=='close' and int(r['horizon'])==h) for h in (1,5,20)]
    bar_values.append((label,[float(r['mae']) for r in rr],[float(r['mae_sd']) for r in rr],color))
add('q2-luong-tu-hoa','Q2 · Quantize ablation','KẾT QUẢ',
    '<div class="ablation-branches"><p><strong>A</strong> Encoder cố định · continuous features · predictor</p><p><strong>B</strong> Cùng encoder · <b>quantize</b> · cùng predictor initialization</p></div>'
    + grouped_bars(['h=1','h=5','h=20'],bar_values,200,width=1698,height=320),
    'Giữ data, initialization và train budget giống nhau. Quantize chưa giúp Close MAE giảm đồng nhất.',
    'Nguồn: ablation_summary.csv · MAE Close, mean ± SD ba seed',
    'Ablation nghĩa là thay riêng một thành phần để đo đóng góp. Hai nhánh dùng cùng fixed small encoder, cùng random small backbone, numeric head/MSE, data và train budget. Nhánh A dùng L2-normalized features trước BSQ; nhánh B dùng features sau BSQ. Initialization hash khớp theo từng seed. Đây là một representation ablation với numeric head; không phải bỏ quantize khỏi pre-trained token predictor rồi giả định nguyên model vẫn chạy được. Mean ± SD theo seed không phải CI. Không mở rộng kết luận thành lợi/hại cho mọi thành phần K-line representation.',['ablation_summary.csv'])

add('q3-du-lieu','Q3 · Data budget và pre-trained','KẾT QUẢ',
    '<div class="two-col">'+learning_chart('kronos-small-ft','Kronos-small')+learning_chart('chronos2-ft','Chronos-2-small')+'</div>'
    + brief('Pre-trained: train tiếp từ weight có sẵn. Random init: predictor bắt đầu từ weight ngẫu nhiên. Trục ngang: session train, trục dọc: Close h=20 MAE.'),
    'Trong budget đã thử, pre-training giúp Chronos rõ hơn. Với Kronos-small, lợi ích tùy trường hợp.',
    'Nguồn: learning_curve.csv · Mean ± SD ba seed · Validation/test giữ cố định',
    'Q3 giữ Kronos-small và Chronos, không thêm mini/base theo phạm vi đã chốt. Các budget 500 / 1.000 / 1.589 session tương ứng 353 / 853 / 1.442 windows, lồng nhau và cùng ngày kết thúc. Random init nghĩa là predictor có weight ngẫu nhiên, còn tokenizer Kronos vẫn pre-trained. Random chọn learning rate trên validation từ 1e-6 / 1e-5 / 1e-4; pre-trained giữ 1e-6 nên tổng search cost khác nhau. Chronos pre-trained có MAE thấp hơn random cả chín ô budget/horizon. Với Kronos, random tốt hơn ở h=5/20 tại 1.000 và full. Full h=20: random 117,220 so với pre-trained 138,716. Không chọn lại budget theo test.',['learning_curve.csv','random_lr_selection.csv'])

add('q4-khoang-bat-dinh','Q4 · MAE có ổn định không?','KẾT QUẢ',
    brief('<strong>Seed</strong>: đổi trạng thái ngẫu nhiên của lần chạy. <strong>Horizon h</strong>: số session cần predict phía trước. Điểm dưới đây là chênh lệch MAE với Naive, seed 42.')
    + forest(),
    'Thanh ngang: CI 95%. Cắt qua 0: chênh lệch MAE với Naive chưa rõ.',
    'Nguồn: paired_intervals.csv · Close · Block 20 origins, bootstrap 2.000 lần',
    'Q4 hỏi model có giữ MAE thấp qua các seed, horizon và giai đoạn hay không. Điểm giữa là mean paired absolute-error difference so với Naive: âm tốt hơn, dương kém hơn. Thanh ngang là percentile CI 95% từ moving-block bootstrap, 2.000 lần lấy mẫu theo block 20 origins. Hình chỉ dùng seed 42; không ghép CI của ba seed thành một CI chung và không bootstrap ba seed như ba thị trường. CI cắt qua 0 chưa phân biệt rõ tốt/kém Naive, không chứng minh hai model tương đương. Chưa điều chỉnh multiple comparisons.',['paired_intervals.csv'])

regimes=[r for r in read_csv('origin_regimes.csv') if r['group']=='evaluation-main/scores/seed-42/test']
high=[r for r in regimes if r['regime']=='high']
clusters={}
for r in high: clusters.setdefault(r['high_cluster'],[]).append(r['origin_date'])
assert [(len(v),v[0],v[-1]) for v in clusters.values()]==[(6,'2026-03-11','2026-03-18'),(11,'2026-03-20','2026-04-03')]
threshold=float(regimes[0]['train_p90'])
add('q4-thoi-gian','Q4 · Volatility và threshold p90','KẾT QUẢ',
    brief('<strong>Volatility</strong> = độ dao động của 20 log-return trước origin. <strong>p90</strong> là threshold mà khoảng 90% volatility train nằm dưới. Giữ threshold này cố định khi phân nhóm test.')
    + volatility_chart()
    + table(['Nhóm test','Forecast origins','Ngày origin'],[
        ['Volatility cao · cụm 1','6','11–18/03/2026'],
        ['Volatility cao · cụm 2','11','20/03–03/04/2026'],
        ['Còn lại','306','Không vượt threshold'],
    ],[42,23,35],'extra-dense')
    + brief(f'Train p90 ≈ {num(threshold*100,3)}% log-return SD. Có 17/323 test origins vượt threshold, không bắt buộc là 10% test. Window chồng lấn nên không đếm mỗi origin như một biến cố.'),
    '',
    'Nguồn: origin_regimes.csv · Chỉ dùng return đã quan sát, không dùng giá tương lai',
    'Volatility dùng standard deviation của 20 log-return đã biết tại mỗi origin, ddof = 1. P90 train = 0,0211480870019929 log-return SD, tương đương khoảng 2,115%. Khoảng 10% giá trị volatility train vượt p90; không phải 90% giá và không bắt buộc 10% test vượt threshold. Threshold được giữ cố định khi phân nhóm test. Snapshot có các window return dao động mạnh nên vượt threshold, không gán high bằng tay. Có 6 origins từ 11–18/03/2026 và 11 origins từ 20/03–03/04/2026, ngắt ở 19/03. Cụm là các origins liên tiếp vượt threshold; chưa gắn nguyên nhân sự kiện cụ thể. Các rolling windows chồng lấn nên 17 origins không đại diện 17 biến cố độc lập, và hai cụm cũng có thể thuộc cùng một giai đoạn biến động.',['origin_regimes.csv'])

folds=read_csv('fold_scores.csv')
fold_rows=[]
for model,label in [('naive','Naive'),('kronos-mini-ft','Kronos-mini SFT'),('kronos-small-ft','Kronos-small SFT'),('kronos-base-ft','Kronos-base SFT'),('chronos2-ft','Chronos-2-small SFT')]:
    vals=[num(next(r for r in folds if r['fold']==f and r['model']==model and r['split']=='test' and r['target']=='close' and r['horizon']=='20')['mae']) for f in ('fold1','fold2')]
    fold_rows.append([label]+vals)
add('q4-folds','Q4 · Fold là gì?','KẾT QUẢ',
    brief('Fold = một lần chia train / validation / test theo thời gian. Fold sau mở rộng train.')
    + '<div class="fold-timelines"><div><b>Fold 1</b><span>Train ≤ 11/03/2022</span><span>Validation<br>14/03/2022–08/02/2023</span><span>Test<br>09/02–29/12/2023</span></div><div><b>Fold 2</b><span>Train ≤ 08/02/2023</span><span>Validation<br>09/02–29/12/2023</span><span>Test<br>02/01–28/11/2024</span></div></div>'
    + table(['Close h=20 MAE','Fold 1','Fold 2'],fold_rows,[48,26,26],'extra-dense scores',highlight=(0,))
    + brief('208 origins/fold, seed 42. Không có lợi thế nhất quán trước Naive qua hai fold và các horizon.'),
    '', 'Nguồn: fold_scores.csv · Mỗi fold chọn checkpoint trên validation riêng',
    'Fold là một lần chia train / validation / test theo thời gian. Cả hai fold bắt đầu train từ 24/08/2017; phần train của fold sau được mở rộng. Test không tham gia chọn checkpoint. Mỗi fold có 208 origins, seed 42. Bảng hiển thị Close h=20 cho dễ đọc; source CSV có h=1/5 và zero-shot. Chronos SFT nhỉnh hơn Naive ở fold 1 h=5: 22,213 so với 22,363, nhưng không giữ lợi thế ở fold 2. Cả hai fold có 0 high-volatility origins theo threshold train riêng nên không bổ sung bằng chứng cho volatility cao. Evaluation hồi cứu chưa loại trừ pre-training overlap.',['fold_scores.csv'])

add('ket-luan','Kết luận Q1–Q4','KẾT LUẬN',
    table(['Câu hỏi','Kết quả trong experiment'],[
        ['<strong>Q1</strong>','Neural model chưa có lợi thế ổn định trước Naive.'],
        ['<strong>Q2</strong>','Model lớn hơn và quantize chưa giúp đồng đều. SFT cải thiện base rõ tại h=20.'],
        ['<strong>Q3</strong>','Lợi ích pre-trained phụ thuộc model. Thêm data chưa làm mọi horizon tốt hơn.'],
        ['<strong>Q4</strong>','MAE thay đổi theo horizon và giai đoạn. Số đợt volatility cao còn ít.'],
    ],[10,90]),
    '', 'Nguồn: Bảng kết quả Q1–Q4 · Snapshot VN30, protocol đã khóa',
    'Kết luận chỉ trong snapshot, split, model và budget đã thử. Không suy lợi nhuận giao dịch từ MAE, không khẳng định train đã hội tụ hoặc dataset acceptance đã đạt. Các source links giữ khả năng truy vết. Q3 chỉ đánh giá Kronos-small và Chronos; Q2 mini/small/base khác tokenizer, nên không tách riêng được tác động số tham số. Bản kết luận không chứa lời kêu gọi xác minh dữ liệu, nhưng không thay đổi trạng thái dataset trong hồ sơ nghiên cứu.',['completion_matrix.csv'])


assert len(slides)==20

extra_css = '''
.members { text-align:center; font-size:36px; line-height:1.7; }
.title-slide .hero { gap:48px; }
.cover-team { font-family:var(--font-body); font-size:46px; padding:25px 85px; }
.content-slide .body { justify-content:center; gap:24px; }
.content-slide .body.compact-body { gap:24px; }
.content-slide .action-title { letter-spacing:-.045em; }
.lead {font-size:38px;line-height:1.55;}
.deck-table th {font-size:26px;}
.deck-table.dense td {font-size:28px;padding:13px 18px;}
.deck-table.extra-dense td {font-size:27px;padding:7px 18px;}
.scores td:not(:first-child),.scores th:not(:first-child) {font-family:var(--font-mono);text-align:right;white-space:nowrap;}
.scores .sd {font-size:23px;color:var(--text-muted);}
.two-col {display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;}
.two-col.aligned {align-items:start;gap:50px;}
.two-col.aligned h3 {font-size:31px;margin-bottom:20px;}
.two-col.aligned .brief {font-size:27px;margin-top:18px;}
.chart-cost {grid-template-columns:1.65fr 1fr;}
.data-chart {display:block;width:100%;height:auto;overflow:visible;font-family:var(--font-body);}
.flow {display:flex;width:100%;gap:30px;align-items:stretch;padding:25px 0;}
.flow-step {flex:1;min-width:0;border-top:2px solid var(--line);padding:18px 0;position:relative;}
.flow-step strong {display:block;font-size:31px;line-height:1.45;margin-bottom:10px;}
.flow-step span {display:block;font-size:25px;line-height:1.5;color:var(--text-muted);}
.flow-step:not(:last-child)::after {content:'›';position:absolute;right:-24px;top:21px;font-size:35px;color:var(--text-muted);}
.split-strip {display:flex;height:62px;gap:3px;font-family:var(--font-mono);font-size:24px;}
.split-strip>div {background:var(--text);color:var(--bg);display:flex;align-items:center;justify-content:center;}
.split-strip>div:nth-child(2) {background:#77786e;}.split-strip>div:nth-child(3) {background:#d2d0c6;color:var(--text);}
.window-strip {display:flex;gap:5px;min-height:140px;}
.window-strip>div {padding:22px 34px;display:flex;flex-direction:column;gap:12px;justify-content:center;}
.window-strip b {font-size:38px;}.window-strip span {font-size:27px;}
.small-window {min-height:100px;}
.small-window b {font-size:31px;}.small-window span {font-size:26px;}
.formula {font-family:var(--font-mono);font-size:33px;line-height:1.5;padding:22px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);}
.ablation-branches {font-size:28px;line-height:1.6;border-top:1px solid var(--line);padding-top:16px;}
.fold-timelines {display:flex;flex-direction:column;gap:10px;}
.fold-timelines>div {display:grid;grid-template-columns:100px 1fr 1.35fr 1.15fr;gap:5px;align-items:stretch;}
.fold-timelines b {font-size:25px;align-self:center;}
.fold-timelines span {font-size:24px;line-height:1.4;padding:10px 14px;background:var(--bg-alt);}
.fold-timelines span:nth-child(2) {background:var(--text);color:var(--bg);}
.fold-timelines span:last-child {border:1px dashed var(--text-muted);}
#q4-folds .body {gap:20px;}
.context {flex:3;background:var(--text);color:var(--bg);}.future {flex:2;background:var(--bg-alt);border:1px dashed var(--text-muted);}
.diagnosis {display:grid;grid-template-columns:1fr 1fr;gap:40px;border-top:1px solid var(--line);padding-top:16px;line-height:1.45;font-size:27px;}
.diagnosis span {font-family:var(--font-mono);color:var(--text-muted);font-size:25px;}
.fold-dates {display:flex;gap:50px;font-size:28px;line-height:1.5;}
.evidence-numbers {display:flex;gap:100px;padding-bottom:10px;}
.evidence-numbers>div {flex:1;display:flex;flex-direction:column;gap:16px;}
.evidence-numbers strong {font-family:var(--font-mono);font-size:108px;line-height:1.15;font-weight:500;letter-spacing:-7px;}
.evidence-numbers span {font-size:29px;color:var(--text-muted);max-width:600px;line-height:1.5;}
@media print {.data-chart {break-inside:avoid;} .reading-progress {display:none!important;} .reveal .slides section::after {display:none!important;} }
'''

template = (VENDOR/'paper-ink-template.html').read_text(encoding='utf-8')
template = template.replace('[TÊN BÀI TRÌNH BÀY]', '1nsider — Kronos-VN30-Time-series-Forecasting')
template = re.sub(r'<link\b[^>]*>\s*', '', template)
css = '\n'.join((VENDOR/f).read_text(encoding='utf-8') for f in ('reset.css','reveal.css','fonts.css'))
template = template.replace('<style>', '<style>\n'+css+'\n', 1)
template = template.replace('  </style>', extra_css+'\n  </style>', 1)
start = template.index('      <!-- BÌA:')
end = template.index('\n    </div>\n  </div>', start)
template = template[:start] + '\n'.join(slides) + template[end:]
for name, url in [('reveal.js','https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js'),('notes.js','https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/notes/notes.js')]:
    code=(VENDOR/name).read_text(encoding='utf-8').replace('</script','<\\/script')
    template=template.replace(f'<script src="{url}"></script>',f'<script>\n{code}\n</script>')
licenses='\n\n'.join((VENDOR/name).read_text(encoding='utf-8') for name in ('LICENSE','bevietnampro-OFL.txt','ibmplexmono-OFL.txt'))
head, closing, tail = template.rpartition('</body>')
template=head+'<!-- Third-party notices: reveal.js 5.1.0 MIT; Be Vietnam Pro / IBM Plex Mono SIL OFL.\n'+licenses.replace('--','—')+'\n-->\n'+closing+tail
OUT.write_text(template,encoding='utf-8')
receipt = {
    'slides':len(slides),'format':'offline_html','template':'Paper & Ink','template_zip_sha256':'96e060255dddadaaf8c564757964d16dd123895a3fd3264bc4530b396e1a7264',
    'data_revision':REV,'evidence_scope':'exploratory_only','dataset_accepted':False,
    'output_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'authoring_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),HERE/'slide-outline.md')},
    'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)},
    'vendor_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(VENDOR.iterdir()) if p.is_file()},
}
(HERE/'build_manifest.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Built {len(slides)} slides: {OUT} ({OUT.stat().st_size:,} bytes)')

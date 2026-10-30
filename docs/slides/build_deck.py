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
    for j, (init, label, color, dash) in enumerate((("pretrained", "Đã pretrain", "#151610", ""), ("random", "Khởi tạo ngẫu nhiên", "#83847a", "9 6"))):
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
    parts = [svg_start(1698, 170, "Biến động 20 phiên đã quan sát tại 323 mốc test")]
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
        parts += [line(x(a), 146, x(b), 146, "#c8c7bd", 2),svg_text((x(a)+x(b))/2, 168, f"Đoạn {n} · {len(indices)} mốc", 23, "middle")]
    parts += [svg_text(20, 20, "Vùng tô: 17 mốc biến động cao trong 2 cụm", 24),svg_text(1680, 20, "Nét đứt: ngưỡng p90 từ train", 24, "end")]
    return ''.join(parts) + '</svg>'


slides = []


def add(identifier, title, section, body, takeaway, source, notes, files=()):
    idx = len(slides) + 1
    full_files = ["docs/VN30_PC_Research_Report.md"] + ["artifacts/local/pc-exploratory-20261030/final-report/" + f for f in files]
    links = ''.join(f'<li><a href="{GITHUB + esc(f)}">{esc(f)}</a></li>' for f in full_files)
    for f in full_files:
        assert (ROOT / f).is_file(), f
        inputs.add(ROOT / f)
    notes_html = f'<p>{notes}</p><p>Phạm vi: kết quả thăm dò trên snapshot VNDIRECT, dataset chưa được chấp nhận cho nghiên cứu chính.</p><ul>{links}</ul>'
    html_body = body + (statement(takeaway) if takeaway else '')
    slides.append(f'''<section id="{identifier}" aria-label="{esc(title)}">
<div class="frame content-slide">
<p class="eyebrow">VN30 / {esc(section)}</p>
<div class="heading"><span class="section-number" data-section></span><h2 class="action-title">{title}</h2></div>
<div class="body compact-body">{html_body}</div>
<footer class="chrome-foot"><p class="source">{source}</p><span data-page></span></footer><div class="bottom-rule" aria-hidden="true"></div>
</div><aside class="notes">{notes_html}</aside></section>''')


# 01. User-supplied names and project identity take precedence over the outline default.
slides.append('''<section id="mo-dau" aria-label="Kronos-VN30-Time-series-Forecasting"><div class="frame title-slide">
<p class="eyebrow">1NSIDER</p><div class="heading"><span class="section-number" data-section></span>
<h1 class="title">Kronos-VN30-<br>Time-series-Forecasting</h1></div>
<div class="body hero"><div class="statement cover-team">Nhóm <strong>1nsider</strong></div>
<div class="members"><p>Vi Nguyễn Ngọc Châu</p><p>Nguyễn Hoàng Kiên</p></div></div>
<footer class="chrome-foot"><span data-page></span></footer><div class="bottom-rule" aria-hidden="true"></div></div>
<aside class="notes"><p>Nhóm 1nsider. Thành viên: Vi Nguyễn Ngọc Châu, Nguyễn Hoàng Kiên. Tên project theo góp ý của nhóm. Đề tài đánh giá Kronos mini/small/base, Chronos và baseline trên VN30. Giải thích phạm vi thăm dò ở phần mở đầu nội dung.</p></aside></section>''')

add('cau-hoi', 'Bốn câu hỏi nghiên cứu', 'MỤC TIÊU',
    table(['Câu hỏi', 'Điều cần kiểm tra', 'Bằng chứng'], [
        ['<strong>Q1</strong>', 'Model học sâu có tốt hơn cách dự báo đơn giản?', 'Naive, Ridge, ARIMA, ETS'],
        ['<strong>Q2</strong>', 'Model lớn và mã hóa rời rạc có giúp ích?', 'Ba Kronos và đối chứng lượng tử hóa'],
        ['<strong>Q3</strong>', 'Dữ liệu và kiến thức học sẵn đóng góp thế nào?', '500 / 1.000 / toàn bộ phiên train'],
        ['<strong>Q4</strong>', 'Kết quả giữ được qua các lần chạy và thời kỳ?', 'Seed, horizon, biến động và hai fold'],
    ], [10, 53, 37]),
    'Đánh giá trên bản dữ liệu cố định, trong phạm vi <strong>thăm dò</strong>.',
    'Nguồn: Báo cáo PC, mục 3–7 · Ma trận nghiệm thu',
    'Baseline là phương pháp làm mốc so sánh. Horizon là số phiên phía trước. Seed điều khiển tính ngẫu nhiên của một lần chạy. Chưa có đủ bằng chứng chấp nhận nhãn OHLC cho kết luận nghiên cứu chính.', ['completion_matrix.csv'])

add('cach-kronos-du-bao', 'Cách Kronos dự báo chuỗi giá', 'PHƯƠNG PHÁP',
    flow([('Chuỗi giá', '128 phiên OHLC'), ('Mã hóa', 'Đặc trưng của nến'), ('Rời rạc hóa', 'Chuyển thành token'), ('Dự báo', 'Sinh token tiếp theo'), ('Giải mã', '20 phiên giá')])
    + table(['Chế độ', 'Cách sử dụng model'], [
        ['<strong>Zero-shot</strong>', 'Dùng trọng số đã học sẵn, chưa huấn luyện thêm với VN30.'],
        ['<strong>SFT</strong>', 'Huấn luyện bổ sung phần dự báo trên VN30, giữ bộ mã hóa cố định.'],
    ], [23,77]) + brief('OHLC: giá mở cửa, cao nhất, thấp nhất và đóng cửa. Volume/amount thiếu nên được điền 0.'),
    '', 'Nguồn: Báo cáo PC, mục 2 và 5 · Mã Kronos đã pin',
    'Tokenizer gồm encoder, lượng tử hóa và decoder. Predictor dự báo các token. Sơ đồ lược bỏ bước chuẩn hóa/khôi phục thang giá để dễ theo dõi. Volume/amount bằng 0 chỉ là cách adapter xử lý thiếu dữ liệu, không phải khối lượng giao dịch thực.')

resources = read_csv('resources.csv')
add('cac-model', 'Bốn model được đánh giá', 'PHƯƠNG PHÁP',
    table(['Model', 'Tham số', 'Bộ mã hóa / vai trò'], [
        ['Kronos-mini', '4,1 triệu', 'Tokenizer-2k'], ['Kronos-small', '24,7 triệu', 'Tokenizer-base'],
        ['Kronos-base', '102,3 triệu', 'Tokenizer-base'], ['Chronos-2-small', '27,9 triệu', 'Đối chứng chuỗi thời gian tổng quát'],
    ], [31,22,47]) + brief('Cả bốn chạy zero-shot và SFT. Checkpoint và điểm số đều từ lượt chạy mới trên PC.'),
    'Mini khác tokenizer, nên so kích thước chưa tách riêng tác động của số tham số.',
    'Nguồn: Provenance model/tokenizer · resources.csv',
    'Chronos-2-small đã xuất hiện trong báo cáo VN30 cũ, vẫn giữ như đối chứng. Trọng tâm là ba Kronos. Không lấy checkpoint môi trường cũ để bổ sung kết quả PC.', ['resources.csv'])

add('du-lieu', 'Dữ liệu VN30 và cách chia tập', 'DỮ LIỆU',
    '<p class="lead"><strong>2.271 phiên</strong> · VNDIRECT · 24/08/2017–01/10/2026</p>'
    + '<div class="split-strip"><div style="flex:70">Train 70%</div><div style="flex:15">Validation 15%</div><div style="flex:15">Test 15%</div></div>'
    + table(['Tập', 'Khoảng thời gian', 'Số phiên', 'Mốc dự báo'], [
        ['Train', '24/08/2017–29/12/2023', '1.589', '1.442'], ['Validation', '02/01/2024–20/05/2025', '340', '321'], ['Test', '21/05/2025–01/10/2026', '342', '323'],
    ], [18,44,16,22], 'dense') + brief('Mốc dự báo là thời điểm sau khi có giá đóng cửa của phiên t. Đơn vị giá: điểm chỉ số.'),
    '', 'Nguồn: Báo cáo PC, mục 1–2 · Ranh giới split đã khóa',
    'Toàn bộ nhãn 20 phiên phải nằm trong split. Context có thể dùng quá khứ trước biên. Request bắt đầu năm 2012 nhưng nguồn chỉ trả từ 2017. Một hàng 01/10/2026 ngoài request được giữ trong snapshot để đối chiếu; không gọi là dữ liệu đã thu thập đủ theo request.')

add('kiem-tra-du-lieu', 'Kiểm tra dữ liệu trước thực nghiệm', 'DỮ LIỆU',
    table(['Phần đã kiểm tra', 'Kết quả và phạm vi'], [
        ['Khôi phục và tính toàn vẹn', 'Raw replay, thời gian và SQLite đã qua kiểm tra.'],
        ['Đối chiếu VPS / DNSE', '1.230 phép so sánh OHLC khác trên 0,02 điểm, gồm 60 ngày Close khác nguồn.'],
        ['Đặc điểm giá mở cửa', '78 phiên Open bằng Close trước, có một đoạn 71 phiên liên tiếp.'],
    ], [35,65]) + brief('Giữ nguyên giá gốc, lưu bằng chứng theo ngày và trường. Cách dựng nến của nguồn và lịch sàn còn cần đối chiếu.'),
    'Dữ liệu thị trường <strong>chưa được xác minh đầy đủ</strong>. Kết quả giữ phạm vi thăm dò.',
    'Nguồn: Audit snapshot · data_adjudication.csv',
    'Diễn đạt trung tính theo góp ý, nhưng không thay trạng thái unverified bằng tuyên bố đã xử lý xong. 1.230 là số phép so sánh khác nguồn, không phải 1.230 lỗi đã chứng minh của VNDIRECT. Đoạn Open bằng Close trước: 05/05–11/08/2025. KRX trùng mốc bắt đầu chỉ là giả thuyết điều tra.', ['data_adjudication.csv'])

add('quy-trinh', 'Quy trình dự báo chung', 'THIẾT KẾ',
    '<div class="window-strip"><div class="context"><b>128 phiên đã biết</b><span>Thông tin đưa vào model</span></div><div class="future"><b>20 phiên cần dự báo</b><span>Chấm tại phiên 1, 5 và 20</span></div></div>'
    + table(['Nguyên tắc', 'Cách thực hiện'], [
        ['Cùng điều kiện', 'Các model dùng chung mốc dự báo, split và ba seed 42 / 43 / 44.'],
        ['Không học từ test', 'Chọn cấu hình bằng validation. Lưu dự báo rồi mới ghép giá thật để chấm.'],
        ['Sai số', 'MAE: trung bình độ lệch tuyệt đối. RMSE bổ sung góc nhìn về lỗi lớn.'],
    ], [27,73], 'dense') + brief('Kronos: trung bình 3 chuỗi sinh ra. Chronos: trung bình 13 mức quantile, không phải 13 mẫu ngẫu nhiên.'),
    '', 'Nguồn: Báo cáo PC, mục 2 · Protocol đánh giá đã khóa',
    'Tất cả 20 nhãn nằm trong split đích. T=1, top-p=0,9, FP32. Context không chứa giá tương lai; ngày phiên đích là ngày lịch sử đã biết. Đây là đánh giá hồi cứu. MAE/RMSE có đơn vị điểm chỉ số. Chưa chứng minh loại bỏ dữ liệu trùng trong quá trình pretraining.')

read_csv('checkpoint_selection.csv')
add('chon-checkpoint', 'Huấn luyện thêm và chọn checkpoint', 'SFT',
    brief('Tối đa 5 vòng học (epoch), FP32, AdamW, learning rate 1e-6, effective batch 16.')
    + table(['Model', 'Tốt nhất sau SFT', 'Được chọn, có xét bản gốc'], [
        ['Kronos-mini', 'Epoch 5', '<strong>Epoch 5</strong>'], ['Kronos-small', 'Epoch 5', '<strong>Epoch 5</strong>'], ['Kronos-base', 'Epoch 5', '<strong>Epoch 5</strong>'], ['Chronos-2-small', 'Epoch 1', '<strong>Epoch 0 · bản gốc</strong>'],
    ], [31,28,41], 'dense'),
    'Với Chronos, huấn luyện thêm chưa cải thiện tiêu chí validation ở cả ba seed.',
    'Nguồn: checkpoint_selection.csv · selected_scores.csv',
    'Checkpoint là bản lưu trọng số model. Epoch 0 là trước cập nhật. Best-trained chọn trong các epoch đã cập nhật; selected được chọn cả epoch 0. Bảng điểm mang SFT phía sau sử dụng best-trained để đo tác động cập nhật. Ba Kronos giữ tokenizer cố định, clipping 1,0, weight decay 0,01. Không so native loss khác hệ giữa các model.', ['checkpoint_selection.csv','selected_scores.csv'])

read_csv('baseline_selection.csv')
add('baseline', 'Các cách dự báo làm mốc so sánh', 'BASELINE',
    table(['Phương pháp', 'Ý tưởng', 'Cấu hình chọn từ validation'], [
        ['<strong>Naive</strong>', 'Giữ Close gần nhất cho mọi phiên đích.', 'Không có tham số cần chọn'],
        ['Ridge', 'Học quan hệ tuyến tính có regularization.', 'Alpha = 10, từ 4 ứng viên'],
        ['ARIMA', 'Mô hình thống kê theo diễn biến quá khứ.', '(0,1,0), từ 18 ứng viên'],
        ['ETS', 'San bằng theo mức / xu hướng.', 'Chỉ mức, từ 3 ứng viên'],
    ], [18,44,38], 'dense') + brief('ARIMA/ETS fit lại trên 128 phiên tại mỗi mốc. Lỗi hội tụ và thiếu mốc được ghi, không thay ngầm bằng Naive.'),
    'Close của ARIMA/ETS được chọn trùng Naive, nên không phải ba bằng chứng độc lập.',
    'Nguồn: baseline_selection.csv · Báo cáo PC, mục 3',
    'Tiêu chí chọn là trung bình MAE Open/Close tại ba horizon, chuẩn hóa bằng SD train. ARIMA có 12/18 cấu hình đủ coverage, 491 failed-origin fits trong lưới, không phải 491 origin test bị loại. Ridge scaler chỉ fit train.', ['baseline_selection.csv'])

add('q1-close', 'Q1 · Sai số giá đóng cửa', 'KẾT QUẢ',
    brief('MAE, đơn vị điểm chỉ số. <strong>Thấp hơn là tốt hơn.</strong> Giá trị ± là độ lệch chuẩn giữa ba seed.') + score_table('close',True),
    'Trong bảng chính, cả bốn neural model chưa vượt Naive ở trung bình ba seed.',
    'Nguồn: main_summary.csv · Test 323 mốc · ARIMA/ETS Close trùng Naive',
    'Bảng hiển thị best-trained SFT, không phải mọi checkpoint selected. Chronos selected giữ bản gốc. Seed SD không phải khoảng tin cậy theo thị trường. Bảng nguồn có đủ zero-shot, validation và RMSE.', ['main_summary.csv'])

add('q1-open', 'Q1 · Sai số giá mở cửa', 'KẾT QUẢ',
    score_table('open') + '<div class="diagnosis"><p><strong>59 mốc</strong> có nhãn trong đoạn Open bất thường<br><span>Naive MAE = 0,000</span></p><p><strong>264 mốc còn lại</strong><br><span>Naive MAE = 7,291</span></p></div>',
    'Open MAE thấp cần đọc cùng đặc điểm nhãn, chưa xác nhận dự báo giá mở cửa chính thức.',
    'Nguồn: main_summary.csv · Chẩn đoán Open trong báo cáo PC',
    'MAE bảng là trung bình ba seed, ± là SD. 59 mốc là số origin h=1 có nhãn trong đoạn bất thường, không phải toàn bộ 78 trường hợp trên cả dữ liệu. Chẩn đoán không được dùng để chọn lại model trên test. Không kết luận mọi Open bằng Close trước là sai.', ['main_summary.csv'])

zero = [float(main_score('kronos-'+v,'close',20)['mae']) for v in ('mini','small','base')]
ft = [float(main_score('kronos-'+v+'-ft','close',20)['mae']) for v in ('mini','small','base')]
costs = [next(r for r in resources if r['model']=='kronos-'+v) for v in ('mini','small','base')]
chart12 = grouped_bars(['Mini','Small','Base'], [('Zero-shot',zero,None,'#aaa99f'),('SFT',ft,None,'#151610')], 200, width=1000, reference=float(main_score('naive','close',20)['mae']))
add('q2-kich-thuoc', 'Q2 · Kích thước và tác động SFT', 'KẾT QUẢ',
    '<div class="two-col chart-cost"><div>'+chart12+'</div><div>' + table(['Model','SFT (giây)','GiB¹'],[[r['model'].replace('kronos-','').title(),num(r['train_seconds_mean'],1),num(r['peak_allocated_GiB'])] for r in costs],[30,38,32],'dense') + brief('¹ Bộ nhớ tensor đỉnh khi huấn luyện, không phải tổng VRAM.') + '</div></div>' + brief('Mini SFT tốt hơn small SFT ở cả ba horizon. Base SFT tốt hơn mini tại h=20, chưa tốt hơn tại h=1/5.'),
    f'Base: MAE Close sau 20 phiên giảm <strong>{num(zero[2]-ft[2])} điểm</strong>, vẫn cao hơn Naive.',
    'Nguồn: main_summary.csv / resources.csv · RTX 4070 SUPER',
    'Dựng lại đồ thị từ CSV cùng nguồn của báo cáo PC theo góp ý có thể dùng ảnh báo cáo. Biểu đồ/vector giữ chỉnh sửa được và khớp màu mẫu. SFT seconds là trung bình tổng lượt train, không phải thời gian inference. Mini khác tokenizer nên không suy tác động nhân quả riêng của số tham số.', ['main_summary.csv','resources.csv'])

ablation = read_csv('ablation_summary.csv')
values=[]
for model,label,color in [('representation-continuous','Liên tục','#aaa99f'),('representation-quantized','Lượng tử hóa','#151610')]:
    rows=[next(r for r in ablation if r['model']==model and r['split']=='test' and r['target']=='close' and int(r['horizon'])==h) for h in (1,5,20)]
    values.append((label,[float(r['mae']) for r in rows],[float(r['mae_sd']) for r in rows],color))
add('q2-luong-tu-hoa', 'Q2 · Kiểm tra riêng bước lượng tử hóa', 'KẾT QUẢ',
    brief('Giữ cùng bộ mã hóa, model dự báo khởi tạo ngẫu nhiên, dữ liệu và ngân sách. Chỉ thay biểu diễn liên tục bằng mã rời rạc.')
    + grouped_bars(['Sau 1 phiên','Sau 5 phiên','Sau 20 phiên'],values,200,width=1698,height=390),
    'Trong đối chứng này, lượng tử hóa chưa làm sai số Close giảm đồng nhất.',
    'Nguồn: ablation_summary.csv · Mean ± SD ba seed · MAE Close',
    'Ablation nghĩa là thay riêng một thành phần trong điều kiện giữ các phần khác giống nhau. Continuous là vector L2-normalized trước BSQ; quantized là sau BSQ. Cùng random backbone small và numeric head/MSE. Không kết luận cho toàn bộ K-line representation. Mean chênh lệch nhỏ không tự chứng minh ý nghĩa thống kê.', ['ablation_summary.csv'])

add('q3-du-lieu', 'Q3 · Dữ liệu và kiến thức học sẵn', 'KẾT QUẢ',
    '<div class="two-col">'+learning_chart('kronos-small-ft','Kronos-small')+learning_chart('chronos2-ft','Chronos-2-small')+'</div>'
    + brief('Trục ngang: 500 / 1.000 / 1.589 phiên train, tương ứng 353 / 853 / 1.442 cửa sổ. Trục dọc: MAE Close sau 20 phiên, mean ± SD ba seed.'),
    'Trong ngân sách đã thử, pretraining giúp Chronos rõ hơn. Với Kronos-small, lợi ích tùy trường hợp.',
    'Nguồn: learning_curve.csv / random_lr_selection.csv · Validation/test cố định',
    'Pretraining là học từ dữ liệu trước khi đến bài VN30. Random là predictor cùng kiến trúc khởi tạo ngẫu nhiên; tokenizer Kronos vẫn pretrained. Chronos pretrained thấp MAE hơn random cả chín ô budget/horizon. Kronos random thấp hơn pretrained tại h=5/20 ở 1.000 và full; full h=20:117,220 so với138,716. Random chọn LR trong1e-6/1e-5/1e-4, pretrained giữ1e-6, nên tổng chi phí tìm cấu hình khác nhau.', ['learning_curve.csv','random_lr_selection.csv'])

add('q4-khoang-bat-dinh', 'Q4 · Khoảng bất định của chênh lệch', 'KẾT QUẢ',
    brief('Điểm giữa: chênh lệch MAE với Naive. Thanh ngang: khoảng tin cậy 95%. Chênh lệch âm nghĩa là tốt hơn Naive.') + forest(),
    'Khoảng cắt qua 0 cho thấy chưa phân biệt rõ hơn hay kém Naive trong phép kiểm này.',
    'Nguồn: paired_intervals.csv · Close, seed 42 · Block 20 mốc, 2.000 lần lấy mẫu',
    'Paired moving-block bootstrap lấy lại mẫu theo khối20 origin, cùng origin giữa hai forecast. Đây là CI seed42, không ghép CI từ ba seed. Khoảng percentile95%, chưa điều chỉnh nhiều phép so sánh. Base h20 CI[-18,439;26,387], small[13,737;85,757]. Các mốc chồng lấn không độc lập.', ['paired_intervals.csv'])

regimes=read_csv('regime_period_summary.csv')
rows16=[]
for model,label in [('kronos-mini-ft','Kronos-mini SFT'),('kronos-small-ft','Kronos-small SFT'),('kronos-base-ft','Kronos-base SFT'),('chronos2-ft','Chronos-2-small SFT')]:
    diffs=[]
    for period in ('period-1','period-2','period-3'):
        get=lambda m:float(next(r for r in regimes if r['model']==m and r['target']=='close' and r['horizon']=='20' and r['grouping']=='period' and r['label']==period)['mae'])
        delta=get(model)-get('naive')
        diffs.append(('+' if delta>0 else '')+num(delta))
    rows16.append([label]+diffs)
add('q4-thoi-gian', 'Q4 · Kết quả theo thời gian', 'KẾT QUẢ',
    volatility_chart() + table(['Chênh lệch MAE với Naive','Đoạn 1','Đoạn 2','Đoạn 3'],rows16,[37,21,21,21],'extra-dense scores')
    + brief('Close sau 20 phiên, trung bình ba seed. Số âm là tốt hơn Naive. Có 306 mốc biến động thường và 17 mốc biến động cao.'),
    '', 'Nguồn: origin_regimes.csv / regime_period_summary.csv',
    'Ngưỡng p90 chỉ lấy từ train. Biến động là SD20 log-return đã quan sát tại origin, ddof1. Hai cụm cao không đại diện nhiều biến cố thị trường độc lập. Bảng chênh lệch lấy mean MAE của nhóm trừ mean Naive cùng nhóm, không tạo một kiểm định mới.', ['origin_regimes.csv','regime_period_summary.csv'])

folds=read_csv('fold_scores.csv')
rows17=[]
for model,label in [('naive','Naive'),('kronos-mini-ft','Kronos-mini SFT'),('kronos-small-ft','Kronos-small SFT'),('kronos-base-ft','Kronos-base SFT'),('chronos2-ft','Chronos-2-small SFT')]:
    vals=[num(next(r for r in folds if r['fold']==f and r['model']==model and r['split']=='test' and r['target']=='close' and r['horizon']=='20')['mae']) for f in ('fold1','fold2')]
    rows17.append([label]+vals)
add('q4-folds', 'Q4 · Hai giai đoạn kiểm tra bổ sung', 'KẾT QUẢ',
    '<div class="fold-dates"><p><strong>Fold 1</strong> · Test 09/02–29/12/2023</p><p><strong>Fold 2</strong> · Test 02/01–28/11/2024</p></div>'
    + table(['MAE Close sau 20 phiên','Fold 1','Fold 2'],rows17,[48,26,26],'dense scores',highlight=(0,))
    + brief('208 mốc/fold, seed 42. Chọn model bằng dữ liệu trước test. Hai fold không có mốc biến động cao.'),
    'Chưa có lợi thế nhất quán trước Naive qua các horizon và hai fold.',
    'Nguồn: fold_scores.csv · Expanding-window evaluation',
    'Expanding-window là mở rộng dữ liệu quá khứ để kiểm tra ở một đoạn thời gian tiếp theo. Hình chính giữ h20 để đọc rõ; CSV có h1/h5 và zero-shot. Chronos SFT fold1 h5=22,213 so với Naive22,363, không giữ lợi thế fold2. Folds hồi cứu không chứng minh sạch pretraining. Bảng dùng best-trained.', ['fold_scores.csv'])

add('kiem-dinh', 'Kiểm định và khả năng tái lập', 'BẰNG CHỨNG',
    '<div class="evidence-numbers"><div><strong>2.160</strong><span>dòng sai số tính lại từ dự báo và nhãn</span></div><div><strong>378</strong><span>khoảng bootstrap kiểm tra độc lập</span></div></div>'
    + flow([('Dữ liệu', 'Hash / nguồn'),('Checkpoint','Trọng số / cấu hình'),('Dự báo','182 file CSV'),('Sai số','88 nhóm chấm'),('Báo cáo','Bảng / hình')])
    + brief('Kiểm thêm 1.782 metric theo nhóm và giai đoạn. Giữ revision, lựa chọn checkpoint và hướng dẫn chạy lại.'),
    'Kiểm đúng phép tính giúp tái lập kết quả, nhưng không thay cho xác minh giá thị trường.',
    'Nguồn: Numerical validation / final verification / completion matrix',
    '85 output receipts và90 cặp training/selection được kiểm hash, không phải90 mẫu nghiên cứu độc lập. Software suite64 tests, skipped1. Native GPU interrupted/resume mới kiểm mini, không mở rộng cho mọi variant hoặc forced-OOM. Forecast được lưu trước khi ghép nhãn.', ['verification.json','completion_matrix.csv'])

add('gioi-han', 'Giới hạn và việc còn cần làm', 'THẢO LUẬN',
    table(['Giới hạn','Ảnh hưởng','Việc cần làm'],[
        ['Giá OHLC và lịch sàn','Kết luận chỉ theo snapshot đang dùng.','Bổ sung nguồn và phân xử từng sai khác.'],
        ['Đánh giá hồi cứu','Chưa loại trừ việc model từng thấy dữ liệu.','Xác minh cutoff và kiểm thêm giai đoạn mới.'],
        ['Ngân sách / số giai đoạn','Năm epoch và ít cụm biến động cao.','Đối chứng thêm khi có dữ liệu đủ căn cứ.'],
        ['Chưa backtest giao dịch','Sai số giá chưa cho biết lợi nhuận.','Đánh giá riêng phí và quy tắc giao dịch.'],
    ],[26,36,38],'dense'),
    'Nếu sửa dữ liệu, cần phiên bản mới và kiểm lại các thí nghiệm phụ thuộc.',
    'Nguồn: Báo cáo PC, mục 9 · completion_matrix.csv',
    'Không hứa đã có dữ liệu hiệu chỉnh hoặc chạy đến hội tụ. Chưa có Directional Accuracy/backtest/transaction costs trong phạm vi đã chốt. Không đổi nhãn checkpoint gốc thành model của phiên bản dữ liệu mới.', ['completion_matrix.csv'])

add('ket-luan', 'Kết luận Q1–Q4', 'KẾT LUẬN',
    table(['Câu hỏi','Kết quả trong thiết lập đã thử'],[
        ['<strong>Q1</strong>','Neural model chưa vượt Naive một cách ổn định.'],
        ['<strong>Q2</strong>','Kích thước và lượng tử hóa chưa có lợi ích đồng nhất. SFT giúp base rõ ở h=20.'],
        ['<strong>Q3</strong>','Lợi ích học sẵn phụ thuộc model. Thêm dữ liệu chưa giúp mọi horizon.'],
        ['<strong>Q4</strong>','Kết quả thay đổi theo giai đoạn. Bằng chứng về biến động cao còn ít.'],
    ],[10,90]),
    'Ưu tiên tiếp theo: <strong>xác minh dữ liệu</strong> trước khi chốt nghiên cứu chính.',
    'Nguồn: Báo cáo PC · Kết quả thăm dò, chưa chấp nhận dữ liệu nghiên cứu chính',
    'Các khoảng trống thí nghiệm đã có kết quả PC thăm dò và được kiểm định số học. Giữ giới hạn snapshot, hồi cứu, tokenizer khác nhau và ngân sách thử nghiệm. Đây cũng là trang trao đổi cuối, không có slide21.', ['completion_matrix.csv'])

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

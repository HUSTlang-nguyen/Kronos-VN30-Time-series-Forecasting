"""Produce LaTeX tables and vector figures from the locked experiment CSVs."""
from pathlib import Path
import csv
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "artifacts/local/pc-exploratory-20261030/final-report"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": .18,
    "grid.linewidth": .5, "savefig.bbox": "tight",
})
for folder in ("tables", "figures"):
    (HERE / folder).mkdir(parents=True, exist_ok=True)
inputs = {}


def rows(name):
    path = DATA / name
    inputs[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def number(value, digits=3):
    return f"{float(value):,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def textext(text):
    return str(text).replace("_", r"\_").replace("%", r"\%")


def table(name, headers, data, spec=None):
    spec = spec or ("l" + "r" * (len(headers) - 1))
    result = [r"\begin{tabular}{" + "@{}" + spec + "@{}}", r"\toprule"]
    result += [" & ".join(headers) + r" \\", r"\midrule"]
    for row in data:
        result.append(r"\midrule" if row is None else " & ".join(map(str, row)) + r" \\")
    result += [r"\bottomrule", r"\end{tabular}", ""]
    (HERE / "tables" / name).write_text("\n".join(result), encoding="utf-8", newline="\n")


def save_figure(name, figure):
    figure.savefig(HERE / "figures" / name, metadata={"Creator": "Matplotlib", "Author": "1nsider"})
    plt.close(figure)


main = rows("main_summary.csv")
selection = rows("checkpoint_selection.csv")
resource = rows("resources.csv")
ablation = rows("ablation_summary.csv")
learning = rows("learning_curve.csv")
intervals = rows("paired_intervals.csv")
folds = rows("fold_scores.csv")
regimes = rows("regime_period_summary.csv")
origins = rows("origin_regimes.csv")
baselines = rows("baseline_selection.csv")
verification = json.loads((DATA / "verification.json").read_text(encoding="utf-8"))
assert verification["status"] == "pass"
assert verification["dataset_accepted"] is False

models = [
    ("naive", "Naive"), ("ridge", "Ridge"), ("arima", "ARIMA"), ("ets", "ETS"),
    ("kronos-mini", "Kronos-mini"), ("kronos-mini-ft", "Kronos-mini SFT"),
    ("kronos-small", "Kronos-small"), ("kronos-small-ft", "Kronos-small SFT"),
    ("kronos-base", "Kronos-base"), ("kronos-base-ft", "Kronos-base SFT"),
    ("chronos2", "Chronos-2-small"), ("chronos2-ft", "Chronos-2-small SFT"),
]
neural = [
    ("kronos-mini-ft", "Mini SFT"), ("kronos-small-ft", "Small SFT"),
    ("kronos-base-ft", "Base SFT"), ("chronos2-ft", "Chronos SFT"),
]
colors = ["#7c858b", "#b46f4d", "#235c7a", "#668168"]


def metric(model, target, h, column="mae"):
    return float(next(r for r in main if r["model"] == model and r["split"] == "test" and
                      r["target"] == target and int(r["horizon"]) == h)[column])


for target in ("close", "open"):
    output = []
    for i, (model, label) in enumerate(models):
        if i == 4:
            output.append(None)
        values = []
        for h in (1, 5, 20):
            val, sd = metric(model, target, h), metric(model, target, h, "mae_sd")
            value = number(val) + (r" $\pm$ " + number(sd) if sd else "")
            if model == "naive":
                value = r"\textbf{" + value + "}"
            values.append(value)
        output.append([label] + values)
    table(f"{target}_mae.tex", ["Model", "$h=1$", "$h=5$", "$h=20$"], output)

table("splits.tex", ["Split", "Từ ngày", "Đến ngày", "Session", "Origins"], [
    ["Train", "24/08/2017", "29/12/2023", "1.589", "1.442"],
    ["Validation", "02/01/2024", "20/05/2025", "340", "321"],
    ["Test", "21/05/2025", "01/10/2026", "342", "323"],
])

epoch_rows = []
for model, label in [("kronos-mini", "Kronos-mini"), ("kronos-small", "Kronos-small"),
                     ("kronos-base", "Kronos-base"), ("chronos2", "Chronos-2-small")]:
    records = [r for r in selection if r["model"] == model]
    assert len(records) == 3
    best = sorted({int(r["best_trained_epoch"]) for r in records})
    selected = sorted({int(r["selected_epoch"]) for r in records})
    epoch_rows.append([label, "/".join(map(str, best)), "/".join(map(str, selected)), "42/43/44"])
table("epochs.tex", ["Model", "Best-trained epoch", "Selected epoch", "Seed"], epoch_rows)

res_rows = []
for model, label in [("kronos-mini", "Kronos-mini"), ("kronos-small", "Kronos-small"),
                     ("kronos-base", "Kronos-base"), ("chronos2", "Chronos-2-small")]:
    r = next(r for r in resource if r["model"] == model)
    res_rows.append([label, number(float(r["parameters"])/1e6, 1),
                     number(r["train_seconds_mean"], 1), number(r["peak_allocated_GiB"])])
table("resources.tex", ["Model", "Tham số (M)", "SFT 5 epoch/seed (s)", "Peak tensor (GiB)"], res_rows)

learning_rows = []
for model, label in [("kronos-small-ft", "Kronos-small"), ("chronos2-ft", "Chronos-2-small")]:
    for initialization, title in [("pretrained", "Pre-trained"), ("random", "Random")]:
        for budget in (500, 1000, 1589):
            records = [next(r for r in learning if r["model"] == model and r["initialization"] == initialization
                           and int(r["train_rows"]) == budget and r["split"] == "test"
                           and r["target"] == "close" and int(r["horizon"]) == h) for h in (1, 5, 20)]
            learning_rows.append([label, title, number(budget, 0)] + [number(r["mae"]) for r in records])
    if model == "kronos-small-ft":
        learning_rows.append(None)
table("learning.tex", ["Model", "Init.", "Session", "$h=1$", "$h=5$", "$h=20$"], learning_rows)

ab_rows = []
for model, label in [("representation-continuous", "Continuous"), ("representation-quantized", "Quantized")]:
    records = [next(r for r in ablation if r["model"] == model and r["split"] == "test"
                   and r["target"] == "close" and int(r["horizon"]) == h) for h in (1, 5, 20)]
    ab_rows.append([label] + [number(r["mae"]) + r" $\pm$ " + number(r["mae_sd"]) for r in records])
table("ablation.tex", ["Representation", "$h=1$", "$h=5$", "$h=20$"], ab_rows)

ci_records = [r for r in intervals if r["group"] == "evaluation-main/scores/seed-42/test"
              and r["target"] == "close" and r["model"] in dict(neural)]
ci_rows = []
for model, label in neural:
    for h in (1, 5, 20):
        r = next(r for r in ci_records if r["model"] == model and int(r["horizon"]) == h)
        ci_rows.append([label, str(h), number(r["difference"]),
                        "[" + number(r["ci_low"]) + "; " + number(r["ci_high"]) + "]"])
table("intervals.tex", ["Model", "$h$", "$\\Delta$MAE", "CI 95\\%"], ci_rows)

fold_rows = []
for fold in ("fold1", "fold2"):
    for model, label in [("naive", "Naive")] + [(m,l) for m,l in models if m not in ("ridge","arima","ets","naive")]:
        vals = [number(next(r for r in folds if r["fold"] == fold and r["model"] == model and
                            r["target"] == "close" and r["split"] == "test" and int(r["horizon"]) == h)["mae"])
                for h in (1, 5, 20)]
        fold_rows.append(["1" if fold == "fold1" else "2", label] + vals)
    if fold == "fold1":
        fold_rows.append(None)
table("folds.tex", ["Fold", "Model", "$h=1$", "$h=5$", "$h=20$"], fold_rows)

regime_rows = []
for model, label in [("naive", "Naive")] + neural:
    values = []
    for group, label_value in [("period","period-1"),("period","period-2"),("period","period-3"),("regime","high")]:
        r = next(r for r in regimes if r["model"] == model and r["target"] == "close"
                 and r["horizon"] == "20" and r["grouping"] == group and r["label"] == label_value)
        values.append(number(r["mae"]))
    regime_rows.append([label] + values)
table("regimes.tex", ["Model", "Đoạn 1", "Đoạn 2", "Đoạn 3", "High-vol."], regime_rows)

# Main Close MAE, all three horizons and all best-trained neural models.
fig, axes = plt.subplots(1, 3, figsize=(10.3, 3.1))
for ax, h in zip(axes, (1, 5, 20)):
    data = [metric("naive", "close", h)] + [metric(m, "close", h) for m, _ in neural]
    errors = [0] + [metric(m, "close", h, "mae_sd") for m, _ in neural]
    ax.bar(np.arange(5), data, color=["#202c35"] + colors, yerr=errors, capsize=3, width=.68)
    ax.set_xticks(np.arange(5), ["Naive", "Mini", "Small", "Base", "Chronos"], rotation=35, ha="right")
    ax.set_title(f"h = {h}")
    ax.set_ylim(0, max(data)*1.18)
axes[0].set_ylabel("Close MAE (điểm)")
fig.tight_layout()
save_figure("main_close.pdf", fig)

# Zero-shot to SFT, retaining Naive as a reference.
fig, ax = plt.subplots(figsize=(7.4, 2.7))
x = np.arange(3)
ax.bar(x-.18, [metric("kronos-"+v, "close", 20) for v in ("mini","small","base")], .36, color="#acb3b8", label="Zero-shot")
ax.bar(x+.18, [metric("kronos-"+v+"-ft", "close", 20) for v in ("mini","small","base")], .36, color="#235c7a", label="SFT")
ax.axhline(metric("naive","close",20), color="#202c35", linestyle="--", linewidth=1.3, label="Naive")
ax.set_xticks(x, ["Kronos-mini", "Kronos-small", "Kronos-base"])
ax.set_ylabel("Close MAE, h=20 (điểm)")
ax.set_ylim(0,190)
ax.legend(ncol=3, frameon=False, loc="upper left")
fig.tight_layout()
save_figure("size_sft.pdf",fig)

fig, axes = plt.subplots(1, 2, figsize=(10.3,3.1), sharey=True)
for ax, (model, title) in zip(axes, [("kronos-small-ft","Kronos-small"),("chronos2-ft","Chronos-2-small")]):
    for initialization, color, style, label in [("pretrained","#235c7a","-","Pre-trained"),("random","#b46f4d","--","Random init")]:
        records = sorted([r for r in learning if r["model"]==model and r["initialization"]==initialization
                          and r["split"]=="test" and r["target"]=="close" and r["horizon"]=="20"],
                         key=lambda r:int(r["train_rows"]))
        ax.errorbar([int(r["train_rows"]) for r in records], [float(r["mae"]) for r in records],
                    yerr=[float(r["mae_sd"]) for r in records], color=color, linestyle=style,
                    marker="o", markersize=4, capsize=3, label=label)
    ax.set_title(title)
    ax.set_xticks([500,1000,1589])
    ax.set_xlabel("Số session train")
    ax.set_ylim(0,210)
    ax.legend(frameon=False)
axes[0].set_ylabel("Close MAE, h=20 (điểm)")
fig.tight_layout()
save_figure("learning.pdf",fig)

fig, ax = plt.subplots(figsize=(7.4,2.7))
for j,(model,label,color) in enumerate([("representation-continuous","Continuous","#acb3b8"),("representation-quantized","Quantized","#235c7a")]):
    records=[next(r for r in ablation if r["model"]==model and r["split"]=="test" and r["target"]=="close" and int(r["horizon"])==h) for h in (1,5,20)]
    ax.bar(x+(j-.5)*.36,[float(r["mae"]) for r in records],.36,yerr=[float(r["mae_sd"]) for r in records],capsize=3,color=color,label=label)
ax.set_xticks(x,["h=1","h=5","h=20"])
ax.set_ylabel("Close MAE (điểm)")
ax.set_ylim(0,195)
ax.legend(frameon=False)
fig.tight_layout()
save_figure("ablation.pdf",fig)

fig, ax=plt.subplots(figsize=(7.4,2.7))
for i,(model,label) in enumerate(neural):
    r=next(r for r in ci_records if r["model"]==model and r["horizon"]=="20")
    d,lo,hi=[float(r[k]) for k in ("difference","ci_low","ci_high")]
    ax.errorbar(d,3-i,xerr=[[d-lo],[hi-d]],fmt="o",color=colors[i],capsize=4)
ax.axvline(0,color="#202c35",linestyle="--",linewidth=1.2)
ax.set_yticks(range(4),[l for _,l in neural][::-1])
ax.set_xlabel("Chênh lệch MAE với Naive (điểm); âm là tốt hơn")
ax.set_ylim(-.6,3.6)
fig.tight_layout()
save_figure("intervals_h20.pdf",fig)

base_zero, base_ft = metric("kronos-base","close",20),metric("kronos-base-ft","close",20)
macros = {
    "BaseGain": number(base_zero-base_ft), "BaseGainPct": number((base_zero-base_ft)/base_zero*100,1),
    "BaseZero": number(base_zero), "BaseSFT":number(base_ft), "NaiveHtwenty":number(metric("naive","close",20)),
    "MiniSFT":number(metric("kronos-mini-ft","close",20)), "SmallSFT":number(metric("kronos-small-ft","close",20)),
    "ChronosSFT":number(metric("chronos2-ft","close",20)),
}
(HERE/"tables/numbers.tex").write_text("\n".join(r"\newcommand{\%s}{%s}"%(k,v) for k,v in macros.items())+"\n",encoding="utf-8",newline="\n")
source_files=[HERE/"build_assets.py",HERE/"main.tex",HERE/"references.bib"]
manifest={
    "data_sha256":verification["dataset_sha256"],"evidence_scope":verification["evidence_scope"],
    "dataset_accepted":verification["dataset_accepted"],"inputs":inputs,
    "source_files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files if p.is_file()},
    "generated":{p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                 for d in ("tables","figures") for p in sorted((HERE/d).glob("*")) if p.is_file()},
    "training_runs_added":0,
}
(HERE/"source_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
print("Generated",len(manifest["generated"]),"tables/figures from",len(inputs),"locked CSVs")

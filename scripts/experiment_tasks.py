"""Workers and evidence-only reporting for run_experiment.py."""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_protocol import atomic_json, expanding_folds, file_hash, portable_path


def deadline():
    if time.time() >= float(os.environ.get("VN30_DEADLINE_UNIX", "inf")):
        raise TimeoutError("Stage budget exhausted")


def prepare(config, out):
    from vn30_forecast import load, split_manifest, check_manifest

    audit = json.loads((out / "audit/audit.json").read_text(encoding="utf-8"))
    if audit["status"] != "accepted_provider_scope":
        raise ValueError(
            "Audit is unverified; no neural training authorized by dataset evidence"
        )
    info = {
        "dataset": config["dataset"],
        "receipt": config["receipt"],
        "audit": (out / "audit/audit.json").relative_to(ROOT).as_posix(),
        "audit_sha256": file_hash(out / "audit/audit.json"),
        "audit_status": audit["status"],
    }
    df, sha = load(portable_path(config["dataset"]), portable_path(config["receipt"]))
    manifests = [
        split_manifest(df, sha, dataset_info=info),
        *expanding_folds(df, sha, info),
    ]
    for name, m in zip(("primary", "fold1", "fold2"), manifests):
        check_manifest(df, sha, m)
        atomic_json(out / (name + ".json"), m)


def tune(config, out, model):
    import numpy as np
    from vn30_forecast import load_manifest_data, build_model, COLS, CONTEXT, HORIZON
    from statistical_baselines import candidates, selection_loss

    m = json.loads((out / "primary.json").read_text())
    df, _ = load_manifest_data(m)
    prices = df[COLS].to_numpy(dtype=float)
    scale = prices[: m["boundaries"]["train"]["row_end_exclusive"]].std(axis=0)
    if (scale <= 0).any():
        raise ValueError("Degenerate training scale")
    trials = []
    for candidate in candidates(model):
        deadline()
        predictions = []
        truths = []
        failures = []
        predictor, _, _ = build_model(model, df, m, "cpu", model_config=candidate)
        for i in m["origins"]["validation"]:
            deadline()
            try:
                predictions.append(
                    predictor(prices[i - CONTEXT + 1 : i + 1], None, 42 + i)
                )
                truths.append(prices[i + 1 : i + HORIZON + 1])
            except Exception as exc:
                failures.append(
                    {"origin_index": i, "error": type(exc).__name__ + ": " + str(exc)}
                )
        loss = (
            None
            if failures
            else selection_loss(np.stack(predictions), np.stack(truths), scale)
        )
        trials.append(
            {
                "config": candidate,
                "validation_loss": loss,
                "failures": failures,
                "expected_origins": len(m["origins"]["validation"]),
                "successful_origins": len(predictions),
            }
        )
        atomic_json(out / "tuning" / (model + "-trials.json"), trials)
    eligible = [r for r in trials if r["validation_loss"] is not None]
    if not eligible:
        raise RuntimeError("No candidate achieved full validation coverage")
    best = min(eligible, key=lambda r: r["validation_loss"])
    atomic_json(out / "tuning" / (model + ".json"), best["config"])


def tune_lr(config, out, task):
    trials = []
    for lr in config["random_learning_rates"]:
        deadline()
        target = out / "lr-trials" / task["id"] / str(lr)
        args = [
            sys.executable,
            "scripts/finetune_vn30.py",
            "--manifest",
            str(out / "primary.json"),
            "--model",
            task["model"],
            "--initialization",
            "random",
            "--seed",
            str(task["seed"]),
            "--epochs",
            str(config["epochs"]),
            "--learning-rate",
            str(lr),
            "--device",
            config["device"],
            "--output",
            str(target),
        ]
        if task["budget"] is not None:
            args.extend(["--data-budget", str(task["budget"])])
        if (target / "training.json").exists():
            pass
        else:
            if (target / "last.pt").exists():
                args.append("--resume")
            subprocess.run(args, cwd=ROOT, check=True)
        result = json.loads((target / "training.json").read_text())
        trials.append(
            {
                "learning_rate": lr,
                "validation_loss": result["best_validation_loss"],
                "checkpoint": target.relative_to(ROOT).as_posix(),
            }
        )
    best = min(trials, key=lambda t: t["validation_loss"])
    atomic_json(
        out / "tuning" / (task["id"] + ".json"),
        {**best, "trials": trials, "test_used": False},
    )


def benchmark(config, out, model):
    import torch

    target = out / "benchmarks" / model
    args = [
        sys.executable,
        "scripts/finetune_vn30.py",
        "--manifest",
        str(out / "primary.json"),
        "--model",
        model,
        "--epochs",
        "1",
        "--device",
        config["device"],
        "--output",
        str(target),
    ]
    if not (target / "training.json").exists():
        if (target / "last.pt").exists():
            args.append("--resume")
        subprocess.run(args, cwd=ROOT, check=True)
    from forecast_vn30 import forecast
    from vn30_forecast import load_manifest_data

    m = json.loads((out / "primary.json").read_text())
    df, _ = load_manifest_data(m)
    dest = out / "benchmarks" / (model + "-validation.csv")
    if not dest.exists():
        forecast(df, m, model, "validation", config["device"], 42, dest, 32)
    timing = json.loads(dest.with_suffix(".json").read_text())
    training = json.loads((target / "training.json").read_text())
    atomic_json(
        out / "benchmarks" / (model + ".json"),
        {
            "train_epoch_seconds": training["elapsed_seconds"],
            "forecast_seconds_per_origin": timing["elapsed_seconds"] / 32,
            "peak_cuda_allocated_bytes": training["peak_cuda_allocated_bytes"],
            "gpu": torch.cuda.get_device_name(0),
            "origins": 32,
            "dataset_sha256": m["sha256"],
        },
    )


def estimate(config, out):
    benchmarks = {
        model: json.loads((out / "benchmarks" / (model + ".json")).read_text())
        for model in config["models"]
    }
    from run_experiment import matrix

    tasks = matrix(config)
    seconds = 0
    m = json.loads((out / "primary.json").read_text())
    for task in tasks:
        if task["kind"] == "train":
            seconds += (
                benchmarks[task["model"]]["train_epoch_seconds"] * config["epochs"]
            )
        elif (
            task["kind"] == "forecast"
            and task["model"].removesuffix("-ft") in benchmarks
        ):
            seconds += (
                benchmarks[task["model"].removesuffix("-ft")][
                    "forecast_seconds_per_origin"
                ]
                * m["origin_counts"][task["split"]]
            )
        elif task["kind"] == "tune_lr":
            seconds += (
                len(config["random_learning_rates"])
                * config["epochs"]
                * benchmarks[task["model"]]["train_epoch_seconds"]
            )
    atomic_json(
        out / "estimate.json",
        {
            "estimated_neural_seconds": seconds,
            "budget_hours": config["hours"],
            "benchmarks": benchmarks,
            "exceeds_total_budget": seconds > config["hours"] * 3600,
            "limitations": "Upper bound uses full train timing for learning budgets; excludes CPU baseline tuning and ablation; stage caps still apply.",
        },
    )


def score_group(config, out, task):
    import numpy as np
    import pandas as pd
    from forecast_vn30 import score, report
    from vn30_forecast import load_manifest_data
    from research_protocol import validate_coverage
    from research_statistics import diagnostics
    from run_experiment import matrix
    from forecast_protocol import validate_forecast_metadata
    import yaml

    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_bytes()
    )

    tasks = {t["id"]: t for t in matrix(config)}
    folds = {tasks[f].get("fold", "primary") for f in task["forecasts"]}
    if len(folds) != 1:
        raise ValueError("Mixed fold comparison")
    m = json.loads((out / (folds.pop() + ".json")).read_text())
    df, _ = load_manifest_data(m)
    groupdir = out / "evaluation" / task["group"]
    for split in ("validation", "test"):
        paths = [
            out / "forecasts" / (f + ".csv")
            for f in task["forecasts"]
            if tasks[f]["split"] == split
        ]
        if not paths:
            continue
        models = set()
        for path in paths:
            meta = json.loads(path.with_suffix(".json").read_text())
            validate_forecast_metadata(
                meta, tasks[path.stem], config, m, out, provenance
            )
            if meta.get("forecast_csv_sha256") != file_hash(path):
                raise ValueError("Forecast CSV differs from its metadata checksum")
            if meta["model"] in models:
                raise ValueError("Duplicate model in comparison")
            models.add(meta["model"])
            if (
                meta["split"] != split
                or meta["dataset_sha256"] != m["sha256"]
                or meta["limited"]
            ):
                raise ValueError("Mismatched or limited forecast")
            if (
                meta["source_identity"]
                != __import__("research_protocol").source_identity()
            ):
                raise ValueError("Forecast came from a different source revision")
            validate_coverage(pd.read_csv(path), m, split)
        dest = groupdir / split
        if dest.exists():
            if not (dest / "verified.json").exists():
                raise ValueError("Unverified partial score directory")
            verified = json.loads((dest / "verified.json").read_text(encoding="utf-8"))
            inputs = {p.relative_to(ROOT).as_posix(): file_hash(p) for p in paths}
            inputs.update(
                {
                    p.with_suffix(".json").relative_to(ROOT).as_posix(): file_hash(
                        p.with_suffix(".json")
                    )
                    for p in paths
                }
            )
            if verified.get("source_forecasts") != inputs or not verified.get(
                "outputs"
            ):
                raise ValueError("Existing score has changed or unverifiable inputs")
            if any(
                not (dest / relative).is_file() or file_hash(dest / relative) != sha
                for relative, sha in verified["outputs"].items()
            ):
                raise ValueError("Existing score artifacts changed")
            continue
        score(df, m, paths, dest)
        table = pd.read_csv(dest / "scores.csv")
        details = pd.read_csv(dest / "details.csv")
        for row in table.itertuples():
            if row.target not in ("open", "close"):
                continue
            part = details.loc[
                (details.model == row.model) & (details.horizon == row.horizon)
            ]
            errors = (
                part["pred_" + row.target] - part["actual_" + row.target]
            ).to_numpy()
            if (
                len(errors) != row.n
                or not np.isclose(np.abs(errors).mean(), row.mae, atol=1e-10)
                or not np.isclose(np.sqrt(np.mean(errors**2)), row.rmse, atol=1e-10)
            ):
                raise ValueError("Independent metric recomputation differs")
        report(dest)
        if split == "test":
            diagnostics(df, m, details, dest)
        atomic_json(
            dest / "verified.json",
            {
                "independent_recomputation": "pass",
                "dataset_sha256": m["sha256"],
                "source_forecasts": {
                    q.relative_to(ROOT).as_posix(): file_hash(q)
                    for p in paths
                    for q in (p, p.with_suffix(".json"))
                },
                "outputs": {
                    p.relative_to(dest).as_posix(): file_hash(p)
                    for p in dest.rglob("*")
                    if p.is_file() and p.name != "verified.json"
                },
            },
        )


def make_report(config, out, state):
    import pandas as pd
    from run_experiment import matrix

    tasks = matrix(config)
    by_id = {t["id"]: t for t in tasks}
    records = []
    timings = []
    training = []
    for task in tasks:
        if state["tasks"].get(task["id"], {}).get("status") != "complete":
            continue
        if task["kind"] == "score":
            for split in ("validation", "test"):
                p = out / "evaluation" / task["group"] / split / "scores.csv"
                if p.exists():
                    frame = pd.read_csv(p)
                    frame["group"] = task["group"]
                    parent = by_id[task["group"]]
                    for key in ("seed", "fold", "budget", "initialization"):
                        frame[key] = parent.get(key)
                    records.append(frame)
        if task["kind"] == "ablation":
            for split in ("validation", "test"):
                p = (
                    out
                    / "ablation"
                    / task["id"]
                    / ("evaluation-" + split)
                    / "scores.csv"
                )
                if p.exists():
                    frame = pd.read_csv(p)
                    frame["group"] = task["id"]
                    frame["seed"] = task["seed"]
                    frame["fold"] = "primary"
                    frame["budget"] = None
                    frame["initialization"] = "random_backbone"
                    records.append(frame)
        if task["kind"] == "forecast":
            p = out / "forecasts" / (task["id"] + ".json")
            timings.append({"task": task["id"], **json.loads(p.read_text())})
        if task["kind"] == "train":
            p = out / "checkpoints" / task["id"] / "training.json"
            data = json.loads(p.read_text())
            training.append(
                {
                    "task": task["id"],
                    **{
                        k: data[k]
                        for k in (
                            "base_model",
                            "seed",
                            "data_budget",
                            "initialization",
                            "initial_validation_loss",
                            "best_validation_loss",
                            "best_epoch",
                            "selected_epoch_including_zero",
                            "elapsed_seconds",
                            "peak_cuda_allocated_bytes",
                        )
                    },
                }
            )
    pd.DataFrame(
        training,
        columns=[
            "task",
            "base_model",
            "seed",
            "data_budget",
            "initialization",
            "initial_validation_loss",
            "best_validation_loss",
            "best_epoch",
            "selected_epoch_including_zero",
            "elapsed_seconds",
            "peak_cuda_allocated_bytes",
        ],
    ).to_csv(out / "training_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                k: r.get(k)
                for k in (
                    "task",
                    "model",
                    "split",
                    "seed",
                    "origins",
                    "elapsed_seconds",
                )
            }
            for r in timings
        ],
        columns=["task", "model", "split", "seed", "origins", "elapsed_seconds"],
    ).to_csv(out / "runtime.csv", index=False)
    table = (
        pd.concat(records, ignore_index=True)
        if records
        else pd.DataFrame(
            columns=[
                "model",
                "split",
                "target",
                "horizon",
                "n",
                "mae",
                "rmse",
                "naive_mae",
                "mae_vs_naive",
                "group",
                "seed",
                "fold",
                "budget",
                "initialization",
            ]
        )
    )
    table.to_csv(out / "scores_all.csv", index=False)
    if not table.empty:
        main = table.loc[table.group.str.startswith("main-")].drop_duplicates(
            ["model", "seed", "split", "target", "horizon"]
        )
        main.groupby(["model", "split", "target", "horizon"]).agg(
            mean_mae=("mae", "mean"),
            std_mae=("mae", "std"),
            mean_rmse=("rmse", "mean"),
            seeds=("seed", "nunique"),
        ).reset_index().to_csv(out / "seed_summary.csv", index=False)
        selected = []
        for info in training:
            if not info["task"].startswith("main-"):
                continue
            chosen = (
                info["base_model"]
                if info["selected_epoch_including_zero"] == 0
                else info["base_model"] + "-ft"
            )
            part = table.loc[
                (table.group == info["task"]) & (table.model == chosen)
            ].copy()
            part["selected_epoch"] = info["selected_epoch_including_zero"]
            selected.append(part)
        if selected:
            pd.concat(selected, ignore_index=True).to_csv(
                out / "selected_scores.csv", index=False
            )
    incomplete = [
        {
            "id": t["id"],
            "stage": t["stage"],
            **state["tasks"].get(t["id"], {"status": "pending"}),
        }
        for t in tasks
        if state["tasks"].get(t["id"], {}).get("status") != "complete"
    ]
    atomic_json(out / "remaining.json", incomplete)
    lines = [
        "# VN30 — kết quả làm lại trên PC",
        "",
        f"Trạng thái: **{'hoàn thành' if not incomplete else 'chưa hoàn thành'}**.",
        "",
        "Kết quả dưới đây chỉ từ lượt chạy PC này. Không dùng forecast/checkpoint fine-tune của môi trường cũ.",
        "",
        f"Công việc hoàn thành: {len(tasks) - len(incomplete)}/{len(tasks)}. Ngân sách tổng: {config['hours']} giờ; không reset khi resume.",
        "",
    ]
    audit = out / "audit/audit.json"
    if audit.exists():
        a = json.loads(audit.read_text())
        lines.extend(
            [
                f"Kiểm toán dữ liệu: **{a['status']}**; dataset SHA256 `{a['dataset_sha256']}`.",
                "",
                "Xem [kiểm toán](audit/summary.md).",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "**Chưa kiểm toán được dữ liệu gốc. Không xác nhận chất lượng từ các score cũ.**",
                "",
            ]
        )
    lines.extend(["| Câu hỏi | Bằng chứng đã chạy |", "|---|---|"])
    for title, stages in (
        ("Q1 — zero-shot và baseline", ["main"]),
        ("Q2 — kích thước và lượng tử hóa", ["ablation"]),
        ("Q3 — lượng dữ liệu và pretraining", ["learning"]),
        ("Q4 — seed, horizon, volatility và fold", ["main", "folds"]),
    ):
        group = [t for t in tasks if t["stage"] in stages]
        done = sum(
            state["tasks"].get(t["id"], {}).get("status") == "complete" for t in group
        )
        lines.append(
            f"| {title} | {done}/{len(group)} công việc; {'đủ lượt chạy đã định' if done == len(group) else 'chưa đủ'} |"
        )
    if not table.empty:
        part = table.loc[(table.split == "test") & table.target.isin(["open", "close"])]
        lines.extend(
            [
                "",
                "## Điểm test đã kiểm tra",
                "",
                "| Nhóm | Model | Target | h | N | MAE | RMSE |",
                "|---|---|---|---:|---:|---:|---:|",
            ]
        )
        for r in part.itertuples():
            lines.append(
                f"| {r.group} | {r.model} | {r.target} | {r.horizon} | {r.n} | {r.mae:.4f} | {r.rmse:.4f} |"
            )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        main = part.loc[part.group.str.startswith("main-")]
        if not main.empty:
            fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
            for i, target in enumerate(("open", "close")):
                for j, h in enumerate((1, 5, 20)):
                    values = (
                        main.loc[(main.target == target) & (main.horizon == h)]
                        .groupby("model")
                        .mae.mean()
                    )
                    axes[i, j].bar(values.index, values.to_numpy())
                    axes[i, j].tick_params(axis="x", rotation=75)
                    axes[i, j].set_title(f"{target} h={h}")
                    axes[i, j].set_ylabel("MAE, VN30 points")
            fig.savefig(out / "main_comparison.png", dpi=140)
            plt.close(fig)
            lines.extend(["", "![MAE theo model](main_comparison.png)"])
        learning = part.loc[
            (part.fold == "primary")
            & part.model.isin(["kronos-small-ft", "chronos2-ft"])
        ].copy()
        if not learning.empty:
            total_train = json.loads((out / "primary.json").read_text())["boundaries"][
                "train"
            ]["rows"]
            learning["budget_sessions"] = (
                pd.to_numeric(learning.budget, errors="raise")
                .fillna(total_train)
                .astype(int)
            )
            curve = (
                learning.groupby(
                    ["model", "initialization", "budget_sessions", "target", "horizon"]
                )
                .agg(
                    mean_mae=("mae", "mean"),
                    std_mae=("mae", "std"),
                    seeds=("seed", "nunique"),
                )
                .reset_index()
            )
            curve.to_csv(out / "learning_curve.csv", index=False)
            fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
            for i, target in enumerate(("open", "close")):
                for j, h in enumerate((1, 5, 20)):
                    for (model, initialization), values in curve.loc[
                        (curve.target == target) & (curve.horizon == h)
                    ].groupby(["model", "initialization"]):
                        axes[i, j].plot(
                            values.budget_sessions,
                            values.mean_mae,
                            marker="o",
                            label=f"{model} {initialization}",
                        )
                    axes[i, j].set_title(f"{target} h={h}")
                    axes[i, j].set_xlabel("Training sessions")
                    axes[i, j].set_ylabel("MAE")
                    axes[i, j].legend(fontsize=6)
            fig.savefig(out / "learning_curve.png", dpi=140)
            plt.close(fig)
            lines.extend(["", "![Learning curve](learning_curve.png)"])
        histories = [
            r for r in training if r["task"].startswith("main-") and r["seed"] == 42
        ]
        if histories:
            fig, axes = plt.subplots(
                1,
                len(histories),
                figsize=(4 * len(histories), 3.5),
                squeeze=False,
                constrained_layout=True,
            )
            for ax, info in zip(axes[0], histories):
                h = pd.read_csv(out / "checkpoints" / info["task"] / "history.csv")
                ax.plot(h.epoch, h.train_loss, label="Train")
                ax.plot(
                    [0, *h.epoch],
                    [info["initial_validation_loss"], *h.validation_loss],
                    label="Validation",
                )
                ax.set_title(info["base_model"])
                ax.set_xlabel("Epoch")
                ax.set_ylabel("Model-specific loss")
                ax.legend()
            fig.savefig(out / "training_curves.png", dpi=140)
            plt.close(fig)
            lines.extend(["", "![Training curves](training_curves.png)"])
        lines.extend(
            [
                "",
                "Các điểm sau lựa chọn có tính epoch 0 nằm trong `selected_scores.csv`; điểm SFT trong bảng là checkpoint tốt nhất sau cập nhật.",
                "Các khoảng tin cậy paired block bootstrap và điểm theo regime/giai đoạn nằm trong từng thư mục `evaluation/<group>/test/`.",
            ]
        )
    lines.extend(
        [
            "",
            "## Giới hạn diễn giải",
            "",
            "- Test là lịch sử đã được xem. Cutoff pretraining chưa xác minh đầy đủ; không tuyên bố backtest triển khai lịch sử sạch.",
            "- Mini khác tokenizer; chênh lệch không chỉ do số tham số.",
            "- Quantization ablation chỉ kiểm tra can thiệp đó với encoder cố định, không chứng minh toàn bộ lợi ích K-line.",
            "- Kronos random control vẫn dùng tokenizer pretrained; đối chứng chỉ tách predictor pretraining.",
            "- Origin chồng lấn; bootstrap dùng block 20. Seed không phải mẫu thị trường độc lập.",
            "- Open phụ thuộc kiểm toán nguồn; không suy ra lợi nhuận giao dịch từ sai số chỉ số.",
            "",
            "## Phần còn thiếu",
            "",
            "Xem [danh sách công việc còn thiếu](remaining.json) và logs tương ứng.",
        ]
    )
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    atomic_json(
        out / "report_sources.json",
        {
            "source_identity": state["identity"],
            "scores_sha256": file_hash(out / "scores_all.csv"),
            "report_sha256": file_hash(out / "report.md"),
            "completed_tasks": {
                k: v.get("evidence", {})
                for k, v in state["tasks"].items()
                if v["status"] == "complete"
            },
        },
    )


def execute(config, out, task):
    kind = task["kind"]
    if kind == "audit":
        from audit_vn30_data import audit

        sources = [portable_path(p) for p in config["independent_sources"]]
        sources.extend(sorted((out / "independent").glob("*.csv")))
        if (out / "audit/audit.json").exists():
            result = json.loads((out / "audit/audit.json").read_text())
        else:
            result = audit(
                portable_path(config["dataset"]),
                portable_path(config["receipt"]),
                out / "audit",
                sources,
                portable_path(config["calendar"]) if config["calendar"] else None,
            )
        # Audit itself completes even when the data is unverified. Prepare blocks.
        print(result["status"])
    elif kind == "prepare":
        prepare(config, out)
    elif kind == "tune":
        tune(config, out, task["model"])
    elif kind == "tune_lr":
        tune_lr(config, out, task)
    elif kind == "benchmark":
        benchmark(config, out, task["model"])
    elif kind == "estimate":
        estimate(config, out)
    elif kind == "score":
        score_group(config, out, task)
    elif kind == "ablation":
        from representation_ablation import run_ablation

        run_ablation(config, out, task["seed"])
    else:
        raise ValueError(kind)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--task", required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    out = portable_path(config["output"])
    execute(config, out, json.loads(args.task))


if __name__ == "__main__":
    main()

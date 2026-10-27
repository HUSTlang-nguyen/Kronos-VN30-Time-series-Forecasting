"""Compare saved zero-shot/fine-tuned forecasts on identical VN30 origins."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--chronos-checkpoint", type=Path, required=True)
    parser.add_argument("--kronos-checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    training = {
        "chronos2": json.loads((args.chronos_checkpoint / "training.json").read_text(encoding="utf-8")),
        "kronos": json.loads((args.kronos_checkpoint / "training.json").read_text(encoding="utf-8")),
    }
    sha = training["chronos2"]["dataset_sha256"]
    for model, info in training.items():
        if (
            info["dataset_sha256"] != sha or info["test_used_for_training_or_selection"]
            or info["boundaries"] != training["chronos2"]["boundaries"]
            or (model == "kronos" and not info.get("teacher_forcing_causal_validation", False))
        ):
            raise ValueError("Training protocol mismatch")
    expected_models = {"naive", "ridge", "chronos2", "kronos", "chronos2-ft", "kronos-ft"}
    scores = []
    for split in ("validation", "test"):
        directory = getattr(args, split)
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        table = pd.read_csv(directory / "scores.csv")
        if manifest["dataset_sha256"] != sha or manifest["split"] != split or set(table.model) != expected_models:
            raise ValueError(f"Mismatched {split} evaluation")
        source_metadata = {}
        for path in manifest["source_forecasts"]:
            meta = json.loads(Path(path).with_suffix(".json").read_text(encoding="utf-8"))
            if meta["limited"] or meta["origins"] != manifest["origins"] or meta["dataset_sha256"] != sha:
                raise ValueError("Incomplete forecast coverage")
            if meta["model"].endswith("-ft"):
                base = meta["model"].removesuffix("-ft")
                if meta["revision"] != "finetuned:" + training[base]["checkpoint_files"]["model.safetensors"]:
                    raise ValueError("Fine-tuned forecast does not match selected checkpoint")
            source_metadata[meta["model"]] = meta
        if set(source_metadata) != expected_models:
            raise ValueError("Forecast model coverage differs")
        for base in training:
            before, after = source_metadata[base], source_metadata[base + "-ft"]
            if before["revision"] != training[base]["base_revision"] or any(
                before[key] != after[key] for key in ("device", "seed", "context", "horizon", "split", "origins")
            ):
                raise ValueError("Zero-shot and fine-tuned inference protocols differ")
            count_before = before.get("quantile_count", before["sample_count"]) if base == "chronos2" else before["sample_count"]
            count_after = after["quantile_count"] if base == "chronos2" else after["sample_count"]
            if count_before != count_after:
                raise ValueError("Forecast aggregation counts differ")
        scores.append(table)
    all_scores = pd.concat(scores, ignore_index=True)
    rows = []
    for split in ("validation", "test"):
        for model in training:
            for horizon in (1, 5, 20):
                for target in ("open", "close"):
                    part = all_scores.loc[(all_scores.split == split) & (all_scores.target == target) & (all_scores.horizon == horizon)].set_index("model")
                    before, after = part.loc[model], part.loc[model + "-ft"]
                    rows.append({
                        "split": split, "model": model, "target": target, "horizon": horizon,
                        "n": int(after.n), "zero_shot_mae": before.mae, "finetuned_mae": after.mae,
                        "naive_mae": part.loc["naive"].mae,
                        "mae_change_percent": 100 * (after.mae / before.mae - 1),
                        "zero_shot_rmse": before.rmse, "finetuned_rmse": after.rmse,
                    })
    comparison = pd.DataFrame(rows)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    comparison.to_csv(args.output / "comparison.csv", index=False)
    all_scores.to_csv(args.output / "scores.csv", index=False)
    source_paths = [
        args.validation / "scores.csv", args.test / "scores.csv",
        args.chronos_checkpoint / "training.json", args.kronos_checkpoint / "training.json",
        args.chronos_checkpoint / "history.csv", args.kronos_checkpoint / "history.csv",
    ]
    receipt = {
        "dataset_sha256": sha,
        "source_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths},
        "selected_checkpoint_sha256": {model: info["checkpoint_files"]["model.safetensors"] for model, info in training.items()},
        "test_used_for_training_or_selection": False,
    }
    (args.output / "manifest.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# VN30 — fine-tune và so sánh zero-shot", "",
        f"Dataset SHA256: `{sha}`. Giữ nguyên snapshot 2.271 phiên và split 70/15/15.", "",
        "Train: 1.589 phiên/1.442 cửa sổ; validation: 340/321; test: 342/323. Context 128, horizon 20.", "",
        "Fine-tune toàn bộ trọng số mô hình; Kronos giữ tokenizer pretrained cố định. Dùng AdamW và FP32. Mọi cửa sổ train được dùng một lần mỗi epoch. Checkpoint được chọn bằng validation loss trong các epoch đã huấn luyện; test không tham gia cập nhật trọng số hoặc chọn checkpoint.", "",
        "| Model | Epoch chọn | Validation loss trước | Validation loss sau | Train + validation (giây) | PyTorch allocated peak (MiB) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model, info in training.items():
        if (
            info["dataset_sha256"] != sha or info["test_used_for_training_or_selection"]
            or (model == "kronos" and not info.get("teacher_forcing_causal_validation", False))
        ):
            raise ValueError("Training protocol mismatch")
        lines.append(f"| {model} | {info['best_epoch']} | {info['initial_validation_loss']:.4f} | {info['best_validation_loss']:.4f} | {info['elapsed_seconds']:.1f} | {info['peak_cuda_allocated_bytes']/2**20:.1f} |")
    lines.append("")
    for model, info in training.items():
        lines.append(f"- {model}: {info['epochs']} epoch, learning rate {info['learning_rate']:g}, batch {info['batch_size_windows']} cửa sổ × accumulation {info['accumulation']}, seed {info['seed']}, device {info['device']}.")
    lines += [
        "", "Validation loss chỉ so sánh trước/sau trong cùng model: Chronos dùng quantile loss, Kronos dùng token cross-entropy cho 20 phiên đích với teacher forcing. Đây không phải sai số giá.", "",
        "MAE bên dưới tính bằng điểm VN30. Thay đổi âm nghĩa là fine-tune giảm lỗi so với zero-shot.", "",
        "| Tập | Model | Target | h | Zero-shot MAE | Fine-tune MAE | Thay đổi | Naive MAE |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in comparison.itertuples(index=False):
        lines.append(f"| {row.split} | {row.model} | {row.target} | {row.horizon} | {row.zero_shot_mae:.2f} | {row.finetuned_mae:.2f} | {row.mae_change_percent:+.2f}% | {row.naive_mae:.2f} |")
    lines += ["", "## Diễn giải", ""]
    for model in training:
        part = comparison.loc[(comparison.split == "test") & (comparison.model == model)]
        lines.append(f"- {model}: fine-tune giảm MAE ở {int((part.finetuned_mae < part.zero_shot_mae).sum())}/6 chỉ tiêu test so với zero-shot; thấp hơn Naive ở {int((part.finetuned_mae < part.naive_mae).sum())}/6 chỉ tiêu.")
        if training[model]["best_validation_loss"] > training[model]["initial_validation_loss"]:
            lines.append(f"- {model}: checkpoint pretrained có validation loss thấp hơn mọi epoch đã fine-tune. Train loss giảm trong khi validation loss tăng là dấu hiệu overfit ở cấu hình này; cải thiện nhỏ trên test không đủ để khẳng định khả năng tổng quát tốt hơn.")
    lines += [
        "", "Đây là một cấu hình và một seed, không phải tìm kiếm siêu tham số đầy đủ. Test đã được xem trong các vòng thử trước, nên kết quả không phải đánh giá trên holdout hoàn toàn mới. Checkpoint của Chronos có thời điểm kết thúc pretraining chưa được xác minh; không thể loại trừ overlap với lịch sử VN30.",
        "", "Kronos giữ causal mask trong teacher-forced validation: thay token tương lai không làm đổi logits ở các vị trí quá khứ. Khác biệt MAE chưa được kiểm định ý nghĩa thống kê; các cửa sổ dự báo chồng lấn nhau.",
        "", "Chronos trả 13 quantile, không phải 13 mẫu ngẫu nhiên. Giữ trung bình đều 13 quantile như vòng zero-shot cũ để so sánh; metadata mới được sửa thành quantile_mean. Kronos dùng trung bình 3 path với cùng seed theo origin, temperature 1 và top_p 0.9.",
        "", "Giá Open vẫn là giá do VNDIRECT cung cấp với một số phiên có cách dựng chưa rõ. Kronos nhận lịch phiên đích lịch sử thực tế. Các metric trên chỉ số không chứng minh lợi nhuận giao dịch.",
    ]
    (args.output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(13, 7), constrained_layout=True)
    model_order = ["naive", "chronos2", "chronos2-ft", "kronos", "kronos-ft"]
    labels = ["Naive", "Chronos ZS", "Chronos FT", "Kronos ZS", "Kronos FT"]
    for row, target in enumerate(("open", "close")):
        for col, horizon in enumerate((1, 5, 20)):
            part = all_scores.loc[(all_scores.split == "test") & (all_scores.target == target) & (all_scores.horizon == horizon)].set_index("model")
            ax = axes[row, col]
            values = part.loc[model_order, "mae"].to_numpy()
            bars = ax.bar(np.arange(len(labels)), values, color=["#666666", "#a7c7e7", "#2166ac", "#fbc19c", "#d95f02"])
            ax.bar_label(bars, fmt="%.1f", fontsize=8, padding=3)
            ax.set_xticks(np.arange(len(labels)), labels, rotation=30, ha="right", fontsize=8)
            ax.set_title(f"{target.title()} — h={horizon}")
            ax.set_ylabel("MAE (index points)")
            ax.set_ylim(0, values.max() * 1.2)
    fig.suptitle("VN30 test: zero-shot (ZS) vs fine-tuned (FT)")
    fig.savefig(args.output / "test_comparison.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), constrained_layout=True)
    directories = {"chronos2": args.chronos_checkpoint, "kronos": args.kronos_checkpoint}
    for ax, (model, info) in zip(axes, training.items()):
        history = pd.read_csv(directories[model] / "history.csv")
        ax.plot(history.epoch, history.train_loss, marker="o", label="Train")
        ax.plot([0, *history.epoch], [info["initial_validation_loss"], *history.validation_loss], marker="o", label="Validation")
        ax.axvline(info["best_epoch"], linestyle="--", color="#888888", label="Selected epoch")
        ax.set_title(model)
        ax.set_xlabel("Epoch (0 = pretrained)")
        ax.set_ylabel("Native loss (model-specific)")
        ax.legend(fontsize=8)
    fig.savefig(args.output / "training_loss.png", dpi=150)
    plt.close(fig)
    print(args.output / "summary.md")


if __name__ == "__main__":
    main()

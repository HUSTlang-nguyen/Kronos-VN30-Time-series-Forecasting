"""Combine complete train/validation/test VN30 evaluations from one snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    for split in ("train", "validation", "test"):
        parser.add_argument(f"--{split}", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    split_manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    frames = []
    expected_models = None
    expected_configs = {}
    for split in ("train", "validation", "test"):
        directory = getattr(args, split)
        evaluation = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        scores = pd.read_csv(directory / "scores.csv")
        models = set(scores.model)
        if (
            evaluation["dataset_sha256"] != split_manifest["sha256"]
            or evaluation["split"] != split
            or evaluation["origins"] != split_manifest["origin_counts"][split]
            or len(evaluation["models"]) != len(models)
            or set(scores.split) != {split}
            or set(scores.n) != {evaluation["origins"]}
            or scores.duplicated(["model", "target", "horizon"]).any()
        ):
            raise ValueError(f"Incomplete or mismatched {split} evaluation")
        if expected_models is None:
            expected_models = models
        elif models != expected_models:
            raise ValueError("Model sets differ across splits")
        source_models = set()
        for source in evaluation["source_forecasts"]:
            metadata = json.loads(Path(source).with_suffix(".json").read_text(encoding="utf-8"))
            model = metadata["model"]
            config = tuple(
                metadata[key]
                for key in ("revision", "device", "seed", "sample_count", "point_functional", "context", "horizon")
            )
            if (
                model in source_models
                or metadata["dataset_sha256"] != split_manifest["sha256"]
                or metadata["split"] != split
                or metadata["origins"] != evaluation["origins"]
                or metadata["limited"]
                or (model in expected_configs and config != expected_configs[model])
            ):
                raise ValueError(f"Forecast configuration mismatch: {split}/{model}")
            source_models.add(model)
            expected_configs[model] = config
        if source_models != models:
            raise ValueError(f"Forecast models differ from {split} scores")
        frames.append(scores)

    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(args.output / "scores_all_splits.csv", index=False)
    lines = [
        "# VN30 full-split experiment",
        "",
        f"Dataset SHA256: `{split_manifest['sha256']}`; {split_manifest['rows']} chronological sessions.",
        "",
        "| Split | Dates | Rows | Forecast origins |",
        "|---|---|---:|---:|",
    ]
    for split in ("train", "validation", "test"):
        boundary = split_manifest["boundaries"][split]
        lines.append(
            f"| {split} | {boundary['first_date']} to {boundary['last_date']} | "
            f"{boundary['rows']} | {split_manifest['origin_counts'][split]} |"
        )
    lines += [
        "",
        "MAE is in VN30 index points; lower is better. Each forecast origin has a complete 20-session target path within its split.",
        "",
        "| Split | Model | Open h1 | Close h1 | Open h5 | Close h5 | Open h20 | Close h20 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for split in ("train", "validation", "test"):
        for model in sorted(expected_models):
            part = combined.loc[(combined.split == split) & (combined.model == model)]
            values = []
            for horizon in (1, 5, 20):
                for target in ("open", "close"):
                    row = part.loc[(part.horizon == horizon) & (part.target == target)]
                    if len(row) != 1:
                        raise ValueError(f"Missing {split}/{model}/{target}/h{horizon}")
                    values.append(f"{row.mae.iloc[0]:.2f}")
            lines.append(f"| {split} | {model} | " + " | ".join(values) + " |")
    lines += [
        "",
        "Ridge is fitted on train, so its train score is in-sample. Naive requires no fit; Chronos-2 and Kronos use pretrained checkpoints without VN30 fine-tuning.",
        "Validation is for model/configuration comparison; test is the final historical holdout. This test period was already inspected in an earlier experiment, so it is not a newly untouched holdout.",
        "Absolute MAE across different time periods also reflects changes in VN30 index level and market volatility; compare models primarily within the same split.",
        "VNDIRECT Open construction is uncertain on some sessions. Kronos uses realized historical target-session dates as calendar features. These index errors do not establish trading performance.",
        "Full MAE/RMSE, gap and intraday scores are in `scores_all_splits.csv`; per-split diagnostics are in the evaluation folders.",
    ]
    (args.output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output / "summary.md")


if __name__ == "__main__":
    main()

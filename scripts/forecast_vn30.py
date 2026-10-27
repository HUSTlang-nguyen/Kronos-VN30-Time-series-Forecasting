"""Run VN30 forecasts on the pinned SQLite snapshot and score saved predictions."""

from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vn30_forecast import (  # noqa: E402 - src is resolved from this checkout
    COLS,
    CONTEXT,
    HORIZON,
    build_model,
    check_manifest,
    load,
    save_json,
    split_manifest,
)


def forecast(df, manifest, name, split, device, seed, out, limit, checkpoint=None):
    if out.exists() or out.with_suffix(".json").exists():
        raise FileExistsError(out)
    origins = manifest["origins"][split]
    if limit is not None:
        if limit < 1:
            raise ValueError("--limit must be positive")
        origins = origins[:limit]
    predictor, revision, samples = build_model(name, df, manifest, device, checkpoint)
    prices = df[COLS].to_numpy(dtype=np.float64)
    rows = []
    for number, i in enumerate(origins, 1):
        history = prices[i - CONTEXT + 1 : i + 1]
        xdates = df.session_date.iloc[i - CONTEXT + 1 : i + 1].reset_index(drop=True)
        ydates = df.session_date.iloc[i + 1 : i + HORIZON + 1].reset_index(drop=True)
        predicted = predictor(history, (xdates, ydates), seed + i)
        if predicted.shape != (HORIZON, 4) or not np.isfinite(predicted).all():
            raise ValueError(f"{name} failed at origin {i}")
        for h, values in enumerate(predicted, 1):
            rows.append(
                {
                    "origin_index": i,
                    "origin_date": df.date.iloc[i],
                    "target_date": df.date.iloc[i + h],
                    "horizon": h,
                    **{f"pred_{col}": float(v) for col, v in zip(COLS, values)},
                }
            )
        if number % 50 == 0 or number == len(origins):
            print(f"{name} {split}: {number}/{len(origins)} origins", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "model": name,
        "revision": revision,
        "dataset_sha256": manifest["sha256"],
        "split": split,
        "context": CONTEXT,
        "horizon": HORIZON,
        "device": device,
        "seed": seed,
        "sample_count": samples if name.startswith("kronos") else 0,
        "quantile_count": samples if name.startswith("chronos2") else 0,
        "point_functional": "quantile_mean" if name.startswith("chronos2") else "sample_mean" if samples else "deterministic",
        "checkpoint": str(checkpoint) if checkpoint else None,
        "origins": len(origins),
        "limited": limit is not None,
        "calendar_note": manifest["calendar_note"],
    }
    temp = out.with_name(out.name + ".partial")
    if temp.exists():
        raise FileExistsError(temp)
    try:
        pd.DataFrame(rows).to_csv(temp, index=False)
        temp.replace(out)
        save_json(out.with_suffix(".json"), meta)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
    print(json.dumps(meta, indent=2))


def score(df, manifest, paths, out):
    if out.exists():
        raise FileExistsError(out)
    labels = df.set_index("date")
    details = []
    stats = []
    comparison = None
    for path in paths:
        meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        if (
            meta["dataset_sha256"] != manifest["sha256"]
            or meta["context"] != CONTEXT
            or meta["horizon"] != HORIZON
        ):
            raise ValueError("Forecast metadata mismatch")
        split = meta["split"]
        origins = manifest["origins"][split][: meta["origins"]]
        if not meta["limited"] and len(origins) != len(manifest["origins"][split]):
            raise ValueError("Incomplete coverage")
        if comparison is None:
            comparison = (split, origins)
        elif comparison != (split, origins):
            raise ValueError("Models use different origins")
        predictions = pd.read_csv(path)
        if len(predictions) != len(origins) * HORIZON:
            raise ValueError("Incomplete forecast file")
        predicted_columns = [f"pred_{col}" for col in COLS]
        if not np.isfinite(predictions[predicted_columns].to_numpy(dtype=float)).all():
            raise ValueError(f"{path}: non-finite forecast")
        own = []
        for index, row in enumerate(predictions.itertuples(index=False)):
            i, h = origins[index // HORIZON], index % HORIZON + 1
            if (
                row.origin_index != i
                or row.horizon != h
                or row.origin_date != df.date.iloc[i]
                or row.target_date != df.date.iloc[i + h]
            ):
                raise ValueError("Forecast dates/origins mismatch")
            actual = labels.loc[row.target_date]
            item = {
                "model": meta["model"],
                "split": split,
                "origin_date": row.origin_date,
                "target_date": row.target_date,
                "horizon": h,
                "outside_request": int(actual.outside_request),
                "open_equals_previous_close": int(
                    abs(actual.open - df.close.iloc[i + h - 1]) < 1e-9
                ),
                "open_pattern_2025": int(
                    "2025-05-05" <= row.target_date <= "2025-08-11"
                ),
            }
            for target in ("open", "close"):
                pred = float(getattr(row, f"pred_{target}"))
                truth = float(actual[target])
                item.update(
                    {
                        f"pred_{target}": pred,
                        f"actual_{target}": truth,
                        f"error_{target}": pred - truth,
                    }
                )
            if h == 1:
                last = float(df.close.iloc[i])
                item.update(
                    {
                        "actual_gap": math.log(item["actual_open"] / last),
                        "pred_gap": math.log(item["pred_open"] / last)
                        if item["pred_open"] > 0
                        else math.nan,
                        "actual_intraday": math.log(
                            item["actual_close"] / item["actual_open"]
                        ),
                        "pred_intraday": math.log(
                            item["pred_close"] / item["pred_open"]
                        )
                        if min(item["pred_open"], item["pred_close"]) > 0
                        else math.nan,
                        "absolute_close_return": abs(
                            math.log(item["actual_close"] / last)
                        ),
                    }
                )
            own.append(item)
        detail = pd.DataFrame(own)
        details.extend(own)
        for h in (1, 5, 20):
            part = detail.loc[detail.horizon == h]
            for target in ("open", "close"):
                e = part[f"error_{target}"].to_numpy()
                stats.append(
                    {
                        "model": meta["model"],
                        "split": split,
                        "target": target,
                        "horizon": h,
                        "n": len(e),
                        "mae": float(np.abs(e).mean()),
                        "rmse": float(np.sqrt(np.mean(e**2))),
                    }
                )
        for target in ("gap", "intraday"):
            part = detail.loc[detail.horizon == 1]
            e = part[f"pred_{target}"] - part[f"actual_{target}"]
            stats.append(
                {
                    "model": meta["model"],
                    "split": split,
                    "target": target,
                    "horizon": 1,
                    "n": int(e.notna().sum()),
                    "mae": float(e.abs().mean()),
                    "rmse": float(np.sqrt(np.nanmean(e**2))),
                }
            )
    table = pd.DataFrame(stats)
    naive = table.loc[table.model == "naive", ["target", "horizon", "mae"]].rename(
        columns={"mae": "naive_mae"}
    )
    table = table.merge(naive, on=["target", "horizon"], how="left")
    table["mae_vs_naive"] = table.mae - table.naive_mae
    out.mkdir(parents=True)
    table.to_csv(out / "scores.csv", index=False)
    pd.DataFrame(details).to_csv(out / "details.csv", index=False)
    save_json(
        out / "manifest.json",
        {
            "dataset_sha256": manifest["sha256"],
            "split": comparison[0],
            "origins": len(comparison[1]),
            "models": [
                json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))["model"]
                for p in paths
            ],
            "source_forecasts": [str(p) for p in paths],
            "open_label": "VNDIRECT provider Open, construction uncertain",
            "tradability": "VN30 index; no trading PnL inferred",
        },
    )
    print(table.to_string(index=False))


def report(out):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    table = pd.read_csv(out / "scores.csv")
    details = pd.read_csv(out / "details.csv")
    for target in ("open", "close"):
        fig, ax = plt.subplots(figsize=(11, 4))
        data = details.loc[details.horizon == 1]
        actual = data.drop_duplicates("target_date").sort_values("target_date").tail(80)
        ax.plot(
            pd.to_datetime(actual.target_date),
            actual[f"actual_{target}"],
            label="VNDIRECT actual",
            color="black",
        )
        for name, group in data.groupby("model"):
            group = group.sort_values("target_date").tail(80)
            ax.plot(
                pd.to_datetime(group.target_date),
                group[f"pred_{target}"],
                label=name,
                alpha=0.7,
            )
        ax.set_title(f"VN30 {target} | last 80 forecast origins")
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(out / f"{target}_forecast.png", dpi=140)
        plt.close(fig)
    day_one = details.loc[details.horizon == 1]
    fig, ax = plt.subplots(figsize=(11, 4))
    for name, group in day_one.groupby("model"):
        group = group.sort_values("target_date")
        ax.plot(
            pd.to_datetime(group.target_date),
            group.error_close.abs().rolling(20, min_periods=1).mean(),
            label=name,
        )
    ax.set_title("VN30 Close h=1 | rolling 20-origin absolute error")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out / "close_error.png", dpi=140)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(11, 4))
    actual = day_one.drop_duplicates("target_date").sort_values("target_date")
    ax.plot(
        pd.to_datetime(actual.target_date),
        actual.actual_gap,
        label="VNDIRECT gap",
        color="black",
        alpha=0.7,
    )
    for name, group in day_one.groupby("model"):
        group = group.sort_values("target_date")
        ax.plot(
            pd.to_datetime(group.target_date), group.pred_gap, label=name, alpha=0.55
        )
    ax.set_title("VN30 next-session log gap (provider Open)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out / "gap_forecast.png", dpi=140)
    plt.close(fig)
    diag = (
        details.loc[details.horizon == 1]
        .groupby(["model", "open_equals_previous_close"], as_index=False)
        .agg(
            n=("error_open", "size"),
            open_mae=("error_open", lambda e: float(e.abs().mean())),
            close_mae=("error_close", lambda e: float(e.abs().mean())),
        )
    )
    diag.to_csv(out / "open_diagnostic.csv", index=False)
    day_one.groupby(["model", "open_pattern_2025"], as_index=False).agg(
        n=("error_open", "size"),
        open_mae=("error_open", lambda e: float(e.abs().mean())),
        close_mae=("error_close", lambda e: float(e.abs().mean())),
    ).to_csv(out / "open_pattern_diagnostic.csv", index=False)
    high_volatility_cutoff = day_one.drop_duplicates(
        "target_date"
    ).absolute_close_return.quantile(0.9)
    day_one = day_one.assign(
        high_volatility=day_one.absolute_close_return >= high_volatility_cutoff
    )
    day_one.groupby(["model", "high_volatility"], as_index=False).agg(
        n=("error_close", "size"),
        close_mae=("error_close", lambda e: float(e.abs().mean())),
    ).to_csv(out / "volatility_diagnostic.csv", index=False)
    details.groupby(["model", "horizon", "outside_request"], as_index=False).agg(
        n=("error_open", "size"),
        open_mae=("error_open", lambda e: float(e.abs().mean())),
        close_mae=("error_close", lambda e: float(e.abs().mean())),
    ).to_csv(out / "outside_request_diagnostic.csv", index=False)
    text = [
        "# VN30 snapshot experiment",
        "",
        f"Dataset SHA256: `{json.loads((out / 'manifest.json').read_text())['dataset_sha256']}`.",
        "",
        "Open is VNDIRECT provider data; its construction on some sessions is uncertain. The actual future trading calendar is supplied to Kronos. VN30 is an index, so these metrics do not imply tradable profit.",
        "",
        "| Model | Target | h | N | MAE | RMSE | MAE vs naive |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in table.itertuples():
        delta = "—" if pd.isna(r.mae_vs_naive) else f"{r.mae_vs_naive:.5f}"
        text.append(
            f"| {r.model} | {r.target} | {r.horizon} | {r.n} | {r.mae:.5f} | {r.rmse:.5f} | {delta} |"
        )
    text += [
        "",
        f"Diagnostic high-volatility threshold: absolute Close return >= {high_volatility_cutoff:.6f} (90th percentile of this test set; descriptive only).",
        "See `manifest.json`, `details.csv`, `open_diagnostic.csv`, `open_pattern_diagnostic.csv`, `outside_request_diagnostic.csv`, `volatility_diagnostic.csv` and the plots for exact inputs and diagnostics.",
    ]
    (out / "summary.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    print(out / "summary.md")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/local/split.json"
    )
    run = sub.add_parser("run")
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument(
        "--model", choices=["naive", "ridge", "chronos2", "kronos", "chronos2-ft", "kronos-ft"], required=True
    )
    run.add_argument("--checkpoint", type=Path, help="Fine-tuning output directory with training.json")
    run.add_argument("--split", choices=["train", "validation", "test"], default="test")
    run.add_argument("--device", default="cuda:0")
    run.add_argument("--seed", type=int, default=42)
    run.add_argument("--limit", type=int)
    run.add_argument("--output", type=Path, required=True)
    ev = sub.add_parser("score")
    ev.add_argument("--manifest", type=Path, required=True)
    ev.add_argument("--forecasts", type=Path, nargs="+", required=True)
    ev.add_argument("--output", type=Path, required=True)
    rep = sub.add_parser("report")
    rep.add_argument("--scores", type=Path, required=True)
    args = p.parse_args()
    if args.command == "report":
        report(args.scores)
        return
    df, sha = load()
    if args.command == "prepare":
        save_json(args.output, split_manifest(df, sha))
        print(args.output)
        return
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    check_manifest(df, sha, manifest)
    if args.command == "run":
        forecast(
            df,
            manifest,
            args.model,
            args.split,
            args.device,
            args.seed,
            args.output,
            args.limit,
            args.checkpoint,
        )
    else:
        score(df, manifest, args.forecasts, args.output)


if __name__ == "__main__":
    main()

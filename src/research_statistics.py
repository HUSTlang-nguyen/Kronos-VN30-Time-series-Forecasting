"""Paired temporal uncertainty and origin-known volatility diagnostics."""

from __future__ import annotations
import numpy as np
import pandas as pd


def block_interval(differences, block=20, draws=2000, seed=42):
    differences = np.asarray(differences, dtype=float)
    if (
        differences.ndim != 1
        or len(differences) == 0
        or not np.isfinite(differences).all()
    ):
        raise ValueError("Invalid paired errors")
    n = len(differences)
    block = min(block, n)
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n - block + 1, size=(draws, int(np.ceil(n / block))))
    indices = (starts[:, :, None] + np.arange(block)).reshape(draws, -1)[:, :n]
    values = differences[indices].mean(axis=1)
    return np.quantile(values, [0.025, 0.975]).tolist()


def diagnostics(df, manifest, details, out):
    from research_protocol import atomic_json

    origins = manifest["origins"]["test"]
    sigma = np.log(df.close / df.close.shift()).rolling(20).std(ddof=1)
    train = manifest["boundaries"]["train"]
    threshold = float(
        sigma.iloc[train["row_start"] : train["row_end_exclusive"]]
        .dropna()
        .quantile(0.9)
    )
    labels = {
        df.date.iloc[i]: "high" if sigma.iloc[i] >= threshold else "normal"
        for i in origins
    }
    chunks = {
        df.date.iloc[i]: f"period-{min(2, k * 3 // len(origins)) + 1}"
        for k, i in enumerate(origins)
    }
    details = details.copy()
    details["regime"] = details.origin_date.map(labels)
    details["period"] = details.origin_date.map(chunks)
    if details[["regime", "period"]].isna().any().any():
        raise ValueError("Unassigned test origin")
    rows = []
    intervals = []
    for (model, h), part in details.loc[details.horizon.isin([1, 5, 20])].groupby(
        ["model", "horizon"]
    ):
        naive = details.loc[(details.model == "naive") & (details.horizon == h)]
        paired = part.merge(
            naive,
            on=["origin_date", "target_date", "horizon"],
            suffixes=("", "_naive"),
            validate="one_to_one",
        ).sort_values("origin_date")
        if len(paired) != len(origins):
            raise ValueError("Bootstrap comparison changed sample")
        for target in ("open", "close"):
            delta = (
                paired["error_" + target].abs()
                - paired["error_" + target + "_naive"].abs()
            ).to_numpy()
            low, high = block_interval(delta)
            intervals.append(
                {
                    "model": model,
                    "horizon": h,
                    "target": target,
                    "n": len(delta),
                    "mae_difference_vs_naive": delta.mean(),
                    "ci_low": low,
                    "ci_high": high,
                    "block": 20,
                    "draws": 2000,
                }
            )
        for grouping in ("regime", "period"):
            for group, subset in part.groupby(grouping):
                for target in ("open", "close"):
                    errors = subset["error_" + target].to_numpy()
                    rows.append(
                        {
                            "model": model,
                            "horizon": h,
                            "target": target,
                            "grouping": grouping,
                            "group": group,
                            "n": len(errors),
                            "mae": np.abs(errors).mean(),
                            "rmse": np.sqrt(np.mean(errors**2)),
                        }
                    )
    pd.DataFrame(rows).to_csv(out / "regime_period_scores.csv", index=False)
    pd.DataFrame(intervals).to_csv(out / "paired_block_intervals.csv", index=False)
    pd.DataFrame(
        {
            "origin_date": [df.date.iloc[i] for i in origins],
            "sigma20": [sigma.iloc[i] for i in origins],
            "regime": [labels[df.date.iloc[i]] for i in origins],
        }
    ).to_csv(out / "origin_regimes.csv", index=False)
    atomic_json(
        out / "diagnostic_manifest.json",
        {
            "threshold": threshold,
            "threshold_fitted_on": "train only",
            "known_at": "origin close",
            "block": 20,
            "bootstrap_draws": 2000,
            "dependent_overlapping_origins": True,
        },
    )

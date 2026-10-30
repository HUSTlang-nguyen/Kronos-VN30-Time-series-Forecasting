"""Read-only verification of completed candidate forecasts against SQLite labels.

This post-run verifier does not import the scorer or consume details.csv to
recompute metrics. It writes a separate receipt, never modifies old artifacts,
and does not promote the candidate dataset to accepted status.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def portable(value):
    path = Path(str(value).replace("\\", "/"))
    return path if path.is_absolute() else ROOT / path


def close(actual, expected, message):
    require(
        np.allclose(actual, expected, rtol=1e-10, atol=1e-10, equal_nan=True),
        message,
    )


def validate_frame(frame, meta, manifest, data):
    origins = np.asarray(manifest["origins"][meta["split"]], dtype=int)
    horizon = int(manifest["horizon"])
    require(not meta["limited"], "Limited forecast cannot certify full coverage")
    require(meta["origins"] == len(origins), "Incorrect metadata origin count")
    require(meta["horizon"] == horizon == 20, "Horizon differs")
    require(meta["context"] == manifest["context"] == 128, "Context differs")
    require(len(frame) == len(origins) * horizon, "Missing/duplicate forecast rows")
    require(not frame.duplicated(["origin_index", "horizon"]).any(), "Duplicate origin/h")
    indices = np.repeat(origins, horizon)
    steps = np.tile(np.arange(1, horizon + 1), len(origins))
    require(np.array_equal(frame.origin_index, indices), "Origin order differs")
    require(np.array_equal(frame.horizon, steps), "Path is not exactly 1..20")
    dates = data.date.to_numpy()
    require(np.array_equal(frame.origin_date, dates[indices]), "Origin date differs")
    require(np.array_equal(frame.target_date, dates[indices + steps]), "Target date differs")
    bounds = manifest["boundaries"][meta["split"]]
    require(
        (indices + steps >= bounds["row_start"]).all()
        and (indices + steps < bounds["row_end_exclusive"]).all(),
        "Forecast labels cross split boundary",
    )
    require(np.isfinite(frame[["pred_" + c for c in ("open", "high", "low", "close")]]).all().all(), "Non-finite forecast")
    errors = {}
    for target in ("open", "close"):
        errors[target] = frame["pred_" + target].to_numpy() - data[target].to_numpy()[indices + steps]
    one = steps == 1
    last = data.close.to_numpy()[indices[one]]
    actual_open = data.open.to_numpy()[indices[one] + 1]
    actual_close = data.close.to_numpy()[indices[one] + 1]
    pred_open = frame.pred_open.to_numpy()[one]
    pred_close = frame.pred_close.to_numpy()[one]
    with np.errstate(invalid="ignore", divide="ignore"):
        errors["gap"] = np.where(pred_open > 0, np.log(pred_open / last), np.nan) - np.log(actual_open / last)
        errors["intraday"] = np.where((pred_open > 0) & (pred_close > 0), np.log(pred_close / pred_open), np.nan) - np.log(actual_close / actual_open)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=ROOT / "artifacts/local/pc-exploratory-20261030")
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    out = candidate / "review"
    out.mkdir(exist_ok=True)
    hashes = {}

    def digest(path):
        path = path.resolve()
        if path not in hashes:
            h = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(4 << 20), b""):
                    h.update(block)
            hashes[path] = h.hexdigest()
        return hashes[path]

    manifest = read(candidate / "candidate.json")
    database = portable(manifest["dataset"])
    require(digest(database) == manifest["sha256"], "Dataset hash differs")
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as con:
        require(con.execute("PRAGMA integrity_check").fetchone() == ("ok",), "SQLite integrity failed")
        data = pd.read_sql_query("SELECT date,open,high,low,close FROM candles ORDER BY date,row_id", con)
    require(len(data) == manifest["rows"], "Dataset row count differs")
    require(not data.date.duplicated().any(), "Duplicate label dates")
    frames = {}
    rebuilt = []
    directories = sorted(p.parent for p in candidate.rglob("scores.csv") if (p.parent / "manifest.json").is_file())
    require(len(directories) == 88, f"Expected 88 scored groups, found {len(directories)}")
    for dest in directories:
        info = read(dest / "manifest.json")
        local = manifest
        if "folds" in dest.parts:
            local = read(dest.parent / "candidate.json")
        require(info["dataset_sha256"] == local["sha256"] == manifest["sha256"], "Score dataset differs")
        computed = {}
        paths = [portable(p) for p in info["source_forecasts"]]
        require(len(paths) == len(set(paths)), "Repeated forecast input")
        for path in paths:
            meta = read(path.with_suffix(".json"))
            require(meta["evidence_scope"] == "exploratory_only", "Forecast scope differs")
            require(meta["dataset_sha256"] == manifest["sha256"], "Forecast dataset differs")
            require(meta["forecast_csv_sha256"] == digest(path), "Forecast hash differs")
            require(meta["split"] == info["split"], "Score split differs")
            if path not in frames:
                frame = pd.read_csv(path)
                errors = validate_frame(frame, meta, local, data)
                frames[path] = (frame, errors)
            frame, errors = frames[path]
            require(meta["model"] not in computed, "Duplicate model in scored group")
            computed[meta["model"]] = {}
            for target, values in errors.items():
                for horizon in ((1, 5, 20) if target in ("open", "close") else (1,)):
                    part = values[frame.horizon.to_numpy() == horizon] if target in ("open", "close") else values
                    finite = part[np.isfinite(part)]
                    require(len(finite) > 0, "No finite metric observations")
                    computed[meta["model"]][target, horizon] = (len(finite), float(np.abs(finite).mean()), float(np.sqrt(np.mean(finite ** 2))))
        table = pd.read_csv(dest / "scores.csv")
        require(len(table) == len(computed) * 8, "Incomplete or excess metric rows")
        require(not table.duplicated(["model", "target", "horizon"]).any(), "Duplicate metric row")
        require(set(table.model) == set(computed), "Score models differ")
        for row in table.itertuples():
            n, mae, rmse = computed[row.model][row.target, row.horizon]
            require(row.n == n, "Metric sample count differs")
            close([row.mae, row.rmse], [mae, rmse], "MAE/RMSE differs from raw forecast + SQLite")
            naive = computed["naive"][row.target, row.horizon][1]
            close([row.naive_mae, row.mae_vs_naive], [naive, mae - naive], "Naive comparison differs")
            rebuilt.append(dict(group=dest.relative_to(candidate).as_posix(), model=row.model, split=row.split, target=row.target, horizon=row.horizon, n=n, mae=mae, rmse=rmse))
    print(f"Verified {len(directories)} score groups from {len(frames)} forecast files", flush=True)
    receipts = 0
    for path in sorted(candidate.rglob("verified.json")):
        proof = read(path)
        if not isinstance(proof, dict) or "outputs" not in proof:
            continue
        for value, sha in proof.get("source_forecasts", {}).items():
            require(digest(portable(value)) == sha, f"Receipt input changed: {value}")
        for name, sha in proof["outputs"].items():
            require(digest(path.parent / name) == sha, f"Receipt output changed: {path.parent / name}")
        receipts += 1
    training_count = 0
    for path in sorted(candidate.rglob("training.json")):
        for name in ("training.json", "selection.json"):
            receipt = read(path.with_name(name))
            require(receipt["dataset_sha256"] == manifest["sha256"], "Training dataset differs")
            require(receipt["evidence_scope"] == "exploratory_only", "Training scope differs")
            require(receipt["test_used_for_training_or_selection"] is False, "Training selection used test")
            for filename, sha in receipt["checkpoint_files"].items():
                checkpoint = path.parent / receipt["checkpoint_directory"] / filename
                require(digest(checkpoint) == sha, f"Checkpoint bytes changed: {checkpoint}")
        training_count += 1
    # Reuse a real frame to prove the independent check rejects shifted dates.
    frame = next(iter(frames.values()))[0].copy()
    sample_path = next(iter(frames))
    sample_meta = read(sample_path.with_suffix(".json"))
    sample_manifest = manifest
    if "folds" in sample_path.parts:
        sample_manifest = read(sample_path.parent.parent / "candidate.json")
    frame.loc[0, "target_date"] = "1900-01-01"
    try:
        validate_frame(frame, sample_meta, sample_manifest, data)
    except ValueError:
        negative_check = "shifted target date rejected"
    else:
        raise ValueError("Negative date check failed to reject corruption")
    pd.DataFrame(rebuilt).to_csv(out / "recomputed_metrics.csv", index=False)
    receipt = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "evidence_scope": "exploratory_only",
        "dataset_accepted": False,
        "dataset_sha256": digest(database),
        "verifier_sha256": digest(Path(__file__)),
        "score_groups": len(directories),
        "forecast_files": len(frames),
        "metric_rows": len(rebuilt),
        "verified_output_receipts": receipts,
        "training_and_selection_pairs": training_count,
        "negative_check": negative_check,
        "metrics_recomputed_from": "raw forecast CSV plus read-only SQLite; scorer/details.csv not used",
        "recomputed_metrics_sha256": digest(out / "recomputed_metrics.csv"),
        "limitations": ["Does not certify market accuracy of provider labels", "Does not prove pretraining exclusion of VN30", "Does not independently rerun bootstrap or statistical model selection"],
        "input_hashes": {p.relative_to(ROOT).as_posix(): sha for p, sha in hashes.items() if p.is_relative_to(ROOT)},
    }
    (out / "numerical_validation.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "input_hashes"}, indent=2))


if __name__ == "__main__":
    main()

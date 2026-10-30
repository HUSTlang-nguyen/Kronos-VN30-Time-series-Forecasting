"""Evaluate frozen PC candidate checkpoints; outputs remain exploratory only."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from research_protocol import (
    MODELS,
    atomic_json,
    file_hash,
    portable_path,
    source_identity,
    validate_coverage,
)
from vn30_forecast import (
    COLS,
    CONTEXT,
    HORIZON,
    build_model,
    check_manifest,
    load_manifest_data,
)
from forecast_protocol import sampling_spec
from forecast_vn30 import forecast, score, report
from run_candidate_training import verify_training
from statistical_baselines import candidates, selection_loss
from research_statistics import diagnostics


def additions_only(previous, current):
    """Old training code stays immutable; only this evaluation entry point is new."""
    if any(current.get(k) != v for k, v in previous.items()):
        raise ValueError("Previously locked training/inference code changed")
    if set(current) - set(previous) != {"scripts/evaluate_candidate.py"}:
        raise ValueError("Unexpected code additions outside the evaluation entry point")


def context(candidate, config_path):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    training = json.loads((candidate / "identity.json").read_text())
    current = source_identity()
    additions_only(training["source_identity"], current)
    if training["config_sha256"] != file_hash(config_path):
        raise ValueError("Original configuration changed")
    parent = json.loads(
        (portable_path(training["parent_output"]) / "state.json").read_text()
    )
    if (parent["started_unix"], parent["deadline_unix"]) != (
        training["original_started_unix"],
        training["deadline_unix"],
    ):
        raise ValueError("Original budget changed")
    provenance_path = ROOT / "data/manifests/checkpoint_provenance.yaml"
    if file_hash(provenance_path) != parent["identity"]["provenance_sha256"]:
        raise ValueError("Checkpoint provenance changed")
    manifest_path = candidate / "candidate.json"
    if file_hash(manifest_path) != training["manifest_sha256"]:
        raise ValueError("Candidate manifest changed")
    manifest = json.loads(manifest_path.read_text())
    df, sha = load_manifest_data(manifest, allow_exploratory=True)
    check_manifest(df, sha, manifest)
    out = candidate / "evaluation-main"
    out.mkdir(parents=True, exist_ok=True)
    identity = {
        "evidence_scope": "exploratory_only",
        "dataset_accepted": False,
        "training_identity_sha256": file_hash(candidate / "identity.json"),
        "manifest_sha256": file_hash(manifest_path),
        "dataset_sha256": sha,
        "source_identity": current,
        "compatibility": "all previously locked files unchanged; evaluation entry point added",
        "original_started_unix": training["original_started_unix"],
        "original_deadline_unix": training["deadline_unix"],
        "main_deadline_unix": min(
            training["deadline_unix"],
            training["original_started_unix"] + config["stage_hours"]["main"] * 3600,
        ),
        "config_sha256": file_hash(config_path),
        "provenance_sha256": file_hash(provenance_path),
    }
    receipt = out / "identity.json"
    if receipt.exists() and json.loads(receipt.read_text()) != identity:
        raise ValueError(
            "Evaluation identity changed; do not overwrite existing evidence"
        )
    if not receipt.exists():
        atomic_json(receipt, identity)
    return config, training, manifest, df, out, identity


def check_deadline(identity):
    if time.time() >= identity["main_deadline_unix"]:
        raise TimeoutError("Original main-stage deadline exhausted")


def checkpoint(candidate, training_identity, config, manifest, model, seed):
    path = candidate / "checkpoints" / f"train-{model}-s{seed}"
    trained = verify_training(
        path, training_identity, model, config["epochs"], seed, config
    )
    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_bytes()
    )
    key, token_key, _ = MODELS[model]
    expected = {
        "base_revision": provenance["models"][key]["repository_revision"],
        "boundaries": manifest["boundaries"],
        "context": CONTEXT,
        "horizon": HORIZON,
        "normalization": "context_only",
        "method": "full",
        "weight_decay": 0.01,
        "origins": {s: len(manifest["origins"][s]) for s in ("train", "validation")},
        "tokenizer": token_key or "not_applicable",
        "tokenizer_revision": provenance["tokenizers"][token_key]["repository_revision"]
        if token_key
        else None,
    }
    if token_key:
        expected["teacher_forcing_causal_validation"] = True
    if any(trained.get(k) != v for k, v in expected.items()):
        raise ValueError("Frozen candidate training protocol differs")
    return path, trained


def validate_forecast(
    path,
    manifest,
    df,
    identity,
    name,
    split,
    seed,
    config,
    ckpt=None,
    trained=None,
    locked=None,
):
    meta = json.loads(path.with_suffix(".json").read_text())
    base = name.removesuffix("-ft")
    neural = base in MODELS
    expected = {
        "evidence_scope": "exploratory_only",
        "model": name,
        "split": split,
        "seed": seed,
        "dataset_sha256": manifest["sha256"],
        "context": CONTEXT,
        "horizon": HORIZON,
        "device": config["device"] if neural else "cpu",
        "origins": len(manifest["origins"][split]),
        "limited": False,
        "source_identity": identity["source_identity"],
        "forecast_csv_sha256": file_hash(path),
        "checkpoint_choice": "best-trained",
        "calendar_note": manifest["calendar_note"],
        "model_config": locked or {},
        "sampling": sampling_spec(name),
        "sample_count": 3 if base.startswith("kronos-") else 0,
        "quantile_count": 13 if base == "chronos2" else 0,
        "point_functional": "quantile_mean"
        if base == "chronos2"
        else "sample_mean"
        if base.startswith("kronos-")
        else "deterministic",
    }
    if ckpt is not None:
        if portable_path(meta.get("checkpoint", "")).resolve() != ckpt.resolve():
            raise ValueError("Candidate forecast refers to a different checkpoint")
        revision = "finetuned:" + trained["checkpoint_files"]["model.safetensors"]
    else:
        if meta.get("checkpoint") is not None:
            raise ValueError("Unexpected candidate checkpoint")
        if neural:
            provenance = yaml.safe_load(
                (ROOT / "data/manifests/checkpoint_provenance.yaml").read_bytes()
            )
            revision = provenance["models"][MODELS[base][0]]["repository_revision"]
        elif name == "naive":
            revision = "last_close"
        elif name == "ridge":
            revision = f"ridge_train_only_alpha{float(locked['alpha']):g}"
        else:
            revision = "validation_locked:" + json.dumps(locked, sort_keys=True)
    expected["revision"] = revision
    if any(meta.get(k) != v for k, v in expected.items()):
        bad = [k for k, v in expected.items() if meta.get(k) != v]
        raise ValueError("Candidate forecast protocol differs: " + ", ".join(bad))
    data = pd.read_csv(path)
    validate_coverage(data, manifest, split)
    for r in data.itertuples():
        if (
            r.origin_date != df.date.iloc[r.origin_index]
            or r.target_date != df.date.iloc[r.origin_index + r.horizon]
        ):
            raise ValueError("Candidate forecast dates differ")
    return meta


def run_forecast(
    candidate,
    training,
    config,
    manifest,
    df,
    out,
    identity,
    model,
    split,
    seed,
    ft=False,
    locked=None,
):
    check_deadline(identity)
    name = model + "-ft" if ft else model
    key = f"{model}-s{seed}-{'ft' if ft else 'zs'}-{split}"
    target = out / "forecasts" / (key + ".csv")
    target.parent.mkdir(exist_ok=True)
    path, receipt = (
        checkpoint(candidate, training, config, manifest, model, seed)
        if ft
        else (None, None)
    )
    if not target.exists():
        forecast(
            df,
            manifest,
            name,
            split,
            config["device"] if model in MODELS else "cpu",
            seed,
            target,
            None,
            path,
            locked,
        )
    validate_forecast(
        target, manifest, df, identity, name, split, seed, config, path, receipt, locked
    )
    return target


def tune(config, manifest, df, out, identity, model):
    trials_path = out / "tuning" / (model + "-trials.json")
    lock = out / "tuning" / (model + ".json")
    if lock.exists():
        return read_lock(out, model, identity)
    prices = df[COLS].to_numpy(float)
    scale = prices[: manifest["boundaries"]["train"]["row_end_exclusive"]].std(axis=0)
    if (scale <= 0).any():
        raise ValueError("Degenerate training scale")
    trials = json.loads(trials_path.read_text()) if trials_path.exists() else []
    grid = candidates(model)
    if [r["config"] for r in trials] != grid[: len(trials)] or any(
        r["expected_origins"] != len(manifest["origins"]["validation"]) for r in trials
    ):
        raise ValueError("Candidate tuning cache differs")
    for candidate_config in grid[len(trials) :]:
        check_deadline(identity)
        predictor, _, _ = build_model(
            model, df, manifest, "cpu", model_config=candidate_config
        )
        predictions, truths, failures = [], [], []
        for i in manifest["origins"]["validation"]:
            check_deadline(identity)
            try:
                predictions.append(
                    predictor(prices[i - CONTEXT + 1 : i + 1], None, 42 + i)
                )
                truths.append(prices[i + 1 : i + HORIZON + 1])
            except Exception as exc:
                failures.append(
                    {
                        "origin_index": i,
                        "date": df.date.iloc[i],
                        "error": type(exc).__name__ + ": " + str(exc),
                    }
                )
        loss = (
            None
            if failures
            else selection_loss(np.stack(predictions), np.stack(truths), scale)
        )
        trials.append(
            {
                "config": candidate_config,
                "validation_loss": loss,
                "expected_origins": len(manifest["origins"]["validation"]),
                "successful_origins": len(predictions),
                "failures": failures,
            }
        )
        atomic_json(trials_path, trials)
        print(
            model,
            candidate_config,
            "validation",
            loss,
            "failures",
            len(failures),
            flush=True,
        )
    eligible = [r for r in trials if r["validation_loss"] is not None]
    if not eligible:
        raise RuntimeError(
            "No baseline configuration achieved full validation coverage"
        )
    best = min(eligible, key=lambda r: r["validation_loss"])
    if lock.exists() and json.loads(lock.read_text()) != best["config"]:
        raise ValueError("Locked candidate baseline configuration changed")
    if not lock.exists():
        atomic_json(lock, best["config"])
    atomic_json(
        out / "tuning" / (model + "-receipt.json"),
        {
            "evidence_scope": "exploratory_only",
            "source_identity": identity["source_identity"],
            "manifest_sha256": identity["manifest_sha256"],
            "selected_on": "validation only",
            "test_used": False,
            "trials_sha256": file_hash(trials_path),
            "config_sha256": file_hash(lock),
        },
    )
    return best["config"]


def read_lock(out, model, identity):
    directory = out / "tuning"
    receipt = json.loads((directory / (model + "-receipt.json")).read_text())
    expected = {
        "evidence_scope": "exploratory_only",
        "source_identity": identity["source_identity"],
        "manifest_sha256": identity["manifest_sha256"],
        "selected_on": "validation only",
        "test_used": False,
        "trials_sha256": file_hash(directory / (model + "-trials.json")),
        "config_sha256": file_hash(directory / (model + ".json")),
    }
    if receipt != expected:
        raise ValueError("Candidate baseline validation lock changed")
    return json.loads((directory / (model + ".json")).read_text())


def verify_metrics(dest):
    details = pd.read_csv(dest / "details.csv")
    table = pd.read_csv(dest / "scores.csv")
    for row in table.itertuples():
        if row.target not in ("open", "close"):
            continue
        part = details.loc[
            (details.model == row.model) & (details.horizon == row.horizon)
        ]
        errors = (part["pred_" + row.target] - part["actual_" + row.target]).to_numpy()
        if (
            len(errors) != row.n
            or not np.isclose(np.abs(errors).mean(), row.mae, atol=1e-10)
            or not np.isclose(np.sqrt(np.mean(errors**2)), row.rmse, atol=1e-10)
        ):
            raise ValueError("Independent candidate metric recomputation differs")
    return details, table


def score_all(candidate, training, config, manifest, df, out, identity):
    for seed in config["seeds"]:
        for split in ("validation", "test"):
            paths = []
            for model in ("naive", "ridge", "ets", "arima"):
                locked = {} if model == "naive" else read_lock(out, model, identity)
                p = out / "forecasts" / f"{model}-s42-zs-{split}.csv"
                validate_forecast(
                    p, manifest, df, identity, model, split, 42, config, locked=locked
                )
                paths.append(p)
            for model in config["models"]:
                for ft in (False, True):
                    p = (
                        out
                        / "forecasts"
                        / f"{model}-s{seed}-{'ft' if ft else 'zs'}-{split}.csv"
                    )
                    path, receipt = (
                        checkpoint(candidate, training, config, manifest, model, seed)
                        if ft
                        else (None, None)
                    )
                    validate_forecast(
                        p,
                        manifest,
                        df,
                        identity,
                        model + ("-ft" if ft else ""),
                        split,
                        seed,
                        config,
                        path,
                        receipt,
                    )
                    paths.append(p)
            dest = out / "scores" / f"seed-{seed}" / split
            inputs = {
                p.relative_to(ROOT).as_posix(): file_hash(p)
                for path in paths
                for p in (path, path.with_suffix(".json"))
            }
            if dest.exists():
                verified = json.loads((dest / "verified.json").read_text())
                if verified["source_forecasts"] != inputs or any(
                    file_hash(dest / name) != sha
                    for name, sha in verified["outputs"].items()
                ):
                    raise ValueError("Candidate score cache changed")
                verify_metrics(dest)
                continue
            score(df, manifest, paths, dest)
            details, table = verify_metrics(dest)
            report(dest)
            if split == "test":
                diagnostics(df, manifest, details, dest)
            summary = dest / "summary.md"
            summary.write_text(
                "**THĂM DÒ — dataset unverified; không phải kết luận chính Q1–Q4.**\n\n"
                + summary.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            atomic_json(
                dest / "verified.json",
                {
                    "evidence_scope": "exploratory_only",
                    "dataset_accepted": False,
                    "independent_recomputation": "pass",
                    "seed": seed,
                    "source_forecasts": inputs,
                    "outputs": {
                        p.relative_to(dest).as_posix(): file_hash(p)
                        for p in dest.rglob("*")
                        if p.is_file()
                    },
                },
            )
    tables = []
    for seed in config["seeds"]:
        for split in ("validation", "test"):
            t = pd.read_csv(out / "scores" / f"seed-{seed}" / split / "scores.csv")
            t["seed"] = seed
            tables.append(t)
    all_scores = pd.concat(tables, ignore_index=True)
    all_scores.to_csv(out / "scores_all.csv", index=False)
    all_scores.groupby(["model", "split", "target", "horizon"]).agg(
        seeds=("seed", "nunique"),
        mae_mean=("mae", "mean"),
        mae_std=("mae", "std"),
        rmse_mean=("rmse", "mean"),
    ).reset_index().to_csv(out / "seed_summary.csv", index=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("phase", choices=["init", "neural", "baselines", "score"])
    p.add_argument(
        "--candidate",
        type=Path,
        default=ROOT / "artifacts/local/pc-exploratory-20261030",
    )
    p.add_argument("--config", type=Path, default=ROOT / "configs/pc_rerun.json")
    args = p.parse_args()
    config, training, manifest, df, out, identity = context(args.candidate, args.config)
    if args.phase == "init":
        print(
            json.dumps(
                {
                    "neural_forecasts": 48,
                    "baseline_forecasts": 8,
                    "evidence_scope": "exploratory_only",
                    "main_deadline_unix": identity["main_deadline_unix"],
                }
            )
        )
        return
    os.environ["VN30_DEADLINE_UNIX"] = str(identity["main_deadline_unix"])
    os.environ["MPLCONFIGDIR"] = str(ROOT / ".cache/matplotlib")
    lock = (
        ROOT
        / ".cache"
        / (
            "vn30-gpu.lock"
            if args.phase == "neural"
            else f"candidate-{args.phase}.lock"
        )
    )
    lock.parent.mkdir(exist_ok=True)
    with lock.open("x") as f:
        json.dump({"pid": os.getpid(), "output": str(out), "phase": args.phase}, f)
    state_path = out / (args.phase + "-state.json")
    state = (
        json.loads(state_path.read_text())
        if state_path.exists()
        else {"evidence_scope": "exploratory_only", "jobs": {}}
    )

    def job(key, action):
        check_deadline(identity)
        state["jobs"][key] = {"status": "running", "started_unix": time.time()}
        atomic_json(state_path, state)
        print(key, flush=True)
        action()
        state["jobs"][key].update(status="complete", ended_unix=time.time())
        atomic_json(state_path, state)

    try:
        if args.phase == "neural":
            import torch

            torch.set_num_threads(4)
            for seed in config["seeds"]:
                for model in config["models"]:
                    for split in ("validation", "test"):
                        for ft in (False, True):
                            job(
                                f"{model}-s{seed}-{'ft' if ft else 'zs'}-{split}",
                                lambda model=model, split=split, seed=seed, ft=ft: (
                                    run_forecast(
                                        args.candidate,
                                        training,
                                        config,
                                        manifest,
                                        df,
                                        out,
                                        identity,
                                        model,
                                        split,
                                        seed,
                                        ft,
                                    )
                                ),
                            )
        elif args.phase == "baselines":
            for model in ("naive", "ridge", "ets", "arima"):
                locked = None
                if model != "naive":
                    job(
                        "tune-" + model,
                        lambda model=model: tune(
                            config, manifest, df, out, identity, model
                        ),
                    )
                    locked = read_lock(out, model, identity)
                for split in ("validation", "test"):
                    job(
                        model + "-" + split,
                        lambda model=model, split=split, locked=locked: run_forecast(
                            args.candidate,
                            training,
                            config,
                            manifest,
                            df,
                            out,
                            identity,
                            model,
                            split,
                            42,
                            locked=locked,
                        ),
                    )
        else:
            job(
                "score-all-seeds",
                lambda: score_all(
                    args.candidate, training, config, manifest, df, out, identity
                ),
            )
    except Exception as exc:
        for entry in state["jobs"].values():
            if entry["status"] == "running":
                entry.update(
                    status="interrupted", error=type(exc).__name__ + ": " + str(exc)
                )
        atomic_json(state_path, state)
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

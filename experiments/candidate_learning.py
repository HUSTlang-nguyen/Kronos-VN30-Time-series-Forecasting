"""Candidate Q3: nested data budgets and random-predictor controls, never primary evidence.

This independent orchestration entry point records its own hash, as well as the
frozen src/scripts identity. It does not edit code used by live main forecasts.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from research_protocol import (
    atomic_json,
    budget_origins,
    file_hash,
    source_identity,
    validate_coverage,
)
from forecast_vn30 import forecast, score, report
from evaluate_candidate import context, verify_metrics


def jobs(config):
    result = []
    for seed in config["seeds"]:
        for model in ("kronos-small", "chronos2"):
            for budget in config["data_budgets"]:
                for initialization in ("pretrained", "random"):
                    result.append(
                        {
                            "model": model,
                            "seed": seed,
                            "budget": budget,
                            "initialization": initialization,
                        }
                    )
    return result


def winning_trial(trials):
    if not trials:
        raise ValueError("No random-LR candidate achieved a valid validation result")
    if len({r["learning_rate"] for r in trials}) != len(trials) or any(
        not math.isfinite(r["validation_loss"]) for r in trials
    ):
        raise ValueError("Ambiguous or non-finite random-LR trials")
    return min(trials, key=lambda r: r["validation_loss"])


def verify_checkpoint(path, task, lr, config, manifest, permitted_sources):
    trained = json.loads((path / "training.json").read_text())
    expected = {
        "evidence_scope": "exploratory_only",
        "base_model": task["model"],
        "seed": task["seed"],
        "data_budget": task["budget"],
        "initialization": task["initialization"],
        "learning_rate": lr,
        "epochs": config["epochs"],
        "device": config["device"],
        "dataset_sha256": manifest["sha256"],
        "boundaries": manifest["boundaries"],
        "context": manifest["context"],
        "horizon": manifest["horizon"],
        "origins": {
            "train": len(budget_origins(manifest, task["budget"])),
            "validation": len(manifest["origins"]["validation"]),
        },
        "manifest_sha256": config["candidate_manifest_sha256"],
        "normalization": "context_only",
        "effective_batch": 16,
        "test_used_for_training_or_selection": False,
    }
    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_bytes()
    )
    from research_protocol import MODELS

    model_key, token_key, _ = MODELS[task["model"]]
    expected.update(
        base_revision=provenance["models"][model_key]["repository_revision"],
        tokenizer=token_key or "not_applicable",
        tokenizer_revision=provenance["tokenizers"][token_key]["repository_revision"]
        if token_key
        else None,
    )
    if token_key:
        expected["teacher_forcing_causal_validation"] = True
    if (
        any(trained.get(k) != v for k, v in expected.items())
        or trained["source_identity"] not in permitted_sources
    ):
        raise ValueError("Candidate learning checkpoint protocol differs")
    # The frozen adapter independently checks variant/tokenizer/dataset and all
    # weight checksums before inference. Check them now before selecting a trial.
    base = (path / trained["checkpoint_directory"]).resolve()
    if (
        not base.is_relative_to(path.resolve())
        or "model.safetensors" not in trained["checkpoint_files"]
    ):
        raise ValueError("Invalid learning checkpoint path")
    for name, sha in trained["checkpoint_files"].items():
        file = (base / name).resolve()
        if not file.is_relative_to(base) or file_hash(file) != sha:
            raise ValueError("Learning checkpoint checksum differs")
    return trained


def train_one(path, task, lr, candidate, config, manifest, sources, env):
    if not (path / "training.json").exists():
        command = [
            sys.executable,
            "scripts/finetune_vn30.py",
            "--manifest",
            str(candidate / "candidate.json"),
            "--model",
            task["model"],
            "--seed",
            str(task["seed"]),
            "--initialization",
            task["initialization"],
            "--learning-rate",
            str(lr),
            "--epochs",
            str(config["epochs"]),
            "--device",
            config["device"],
            "--output",
            str(path),
            "--exploratory",
        ]
        if task["budget"] is not None:
            command.extend(["--data-budget", str(task["budget"])])
        if (path / "last.pt").exists():
            command.append("--resume")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.with_suffix(".log").open("a", encoding="utf-8") as log:
            subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
    return verify_checkpoint(path, task, lr, config, manifest, sources)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--candidate",
        type=Path,
        default=ROOT / "artifacts/local/pc-exploratory-20261030",
    )
    p.add_argument("--config", type=Path, default=ROOT / "configs/pc_rerun.json")
    p.add_argument("--wait-for-gpu", action="store_true")
    args = p.parse_args()
    config, training, manifest, df, main_out, evaluation_identity = context(
        args.candidate, args.config
    )
    config = {
        **config,
        "candidate_manifest_sha256": evaluation_identity["manifest_sha256"],
    }
    out = args.candidate / "learning"
    out.mkdir(parents=True, exist_ok=True)
    deadline = min(
        training["deadline_unix"],
        training["original_started_unix"] + config["stage_hours"]["learning"] * 3600,
    )
    identity = {
        "evidence_scope": "exploratory_only",
        "dataset_accepted": False,
        "orchestrator_sha256": file_hash(Path(__file__), normalized=True),
        "orchestrator_hash_policy": "sha256_normalized_lf",
        "source_identity": source_identity(),
        "training_identity_sha256": file_hash(args.candidate / "identity.json"),
        "manifest_sha256": training["manifest_sha256"],
        "config_sha256": file_hash(args.config),
        "original_deadline_unix": training["deadline_unix"],
        "stage_deadline_unix": deadline,
        "jobs": jobs(config),
        "random_lr_grid": config["random_learning_rates"],
        "selection": "validation only; reuse exact winning trial checkpoint, no retraining",
    }
    identity_path = out / "identity.json"
    if identity_path.exists() and json.loads(identity_path.read_text()) != identity:
        raise ValueError("Candidate learning identity changed")
    if not identity_path.exists():
        atomic_json(identity_path, identity)

    def remaining():
        if time.time() >= deadline:
            raise TimeoutError("Original learning-stage budget exhausted")

    lock = ROOT / ".cache/vn30-gpu.lock"
    atomic_json(
        out / "queue.json",
        {
            "pid": os.getpid(),
            "status": "waiting_for_sequential_gpu_slot",
            "evidence_scope": "exploratory_only",
            "stage_deadline_unix": deadline,
            "orchestrator_sha256": identity["orchestrator_sha256"],
            "planned_comparisons": len(jobs(config)),
        },
    )
    while True:
        remaining()
        try:
            with lock.open("x") as f:
                json.dump(
                    {"pid": os.getpid(), "output": str(out), "phase": "learning"}, f
                )
            break
        except FileExistsError:
            if not args.wait_for_gpu:
                raise
            print("Waiting for the sequential GPU slot", flush=True)
            time.sleep(20)
    atomic_json(
        out / "queue.json",
        {
            "pid": os.getpid(),
            "status": "running",
            "evidence_scope": "exploratory_only",
            "stage_deadline_unix": deadline,
            "orchestrator_sha256": identity["orchestrator_sha256"],
            "planned_comparisons": len(jobs(config)),
        },
    )
    import torch

    torch.set_num_threads(4)
    env = dict(
        os.environ,
        VN30_DEADLINE_UNIX=str(deadline),
        MPLCONFIGDIR=str(ROOT / ".cache/matplotlib"),
    )
    os.environ.update({k: env[k] for k in ("VN30_DEADLINE_UNIX", "MPLCONFIGDIR")})
    state_path = out / "state.json"
    state = (
        json.loads(state_path.read_text())
        if state_path.exists()
        else {"evidence_scope": "exploratory_only", "jobs": {}}
    )
    sources = [training["source_identity"], identity["source_identity"]]
    try:
        for task in jobs(config):
            remaining()
            model, seed, budget, initialization = (
                task[k] for k in ("model", "seed", "budget", "initialization")
            )
            key = f"{model}-s{seed}-n{budget or 'full'}-{initialization}"
            state["jobs"][key] = {"status": "running", "task": task}
            atomic_json(state_path, state)
            print(key, flush=True)
            target = out / "checkpoints" / key
            if initialization == "pretrained" and budget is None:
                target = args.candidate / "checkpoints" / f"train-{model}-s{seed}"
                trained = verify_checkpoint(
                    target, task, config["learning_rate"], config, manifest, sources
                )
                choice = {
                    "checkpoint": target.relative_to(ROOT).as_posix(),
                    "learning_rate": config["learning_rate"],
                    "reused_main_full_budget": True,
                }
            elif initialization == "pretrained":
                trained = train_one(
                    target,
                    task,
                    config["learning_rate"],
                    args.candidate,
                    config,
                    manifest,
                    sources,
                    env,
                )
                choice = {
                    "checkpoint": target.relative_to(ROOT).as_posix(),
                    "learning_rate": config["learning_rate"],
                }
            else:
                trials = []
                for lr in config["random_learning_rates"]:
                    remaining()
                    trial_path = out / "lr-trials" / key / str(lr)
                    try:
                        trial = train_one(
                            trial_path,
                            task,
                            lr,
                            args.candidate,
                            config,
                            manifest,
                            sources,
                            env,
                        )
                        trials.append(
                            {
                                "status": "pass",
                                "learning_rate": lr,
                                "validation_loss": trial["best_validation_loss"],
                                "checkpoint": trial_path.relative_to(ROOT).as_posix(),
                                "training_sha256": file_hash(
                                    trial_path / "training.json"
                                ),
                            }
                        )
                    except subprocess.CalledProcessError as exc:
                        trials.append(
                            {
                                "status": "failed",
                                "learning_rate": lr,
                                "checkpoint": trial_path.relative_to(ROOT).as_posix(),
                                "error": str(exc),
                                "returncode": exc.returncode,
                            }
                        )
                    atomic_json(
                        out / "tuning" / (key + "-trials.json"),
                        {"test_used": False, "trials": trials},
                    )
                choice = {
                    **winning_trial([r for r in trials if r["status"] == "pass"]),
                    "test_used": False,
                    "reused_winning_trial": True,
                }
                target = ROOT / choice["checkpoint"]
                trained = verify_checkpoint(
                    target, task, choice["learning_rate"], config, manifest, sources
                )
            receipt = out / "tuning" / (key + ".json")
            if receipt.exists() and json.loads(receipt.read_text()) != choice:
                raise ValueError("Learning checkpoint selection changed")
            if not receipt.exists():
                atomic_json(receipt, choice)
            for split in ("validation", "test"):
                remaining()
                dest = out / "forecasts" / (key + "-" + split + ".csv")
                dest.parent.mkdir(exist_ok=True)
                if not dest.exists():
                    forecast(
                        df,
                        manifest,
                        model + "-ft",
                        split,
                        config["device"],
                        seed,
                        dest,
                        None,
                        target,
                    )
                meta = json.loads(dest.with_suffix(".json").read_text())
                expected = {
                    "evidence_scope": "exploratory_only",
                    "model": model + "-ft",
                    "dataset_sha256": manifest["sha256"],
                    "split": split,
                    "seed": seed,
                    "source_identity": identity["source_identity"],
                    "limited": False,
                    "forecast_csv_sha256": file_hash(dest),
                    "checkpoint": str(target),
                    "revision": "finetuned:"
                    + trained["checkpoint_files"]["model.safetensors"],
                    "checkpoint_choice": "best-trained",
                }
                if any(meta.get(k) != v for k, v in expected.items()):
                    raise ValueError("Learning forecast protocol differs")
                validate_coverage(pd.read_csv(dest), manifest, split)
                naive = main_out / "forecasts" / f"naive-s42-zs-{split}.csv"
                baseline_meta = json.loads(naive.with_suffix(".json").read_text())
                if (
                    baseline_meta["forecast_csv_sha256"] != file_hash(naive)
                    or baseline_meta["evidence_scope"] != "exploratory_only"
                    or baseline_meta["dataset_sha256"] != manifest["sha256"]
                ):
                    raise ValueError("Learning baseline identity differs")
                validate_coverage(pd.read_csv(naive), manifest, split)
                evaluation = out / "scores" / key / split
                inputs = {
                    p.relative_to(ROOT).as_posix(): file_hash(p)
                    for file in (naive, dest)
                    for p in (file, file.with_suffix(".json"))
                }
                if not evaluation.exists():
                    score(df, manifest, [naive, dest], evaluation)
                    verify_metrics(evaluation)
                    report(evaluation)
                    summary = evaluation / "summary.md"
                    summary.write_text(
                        "**THĂM DÒ — dataset unverified; chưa phải kết luận Q3 chính.**\n\n"
                        + summary.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                    atomic_json(
                        evaluation / "verified.json",
                        {
                            "evidence_scope": "exploratory_only",
                            "source_forecasts": inputs,
                            "outputs": {
                                p.relative_to(evaluation).as_posix(): file_hash(p)
                                for p in evaluation.rglob("*")
                                if p.is_file()
                            },
                        },
                    )
                else:
                    verified = json.loads((evaluation / "verified.json").read_text())
                    if verified["source_forecasts"] != inputs or any(
                        file_hash(evaluation / name) != sha
                        for name, sha in verified["outputs"].items()
                    ):
                        raise ValueError("Learning score cache differs")
                    verify_metrics(evaluation)
            state["jobs"][key].update(
                status="complete",
                checkpoint=target.relative_to(ROOT).as_posix(),
                training_sha256=file_hash(target / "training.json"),
                train_windows=trained["origins"]["train"],
                best_epoch=trained["best_epoch"],
                selection=choice,
            )
            atomic_json(state_path, state)
        rows = []
        for key, entry in state["jobs"].items():
            if entry["status"] != "complete":
                continue
            for split in ("validation", "test"):
                table = pd.read_csv(out / "scores" / key / split / "scores.csv")
                for k, v in entry["task"].items():
                    if k != "model":
                        table[k] = v
                table["train_windows"] = entry["train_windows"]
                table["group"] = key
                rows.append(table)
        pd.concat(rows, ignore_index=True).to_csv(out / "scores_all.csv", index=False)
        learning_curves(out, manifest)
        print("Candidate learning complete; dataset remains unverified.", flush=True)
        atomic_json(
            out / "queue.json",
            {
                "status": "complete",
                "evidence_scope": "exploratory_only",
                "orchestrator_sha256": identity["orchestrator_sha256"],
                "completed_comparisons": len(state["jobs"]),
            },
        )
    except Exception as exc:
        for entry in state["jobs"].values():
            if entry["status"] == "running":
                entry.update(
                    status="interrupted", error=type(exc).__name__ + ": " + str(exc)
                )
        atomic_json(state_path, state)
        atomic_json(
            out / "queue.json",
            {
                "status": "interrupted",
                "evidence_scope": "exploratory_only",
                "error": type(exc).__name__ + ": " + str(exc),
                "orchestrator_sha256": identity["orchestrator_sha256"],
            },
        )
        raise
    finally:
        lock.unlink(missing_ok=True)


def learning_curves(out, manifest):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    table = pd.read_csv(out / "scores_all.csv")
    table = table.loc[
        (table.split == "test")
        & (table.target.isin(["open", "close"]))
        & table.model.str.endswith("-ft")
    ].copy()
    table["train_rows"] = pd.to_numeric(table.budget).fillna(
        manifest["boundaries"]["train"]["rows"]
    )
    summary = (
        table.groupby(["model", "initialization", "train_rows", "target", "horizon"])
        .agg(
            seeds=("seed", "nunique"),
            mae=("mae", "mean"),
            mae_std=("mae", "std"),
            rmse=("rmse", "mean"),
        )
        .reset_index()
    )
    if not (summary.seeds == 3).all():
        raise ValueError("Learning curve lacks one of the planned seeds")
    summary.to_csv(out / "learning_curve.csv", index=False)
    for model in summary.model.unique():
        fig, axes = plt.subplots(2, 3, figsize=(12, 6), layout="constrained")
        for row, target in enumerate(["open", "close"]):
            for column, horizon in enumerate([1, 5, 20]):
                ax = axes[row, column]
                for initialization in ["pretrained", "random"]:
                    part = summary.loc[
                        (summary.model == model)
                        & (summary.target == target)
                        & (summary.horizon == horizon)
                        & (summary.initialization == initialization)
                    ].sort_values("train_rows")
                    ax.errorbar(
                        part.train_rows,
                        part.mae,
                        yerr=part.mae_std,
                        marker="o",
                        capsize=3,
                        label=initialization,
                    )
                ax.set_title(f"{target}, h={horizon}")
                ax.set_xlabel("Train sessions")
                ax.set_ylabel("MAE (index points)")
                ax.grid(alpha=0.2)
                ax.legend()
        fig.suptitle(
            model
            + " | exploratory learning curve; dataset unverified\nError bars show SD across seeds, not independent market samples"
        )
        fig.savefig(out / ("learning_curve_" + model + ".png"), dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    main()

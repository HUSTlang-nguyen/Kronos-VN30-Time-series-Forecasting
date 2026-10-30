"""Queue candidate Q2 ablation and Q4 folds after Q3, under the original budget."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "experiments")]
from research_protocol import (
    atomic_json,
    expanding_folds,
    file_hash,
    source_identity,
    validate_coverage,
)
from evaluate_candidate import context, verify_metrics, validate_forecast
from candidate_learning import train_one
from candidate_ablation import run_candidate_ablation
from forecast_vn30 import forecast, score, report
from research_statistics import diagnostics
from vn30_forecast import check_manifest


def folds(df, manifest):
    return expanding_folds(df, manifest["sha256"], manifest["dataset_info"])


def verify_outputs(folder, manifest, identity):
    result = json.loads((folder / "result.json").read_text())
    if result.get("evidence_scope") != "exploratory_only" or not result.get(
        "initial_backbone_equal"
    ):
        raise ValueError(
            "Candidate ablation is missing its paired initialization proof"
        )
    previous = folder / "verified.json"
    if previous.exists():
        verified = json.loads(previous.read_text())
        if any(
            not (folder / name).is_file() or file_hash(folder / name) != sha
            for name, sha in verified["outputs"].items()
        ):
            raise ValueError("Previously verified ablation outputs changed")
        for split in ("validation", "test"):
            verify_metrics(folder / ("evaluation-" + split))
        return
    inputs = {}
    for arm in ("continuous", "quantized"):
        for split in ("validation", "test"):
            path = folder / (arm + "-" + split + ".csv")
            meta = json.loads(path.with_suffix(".json").read_text())
            if (
                meta.get("evidence_scope") != "exploratory_only"
                or meta.get("forecast_csv_sha256") != file_hash(path)
                or meta.get("source_identity") != identity["source_identity"]
            ):
                raise ValueError("Ablation forecast provenance differs")
            validate_coverage(pd.read_csv(path), manifest, split)
            inputs[path.relative_to(ROOT).as_posix()] = file_hash(path)
    for split in ("validation", "test"):
        verify_metrics(folder / ("evaluation-" + split))
        report(folder / ("evaluation-" + split))
    atomic_json(
        folder / "verified.json",
        {
            "evidence_scope": "exploratory_only",
            "independent_metric_recomputation": "pass",
            "paired_initialization": "pass",
            "source_forecasts": inputs,
            "outputs": {
                p.relative_to(folder).as_posix(): file_hash(p)
                for p in folder.rglob("*")
                if p.is_file()
                and p.suffix not in (".pt", ".tmp")
                and p.name != "verified.json"
            },
        },
    )


def run_fold(candidate, out, name, manifest, df, config, training, identity, env):
    folder = out / "folds" / name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "candidate.json"
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError("Candidate expanding fold changed")
    if not path.exists():
        atomic_json(path, manifest)
    config = {**config, "candidate_manifest_sha256": file_hash(path)}
    seed = 42
    paths = {s: [] for s in ("validation", "test")}
    for split in paths:
        target = folder / "forecasts" / ("naive-" + split + ".csv")
        target.parent.mkdir(exist_ok=True)
        if not target.exists():
            forecast(df, manifest, "naive", split, "cpu", seed, target, None)
        validate_forecast(target, manifest, df, identity, "naive", split, seed, config)
        paths[split].append(target)
    for model in config["models"]:
        check_time(identity)
        task = {
            "model": model,
            "seed": seed,
            "budget": None,
            "initialization": "pretrained",
        }
        ckpt = folder / "checkpoints" / model
        receipt = train_one(
            ckpt,
            task,
            config["learning_rate"],
            folder,
            config,
            manifest,
            [identity["source_identity"]],
            env,
        )
        for split in paths:
            for ft in (False, True):
                check_time(identity)
                target = (
                    folder
                    / "forecasts"
                    / (model + ("-ft" if ft else "") + "-" + split + ".csv")
                )
                if not target.exists():
                    forecast(
                        df,
                        manifest,
                        model + ("-ft" if ft else ""),
                        split,
                        config["device"],
                        seed,
                        target,
                        None,
                        ckpt if ft else None,
                    )
                paths[split].append(target)
                meta = json.loads(target.with_suffix(".json").read_text())
                expected = {
                    "evidence_scope": "exploratory_only",
                    "dataset_sha256": manifest["sha256"],
                    "source_identity": identity["source_identity"],
                    "seed": seed,
                    "split": split,
                    "model": model + ("-ft" if ft else ""),
                    "limited": False,
                    "forecast_csv_sha256": file_hash(target),
                }
                if ft:
                    expected.update(
                        checkpoint=str(ckpt),
                        revision="finetuned:"
                        + receipt["checkpoint_files"]["model.safetensors"],
                    )
                if any(meta.get(k) != v for k, v in expected.items()):
                    raise ValueError("Candidate fold forecast differs")
                validate_coverage(pd.read_csv(target), manifest, split)
                validate_forecast(
                    target,
                    manifest,
                    df,
                    identity,
                    model + ("-ft" if ft else ""),
                    split,
                    seed,
                    config,
                    ckpt if ft else None,
                    receipt if ft else None,
                )
    for split, files in paths.items():
        for target in files:
            validate_coverage(pd.read_csv(target), manifest, split)
        target = folder / ("evaluation-" + split)
        inputs = {
            p.relative_to(ROOT).as_posix(): file_hash(p)
            for file in files
            for p in (file, file.with_suffix(".json"))
        }
        if not target.exists():
            score(df, manifest, files, target)
            details, _ = verify_metrics(target)
            report(target)
            if split == "test":
                diagnostics(df, manifest, details, target)
            summary = target / "summary.md"
            summary.write_text(
                "**THĂM DÒ — expanding fold, dataset unverified.**\n\n"
                + summary.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            atomic_json(
                target / "verified.json",
                {
                    "evidence_scope": "exploratory_only",
                    "source_forecasts": inputs,
                    "independent_recomputation": "pass",
                    "outputs": {
                        p.relative_to(target).as_posix(): file_hash(p)
                        for p in target.rglob("*")
                        if p.is_file()
                    },
                },
            )
        else:
            verified = json.loads((target / "verified.json").read_text())
            if verified["source_forecasts"] != inputs or any(
                file_hash(target / key) != sha
                for key, sha in verified["outputs"].items()
            ):
                raise ValueError("Fold score cache differs")
            verify_metrics(target)


def check_time(identity):
    if time.time() >= identity["stage_deadline_unix"]:
        raise TimeoutError("Original ablation/fold stage deadline exhausted")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--candidate",
        type=Path,
        default=ROOT / "artifacts/local/pc-exploratory-20261030",
    )
    p.add_argument("--config", type=Path, default=ROOT / "configs/pc_rerun.json")
    p.add_argument("--wait-for-learning", action="store_true")
    args = p.parse_args()
    config, training, manifest, df, main_out, main_identity = context(
        args.candidate, args.config
    )
    out = args.candidate / "followups"
    out.mkdir(parents=True, exist_ok=True)
    identity = {
        "evidence_scope": "exploratory_only",
        "dataset_accepted": False,
        "source_identity": source_identity(),
        "manifest_sha256": file_hash(args.candidate / "candidate.json"),
        "original_deadline_unix": training["deadline_unix"],
        "stage_deadline_unix": min(
            training["deadline_unix"],
            training["original_started_unix"]
            + config["stage_hours"]["ablation"] * 3600,
        ),
        "orchestrators": {
            p.name: file_hash(p, normalized=True)
            for p in (
                Path(__file__),
                Path(__file__).with_name("candidate_ablation.py"),
                Path(__file__).with_name("candidate_learning.py"),
            )
        },
        "specialized_from": {
            "scripts/representation_ablation.py": file_hash(
                ROOT / "scripts/representation_ablation.py", normalized=True
            )
        },
        "ablation_seeds": config["seeds"],
        "folds": folds(df, manifest),
    }
    receipt = out / "identity.json"
    if receipt.exists() and json.loads(receipt.read_text()) != identity:
        raise ValueError("Candidate follow-up identity changed")
    if not receipt.exists():
        atomic_json(receipt, identity)
    atomic_json(
        out / "queue.json",
        {
            "pid": os.getpid(),
            "status": "waiting_for_learning",
            "evidence_scope": "exploratory_only",
            "planned_jobs": 5,
            "stage_deadline_unix": identity["stage_deadline_unix"],
        },
    )
    while True:
        check_time(identity)
        queue = args.candidate / "learning/queue.json"
        status = (
            json.loads(queue.read_text())["status"] if queue.exists() else "missing"
        )
        if status == "complete":
            break
        if status == "interrupted" or not args.wait_for_learning:
            raise RuntimeError("Complete the planned learning phase first")
        print("Waiting for learning phase", flush=True)
        time.sleep(20)
    lock = ROOT / ".cache/vn30-gpu.lock"
    while True:
        check_time(identity)
        try:
            with lock.open("x") as f:
                json.dump(
                    {
                        "pid": os.getpid(),
                        "phase": "candidate-followups",
                        "output": str(out),
                    },
                    f,
                )
            break
        except FileExistsError:
            time.sleep(5)
    atomic_json(
        out / "queue.json",
        {
            "pid": os.getpid(),
            "status": "running",
            "evidence_scope": "exploratory_only",
            "planned_jobs": 5,
        },
    )
    import torch

    torch.set_num_threads(4)
    env = dict(
        os.environ,
        VN30_DEADLINE_UNIX=str(identity["stage_deadline_unix"]),
        MPLCONFIGDIR=str(ROOT / ".cache/matplotlib"),
    )
    os.environ.update({k: env[k] for k in ("VN30_DEADLINE_UNIX", "MPLCONFIGDIR")})
    state_path = out / "state.json"
    state = (
        json.loads(state_path.read_text())
        if state_path.exists()
        else {"evidence_scope": "exploratory_only", "jobs": {}}
    )
    primary = out / "primary.json"
    if not primary.exists():
        atomic_json(primary, manifest)
    elif json.loads(primary.read_text()) != manifest:
        raise ValueError("Ablation manifest changed")

    def job(key, action):
        check_time(identity)
        state["jobs"][key] = {"status": "running"}
        atomic_json(state_path, state)
        print(key, flush=True)
        action()
        state["jobs"][key] = {"status": "complete"}
        atomic_json(state_path, state)

    try:
        for seed in config["seeds"]:
            job(
                f"ablation-s{seed}",
                lambda seed=seed: (
                    run_candidate_ablation(config, out, seed),
                    verify_outputs(
                        out / "ablation" / f"representation-s{seed}", manifest, identity
                    ),
                ),
            )
        for name, m in zip(("fold1", "fold2"), identity["folds"]):
            check_manifest(df, manifest["sha256"], m)
            job(
                name,
                lambda name=name, m=m: run_fold(
                    args.candidate, out, name, m, df, config, training, identity, env
                ),
            )
        atomic_json(
            out / "queue.json",
            {
                "status": "complete",
                "evidence_scope": "exploratory_only",
                "completed_jobs": 5,
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
            },
        )
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

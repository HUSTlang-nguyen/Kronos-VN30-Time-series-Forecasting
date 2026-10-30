"""Bounded PC experiment: plan/run/resume/status/report, with no legacy scores."""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_protocol import atomic_json, file_hash, portable_path, source_identity


def refresh_preflight(config, config_path, reason):
    """Revalidate code fixes before research starts, preserving evidence and budget."""
    if not reason or not reason.strip():
        raise ValueError("A recorded reason is required")
    out = portable_path(config["output"]).resolve()
    if not out.is_relative_to(ROOT.resolve()):
        raise ValueError("Preflight refresh must stay inside the workspace")
    state_path = out / "state.json"
    if (out / "coordinator.lock").exists():
        raise RuntimeError("A coordinator lock exists; do not refresh a live run")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    identity = {
        "config_sha256": file_hash(config_path),
        "source_identity": source_identity(),
        "provenance_sha256": file_hash(
            ROOT / "data/manifests/checkpoint_provenance.yaml"
        ),
    }
    if any(
        state["identity"][key] != identity[key]
        for key in ("config_sha256", "provenance_sha256")
    ):
        raise ValueError("Cannot refresh a changed dataset/config/provenance")
    allowed = {"recover", "independent", "audit", "weights", "bootstrap"}
    for key, entry in state["tasks"].items():
        if entry["status"] in ("running", "interrupted"):
            raise ValueError("Resolve interrupted/live jobs before refresh")
        if entry["status"] == "complete":
            if key not in allowed:
                raise ValueError(
                    "Research/protocol work has already completed; a preflight refresh is unsafe"
                )
            if any(
                not portable_path(p).is_file() or file_hash(portable_path(p)) != h
                for p, h in entry["evidence"].items()
            ):
                raise ValueError("Previous preflight evidence changed")
    for folder in ("checkpoints", "forecasts", "benchmarks", "ablation", "lr-trials"):
        if (out / folder).exists() and any(
            p.is_file() for p in (out / folder).rglob("*")
        ):
            raise ValueError(
                "Research artifacts already exist; preflight-only refresh refused"
            )
    archive = (
        out
        / "preflight_history"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + uuid.uuid4().hex[:8]
        )
    )
    archive.mkdir(parents=True, exist_ok=False)
    atomic_json(archive / "state.json", state)
    for name in (
        "audit",
        "logs",
        "report.md",
        "report_sources.json",
        "remaining.json",
        "matrix.json",
    ):
        old = out / name
        destination = archive / name
        if old.exists():
            if not old.resolve().is_relative_to(
                out
            ) or not destination.resolve().is_relative_to(out):
                raise ValueError("Unsafe archive move")
            old.rename(destination)
    history = {
        "reason": reason.strip(),
        "previous_identity": state["identity"],
        "new_identity": identity,
        "previous_state_sha256": file_hash(archive / "state.json"),
        "original_started_unix": state["started_unix"],
        "original_deadline_unix": state["deadline_unix"],
        "archive": archive.relative_to(ROOT).as_posix(),
    }
    atomic_json(archive / "refresh.json", history)
    state["identity"] = identity
    state["tasks"] = {}
    state["status"] = "preflight_refresh_pending"
    state.setdefault("preflight_refreshes", []).append(history)
    atomic_json(state_path, state)
    return state


def matrix(config):
    """Dependencies are explicit so an incomplete group never becomes a table."""
    tasks = []

    def add(key, kind, stage, deps=(), **kwargs):
        tasks.append(
            dict(id=key, kind=kind, stage=stage, dependencies=list(deps), **kwargs)
        )

    add("recover", "recover", "setup")
    add("independent", "fetch", "setup")
    add("audit", "audit", "setup", ["recover", "independent"])
    add("prepare", "prepare", "setup", ["audit"])
    add("weights", "weights", "setup")
    add("bootstrap", "bootstrap", "setup")
    add("protocol", "protocol", "setup", ["prepare", "weights", "bootstrap"])
    for model in config["models"]:
        add("benchmark-" + model, "benchmark", "setup", ["protocol"], model=model)
    add("estimate", "estimate", "setup", ["benchmark-" + m for m in config["models"]])
    for model in ("ridge", "arima", "ets"):
        add("tune-" + model, "tune", "main", ["prepare"], model=model)
    baselines = []
    for split in ("validation", "test"):
        for model in ("naive", "ridge", "arima", "ets"):
            key = f"baseline-{model}-{split}"
            baselines.append(key)
            add(
                key,
                "forecast",
                "main",
                ["tune-" + model] if model != "naive" else ["prepare"],
                model=model,
                split=split,
                seed=42,
                fold="primary",
                budget=None,
                initialization="pretrained",
            )
    for seed in config["seeds"]:
        for model in config["models"]:
            train = f"main-{model}-s{seed}"
            add(
                train,
                "train",
                "main",
                ["estimate"],
                model=model,
                seed=seed,
                budget=None,
                initialization="pretrained",
                fold="primary",
            )
            forecasts = []
            for split in ("validation", "test"):
                for ft in (False, True):
                    key = f"{train}-{'ft' if ft else 'zs'}-{split}"
                    forecasts.append(key)
                    add(
                        key,
                        "forecast",
                        "main",
                        [train] if ft else ["estimate"],
                        model=model + ("-ft" if ft else ""),
                        seed=seed,
                        split=split,
                        checkpoint=train if ft else None,
                        fold="primary",
                        budget=None,
                        initialization="pretrained",
                    )
            add(
                train + "-score",
                "score",
                "main",
                [*forecasts, *baselines],
                forecasts=forecasts + baselines,
                group=train,
            )
    for model in ("kronos-small", "chronos2"):
        for budget in config["data_budgets"]:
            for seed in config["seeds"]:
                for initialization in ("pretrained", "random"):
                    if budget is None and initialization == "pretrained":
                        continue  # reuse main FULL job
                    key = (
                        f"learning-{model}-{budget or 'full'}-{initialization}-s{seed}"
                    )
                    deps = ["estimate"]
                    if initialization == "random":
                        tune = key + "-lr"
                        add(
                            tune,
                            "tune_lr",
                            "learning",
                            deps,
                            model=model,
                            seed=seed,
                            budget=budget,
                        )
                        deps = [tune]
                    add(
                        key,
                        "train",
                        "learning",
                        deps,
                        model=model,
                        seed=seed,
                        budget=budget,
                        initialization=initialization,
                        fold="primary",
                    )
                    forecasts = []
                    for split in ("validation", "test"):
                        f = key + "-" + split
                        forecasts.append(f)
                        add(
                            f,
                            "forecast",
                            "learning",
                            [key],
                            model=model + "-ft",
                            seed=seed,
                            split=split,
                            checkpoint=key,
                            fold="primary",
                            budget=budget,
                            initialization=initialization,
                        )
                    add(
                        key + "-score",
                        "score",
                        "learning",
                        [*forecasts, *baselines],
                        forecasts=forecasts + baselines,
                        group=key,
                    )
    for seed in config["seeds"]:
        add(f"representation-s{seed}", "ablation", "ablation", ["estimate"], seed=seed)
    for fold in ("fold1", "fold2"):
        baseline = []
        for split in ("validation", "test"):
            key = f"{fold}-naive-{split}"
            baseline.append(key)
            add(
                key,
                "forecast",
                "folds",
                ["prepare"],
                model="naive",
                seed=42,
                split=split,
                fold=fold,
                budget=None,
                initialization="pretrained",
            )
        for model in config["models"]:
            key = f"{fold}-{model}"
            add(
                key,
                "train",
                "folds",
                ["estimate"],
                model=model,
                seed=42,
                budget=None,
                initialization="pretrained",
                fold=fold,
            )
            forecasts = []
            for split in ("validation", "test"):
                for ft in (False, True):
                    f = key + f"-{'ft' if ft else 'zs'}-{split}"
                    forecasts.append(f)
                    add(
                        f,
                        "forecast",
                        "folds",
                        [key] if ft else ["estimate"],
                        model=model + ("-ft" if ft else ""),
                        seed=42,
                        split=split,
                        checkpoint=key if ft else None,
                        fold=fold,
                        budget=None,
                        initialization="pretrained",
                    )
            add(
                key + "-score",
                "score",
                "folds",
                [*forecasts, *baseline],
                forecasts=forecasts + baseline,
                group=key,
            )
    return tasks


def command_for(task, config, out):
    """All subprocesses use explicit arguments; never shell command strings."""
    py = sys.executable
    kind = task["kind"]
    manifest = out / (task.get("fold", "primary") + ".json")
    if kind == "recover":
        if (
            portable_path(config["dataset"]).exists()
            and (
                ROOT / ".dvc/cache/files/md5/fe/cae9449c856a16470d552e40f957f8.dir"
            ).exists()
        ):
            return [
                py,
                "scripts/restore_pc_data.py",
                "--receipt",
                str(out / "recovery.json"),
            ]
        executable = portable_path(config["dvc_executable"])
        return [
            str(executable),
            "pull",
            "data/raw.dvc",
            config["dataset"] + ".dvc",
            config["dataset"].replace(".sqlite", ".zip.dvc"),
        ]
    if kind == "fetch":
        if (out / "independent/fetch_status.json").exists():
            return [py, "-c", "import sys; sys.exit(0)"]
        return [
            py,
            "scripts/fetch_audit_sources.py",
            "--output",
            str(out / "independent"),
        ]
    if kind == "weights":
        return [
            py,
            "scripts/verify_checkpoint_provenance.py",
            "--output",
            str(out / "weights.json"),
        ]
    if kind == "bootstrap":
        return [py, "scripts/bootstrap_kronos.py"]
    if kind == "protocol":
        return [
            py,
            "scripts/check_finetune_protocol.py",
            "--manifest",
            str(out / "primary.json"),
            "--all-models",
            "--device",
            config["device"],
            "--output",
            str(out / "protocol.json"),
        ]
    if kind == "train":
        args = [
            py,
            "scripts/finetune_vn30.py",
            "--manifest",
            str(manifest),
            "--model",
            task["model"],
            "--output",
            str(out / "checkpoints" / task["id"]),
            "--seed",
            str(task["seed"]),
            "--epochs",
            str(config["epochs"]),
            "--device",
            config["device"],
            "--initialization",
            task["initialization"],
            "--learning-rate",
            str(config["learning_rate"]),
        ]
        if task["initialization"] == "random":
            rate = json.loads((out / "tuning" / (task["id"] + "-lr.json")).read_text())[
                "learning_rate"
            ]
            args[-1] = str(rate)
        if task["budget"] is not None:
            args.extend(["--data-budget", str(task["budget"])])
        if (out / "checkpoints" / task["id"] / "last.pt").exists():
            args.append("--resume")
        return args
    if kind == "forecast":
        model = task["model"]
        args = [
            py,
            "scripts/forecast_vn30.py",
            "run",
            "--manifest",
            str(manifest),
            "--model",
            model,
            "--split",
            task["split"],
            "--seed",
            str(task["seed"]),
            "--device",
            config["device"]
            if model not in ("naive", "ridge", "arima", "ets")
            else "cpu",
            "--output",
            str(out / "forecasts" / (task["id"] + ".csv")),
        ]
        if task.get("checkpoint"):
            args.extend(["--checkpoint", str(out / "checkpoints" / task["checkpoint"])])
        if model in ("ridge", "arima", "ets"):
            args.extend(["--model-config", str(out / "tuning" / (model + ".json"))])
        return args
    return [
        py,
        "scripts/experiment_tasks.py",
        "--config",
        str(out / "config.json"),
        "--task",
        json.dumps(task),
    ]


def evidence(task, out):
    kind = task["kind"]
    key = task["id"]
    if kind == "forecast":
        return [out / "forecasts" / (key + suffix) for suffix in (".csv", ".json")]
    if kind == "train":
        return [
            out / "checkpoints" / key / "training.json",
            out / "checkpoints" / key / "selection.json",
        ]
    mapping = {
        "recover": [
            ROOT / "data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite",
            ROOT / "data/share/vn30_vndirect_20261001T151513588605Z_candidate.zip",
        ],
        "bootstrap": [ROOT / ".vendor/Kronos/.git/HEAD"],
        "fetch": [out / "independent/fetch_status.json"],
        "audit": [out / "audit/audit.json"],
        "prepare": [out / "primary.json", out / "fold1.json", out / "fold2.json"],
        "weights": [out / "weights.json"],
        "protocol": [out / "protocol.json"],
        "benchmark": [out / "benchmarks" / (task.get("model", "") + ".json")],
        "estimate": [out / "estimate.json"],
        "tune": [out / "tuning" / (task.get("model", "") + ".json")],
        "tune_lr": [out / "tuning" / (key + ".json")],
        "score": [out / "evaluation" / task.get("group", "") / "test/scores.csv"],
        "ablation": [out / "ablation" / key / "result.json"],
    }
    return mapping[kind]


def run(config, config_path, resume=False):
    out = portable_path(config["output"])
    state_path = out / "state.json"
    identity = {
        "config_sha256": file_hash(config_path),
        "source_identity": source_identity(),
        "provenance_sha256": file_hash(
            ROOT / "data/manifests/checkpoint_provenance.yaml"
        ),
    }
    if resume:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state["identity"] != identity:
            raise ValueError("Cannot resume changed code, provenance or config")
        for entry in state["tasks"].values():
            if entry["status"] == "complete":
                if any(
                    not portable_path(p).exists() or file_hash(portable_path(p)) != h
                    for p, h in entry["evidence"].items()
                ):
                    raise ValueError("Completed task evidence changed")
    else:
        if state_path.exists():
            raise FileExistsError("Use resume; do not reset the 24-hour clock")
        out.mkdir(parents=True, exist_ok=True)
        started = time.time()
        state = {
            "identity": identity,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "started_unix": started,
            "deadline_unix": started + config["hours"] * 3600,
            "status": "running",
            "tasks": {},
        }
        atomic_json(out / "config.json", config)
    tasks = matrix(config)
    atomic_json(out / "matrix.json", tasks)
    atomic_json(state_path, state)
    (out / "logs").mkdir(exist_ok=True)
    # Prevent two coordinators from training on the same GPU/output.
    lock = out / "coordinator.lock"
    try:
        handle = lock.open("x")
        handle.write(str(os.getpid()))
        handle.close()
    except FileExistsError:
        raise RuntimeError(
            "Coordinator lock exists; verify its PID before removing a stale lock"
        )
    try:
        for task in tasks:
            key = task["id"]
            if state["tasks"].get(key, {}).get("status") == "complete":
                continue
            deps = [
                d
                for d in task["dependencies"]
                if state["tasks"].get(d, {}).get("status") != "complete"
            ]
            if deps:
                state["tasks"][key] = {"status": "blocked", "dependencies": deps}
                continue
            if task["kind"] == "prepare":
                audit = json.loads(
                    (out / "audit/audit.json").read_text(encoding="utf-8")
                )
                if audit["status"] != "accepted_provider_scope":
                    state["tasks"][key] = {
                        "status": "blocked",
                        "reason": "dataset_unverified",
                        "audit": "audit/audit.json",
                    }
                    atomic_json(state_path, state)
                    continue
            stage_deadline = min(
                state["deadline_unix"],
                state["started_unix"] + config["stage_hours"][task["stage"]] * 3600,
            )
            if time.time() >= stage_deadline:
                state["tasks"][key] = {"status": "budget_exhausted"}
                continue
            state["tasks"][key] = {"status": "running", "started_unix": time.time()}
            atomic_json(state_path, state)
            env = {
                **os.environ,
                "VN30_DEADLINE_UNIX": str(stage_deadline),
                "PYTHONUNBUFFERED": "1",
                "MPLCONFIGDIR": str(ROOT / ".cache/matplotlib"),
            }
            try:
                command = command_for(task, config, out)
            except Exception as exc:
                state["tasks"][key].update(
                    status="failed", error=type(exc).__name__ + ": " + str(exc)
                )
                atomic_json(state_path, state)
                continue
            print(key, flush=True)
            with (out / "logs" / (key + ".log")).open("a", encoding="utf-8") as log:
                try:
                    process = subprocess.Popen(
                        command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT
                    )
                except OSError as exc:
                    state["tasks"][key].update(status="failed", error=str(exc))
                    atomic_json(state_path, state)
                    continue
                try:
                    code = process.wait(timeout=max(0.1, stage_deadline - time.time()))
                except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
                    if os.name == "nt":
                        subprocess.run(
                            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                            capture_output=True,
                        )
                    else:
                        process.kill()
                    process.wait()
                    code = 124
                    if isinstance(exc, KeyboardInterrupt):
                        state["tasks"][key].update(status="interrupted")
                        atomic_json(state_path, state)
                        raise
            paths = evidence(task, out)
            passed = code == 0 and all(p.is_file() for p in paths)
            state["tasks"][key].update(
                status="complete"
                if passed
                else "budget_exhausted"
                if code == 124
                else "failed",
                returncode=code,
                finished_unix=time.time(),
                evidence={
                    p.relative_to(ROOT).as_posix(): file_hash(p)
                    for p in paths
                    if p.is_file()
                },
            )
            atomic_json(state_path, state)
        state["status"] = (
            "complete"
            if all(t["status"] == "complete" for t in state["tasks"].values())
            else "incomplete"
        )
        atomic_json(state_path, state)
        from experiment_tasks import make_report

        make_report(config, out, state)
    finally:
        lock.unlink(missing_ok=True)
    return state


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "command",
        choices=["plan", "run", "resume", "status", "report", "refresh-preflight"],
    )
    p.add_argument("--config", type=Path, default=ROOT / "configs/pc_rerun.json")
    p.add_argument(
        "--reason", help="Required audit trail for pre-research code refresh"
    )
    args = p.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    out = portable_path(config["output"])
    if args.command == "plan":
        tasks = matrix(config)
        print(
            json.dumps(
                {"hours": config["hours"], "tasks": len(tasks), "matrix": tasks},
                indent=2,
            )
        )
        return
    if args.command == "refresh-preflight":
        state = refresh_preflight(config, args.config, args.reason)
    elif args.command in ("run", "resume"):
        state = run(config, args.config, args.command == "resume")
    else:
        state = json.loads((out / "state.json").read_text(encoding="utf-8"))
        if args.command == "report":
            from experiment_tasks import make_report

            make_report(config, out, state)
    from collections import Counter

    print(
        json.dumps(
            {
                "status": state["status"],
                "tasks": dict(Counter(t["status"] for t in state["tasks"].values())),
                "report": str(out / "report.md"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

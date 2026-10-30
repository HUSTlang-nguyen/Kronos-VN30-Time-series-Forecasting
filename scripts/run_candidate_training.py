"""Train audited candidate data as exploration within the ORIGINAL PC deadline."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from research_protocol import (
    MODELS,
    atomic_json,
    file_hash,
    portable_path,
    source_identity,
)
from vn30_forecast import check_manifest, load, load_manifest_data, split_manifest


def prepare_candidate(config_path, parent, out):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    state = json.loads((parent / "state.json").read_text(encoding="utf-8"))
    if state["identity"]["config_sha256"] != file_hash(config_path):
        raise ValueError("Original config changed")
    if state["identity"]["source_identity"] != source_identity():
        raise ValueError("Revalidate preflight code before candidate training")
    if state["identity"]["provenance_sha256"] != file_hash(
        ROOT / "data/manifests/checkpoint_provenance.yaml"
    ):
        raise ValueError("Model provenance changed")
    if time.time() >= state["deadline_unix"]:
        raise TimeoutError("Original 24-hour budget exhausted")
    if out.resolve() == parent.resolve() or not out.resolve().is_relative_to(ROOT):
        raise ValueError("Exploration requires a separate workspace output")
    audit_path = parent / "audit/audit.json"
    evidence = state.get("tasks", {}).get("audit", {})
    if evidence.get("status") != "complete" or evidence.get("evidence", {}).get(
        audit_path.relative_to(ROOT).as_posix()
    ) != file_hash(audit_path):
        raise ValueError("Audit must match the completed original preflight receipt")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    df, sha = load(portable_path(config["dataset"]), portable_path(config["receipt"]))
    if audit["dataset_sha256"] != sha or audit["status"] != "unverified":
        raise ValueError("This command is only for the explicitly unverified snapshot")
    out.mkdir(parents=True, exist_ok=True)
    copied_audit = out / "audit.json"
    if copied_audit.exists() and file_hash(copied_audit) != file_hash(audit_path):
        raise ValueError("Exploratory audit changed; do not overwrite evidence")
    if not copied_audit.exists():
        copied_audit.write_bytes(audit_path.read_bytes())
    info = {
        "dataset": config["dataset"],
        "receipt": config["receipt"],
        "audit": copied_audit.relative_to(ROOT).as_posix(),
        "audit_sha256": file_hash(copied_audit),
        "audit_status": "unverified",
        "usage": "exploratory_only",
    }
    manifest = split_manifest(df, sha, dataset_info=info)
    check_manifest(df, sha, manifest)
    load_manifest_data(manifest, allow_exploratory=True)
    path = out / "candidate.json"
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError("Candidate manifest changed")
    if not path.exists():
        atomic_json(path, manifest)
    identity = {
        "evidence_scope": "exploratory_only",
        "dataset_accepted": False,
        "parent_output": parent.relative_to(ROOT).as_posix(),
        "config_sha256": file_hash(config_path),
        "dataset_sha256": sha,
        "manifest_sha256": file_hash(path),
        "source_identity": source_identity(),
        "original_started_unix": state["started_unix"],
        "deadline_unix": state["deadline_unix"],
        "limitations": [
            "OHLC discrepancies unresolved",
            "Calendar unverified",
            "Not primary Q1-Q4 evidence",
            "No automatic promotion of checkpoints",
        ],
    }
    receipt = out / "identity.json"
    if receipt.exists() and json.loads(receipt.read_text()) != identity:
        raise ValueError("Exploratory identity/deadline changed")
    if not receipt.exists():
        atomic_json(receipt, identity)
    return config, manifest, identity, df


def verify_training(path, identity, model, epochs, seed, config):
    trained = json.loads((path / "training.json").read_text())
    expected = {
        "evidence_scope": "exploratory_only",
        "base_model": model,
        "epochs": epochs,
        "seed": seed,
        "device": config["device"],
        "learning_rate": config["learning_rate"],
        "initialization": "pretrained",
        "data_budget": None,
        "source_identity": identity["source_identity"],
        "manifest_sha256": identity["manifest_sha256"],
        "dataset_sha256": identity["dataset_sha256"],
        "test_used_for_training_or_selection": False,
        "effective_batch": 16,
    }
    if any(trained.get(k) != v for k, v in expected.items()):
        raise ValueError("Candidate checkpoint protocol differs")
    for receipt in (trained, json.loads((path / "selection.json").read_text())):
        if any(receipt.get(k) != v for k, v in expected.items()):
            raise ValueError("Candidate selected checkpoint protocol differs")
        base = (path / receipt["checkpoint_directory"]).resolve()
        if (
            not base.is_relative_to(path.resolve())
            or "model.safetensors" not in receipt["checkpoint_files"]
        ):
            raise ValueError("Unsafe or empty candidate checkpoint")
        for name, checksum in receipt["checkpoint_files"].items():
            file = (base / name).resolve()
            if not file.is_relative_to(base) or file_hash(file) != checksum:
                raise ValueError("Candidate checkpoint checksum differs")
    return trained


def report(out, state):
    rows = [
        "# VN30 — huấn luyện thăm dò trên PC",
        "",
        "**Dataset chưa được chấp nhận. Không dùng bảng này để chốt Q1–Q4.**",
        "",
        "Đồng hồ và hạn dừng dùng chung lượt PC gốc; không cấp thêm 24 giờ.",
        "",
        "| Job | Trạng thái | Epoch tốt nhất | Validation loss | Giây train |",
        "|---|---|---:|---:|---:|",
    ]
    for key, entry in state["jobs"].items():
        r = entry.get("training", {})
        rows.append(
            f"| {key} | {entry['status']} | {r.get('best_epoch', '')} | {r.get('best_validation_loss', '')} | {r.get('elapsed_seconds', '')} |"
        )
    (out / "report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=ROOT / "configs/pc_rerun.json")
    p.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/local/pc-exploratory-20261030"
    )
    p.add_argument("--models", nargs="+", choices=list(MODELS), default=list(MODELS))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--phase", choices=["benchmark", "train", "both"], default="both")
    args = p.parse_args()
    parent = portable_path(json.loads(args.config.read_text())["output"])
    out = args.output.resolve()
    config, manifest, identity, df = prepare_candidate(args.config, parent, out)
    state_path = out / "state.json"
    state = (
        json.loads(state_path.read_text())
        if state_path.exists()
        else {"evidence_scope": "exploratory_only", "jobs": {}}
    )
    lock = ROOT / ".cache/vn30-gpu.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("x") as f:
        json.dump({"pid": os.getpid(), "output": str(out)}, f)
    env = dict(
        os.environ,
        VN30_DEADLINE_UNIX=str(identity["deadline_unix"]),
        MPLCONFIGDIR=str(ROOT / ".cache/matplotlib"),
    )
    try:
        phases = ["benchmark", "train"] if args.phase == "both" else [args.phase]
        for phase in phases:
            for model in args.models:
                if time.time() >= identity["deadline_unix"]:
                    raise TimeoutError("Original deadline reached")
                epochs = 1 if phase == "benchmark" else config["epochs"]
                key = f"{phase}-{model}-s{args.seed}"
                target = out / "checkpoints" / key
                state["jobs"][key] = {"status": "running", "started_unix": time.time()}
                atomic_json(state_path, state)
                report(out, state)
                print(key, flush=True)
                if not (target / "training.json").exists():
                    cmd = [
                        sys.executable,
                        "scripts/finetune_vn30.py",
                        "--manifest",
                        str(out / "candidate.json"),
                        "--model",
                        model,
                        "--output",
                        str(target),
                        "--device",
                        config["device"],
                        "--epochs",
                        str(epochs),
                        "--seed",
                        str(args.seed),
                        "--learning-rate",
                        str(config["learning_rate"]),
                        "--exploratory",
                    ]
                    if (target / "last.pt").exists():
                        cmd.append("--resume")
                    with (out / (key + ".log")).open("a", encoding="utf-8") as log:
                        subprocess.run(
                            cmd,
                            cwd=ROOT,
                            env=env,
                            stdout=log,
                            stderr=subprocess.STDOUT,
                            check=True,
                        )
                trained = verify_training(
                    target, identity, model, epochs, args.seed, config
                )
                if phase == "benchmark":
                    from forecast_vn30 import forecast

                    dest = out / "benchmarks" / (model + ".csv")
                    dest.parent.mkdir(exist_ok=True)
                    if not dest.exists():
                        old_deadline = os.environ.get("VN30_DEADLINE_UNIX")
                        os.environ["VN30_DEADLINE_UNIX"] = str(
                            identity["deadline_unix"]
                        )
                        try:
                            forecast(
                                df,
                                manifest,
                                model,
                                "validation",
                                config["device"],
                                args.seed,
                                dest,
                                32,
                            )
                        finally:
                            if old_deadline is None:
                                os.environ.pop("VN30_DEADLINE_UNIX", None)
                            else:
                                os.environ["VN30_DEADLINE_UNIX"] = old_deadline
                    meta = json.loads(dest.with_suffix(".json").read_text())
                    expected = {
                        "evidence_scope": "exploratory_only",
                        "dataset_sha256": identity["dataset_sha256"],
                        "source_identity": identity["source_identity"],
                        "model": model,
                        "seed": args.seed,
                        "split": "validation",
                        "origins": 32,
                        "limited": True,
                        "forecast_csv_sha256": file_hash(dest),
                    }
                    if any(meta.get(k) != v for k, v in expected.items()):
                        raise ValueError(
                            "Candidate benchmark forecast identity differs"
                        )
                state["jobs"][key] = {
                    "status": "complete",
                    "training": trained,
                    "checkpoint": target.relative_to(ROOT).as_posix(),
                }
                atomic_json(state_path, state)
                report(out, state)
                print(key, "complete", flush=True)
    except Exception as exc:
        if "key" in locals() and state["jobs"].get(key, {}).get("status") == "running":
            state["jobs"][key].update(
                status="interrupted", error=type(exc).__name__ + ": " + str(exc)
            )
            atomic_json(state_path, state)
            report(out, state)
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

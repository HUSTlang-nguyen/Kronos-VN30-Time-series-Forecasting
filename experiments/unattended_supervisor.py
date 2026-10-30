"""Local, quota-free supervision of the authorized VN30 candidate pipeline.

Adopts existing workers, restarts only verified-dead processes, preserves all
scientific settings and the original deadline, and keeps progress reviewable.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_protocol import atomic_json, file_hash, source_identity

PHASES = {
    "baselines": ["scripts/evaluate_candidate.py", "baselines"],
    "neural": ["scripts/evaluate_candidate.py", "neural"],
    "score": ["scripts/evaluate_candidate.py", "score"],
    "learning": ["experiments/candidate_learning.py", "--wait-for-gpu"],
    "followups": ["experiments/candidate_stability.py", "--wait-for-learning"],
}
EXPECTED = {"baselines": 11, "neural": 48, "score": 1, "learning": 36, "followups": 5}


def matches(command, arguments):
    if not command:
        return False
    aliases = {
        arguments[0].replace("\\", "/").casefold(),
        (ROOT / arguments[0]).as_posix().casefold(),
    }
    for index, part in enumerate(command):
        if part.replace("\\", "/").casefold() in aliases:
            return command[index + 1 : index + len(arguments)] == arguments[1:]
    return False


def workers(arguments):
    found = []
    for process in psutil.process_iter(["pid", "cmdline", "create_time"]):
        try:
            if (
                matches(process.info["cmdline"], arguments)
                and process.is_running()
                and process.status() != psutil.STATUS_ZOMBIE
            ):
                found.append(
                    {"pid": process.pid, "created_unix": process.create_time()}
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return found


def phase_state(candidate, phase):
    if phase in ("neural", "baselines", "score"):
        path = candidate / "evaluation-main" / (phase + "-state.json")
    else:
        path = candidate / phase / "state.json"
    data = json.loads(path.read_text()) if path.exists() else {"jobs": {}}
    done = sum(entry["status"] == "complete" for entry in data["jobs"].values())
    return {
        "complete": done == EXPECTED[phase] and len(data["jobs"]) == EXPECTED[phase],
        "done": done,
        "expected": EXPECTED[phase],
        "state_path": str(path),
    }


def clean_stale_lock(path, archive, emit):
    if not path.exists():
        return True
    record = json.loads(path.read_text())
    pid = record.get("pid")
    if pid and psutil.pid_exists(pid):
        return False  # An observation timeout never makes a live owner stale.
    # A dead coordinator can leave an epoch worker alive. Never overlap it.
    if path.name == "vn30-gpu.lock":
        if workers(PHASES["neural"]) or workers(["scripts/finetune_vn30.py"]):
            return False
        for phase in ("learning", "followups"):
            for live in workers(PHASES[phase]):
                # Queued coordinators wait without holding GPU tensors.
                queue = (
                    ROOT
                    / "artifacts/local/pc-exploratory-20261030"
                    / phase
                    / "queue.json"
                )
                if (
                    not queue.exists()
                    or json.loads(queue.read_text()).get("status") == "running"
                ):
                    return False
    else:
        phase = path.stem.removeprefix("candidate-")
        if phase in PHASES and workers(PHASES[phase]):
            return False
    if path.resolve() != (
        ROOT / ".cache/vn30-gpu.lock"
    ).resolve() and not path.resolve().is_relative_to(ROOT / ".cache"):
        raise ValueError("Unsafe lock recovery path")
    archive.mkdir(parents=True, exist_ok=True)
    atomic_json(
        archive / (str(time.time_ns()) + ".json"),
        {"path": str(path), "previous": record, "sha256": file_hash(path)},
    )
    path.unlink()
    emit("recovered_dead_owner_lock", path=str(path), previous_pid=pid)
    return True


def protocol_failure(phase):
    logs = [
        ROOT / ".cache" / f"candidate-{phase}.log",
        ROOT / ".cache" / f"supervised-{phase}.log",
    ]
    existing = [p for p in logs if p.exists()]
    if not existing:
        return False
    text = (
        max(existing, key=lambda p: p.stat().st_mtime)
        .read_bytes()[-8000:]
        .decode("utf-8", errors="replace")
        .lower()
    )
    return "traceback" in text and any(
        word in text
        for word in ("identity", "protocol", "checksum", "audit", "manifest")
    )


def launch(command, log_path):
    with log_path.open("a", encoding="utf-8") as log:
        flags = (
            subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
            if os.name == "nt"
            else 0
        )
        return subprocess.Popen(
            [sys.executable, *command],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )


def self_test():
    import tempfile

    temporary = ROOT / ".cache/supervisor-tests"
    temporary.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temporary) as directory:
        folder = Path(directory)
        worker = folder / "worker.py"
        checkpoint = folder / "checkpoint.json"
        worker.write_text(
            "import json,sys,time\nfrom pathlib import Path\np=Path(sys.argv[1])\ns=json.loads(p.read_text()) if p.exists() else {'attempts':0,'completed_epoch':0}\ns['attempts']+=1\ns['completed_epoch']+=1\np.write_text(json.dumps(s))\ntime.sleep(.2)\nsys.exit(7 if s['attempts']==1 else 0)\n",
            encoding="utf-8",
        )
        command = [str(worker), str(checkpoint)]
        first = launch(command, folder / "worker.log")
        assert first.wait(timeout=10) == 7
        assert not workers(command)
        saved = json.loads(checkpoint.read_text())
        second = launch(command, folder / "worker.log")
        assert second.wait(timeout=10) == 0
        result = json.loads(checkpoint.read_text())
        assert saved["completed_epoch"] == 1 and result == {
            "attempts": 2,
            "completed_epoch": 2,
        }
        receipt = {
            "classification": "disposable_process_recovery_test_not_research",
            "status": "pass",
            "first_exit_code": 7,
            "restart_exit_code": 0,
            "checkpoint_preserved": True,
            "real_research_processes_touched": False,
        }
        atomic_json(
            ROOT
            / "artifacts/local/pc-preflight-20261030/supervisor_recovery_test.json",
            receipt,
        )
        print(json.dumps(receipt))


def render(candidate, state):
    lines = [
        "# VN30 — chạy tự động trên PC",
        "",
        "**Dataset vẫn unverified; kết quả mang nhãn thăm dò.**",
        "",
        f"Cập nhật UTC: {state['updated_utc']}. Hạn gốc Unix: {state['deadline_unix']}.",
        "",
        "| Phần | Hoàn tất | Trạng thái | PID đang sống | Lần khởi động lại |",
        "|---|---:|---|---|---:|",
    ]
    for name, entry in state["phases"].items():
        lines.append(
            f"| {name} | {entry['done']}/{entry['expected']} | {entry['status']} | {', '.join(str(p['pid']) for p in entry['processes'])} | {entry['restarts']} |"
        )
    lines += [
        "",
        "GPU tuần tự; không đổi learning rate, precision, seed, origin hoặc trạng thái kiểm toán để vượt lỗi.",
        "Các lượt còn sống không bị khởi động lại chỉ vì chậm. Lỗi protocol/hash phải chờ kiểm tra; lỗi tiến trình có tối đa hai lần tiếp tục.",
        "",
    ]
    table = candidate / "evaluation-main/seed_summary.csv"
    if table.exists():
        import pandas as pd

        frame = pd.read_csv(table)
        selected = frame.loc[(frame.split == "test") & (frame.target == "close")]
        pivot = selected.pivot(index="model", columns="horizon", values="mae_mean")
        lines += [
            "## MAE Close từ các seed đã chấm",
            "",
            "Số seed đang có: "
            + str(sorted(selected.seeds.unique().tolist()))
            + ". Không coi seed là các tập thị trường độc lập.",
            "",
            "| Model | h=1 | h=5 | h=20 |",
            "|---|---:|---:|---:|",
        ]
        for model, row in pivot.iterrows():
            lines.append(
                "| "
                + model
                + " | "
                + " | ".join(f"{row.get(h, float('nan')):.3f}" for h in (1, 5, 20))
                + " |"
            )
    lines += [
        "",
        "## Giới hạn còn lại",
        "",
        "- Chưa phân xử đủ chênh lệch OHLC và chưa xác nhận Open chính thức.",
        "- Không tự chuyển checkpoint thăm dò thành bằng chứng chính hoặc đánh dấu bài hoàn thiện.",
        "- Bảng chi tiết: evaluation-main/, learning/, followups/. Nhật ký: supervision/events.jsonl.",
        "",
    ]
    (candidate / "UNATTENDED_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def artifact_checkpoint(candidate, emit):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never")

    def git(*args):
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
        )

    if git("diff", "--cached", "--name-only").stdout.strip():
        emit("git_skipped_index_busy")
        return
    added = git("add", "--", candidate.relative_to(ROOT).as_posix())
    if added.returncode:
        emit("git_add_failed", returncode=added.returncode)
        return
    names = git("diff", "--cached", "--name-only").stdout.splitlines()
    if not names:
        return
    if any(
        Path(name).suffix.lower()
        not in {".json", ".jsonl", ".csv", ".png", ".md", ".txt"}
        for name in names
    ):
        emit("git_refused_unexpected_payload")
        return
    committed = git("commit", "-m", "chore: save PC experiment progress")
    if committed.returncode:
        emit("git_commit_failed", returncode=committed.returncode)
        return
    pushed = git(
        "-c", "credential.interactive=never", "push", "origin", "neikhn/lam-lai-vn30-pc"
    )
    emit(
        "artifact_checkpoint",
        commit=git("rev-parse", "--short", "HEAD").stdout.strip(),
        pushed=pushed.returncode == 0,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--candidate",
        type=Path,
        default=ROOT / "artifacts/local/pc-exploratory-20261030",
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="Read-only health snapshot; no launches or git",
    )
    p.add_argument(
        "--self-test",
        action="store_true",
        help="Test a disposable failed process and checkpoint continuation",
    )
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    candidate = args.candidate.resolve()
    if not candidate.is_relative_to(ROOT):
        raise ValueError("Supervisor output must remain in the workspace")
    out = candidate / "supervision"
    out.mkdir(parents=True, exist_ok=True)
    parent = json.loads(
        (ROOT / "artifacts/local/pc-rerun-20261030/state.json").read_text()
    )
    deadline = parent["deadline_unix"]
    source_files = {
        p.relative_to(ROOT).as_posix(): file_hash(p, normalized=True)
        for p in (ROOT / "experiments").glob("*.py")
    }
    identity = {
        "source_identity": source_identity(),
        "orchestrators": source_files,
        "deadline_unix": deadline,
        "evidence_scope": "exploratory_only",
        "max_restarts": 2,
    }
    identity_path = out / "identity.json"
    if identity_path.exists() and json.loads(identity_path.read_text()) != identity:
        raise ValueError("Supervisor code/deadline changed")
    if not identity_path.exists():
        atomic_json(identity_path, identity)
    events = out / "events.jsonl"

    def emit(event, **fields):
        with events.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "utc": datetime.now(timezone.utc).isoformat(),
                        "event": event,
                        **fields,
                    }
                )
                + "\n"
            )

    state_path = out / "status.json"
    previous = (
        json.loads(state_path.read_text()) if state_path.exists() else {"phases": {}}
    )
    attempts = {
        name: previous["phases"].get(name, {}).get("restarts", 0) for name in PHASES
    }
    last_launch = {name: 0.0 for name in PHASES}
    last_git = time.time()
    previously_done = set()
    power = False
    supervisor_lock = out / "supervisor.lock"
    if not args.once:
        if supervisor_lock.exists():
            old = json.loads(supervisor_lock.read_text())
            if psutil.pid_exists(old["pid"]):
                raise RuntimeError(
                    "A supervisor is already alive; do not start another"
                )
            atomic_json(out / ("old_supervisor_" + str(time.time_ns()) + ".json"), old)
            supervisor_lock.unlink()
        with supervisor_lock.open("x") as f:
            json.dump(
                {"pid": os.getpid(), "created_unix": psutil.Process().create_time()}, f
            )
    if os.name == "nt" and not args.once:
        power = bool(ctypes.windll.kernel32.SetThreadExecutionState(0x80000001))
    emit(
        "supervisor_started", pid=os.getpid(), keep_awake=power, snapshot_only=args.once
    )
    try:
        while True:
            now = time.time()
            source_changed = source_identity() != identity["source_identity"] or any(
                file_hash(ROOT / name, normalized=True) != sha
                for name, sha in source_files.items()
            )
            snapshot = {
                "pid": os.getpid(),
                "updated_utc": datetime.now(timezone.utc).isoformat(),
                "deadline_unix": deadline,
                "evidence_scope": "exploratory_only",
                "dataset_accepted": False,
                "keep_awake": power,
                "phases": {},
            }
            for name, command in PHASES.items():
                entry = phase_state(candidate, name)
                live = workers(command)
                entry.update(
                    processes=live,
                    restarts=attempts[name],
                    status="complete"
                    if entry["complete"]
                    else "running"
                    if live
                    else "pending",
                )
                queue_file = candidate / name / "queue.json"
                if live and name in ("learning", "followups") and queue_file.exists():
                    queue_status = json.loads(queue_file.read_text()).get("status", "")
                    if queue_status.startswith("waiting_"):
                        entry["status"] = queue_status
                ready = (
                    name in ("baselines", "neural", "learning")
                    or (
                        name == "score"
                        and all(
                            phase_state(candidate, k)["complete"]
                            for k in ("baselines", "neural")
                        )
                    )
                    or (
                        name == "followups"
                        and phase_state(candidate, "learning")["complete"]
                    )
                )
                if (
                    not entry["complete"]
                    and not live
                    and ready
                    and not args.once
                    and now < deadline
                    and now - last_launch[name] >= 60
                ):
                    if source_changed:
                        entry["status"] = "needs_attention_source_changed"
                    elif protocol_failure(name):
                        entry["status"] = "needs_attention_protocol_error"
                    elif attempts[name] >= 2:
                        entry["status"] = "needs_attention_retry_limit"
                    elif shutil.disk_usage(ROOT).free < 10 * 1024**3:
                        entry["status"] = "needs_attention_disk_space"
                    else:
                        lock = (
                            ROOT
                            / ".cache"
                            / (
                                "vn30-gpu.lock"
                                if name in ("neural", "learning", "followups")
                                else f"candidate-{name}.lock"
                            )
                        )
                        clean = not lock.exists() or clean_stale_lock(
                            lock, out / "recovered_locks", emit
                        )
                        # Waiting learning/followup coordinators do not hold the GPU.
                        if clean:
                            process = launch(
                                command, ROOT / ".cache" / f"supervised-{name}.log"
                            )
                            attempts[name] += 1
                            last_launch[name] = now
                            entry.update(
                                status="launched",
                                restarts=attempts[name],
                                processes=[{"pid": process.pid, "created_unix": now}],
                            )
                            emit(
                                "phase_started",
                                phase=name,
                                pid=process.pid,
                                attempt=attempts[name],
                            )
                        else:
                            entry["status"] = "waiting_for_existing_owner"
                snapshot["phases"][name] = entry
            snapshot["pipeline_complete"] = all(
                e["complete"] for e in snapshot["phases"].values()
            )
            atomic_json(state_path, snapshot)
            render(candidate, snapshot)
            done = {
                name for name, entry in snapshot["phases"].items() if entry["complete"]
            }
            if not args.once and (done - previously_done or now - last_git >= 3600):
                try:
                    artifact_checkpoint(candidate, emit)
                except Exception as exc:
                    emit("git_nonfatal_error", error=type(exc).__name__)
                last_git = now
            previously_done = done
            if args.once or snapshot["pipeline_complete"] or now >= deadline:
                emit(
                    "supervisor_finished",
                    pipeline_complete=snapshot["pipeline_complete"],
                    original_deadline_reached=now >= deadline,
                )
                break
            time.sleep(30)
    finally:
        if power:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        if (
            not args.once
            and supervisor_lock.exists()
            and json.loads(supervisor_lock.read_text()).get("pid") == os.getpid()
        ):
            supervisor_lock.unlink()


if __name__ == "__main__":
    main()

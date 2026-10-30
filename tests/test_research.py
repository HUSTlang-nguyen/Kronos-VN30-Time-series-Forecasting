"""Protocol tests use synthetic data, never legacy experimental scores."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import numpy as np
import pandas as pd

TEMP_ROOT = ROOT / ".cache/test-runs"
TEMP_ROOT.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(TEMP_ROOT)
from research_protocol import (
    atomic_json,
    budget_origins,
    expanding_folds,
    file_hash,
    portable_path,
    validate_coverage,
)
from vn30_forecast import (
    CONTEXT,
    HORIZON,
    COLS,
    load,
    split_manifest,
    check_manifest,
    build_model,
)
from research_statistics import block_interval


def frame(n=400):
    dates = pd.bdate_range("2020-01-01", periods=n)
    close = 100 + np.arange(n) * 0.03 + np.sin(np.arange(n) / 7)
    result = pd.DataFrame(
        {
            "row_id": np.arange(1, n + 1),
            "date": dates.strftime("%Y-%m-%d"),
            "open": close - 0.1,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
        }
    )
    for flag in (
        "duplicate_date",
        "invalid_numeric",
        "invalid_ohlc",
        "outside_request",
    ):
        result[flag] = 0
    result["session_date"] = dates
    return result


def snapshot(folder, n=400):
    from validate_vn30_sources import parse
    from share_vndirect_sqlite import export_sqlite

    df = frame(n)
    dates = pd.to_datetime(df.date, utc=True)
    payload = {
        "s": "ok",
        "t": (dates.astype("int64") // 10**9).tolist(),
        **{c[0]: df[c].tolist() for c in COLS},
    }
    config = {
        "timezone": "Asia/Ho_Chi_Minh",
        "start": df.date.min(),
        "end": df.date.max(),
    }
    raw = json.dumps(payload).encode()
    parsed = parse(raw, config)
    parsed["date"] = parsed.date.dt.strftime("%Y-%m-%d")
    files = {
        "original_response.json": raw,
        "audit_config.yaml": json.dumps(config).encode(),
        "audit_manifest.json": b"{}",
        "parser.py": b"# fixture parser\n",
        "vn30_daily.csv": parsed.to_csv(index=False).encode(),
    }
    manifest = {
        "symbol": "VN30",
        "provider": "vndirect",
        "rows": len(df),
        "first_date": df.date.min(),
        "last_date": df.date.max(),
        "quality_counts": {
            k: 0
            for k in (
                "duplicate_date",
                "invalid_numeric",
                "invalid_ohlc",
                "outside_request",
            )
        },
        "units": "index_points",
        "timezone": config["timezone"],
        "request_url": "https://fixture.invalid?from=1&to=2",
        "files": {
            name: {"sha256": hashlib.sha256(b).hexdigest(), "size_bytes": len(b)}
            for name, b in files.items()
        },
    }
    archive = folder / "snapshot.zip"
    with ZipFile(archive, "w") as z:
        for name, b in files.items():
            z.writestr(name, b)
        z.writestr("manifest.json", json.dumps(manifest))
    database = folder / "snapshot.sqlite"
    result = export_sqlite(archive, database, file_hash(archive))
    receipt = folder / "receipt.json"
    atomic_json(receipt, result)
    return df, database, receipt


class TemporalTests(unittest.TestCase):
    def setUp(self):
        self.df = frame()
        self.m = split_manifest(self.df, "fixture")

    def test_original_manifest_compatible(self):
        check_manifest(self.df, "fixture", self.m)

    def test_no_future_labels_cross_split(self):
        for split, origins in self.m["origins"].items():
            a = self.m["boundaries"][split]["row_start"]
            b = self.m["boundaries"][split]["row_end_exclusive"]
            self.assertTrue(all(i + 1 >= a and i + HORIZON < b for i in origins))

    def test_reject_tampered_origin(self):
        self.m["origins"]["train"].append(399)
        with self.assertRaises(ValueError):
            check_manifest(self.df, "fixture", self.m)

    def test_nested_budget_counts(self):
        large = set(budget_origins(self.m, 250))
        small = set(budget_origins(self.m, 200))
        self.assertTrue(small < large)
        self.assertEqual(len(small), 200 - CONTEXT - HORIZON + 1)
        with self.assertRaises(ValueError):
            budget_origins(self.m, 1000)

    def test_folds_do_not_overlap_their_own_partitions(self):
        for m in expanding_folds(frame(1000), "fixture", {"dataset": "fixture"}):
            check_manifest(frame(1000), "fixture", m)

    @unittest.skipUnless(
        importlib.util.find_spec("sklearn"), "Optional model dependency scikit-learn"
    )
    def test_ridge_ignores_test_prices(self):
        changed = self.df.copy()
        changed.loc[self.m["boundaries"]["test"]["row_start"] :, COLS] *= 10
        a = build_model("ridge", self.df, self.m, "cpu")[0]
        b = build_model("ridge", changed, self.m, "cpu")[0]
        x = self.df[COLS].to_numpy()[:CONTEXT]
        np.testing.assert_array_equal(a(x, None, 42), b(x, None, 42))

    @unittest.skipUnless(
        importlib.util.find_spec("torch"), "Optional GPU training dependencies"
    )
    def test_normalization_ignores_future(self):
        from finetune_vn30 import context_normalize

        values = np.random.default_rng(42).normal(size=(2, 148, 6)).astype(np.float32)
        changed = values.copy()
        changed[:, 128:] *= 100
        np.testing.assert_array_equal(
            context_normalize(values)[:, :128], context_normalize(changed)[:, :128]
        )

    def test_coverage_rejects_duplicates(self):
        rows = [
            {"origin_index": i, "horizon": h, **{"pred_" + c: 1.0 for c in COLS}}
            for i in self.m["origins"]["test"]
            for h in range(1, 21)
        ]
        values = pd.DataFrame(rows)
        validate_coverage(values, self.m, "test")
        values.iloc[1] = values.iloc[0]
        with self.assertRaises(ValueError):
            validate_coverage(values, self.m, "test")

    def test_block_interval_constant_difference(self):
        self.assertEqual(block_interval(np.ones(50)), [1.0, 1.0])

    def test_portable_old_receipt(self):
        self.assertEqual(
            portable_path("artifacts\\local\\test.csv"),
            ROOT / "artifacts/local/test.csv",
        )


class AuditTests(unittest.TestCase):
    def test_integrity_alone_never_accepts_data(self):
        from audit_vn30_data import audit

        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            df, database, receipt = snapshot(folder)
            loaded, _ = load(database, receipt)
            self.assertEqual(len(loaded), len(df))
            result = audit(database, receipt, folder / "audit")
            self.assertEqual(result["status"], "unverified")
            self.assertEqual(result["raw_replay"], "pass")

    def test_matching_independent_evidence_and_calendar(self):
        from audit_vn30_data import audit

        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            df, database, receipt = snapshot(folder)
            source = folder / "independent.csv"
            df[["date", *COLS]].to_csv(source, index=False)
            atomic_json(
                source.with_suffix(".json"),
                {
                    "provider": "fixture_independent",
                    "symbol": "VN30",
                    "url": "https://fixture.invalid/prices",
                    "csv_sha256": file_hash(source),
                },
            )
            calendar = folder / "calendar.csv"
            df[["date"]].to_csv(calendar, index=False)
            atomic_json(
                calendar.with_suffix(".json"),
                {
                    "url": "https://fixture.invalid/calendar",
                    "csv_sha256": file_hash(calendar),
                },
            )
            result = audit(database, receipt, folder / "audit", [source], calendar)
            self.assertEqual(result["status"], "accepted_provider_scope")

    def test_byte_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            _, database, receipt = snapshot(folder)
            with database.open("ab") as f:
                f.write(b"X")
            with self.assertRaises(ValueError):
                load(database, receipt)


class CoordinatorTests(unittest.TestCase):
    def test_expired_resume_preserves_original_deadline(self):
        import time
        from run_experiment import run
        from research_protocol import source_identity

        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            config = json.loads((ROOT / "configs/pc_rerun.json").read_text())
            config["output"] = str(folder)
            path = folder / "input.json"
            atomic_json(path, config)
            end = time.time() - 1
            identity = {
                "config_sha256": file_hash(path),
                "source_identity": source_identity(),
                "provenance_sha256": file_hash(
                    ROOT / "data/manifests/checkpoint_provenance.yaml"
                ),
            }
            atomic_json(
                folder / "state.json",
                {
                    "identity": identity,
                    "started_unix": end - 86400,
                    "deadline_unix": end,
                    "status": "incomplete",
                    "tasks": {},
                },
            )
            result = run(config, path, resume=True)
            self.assertEqual(result["deadline_unix"], end)
            self.assertEqual(result["status"], "incomplete")
            self.assertFalse(
                any(t["status"] == "complete" for t in result["tasks"].values())
            )

    def test_matrix_has_valid_dependencies_and_no_legacy_forecasts(self):
        from run_experiment import matrix

        config = json.loads((ROOT / "configs/pc_rerun.json").read_text())
        tasks = matrix(config)
        seen = set()
        for task in tasks:
            self.assertNotIn(task["id"], seen)
            self.assertTrue(set(task["dependencies"]) <= seen)
            seen.add(task["id"])
        self.assertEqual(config["seeds"], [42, 43, 44])
        self.assertEqual(config["hours"], 24)

    def test_changed_checkpoint_variant_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary)
            atomic_json(
                checkpoint / "training.json",
                {"dataset_sha256": "fixture", "base_model": "kronos-base"},
            )
            with self.assertRaises(ValueError):
                build_model(
                    "kronos-mini-ft",
                    frame(),
                    split_manifest(frame(), "fixture"),
                    "cpu",
                    checkpoint,
                )


@unittest.skipUnless(
    importlib.util.find_spec("torch"), "Optional GPU training dependencies"
)
class ResumeTests(unittest.TestCase):
    def test_epoch_resume_matches_uninterrupted_cpu_training(self):
        import torch
        import finetune_vn30 as trainer
        from safetensors.torch import save_file

        df = frame()
        manifest = split_manifest(df, "fixture")
        counter = {"n": 0, "interrupt": False}

        def setup(spec, arrays, device, batch_size, initialization):
            model = torch.nn.Sequential(
                torch.nn.Linear(4, 8), torch.nn.Dropout(0.1), torch.nn.Linear(8, 4)
            )

            def batches(split, order):
                active = getattr(batches, "batch_size", batch_size)
                for start in range(0, len(order), active):
                    indices = order[start : start + active]
                    values = torch.from_numpy(arrays[split][indices]) / 100
                    yield values, len(indices)

            def loss(values):
                counter["n"] += 1
                if counter["interrupt"] and counter["n"] == 30:
                    raise TimeoutError("simulated interruption")
                return torch.nn.functional.mse_loss(
                    model(values[:, :128].mean(1)), values[:, 128:].mean(1)
                )

            def save(path):
                path.mkdir(parents=True, exist_ok=True)
                save_file(model.state_dict(), str(path / "model.safetensors"))

            return model, batches, loss, save, "fixture_mse"

        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            mfile = folder / "split.json"
            atomic_json(mfile, manifest)

            def run(name, resume=False):
                argv = [
                    "finetune",
                    "--manifest",
                    str(mfile),
                    "--model",
                    "chronos2",
                    "--device",
                    "cpu",
                    "--epochs",
                    "2",
                    "--output",
                    str(folder / name),
                ]
                if resume:
                    argv.append("--resume")
                with (
                    patch.object(sys, "argv", argv),
                    patch.object(
                        trainer, "load_manifest_data", return_value=(df, "fixture")
                    ),
                    patch.object(trainer, "setup_chronos", side_effect=setup),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    trainer.main()

            with patch.dict(os.environ, {"VN30_DEADLINE_UNIX": "inf"}):
                run("reference")
                counter.update(n=0, interrupt=True)
                with self.assertRaises(TimeoutError):
                    run("resumed")
                self.assertTrue((folder / "resumed/last.pt").exists())
                counter.update(n=0, interrupt=False)
                run("resumed", True)
            a = json.loads((folder / "reference/training.json").read_text())
            b = json.loads((folder / "resumed/training.json").read_text())
            self.assertEqual(
                a["selected_parameter_sha256"], b["selected_parameter_sha256"]
            )
            self.assertEqual(a["best_validation_loss"], b["best_validation_loss"])


if __name__ == "__main__":
    unittest.main()

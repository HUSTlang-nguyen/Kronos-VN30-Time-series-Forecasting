"""Evaluation may extend an immutable run, never silently change its protocol."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]
import numpy as np
import pandas as pd
from research_protocol import atomic_json, file_hash, source_identity
import test_research as fixture
from vn30_forecast import split_manifest
from evaluate_candidate import (
    additions_only,
    read_lock,
    validate_forecast,
    verify_metrics,
)


class CandidateEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=fixture.TEMP_ROOT)
        self.out = Path(self.temp.name)
        self.df = fixture.frame(400)
        self.manifest = split_manifest(self.df, "synthetic")
        self.identity = {
            "source_identity": source_identity(),
            "manifest_sha256": "synthetic_manifest",
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_only_evaluation_entry_point_can_be_added(self):
        previous = {"src/vn30_forecast.py": "oldhash"}
        additions_only(
            previous, {**previous, "scripts/evaluate_candidate.py": "newhash"}
        )
        for current in [
            previous,
            {
                "src/vn30_forecast.py": "changed",
                "scripts/evaluate_candidate.py": "newhash",
            },
            {
                **previous,
                "scripts/evaluate_candidate.py": "newhash",
                "scripts/other.py": "unreviewed",
            },
            {"scripts/evaluate_candidate.py": "newhash"},
        ]:
            with self.assertRaises(ValueError):
                additions_only(previous, current)

    def test_baseline_lock_must_preserve_full_validation_receipt(self):
        directory = self.out / "tuning"
        lock = directory / "ridge.json"
        trials = directory / "ridge-trials.json"
        atomic_json(lock, {"alpha": 10})
        atomic_json(trials, [{"config": {"alpha": 10}, "validation_loss": 0.1}])
        receipt = {
            "evidence_scope": "exploratory_only",
            **self.identity,
            "selected_on": "validation only",
            "test_used": False,
            "trials_sha256": file_hash(trials),
            "config_sha256": file_hash(lock),
        }
        atomic_json(directory / "ridge-receipt.json", receipt)
        self.assertEqual(read_lock(self.out, "ridge", self.identity), {"alpha": 10})
        atomic_json(lock, {"alpha": 100})
        with self.assertRaises(ValueError):
            read_lock(self.out, "ridge", self.identity)

    def test_forecast_scope_seed_dates_and_bytes_are_bound(self):
        p = self.out / "naive.csv"
        rows = []
        for i in self.manifest["origins"]["test"]:
            for h in range(1, 21):
                rows.append(
                    {
                        "origin_index": i,
                        "origin_date": self.df.date.iloc[i],
                        "target_date": self.df.date.iloc[i + h],
                        "horizon": h,
                        **{
                            "pred_" + c: float(self.df.close.iloc[i])
                            for c in ("open", "high", "low", "close")
                        },
                    }
                )
        pd.DataFrame(rows).to_csv(p, index=False)
        meta = {
            "evidence_scope": "exploratory_only",
            "model": "naive",
            "split": "test",
            "seed": 42,
            "dataset_sha256": "synthetic",
            "context": 128,
            "horizon": 20,
            "device": "cpu",
            "origins": len(self.manifest["origins"]["test"]),
            "limited": False,
            "source_identity": self.identity["source_identity"],
            "forecast_csv_sha256": file_hash(p),
            "checkpoint_choice": "best-trained",
            "calendar_note": self.manifest["calendar_note"],
            "model_config": {},
            "sampling": None,
            "sample_count": 0,
            "quantile_count": 0,
            "point_functional": "deterministic",
            "checkpoint": None,
            "revision": "last_close",
        }
        atomic_json(p.with_suffix(".json"), meta)
        validate_forecast(
            p, self.manifest, self.df, self.identity, "naive", "test", 42, {}
        )
        for field, value in [
            ("seed", 43),
            ("evidence_scope", "primary"),
            ("point_functional", "sample_mean"),
            ("forecast_csv_sha256", "changed"),
        ]:
            atomic_json(p.with_suffix(".json"), {**meta, field: value})
            with self.assertRaises(ValueError):
                validate_forecast(
                    p, self.manifest, self.df, self.identity, "naive", "test", 42, {}
                )

    def test_metrics_are_recomputed_from_errors(self):
        pd.DataFrame(
            {
                "model": ["naive", "naive"],
                "horizon": [1, 1],
                "pred_close": [2, 4],
                "actual_close": [1, 1],
            }
        ).to_csv(self.out / "details.csv", index=False)
        scores = pd.DataFrame(
            [
                {
                    "model": "naive",
                    "horizon": 1,
                    "target": "close",
                    "n": 2,
                    "mae": 2,
                    "rmse": np.sqrt(5),
                }
            ]
        )
        scores.to_csv(self.out / "scores.csv", index=False)
        verify_metrics(self.out)
        scores.loc[0, "mae"] = 1
        scores.to_csv(self.out / "scores.csv", index=False)
        with self.assertRaises(ValueError):
            verify_metrics(self.out)


if __name__ == "__main__":
    unittest.main()

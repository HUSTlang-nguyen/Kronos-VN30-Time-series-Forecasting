"""Negative protocol tests: internally consistent wrong metadata must still fail."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]
import yaml
from test_research import frame, TEMP_ROOT
from vn30_forecast import split_manifest
from research_protocol import (
    MODELS,
    atomic_json,
    budget_origins,
    file_hash,
    source_identity,
)
from forecast_protocol import sampling_spec, validate_forecast_metadata


class ForecastProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=TEMP_ROOT)
        self.out = Path(self.temp.name)
        self.config = json.loads((ROOT / "configs/pc_rerun.json").read_text())
        self.provenance = yaml.safe_load(
            (ROOT / "data/manifests/checkpoint_provenance.yaml").read_bytes()
        )
        self.manifest = split_manifest(frame(1000), "synthetic_protocol_only")
        atomic_json(self.out / "primary.json", self.manifest)
        self.task = {
            "model": "kronos-small-ft",
            "seed": 43,
            "split": "test",
            "fold": "primary",
            "checkpoint": "main-kronos-small-s43",
            "budget": None,
            "initialization": "pretrained",
        }
        self.directory = self.out / "checkpoints" / self.task["checkpoint"]
        (self.directory / "best").mkdir(parents=True)
        weights = self.directory / "best/model.safetensors"
        weights.write_bytes(b"synthetic checksum fixture, not loadable weights")
        model_key, token_key, _ = MODELS["kronos-small"]
        self.training = {
            "dataset_sha256": self.manifest["sha256"],
            "base_model": "kronos-small",
            "base_revision": self.provenance["models"][model_key][
                "repository_revision"
            ],
            "context": 128,
            "horizon": 20,
            "boundaries": self.manifest["boundaries"],
            "seed": 43,
            "device": "cuda:0",
            "data_budget": None,
            "initialization": "pretrained",
            "test_used_for_training_or_selection": False,
            "source_identity": source_identity(),
            "manifest_sha256": file_hash(self.out / "primary.json"),
            "checkpoint_directory": "best",
            "epochs": self.config["epochs"],
            "method": "full",
            "normalization": "context_only",
            "weight_decay": 0.01,
            "effective_batch": 16,
            "learning_rate": self.config["learning_rate"],
            "origins": {
                "train": len(budget_origins(self.manifest)),
                "validation": len(self.manifest["origins"]["validation"]),
            },
            "tokenizer": token_key,
            "tokenizer_revision": self.provenance["tokenizers"][token_key][
                "repository_revision"
            ],
            "teacher_forcing_causal_validation": True,
            "checkpoint_files": {"model.safetensors": file_hash(weights)},
        }
        atomic_json(self.directory / "training.json", self.training)
        self.meta = {
            "model": self.task["model"],
            "dataset_sha256": self.manifest["sha256"],
            "split": "test",
            "context": 128,
            "horizon": 20,
            "seed": 43,
            "origins": self.manifest["origin_counts"]["test"],
            "limited": False,
            "device": "cuda:0",
            "checkpoint_choice": "best-trained",
            "source_identity": source_identity(),
            "calendar_note": self.manifest["calendar_note"],
            "sampling": sampling_spec(self.task["model"]),
            "sample_count": 3,
            "quantile_count": 0,
            "point_functional": "sample_mean",
            "model_config": {},
            "checkpoint": str(self.directory),
            "revision": "finetuned:" + file_hash(weights),
        }

    def tearDown(self):
        self.temp.cleanup()

    def check(self, meta=None, task=None):
        validate_forecast_metadata(
            meta or self.meta,
            task or self.task,
            self.config,
            self.manifest,
            self.out,
            self.provenance,
        )

    def test_valid_checkpoint_and_protocol(self):
        self.check()

    def test_incorrect_forecast_fields_rejected(self):
        cases = {
            "seed": 42,
            "device": "cpu",
            "sample_count": 1,
            "quantile_count": 13,
            "point_functional": "quantile_mean",
            "checkpoint_choice": "selected",
            "context": 127,
            "horizon": 19,
            "model": "kronos-base-ft",
            "revision": "finetuned:wrong",
            "limited": True,
            "sampling": {
                "temperature": 0.5,
                "top_p": 0.9,
                "seed_rule": "seed+origin_index",
            },
            "source_identity": {},
            "model_config": {"alpha": 100},
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                bad = {**self.meta, field: value}
                with self.assertRaises(ValueError):
                    self.check(bad)

    def test_training_metadata_mutations_rejected(self):
        for field, value in {
            "seed": 42,
            "data_budget": 500,
            "initialization": "random",
            "epochs": 1,
            "learning_rate": 1e-4,
            "tokenizer_revision": "wrong",
            "test_used_for_training_or_selection": True,
            "source_identity": {},
            "effective_batch": 8,
            "manifest_sha256": "wrong",
        }.items():
            with self.subTest(field=field):
                atomic_json(
                    self.directory / "training.json", {**self.training, field: value}
                )
                with self.assertRaises(ValueError):
                    self.check()
        atomic_json(self.directory / "training.json", self.training)

    def test_changed_weights_rejected(self):
        (self.directory / "best/model.safetensors").write_bytes(b"modified")
        with self.assertRaises(ValueError):
            self.check()

    def test_wrong_checkpoint_path_rejected(self):
        with self.assertRaises(ValueError):
            self.check({**self.meta, "checkpoint": str(self.out / "other")})

    def test_zero_shot_revision_must_be_pinned(self):
        task = {**self.task, "model": "kronos-small", "checkpoint": None}
        meta = {
            **self.meta,
            "model": "kronos-small",
            "checkpoint": None,
            "revision": self.provenance["models"]["kronos_small"][
                "repository_revision"
            ],
        }
        self.check(meta, task)
        with self.assertRaises(ValueError):
            self.check({**meta, "revision": "main"}, task)

    def test_deterministic_baseline_uses_its_own_task_seed(self):
        task = {**self.task, "model": "naive", "seed": 42, "checkpoint": None}
        meta = {
            **self.meta,
            "model": "naive",
            "seed": 42,
            "device": "cpu",
            "checkpoint": None,
            "sample_count": 0,
            "point_functional": "deterministic",
            "sampling": None,
            "revision": "last_close",
        }
        self.check(meta, task)

    def test_baseline_config_must_match_validation_lock(self):
        atomic_json(self.out / "tuning/ridge.json", {"alpha": 10})
        task = {**self.task, "model": "ridge", "seed": 42, "checkpoint": None}
        meta = {
            **self.meta,
            "model": "ridge",
            "seed": 42,
            "device": "cpu",
            "checkpoint": None,
            "sample_count": 0,
            "point_functional": "deterministic",
            "sampling": None,
            "revision": "ridge_train_only_alpha10",
            "model_config": {"alpha": 10},
        }
        self.check(meta, task)
        with self.assertRaises(ValueError):
            self.check({**meta, "model_config": {"alpha": 100}}, task)


if __name__ == "__main__":
    unittest.main()

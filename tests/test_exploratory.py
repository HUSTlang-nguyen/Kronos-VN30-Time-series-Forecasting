"""Candidate training never accepts data or leaks into primary comparisons."""

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]
import test_research as fixtures
from forecast_protocol import validate_forecast_metadata
from research_protocol import atomic_json, file_hash, source_identity
from run_candidate_training import prepare_candidate
from vn30_forecast import load_manifest_data


class ExploratoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=fixtures.TEMP_ROOT)
        self.folder = Path(self.temp.name)
        self.parent = self.folder / "primary"
        self.out = self.folder / "candidate"
        self.parent.mkdir()
        df, database, receipt = fixtures.snapshot(self.folder)
        self.config = {"dataset": str(database), "receipt": str(receipt)}
        self.config_path = self.folder / "config.json"
        atomic_json(self.config_path, self.config)
        self.state = {
            "started_unix": time.time() - 100,
            "deadline_unix": time.time() + 86300,
            "identity": {
                "config_sha256": file_hash(self.config_path),
                "source_identity": source_identity(),
                "provenance_sha256": file_hash(
                    ROOT / "data/manifests/checkpoint_provenance.yaml"
                ),
            },
        }
        atomic_json(self.parent / "state.json", self.state)
        self.audit = {
            "status": "unverified",
            "dataset_sha256": file_hash(database),
            "raw_replay": "pass",
            "timestamp_timezone_replay": "pass",
            "quality_flag_replay": "pass",
            "invalid_or_duplicate_flags": 0,
            "independent_sources": [{"provider": "fixture"}],
            "required_dates_without_reference": [],
            "price_edits": [],
        }
        atomic_json(self.parent / "audit/audit.json", self.audit)
        self.state["tasks"] = {
            "audit": {
                "status": "complete",
                "evidence": {
                    (self.parent / "audit/audit.json")
                    .relative_to(ROOT)
                    .as_posix(): file_hash(self.parent / "audit/audit.json")
                },
            }
        }
        atomic_json(self.parent / "state.json", self.state)

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self):
        return prepare_candidate(self.config_path, self.parent, self.out)

    def test_explicit_opt_in_and_original_budget(self):
        _, manifest, identity, df = self.prepare()
        with self.assertRaises(ValueError):
            load_manifest_data(manifest)
        actual, sha = load_manifest_data(manifest, allow_exploratory=True)
        self.assertEqual(len(actual), len(df))
        self.assertEqual(sha, manifest["sha256"])
        self.assertEqual(identity["deadline_unix"], self.state["deadline_unix"])
        self.assertEqual(identity["original_started_unix"], self.state["started_unix"])
        self.assertFalse(identity["dataset_accepted"])
        self.assertEqual(
            json.loads((self.parent / "audit/audit.json").read_text()), self.audit
        )

    def test_failed_integrity_cannot_be_explored(self):
        for field, value in [
            ("raw_replay", "fail"),
            ("invalid_or_duplicate_flags", 1),
            ("independent_sources", []),
            ("required_dates_without_reference", ["2020-01-01"]),
            ("price_edits", [{"open": 1}]),
        ]:
            with self.subTest(field=field):
                bad = {**self.audit, field: value}
                atomic_json(self.parent / "audit/audit.json", bad)
                self.state["tasks"]["audit"]["evidence"] = {
                    (self.parent / "audit/audit.json")
                    .relative_to(ROOT)
                    .as_posix(): file_hash(self.parent / "audit/audit.json")
                }
                atomic_json(self.parent / "state.json", self.state)
                with tempfile.TemporaryDirectory(dir=self.folder) as candidate:
                    with self.assertRaises(ValueError):
                        prepare_candidate(
                            self.config_path, self.parent, Path(candidate)
                        )

    def test_expired_budget_rejected(self):
        self.state["deadline_unix"] = time.time() - 1
        atomic_json(self.parent / "state.json", self.state)
        with self.assertRaises(TimeoutError):
            self.prepare()

    def test_primary_output_refused(self):
        with self.assertRaises(ValueError):
            prepare_candidate(self.config_path, self.parent, self.parent)

    def test_changed_candidate_receipt_refused(self):
        self.prepare()
        self.state["deadline_unix"] += 3600
        atomic_json(self.parent / "state.json", self.state)
        with self.assertRaises(ValueError):
            self.prepare()

    def test_primary_scorer_rejects_exploratory_manifest_or_metadata(self):
        for manifest, meta in [
            ({"dataset_info": {"usage": "exploratory_only"}}, {}),
            ({}, {"evidence_scope": "exploratory_only"}),
        ]:
            with self.assertRaisesRegex(ValueError, "Exploratory"):
                validate_forecast_metadata(meta, {}, {}, manifest, self.out, {})

    def test_exploratory_switch_cannot_bypass_legacy_loader(self):
        with self.assertRaises(ValueError):
            load_manifest_data({}, allow_exploratory=True)


if __name__ == "__main__":
    unittest.main()

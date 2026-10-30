"""A code refresh is permitted only before research and never resets the clock."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]
from test_research import TEMP_ROOT
from research_protocol import atomic_json, file_hash, source_identity
from run_experiment import refresh_preflight


class PreflightRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=TEMP_ROOT)
        self.out = Path(self.temp.name)
        self.config = {"output": str(self.out)}
        self.path = self.out / "input.json"
        atomic_json(self.path, self.config)
        self.identity = {
            "config_sha256": file_hash(self.path),
            "source_identity": {"previous": "sha"},
            "provenance_sha256": file_hash(
                ROOT / "data/manifests/checkpoint_provenance.yaml"
            ),
        }
        (self.out / "audit").mkdir()
        atomic_json(self.out / "audit/audit.json", {"status": "unverified"})
        artifact = self.out / "audit/audit.json"
        self.state = {
            "identity": self.identity,
            "started_unix": 100,
            "deadline_unix": 86500,
            "status": "incomplete",
            "tasks": {
                "audit": {
                    "status": "complete",
                    "evidence": {
                        artifact.relative_to(ROOT).as_posix(): file_hash(artifact)
                    },
                }
            },
        }
        atomic_json(self.out / "state.json", self.state)

    def tearDown(self):
        self.temp.cleanup()

    def refresh(self):
        return refresh_preflight(
            self.config, self.path, "Validate scoring protocol fix before training"
        )

    def test_refresh_archives_and_keeps_budget(self):
        result = self.refresh()
        self.assertEqual(result["started_unix"], 100)
        self.assertEqual(result["deadline_unix"], 86500)
        self.assertEqual(result["tasks"], {})
        self.assertEqual(result["identity"]["source_identity"], source_identity())
        archive = ROOT / result["preflight_refreshes"][0]["archive"]
        self.assertTrue((archive / "audit/audit.json").is_file())
        self.assertEqual(json.loads((archive / "state.json").read_text()), self.state)

    def test_changed_config_rejected(self):
        self.path.write_text("{}")
        with self.assertRaises(ValueError):
            self.refresh()

    def test_research_artifacts_rejected(self):
        (self.out / "forecasts").mkdir()
        (self.out / "forecasts/test.csv").write_text("fixture")
        with self.assertRaises(ValueError):
            self.refresh()

    def test_completed_research_rejected(self):
        self.state["tasks"]["main-kronos-small-s42"] = {
            "status": "complete",
            "evidence": {},
        }
        atomic_json(self.out / "state.json", self.state)
        with self.assertRaises(ValueError):
            self.refresh()

    def test_modified_evidence_rejected(self):
        (self.out / "audit/audit.json").write_text("{}")
        with self.assertRaises(ValueError):
            self.refresh()

    def test_live_coordinator_rejected(self):
        (self.out / "coordinator.lock").write_text("fixture pid")
        with self.assertRaises(RuntimeError):
            self.refresh()


if __name__ == "__main__":
    unittest.main()

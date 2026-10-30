"""Supervision identifies only exact workers and never reclaims a live owner's lock."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "experiments"), str(ROOT / "src"), str(ROOT / "tests")]
from unattended_supervisor import matches, clean_stale_lock, phase_state
from research_protocol import atomic_json
from test_research import TEMP_ROOT


class SupervisorTests(unittest.TestCase):
    def test_exact_worker_matching_excludes_shell_text_and_other_phases(self):
        expected = ["scripts/evaluate_candidate.py", "neural"]
        self.assertTrue(
            matches(["python.exe", "scripts/evaluate_candidate.py", "neural"], expected)
        )
        self.assertTrue(
            matches(
                ["python.exe", str(ROOT / "scripts/evaluate_candidate.py"), "neural"],
                expected,
            )
        )
        self.assertFalse(
            matches(
                [
                    "powershell.exe",
                    "-Command",
                    "python scripts/evaluate_candidate.py neural",
                ],
                expected,
            )
        )
        self.assertFalse(
            matches(["python.exe", "scripts/evaluate_candidate.py", "score"], expected)
        )

    def test_live_owner_lock_is_preserved(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temporary:
            folder = Path(temporary)
            lock = folder / "candidate-score.lock"
            atomic_json(lock, {"pid": os.getpid()})
            original = lock.read_bytes()
            self.assertFalse(
                clean_stale_lock(lock, folder / "archive", lambda *a, **k: None)
            )
            self.assertEqual(lock.read_bytes(), original)

    def test_partial_state_is_never_reported_as_complete(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temporary:
            candidate = Path(temporary)
            path = candidate / "evaluation-main/neural-state.json"
            atomic_json(
                path, {"jobs": {str(i): {"status": "complete"} for i in range(47)}}
            )
            self.assertFalse(phase_state(candidate, "neural")["complete"])
            atomic_json(
                path, {"jobs": {str(i): {"status": "complete"} for i in range(48)}}
            )
            self.assertTrue(phase_state(candidate, "neural")["complete"])


if __name__ == "__main__":
    unittest.main()

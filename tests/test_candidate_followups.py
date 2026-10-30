"""Historical folds remain chronological; candidate ablation never accepts primary data."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / "experiments"),
    str(ROOT / "scripts"),
    str(ROOT / "src"),
    str(ROOT / "tests"),
]
from candidate_stability import folds
from research_protocol import atomic_json
from test_research import TEMP_ROOT, frame
from vn30_forecast import check_manifest, split_manifest


class CandidateFollowupTests(unittest.TestCase):
    def test_two_folds_with_separate_validation_and_test(self):
        df = frame(2271)
        info = {"dataset": "fixture", "usage": "exploratory_only"}
        primary = split_manifest(df, "synthetic", dataset_info=info)
        historical = folds(df, primary)
        self.assertEqual(len(historical), 2)
        for manifest in historical:
            check_manifest(df, "synthetic", manifest)
            b = manifest["boundaries"]
            self.assertLess(
                b["train"]["row_end_exclusive"],
                primary["boundaries"]["train"]["row_end_exclusive"],
            )
            self.assertEqual(
                b["validation"]["row_end_exclusive"], b["test"]["row_start"]
            )
            self.assertLessEqual(
                b["test"]["row_end_exclusive"],
                primary["boundaries"]["validation"]["row_end_exclusive"],
            )
            self.assertTrue(
                all(
                    i + 20 < b["test"]["row_end_exclusive"]
                    for i in manifest["origins"]["test"]
                )
            )
            self.assertEqual(manifest["dataset_info"]["usage"], "exploratory_only")

    @unittest.skipUnless(
        importlib.util.find_spec("torch") and (ROOT / ".vendor/Kronos/model").exists(),
        "Optional native model dependencies",
    )
    def test_candidate_ablation_refuses_primary_scope_before_loading_weights(self):
        from candidate_ablation import run_candidate_ablation

        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temporary:
            out = Path(temporary)
            atomic_json(
                out / "primary.json",
                {
                    "dataset_info": {
                        "usage": "primary",
                        "audit_status": "accepted_provider_scope",
                    }
                },
            )
            with self.assertRaisesRegex(ValueError, "Exploratory"):
                run_candidate_ablation({"device": "cuda:0", "epochs": 5}, out, 42)


if __name__ == "__main__":
    unittest.main()

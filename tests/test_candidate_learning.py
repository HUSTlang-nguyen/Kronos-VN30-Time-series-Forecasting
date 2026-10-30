"""Learning controls preserve nested budgets and choose learning rate before test."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / "experiments"),
    str(ROOT / "scripts"),
    str(ROOT / "src"),
    str(ROOT / "tests"),
]
from candidate_learning import jobs, winning_trial
from research_protocol import budget_origins
from vn30_forecast import split_manifest
from test_research import frame


class CandidateLearningTests(unittest.TestCase):
    def test_full_matrix_and_exact_main_reuse(self):
        config = json.loads((ROOT / "configs/pc_rerun.json").read_text())
        matrix = jobs(config)
        self.assertEqual(len(matrix), 36)
        self.assertEqual({j["seed"] for j in matrix}, {42, 43, 44})
        self.assertEqual(
            sum(
                j["budget"] is None and j["initialization"] == "pretrained"
                for j in matrix
            ),
            6,
        )
        self.assertEqual(
            sum(j["initialization"] == "random" for j in matrix)
            * len(config["random_learning_rates"]),
            54,
        )
        self.assertEqual(
            len(
                {
                    (j["model"], j["seed"], j["budget"], j["initialization"])
                    for j in matrix
                }
            ),
            36,
        )

    def test_nested_budgets_share_train_end_and_holdouts(self):
        manifest = split_manifest(frame(2271), "synthetic")
        small, medium, full = [budget_origins(manifest, n) for n in (500, 1000, None)]
        self.assertEqual([len(small), len(medium), len(full)], [353, 853, 1442])
        self.assertTrue(set(small) < set(medium) < set(full))
        self.assertEqual(small[-1], full[-1])
        self.assertLess(
            full[-1] + 20, manifest["boundaries"]["validation"]["row_start"]
        )

    def test_winning_lr_uses_validation_and_rejects_ambiguous_trials(self):
        trials = [
            {"learning_rate": lr, "validation_loss": loss, "checkpoint": str(i)}
            for i, (lr, loss) in enumerate([(1e-6, 2), (1e-5, 1), (1e-4, 3)])
        ]
        self.assertEqual(winning_trial(trials)["checkpoint"], "1")
        with self.assertRaises(ValueError):
            winning_trial([trials[0], trials[0]])
        with self.assertRaises(ValueError):
            winning_trial([{**trials[0], "validation_loss": float("nan")}])


if __name__ == "__main__":
    unittest.main()

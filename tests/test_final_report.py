"""Independent postprocessing: temporal isolation, failed trials and portability."""
import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from finalize_pc_report import moving_interval, pick_trial, volatility, validate_publisher_case
from verify_completed_candidate import portable


class FinalReportTests(unittest.TestCase):
    def test_adjudication_rejects_wrong_symbol_date_semantics_value_or_hash(self):
        case = dict(symbol="VN30", field="close", date="2020-01-02", market_date="2020-01-02", semantics="session_close", evidence_locator="cash index table", evidence_sha256="a" * 64, value=1000.0)
        validate_publisher_case(case, 1000.0, "a" * 64)
        for key, value in (("symbol", "VN30F1M"), ("market_date", "2020-01-03"), ("semantics", "table_candidate"), ("evidence_sha256", "b" * 64), ("value", 999.0)):
            with self.assertRaises(ValueError):
                validate_publisher_case({**case, key: value}, 1000.0, "a" * 64)

    def test_block_bootstrap_preserves_constant_paired_difference(self):
        np.testing.assert_allclose(moving_interval(np.full(43, -2.5)), [-2.5, -2.5])
        with self.assertRaises(ValueError):
            moving_interval([0.0, np.nan])

    def test_moving_blocks_match_literal_resampling(self):
        delta = np.arange(47, dtype=float) ** 2
        rng = np.random.default_rng(42)
        values = []
        for _ in range(2000):
            pieces = [delta[start:start + 20] for start in rng.integers(0, 28, size=3)]
            values.append(np.concatenate(pieces)[:47].mean())
        np.testing.assert_allclose(moving_interval(delta), np.quantile(values, [0.025, 0.975]))

    def test_future_test_changes_do_not_change_train_cutoff_or_past_regimes(self):
        data = pd.DataFrame(dict(date=pd.date_range("2020-01-01", periods=100).strftime("%Y-%m-%d"), close=np.exp(np.cumsum(0.001 + 0.01 * np.sin(np.arange(100))))))
        manifest = dict(boundaries=dict(train=dict(row_start=0, row_end_exclusive=50)), origins=dict(test=list(range(60, 80))))
        before, cutoff = volatility(data, manifest)
        changed = data.copy()
        changed.loc[75:, "close"] *= 10
        after, new_cutoff = volatility(changed, manifest)
        self.assertEqual(cutoff, new_cutoff)
        pd.testing.assert_frame_equal(before.iloc[:15], after.iloc[:15])

    def test_incomplete_or_failed_trial_cannot_win(self):
        good = dict(validation_loss=2.0, successful_origins=10, expected_origins=10)
        trials = [dict(validation_loss=0.1, successful_origins=9, expected_origins=10), dict(validation_loss=0.01, status="failed"), good]
        self.assertIs(pick_trial(trials), good)

    def test_receipts_rebase_foreign_host_paths_without_traversal(self):
        target = ROOT / "artifacts/local/example.csv"
        self.assertEqual(portable("Z:/old/" + ROOT.name + "/artifacts/local/example.csv"), target)
        self.assertEqual(portable("/old/" + ROOT.name + "/artifacts/local/example.csv"), target)
        self.assertEqual(portable("artifacts\\local\\example.csv"), target)
        for path in ("../outside.csv", "Z:/unknown/private.csv"):
            with self.assertRaises(ValueError):
                portable(path)


if __name__ == "__main__":
    unittest.main()

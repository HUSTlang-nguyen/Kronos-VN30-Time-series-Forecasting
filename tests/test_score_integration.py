"""A complete comparison and its cached artifacts must keep their provenance."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]
import pandas as pd
import test_forecast_protocol as protocol_fixture
from test_research import frame
from research_protocol import atomic_json, file_hash
from forecast_protocol import sampling_spec
from run_experiment import matrix
from experiment_tasks import score_group


@unittest.skipUnless(
    importlib.util.find_spec("matplotlib"), "Optional plotting dependency"
)
class ScoreIntegrationTests(unittest.TestCase):
    def test_complete_comparison_then_reject_modified_score_and_forecast(self):
        fixture = protocol_fixture.ForecastProtocolTests()
        fixture.setUp()
        try:
            out = fixture.out
            config = fixture.config
            manifest = fixture.manifest
            df = frame(1000)
            tasks = matrix(config)
            by_id = {t["id"]: t for t in tasks}
            group = by_id["main-kronos-small-s43-score"]
            locks = {
                "ridge": {"alpha": 10},
                "arima": {"order": [0, 1, 0]},
                "ets": {"trend": None, "damped_trend": False},
            }
            for name, value in locks.items():
                atomic_json(out / "tuning" / (name + ".json"), value)
            paths = []
            for key in group["forecasts"]:
                task = by_id[key]
                name = task["model"]
                split = task["split"]
                rows = []
                for i in manifest["origins"][split]:
                    for h in range(1, 21):
                        rows.append(
                            {
                                "origin_index": i,
                                "origin_date": df.date.iloc[i],
                                "target_date": df.date.iloc[i + h],
                                "horizon": h,
                                **{
                                    "pred_" + c: float(df.close.iloc[i])
                                    for c in ("open", "high", "low", "close")
                                },
                            }
                        )
                path = out / "forecasts" / (key + ".csv")
                path.parent.mkdir(exist_ok=True)
                pd.DataFrame(rows).to_csv(path, index=False)
                meta = {
                    **fixture.meta,
                    "model": name,
                    "split": split,
                    "seed": task["seed"],
                    "origins": manifest["origin_counts"][split],
                    "sampling": sampling_spec(name),
                    "model_config": locks.get(name, {}),
                    "forecast_csv_sha256": file_hash(path),
                }
                if not name.endswith("-ft"):
                    meta["checkpoint"] = None
                if name == "kronos-small":
                    meta["revision"] = fixture.provenance["models"]["kronos_small"][
                        "repository_revision"
                    ]
                if name in ("naive", "ridge", "arima", "ets"):
                    meta.update(
                        device="cpu", sample_count=0, point_functional="deterministic"
                    )
                    meta["revision"] = (
                        "last_close"
                        if name == "naive"
                        else "ridge_train_only_alpha10"
                        if name == "ridge"
                        else "validation_locked:"
                        + json.dumps(locks[name], sort_keys=True)
                    )
                atomic_json(path.with_suffix(".json"), meta)
                paths.append(path)
            with patch(
                "vn30_forecast.load_manifest_data",
                return_value=(df, manifest["sha256"]),
            ):
                score_group(config, out, group)
                score_group(config, out, group)  # verified reuse is valid
                score = out / "evaluation" / group["group"] / "test/scores.csv"
                original = score.read_bytes()
                score.write_bytes(original + b"\n")
                with self.assertRaisesRegex(ValueError, "artifacts changed"):
                    score_group(config, out, group)
                score.write_bytes(original)
                paths[0].write_bytes(paths[0].read_bytes() + b"\n")
                with self.assertRaisesRegex(ValueError, "metadata checksum"):
                    score_group(config, out, group)
        finally:
            fixture.tearDown()


if __name__ == "__main__":
    unittest.main()

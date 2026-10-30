import copy
import csv
import io
import json
import threading
import time
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from demo.app import create_app
from demo.runtime import DEMO, DemoError, Engine, Jobs, Sample


class FakeEngine:
    preferred = "cpu"

    def __init__(self, gate=None):
        self.registry = json.loads((DEMO / "registry.json").read_text())["models"]
        self.gate, self.calls, self.threads = gate, [], set()

    def predict(self, model, past, dates, progress):
        self.calls.append((model, past.copy(), list(dates)))
        self.threads.add(threading.get_ident())
        progress("running")
        if self.gate:
            self.gate.wait(5)
        # Unit-test stub only: the production app always constructs the real Engine.
        return dict(predictions=[dict(date=d, step=i + 1, open=float(past.close.iloc[-1]), high=2000.0, low=1000.0, close=float(past.close.iloc[-1])) for i, d in enumerate(dates)], device="cpu", device_name="CPU", elapsed_seconds=0.01, fallback_reason=None)


class DemoTests(unittest.TestCase):
    def test_every_origin_has_exact_context_and_full_observed_calendar(self):
        sample = Sample()
        self.assertEqual(len(sample.origins), 323)
        for origin in sample.origins:
            past, future = sample.window(origin)
            self.assertEqual(len(past), 128)
            self.assertEqual(past.date.iloc[-1], origin)
            self.assertEqual(len(future), 20)
            self.assertTrue(all(d > origin for d in future))
        with self.assertRaises(DemoError):
            sample.window("2026-10-01")

    def test_future_prices_do_not_enter_model_inputs(self):
        sample = Sample()
        origin = list(sample.origins)[20]
        before, dates = sample.window(origin)
        sample.frame.loc[sample.frame.date > origin, ["open", "high", "low", "close"]] *= 100
        after, new_dates = sample.window(origin)
        pd.testing.assert_frame_equal(before, after)
        self.assertEqual(dates, new_dates)

    def test_rejects_model_hash_and_missing_weights(self):
        engine = Engine()
        spec = copy.deepcopy(engine.registry["kronos-mini"])
        spec["files"]["config.json"] = "0" * 64
        with self.assertRaisesRegex(DemoError, "MODEL_HASH"):
            engine.resolve(spec)
        spec["local_path"] = "models/not-present"
        # This case tests a missing unpublished model; published models download by revision.
        spec["hub_repo"], spec["hub_revision"] = None, None
        with self.assertRaisesRegex(DemoError, "MODEL_MISSING"):
            engine.resolve(spec)
        spec["local_path"] = "../outside"
        with self.assertRaisesRegex(DemoError, "MODEL_HASH"):
            engine.resolve(spec)

    def test_queue_is_bounded_deduplicated_and_serial(self):
        sample, gate = Sample(), threading.Event()
        engine = FakeEngine(gate)
        jobs = Jobs(sample, engine)
        origins = list(sample.origins)
        try:
            first = jobs.submit("kronos-small", origins[0])
            duplicate = jobs.submit("kronos-small", origins[0])
            self.assertEqual(first["id"], duplicate["id"])
            for origin in origins[1:4]:
                jobs.submit("kronos-small", origin)
            with self.assertRaisesRegex(DemoError, "BUSY"):
                jobs.submit("kronos-small", origins[4])
        finally:
            gate.set()
            jobs.pool.shutdown(wait=True)
        self.assertEqual(len(engine.calls), 4)
        self.assertEqual(len(engine.threads), 1)

    def test_api_validation_job_and_csv_match(self):
        sample, engine = Sample(), FakeEngine()
        app = create_app(sample, engine)
        with TestClient(app) as client:
            catalog = client.get("/api/catalog").json()
            origin = catalog["default_origin"]
            history = client.get("/api/history/" + origin).json()
            self.assertNotIn("actual", history)
            self.assertEqual(len(history["history"]), 128)
            self.assertEqual(client.post("/api/forecasts", json=dict(model_id="invalid", origin=origin)).status_code, 422)
            self.assertEqual(client.post("/api/forecasts", json=dict(model_id="kronos-mini", origin=origin, checkpoint="any")).status_code, 422)
            response = client.post("/api/forecasts", json=dict(model_id="kronos-mini", origin=origin))
            self.assertEqual(response.status_code, 202)
            key = response.json()["id"]
            for _ in range(100):
                job = client.get("/api/jobs/" + key).json()
                if job["status"] == "complete":
                    break
                time.sleep(0.01)
            self.assertEqual(job["status"], "complete")
            export = client.get(f"/api/jobs/{key}/forecast.csv")
            rows = list(csv.DictReader(io.StringIO(export.text)))
            self.assertEqual(len(rows), 20)
            for row, prediction in zip(rows, job["result"]["predictions"]):
                self.assertEqual(row["date"], prediction["date"])
                self.assertEqual(float(row["close"]), prediction["close"])
            self.assertEqual(client.get("/api/reference/" + origin).json()["actual"], sample.reference(origin))
            self.assertEqual(client.get("/api/jobs/nonexistent").status_code, 404)
            self.assertEqual(engine.calls[0][1].date.iloc[-1], origin)

    def test_cuda_oom_replays_whole_job_on_cpu(self):
        import torch
        sample, engine = Sample(), Engine()
        past, dates = sample.window(list(sample.origins)[-1])
        devices = []

        class Predictor:
            def __init__(self, device): self.device = device
            def predict(self, history, *args, **kwargs):
                if self.device.startswith("cuda"):
                    raise torch.cuda.OutOfMemoryError("unit test")
                return pd.DataFrame(np.full((20, 4), 1500.0), columns=["open", "high", "low", "close"])

        def load(model, device):
            devices.append(device)
            engine.predictor = Predictor(device)

        with patch.object(torch.cuda, "is_available", return_value=True), patch.object(torch.cuda, "empty_cache"), patch.object(torch.cuda, "manual_seed_all"), patch.object(engine, "load", side_effect=load):
            result = engine.predict("kronos-small", past, dates, lambda status: None)
        self.assertEqual(devices, ["cuda:0", "cpu"])
        self.assertEqual(result["device"], "cpu")
        self.assertEqual(result["fallback_reason"], "cuda_out_of_memory")
        self.assertEqual(len(result["predictions"]), 20)


if __name__ == "__main__":
    unittest.main()

"""Validated data slicing, pinned model loading and serial local inference."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import gc
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import uuid
import sys

import numpy as np
import pandas as pd

DEMO = Path(__file__).resolve().parent
COLS = ["open", "high", "low", "close"]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class DemoError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


class Sample:
    def __init__(self, folder=DEMO):
        self.folder = Path(folder)
        self.manifest = json.loads((self.folder / "data/manifest.json").read_text())
        if sha(self.folder / "data/vn30.csv") != self.manifest["csv_sha256"]:
            raise DemoError("DATA_HASH")
        self.frame = pd.read_csv(self.folder / "data/vn30.csv")
        if self.frame.date.duplicated().any() or not self.frame.date.is_monotonic_increasing or not np.isfinite(self.frame[COLS]).all().all():
            raise DemoError("INVALID_DATA")
        self.origins = {self.frame.date.iloc[i]: i for i in self.manifest["origins"]}
        for i in self.origins.values():
            if i < 127 or i + 20 >= len(self.frame):
                raise DemoError("INVALID_ORIGIN")

    def window(self, origin):
        if origin not in self.origins:
            raise DemoError("INVALID_ORIGIN")
        i = self.origins[origin]
        past = self.frame.iloc[i - 127:i + 1].copy()
        future_dates = self.frame.date.iloc[i + 1:i + 21].tolist()
        return past, future_dates

    def reference(self, origin):
        i = self.origins.get(origin)
        if i is None:
            raise DemoError("INVALID_ORIGIN")
        return self.frame.iloc[i + 1:i + 21].to_dict("records")


class Engine:
    def __init__(self, folder=DEMO, preferred="auto"):
        self.folder = Path(folder)
        self.registry = json.loads((self.folder / "registry.json").read_text())["models"]
        self.preferred = preferred
        self.active = None
        self.predictor = None

    def resolve(self, spec, tokenizer=False):
        from huggingface_hub import snapshot_download
        item = spec["tokenizer"] if tokenizer else spec
        local = (self.folder / item["local_path"]).resolve()
        if not local.is_relative_to(self.folder):
            raise DemoError("MODEL_HASH")
        if not (local / "model.safetensors").is_file():
            repo = item["repository"] if tokenizer else item.get("hub_repo")
            revision = item["revision"] if tokenizer else item.get("hub_revision")
            if not repo or not revision:
                raise DemoError("MODEL_MISSING")
            local = Path(snapshot_download(repo, revision=revision, allow_patterns=list(item["files"]), cache_dir=self.folder / "cache/hub"))
        for name, expected in item["files"].items():
            target = local / name
            if not target.is_file() or sha(target) != expected:
                raise DemoError("MODEL_HASH")
        return local

    def unload(self):
        self.predictor, self.active = None, None
        gc.collect()
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def load(self, model_id, device):
        import torch
        if self.active == (model_id, device):
            return
        self.unload()
        spec = self.registry[model_id]
        vendor = self.folder / "vendor/kronos"
        code = json.loads((vendor / "manifest.json").read_text())
        for name, expected in code["normalized_lf_sha256"].items():
            if hashlib.sha256((vendor / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() != expected:
                raise DemoError("CODE_HASH")
        sys.path.insert(0, str(vendor))
        from model import Kronos, KronosTokenizer, KronosPredictor
        tokenizer = KronosTokenizer.from_pretrained(str(self.resolve(spec, True))).eval()
        model = Kronos.from_pretrained(str(self.resolve(spec))).eval()
        if (model.s1_bits, model.s2_bits) != (tokenizer.s1_bits, tokenizer.s2_bits):
            raise DemoError("TOKENIZER_MISMATCH")
        self.predictor = KronosPredictor(model, tokenizer, device=device, max_context=2048 if spec["variant"] == "mini" else 512)
        self.active = (model_id, device)

    def predict(self, model_id, past, future_dates, progress):
        import torch
        torch.set_num_threads(4)
        device = "cuda:0" if self.preferred != "cpu" and torch.cuda.is_available() else "cpu"
        reason = "cuda_unavailable" if device == "cpu" and self.preferred != "cpu" else None
        started = time.perf_counter()
        for attempt in range(2):
            try:
                progress("loading")
                self.load(model_id, device)
                progress("running")
                torch.manual_seed(42)
                if device.startswith("cuda"):
                    torch.cuda.manual_seed_all(42)
                history = past[COLS].copy()
                history["volume"], history["amount"] = 0.0, 0.0
                with torch.inference_mode():
                    result = self.predictor.predict(history, pd.to_datetime(past.date), pd.Series(pd.to_datetime(future_dates)), pred_len=20, T=1.0, top_p=0.9, sample_count=3, verbose=False)
                values = result[COLS].to_numpy(dtype=float)
                if values.shape != (20, 4) or not np.isfinite(values).all():
                    raise DemoError("INVALID_FORECAST")
                rows = [dict(date=date, step=i + 1, **{name: float(values[i, j]) for j, name in enumerate(COLS)}) for i, date in enumerate(future_dates)]
                return dict(predictions=rows, elapsed_seconds=round(time.perf_counter() - started, 3), device=device, device_name=torch.cuda.get_device_name(0) if device.startswith("cuda") else "CPU", fallback_reason=reason, seed=42, sample_count=3, context=128, horizon=20, precision="float32", checkpoint_sha256=self.registry[model_id]["files"]["model.safetensors"])
            except torch.cuda.OutOfMemoryError:
                self.unload()
                if device == "cpu" or attempt:
                    raise DemoError("OUT_OF_MEMORY")
                device, reason = "cpu", "cuda_out_of_memory"
        raise DemoError("INFERENCE_FAILED")


class Jobs:
    def __init__(self, sample, engine):
        self.sample, self.engine = sample, engine
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="vn30-inference")
        self.lock = threading.Lock()
        self.items = {}

    def submit(self, model_id, origin):
        if model_id not in self.engine.registry:
            raise DemoError("INVALID_MODEL")
        self.sample.window(origin)
        with self.lock:
            active = [j for j in self.items.values() if j["status"] in ("queued", "loading", "running")]
            for item in active:
                if item["model_id"] == model_id and item["origin"] == origin:
                    return dict(item)
            if len(active) >= 4:
                raise DemoError("BUSY")
            for key in list(self.items):
                if len(self.items) < 30:
                    break
                if self.items[key]["status"] in ("complete", "error"):
                    del self.items[key]
            key = uuid.uuid4().hex
            self.items[key] = dict(id=key, model_id=model_id, origin=origin, status="queued", created_at=time.time())
        self.pool.submit(self._run, key)
        return self.get(key)

    def _run(self, key):
        def progress(status):
            with self.lock:
                self.items[key]["status"] = status
        try:
            item = self.get(key)
            past, future_dates = self.sample.window(item["origin"])
            result = self.engine.predict(item["model_id"], past, future_dates, progress)
            with self.lock:
                self.items[key].update(status="complete", result=result)
        except Exception as exc:
            import logging
            logging.getLogger("vn30").exception("Inference job failed")
            with self.lock:
                self.items[key].update(status="error", error=exc.code if isinstance(exc, DemoError) else "INFERENCE_FAILED")

    def get(self, key):
        with self.lock:
            if key not in self.items:
                raise DemoError("JOB_NOT_FOUND")
            return dict(self.items[key])

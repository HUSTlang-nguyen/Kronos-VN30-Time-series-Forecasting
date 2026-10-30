"""Opt-in GPU/native checkpoint replay; synthetic data, never research results."""

import contextlib
import gc
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "tests")]


@unittest.skipUnless(
    os.environ.get("VN30_NATIVE_GPU_TEST") == "1" and importlib.util.find_spec("torch"),
    "Opt-in native GPU check",
)
class NativeResumeTests(unittest.TestCase):
    def test_kronos_mini_native_gpu_resume_matches_full_run(self):
        import numpy as np
        import torch
        import finetune_vn30 as trainer
        from safetensors.torch import load_file
        from test_research import frame, TEMP_ROOT
        from vn30_forecast import split_manifest
        from research_protocol import atomic_json

        if not torch.cuda.is_available():
            self.skipTest("CUDA unavailable")
        df = frame()
        manifest = split_manifest(df, "synthetic_native_resume_only")
        counter = {"n": 0, "interrupt": False}
        real_setup = trainer.setup_kronos

        def setup(*args, **kwargs):
            model, batches, loss, save, objective = real_setup(*args, **kwargs)

            def wrapped(batch):
                counter["n"] += 1
                if counter["interrupt"] and counter["n"] == 30:
                    raise TimeoutError("simulated native interruption")
                return loss(batch)

            return model, batches, wrapped, save, objective

        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temporary:
            folder = Path(temporary)
            path = folder / "split.json"
            atomic_json(path, manifest)

            def run(name, resume=False):
                argv = [
                    "finetune",
                    "--manifest",
                    str(path),
                    "--model",
                    "kronos-mini",
                    "--device",
                    "cuda:0",
                    "--epochs",
                    "2",
                    "--output",
                    str(folder / name),
                ]
                if resume:
                    argv.append("--resume")
                with (
                    patch.object(sys, "argv", argv),
                    patch.object(
                        trainer,
                        "load_manifest_data",
                        return_value=(df, manifest["sha256"]),
                    ),
                    patch.object(trainer, "setup_kronos", side_effect=setup),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    trainer.main()
                gc.collect()
                torch.cuda.empty_cache()

            with patch.dict(os.environ, {"VN30_DEADLINE_UNIX": "inf"}):
                run("reference")
                counter.update(n=0, interrupt=True)
                with self.assertRaises(TimeoutError):
                    run("resumed")
                gc.collect()
                torch.cuda.empty_cache()
                counter.update(n=0, interrupt=False)
                run("resumed", True)
            a = load_file(str(folder / "reference/best/model.safetensors"))
            b = load_file(str(folder / "resumed/best/model.safetensors"))
            delta = max(float((a[k] - b[k]).abs().max()) for k in a)
            self.assertLessEqual(delta, 1e-6)
            first = json.loads((folder / "reference/training.json").read_text())
            second = json.loads((folder / "resumed/training.json").read_text())
            self.assertTrue(
                np.isclose(
                    first["best_validation_loss"],
                    second["best_validation_loss"],
                    rtol=1e-6,
                    atol=1e-7,
                )
            )
            atomic_json(
                ROOT / "artifacts/local/pc-preflight-20261030/native_resume_smoke.json",
                {
                    "classification": "synthetic_gpu_integration_not_research_results",
                    "model": "kronos-mini",
                    "gpu": torch.cuda.get_device_name(0),
                    "status": "pass",
                    "maximum_parameter_delta": delta,
                    "reference_validation_loss": first["best_validation_loss"],
                    "resumed_validation_loss": second["best_validation_loss"],
                    "interrupted_after_completed_epoch": 1,
                    "epochs": 2,
                },
            )


if __name__ == "__main__":
    unittest.main()

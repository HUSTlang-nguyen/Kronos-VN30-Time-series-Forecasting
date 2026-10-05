from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[1]
SMOKE_OUTPUT = ROOT / "artifacts" / "smoke" / "phase0_model_smoke.json"

CHRONOS_MODEL = "autogluon/chronos-2-small"
CHRONOS_REVISION = "ddec01313e50b6bc58ebaa92ede81bc24a3d9f9a"
KRONOS_MODEL = "NeoQuasar/Kronos-small"
KRONOS_REVISION = "901c26c1332695a2a8f243eb2f37243a37bea320"
KRONOS_TOKENIZER = "NeoQuasar/Kronos-Tokenizer-base"
KRONOS_TOKENIZER_REVISION = "0e0117387f39004a9016484a186a908917e22426"
KRONOS_CODE_REVISION = "67b630e67f6a18c9e9be918d9b4337c960db1e9a"


def choose_device(requested: str) -> str:
    if requested != "auto":
        return requested
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def synthetic_ohlc(length: int = 128) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    close = 1200.0 + np.cumsum(rng.normal(0.2, 3.0, size=length))
    open_ = close + rng.normal(0.0, 1.2, size=length)
    high = np.maximum(open_, close) + rng.uniform(0.2, 2.5, size=length)
    low = np.minimum(open_, close) - rng.uniform(0.2, 2.5, size=length)
    return pd.DataFrame(
        {
            "open": open_.astype(np.float32),
            "high": high.astype(np.float32),
            "low": low.astype(np.float32),
            "close": close.astype(np.float32),
            "volume": np.zeros(length, dtype=np.float32),
            "amount": np.zeros(length, dtype=np.float32),
        }
    )


def smoke_chronos2(device: str) -> dict:
    from chronos import BaseChronosPipeline

    started = time.perf_counter()
    frame = synthetic_ohlc()
    inputs = torch.from_numpy(frame[["open", "high", "low", "close"]].to_numpy().T).unsqueeze(0)
    pipeline = BaseChronosPipeline.from_pretrained(
        CHRONOS_MODEL,
        revision=CHRONOS_REVISION,
        device_map=device,
        torch_dtype=torch.float32,
    )
    with torch.inference_mode():
        outputs = pipeline.predict(inputs, prediction_length=20)

    assert len(outputs) == 1
    output = outputs[0]
    assert tuple(output.shape)[0] == 4
    assert tuple(output.shape)[-1] == 20
    assert bool(torch.isfinite(output).all())
    return {
        "status": "pass",
        "device": device,
        "model": CHRONOS_MODEL,
        "revision": CHRONOS_REVISION,
        "input_shape": list(inputs.shape),
        "output_shape": list(output.shape),
        "finite": True,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }


def smoke_kronos(device: str) -> dict:
    vendor = ROOT / ".vendor" / "Kronos"
    if not (vendor / "model" / "kronos.py").exists():
        raise FileNotFoundError("Run python scripts/bootstrap_kronos.py before the Kronos smoke test")
    sys.path.insert(0, str(vendor))
    from model import Kronos, KronosPredictor, KronosTokenizer

    started = time.perf_counter()
    frame = synthetic_ohlc()
    history_dates = pd.Series(pd.bdate_range("2025-01-02", periods=len(frame)))
    future_dates = pd.Series(pd.bdate_range(history_dates.iloc[-1] + pd.Timedelta(days=1), periods=20))

    tokenizer = KronosTokenizer.from_pretrained(
        KRONOS_TOKENIZER,
        revision=KRONOS_TOKENIZER_REVISION,
    )
    model = Kronos.from_pretrained(KRONOS_MODEL, revision=KRONOS_REVISION)
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
    prediction = predictor.predict(
        df=frame,
        x_timestamp=history_dates,
        y_timestamp=future_dates,
        pred_len=20,
        T=1.0,
        top_p=0.9,
        sample_count=1,
        verbose=False,
    )

    assert prediction.shape[0] == 20
    assert set(["open", "high", "low", "close"]).issubset(prediction.columns)
    assert bool(np.isfinite(prediction[["open", "high", "low", "close"]].to_numpy()).all())
    return {
        "status": "pass",
        "device": device,
        "model": KRONOS_MODEL,
        "revision": KRONOS_REVISION,
        "tokenizer": KRONOS_TOKENIZER,
        "tokenizer_revision": KRONOS_TOKENIZER_REVISION,
        "code_revision": KRONOS_CODE_REVISION,
        "input_shape": [len(frame), 6],
        "output_shape": list(prediction.shape),
        "finite": True,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }


def release_memory() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["all", "chronos2", "kronos"], default="all")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output", type=Path, default=SMOKE_OUTPUT)
    args = parser.parse_args()

    torch.manual_seed(42)
    np.random.seed(42)
    device = choose_device(args.device)
    selected = ["chronos2", "kronos"] if args.model == "all" else [args.model]
    result = {
        "schema_version": 1,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "requested_device": args.device,
        "resolved_device": device,
        "models": {},
    }

    failed = False
    for name in selected:
        try:
            result["models"][name] = smoke_chronos2(device) if name == "chronos2" else smoke_kronos(device)
        except Exception as exc:
            failed = True
            result["models"][name] = {
                "status": "fail",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        finally:
            release_memory()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

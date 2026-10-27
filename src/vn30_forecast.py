"""Pinned VN30 data, chronological origins and model adapters."""

from __future__ import annotations
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite"
RECEIPT = ROOT / "data/manifests/vndirect_sqlite_snapshot.json"
COLS = ["open", "high", "low", "close"]
FLAGS = ["duplicate_date", "invalid_numeric", "invalid_ohlc", "outside_request"]
CONTEXT, HORIZON = 128, 20


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load(path=DATA):
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if not path.is_file():
        raise FileNotFoundError(f"{path}: run dvc pull")
    sha = digest(path)
    if sha != receipt["database_sha256"]:
        raise ValueError("SQLite SHA256 differs from pinned receipt")
    con = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        if con.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise ValueError("SQLite integrity failed")
        df = pd.read_sql_query(
            "SELECT row_id,date,open,high,low,close,duplicate_date,invalid_numeric,invalid_ohlc,outside_request FROM candles ORDER BY date,row_id",
            con,
        )
    finally:
        con.close()
    snapshot = receipt["snapshot"]
    if (len(df), df.date.iloc[0], df.date.iloc[-1]) != (
        snapshot["rows"],
        snapshot["first_date"],
        snapshot["last_date"],
    ):
        raise ValueError("Dataset shape/date mismatch")
    if df.date.duplicated().any() or not df.date.is_monotonic_increasing:
        raise ValueError("Duplicate/unsorted sessions")
    values = df[COLS].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Non-finite/nonpositive price")
    if (df.high < df[["open", "close", "low"]].max(axis=1)).any() or (
        df.low > df[["open", "close", "high"]].min(axis=1)
    ).any():
        raise ValueError("Invalid OHLC")
    for flag in FLAGS:
        if (
            not df[flag].isin([0, 1]).all()
            or int(df[flag].sum()) != snapshot["quality_counts"][flag]
        ):
            raise ValueError(f"{flag} flags differ")
    df["session_date"] = pd.to_datetime(df.date)
    return df, sha


def split_manifest(df, sha):
    n = len(df)
    train = int(n * 0.70)
    val = train + int(n * 0.15)
    ranges = {"train": (0, train), "validation": (train, val), "test": (val, n)}
    origins = {
        s: list(range(max(CONTEXT - 1, a - 1), b - HORIZON))
        for s, (a, b) in ranges.items()
    }
    assert all(origins.values())
    return {
        "schema_version": 1,
        "dataset": str(DATA.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha,
        "rows": n,
        "context": CONTEXT,
        "horizon": HORIZON,
        "rule": "chronological_70_15_15_floor",
        "boundaries": {
            s: {
                "row_start": a,
                "row_end_exclusive": b,
                "first_date": df.date.iloc[a],
                "last_date": df.date.iloc[b - 1],
                "rows": b - a,
            }
            for s, (a, b) in ranges.items()
        },
        "origins": origins,
        "origin_counts": {s: len(v) for s, v in origins.items()},
        "origin_definition": "after close t; full future path in split",
        "calendar_note": "realized historical exchange dates supplied to Kronos",
    }


def check_manifest(df, sha, manifest):
    if manifest != split_manifest(df, sha):
        raise ValueError("Split manifest differs from fixed dataset/rule")
    for split, origins in manifest["origins"].items():
        a = manifest["boundaries"][split]["row_start"]
        b = manifest["boundaries"][split]["row_end_exclusive"]
        assert all(i >= CONTEXT - 1 and i + 1 >= a and i + HORIZON < b for i in origins)


def build_model(name, df, manifest, device, checkpoint=None):
    revision_override = None
    if name.endswith("-ft"):
        if checkpoint is None:
            raise ValueError("Fine-tuned models require --checkpoint")
        checkpoint = Path(checkpoint)
        trained = json.loads((checkpoint / "training.json").read_text(encoding="utf-8"))
        base_name = name.removesuffix("-ft")
        if (
            trained["dataset_sha256"] != manifest["sha256"]
            or trained["base_model"] != base_name
            or trained["context"] != CONTEXT or trained["horizon"] != HORIZON
            or trained["boundaries"] != manifest["boundaries"]
            or trained["test_used_for_training_or_selection"]
            or (base_name == "kronos" and not trained.get("teacher_forcing_causal_validation", False))
        ):
            raise ValueError("Fine-tuned checkpoint has a different dataset/split/protocol")
        files = trained["checkpoint_files"]
        if not files or "model.safetensors" not in files:
            raise ValueError("Missing checkpoint weight hash")
        best = (checkpoint / "best").resolve()
        for relative, expected in files.items():
            path = (best / relative).resolve()
            if not path.is_relative_to(best) or digest(path) != expected:
                raise ValueError(f"Checkpoint hash mismatch: {relative}")
        revision_override = "finetuned:" + files["model.safetensors"]
        name = base_name
    elif checkpoint is not None:
        raise ValueError("--checkpoint is only valid for fine-tuned models")
    if name == "naive":
        return (
            lambda history, dates, seed: np.full((HORIZON, 4), history[-1, 3]),
            "last_close",
            0,
        )
    if name == "ridge":
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import StandardScaler

        raw = df[COLS].to_numpy(dtype=np.float64)
        end = manifest["boundaries"]["train"]["row_end_exclusive"]
        xs = np.stack(
            [
                raw[i - CONTEXT + 1 : i + 1].ravel()
                for i in range(CONTEXT - 1, end - HORIZON)
            ]
        )
        ys = np.stack(
            [
                raw[i + 1 : i + HORIZON + 1].ravel()
                for i in range(CONTEXT - 1, end - HORIZON)
            ]
        )
        sx, sy = StandardScaler().fit(xs), StandardScaler().fit(ys)
        model = Ridge(alpha=100.0).fit(sx.transform(xs), sy.transform(ys))

        def predict(history, dates, seed):
            return sy.inverse_transform(
                model.predict(sx.transform(history.ravel()[None, :]))
            ).reshape(HORIZON, 4)

        return predict, "ridge_train_only_alpha100", 0
    import torch
    import yaml

    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_text(encoding="utf-8")
    )
    if revision_override:
        base_spec = provenance["models"]["chronos_2_small" if name == "chronos2" else "kronos_small"]
        if trained["base_revision"] != base_spec["repository_revision"]:
            raise ValueError("Fine-tuning started from a different pretrained revision")
    if name == "chronos2":
        from chronos import BaseChronosPipeline

        spec = provenance["models"]["chronos_2_small"]
        pipeline = BaseChronosPipeline.from_pretrained(
            str(best) if revision_override else spec["repository"],
            **({} if revision_override else {"revision": spec["repository_revision"]}),
            device_map=device,
            torch_dtype=torch.float32,
        )

        def predict(history, dates, seed):
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
            with torch.inference_mode():
                samples = pipeline.predict(
                    torch.tensor(history.T[None, :, :], dtype=torch.float32),
                    prediction_length=HORIZON,
                )[0]
            return samples.float().mean(dim=1).cpu().numpy().T

        return predict, revision_override or spec["repository_revision"], 13
    if name == "kronos":
        vendor = ROOT / ".vendor/Kronos"
        if not (vendor / "model/kronos.py").exists():
            raise FileNotFoundError("Run scripts/bootstrap_kronos.py first")
        sys.path.insert(0, str(vendor))
        from model import Kronos, KronosPredictor, KronosTokenizer

        model_spec = provenance["models"]["kronos_small"]
        token_spec = provenance["tokenizers"]["kronos_tokenizer_base"]
        tokenizer = KronosTokenizer.from_pretrained(
            token_spec["repository"], revision=token_spec["repository_revision"]
        )
        model = Kronos.from_pretrained(
            str(best) if revision_override else model_spec["repository"],
            **({} if revision_override else {"revision": model_spec["repository_revision"]}),
        )
        model.eval()
        tokenizer.eval()
        predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)

        def predict(history, dates, seed):
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
            xdates, ydates = dates
            candles = pd.DataFrame(history, columns=COLS)
            candles["volume"] = 0.0
            candles["amount"] = 0.0
            result = predictor.predict(
                candles,
                pd.Series(xdates),
                pd.Series(ydates),
                pred_len=HORIZON,
                T=1.0,
                top_p=0.9,
                sample_count=3,
                verbose=False,
            )
            return result[COLS].to_numpy(dtype=np.float64)

        return predict, revision_override or model_spec["repository_revision"], 3
    raise ValueError(name)

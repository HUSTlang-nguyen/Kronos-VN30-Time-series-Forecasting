"""Pinned VN30 data, chronological origins and model adapters."""

from __future__ import annotations
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from research_protocol import MODELS, canonical_model, portable_path

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


def load(path=DATA, receipt_path=RECEIPT):
    path = Path(path)
    receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
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


def split_manifest(df, sha, dataset_info=None, ranges=None):
    n = len(df)
    train = int(n * 0.70)
    val = train + int(n * 0.15)
    ranges = ranges or {
        "train": (0, train),
        "validation": (train, val),
        "test": (val, n),
    }
    origins = {
        s: list(range(max(CONTEXT - 1, a - 1), b - HORIZON))
        for s, (a, b) in ranges.items()
    }
    assert all(origins.values())
    result = {
        "schema_version": 2 if dataset_info else 1,
        "dataset": dataset_info["dataset"]
        if dataset_info
        else str(DATA.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha,
        "rows": n,
        "context": CONTEXT,
        "horizon": HORIZON,
        "rule": "chronological_explicit"
        if dataset_info
        else "chronological_70_15_15_floor",
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
    if dataset_info:
        result["dataset_info"] = dataset_info
    return result


def load_manifest_data(manifest, *, allow_exploratory=False):
    info = manifest.get("dataset_info")
    if not info:
        if allow_exploratory:
            raise ValueError(
                "Exploratory training requires an explicit audited manifest"
            )
        return load()
    if info.get("usage", "primary") not in ("primary", "exploratory_only"):
        raise ValueError("Unknown dataset evidence scope")
    exploratory = info.get("usage") == "exploratory_only"
    if exploratory != allow_exploratory:
        raise ValueError(
            "Exploratory data require explicit opt-in and separate outputs"
        )
    expected_status = "unverified" if exploratory else "accepted_provider_scope"
    if info.get("audit_status") != expected_status:
        raise ValueError("Dataset has not passed its audit; research run refused")
    audit_path = portable_path(info["audit"])
    from research_protocol import file_hash

    if file_hash(audit_path) != info["audit_sha256"]:
        raise ValueError("Audit receipt hash mismatch")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if (
        audit.get("status") != expected_status
        or audit["dataset_sha256"] != manifest["sha256"]
    ):
        raise ValueError("Audit receipt does not accept this dataset")
    if exploratory and (
        any(
            audit.get(key) != "pass"
            for key in (
                "raw_replay",
                "timestamp_timezone_replay",
                "quality_flag_replay",
            )
        )
        or audit.get("invalid_or_duplicate_flags") != 0
        or not audit.get("independent_sources")
        or audit.get("required_dates_without_reference") != []
        or audit.get("price_edits") != []
    ):
        raise ValueError(
            "Candidate integrity/reference checks do not permit exploration"
        )
    return load(portable_path(info["dataset"]), portable_path(info["receipt"]))


def check_manifest(df, sha, manifest):
    info = manifest.get("dataset_info")
    ranges = None
    if info:
        ranges = {
            s: (b["row_start"], b["row_end_exclusive"])
            for s, b in manifest["boundaries"].items()
        }
        parts = list(ranges.values())
        if (
            list(ranges) != ["train", "validation", "test"]
            or parts[0][0] != 0
            or any(a < 0 or b <= a or b > len(df) for a, b in parts)
            or any(parts[i][1] != parts[i + 1][0] for i in (0, 1))
        ):
            raise ValueError("Invalid or overlapping temporal partitions")
    if manifest != split_manifest(df, sha, dataset_info=info, ranges=ranges):
        raise ValueError("Split manifest differs from fixed dataset/rule")
    for split, origins in manifest["origins"].items():
        a = manifest["boundaries"][split]["row_start"]
        b = manifest["boundaries"][split]["row_end_exclusive"]
        assert all(i >= CONTEXT - 1 and i + 1 >= a and i + HORIZON < b for i in origins)


def build_model(
    name,
    df,
    manifest,
    device,
    checkpoint=None,
    model_config=None,
    checkpoint_choice="best-trained",
):
    model_config = model_config or {}
    revision_override = None
    if name.endswith("-ft"):
        if checkpoint is None:
            raise ValueError("Fine-tuned models require --checkpoint")
        checkpoint = Path(checkpoint)
        if checkpoint_choice not in ("best-trained", "selected"):
            raise ValueError("Unknown checkpoint choice")
        receipt_name = (
            "selection.json" if checkpoint_choice == "selected" else "training.json"
        )
        trained = json.loads((checkpoint / receipt_name).read_text(encoding="utf-8"))
        scope = manifest.get("dataset_info", {}).get("usage", "primary")
        if trained.get("evidence_scope", "primary") != scope:
            raise ValueError(
                "Exploratory checkpoints cannot be used as primary evidence"
            )
        base_name = name.removesuffix("-ft")
        if (
            trained["dataset_sha256"] != manifest["sha256"]
            or canonical_model(trained["base_model"]) != canonical_model(base_name)
            or trained["context"] != CONTEXT
            or trained["horizon"] != HORIZON
            or trained["boundaries"] != manifest["boundaries"]
            or trained["test_used_for_training_or_selection"]
            or (
                base_name.startswith("kronos")
                and not trained.get("teacher_forcing_causal_validation", False)
            )
        ):
            raise ValueError(
                "Fine-tuned checkpoint has a different dataset/split/protocol"
            )
        files = trained["checkpoint_files"]
        if not files or "model.safetensors" not in files:
            raise ValueError("Missing checkpoint weight hash")
        best = (checkpoint / trained.get("checkpoint_directory", "best")).resolve()
        for relative, expected in files.items():
            path = (best / relative).resolve()
            if not path.is_relative_to(best) or digest(path) != expected:
                raise ValueError(f"Checkpoint hash mismatch: {relative}")
        prefix = (
            "selected-pretrained:"
            if checkpoint_choice == "selected" and trained["best_epoch"] == 0
            else "finetuned:"
        )
        revision_override = prefix + files["model.safetensors"]
        name = base_name
    elif checkpoint is not None:
        raise ValueError("--checkpoint is only valid for fine-tuned models")
    name = canonical_model(name)
    if name in ("arima", "ets"):
        from statistical_baselines import statistical_predictor

        return (
            statistical_predictor(name, model_config),
            "validation_locked:" + json.dumps(model_config, sort_keys=True),
            0,
        )
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
        alpha = float(model_config.get("alpha", 100.0))
        model = Ridge(alpha=alpha).fit(sx.transform(xs), sy.transform(ys))

        def predict(history, dates, seed):
            return sy.inverse_transform(
                model.predict(sx.transform(history.ravel()[None, :]))
            ).reshape(HORIZON, 4)

        return predict, f"ridge_train_only_alpha{alpha:g}", 0
    import torch
    import yaml

    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_text(encoding="utf-8")
    )
    if revision_override:
        base_spec = provenance["models"][MODELS[name][0]]
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
    if name.startswith("kronos-"):
        vendor = ROOT / ".vendor/Kronos"
        if not (vendor / "model/kronos.py").exists():
            raise FileNotFoundError("Run scripts/bootstrap_kronos.py first")
        sys.path.insert(0, str(vendor))
        from model import Kronos, KronosPredictor, KronosTokenizer

        model_key, token_key, max_context = MODELS[name]
        model_spec = provenance["models"][model_key]
        token_spec = provenance["tokenizers"][token_key]
        if (
            revision_override
            and trained.get("tokenizer_revision", token_spec["repository_revision"])
            != token_spec["repository_revision"]
        ):
            raise ValueError("Checkpoint tokenizer revision mismatch")
        tokenizer = KronosTokenizer.from_pretrained(
            token_spec["repository"], revision=token_spec["repository_revision"]
        )
        model = Kronos.from_pretrained(
            str(best) if revision_override else model_spec["repository"],
            **(
                {}
                if revision_override
                else {"revision": model_spec["repository_revision"]}
            ),
        )
        model.eval()
        tokenizer.eval()
        if (model.s1_bits, model.s2_bits) != (tokenizer.s1_bits, tokenizer.s2_bits):
            raise ValueError("Tokenizer/model vocabulary mismatch")
        predictor = KronosPredictor(
            model, tokenizer, device=device, max_context=max_context
        )

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

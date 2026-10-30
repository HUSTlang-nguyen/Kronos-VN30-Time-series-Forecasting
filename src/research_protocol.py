"""Versioned identities and temporal rules for the PC rerun."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    "kronos-mini": ("kronos_mini", "kronos_tokenizer_2k", 2048),
    "kronos-small": ("kronos_small", "kronos_tokenizer_base", 512),
    "kronos-base": ("kronos_base", "kronos_tokenizer_base", 512),
    "chronos2": ("chronos_2_small", None, 8192),
}


def canonical_model(name):
    return "kronos-small" if name == "kronos" else name


def portable_path(value, base=ROOT):
    """Accept old Windows receipts on either OS without persisting host paths."""
    value = str(value)
    if PureWindowsPath(value).is_absolute() and os.name != "nt":
        raise ValueError("Receipt contains a host-specific absolute Windows path")
    path = Path(value.replace("\\", "/"))
    return path if path.is_absolute() else Path(base) / path


def file_hash(path, normalized=False):
    data = Path(path).read_bytes()
    if normalized:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def source_identity():
    return {
        p.relative_to(ROOT).as_posix(): file_hash(p, normalized=True)
        for folder in ("src", "scripts")
        for p in sorted((ROOT / folder).glob("*.py"))
    }


def budget_origins(manifest, rows=None):
    end = manifest["boundaries"]["train"]["row_end_exclusive"]
    start = manifest["boundaries"]["train"]["row_start"]
    if rows is not None:
        if rows < manifest["context"] + manifest["horizon"] or rows > end - start:
            raise ValueError(
                "Train budget must fit train and contain context plus labels"
            )
        start = end - rows
    origins = [
        i for i in manifest["origins"]["train"] if i - manifest["context"] + 1 >= start
    ]
    if not origins:
        raise ValueError("Empty training budget")
    return origins


def validate_coverage(frame, manifest, split):
    """A failed or missing origin never silently changes the comparison sample."""
    import numpy as np

    expected = [
        (i, h)
        for i in manifest["origins"][split]
        for h in range(1, manifest["horizon"] + 1)
    ]
    if not np.isfinite(frame[["origin_index", "horizon"]].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite forecast coordinates")
    if ((frame.origin_index % 1 != 0) | (frame.horizon % 1 != 0)).any():
        raise ValueError("Noninteger forecast coordinates")
    actual = list(zip(frame.origin_index.astype(int), frame.horizon.astype(int)))
    if actual != expected:
        raise ValueError("Incomplete, duplicated, or reordered forecast coverage")
    columns = ["pred_" + c for c in ("open", "high", "low", "close")]
    if not np.isfinite(frame[columns].to_numpy()).all():
        raise ValueError("Non-finite forecast")


def expanding_folds(df, sha, dataset_info):
    from vn30_forecast import split_manifest

    n = len(df)
    # Two historical folds before the primary holdout. All 20 labels stay inside
    # each partition; the validation block immediately precedes its test block.
    folds = []
    for fraction in (0.50, 0.60):
        train_end = int(n * fraction)
        val_end = train_end + int(n * 0.10)
        test_end = val_end + int(n * 0.10)
        folds.append(
            split_manifest(
                df,
                sha,
                dataset_info=dataset_info,
                ranges={
                    "train": (0, train_end),
                    "validation": (train_end, val_end),
                    "test": (val_end, test_end),
                },
            )
        )
    return folds

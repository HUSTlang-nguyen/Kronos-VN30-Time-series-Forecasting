"""Validate forecasts against the locked task, not merely against each other."""

from __future__ import annotations

import json

from research_protocol import (
    MODELS,
    budget_origins,
    canonical_model,
    file_hash,
    portable_path,
    source_identity,
)


def sampling_spec(name):
    if canonical_model(name.removesuffix("-ft")).startswith("kronos-"):
        return {"temperature": 1.0, "top_p": 0.9, "seed_rule": "seed+origin_index"}
    return None


def validate_forecast_metadata(meta, task, config, manifest, out, provenance):
    """Baseline seeds can differ from neural seeds, but must match their own task."""
    name = task["model"]
    base = canonical_model(name.removesuffix("-ft"))
    neural = base in MODELS
    expected = {
        "model": name,
        "dataset_sha256": manifest["sha256"],
        "split": task["split"],
        "context": manifest["context"],
        "horizon": manifest["horizon"],
        "seed": task["seed"],
        "origins": len(manifest["origins"][task["split"]]),
        "limited": False,
        "device": config["device"] if neural else "cpu",
        "checkpoint_choice": "best-trained",
        "source_identity": source_identity(),
        "calendar_note": manifest["calendar_note"],
        "sampling": sampling_spec(name),
    }
    expected.update(
        sample_count=3 if base.startswith("kronos-") else 0,
        quantile_count=13 if base == "chronos2" else 0,
        point_functional="quantile_mean"
        if base == "chronos2"
        else "sample_mean"
        if base.startswith("kronos-")
        else "deterministic",
    )
    for key, value in expected.items():
        if key not in meta or meta[key] != value:
            raise ValueError(f"Forecast protocol mismatch: {key}")
    locked = {}
    if base in ("ridge", "arima", "ets"):
        locked = json.loads(
            (out / "tuning" / (base + ".json")).read_text(encoding="utf-8")
        )
    if meta.get("model_config") != locked:
        raise ValueError("Forecast baseline configuration differs from validation lock")
    if name.endswith("-ft"):
        checkpoint = (out / "checkpoints" / task["checkpoint"]).resolve()
        if portable_path(meta.get("checkpoint", "")).resolve() != checkpoint:
            raise ValueError("Forecast points at a different checkpoint")
        trained = json.loads((checkpoint / "training.json").read_text(encoding="utf-8"))
        model_key, token_key, _ = MODELS[base]
        expected_training = {
            "dataset_sha256": manifest["sha256"],
            "base_model": base,
            "base_revision": provenance["models"][model_key]["repository_revision"],
            "context": manifest["context"],
            "horizon": manifest["horizon"],
            "boundaries": manifest["boundaries"],
            "seed": task["seed"],
            "device": config["device"],
            "data_budget": task["budget"],
            "initialization": task["initialization"],
            "test_used_for_training_or_selection": False,
            "source_identity": source_identity(),
            "manifest_sha256": file_hash(out / (task["fold"] + ".json")),
            "checkpoint_directory": "best",
            "epochs": config["epochs"],
            "method": "full",
            "normalization": "context_only",
            "weight_decay": 0.01,
            "effective_batch": 16,
            "origins": {
                "train": len(budget_origins(manifest, task["budget"])),
                "validation": len(manifest["origins"]["validation"]),
            },
        }
        lr = config["learning_rate"]
        if task["initialization"] == "random":
            lr = json.loads(
                (out / "tuning" / (task["checkpoint"] + "-lr.json")).read_text(
                    encoding="utf-8"
                )
            )["learning_rate"]
        expected_training["learning_rate"] = lr
        if token_key:
            expected_training.update(
                tokenizer=token_key,
                tokenizer_revision=provenance["tokenizers"][token_key][
                    "repository_revision"
                ],
                teacher_forcing_causal_validation=True,
            )
        for key, value in expected_training.items():
            if key not in trained or trained[key] != value:
                raise ValueError(f"Checkpoint protocol mismatch: {key}")
        files = trained["checkpoint_files"]
        if "model.safetensors" not in files:
            raise ValueError("Missing selected model weight checksum")
        best = (checkpoint / "best").resolve()
        for relative, expected_hash in files.items():
            path = (best / relative).resolve()
            if (
                not path.is_relative_to(best)
                or not path.is_file()
                or file_hash(path) != expected_hash
            ):
                raise ValueError("Selected checkpoint file checksum differs")
        revision = "finetuned:" + files["model.safetensors"]
    else:
        if meta.get("checkpoint") is not None:
            raise ValueError("Zero-shot/baseline forecast has an unexpected checkpoint")
        if neural:
            revision = provenance["models"][MODELS[base][0]]["repository_revision"]
        elif base == "naive":
            revision = "last_close"
        elif base == "ridge":
            revision = f"ridge_train_only_alpha{float(locked['alpha']):g}"
        else:
            revision = "validation_locked:" + json.dumps(locked, sort_keys=True)
    if meta.get("revision") != revision:
        raise ValueError(
            "Forecast revision differs from the locked pretrained/selected checkpoint"
        )

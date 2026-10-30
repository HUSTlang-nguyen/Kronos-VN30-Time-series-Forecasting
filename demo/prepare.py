"""Export the three PC selected checkpoints and historical demo sample."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sqlite3
import sys

import pandas as pd
import yaml
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
DEMO = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def checked_copy(source, target, expected):
    source, target = Path(source), Path(target)
    if sha(source) != expected:
        raise ValueError("Source checksum mismatch: " + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and sha(target) != expected:
        raise ValueError("Refusing to overwrite different model bytes: " + str(target))
    if not target.exists():
        shutil.copyfile(source, target)


def prepare():
    candidate = ROOT / "artifacts/local/pc-exploratory-20261030"
    manifest = json.loads((candidate / "candidate.json").read_text())
    provenance = yaml.safe_load((ROOT / "data/manifests/checkpoint_provenance.yaml").read_text())
    database = ROOT / manifest["dataset"]
    if sha(database) != manifest["sha256"]:
        raise ValueError("Original snapshot checksum differs")
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as con:
        frame = pd.read_sql_query("SELECT date,open,high,low,close FROM candles ORDER BY date,row_id", con)
    offset = manifest["origins"]["test"][0] - 127
    sample = frame.iloc[offset:].reset_index(drop=True)
    data_path = DEMO / "data/vn30.csv"
    data_path.parent.mkdir(exist_ok=True)
    sample.to_csv(data_path, index=False, lineterminator="\n")
    origins = [int(i - offset) for i in manifest["origins"]["test"]]
    write_json(DEMO / "data/manifest.json", dict(symbol="VN30", provider="VNDIRECT", dataset_sha256=manifest["sha256"], csv_sha256=sha(data_path), evidence_scope="exploratory_only", dataset_accepted=False, context=128, horizon=20, original_row_offset=offset, origins=origins, first_date=sample.date.iloc[0], last_date=sample.date.iloc[-1], snapshot_first_date=frame.date.iloc[0], snapshot_last_date=frame.date.iloc[-1]))

    vendor = DEMO / "vendor/kronos"
    files = {}
    for name in ("__init__.py", "kronos.py", "module.py"):
        raw = (ROOT / ".vendor/Kronos/model" / name).read_bytes().replace(b"\r\n", b"\n")
        target = vendor / "model" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        files["model/" + name] = hashlib.sha256(raw).hexdigest()
    shutil.copyfile(ROOT / ".vendor/Kronos/LICENSE", vendor / "LICENSE")
    (vendor / "REVISION").write_text(provenance["implementation_code"]["kronos"]["revision"] + "\n", encoding="utf-8")
    write_json(vendor / "manifest.json", dict(revision=provenance["implementation_code"]["kronos"]["revision"], repository=provenance["implementation_code"]["kronos"]["repository"], normalized_lf_sha256=files))

    registry_path = DEMO / "registry.json"
    previous = json.loads(registry_path.read_text())["models"] if registry_path.exists() else {}
    registry = {}
    for variant in ("mini", "small", "base"):
        model_id = "kronos-" + variant
        selected = json.loads((candidate / "checkpoints" / f"train-{model_id}-s42/selection.json").read_text())
        if selected["best_epoch"] != 5 or selected["seed"] != 42 or selected["dataset_sha256"] != manifest["sha256"]:
            raise ValueError("Unexpected selected checkpoint")
        folder = DEMO / "models" / model_id
        source = candidate / "checkpoints" / f"train-{model_id}-s42/selected"
        for filename in ("config.json", "model.safetensors"):
            checked_copy(source / filename, folder / filename, selected["checkpoint_files"][filename])
        token_key = "kronos_tokenizer_2k" if variant == "mini" else "kronos_tokenizer_base"
        token = provenance["tokenizers"][token_key]
        token_dir = DEMO / "models/tokenizers" / token_key
        for filename in ("config.json", "model.safetensors"):
            cached = hf_hub_download(token["repository"], filename, revision=token["repository_revision"])
            expected = token["weights_sha256"] if filename == "model.safetensors" else sha(cached)
            checked_copy(cached, token_dir / filename, expected)
        token_files = {name: sha(token_dir / name) for name in ("config.json", "model.safetensors")}
        spec = dict(id=model_id, label=f"Kronos {variant.title()}", variant=variant, parameters=selected["trainable_parameters"], epoch=5, training_seed=42, evidence_scope="exploratory_only", base_repository=provenance["models"]["kronos_" + variant]["repository"], base_revision=selected["base_revision"], dataset_sha256=manifest["sha256"], local_path=f"models/{model_id}", files={name: selected["checkpoint_files"][name] for name in ("config.json", "model.safetensors")}, hub_repo=None, hub_revision=None, tokenizer=dict(repository=token["repository"], revision=token["repository_revision"], local_path=f"models/tokenizers/{token_key}", files=token_files), inference=dict(context=128, horizon=20, sample_count=3, temperature=1.0, top_p=0.9, seed=42, precision="float32", point_functional="sample_mean"))
        if model_id in previous and previous[model_id]["files"] == spec["files"]:
            spec.update(hub_repo=previous[model_id].get("hub_repo"), hub_revision=previous[model_id].get("hub_revision"))
        write_json(folder / "inference_spec.json", spec)
        write_json(folder / "provenance.json", {k: spec[k] for k in ("id", "epoch", "training_seed", "evidence_scope", "base_repository", "base_revision", "dataset_sha256", "files", "tokenizer", "inference")})
        (folder / "README.md").write_text(f"""---
license: mit
base_model: {spec['base_repository']}
pipeline_tag: time-series-forecasting
tags: [kronos, vn30, fine-tuned, exploratory]
---
# {spec['label']} — VN30 SFT

Predictor fine-tuned on the fixed VNDIRECT VN30 snapshot, on the PC rerun.
Selected by native validation including epoch zero: epoch 5, training seed 42.
This is **exploratory research**. Provider OHLC construction is not fully verified.
No claim of superiority to Naive or of deployable trading performance is made.

## Load
Use the pinned Kronos implementation `{provenance['implementation_code']['kronos']['revision']}`
and `Kronos.from_pretrained(local_model_directory)`.
Tokenizer: `{token['repository']}` at `{token['repository_revision']}`.
The custom Kronos architecture does not automatically provide a hosted inference API.
The project includes a local React/FastAPI dashboard; no Space is required.

## Protocol and provenance
128 historical sessions, 20 future sessions, FP32, mean of 3 paths,
temperature 1.0, top-p 0.9. The tokenizer is frozen during fine-tuning.
Missing volume/amount are zero-filled by the adapter.
Snapshot SHA256: `{manifest['sha256']}`.
See `provenance.json` and `inference_spec.json` for revision and byte hashes.
No raw dataset, optimizer, RNG snapshots or credentials are included.

## License
MIT, retaining the original Kronos attribution. See LICENSE.
""", encoding="utf-8", newline="\n")
        shutil.copyfile(vendor / "LICENSE", folder / "LICENSE")
        registry[model_id] = spec
    write_json(DEMO / "registry.json", dict(version=1, models=registry))
    print("Prepared 3 selected PC models, 2 tokenizers, 470 sample sessions and 323 origins")


if __name__ == "__main__":
    prepare()

"""Fine-tune pinned small models on train; select by validation loss only."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vn30_forecast import (
    COLS,
    CONTEXT,
    HORIZON,
    check_manifest,
    digest,
    load_manifest_data,
    save_json,
)
from research_protocol import (
    MODELS,
    atomic_json,
    budget_origins,
    canonical_model,
    source_identity,
)


def windows(df, origins):
    prices = df[COLS].to_numpy(dtype=np.float32)
    return np.stack([prices[i - CONTEXT + 1 : i + HORIZON + 1] for i in origins])


def context_normalize(values):
    # Future targets must never determine the scale used for their context.
    context = np.ascontiguousarray(values[:, :CONTEXT])
    return np.clip(
        (values - context.mean(axis=1, keepdims=True))
        / (context.std(axis=1, keepdims=True) + 1e-5),
        -5.0,
        5.0,
    ).astype(np.float32)


def parameter_digest(model):
    result = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        result.update(name.encode())
        result.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return result.hexdigest()


def kronos_teacher_logits(model, first, second, stamps):
    # Upstream disables dependency cross-attention's causal mask in eval mode
    # for autoregressive decoding. Full teacher-forced validation needs it on.
    attention = model.dep_layer.cross_attn
    if attention.attn_dropout_p != 0:
        raise ValueError("Causal validation workaround requires zero attention dropout")
    previous = attention.training
    attention.training = True
    try:
        return model(
            first[:, :-1],
            second[:, :-1],
            stamps[:, :-1],
            use_teacher_forcing=True,
            s1_targets=first[:, 1:],
        )
    finally:
        attention.training = previous


def setup_chronos(spec, arrays, device, batch_size, initialization="pretrained"):
    from chronos import BaseChronosPipeline
    from chronos.chronos2.dataset import Chronos2Dataset, DatasetMode

    pipeline = BaseChronosPipeline.from_pretrained(
        spec["repository"],
        revision=spec["repository_revision"],
        device_map=device,
        torch_dtype=torch.float32,
    )
    model = pipeline.model
    if initialization == "random":
        pipeline.model = type(model)(model.config).to(device)
        model = pipeline.model

    def batches(split, order):
        # Every input has exactly 128 context + 20 labels. Sequential mode fixes
        # that cut; order is shuffled explicitly for training, without replacement.
        inputs = [arrays[split][i].T for i in order]
        dataset = Chronos2Dataset(
            inputs=inputs,
            context_length=CONTEXT,
            prediction_length=HORIZON,
            batch_size=getattr(batches, "batch_size", batch_size) * len(COLS),
            output_patch_size=pipeline.model_output_patch_size,
            min_past=CONTEXT,
            mode=DatasetMode.VALIDATION,
        )
        for batch in dataset:
            count = batch["context"].shape[0] // len(COLS)
            yield (
                {
                    k: v.to(device) if isinstance(v, torch.Tensor) else v
                    for k, v in batch.items()
                },
                count,
            )

    def loss(batch):
        return model(**batch).loss

    def save(path):
        pipeline.save_pretrained(path)

    return model, batches, loss, save, "native_normalized_quantile_loss"


def setup_kronos(
    spec,
    provenance,
    df,
    manifest,
    arrays,
    device,
    batch_size,
    initialization="pretrained",
    token_key="kronos_tokenizer_base",
):
    vendor = ROOT / ".vendor/Kronos"
    if not (vendor / "model/kronos.py").is_file():
        raise FileNotFoundError("Run scripts/bootstrap_kronos.py first")
    sys.path.insert(0, str(vendor))
    from model import Kronos, KronosTokenizer
    from model.kronos import calc_time_stamps

    token_spec = provenance["tokenizers"][token_key]
    tokenizer = (
        KronosTokenizer.from_pretrained(
            token_spec["repository"], revision=token_spec["repository_revision"]
        )
        .to(device)
        .eval()
        .requires_grad_(False)
    )
    model = Kronos.from_pretrained(
        spec["repository"], revision=spec["repository_revision"]
    ).to(device)
    if initialization == "random":
        model = Kronos(
            **{
                key: getattr(model, key)
                for key in (
                    "s1_bits",
                    "s2_bits",
                    "n_layers",
                    "d_model",
                    "n_heads",
                    "ff_dim",
                    "ffn_dropout_p",
                    "attn_dropout_p",
                    "resid_dropout_p",
                    "token_dropout_p",
                    "learn_te",
                )
            }
        ).to(device)
    if (model.s1_bits, model.s2_bits) != (tokenizer.s1_bits, tokenizer.s2_bits):
        raise ValueError("Wrong tokenizer for Kronos variant")
    encoded = {}
    all_stamps = calc_time_stamps(df.session_date).to_numpy(dtype=np.float32)
    for split, values in arrays.items():
        six_channels = np.concatenate(
            [values, np.zeros((*values.shape[:2], 2), dtype=np.float32)], axis=-1
        )
        normalized = context_normalize(six_channels)
        token_parts = [[], []]
        with torch.no_grad():
            for start in range(0, len(values), batch_size):
                ids = tokenizer.encode(
                    torch.from_numpy(normalized[start : start + batch_size]).to(device),
                    half=True,
                )
                for channel in range(2):
                    token_parts[channel].append(ids[channel].cpu())
        stamps = np.stack(
            [
                all_stamps[i - CONTEXT + 1 : i + HORIZON + 1]
                for i in manifest["origins"][split]
            ]
        )
        encoded[split] = (
            *[torch.cat(parts) for parts in token_parts],
            torch.from_numpy(stamps),
        )
    del tokenizer
    torch.cuda.empty_cache()

    def batches(split, order):
        active = getattr(batches, "batch_size", batch_size)
        for start in range(0, len(order), active):
            indices = order[start : start + active]
            yield (
                tuple(values[indices].to(device) for values in encoded[split]),
                len(indices),
            )

    def loss(batch):
        first, second, stamps = batch
        logits = kronos_teacher_logits(model, first, second, stamps)
        # Only the 20 future labels contribute to the objective.
        start = CONTEXT - 1
        return model.head.compute_loss(
            logits[0][:, start:],
            logits[1][:, start:],
            first[:, CONTEXT:],
            second[:, CONTEXT:],
        )[0]

    return (
        model,
        batches,
        loss,
        model.save_pretrained,
        "future20_token_cross_entropy_teacher_forcing",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--model", choices=["kronos", *MODELS], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument(
        "--batch-size", type=int, default=8, help="Number of OHLC windows"
    )
    parser.add_argument("--accumulation", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=1e-6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data-budget", type=int)
    parser.add_argument(
        "--initialization", choices=["pretrained", "random"], default="pretrained"
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if min(args.epochs, args.batch_size, args.accumulation, args.learning_rate) <= 0:
        parser.error(
            "Epochs, batch size, accumulation and learning rate must be positive"
        )
    if args.output.exists() and not args.resume:
        raise FileExistsError(args.output)
    if args.resume and not (args.output / "last.pt").exists():
        raise FileNotFoundError("No resumable epoch checkpoint")
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    df, sha = load_manifest_data(manifest)
    check_manifest(df, sha, manifest)
    # Test prices are never included in these arrays or optimization batches.
    arrays = {
        split: windows(df, manifest["origins"][split])
        for split in ("train", "validation")
    }
    train_origins = budget_origins(manifest, args.data_budget)
    arrays["train"] = windows(df, train_origins)
    training_manifest = {
        **manifest,
        "origins": {**manifest["origins"], "train": train_origins},
    }
    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_text(encoding="utf-8")
    )
    args.model = canonical_model(args.model)
    model_key, token_key, _ = MODELS[args.model]
    spec = provenance["models"][model_key]
    if args.model == "chronos2":
        model, batches, loss_fn, save, objective = setup_chronos(
            spec, arrays, args.device, args.batch_size, args.initialization
        )
    else:
        model, batches, loss_fn, save, objective = setup_kronos(
            spec,
            provenance,
            df,
            training_manifest,
            arrays,
            args.device,
            args.batch_size,
            args.initialization,
            token_key,
        )
    args.output.mkdir(parents=True, exist_ok=args.resume)
    config = {
        "base_model": args.model,
        "base_revision": spec["repository_revision"],
        "dataset_sha256": sha,
        "context": CONTEXT,
        "horizon": HORIZON,
        "seed": args.seed,
        "device": args.device,
        "epochs": args.epochs,
        "batch_size_windows": args.batch_size,
        "accumulation": args.accumulation,
        "learning_rate": args.learning_rate,
        "weight_decay": 0.01,
        "method": "full",
        "objective": objective,
        "tokenizer": token_key or "not_applicable",
        "tokenizer_revision": provenance["tokenizers"][token_key]["repository_revision"]
        if token_key
        else None,
        "teacher_forcing_causal_validation": args.model.startswith("kronos"),
        "normalization": "context_only",
        "selection": "best_trained_and_best_including_epoch_zero",
        "data_budget": args.data_budget,
        "initialization": args.initialization,
        "manifest_sha256": digest(args.manifest),
        "source_identity": source_identity(),
        "origins": {split: len(arrays[split]) for split in arrays},
        "boundaries": manifest["boundaries"],
        "test_used_for_training_or_selection": False,
        "trainable_parameters": sum(
            p.numel() for p in model.parameters() if p.requires_grad
        ),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "initial_parameter_sha256": parameter_digest(model),
    }
    if args.resume:
        previous = json.loads((args.output / "config.json").read_text(encoding="utf-8"))
        if config != previous:
            raise ValueError(
                "Resume config, dataset, variant, revision or source differs"
            )
    else:
        save_json(args.output / "config.json", config)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=0.01
    )
    history = []
    best_loss = math.inf
    best_epoch = None
    rng = np.random.default_rng(args.seed)
    started = time.monotonic()
    effective_batch = args.batch_size * args.accumulation
    microbatch = args.batch_size
    batches.batch_size = microbatch
    deadline = float(os.environ.get("VN30_DEADLINE_UNIX", "inf"))

    def check_deadline():
        if time.time() >= deadline:
            raise TimeoutError(
                "Experiment deadline reached; last complete epoch is resumable"
            )

    def validate():
        model.eval()
        total, count = 0.0, 0
        # Kronos caches rotary tensors; inference_mode would make that cache
        # unusable by autograd when training resumes after validation.
        with torch.no_grad():
            for batch, size in batches(
                "validation", np.arange(len(arrays["validation"]))
            ):
                check_deadline()
                loss = loss_fn(batch)
                if not torch.isfinite(loss):
                    raise ValueError("Non-finite validation loss")
                total += float(loss) * size
                count += size
        assert count == len(arrays["validation"])
        return total / count

    initial_loss = validate() if not args.resume else None
    selected_loss = initial_loss
    selected_epoch = 0
    if not args.resume:
        save(args.output / "selected")
    elapsed_before = 0.0

    def checkpoint(epoch):
        # Epoch boundary snapshots include all random streams and optimizer state.
        state = {
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "torch_rng": torch.get_rng_state(),
            "cuda_rng": torch.cuda.get_rng_state_all()
            if torch.cuda.is_available()
            else None,
            "numpy_rng": np.random.get_state(),
            "python_rng": random.getstate(),
            "order_rng": rng.bit_generator.state,
            "history": history,
            "best_loss": best_loss,
            "best_epoch": best_epoch,
            "selected_loss": selected_loss,
            "selected_epoch": selected_epoch,
            "initial_loss": initial_loss,
            "selected_parameter_sha256": config.get("selected_parameter_sha256"),
            "microbatch": microbatch,
            "elapsed_seconds": elapsed_before + time.monotonic() - started,
        }
        temp = args.output / "last.pt.tmp"
        torch.save(state, temp)
        temp.replace(args.output / "last.pt")

    def restore():
        nonlocal \
            history, \
            best_loss, \
            best_epoch, \
            selected_loss, \
            selected_epoch, \
            initial_loss
        state = torch.load(
            args.output / "last.pt", map_location="cpu", weights_only=False
        )
        model.load_state_dict(state["model"])
        optimizer.load_state_dict(state["optimizer"])
        torch.set_rng_state(state["torch_rng"])
        if state["cuda_rng"] is not None:
            torch.cuda.set_rng_state_all(state["cuda_rng"])
        np.random.set_state(state["numpy_rng"])
        random.setstate(state["python_rng"])
        rng.bit_generator.state = state["order_rng"]
        history, best_loss, best_epoch = (
            state["history"],
            state["best_loss"],
            state["best_epoch"],
        )
        selected_loss, selected_epoch, initial_loss = (
            state["selected_loss"],
            state["selected_epoch"],
            state["initial_loss"],
        )
        if state["selected_parameter_sha256"]:
            config["selected_parameter_sha256"] = state["selected_parameter_sha256"]
        return state

    if args.resume:
        restored = restore()
        elapsed_before = restored["elapsed_seconds"]
        microbatch = restored["microbatch"]
        batches.batch_size = microbatch
        first_epoch = restored["epoch"] + 1
    else:
        checkpoint(0)
        first_epoch = 1
    print(f"{args.model}: initial validation loss={initial_loss:.6f}", flush=True)
    for epoch in range(first_epoch, args.epochs + 1):
        while True:
            try:
                model.train()
                optimizer.zero_grad(set_to_none=True)
                total, seen = 0.0, 0
                n = len(arrays["train"])
                order = rng.permutation(n)
                batch_count = math.ceil(n / microbatch)
                accumulation = effective_batch // microbatch
                for number, (batch, size) in enumerate(batches("train", order)):
                    check_deadline()
                    group_start = (number // accumulation) * effective_batch
                    group_size = min(effective_batch, n - group_start)
                    loss = loss_fn(batch)
                    if not torch.isfinite(loss):
                        raise ValueError("Non-finite training loss")
                    (loss * (size / group_size)).backward()
                    total += float(loss.detach()) * size
                    seen += size
                    if (number + 1) % accumulation == 0 or number + 1 == batch_count:
                        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                        if not torch.isfinite(norm):
                            raise ValueError("Non-finite gradients")
                        optimizer.step()
                        optimizer.zero_grad(set_to_none=True)
                    if (number + 1) % 50 == 0:
                        print(
                            f"{args.model}: epoch {epoch}/{args.epochs}, {seen}/{n} train windows",
                            flush=True,
                        )
                assert seen == n
                val_loss = validate()
                if val_loss < best_loss:
                    best_loss, best_epoch = val_loss, epoch
                    save(args.output / "best")
                    config["selected_parameter_sha256"] = parameter_digest(model)
                if val_loss < selected_loss:
                    selected_loss, selected_epoch = val_loss, epoch
                    save(args.output / "selected")
                history.append(
                    {
                        "epoch": epoch,
                        "train_loss": total / seen,
                        "validation_loss": val_loss,
                        "selected": epoch == best_epoch,
                    }
                )
                for row in history:
                    row["selected"] = row["epoch"] == best_epoch
                pd.DataFrame(history).to_csv(args.output / "history.csv", index=False)
                print(
                    f"{args.model}: epoch {epoch}, train={total / seen:.6f}, validation={val_loss:.6f}, best_epoch={best_epoch}",
                    flush=True,
                )
                checkpoint(epoch)
                break
            except torch.cuda.OutOfMemoryError:
                if microbatch == 1:
                    raise
                optimizer.zero_grad(set_to_none=True)
                torch.cuda.empty_cache()
                restore()
                microbatch //= 2
                batches.batch_size = microbatch
                print(
                    f"OOM: replay epoch {epoch} with microbatch={microbatch}, effective batch={effective_batch}",
                    flush=True,
                )
    model.eval()
    if config["selected_parameter_sha256"] == config["initial_parameter_sha256"]:
        raise ValueError("Fine-tuning did not change model parameters")
    config.update(
        {
            "initial_validation_loss": initial_loss,
            "best_validation_loss": best_loss,
            "best_epoch": best_epoch,
            "elapsed_seconds": elapsed_before + time.monotonic() - started,
            "selected_epoch_including_zero": selected_epoch,
            "selected_validation_loss_including_zero": selected_loss,
            "checkpoint_directory": "best",
            "effective_batch": effective_batch,
            "final_microbatch": microbatch,
            "checkpoint_files": {
                str(p.relative_to(args.output / "best")).replace("\\", "/"): digest(p)
                for p in sorted((args.output / "best").rglob("*"))
                if p.is_file()
            },
            "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated()
            if args.device.startswith("cuda")
            else None,
        }
    )
    atomic_json(args.output / "training.json", config)
    selected = {
        **config,
        "checkpoint_directory": "selected",
        "best_epoch": selected_epoch,
        "checkpoint_files": {
            p.relative_to(args.output / "selected").as_posix(): digest(p)
            for p in (args.output / "selected").rglob("*")
            if p.is_file()
        },
    }
    atomic_json(args.output / "selection.json", selected)
    print(json.dumps(config, indent=2), flush=True)


if __name__ == "__main__":
    main()

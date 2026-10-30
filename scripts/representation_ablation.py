"""Paired continuous-vs-BSQ features from ONE fixed small tokenizer encoder."""

from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def run_ablation(config, out, seed):
    import numpy as np
    import pandas as pd
    import torch
    import torch.nn.functional as F
    import yaml
    from research_protocol import atomic_json, file_hash, source_identity
    from vn30_forecast import load_manifest_data, COLS, CONTEXT, HORIZON
    from finetune_vn30 import windows, context_normalize, parameter_digest
    from forecast_vn30 import score
    from research_statistics import diagnostics

    sys.path.insert(0, str(ROOT / ".vendor/Kronos"))
    from model import KronosTokenizer
    from model.module import TransformerBlock, RMSNorm

    manifest = json.loads((out / "primary.json").read_text())
    df, sha = load_manifest_data(manifest)
    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_bytes()
    )
    spec = provenance["tokenizers"]["kronos_tokenizer_base"]
    device = config["device"]
    torch.set_num_threads(4)
    encoder = (
        KronosTokenizer.from_pretrained(
            spec["repository"], revision=spec["repository_revision"]
        )
        .to(device)
        .eval()
        .requires_grad_(False)
    )
    small = provenance["models"]["kronos_small"]
    from huggingface_hub import hf_hub_download

    backbone_config = json.loads(
        Path(
            hf_hub_download(
                small["repository"],
                "config.json",
                revision=small["repository_revision"],
            )
        ).read_text()
    )
    folder = out / "ablation" / f"representation-s{seed}"
    folder.mkdir(parents=True, exist_ok=True)
    identity = {
        "dataset": sha,
        "source": source_identity(),
        "seed": seed,
        "epochs": config["epochs"],
        "lr": 1e-4,
        "tokenizer_revision": spec["repository_revision"],
        "backbone_config": backbone_config,
    }

    def check():
        if time.time() >= float(os.environ.get("VN30_DEADLINE_UNIX", "inf")):
            raise TimeoutError("Ablation budget exhausted")

    def features(x, arm):
        with torch.no_grad():
            z = encoder.embed(x)
            for layer in encoder.encoder:
                z = layer(z)
            z = encoder.quant_embed(z)
            if arm == "continuous":
                return F.normalize(z, dim=-1)
            return encoder.tokenizer(z, collect_metrics=False)[1]

    class Forecaster(torch.nn.Module):
        def __init__(self):
            super().__init__()
            c = backbone_config
            self.project = torch.nn.Linear(encoder.codebook_dim, c["d_model"])
            self.blocks = torch.nn.ModuleList(
                [
                    TransformerBlock(
                        c["d_model"],
                        c["n_heads"],
                        c["ff_dim"],
                        c["ffn_dropout_p"],
                        c["attn_dropout_p"],
                        c["resid_dropout_p"],
                    )
                    for _ in range(c["n_layers"])
                ]
            )
            self.norm = RMSNorm(c["d_model"])
            self.head = torch.nn.Linear(c["d_model"], 4)

        def forward(self, x):
            x = self.project(x)
            for block in self.blocks:
                x = block(x)
            return self.head(self.norm(x))

    arrays = {
        split: windows(df, manifest["origins"][split])
        for split in ("train", "validation")
    }
    six = {
        split: context_normalize(
            np.concatenate([a, np.zeros((*a.shape[:2], 2), dtype=np.float32)], axis=-1)
        )
        for split, a in arrays.items()
    }
    initial_hashes = []
    results = {}
    for arm in ("continuous", "quantized"):
        check()
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        model = Forecaster().to(device)
        initial_hashes.append(parameter_digest(model))
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
        rng = np.random.default_rng(seed)
        history = []
        best = float("inf")
        first = 1
        resume = folder / (arm + "-last.pt")
        if resume.exists():
            state = torch.load(resume, map_location="cpu", weights_only=False)
            if state["identity"] != identity:
                raise ValueError("Ablation resume identity differs")
            model.load_state_dict(state["model"])
            optimizer.load_state_dict(state["optimizer"])
            torch.set_rng_state(state["torch_rng"])
            torch.cuda.set_rng_state_all(state["cuda_rng"])
            rng.bit_generator.state = state["rng"]
            history = state["history"]
            best = state["best"]
            first = state["epoch"] + 1
        cached = {}
        for split, values in six.items():
            chunks = []
            for start in range(0, len(values), 8):
                check()
                chunks.append(
                    features(
                        torch.from_numpy(values[start : start + 8]).to(device), arm
                    ).cpu()
                )
            cached[split] = torch.cat(chunks)

        def loss(indices, split):
            x = cached[split][indices, :-1].to(device)
            y = torch.from_numpy(six[split][indices, 1:, :4]).to(device)
            predicted = model(x)
            return F.mse_loss(predicted[:, CONTEXT - 1 :], y[:, CONTEXT - 1 :])

        def save_epoch(epoch):
            state = {
                "identity": identity,
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "epoch": epoch,
                "torch_rng": torch.get_rng_state(),
                "cuda_rng": torch.cuda.get_rng_state_all(),
                "rng": rng.bit_generator.state,
                "history": history,
                "best": best,
            }
            temp = resume.with_suffix(".tmp")
            torch.save(state, temp)
            temp.replace(resume)

        if not resume.exists():
            save_epoch(0)
        for epoch in range(first, config["epochs"] + 1):
            model.train()
            order = rng.permutation(len(arrays["train"]))
            total = 0
            optimizer.zero_grad(set_to_none=True)
            for start in range(0, len(order), 8):
                check()
                indices = order[start : start + 8]
                value = loss(indices, "train")
                if not torch.isfinite(value):
                    raise ValueError("Non-finite ablation loss")
                group_start = (start // 16) * 16
                group_size = min(16, len(order) - group_start)
                (value * len(indices) / group_size).backward()
                total += float(value.detach()) * len(indices)
                if (start // 8 + 1) % 2 == 0 or start + 8 >= len(order):
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
            model.eval()
            validation = 0
            with torch.no_grad():
                for start in range(0, len(arrays["validation"]), 8):
                    check()
                    indices = np.arange(
                        start, min(start + 8, len(arrays["validation"]))
                    )
                    validation += float(loss(indices, "validation")) * len(indices)
            validation /= len(arrays["validation"])
            if validation < best:
                best = validation
                torch.save(model.state_dict(), folder / (arm + "-best.pt"))
            history.append(
                {
                    "epoch": epoch,
                    "train_loss": total / len(order),
                    "validation_loss": validation,
                }
            )
            save_epoch(epoch)
            pd.DataFrame(history).to_csv(folder / (arm + "-history.csv"), index=False)
        model.load_state_dict(
            torch.load(
                folder / (arm + "-best.pt"), map_location=device, weights_only=True
            )
        )
        model.eval()
        paths = {}
        for split in ("validation", "test"):
            dest = folder / (arm + "-" + split + ".csv")
            paths[split] = dest
            if dest.exists():
                continue
            rows = []
            prices = df[COLS].to_numpy(dtype=np.float32)
            for i in manifest["origins"][split]:
                check()
                history = prices[i - CONTEXT + 1 : i + 1]
                mean = history.mean(0)
                std = history.std(0) + 1e-5
                normalized = np.clip((history - mean) / std, -5, 5)
                x = torch.from_numpy(
                    np.concatenate(
                        [normalized, np.zeros((CONTEXT, 2), np.float32)], axis=-1
                    )[None]
                ).to(device)
                with torch.no_grad():
                    for h in range(1, HORIZON + 1):
                        predicted = model(features(x, arm))[:, -1]
                        values = predicted[0].cpu().numpy() * std + mean
                        if not np.isfinite(values).all():
                            raise ValueError("Non-finite ablation forecast")
                        rows.append(
                            {
                                "origin_index": i,
                                "origin_date": df.date.iloc[i],
                                "target_date": df.date.iloc[i + h],
                                "horizon": h,
                                **{"pred_" + c: float(v) for c, v in zip(COLS, values)},
                            }
                        )
                        x = torch.cat(
                            [
                                x,
                                torch.cat(
                                    [
                                        predicted.clamp(-5, 5),
                                        torch.zeros((1, 2), device=device),
                                    ],
                                    dim=-1,
                                )[:, None],
                            ],
                            dim=1,
                        )
            pd.DataFrame(rows).to_csv(dest, index=False)
            atomic_json(
                dest.with_suffix(".json"),
                {
                    "model": "representation-" + arm,
                    "revision": file_hash(folder / (arm + "-best.pt")),
                    "dataset_sha256": sha,
                    "split": split,
                    "context": CONTEXT,
                    "horizon": HORIZON,
                    "device": device,
                    "seed": seed,
                    "sample_count": 0,
                    "quantile_count": 0,
                    "point_functional": "deterministic",
                    "origins": len(manifest["origins"][split]),
                    "limited": False,
                    "source_identity": source_identity(),
                },
            )
        results[arm] = {
            "best_validation_loss": best,
            "initial_backbone_sha256": initial_hashes[-1],
            "paths": {k: str(v) for k, v in paths.items()},
        }
        model = optimizer = cached = None
        torch.cuda.empty_cache()
    if initial_hashes[0] != initial_hashes[1]:
        raise ValueError("Ablation backbones did not start identically")
    for split in ("validation", "test"):
        naive = folder / ("naive-" + split + ".csv")
        if not naive.exists():
            from forecast_vn30 import forecast

            forecast(df, manifest, "naive", split, "cpu", seed, naive, None)
        target = folder / ("evaluation-" + split)
        if not target.exists():
            score(
                df,
                manifest,
                [naive, *[Path(results[a]["paths"][split]) for a in results]],
                target,
            )
            if split == "test":
                diagnostics(df, manifest, pd.read_csv(target / "details.csv"), target)
    atomic_json(
        folder / "result.json",
        {
            "identity": identity,
            "arms": results,
            "initial_backbone_equal": True,
            "interpretation": "Effect of quantization under fixed pretrained encoder and random price backbone; not all K-line representation effects.",
        },
    )

"""GPU smoke on SYNTHETIC prices; never eligible for research score tables."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]


def main():
    import numpy as np
    import pandas as pd
    import torch
    import yaml
    from research_protocol import MODELS, atomic_json
    from vn30_forecast import split_manifest, build_model, COLS
    from finetune_vn30 import (
        windows,
        setup_chronos,
        setup_kronos,
        kronos_teacher_logits,
    )

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--device", default="cuda:0")
    args = p.parse_args()
    torch.set_num_threads(4)
    n = 1000
    dates = pd.bdate_range("2020-01-01", periods=n)
    close = 100 + np.arange(n) * 0.03 + np.sin(np.arange(n) / 7)
    df = pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "session_date": dates,
            "open": close - 0.1,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
        }
    )
    m = split_manifest(df, "synthetic_smoke_only")
    arrays = {s: windows(df, m["origins"][s][:2]) for s in ("train", "validation")}
    short = {**m, "origins": {s: v[:2] for s, v in m["origins"].items()}}
    provenance = yaml.safe_load(
        (ROOT / "data/manifests/checkpoint_provenance.yaml").read_bytes()
    )
    checks = {}
    for name, (key, token_key, _) in MODELS.items():
        predictor, revision, _ = build_model(name, df, m, args.device)
        i = m["origins"]["validation"][0]
        history = df[COLS].iloc[i - 127 : i + 1].to_numpy()
        dates = (
            df.session_date.iloc[i - 127 : i + 1].reset_index(drop=True),
            df.session_date.iloc[i + 1 : i + 21].reset_index(drop=True),
        )
        a = predictor(history, dates, 42 + i)
        b = predictor(history, dates, 42 + i)
        if a.shape != (20, 4) or not np.isfinite(a).all() or not np.array_equal(a, b):
            raise ValueError("Smoke shape/finite/replay failed: " + name)
        del predictor
        torch.cuda.empty_cache()
        setup = (
            setup_chronos(provenance["models"][key], arrays, args.device, 2)
            if name == "chronos2"
            else setup_kronos(
                provenance["models"][key],
                provenance,
                df,
                short,
                arrays,
                args.device,
                2,
                token_key=token_key,
            )
        )
        model, batches, loss_fn, save, objective = setup
        model.train()
        batch, count = next(batches("train", np.arange(2)))
        loss = loss_fn(batch)
        loss.backward()
        if not torch.isfinite(loss) or not any(
            p.grad is not None and torch.isfinite(p.grad).all()
            for p in model.parameters()
        ):
            raise ValueError("Native training gradient check failed")
        delta = None
        token_prefix = None
        if token_key:
            model.eval()
            torch.manual_seed(42)
            first = torch.randint(model.s1_vocab_size, (1, 148), device=args.device)
            second = torch.randint(2**model.s2_bits, (1, 148), device=args.device)
            stamps = torch.zeros((1, 148, 5), device=args.device)
            changed = first.clone()
            changed[:, 138:] = (changed[:, 138:] + 1) % model.s1_vocab_size
            with torch.no_grad():
                before = kronos_teacher_logits(model, first, second, stamps)
                after = kronos_teacher_logits(model, changed, second, stamps)
                delta = max(
                    float((x[:, :137] - y[:, :137]).abs().max())
                    for x, y in zip(before, after)
                )
            if delta > 1e-6:
                raise ValueError("Teacher forcing future leakage")
            from model import KronosTokenizer

            spec = provenance["tokenizers"][token_key]
            tok = (
                KronosTokenizer.from_pretrained(
                    spec["repository"], revision=spec["repository_revision"]
                )
                .to(args.device)
                .eval()
            )
            numeric = torch.randn(1, 148, 6, device=args.device)
            altered = numeric.clone()
            altered[:, 128:] *= 10
            with torch.no_grad():
                x = tok.encode(numeric, half=True)
                y = tok.encode(altered, half=True)
            token_prefix = all(
                torch.equal(u[:, :128], v[:, :128]) for u, v in zip(x, y)
            )
            if not token_prefix:
                raise ValueError("Tokenizer sees future")
            del tok, before, after, first, second, stamps
        checks[name] = {
            "revision": revision,
            "shape": list(a.shape),
            "replay_identical": True,
            "native_loss": float(loss.detach()),
            "gradients_finite": True,
            "causal_logit_max_delta": delta,
            "tokenizer_prefix_invariant": token_prefix,
        }
        del model, batches, loss_fn, save, setup, loss, batch
        torch.cuda.empty_cache()
        atomic_json(
            args.output,
            {
                "classification": "synthetic_smoke_not_research_results",
                "gpu": torch.cuda.get_device_name(0),
                "checks": checks,
            },
        )
        print(name, "PASS", flush=True)


if __name__ == "__main__":
    main()

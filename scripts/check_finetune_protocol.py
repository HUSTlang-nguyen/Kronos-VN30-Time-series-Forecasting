"""Check temporal isolation and Kronos teacher-forcing causality."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

from finetune_vn30 import ROOT, COLS, CONTEXT, HORIZON, context_normalize, kronos_teacher_logits, windows
from vn30_forecast import check_manifest, load, save_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    df, sha = load()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    check_manifest(df, sha, manifest)
    perturbed = df.copy()
    perturbed.loc[manifest["boundaries"]["test"]["row_start"]:, COLS] *= 10
    for split in ("train", "validation"):
        original = windows(df, manifest["origins"][split])
        modified = windows(perturbed, manifest["origins"][split])
        assert np.array_equal(original, modified), "Test prices leaked into training/validation"
        assert original.shape == (manifest["origin_counts"][split], CONTEXT + HORIZON, len(COLS))
    original = windows(df, manifest["origins"]["train"][:2])
    modified = original.copy()
    modified[:, CONTEXT:] *= 10
    assert np.array_equal(context_normalize(original)[:, :CONTEXT], context_normalize(modified)[:, :CONTEXT])

    sys.path.insert(0, str(ROOT / ".vendor/Kronos"))
    from model import Kronos
    spec = yaml.safe_load((ROOT / "data/manifests/checkpoint_provenance.yaml").read_text())["models"]["kronos_small"]
    model = Kronos.from_pretrained(spec["repository"], revision=spec["repository_revision"]).to(args.device).eval()
    torch.manual_seed(42)
    length = CONTEXT + HORIZON
    first = torch.randint(model.s1_vocab_size, (1, length), device=args.device)
    second = torch.randint(2 ** model.s2_bits, (1, length), device=args.device)
    stamps = torch.zeros((1, length, 5), device=args.device)
    modified = first.clone()
    cut = CONTEXT + HORIZON // 2
    modified[:, cut:] = (modified[:, cut:] + 1) % model.s1_vocab_size
    with torch.no_grad():
        before = kronos_teacher_logits(model, first, second, stamps)
        after = kronos_teacher_logits(model, modified, second, stamps)
        deltas = [float((a[:, :cut-1] - b[:, :cut-1]).abs().max()) for a, b in zip(before, after)]
    assert max(deltas) < 1e-6, f"Future token leakage: {deltas}"
    assert not model.training and not model.dep_layer.cross_attn.training
    result = {
        "dataset_sha256": sha, "test_price_isolation": "pass",
        "context_only_normalization": "pass", "teacher_forcing_causality": "pass",
        "prefix_logit_max_deltas": deltas, "device": args.device,
    }
    if args.output:
        save_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

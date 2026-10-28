# Experiment artifacts

This directory contains saved forecasts, scores, figures, source audits and model checkpoints. Checkpoint weights use Git LFS; run `git lfs pull` after cloning.

For the final fine-tuning results, follow `local/vn30-finetune-20261027/active_run.json`:

- Checkpoints: `chronos2/` and `kronos-causal/`.
- Validation: `evaluation-validation-final/`.
- Test: `evaluation-test/`.
- Comparison: `comparison-final/`.

Earlier attempts and replay outputs are retained for traceability. In particular, `kronos-full/`, `evaluation-validation/` and `comparison/` under that run are superseded; do not substitute them for the active results. The corrected Kronos checkpoint uses causal teacher-forcing validation.

The SQLite dataset remains managed separately by DVC.

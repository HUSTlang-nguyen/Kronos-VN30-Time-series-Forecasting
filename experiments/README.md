# Independent candidate follow-ups

These entry points orchestrate exploratory follow-ups without editing the frozen
`src/` and `scripts/` files used by a live inference phase. Each run records both
the frozen source identity and its own orchestrator hash (normalized LF).
Changing either identity refuses resume. This does not accept the dataset or
promote exploratory checkpoints to primary research evidence.

```powershell
.venv/Scripts/python.exe experiments/candidate_learning.py --wait-for-gpu
```

Q3 waits for the existing GPU phase, then runs sequentially within the original
learning-stage/24-hour deadline. It uses nested 500/1,000/full train sessions,
Kronos-small and Chronos, all three seeds, pretrained/random predictor controls,
and the fixed validation LR grid. It reuses six exact full-budget pretrained
checkpoints and uses each winning random-LR trial directly; no duplicate training
or test-based selection. Failed trials remain in the receipts.

Results remain under `artifacts/local/pc-exploratory-20261030/learning/`. Inspect
`queue.json`, `state.json`, per-trial logs, and verification receipts before
assuming a process is still running. Weights and optimizer snapshots stay local.

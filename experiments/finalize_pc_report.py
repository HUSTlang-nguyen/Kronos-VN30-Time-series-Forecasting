"""Build the PC research report from verified artifacts; never promote the dataset."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from verify_completed_candidate import read, require, portable, close, validate_frame


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def moving_interval(delta, block=20, draws=2000, seed=42):
    """Independently assemble sampled moving windows in draw order."""
    values = np.asarray(delta, dtype=float)
    require(values.ndim == 1 and len(values) > 0 and np.isfinite(values).all(), "Invalid bootstrap differences")
    width = min(block, len(values))
    windows = np.lib.stride_tricks.sliding_window_view(values, width)
    count = int(np.ceil(len(values) / width))
    choices = np.random.default_rng(seed).integers(len(windows), size=draws * count)
    samples = windows[choices].reshape(draws, count * width)[:, :len(values)]
    return np.quantile(samples.mean(axis=1), [0.025, 0.975])


def volatility(data, manifest):
    prices = data.close.to_numpy(dtype=float)
    returns = np.r_[np.nan, np.diff(np.log(prices))]
    sigma = np.full(len(prices), np.nan)
    for i in range(20, len(prices)):
        sigma[i] = np.std(returns[i - 19:i + 1], ddof=1)
    train = manifest["boundaries"]["train"]
    known_train = sigma[train["row_start"]:train["row_end_exclusive"]]
    cutoff = np.quantile(known_train[np.isfinite(known_train)], 0.9)
    origins = np.asarray(manifest["origins"]["test"])
    high = sigma[origins] >= cutoff
    cluster = np.cumsum(high & ~np.r_[False, high[:-1]])
    result = pd.DataFrame(dict(origin_date=data.date.to_numpy()[origins], sigma20=sigma[origins], regime=np.where(high, "high", "normal"), period=[f"period-{min(2, k * 3 // len(origins)) + 1}" for k in range(len(origins))], high_cluster=np.where(high, cluster, 0)))
    return result, float(cutoff)


def pick_trial(trials):
    good = [t for t in trials if t.get("validation_loss") is not None and np.isfinite(t["validation_loss"]) and t.get("status", "pass") == "pass" and t.get("successful_origins", 0) == t.get("expected_origins", 0)]
    require(bool(good), "No fully covered valid tuning trial")
    return min(good, key=lambda t: t["validation_loss"])


def validate_publisher_case(case, expected_value, raw_sha256):
    require(case.get("symbol") == "VN30" and case.get("field") == "close", "Evidence must identify cash VN30 Close")
    require(case.get("market_date") == case.get("date"), "Publication date is not the verified market date")
    require(case.get("semantics") == "session_close" and bool(case.get("evidence_locator")), "Close semantics or locator missing")
    require(re.fullmatch(r"[0-9a-f]{64}", case.get("evidence_sha256", "")) is not None and case["evidence_sha256"] == raw_sha256, "Publisher raw hash differs")
    close(case["value"], expected_value, "Publisher value differs from claimed corroboration")


def md_table(frame, columns=None, digits=3):
    frame = frame if columns is None else frame[columns]
    def cell(value):
        if pd.isna(value):
            return "—"
        if isinstance(value, (float, np.floating)):
            return f"{value:.{digits}f}"
        return str(value).replace("|", "\\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(frame.columns) + " |", "| " + " | ".join(["---"] * len(frame.columns)) + " |"] + ["| " + " | ".join(cell(v) for v in row) + " |" for row in frame.itertuples(index=False, name=None)])


def summarized(frame, keys):
    return frame.groupby(keys, dropna=False).agg(seeds=("seed", "nunique"), mae=("mae", "mean"), mae_sd=("mae", "std"), rmse=("rmse", "mean")).reset_index()


def matrix(frame, target="close", spread=False):
    part = frame.loc[(frame.target == target) & (frame.split == "test")]
    if spread:
        grouped = part.groupby(["model", "horizon"]).mae.agg(["mean", "std"])
        grouped["display"] = [f"{row['mean']:.3f} ± {row['std']:.3f}" for _, row in grouped.iterrows()]
        return grouped.display.unstack("horizon").rename(columns={1: "h=1", 5: "h=5", 20: "h=20"}).reset_index()
    return part.pivot_table(index="model", columns="horizon", values="mae", aggfunc="mean").rename(columns={1: "h=1", 5: "h=5", 20: "h=20"}).reset_index()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=ROOT / "artifacts/local/pc-exploratory-20261030")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path, default=ROOT / "docs/VN30_PC_Research_Report.md")
    args = parser.parse_args()
    args.report = args.report.resolve()
    candidate = args.candidate.resolve()
    output = (args.output or candidate / "final-report").resolve()
    require(candidate.is_relative_to(ROOT) and output.is_relative_to(ROOT) and args.report.is_relative_to(ROOT), "Report artifacts must stay inside this repository")
    output.mkdir(parents=True, exist_ok=True)
    inputs = {}

    def track(path):
        path = Path(path).resolve()
        inputs[path.relative_to(ROOT).as_posix()] = file_hash(path)
        return path

    manifest = read(track(candidate / "candidate.json"))
    require(manifest["sha256"] == "fee0bd8c240a9d2be4ef5c9d287eede6c5506b0358c25545e72de99709da4fd2", "This report specification covers the frozen PC snapshot; a corrected dataset needs a revised protocol/report")
    proof = read(track(candidate / "review/numerical_validation.json"))
    require(proof["status"] == "pass" and not proof["dataset_accepted"], "Numerical verification missing or scope differs")
    for name, sha in proof["input_hashes"].items():
        require(file_hash(portable(name)) == sha, "Verified input changed: " + name)
    metric_file = track(candidate / "review/recomputed_metrics.csv")
    require(file_hash(metric_file) == proof["recomputed_metrics_sha256"], "Recomputed metrics changed")
    metrics = pd.read_csv(metric_file)
    db = portable(manifest["dataset"])
    require(file_hash(db) == manifest["sha256"], "Dataset hash differs")
    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as con:
        data = pd.read_sql_query("SELECT date,open,high,low,close FROM candles ORDER BY date,row_id", con)
    training = read(track(candidate / "identity.json"))
    # New postprocessing lives in experiments/; the frozen forecasting core must match.
    core_identity = read(track(candidate / "evaluation-main/identity.json"))["source_identity"]
    current_names = {p.relative_to(ROOT).as_posix() for folder in ("src", "scripts") for p in (ROOT / folder).rglob("*.py")}
    require(current_names == set(core_identity), "Frozen core file set changed")
    for name, sha in core_identity.items():
        text = portable(name).read_bytes().replace(b"\r\n", b"\n")
        require(hashlib.sha256(text).hexdigest() == sha, "Frozen core changed: " + name)
    learning_identity = read(track(candidate / "learning/identity.json"))
    followup_identity = read(track(candidate / "followups/identity.json"))
    require(learning_identity["source_identity"] == followup_identity["source_identity"] == core_identity, "Experiment core identities differ")
    for name, sha in followup_identity["orchestrators"].items():
        path = track(ROOT / "experiments" / name)
        require(hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == sha, "Frozen experiment orchestrator changed: " + name)
    require(learning_identity["orchestrator_sha256"] == followup_identity["orchestrators"]["candidate_learning.py"], "Learning orchestrator identity differs")

    main_scores = metrics.loc[metrics.group.str.startswith("evaluation-main/")].copy()
    main_scores["seed"] = main_scores.group.str.extract(r"seed-(\d+)").astype(int)
    require(set(main_scores.seed) == {42, 43, 44}, "Main seed missing")
    main_summary = summarized(main_scores, ["model", "split", "target", "horizon"])
    main_summary.to_csv(output / "main_summary.csv", index=False)
    selected, inventory = [], []
    for model in ("kronos-mini", "kronos-small", "kronos-base", "chronos2"):
        for seed in (42, 43, 44):
            folder = candidate / "checkpoints" / f"train-{model}-s{seed}"
            trained = read(track(folder / "training.json"))
            choice = read(track(folder / "selection.json"))
            epoch = choice["best_epoch"]
            expected_epoch = 0 if trained["initial_validation_loss"] <= trained["best_validation_loss"] else trained["best_epoch"]
            require(epoch == expected_epoch, "Epoch-zero choice is inconsistent with validation")
            source_model = model if epoch == 0 else model + "-ft"
            chosen_meta = read(candidate / "evaluation-main/forecasts" / f"{model}-s{seed}-{'zs' if epoch == 0 else 'ft'}-test.json")
            if epoch == 0:
                import yaml
                provenance = yaml.safe_load((ROOT / "data/manifests/checkpoint_provenance.yaml").read_text())
                key = {"chronos2": "chronos_2_small", "kronos-mini": "kronos_mini", "kronos-small": "kronos_small", "kronos-base": "kronos_base"}[model]
                require(choice["checkpoint_files"]["model.safetensors"] == provenance["models"][key]["weights_sha256"], "Selected epoch-zero weights differ from zero-shot")
                require(chosen_meta["revision"] == choice["base_revision"], "Zero-shot revision differs")
            else:
                require(choice["checkpoint_files"] == trained["checkpoint_files"], "Selected updated checkpoint differs from best-trained")
            part = main_scores.loc[(main_scores.seed == seed) & (main_scores.model == source_model)].copy()
            part["model"] = model + "-selected"
            part["selected_epoch"] = epoch
            part["source_model"] = source_model
            selected.append(part)
            inventory.append(dict(model=model, seed=seed, best_trained_epoch=trained["best_epoch"], selected_epoch=epoch, initial_validation_loss=trained["initial_validation_loss"], best_trained_validation_loss=trained["best_validation_loss"], selected_validation_loss=choice["selected_validation_loss_including_zero"], train_seconds=trained["elapsed_seconds"], peak_allocated_GiB=trained["peak_cuda_allocated_bytes"] / 2 ** 30, trainable_parameters=trained["trainable_parameters"]))
    selected = pd.concat(selected, ignore_index=True)
    selected.to_csv(output / "selected_scores.csv", index=False)
    inventory = pd.DataFrame(inventory)
    inventory.to_csv(output / "checkpoint_selection.csv", index=False)

    learning_state = read(track(candidate / "learning/state.json"))
    require(len(learning_state["jobs"]) == 36 and all(x["status"] == "complete" for x in learning_state["jobs"].values()), "Learning matrix incomplete")
    learning_rows, lr_rows = [], []
    for key, job in learning_state["jobs"].items():
        task = job["task"]
        part = metrics.loc[metrics.group.str.startswith("learning/scores/" + key + "/")].copy()
        require(len(part) == 32, "Learning score group incomplete: " + key)
        part = part.loc[part.model != "naive"]
        part["seed"], part["initialization"] = task["seed"], task["initialization"]
        part["train_rows"] = task["budget"] or manifest["boundaries"]["train"]["rows"]
        part["train_windows"] = job["train_windows"]
        learning_rows.append(part)
        if task["initialization"] == "random":
            trials = read(track(candidate / "learning/tuning" / (key + "-trials.json")))
            require(trials["test_used"] is False, "Random LR selection used test")
            best = pick_trial(trials["trials"])
            require(best["learning_rate"] == job["selection"]["learning_rate"] and best["checkpoint"] == job["checkpoint"], "Random LR winner differs")
            require(set(t["learning_rate"] for t in trials["trials"]) == {1e-6, 1e-5, 1e-4}, "Random LR grid differs")
            lr_rows.append(dict(job=key, model=task["model"], seed=task["seed"], train_rows=task["budget"] or 1589, learning_rate=best["learning_rate"], validation_loss=best["validation_loss"]))
    learning = pd.concat(learning_rows, ignore_index=True)
    curve = summarized(learning, ["model", "initialization", "train_rows", "train_windows", "split", "target", "horizon"])
    require((curve.seeds == 3).all(), "Learning curve has missing seed")
    curve.to_csv(output / "learning_curve.csv", index=False)
    pd.DataFrame(lr_rows).to_csv(output / "random_lr_selection.csv", index=False)

    ablation = metrics.loc[metrics.group.str.contains("followups/ablation/")].copy()
    ablation["seed"] = ablation.group.str.extract(r"representation-s(\d+)").astype(int)
    for seed in (42, 43, 44):
        result = read(track(candidate / "followups/ablation" / f"representation-s{seed}" / "result.json"))
        require(result["initial_backbone_equal"] is True, "Ablation is not paired")
        arms = result["arms"]
        require(arms["continuous"]["initial_backbone_sha256"] == arms["quantized"]["initial_backbone_sha256"], "Initial backbones differ")
    ablation_summary = summarized(ablation, ["model", "split", "target", "horizon"])
    ablation_summary.to_csv(output / "ablation_summary.csv", index=False)
    fold_scores = metrics.loc[metrics.group.str.contains("followups/folds/")].copy()
    fold_scores["fold"] = fold_scores.group.str.extract(r"folds/(fold\d+)")
    fold_scores.to_csv(output / "fold_scores.csv", index=False)

    baseline_rows = []
    for model, count in (("ridge", 4), ("arima", 18), ("ets", 3)):
        folder = candidate / "evaluation-main/tuning"
        trials_path = track(folder / (model + "-trials.json"))
        trials = read(trials_path)
        config_path = track(folder / (model + ".json"))
        locked = read(track(folder / (model + "-receipt.json")))
        require(locked["test_used"] is False and locked["selected_on"] == "validation only", "Baseline selected using test")
        require(locked["trials_sha256"] == file_hash(trials_path) and locked["config_sha256"] == file_hash(config_path), "Baseline validation lock hash differs")
        require(len(trials) == count and pick_trial(trials)["config"] == read(config_path), "Baseline grid/winner differs")
        baseline_rows.append(dict(model=model, grid_candidates=len(trials), eligible_candidates=sum(t["validation_loss"] is not None for t in trials), failed_origin_fits=sum(len(t.get("failures", [])) for t in trials), selected_config=json.dumps(read(config_path)), validation_loss=pick_trial(trials)["validation_loss"]))
    baseline_summary = pd.DataFrame(baseline_rows)
    baseline_summary.to_csv(output / "baseline_selection.csv", index=False)

    # Recompute diagnostics from raw forecast errors, independently of details.csv.
    bootstrap_rows, regime_rows, regime_inventory = [], [], []
    for manifest_path in sorted(candidate.rglob("diagnostic_manifest.json")):
        dest = manifest_path.parent
        info = read(track(dest / "manifest.json"))
        local = read(dest.parent / "candidate.json") if "folds" in dest.parts else manifest
        regimes, threshold = volatility(data, local)
        expected = read(track(manifest_path))
        close(threshold, expected["threshold"], "Volatility cutoff differs")
        require(expected["threshold_fitted_on"] == "train only" and expected["known_at"] == "origin close", "Volatility lookahead")
        saved_regimes = pd.read_csv(track(dest / "origin_regimes.csv"))
        require(regimes.origin_date.equals(saved_regimes.origin_date) and regimes.regime.equals(saved_regimes.regime), "Origin regime differs")
        close(regimes.sigma20, saved_regimes.sigma20, "Rolling sigma differs")
        group = dest.relative_to(candidate).as_posix()
        regimes["group"] = group
        regime_inventory.append(regimes.assign(train_p90=threshold))
        own = {}
        for value in info["source_forecasts"]:
            path = portable(value)
            meta = read(track(path.with_suffix(".json")))
            frame = pd.read_csv(track(path))
            own[meta["model"]] = (frame, validate_frame(frame, meta, local, data))
        stored_ci = pd.read_csv(track(dest / "paired_block_intervals.csv"))
        stored_groups = pd.read_csv(track(dest / "regime_period_scores.csv"))
        for model, (frame, errors) in own.items():
            for h in (1, 5, 20):
                mask = frame.horizon.to_numpy() == h
                for target in ("open", "close"):
                    e = errors[target][mask]
                    delta = np.abs(e) - np.abs(own["naive"][1][target][mask])
                    low, high = moving_interval(delta)
                    row = stored_ci.loc[(stored_ci.model == model) & (stored_ci.horizon == h) & (stored_ci.target == target)]
                    require(len(row) == 1 and int(row.iloc[0].n) == len(e) and int(row.iloc[0].block) == 20 and int(row.iloc[0].draws) == 2000, "Bootstrap coverage/config differs")
                    close([low, high, delta.mean()], row.iloc[0][["ci_low", "ci_high", "mae_difference_vs_naive"]].to_numpy(dtype=float), "Independent paired CI differs")
                    bootstrap_rows.append(dict(group=group, model=model, horizon=h, target=target, n=len(e), difference=delta.mean(), ci_low=low, ci_high=high, block=20, draws=2000))
                    for grouping in ("regime", "period"):
                        for label in regimes[grouping].unique():
                            part = e[regimes[grouping].to_numpy() == label]
                            row = stored_groups.loc[(stored_groups.model == model) & (stored_groups.horizon == h) & (stored_groups.target == target) & (stored_groups.grouping == grouping) & (stored_groups.group == label)]
                            require(len(row) == 1 and int(row.iloc[0].n) == len(part), "Regime/period sample differs")
                            close([np.abs(part).mean(), np.sqrt(np.mean(part ** 2))], row.iloc[0][["mae", "rmse"]].to_numpy(dtype=float), "Regime/period metrics differ")
                            regime_rows.append(dict(group=group, model=model, horizon=h, target=target, grouping=grouping, label=label, n=len(part), mae=np.abs(part).mean(), rmse=np.sqrt(np.mean(part ** 2))))
    bootstrap = pd.DataFrame(bootstrap_rows)
    bootstrap.to_csv(output / "paired_intervals.csv", index=False)
    regime_table = pd.DataFrame(regime_rows)
    regime_table.to_csv(output / "regime_period_scores.csv", index=False)
    regime_main_summary = regime_table.loc[regime_table.group.str.startswith("evaluation-main/")].copy()
    regime_main_summary["seed"] = regime_main_summary.group.str.extract(r"seed-(\d+)").astype(int)
    regime_main_summary = regime_main_summary.groupby(["model", "horizon", "target", "grouping", "label"]).agg(n=("n", "first"), seeds=("seed", "nunique"), mae=("mae", "mean"), mae_sd=("mae", "std"), rmse=("rmse", "mean")).reset_index()
    regime_main_summary.to_csv(output / "regime_period_summary.csv", index=False)
    regimes = pd.concat(regime_inventory, ignore_index=True)
    regimes.to_csv(output / "origin_regimes.csv", index=False)
    print(f"Verified {len(bootstrap)} bootstrap intervals and {len(regime_rows)} regime/period metrics", flush=True)

    # Evidence ledger is deliberately separate from the frozen audit acceptance gate.
    audit_dir = ROOT / "artifacts/local/pc-rerun-20261030/audit"
    audit = read(track(audit_dir / "audit.json"))
    comparisons = pd.read_csv(track(audit_dir / "crosscheck.csv"))
    ledger = comparisons.loc[comparisons.status == "unresolved"].copy()
    previous_close = pd.Series(data.close.shift().to_numpy(), index=data.date)
    ledger["previous_close"] = ledger.date.map(previous_close)
    ledger["previous_close_anchor_matches"] = False
    for field in ("open", "high", "low"):
        mask = ledger.field == field
        previous = ledger.loc[mask, "previous_close"].to_numpy()
        reference = ledger.loc[mask, "reference"].to_numpy()
        predicted = np.maximum(reference, previous) if field == "high" else np.minimum(reference, previous) if field == "low" else previous
        ledger.loc[mask, "previous_close_anchor_matches"] = np.isclose(ledger.loc[mask, "original"], predicted, rtol=0, atol=0.02)
    anchor_summary = ledger.groupby(["provider", "field"]).agg(discrepancies=("date", "size"), previous_close_anchor_matches=("previous_close_anchor_matches", "sum")).reset_index()
    anchor_summary["interpretation"] = "diagnostic_only_not_price_adjudication"
    anchor_summary.to_csv(output / "previous_close_anchor_diagnostic.csv", index=False)
    range_rows = ledger.loc[ledger.field.isin(["high", "low"])]
    range_anchor_count = int(range_rows.previous_close_anchor_matches.sum())
    ledger["decision"] = "unresolved"
    ledger["evidence_url"], ledger["evidence_sha256"] = "", ""
    review_path = ROOT / "artifacts/local/pc-preflight-20261030/publisher_close_review/cached_reparse.json"
    cases = read(track(review_path))["cases"]
    source_catalog = []
    for case in cases:
        evidence = portable(case["evidence_path"])
        require(file_hash(evidence) == case["evidence_sha256"], "Publisher evidence hash differs")
        source_catalog.append(case)
        matched = (ledger.date == case["date"]) & (ledger.field == "close")
        ledger.loc[matched, "evidence_url"] = case["url"]
        ledger.loc[matched, "evidence_sha256"] = case["evidence_sha256"]
        if case["status"] == "corroborates_original":
            validate_publisher_case({**case, "symbol": "VN30", "field": "close", "semantics": "session_close"}, case["original_close"], file_hash(evidence))
            ledger.loc[matched, "decision"] = "original_corroborated_not_dataset_acceptance"
        else:
            ledger.loc[matched, "decision"] = "candidate_value_close_semantics_unverified"
    # Preserve additional PDF observations already visually reviewed in the agent log.
    pdf_manifests = [ROOT / "data/raw/source_evidence/pc-20261030/manifest.json", ROOT / "data/raw/source_evidence/close-disputes-20261030/manifest.json"]
    pdf_notes = {
        "csi_20200409.pdf": ("2020-04-09", 697.85, "session_close", "CSI cash VN30 table; visual review logged"),
        "phfm_20200923.pdf": ("2020-09-22", 852.72, "session_close", "Phu Hung publication 23/09 describing session 22/09; visual review logged"),
        "pinetree_20210305.pdf": ("2021-03-05", 1174.16, "end_of_day_table_close_unverified", "TTCK VIET NAM/VN30 table separate from futures; visual review logged"),
        "pinetree_20210324.pdf": ("2021-03-24", 1167.49, "end_of_day_table_close_unverified", "TTCK VIET NAM/VN30 table separate from futures; visual review logged"),
    }
    for manifest_path in pdf_manifests:
        catalog = read(track(manifest_path))
        for item in (catalog["sources"] if isinstance(catalog, dict) else catalog):
            if "path" not in item or Path(item["path"]).name not in pdf_notes:
                continue
            date, value, semantics, locator = pdf_notes[Path(item["path"]).name]
            raw = portable(item["path"])
            require(file_hash(raw) == item["sha256"], "Reviewed PDF changed")
            observation = dict(date=date, market_date=date, symbol="VN30", field="close", value=value, semantics=semantics, evidence_locator=locator, evidence_path=item["path"], evidence_sha256=item["sha256"], url=item["url"])
            source_catalog.append(observation)
            matched = (ledger.date == date) & (ledger.field == "close")
            if semantics == "session_close":
                original_value = float(data.loc[data.date == date, "close"].item())
                validate_publisher_case(observation, original_value, file_hash(raw))
                ledger.loc[matched, "decision"] = "original_corroborated_not_dataset_acceptance"
            # Existing and new evidence remain visible, even where semantics conflict.
            for index in ledger.index[matched]:
                for column, content in (("evidence_url", item["url"]), ("evidence_sha256", item["sha256"])):
                    previous = ledger.at[index, column]
                    ledger.at[index, column] = (previous + " | " if previous else "") + content
    ledger.to_csv(output / "data_adjudication.csv", index=False)
    save_json(output / "source_catalog.json", dict(classification="partial_publisher_evidence_not_dataset_acceptance", observations=source_catalog, exact_raw_files_required_locally=True))

    resources = inventory.groupby("model").agg(parameters=("trainable_parameters", "first"), train_seconds_mean=("train_seconds", "mean"), peak_allocated_GiB=("peak_allocated_GiB", "max")).reset_index()
    for i, row in resources.iterrows():
        benchmark = read(track(candidate / "checkpoints" / f"benchmark-{row.model}-s42" / "training.json"))
        forecast = read(track(candidate / "benchmarks" / (row.model + ".json")))
        resources.loc[i, "epoch_seconds"] = benchmark["elapsed_seconds"]
        resources.loc[i, "validation_32_origins_seconds"] = forecast["elapsed_seconds"]
    resources.to_csv(output / "resources.csv", index=False)

    completion = pd.DataFrame([
        ("Environment/CUDA/model/tokenizer hashes", "verified", "benchmarks/; checkpoint provenance; numerical_validation"),
        ("Raw replay/timestamp/SQLite integrity", "verified", "audit/audit.json"),
        ("Market OHLC adjudication", "unverified", "data_adjudication.csv; evidence_review.md"),
        ("Official exchange calendar", "unverified", "calendar_crosscheck/audit; observed VNINDEX dates only"),
        ("Main 4 models x 3 seeds x ZS/SFT", "verified_exploratory", "main_summary.csv; 48 neural forecasts"),
        ("Naive/Ridge/ARIMA/ETS validation-only selection", "verified_exploratory", "baseline_selection.csv; original tuning receipts"),
        ("Best-trained and selected including epoch 0", "verified_exploratory", "checkpoint_selection.csv; selected_scores.csv"),
        ("Q2 paired fixed-encoder ablation, 3 seeds", "verified_exploratory", "ablation_summary.csv; result.json"),
        ("Q3 nested budgets and random LR trials, 3 seeds", "verified_exploratory", "learning_curve.csv; random_lr_selection.csv"),
        ("Q4 periods/volatility/2 folds/paired bootstrap", "verified_exploratory_limited_regime_coverage", "fold_scores.csv; origin_regimes.csv; paired_intervals.csv"),
        ("Independent forecast/SQLite MAE and RMSE", "verified", "review/numerical_validation.json; recomputed_metrics.csv"),
        ("Native interrupted/resumed GPU equivalence", "verified_mini_only", "pc-preflight-20261030/native_resume_smoke.json"),
        ("Resume equivalence all variants / forced OOM", "not_fully_tested", "Do not generalize mini proof"),
        ("Exact checkpoint pretraining exclusions", "unverified", "checkpoint_provenance.yaml; retrospective evaluation"),
        ("Research acceptance gate", "not_achieved", "Primary run remains blocked; no candidate promotion"),
    ], columns=["requirement", "status", "evidence_or_limitation"])
    completion.to_csv(output / "completion_matrix.csv", index=False)
    software_tests = output / "software_tests.json"
    software_note = "Các kiểm thử phần mềm trước chạy đạt 58 ca, skipped=1 native opt-in đã chạy riêng."
    if software_tests.exists():
        test_info = read(track(software_tests))
        require(test_info["status"] == "pass", "Software tests did not pass")
        software_note = f"Bộ kiểm thử sau hoàn thiện đạt {test_info['tests']} ca, skipped={test_info['skipped']}; native GPU opt-in đã chạy riêng trước đó."

    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
    for ax, target in zip(axes, ("open", "close")):
        view = main_summary.loc[(main_summary.target == target) & (main_summary.split == "test")]
        pivot = view.pivot(index="model", columns="horizon", values="mae")
        pivot.plot.bar(ax=ax, rot=65)
        ax.set_title(f"{target.title()} MAE | 3-seed mean | exploratory")
        ax.set_ylabel("VN30 index points")
        ax.grid(axis="y", alpha=0.2)
    fig.savefig(output / "main_mae.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(12, 6), layout="constrained")
    for i, target in enumerate(("open", "close")):
        for j, h in enumerate((1, 5, 20)):
            ax = axes[i, j]
            part = ablation_summary.loc[(ablation_summary.split == "test") & (ablation_summary.target == target) & (ablation_summary.horizon == h) & (ablation_summary.model != "naive")]
            ax.bar(part.model.str.removeprefix("representation-"), part.mae, yerr=part.mae_sd, capsize=4)
            ax.set_title(f"{target}, h={h}")
            ax.set_ylabel("MAE (index points)")
    fig.suptitle("Fixed-encoder quantization ablation | seed SD | exploratory")
    fig.savefig(output / "ablation_mae.png", dpi=160)
    plt.close(fig)

    def link(path):
        return Path(os.path.relpath(path, args.report.parent)).as_posix()
    split_rows = [dict(split=s, first=v["first_date"], last=v["last_date"], sessions=v["rows"], origins=len(manifest["origins"][s])) for s, v in manifest["boundaries"].items()]
    regime_main = regimes.loc[regimes.group == "evaluation-main/scores/seed-42/test"]
    cluster_count = regime_main.loc[regime_main.regime == "high", "high_cluster"].nunique()
    delta_base = (matrix(main_scores).set_index("model").loc["kronos-base", "h=20"] - matrix(main_scores).set_index("model").loc["kronos-base-ft", "h=20"])
    test_ci = bootstrap.loc[(bootstrap.group == "evaluation-main/scores/seed-42/test") & (bootstrap.target == "close") & (bootstrap.model.isin(["kronos-mini-ft", "kronos-small-ft", "kronos-base-ft", "chronos2-ft"]))]
    fold_ranges = []
    for name in ("fold1", "fold2"):
        m = read(track(candidate / "followups/folds" / name / "candidate.json"))
        fold_ranges.append(dict(fold=name, train_end=m["boundaries"]["train"]["last_date"], validation_start=m["boundaries"]["validation"]["first_date"], validation_end=m["boundaries"]["validation"]["last_date"], test_start=m["boundaries"]["test"]["first_date"], test_end=m["boundaries"]["test"]["last_date"], test_origins=len(m["origins"]["test"])))
    curve_close = curve.loc[(curve.split == "test") & (curve.target == "close")]
    curve_display = curve_close.pivot_table(index=["model", "initialization", "train_rows", "train_windows"], columns="horizon", values="mae").reset_index().rename(columns={1: "h=1", 5: "h=5", 20: "h=20"})
    ablation_display = ablation_summary.loc[(ablation_summary.split == "test") & (ablation_summary.target == "close")]
    fold_display = fold_scores.loc[(fold_scores.split == "test") & (fold_scores.target == "close")].pivot_table(index=["fold", "model"], columns="horizon", values="mae").reset_index().rename(columns={1: "h=1", 5: "h=5", 20: "h=20"})
    regime_display = regime_main_summary.loc[(regime_main_summary.target == "close") & (regime_main_summary.horizon == 20) & regime_main_summary.model.isin(["naive", "kronos-mini-ft", "kronos-small-ft", "kronos-base-ft", "chronos2-ft"])]
    def aval(arm, h):
        return float(ablation_display.loc[(ablation_display.model == "representation-" + arm) & (ablation_display.horizon == h), "mae"].item())
    def cval(model, init, rows, h):
        return float(curve_close.loc[(curve_close.model == model) & (curve_close.initialization == init) & (curve_close.train_rows == rows) & (curve_close.horizon == h), "mae"].item())
    def fval(fold, model, h):
        return float(fold_scores.loc[(fold_scores.fold == fold) & (fold_scores.model == model) & (fold_scores.split == "test") & (fold_scores.target == "close") & (fold_scores.horizon == h), "mae"].item())
    origin_indices = np.asarray(manifest["origins"]["test"])
    target_dates = data.date.to_numpy()[origin_indices + 1]
    open_anomaly = (target_dates >= "2025-05-05") & (target_dates <= "2025-08-11")
    naive_open_errors = np.abs(data.close.to_numpy()[origin_indices] - data.open.to_numpy()[origin_indices + 1])
    text = f"""# Nghiên cứu dự báo VN30 trên PC: Kronos mini, small, base và Chronos-2-small

**Ngày tổng hợp:** {datetime.now(timezone.utc).astimezone().strftime('%d/%m/%Y')}. **Trạng thái: báo cáo kết quả thăm dò; nghiên cứu chính chưa hoàn tất vì dữ liệu chưa được chấp nhận.**

## Tóm tắt

Nghiên cứu đánh giá dự báo mức giá Open/Close VN30 với context 128 phiên, path 20 phiên và horizon 1/5/20. Ba Kronos và Chronos-2-small được chạy zero-shot/SFT bằng ba seed, đối chiếu Naive, Ridge, ARIMA và ETS. Bổ sung learning curve pretrained/random, ablation lượng tử hóa và hai expanding folds. Tất cả kết quả dưới đây đến từ lượt PC; không lấy checkpoint hoặc score cũ để lấp.

Trong bảng chính, Naive có MAE Close thấp hơn các neural model ở cả ba horizon khi lấy trung bình ba seed. SFT Kronos-base giảm MAE Close h=20 khoảng **{delta_base:.3f} điểm** so với zero-shot nhưng vẫn chưa vượt Naive. Không suy từ đây rằng mọi foundation model đều kém baseline trong mọi điều kiện. Native validation của Chronos chọn epoch 0 ở cả ba seed; điểm best-trained SFT được giữ riêng để đo tác động cập nhật.

## 1. Dữ liệu và mức độ tin cậy

Snapshot VNDIRECT gồm 2.271 phiên từ 24/08/2017 đến 01/10/2026; đơn vị điểm chỉ số, ngày theo múi giờ Việt Nam. SHA256: `{manifest['sha256']}`. Không có chỉnh sửa giá, nội suy ngày hay ghép nguồn theo ô.

Raw replay, timestamp, SQLite integrity và flags đã đạt kiểm tra. Tuy nhiên có 1.230 phép so sánh OHLC lệch hơn 0,02 điểm với VPS/DNSE, gồm 60 ngày Close khác nguồn. Đây là các sai khác cần phân xử, không phải 1.230 lỗi VNDIRECT đã chứng minh. Có 78 Open bằng Close trước, trong đó 71 phiên liên tiếp 05/05–11/08/2025; một hàng ngoài request, giữ nguyên và có chẩn đoán riêng. Request từ năm 2012 nhưng nguồn chỉ trả lịch sử từ 2017; không xem giai đoạn trước đó là đã được thu thập.

Lịch quan sát VNINDEX từ VPS khớp các ngày snapshot; nguồn DNSE thiếu 33 ngày. Điều này hỗ trợ lịch trong phạm vi nguồn, chưa phải lịch sàn chính thức. Ngưỡng 0,02 chỉ dùng phát hiện sai khác. Bản tin độc lập hỗ trợ một số giá gốc và một số giá khác; không dùng đa số phiếu để chọn nguồn. Sổ bằng chứng [data_adjudication.csv]({link(output / 'data_adjudication.csv')}) giữ mọi sai khác, URL/hash và trạng thái; không nâng trạng thái audit đang khóa. Hàng ngoài request là 01/10/2026; giữ nguyên để đối chiếu snapshot, không gọi là nằm trong request.

Trong test h=1 có {int(open_anomaly.sum())} origin mà ngày đích nằm trong đoạn Open bất thường. Naive có Open MAE bằng {naive_open_errors[open_anomaly].mean():.3f} trên các nhãn này, so với {naive_open_errors[~open_anomaly].mean():.3f} trên {int((~open_anomaly).sum())} origin còn lại. Đây là chẩn đoán theo đoạn đã phát hiện, không phải tập test mới để chọn model; nó giải thích vì sao không được coi Open MAE thấp là bằng chứng dự báo giá mở cửa chính thức tốt.

Kiểm tra giả thuyết nến bao gồm mốc Close trước: công thức `High=max(High nguồn đối chiếu, Close trước)` và `Low=min(Low nguồn đối chiếu, Close trước)` chỉ khớp {range_anchor_count}/{len(range_rows)} sai khác High/Low trong ngưỡng 0,02. Vì vậy đây không phải lời giải chung cho khác biệt nhà cung cấp và không đủ căn cứ sửa giá. [Chẩn đoán theo nguồn/trường]({link(output / 'previous_close_anchor_diagnostic.csv')}) giữ kết quả kiểm tra giả thuyết, tách khỏi quyết định phân xử.

Vì chưa giải thích đủ O/H/L/Close, kết quả chỉ mô tả hành vi trên nhãn của snapshot, đặc biệt Open/gap còn thăm dò. Ngày bắt đầu chuỗi Open bất thường trùng KRX vận hành là giả thuyết, chưa chứng minh nguyên nhân. [Hồ sơ điều tra](../artifacts/local/pc-preflight-20261030/evidence_review.md) lưu nguồn và giới hạn.

## 2. Thiết kế và khả năng tái lập

{md_table(pd.DataFrame(split_rows))}

Mỗi origin đặt sau Close phiên t; toàn bộ 20 nhãn nằm trong split tương ứng. Context được phép dùng quá khứ trước ranh giới. Dự báo được lưu trước khi ghép nhãn. Test lịch sử đã được xem trong nghiên cứu trước, nên đây là đánh giá hồi cứu. Không tuyên bố checkpoint pretrained chưa từng thấy VN30; cutoff của mọi revision chưa được xác minh đầy đủ. Các fold lịch sử cũng không phải backtest triển khai sạch.

Kronos-mini dùng Tokenizer-2k; small/base dùng Tokenizer-base. Predictor SFT cập nhật toàn bộ trọng số, tokenizer cố định. FP32, AdamW, tối đa năm epoch, LR 1e-6, effective batch 16, gradient clipping 1, weight decay 0,01. Seed 42/43/44. Kronos lấy trung bình ba path, temperature 1, top-p 0,9; Chronos lấy trung bình đều 13 quantile, không phải 13 mẫu ngẫu nhiên. Volume/amount thiếu được điền 0 theo adapter; đó không phải khối lượng thực. Kronos nhận ngày phiên đích lịch sử đã biết, là giới hạn của đánh giá hồi cứu.

MAE là metric chính; RMSE bổ sung. Điểm Open/Close có đơn vị điểm chỉ số. Seed SD mô tả biến thiên chạy, không thay thế khoảng tin cậy theo thị trường. Nhãn `-ft` luôn chỉ **best-trained**; bảng selected riêng tuân theo validation có xét epoch 0. Bảng MAE/RMSE validation/test đầy đủ nằm ở [main_summary.csv]({link(output / 'main_summary.csv')}).

## 3. Q1 — Neural model và baseline thống kê

Naive đặt Open/Close ở mọi horizon bằng Close tại origin. Ridge học ánh xạ từ context OHLC sang path tương lai, scaler/hệ số chỉ fit trên train. Các cấu hình baseline chọn bằng validation, tiêu chí trung bình MAE Open/Close tại ba horizon chuẩn hóa bằng độ lệch chuẩn train. ARIMA/ETS refit từng origin trên 128 phiên quá khứ từng kênh; không có seasonal. Ứng viên không phủ đủ mẫu hoặc hội tụ lỗi không được dùng để thắng lựa chọn; không Naive fallback.

{md_table(baseline_summary)}

### Test: MAE Close, trung bình ± SD ba seed

{md_table(matrix(main_scores, spread=True))}

### Test: MAE Open, trung bình ± SD ba seed

{md_table(matrix(main_scores, 'open', spread=True))}

Baseline deterministic dùng chung forecast giữa các seed; ba dòng tương ứng không phải ba lần ước lượng độc lập. ARIMA(0,1,0) và ETS level trong cấu hình thắng cho Close trùng Naive; không diễn giải ba nhãn này thành ba bằng chứng độc lập về ưu thế.

![MAE chính]({link(output / 'main_mae.png')})

**Trả lời Q1:** chưa có lợi thế tổng thể của neural model trước Naive trên Close trong thiết lập đã thử. Kết luận chỉ áp dụng snapshot, protocol và các checkpoint này; các kết quả Open chịu giới hạn dữ liệu nêu trên.

## 4. SFT và lựa chọn có tính epoch 0

{md_table(inventory[['model', 'seed', 'best_trained_epoch', 'selected_epoch', 'initial_validation_loss', 'best_trained_validation_loss', 'selected_validation_loss']])}

Chronos có native validation pretrained tốt hơn mọi epoch cập nhật ở cả ba seed. Vì vậy lựa chọn có xét epoch 0 là pretrained; không được gọi SFT là cải thiện validation. Kronos chọn epoch 5 trong ngân sách năm epoch, không khẳng định đã hội tụ. Token cross-entropy và quantile loss không so trực tiếp giữa họ model/tokenizer. [Selected scores]({link(output / 'selected_scores.csv')}) lấy đúng forecast của checkpoint đã được validation chọn, không chọn theo test.

## 5. Q2 — Kích thước và representation

Bảng chính cho phép so sánh các hệ thống mini/small/base. Mini khác tokenizer nên khác biệt không phải ảnh hưởng thuần túy của số tham số. Đối chứng representation dùng cùng encoder tokenizer small cố định; đặc trưng liên tục L2-normalized so với đặc trưng BSQ; cùng backbone random small, numeric head/MSE, dữ liệu và ngân sách. Ba seed đều có hash backbone khởi tạo khớp giữa hai nhánh.

### Ablation: Close test, mean và SD giữa seed

{md_table(ablation_display, ['model', 'horizon', 'seeds', 'mae', 'mae_sd', 'rmse'])}

![Ablation Open/Close]({link(output / 'ablation_mae.png')})

Bảng đầy đủ [ablation_summary.csv]({link(output / 'ablation_summary.csv')}) chứa cả Open/Close và validation. Đây là phép can thiệp lượng tử hóa trong thiết lập cố định, không tách mọi thành phần của K-line representation. Không dùng Kronos–Chronos hoặc bỏ kênh giá để suy quan hệ nhân quả cho toàn bộ representation. Kết luận về chiều tác động phải đọc theo từng horizon/target trong bảng, không khẳng định lợi ích đồng nhất.

**Trả lời Q2:** với Close, hai nhánh gần như ngang nhau tại h=1 (continuous {aval('continuous', 1):.3f}, quantized {aval('quantized', 1):.3f} điểm); lượng tử hóa có MAE trung bình cao hơn ở h=5 ({aval('quantized', 5):.3f} so với {aval('continuous', 5):.3f}) và h=20 ({aval('quantized', 20):.3f} so với {aval('continuous', 20):.3f}). Chưa có bằng chứng lượng tử hóa cải thiện đồng nhất trong ablation này. SD giữa ba seed lớn ở một số ô; không coi chênh lệch mean nhỏ là ý nghĩa thống kê. Ở bảng SFT, mini có Close MAE thấp hơn small tại cả ba horizon, nên tăng kích thước cũng không cho lợi thế đơn điệu; khác tokenizer vẫn ngăn diễn giải thành hiệu ứng số tham số thuần túy.

## 6. Q3 — Lượng dữ liệu và predictor pretraining

Train 500/1.000/toàn bộ 1.589 phiên lồng nhau cùng ngày kết thúc, tương ứng 353/853/1.442 cửa sổ. Giữ nguyên validation/test. Hai model đại diện: Kronos-small và Chronos-2-small; mỗi cấu hình ba seed, pretrained hoặc predictor random. Random chọn LR trong 1e-6/1e-5/1e-4 bằng native validation; lưu trial thắng và dùng trực tiếp checkpoint đó để tránh train trùng. Sáu full-budget pretrained checkpoint được tái dùng từ lượt PC sau kiểm protocol, không lấy từ môi trường cũ.

### Learning curve Close test

{md_table(curve_display)}

![Learning Kronos](../artifacts/local/pc-exploratory-20261030/learning/learning_curve_kronos-small-ft.png)

![Learning Chronos](../artifacts/local/pc-exploratory-20261030/learning/learning_curve_chronos2-ft.png)

Bảng [learning_curve.csv]({link(output / 'learning_curve.csv')}) chứa cả target, split, mean/SD và số cửa sổ. [random_lr_selection.csv]({link(output / 'random_lr_selection.csv')}) ghi lựa chọn validation. Sai số thay đổi theo budget không được mặc định đơn điệu. Lợi ích predictor pretraining chỉ được kết luận trong ngân sách huấn luyện đã thử; random Kronos vẫn dùng tokenizer pretrained. Không đồng nhất năm epoch với tối ưu đến hội tụ hoặc random predictor với toàn hệ thống chưa pretrain.

**Trả lời Q3:** pretrained Chronos có Close MAE thấp hơn random trong cả chín ô budget/horizon; random còn kém xa trong ngân sách này. Kronos-small không cho lợi ích phổ quát: tại 1.000 phiên, random tốt hơn pretrained ở h=5/20 ({cval('kronos-small-ft', 'random', 1000, 5):.3f}/{cval('kronos-small-ft', 'random', 1000, 20):.3f} so với {cval('kronos-small-ft', 'pretrained', 1000, 5):.3f}/{cval('kronos-small-ft', 'pretrained', 1000, 20):.3f}); full budget cũng có lợi thế random tại h=5/20. Với pretrained Kronos-small, thêm dữ liệu giúp h=20 nhưng không cải thiện h=1/5. Không dùng kết quả test này để đổi LR/epoch hoặc chọn budget triển khai. Random được thử ba LR trong khi pretrained giữ LR chính, nên tổng chi phí tìm cấu hình không bằng nhau dù mỗi trial đều tối đa năm epoch.

## 7. Q4 — Seed, thời gian, volatility và folds

Volatility là SD của 20 log-return đã biết tại origin (ddof=1); ngưỡng p90 chỉ fit trên train. Test chính có **{int((regime_main.regime == 'high').sum())}/{len(regime_main)} origin volatility cao**, tạo **{cluster_count} cụm liên tiếp**. Cụm này không được mặc định là các biến cố độc lập. Ba đoạn test liên tiếp được chia theo origin; số mẫu và ranh giới có trong [origin_regimes.csv]({link(output / 'origin_regimes.csv')}). Không dùng `volatility_diagnostic.csv` mô tả theo return thực hiện tương lai làm regime của Q4.

Paired moving-block bootstrap so chênh lệch absolute error cùng origin với Naive: block 20 origin, 2.000 draws, percentile 95%, RNG seed 42. Đã tính lại độc lập từ forecast và SQLite; không bootstrap seed như các thị trường độc lập. CI chưa điều chỉnh multiple comparisons và phụ thuộc giả định block; không diễn giải thành bảo đảm lợi nhuận.

### CI Close của seed 42, bảng chính

{md_table(test_ci, ['model', 'horizon', 'n', 'difference', 'ci_low', 'ci_high'])}

Chênh lệch âm nghĩa là MAE thấp hơn Naive. CI từng seed và fold/ablation đầy đủ ở [paired_intervals.csv]({link(output / 'paired_intervals.csv')}); bảng regime/period ở [regime_period_scores.csv]({link(output / 'regime_period_scores.csv')}). Không lấy trung bình hai đầu CI qua các seed để tạo một CI tổng hợp.

### Close h=20 theo regime/giai đoạn, trung bình ba seed

{md_table(regime_display, ['model', 'grouping', 'label', 'n', 'mae', 'mae_sd'])}

Nhóm volatility được xác định tại origin, không phải từ giá tương lai tại ngày đích. Bảng trung bình/SD đầy đủ cho cả Open/Close và ba horizon ở [regime_period_summary.csv]({link(output / 'regime_period_summary.csv')}); subgroup ít mẫu không được coi là xác nhận lợi thế qua nhiều biến cố độc lập.

### Hai expanding folds, neural seed 42

{md_table(pd.DataFrame(fold_ranges))}

Mỗi fold huấn luyện và chọn checkpoint trên train/validation riêng trước test của fold. Chấm đủ bốn neural model zero-shot/best-trained và Naive; [fold_scores.csv]({link(output / 'fold_scores.csv')}) lưu metric validation/test. Fold hồi cứu có thể nằm trước thời điểm checkpoint công khai; không coi việc chia thời gian là bằng chứng loại bỏ rò rỉ pretraining.

### MAE Close của hai fold

{md_table(fold_display)}

**Trả lời Q4:** chưa có lợi thế ổn định trước Naive. Chronos SFT nhỉnh hơn Naive tại fold1 h=5 ({fval('fold1', 'chronos2-ft', 5):.3f} so với {fval('fold1', 'naive', 5):.3f}), nhưng không giữ lợi thế ở fold2; các neural model còn lại cũng không thắng nhất quán cả ba horizon và hai fold. Cả hai fold có **0 origin volatility cao** theo ngưỡng train riêng, nên chúng không bổ sung bằng chứng cho regime cao. Test chính chỉ có {int((regime_main.regime == 'high').sum())} origin cao trong {cluster_count} cụm; không thể suy độ bền qua nhiều khủng hoảng độc lập. Đọc CI từng seed/horizon để phân biệt chênh lệch số học với bằng chứng bất định.

## 8. Chi phí và kiểm định

RTX 4070 SUPER 12 GB, RAM khoảng 32 GB, Python 3.11.9; torch 2.14.0+cu130 đã kiểm CUDA thực tế. GPU chạy tuần tự. Bảng dưới là thời gian đo, không phải dự toán; peak allocated là bộ nhớ tensor do PyTorch ghi nhận, không phải tổng VRAM tiến trình.

{md_table(resources)}

Hạn gốc 31/10/2026 14:09:17 +07; hàng đợi kết thúc 30/10/2026 18:22:28 +07. Không reset đồng hồ. 90 cặp training/selection receipts gồm benchmark, main, LR trials và folds; không phải 90 mẫu nghiên cứu độc lập. Loss/history/checkpoint vẫn giữ trên PC; code, CSV, đồ thị và receipts được lưu Git.

Kiểm định số học trực tiếp: 88 nhóm score, 182 file forecast, 2.160 dòng metric khớp nhãn SQLite; 85 output receipts và 90 cặp training/selection khớp hash. Ca đổi ngày đích bị từ chối. Kiểm định thống kê độc lập lần này xác nhận {len(bootstrap)} CI và {len(regime_rows)} metric regime/period. {software_note} Native GPU resume mini sai khác tham số tối đa 5,96e-8; chưa kiểm stress forced-OOM và resume toàn bộ variant.

## 9. Kết luận và điều kiện chưa đạt

Các khoảng trống thí nghiệm của bài cũ đã có kết quả PC thăm dò: baseline thống kê, ba kích thước Kronos, ba seed, learning curve/random controls, ablation và folds. Tuy nhiên **nghiên cứu chính vẫn chưa đủ điều kiện chốt hoàn thiện**: nhãn OHLC chưa được phân xử đủ, Open chính thức và lịch sàn chưa xác nhận hoàn toàn, pretraining cutoff chưa đủ cho tuyên bố triển khai lịch sử sạch. Không dùng kết quả thăm dò để đóng cổng kiểm toán chính.

Ma trận nghiệm thu từng yêu cầu và bằng chứng/giới hạn: [completion_matrix.csv]({link(output / 'completion_matrix.csv')}). “Verified exploratory” chỉ xác nhận thí nghiệm và phép tính trên snapshot; không đồng nghĩa giá thị trường đã được xác nhận.

Không có backtest giao dịch, transaction costs, Directional Accuracy hoặc bản theo mẫu tạp chí trong phạm vi đã chốt. Sai số chỉ số không suy ra lợi nhuận. Nếu dữ liệu được hiệu chỉnh, phải có phiên bản/manifest riêng và kiểm tra lại toàn bộ thí nghiệm phụ thuộc; không đổi nhãn checkpoint của snapshot gốc.

## 10. Tái lập và hồ sơ nguồn

Từ repo root, dùng môi trường đã khóa và chạy:

```powershell
.venv/Scripts/python.exe experiments/verify_completed_candidate.py
.venv/Scripts/python.exe experiments/finalize_pc_report.py
```

Lệnh thứ nhất kiểm byte checkpoints local nên cần giữ thư mục weights. Lệnh thứ hai kiểm receipt/input/frozen core, tính lại thống kê, sinh bảng/hình và báo cáo này; không cần train/inference GPU lại. Cần giữ các raw công bố đã tải tại PC; [source_catalog.json]({link(output / 'source_catalog.json')}) ghi URL/hash để truy vết. Raw bổ sung không nằm trong Git; tải lại HTML động có thể không trùng bytes, khi đó phải dùng bản archive gốc chứ không sửa hash cho qua. Tham số `--candidate`, `--output`, `--report` cho phép chọn output; không trộn các snapshot. Xem [quy trình PC](PC_Rerun.md) cho tải dữ liệu, environment, train và inference; các stage cap/deadline vẫn áp dụng khi chạy tiếp lượt gốc.

- [Numerical validation](../artifacts/local/pc-exploratory-20261030/review/numerical_validation.json), [final verification]({link(output / 'verification.json')}) và [report sources]({link(output / 'report_sources.json')}).
- Model/tokenizer mapping: [Kronos chính thức](https://github.com/shiyu-coder/Kronos#-model-zoo); revision/hash cụ thể ở [checkpoint provenance](../data/manifests/checkpoint_provenance.yaml).
- Dữ liệu, request và raw replay: [audit snapshot](../artifacts/local/pc-rerun-20261030/audit/summary.md); [calendar đối chiếu](../artifacts/local/pc-preflight-20261030/calendar_crosscheck/audit/summary.md).
- Bản lịch sử được giữ riêng ở [báo cáo 27/10](VN30_Experimental_Results_Q1_Q4.md); không dùng số liệu đó trong các bảng PC.
"""
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(text, encoding="utf-8")
    save_json(output / "verification.json", dict(status="pass", evidence_scope="exploratory_only", dataset_accepted=False, dataset_sha256=manifest["sha256"], bootstrap_intervals=len(bootstrap), regime_period_metric_rows=len(regime_rows), random_lr_selections=len(lr_rows), baseline_grids_checked=3, paired_ablation_seeds=3, selected_main_checkpoints=len(inventory), research_complete=False, unfinished=["market_data_adjudication", "official_open_definition", "official_exchange_calendar", "research_acceptance_gate"]))
    inputs[Path(__file__).relative_to(ROOT).as_posix()] = file_hash(Path(__file__))
    save_json(output / "report_sources.json", dict(inputs=inputs, outputs={p.relative_to(ROOT).as_posix(): file_hash(p) for p in [args.report, *output.iterdir()] if p.is_file() and p.name != "report_sources.json"}, no_old_run_scores=True, checked_utc=datetime.now(timezone.utc).isoformat()))
    print(args.report, flush=True)


if __name__ == "__main__":
    main()

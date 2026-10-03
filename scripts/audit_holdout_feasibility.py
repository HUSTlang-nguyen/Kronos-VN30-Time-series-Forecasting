"""Calendar-based planning from unaccepted data; never writes accepted splits."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from build_hose_calendar import build, verify_sources
from phase1_pipeline import temporal_split
from verify_vnstock_capture import reconstruct

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    capture = ROOT / "data/raw/vnstock_audit/20261001T154235115506Z"
    manifest = json.loads((capture / "manifest.json").read_text())
    config = yaml.safe_load((ROOT / "configs/data_source_acceptance.yaml").read_text())
    config["end"] = manifest["end"]
    calendar_path = ROOT / "data/manifests/hose_calendar_evidence.yaml"
    calendar_config = yaml.safe_load(calendar_path.read_text())
    verify_sources(calendar_config)
    calendar = build(calendar_config, "2025-01-01", "2026-12-31")
    sessions = pd.DatetimeIndex(calendar.loc[calendar.is_session, "date"])
    response = manifest["providers"]["vci"]["http_captures"][0]
    raw = (capture / response["file"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != response["sha256"]:
        raise ValueError("VCI raw hash changed")
    frame = reconstruct("vci", raw, config)
    # Calendar coverage starts in 2025. This subset is used solely for planning:
    # the full-history dataset remains unchanged and unaccepted.
    observed = frame.loc[frame.date >= sessions[0], "date"]
    provenance_path = ROOT / "data/manifests/checkpoint_provenance.yaml"
    provenance = yaml.safe_load(provenance_path.read_text())
    study_path = ROOT / "configs/study.yaml"
    study = yaml.safe_load(study_path.read_text())
    _, report = temporal_split(observed, sessions,
                              provenance["common_provenance_boundary"]["timestamp_utc"], manifest["end"],
                              context=study["forecast"]["primary_context_length"],
                              path=study["forecast"]["path_length"])
    report.update({"classification": "planning_only_pending_G1_and_T012", "inference_allowed": False,
                   "observed_calendar_overlap_start": str(observed.iloc[0].date()),
                   "G1": "pending", "calendar_status": calendar_config["status"],
                   "calendar_evidence_sha256": hashlib.sha256(calendar_path.read_bytes()).hexdigest(),
                   "checkpoint_provenance_sha256": hashlib.sha256(provenance_path.read_bytes()).hexdigest(),
                   "study_sha256": hashlib.sha256(study_path.read_bytes()).hexdigest(),
                   "raw_response_sha256": response["sha256"],
                   "checkpoint_provenance": provenance,
                   "limitations": calendar_config["limitations"],
                   "contains_forecasts_or_metrics": False})
    output = ROOT / "artifacts/source_audit/vnstock_20261001T154235115506Z/candidate_holdout_feasibility.json"
    serialized = json.dumps(report, indent=2, default=str)
    if output.exists() and output.read_text() != serialized:
        raise ValueError("Planning inputs changed; preserve evidence and choose a new run")
    output.write_text(serialized, encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "checkpoint_provenance"}, indent=2))


if __name__ == "__main__":
    main()

import json
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from freeze_phase1 import CRITERIA, freeze, sha, verify_freeze


def fixture(root, shortened=False):
    # Every calendar/source acceptance record here is synthetic, in pytest's
    # temporary directory. It is never research evidence for the real project.
    inp = root / "inputs"
    inp.mkdir()
    dates = pd.date_range("2025-01-01", periods=450)
    days = pd.DataFrame({"date": dates, "is_session": True})
    if shortened:
        days["session_quality_flag"] = ""
        days["event_source"] = ""
        days.loc[0, ["session_quality_flag", "event_source"]] = ["shortened_session", "synthetic"]
    days.to_parquet(inp / "days.parquet", index=False)
    raw = pd.DataFrame({"date": dates[:400], "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0})
    raw.to_csv(inp / "raw.csv", index=False)
    (inp / "response.bin").write_bytes(b"synthetic original response")
    (inp / "evidence.txt").write_text("synthetic test review")

    def record(path):
        return {"path": str(path.relative_to(root)), "sha256": sha(path)}

    def save(name, value):
        path = inp / name
        path.write_text(yaml.safe_dump(value), encoding="utf-8")
        return record(path)

    acceptance = save("acceptance.yaml", {"status": "accepted", "provider": "synthetic", "units": "index_points",
                       "raw_csv_sha256": sha(inp / "raw.csv"), "crosschecked_dates": 30,
                       "extreme_return_dates_reviewed": 10, "unresolved_material_discrepancies": 0,
                       "criteria": {key: {"status": "pass", "review_note": "synthetic fixture only",
                                         "evidence": record(inp / "evidence.txt")} for key in CRITERIA}})
    calendar = save("calendar.yaml", {"status": "accepted", "calendar_sha256": sha(inp / "days.parquet"),
                    "exceptional_closures_reviewed": True, "sources": [record(inp / "evidence.txt")]})
    provenance = save("provenance.yaml", {"status": "accepted_for_phase_0",
                      "common_provenance_boundary": {"timestamp_utc": str(dates[191].tz_localize("UTC"))}})
    study = save("study.yaml", {"forecast": {"path_length": 20, "primary_context_length": 128}})
    spec = root / "spec.yaml"
    spec.write_text(yaml.safe_dump({"status": "accepted_inputs", "source_acceptance": acceptance,
                    "raw_csv": record(inp / "raw.csv"), "original_responses": [record(inp / "response.bin")],
                    "calendar": record(inp / "days.parquet"), "calendar_manifest": calendar,
                    "checkpoint_provenance": provenance, "study": study,
                    "freeze": str(dates[399].date()), "retrieved_at_utc": "2026-03-01T10:00:00Z"}), encoding="utf-8")
    return spec


def test_end_to_end_freeze_preserves_raw_and_verifies_every_output(tmp_path):
    spec = fixture(tmp_path)
    original = (tmp_path / "inputs/raw.csv").read_bytes()
    receipt = freeze(spec, tmp_path)
    assert receipt["classification"] == "confirmatory"
    assert "research_use" not in receipt["g1_criteria"]
    assert receipt["research_use_criterion"] == "excluded_by_user_request_2026-10-02"
    raw = tmp_path / "data/raw/vn30/synthetic/2026-03-01/vn30_daily.csv"
    assert raw.read_bytes() == original
    assert verify_freeze(tmp_path)["status"] == "verified"
    feasibility = json.loads((tmp_path / "data/manifests/holdout_feasibility.json").read_text())
    assert feasibility["test_origins"] == 126
    assert feasibility["contains_forecasts_or_metrics"] is False
    with pytest.raises(ValueError, match="already exist"):
        freeze(spec, tmp_path)
    (tmp_path / "data/processed/vn30_daily.parquet").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_freeze(tmp_path)


def test_freeze_keeps_shortened_session_and_reports_combined_flags(tmp_path):
    spec = fixture(tmp_path, shortened=True)
    freeze(spec, tmp_path)
    result = pd.read_parquet(tmp_path / "data/processed/vn30_daily.parquet")
    assert len(result) == 400
    assert result.quality_flags.iloc[0] == "first_return_undefined;shortened_session"
    report = json.loads((tmp_path / "reports/data_quality.json").read_text())
    assert report["flagged_observations"][0]["quality_flags"] == result.quality_flags.iloc[0]
    assert verify_freeze(tmp_path)["status"] == "verified"


def test_pending_gate_writes_no_outputs(tmp_path):
    spec = tmp_path / "spec.yaml"
    spec.write_text("status: pending\n")
    with pytest.raises(ValueError, match="pending"):
        freeze(spec, tmp_path)
    assert not (tmp_path / "data").exists()


def test_changed_snapshot_is_rejected_before_output(tmp_path):
    spec = fixture(tmp_path)
    (tmp_path / "inputs/raw.csv").write_text("changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        freeze(spec, tmp_path)
    assert not (tmp_path / "data").exists()


@pytest.mark.parametrize("criterion", ["reproducible_download", "dates_and_units",
    "independent_crosscheck", "material_discrepancies_resolved", "session_reconciliation"])
def test_permission_exclusion_does_not_relax_quality_gates(tmp_path, criterion):
    spec = fixture(tmp_path)
    acceptance_path = tmp_path / "inputs/acceptance.yaml"
    acceptance = yaml.safe_load(acceptance_path.read_text())
    assert set(acceptance["criteria"]) == {
        "reproducible_download", "dates_and_units", "independent_crosscheck",
        "material_discrepancies_resolved", "session_reconciliation"}
    acceptance["criteria"][criterion]["status"] = "pending"
    acceptance_path.write_text(yaml.safe_dump(acceptance), encoding="utf-8")
    config = yaml.safe_load(spec.read_text())
    config["source_acceptance"]["sha256"] = sha(acceptance_path)
    spec.write_text(yaml.safe_dump(config), encoding="utf-8")
    with pytest.raises(ValueError, match=f"G1 criterion unresolved: {criterion}"):
        freeze(spec, tmp_path)
    assert not (tmp_path / "data").exists()

"""Investigate every registered discrepancy using retained bytes and shorter requests."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import yaml

from audit_vnstock_sources import normalize
from review_vndirect_candidate import ROOT, load_audit, sha, write_once
from validate_vn30_sources import FIELDS, compare, parse
from verify_vnstock_capture import reconstruct


def row_at(frame: pd.DataFrame, day: pd.Timestamp) -> pd.Series | None:
    rows = frame.loc[frame.date.eq(day)]
    return rows.iloc[0] if len(rows) == 1 else None


def usable(row: pd.Series | None) -> bool:
    return row is not None and not any(bool(row[f]) for f in
                                     ("duplicate_date", "invalid_numeric", "invalid_ohlc", "outside_request"))


def published_verdict(field: str, primary: float, other: float, tolerance: float,
                      evidence: list[dict]) -> str:
    values = [float(e["value"]) for e in evidence if e["field"] == field]
    if not values:
        return "unresolved"
    primary_matches = all(abs(v - primary) <= tolerance + 1e-9 for v in values)
    other_matches = all(abs(v - other) <= tolerance + 1e-9 for v in values)
    if primary_matches and not other_matches:
        return "published_value_supports_vndirect"
    if other_matches and not primary_matches:
        return "published_value_supports_comparator"
    return "conflicting_or_inconclusive_publications"


def capture_requests(config: dict, years: list[int], destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {"classification": "shorter_window_diagnostic", "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "script_sha256": sha(Path(__file__).read_bytes()),
                "effective_config_sha256": sha(json.dumps(config, sort_keys=True).encode()), "requests": []}
    requests = []
    for year in years:
        start, end = f"{year}-01-01", min(f"{year}-12-31", config["end"])
        for provider, spec in config["providers"].items():
            params = {"symbol": "VN30", "resolution": spec["resolution"],
                      "from": int(pd.Timestamp(start, tz="UTC").timestamp()),
                      "to": int((pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)).timestamp()) - 1}
            requests.append((provider, start, end, spec["endpoint"] + "?" + urlencode(params), None))
    # Extend the two retained diagnostic providers to cover the last registered case.
    requests.extend([
        ("kbs", "2026-01-01", config["end"],
         "https://kbbuddywts.kbsec.com.vn/iis-server/investment/index/VN30/data_day?" +
         urlencode({"sdate": "01-01-2026", "edate": pd.Timestamp(config["end"]).strftime("%d-%m-%Y")}), None),
        ("vci", "2026-01-01", config["end"], "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart",
         {"timeFrame": "ONE_DAY", "symbols": ["VN30"],
          "to": int((pd.Timestamp(config["end"], tz="UTC") + pd.Timedelta(days=1)).timestamp()) - 1, "countBack": 300}),
    ])
    for provider, start, end, url, body in requests:
        entry = {"provider": provider, "start": start, "end": end, "url": url,
                 "method": "POST" if body else "GET", "body": body}
        request = Request(url, data=json.dumps(body).encode() if body else None,
                          headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
        try:
            try:
                with urlopen(request, timeout=30) as response:
                    raw, status = response.read(), response.status
            except HTTPError as exc:
                raw, status = exc.read(), exc.code
            name = f"{provider}_{start}.bin"
            write_once(destination / name, raw)
            entry.update(file=name, sha256=sha(raw), status=status)
        except (OSError, TimeoutError) as exc:
            entry.update(error=f"{type(exc).__name__}: {exc}")
        manifest["requests"].append(entry)
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(provider, start, entry.get("status", entry.get("error")), flush=True)
    return manifest


def execute(spec_path: Path, capture: Path, output: Path, fetch: bool) -> dict:
    spec_bytes = spec_path.read_bytes()
    spec = yaml.safe_load(spec_bytes)
    config, _, frames = load_audit(ROOT, spec["audit_config"], spec["audit"])
    cases = compare(frames, config)
    cases = cases.loc[cases.status.eq("discrepancy") &
                      (cases.left_provider.eq("vndirect") | cases.right_provider.eq("vndirect"))].copy()
    if len(cases) != spec["expected_case_count"] or cases.date.nunique() != spec["expected_date_count"]:
        raise ValueError("Registered discrepancy population changed")
    old_root = ROOT / spec["vnstock_capture"]
    old_manifest = json.loads((old_root / "manifest.json").read_bytes())
    old_config_bytes = (ROOT / spec["vnstock_config"]).read_bytes()
    if sha(old_config_bytes) != spec["vnstock_config_sha256"] or sha((ROOT / "scripts/audit_vnstock_sources.py").read_bytes()) != spec["vnstock_normalizer_sha256"]:
        raise ValueError("vnstock capture identity changed")
    old_config = yaml.safe_load(old_config_bytes) | {"end": old_manifest["end"]}
    for provider, entry in old_manifest["providers"].items():
        record, = entry["http_captures"]
        raw = (old_root / record["file"]).read_bytes()
        csv = (old_root / f"{provider}_normalized.csv").read_bytes()
        if sha(raw) != record["sha256"] or sha(csv) != entry["normalized_sha256"]:
            raise ValueError("vnstock raw or normalized bytes changed")
        frame = reconstruct(provider, raw, old_config)
        saved = normalize(pd.read_csv(old_root / f"{provider}_normalized.csv"), old_config).sort_values("date").reset_index(drop=True)
        pd.testing.assert_frame_equal(frame[["date", *FIELDS]], saved[["date", *FIELDS]], check_dtype=False, rtol=0, atol=1e-9)
        frames[provider] = frame
    if fetch:
        capture_requests(config, sorted(set(cases.date.dt.year)), capture)
    repeat_manifest = json.loads((capture / "manifest.json").read_bytes())
    if repeat_manifest["script_sha256"] != sha(Path(__file__).read_bytes()):
        raise ValueError("Repeat parser/capture script changed")
    if repeat_manifest["effective_config_sha256"] != sha(json.dumps(config, sort_keys=True).encode()):
        raise ValueError("Repeat request configuration changed")
    repeat, errors = {}, []
    for entry in repeat_manifest["requests"]:
        key = (entry["provider"], int(entry["start"][:4]))
        if "file" not in entry:
            errors.append(entry)
            continue
        raw = (capture / entry["file"]).read_bytes()
        if sha(raw) != entry["sha256"]:
            raise ValueError("Repeat response bytes changed")
        try:
            if entry["status"] != 200:
                raise ValueError(f"HTTP {entry['status']}")
            scoped = config | {"start": entry["start"], "end": entry["end"]}
            repeat[key] = reconstruct(entry["provider"], raw, scoped) if entry["provider"] in ("kbs", "vci") else parse(raw, scoped)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(entry | {"parse_error": str(exc)})
    publication_path = ROOT / spec["independent_evidence"]
    publications = yaml.safe_load(publication_path.read_bytes())
    for source in publications["sources"]:
        if sha((ROOT / source["file"]).read_bytes()) != source["sha256"]:
            raise ValueError("Publication bytes changed")
    findings, candles = [], []
    for index, case in enumerate(cases.itertuples(index=False), 1):
        day, field = case.date, case.field
        other = case.right_provider if case.left_provider == "vndirect" else case.left_provider
        primary_value = case.left_value if case.left_provider == "vndirect" else case.right_value
        other_value = case.right_value if case.left_provider == "vndirect" else case.left_value
        result = {"case_id": f"C{index:02}", "date": str(day.date()), "field": field,
                  "comparator": other, "vndirect": primary_value, "comparator_value": other_value,
                  "abs_difference": case.abs_difference, "tolerance": case.tolerance}
        for provider, frame in frames.items():
            row = row_at(frame, day)
            result[f"{provider}_field"] = None if row is None else float(row[field])
            result[f"{provider}_valid_candle"] = usable(row)
            repeated = row_at(repeat.get((provider, day.year), pd.DataFrame(columns=["date"])), day)
            result[f"{provider}_repeat_field"] = None if repeated is None else float(repeated[field])
            result[f"{provider}_repeat_valid_candle"] = usable(repeated)
            result[f"{provider}_repeat_unchanged"] = None if row is None or repeated is None else abs(float(row[field]) - float(repeated[field])) <= 1e-9
            if row is not None:
                previous = frame.loc[frame.date.lt(day) & ~frame.duplicate_date].sort_values("date").tail(1)
                previous_close = None if previous.empty else float(previous.iloc[0].close)
                candles.append({"case_id": result["case_id"], "provider": provider, "date": str(day.date()),
                                **{f: float(row[f]) for f in FIELDS}, "valid_candle": usable(row),
                                "previous_date": None if previous.empty else str(previous.iloc[0].date.date()),
                                "previous_close": previous_close,
                                "open_equals_previous_close": previous_close is not None and abs(float(row.open) - previous_close) <= 1e-9})
        evidence = [source for source in publications["sources"] if source["date"] == str(day.date())]
        result["publication_ids"] = ";".join(e["id"] for e in evidence if e["field"] == field)
        result["adjudication"] = published_verdict(field, primary_value, other_value, case.tolerance, evidence)
        result["root_cause"] = "unresolved"
        findings.append(result)
    output.mkdir(parents=True, exist_ok=True)
    files = {"cases.csv": pd.DataFrame(findings).to_csv(index=False, lineterminator="\n").encode(),
             "candles.csv": pd.DataFrame(candles).to_csv(index=False, lineterminator="\n").encode()}
    summary = {"classification": "case_investigation_not_G1_acceptance", "case_count": len(findings),
               "unique_dates": int(cases.date.nunique()), "spec_sha256": sha(spec_bytes),
               "source_manifest_sha256": sha((ROOT / spec["audit"] / "manifest.json").read_bytes()),
               "vnstock_manifest_sha256": sha((old_root / "manifest.json").read_bytes()),
               "repeat_capture": capture.relative_to(ROOT).as_posix(),
               "repeat_manifest_sha256": sha((capture / "manifest.json").read_bytes()),
               "publication_manifest_sha256": sha(publication_path.read_bytes()), "repeat_errors": errors,
               "adjudications": pd.Series([f["adjudication"] for f in findings]).value_counts().to_dict(),
               "gate_G1": "pending", "upstream_independence": "unverified",
               "files": {name: sha(raw) for name, raw in files.items()}}
    for name, raw in files.items():
        write_once(output / name, raw)
    write_once(output / "summary.json", json.dumps(summary, indent=2, sort_keys=True).encode())
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs/vndirect_discrepancy_investigation.yaml")
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(args.config.resolve(), args.capture.resolve(), args.output.resolve(), args.fetch), indent=2))

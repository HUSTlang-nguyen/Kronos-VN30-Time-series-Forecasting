"""Reproduce the T010 source audit; never treat the result as an accepted dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "manifests" / "source_crosscheck.parquet"
EVIDENCE = ROOT / "artifacts" / "source_audit" / "retrieval.json"
START = int(datetime(2012, 1, 1, tzinfo=timezone.utc).timestamp())
END = int(datetime(2026, 9, 26, tzinfo=timezone.utc).timestamp()) - 1
TOLERANCE = 0.02  # index points per field; fixed before reviewing comparisons
SEED = 20260926
FIELDS = ("open", "high", "low", "close")
SOURCES = {
    "vps": ("https://histdatafeed.vps.com.vn/tradingview/history", "D"),
    "vndirect": ("https://dchart-api.vndirect.com.vn/dchart/history", "D"),
    "dnse": ("https://api.dnse.com.vn/chart-api/v2/ohlcs/index", "1D"),
}


def fetch(source: str) -> tuple[pd.DataFrame, dict]:
    base, resolution = SOURCES[source]
    url = base + "?" + urlencode(
        {"symbol": "VN30", "resolution": resolution, "from": START, "to": END}
    )
    request = Request(url, headers={"User-Agent": "vn30-academic-source-audit/0.1"})
    error = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                raw = response.read()
            break
        except Exception as exc:
            error = exc
            if attempt == 2:
                raise RuntimeError(f"{source} download failed") from error
            time.sleep(2**attempt)
    payload = json.loads(raw)
    if payload.get("s") not in (None, "ok"):
        raise ValueError(f"{source}: unexpected status {payload.get('s')}")
    timestamps = payload.get("t", [])
    if not timestamps:
        raise ValueError(f"{source}: no observations")
    if any(len(payload.get(field[0], [])) != len(timestamps) for field in FIELDS):
        raise ValueError(f"{source}: inconsistent OHLC lengths")
    frame = pd.DataFrame(
        {"date": pd.to_datetime(timestamps, unit="s", utc=True).date}
        | {field: payload[field[0]] for field in FIELDS}
    )
    frame["date"] = pd.to_datetime(frame["date"])
    raw_row_count = len(frame)
    frame = frame.sort_values("date").reset_index(drop=True)
    duplicates = int(frame.date.duplicated().sum())
    ambiguous_dates = frame.loc[frame.date.duplicated(keep=False), "date"].unique()
    # Never pick one of two conflicting candles without independent evidence.
    frame = frame.loc[~frame.date.isin(ambiguous_dates)].copy()
    for field in FIELDS:
        frame[field] = pd.to_numeric(frame[field], errors="raise")
    if not np.isfinite(frame[list(FIELDS)].to_numpy()).all():
        raise ValueError(f"{source}: non-finite OHLC")
    if (frame[list(FIELDS)] <= 0).any().any():
        raise ValueError(f"{source}: non-positive OHLC")
    high_invalid = frame.high < frame[["open", "close", "low"]].max(axis=1) - TOLERANCE
    low_invalid = frame.low > frame[["open", "close", "high"]].min(axis=1) + TOLERANCE
    evidence = {
        "url": url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_row_count": raw_row_count,
        "unambiguous_row_count": len(frame),
        "first_date": str(frame.date.iloc[0].date()),
        "last_date": str(frame.date.iloc[-1].date()),
        "duplicates": duplicates,
        "ambiguous_dates_excluded": [str(pd.Timestamp(d).date()) for d in ambiguous_dates],
        "ohlc_inequality_failures": int((high_invalid | low_invalid).sum()),
        "ohlc_inequality_dates": [str(d.date()) for d in frame.loc[high_invalid | low_invalid, "date"]],
    }
    return frame, evidence


def selected_dates(primary: pd.DataFrame) -> dict[pd.Timestamp, str]:
    rng = np.random.default_rng(SEED)
    selected = {}
    for _, year_frame in primary.groupby(primary.date.dt.year, sort=True):
        picks = rng.choice(year_frame.date.to_numpy(), size=min(5, len(year_frame)), replace=False)
        for date in picks:
            selected[pd.Timestamp(date)] = "year_stratified"
    ranked = primary.assign(abs_return=primary.close.pct_change().abs()).nlargest(10, "abs_return")
    for date in ranked.date:
        selected[date] = (
            selected[date] + "+extreme_return" if date in selected else "extreme_return"
        )
    return selected


def audit(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    primary = frames["vps"]
    dates = selected_dates(primary)
    indexed = {name: frame.set_index("date") for name, frame in frames.items()}
    rows = []
    for date, reason in sorted(dates.items()):
        base = indexed["vps"].loc[date]
        for secondary in ("dnse", "vndirect"):
            found = date in indexed[secondary].index
            other = indexed[secondary].loc[date] if found else None
            row = {"date": date, "year": date.year, "selection": reason,
                   "primary": "vps", "secondary": secondary,
                   "secondary_available": found, "tolerance_points": TOLERANCE}
            for field in FIELDS:
                row[f"primary_{field}"] = float(base[field])
                row[f"secondary_{field}"] = float(other[field]) if found else np.nan
                row[f"abs_diff_{field}"] = abs(float(base[field]) - float(other[field])) if found else np.nan
                row[f"pass_{field}"] = bool(row[f"abs_diff_{field}"] <= TOLERANCE) if found else False
            row["all_fields_pass"] = found and all(row[f"pass_{field}"] for field in FIELDS)
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    frames, evidence = {}, {"seed": SEED, "tolerance_points": TOLERANCE, "sources": {}}
    for source in SOURCES:
        frames[source], evidence["sources"][source] = fetch(source)
        time.sleep(1)
    crosscheck = audit(frames)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    crosscheck.to_parquet(args.output, index=False)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    summary = {
        "sample_dates": int(crosscheck.date.nunique()),
        "years": sorted(int(y) for y in crosscheck.year.unique()),
        "comparisons": crosscheck.groupby("secondary").agg(
            available=("secondary_available", "sum"),
            all_ohlc_pass=("all_fields_pass", "sum"),
        ).to_dict("index"),
        "output": str(args.output),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

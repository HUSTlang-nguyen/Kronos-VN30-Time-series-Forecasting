"""Strict Phase 1 validation and temporal split primitives; no gate overrides."""
from __future__ import annotations

import numpy as np
import pandas as pd

OHLC = ["open", "high", "low", "close"]


def session_dates(values) -> pd.DatetimeIndex:
    dates = pd.DatetimeIndex(pd.to_datetime(values, errors="raise"))
    if dates.hasnans or dates.tz is not None or not dates.equals(dates.normalize()):
        raise ValueError("Session dates must be non-null, timezone-free local dates")
    if dates.has_duplicates or not dates.is_monotonic_increasing:
        raise ValueError("Session dates must be unique and sorted")
    return dates


def quality_report(frame: pd.DataFrame, sessions) -> dict:
    if not {"date", *OHLC}.issubset(frame.columns):
        raise ValueError("Missing required date/OHLC columns")
    dates = session_dates(frame.date)
    calendar = session_dates(sessions)
    if dates.empty or calendar.empty:
        raise ValueError("Dataset and calendar must be nonempty")
    values = frame[OHLC].apply(pd.to_numeric, errors="raise")
    invalid_numeric = ~np.isfinite(values.to_numpy()).all(axis=1) | (values <= 0).any(axis=1)
    invalid_ohlc = (values.high < values[["open", "close", "low"]].max(axis=1)) | (values.low > values[["open", "close", "high"]].min(axis=1))
    expected = calendar[(calendar >= dates.min()) & (calendar <= dates.max())]
    encode = lambda seq: [str(d.date()) for d in seq]
    return {
        "row_count": len(frame), "start": str(dates.min().date()), "end": str(dates.max().date()),
        "invalid_numeric_dates": encode(dates[np.asarray(invalid_numeric)]),
        "invalid_ohlc_dates": encode(dates[np.asarray(invalid_ohlc)]),
        "missing_sessions": encode(expected.difference(dates)),
        "non_session_dates": encode(dates.difference(calendar)),
    }


def process(frame: pd.DataFrame, sessions, *, source: str, g1_accepted: bool,
            calendar_accepted: bool, session_annotations: pd.DataFrame | None = None) -> pd.DataFrame:
    if not g1_accepted or not calendar_accepted:
        raise ValueError("G1 and accepted exchange calendar are required")
    report = quality_report(frame, sessions)
    if any(report[key] for key in ("invalid_numeric_dates", "invalid_ohlc_dates", "missing_sessions", "non_session_dates")):
        raise ValueError(f"Unresolved data quality failures: {report}")
    if not source.strip():
        raise ValueError("Source identifier is required")
    if "source" in frame and not frame.source.eq(source).all():
        raise ValueError("Mixed or mismatched source identifiers")
    result = frame[["date", *OHLC] + (["trade_value"] if "trade_value" in frame else [])].copy()
    result["date"] = pd.to_datetime(result.date, errors="raise")
    for field in OHLC:
        result[field] = pd.to_numeric(result[field], errors="raise")
    result["log_close"] = np.log(result.close)
    result["return_1d"] = result.close.pct_change(fill_method=None)
    result["log_return_1d"] = result.log_close.diff()
    result["range_abs"] = result.high - result.low
    result["range_pct"] = result.range_abs / result.close
    result["body_abs"] = (result.close - result.open).abs()
    result["body_pct"] = result.body_abs / result.open
    result["source"] = source
    result["quality_flags"] = ""
    result.loc[result.index[0], "quality_flags"] = "first_return_undefined"
    # Suspicious returns remain observations. This threshold is a review flag,
    # never a correction or a data-selection rule.
    result.loc[result.return_1d.abs() > 0.10, "quality_flags"] = "abs_return_gt_10pct"
    if session_annotations is not None:
        if not {"date", "session_quality_flag"}.issubset(session_annotations.columns):
            raise ValueError("Session annotations require date and quality flag")
        annotated_dates = session_dates(session_annotations.date)
        if not annotated_dates.isin(session_dates(sessions)).all():
            raise ValueError("Session annotations refer to non-session dates")
        flags = session_annotations.session_quality_flag
        if flags.isna().any() or not flags.isin(["shortened_session"]).all():
            raise ValueError("Unsupported session quality flag")
        mapping = dict(zip(annotated_dates, flags))
        for index, day in result.date.items():
            if day in mapping:
                existing = result.at[index, "quality_flags"]
                result.at[index, "quality_flags"] = (
                    existing + ";" if existing else ""
                ) + mapping[day]
    return result


def temporal_split(observed_sessions, calendar_sessions, boundary: str, freeze: str,
                   *, context: int = 128, path: int = 20, validation: int = 63,
                   minimum_test_origins: int = 126) -> tuple[pd.DataFrame, dict]:
    if min(context, path, validation, minimum_test_origins) < 1:
        raise ValueError("Split sizes must be positive")
    observed = session_dates(observed_sessions)
    calendar = session_dates(calendar_sessions)
    if observed.empty or calendar.empty:
        raise ValueError("Observed and calendar sessions must be nonempty")
    freeze_date = pd.Timestamp(freeze)
    if freeze_date.tz is not None or freeze_date != freeze_date.normalize():
        raise ValueError("Freeze must be a local session date")
    boundary_stamp = pd.Timestamp(boundary)
    if boundary_stamp.tz is None:
        raise ValueError("Provenance boundary must include timezone")
    boundary_date = boundary_stamp.tz_convert("Asia/Ho_Chi_Minh").tz_localize(None).normalize()
    observed = observed[observed <= freeze_date]
    if observed.empty or freeze_date > calendar.max():
        raise ValueError("Freeze lacks observed history or calendar coverage")
    expected = calendar[(calendar >= observed.min()) & (calendar <= freeze_date)]
    if not expected.equals(observed):
        raise ValueError("Observed history does not match the exchange calendar through freeze")
    eligible = observed[observed > boundary_date]
    targets = {"validation": eligible[:validation], "test": eligible[validation:]}
    rows = []
    for partition, interval in targets.items():
        allowed = set(interval)
        for start in range(len(interval) - path + 1):
            target = interval[start:start + path]
            origin_position = observed.get_loc(target[0]) - 1
            if origin_position < context - 1:
                continue
            origin = observed[origin_position]
            if not all(d in allowed and d > origin for d in target):
                raise AssertionError("Target path crossed a temporal boundary")
            rows.append({"partition": partition, "origin_date": origin,
                         "context_start": observed[origin_position - context + 1],
                         "context_end": origin, "target_start": target[0], "target_end": target[-1],
                         "target_dates": [str(d.date()) for d in target]})
    origins = pd.DataFrame(rows, columns=["partition", "origin_date", "context_start", "context_end", "target_start", "target_end", "target_dates"])
    test = origins[origins.partition.eq("test")]
    future_eligible = calendar[calendar > boundary_date]
    # 63 validation targets + 126 full-path origins + 19 tail targets.
    pre_boundary_context = len(calendar[(calendar >= observed[0]) & (calendar <= boundary_date)])
    first_valid_test_target = max(validation, context - pre_boundary_context)
    required_targets = first_valid_test_target + minimum_test_origins + path - 1
    projected = future_eligible[required_targets - 1] if len(future_eligible) >= required_targets else None
    describe = lambda dates: {"start": str(dates[0].date()) if len(dates) else None,
                              "end": str(dates[-1].date()) if len(dates) else None, "sessions": len(dates)}
    feasibility = {
        "provenance_boundary_utc": str(boundary_stamp.tz_convert("UTC")),
        "boundary_local_date_excluded": str(boundary_date.date()), "freeze": str(freeze_date.date()),
        "eligible_sessions": len(eligible), "validation_targets": describe(targets["validation"]),
        "test_targets": describe(targets["test"]), "validation_origins": int(origins.partition.eq("validation").sum()),
        "test_origins": len(test), "required_test_origins": minimum_test_origins,
        "first_test_origin": str(test.origin_date.iloc[0].date()) if len(test) else None,
        "last_test_origin": str(test.origin_date.iloc[-1].date()) if len(test) else None,
        "earliest_projected_freeze": str(projected.date()) if projected is not None else None,
        "projection_status": "scheduled_calendar_only" if projected is not None else "insufficient_future_calendar_coverage",
        "size_gate": "pass" if len(test) >= minimum_test_origins else "pilot",
    }
    return origins, feasibility

"""Audit the ORIGINAL snapshot; never repair prices or accept it from hashes alone."""

from __future__ import annotations
import argparse
from contextlib import closing
import json
import sqlite3
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_protocol import atomic_json, file_hash


def audit(database, receipt, output, independent=(), calendar=None):
    import numpy as np
    import pandas as pd
    from share_vndirect_sqlite import verify_sqlite
    from validate_vn30_sources import parse

    record = json.loads(Path(receipt).read_text(encoding="utf-8"))
    verified = verify_sqlite(Path(database), record["database_sha256"])
    if verified["snapshot"] != record["snapshot"]:
        raise ValueError("Snapshot differs from pinned receipt")
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    with closing(
        sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True)
    ) as con:
        df = pd.read_sql_query("SELECT * FROM candles ORDER BY row_id", con)
        embedded = {
            name: bytes(raw)
            for name, raw in con.execute("SELECT name,content FROM source_files")
        }
    snapshot = record["snapshot"]
    cfg = __import__("yaml").safe_load(embedded["audit_config.yaml"])
    replay = parse(embedded["original_response.json"], cfg)
    fields = ["open", "high", "low", "close"]
    if len(replay) != len(df) or not np.array_equal(
        replay[fields].to_numpy(), df[fields].to_numpy()
    ):
        raise ValueError("Raw OHLC replay differs from SQLite")
    if list(replay.date.dt.strftime("%Y-%m-%d")) != list(df.date):
        raise ValueError("Raw timestamps do not replay to persisted local dates")
    for flag in (
        "duplicate_date",
        "invalid_numeric",
        "invalid_ohlc",
        "outside_request",
    ):
        if not np.array_equal(replay[flag].astype(int).to_numpy(), df[flag].to_numpy()):
            raise ValueError("Raw quality flag replay differs: " + flag)
    df = df.sort_values(["date", "row_id"]).reset_index(drop=True)
    equal = np.isclose(df.open, df.close.shift(), rtol=0, atol=1e-9)
    returns = np.log(df.close / df.close.shift())
    selected = set(df.loc[equal | df.outside_request.astype(bool), "date"])
    selected.update(df.loc[returns.abs().nlargest(20).index, "date"])
    rng = np.random.default_rng(20261030)
    for _, part in df.groupby(df.date.str[:4]):
        selected.update(
            rng.choice(part.date, min(5, len(part)), replace=False).tolist()
        )
    runs = []
    start = None
    for i, flag in enumerate([*equal, False]):
        if flag and start is None:
            start = i
        if not flag and start is not None:
            runs.append(
                {
                    "first_date": df.date.iloc[start],
                    "last_date": df.date.iloc[i - 1],
                    "sessions": i - start,
                }
            )
            start = None
    anomaly = df.loc[
        equal
        | df.outside_request.astype(bool)
        | df.invalid_ohlc.astype(bool)
        | df.invalid_numeric.astype(bool)
    ].copy()
    anomaly["open_equals_previous_close"] = equal[anomaly.index]
    anomaly.to_csv(output / "anomalies.csv", index=False)
    pd.DataFrame({"date": sorted(selected)}).to_csv(
        output / "required_crosscheck_dates.csv", index=False
    )
    comparisons = []
    source_records = []
    independently_verified_dates = set()
    for source in independent:
        source = Path(source)
        metadata_path = source.with_suffix(".json")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if (
            metadata.get("provider") in (None, "vndirect")
            or metadata.get("symbol") != "VN30"
        ):
            raise ValueError(
                "Independent evidence must identify a different VN30 provider"
            )
        if metadata.get("csv_sha256") != file_hash(source) or not metadata.get("url"):
            raise ValueError(
                "Independent evidence needs source URL and matching CSV checksum"
            )
        other = pd.read_csv(source, dtype={"date": str})
        if other.date.duplicated().any():
            raise ValueError("Ambiguous independent duplicate dates")
        merged = df[["date", *fields]].merge(
            other[["date", *fields]], on="date", suffixes=("_original", "_reference")
        )
        independently_verified_dates.update(merged.date)
        for row in merged.itertuples(index=False):
            for field in fields:
                original = getattr(row, field + "_original")
                reference = getattr(row, field + "_reference")
                delta = abs(original - reference)
                comparisons.append(
                    {
                        "date": row.date,
                        "provider": metadata["provider"],
                        "field": field,
                        "original": original,
                        "reference": reference,
                        "difference": delta,
                        "required_sample": row.date in selected,
                        "status": "pass"
                        if np.isfinite(delta) and delta <= 0.02 + 1e-9
                        else "unresolved",
                    }
                )
        source_records.append(
            {
                **metadata,
                "path": source.as_posix(),
                "overlap": len(merged),
                "metadata_sha256": file_hash(metadata_path),
            }
        )
    comparison = pd.DataFrame(
        comparisons,
        columns=[
            "date",
            "provider",
            "field",
            "original",
            "reference",
            "difference",
            "required_sample",
            "status",
        ],
    )
    comparison.to_csv(output / "crosscheck.csv", index=False)
    failed = comparison.loc[comparison.status == "unresolved"]
    breakdown = (
        failed.groupby(["provider", "field"])
        .agg(
            comparisons=("date", "size"),
            max_difference=("difference", "max"),
            first_date=("date", "min"),
            last_date=("date", "max"),
        )
        .reset_index()
    )
    breakdown.to_csv(output / "discrepancy_summary.csv", index=False)
    failed.sort_values("difference",ascending=False).head(20).to_csv(
        output / "largest_discrepancies.csv", index=False
    )
    actual_dates = set(df.date)
    weekday_candidates = (
        set(pd.bdate_range(df.date.min(), df.date.max()).strftime("%Y-%m-%d"))
        - actual_dates
    )
    calendar_result = {
        "status": "unverified",
        "missing_weekdays_are_not_assumed_errors": True,
    }
    if calendar:
        calendar = Path(calendar)
        meta_path = calendar.with_suffix(".json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not meta.get("url") or meta.get("csv_sha256") != file_hash(calendar):
            raise ValueError("Calendar must have a source URL and matching checksum")
        dates = set(pd.read_csv(calendar, dtype=str).date)
        dates = {d for d in dates if df.date.min() <= d <= df.date.max()}
        calendar_result = {
            "status": "pass" if dates == actual_dates else "unresolved",
            "missing_sessions": sorted(dates - actual_dates),
            "unexpected_sessions": sorted(actual_dates - dates),
            "source": meta,
        }
    pd.DataFrame({"date": sorted(weekday_candidates)}).to_csv(
        output / "weekday_gaps_to_reconcile.csv", index=False
    )
    bad_prices = int(
        df[["invalid_numeric", "invalid_ohlc", "duplicate_date"]].sum().sum()
    )
    unresolved = int((comparison.status == "unresolved").sum())
    required_missing = sorted(selected - independently_verified_dates)
    status = (
        "accepted_provider_scope"
        if source_records
        and not bad_prices
        and not unresolved
        and not required_missing
        and calendar_result["status"] == "pass"
        else "unverified"
    )
    query = parse_qs(urlparse(snapshot["request_url"]).query)
    result = {
        "schema_version": 1,
        "status": status,
        "dataset_sha256": record["database_sha256"],
        "rows": len(df),
        "first_date": df.date.min(),
        "last_date": df.date.max(),
        "raw_replay": "pass",
        "timestamp_timezone_replay": "pass",
        "quality_flag_replay": "pass",
        "provider": snapshot["provider"],
        "symbol": snapshot["symbol"],
        "units": snapshot["units"],
        "request": query,
        "observed_history_starts_later_than_requested": bool(
            query.get("from")
            and pd.Timestamp(df.date.min())
            > pd.Timestamp(int(query["from"][0]), unit="s", tz="UTC")
            .tz_convert(snapshot["timezone"])
            .tz_localize(None)
            .normalize()
        ),
        "outside_request_rows": int(df.outside_request.sum()),
        "invalid_or_duplicate_flags": bad_prices,
        "open_equals_previous_close_sessions": int(equal.sum()),
        "open_equal_runs": runs,
        "calendar": calendar_result,
        "independent_sources": source_records,
        "unresolved_field_comparisons": unresolved,
        "discrepancy_summary": json.loads(breakdown.to_json(orient="records")),
        "unique_dates_with_close_discrepancies": int(
            failed.loc[failed.field == "close", "date"].nunique()
        ),
        "required_dates_without_reference": required_missing,
        "price_edits": [],
        "limitations": [
            "Provider Open is not automatically official exchange Open.",
            "Byte integrity is not market-data correctness.",
            "No missing session is imputed.",
        ],
    }
    atomic_json(output / "audit.json", result)
    summary = (
        "# Kiểm toán dữ liệu VN30\n\n"
        + f"Trạng thái: **{status}**. {len(df)} phiên; SHA256 `{record['database_sha256']}`.\n\n"
        + f"Raw/timestamp/flags replay: pass. Open bằng Close trước: {int(equal.sum())} phiên. "
        f"Ngoài request: {int(df.outside_request.sum())}. Sai khác OHLC chưa giải quyết: {unresolved}.\n\n"
        + f"Đối chiếu lịch: {calendar_result['status']}. Ngày kiểm tra bắt buộc chưa có nguồn độc lập: {len(required_missing)}.\n\n"
        + "Không sửa giá. Không xác nhận chất lượng thị trường chỉ từ checksum.\n"
    )
    summary += "\n| Nguồn đối chiếu | Trường | Số chênh lệch | Lớn nhất (điểm) |\n|---|---|---:|---:|\n"
    for row in breakdown.itertuples(index=False):
        summary += f"| {row.provider} | {row.field} | {row.comparisons} | {row.max_difference:.2f} |\n"
    summary += "\nChênh lệch giữa nhà cung cấp chưa xác định được bên nào sai. Không được xem số đếm này là số lỗi đã chứng minh của VNDIRECT.\n"
    summary += "\nBước giải quyết: đối chiếu giá công bố có nguồn cho các ngày cụ thể, xác minh cách dựng O/H/L và hoàn tất lịch phiên. Nếu chưa có bằng chứng, giữ trạng thái chưa kiểm chứng và chặn huấn luyện chính.\n"
    (output / "summary.md").write_text(summary, encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--database",
        type=Path,
        default=ROOT
        / "data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite",
    )
    p.add_argument(
        "--receipt",
        type=Path,
        default=ROOT / "data/manifests/vndirect_sqlite_snapshot.json",
    )
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--independent", type=Path, nargs="*", default=[])
    p.add_argument("--calendar", type=Path)
    args = p.parse_args()
    print(
        json.dumps(
            audit(
                args.database,
                args.receipt,
                args.output,
                args.independent,
                args.calendar,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

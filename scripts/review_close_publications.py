"""Corroborate disputed Close values against dated publisher reports, not votes."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from research_protocol import atomic_json, file_hash


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def extract_close(html, market_date):
    parser = VisibleText()
    parser.feed(html)
    text = re.sub(r"\s+", " ", " ".join(parser.parts))
    date = datetime.strptime(market_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    if not re.search(r"Bản tin thị trường ngày\s+" + re.escape(date), text, re.I):
        return {"status": "unverified_publication_date"}
    section = re.search(r"TTCK VIỆT NAM\s+(.*?)\s+ETF\s*&\s*PHÁI SINH", text, re.I)
    if not section:
        return {"status": "unverified_report_section"}
    match = re.search(r"\bVN30\b\s+([\d,.]+)", section.group(1))
    if not match:
        return {"status": "unverified_index_value"}
    number = match.group(1)
    if "," in number and "." in number and number.rfind(",") > number.rfind("."):
        number = number.replace(".", "").replace(",", ".")
    else:
        number = number.replace(",", "")
    value = float(number)
    if not 0 < value < 100000:
        raise ValueError("Invalid publisher index value")
    if not re.search(
        r"kết\s+(?:thúc\s+)?phiên|đóng\s+cửa|chốt\s+phiên|khép\s+phiên",
        section.group(1),
        re.I,
    ):
        # Keep a candidate for manual review; never silently treat an index table
        # without closing semantics as independently verified Close.
        return {"status": "unverified_close_semantics", "candidate_value": value}
    return {
        "status": "extracted_dated_close",
        "value": value,
        "publisher": "Pinetree",
        "market_date": market_date,
        "evidence_locator": "TTCK VIỆT NAM / VN30 and session-close commentary",
    }


def main():
    import pandas as pd

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--crosscheck", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument(
        "--raw",
        type=Path,
        default=ROOT / "data/raw/source_evidence/pinetree-close-review",
    )
    p.add_argument(
        "--budget-state",
        type=Path,
        default=ROOT / "artifacts/local/pc-rerun-20261030/state.json",
    )
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    args.raw.mkdir(parents=True, exist_ok=True)
    end = json.loads(args.budget_state.read_text())["deadline_unix"]
    crosscheck = pd.read_csv(args.crosscheck)
    disputed = crosscheck.loc[
        (crosscheck.field == "close") & (crosscheck.status == "unresolved")
    ]
    rows = []
    for date, part in disputed.groupby("date", sort=True):
        if time.time() >= end:
            break
        if part.original.nunique() != 1:
            raise ValueError("Original price differs within one date")
        day = datetime.strptime(date, "%Y-%m-%d")
        url = f"https://pinetree.vn/post/{day:%Y%m%d}/ban-tin-thi-truong-ngay-{day:%d-%m-%Y}/"
        raw = args.raw / (day.strftime("%Y%m%d") + ".html")
        record = {
            "date": date,
            "original_close": float(part.original.iloc[0]),
            "reference_values": part[["provider", "reference"]].to_dict("records"),
            "url": url,
        }
        try:
            if not raw.exists():
                with urlopen(
                    Request(url, headers={"User-Agent": "VN30-research-audit/1.0"}),
                    timeout=20,
                ) as response:
                    payload = response.read()
                raw.write_bytes(payload)
                atomic_json(
                    raw.with_suffix(".json"),
                    {
                        "url": url,
                        "sha256": file_hash(raw),
                        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                    },
                )
            metadata = json.loads(raw.with_suffix(".json").read_text())
            if metadata["url"] != url or metadata["sha256"] != file_hash(raw):
                raise ValueError("Publisher cache identity differs")
            result = extract_close(
                raw.read_text(encoding="utf-8", errors="replace"), date
            )
            record.update(
                result,
                evidence_path=raw.relative_to(ROOT).as_posix(),
                evidence_sha256=file_hash(raw),
            )
            if result["status"] == "extracted_dated_close":
                record["difference_vs_original"] = abs(
                    result["value"] - record["original_close"]
                )
                record["status"] = (
                    "corroborates_original"
                    if record["difference_vs_original"] <= 0.02 + 1e-9
                    else "conflicts_original"
                )
        except Exception as exc:
            record.update(
                status="unavailable", error=type(exc).__name__ + ": " + str(exc)
            )
        rows.append(record)
        atomic_json(
            args.output / "review.json",
            {
                "classification": "partial_publisher_evidence_not_dataset_acceptance",
                "source_crosscheck_sha256": file_hash(args.crosscheck),
                "expected_disputed_dates": disputed.date.nunique(),
                "cases": rows,
            },
        )
        print(date, record["status"], record.get("value"), flush=True)
        time.sleep(0.5)
    counts = pd.Series([r["status"] for r in rows]).value_counts().to_dict()
    atomic_json(
        args.output / "summary.json",
        {
            "expected_dates": int(disputed.date.nunique()),
            "reviewed_dates": len(rows),
            "counts": counts,
            "dataset_accepted": False,
            "ohlc_and_calendar_still_require_separate_evidence": True,
        },
    )
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()

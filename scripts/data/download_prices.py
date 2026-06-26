#!/usr/bin/env python3
"""Create repo-only public-price input files from the ETF universe."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from load_universe import UNIVERSE_PATH, allowed_entries, validate_requested_symbols


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PRICE_CSV = RAW_DIR / "prices_sample.csv"
METADATA_JSON = RAW_DIR / "prices_sample_metadata.json"


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def business_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    cursor = start
    while cursor <= end:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def selected_entries(symbols: str | None) -> list[dict[str, object]]:
    entries = allowed_entries(UNIVERSE_PATH)
    if not symbols:
        return entries
    requested = validate_requested_symbols(symbols.split(","), UNIVERSE_PATH)
    requested_set = set(requested)
    return [entry for entry in entries if str(entry["symbol"]).upper() in requested_set]


def sample_rows(entries: list[dict[str, object]], start: date, end: date) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    dates = business_days(start, end)
    for symbol_index, entry in enumerate(entries):
        symbol = str(entry["symbol"]).upper()
        first_offset = symbol_index % 3
        first_date = dates[min(first_offset, len(dates) - 1)] if dates else start
        base = 75.0 + symbol_index * 11.0
        for day_index, current_day in enumerate(dates):
            if current_day < first_date:
                continue
            adjusted_close = base * (1.0 + 0.0025 * day_index + 0.0003 * symbol_index)
            total_return_index = 100.0 * (adjusted_close / base)
            rows.append(
                {
                    "source": "sample",
                    "symbol": symbol,
                    "date": current_day.isoformat(),
                    "adjusted_close": f"{adjusted_close:.4f}",
                    "total_return_index": f"{total_return_index:.4f}",
                }
            )
    return rows


def write_outputs(source: str, symbols: str | None, start: date, end: date) -> dict[str, object]:
    if source != "sample":
        raise ValueError(
            "Only the repo-only sample source is available without approved dependencies"
        )

    entries = selected_entries(symbols)
    rows = sample_rows(entries, start, end)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with PRICE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source",
                "symbol",
                "date",
                "adjusted_close",
                "total_return_index",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    first_available: dict[str, str] = {}
    for row in rows:
        first_available.setdefault(row["symbol"], row["date"])

    downloaded_at = datetime.now(timezone.utc).isoformat()
    if METADATA_JSON.exists():
        previous = json.loads(METADATA_JSON.read_text(encoding="utf-8"))
        same_request = (
            previous.get("source") == source
            and previous.get("symbols") == [str(entry["symbol"]).upper() for entry in entries]
            and previous.get("start_date") == start.isoformat()
            and previous.get("end_date") == end.isoformat()
        )
        if same_request and previous.get("downloaded_at"):
            downloaded_at = str(previous["downloaded_at"])

    metadata = {
        "source": source,
        "downloaded_at": downloaded_at,
        "universe_file": "configs/universe/etf_universe.yaml",
        "symbols": [str(entry["symbol"]).upper() for entry in entries],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "first_available_dates": first_available,
        "price_field": "adjusted_close",
        "total_return_field": "total_return_index",
        "raw_file": "data/raw/prices_sample.csv",
    }
    METADATA_JSON.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Download or generate ETF price inputs")
    parser.add_argument("--source", default="sample")
    parser.add_argument("--start", default="2024-01-02")
    parser.add_argument("--end", default="2024-01-31")
    parser.add_argument("--symbols", default=None)
    args = parser.parse_args()

    metadata = write_outputs(
        source=args.source,
        symbols=args.symbols,
        start=parse_date(args.start),
        end=parse_date(args.end),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

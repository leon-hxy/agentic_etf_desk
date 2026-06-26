#!/usr/bin/env python3
"""Build a machine-readable ETF adjusted-close price panel."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from load_universe import UNIVERSE_PATH, allowed_symbols


ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / "data" / "raw" / "prices_sample.csv"
RAW_METADATA = ROOT / "data" / "raw" / "prices_sample_metadata.json"
PROCESSED_DIR = ROOT / "data" / "processed"
PANEL_CSV = PROCESSED_DIR / "price_panel.csv"
PANEL_METADATA = PROCESSED_DIR / "price_panel_metadata.json"


def read_prices(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_panel(raw_csv: Path = RAW_CSV) -> dict[str, object]:
    if not raw_csv.exists():
        raise FileNotFoundError(f"Missing raw price file: {raw_csv}")

    allowed = set(allowed_symbols(UNIVERSE_PATH))
    rows = read_prices(raw_csv)
    unknown = sorted({row["symbol"] for row in rows if row["symbol"] not in allowed})
    if unknown:
        raise ValueError(f"Raw price file contains symbols outside universe: {', '.join(unknown)}")

    by_date: dict[str, dict[str, str]] = defaultdict(dict)
    by_symbol: dict[str, list[tuple[str, float]]] = defaultdict(list)
    abnormal: list[dict[str, object]] = []

    for row in rows:
        symbol = row["symbol"]
        value = float(row["adjusted_close"])
        if value <= 0:
            abnormal.append({"symbol": symbol, "date": row["date"], "reason": "non_positive"})
            continue
        by_date[row["date"]][symbol] = f"{value:.4f}"
        by_symbol[symbol].append((row["date"], value))

    for symbol, series in by_symbol.items():
        series.sort()
        previous: float | None = None
        for current_date, value in series:
            if previous is not None and abs(value / previous - 1.0) > 0.80:
                abnormal.append({"symbol": symbol, "date": current_date, "reason": "large_move"})
            previous = value

    symbols = sorted(by_symbol)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with PANEL_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", *symbols], lineterminator="\n")
        writer.writeheader()
        for current_date in sorted(by_date):
            output_row = {"date": current_date}
            for symbol in symbols:
                output_row[symbol] = by_date[current_date].get(symbol, "")
            writer.writerow(output_row)

    all_dates = sorted(by_date)
    missing_values = {
        symbol: sum(1 for current_date in all_dates if symbol not in by_date[current_date])
        for symbol in symbols
    }
    first_available = {
        symbol: min(date_value for date_value, _ in values)
        for symbol, values in by_symbol.items()
        if values
    }

    source = "sample"
    if RAW_METADATA.exists():
        source = json.loads(RAW_METADATA.read_text(encoding="utf-8")).get("source", source)

    generated_at = datetime.now(timezone.utc).isoformat()
    if PANEL_METADATA.exists():
        previous = json.loads(PANEL_METADATA.read_text(encoding="utf-8"))
        same_panel = (
            previous.get("raw_file") == "data/raw/prices_sample.csv"
            and previous.get("symbols") == symbols
            and previous.get("panel_start_date") == (all_dates[0] if all_dates else None)
            and previous.get("panel_end_date") == (all_dates[-1] if all_dates else None)
        )
        if same_panel and previous.get("generated_at"):
            generated_at = str(previous["generated_at"])

    metadata = {
        "source": source,
        "generated_at": generated_at,
        "universe_file": "configs/universe/etf_universe.yaml",
        "raw_file": "data/raw/prices_sample.csv",
        "price_panel_file": "data/processed/price_panel.csv",
        "symbols": symbols,
        "unknown_symbols": unknown,
        "panel_start_date": all_dates[0] if all_dates else None,
        "panel_end_date": all_dates[-1] if all_dates else None,
        "first_available_dates": first_available,
        "missing_values_by_symbol": missing_values,
        "abnormal_price_points": abnormal,
        "price_field": "adjusted_close",
        "total_return_supported": True,
    }
    PANEL_METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Build ETF price panel")
    parser.add_argument("--raw-csv", default=str(RAW_CSV))
    args = parser.parse_args()
    metadata = build_panel(Path(args.raw_csv))
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

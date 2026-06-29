#!/usr/bin/env python3
"""Create repo-only public-price input files from the ETF universe."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen

from load_universe import UNIVERSE_PATH, allowed_entries, validate_requested_symbols


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PRICE_CSV = RAW_DIR / "prices_sample.csv"
METADATA_JSON = RAW_DIR / "prices_sample_metadata.json"
STOOQ_PRICE_CSV = RAW_DIR / "prices_stooq_daily.csv"
STOOQ_METADATA_JSON = RAW_DIR / "prices_stooq_daily_metadata.json"
STOOQ_CACHE_DIR = ROOT / "data" / "cache" / "stooq_daily_csv"
STOOQ_CACHE_MANIFEST = STOOQ_CACHE_DIR / "cache_manifest.json"
STOOQ_URL_TEMPLATE = "https://stooq.com/q/d/l/?s={symbol}.us&i=d"
YAHOO_PRICE_CSV = RAW_DIR / "prices_yahoo_chart.csv"
YAHOO_METADATA_JSON = RAW_DIR / "prices_yahoo_chart_metadata.json"
YAHOO_CACHE_DIR = ROOT / "data" / "cache" / "yahoo_chart_public"
YAHOO_CACHE_MANIFEST = YAHOO_CACHE_DIR / "cache_manifest.json"
YAHOO_URL_TEMPLATE = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    "?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"
)
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."

Fetcher = Callable[[str, str], str]


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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


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


def stooq_url(symbol: str) -> str:
    return STOOQ_URL_TEMPLATE.format(symbol=symbol.lower())


def yahoo_url(symbol: str, start: date, end: date) -> str:
    period1 = int(datetime.combine(start, time.min, tzinfo=timezone.utc).timestamp())
    period2 = int(
        datetime.combine(end + timedelta(days=1), time.min, tzinfo=timezone.utc).timestamp()
    )
    return YAHOO_URL_TEMPLATE.format(symbol=symbol.upper(), period1=period1, period2=period2)


def default_stooq_fetcher(_symbol: str, url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "agentic-etf-desk/1.0 "
                "(read-only ETF historical research cache; contact: local user)"
            )
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8-sig")


def default_public_json_fetcher(_symbol: str, url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "agentic-etf-desk/1.0 "
                "(read-only ETF historical research cache; contact: local user)"
            )
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def stooq_cache_file(cache_dir: Path, symbol: str, start: date, end: date, as_of_date: date) -> Path:
    return cache_dir / f"{symbol.lower()}_us_{start.isoformat()}_{end.isoformat()}_{as_of_date.isoformat()}.csv"


def yahoo_cache_file(cache_dir: Path, symbol: str, start: date, end: date, as_of_date: date) -> Path:
    return cache_dir / f"{symbol.upper()}_{start.isoformat()}_{end.isoformat()}_{as_of_date.isoformat()}.json"


def ensure_stooq_csv(raw_text: str, symbol: str) -> None:
    first_line = raw_text.splitlines()[0] if raw_text.splitlines() else ""
    if "Date" not in first_line or "Close" not in first_line:
        raise ValueError(
            f"Stooq did not return CSV for {symbol}; response was not cached"
        )


def ensure_json(raw_text: str, symbol: str, source: str) -> None:
    try:
        json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{source} did not return JSON for {symbol}; response was not cached") from exc


def read_or_fetch_stooq(
    symbol: str,
    start: date,
    end: date,
    cache_dir: Path,
    as_of_date: date,
    fetcher: Fetcher,
) -> tuple[str, dict[str, object]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    url = stooq_url(symbol)
    cache_file = stooq_cache_file(cache_dir, symbol, start, end, as_of_date)
    cache_status = "hit"
    if cache_file.exists():
        raw_text = cache_file.read_text(encoding="utf-8")
        ensure_stooq_csv(raw_text, symbol)
    else:
        cache_status = "miss"
        raw_text = fetcher(symbol, url)
        ensure_stooq_csv(raw_text, symbol)
        cache_file.write_text(raw_text, encoding="utf-8")

    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    return raw_text, {
        "symbol": symbol,
        "stooq_symbol": f"{symbol.lower()}.us",
        "source_url": url,
        "cache_file": rel(cache_file),
        "cache_sha256": digest,
        "cache_status": cache_status,
        "as_of_date": as_of_date.isoformat(),
    }


def read_or_fetch_yahoo(
    symbol: str,
    start: date,
    end: date,
    cache_dir: Path,
    as_of_date: date,
    fetcher: Fetcher,
) -> tuple[str, dict[str, object]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    url = yahoo_url(symbol, start, end)
    cache_file = yahoo_cache_file(cache_dir, symbol, start, end, as_of_date)
    cache_status = "hit"
    if cache_file.exists():
        raw_text = cache_file.read_text(encoding="utf-8")
        ensure_json(raw_text, symbol, "Yahoo Chart")
    else:
        cache_status = "miss"
        raw_text = fetcher(symbol, url)
        ensure_json(raw_text, symbol, "Yahoo Chart")
        cache_file.write_text(raw_text, encoding="utf-8")

    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    return raw_text, {
        "symbol": symbol,
        "source_url": url,
        "cache_file": rel(cache_file),
        "cache_sha256": digest,
        "cache_status": cache_status,
        "as_of_date": as_of_date.isoformat(),
    }


def stooq_rows(raw_text: str, symbol: str, start: date, end: date) -> list[dict[str, str]]:
    reader = csv.DictReader(raw_text.splitlines())
    rows: list[dict[str, str]] = []
    first_price: float | None = None
    for raw_row in reader:
        raw_date = raw_row.get("Date") or raw_row.get("date")
        raw_close = raw_row.get("Close") or raw_row.get("close")
        if not raw_date or not raw_close:
            continue
        current_date = date.fromisoformat(raw_date)
        if current_date < start or current_date > end:
            continue
        adjusted_close = float(raw_close)
        if adjusted_close <= 0:
            continue
        if first_price is None:
            first_price = adjusted_close
        total_return_index = 100.0 * adjusted_close / first_price
        rows.append(
            {
                "source": "stooq_daily_csv",
                "symbol": symbol,
                "date": current_date.isoformat(),
                "adjusted_close": f"{adjusted_close:.4f}",
                "total_return_index": f"{total_return_index:.4f}",
            }
        )
    if not rows:
        raise ValueError(f"Stooq returned no usable rows for {symbol} between {start} and {end}")
    return rows


def yahoo_rows(raw_text: str, symbol: str, start: date, end: date) -> list[dict[str, str]]:
    payload = json.loads(raw_text)
    chart = payload.get("chart", {})
    if chart.get("error"):
        raise ValueError(f"Yahoo Chart returned an error for {symbol}: {chart['error']}")
    results = chart.get("result") or []
    if not results:
        raise ValueError(f"Yahoo Chart returned no result for {symbol}")

    result = results[0]
    meta = result.get("meta", {})
    instrument_type = str(meta.get("instrumentType", "")).upper()
    if instrument_type and instrument_type != "ETF":
        raise ValueError(f"Yahoo Chart instrumentType for {symbol} is not ETF: {instrument_type}")

    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    adjclose_series = (indicators.get("adjclose") or [{}])[0].get("adjclose") or []
    quote_close_series = (indicators.get("quote") or [{}])[0].get("close") or []
    rows: list[dict[str, str]] = []
    first_price: float | None = None

    for index, timestamp in enumerate(timestamps):
        current_date = datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date()
        if current_date < start or current_date > end:
            continue
        raw_price = None
        if index < len(adjclose_series):
            raw_price = adjclose_series[index]
        if raw_price is None and index < len(quote_close_series):
            raw_price = quote_close_series[index]
        if raw_price is None:
            continue
        adjusted_close = float(raw_price)
        if adjusted_close <= 0:
            continue
        if first_price is None:
            first_price = adjusted_close
        total_return_index = 100.0 * adjusted_close / first_price
        rows.append(
            {
                "source": "yahoo_chart_public",
                "symbol": symbol,
                "date": current_date.isoformat(),
                "adjusted_close": f"{adjusted_close:.4f}",
                "total_return_index": f"{total_return_index:.4f}",
            }
        )

    if not rows:
        raise ValueError(f"Yahoo Chart returned no usable rows for {symbol} between {start} and {end}")
    return rows


def previous_timestamp_if_same(path: Path, metadata: dict[str, object], field: str) -> str:
    current = datetime.now(timezone.utc).isoformat()
    if not path.exists():
        return current
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return current
    comparable = dict(metadata)
    comparable.pop(field, None)
    previous_comparable = dict(previous)
    previous_comparable.pop(field, None)
    if comparable == previous_comparable and previous.get(field):
        return str(previous[field])
    return current


def write_sample_outputs(
    symbols: str | None,
    start: date,
    end: date,
    raw_csv: Path,
    metadata_json: Path,
) -> dict[str, object]:
    entries = selected_entries(symbols)
    rows = sample_rows(entries, start, end)
    raw_csv.parent.mkdir(parents=True, exist_ok=True)

    with raw_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
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

    metadata = {
        "source": "sample",
        "universe_file": "configs/universe/etf_universe.yaml",
        "symbols": [str(entry["symbol"]).upper() for entry in entries],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "first_available_dates": first_available,
        "price_field": "adjusted_close",
        "total_return_field": "total_return_index",
        "raw_file": rel(raw_csv),
    }
    metadata["downloaded_at"] = previous_timestamp_if_same(
        metadata_json, metadata, "downloaded_at"
    )
    metadata_json.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return metadata


def write_stooq_outputs(
    symbols: str | None,
    start: date,
    end: date,
    raw_csv: Path,
    metadata_json: Path,
    cache_dir: Path,
    cache_manifest_json: Path,
    as_of_date: date,
    fetcher: Fetcher,
) -> dict[str, object]:
    entries = selected_entries(symbols)
    raw_rows: list[dict[str, str]] = []
    cache_entries: list[dict[str, object]] = []

    for entry in entries:
        symbol = str(entry["symbol"]).upper()
        raw_text, cache_entry = read_or_fetch_stooq(
            symbol=symbol,
            start=start,
            end=end,
            cache_dir=cache_dir,
            as_of_date=as_of_date,
            fetcher=fetcher,
        )
        rows = stooq_rows(raw_text, symbol, start, end)
        cache_entry["row_count"] = len(rows)
        cache_entry["first_date"] = rows[0]["date"]
        cache_entry["last_date"] = rows[-1]["date"]
        cache_entries.append(cache_entry)
        raw_rows.extend(rows)

    raw_rows.sort(key=lambda row: (row["symbol"], row["date"]))
    raw_csv.parent.mkdir(parents=True, exist_ok=True)
    with raw_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=[
                "source",
                "symbol",
                "date",
                "adjusted_close",
                "total_return_index",
            ],
        )
        writer.writeheader()
        writer.writerows(raw_rows)

    symbols_out = [str(entry["symbol"]).upper() for entry in entries]
    first_available = {
        str(entry["symbol"]).upper(): next(
            row["date"] for row in raw_rows if row["symbol"] == str(entry["symbol"]).upper()
        )
        for entry in entries
    }
    last_available = {
        str(entry["symbol"]).upper(): next(
            row["date"]
            for row in reversed(raw_rows)
            if row["symbol"] == str(entry["symbol"]).upper()
        )
        for entry in entries
    }

    cache_manifest = {
        "source": "stooq_daily_csv",
        "public_data_source": "Stooq daily CSV",
        "read_only_public_source": True,
        "requires_secret": False,
        "broker_surface": False,
        "universe_file": "configs/universe/etf_universe.yaml",
        "symbols": symbols_out,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "as_of_date": as_of_date.isoformat(),
        "cache_entries": cache_entries,
        "license_caveat": "Confirm permitted use before publication, redistribution, or commercial use.",
    }
    cache_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest_json.write_text(
        json.dumps(cache_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    metadata: dict[str, object] = {
        "source": "stooq_daily_csv",
        "public_data_source": "Stooq daily CSV",
        "read_only_public_source": True,
        "requires_secret": False,
        "broker_surface": False,
        "universe_file": "configs/universe/etf_universe.yaml",
        "symbols": symbols_out,
        "unknown_symbols": [],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "as_of_date": as_of_date.isoformat(),
        "first_available_dates": first_available,
        "last_available_dates": last_available,
        "price_field": "adjusted_close",
        "price_field_source": "Stooq Close column treated as the adjusted-price proxy for WP1; WP2 validates adjusted coverage.",
        "total_return_field": "total_return_index",
        "raw_file": rel(raw_csv),
        "cache_manifest_file": rel(cache_manifest_json),
        "cache_entries": cache_entries,
        "row_count": len(raw_rows),
        "final_trading_notice": FINAL_TRADING_NOTICE,
    }
    metadata["downloaded_at"] = previous_timestamp_if_same(
        metadata_json, metadata, "downloaded_at"
    )
    metadata_json.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def write_yahoo_outputs(
    symbols: str | None,
    start: date,
    end: date,
    raw_csv: Path,
    metadata_json: Path,
    cache_dir: Path,
    cache_manifest_json: Path,
    as_of_date: date,
    fetcher: Fetcher,
) -> dict[str, object]:
    entries = selected_entries(symbols)
    raw_rows: list[dict[str, str]] = []
    cache_entries: list[dict[str, object]] = []

    for entry in entries:
        symbol = str(entry["symbol"]).upper()
        raw_text, cache_entry = read_or_fetch_yahoo(
            symbol=symbol,
            start=start,
            end=end,
            cache_dir=cache_dir,
            as_of_date=as_of_date,
            fetcher=fetcher,
        )
        rows = yahoo_rows(raw_text, symbol, start, end)
        cache_entry["row_count"] = len(rows)
        cache_entry["first_date"] = rows[0]["date"]
        cache_entry["last_date"] = rows[-1]["date"]
        cache_entries.append(cache_entry)
        raw_rows.extend(rows)

    raw_rows.sort(key=lambda row: (row["symbol"], row["date"]))
    raw_csv.parent.mkdir(parents=True, exist_ok=True)
    with raw_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=[
                "source",
                "symbol",
                "date",
                "adjusted_close",
                "total_return_index",
            ],
        )
        writer.writeheader()
        writer.writerows(raw_rows)

    symbols_out = [str(entry["symbol"]).upper() for entry in entries]
    first_available = {
        str(entry["symbol"]).upper(): next(
            row["date"] for row in raw_rows if row["symbol"] == str(entry["symbol"]).upper()
        )
        for entry in entries
    }
    last_available = {
        str(entry["symbol"]).upper(): next(
            row["date"]
            for row in reversed(raw_rows)
            if row["symbol"] == str(entry["symbol"]).upper()
        )
        for entry in entries
    }

    cache_manifest = {
        "source": "yahoo_chart_public",
        "public_data_source": "Yahoo Chart public JSON",
        "read_only_public_source": True,
        "requires_secret": False,
        "broker_surface": False,
        "universe_file": "configs/universe/etf_universe.yaml",
        "symbols": symbols_out,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "as_of_date": as_of_date.isoformat(),
        "cache_entries": cache_entries,
        "license_caveat": "Confirm permitted use before publication, redistribution, or commercial use.",
    }
    cache_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    cache_manifest_json.write_text(
        json.dumps(cache_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    metadata: dict[str, object] = {
        "source": "yahoo_chart_public",
        "public_data_source": "Yahoo Chart public JSON",
        "read_only_public_source": True,
        "requires_secret": False,
        "broker_surface": False,
        "universe_file": "configs/universe/etf_universe.yaml",
        "symbols": symbols_out,
        "unknown_symbols": [],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "as_of_date": as_of_date.isoformat(),
        "first_available_dates": first_available,
        "last_available_dates": last_available,
        "price_field": "adjusted_close",
        "price_field_source": "Yahoo Chart adjclose field, falling back to close only when adjclose is unavailable.",
        "total_return_field": "total_return_index",
        "raw_file": rel(raw_csv),
        "cache_manifest_file": rel(cache_manifest_json),
        "cache_entries": cache_entries,
        "row_count": len(raw_rows),
        "final_trading_notice": FINAL_TRADING_NOTICE,
    }
    metadata["downloaded_at"] = previous_timestamp_if_same(
        metadata_json, metadata, "downloaded_at"
    )
    metadata_json.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def write_outputs(
    source: str,
    symbols: str | None,
    start: date,
    end: date,
    raw_csv: Path | None = None,
    metadata_json: Path | None = None,
    cache_dir: Path | None = None,
    cache_manifest_json: Path | None = None,
    as_of_date: date | None = None,
    fetcher: Fetcher | None = None,
) -> dict[str, object]:
    if source == "sample":
        return write_sample_outputs(
            symbols=symbols,
            start=start,
            end=end,
            raw_csv=raw_csv or PRICE_CSV,
            metadata_json=metadata_json or METADATA_JSON,
        )
    if source == "stooq_daily_csv":
        return write_stooq_outputs(
            symbols=symbols,
            start=start,
            end=end,
            raw_csv=raw_csv or STOOQ_PRICE_CSV,
            metadata_json=metadata_json or STOOQ_METADATA_JSON,
            cache_dir=cache_dir or STOOQ_CACHE_DIR,
            cache_manifest_json=cache_manifest_json or STOOQ_CACHE_MANIFEST,
            as_of_date=as_of_date or datetime.now(timezone.utc).date(),
            fetcher=fetcher or default_stooq_fetcher,
        )
    if source == "yahoo_chart_public":
        return write_yahoo_outputs(
            symbols=symbols,
            start=start,
            end=end,
            raw_csv=raw_csv or YAHOO_PRICE_CSV,
            metadata_json=metadata_json or YAHOO_METADATA_JSON,
            cache_dir=cache_dir or YAHOO_CACHE_DIR,
            cache_manifest_json=cache_manifest_json or YAHOO_CACHE_MANIFEST,
            as_of_date=as_of_date or datetime.now(timezone.utc).date(),
            fetcher=fetcher or default_public_json_fetcher,
        )
    raise ValueError(f"Unsupported source: {source}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download or generate ETF price inputs")
    parser.add_argument("--source", default="sample")
    parser.add_argument("--start", default="2024-01-02")
    parser.add_argument("--end", default="2024-01-31")
    parser.add_argument("--symbols", default=None)
    parser.add_argument("--as-of-date", default=None)
    args = parser.parse_args()

    metadata = write_outputs(
        source=args.source,
        symbols=args.symbols,
        start=parse_date(args.start),
        end=parse_date(args.end),
        as_of_date=parse_date(args.as_of_date) if args.as_of_date else None,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

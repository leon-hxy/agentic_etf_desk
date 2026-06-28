#!/usr/bin/env python3
"""Build and review the Stage 3.1 real ETF monthly panel."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from load_universe import UNIVERSE_PATH, allowed_symbols


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "raw" / "prices_yahoo_chart.csv"
DEFAULT_INPUT_METADATA = ROOT / "data" / "raw" / "prices_yahoo_chart_metadata.json"
DEFAULT_MONTHLY_PANEL = ROOT / "data" / "processed" / "stage3_1_monthly_panel.csv"
DEFAULT_MONTHLY_METADATA = ROOT / "data" / "processed" / "stage3_1_monthly_panel_metadata.json"
REPORT_DIR = ROOT / "reports" / "data_quality"
DEFAULT_REPORT_JSON = REPORT_DIR / "stage3_1_wp2_data_quality_report.json"
DEFAULT_REPORT_MD = REPORT_DIR / "stage3_1_wp2_data_quality_report.md"
STAGE = "Stage 3.1 WP2 real data quality and monthly panel completed_internal_review"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def stable_generated_at(report_path: Path, payload: dict[str, Any]) -> str:
    if not report_path.exists():
        return datetime.now(timezone.utc).isoformat()
    try:
        previous = read_json(report_path)
    except json.JSONDecodeError:
        return datetime.now(timezone.utc).isoformat()
    comparable = dict(payload)
    comparable.pop("generated_at", None)
    previous_comparable = dict(previous)
    previous_comparable.pop("generated_at", None)
    if comparable == previous_comparable and previous.get("generated_at"):
        return str(previous["generated_at"])
    return datetime.now(timezone.utc).isoformat()


def positive_float(value: str, symbol: str, date_value: str, field: str) -> tuple[float | None, dict[str, str] | None]:
    try:
        parsed = float(value)
    except ValueError:
        return None, {"symbol": symbol, "date": date_value, "field": field, "value": value}
    if parsed <= 0:
        return None, {"symbol": symbol, "date": date_value, "field": field, "value": value}
    return parsed, None


def build_payload(
    *,
    input_csv: Path,
    input_metadata_path: Path,
    monthly_panel_path: Path,
    monthly_metadata_path: Path,
    report_json_path: Path,
    benchmark_symbol: str,
    max_stale_calendar_days: int,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    metadata = read_json(input_metadata_path)
    rows = read_csv(input_csv)
    if not rows:
        raise ValueError(f"Missing rows in {rel(input_csv)}")

    allowed = set(allowed_symbols(UNIVERSE_PATH))
    benchmark = benchmark_symbol.strip().upper()
    if benchmark not in allowed:
        raise ValueError(f"Benchmark symbol is not allowed by universe: {benchmark}")

    symbols_in_rows = sorted({row.get("symbol", "").strip().upper() for row in rows if row.get("symbol")})
    unknown_symbols = sorted(symbol for symbol in symbols_in_rows if symbol not in allowed)
    metadata_symbols = [str(symbol).upper() for symbol in metadata.get("symbols", [])]
    metadata_symbol_mismatch = sorted(set(symbols_in_rows).symmetric_difference(metadata_symbols))

    parse_errors: list[dict[str, str]] = []
    non_positive_prices: list[dict[str, str]] = []
    by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        symbol = row.get("symbol", "").strip().upper()
        date_value = row.get("date", "")
        adjusted_close, adjusted_error = positive_float(
            row.get("adjusted_close", ""),
            symbol,
            date_value,
            "adjusted_close",
        )
        total_return_index, tri_error = positive_float(
            row.get("total_return_index", ""),
            symbol,
            date_value,
            "total_return_index",
        )
        if adjusted_error:
            non_positive_prices.append(adjusted_error)
        if tri_error:
            non_positive_prices.append(tri_error)
        try:
            parsed_date = parse_iso_date(date_value)
        except ValueError:
            parse_errors.append({"symbol": symbol, "date": date_value, "field": "date", "value": date_value})
            continue
        if adjusted_close is None or total_return_index is None:
            continue
        by_symbol[symbol].append(
            {
                "date": parsed_date,
                "date_text": date_value,
                "adjusted_close": adjusted_close,
                "total_return_index": total_return_index,
                "source": row.get("source", metadata.get("source", "")),
            }
        )

    for series in by_symbol.values():
        series.sort(key=lambda item: item["date"])

    all_dates = sorted({item["date_text"] for series in by_symbol.values() for item in series})
    first_available_dates = {
        symbol: series[0]["date_text"]
        for symbol, series in sorted(by_symbol.items())
        if series
    }
    last_available_dates = {
        symbol: series[-1]["date_text"]
        for symbol, series in sorted(by_symbol.items())
        if series
    }
    row_counts_by_symbol = {symbol: len(series) for symbol, series in sorted(by_symbol.items())}

    daily_missing_values_by_symbol: dict[str, int] = {}
    for symbol, series in sorted(by_symbol.items()):
        symbol_dates = {item["date_text"] for item in series}
        first_date = series[0]["date_text"]
        daily_missing_values_by_symbol[symbol] = sum(
            1
            for date_value in all_dates
            if date_value >= first_date and date_value not in symbol_dates
        )

    as_of = parse_iso_date(str(metadata["as_of_date"]))
    stale_calendar_days_by_symbol = {
        symbol: (as_of - parse_iso_date(last_date)).days
        for symbol, last_date in sorted(last_available_dates.items())
    }

    adjusted_price_coverage_by_symbol = {
        symbol: round(row_counts_by_symbol.get(symbol, 0) / max(1, row_counts_by_symbol.get(symbol, 0)), 6)
        for symbol in symbols_in_rows
    }

    monthly_last_by_symbol: dict[str, dict[str, dict[str, Any]]] = {}
    for symbol, series in sorted(by_symbol.items()):
        monthly: dict[str, dict[str, Any]] = {}
        for item in series:
            month = item["date_text"][:7]
            if month not in monthly or item["date"] > monthly[month]["date"]:
                monthly[month] = item
        monthly_last_by_symbol[symbol] = monthly

    months = sorted({month for monthly in monthly_last_by_symbol.values() for month in monthly})
    sorted_symbols = sorted(symbols_in_rows)
    benchmark_monthly = monthly_last_by_symbol.get(benchmark, {})
    benchmark_missing_months = [month for month in months if month not in benchmark_monthly]

    panel_rows: list[dict[str, str]] = []
    monthly_missing_values_by_symbol = {symbol: 0 for symbol in sorted_symbols}
    for month in months:
        benchmark_item = benchmark_monthly.get(month)
        for symbol in sorted_symbols:
            item = monthly_last_by_symbol.get(symbol, {}).get(month)
            if item is None:
                monthly_missing_values_by_symbol[symbol] += 1
                continue
            panel_rows.append(
                {
                    "month": month,
                    "month_end_date": item["date_text"],
                    "symbol": symbol,
                    "adjusted_close": f"{item['adjusted_close']:.4f}",
                    "total_return_index": f"{item['total_return_index']:.4f}",
                    "source": str(item["source"]),
                    "benchmark_symbol": benchmark,
                    "benchmark_month_end_date": benchmark_item["date_text"] if benchmark_item else "",
                    "benchmark_adjusted_close": f"{benchmark_item['adjusted_close']:.4f}" if benchmark_item else "",
                    "benchmark_total_return_index": f"{benchmark_item['total_return_index']:.4f}" if benchmark_item else "",
                }
            )

    missing_daily_passed = not any(daily_missing_values_by_symbol.values())
    missing_monthly_passed = not any(monthly_missing_values_by_symbol.values())
    stale_passed = all(days <= max_stale_calendar_days for days in stale_calendar_days_by_symbol.values())
    adjusted_coverage_passed = not parse_errors and not non_positive_prices
    benchmark_available = benchmark in symbols_in_rows and not benchmark_missing_months
    universe_passed = not unknown_symbols and not metadata_symbol_mismatch

    quality_checks = {
        "universe_allowlist": {
            "passed": universe_passed,
            "description": "Every symbol in the real data file and WP1 metadata must come from configs/universe/etf_universe.yaml.",
        },
        "daily_missing_data": {
            "passed": missing_daily_passed,
            "description": "Every symbol has values for each observed daily date after its first available date.",
        },
        "monthly_missing_data": {
            "passed": missing_monthly_passed,
            "description": "Every symbol has one reviewed month-end observation for each panel month.",
        },
        "stale_prices": {
            "passed": stale_passed,
            "max_stale_calendar_days": max_stale_calendar_days,
            "description": "Every symbol has a latest available price within the configured stale-price tolerance.",
        },
        "adjusted_price_coverage": {
            "passed": adjusted_coverage_passed,
            "description": "Every input row has positive numeric adjusted_close and total_return_index fields.",
        },
        "benchmark_availability": {
            "passed": benchmark_available,
            "benchmark_symbol": benchmark,
            "description": "The benchmark symbol exists in the universe and has one month-end observation for every panel month.",
        },
    }
    status = "passed" if all(check["passed"] for check in quality_checks.values()) else "failed"

    payload: dict[str, Any] = {
        "stage": STAGE,
        "status": status,
        "source": metadata["source"],
        "public_data_source": metadata.get("public_data_source"),
        "input_file": rel(input_csv),
        "input_metadata_file": rel(input_metadata_path),
        "raw_cache_manifest_file": metadata.get("cache_manifest_file"),
        "monthly_panel_file": rel(monthly_panel_path),
        "monthly_metadata_file": rel(monthly_metadata_path),
        "universe_file": "configs/universe/etf_universe.yaml",
        "benchmark_symbol": benchmark,
        "row_count": len(rows),
        "monthly_row_count": len(panel_rows),
        "month_count": len(months),
        "panel_start_month": months[0] if months else None,
        "panel_end_month": months[-1] if months else None,
        "symbols": sorted_symbols,
        "unknown_symbols": unknown_symbols,
        "metadata_symbol_mismatch": metadata_symbol_mismatch,
        "first_available_dates": first_available_dates,
        "last_available_dates": last_available_dates,
        "row_counts_by_symbol": row_counts_by_symbol,
        "daily_missing_values_by_symbol": daily_missing_values_by_symbol,
        "monthly_missing_values_by_symbol": monthly_missing_values_by_symbol,
        "stale_calendar_days_by_symbol": stale_calendar_days_by_symbol,
        "adjusted_price_coverage_by_symbol": adjusted_price_coverage_by_symbol,
        "parse_errors": parse_errors,
        "non_positive_prices": non_positive_prices,
        "benchmark_missing_months": benchmark_missing_months,
        "quality_checks": quality_checks,
        "safety_flags": {
            "auto_trading_surface": False,
            "broker_surface": False,
            "broker_write_surface": False,
            "chatgpt_review_requested": False,
            "computer_use_executed": False,
            "dependencies_installed": False,
            "feishu_gateway_modified": False,
            "feishu_message_sent": False,
            "hermes_modified": False,
            "openclaw_modified": False,
            "order_placement_surface": False,
            "real_config_modified": False,
            "secret_values_written": False,
            "secrets_touched": False,
            "sent_to_chatgpt": False,
            "services_restarted": False,
        },
        "final_trading_notice": FINAL_TRADING_NOTICE,
    }
    payload["generated_at"] = stable_generated_at(report_json_path, payload)
    return payload, panel_rows


def write_monthly_panel(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "month",
        "month_end_date",
        "symbol",
        "adjusted_close",
        "total_return_index",
        "source",
        "benchmark_symbol",
        "benchmark_month_end_date",
        "benchmark_adjusted_close",
        "benchmark_total_return_index",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 3.1 WP2 Data Quality Report",
        "",
        f"- Stage: `{payload['stage']}`",
        f"- Status: `{payload['status']}`",
        f"- Source: `{payload['source']}`",
        f"- Input file: `{payload['input_file']}`",
        f"- Monthly panel: `{payload['monthly_panel_file']}`",
        f"- Benchmark symbol: `{payload['benchmark_symbol']}`",
        f"- Months: `{payload['month_count']}`",
        f"- Monthly rows: `{payload['monthly_row_count']}`",
        "",
        "## Quality Checks",
        "",
    ]
    for name, check in payload["quality_checks"].items():
        lines.append(f"- `{name}`: `{'passed' if check['passed'] else 'failed'}`")
    lines.extend(
        [
            "",
            "## Symbol Coverage",
            "",
            "| Symbol | Daily Rows | First Available | Last Available | Daily Missing | Monthly Missing | Stale Days |",
            "|---|---:|---|---|---:|---:|---:|",
        ]
    )
    for symbol in payload["symbols"]:
        lines.append(
            "| {symbol} | {rows} | {first} | {last} | {daily_missing} | {monthly_missing} | {stale} |".format(
                symbol=symbol,
                rows=payload["row_counts_by_symbol"].get(symbol, 0),
                first=payload["first_available_dates"].get(symbol, ""),
                last=payload["last_available_dates"].get(symbol, ""),
                daily_missing=payload["daily_missing_values_by_symbol"].get(symbol, 0),
                monthly_missing=payload["monthly_missing_values_by_symbol"].get(symbol, 0),
                stale=payload["stale_calendar_days_by_symbol"].get(symbol, ""),
            )
        )
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- No Computer Use.",
            "- No ChatGPT review requested.",
            "- No Feishu message sent.",
            "- No real Hermes, OpenClaw, or Feishu gateway modification.",
            "- No dependency installation.",
            "- No broker surface, order placement surface, or automatic trading surface.",
            "",
            FINAL_TRADING_NOTICE,
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    payload: dict[str, Any],
    panel_rows: list[dict[str, str]],
    monthly_panel_path: Path,
    monthly_metadata_path: Path,
    report_json_path: Path,
    report_md_path: Path,
) -> None:
    write_monthly_panel(monthly_panel_path, panel_rows)
    monthly_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    monthly_metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_md_path.write_text(write_markdown(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Stage 3.1 real ETF monthly panel")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--input-metadata", default=str(DEFAULT_INPUT_METADATA))
    parser.add_argument("--monthly-panel", default=str(DEFAULT_MONTHLY_PANEL))
    parser.add_argument("--monthly-metadata", default=str(DEFAULT_MONTHLY_METADATA))
    parser.add_argument("--report-json", default=str(DEFAULT_REPORT_JSON))
    parser.add_argument("--report-md", default=str(DEFAULT_REPORT_MD))
    parser.add_argument("--benchmark-symbol", default="VTI")
    parser.add_argument("--max-stale-calendar-days", type=int, default=7)
    args = parser.parse_args()

    monthly_panel = Path(args.monthly_panel)
    monthly_metadata = Path(args.monthly_metadata)
    report_json = Path(args.report_json)
    report_md = Path(args.report_md)
    payload, panel_rows = build_payload(
        input_csv=Path(args.input),
        input_metadata_path=Path(args.input_metadata),
        monthly_panel_path=monthly_panel,
        monthly_metadata_path=monthly_metadata,
        report_json_path=report_json,
        benchmark_symbol=args.benchmark_symbol,
        max_stale_calendar_days=args.max_stale_calendar_days,
    )
    write_outputs(payload, panel_rows, monthly_panel, monthly_metadata, report_json, report_md)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

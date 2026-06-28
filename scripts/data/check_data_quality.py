#!/usr/bin/env python3
"""Run repo-only ETF price data quality checks."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from load_universe import UNIVERSE_PATH, allowed_symbols


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "raw" / "prices_sample.csv"
SOURCE_PLAN = ROOT / "configs" / "data_sources" / "stage3_data_sources.json"
REPORT_DIR = ROOT / "reports" / "data_quality"
REPORT_JSON = REPORT_DIR / "stage3b_data_quality_report.json"
REPORT_MD = REPORT_DIR / "stage3b_data_quality_report.md"
STAGE = "Stage 3B data quality checks completed"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_source_plan(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("selected_primary_source") != "stooq_daily_csv":
        raise ValueError("Stage 3B expects the Stage 3A primary source to be stooq_daily_csv")
    if payload.get("automatic_trading_allowed") is not False:
        raise ValueError("Data source plan must not allow automatic trading")
    if payload.get("broker_access_write_allowed") is not False:
        raise ValueError("Data source plan must not allow broker write access")
    return payload


def stable_generated_at(payload: dict[str, Any]) -> str:
    if not REPORT_JSON.exists():
        return datetime.now(timezone.utc).isoformat()
    try:
        previous = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return datetime.now(timezone.utc).isoformat()
    comparable = dict(payload)
    comparable.pop("generated_at", None)
    previous_comparable = dict(previous)
    previous_comparable.pop("generated_at", None)
    if comparable == previous_comparable and previous.get("generated_at"):
        return str(previous["generated_at"])
    return datetime.now(timezone.utc).isoformat()


def analyze(raw_csv: Path, source_plan_path: Path, abnormal_threshold: float) -> dict[str, Any]:
    plan = read_source_plan(source_plan_path)
    allowed = set(allowed_symbols(UNIVERSE_PATH))
    rows = read_csv(raw_csv)
    if not rows:
        raise ValueError(f"Missing rows in {rel(raw_csv)}")

    symbols_in_rows = sorted({row.get("symbol", "").upper() for row in rows if row.get("symbol")})
    unknown_symbols = sorted(symbol for symbol in symbols_in_rows if symbol not in allowed)

    by_symbol: dict[str, list[tuple[str, float]]] = defaultdict(list)
    non_positive_prices: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []

    for row in rows:
        symbol = row.get("symbol", "").upper()
        date_value = row.get("date", "")
        raw_price = row.get("adjusted_close", "")
        try:
            price = float(raw_price)
        except ValueError:
            parse_errors.append({"symbol": symbol, "date": date_value, "value": raw_price})
            continue
        if price <= 0:
            non_positive_prices.append({"symbol": symbol, "date": date_value, "value": price})
            continue
        by_symbol[symbol].append((date_value, price))

    all_dates = sorted({date_value for series in by_symbol.values() for date_value, _ in series})
    first_available_dates = {
        symbol: min(date_value for date_value, _ in series)
        for symbol, series in sorted(by_symbol.items())
        if series
    }
    last_available_dates = {
        symbol: max(date_value for date_value, _ in series)
        for symbol, series in sorted(by_symbol.items())
        if series
    }
    row_counts_by_symbol = {
        symbol: len(series)
        for symbol, series in sorted(by_symbol.items())
    }
    missing_values_by_symbol = {}
    pre_start_gaps_by_symbol = {}
    for symbol, series in sorted(by_symbol.items()):
        symbol_dates = {date for date, _ in series}
        first_date = min(symbol_dates)
        missing_values_by_symbol[symbol] = sum(
            1
            for date_value in all_dates
            if date_value >= first_date and date_value not in symbol_dates
        )
        pre_start_gaps_by_symbol[symbol] = sum(
            1 for date_value in all_dates if date_value < first_date
        )

    abnormal_price_points: list[dict[str, Any]] = []
    for symbol, series in sorted(by_symbol.items()):
        series.sort()
        previous: float | None = None
        for date_value, price in series:
            if previous is not None:
                move = price / previous - 1.0
                if abs(move) > abnormal_threshold:
                    abnormal_price_points.append(
                        {
                            "symbol": symbol,
                            "date": date_value,
                            "daily_move": round(move, 6),
                            "threshold": abnormal_threshold,
                        }
                    )
            previous = price

    missing_passed = not any(missing_values_by_symbol.values())
    adjusted_passed = not non_positive_prices and not parse_errors
    abnormal_passed = not abnormal_price_points
    start_dates_passed = set(first_available_dates) == set(symbols_in_rows)
    status = "passed" if not unknown_symbols and missing_passed and adjusted_passed and abnormal_passed and start_dates_passed else "failed"

    payload: dict[str, Any] = {
        "stage": STAGE,
        "status": status,
        "input_file": rel(raw_csv),
        "source_plan_file": rel(source_plan_path),
        "source_plan": {
            "selected_primary_source": plan["selected_primary_source"],
            "selected_stage3b_source_note": "Stage 3B validates quality logic on the current repo raw input; public source fetch is not required for this test run.",
        },
        "row_count": len(rows),
        "symbols": symbols_in_rows,
        "unknown_symbols": unknown_symbols,
        "panel_start_date": all_dates[0] if all_dates else None,
        "panel_end_date": all_dates[-1] if all_dates else None,
        "row_counts_by_symbol": row_counts_by_symbol,
        "first_available_dates": first_available_dates,
        "last_available_dates": last_available_dates,
        "missing_values_by_symbol": missing_values_by_symbol,
        "pre_start_gaps_by_symbol": pre_start_gaps_by_symbol,
        "non_positive_prices": non_positive_prices,
        "parse_errors": parse_errors,
        "abnormal_price_points": abnormal_price_points,
        "quality_checks": {
            "missing_values": {
                "passed": missing_passed,
                "description": "Every symbol has values for each observed panel date after its first available date.",
            },
            "start_dates": {
                "passed": start_dates_passed,
                "description": "Every symbol has a first and last available date recorded.",
            },
            "adjusted_prices": {
                "passed": adjusted_passed,
                "assumption": "Input adjusted_close is treated as the adjusted price field and must be numeric and positive.",
            },
            "abnormal_prices": {
                "passed": abnormal_passed,
                "threshold": abnormal_threshold,
                "description": "Flag absolute one-day adjusted-close moves above the configured threshold.",
            },
        },
        "safety_flags": {
            "auto_trading_surface": False,
            "broker_surface": False,
            "chatgpt_review_requested": False,
            "computer_use_executed": False,
            "dependencies_installed": False,
            "feishu_gateway_modified": False,
            "feishu_message_sent": False,
            "hermes_modified": False,
            "openclaw_modified": False,
            "real_config_modified": False,
            "secret_values_written": False,
            "secrets_touched": False,
            "sent_to_chatgpt": False,
            "services_restarted": False,
        },
        "final_trading_notice": FINAL_TRADING_NOTICE,
    }
    payload["generated_at"] = stable_generated_at(payload)
    return payload


def write_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 3B Data Quality Report",
        "",
        f"- Stage: `{payload['stage']}`",
        f"- Status: `{payload['status']}`",
        f"- Input file: `{payload['input_file']}`",
        f"- Source plan: `{payload['source_plan_file']}`",
        f"- Primary source from Stage 3A: `{payload['source_plan']['selected_primary_source']}`",
        f"- Row count: `{payload['row_count']}`",
        "",
        "## Quality Checks",
        "",
    ]
    for name, check in payload["quality_checks"].items():
        lines.append(f"- `{name}`: `{'passed' if check['passed'] else 'failed'}`")
    lines.extend(
        [
            "",
            "## Symbols",
            "",
            "| Symbol | Rows | First Available | Last Available | Missing Values |",
            "|---|---:|---|---|---:|",
        ]
    )
    for symbol in payload["symbols"]:
        lines.append(
            "| {symbol} | {rows} | {first} | {last} | {missing} |".format(
                symbol=symbol,
                rows=payload["row_counts_by_symbol"].get(symbol, 0),
                first=payload["first_available_dates"].get(symbol, ""),
                last=payload["last_available_dates"].get(symbol, ""),
                missing=payload["missing_values_by_symbol"].get(symbol, 0),
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
            "- No broker surface or automatic trading surface.",
            "",
            FINAL_TRADING_NOTICE,
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(write_markdown(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ETF data quality checks")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--source-plan", default=str(SOURCE_PLAN))
    parser.add_argument("--abnormal-threshold", type=float, default=0.80)
    args = parser.parse_args()

    payload = analyze(Path(args.input), Path(args.source_plan), args.abnormal_threshold)
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

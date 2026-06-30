#!/usr/bin/env python3
"""Import manually supplied ETF holdings through the repo universe allowlist."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "portfolio"
OUTPUT_CSV = DATA_DIR / "manual_holdings_latest.csv"
OUTPUT_JSON = DATA_DIR / "manual_holdings_latest.json"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))

SCRIPTS_DATA = ROOT / "scripts" / "data"
if str(SCRIPTS_DATA) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DATA))

from load_universe import validate_requested_symbols  # noqa: E402


REQUIRED_COLUMNS = ["symbol", "quantity", "market_value"]


def _decimal(value: str, field: str, symbol: str) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"{symbol} has invalid {field}: {value}") from exc
    if parsed < 0:
        raise ValueError(f"{symbol} has negative {field}: {value}")
    return parsed


def _read_rows(input_csv: Path) -> list[dict[str, Any]]:
    with input_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Holdings CSV missing required column(s): {', '.join(missing)}")
        raw_rows = list(reader)

    if not raw_rows:
        raise ValueError("Holdings CSV must contain at least one row")

    requested = [str(row["symbol"]) for row in raw_rows]
    normalized_symbols = validate_requested_symbols(requested)
    if len(set(normalized_symbols)) != len(normalized_symbols):
        raise ValueError("Holdings CSV must not contain duplicate symbols")

    rows: list[dict[str, Any]] = []
    total_market_value = Decimal("0")
    for raw, symbol in zip(raw_rows, normalized_symbols, strict=True):
        quantity = _decimal(raw["quantity"], "quantity", symbol)
        market_value = _decimal(raw["market_value"], "market_value", symbol)
        total_market_value += market_value
        rows.append(
            {
                "market_value_decimal": market_value,
                "quantity_decimal": quantity,
                "symbol": symbol,
            }
        )

    if total_market_value <= 0:
        raise ValueError("Holdings CSV total market_value must be greater than zero")

    normalized: list[dict[str, Any]] = []
    for row in rows:
        market_value = row["market_value_decimal"]
        quantity = row["quantity_decimal"]
        normalized.append(
            {
                "market_value": float(market_value),
                "portfolio_weight": float(market_value / total_market_value),
                "quantity": float(quantity),
                "symbol": row["symbol"],
            }
        )
    return normalized


def import_holdings(input_csv: Path, output_csv: Path = OUTPUT_CSV, output_json: Path = OUTPUT_JSON) -> dict[str, Any]:
    holdings = _read_rows(input_csv)
    total_market_value = sum(row["market_value"] for row in holdings)
    payload = {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "holdings": holdings,
        "manual_trading_note": MANUAL_NOTE_EN,
        "source": "manual_csv_import",
        "symbol_count": len(holdings),
        "total_market_value": round(total_market_value, 10),
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
    }

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["symbol", "quantity", "market_value", "portfolio_weight"])
        writer.writeheader()
        writer.writerows(holdings)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a manual ETF holdings CSV")
    parser.add_argument("--input", required=True, help="CSV with symbol, quantity, and market_value columns")
    args = parser.parse_args()
    try:
        payload = import_holdings(Path(args.input))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "symbols": [row["symbol"] for row in payload["holdings"]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

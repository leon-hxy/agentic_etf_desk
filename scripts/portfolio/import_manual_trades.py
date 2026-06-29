#!/usr/bin/env python3
"""Import manually supplied ETF trades through the repo universe allowlist."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "portfolio"
OUTPUT_CSV = DATA_DIR / "manual_trades_latest.csv"
OUTPUT_JSON = DATA_DIR / "manual_trades_latest.json"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))

SCRIPTS_DATA = ROOT / "scripts" / "data"
if str(SCRIPTS_DATA) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DATA))

from load_universe import validate_requested_symbols  # noqa: E402


REQUIRED_COLUMNS = ["trade_date", "symbol", "side", "quantity", "price"]
ALLOWED_SIDES = {"BUY", "SELL"}


def _decimal(value: str, field: str, symbol: str) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"{symbol} has invalid {field}: {value}") from exc
    if parsed <= 0:
        raise ValueError(f"{symbol} has non-positive {field}: {value}")
    return parsed


def _trade_date(value: str, symbol: str) -> str:
    raw = str(value).strip()
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError as exc:
        raise ValueError(f"{symbol} has invalid trade_date: {value}") from exc


def _side(value: str, symbol: str) -> str:
    side = str(value).strip().upper()
    if side not in ALLOWED_SIDES:
        raise ValueError(f"{symbol} has invalid side: {value}")
    return side


def _read_rows(input_csv: Path) -> list[dict[str, Any]]:
    with input_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Trades CSV missing required column(s): {', '.join(missing)}")
        raw_rows = list(reader)

    if not raw_rows:
        raise ValueError("Trades CSV must contain at least one row")

    requested = [str(row["symbol"]) for row in raw_rows]
    normalized_symbols = validate_requested_symbols(requested)

    normalized: list[dict[str, Any]] = []
    for raw, symbol in zip(raw_rows, normalized_symbols, strict=True):
        quantity = _decimal(raw["quantity"], "quantity", symbol)
        price = _decimal(raw["price"], "price", symbol)
        side = _side(raw["side"], symbol)
        signed_quantity = quantity if side == "BUY" else -quantity
        normalized.append(
            {
                "gross_notional": float(quantity * price),
                "price": float(price),
                "quantity": float(quantity),
                "side": side,
                "signed_quantity": float(signed_quantity),
                "symbol": symbol,
                "trade_date": _trade_date(raw["trade_date"], symbol),
            }
        )
    return normalized


def import_trades(input_csv: Path, output_csv: Path = OUTPUT_CSV, output_json: Path = OUTPUT_JSON) -> dict[str, Any]:
    trades = _read_rows(input_csv)
    gross_notional = sum(row["gross_notional"] for row in trades)
    payload = {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "gross_notional": round(gross_notional, 10),
        "manual_trading_note": MANUAL_NOTE_EN,
        "source": "manual_csv_import",
        "symbol_count": len({row["symbol"] for row in trades}),
        "trade_count": len(trades),
        "trades": trades,
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
    }

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["trade_date", "symbol", "side", "quantity", "price", "signed_quantity", "gross_notional"],
        )
        writer.writeheader()
        writer.writerows(trades)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a manual ETF trades CSV")
    parser.add_argument("--input", required=True, help="CSV with trade_date, symbol, side, quantity, and price columns")
    args = parser.parse_args()
    try:
        payload = import_trades(Path(args.input))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "symbols": [row["symbol"] for row in payload["trades"]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

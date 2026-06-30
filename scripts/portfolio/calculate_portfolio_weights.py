#!/usr/bin/env python3
"""Calculate ETF portfolio weights from the latest manual holdings snapshot."""

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
DEFAULT_HOLDINGS_JSON = DATA_DIR / "manual_holdings_latest.json"
OUTPUT_CSV = DATA_DIR / "portfolio_weights_latest.csv"
OUTPUT_JSON = DATA_DIR / "portfolio_weights_latest.json"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))

SCRIPTS_DATA = ROOT / "scripts" / "data"
if str(SCRIPTS_DATA) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DATA))

from load_universe import validate_requested_symbols  # noqa: E402


def _decimal(value: Any, field: str, symbol: str) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"{symbol} has invalid {field}: {value}") from exc
    if parsed < 0:
        raise ValueError(f"{symbol} has negative {field}: {value}")
    return parsed


def _read_holdings(path: Path) -> list[dict[str, Decimal | str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_holdings = payload.get("holdings")
    if not isinstance(raw_holdings, list) or not raw_holdings:
        raise ValueError("Holdings snapshot must contain a non-empty holdings list")

    requested = [str(row.get("symbol", "")) for row in raw_holdings]
    normalized_symbols = validate_requested_symbols(requested)
    if len(set(normalized_symbols)) != len(normalized_symbols):
        raise ValueError("Holdings snapshot must not contain duplicate symbols")

    holdings: list[dict[str, Decimal | str]] = []
    total_market_value = Decimal("0")
    for raw, symbol in zip(raw_holdings, normalized_symbols, strict=True):
        if not isinstance(raw, dict):
            raise ValueError("Each holding must be an object")
        quantity = _decimal(raw.get("quantity"), "quantity", symbol)
        market_value = _decimal(raw.get("market_value"), "market_value", symbol)
        total_market_value += market_value
        holdings.append({"market_value": market_value, "quantity": quantity, "symbol": symbol})

    if total_market_value <= 0:
        raise ValueError("Holdings snapshot total market_value must be greater than zero")
    return holdings


def calculate_portfolio_weights(
    holdings_json: Path = DEFAULT_HOLDINGS_JSON,
    output_csv: Path = OUTPUT_CSV,
    output_json: Path = OUTPUT_JSON,
) -> dict[str, Any]:
    holdings = _read_holdings(holdings_json)
    total_market_value = sum(row["market_value"] for row in holdings if isinstance(row["market_value"], Decimal))

    weights: list[dict[str, Any]] = []
    for row in holdings:
        market_value = row["market_value"]
        quantity = row["quantity"]
        assert isinstance(market_value, Decimal)
        assert isinstance(quantity, Decimal)
        weights.append(
            {
                "market_value": float(market_value),
                "portfolio_weight": float(market_value / total_market_value),
                "quantity": float(quantity),
                "symbol": row["symbol"],
            }
        )

    largest = max(weights, key=lambda row: row["portfolio_weight"])
    smallest = min(weights, key=lambda row: row["portfolio_weight"])
    total_weight = sum(row["portfolio_weight"] for row in weights)
    payload = {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "largest_position": largest,
        "manual_trading_note": MANUAL_NOTE_EN,
        "smallest_position": smallest,
        "source": "manual_holdings_snapshot",
        "symbol_count": len(weights),
        "total_market_value": round(float(total_market_value), 10),
        "total_weight": round(total_weight, 12),
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
        "weights": weights,
    }

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["symbol", "quantity", "market_value", "portfolio_weight"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(weights)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate ETF portfolio weights from manual holdings")
    parser.add_argument("--holdings", default=str(DEFAULT_HOLDINGS_JSON), help="Manual holdings JSON snapshot")
    args = parser.parse_args()
    try:
        payload = calculate_portfolio_weights(Path(args.holdings))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "symbols": [row["symbol"] for row in payload["weights"]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

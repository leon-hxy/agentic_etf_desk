#!/usr/bin/env python3
"""Portfolio data helpers for the repo-only ETF backtest engine."""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_SOURCE = "data/processed/price_panel.csv"
UNIVERSE_SOURCE = "configs/universe/etf_universe.yaml"
PANEL_CSV = ROOT / DATA_SOURCE

sys.path.insert(0, str(ROOT / "scripts" / "data"))
from load_universe import allowed_symbols, validate_requested_symbols  # noqa: E402


PriceRow = dict[str, Any]


def allowed_universe_symbols() -> list[str]:
    return allowed_symbols(ROOT / UNIVERSE_SOURCE)


def validate_symbols(symbols: list[str] | None) -> list[str]:
    if not symbols:
        return allowed_universe_symbols()
    return validate_requested_symbols(symbols, ROOT / UNIVERSE_SOURCE)


def load_price_panel(path: Path = PANEL_CSV) -> list[PriceRow]:
    if not path.exists():
        raise FileNotFoundError(f"Missing price panel: {DATA_SOURCE}")

    rows: list[PriceRow] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "date" not in reader.fieldnames:
            raise ValueError("price panel must contain a date column")
        for raw in reader:
            parsed: PriceRow = {"date": raw["date"], "date_value": date.fromisoformat(raw["date"])}
            for field, value in raw.items():
                if field == "date":
                    continue
                parsed[field] = float(value) if value else None
            rows.append(parsed)

    rows.sort(key=lambda row: row["date"])
    return rows


def panel_symbols(panel: list[PriceRow]) -> list[str]:
    if not panel:
        return []
    return sorted(key for key in panel[0] if key not in {"date", "date_value"})


def filter_panel_symbols(panel: list[PriceRow], requested_symbols: list[str]) -> list[str]:
    available = set(panel_symbols(panel))
    allowed = set(allowed_universe_symbols())
    symbols = [symbol for symbol in requested_symbols if symbol in available and symbol in allowed]
    if not symbols:
        raise ValueError("No requested symbols are both allowed by universe and present in price panel")
    return symbols


def latest_price(panel: list[PriceRow], symbol: str, index: int) -> float | None:
    cursor = min(index, len(panel) - 1)
    while cursor >= 0:
        value = panel[cursor].get(symbol)
        if isinstance(value, float):
            return value
        cursor -= 1
    return None


def historical_prices(panel: list[PriceRow], symbol: str, end_index: int, lookback: int) -> list[float]:
    values: list[float] = []
    cursor = min(end_index, len(panel) - 1)
    while cursor >= 0 and len(values) < lookback:
        value = panel[cursor].get(symbol)
        if isinstance(value, float):
            values.append(value)
        cursor -= 1
    return list(reversed(values))


def period_return(panel: list[PriceRow], symbol: str, previous_index: int, current_index: int) -> float:
    previous = latest_price(panel, symbol, previous_index)
    current = panel[current_index].get(symbol) if current_index < len(panel) else None
    if not isinstance(previous, float) or not isinstance(current, float) or previous <= 0:
        return 0.0
    return current / previous - 1.0


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    cleaned = {symbol: max(0.0, float(weight)) for symbol, weight in weights.items() if weight > 0}
    total = sum(cleaned.values())
    if total <= 0:
        return {}
    return {symbol: weight / total for symbol, weight in cleaned.items()}


def equal_weights(symbols: list[str]) -> dict[str, float]:
    if not symbols:
        return {}
    weight = 1.0 / len(symbols)
    return {symbol: weight for symbol in symbols}


def turnover(previous: dict[str, float], current: dict[str, float]) -> float:
    symbols = set(previous) | set(current)
    return sum(abs(current.get(symbol, 0.0) - previous.get(symbol, 0.0)) for symbol in symbols)

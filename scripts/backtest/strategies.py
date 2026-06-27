#!/usr/bin/env python3
"""Strategy weight rules for data/processed/price_panel.csv ETF backtests."""

from __future__ import annotations

import json
from pathlib import Path

from metrics import stdev
from portfolio import PriceRow, equal_weights, historical_prices, normalize_weights, period_return


ROOT = Path(__file__).resolve().parents[2]
DATA_SOURCE = "data/processed/price_panel.csv"
UNIVERSE_SOURCE = "configs/universe/etf_universe.yaml"
STRATEGY_ROOT = ROOT / "strategies"


def load_strategy_config(strategy_id: str) -> dict[str, object]:
    path = STRATEGY_ROOT / strategy_id / "strategy.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing strategy config: strategies/{strategy_id}/strategy.yaml")
    return json.loads(path.read_text(encoding="utf-8"))


def _configured_symbols(config: dict[str, object], allowed_symbols: list[str]) -> list[str]:
    configured = [str(symbol) for symbol in config.get("allowed_symbols", [])]
    allowed = set(allowed_symbols)
    return [symbol for symbol in configured if symbol in allowed]


def _defensive(config: dict[str, object], allowed_symbols: list[str]) -> dict[str, float]:
    rule = dict(config.get("weight_rule", {}))
    defensive_symbol = str(rule.get("defensive_symbol", "BIL"))
    if defensive_symbol not in allowed_symbols:
        defensive_symbol = allowed_symbols[0]
    return {defensive_symbol: 1.0}


def _static(config: dict[str, object], allowed_symbols: list[str]) -> dict[str, float]:
    rule = dict(config.get("weight_rule", {}))
    target_weights = dict(rule.get("target_weights", {}))
    return normalize_weights(
        {symbol: float(weight) for symbol, weight in target_weights.items() if symbol in allowed_symbols}
    )


def _equal(config: dict[str, object], allowed_symbols: list[str]) -> dict[str, float]:
    return equal_weights(_configured_symbols(config, allowed_symbols))


def _sma_filter(
    config: dict[str, object],
    panel: list[PriceRow],
    signal_index: int,
    allowed_symbols: list[str],
) -> dict[str, float]:
    rule = dict(config.get("weight_rule", {}))
    lookback = int(rule.get("lookback_months", 10)) * 21
    passing: list[str] = []
    for symbol in rule.get("risk_symbols", []):
        if symbol not in allowed_symbols:
            continue
        history = historical_prices(panel, str(symbol), signal_index, lookback)
        if len(history) < max(2, min(lookback, len(panel))):
            continue
        average = sum(history) / len(history)
        if history[-1] > average:
            passing.append(str(symbol))
    return equal_weights(passing) if passing else _defensive(config, allowed_symbols)


def _dual_momentum(
    config: dict[str, object],
    panel: list[PriceRow],
    signal_index: int,
    allowed_symbols: list[str],
) -> dict[str, float]:
    rule = dict(config.get("weight_rule", {}))
    lookback = int(rule.get("lookback_months", 12)) * 21
    threshold = float(rule.get("absolute_momentum_threshold", 0.0))
    scores: dict[str, float] = {}
    for symbol in rule.get("candidate_symbols", []):
        if symbol not in allowed_symbols:
            continue
        history = historical_prices(panel, str(symbol), signal_index, lookback)
        if len(history) < 2 or history[0] <= 0:
            continue
        scores[str(symbol)] = history[-1] / history[0] - 1.0
    if not scores:
        return _defensive(config, allowed_symbols)
    best_symbol, best_score = max(scores.items(), key=lambda item: item[1])
    return {best_symbol: 1.0} if best_score > threshold else _defensive(config, allowed_symbols)


def _inverse_volatility(
    config: dict[str, object],
    panel: list[PriceRow],
    signal_index: int,
    allowed_symbols: list[str],
) -> dict[str, float]:
    rule = dict(config.get("weight_rule", {}))
    lookback = int(rule.get("volatility_lookback_days", 63))
    weights: dict[str, float] = {}
    for symbol in _configured_symbols(config, allowed_symbols):
        history = historical_prices(panel, symbol, signal_index, lookback + 1)
        returns = [history[index] / history[index - 1] - 1.0 for index in range(1, len(history))]
        volatility = stdev(returns) if len(returns) >= 2 else 0.01
        weights[symbol] = 1.0 / max(volatility, 0.0001)
    risk_limits = dict(config.get("risk_limits", {}))
    max_weight = float(risk_limits.get("max_single_etf_weight", 1.0))
    normalized = normalize_weights(weights)
    capped = {symbol: min(weight, max_weight) for symbol, weight in normalized.items()}
    return normalize_weights(capped)


def _trend_inverse_volatility(
    config: dict[str, object],
    panel: list[PriceRow],
    signal_index: int,
    allowed_symbols: list[str],
) -> dict[str, float]:
    passing_config = dict(config)
    rule = dict(config.get("weight_rule", {}))
    passing_config["weight_rule"] = {
        "risk_symbols": _configured_symbols(config, allowed_symbols),
        "defensive_symbol": rule.get("defensive_symbol", "BIL"),
        "lookback_months": rule.get("lookback_months", 10),
    }
    passing = _sma_filter(passing_config, panel, signal_index, allowed_symbols)
    if set(passing) == {str(rule.get("defensive_symbol", "BIL"))}:
        return passing
    vol_config = dict(config)
    vol_config["allowed_symbols"] = list(passing)
    return _inverse_volatility(vol_config, panel, signal_index, allowed_symbols)


def _mean_reversion(
    config: dict[str, object],
    panel: list[PriceRow],
    signal_index: int,
    allowed_symbols: list[str],
) -> dict[str, float]:
    rule = dict(config.get("weight_rule", {}))
    lookback = int(rule.get("lookback_days", 5))
    scores: dict[str, float] = {}
    for symbol in _configured_symbols(config, allowed_symbols):
        history = historical_prices(panel, symbol, signal_index, lookback + 1)
        if len(history) >= 2 and history[0] > 0:
            scores[symbol] = history[-1] / history[0] - 1.0
    if not scores:
        return _defensive(config, allowed_symbols)
    selected = sorted(scores.items(), key=lambda item: item[1])[:3]
    return equal_weights([symbol for symbol, _ in selected])


def weights_for_strategy(
    strategy_id: str,
    config: dict[str, object],
    panel: list[PriceRow],
    signal_index: int,
    allowed_symbols: list[str],
) -> dict[str, float]:
    if strategy_id in {"benchmark_buy_hold", "static_6040"}:
        return _static(config, allowed_symbols)
    if strategy_id == "equal_weight_etf":
        return _equal(config, allowed_symbols)
    if strategy_id == "gtaa_10m_sma":
        return _sma_filter(config, panel, signal_index, allowed_symbols)
    if strategy_id == "dual_momentum":
        return _dual_momentum(config, panel, signal_index, allowed_symbols)
    if strategy_id == "time_series_momentum_vol_target":
        return _trend_inverse_volatility(config, panel, signal_index, allowed_symbols)
    if strategy_id == "inverse_volatility_allocation":
        return _inverse_volatility(config, panel, signal_index, allowed_symbols)
    if strategy_id == "etf_mean_reversion_sandbox":
        return _mean_reversion(config, panel, signal_index, allowed_symbols)
    raise ValueError(f"Unknown strategy_id: {strategy_id}")


def benchmark_return(panel: list[PriceRow], benchmark_symbol: str, previous_index: int, current_index: int) -> float:
    return period_return(panel, benchmark_symbol, previous_index, current_index)

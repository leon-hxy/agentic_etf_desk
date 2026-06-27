#!/usr/bin/env python3
"""Performance metrics for data/processed/price_panel.csv ETF backtests."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Any


DATA_SOURCE = "data/processed/price_panel.csv"
UNIVERSE_SOURCE = "configs/universe/etf_universe.yaml"
TRADING_DAYS = 252


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    variance = sum((value - avg) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(max(0.0, variance))


def compound_return(returns: list[float]) -> float:
    value = 1.0
    for period_return in returns:
        value *= 1.0 + period_return
    return value - 1.0


def annualized_return(returns: list[float], periods_per_year: int = TRADING_DAYS) -> float:
    if not returns:
        return 0.0
    total = compound_return(returns)
    years = len(returns) / periods_per_year
    if years <= 0 or total <= -1:
        return 0.0
    return (1.0 + total) ** (1.0 / years) - 1.0


def max_drawdown(equity: list[float]) -> float:
    if not equity:
        return 0.0
    peak = equity[0]
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        drawdown = safe_divide(value, peak) - 1.0
        worst = min(worst, drawdown)
    return worst


def longest_recovery_days(dates: list[date], equity: list[float]) -> int:
    if not dates or not equity:
        return 0
    peak = equity[0]
    drawdown_start: date | None = None
    longest = 0
    for current_date, value in zip(dates, equity, strict=False):
        if value >= peak:
            if drawdown_start is not None:
                longest = max(longest, (current_date - drawdown_start).days)
                drawdown_start = None
            peak = value
        elif drawdown_start is None:
            drawdown_start = current_date
    if drawdown_start is not None:
        longest = max(longest, (dates[-1] - drawdown_start).days)
    return longest


def grouped_period_returns(dates: list[date], returns: list[float], group: str) -> dict[str, float]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for current_date, period_return in zip(dates, returns, strict=False):
        key = current_date.strftime("%Y-%m" if group == "month" else "%Y")
        buckets[key].append(period_return)
    return {key: compound_return(values) for key, values in buckets.items()}


def worst_period(period_returns: dict[str, float]) -> dict[str, Any]:
    if not period_returns:
        return {"period": None, "return": 0.0}
    period, value = min(period_returns.items(), key=lambda item: item[1])
    return {"period": period, "return": value}


def performance_metrics(
    dates: list[date],
    returns: list[float],
    equity: list[float],
    turnovers: list[float],
) -> dict[str, Any]:
    cagr = annualized_return(returns)
    volatility = stdev(returns) * math.sqrt(TRADING_DAYS)
    downside = [min(0.0, value) for value in returns]
    downside_volatility = stdev(downside) * math.sqrt(TRADING_DAYS)
    drawdown = max_drawdown(equity)
    month_returns = grouped_period_returns(dates, returns, "month")
    year_returns = grouped_period_returns(dates, returns, "year")
    trade_count = sum(1 for value in turnovers if value > 0.000001)

    return {
        "cagr": cagr,
        "sharpe": safe_divide(mean(returns) * TRADING_DAYS, volatility),
        "sortino": safe_divide(mean(returns) * TRADING_DAYS, downside_volatility),
        "max_drawdown": drawdown,
        "calmar": safe_divide(cagr, abs(drawdown)),
        "annualized_volatility": volatility,
        "win_rate": safe_divide(sum(1 for value in returns if value > 0), len(returns)),
        "turnover": sum(turnovers),
        "trade_count": trade_count,
        "worst_month": worst_period(month_returns),
        "worst_year": worst_period(year_returns),
        "longest_drawdown_recovery_days": longest_recovery_days(dates, equity),
    }

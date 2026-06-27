#!/usr/bin/env python3
"""Run repo-only ETF backtests from configs/universe/etf_universe.yaml."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from metrics import performance_metrics
from portfolio import (
    DATA_SOURCE,
    UNIVERSE_SOURCE,
    filter_panel_symbols,
    load_price_panel,
    period_return,
    turnover,
    validate_symbols,
)
from report_writer import write_aggregate_report
from strategies import benchmark_return, load_strategy_config, weights_for_strategy


ROOT = Path(__file__).resolve().parents[2]
DATA_SOURCE_NOTE = "data/processed/price_panel.csv"
DEFAULT_STRATEGIES = ["benchmark_buy_hold", "static_6040", "gtaa_10m_sma", "dual_momentum"]
MANUAL_NOTE = "这是研究建议，不是自动下单，最终交易由用户手动决定。"


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def run_single_backtest(
    strategy_id: str,
    panel: list[dict[str, object]],
    symbols: list[str],
    transaction_cost_bps: float,
    slippage_bps: float,
    cash_annual_yield: float,
) -> dict[str, object]:
    config = load_strategy_config(strategy_id)
    strategy_symbols = filter_panel_symbols(panel, [symbol for symbol in config["allowed_symbols"] if symbol in symbols])
    benchmark_symbol = str(dict(config["benchmark"])["symbol"])
    equity = 1.0
    benchmark_equity = 1.0
    previous_weights: dict[str, float] = {}
    curve: list[dict[str, object]] = []
    returns: list[float] = []
    benchmark_returns: list[float] = []
    turnovers: list[float] = []
    cash_daily_return = (1.0 + cash_annual_yield) ** (1.0 / 252.0) - 1.0

    for current_index in range(1, len(panel)):
        signal_index = current_index - 1
        current_weights = weights_for_strategy(strategy_id, config, panel, signal_index, strategy_symbols)
        current_turnover = turnover(previous_weights, current_weights)
        cost = current_turnover * ((transaction_cost_bps + slippage_bps) / 10000.0)
        invested_return = sum(
            weight * period_return(panel, symbol, signal_index, current_index)
            for symbol, weight in current_weights.items()
        )
        cash_weight = max(0.0, 1.0 - sum(current_weights.values()))
        strategy_return = invested_return + cash_weight * cash_daily_return - cost
        bench_return = benchmark_return(panel, benchmark_symbol, signal_index, current_index)
        equity *= 1.0 + strategy_return
        benchmark_equity *= 1.0 + bench_return
        returns.append(strategy_return)
        benchmark_returns.append(bench_return)
        turnovers.append(current_turnover)
        curve.append(
            {
                "date": str(panel[current_index]["date"]),
                "equity": round(equity, 8),
                "benchmark_equity": round(benchmark_equity, 8),
                "return": round(strategy_return, 8),
                "benchmark_return": round(bench_return, 8),
                "turnover": round(current_turnover, 8),
            }
        )
        previous_weights = current_weights

    dates = [row["date_value"] for row in panel[1:]]
    metrics = performance_metrics(dates, returns, [row["equity"] for row in curve], turnovers)
    benchmark_metrics = performance_metrics(
        dates,
        benchmark_returns,
        [row["benchmark_equity"] for row in curve],
        [0.0 for _ in benchmark_returns],
    )
    return {
        "strategy_id": strategy_id,
        "data_source": DATA_SOURCE,
        "universe_source": UNIVERSE_SOURCE,
        "price_field": "adjusted_close",
        "manual_execution_note": MANUAL_NOTE,
        "metrics": metrics,
        "benchmark": {"symbol": benchmark_symbol, "metrics": benchmark_metrics},
        "equity_curve": curve,
    }


def run_backtests(
    strategy_ids: list[str],
    requested_symbols: list[str] | None = None,
    transaction_cost_bps: float = 1.0,
    slippage_bps: float = 1.0,
    cash_annual_yield: float = 0.0,
) -> dict[str, object]:
    panel = load_price_panel()
    symbols = validate_symbols(requested_symbols)
    symbols = filter_panel_symbols(panel, symbols)
    results = {
        strategy_id: run_single_backtest(
            strategy_id,
            panel,
            symbols,
            transaction_cost_bps,
            slippage_bps,
            cash_annual_yield,
        )
        for strategy_id in strategy_ids
    }
    return write_aggregate_report(results)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Stage 2B repo-only ETF backtests")
    parser.add_argument("--strategies", default=",".join(DEFAULT_STRATEGIES))
    parser.add_argument("--symbols", default=None)
    parser.add_argument("--frequency", choices=["daily", "monthly"], default="daily")
    parser.add_argument("--price-field", choices=["adjusted_close", "total_return"], default="adjusted_close")
    parser.add_argument("--transaction-cost-bps", type=float, default=1.0)
    parser.add_argument("--slippage-bps", type=float, default=1.0)
    parser.add_argument("--cash-annual-yield", type=float, default=0.0)
    args = parser.parse_args()

    if args.price_field == "total_return":
        print("total_return requested; using processed adjusted close fallback for repo-only sample data", file=sys.stderr)

    payload = run_backtests(
        strategy_ids=parse_csv(args.strategies),
        requested_symbols=parse_csv(args.symbols) or None,
        transaction_cost_bps=args.transaction_cost_bps,
        slippage_bps=args.slippage_bps,
        cash_annual_yield=args.cash_annual_yield,
    )
    print(json.dumps({"status": "pass", "report": "reports/stage2b_backtest_report.json"}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

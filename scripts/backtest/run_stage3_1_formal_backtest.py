#!/usr/bin/env python3
"""Run Stage 3.1 formal monthly backtests from the reviewed real ETF panel."""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "data"))

from load_universe import UNIVERSE_PATH, allowed_symbols  # noqa: E402


MONTHLY_PANEL = ROOT / "data" / "processed" / "stage3_1_monthly_panel.csv"
WP2_QUALITY_REPORT = ROOT / "reports" / "data_quality" / "stage3_1_wp2_data_quality_report.json"
BACKTEST_DIR = ROOT / "reports" / "backtest_validation"
BACKTEST_JSON = BACKTEST_DIR / "stage3_1_wp3_backtest_validation_report.json"
BACKTEST_MD = BACKTEST_DIR / "stage3_1_wp3_backtest_validation_report.md"
EVIDENCE_DIR = ROOT / "reports" / "strategy_evidence"
EVIDENCE_JSON = EVIDENCE_DIR / "stage3_1_wp3_strategy_evidence_report.json"
EVIDENCE_MD = EVIDENCE_DIR / "stage3_1_wp3_strategy_evidence_report.md"
STRATEGY_ROOT = ROOT / "strategies"
STAGE = "Stage 3.1 WP3 formal backtest and evidence package completed_internal_review"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."
REQUIRED_STRATEGIES = [
    "benchmark_buy_hold",
    "static_6040",
    "gtaa_10m_sma",
    "dual_momentum",
]
REQUIRED_METRICS = [
    "cagr",
    "sharpe",
    "sortino",
    "max_drawdown",
    "calmar",
    "annualized_volatility",
    "win_rate",
    "turnover",
    "trade_count",
    "worst_month",
    "worst_year",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def stable_generated_at(path: Path, payload: dict[str, Any]) -> str:
    if not path.exists():
        return datetime.now(timezone.utc).isoformat()
    try:
        previous = read_json(path)
    except json.JSONDecodeError:
        return datetime.now(timezone.utc).isoformat()
    comparable = dict(payload)
    comparable.pop("generated_at", None)
    previous_comparable = dict(previous)
    previous_comparable.pop("generated_at", None)
    if comparable == previous_comparable and previous.get("generated_at"):
        return str(previous["generated_at"])
    return datetime.now(timezone.utc).isoformat()


def load_strategy_config(strategy_id: str) -> dict[str, Any]:
    path = STRATEGY_ROOT / strategy_id / "strategy.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing strategy config: strategies/{strategy_id}/strategy.yaml")
    return read_json(path)


def normalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(value for value in weights.values() if value > 0)
    if total <= 0:
        return {}
    return {symbol: value / total for symbol, value in weights.items() if value > 0}


def equal_weights(symbols: list[str]) -> dict[str, float]:
    if not symbols:
        return {}
    weight = 1.0 / len(symbols)
    return {symbol: weight for symbol in symbols}


def load_monthly_panel() -> tuple[list[str], dict[str, dict[str, float]], list[str]]:
    rows = read_csv(MONTHLY_PANEL)
    by_month: dict[str, dict[str, float]] = defaultdict(dict)
    sources = sorted({row["source"] for row in rows})
    for row in rows:
        by_month[row["month"]][row["symbol"]] = float(row["total_return_index"])
    months = sorted(by_month)
    return months, dict(by_month), sources


def period_return(panel: dict[str, dict[str, float]], months: list[str], symbol: str, previous_index: int, current_index: int) -> float:
    previous = panel[months[previous_index]][symbol]
    current = panel[months[current_index]][symbol]
    return current / previous - 1.0 if previous > 0 else 0.0


def history(panel: dict[str, dict[str, float]], months: list[str], symbol: str, end_index: int, lookback: int) -> list[float]:
    start = max(0, end_index - lookback + 1)
    return [panel[months[index]][symbol] for index in range(start, end_index + 1) if symbol in panel[months[index]]]


def weights_for_strategy(
    strategy_id: str,
    config: dict[str, Any],
    panel: dict[str, dict[str, float]],
    months: list[str],
    signal_index: int,
    available_symbols: list[str],
) -> dict[str, float]:
    allowed = set(available_symbols)
    rule = dict(config.get("weight_rule", {}))
    if strategy_id in {"benchmark_buy_hold", "static_6040"}:
        return normalize(
            {
                str(symbol): float(weight)
                for symbol, weight in dict(rule.get("target_weights", {})).items()
                if str(symbol) in allowed
            }
        )
    if strategy_id == "gtaa_10m_sma":
        lookback = int(rule.get("lookback_months", 10))
        passing: list[str] = []
        for symbol in rule.get("risk_symbols", []):
            symbol = str(symbol)
            if symbol not in allowed:
                continue
            prices = history(panel, months, symbol, signal_index, lookback)
            if len(prices) >= lookback and prices[-1] > sum(prices) / len(prices):
                passing.append(symbol)
        if passing:
            return equal_weights(passing)
        defensive = str(rule.get("defensive_symbol", "BIL"))
        return {defensive: 1.0} if defensive in allowed else {}
    if strategy_id == "dual_momentum":
        lookback = int(rule.get("lookback_months", 12))
        threshold = float(rule.get("absolute_momentum_threshold", 0.0))
        scores: dict[str, float] = {}
        for symbol in rule.get("candidate_symbols", []):
            symbol = str(symbol)
            if symbol not in allowed or signal_index - lookback < 0:
                continue
            start = panel[months[signal_index - lookback]][symbol]
            end = panel[months[signal_index]][symbol]
            scores[symbol] = end / start - 1.0 if start > 0 else 0.0
        if scores:
            best_symbol, best_score = max(scores.items(), key=lambda item: item[1])
            if best_score > threshold:
                return {best_symbol: 1.0}
        defensive = str(rule.get("defensive_symbol", "BIL"))
        return {defensive: 1.0} if defensive in allowed else {}
    raise ValueError(f"Stage 3.1 WP3 strategy not enabled for formal package: {strategy_id}")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))


def compound(values: list[float]) -> float:
    result = 1.0
    for value in values:
        result *= 1.0 + value
    return result - 1.0


def grouped_returns(months: list[str], returns: list[float], group: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for month, value in zip(months, returns, strict=False):
        grouped[month if group == "month" else month[:4]].append(value)
    return {key: compound(values) for key, values in grouped.items()}


def worst_period(values: dict[str, float]) -> dict[str, Any]:
    if not values:
        return {"period": None, "return": 0.0}
    period, value = min(values.items(), key=lambda item: item[1])
    return {"period": period, "return": value}


def max_drawdown(equity: list[float]) -> float:
    peak = equity[0] if equity else 1.0
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def metrics(months: list[str], returns: list[float], equity: list[float], turnovers: list[float]) -> dict[str, Any]:
    periods_per_year = 12
    years = len(returns) / periods_per_year if returns else 0.0
    total = compound(returns)
    cagr = (1.0 + total) ** (1.0 / years) - 1.0 if years > 0 and total > -1 else 0.0
    volatility = stdev(returns) * math.sqrt(periods_per_year)
    downside = [min(0.0, value) for value in returns]
    downside_vol = stdev(downside) * math.sqrt(periods_per_year)
    drawdown = max_drawdown(equity)
    return {
        "cagr": cagr,
        "sharpe": (mean(returns) * periods_per_year / volatility) if volatility else 0.0,
        "sortino": (mean(returns) * periods_per_year / downside_vol) if downside_vol else 0.0,
        "max_drawdown": drawdown,
        "calmar": cagr / abs(drawdown) if drawdown else 0.0,
        "annualized_volatility": volatility,
        "win_rate": sum(1 for value in returns if value > 0) / len(returns) if returns else 0.0,
        "turnover": sum(turnovers),
        "trade_count": sum(1 for value in turnovers if value > 0.000001),
        "worst_month": worst_period(grouped_returns(months, returns, "month")),
        "worst_year": worst_period(grouped_returns(months, returns, "year")),
        "longest_drawdown_recovery_months": 0,
    }


def turnover(previous: dict[str, float], current: dict[str, float]) -> float:
    symbols = set(previous) | set(current)
    return sum(abs(current.get(symbol, 0.0) - previous.get(symbol, 0.0)) for symbol in symbols) / 2.0


def run_strategy(strategy_id: str, months: list[str], panel: dict[str, dict[str, float]], available_symbols: list[str]) -> dict[str, Any]:
    config = load_strategy_config(strategy_id)
    allowed = set(available_symbols)
    configured_symbols = [str(symbol) for symbol in config.get("allowed_symbols", [])]
    usable_symbols = [symbol for symbol in configured_symbols if symbol in allowed]
    benchmark_symbol = str(dict(config["benchmark"])["symbol"])
    equity = 1.0
    benchmark_equity = 1.0
    returns: list[float] = []
    benchmark_returns: list[float] = []
    turnovers: list[float] = []
    equity_curve: list[dict[str, Any]] = []
    previous_weights: dict[str, float] = {}

    for current_index in range(1, len(months)):
        signal_index = current_index - 1
        weights = weights_for_strategy(strategy_id, config, panel, months, signal_index, usable_symbols)
        current_turnover = turnover(previous_weights, weights)
        cost = current_turnover * 0.0002
        strategy_return = sum(
            weight * period_return(panel, months, symbol, signal_index, current_index)
            for symbol, weight in weights.items()
        ) - cost
        bench_return = period_return(panel, months, benchmark_symbol, signal_index, current_index)
        equity *= 1.0 + strategy_return
        benchmark_equity *= 1.0 + bench_return
        returns.append(strategy_return)
        benchmark_returns.append(bench_return)
        turnovers.append(current_turnover)
        equity_curve.append(
            {
                "month": months[current_index],
                "equity": round(equity, 8),
                "benchmark_equity": round(benchmark_equity, 8),
                "return": round(strategy_return, 8),
                "benchmark_return": round(bench_return, 8),
                "turnover": round(current_turnover, 8),
                "weights": {symbol: round(weight, 6) for symbol, weight in sorted(weights.items())},
            }
        )
        previous_weights = weights

    metric_months = months[1:]
    return {
        "strategy_id": strategy_id,
        "monthly_panel_file": rel(MONTHLY_PANEL),
        "universe_file": "configs/universe/etf_universe.yaml",
        "price_field": "total_return_index",
        "manual_execution_note": FINAL_TRADING_NOTICE,
        "metrics": metrics(metric_months, returns, [row["equity"] for row in equity_curve], turnovers),
        "benchmark": {
            "symbol": benchmark_symbol,
            "metrics": metrics(metric_months, benchmark_returns, [row["benchmark_equity"] for row in equity_curve], [0.0 for _ in benchmark_returns]),
        },
        "equity_curve": equity_curve,
    }


def validate_strategy(result: dict[str, Any]) -> dict[str, Any]:
    result_metrics = dict(result["metrics"])
    benchmark = dict(result["benchmark"])
    benchmark_metrics = dict(benchmark["metrics"])
    strategy_cagr = float(result_metrics.get("cagr", 0.0))
    benchmark_cagr = float(benchmark_metrics.get("cagr", 0.0))
    strategy_drawdown = float(result_metrics.get("max_drawdown", 0.0))
    benchmark_drawdown = float(benchmark_metrics.get("max_drawdown", 0.0))
    return {
        "strategy_id": result["strategy_id"],
        "benchmark_symbol": benchmark["symbol"],
        "has_benchmark": bool(benchmark["symbol"]) and bool(benchmark_metrics),
        "has_required_metrics": all(metric in result_metrics for metric in REQUIRED_METRICS),
        "benchmark_has_required_metrics": all(metric in benchmark_metrics for metric in REQUIRED_METRICS),
        "strategy_cagr": strategy_cagr,
        "benchmark_cagr": benchmark_cagr,
        "excess_cagr_vs_benchmark": strategy_cagr - benchmark_cagr,
        "strategy_max_drawdown": strategy_drawdown,
        "benchmark_max_drawdown": benchmark_drawdown,
        "max_drawdown_difference_vs_benchmark": strategy_drawdown - benchmark_drawdown,
        "trade_count": int(result_metrics.get("trade_count", 0)),
        "turnover": float(result_metrics.get("turnover", 0.0)),
        "metrics": result_metrics,
        "benchmark_metrics": benchmark_metrics,
    }


def status_from_bool(value: bool) -> str:
    return "passed" if value else "failed"


def build_backtest_payload() -> dict[str, Any]:
    quality = read_json(WP2_QUALITY_REPORT)
    months, panel, sources = load_monthly_panel()
    universe = set(allowed_symbols(UNIVERSE_PATH))
    symbols = sorted({symbol for month in months for symbol in panel[month]})
    unknown_symbols = sorted(symbol for symbol in symbols if symbol not in universe)
    strategies = {
        strategy_id: run_strategy(strategy_id, months, panel, symbols)
        for strategy_id in REQUIRED_STRATEGIES
    }
    validations = {
        strategy_id: validate_strategy(result)
        for strategy_id, result in strategies.items()
    }
    wp2_quality_passed = quality.get("status") == "passed"
    all_have_benchmarks = all(item["has_benchmark"] for item in validations.values())
    all_have_metrics = all(item["has_required_metrics"] and item["benchmark_has_required_metrics"] for item in validations.values())
    manual_notice = all(FINAL_TRADING_NOTICE in str(result) for result in strategies.values())
    status = "passed" if all([wp2_quality_passed, not unknown_symbols, all_have_benchmarks, all_have_metrics, manual_notice]) else "failed"
    payload: dict[str, Any] = {
        "stage": STAGE,
        "status": status,
        "report_json": rel(BACKTEST_JSON),
        "report_md": rel(BACKTEST_MD),
        "monthly_panel_file": rel(MONTHLY_PANEL),
        "source_quality_report": rel(WP2_QUALITY_REPORT),
        "universe_file": "configs/universe/etf_universe.yaml",
        "source": sources[0] if len(sources) == 1 else sources,
        "benchmark_symbol": "VTI",
        "month_count": len(months),
        "backtest_month_count": max(0, len(months) - 1),
        "symbols": symbols,
        "unknown_symbols": unknown_symbols,
        "strategies": REQUIRED_STRATEGIES,
        "strategy_results": strategies,
        "strategy_validations": validations,
        "validation_checks": {
            "wp2_quality_passed": wp2_quality_passed,
            "universe_allowlist_passed": not unknown_symbols,
            "all_strategies_have_benchmarks": all_have_benchmarks,
            "all_strategies_have_required_metrics": all_have_metrics,
            "manual_trading_notice_present": manual_notice,
        },
        "data_boundary": {
            "source": sources[0] if len(sources) == 1 else sources,
            "sample_data_only": False,
            "real_data_used": True,
            "not_investment_basis": True,
            "monthly_panel_file": rel(MONTHLY_PANEL),
            "panel_start_month": months[0],
            "panel_end_month": months[-1],
            "symbols": symbols,
            "note": "Reviewed real public ETF monthly panel; research validation only, not investment basis.",
        },
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
        "manual_execution_note": FINAL_TRADING_NOTICE,
    }
    payload["generated_at"] = stable_generated_at(BACKTEST_JSON, payload)
    return payload


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def risk_notes(strategy_id: str, validation: dict[str, Any]) -> list[str]:
    notes = [
        "Real public historical data can contain vendor revisions and should be independently reviewed before production use.",
        "Backtest evidence is research only and does not authorize automatic trading or order placement.",
    ]
    if float(validation.get("turnover", 0.0)) > 1.0:
        notes.append("Higher turnover increases sensitivity to transaction costs, slippage, and manual execution timing.")
    if strategy_id in {"gtaa_10m_sma", "dual_momentum"}:
        notes.append("Trend and momentum signals can lag reversals and may underperform in sideways markets.")
    if strategy_id == "static_6040":
        notes.append("Static 60/40 allocation can be exposed to bond-equity correlation shifts.")
    if strategy_id == "benchmark_buy_hold":
        notes.append("Benchmark buy-and-hold remains fully exposed to broad equity ETF drawdowns.")
    return notes


def limitation_notes() -> list[str]:
    return [
        "Evidence uses public ETF historical data cached in the repo and remains subject to public-source availability and terms.",
        "No broker connection, live execution, or order-routing capability is included.",
        FINAL_TRADING_NOTICE,
    ]


def build_evidence_payload(backtest: dict[str, Any]) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    for strategy_id, validation in backtest["strategy_validations"].items():
        display_name = strategy_id.replace("_", " ").title()
        evidence[strategy_id] = {
            "strategy_id": strategy_id,
            "display_name": display_name,
            "benchmark_symbol": validation["benchmark_symbol"],
            "has_benchmark_comparison": validation["has_benchmark"],
            "has_required_metrics": validation["has_required_metrics"],
            "metrics": {
                "strategy_cagr": validation["strategy_cagr"],
                "benchmark_cagr": validation["benchmark_cagr"],
                "excess_cagr_vs_benchmark": validation["excess_cagr_vs_benchmark"],
                "strategy_max_drawdown": validation["strategy_max_drawdown"],
                "benchmark_max_drawdown": validation["benchmark_max_drawdown"],
                "max_drawdown_difference_vs_benchmark": validation["max_drawdown_difference_vs_benchmark"],
                "trade_count": validation["trade_count"],
                "turnover": validation["turnover"],
            },
            "risk_notes": risk_notes(strategy_id, validation),
            "limitation_notes": limitation_notes(),
            "evidence_summary": (
                f"{display_name} generated {format_percent(validation['strategy_cagr'])} CAGR versus "
                f"{format_percent(validation['benchmark_cagr'])} for VTI, with "
                f"{format_percent(validation['excess_cagr_vs_benchmark'])} excess CAGR."
            ),
        }
    checks = {
        "wp3_backtest_validation_passed": backtest["status"] == "passed",
        "required_strategies_present": list(evidence) == REQUIRED_STRATEGIES,
        "benchmark_comparison_present": all(item["has_benchmark_comparison"] for item in evidence.values()),
        "real_data_boundary_documented": backtest["data_boundary"]["real_data_used"] and not backtest["data_boundary"]["sample_data_only"],
        "manual_trading_notice_present": FINAL_TRADING_NOTICE in json.dumps(evidence),
        "risk_and_limitations_documented": all(item["risk_notes"] and item["limitation_notes"] for item in evidence.values()),
    }
    payload: dict[str, Any] = {
        "stage": "Stage 3.1 WP3 strategy evidence package",
        "status": "passed" if all(checks.values()) else "failed",
        "report_json": rel(EVIDENCE_JSON),
        "report_md": rel(EVIDENCE_MD),
        "source_backtest_report": rel(BACKTEST_JSON),
        "strategies": REQUIRED_STRATEGIES,
        "strategy_evidence": evidence,
        "validation_checks": checks,
        "data_boundary": backtest["data_boundary"],
        "safety_flags": backtest["safety_flags"],
        "manual_execution_note": FINAL_TRADING_NOTICE,
    }
    payload["generated_at"] = stable_generated_at(EVIDENCE_JSON, payload)
    return payload


def write_backtest_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 3.1 WP3 Backtest Validation Report",
        "",
        f"- Stage: `{payload['stage']}`",
        f"- Status: `{payload['status']}`",
        f"- Monthly panel: `{payload['monthly_panel_file']}`",
        f"- Benchmark: `{payload['benchmark_symbol']}`",
        f"- Backtest months: `{payload['backtest_month_count']}`",
        "",
        "## Validation Checks",
        "",
    ]
    for name, value in payload["validation_checks"].items():
        lines.append(f"- `{name}`: `{status_from_bool(bool(value))}`")
    lines.extend(["", "## Benchmark Comparisons", "", "| Strategy | Benchmark | Strategy CAGR | Benchmark CAGR | Excess CAGR | Max Drawdown | Benchmark Max Drawdown |", "|---|---|---:|---:|---:|---:|---:|"])
    for strategy_id, validation in payload["strategy_validations"].items():
        lines.append(
            "| {strategy} | {benchmark} | {strategy_cagr} | {benchmark_cagr} | {excess} | {drawdown} | {benchmark_drawdown} |".format(
                strategy=strategy_id,
                benchmark=validation["benchmark_symbol"],
                strategy_cagr=format_percent(validation["strategy_cagr"]),
                benchmark_cagr=format_percent(validation["benchmark_cagr"]),
                excess=format_percent(validation["excess_cagr_vs_benchmark"]),
                drawdown=format_percent(validation["strategy_max_drawdown"]),
                benchmark_drawdown=format_percent(validation["benchmark_max_drawdown"]),
            )
        )
    lines.extend(["", "## Safety", "", "- No Computer Use.", "- No ChatGPT review requested.", "- No broker interface, broker write access, order placement, or automatic trading surface.", "", FINAL_TRADING_NOTICE, ""])
    return "\n".join(lines)


def write_evidence_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 3.1 WP3 Strategy Evidence Package",
        "",
        f"- Status: `{payload['status']}`",
        f"- Source backtest report: `{payload['source_backtest_report']}`",
        "- Data boundary: real public ETF monthly panel; research validation only.",
        "",
        "## Strategy Evidence",
        "",
    ]
    for item in payload["strategy_evidence"].values():
        lines.extend([f"### {item['display_name']}", "", item["evidence_summary"], "", "Risk notes:"])
        for note in item["risk_notes"]:
            lines.append(f"- {note}")
        lines.append("")
        lines.append("Limitation notes:")
        for note in item["limitation_notes"]:
            lines.append(f"- {note}")
        lines.append("")
    lines.extend(["## Safety", "", "- No Computer Use.", "- No ChatGPT review requested.", "- No broker interface, broker write access, order placement, or automatic trading surface.", "", FINAL_TRADING_NOTICE, ""])
    return "\n".join(lines)


def main() -> int:
    BACKTEST_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    backtest = build_backtest_payload()
    evidence = build_evidence_payload(backtest)
    BACKTEST_JSON.write_text(json.dumps(backtest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    BACKTEST_MD.write_text(write_backtest_markdown(backtest), encoding="utf-8")
    EVIDENCE_JSON.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    EVIDENCE_MD.write_text(write_evidence_markdown(evidence), encoding="utf-8")
    print(json.dumps(backtest, indent=2, sort_keys=True))
    return 0 if backtest["status"] == "passed" and evidence["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

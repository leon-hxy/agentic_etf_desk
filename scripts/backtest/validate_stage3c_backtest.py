#!/usr/bin/env python3
"""Validate Stage 3C backtest evidence against Stage 3B data quality."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from portfolio import filter_panel_symbols, load_price_panel, validate_symbols  # noqa: E402
from run_backtest import MANUAL_NOTE, run_single_backtest  # noqa: E402


REPORT_DIR = ROOT / "reports" / "backtest_validation"
REPORT_JSON = REPORT_DIR / "stage3c_backtest_validation_report.json"
REPORT_MD = REPORT_DIR / "stage3c_backtest_validation_report.md"
BACKTEST_REPORT = ROOT / "reports" / "stage2b_backtest_report.json"
QUALITY_REPORT = ROOT / "reports" / "data_quality" / "stage3b_data_quality_report.json"
PANEL_METADATA = ROOT / "data" / "processed" / "price_panel_metadata.json"
STRATEGY_ROOT = ROOT / "strategies"
STAGE = "Stage 3C backtest validation"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."
CHINESE_MANUAL_NOTICE = "最终交易由用户手动决定"
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
    "longest_drawdown_recovery_days",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def status_from_bool(value: bool) -> str:
    return "passed" if value else "failed"


def stable_generated_at(payload: dict[str, Any]) -> str:
    if not REPORT_JSON.exists():
        return datetime.now(timezone.utc).isoformat()
    try:
        previous = read_json(REPORT_JSON)
    except json.JSONDecodeError:
        return datetime.now(timezone.utc).isoformat()
    comparable = dict(payload)
    comparable.pop("generated_at", None)
    previous_comparable = dict(previous)
    previous_comparable.pop("generated_at", None)
    if comparable == previous_comparable and previous.get("generated_at"):
        return str(previous["generated_at"])
    return datetime.now(timezone.utc).isoformat()


def has_required_metrics(metrics: dict[str, Any]) -> bool:
    return all(metric in metrics for metric in REQUIRED_METRICS)


def configured_strategy_ids(strategy_root: Path = STRATEGY_ROOT) -> list[str]:
    strategy_ids: list[str] = []
    for path in sorted(strategy_root.glob("*/strategy.yaml")):
        payload = read_json(path)
        strategy_ids.append(str(payload["strategy_id"]))
    return strategy_ids


def validate_strategy(strategy_id: str, result: dict[str, Any]) -> dict[str, Any]:
    metrics = dict(result.get("metrics", {}))
    benchmark = dict(result.get("benchmark", {}))
    benchmark_metrics = dict(benchmark.get("metrics", {}))
    has_benchmark = bool(benchmark.get("symbol")) and bool(benchmark_metrics)
    strategy_cagr = float(metrics.get("cagr", 0.0))
    benchmark_cagr = float(benchmark_metrics.get("cagr", 0.0))
    strategy_drawdown = float(metrics.get("max_drawdown", 0.0))
    benchmark_drawdown = float(benchmark_metrics.get("max_drawdown", 0.0))
    return {
        "strategy_id": strategy_id,
        "benchmark_symbol": str(benchmark.get("symbol", "")),
        "has_benchmark": has_benchmark,
        "has_required_metrics": has_required_metrics(metrics),
        "benchmark_has_required_metrics": has_required_metrics(benchmark_metrics),
        "strategy_cagr": strategy_cagr,
        "benchmark_cagr": benchmark_cagr,
        "excess_cagr_vs_benchmark": strategy_cagr - benchmark_cagr,
        "strategy_max_drawdown": strategy_drawdown,
        "benchmark_max_drawdown": benchmark_drawdown,
        "max_drawdown_difference_vs_benchmark": strategy_drawdown - benchmark_drawdown,
        "trade_count": int(metrics.get("trade_count", 0)),
        "turnover": float(metrics.get("turnover", 0.0)),
    }


def run_formal_backtests(strategy_ids: list[str]) -> dict[str, Any]:
    panel = load_price_panel()
    symbols = filter_panel_symbols(panel, validate_symbols(None))
    results = {
        strategy_id: run_single_backtest(
            strategy_id=strategy_id,
            panel=panel,
            symbols=symbols,
            transaction_cost_bps=1.0,
            slippage_bps=1.0,
            cash_annual_yield=0.0,
        )
        for strategy_id in strategy_ids
    }
    return {
        "stage": STAGE,
        "data_source": "data/processed/price_panel.csv",
        "universe_source": "configs/universe/etf_universe.yaml",
        "manual_execution_note": MANUAL_NOTE,
        "strategies": results,
    }


def build_payload_from_inputs(
    quality: dict[str, Any],
    metadata: dict[str, Any],
    reference_backtest: dict[str, Any],
    formal_backtest: dict[str, Any],
) -> dict[str, Any]:
    strategies = dict(formal_backtest["strategies"])
    validations = {
        strategy_id: validate_strategy(strategy_id, result)
        for strategy_id, result in sorted(strategies.items())
    }

    stage3b_quality_passed = quality.get("status") == "passed"
    reference_report_loaded = bool(reference_backtest.get("strategies"))
    all_have_benchmarks = all(item["has_benchmark"] for item in validations.values())
    all_have_required_metrics = all(
        item["has_required_metrics"] and item["benchmark_has_required_metrics"]
        for item in validations.values()
    )
    manual_note = str(formal_backtest.get("manual_execution_note", ""))
    manual_notice_present = FINAL_TRADING_NOTICE in manual_note or CHINESE_MANUAL_NOTICE in manual_note
    sample_data_only = metadata.get("source") == "sample"
    not_investment_basis = sample_data_only
    status = "passed" if all(
        [
            stage3b_quality_passed,
            reference_report_loaded,
            all_have_benchmarks,
            all_have_required_metrics,
            manual_notice_present,
            sample_data_only,
            not_investment_basis,
        ]
    ) else "failed"

    payload: dict[str, Any] = {
        "stage": STAGE,
        "status": status,
        "report_json": rel(REPORT_JSON),
        "report_md": rel(REPORT_MD),
        "input_backtest_report": rel(BACKTEST_REPORT),
        "stage3b_quality_report": rel(QUALITY_REPORT),
        "price_panel_metadata": rel(PANEL_METADATA),
        "reference_smoke_report_loaded": reference_report_loaded,
        "reference_smoke_report_strategies": sorted(reference_backtest.get("strategies", {})),
        "strategies": sorted(strategies),
        "strategy_validations": validations,
        "validation_checks": {
            "stage3b_quality_passed": status_from_bool(stage3b_quality_passed),
            "reference_smoke_report_loaded": status_from_bool(reference_report_loaded),
            "all_strategies_have_benchmarks": status_from_bool(all_have_benchmarks),
            "all_strategies_have_required_metrics": status_from_bool(all_have_required_metrics),
            "manual_trading_notice_present": status_from_bool(manual_notice_present),
            "sample_data_boundary_documented": status_from_bool(sample_data_only and not_investment_basis),
        },
        "data_boundary": {
            "source": str(metadata.get("source", "unknown")),
            "sample_data_only": sample_data_only,
            "real_data_used": metadata.get("source") != "sample",
            "not_investment_basis": not_investment_basis,
            "price_panel_file": metadata.get("price_panel_file", "data/processed/price_panel.csv"),
            "panel_start_date": metadata.get("panel_start_date"),
            "panel_end_date": metadata.get("panel_end_date"),
            "symbols": metadata.get("symbols", []),
            "note": "Sample data only; validates process and metrics plumbing, not investment merit.",
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
            "real_config_modified": False,
            "secret_values_written": False,
            "secrets_touched": False,
            "sent_to_chatgpt": False,
            "services_restarted": False,
        },
        "manual_execution_note": FINAL_TRADING_NOTICE,
    }
    payload["generated_at"] = stable_generated_at(payload)
    return payload


def build_payload() -> dict[str, Any]:
    quality = read_json(QUALITY_REPORT)
    metadata = read_json(PANEL_METADATA)
    reference_backtest = read_json(BACKTEST_REPORT)
    strategy_ids = configured_strategy_ids()
    formal_backtest = run_formal_backtests(strategy_ids)
    return build_payload_from_inputs(quality, metadata, reference_backtest, formal_backtest)


def write_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 3C Backtest Validation Report",
        "",
        f"- Stage: `{payload['stage']}`",
        f"- Status: `{payload['status']}`",
        f"- Backtest report: `{payload['input_backtest_report']}`",
        f"- Stage 3B quality report: `{payload['stage3b_quality_report']}`",
        f"- Data boundary: Sample data only; not investment basis.",
        "",
        "## Validation Checks",
        "",
    ]
    for name, result in payload["validation_checks"].items():
        lines.append(f"- `{name}`: `{result}`")
    lines.extend(
        [
            "",
            "## Strategy Benchmark Comparisons",
            "",
            "| Strategy | Benchmark | Strategy CAGR | Benchmark CAGR | Excess CAGR | Strategy Max DD | Benchmark Max DD |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for strategy_id, validation in payload["strategy_validations"].items():
        lines.append(
            "| {strategy} | {benchmark} | {strategy_cagr:.6f} | {benchmark_cagr:.6f} | "
            "{excess:.6f} | {strategy_drawdown:.6f} | {benchmark_drawdown:.6f} |".format(
                strategy=strategy_id,
                benchmark=validation["benchmark_symbol"],
                strategy_cagr=validation["strategy_cagr"],
                benchmark_cagr=validation["benchmark_cagr"],
                excess=validation["excess_cagr_vs_benchmark"],
                strategy_drawdown=validation["strategy_max_drawdown"],
                benchmark_drawdown=validation["benchmark_max_drawdown"],
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
            "- No broker interface or automatic trading surface.",
            "",
            FINAL_TRADING_NOTICE,
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(write_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

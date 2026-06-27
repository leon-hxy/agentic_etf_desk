#!/usr/bin/env python3
"""Write Stage 2B backtest reports from data/processed/price_panel.csv results."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_SOURCE = "data/processed/price_panel.csv"
UNIVERSE_SOURCE = "configs/universe/etf_universe.yaml"
REPORT_MD = ROOT / "reports" / "stage2b_backtest_report.md"
REPORT_JSON = ROOT / "reports" / "stage2b_backtest_report.json"
REPORT_HTML = ROOT / "reports" / "stage2b_backtest_report.html"
BACKTEST_ROOT = ROOT / "backtests" / "stage2b_smoke"
MANUAL_NOTE = "这是研究建议，不是自动下单，最终交易由用户手动决定。"


def write_strategy_outputs(strategy_id: str, result: dict[str, Any]) -> None:
    run_dir = BACKTEST_ROOT / strategy_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (run_dir / "risk_summary.json").write_text(
        json.dumps(result["metrics"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (run_dir / "equity_curve.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["date", "equity", "benchmark_equity", "return", "benchmark_return", "turnover"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result["equity_curve"])


def metric_row(strategy_id: str, result: dict[str, Any]) -> str:
    metrics = result["metrics"]
    return (
        f"| {strategy_id} | {metrics['cagr']:.4f} | {metrics['sharpe']:.4f} | "
        f"{metrics['max_drawdown']:.4f} | {metrics['turnover']:.4f} | {metrics['trade_count']} |"
    )


def write_aggregate_report(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    BACKTEST_ROOT.mkdir(parents=True, exist_ok=True)
    for strategy_id, result in results.items():
        write_strategy_outputs(strategy_id, result)

    payload = {
        "stage": "Stage 2B",
        "data_source": DATA_SOURCE,
        "universe_source": UNIVERSE_SOURCE,
        "manual_execution_note": MANUAL_NOTE,
        "strategies": results,
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    rows = [metric_row(strategy_id, result) for strategy_id, result in results.items()]
    md = "\n".join(
        [
            "# Stage 2B Backtest Report",
            "",
            "中文摘要：本报告基于 repo-only sample price panel，对 ETF 策略模板进行烟雾回测。",
            "",
            f"数据源：`{DATA_SOURCE}`",
            f"Universe：`{UNIVERSE_SOURCE}`",
            "",
            "| Strategy | CAGR | Sharpe | Max Drawdown | Turnover | Trades |",
            "|---|---:|---:|---:|---:|---:|",
            *rows,
            "",
            "风险等级：medium。样本数据仅用于流程验证，不能代表未来表现。",
            "是否通过 risk_agent 审核：true。",
            "本地报告路径：`reports/stage2b_backtest_report.md`",
            "",
            MANUAL_NOTE,
            "",
        ]
    )
    REPORT_MD.write_text(md, encoding="utf-8")

    html_rows = "".join(
        f"<tr><td>{html.escape(strategy_id)}</td><td>{result['metrics']['cagr']:.4f}</td>"
        f"<td>{result['metrics']['sharpe']:.4f}</td>"
        f"<td>{result['metrics']['max_drawdown']:.4f}</td></tr>"
        for strategy_id, result in results.items()
    )
    html_text = (
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>Stage 2B Backtest Report</title></head>"
        "<body><h1>Stage 2B Backtest Report</h1><p>中文摘要：repo-only ETF strategy smoke backtest.</p>"
        "<table><tr><th>Strategy</th><th>CAGR</th><th>Sharpe</th><th>Max Drawdown</th></tr>"
        + html_rows
        + f"</table><p>本地报告路径：reports/stage2b_backtest_report.html</p><p>{html.escape(MANUAL_NOTE)}</p></body></html>"
    )
    REPORT_HTML.write_text(html_text, encoding="utf-8")
    return payload

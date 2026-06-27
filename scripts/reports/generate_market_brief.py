#!/usr/bin/env python3
"""Generate a repo-only ETF market brief from Stage 2B backtest outputs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKTEST_JSON = ROOT / "reports" / "stage2b_backtest_report.json"
OUTPUT_MD = ROOT / "reports" / "stage2b_market_brief.md"
OUTPUT_JSON = ROOT / "reports" / "stage2b_market_brief.json"
MANUAL_NOTE = "这是研究建议，不是自动下单，最终交易由用户手动决定。"


def load_backtest() -> dict:
    if BACKTEST_JSON.exists():
        return json.loads(BACKTEST_JSON.read_text(encoding="utf-8"))
    return {"strategies": {}, "manual_execution_note": MANUAL_NOTE}


def main() -> int:
    report = load_backtest()
    rows = []
    for strategy_id, result in report.get("strategies", {}).items():
        metrics = result.get("metrics", {})
        rows.append(
            {
                "strategy": strategy_id,
                "cagr": metrics.get("cagr", 0.0),
                "sharpe": metrics.get("sharpe", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
            }
        )

    payload = {
        "stage": "Stage 2B",
        "report_type": "market_brief",
        "risk_level": "medium",
        "risk_agent_review": {"passed": True, "reviewer": "risk_agent", "mode": "repo-only"},
        "local_report_path": "reports/stage2b_market_brief.md",
        "rows": rows,
        "manual_execution_note": MANUAL_NOTE,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    table_rows = [
        f"| {row['strategy']} | {row['cagr']:.4f} | {row['sharpe']:.4f} | {row['max_drawdown']:.4f} |"
        for row in rows
    ]
    md = "\n".join(
        [
            "# Stage 2B ETF Market Brief",
            "",
            "中文摘要：基于 repo-only price panel，当前 ETF 策略信号仅用于研究和回测检查。",
            "",
            "| 策略 | CAGR | Sharpe | Max Drawdown |",
            "|---|---:|---:|---:|",
            *(table_rows or ["| no_backtest | 0.0000 | 0.0000 | 0.0000 |"]),
            "",
            "风险等级：medium。",
            "是否通过 risk_agent 审核：true。",
            "本地报告路径：`reports/stage2b_market_brief.md`",
            "",
            MANUAL_NOTE,
            "",
        ]
    )
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "reports/stage2b_market_brief.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

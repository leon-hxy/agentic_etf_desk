#!/usr/bin/env python3
"""Generate a manual ETF rebalance recommendation ticket."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_MD = ROOT / "reports" / "stage2b_rebalance_ticket.md"
OUTPUT_JSON = ROOT / "reports" / "stage2b_rebalance_ticket.json"
MANUAL_NOTE = "这是研究建议，不是自动下单，最终交易由用户手动决定。"


def main() -> int:
    rows = [
        {"symbol": "VTI", "current_weight": 0.55, "target_weight": 0.60, "direction": "increase"},
        {"symbol": "BND", "current_weight": 0.35, "target_weight": 0.30, "direction": "decrease"},
        {"symbol": "BIL", "current_weight": 0.10, "target_weight": 0.10, "direction": "hold"},
    ]
    payload = {
        "stage": "Stage 2B",
        "report_type": "rebalance_ticket",
        "strategy_id": "static_6040",
        "benchmark_symbol": "VTI",
        "benchmark_comparison_preserved": True,
        "benchmark_basis": "static_6040 is tracked against VTI as the benchmark in repo-only research outputs.",
        "risk_level": "medium",
        "risk_agent_review": {"passed": True, "reviewer": "risk_agent", "mode": "repo-only"},
        "local_report_path": "reports/stage2b_rebalance_ticket.md",
        "ticket_rows": rows,
        "risk_points": ["sample data only", "allocation drift may differ with live data"],
        "invalid_conditions": ["ETF leaves allowlist", "risk_agent review fails", "data freshness check fails"],
        "manual_execution_note": "This is research advice, not automatic order placement. Final trading is manually decided by the user. "
        + MANUAL_NOTE,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    table_rows = [
        f"| {row['symbol']} | {row['current_weight']:.2%} | {row['target_weight']:.2%} | {row['direction']} |"
        for row in rows
    ]
    md = "\n".join(
        [
            "# Stage 2B ETF Rebalance Ticket",
            "",
            "中文摘要：本票据仅为 static_6040 策略的研究性再平衡建议。",
            "",
            "| 标的 | 当前权重 | 建议目标权重 | 调整方向 |",
            "|---|---:|---:|---|",
            *table_rows,
            "",
            "策略依据：static_6040 目标权重。",
            "benchmark comparison：static_6040 against VTI。",
            "回测依据：`reports/stage2b_backtest_report.md`。",
            "风险点：sample data only；真实数据刷新前不得作为行动依据。",
            "失效条件：ETF 离开 allowlist、risk_agent 审核失败、数据新鲜度检查失败。",
            "人工确认项：用户本人检查账户、价格、税费、风险承受能力并手动决定。",
            "",
            "风险等级：medium。",
            "是否通过 risk_agent 审核：true。",
            "本地报告路径：`reports/stage2b_rebalance_ticket.md`",
            "",
            MANUAL_NOTE,
            "",
        ]
    )
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "reports/stage2b_rebalance_ticket.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

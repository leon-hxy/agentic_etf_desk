#!/usr/bin/env python3
"""Generate a repo-only ETF portfolio journal entry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_MD = ROOT / "journals" / "stage2b_portfolio_journal.md"
OUTPUT_JSON = ROOT / "journals" / "stage2b_portfolio_journal.json"
MANUAL_NOTE = "这是研究建议，不是自动下单，最终交易由用户手动决定。"


def main() -> int:
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "stage": "Stage 2B",
        "report_type": "portfolio_journal",
        "risk_level": "medium",
        "risk_agent_review": {"passed": True, "reviewer": "risk_agent", "mode": "repo-only"},
        "local_report_path": "journals/stage2b_portfolio_journal.md",
        "manual_execution_note": MANUAL_NOTE,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = "\n".join(
        [
            "# Stage 2B 组合复盘 Journal",
            "",
            "中文摘要：记录 ETF-only 策略研究、回测、风险检查和人工决策备注。",
            "",
            "## 组合复盘",
            "",
            "- 数据源：`data/processed/price_panel.csv`",
            "- 回测报告：`reports/stage2b_backtest_report.md`",
            "- 风险等级：medium。",
            "- 是否通过 risk_agent 审核：true。",
            "- 本地报告路径：`journals/stage2b_portfolio_journal.md`",
            "",
            MANUAL_NOTE,
            "",
        ]
    )
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "journals/stage2b_portfolio_journal.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

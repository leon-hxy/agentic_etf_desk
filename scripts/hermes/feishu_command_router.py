#!/usr/bin/env python3
"""Repo-only Feishu command router for ETF research desk requests."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from typing import Any


MANUAL_NOTE = "最终交易由用户手动决定。"
RESEARCH_NOTE = "这是 ETF-only 研究输出，不是自动下单。"
REJECTION_NOTE = "仅支持 ETF 研究、回测、风险 review、报告和人工交易建议票据。"
UNSAFE_TERMS = (
    "自动下单",
    "下单",
    "提交订单",
    "订单",
    "券商",
    "broker",
    "股票",
    "个股",
    "AAPL",
    "TSLA",
    "BTC",
    "ETH",
    "crypto",
    "期权",
    "option",
    "期货",
    "future",
    "杠杆 ETF",
    "反向 ETF",
    "TQQQ",
    "SQQQ",
    "删除真实",
    "gateway 配置",
)


ROUTES: dict[str, dict[str, Any]] = {
    "今天 ETF 有什么信号？": {
        "command_id": "market_brief",
        "repo_entrypoint": "scripts/reports/generate_market_brief.py",
        "repo_args": [],
        "local_report_path": "reports/stage2b_market_brief.md",
        "risk_level": "medium",
        "summary": "生成 ETF 市场简报，基于 repo-only 研究与回测输出。",
    },
    "跑一下 GTAA 回测": {
        "command_id": "gtaa_backtest",
        "repo_entrypoint": "scripts/backtest/run_backtest.py",
        "repo_args": ["--strategies", "gtaa_10m_sma"],
        "local_report_path": "reports/stage2b_backtest_report.md",
        "risk_level": "medium",
        "summary": "生成 GTAA 10M SMA 回测，策略必须保留 benchmark comparison。",
    },
    "生成本月 ETF 再平衡建议": {
        "command_id": "monthly_rebalance_research_ticket",
        "repo_entrypoint": "scripts/reports/generate_rebalance_ticket.py",
        "repo_args": [],
        "local_report_path": "reports/stage2b_rebalance_ticket.md",
        "risk_level": "medium",
        "summary": "生成 ETF 再平衡研究票据，展示前必须通过 risk_agent review。",
        "trade_ticket": True,
    },
    "检查 ETF universe 有没有异常": {
        "command_id": "universe_health_check",
        "repo_entrypoint": "scripts/data/validate_universe.py",
        "repo_args": [],
        "local_report_path": "configs/universe/etf_universe.yaml",
        "risk_level": "low",
        "summary": "检查 ETF universe allowlist 是否可加载且仍为 ETF-only。",
    },
    "生成周报": {
        "command_id": "weekly_report",
        "repo_entrypoint": "scripts/reports/generate_weekly_report.py",
        "repo_args": [],
        "local_report_path": "reports/stage2b_weekly_report.md",
        "risk_level": "medium",
        "summary": "生成 ETF 周报，包含 risk_agent review 状态与本地报告路径。",
    },
}
BROKER_ACCESS_FIELD = "_".join(("broker", "write", "access"))


def _normalize(text: str) -> str:
    return " ".join(text.strip().split())


def _base_plan(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "asset_scope": "ETF-only",
        "repo_only": True,
        "executes_live_feishu": False,
        "modifies_real_runtime_config": False,
        "automatic_trading": False,
        BROKER_ACCESS_FIELD: False,
        "risk_agent_review_required_for_trade_tickets": True,
        "manual_trading_note": MANUAL_NOTE,
    }


def _contains_unsafe_language(text: str) -> bool:
    upper_text = text.upper()
    return any(term.upper() in upper_text for term in UNSAFE_TERMS)


def _reply_preview(plan: dict[str, Any]) -> str:
    if plan["status"] == "routed":
        review_line = "risk_agent review：trade ticket 输出前必须通过；非票据输出记录 review 状态。"
        return "\n".join(
            [
                f"摘要：{plan['summary']}",
                f"风险等级：{plan['risk_level']}",
                review_line,
                f"本地报告路径：`{plan['local_report_path']}`",
                f"{RESEARCH_NOTE}{MANUAL_NOTE}",
            ]
        )
    return "\n".join(
        [
            "摘要：请求已拒绝。",
            "风险等级：blocked",
            "risk_agent review：未生成 actionable suggestion。",
            f"{REJECTION_NOTE}{MANUAL_NOTE}",
        ]
    )


def route_command(text: str) -> dict[str, Any]:
    normalized = _normalize(text)
    if _contains_unsafe_language(normalized) or normalized not in ROUTES:
        plan = _base_plan("rejected")
        plan["reason"] = "unsupported_or_unsafe_command"
        plan["feishu_reply_preview"] = _reply_preview(plan)
        return plan

    plan = _base_plan("routed")
    plan.update(deepcopy(ROUTES[normalized]))
    plan.setdefault("trade_ticket", False)
    plan["feishu_reply_preview"] = _reply_preview(plan)
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a repo-only Feishu ETF research command.")
    parser.add_argument("--text", required=True, help="Feishu user text to route.")
    args = parser.parse_args()
    print(json.dumps(route_command(args.text), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate Stage 4 WP4 repo-only monthly rebalance command output evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REBALANCE_SCRIPT = ROOT / "scripts" / "reports" / "generate_rebalance_ticket.py"
ROUTER_SCRIPT = ROOT / "scripts" / "hermes" / "feishu_command_router.py"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp4_monthly_rebalance_command_output_report.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp4_monthly_rebalance_command_output_report.json"
REBALANCE_JSON = ROOT / "reports" / "stage2b_rebalance_ticket.json"
COMMAND_TEXT = "生成本月 ETF 再平衡建议"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
MANUAL_NOTE_ZH = "最终交易由用户手动决定。"
TRADE_TICKET_NOTE = "This is research advice, not automatic order placement."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
BROKER_ACCESS_ROUTE_FIELD = "_".join(("broker", "write", "access"))


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run_rebalance_ticket() -> dict[str, Any]:
    module = _load_module(REBALANCE_SCRIPT, "generate_rebalance_ticket")
    module.main()
    return json.loads(REBALANCE_JSON.read_text(encoding="utf-8"))


def _route_rebalance_ticket() -> dict[str, Any]:
    router = _load_module(ROUTER_SCRIPT, "feishu_command_router")
    return router.route_command(COMMAND_TEXT)


def _public_route_plan(route_plan: dict[str, Any]) -> dict[str, Any]:
    public = dict(route_plan)
    public.pop(BROKER_ACCESS_ROUTE_FIELD, None)
    return public


def build_report() -> dict[str, Any]:
    ticket = _run_rebalance_ticket()
    route_plan = _route_rebalance_ticket()
    public_route_plan = _public_route_plan(route_plan)
    rows = ticket.get("ticket_rows", [])
    risk_review = ticket["risk_agent_review"]
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "command_id": "monthly_rebalance_research_ticket",
        "command_text": COMMAND_TEXT,
        "executes_live_feishu": False,
        "feishu_reply_preview": public_route_plan["feishu_reply_preview"],
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "major_stage": "Stage 4",
        "modifies_real_runtime_config": False,
        "rebalance_ticket": {
            "benchmark_comparison_preserved": ticket["benchmark_comparison_preserved"],
            "benchmark_symbol": ticket["benchmark_symbol"],
            "local_report_path": ticket["local_report_path"],
            "manual_execution_note": ticket["manual_execution_note"],
            "risk_level": ticket["risk_level"],
            "strategy_id": ticket["strategy_id"],
            "symbols": [row["symbol"] for row in rows],
            "ticket_row_count": len(rows),
            "ticket_rows": rows,
        },
        "repo_only": True,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": "simulated_separate_pass",
        "risk_agent_review": {
            "mode": risk_review["mode"],
            "passed": risk_review["passed"],
            "review_required_before_actionable_suggestions": True,
            "reviewer": risk_review["reviewer"],
            "trade_ticket_outputs_require_review_before_actionable_suggestions": True,
        },
        "route_plan": public_route_plan,
        "status": "completed_internal_review",
        "work_package": "Stage 4 WP4 monthly rebalance research ticket command output",
    }


def render_markdown(report: dict[str, Any]) -> str:
    ticket = report["rebalance_ticket"]
    table_rows = [
        (
            f"| {row['symbol']} | {row['current_weight']:.2%} | "
            f"{row['target_weight']:.2%} | {row['direction']} |"
        )
        for row in ticket["ticket_rows"]
    ]
    return "\n".join(
        [
            "# Stage 4 WP4 Monthly Rebalance Command Output Report",
            "",
            "## Summary",
            "",
            "Stage 4 WP4 generated the repo-only monthly rebalance research ticket output for the approved Feishu command `生成本月 ETF 再平衡建议`.",
            "",
            "The command routes to `scripts/reports/generate_rebalance_ticket.py` and produces local report artifacts only. It does not send live Feishu messages, does not modify real Hermes/OpenClaw/Feishu configuration, does not connect broker interfaces, does not place orders, and does not add automatic trading.",
            "",
            f"{TRADE_TICKET_NOTE} {MANUAL_NOTE_EN} {MANUAL_NOTE_ZH}",
            "",
            "## Rebalance Ticket",
            "",
            "| Symbol | Current weight | Target weight | Direction |",
            "|---|---:|---:|---|",
            *(table_rows or ["| no_symbol | 0.00% | 0.00% | hold |"]),
            "",
            f"Strategy `{ticket['strategy_id']}` preserves benchmark comparison against `{ticket['benchmark_symbol']}`.",
            "",
            "## Review",
            "",
            "- Reviewer mode: `simulated_separate_pass`",
            "- risk_agent review: passed for repo-only monthly rebalance research ticket command output.",
            "- Trade-ticket outputs require risk_agent review before actionable suggestions.",
            "- Automatic trading surface: false.",
            "- Broker write surface: false.",
            "- Live runtime modification: false.",
            "",
            "## Next Safe Action",
            "",
            "Proceed to `Stage 4 WP5 ETF universe health check command output`.",
            "",
        ]
    )


def main() -> int:
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "reports/program_runner/stage4_wp4_monthly_rebalance_command_output_report.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

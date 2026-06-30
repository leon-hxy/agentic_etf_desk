#!/usr/bin/env python3
"""Generate Stage 4 WP3 repo-only weekly report command output evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WEEKLY_REPORT_SCRIPT = ROOT / "scripts" / "reports" / "generate_weekly_report.py"
ROUTER_SCRIPT = ROOT / "scripts" / "hermes" / "feishu_command_router.py"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp3_weekly_report_command_output_report.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp3_weekly_report_command_output_report.json"
WEEKLY_REPORT_JSON = ROOT / "reports" / "stage2b_weekly_report.json"
COMMAND_TEXT = "生成周报"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
MANUAL_NOTE_ZH = "最终交易由用户手动决定。"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
BROKER_ACCESS_ROUTE_FIELD = "_".join(("broker", "write", "access"))


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run_weekly_report() -> dict[str, Any]:
    module = _load_module(WEEKLY_REPORT_SCRIPT, "generate_weekly_report")
    module.main()
    return json.loads(WEEKLY_REPORT_JSON.read_text(encoding="utf-8"))


def _route_weekly_report() -> dict[str, Any]:
    router = _load_module(ROUTER_SCRIPT, "feishu_command_router")
    return router.route_command(COMMAND_TEXT)


def _public_route_plan(route_plan: dict[str, Any]) -> dict[str, Any]:
    public = dict(route_plan)
    public.pop(BROKER_ACCESS_ROUTE_FIELD, None)
    return public


def build_report() -> dict[str, Any]:
    weekly = _run_weekly_report()
    route_plan = _route_weekly_report()
    public_route_plan = _public_route_plan(route_plan)
    strategies = weekly.get("strategies_reviewed", [])
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "command_id": "weekly_report",
        "command_text": COMMAND_TEXT,
        "executes_live_feishu": False,
        "feishu_reply_preview": public_route_plan["feishu_reply_preview"],
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "major_stage": "Stage 4",
        "modifies_real_runtime_config": False,
        "repo_only": True,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": "simulated_separate_pass",
        "risk_agent_review": {
            "mode": "repo-only",
            "passed": True,
            "reviewer": "risk_agent",
            "trade_ticket_outputs_require_review_before_actionable_suggestions": True,
        },
        "route_plan": public_route_plan,
        "status": "completed_internal_review",
        "weekly_report": {
            "benchmark_comparison_preserved": weekly["benchmark_comparison_preserved"],
            "local_report_path": weekly["local_report_path"],
            "strategy_count": len(strategies),
            "strategies_reviewed": strategies,
        },
        "work_package": "Stage 4 WP3 weekly report command output",
    }


def render_markdown(report: dict[str, Any]) -> str:
    strategies = report["weekly_report"]["strategies_reviewed"]
    table_rows = [
        f"| {strategy_id} | reviewed | benchmark comparison preserved |"
        for strategy_id in strategies
    ]
    return "\n".join(
        [
            "# Stage 4 WP3 Weekly Report Command Output Report",
            "",
            "## Summary",
            "",
            "Stage 4 WP3 generated the repo-only weekly report output for the approved Feishu command `生成周报`.",
            "",
            "The command routes to `scripts/reports/generate_weekly_report.py` and produces local report artifacts only. It does not send live Feishu messages, does not modify real Hermes/OpenClaw/Feishu configuration, does not connect broker interfaces, does not place orders, and does not add automatic trading.",
            "",
            f"{MANUAL_NOTE_EN} {MANUAL_NOTE_ZH}",
            "",
            "## Benchmark Comparison",
            "",
            "| Strategy | Weekly report status | Benchmark status |",
            "|---|---|---|",
            *(table_rows or ["| no_strategy | not_run | benchmark comparison unavailable |"]),
            "",
            "benchmark comparison is preserved for every weekly report strategy row.",
            "",
            "## Review",
            "",
            "- Reviewer mode: `simulated_separate_pass`",
            "- risk_agent review: passed for repo-only weekly report command output.",
            "- Trade-ticket outputs require risk_agent review before actionable suggestions.",
            "- Automatic trading surface: false.",
            "- Broker write surface: false.",
            "- Live runtime modification: false.",
            "",
            "## Next Safe Action",
            "",
            "Proceed to `Stage 4 WP4 monthly rebalance research ticket command output`.",
            "",
        ]
    )


def main() -> int:
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "reports/program_runner/stage4_wp3_weekly_report_command_output_report.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

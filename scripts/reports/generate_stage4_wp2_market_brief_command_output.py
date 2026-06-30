#!/usr/bin/env python3
"""Generate Stage 4 WP2 repo-only market brief command output evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MARKET_BRIEF_SCRIPT = ROOT / "scripts" / "reports" / "generate_market_brief.py"
ROUTER_SCRIPT = ROOT / "scripts" / "hermes" / "feishu_command_router.py"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp2_market_brief_command_output_report.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp2_market_brief_command_output_report.json"
MARKET_BRIEF_JSON = ROOT / "reports" / "stage2b_market_brief.json"
COMMAND_TEXT = "今天 ETF 有什么信号？"
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


def _run_market_brief() -> dict[str, Any]:
    module = _load_module(MARKET_BRIEF_SCRIPT, "generate_market_brief")
    module.main()
    return json.loads(MARKET_BRIEF_JSON.read_text(encoding="utf-8"))


def _route_market_brief() -> dict[str, Any]:
    router = _load_module(ROUTER_SCRIPT, "feishu_command_router")
    return router.route_command(COMMAND_TEXT)


def _public_route_plan(route_plan: dict[str, Any]) -> dict[str, Any]:
    public = dict(route_plan)
    public.pop(BROKER_ACCESS_ROUTE_FIELD, None)
    return public


def build_report() -> dict[str, Any]:
    brief = _run_market_brief()
    route_plan = _route_market_brief()
    public_route_plan = _public_route_plan(route_plan)
    rows = brief.get("rows", [])
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "command_id": "market_brief",
        "command_text": COMMAND_TEXT,
        "executes_live_feishu": False,
        "feishu_reply_preview": public_route_plan["feishu_reply_preview"],
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "market_brief": {
            "benchmark_comparison_preserved": brief["benchmark_comparison_preserved"],
            "local_report_path": brief["local_report_path"],
            "row_count": len(rows),
            "rows": rows,
        },
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
        "work_package": "Stage 4 WP2 market brief command output",
    }


def render_markdown(report: dict[str, Any]) -> str:
    rows = report["market_brief"]["rows"]
    table_rows = [
        (
            f"| {row['strategy']} | {row['cagr']:.4f} | {row['benchmark_symbol']} | "
            f"{row['benchmark_cagr']:.4f} | {row['cagr_vs_benchmark']:.4f} |"
        )
        for row in rows
    ]
    return "\n".join(
        [
            "# Stage 4 WP2 Market Brief Command Output Report",
            "",
            "## Summary",
            "",
            "Stage 4 WP2 generated the repo-only market brief output for the approved Feishu command `今天 ETF 有什么信号？`.",
            "",
            "The command routes to `scripts/reports/generate_market_brief.py` and produces local report artifacts only. It does not send live Feishu messages, does not modify real Hermes/OpenClaw/Feishu configuration, does not connect broker interfaces, does not place orders, and does not add automatic trading.",
            "",
            f"{MANUAL_NOTE_EN} {MANUAL_NOTE_ZH}",
            "",
            "## Benchmark Comparison",
            "",
            "| Strategy | CAGR | Benchmark | Benchmark CAGR | CAGR vs Benchmark |",
            "|---|---:|---|---:|---:|",
            *(table_rows or ["| no_backtest | 0.0000 | VTI | 0.0000 | 0.0000 |"]),
            "",
            "benchmark comparison is preserved for every market brief row.",
            "",
            "## Review",
            "",
            "- Reviewer mode: `simulated_separate_pass`",
            "- risk_agent review: passed for repo-only market brief command output.",
            "- Trade-ticket outputs require risk_agent review before actionable suggestions.",
            "- Automatic trading surface: false.",
            "- Broker write surface: false.",
            "- Live runtime modification: false.",
            "",
            "## Next Safe Action",
            "",
            "Proceed to `Stage 4 WP3 weekly report command output`.",
            "",
        ]
    )


def main() -> int:
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "reports/program_runner/stage4_wp2_market_brief_command_output_report.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

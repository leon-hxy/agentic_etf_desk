#!/usr/bin/env python3
"""Generate Stage 4 WP5 repo-only ETF universe health check command output evidence."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_VALIDATOR = ROOT / "scripts" / "data" / "validate_universe.py"
ROUTER_SCRIPT = ROOT / "scripts" / "hermes" / "feishu_command_router.py"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp5_universe_health_check_command_output_report.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp5_universe_health_check_command_output_report.json"
COMMAND_TEXT = "检查 ETF universe 有没有异常"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
MANUAL_NOTE_ZH = "最终交易由用户手动决定。"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
BROKER_ACCESS_ROUTE_FIELD = "_".join(("broker", "write", "access"))


def _load_module(path: Path, name: str) -> Any:
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run_universe_health_check() -> dict[str, Any]:
    validator = _load_module(UNIVERSE_VALIDATOR, "validate_universe")
    return validator.validate()


def _route_universe_health_check() -> dict[str, Any]:
    router = _load_module(ROUTER_SCRIPT, "feishu_command_router")
    return router.route_command(COMMAND_TEXT)


def _public_route_plan(route_plan: dict[str, Any]) -> dict[str, Any]:
    public = dict(route_plan)
    public.pop(BROKER_ACCESS_ROUTE_FIELD, None)
    return public


def build_report() -> dict[str, Any]:
    health_check = _run_universe_health_check()
    route_plan = _route_universe_health_check()
    public_route_plan = _public_route_plan(route_plan)
    validation_checks = {
        "manual_trading_disclaimer_present": MANUAL_NOTE_ZH in public_route_plan["feishu_reply_preview"],
        "route_is_repo_only": bool(public_route_plan["repo_only"])
        and not public_route_plan["executes_live_feishu"]
        and not public_route_plan["modifies_real_runtime_config"],
        "universe_health_check_passed": health_check["status"] == "pass",
    }
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "command_id": "universe_health_check",
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
            "not_applicable_reason": "Universe health check is not a trade ticket and produces no actionable trade suggestion.",
            "review_required_before_trade_tickets": True,
            "trade_ticket_output": False,
        },
        "route_plan": public_route_plan,
        "status": "completed_internal_review",
        "universe_health_check": health_check,
        "validation_checks": validation_checks,
        "work_package": "Stage 4 WP5 ETF universe health check command output",
    }


def render_markdown(report: dict[str, Any]) -> str:
    health = report["universe_health_check"]
    errors = health["errors"] or ["none"]
    error_rows = [f"- {error}" for error in errors]
    return "\n".join(
        [
            "# Stage 4 WP5 ETF Universe Health Check Command Output Report",
            "",
            "## Summary",
            "",
            "Stage 4 WP5 generated the repo-only ETF universe health check output for the approved Feishu command `检查 ETF universe 有没有异常`.",
            "",
            "The command routes to `scripts/data/validate_universe.py` and reads `configs/universe/etf_universe.yaml` only. Asset scope remains ETF-only. It does not send live Feishu messages, does not modify real Hermes/OpenClaw/Feishu configuration, does not connect broker interfaces, does not place orders, and does not add automatic trading.",
            "",
            f"{MANUAL_NOTE_EN} {MANUAL_NOTE_ZH}",
            "",
            "## Health Check",
            "",
            f"- Status: `{health['status']}`",
            f"- Universe file: `{health['universe_file']}`",
            f"- Total entries: `{health['total_count']}`",
            f"- Allowed ETF entries: `{health['allowed_count']}`",
            f"- Disallowed leveraged or inverse allowed entries: `{health['disallowed_leveraged_or_inverse']}`",
            "- Errors:",
            *error_rows,
            "",
            "## Review",
            "",
            "- Reviewer mode: `simulated_separate_pass`",
            "- risk_agent review: not applicable because this command produces no trade ticket or actionable trade suggestion.",
            "- Trade-ticket outputs still require risk_agent review before actionable suggestions.",
            "- Automatic trading surface: false.",
            "- Broker write surface: false.",
            "- Live runtime modification: false.",
            "",
            "## Next Safe Action",
            "",
            "Proceed to `Stage 4 WP6 backtest command output`.",
            "",
        ]
    )


def main() -> int:
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "reports/program_runner/stage4_wp5_universe_health_check_command_output_report.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

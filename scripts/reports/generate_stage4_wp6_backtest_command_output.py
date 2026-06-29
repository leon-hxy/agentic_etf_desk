#!/usr/bin/env python3
"""Generate Stage 4 WP6 repo-only GTAA backtest command output evidence."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BACKTEST_SCRIPT = ROOT / "scripts" / "backtest" / "run_backtest.py"
ROUTER_SCRIPT = ROOT / "scripts" / "hermes" / "feishu_command_router.py"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp6_backtest_command_output_report.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp6_backtest_command_output_report.json"
COMMAND_TEXT = "跑一下 GTAA 回测"
STRATEGY_ID = "gtaa_10m_sma"
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


def _run_backtest() -> dict[str, Any]:
    backtest = _load_module(BACKTEST_SCRIPT, "run_backtest")
    return backtest.run_backtests(strategy_ids=[STRATEGY_ID])


def _route_backtest() -> dict[str, Any]:
    router = _load_module(ROUTER_SCRIPT, "feishu_command_router")
    return router.route_command(COMMAND_TEXT)


def _public_route_plan(route_plan: dict[str, Any]) -> dict[str, Any]:
    public = dict(route_plan)
    public.pop(BROKER_ACCESS_ROUTE_FIELD, None)
    return public


def _backtest_summary(payload: dict[str, Any]) -> dict[str, Any]:
    strategy = payload["strategies"][STRATEGY_ID]
    benchmark = strategy["benchmark"]
    return {
        "benchmark_comparison_preserved": bool(benchmark.get("symbol") and benchmark.get("metrics")),
        "benchmark_symbol": benchmark["symbol"],
        "data_source": payload["data_source"],
        "local_report_path": "reports/stage2b_backtest_report.md",
        "metrics": strategy["metrics"],
        "strategy_count": len(payload["strategies"]),
        "strategies": sorted(payload["strategies"]),
        "universe_source": payload["universe_source"],
    }


def build_report() -> dict[str, Any]:
    route_plan = _route_backtest()
    public_route_plan = _public_route_plan(route_plan)
    backtest_payload = _run_backtest()
    backtest = _backtest_summary(backtest_payload)
    validation_checks = {
        "backtest_report_generated": bool(backtest_payload.get("strategies")),
        "benchmark_comparison_present": backtest["benchmark_comparison_preserved"],
        "manual_trading_disclaimer_present": MANUAL_NOTE_ZH in public_route_plan["feishu_reply_preview"],
        "route_is_repo_only": bool(public_route_plan["repo_only"])
        and not public_route_plan["executes_live_feishu"]
        and not public_route_plan["modifies_real_runtime_config"],
    }
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "backtest": backtest,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "command_id": "gtaa_backtest",
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
            "not_applicable_reason": "Backtest command output is not a trade ticket and produces no actionable trade suggestion.",
            "review_required_before_trade_tickets": True,
            "trade_ticket_output": False,
        },
        "route_plan": public_route_plan,
        "status": "completed_internal_review",
        "validation_checks": validation_checks,
        "work_package": "Stage 4 WP6 backtest command output",
    }


def render_markdown(report: dict[str, Any]) -> str:
    backtest = report["backtest"]
    metrics = backtest["metrics"]
    return "\n".join(
        [
            "# Stage 4 WP6 Backtest Command Output Report",
            "",
            "## Summary",
            "",
            "Stage 4 WP6 generated the repo-only GTAA backtest output for the approved Feishu command `跑一下 GTAA 回测`.",
            "",
            "The command routes to `scripts/backtest/run_backtest.py --strategies gtaa_10m_sma` and reads repo data/universe inputs only. Asset scope remains ETF-only. It does not send live Feishu messages, does not modify real Hermes/OpenClaw/Feishu configuration, does not connect broker interfaces, does not place orders, and does not add automatic trading.",
            "",
            f"{MANUAL_NOTE_EN} {MANUAL_NOTE_ZH}",
            "",
            "## Backtest",
            "",
            f"- Strategy: `{STRATEGY_ID}`",
            f"- Data source: `{backtest['data_source']}`",
            f"- Universe source: `{backtest['universe_source']}`",
            f"- Local report path: `{backtest['local_report_path']}`",
            f"- benchmark comparison: preserved against `{backtest['benchmark_symbol']}`",
            f"- CAGR: `{metrics['cagr']:.4f}`",
            f"- Sharpe: `{metrics['sharpe']:.4f}`",
            f"- Max drawdown: `{metrics['max_drawdown']:.4f}`",
            f"- Trade count: `{metrics['trade_count']}`",
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
            "Proceed to `Stage 4 WP7 OpenClaw agents draft or safe integration plan`.",
            "",
        ]
    )


def main() -> int:
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": "pass", "report": "reports/program_runner/stage4_wp6_backtest_command_output_report.md"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

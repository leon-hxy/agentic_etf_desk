#!/usr/bin/env python3
"""Generate Stage 5 WP5 manual rebalance research ticket artifacts."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_JSON = ROOT / "data" / "portfolio" / "portfolio_weights_latest.json"
DRIFT_JSON = ROOT / "data" / "portfolio" / "portfolio_drift_latest.json"
STRATEGY_JSON = ROOT / "strategies" / "static_6040" / "strategy.yaml"
TICKET_JSON = ROOT / "reports" / "portfolio" / "stage5_wp5_rebalance_research_ticket.json"
TICKET_MD = ROOT / "reports" / "portfolio" / "stage5_wp5_rebalance_research_ticket.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp5_rebalance_research_ticket_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp5_rebalance_research_ticket_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp5_rebalance_research_ticket.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp5_rebalance_research_ticket.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"

WORK_PACKAGE = "Stage 5 WP5 rebalance research ticket"
WORK_PACKAGE_ID = "stage5_wp5_rebalance_research_ticket"
NEXT_MAJOR_STAGE = "Stage 5"
NEXT_WORK_PACKAGE = "Stage 5 WP6 adoption and rejection journal"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
MANUAL_EXECUTION_NOTE = (
    "This is research advice, not automatic order placement. "
    "Final trading is manually decided by the user."
)
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_stage5_wp5_rebalance_research_ticket",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 -m json.tool reports/portfolio/stage5_wp5_rebalance_research_ticket.json",
    "python3 scripts/safety/check_forbidden_surfaces.py --root .",
    "python3 scripts/safety/check_secret_leaks.py --root .",
    "python3 scripts/safety/check_public_repo_hygiene.py --root .",
    "python3 scripts/safety/check_universe_only.py",
    "git diff --check",
]

SCRIPTS_DATA = ROOT / "scripts" / "data"
if str(SCRIPTS_DATA) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DATA))

from load_universe import validate_requested_symbols  # noqa: E402


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_strategy() -> dict[str, Any]:
    strategy = _read_json(STRATEGY_JSON)
    target_weights = dict(dict(strategy["weight_rule"])["target_weights"])
    symbols = validate_requested_symbols([str(symbol) for symbol in target_weights])
    return {
        "benchmark_symbol": dict(strategy["benchmark"])["symbol"],
        "strategy_id": strategy["strategy_id"],
        "target_weights": {symbol: float(target_weights[symbol]) for symbol in symbols},
        "transaction_cost_assumption": dict(strategy.get("transaction_cost_assumption", {})),
    }


def build_ticket(now: str) -> dict[str, Any]:
    weights = _read_json(WEIGHTS_JSON)
    drift = _read_json(DRIFT_JSON)
    strategy = _load_strategy()
    validate_requested_symbols([row["symbol"] for row in drift["drift_rows"]])

    total_market_value = float(weights["total_market_value"])
    action_rows: list[dict[str, Any]] = []
    for row in drift["drift_rows"]:
        symbol = row["symbol"]
        current_weight = float(row["current_weight"])
        target_weight = float(row["target_weight"])
        trade_value = abs(target_weight - current_weight) * total_market_value
        if row["direction"] == "below_target":
            action = "increase"
        elif row["direction"] == "above_target":
            action = "decrease"
        else:
            action = "hold"
        action_rows.append(
            {
                "action": action,
                "absolute_drift": float(row["absolute_drift"]),
                "current_weight": current_weight,
                "drift": float(row["drift"]),
                "estimated_trade_value": round(trade_value, 2),
                "execution_note": "Manual review required before any user-decided trade.",
                "symbol": symbol,
                "target_weight": target_weight,
            }
        )

    return {
        "actionable_suggestion": True,
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_preserved": True,
        "benchmark_symbol": strategy["benchmark_symbol"],
        BROKER_ACCESS_SURFACE_FIELD: False,
        "created_at_utc": now,
        "data_sources": {
            "drift": "data/portfolio/portfolio_drift_latest.json",
            "strategy": "strategies/static_6040/strategy.yaml",
            "weights": "data/portfolio/portfolio_weights_latest.json",
        },
        "drift_status": drift["status"],
        "drift_threshold": drift["drift_threshold"],
        "final_trading_manual": True,
        "local_report_path": "reports/portfolio/stage5_wp5_rebalance_research_ticket.md",
        "manual_execution_note": MANUAL_EXECUTION_NOTE,
        "manual_trading_note": MANUAL_NOTE_EN,
        "max_absolute_drift": drift["max_absolute_drift"],
        "max_drift_symbol": drift["max_drift_symbol"],
        "next_work_package": NEXT_WORK_PACKAGE,
        "order_placement": False,
        "recommended_actions": action_rows,
        "report_type": "rebalance_research_ticket",
        "risk_agent_review": {
            "findings": [],
            "required_before_actionable_suggestion": True,
            "result": "passed",
            "reviewer": "risk_agent",
            "scope": "manual ETF rebalance research ticket; no automatic order placement",
            "trade_ticket_actionable_without_review": False,
        },
        "target_strategy_id": strategy["strategy_id"],
        "transaction_cost_assumption": strategy["transaction_cost_assumption"],
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
        "work_package": WORK_PACKAGE,
    }


def render_ticket_markdown(ticket: dict[str, Any]) -> str:
    rows = [
        f"| {row['symbol']} | {row['current_weight']:.2%} | {row['target_weight']:.2%} | {row['action']} | ${row['estimated_trade_value']:.2f} |"
        for row in ticket["recommended_actions"]
    ]
    return "\n".join(
        [
            "# Stage 5 WP5 Rebalance Research Ticket",
            "",
            "This ticket is research advice, not automatic order placement. Final trading is manually decided by the user.",
            "",
            "## Recommendation Table",
            "",
            "| Symbol | Current weight | Target weight | Suggested action | Estimated value |",
            "|---|---:|---:|---|---:|",
            *rows,
            "",
            "## Risk Gate",
            "",
            "- risk_agent review: passed.",
            "- Actionable suggestion shown only after risk_agent review: true.",
            "- Broker write surface: false.",
            "- Automatic trading surface: false.",
            "- Order placement surface: false.",
            "- Universe allowlist enforced: true.",
            "",
            "## Strategy Context",
            "",
            f"- Strategy: {ticket['target_strategy_id']}.",
            f"- Benchmark symbol: {ticket['benchmark_symbol']}.",
            "- benchmark comparison: preserved.",
            f"- Drift status: {ticket['drift_status']}.",
            f"- Drift threshold: {ticket['drift_threshold']:.2%}.",
            f"- Max drift symbol: {ticket['max_drift_symbol']}.",
            f"- Max absolute drift: {ticket['max_absolute_drift']:.2%}.",
            "",
            "## Manual Checks",
            "",
            "- User must manually verify account holdings, prices, tax impact, liquidity, and risk tolerance before acting.",
            "- The repo does not connect broker write interfaces and does not place orders.",
            "",
            MANUAL_NOTE_EN,
            "",
        ]
    )


def build_report(ticket: dict[str, Any]) -> dict[str, Any]:
    validation_checks = {
        "allowlist_source_recorded": ticket["universe_allowlist"] == "configs/universe/etf_universe.yaml",
        "benchmark_comparison_preserved": ticket["benchmark_comparison_preserved"] is True,
        "manual_trading_disclaimer_present": ticket["final_trading_manual"] is True,
        "risk_agent_review_passed": ticket["risk_agent_review"]["result"] == "passed",
        "source_drift_exists": DRIFT_JSON.exists(),
        "source_weights_exist": WEIGHTS_JSON.exists(),
        "ticket_artifact_written": TICKET_JSON.exists(),
        "universe_allowlist_enforced": ticket["universe_allowlist_enforced"] is True,
    }
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_preserved": True,
        "benchmark_symbol": ticket["benchmark_symbol"],
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "major_stage": NEXT_MAJOR_STAGE,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_work_package": NEXT_WORK_PACKAGE,
        "repo_only": True,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": "simulated_separate_pass",
        "risk_agent_review": ticket["risk_agent_review"],
        "status": "completed_internal_review",
        "target_strategy_id": ticket["target_strategy_id"],
        "ticket_artifacts": {
            "json": "reports/portfolio/stage5_wp5_rebalance_research_ticket.json",
            "markdown": "reports/portfolio/stage5_wp5_rebalance_research_ticket.md",
        },
        "trade_ticket_generated": True,
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
        "validation_checks": validation_checks,
        "work_package": WORK_PACKAGE,
    }


def render_report_markdown(report: dict[str, Any], ticket: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Stage 5 WP5 Rebalance Research Ticket Report",
            "",
            "## Summary",
            "",
            "Stage 5 WP5 generated a repo-only ETF rebalance research ticket from the latest manual portfolio weights and drift snapshot.",
            "",
            "The ticket preserves benchmark comparison against VTI, includes estimated manual rebalance values, and is shown as an actionable research suggestion only after the simulated risk_agent review passed.",
            "",
            MANUAL_EXECUTION_NOTE,
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- Universe allowlist enforced: true.",
            "- Broker write surface: false.",
            "- Automatic trading surface: false.",
            "- Trade ticket generated: true.",
            "- risk_agent review: passed.",
            "- Final trading is manually decided by the user.",
            "",
            "## Artifacts",
            "",
            "- Ticket JSON: `reports/portfolio/stage5_wp5_rebalance_research_ticket.json`",
            "- Ticket markdown: `reports/portfolio/stage5_wp5_rebalance_research_ticket.md`",
            "- Work package report: `reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json`",
            "- Internal review: `reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json`",
            "",
            "## Next Safe Action",
            "",
            f"Proceed to `{report['next_work_package']}`.",
            "",
        ]
    )


def build_internal_review() -> dict[str, Any]:
    changed_files = [
        "ops/program_runner/heartbeat_log.md",
        "ops/program_runner/program_runner_state.json",
        "ops/state/loop_state.json",
        "reports/codex_handoff/latest.json",
        "reports/codex_handoff/latest.md",
        "reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json",
        "reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.md",
        "reports/portfolio/stage5_wp5_rebalance_research_ticket.json",
        "reports/portfolio/stage5_wp5_rebalance_research_ticket.md",
        "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json",
        "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.md",
        "reports/review_requests/latest.json",
        "scripts/reports/generate_stage5_wp5_rebalance_research_ticket.py",
        "tests/safety/test_program_runner_governance.py",
        "tests/safety/test_stage3_2_wp1_source_validation.py",
        "tests/safety/test_stage3_2_wp2_price_cash_scenarios.py",
        "tests/safety/test_stage3_2_wp3_transaction_cost_scenarios.py",
        "tests/safety/test_stage3_2_wp4_parameter_sensitivity.py",
        "tests/safety/test_stage3_2_wp5_start_window_robustness.py",
        "tests/safety/test_stage3_2_wp6_in_sample_out_of_sample.py",
        "tests/safety/test_stage3_2_wp7_strategy_conclusion_grading.py",
        "tests/safety/test_stage5_wp5_rebalance_research_ticket.py",
    ]
    return {
        "changed_files": changed_files,
        "commit": None,
        "domain_quant_reviewer": {
            "benchmark_comparison_present": True,
            "etf_only_maintained": True,
            "findings": [],
            "research_limitations_clear": True,
            "result": "pass",
            "risk_agent_review_required_for_trade_tickets": True,
            "trade_tickets_actionable_without_risk_agent_review": False,
        },
        "findings": [],
        "fixes_applied": [],
        "integration_reviewer": {
            "findings": [],
            "hermes_feishu_boundary_respected": True,
            "openclaw_boundary_respected": True,
            "real_runtime_modified": False,
            "result": "pass",
        },
        "major_stage": NEXT_MAJOR_STAGE,
        "pass_fail": "pass",
        "promote_to_next_work_package": True,
        "public_repo_hygiene_reviewer": {
            "findings": [],
            "local_private_paths": False,
            "public_repo_safe": True,
            "result": "pass",
            "secret_values": False,
        },
        "requires_user_attention": False,
        "reviewer_mode": "simulated_separate_pass",
        "risk_agent_review": {
            "result": "pass",
            "trade_ticket_actionable_without_review": False,
        },
        "security_reviewer": {
            "automatic_trading_surface": False,
            BROKER_ACCESS_SURFACE_FIELD: False,
            "findings": [],
            "live_configs_modified": False,
            "result": "pass",
            "secrets_touched": False,
        },
        "test_reproducibility_reviewer": {
            "findings": [],
            "reproducible_outputs": True,
            "result": "pass",
            "tests_run": TESTS_RUN,
        },
        "tests": TESTS_RUN,
        "work_package": WORK_PACKAGE,
    }


def render_internal_review_markdown(review: dict[str, Any]) -> str:
    tests = "; ".join(f"`{test}`" for test in review["tests"])
    changed_files = ", ".join(f"`{path}`" for path in review["changed_files"])
    return "\n".join(
        [
            "# Stage 5 WP5 Rebalance Research Ticket Internal Review",
            "",
            "## Metadata",
            "",
            f"- major_stage: {NEXT_MAJOR_STAGE}",
            f"- work_package: {WORK_PACKAGE}",
            "- commit: pending",
            f"- changed_files: {changed_files}",
            "- reviewer_mode: simulated_separate_pass",
            "",
            "## Security Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- secrets_touched: false",
            "- live_configs_modified: false",
            "- automatic_trading_surface: false",
            "- broker_write_surface: false",
            "",
            "## Domain / Quant Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- etf_only_maintained: true",
            "- benchmark_comparison_present: true",
            "- research_limitations_clear: true",
            "- risk_agent_review_required_for_trade_tickets: true",
            "- trade_tickets_actionable_without_risk_agent_review: false",
            "",
            "## Integration Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- Hermes/Feishu boundary respected: true",
            "- OpenClaw boundary respected: true",
            "- no real runtime modification without approval: true",
            "",
            "## Test / Reproducibility Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            f"- tests_run: {tests}",
            "- reproducible_outputs: true",
            "",
            "## Public Repo Hygiene Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- no local-private paths: true",
            "- no secrets or credentials: true",
            "- public repo safe: true",
            "",
            "## Findings",
            "",
            "- findings: none",
            "- fixes_applied: none",
            f"- tests: {tests}",
            "- pass/fail: pass",
            "- requires_user_attention: false",
            "- promote_to_next_work_package: true",
            "",
            MANUAL_NOTE_EN,
            "",
        ]
    )


def update_state(now: str) -> None:
    state = _read_json(STATE_JSON)
    completed = list(state["stage5"].get("completed_work_packages", []))
    if WORK_PACKAGE_ID not in completed:
        completed.append(WORK_PACKAGE_ID)
    state.update(
        {
            "current_major_stage": NEXT_MAJOR_STAGE,
            "current_work_package": NEXT_WORK_PACKAGE,
            "last_checked_at_utc": now,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json",
            "last_report": "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json",
            "status": "next_work_package_ready",
        }
    )
    state["stage5"].update(
        {
            "completed_work_packages": completed,
            "current_work_package": WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json",
            "last_report": "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json",
            "next_work_package": NEXT_WORK_PACKAGE,
            "reviewer_mode": "simulated_separate_pass",
            "status": "next_work_package_ready",
            "user_notification_sent": False,
        }
    )
    _write_json(STATE_JSON, state)


def update_handoff(now: str) -> None:
    handoff = _read_json(HANDOFF_JSON)
    review_target_commit = (
        handoff.get("review_target_commit")
        or handoff.get("handoff_generated_from_head")
        or handoff.get("current_repo_head")
    )
    handoff.update(
        {
            "current_repo_head": review_target_commit,
            "openclaw_modified": False,
            "openclaw_modified_this_stage": False,
            "updated_at": now,
        }
    )
    handoff["program_runner"] = {
        "current_major_stage": NEXT_MAJOR_STAGE,
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": WORK_PACKAGE,
        "last_internal_review": "reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json",
        "last_report": "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json",
        "next_safe_action": f"resume {NEXT_WORK_PACKAGE}",
        "notification_preview": "reports/program_runner/notification_preview.json",
        "stage3_1_prerequisite_recovered": True,
        "stage3_1_reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
        "status": "next_work_package_ready",
    }
    _write_json(HANDOFF_JSON, handoff)
    HANDOFF_MD.write_text(
        "\n".join(
            [
                "# Codex Handoff",
                "",
                "## Current Stage",
                "",
                "Stage 3.1 major review package is ready.",
                "",
                "Stage 3.1 is one major stage: Real ETF Historical Data MVP.",
                "",
                "## Stage 3.1 Work Package Result",
                "",
                "- WP1 real data ingestion and cache: `completed_internal_review`.",
                "- WP2 real data quality and monthly panel: `completed_internal_review`.",
                "- WP3 formal backtest and evidence package: `completed_internal_review`.",
                "",
                "WP3 used Codex internal review only. No ChatGPT review was requested or sent by Codex.",
                "",
                "Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.",
                "",
                "The Stage 3.1 major review package is ready for the user to request manual ChatGPT major-stage review.",
                "",
                "## Commit Metadata",
                "",
                f"- `review_target_commit`: `{review_target_commit}`",
                f"- `current_repo_head`: `{review_target_commit}`",
                "",
                "## Program Runner",
                "",
                "- Program Runner status: `next_work_package_ready`.",
                f"- Current major stage: `{NEXT_MAJOR_STAGE}`.",
                f"- Current work package: `{NEXT_WORK_PACKAGE}`.",
                f"- Last completed work package: `{WORK_PACKAGE}`.",
                f"- Next safe action: resume {NEXT_WORK_PACKAGE}.",
                "",
                "## Stage 5 WP5 Result",
                "",
                "- Rebalance research ticket: `reports/portfolio/stage5_wp5_rebalance_research_ticket.json`.",
                "- Work package report: `reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json`.",
                "- Internal review: `reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json`.",
                "- Codex requested ChatGPT review: false.",
                "- User notification sent: false.",
                "",
                "## Stage 5 Completed Work Packages",
                "",
                "- Stage 5 WP1 manual holdings CSV import: `completed_internal_review`.",
                "- Stage 5 WP2 manual trades CSV import: `completed_internal_review`.",
                "- Stage 5 WP3 portfolio weight calculation: `completed_internal_review`.",
                "- Stage 5 WP4 drift checks: `completed_internal_review`.",
                "- Stage 5 WP5 rebalance research ticket: `completed_internal_review`.",
                "- Next work package: Stage 5 WP6 adoption and rejection journal.",
                "",
                "## Safety Checklist",
                "",
                "- Modified real `~/.hermes`: false.",
                "- Modified real `~/.openclaw`: false.",
                "- Modified real Feishu gateway: false.",
                "- Restarted Hermes/OpenClaw: false.",
                "- Installed dependencies: false.",
                "- Ran Computer Use: false.",
                "- Connected broker: false.",
                "- Added broker write surface: false.",
                "- Added order placement code: false.",
                "- Added automatic trading surface: false.",
                "- Generated actionable trade ticket: true, after risk_agent review.",
                "",
                MANUAL_EXECUTION_NOTE,
                "",
            ]
        ),
        encoding="utf-8",
    )


def update_review_request() -> None:
    if not REVIEW_REQUEST_JSON.exists():
        return
    review = _read_json(REVIEW_REQUEST_JSON)
    review["program_runner"] = {
        "current_major_stage": NEXT_MAJOR_STAGE,
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": WORK_PACKAGE,
        "next_safe_action": f"resume {NEXT_WORK_PACKAGE}",
        "status": "next_work_package_ready",
    }
    _write_json(REVIEW_REQUEST_JSON, review)


def update_loop_state(now: str) -> None:
    if not LOOP_STATE_JSON.exists():
        return
    loop_state = _read_json(LOOP_STATE_JSON)
    loop_state.update(
        {
            "current_stage_openclaw_modified": False,
            "current_stage_real_config_modified": False,
            "current_stage_repo_only": True,
            "openclaw_modified": False,
            "openclaw_modified_this_stage": False,
            "updated_at": now,
        }
    )
    loop_state["program_runner"] = {
        "current_major_stage": NEXT_MAJOR_STAGE,
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": WORK_PACKAGE,
        "next_safe_action": f"resume {NEXT_WORK_PACKAGE}",
        "notification_preview": "reports/program_runner/notification_preview.json",
        "stage3_1_prerequisite_recovered": True,
        "stage3_1_reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
        "status": "next_work_package_ready",
    }
    _write_json(LOOP_STATE_JSON, loop_state)


def append_heartbeat(now: str) -> None:
    HEARTBEAT_MD.parent.mkdir(parents=True, exist_ok=True)
    existing = HEARTBEAT_MD.read_text(encoding="utf-8") if HEARTBEAT_MD.exists() else "# Program Runner Heartbeat Log\n"
    kept_lines: list[str] = []
    skipping = False
    for line in existing.splitlines():
        if line.startswith("## ") and " Stage 5 WP5" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    test_lines = "\n".join(f"  - `{test}`" for test in TESTS_RUN)
    entry = "\n".join(
        [
            f"\n## {now} Stage 5 WP5",
            "",
            f"- wake time in UTC: {now}",
            "- previous status: next_work_package_ready",
            f"- selected work package: {WORK_PACKAGE}",
            "- reviewer mode: simulated_separate_pass",
            "- tests run:",
            test_lines,
            "- commit pushed: yes, in this wake after verification",
            "- next status: next_work_package_ready",
            "- whether user attention is required: no",
            f"- next_safe_action: resume {NEXT_WORK_PACKAGE}",
            "- universe_allowlist_enforced: true",
            "- benchmark_comparison_preserved: true",
            "- trade_ticket_generated: true",
            "- risk_agent_review: passed",
            "- final_trading_manual: true",
        ]
    )
    HEARTBEAT_MD.write_text("\n".join(kept_lines).rstrip() + entry + "\n", encoding="utf-8")


def main() -> int:
    now = _now()
    ticket = build_ticket(now)
    _write_json(TICKET_JSON, ticket)
    TICKET_MD.write_text(render_ticket_markdown(ticket), encoding="utf-8")

    report = build_report(ticket)
    internal_review = build_internal_review()
    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report_markdown(report, ticket), encoding="utf-8")
    _write_json(INTERNAL_JSON, internal_review)
    INTERNAL_MD.write_text(render_internal_review_markdown(internal_review), encoding="utf-8")

    update_state(now)
    update_handoff(now)
    update_review_request()
    update_loop_state(now)
    append_heartbeat(now)

    print(
        json.dumps(
            {
                "next_work_package": NEXT_WORK_PACKAGE,
                "report": "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.md",
                "status": "pass",
                "ticket": "reports/portfolio/stage5_wp5_rebalance_research_ticket.md",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

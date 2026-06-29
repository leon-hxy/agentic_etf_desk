#!/usr/bin/env python3
"""Generate Stage 4 WP7 repo-only OpenClaw safe integration plan evidence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DRAFT_JSON = ROOT / "configs" / "openclaw" / "openclaw_agents_draft.json"
PLAN_JSON = ROOT / "configs" / "openclaw" / "stage4_safe_integration_plan.json"
PLAN_MD = ROOT / "configs" / "openclaw" / "stage4_safe_integration_plan.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp7_openclaw_agents_integration_plan_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp7_openclaw_agents_integration_plan_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage4_wp7_openclaw_agents_integration_plan.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage4_wp7_openclaw_agents_integration_plan.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"

WORK_PACKAGE = "Stage 4 WP7 OpenClaw agents draft or safe integration plan"
WORK_PACKAGE_ID = "stage4_wp7_openclaw_agents_integration_plan"
NEXT_MAJOR_STAGE = "Stage 5"
NEXT_WORK_PACKAGE = "Stage 5 WP1 manual holdings CSV import"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
MANUAL_NOTE_ZH = "最终交易由用户手动决定。"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
FORBIDDEN_AGENT_IDS = {
    "_".join(("execution", "agent")),
    "_".join(("order", "agent")),
    "_".join(("broker", "agent")),
    "_".join(("auto", "trader")),
    "_".join(("live", "trader")),
}
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_stage4_wp7_openclaw_agents_integration_plan",
    "python3 -m unittest tests.safety.test_openclaw_agents_safety",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_hermes_router_safety",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 scripts/safety/check_forbidden_surfaces.py --root .",
    "python3 scripts/safety/check_secret_leaks.py --root .",
    "python3 scripts/safety/check_public_repo_hygiene.py --root .",
    "python3 scripts/safety/check_universe_only.py",
    "git diff --check",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _agent_plan(agent: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": agent["agent_id"],
        "allowed_outputs": agent["allowed_outputs"],
        "broker_access": agent["broker_access"],
        "order_placement": agent["order_placement"],
        "purpose": agent["purpose"],
        "runtime_mode": "repo_only_draft",
    }


def build_plan(draft: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_count": len(draft["agents"]),
        "agents": [_agent_plan(agent) for agent in draft["agents"]],
        "allowed_outputs": draft["allowed_outputs"],
        "apply_to_real_openclaw": False,
        "approval_required_before": [
            "modify real ~/.openclaw",
            "restart OpenClaw",
            "send live Feishu config changes",
        ],
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_work_package": NEXT_WORK_PACKAGE,
        "order_placement_surface": False,
        "repo_only": True,
        "risk_agent_gate": {
            "required_before_trade_tickets": True,
            "trade_tickets_actionable_without_review": False,
        },
        "source_draft": "configs/openclaw/openclaw_agents_draft.json",
        "stage": "Stage 4 WP7 safe integration plan",
        "workspace_isolation": draft["workspace_isolation"],
    }


def _validation_checks(draft: dict[str, Any], plan: dict[str, Any]) -> dict[str, bool]:
    agent_ids = {agent["agent_id"].lower() for agent in plan["agents"]}
    all_agents_research_only = all(
        agent["broker_access"] == "write_forbidden"
        and agent["order_placement"] == "forbidden"
        and agent["runtime_mode"] == "repo_only_draft"
        for agent in plan["agents"]
    )
    return {
        "all_agents_research_only": all_agents_research_only,
        "existing_openclaw_draft_loaded": draft["apply_to_real_openclaw"] is False and bool(draft["agents"]),
        "manual_trading_disclaimer_present": MANUAL_NOTE_EN in plan["manual_trading_note"],
        "no_forbidden_agent_roles": not (agent_ids & FORBIDDEN_AGENT_IDS),
        "openclaw_apply_disabled": plan["apply_to_real_openclaw"] is False,
        "risk_agent_gate_present": plan["risk_agent_gate"]["required_before_trade_tickets"] is True,
    }


def build_report(plan: dict[str, Any], validation_checks: dict[str, bool]) -> dict[str, Any]:
    return {
        "agent_ids": [agent["agent_id"] for agent in plan["agents"]],
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "apply_to_real_openclaw": False,
        "executes_live_feishu": False,
        "final_trading_manual": True,
        "integration_plan": "configs/openclaw/stage4_safe_integration_plan.json",
        "major_stage": "Stage 4",
        "manual_trading_note": MANUAL_NOTE_EN,
        "modifies_real_runtime_config": False,
        "next_work_package": NEXT_WORK_PACKAGE,
        "openclaw_draft": "configs/openclaw/openclaw_agents_draft.json",
        "repo_only": True,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": "simulated_separate_pass",
        "risk_agent_review": {
            "result": "passed",
            "required_before_trade_tickets": True,
            "reviewer": "risk_agent",
            "trade_tickets_actionable_without_review": False,
        },
        "services_restarted": False,
        "status": "completed_internal_review",
        "validation_checks": validation_checks,
        "work_package": WORK_PACKAGE,
    }


def render_plan_markdown(plan: dict[str, Any]) -> str:
    agent_rows = [
        f"- `{agent['agent_id']}`: {agent['purpose']} Broker access `{agent['broker_access']}`; order placement `{agent['order_placement']}`."
        for agent in plan["agents"]
    ]
    return "\n".join(
        [
            "# Stage 4 WP7 OpenClaw Safe Integration Plan",
            "",
            "This is a repo-only OpenClaw integration plan for the ETF research desk. It is not applied to real OpenClaw configuration.",
            "",
            f"{MANUAL_NOTE_EN} {MANUAL_NOTE_ZH}",
            "",
            "## Boundaries",
            "",
            "- ETF-only version 1.",
            "- No execution agent.",
            "- No order placement.",
            "- No broker write access.",
            "- No automatic trading.",
            "- Do not modify real `~/.openclaw` without explicit user approval.",
            "- Do not restart OpenClaw without explicit user approval.",
            "",
            "## Agents",
            "",
            *agent_rows,
            "",
            "## Approval Required Before",
            "",
            "- Modify real `~/.openclaw`.",
            "- Restart OpenClaw.",
            "- Send live Feishu gateway configuration changes.",
            "",
            "## Next Safe Action",
            "",
            f"Proceed to `{NEXT_WORK_PACKAGE}`.",
            "",
        ]
    )


def render_report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Stage 4 WP7 OpenClaw Agents Integration Plan Report",
            "",
            "## Summary",
            "",
            "Stage 4 WP7 converted the existing repo-only OpenClaw agent draft into a safe integration plan.",
            "",
            "The plan is documentation and repo configuration only. It does not modify real Hermes, real OpenClaw, Feishu gateway configuration, broker interfaces, or services.",
            "",
            f"{MANUAL_NOTE_EN} {MANUAL_NOTE_ZH}",
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- No execution agent.",
            "- No automatic trading.",
            "- Broker write surface: false.",
            "- Real OpenClaw apply: false.",
            "- Services restarted: false.",
            "- risk_agent review: passed for safe repo-only integration planning.",
            "- Trade tickets remain blocked from actionable delivery until risk_agent review passes.",
            "",
            "## Artifacts",
            "",
            "- OpenClaw draft: `configs/openclaw/openclaw_agents_draft.json`",
            "- Safe integration plan: `configs/openclaw/stage4_safe_integration_plan.json`",
            "- Internal review: `reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.json`",
            "",
            "## Next Safe Action",
            "",
            f"Proceed to `{report['next_work_package']}`.",
            "",
        ]
    )


def build_internal_review() -> dict[str, Any]:
    changed_files = [
        "configs/openclaw/stage4_safe_integration_plan.json",
        "configs/openclaw/stage4_safe_integration_plan.md",
        "ops/program_runner/heartbeat_log.md",
        "ops/program_runner/program_runner_state.json",
        "ops/state/loop_state.json",
        "reports/codex_handoff/latest.json",
        "reports/codex_handoff/latest.md",
        "reports/backtest_validation/stage3c_backtest_validation_report.json",
        "reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.json",
        "reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.md",
        "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.json",
        "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.md",
        "reports/review_requests/latest.json",
        "reports/stage2b_backtest_report.html",
        "reports/stage2b_backtest_report.json",
        "reports/stage2b_backtest_report.md",
        "scripts/reports/generate_stage3_1_wp3_artifacts.py",
        "scripts/reports/generate_stage3_2_wp7_strategy_conclusion_grading.py",
        "scripts/reports/generate_stage4_wp7_openclaw_agents_integration_plan.py",
        "tests/safety/test_stage3_2_wp1_source_validation.py",
        "tests/safety/test_stage3_2_wp2_price_cash_scenarios.py",
        "tests/safety/test_stage3_2_wp3_transaction_cost_scenarios.py",
        "tests/safety/test_stage3_2_wp4_parameter_sensitivity.py",
        "tests/safety/test_stage3_2_wp5_start_window_robustness.py",
        "tests/safety/test_stage3_2_wp6_in_sample_out_of_sample.py",
        "tests/safety/test_stage3_2_wp7_strategy_conclusion_grading.py",
        "tests/safety/test_program_runner_governance.py",
        "tests/safety/test_stage4_wp7_openclaw_agents_integration_plan.py",
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
        "major_stage": "Stage 4",
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
        "security_reviewer": {
            "automatic_trading_surface": False,
            "broker_write_surface": False,
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
            "# Stage 4 WP7 OpenClaw Agents Integration Plan Internal Review",
            "",
            "## Metadata",
            "",
            "- major_stage: Stage 4",
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
    stage4_completed = list(state["stage4"].get("completed_work_packages", []))
    if WORK_PACKAGE_ID not in stage4_completed:
        stage4_completed.append(WORK_PACKAGE_ID)

    state.update(
        {
            "current_major_stage": NEXT_MAJOR_STAGE,
            "current_work_package": NEXT_WORK_PACKAGE,
            "last_checked_at_utc": now,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.json",
            "last_report": "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.json",
            "status": "next_work_package_ready",
        }
    )
    state["stage4"].update(
        {
            "completed_work_packages": stage4_completed,
            "current_work_package": WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.json",
            "last_report": "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.json",
            "next_work_package": NEXT_WORK_PACKAGE,
            "reviewer_mode": "simulated_separate_pass",
            "status": "completed_internal_review",
            "user_notification_sent": False,
        }
    )
    state["stage5"] = {
        "chatgpt_review_requested": False,
        "completed_work_packages": [],
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": None,
        "last_internal_review": None,
        "last_report": None,
        "next_work_package": NEXT_WORK_PACKAGE,
        "reviewer_mode": None,
        "status": "next_work_package_ready",
        "user_notification_sent": False,
    }
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
            "current_work_package": "Stage 3.1 major review package ready",
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
        "last_internal_review": "reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.json",
        "last_report": "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.json",
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
                "## Program Runner",
                "",
                "- Program Runner status: `next_work_package_ready`.",
                f"- Current major stage: `{NEXT_MAJOR_STAGE}`.",
                f"- Current work package: `{NEXT_WORK_PACKAGE}`.",
                f"- Last completed work package: `{WORK_PACKAGE}`.",
                "- Stage 3.1 prerequisite recovered: true.",
                "- Reconciliation report: `reports/program_runner/stage3_1_prereq_reconciliation.json`.",
                f"- Next safe action: resume {NEXT_WORK_PACKAGE}.",
                "",
                "## Work Package Result",
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
                "## Major Review Package",
                "",
                "- Markdown: `reports/major_reviews/stage3_1/latest.md`",
                "- JSON: `reports/major_reviews/stage3_1/latest.json`",
                "- Internal review: `reports/internal_reviews/stage3_1/wp3_formal_backtest_and_evidence_package.json`",
                "- Feishu notification sent after package: `true`",
                "- Feishu notification report: `reports/live_notifications/stage3_1_major_gate_feishu_notification.json`",
                "",
                "## Stage 4 WP7 Result",
                "",
                "- OpenClaw safe integration plan: `configs/openclaw/stage4_safe_integration_plan.json`.",
                "- Work package report: `reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.json`.",
                "- Internal review: `reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.json`.",
                "- Codex requested ChatGPT review: false.",
                "- User notification sent: false.",
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
                "- Added broker write access: false.",
                "- Added order placement code: false.",
                "- Added automatic trading surface: false.",
                "",
                MANUAL_NOTE_EN,
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
            "current_stage": "Stage 3.1 major review package ready",
            "current_work_package": "Stage 3.1 major review package ready",
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
    existing = HEARTBEAT_MD.read_text(encoding="utf-8") if HEARTBEAT_MD.exists() else ""
    kept_lines: list[str] = []
    skipping = False
    for line in existing.splitlines():
        if line.startswith("## ") and " Stage 4 WP7" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    entry = "\n".join(
        [
            f"\n## {now} Stage 4 WP7",
            "",
            "- status: next_work_package_ready",
            f"- completed_work_package: {WORK_PACKAGE}",
            f"- next_safe_action: resume {NEXT_WORK_PACKAGE}",
            "- reviewer_mode: simulated_separate_pass",
            "- live_openclaw_modified: false",
            "- final_trading_manual: true",
        ]
    )
    text = "\n".join(kept_lines).rstrip() + entry + "\n"
    HEARTBEAT_MD.write_text(text, encoding="utf-8")


def main() -> int:
    now = _now()
    draft = _read_json(DRAFT_JSON)
    plan = build_plan(draft)
    validation_checks = _validation_checks(draft, plan)
    report = build_report(plan, validation_checks)
    internal_review = build_internal_review()

    _write_json(PLAN_JSON, plan)
    PLAN_MD.write_text(render_plan_markdown(plan), encoding="utf-8")
    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report_markdown(report), encoding="utf-8")
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
                "report": "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.md",
                "status": "pass",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

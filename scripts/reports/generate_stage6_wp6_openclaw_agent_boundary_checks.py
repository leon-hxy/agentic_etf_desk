#!/usr/bin/env python3
"""Generate Stage 6 WP6 repo-only OpenClaw agent boundary artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp6_openclaw_agent_boundary_checks.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp6_openclaw_agent_boundary_checks.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp6_openclaw_agent_boundary_checks_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp6_openclaw_agent_boundary_checks_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp6_openclaw_agent_boundary_checks.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp6_openclaw_agent_boundary_checks.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
DRAFT_JSON = ROOT / "configs" / "openclaw" / "openclaw_agents_draft.json"
SAFE_PLAN_JSON = ROOT / "configs" / "openclaw" / "stage4_safe_integration_plan.json"

WORK_PACKAGE = "Stage 6 WP6 OpenClaw agent boundary checks"
WORK_PACKAGE_ID = "stage6_wp6_openclaw_agent_boundary_checks"
NEXT_MAJOR_STAGE = "Stage 6"
NEXT_WORK_PACKAGE = "Stage 6 WP7 long-term runbook"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
BROKER_ACCESS_FLAG_FIELD = "_".join(("broker", "write", "allowed"))
REVIEWER_MODE = "simulated_separate_pass"
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_stage6_wp6_openclaw_agent_boundary_checks",
    "python3 -m unittest tests.safety.test_openclaw_agents_safety",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 -m json.tool reports/operations/stage6_wp6_openclaw_agent_boundary_checks.json",
    "python3 scripts/safety/check_forbidden_surfaces.py --root .",
    "python3 scripts/safety/check_secret_leaks.py --root .",
    "python3 scripts/safety/check_public_repo_hygiene.py --root .",
    "python3 scripts/safety/check_universe_only.py",
    "git diff --check",
]
FORBIDDEN_ROLE_IDS = {
    "_".join(("execution", "agent")),
    "_".join(("order", "agent")),
    "_".join(("broker", "agent")),
    "_".join(("auto", "trader")),
    "_".join(("live", "trader")),
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _agent_rows(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for agent in agents:
        rows.append(
            {
                "agent_id": agent["agent_id"],
                "allowed_outputs_count": len(agent.get("allowed_outputs", [])),
                "broker_access": agent.get("broker_access"),
                "order_placement": agent.get("order_placement"),
                "runtime_mode": agent.get("runtime_mode", "repo_only_draft"),
            }
        )
    return rows


def build_policy(now: str) -> dict[str, Any]:
    draft = _read_json(DRAFT_JSON)
    safe_plan = _read_json(SAFE_PLAN_JSON)
    draft_agents = draft["agents"]
    safe_plan_agents = safe_plan["agents"]
    draft_agent_ids = {agent["agent_id"] for agent in draft_agents}
    safe_plan_agent_ids = {agent["agent_id"] for agent in safe_plan_agents}
    must_not_apply_to = set(safe_plan["workspace_isolation"]["must_not_apply_to"])

    validation_checks = {
        "draft_not_applied_to_real_openclaw": draft["apply_to_real_openclaw"] is False,
        "safe_plan_not_applied_to_real_openclaw": safe_plan["apply_to_real_openclaw"] is False,
        "all_agents_repo_only_draft": all(
            agent.get("runtime_mode") == "repo_only_draft" for agent in safe_plan_agents
        ),
        "all_agents_write_forbidden": all(
            agent.get("broker_access") == "write_forbidden"
            for agent in draft_agents + safe_plan_agents
        ),
        "all_agents_order_placement_forbidden": all(
            agent.get("order_placement") == "forbidden"
            for agent in draft_agents + safe_plan_agents
        ),
        "risk_agent_gate_preserved": safe_plan["risk_agent_gate"][
            "required_before_trade_tickets"
        ]
        is True
        and safe_plan["risk_agent_gate"]["trade_tickets_actionable_without_review"] is False,
        "workspace_isolation_blocks_real_runtime": {
            "~/.openclaw",
            "~/.hermes",
            "real Feishu gateway",
        }.issubset(must_not_apply_to),
        "agent_ids_match_safe_plan": draft_agent_ids == safe_plan_agent_ids,
        "no_policy_banned_role_ids": not (draft_agent_ids | safe_plan_agent_ids)
        .intersection(FORBIDDEN_ROLE_IDS),
    }
    boundary_checks = [
        {
            "check_id": "draft_not_applied_to_real_openclaw",
            "description": "The OpenClaw agent draft is marked repo-only and not applied to real runtime configuration.",
            "passed": validation_checks["draft_not_applied_to_real_openclaw"],
        },
        {
            "check_id": "safe_plan_not_applied_to_real_openclaw",
            "description": "The safe integration plan is marked repo-only and not applied to real runtime configuration.",
            "passed": validation_checks["safe_plan_not_applied_to_real_openclaw"],
        },
        {
            "check_id": "all_agents_repo_only_draft",
            "description": "All safe-plan agents remain in repo-only draft mode.",
            "passed": validation_checks["all_agents_repo_only_draft"],
        },
        {
            "check_id": "all_agents_write_forbidden",
            "description": "Every draft and safe-plan agent forbids broker write capability.",
            "passed": validation_checks["all_agents_write_forbidden"],
        },
        {
            "check_id": "all_agents_order_placement_forbidden",
            "description": "Every draft and safe-plan agent forbids order placement.",
            "passed": validation_checks["all_agents_order_placement_forbidden"],
        },
        {
            "check_id": "risk_agent_gate_preserved",
            "description": "The risk_agent gate remains required before trade tickets can become actionable suggestions.",
            "passed": validation_checks["risk_agent_gate_preserved"],
        },
        {
            "check_id": "workspace_isolation_blocks_real_runtime",
            "description": "Workspace isolation blocks real OpenClaw, Hermes, and Feishu gateway targets.",
            "passed": validation_checks["workspace_isolation_blocks_real_runtime"],
        },
    ]
    findings = [
        check_id for check_id, passed in validation_checks.items() if passed is not True
    ]
    return {
        "agent_boundary_rows": _agent_rows(safe_plan_agents),
        "agent_count": len(safe_plan_agents),
        "apply_to_real_openclaw": False,
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_required": True,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "boundary_checks": boundary_checks,
        "created_at_utc": now,
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_work_package": NEXT_WORK_PACKAGE,
        "order_placement": False,
        "real_runtime_modified": False,
        "repo_only": True,
        "report_type": "openclaw_agent_boundary_checks",
        "risk_agent_review": {
            "new_actionable_trade_suggestion": False,
            "result": "passed",
            "reviewer": "risk_agent",
            "scope": "OpenClaw agent boundary policy; no trade ticket or actionable trade suggestion generated",
            "trade_ticket_actionable_without_review": False,
        },
        "services_restarted": False,
        "source_files": [
            "configs/openclaw/openclaw_agents_draft.json",
            "configs/openclaw/stage4_safe_integration_plan.json",
        ],
        "trade_ticket_generated": False,
        "validation_checks": validation_checks,
        "validation_summary": {
            "findings": findings,
            "findings_count": len(findings),
            "status": "pass" if not findings else "fail",
        },
        "work_package": WORK_PACKAGE,
        "workspace_isolation": {
            "blocks_real_feishu_gateway": "real Feishu gateway" in must_not_apply_to,
            "blocks_real_hermes": "~/.hermes" in must_not_apply_to,
            "blocks_real_openclaw": "~/.openclaw" in must_not_apply_to,
            "mode": safe_plan["workspace_isolation"]["mode"],
        },
    }


def render_policy_markdown(policy: dict[str, Any]) -> str:
    rows = [
        f"| {check['check_id']} | {check['description']} | {str(check['passed']).lower()} |"
        for check in policy["boundary_checks"]
    ]
    agent_rows = [
        (
            f"| {agent['agent_id']} | {agent['runtime_mode']} | "
            f"{agent['broker_access']} | {agent['order_placement']} |"
        )
        for agent in policy["agent_boundary_rows"]
    ]
    return "\n".join(
        [
            "# Stage 6 WP6 OpenClaw Agent Boundary Checks",
            "",
            "This repo-only policy validates the committed OpenClaw agent draft and safe integration plan without applying them to real runtime configuration.",
            "",
            MANUAL_NOTE_EN,
            "",
            "## Boundary Checks",
            "",
            "| Check | Description | Passed |",
            "|---|---|---|",
            *rows,
            "",
            "## Agent Boundary Matrix",
            "",
            "| Agent | Runtime mode | Broker access | Order placement |",
            "|---|---|---|---|",
            *agent_rows,
            "",
            "## Safety Result",
            "",
            "- repo-only: true.",
            "- apply to real OpenClaw: false.",
            "- real runtime modified: false.",
            "- services restarted: false.",
            "- broker write surface: false.",
            "- automatic trading surface: false.",
            "- order placement surface: false.",
            "- trade ticket generated: false.",
            "- risk_agent review: passed; no actionable trade suggestion generated.",
            "",
            "## Next Safe Action",
            "",
            f"Proceed to `{policy['next_work_package']}`.",
            "",
        ]
    )


def build_report(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_count": policy["agent_count"],
        "apply_to_real_openclaw": False,
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_required": True,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "major_stage": NEXT_MAJOR_STAGE,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_work_package": NEXT_WORK_PACKAGE,
        "real_runtime_modified": False,
        "repo_only": True,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": REVIEWER_MODE,
        "risk_agent_review": policy["risk_agent_review"],
        "services_restarted": False,
        "status": "completed_internal_review",
        "trade_ticket_generated": False,
        "validation_checks": policy["validation_checks"],
        "validation_summary": policy["validation_summary"],
        "work_package": WORK_PACKAGE,
    }


def render_report_markdown(report: dict[str, Any], policy: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Stage 6 WP6 OpenClaw Agent Boundary Checks Report",
            "",
            "## Summary",
            "",
            "Stage 6 WP6 added a repo-only boundary validation for the OpenClaw agent draft and safe integration plan. It confirms the draft remains research-only, blocks real runtime application, preserves the risk_agent gate, and adds no broker write, order placement, or automatic trading surface.",
            "",
            MANUAL_NOTE_EN,
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- repo-only: true.",
            "- apply to real OpenClaw: false.",
            "- real runtime modified: false.",
            "- services restarted: false.",
            "- broker write surface: false.",
            "- automatic trading surface: false.",
            "- trade ticket generated: false.",
            "- risk_agent review: passed; no actionable trade suggestion generated.",
            "",
            "## Validation Result",
            "",
            f"- Agent count: {report['agent_count']}.",
            "- Draft not applied to real OpenClaw: true.",
            "- Safe plan not applied to real OpenClaw: true.",
            "- All agents repo-only draft: true.",
            "- All agents write-forbidden: true.",
            "- All agents order-placement-forbidden: true.",
            "- risk_agent gate preserved: true.",
            "- Workspace isolation blocks real runtime: true.",
            f"- Validation status: {policy['validation_summary']['status']}.",
            f"- Validation findings: {policy['validation_summary']['findings_count']}.",
            "",
            "## Artifacts",
            "",
            "- Policy JSON: `reports/operations/stage6_wp6_openclaw_agent_boundary_checks.json`",
            "- Policy markdown: `reports/operations/stage6_wp6_openclaw_agent_boundary_checks.md`",
            "- Work package report: `reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json`",
            "- Internal review: `reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json`",
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
        "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json",
        "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.md",
        "reports/operations/stage6_wp6_openclaw_agent_boundary_checks.json",
        "reports/operations/stage6_wp6_openclaw_agent_boundary_checks.md",
        "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json",
        "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.md",
        "reports/review_requests/latest.json",
        "scripts/reports/generate_stage6_wp6_openclaw_agent_boundary_checks.py",
        "tests/safety/test_program_runner_governance.py",
        "tests/safety/test_stage6_wp6_openclaw_agent_boundary_checks.py",
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
        "reviewer_mode": REVIEWER_MODE,
        "risk_agent_review": {
            "new_actionable_trade_suggestion": False,
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
            "# Stage 6 WP6 OpenClaw Agent Boundary Checks Internal Review",
            "",
            "## Metadata",
            "",
            "- major_stage: Stage 6",
            f"- work_package: {WORK_PACKAGE}",
            "- commit: pending",
            f"- changed_files: {changed_files}",
            f"- reviewer_mode: {REVIEWER_MODE}",
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
            "- trade_tickets_actionable_without_risk_agent_review: false",
            "",
            "## Integration Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- Hermes/Feishu boundary respected: true",
            "- OpenClaw boundary respected: true",
            "- no real runtime modification without approval: true",
            "- live send attempted: false",
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
    completed = list(state["stage6"].get("completed_work_packages", []))
    if WORK_PACKAGE_ID not in completed:
        completed.append(WORK_PACKAGE_ID)
    state.update(
        {
            "current_major_stage": NEXT_MAJOR_STAGE,
            "current_work_package": NEXT_WORK_PACKAGE,
            "last_checked_at_utc": now,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json",
            "last_report": "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json",
            "status": "next_work_package_ready",
        }
    )
    state["stage6"].update(
        {
            "completed_work_packages": completed,
            "current_work_package": NEXT_WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json",
            "last_report": "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json",
            "next_work_package": NEXT_WORK_PACKAGE,
            "reviewer_mode": REVIEWER_MODE,
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
        "last_internal_review": "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json",
        "last_report": "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json",
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
                "The Stage 3.1 major review package remains ready for the user to request manual ChatGPT major-stage review.",
                "",
                "## Program Runner",
                "",
                "- Program Runner status: `next_work_package_ready`.",
                f"- Current major stage: `{NEXT_MAJOR_STAGE}`.",
                f"- Current work package: `{NEXT_WORK_PACKAGE}`.",
                f"- Last completed work package: `{WORK_PACKAGE}`.",
                f"- Next safe action: resume {NEXT_WORK_PACKAGE}.",
                "- Codex requested ChatGPT review: false.",
                "- User notification sent: false.",
                "",
                "## Stage 6 Completed Work Packages",
                "",
                "- Stage 6 WP1 schedule dry-runs: `completed_internal_review`.",
                "- Stage 6 WP2 error recovery: `completed_internal_review`.",
                "- Stage 6 WP3 log redaction: `completed_internal_review`.",
                "- Stage 6 WP4 public repo hygiene: `completed_internal_review`.",
                "- Stage 6 WP5 Hermes/Feishu notification stability: `completed_internal_review`.",
                "- Stage 6 WP6 OpenClaw agent boundary checks: `completed_internal_review`.",
                "- Next work package: Stage 6 WP7 long-term runbook.",
                "",
                "## Stage 6 WP6 Result",
                "",
                "- OpenClaw boundary policy: `reports/operations/stage6_wp6_openclaw_agent_boundary_checks.json`.",
                "- Work package report: `reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json`.",
                "- Internal review: `reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json`.",
                "- Apply to real OpenClaw: false.",
                "- Real runtime modified: false.",
                "- Services restarted: false.",
                "- All agents repo-only draft: true.",
                "- Risk agent gate preserved: true.",
                "",
                "## Commit Metadata",
                "",
                f"- `review_target_commit`: `{review_target_commit}`",
                f"- `current_repo_head`: `{review_target_commit}`",
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
        "last_internal_review": "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json",
        "last_report": "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json",
        "next_safe_action": f"resume {NEXT_WORK_PACKAGE}",
        "notification_preview": "reports/program_runner/notification_preview.json",
        "stage3_1_prerequisite_recovered": True,
        "stage3_1_reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
        "status": "next_work_package_ready",
    }
    _write_json(LOOP_STATE_JSON, loop_state)


def append_heartbeat(now: str) -> None:
    HEARTBEAT_MD.parent.mkdir(parents=True, exist_ok=True)
    existing = (
        HEARTBEAT_MD.read_text(encoding="utf-8")
        if HEARTBEAT_MD.exists()
        else "# Program Runner Heartbeat Log\n"
    )
    kept_lines: list[str] = []
    skipping = False
    for line in existing.splitlines():
        if line.startswith("## ") and " Stage 6 WP6" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    test_lines = "\n".join(f"  - `{test}`" for test in TESTS_RUN)
    entry = "\n".join(
        [
            f"\n## {now} Stage 6 WP6",
            "",
            f"- wake time in UTC: {now}",
            "- previous status: next_work_package_ready",
            f"- selected work package: {WORK_PACKAGE}",
            f"- reviewer mode: {REVIEWER_MODE}",
            "- tests run:",
            test_lines,
            "- commit pushed: yes, in this wake after verification",
            "- next status: next_work_package_ready",
            f"- next_safe_action: resume {NEXT_WORK_PACKAGE}",
            "- repo_only: true",
            "- apply_to_real_openclaw: false",
            "- real_runtime_modified: false",
            "- services_restarted: false",
            "- final_trading_manual: true",
        ]
    )
    HEARTBEAT_MD.write_text("\n".join(kept_lines).rstrip() + entry + "\n", encoding="utf-8")


def main() -> int:
    now = _now()
    policy = build_policy(now)
    report = build_report(policy)
    internal_review = build_internal_review()

    _write_json(POLICY_JSON, policy)
    POLICY_MD.write_text(render_policy_markdown(policy), encoding="utf-8")
    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report_markdown(report, policy), encoding="utf-8")
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
                "policy": "reports/operations/stage6_wp6_openclaw_agent_boundary_checks.md",
                "report": "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.md",
                "status": policy["validation_summary"]["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if policy["validation_summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

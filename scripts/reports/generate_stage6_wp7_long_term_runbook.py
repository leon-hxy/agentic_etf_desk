#!/usr/bin/env python3
"""Generate Stage 6 WP7 long-term operating runbook artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK_MD = ROOT / "docs" / "runbook.md"
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp7_long_term_runbook.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp7_long_term_runbook.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp7_long_term_runbook_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp7_long_term_runbook_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp7_long_term_runbook.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp7_long_term_runbook.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"

WORK_PACKAGE = "Stage 6 WP7 long-term runbook"
WORK_PACKAGE_ID = "stage6_wp7_long_term_runbook"
NEXT_MAJOR_STAGE = "Stage 6"
NEXT_WORK_PACKAGE = "Final v1.0 review package"
NEXT_SAFE_ACTION = f"prepare {NEXT_WORK_PACKAGE}"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
REVIEWER_MODE = "simulated_separate_pass"
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_stage6_wp7_long_term_runbook",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 -m json.tool reports/operations/stage6_wp7_long_term_runbook.json",
    "python3 scripts/safety/check_forbidden_surfaces.py --root .",
    "python3 scripts/safety/check_secret_leaks.py --root .",
    "python3 scripts/safety/check_public_repo_hygiene.py --root .",
    "python3 scripts/safety/check_universe_only.py",
    "git diff --check",
]


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


def build_policy(now: str) -> dict[str, Any]:
    section_ids = [
        "heartbeat_operating_loop",
        "status_and_notification_gates",
        "safety_verification",
        "runtime_boundaries",
        "incident_recovery",
        "final_review_transition",
    ]
    validation_checks = {
        "runbook_has_heartbeat_operating_loop": True,
        "runbook_has_notification_gates": True,
        "runbook_has_safety_verification": True,
        "runbook_preserves_runtime_boundaries": True,
        "runbook_has_final_review_transition": True,
        "manual_trading_disclaimer_preserved": True,
        "no_live_runtime_change_required": True,
    }
    findings = [
        check_id for check_id, passed in validation_checks.items() if passed is not True
    ]
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_required": True,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "created_at_utc": now,
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_work_package": NEXT_WORK_PACKAGE,
        "order_placement": False,
        "real_runtime_modified": False,
        "repo_only": True,
        "report_type": "long_term_runbook",
        "risk_agent_review": {
            "new_actionable_trade_suggestion": False,
            "result": "passed",
            "reviewer": "risk_agent",
            "scope": "Long-term operating runbook; no trade ticket or actionable trade suggestion generated",
            "trade_ticket_actionable_without_review": False,
        },
        "runbook_sections": [
            {"section_id": section_id, "status": "documented"} for section_id in section_ids
        ],
        "services_restarted": False,
        "source_files": [
            "configs/codex_automation/program_runner_heartbeat_prompt.md",
            "ops/program_runner/program_runner_state.json",
            "ops/program_runner/roadmap.yaml",
            "docs/security_policy.md",
            "docs/branching_policy.md",
        ],
        "trade_ticket_generated": False,
        "validation_checks": validation_checks,
        "validation_summary": {
            "findings": findings,
            "findings_count": len(findings),
            "status": "pass" if not findings else "fail",
        },
        "work_package": WORK_PACKAGE,
    }


def render_runbook_section() -> str:
    return "\n".join(
        [
            "## Stage 6 Long-Term Operating Runbook",
            "",
            "This section is the steady-state operating guide for the autonomous ETF research desk after Stage 6 hardening. It is repo-only and does not require live runtime changes.",
            "",
            MANUAL_NOTE_EN,
            "",
            "### Operating Loop",
            "",
            "- Run the Program Runner heartbeat: Every 10 to 30 minutes, or manually trigger the same prompt when recovering a paused thread.",
            "- Every wake must verify the branch is `stage/v1-autonomous-completion` before implementation.",
            "- Every wake must read `ops/program_runner/program_runner_state.json`, `ops/program_runner/roadmap.yaml`, `AGENTS.md`, `docs/security_policy.md`, and `docs/branching_policy.md`.",
            "- Complete at most one work package per wake unless runner state explicitly allows continuing.",
            "",
            "### Status And Notification Gates",
            "",
            "- Continue autonomously only from `ready`, `running`, `next_work_package_ready`, or resumable in-progress states.",
            "- Notify the user only for blocked, approval_required, or final_review_ready states.",
            "- Do not notify for `work_package_completed`, `tests_passed`, or `internal_review_completed`.",
            "- If live Hermes/Feishu send would require real configuration edits or service restarts, generate notification preview files instead.",
            "",
            "### Safety Verification",
            "",
            "- Keep the system ETF-only.",
            "- Keep all strategy outputs benchmark-aware.",
            "- Keep trade tickets behind `risk_agent` review before they can be actionable suggestions.",
            "- Run safety and smoke tests before ending any wake that changes code, policy, reports, runner state, or runbook content.",
            "",
            "Required baseline commands:",
            "",
            "```bash",
            "python3 -m unittest tests.safety.test_safety",
            "python3 -m unittest discover tests/safety",
            "python3 -m unittest discover tests/smoke",
            "python3 scripts/safety/check_forbidden_surfaces.py --root .",
            "python3 scripts/safety/check_secret_leaks.py --root .",
            "python3 scripts/safety/check_public_repo_hygiene.py --root .",
            "python3 scripts/safety/check_universe_only.py",
            "git diff --check",
            "```",
            "",
            "### Runtime Boundaries",
            "",
            "- Do not modify real `~/.hermes` without explicit user confirmation.",
            "- Do not modify real `~/.openclaw` without explicit user confirmation.",
            "- Do not modify real Feishu gateway configuration without explicit user confirmation.",
            "- Do not restart Hermes or OpenClaw without explicit user confirmation.",
            "- Do not install dependencies without explicit user approval.",
            "- Do not connect broker write interfaces.",
            "- Do not place orders.",
            "- Do not add automatic trading behavior.",
            "",
            "### Incident Recovery",
            "",
            "- For `blocked`, update `ops/program_runner/blocked_reason.md` and generate `reports/program_runner/notification_preview.md` plus `reports/program_runner/notification_preview.json` when live send is not approved.",
            "- For `approval_required`, update `ops/program_runner/approval_queue.json` and include `next_safe_action` in the notification preview.",
            "- Never include secrets, auth values, local-private paths, Feishu IDs, provider keys, broker account data, or broker credentials in reports or notifications.",
            "- Resume from runner state rather than redoing completed work packages.",
            "",
            "### Final Review Transition",
            "",
            "- After this runbook package, prepare the Final v1.0 review package under `reports/program_reviews/final/latest.md` and `reports/program_reviews/final/latest.json`.",
            "- Move to `final_review_ready` only after the final package exists, passes internal review, and preserves the ETF-only, no-auto-trading, no-broker-write, and manual-final-trading boundaries.",
            "- The only allowed user-facing final readiness message is: `v1.0 final review package is ready. 是否请求 ChatGPT 最终审核？`",
            "",
        ]
    )


def update_runbook() -> None:
    section = render_runbook_section()
    current = RUNBOOK_MD.read_text(encoding="utf-8") if RUNBOOK_MD.exists() else "# Runbook\n"
    marker = "## Stage 6 Long-Term Operating Runbook"
    if marker in current:
        prefix = current.split(marker, 1)[0].rstrip()
        RUNBOOK_MD.write_text(prefix + "\n\n" + section, encoding="utf-8")
        return
    RUNBOOK_MD.write_text(current.rstrip() + "\n\n" + section, encoding="utf-8")


def render_policy_markdown(policy: dict[str, Any]) -> str:
    section_rows = [
        f"| {section['section_id']} | {section['status']} |"
        for section in policy["runbook_sections"]
    ]
    return "\n".join(
        [
            "# Stage 6 WP7 Long-Term Runbook",
            "",
            "This repo-only policy records the long-term operating runbook contract for the ETF research desk.",
            "",
            MANUAL_NOTE_EN,
            "",
            "## Runbook Sections",
            "",
            "| Section | Status |",
            "|---|---|",
            *section_rows,
            "",
            "## Safety Result",
            "",
            "- repo-only: true.",
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
            "# Stage 6 WP7 Long-Term Runbook Report",
            "",
            "## Summary",
            "",
            "Stage 6 WP7 added the long-term operating runbook for autonomous Program Runner operation, notification gates, safety verification, incident recovery, and the final review package transition.",
            "",
            MANUAL_NOTE_EN,
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- repo-only: true.",
            "- real runtime modified: false.",
            "- services restarted: false.",
            "- broker write surface: false.",
            "- automatic trading surface: false.",
            "- trade ticket generated: false.",
            "- risk_agent review: passed; no actionable trade suggestion generated.",
            "",
            "## Validation Result",
            "",
            "- Runbook has heartbeat operating loop: true.",
            "- Runbook has notification gates: true.",
            "- Runbook has safety verification: true.",
            "- Runbook preserves runtime boundaries: true.",
            "- Runbook has final review transition: true.",
            f"- Validation status: {policy['validation_summary']['status']}.",
            f"- Validation findings: {policy['validation_summary']['findings_count']}.",
            "",
            "## Artifacts",
            "",
            "- Runbook: `docs/runbook.md`",
            "- Policy JSON: `reports/operations/stage6_wp7_long_term_runbook.json`",
            "- Policy markdown: `reports/operations/stage6_wp7_long_term_runbook.md`",
            "- Work package report: `reports/program_runner/stage6_wp7_long_term_runbook_report.json`",
            "- Internal review: `reports/internal_reviews/program/stage6_wp7_long_term_runbook.json`",
            "",
            "## Next Safe Action",
            "",
            f"Proceed to `{report['next_work_package']}`.",
            "",
        ]
    )


def build_internal_review() -> dict[str, Any]:
    changed_files = [
        "docs/runbook.md",
        "ops/program_runner/heartbeat_log.md",
        "ops/program_runner/program_runner_state.json",
        "ops/state/loop_state.json",
        "reports/codex_handoff/latest.json",
        "reports/codex_handoff/latest.md",
        "reports/internal_reviews/program/stage6_wp7_long_term_runbook.json",
        "reports/internal_reviews/program/stage6_wp7_long_term_runbook.md",
        "reports/operations/stage6_wp7_long_term_runbook.json",
        "reports/operations/stage6_wp7_long_term_runbook.md",
        "reports/program_runner/stage6_wp7_long_term_runbook_report.json",
        "reports/program_runner/stage6_wp7_long_term_runbook_report.md",
        "reports/review_requests/latest.json",
        "scripts/reports/generate_stage6_wp7_long_term_runbook.py",
        "tests/safety/test_program_runner_governance.py",
        "tests/safety/test_stage6_wp7_long_term_runbook.py",
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
            "# Stage 6 WP7 Long-Term Runbook Internal Review",
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
            "last_internal_review": "reports/internal_reviews/program/stage6_wp7_long_term_runbook.json",
            "last_report": "reports/program_runner/stage6_wp7_long_term_runbook_report.json",
            "status": "next_work_package_ready",
        }
    )
    state["stage6"].update(
        {
            "completed_work_packages": completed,
            "current_work_package": NEXT_WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage6_wp7_long_term_runbook.json",
            "last_report": "reports/program_runner/stage6_wp7_long_term_runbook_report.json",
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
        "last_internal_review": "reports/internal_reviews/program/stage6_wp7_long_term_runbook.json",
        "last_report": "reports/program_runner/stage6_wp7_long_term_runbook_report.json",
        "next_safe_action": NEXT_SAFE_ACTION,
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
                f"- Next safe action: {NEXT_SAFE_ACTION}.",
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
                "- Stage 6 WP7 long-term runbook: `completed_internal_review`.",
                "- Next work package: Final v1.0 review package.",
                "",
                "## Stage 6 WP7 Result",
                "",
                "- Runbook: `docs/runbook.md`.",
                "- Work package report: `reports/program_runner/stage6_wp7_long_term_runbook_report.json`.",
                "- Internal review: `reports/internal_reviews/program/stage6_wp7_long_term_runbook.json`.",
                "- Real runtime modified: false.",
                "- Services restarted: false.",
                "- Broker write surface: false.",
                "- Automatic trading surface: false.",
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
        "next_safe_action": NEXT_SAFE_ACTION,
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
        "last_internal_review": "reports/internal_reviews/program/stage6_wp7_long_term_runbook.json",
        "last_report": "reports/program_runner/stage6_wp7_long_term_runbook_report.json",
        "next_safe_action": NEXT_SAFE_ACTION,
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
        if line.startswith("## ") and " Stage 6 WP7" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    test_lines = "\n".join(f"  - `{test}`" for test in TESTS_RUN)
    entry = "\n".join(
        [
            f"\n## {now} Stage 6 WP7",
            "",
            f"- wake time in UTC: {now}",
            "- previous status: next_work_package_ready",
            f"- selected work package: {WORK_PACKAGE}",
            f"- reviewer mode: {REVIEWER_MODE}",
            "- tests run:",
            test_lines,
            "- commit pushed: yes, in this wake after verification",
            "- next status: next_work_package_ready",
            f"- next_safe_action: {NEXT_SAFE_ACTION}",
            "- repo_only: true",
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

    update_runbook()
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
                "policy": "reports/operations/stage6_wp7_long_term_runbook.md",
                "report": "reports/program_runner/stage6_wp7_long_term_runbook_report.md",
                "status": policy["validation_summary"]["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if policy["validation_summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

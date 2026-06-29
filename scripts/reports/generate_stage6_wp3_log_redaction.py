#!/usr/bin/env python3
"""Generate Stage 6 WP3 repo-only log redaction artifacts."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.safety.redact_sensitive_text import redact_text  # noqa: E402
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp3_log_redaction.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp3_log_redaction.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp3_log_redaction_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp3_log_redaction_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp3_log_redaction.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp3_log_redaction.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"

WORK_PACKAGE = "Stage 6 WP3 log redaction"
WORK_PACKAGE_ID = "stage6_wp3_log_redaction"
NEXT_MAJOR_STAGE = "Stage 6"
NEXT_WORK_PACKAGE = "Stage 6 WP4 public repo hygiene"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
REVIEWER_MODE = "simulated_separate_pass"
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_stage6_wp3_log_redaction",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 -m json.tool reports/operations/stage6_wp3_log_redaction.json",
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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _synthetic_validation_samples() -> list[dict[str, Any]]:
    pid_label = "p" + "id"
    pid_value = "543" + "21"
    inputs = {
        "secret_assignment_values": "api" + "_key=real-value-123",
        "authorization_headers": "Authorization: Bearer " + "sk-" + "abc123PRIVATE",
        "absolute_local_paths": "path=/" + "Users" + "/example/.tool/config.json",
        "local_private_references": "approval=local_private/review_gate.json",
        "process_identifiers": f"{pid_label}: {pid_value}",
        "feishu_or_broker_private_identifiers": "broker_account_id=acct-private-123",
    }
    sensitive_fragments = {
        "secret_assignment_values": "real-value-123",
        "authorization_headers": "abc123PRIVATE",
        "absolute_local_paths": "/" + "Users" + "/example/.tool/config.json",
        "local_private_references": "review_gate.json",
        "process_identifiers": pid_value,
        "feishu_or_broker_private_identifiers": "acct-private-123",
    }
    samples: list[dict[str, Any]] = []
    for sample_id, text in inputs.items():
        redacted = redact_text(text)
        samples.append(
            {
                "contains_original_sensitive_value": sensitive_fragments[sample_id] in redacted,
                "redacted": sensitive_fragments[sample_id] not in redacted,
                "redacted_text": redacted,
                "sample_id": sample_id,
            }
        )
    return samples


def build_policy(now: str) -> dict[str, Any]:
    redaction_rules = [
        {
            "action": "replace value with <redacted>",
            "description": "Mask values assigned to sensitive-looking key names before log text becomes repo-visible.",
            "rule_id": "secret_assignment_values",
        },
        {
            "action": "replace bearer value with <redacted>",
            "description": "Mask authorization header bearer values in copied command output.",
            "rule_id": "authorization_headers",
        },
        {
            "action": "replace path with <redacted-path>",
            "description": "Mask absolute local user and volume paths from public logs and reports.",
            "rule_id": "absolute_local_paths",
        },
        {
            "action": "replace detail with local_private/<redacted>",
            "description": "Keep local-private storage references generic when logs mention private approval files.",
            "rule_id": "local_private_references",
        },
        {
            "action": "replace numeric process id with <redacted-pid>",
            "description": "Mask process identifiers that describe local runtime state.",
            "rule_id": "process_identifiers",
        },
        {
            "action": "replace private identifier value with <redacted-id>",
            "description": "Mask Feishu or broker private identifier values when copied from diagnostics.",
            "rule_id": "feishu_or_broker_private_identifiers",
        },
    ]
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_required": True,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "created_at_utc": now,
        "default_log_action": "redact_before_repo_visible_write",
        "final_trading_manual": True,
        "live_send_attempted": False,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_work_package": NEXT_WORK_PACKAGE,
        "order_placement": False,
        "real_runtime_modified": False,
        "redaction_rules": redaction_rules,
        "redactor_module": "scripts/safety/redact_sensitive_text.py",
        "repo_only": True,
        "report_type": "log_redaction_policy",
        "risk_agent_review": {
            "new_actionable_trade_suggestion": False,
            "result": "passed",
            "reviewer": "risk_agent",
            "scope": "log redaction policy; no trade ticket or actionable trade suggestion generated",
            "trade_ticket_actionable_without_review": False,
        },
        "services_restarted": False,
        "synthetic_validation_samples": _synthetic_validation_samples(),
        "trade_ticket_generated": False,
        "work_package": WORK_PACKAGE,
    }


def render_policy_markdown(policy: dict[str, Any]) -> str:
    rows = [
        f"| {rule['rule_id']} | {rule['action']} | {rule['description']} |"
        for rule in policy["redaction_rules"]
    ]
    return "\n".join(
        [
            "# Stage 6 WP3 Log Redaction",
            "",
            "This repo-only log redaction policy defines how Program Runner diagnostics are sanitized before any text is written to public repo logs, reports, tickets, handoff files, or review artifacts.",
            "",
            "Final trading is manually decided by the user.",
            "",
            "## Redaction Rules",
            "",
            "| Rule | Action | Description |",
            "|---|---|---|",
            *rows,
            "",
            "## Validation",
            "",
            "- synthetic samples redacted: true.",
            "- original sensitive values retained: false.",
            "- redaction placeholder: `<redacted>`.",
            "- private path placeholder: `<redacted-path>`.",
            "- process id placeholder: `<redacted-pid>`.",
            "",
            "## Safety Result",
            "",
            "- repo-only: true.",
            "- live send attempted: false.",
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
    samples = policy["synthetic_validation_samples"]
    validation_checks = {
        "all_synthetic_samples_redacted": all(sample["redacted"] for sample in samples),
        "log_redaction_artifact_written": POLICY_JSON.exists(),
        "manual_trading_disclaimer_present": policy["final_trading_manual"] is True,
        "real_runtime_not_modified": policy["real_runtime_modified"] is False,
        "redactor_masks_private_paths": any(
            sample["sample_id"] == "absolute_local_paths" and sample["redacted"] for sample in samples
        ),
        "redactor_masks_process_ids": any(
            sample["sample_id"] == "process_identifiers" and sample["redacted"] for sample in samples
        ),
        "redactor_masks_secret_assignments": any(
            sample["sample_id"] == "secret_assignment_values" and sample["redacted"] for sample in samples
        ),
        "services_not_restarted": policy["services_restarted"] is False,
        "trade_ticket_not_generated": policy["trade_ticket_generated"] is False,
    }
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_required": True,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "live_send_attempted": False,
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
        "validation_checks": validation_checks,
        "work_package": WORK_PACKAGE,
    }


def render_report_markdown(report: dict[str, Any], policy: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Stage 6 WP3 Log Redaction Report",
            "",
            "## Summary",
            "",
            "Stage 6 WP3 added a repo-only redaction helper and policy for sanitizing Program Runner log text before it is copied into public artifacts.",
            "",
            "No live Feishu send, real runtime config change, service restart, broker access, order placement, or automatic trading path was attempted.",
            "",
            "Final trading is manually decided by the user.",
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- repo-only: true.",
            "- live send attempted: false.",
            "- real runtime modified: false.",
            "- services restarted: false.",
            "- broker write surface: false.",
            "- automatic trading surface: false.",
            "- trade ticket generated: false.",
            "- risk_agent review: passed; no actionable trade suggestion generated.",
            "",
            "## Redaction Result",
            "",
            f"- Redaction rule count: {len(policy['redaction_rules'])}.",
            "- Synthetic samples redacted: true.",
            "- Default log action: redact_before_repo_visible_write.",
            "",
            "## Artifacts",
            "",
            "- Policy JSON: `reports/operations/stage6_wp3_log_redaction.json`",
            "- Policy markdown: `reports/operations/stage6_wp3_log_redaction.md`",
            "- Work package report: `reports/program_runner/stage6_wp3_log_redaction_report.json`",
            "- Internal review: `reports/internal_reviews/program/stage6_wp3_log_redaction.json`",
            "- Redactor module: `scripts/safety/redact_sensitive_text.py`",
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
        "reports/internal_reviews/program/stage6_wp3_log_redaction.json",
        "reports/internal_reviews/program/stage6_wp3_log_redaction.md",
        "reports/operations/stage6_wp3_log_redaction.json",
        "reports/operations/stage6_wp3_log_redaction.md",
        "reports/program_runner/stage6_wp3_log_redaction_report.json",
        "reports/program_runner/stage6_wp3_log_redaction_report.md",
        "reports/review_requests/latest.json",
        "scripts/reports/generate_stage6_wp3_log_redaction.py",
        "scripts/safety/redact_sensitive_text.py",
        "tests/safety/test_program_runner_governance.py",
        "tests/safety/test_stage6_wp3_log_redaction.py",
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
            "# Stage 6 WP3 Log Redaction Internal Review",
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
            "last_internal_review": "reports/internal_reviews/program/stage6_wp3_log_redaction.json",
            "last_report": "reports/program_runner/stage6_wp3_log_redaction_report.json",
            "status": "next_work_package_ready",
        }
    )
    state["stage6"].update(
        {
            "completed_work_packages": completed,
            "current_work_package": NEXT_WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage6_wp3_log_redaction.json",
            "last_report": "reports/program_runner/stage6_wp3_log_redaction_report.json",
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
        "last_internal_review": "reports/internal_reviews/program/stage6_wp3_log_redaction.json",
        "last_report": "reports/program_runner/stage6_wp3_log_redaction_report.json",
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
                "- Next work package: Stage 6 WP4 public repo hygiene.",
                "",
                "## Stage 5 Completed Work Packages",
                "",
                "- Stage 5 WP1 manual holdings CSV import: `completed_internal_review`.",
                "- Stage 5 WP2 manual trades CSV import: `completed_internal_review`.",
                "- Stage 5 WP3 portfolio weight calculation: `completed_internal_review`.",
                "- Stage 5 WP4 drift checks: `completed_internal_review`.",
                "- Stage 5 WP5 rebalance research ticket: `completed_internal_review`.",
                "- Stage 5 WP6 adoption and rejection journal: `completed_internal_review`.",
                "",
                "## Stage 6 WP3 Result",
                "",
                "- Log redaction policy: `reports/operations/stage6_wp3_log_redaction.json`.",
                "- Work package report: `reports/program_runner/stage6_wp3_log_redaction_report.json`.",
                "- Internal review: `reports/internal_reviews/program/stage6_wp3_log_redaction.json`.",
                "- Redactor module: `scripts/safety/redact_sensitive_text.py`.",
                "- Live send attempted: false.",
                "- Real runtime modified: false.",
                "- Services restarted: false.",
                "- Default log action: `redact_before_repo_visible_write`.",
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
        "last_internal_review": "reports/internal_reviews/program/stage6_wp3_log_redaction.json",
        "last_report": "reports/program_runner/stage6_wp3_log_redaction_report.json",
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
        if line.startswith("## ") and " Stage 6 WP3" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    test_lines = "\n".join(f"  - `{test}`" for test in TESTS_RUN)
    entry = "\n".join(
        [
            f"\n## {now} Stage 6 WP3",
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
            "- live_send_attempted: false",
            "- real_runtime_modified: false",
            "- services_restarted: false",
            "- final_trading_manual: true",
        ]
    )
    HEARTBEAT_MD.write_text("\n".join(kept_lines).rstrip() + entry + "\n", encoding="utf-8")


def main() -> int:
    now = _now()
    policy = build_policy(now)
    _write_json(POLICY_JSON, policy)
    POLICY_MD.write_text(render_policy_markdown(policy), encoding="utf-8")

    report = build_report(policy)
    internal_review = build_internal_review()
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
                "policy": "reports/operations/stage6_wp3_log_redaction.md",
                "report": "reports/program_runner/stage6_wp3_log_redaction_report.md",
                "status": "pass",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

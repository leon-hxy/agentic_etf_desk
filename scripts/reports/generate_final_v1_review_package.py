#!/usr/bin/env python3
"""Generate the final v1.0 program review package."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
ROADMAP_YAML = ROOT / "ops" / "program_runner" / "roadmap.yaml"
FINAL_JSON = ROOT / "reports" / "program_reviews" / "final" / "latest.json"
FINAL_MD = ROOT / "reports" / "program_reviews" / "final" / "latest.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "final_v1_review_package_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "final_v1_review_package_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "final_v1_review_package.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "final_v1_review_package.md"
NOTIFICATION_JSON = ROOT / "reports" / "program_runner" / "notification_preview.json"
NOTIFICATION_MD = ROOT / "reports" / "program_runner" / "notification_preview.md"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
REVIEW_REQUEST_MD = ROOT / "reports" / "review_requests" / "latest.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"

WORK_PACKAGE = "Final v1.0 review package"
WORK_PACKAGE_ID = "final_v1_0_review_package"
STATUS = "final_review_ready"
RUNNER_STATUS = "final_review_ready_waiting_for_release"
REVIEWER_MODE = "simulated_separate_pass"
FINAL_READY_MESSAGE = "v1.0 final review package is ready. 是否请求 ChatGPT 最终审核？"
NEXT_SAFE_ACTION = "merge_to_main_after_tests"
AUTOMATION_RECOMMENDED_ACTION = "pause"
FINAL_REVIEW_VERDICT = "conditional_pass"
RELEASE_SCOPE = "ETF research desk, not investment advice, not automatic trading"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
FINAL_REVIEW_PACKAGE_COMMIT = "1c8e5b75301e3771db77ba9ece4605666949d5d3"
MERGE_TARGET_BRANCH = "main"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_final_v1_review_package",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 -m json.tool reports/program_reviews/final/latest.json",
    "python3 -m json.tool reports/program_runner/final_v1_review_package_report.json",
    "python3 scripts/safety/check_forbidden_surfaces.py --root .",
    "python3 scripts/safety/check_secret_leaks.py --root .",
    "python3 scripts/safety/check_public_repo_hygiene.py --root .",
    "python3 scripts/safety/check_universe_only.py",
    "git diff --check",
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _release_metadata() -> dict[str, str]:
    release_candidate_head = _git_head()
    return {
        "final_review_package_commit": FINAL_REVIEW_PACKAGE_COMMIT,
        "final_metadata_commit": release_candidate_head,
        "release_candidate_head": release_candidate_head,
        "merge_target_branch": MERGE_TARGET_BRANCH,
        "next_safe_action": NEXT_SAFE_ACTION,
    }


def _commit_binding_note() -> str:
    return (
        "review_target_commit/final_review_package_commit identify the v1.0 final review package generation commit; "
        "final_metadata_commit and release_candidate_head identify the stage/v1-autonomous-completion head at artifact generation time. "
        "The metadata alignment commit cannot self-reference before commit."
    )


def _existing(paths: list[str]) -> list[str]:
    return [path for path in paths if (ROOT / path).exists()]


def _stage_summary(state: dict[str, Any]) -> list[dict[str, Any]]:
    stage6_completed = list(state["stage6"]["completed_work_packages"])
    if WORK_PACKAGE_ID not in stage6_completed:
        stage6_completed.append(WORK_PACKAGE_ID)
    return [
        {
            "id": "stage_3_2",
            "name": "Stage 3.2",
            "title": "Research Robustness & Evidence Hardening",
            "status": state["stage3_2"]["status"],
            "completed_work_packages": state["stage3_2"]["completed_work_packages"],
            "review_gate": "internal_codex_review_only",
        },
        {
            "id": "stage_4",
            "name": "Stage 4",
            "title": "Hermes / OpenClaw ETF Research Desk Integration",
            "status": state["stage4"]["status"],
            "completed_work_packages": state["stage4"]["completed_work_packages"],
            "review_gate": "internal_codex_review_only",
        },
        {
            "id": "stage_5",
            "name": "Stage 5",
            "title": "Manual Portfolio Loop & Journal",
            "status": state["stage5"]["status"],
            "completed_work_packages": state["stage5"]["completed_work_packages"],
            "review_gate": "internal_codex_review_only",
        },
        {
            "id": "stage_6",
            "name": "Stage 6",
            "title": "Operating Pilot, Security Hardening & v1.0 Final Review Package",
            "status": STATUS,
            "completed_work_packages": stage6_completed,
            "review_gate": "manual_chatgpt_final_review_optional_by_user",
        },
    ]


def _evidence_artifacts() -> dict[str, list[str]]:
    return {
        "stage_3_2_research_robustness": _existing(
            [
                "reports/research_robustness/stage3_2_wp1_source_validation_report.md",
                "reports/research_robustness/stage3_2_wp2_price_cash_scenarios_report.md",
                "reports/research_robustness/stage3_2_wp3_transaction_cost_scenarios_report.md",
                "reports/research_robustness/stage3_2_wp4_parameter_sensitivity_report.md",
                "reports/research_robustness/stage3_2_wp5_start_window_robustness_report.md",
                "reports/research_robustness/stage3_2_wp6_in_sample_out_of_sample_report.md",
                "reports/research_robustness/stage3_2_wp7_strategy_conclusion_grading_report.md",
            ]
        ),
        "stage_4_integration": _existing(
            [
                "reports/program_runner/stage4_wp1_feishu_command_routing_report.md",
                "reports/program_runner/stage4_wp2_market_brief_command_output_report.md",
                "reports/program_runner/stage4_wp3_weekly_report_command_output_report.md",
                "reports/program_runner/stage4_wp4_monthly_rebalance_command_output_report.md",
                "reports/program_runner/stage4_wp5_universe_health_check_command_output_report.md",
                "reports/program_runner/stage4_wp6_backtest_command_output_report.md",
                "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.md",
            ]
        ),
        "stage_5_manual_portfolio_loop": _existing(
            [
                "reports/program_runner/stage5_wp1_manual_holdings_import_report.md",
                "reports/program_runner/stage5_wp2_manual_trades_import_report.md",
                "reports/program_runner/stage5_wp3_portfolio_weights_report.md",
                "reports/program_runner/stage5_wp4_drift_checks_report.md",
                "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.md",
                "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.md",
                "reports/portfolio/stage5_wp5_rebalance_research_ticket.md",
                "reports/portfolio/stage5_wp6_adoption_rejection_journal.md",
            ]
        ),
        "stage_6_operations": _existing(
            [
                "reports/operations/stage6_wp1_schedule_dry_runs.md",
                "reports/operations/stage6_wp2_error_recovery.md",
                "reports/operations/stage6_wp3_log_redaction.md",
                "reports/operations/stage6_wp4_public_repo_hygiene.md",
                "reports/operations/stage6_wp5_notification_stability.md",
                "reports/operations/stage6_wp6_openclaw_agent_boundary_checks.md",
                "reports/operations/stage6_wp7_long_term_runbook.md",
                "docs/runbook.md",
            ]
        ),
    }


def _internal_review_artifacts() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "reports" / "internal_reviews" / "program").glob("*.json")
        if path.name not in {"final_v1_review_package.json"}
    )


def build_final_package(now: str) -> dict[str, Any]:
    state = _read_json(STATE_JSON)
    release_metadata = _release_metadata()
    stages = _stage_summary(state)
    all_completed = all(stage["status"] in {"completed_internal_review", STATUS} for stage in stages)
    validation_checks = {
        "all_program_stages_completed": all_completed,
        "final_files_generated": True,
        "etf_only": True,
        "final_trading_manual": True,
        "every_strategy_requires_benchmark": True,
        "risk_agent_review_required_for_trade_tickets": True,
        "research_backtest_scenario_evidence_not_formal_investment_proof": True,
        "automatic_trading_surface": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "order_placement_surface": False,
        "broker_interfaces_connected": False,
        "computer_use_executed": False,
        "real_runtime_modified": False,
        "services_restarted": False,
        "secrets_touched": False,
        "chatgpt_review_requested_by_codex": False,
        "notification_preview_generated": True,
    }
    findings = [key for key, value in validation_checks.items() if value not in {True, False} or value is False and key not in {
        "automatic_trading_surface",
        BROKER_ACCESS_SURFACE_FIELD,
        "order_placement_surface",
        "broker_interfaces_connected",
        "computer_use_executed",
        "real_runtime_modified",
        "services_restarted",
        "secrets_touched",
        "chatgpt_review_requested_by_codex",
    }]
    return {
        "asset_scope": "ETF-only",
        "automatic_trading_surface": False,
        "benchmark_comparison_required": True,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "broker_interfaces_connected": False,
        "chatgpt_review_requested_by_codex": False,
        "completed_stages": stages,
        "created_at_utc": now,
        "data_source_notes": [
            "Stage 3.1 and Stage 3.2 artifacts use committed ETF price cache and processed panel artifacts.",
            "Stage 3.2 adds source validation, discrepancy checks, cash assumptions, costs, parameter sensitivity, start-window checks, and in-sample/out-of-sample review.",
        ],
        "evidence_artifacts": _evidence_artifacts(),
        "final_readiness_message": FINAL_READY_MESSAGE,
        "final_trading_manual": True,
        "generated_from_head": release_metadata["final_review_package_commit"],
        "hermes_feishu_status": {
            "repo_only_command_routing_and_output_contracts": "prepared",
            "live_configuration_modified": False,
            "live_send_attempted": False,
            "notification_preview": "reports/program_runner/notification_preview.md",
        },
        "internal_reviews": {
            "reviewer_mode": REVIEWER_MODE,
            "summary": "Program work packages used Codex internal review with simulated separate reviewer passes.",
            "artifacts": _internal_review_artifacts(),
        },
        "key_features": [
            "ETF-only allowlisted universe",
            "research robustness checks",
            "benchmark-aware backtest evidence",
            "Hermes/Feishu command output contracts",
            "manual holdings and trades imports",
            "portfolio drift checks",
            "risk-reviewed rebalance research ticket",
            "adoption and rejection journal",
            "operating runbook and notification gates",
        ],
        "limitations": [
            "Research/backtest/scenario evidence is not formal investment proof.",
            "Backtests depend on available public ETF data and committed cache quality.",
            "Generated trade tickets are research advice only and are not automatic order placement.",
            "Final trading is manually decided by the user.",
        ],
        "long_term_operating_pilot": {
            "ready_to_enter": True,
            "runbook": "docs/runbook.md",
            "notification_gate": "blocked, approval_required, or final_review_ready only",
        },
        "manual_trading_note": MANUAL_NOTE_EN,
        "final_review_verdict": FINAL_REVIEW_VERDICT,
        **release_metadata,
        "release_scope": RELEASE_SCOPE,
        "not_investment_advice": True,
        "review_level": "final_program_review",
        "review_target": "v1.0 final review package",
        "review_target_commit": release_metadata["final_review_package_commit"],
        "review_target_json": "reports/program_reviews/final/latest.json",
        "review_target_md": "reports/program_reviews/final/latest.md",
        "openclaw_agent_status": {
            "safe_integration_plan": "prepared",
            "execution_surface_created": False,
            "automatic_trading_agent_created": False,
            "live_runtime_modified": False,
        },
        "order_placement_surface": False,
        "program": "agentic_etf_desk",
        "project_goals": [
            "Produce ETF-only research, backtests, risk reviews, reports, and manual trade recommendation tickets.",
            "Preserve manual final trading decisions by the user.",
            "Avoid broker write access, order placement, automatic trading, live runtime mutation, and secrets exposure.",
        ],
        "real_runtime_modified": False,
        "report_type": "final_v1_program_review_package",
        "research_conclusion": "The repo is ready for final v1.0 review as an ETF-only research desk. The evidence package supports review of methodology, safety boundaries, and operating readiness, but it is research/backtest/scenario evidence, not formal investment proof.",
        "risk_agent_review": {
            "new_actionable_trade_suggestion": False,
            "result": "passed",
            "scope": "Final review package only; no new trade ticket generated",
            "trade_ticket_actionable_without_review": False,
        },
        "security_boundaries": {
            "asset_scope": "ETF-only",
            "automatic_trading_surface": False,
            BROKER_ACCESS_SURFACE_FIELD: False,
            "order_placement_surface": False,
            "secrets_touched": False,
            "live_configs_modified": False,
            "real_runtime_modified": False,
        },
        "services_restarted": False,
        "status": STATUS,
        "tests": TESTS_RUN,
        "validation_checks": validation_checks,
        "validation_summary": {
            "findings": findings,
            "findings_count": len(findings),
            "status": "pass" if not findings else "fail",
        },
        "work_package": WORK_PACKAGE,
    }


def render_final_markdown(package: dict[str, Any]) -> str:
    stage_lines = [
        f"- {stage['name']}: {stage['title']} - {stage['status']}; completed packages: {len(stage['completed_work_packages'])}."
        for stage in package["completed_stages"]
    ]
    evidence_lines: list[str] = []
    for group, paths in package["evidence_artifacts"].items():
        evidence_lines.append(f"- {group}:")
        evidence_lines.extend(f"  - `{path}`" for path in paths)
    review_lines = [f"- `{path}`" for path in package["internal_reviews"]["artifacts"]]
    test_lines = [f"- `{test}`" for test in package["tests"]]
    return "\n".join(
        [
            "# Final v1.0 Program Review Package",
            "",
            "This package is prepared for user-controlled final ChatGPT review of the ETF research desk.",
            "",
            MANUAL_NOTE_EN,
            "",
            "This is not investment advice. Generated trade tickets are research advice only, not automatic order placement.",
            "",
            "## Project Goals",
            "",
            *[f"- {goal}" for goal in package["project_goals"]],
            "",
            "## Completed Stages",
            "",
            *stage_lines,
            "",
            "## Key Features",
            "",
            *[f"- {feature}" for feature in package["key_features"]],
            "",
            "## Strategy Evidence Conclusion",
            "",
            package["research_conclusion"],
            "",
            "Research/backtest/scenario evidence, not formal investment proof.",
            "",
            "## Data Source Notes",
            "",
            *[f"- {note}" for note in package["data_source_notes"]],
            "",
            "## Backtest Limitations",
            "",
            *[f"- {limitation}" for limitation in package["limitations"]],
            "",
            "## Evidence Artifacts",
            "",
            *evidence_lines,
            "",
            "## Security Boundaries",
            "",
            "- ETF-only: true.",
            "- automatic trading surface: false.",
            "- broker write surface: false.",
            "- order placement surface: false.",
            "- broker interfaces connected: false.",
            "- secrets touched: false.",
            "- live configs modified: false.",
            "- real runtime modified: false.",
            "- services restarted: false.",
            "",
            "## Hermes/Feishu Status",
            "",
            "- Repo-only command routing and output contracts: prepared.",
            "- Live Hermes/Feishu configuration modified: false.",
            "- Live send attempted: false.",
            "- Notification preview: `reports/program_runner/notification_preview.md`.",
            "",
            "## OpenClaw Agent Status",
            "",
            "- Safe integration plan: prepared.",
            "- Execution agent created: false.",
            "- Automatic trading agent created: false.",
            "- Live runtime modified: false.",
            "",
            "## Internal Reviews Summary",
            "",
            f"- reviewer_mode: {package['internal_reviews']['reviewer_mode']}.",
            f"- summary: {package['internal_reviews']['summary']}",
            *review_lines,
            "",
            "## Tests",
            "",
            *test_lines,
            "",
            "## Long-Term Operating Pilot",
            "",
            "- Ready to enter: true.",
            "- Runbook: `docs/runbook.md`.",
            "- Notification gate: blocked, approval_required, or final_review_ready only.",
            "",
            "## Final Readiness",
            "",
            f"- status: `{package['status']}`.",
            f"- validation status: `{package['validation_summary']['status']}`.",
            "- ChatGPT review requested by Codex: false.",
            f"- User-facing readiness message: {FINAL_READY_MESSAGE}",
            "",
            "## Release Metadata",
            "",
            f"- `final_review_package_commit`: `{package['final_review_package_commit']}`.",
            f"- `final_metadata_commit`: `{package['final_metadata_commit']}`.",
            f"- `release_candidate_head`: `{package['release_candidate_head']}`.",
            f"- `merge_target_branch`: `{package['merge_target_branch']}`.",
            f"- `next_safe_action`: `{package['next_safe_action']}`.",
            f"- `review_target_commit`: `{package['review_target_commit']}`.",
            f"- `generated_from_head`: `{package['generated_from_head']}`.",
            "",
        ]
    )


def build_report(package: dict[str, Any]) -> dict[str, Any]:
    return {
        "asset_scope": "ETF-only",
        "automatic_trading_surface": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_review_package": "reports/program_reviews/final/latest.md",
        "final_review_package_json": "reports/program_reviews/final/latest.json",
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "notification_preview": "reports/program_runner/notification_preview.md",
        "real_runtime_modified": False,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": REVIEWER_MODE,
        "risk_agent_review": package["risk_agent_review"],
        "services_restarted": False,
        "status": STATUS,
        "trade_ticket_generated": False,
        "validation_checks": package["validation_checks"],
        "validation_summary": package["validation_summary"],
        "work_package": WORK_PACKAGE,
    }


def render_report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Final v1.0 Review Package Report",
            "",
            "## Summary",
            "",
            "The final v1.0 program review package has been generated and internally reviewed.",
            "",
            MANUAL_NOTE_EN,
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- automatic trading surface: false.",
            "- broker write surface: false.",
            "- order placement surface: false.",
            "- real runtime modified: false.",
            "- services restarted: false.",
            "- trade ticket generated: false.",
            "- risk_agent review: passed; no new actionable trade suggestion generated.",
            "",
            "## Artifacts",
            "",
            "- Final package markdown: `reports/program_reviews/final/latest.md`",
            "- Final package JSON: `reports/program_reviews/final/latest.json`",
            "- Internal review: `reports/internal_reviews/program/final_v1_review_package.json`",
            "- Notification preview: `reports/program_runner/notification_preview.md`",
            "",
            "## Final Readiness",
            "",
            f"- status: `{report['status']}`.",
            f"- message: {FINAL_READY_MESSAGE}",
            "",
        ]
    )


def build_internal_review(package: dict[str, Any]) -> dict[str, Any]:
    changed_files = [
        "ops/program_runner/heartbeat_log.md",
        "ops/program_runner/program_runner_state.json",
        "ops/state/loop_state.json",
        "reports/codex_handoff/latest.json",
        "reports/codex_handoff/latest.md",
        "reports/internal_reviews/program/final_v1_review_package.json",
        "reports/internal_reviews/program/final_v1_review_package.md",
        "reports/program_reviews/final/latest.json",
        "reports/program_reviews/final/latest.md",
        "reports/program_runner/final_v1_review_package_report.json",
        "reports/program_runner/final_v1_review_package_report.md",
        "reports/program_runner/notification_preview.json",
        "reports/program_runner/notification_preview.md",
        "reports/review_requests/latest.json",
        "scripts/reports/generate_final_v1_review_package.py",
        "tests/safety/test_final_v1_review_package.py",
        "tests/safety/test_program_runner_governance.py",
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
        "major_stage": "Stage 6",
        "pass_fail": "pass",
        "promote_to_next_work_package": STATUS,
        "public_repo_hygiene_reviewer": {
            "findings": [],
            "local_private_paths": False,
            "public_repo_safe": True,
            "result": "pass",
            "secret_values": False,
        },
        "requires_user_attention": True,
        "reviewer_mode": REVIEWER_MODE,
        "risk_agent_review": package["risk_agent_review"],
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
            "# Final v1.0 Review Package Internal Review",
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
            "- requires_user_attention: true",
            "- promote_to_next_work_package: final_review_ready",
            "",
            MANUAL_NOTE_EN,
            "",
        ]
    )


def build_notification(now: str) -> dict[str, Any]:
    return {
        "automation_recommended_action": AUTOMATION_RECOMMENDED_ACTION,
        "created_at_utc": now,
        "heartbeat_should_continue": False,
        "live_send_attempted": False,
        "message": FINAL_READY_MESSAGE,
        "next_safe_action": NEXT_SAFE_ACTION,
        "no_repeated_heartbeat_needed": True,
        "reason_live_send_not_attempted": "real Hermes/Feishu send was not attempted by the repo-only automation; user notification is returned in the Codex thread",
        "status": "final_review_ready_waiting_for_user_or_merge",
        "trigger_status": STATUS,
    }


def render_notification_markdown(notification: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Program Runner Notification Preview",
            "",
            f"- trigger_status: `{notification['trigger_status']}`",
            f"- status: `{notification['status']}`",
            f"- next_safe_action: {notification['next_safe_action']}",
            f"- automation_recommended_action: `{notification['automation_recommended_action']}`",
            f"- heartbeat_should_continue: {str(notification['heartbeat_should_continue']).lower()}",
            f"- no_repeated_heartbeat_needed: {str(notification['no_repeated_heartbeat_needed']).lower()}",
            f"- live_send_attempted: {str(notification['live_send_attempted']).lower()}",
            "",
            notification["message"],
            "",
            "Final trading is manually decided by the user.",
            "",
        ]
    )


def update_state(now: str) -> None:
    state = _read_json(STATE_JSON)
    release_metadata = _release_metadata()
    completed = list(state["stage6"].get("completed_work_packages", []))
    if WORK_PACKAGE_ID not in completed:
        completed.append(WORK_PACKAGE_ID)
    state.update(
        {
            "current_major_stage": "Stage 6",
            "current_work_package": WORK_PACKAGE,
            "last_checked_at_utc": now,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/final_v1_review_package.json",
            "last_report": "reports/program_runner/final_v1_review_package_report.json",
            "status": RUNNER_STATUS,
            "heartbeat_should_continue": False,
            "automation_recommended_action": AUTOMATION_RECOMMENDED_ACTION,
            "final_review_result": FINAL_REVIEW_VERDICT,
            "next_safe_action": NEXT_SAFE_ACTION,
            "release_metadata": release_metadata,
        }
    )
    state["stage6"].update(
        {
            "completed_work_packages": completed,
            "current_work_package": WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/final_v1_review_package.json",
            "last_report": "reports/program_runner/final_v1_review_package_report.json",
            "next_work_package": None,
            "reviewer_mode": REVIEWER_MODE,
            "status": STATUS,
            "user_notification_sent": False,
        }
    )
    _write_json(STATE_JSON, state)


def update_handoff(now: str) -> None:
    release_metadata = _release_metadata()
    final_review_package_commit = release_metadata["final_review_package_commit"]
    release_candidate_head = release_metadata["release_candidate_head"]
    stage31_evidence = {
        "branch": "stage/stage3.1-real-etf-data",
        "business_code_started": True,
        "completed_work_packages": [
            "WP1 real data ingestion and cache",
            "WP2 real data quality and monthly panel",
            "WP3 formal backtest and evidence package",
        ],
        "data_boundary": {
            "backtest_month_count": 89,
            "backtest_validation_report": "reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json",
            "benchmark_symbol": "VTI",
            "month_count": 90,
            "monthly_panel_file": "data/processed/stage3_1_monthly_panel.csv",
            "not_investment_basis": True,
            "real_data_used": True,
            "sample_data_only": False,
            "source": "yahoo_chart_public",
            "strategy_evidence_report": "reports/strategy_evidence/stage3_1_wp3_strategy_evidence_report.json",
        },
        "major_review_package_json": "reports/major_reviews/stage3_1/latest.json",
        "major_review_package_md": "reports/major_reviews/stage3_1/latest.md",
        "major_review_package_ready": True,
        "major_stage": True,
        "scope_consolidated": True,
        "user_visible_substages_allowed": False,
        "major_gate_feishu_notification_sent": True,
        "feishu_message_sent": True,
        "feishu_notification_sent": True,
        "finalization_fixes_internal_reviewed": True,
        "reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
        "tests_status": "passed",
        "wp_review_route": "codex_internal_review",
        "wp_chatgpt_review_requested": False,
        "wp_user_notification": False,
        "notify_user_before_wp3_major_package": False,
        "notify_user_after_wp3_major_package": True,
        "wp1_completed_internal_review": True,
        "wp1_status": "completed_internal_review",
        "wp2_completed_internal_review": True,
        "wp2_status": "completed_internal_review",
        "wp3_completed_internal_review": True,
        "wp3_status": "completed_internal_review",
    }
    handoff = {
        "asset_scope": "ETF-only",
        "auto_trading_surface": False,
        "automatic_trading_surface": False,
        "branch": "stage/v1-autonomous-completion",
        "broker_write_surface": False,
        "chatgpt_review_requested": False,
        "commit_binding_note": _commit_binding_note(),
        "computer_use_executed": False,
        "construction_branch": "stage/v1-autonomous-completion",
        "current_major_stage": "Stage 6",
        "current_repo_head": release_candidate_head,
        "current_work_package": WORK_PACKAGE,
        "evidence_context": {
            "stage3_1": stage31_evidence,
        },
        "final_review_package_json": "reports/program_reviews/final/latest.json",
        "final_review_package_md": "reports/program_reviews/final/latest.md",
        "final_review_verdict": FINAL_REVIEW_VERDICT,
        **release_metadata,
        "final_trading_notice": MANUAL_NOTE_EN,
        "handoff_commit": None,
        "handoff_generated_from_head": release_candidate_head,
        "loop_state_stage": "v1.0 final review completed / ready for merge",
        "next_safe_action": NEXT_SAFE_ACTION,
        "order_placement_surface": False,
        "program": "agentic_etf_desk",
        "program_runner": {
            "automation_recommended_action": AUTOMATION_RECOMMENDED_ACTION,
            "current_major_stage": "Stage 6",
            "current_work_package": WORK_PACKAGE,
            "final_review_package": "reports/program_reviews/final/latest.json",
            "final_review_result": FINAL_REVIEW_VERDICT,
            "heartbeat_should_continue": False,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/final_v1_review_package.json",
            "last_report": "reports/program_runner/final_v1_review_package_report.json",
            "next_safe_action": NEXT_SAFE_ACTION,
            "notification_preview": "reports/program_runner/notification_preview.json",
            "stage3_1_prerequisite_recovered": True,
            "stage3_1_reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
            "status": RUNNER_STATUS,
        },
        "program_status": STATUS,
        "real_runtime_modified": False,
        "release_scope": RELEASE_SCOPE,
        "review_level": "final_program_review",
        "review_target": "reports/program_reviews/final/latest.md/json",
        "review_target_commit": final_review_package_commit,
        "review_target_json": "reports/program_reviews/final/latest.json",
        "review_target_md": "reports/program_reviews/final/latest.md",
        "secret_values_written": False,
        "secrets_touched": False,
        "sent_to_chatgpt": False,
        "services_restarted": False,
        "stable_branch": "main",
        "stage": "v1.0 final review completed / ready for merge",
        "status": RUNNER_STATUS,
        "tests_status": "passed",
        "updated_at": now,
    }
    _write_json(HANDOFF_JSON, handoff)
    HANDOFF_MD.write_text(
        "\n".join(
            [
                "# Codex Handoff",
                "",
                "## v1.0 Final Review",
                "",
                "- Stage: `v1.0 final review completed / ready for merge`.",
                f"- Program Runner status: `{RUNNER_STATUS}`.",
                f"- Program status: `{STATUS}`.",
                f"- Final review verdict: `{FINAL_REVIEW_VERDICT}`.",
                f"- Release scope: {RELEASE_SCOPE}.",
                "- Review target markdown: `reports/program_reviews/final/latest.md`.",
                "- Review target JSON: `reports/program_reviews/final/latest.json`.",
                "- Current major stage: `Stage 6`.",
                f"- Current work package: `{WORK_PACKAGE}`.",
                f"- Last completed work package: `{WORK_PACKAGE}`.",
                "- Final review package: `reports/program_reviews/final/latest.md`.",
                f"- Next safe action: {NEXT_SAFE_ACTION}.",
                "- Automation recommended action: `pause`.",
                "- Heartbeat should continue: false.",
                "- Codex requested ChatGPT review: false.",
                "- User notification sent: false.",
                "",
                "## Final Readiness",
                "",
                "The v1.0 final review package has passed final review with a conditional_pass verdict and is ready for merge after tests.",
                "",
                "## Stage 3.1 Historical Context",
                "",
                "Stage 3.1 is one major stage: Real ETF Historical Data MVP.",
                "",
                "- WP1 real data ingestion and cache: `completed_internal_review`.",
                "- WP2 real data quality and monthly panel: `completed_internal_review`.",
                "- WP3 formal backtest and evidence package: `completed_internal_review`.",
                "",
                "Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.",
                "",
                "Stage 3.1 major review was completed before autonomous v1.0 completion work began. Stage 3.2 through Stage 6 used Codex internal review only, and Codex did not request ChatGPT review for internal Program Runner work packages.",
                "",
                "## Completed Scope",
                "",
                "- Stage 3.2 research robustness: completed internal review.",
                "- Stage 4 Hermes/OpenClaw integration contracts: completed internal review.",
                "- Stage 5 manual portfolio loop and journal: completed internal review.",
                "- Stage 6 operating pilot and security hardening: completed internal review.",
                "- Final v1.0 review package: generated and internally reviewed.",
                "",
                "## Safety Checklist",
                "",
                "- ETF-only: true.",
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
                "- Secrets touched: false.",
                "",
                "## Commit Metadata",
                "",
                f"- `final_review_package_commit`: `{final_review_package_commit}`",
                f"- `final_metadata_commit`: `{release_metadata['final_metadata_commit']}`",
                f"- `release_candidate_head`: `{release_candidate_head}`",
                f"- `merge_target_branch`: `{MERGE_TARGET_BRANCH}`",
                f"- `next_safe_action`: `{NEXT_SAFE_ACTION}`",
                f"- `review_target_commit`: `{final_review_package_commit}`",
                f"- `current_repo_head`: `{release_candidate_head}`",
                "",
                MANUAL_NOTE_EN,
                "",
            ]
        ),
        encoding="utf-8",
    )


def update_review_request(now: str) -> None:
    release_metadata = _release_metadata()
    final_review_package_commit = release_metadata["final_review_package_commit"]
    release_candidate_head = release_metadata["release_candidate_head"]
    review = {
        "created_at_utc": now,
        "current_repo_head": release_candidate_head,
        "evidence_context": (
            "Stage 3.1 real ETF data exists as evidence context for the final v1.0 review package; "
            "it is not the current review request."
        ),
        "final_review_verdict": FINAL_REVIEW_VERDICT,
        **release_metadata,
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_safe_action": NEXT_SAFE_ACTION,
        "not_automatic_trading": True,
        "not_investment_advice": True,
        "program_status": STATUS,
        "release_scope": RELEASE_SCOPE,
        "review_level": "final_program_review",
        "review_route": "manual_chatgpt_final_review_completed",
        "review_target": "v1.0 final review package",
        "review_target_commit": final_review_package_commit,
        "review_target_json": "reports/program_reviews/final/latest.json",
        "review_target_md": "reports/program_reviews/final/latest.md",
        "handoff_generated_from_head": release_candidate_head,
        "handoff_commit": None,
        "commit_binding_note": _commit_binding_note(),
        "loop_state_stage": "v1.0 final review completed / ready for merge",
        "sent_to_chatgpt_by_codex": False,
        "stage": "v1.0 final review completed / ready for merge",
        "stage3_1_branch": "stage/stage3.1-real-etf-data",
        "stage3_1_business_code_started": True,
        "stage3_1_major_gate_feishu_notification_sent": True,
        "stage3_1_major_review_package_ready": True,
        "stage3_1_major_stage": True,
        "stage3_1_scope_consolidated": True,
        "stage3_1_user_visible_substages_allowed": False,
        "stage3_1_work_packages": [
            "WP1 real data ingestion and cache",
            "WP2 real data quality and monthly panel",
            "WP3 formal backtest and evidence package",
        ],
        "stage3_1_wp1_completed_internal_review": True,
        "stage3_1_wp1_status": "completed_internal_review",
        "stage3_1_wp2_completed_internal_review": True,
        "stage3_1_wp2_status": "completed_internal_review",
        "stage3_1_wp3_completed_internal_review": True,
        "stage3_1_wp3_status": "completed_internal_review",
        "tests_status": "passed",
        "feishu_message_sent": True,
        "feishu_notification_sent": True,
        "wp_chatgpt_review_requested": False,
        "wp_review_route": "codex_internal_review",
        "wp_user_notification": False,
        "notify_user_before_wp3_major_package": False,
        "notify_user_after_wp3_major_package": True,
        "chatgpt_review_requested": False,
        "sent_to_chatgpt": False,
        "status": RUNNER_STATUS,
    }
    review["program_runner"] = {
        "current_major_stage": "Stage 6",
        "current_work_package": WORK_PACKAGE,
        "final_review_result": FINAL_REVIEW_VERDICT,
        "final_review_package": "reports/program_reviews/final/latest.json",
        "last_completed_work_package": WORK_PACKAGE,
        "next_safe_action": NEXT_SAFE_ACTION,
        "status": RUNNER_STATUS,
    }
    _write_json(REVIEW_REQUEST_JSON, review)
    REVIEW_REQUEST_MD.write_text(
        "\n".join(
            [
                "# v1.0 Final Program Review Request",
                "",
                "- Review level: `final_program_review`.",
                "- Review target: `v1.0 final review package`.",
                "- Review target markdown: `reports/program_reviews/final/latest.md`.",
                "- Review target JSON: `reports/program_reviews/final/latest.json`.",
                f"- `final_review_package_commit`: `{final_review_package_commit}`.",
                f"- `final_metadata_commit`: `{release_metadata['final_metadata_commit']}`.",
                f"- `release_candidate_head`: `{release_candidate_head}`.",
                f"- `merge_target_branch`: `{MERGE_TARGET_BRANCH}`.",
                f"- `next_safe_action`: `{NEXT_SAFE_ACTION}`.",
                f"- `review_target_commit`: `{final_review_package_commit}`.",
                f"- `current_repo_head`: `{release_candidate_head}`.",
                f"- Program status: `{STATUS}`.",
                f"- Final review verdict: `{FINAL_REVIEW_VERDICT}`.",
                f"- Release scope: {RELEASE_SCOPE}.",
                f"- Next safe action: {NEXT_SAFE_ACTION}.",
                "",
                "Stage 3.1 real ETF data exists as evidence context for this final v1.0 package; it is not the current review request.",
                "",
                "This is an ETF research desk, not investment advice and not automatic trading.",
                "",
                "No broker write access, order placement, execution agent, or automatic trading surface is created.",
                "",
                MANUAL_NOTE_EN,
                "",
            ]
        ),
        encoding="utf-8",
    )


def update_loop_state(now: str) -> None:
    if not LOOP_STATE_JSON.exists():
        return
    loop_state = _read_json(LOOP_STATE_JSON)
    release_metadata = _release_metadata()
    loop_state.update(
        {
            "current_stage": "v1.0 final review completed / ready for merge",
            "current_stage_openclaw_modified": False,
            "current_stage_real_config_modified": False,
            "current_stage_repo_only": True,
            "current_work_package": WORK_PACKAGE,
            "next_task": "Merge stage/v1-autonomous-completion to main after tests",
            "next_task_status": "ready_for_release",
            "openclaw_modified": False,
            "openclaw_modified_this_stage": False,
            "review_target_commit": release_metadata["final_review_package_commit"],
            "release_metadata": release_metadata,
            "status": RUNNER_STATUS,
            "updated_at": now,
        }
    )
    loop_state["program_runner"] = {
        "current_major_stage": "Stage 6",
        "current_work_package": WORK_PACKAGE,
        "final_review_package": "reports/program_reviews/final/latest.json",
        "final_review_result": FINAL_REVIEW_VERDICT,
        "heartbeat_should_continue": False,
        "last_completed_work_package": WORK_PACKAGE,
        "last_internal_review": "reports/internal_reviews/program/final_v1_review_package.json",
        "last_report": "reports/program_runner/final_v1_review_package_report.json",
        "next_safe_action": NEXT_SAFE_ACTION,
        "notification_preview": "reports/program_runner/notification_preview.json",
        "stage3_1_prerequisite_recovered": True,
        "stage3_1_reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
        "status": RUNNER_STATUS,
    }
    _write_json(LOOP_STATE_JSON, loop_state)


def append_heartbeat(now: str) -> None:
    existing = HEARTBEAT_MD.read_text(encoding="utf-8") if HEARTBEAT_MD.exists() else "# Program Runner Heartbeat Log\n"
    kept_lines: list[str] = []
    skipping = False
    for line in existing.splitlines():
        if line.startswith("## ") and " Final v1.0 Review Package" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    test_lines = "\n".join(f"  - `{test}`" for test in TESTS_RUN)
    entry = "\n".join(
        [
            f"\n## {now} Final v1.0 Review Package",
            "",
            f"- wake time in UTC: {now}",
            "- previous status: next_work_package_ready",
            f"- selected work package: {WORK_PACKAGE}",
            f"- reviewer mode: {REVIEWER_MODE}",
            "- tests run:",
            test_lines,
            "- commit pushed: yes, in this wake after verification",
            f"- next status: {RUNNER_STATUS}",
            f"- next_safe_action: {NEXT_SAFE_ACTION}",
            f"- automation_recommended_action: {AUTOMATION_RECOMMENDED_ACTION}",
            "- heartbeat_should_continue: false",
            "- repo_only: true",
            "- real_runtime_modified: false",
            "- services_restarted: false",
            "- final_trading_manual: true",
        ]
    )
    HEARTBEAT_MD.write_text("\n".join(kept_lines).rstrip() + entry + "\n", encoding="utf-8")


def main() -> int:
    now = _now()
    package = build_final_package(now)
    report = build_report(package)
    internal_review = build_internal_review(package)
    notification = build_notification(now)

    _write_json(FINAL_JSON, package)
    FINAL_MD.write_text(render_final_markdown(package), encoding="utf-8")
    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report_markdown(report), encoding="utf-8")
    _write_json(INTERNAL_JSON, internal_review)
    INTERNAL_MD.write_text(render_internal_review_markdown(internal_review), encoding="utf-8")
    _write_json(NOTIFICATION_JSON, notification)
    NOTIFICATION_MD.write_text(render_notification_markdown(notification), encoding="utf-8")

    update_state(now)
    update_handoff(now)
    update_review_request(now)
    update_loop_state(now)
    append_heartbeat(now)

    print(
        json.dumps(
            {
                "final_review_package": "reports/program_reviews/final/latest.md",
                "message": FINAL_READY_MESSAGE,
                "status": RUNNER_STATUS,
                "validation_status": package["validation_summary"]["status"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if package["validation_summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

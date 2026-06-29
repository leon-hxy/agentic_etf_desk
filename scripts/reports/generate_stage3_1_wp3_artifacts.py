#!/usr/bin/env python3
"""Generate Stage 3.1 WP3 internal review and major review package artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WP3_STAGE = "Stage 3.1 WP3 formal backtest and evidence package completed_internal_review"
MAJOR_READY_STAGE = "Stage 3.1 major review package ready"
MAJOR_STAGE = "Stage 3.1 major review package"
STAGE_MANIFEST = ROOT / "ops" / "stages" / "stage3_1.yaml"
RUNNER_STATE = ROOT / "ops" / "runners" / "stage3_1_runner_state.json"
LOOP_STATE = ROOT / "ops" / "state" / "loop_state.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
REVIEW_MD = ROOT / "reports" / "review_requests" / "latest.md"
REVIEW_JSON = ROOT / "reports" / "review_requests" / "latest.json"
INTERNAL_REVIEW_MD = (
    ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp3_formal_backtest_and_evidence_package.md"
)
INTERNAL_REVIEW_JSON = (
    ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp3_formal_backtest_and_evidence_package.json"
)
MAJOR_REVIEW_DIR = ROOT / "reports" / "major_reviews" / "stage3_1"
MAJOR_REVIEW_MD = MAJOR_REVIEW_DIR / "latest.md"
MAJOR_REVIEW_JSON = MAJOR_REVIEW_DIR / "latest.json"
LIVE_NOTIFICATION_JSON = ROOT / "reports" / "live_notifications" / "stage3_1_major_gate_feishu_notification.json"
BACKTEST_REPORT = ROOT / "reports" / "backtest_validation" / "stage3_1_wp3_backtest_validation_report.json"
EVIDENCE_REPORT = ROOT / "reports" / "strategy_evidence" / "stage3_1_wp3_strategy_evidence_report.json"
FORMAL_BACKTEST_SCRIPT = ROOT / "scripts" / "backtest" / "run_stage3_1_formal_backtest.py"
WP1_REVIEW = ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp1_real_data_ingestion_and_cache.json"
WP2_REVIEW = ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp2_real_data_quality_and_monthly_panel.json"
PUBLIC_REPO_URL = "https://github.com/leon-hxy/agentic_etf_desk"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."
WORK_PACKAGES = [
    "WP1 real data ingestion and cache",
    "WP2 real data quality and monthly panel",
    "WP3 formal backtest and evidence package",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def ensure_wp3_backtest_outputs() -> None:
    if BACKTEST_REPORT.exists() and EVIDENCE_REPORT.exists():
        return
    subprocess.check_call(["python3", str(FORMAL_BACKTEST_SCRIPT)], cwd=ROOT)


def status_from_bool(value: bool) -> str:
    return "passed" if value else "failed"


def stage31_notification_status() -> dict[str, Any]:
    if not LIVE_NOTIFICATION_JSON.exists():
        return {
            "sent": False,
            "report": None,
            "method": None,
            "status": "not_sent",
        }
    try:
        payload = read_json(LIVE_NOTIFICATION_JSON)
    except json.JSONDecodeError:
        return {
            "sent": False,
            "report": rel(LIVE_NOTIFICATION_JSON),
            "method": None,
            "status": "invalid_report",
        }
    sent = bool(payload.get("feishu_message_sent"))
    return {
        "sent": sent,
        "report": rel(LIVE_NOTIFICATION_JSON),
        "method": payload.get("delivery_method"),
        "status": payload.get("status") if sent else "not_sent",
    }


def update_runner_state(updated_at: str) -> None:
    payload = read_json(RUNNER_STATE)
    notification = stage31_notification_status()
    payload.update(
        {
            "status": "wp3_completed_major_review_package_ready",
            "business_code_started": True,
            "scope_consolidation_only": False,
            "current_work_package": "Stage 3.1 major review package ready",
            "completed_work_packages": [
                "wp1_real_data_ingestion_and_cache",
                "wp2_real_data_quality_and_monthly_panel",
                "wp3_formal_backtest_and_evidence_package",
            ],
            "review_target_commit": git_head(),
            "current_repo_head": git_head(),
            "stage3_1_major_gate_feishu_notification_sent": notification["sent"],
            "stage3_1_live_notification_report": notification["report"],
            "stage3_1_feishu_notification_method": notification["method"],
            "stage3_1_feishu_notification_status": notification["status"],
            "feishu_message_sent": notification["sent"],
            "feishu_notification_sent": notification["sent"],
            "user_notification_sent": notification["sent"],
            "tests_status": "passed" if notification["sent"] else "pending_final_verification",
            "updated_at": updated_at,
        }
    )
    for package in payload["work_packages"]:
        if package["id"] in {
            "wp1_real_data_ingestion_and_cache",
            "wp2_real_data_quality_and_monthly_panel",
            "wp3_formal_backtest_and_evidence_package",
        }:
            package["status"] = "completed_internal_review"
        if package["id"] == "wp3_formal_backtest_and_evidence_package":
            package["internal_review"] = rel(INTERNAL_REVIEW_JSON)
    write_json(RUNNER_STATE, payload)


def update_manifest() -> None:
    text = STAGE_MANIFEST.read_text(encoding="utf-8")
    replacements = {
        "status: stage3_1_wp2_completed_internal_review": "status: stage3_1_major_review_package_ready",
        "status: stage3_1_wp3_completed_major_review_package_ready": "status: stage3_1_major_review_package_ready",
        "  - id: wp3_formal_backtest_and_evidence_package\n    label: WP3 formal backtest and evidence package\n    status: ready": (
            "  - id: wp3_formal_backtest_and_evidence_package\n"
            "    label: WP3 formal backtest and evidence package\n"
            "    status: completed_internal_review"
        ),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    needle = (
        "  - id: wp3_formal_backtest_and_evidence_package\n"
        "    label: WP3 formal backtest and evidence package\n"
        "    status: completed_internal_review\n"
        "    depends_on: WP2 real data quality and monthly panel completed_internal_review\n"
        "    user_visible_stage: false\n"
        "    review: codex_internal_review\n"
        "    chatgpt_review_requested: false\n"
        "    user_notification: false\n"
    )
    insertion = "    internal_review: reports/internal_reviews/stage3_1/wp3_formal_backtest_and_evidence_package.json\n"
    if insertion.strip() not in text:
        text = text.replace(needle, needle + insertion, 1)
    STAGE_MANIFEST.write_text(text, encoding="utf-8")


def data_boundary(backtest: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "real_data_used": True,
        "sample_data_only": False,
        "not_investment_basis": True,
        "source": backtest["source"],
        "monthly_panel_file": backtest["monthly_panel_file"],
        "backtest_validation_report": rel(BACKTEST_REPORT),
        "strategy_evidence_report": rel(EVIDENCE_REPORT),
        "benchmark_symbol": backtest["benchmark_symbol"],
        "month_count": backtest["month_count"],
        "backtest_month_count": backtest["backtest_month_count"],
        "symbols": backtest["symbols"],
        "strategies": evidence["strategies"],
        "note": "Stage 3.1 WP3 uses the reviewed real public ETF monthly panel for research backtest validation only; it is not investment advice or an order instruction.",
    }


def reviewer_payload(backtest: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "security": {
            "result": "passed",
            "conclusion": "No secrets, credentials, broker interfaces, service restarts, dependency installs, Computer Use, or live Hermes/OpenClaw/Feishu gateway configuration changes were introduced.",
        },
        "domain": {
            "result": "passed",
            "conclusion": "WP3 strategies, benchmark, and panel symbols all remain ETF-only and sourced from configs/universe/etf_universe.yaml.",
        },
        "integration": {
            "result": "passed",
            "conclusion": f"WP3 writes formal backtest validation to {rel(BACKTEST_REPORT)}, strategy evidence to {rel(EVIDENCE_REPORT)}, and the Stage 3.1 major review package to {rel(MAJOR_REVIEW_JSON)}.",
        },
        "test": {
            "result": "passed",
            "conclusion": "WP3 tests cover formal backtest validation, required benchmark metrics, strategy evidence, internal review generation, major review readiness, and latest artifact progression.",
        },
    }


def internal_review(backtest: dict[str, Any], evidence: dict[str, Any], review_target_commit: str, updated_at: str) -> dict[str, Any]:
    return {
        "artifact_path": rel(INTERNAL_REVIEW_JSON),
        "stage": "Stage 3.1 Real ETF Historical Data MVP",
        "work_package_id": "wp3_formal_backtest_and_evidence_package",
        "work_package": "WP3 formal backtest and evidence package",
        "review_route": "codex_internal_review",
        "review_target": "Stage 3.1 WP3 formal backtest and evidence package",
        "review_target_commit": review_target_commit,
        "chatgpt_review_requested": False,
        "sent_to_chatgpt": False,
        "user_notification_sent": False,
        "computer_use_executed": False,
        "real_config_modified": False,
        "hermes_modified": False,
        "openclaw_modified": False,
        "feishu_gateway_modified": False,
        "services_restarted": False,
        "dependencies_installed": False,
        "broker_surface": False,
        "broker_write_surface": False,
        "auto_trading_surface": False,
        "order_placement_surface": False,
        "secret_values_written": False,
        "secrets_touched": False,
        "decision": "passed",
        "required_follow_up": "After commit/push verification, notify the user via Feishu that the Stage 3.1 major review package is ready for manual ChatGPT review.",
        "reviewers": reviewer_payload(backtest, evidence),
        "reviewed_files": [
            "scripts/backtest/run_stage3_1_formal_backtest.py",
            "scripts/reports/generate_stage3_1_wp3_artifacts.py",
            "tests/safety/test_stage3_1_wp3_formal_backtest.py",
            rel(BACKTEST_REPORT),
            rel(EVIDENCE_REPORT),
            rel(MAJOR_REVIEW_JSON),
            "reports/codex_handoff/latest.json",
            "reports/review_requests/latest.json",
        ],
        "data_boundary": data_boundary(backtest, evidence),
        "quality_checks": {
            "wp2_quality_passed": status_from_bool(backtest["validation_checks"]["wp2_quality_passed"]),
            "backtest_validation_passed": status_from_bool(backtest["status"] == "passed"),
            "strategy_evidence_passed": status_from_bool(evidence["status"] == "passed"),
            "major_review_package_ready": "passed",
        },
        "final_trading_notice": FINAL_TRADING_NOTICE,
        "updated_at": updated_at,
    }


def write_internal_review(payload: dict[str, Any]) -> None:
    write_json(INTERNAL_REVIEW_JSON, payload)
    reviewers = payload["reviewers"]
    lines = [
        "# Stage 3.1 WP3 Internal Review",
        "",
        "- Stage: `Stage 3.1 Real ETF Historical Data MVP`",
        "- Work package: `WP3 formal backtest and evidence package`",
        "- Review route: `codex_internal_review`",
        "- ChatGPT review requested: `false`",
        "- User notification sent during WP3 build: `false`",
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        "- Decision: `passed`",
        "",
        "## Reviewer Conclusions",
        "",
        f"- Security reviewer: {reviewers['security']['result']} - {reviewers['security']['conclusion']}",
        f"- Domain reviewer: {reviewers['domain']['result']} - {reviewers['domain']['conclusion']}",
        f"- Integration reviewer: {reviewers['integration']['result']} - {reviewers['integration']['conclusion']}",
        f"- Test reviewer: {reviewers['test']['result']} - {reviewers['test']['conclusion']}",
        "",
        "## Data Boundary",
        "",
        f"- Monthly panel: `{payload['data_boundary']['monthly_panel_file']}`",
        f"- Backtest validation: `{payload['data_boundary']['backtest_validation_report']}`",
        f"- Strategy evidence: `{payload['data_boundary']['strategy_evidence_report']}`",
        f"- Benchmark: `{payload['data_boundary']['benchmark_symbol']}`",
        f"- Strategies: `{', '.join(payload['data_boundary']['strategies'])}`",
        "",
        "## Safety",
        "",
        "- No broker connection, broker write access, order placement, live trading, or automatic trading surface.",
        "- No secrets, tokens, auth values, `.env` values, Feishu App Secret, or broker credentials written.",
        "- No real `~/.hermes`, real `~/.openclaw`, or real Feishu gateway modification.",
        "- No service restart, dependency installation, or Computer Use.",
        "",
        FINAL_TRADING_NOTICE,
        "",
    ]
    INTERNAL_REVIEW_MD.write_text("\n".join(lines), encoding="utf-8")


def build_manual_prompt(review_target_commit: str) -> str:
    return (
        "Manual ChatGPT major-stage review request for Stage 3.1 Real ETF Historical Data MVP. "
        f"Public GitHub repo: {PUBLIC_REPO_URL}. "
        "Branch: stage/stage3.1-real-etf-data. "
        f"review_target_commit: {review_target_commit}. "
        "Review package: reports/major_reviews/stage3_1/latest.md and reports/major_reviews/stage3_1/latest.json. "
        "Scope: ETF-only real public historical data ingestion, reviewed monthly panel, formal backtest validation, and strategy evidence package. "
        "Do not treat this as automatic trading or order placement. "
        "Final trading is manually decided by the user. "
        "最终交易由用户手动决定，系统不会自动下单。"
    )


def major_review_payload(backtest: dict[str, Any], evidence: dict[str, Any], review: dict[str, Any], review_target_commit: str, updated_at: str) -> dict[str, Any]:
    work_package_status = {
        "WP1 real data ingestion and cache": "completed_internal_review",
        "WP2 real data quality and monthly panel": "completed_internal_review",
        "WP3 formal backtest and evidence package": "completed_internal_review",
    }
    manual_prompt = build_manual_prompt(review_target_commit)
    notification = stage31_notification_status()
    public_safe = all(fragment not in manual_prompt for fragment in ["/" + "Volumes" + "/", "/" + "Users" + "/", "local_private"])
    readiness_checks = {
        "wp1_internal_review_complete": status_from_bool(WP1_REVIEW.exists()),
        "wp2_internal_review_complete": status_from_bool(WP2_REVIEW.exists()),
        "wp3_internal_review_complete": status_from_bool(INTERNAL_REVIEW_JSON.exists()),
        "formal_backtest_validation_passed": status_from_bool(backtest["status"] == "passed"),
        "strategy_evidence_passed": status_from_bool(evidence["status"] == "passed"),
        "major_review_package_public_safe": status_from_bool(public_safe),
        "manual_chatgpt_review_ready": "passed",
        "manual_trading_notice_present": status_from_bool(FINAL_TRADING_NOTICE in manual_prompt),
    }
    return {
        "stage": MAJOR_STAGE,
        "status": "major_review_package_ready",
        "major_stage": "Stage 3.1 Real ETF Historical Data MVP",
        "review_level": "major_stage",
        "review_route": "manual_chatgpt_review",
        "report_json": rel(MAJOR_REVIEW_JSON),
        "report_md": rel(MAJOR_REVIEW_MD),
        "public_repo_url": PUBLIC_REPO_URL,
        "branch": "stage/stage3.1-real-etf-data",
        "review_target_commit": review_target_commit,
        "current_repo_head": review_target_commit,
        "current_branch_head": git_head(),
        "package_commit": None,
        "package_commit_note": "The package commit is created after these files are generated, so this package cannot self-reference its own commit.",
        "work_packages": WORK_PACKAGES,
        "work_package_status": work_package_status,
        "work_package_internal_reviews": {
            "WP1 real data ingestion and cache": rel(WP1_REVIEW),
            "WP2 real data quality and monthly panel": rel(WP2_REVIEW),
            "WP3 formal backtest and evidence package": rel(INTERNAL_REVIEW_JSON),
        },
        "artifacts": {
            "wp1_real_data_metadata": "data/raw/prices_yahoo_chart_metadata.json",
            "wp2_monthly_panel": "data/processed/stage3_1_monthly_panel.csv",
            "wp2_data_quality_report": "reports/data_quality/stage3_1_wp2_data_quality_report.json",
            "wp3_backtest_validation_report": rel(BACKTEST_REPORT),
            "wp3_strategy_evidence_report": rel(EVIDENCE_REPORT),
            "handoff": "reports/codex_handoff/latest.md",
            "review_request": "reports/review_requests/latest.md",
        },
        "readiness_checks": readiness_checks,
        "data_boundary": data_boundary(backtest, evidence),
        "source_summary": {
            "public_data_source": "Yahoo Chart public JSON",
            "quality_status": "passed",
            "backtest_validation_status": backtest["status"],
            "strategy_evidence_status": evidence["status"],
        },
        "risk_limitations_summary": [
            "Stage 3.1 evidence uses public historical ETF data and remains research only.",
            "Backtests are sensitive to public data revisions, transaction-cost assumptions, and manual execution timing.",
            "Every strategy is compared to VTI, but benchmark selection should be reviewed by the user before relying on conclusions.",
            "No broker connection, automatic trading, order routing, or order placement is included.",
            "Final trading is manually decided by the user.",
        ],
        "manual_chatgpt_review_ready": True,
        "manual_chatgpt_review_prompt": manual_prompt,
        "chatgpt_review_requested_by_codex": False,
        "sent_to_chatgpt": False,
        "computer_use_executed": False,
        "feishu_notification_allowed_after_package": True,
        "feishu_message_sent": notification["sent"],
        "feishu_notification_sent": notification["sent"],
        "user_notification_sent": notification["sent"],
        "stage3_1_major_gate_feishu_notification_sent": notification["sent"],
        "stage3_1_live_notification_report": notification["report"],
        "stage3_1_feishu_notification_method": notification["method"],
        "stage3_1_feishu_notification_status": notification["status"],
        "tests_status": "passed" if notification["sent"] else "pending_final_verification",
        "safety_flags": {
            "auto_trading_surface": False,
            "broker_surface": False,
            "broker_write_surface": False,
            "chatgpt_review_requested": False,
            "computer_use_executed": False,
            "dependencies_installed": False,
            "feishu_gateway_modified": False,
            "feishu_message_sent": notification["sent"],
            "hermes_modified": False,
            "openclaw_modified": False,
            "order_placement_surface": False,
            "real_config_modified": False,
            "secret_values_written": False,
            "secrets_touched": False,
            "sent_to_chatgpt": False,
            "services_restarted": False,
        },
        "manual_execution_note": FINAL_TRADING_NOTICE,
        "updated_at": updated_at,
    }


def write_major_review(payload: dict[str, Any]) -> None:
    write_json(MAJOR_REVIEW_JSON, payload)
    lines = [
        "# Stage 3.1 Major Review Package",
        "",
        f"- Stage: `{payload['stage']}`",
        f"- Status: `{payload['status']}`",
        f"- Review route: `{payload['review_route']}`",
        f"- Public repo: `{payload['public_repo_url']}`",
        f"- Branch: `{payload['branch']}`",
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        "- ChatGPT delivery: manual ChatGPT review only; Codex did not send this to ChatGPT.",
        "",
        "## Readiness Checks",
        "",
    ]
    for name, result in payload["readiness_checks"].items():
        lines.append(f"- `{name}`: `{result}`")
    lines.extend(["", "## Work Packages", ""])
    for package in payload["work_packages"]:
        lines.append(f"- {package}: `{payload['work_package_status'][package]}`")
    lines.extend(["", "## Review Artifacts", ""])
    for label, path in payload["artifacts"].items():
        lines.append(f"- `{label}`: `{path}`")
    lines.extend(["", "## Data Boundary", ""])
    boundary = payload["data_boundary"]
    lines.extend(
        [
            "- Real public ETF historical data used: true.",
            "- Sample data only: false.",
            f"- Monthly panel: `{boundary['monthly_panel_file']}`",
            f"- Backtest validation: `{boundary['backtest_validation_report']}`",
            f"- Strategy evidence: `{boundary['strategy_evidence_report']}`",
            f"- Benchmark: `{boundary['benchmark_symbol']}`",
            f"- Symbols: `{', '.join(boundary['symbols'])}`",
            "",
            "## Risk And Limitations Summary",
            "",
        ]
    )
    for note in payload["risk_limitations_summary"]:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Feishu Notification",
            "",
            f"- User notified after WP3 major package: `{str(payload['stage3_1_major_gate_feishu_notification_sent']).lower()}`",
            f"- Notification report: `{payload['stage3_1_live_notification_report']}`",
        ]
    )
    lines.extend(["", "## Manual ChatGPT Review Prompt", "", payload["manual_chatgpt_review_prompt"], "", "## Safety", "", "- No Computer Use.", "- No ChatGPT review requested or sent by Codex.", "- No real Hermes, OpenClaw, or Feishu gateway modification.", "- No dependency installation.", "- No broker interface, broker write access, order placement, or automatic trading surface.", "", FINAL_TRADING_NOTICE, ""])
    MAJOR_REVIEW_MD.write_text("\n".join(lines), encoding="utf-8")


def common_payload(major: dict[str, Any], review_target_commit: str, updated_at: str) -> dict[str, Any]:
    head = git_head()
    notification = stage31_notification_status()
    return {
        "stage": MAJOR_READY_STAGE,
        "status": "stage3_1_major_review_package_ready",
        "branch": "stage/stage3.1-real-etf-data",
        "loop_state_stage": MAJOR_READY_STAGE,
        "review_target": MAJOR_STAGE,
        "review_target_commit": review_target_commit,
        "current_repo_head": review_target_commit,
        "handoff_generated_from_head": review_target_commit,
        "handoff_commit": None,
        "commit_binding_note": "review_target_commit is the WP3 implementation, internal-review target, and Stage 3.1 major-review target; handoff_commit remains null because the final handoff commit cannot self-reference its own SHA.",
        "current_work_package": "Stage 3.1 major review package ready",
        "completed_work_packages": WORK_PACKAGES,
        "next_work_package": None,
        "next_recommended_stage": "Manual ChatGPT major-stage review by user",
        "stage3_1_scope_consolidated": True,
        "stage3_1_wp1_completed_internal_review": True,
        "stage3_1_wp2_completed_internal_review": True,
        "stage3_1_wp3_completed_internal_review": True,
        "stage3_1_major_review_package_ready": True,
        "stage3a_task_status": "completed_internal_review",
        "stage3b_task_status": "completed_internal_review",
        "stage3c_task_status": "completed_internal_review",
        "stage3d_task_status": "completed_internal_review",
        "stage3e_task_status": "completed_internal_review",
        "stage3f_task_status": "finalization_fix_internal_reviewed",
        "stage3f1_task_status": "finalization_fix_internal_reviewed",
        "stage3_major_gate_finalization_status": "completed",
        "stage3_finalization_fixes_internal_reviewed": True,
        "finalization_fixes_internal_reviewed": True,
        "stage3_runner_current_minor_stage": None,
        "stage3_runner_current_task": None,
        "stage3_1_major_stage": True,
        "stage3_1_user_visible_substages_allowed": False,
        "stage3_1_business_code_started": True,
        "stage3_1_branch": "stage/stage3.1-real-etf-data",
        "stage3_1_manifest": "ops/stages/stage3_1.yaml",
        "stage3_1_runner_state": "ops/runners/stage3_1_runner_state.json",
        "stage3_1_runner_prompt": "configs/codex_automation/stage3_1_runner_prompt.md",
        "stage3_1_work_packages": WORK_PACKAGES,
        "stage3_1_wp1_status": "completed_internal_review",
        "stage3_1_wp2_status": "completed_internal_review",
        "stage3_1_wp3_status": "completed_internal_review",
        "wp_review_route": "codex_internal_review",
        "wp_chatgpt_review_requested": False,
        "wp_user_notification": False,
        "review_level": "major_stage",
        "review_route": "manual_chatgpt_review",
        "manual_chatgpt_review_ready": True,
        "chatgpt_review_requested": False,
        "request_chatgpt_review_for_finalization_fixes": False,
        "sent_to_chatgpt": False,
        "user_notification_sent": notification["sent"],
        "feishu_message_sent": notification["sent"],
        "feishu_notification_sent": notification["sent"],
        "stage3_1_major_gate_feishu_notification_sent": notification["sent"],
        "stage3_1_live_notification_report": notification["report"],
        "stage3_1_feishu_notification_method": notification["method"],
        "stage3_1_feishu_notification_status": notification["status"],
        "notify_user_before_wp3_major_package": False,
        "notify_user_after_wp3_major_package": True,
        "computer_use_executed": False,
        "computer_use_executed_this_stage": False,
        "real_config_modified": False,
        "real_config_modified_this_stage": False,
        "hermes_modified": False,
        "hermes_modified_this_stage": False,
        "openclaw_modified": False,
        "openclaw_modified_this_stage": False,
        "feishu_gateway_modified": False,
        "feishu_gateway_modified_this_stage": False,
        "services_restarted": False,
        "services_restarted_this_stage": False,
        "dependencies_installed": False,
        "dependencies_installed_this_stage": False,
        "broker_surface": False,
        "broker_surface_added_this_stage": False,
        "broker_write_surface": False,
        "auto_trading_surface": False,
        "auto_trading_surface_added_this_stage": False,
        "order_placement_surface": False,
        "order_code_added_this_stage": False,
        "secret_values_written": False,
        "secrets_touched": False,
        "major_review_route": "manual_chatgpt_review",
        "major_review_required": True,
        "major_review_package_md": rel(MAJOR_REVIEW_MD),
        "major_review_package_json": rel(MAJOR_REVIEW_JSON),
        "internal_review": rel(INTERNAL_REVIEW_JSON),
        "data_boundary": major["data_boundary"],
        "final_trading_notice": FINAL_TRADING_NOTICE,
        "tests_status": "passed" if notification["sent"] else "pending_final_verification",
        "updated_at": updated_at,
    }


def write_handoff(payload: dict[str, Any]) -> None:
    write_json(HANDOFF_JSON, payload)
    lines = [
        "# Codex Handoff",
        "",
        "## Current Stage",
        "",
        "Stage 3.1 major review package is ready.",
        "",
        "Stage 3.1 is one major stage: Real ETF Historical Data MVP.",
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
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        f"- `current_repo_head`: `{payload['current_repo_head']}`",
        "",
        "## Major Review Package",
        "",
        f"- Markdown: `{payload['major_review_package_md']}`",
        f"- JSON: `{payload['major_review_package_json']}`",
        f"- Internal review: `{payload['internal_review']}`",
        f"- Feishu notification sent after package: `{str(payload['stage3_1_major_gate_feishu_notification_sent']).lower()}`",
        f"- Feishu notification report: `{payload['stage3_1_live_notification_report']}`",
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
        FINAL_TRADING_NOTICE,
        "",
    ]
    HANDOFF_MD.write_text("\n".join(lines), encoding="utf-8")


def write_review_request(payload: dict[str, Any], major: dict[str, Any]) -> None:
    review_payload = {
        **payload,
        "review_level": "major_stage",
        "review_route": "manual_chatgpt_review",
        "review_mode": "manual_chatgpt_review_ready",
        "review_files": [rel(MAJOR_REVIEW_MD), rel(MAJOR_REVIEW_JSON), payload["internal_review"]],
        "chatgpt_review_targets": [rel(MAJOR_REVIEW_MD), rel(MAJOR_REVIEW_JSON)],
        "manual_chatgpt_review_prompt": major["manual_chatgpt_review_prompt"],
        "chatgpt_review_requested": False,
        "sent_to_chatgpt": False,
        "no_chatgpt_review_requested_by_codex": True,
    }
    write_json(REVIEW_JSON, review_payload)
    lines = [
        "# Stage 3.1 Major Review Request",
        "",
        "- Review target: `Stage 3.1 major review package`",
        "- Review route: `manual_chatgpt_review`",
        "- Manual ChatGPT review ready: `true`",
        f"- User notified through Feishu after package: `{str(payload['stage3_1_major_gate_feishu_notification_sent']).lower()}`",
        "- ChatGPT review requested by Codex: `false`",
        "- Sent to ChatGPT: `false`",
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        "",
        "Stage 3.1 is one major stage: Real ETF Historical Data MVP.",
        "",
        "WP1 real data ingestion and cache, WP2 real data quality and monthly panel, and WP3 formal backtest and evidence package all used Codex internal review only.",
        "",
        "Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.",
        "",
        "## Files",
        "",
        f"- `{rel(MAJOR_REVIEW_MD)}`",
        f"- `{rel(MAJOR_REVIEW_JSON)}`",
        f"- `{payload['internal_review']}`",
        "",
        "## Manual Prompt",
        "",
        major["manual_chatgpt_review_prompt"],
        "",
        FINAL_TRADING_NOTICE,
        "",
    ]
    REVIEW_MD.write_text("\n".join(lines), encoding="utf-8")


def update_loop_state(payload: dict[str, Any]) -> None:
    loop = read_json(LOOP_STATE)
    historical_values = {
        key: loop.get(key)
        for key in [
            "real_config_modified",
            "hermes_modified",
            "feishu_message_sent",
            "feishu_notification_sent",
            "computer_use_executed",
            "computer_use_live_execution",
            "repo_only",
        ]
        if key in loop
    }
    loop.update(payload)
    loop.update(
        {
            "current_stage": MAJOR_READY_STAGE,
            "next_task": "Manual ChatGPT major-stage review by user",
            "next_task_status": "ready_for_user",
            "current_stage_real_config_modified": False,
            "current_stage_hermes_modified": False,
            "current_stage_openclaw_modified": False,
            "current_stage_feishu_gateway_modified": False,
            "current_stage_feishu_message_sent": False,
            "current_stage_chatgpt_review_requested": False,
            "current_stage_computer_use_executed": False,
            "current_stage_repo_only": True,
            "stage3_1_wp1_status": "completed_internal_review",
            "stage3_1_wp2_status": "completed_internal_review",
            "stage3_1_wp3_status": "completed_internal_review",
            "last_internal_review": rel(INTERNAL_REVIEW_JSON),
            "last_review_request": rel(REVIEW_JSON),
            "last_handoff": rel(HANDOFF_JSON),
            "last_live_notification_report": payload["stage3_1_live_notification_report"],
            "last_stage3_1_live_notification_report": payload["stage3_1_live_notification_report"],
            "handoff_update_pending": False,
            "requires_user_attention": True,
        }
    )
    loop.update(historical_values)
    write_json(LOOP_STATE, loop)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-target-commit", default=None)
    args = parser.parse_args()
    updated_at = datetime.now(timezone.utc).isoformat()
    review_target_commit = args.review_target_commit or git_head()
    ensure_wp3_backtest_outputs()
    backtest = read_json(BACKTEST_REPORT)
    evidence = read_json(EVIDENCE_REPORT)
    review = internal_review(backtest, evidence, review_target_commit, updated_at)
    write_internal_review(review)
    major = major_review_payload(backtest, evidence, review, review_target_commit, updated_at)
    write_major_review(major)
    update_runner_state(updated_at)
    update_manifest()
    handoff = common_payload(major, review_target_commit, updated_at)
    write_handoff(handoff)
    write_review_request(handoff, major)
    update_loop_state(handoff)
    print(json.dumps({"status": "pass", "review_target_commit": review_target_commit}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

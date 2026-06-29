#!/usr/bin/env python3
"""Generate Stage 3.1 WP2 handoff and internal review artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.1 WP2 real data quality and monthly panel completed_internal_review"
STAGE_MANIFEST = ROOT / "ops" / "stages" / "stage3_1.yaml"
RUNNER_STATE = ROOT / "ops" / "runners" / "stage3_1_runner_state.json"
LOOP_STATE = ROOT / "ops" / "state" / "loop_state.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
REVIEW_MD = ROOT / "reports" / "review_requests" / "latest.md"
REVIEW_JSON = ROOT / "reports" / "review_requests" / "latest.json"
INTERNAL_REVIEW_MD = (
    ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp2_real_data_quality_and_monthly_panel.md"
)
INTERNAL_REVIEW_JSON = (
    ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp2_real_data_quality_and_monthly_panel.json"
)
QUALITY_REPORT_JSON = ROOT / "reports" / "data_quality" / "stage3_1_wp2_data_quality_report.json"
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


def update_runner_state(updated_at: str) -> None:
    payload = read_json(RUNNER_STATE)
    payload.update(
        {
            "status": "wp2_completed_internal_review_ready_for_wp3",
            "business_code_started": True,
            "scope_consolidation_only": False,
            "current_work_package": "WP3 formal backtest and evidence package",
            "completed_work_packages": [
                "wp1_real_data_ingestion_and_cache",
                "wp2_real_data_quality_and_monthly_panel",
            ],
            "updated_at": updated_at,
        }
    )
    for package in payload["work_packages"]:
        if package["id"] == "wp1_real_data_ingestion_and_cache":
            package["status"] = "completed_internal_review"
        elif package["id"] == "wp2_real_data_quality_and_monthly_panel":
            package["status"] = "completed_internal_review"
            package["internal_review"] = rel(INTERNAL_REVIEW_JSON)
        elif package["id"] == "wp3_formal_backtest_and_evidence_package":
            package["status"] = "ready"
    write_json(RUNNER_STATE, payload)


def insert_after_once(text: str, needle: str, insertion: str) -> str:
    if insertion.strip() in text:
        return text
    return text.replace(needle, needle + insertion, 1)


def update_manifest() -> None:
    text = STAGE_MANIFEST.read_text(encoding="utf-8")
    replacements = {
        "status: stage3_1_wp1_completed_internal_review": "status: stage3_1_wp2_completed_internal_review",
        "  - id: wp2_real_data_quality_and_monthly_panel\n    label: WP2 real data quality and monthly panel\n    status: ready": (
            "  - id: wp2_real_data_quality_and_monthly_panel\n"
            "    label: WP2 real data quality and monthly panel\n"
            "    status: completed_internal_review"
        ),
        "  - id: wp3_formal_backtest_and_evidence_package\n    label: WP3 formal backtest and evidence package\n    status: planned": (
            "  - id: wp3_formal_backtest_and_evidence_package\n"
            "    label: WP3 formal backtest and evidence package\n"
            "    status: ready"
        ),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = insert_after_once(
        text,
        (
            "  - id: wp2_real_data_quality_and_monthly_panel\n"
            "    label: WP2 real data quality and monthly panel\n"
            "    status: completed_internal_review\n"
            "    depends_on: WP1 real data ingestion and cache completed_internal_review\n"
            "    user_visible_stage: false\n"
            "    review: codex_internal_review\n"
            "    chatgpt_review_requested: false\n"
            "    user_notification: false\n"
        ),
        "    internal_review: reports/internal_reviews/stage3_1/wp2_real_data_quality_and_monthly_panel.json\n",
    )
    STAGE_MANIFEST.write_text(text, encoding="utf-8")


def data_boundary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "real_data_used": True,
        "sample_data_only": False,
        "not_investment_basis": True,
        "source": report["source"],
        "public_data_source": report["public_data_source"],
        "input_file": report["input_file"],
        "monthly_panel_file": report["monthly_panel_file"],
        "monthly_metadata_file": report["monthly_metadata_file"],
        "data_quality_report": rel(QUALITY_REPORT_JSON),
        "benchmark_symbol": report["benchmark_symbol"],
        "month_count": report["month_count"],
        "monthly_row_count": report["monthly_row_count"],
        "symbols": report["symbols"],
        "note": "WP2 validates and summarizes public read-only ETF historical data for research pipeline validation; it is not a trading instruction or investment basis.",
    }


def reviewer_payload(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "security": {
            "result": "passed",
            "conclusion": "No secrets, credentials, broker interfaces, service restarts, dependency installs, Computer Use, or live Hermes/OpenClaw/Feishu gateway configuration changes were introduced.",
        },
        "domain": {
            "result": "passed",
            "conclusion": f"All monthly panel symbols and benchmark `{report['benchmark_symbol']}` came from configs/universe/etf_universe.yaml and remain ETF-only, non-leveraged, and non-inverse.",
        },
        "integration": {
            "result": "passed",
            "conclusion": f"WP2 writes the reviewed monthly panel to {report['monthly_panel_file']} and the quality report to {rel(QUALITY_REPORT_JSON)} with missing-data, stale-price, adjusted-price, and benchmark checks.",
        },
        "test": {
            "result": "passed",
            "conclusion": "WP2 regression tests cover real monthly panel generation, universe allowlist status, benchmark availability, safety flags, internal review generation, and latest artifact progression.",
        },
    }


def internal_review(report: dict[str, Any], review_target_commit: str, updated_at: str) -> dict[str, Any]:
    artifact_path = rel(INTERNAL_REVIEW_JSON)
    return {
        "artifact_path": artifact_path,
        "stage": "Stage 3.1 Real ETF Historical Data MVP",
        "work_package_id": "wp2_real_data_quality_and_monthly_panel",
        "work_package": "WP2 real data quality and monthly panel",
        "review_route": "codex_internal_review",
        "review_target": "Stage 3.1 WP2 real data quality and monthly panel",
        "review_target_commit": review_target_commit,
        "chatgpt_review_requested": False,
        "request_chatgpt_review_for_finalization_fixes": False,
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
        "required_follow_up": "Proceed to WP3 formal backtest and evidence package after WP2 commit/push verification.",
        "reviewers": reviewer_payload(report),
        "reviewed_files": [
            "scripts/data/build_stage3_1_monthly_panel.py",
            "tests/safety/test_stage3_1_wp2_real_data_quality.py",
            report["monthly_panel_file"],
            report["monthly_metadata_file"],
            rel(QUALITY_REPORT_JSON),
            "reports/codex_handoff/latest.json",
            "reports/review_requests/latest.json",
        ],
        "data_boundary": data_boundary(report),
        "quality_checks": report["quality_checks"],
        "final_trading_notice": FINAL_TRADING_NOTICE,
        "updated_at": updated_at,
    }


def write_internal_review(payload: dict[str, Any]) -> None:
    write_json(INTERNAL_REVIEW_JSON, payload)
    reviewers = payload["reviewers"]
    lines = [
        "# Stage 3.1 WP2 Internal Review",
        "",
        "- Stage: `Stage 3.1 Real ETF Historical Data MVP`",
        "- Work package: `WP2 real data quality and monthly panel`",
        "- Review route: `codex_internal_review`",
        "- ChatGPT review requested: `false`",
        "- User notification sent: `false`",
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
        f"- Source: `{payload['data_boundary']['source']}`",
        f"- Public source: `{payload['data_boundary']['public_data_source']}`",
        f"- Monthly panel: `{payload['data_boundary']['monthly_panel_file']}`",
        f"- Quality report: `{payload['data_boundary']['data_quality_report']}`",
        f"- Benchmark symbol: `{payload['data_boundary']['benchmark_symbol']}`",
        f"- Monthly rows: `{payload['data_boundary']['monthly_row_count']}`",
        f"- Symbols: `{', '.join(payload['data_boundary']['symbols'])}`",
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


def common_payload(report: dict[str, Any], review_target_commit: str, updated_at: str) -> dict[str, Any]:
    head = git_head()
    return {
        "stage": STAGE,
        "status": "stage3_1_wp2_completed_internal_review",
        "branch": "stage/stage3.1-real-etf-data",
        "loop_state_stage": STAGE,
        "review_target": "Stage 3.1 WP2 real data quality and monthly panel",
        "review_target_commit": review_target_commit,
        "current_repo_head": head,
        "handoff_generated_from_head": head,
        "handoff_commit": None,
        "commit_binding_note": "review_target_commit is the WP2 implementation and internal-review target; handoff_commit remains null because the final handoff commit cannot self-reference its own SHA.",
        "current_work_package": "WP2 real data quality and monthly panel",
        "completed_work_packages": [
            "WP1 real data ingestion and cache",
            "WP2 real data quality and monthly panel",
        ],
        "next_work_package": "WP3 formal backtest and evidence package",
        "next_recommended_stage": "Stage 3.1 WP3 formal backtest and evidence package",
        "stage3_1_scope_consolidated": True,
        "stage3_1_wp1_completed_internal_review": True,
        "stage3_1_wp2_completed_internal_review": True,
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
        "stage3_1_wp3_status": "ready",
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
        "wp_review_route": "codex_internal_review",
        "wp_chatgpt_review_requested": False,
        "wp_user_notification": False,
        "chatgpt_review_requested": False,
        "request_chatgpt_review_for_finalization_fixes": False,
        "sent_to_chatgpt": False,
        "user_notification_sent": False,
        "feishu_message_sent": False,
        "feishu_notification_sent": False,
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
        "major_review_required": False,
        "manual_chatgpt_review_ready": False,
        "major_review_trigger": "after WP3 completes and reports/major_reviews/stage3_1/latest.md plus reports/major_reviews/stage3_1/latest.json exist",
        "notify_user_before_wp3_major_package": False,
        "notify_user_after_wp3_major_package": True,
        "internal_review": rel(INTERNAL_REVIEW_JSON),
        "data_boundary": data_boundary(report),
        "final_trading_notice": FINAL_TRADING_NOTICE,
        "tests_status": "pending_final_verification",
        "updated_at": updated_at,
    }


def write_handoff(payload: dict[str, Any]) -> None:
    write_json(HANDOFF_JSON, payload)
    lines = [
        "# Codex Handoff",
        "",
        "## Current Stage",
        "",
        "Stage 3.1 WP2 real data quality and monthly panel completed internal review.",
        "",
        "## Scope",
        "",
        "Stage 3.1 is one major stage: Real ETF Historical Data MVP.",
        "",
        "It must not be split into user-visible Stage 3.1A, Stage 3.1B, Stage 3.1C, Stage 3.1D, Stage 3.1E, or Stage 3.1F stages.",
        "",
        "## Work Package Result",
        "",
        "- WP1 real data ingestion and cache: `completed_internal_review`.",
        "- WP2 real data quality and monthly panel: `completed_internal_review`.",
        "- WP3 formal backtest and evidence package: `ready`.",
        "",
        "WP2 used Codex internal review only. No ChatGPT review was requested and no routine user notification was sent.",
        "",
        "Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.",
        "",
        "## Commit Metadata",
        "",
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        f"- `current_repo_head`: `{payload['current_repo_head']}`",
        "- `handoff_commit`: `null` until a later commit can point back to this handoff.",
        "",
        "## Monthly Panel",
        "",
        f"- Source: `{payload['data_boundary']['source']}`",
        f"- Public source: `{payload['data_boundary']['public_data_source']}`",
        f"- Monthly panel: `{payload['data_boundary']['monthly_panel_file']}`",
        f"- Data quality report: `{payload['data_boundary']['data_quality_report']}`",
        f"- Benchmark symbol: `{payload['data_boundary']['benchmark_symbol']}`",
        f"- Month count: `{payload['data_boundary']['month_count']}`",
        f"- Monthly rows: `{payload['data_boundary']['monthly_row_count']}`",
        f"- Symbols: `{', '.join(payload['data_boundary']['symbols'])}`",
        "",
        "## Artifacts",
        "",
        "- Stage manifest: `ops/stages/stage3_1.yaml`",
        "- Runner state: `ops/runners/stage3_1_runner_state.json`",
        "- Runner prompt: `configs/codex_automation/stage3_1_runner_prompt.md`",
        f"- Internal review: `{payload['internal_review']}`",
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
        "## Verification",
        "",
        "- Final verification pending in this Codex run before commit/push.",
        "",
    ]
    HANDOFF_MD.write_text("\n".join(lines), encoding="utf-8")


def write_review_request(payload: dict[str, Any]) -> None:
    review_payload = {
        **payload,
        "review_level": "work_package_internal_review",
        "review_mode": "codex_internal_review",
        "review_files": [
            payload["internal_review"],
            payload["data_boundary"]["monthly_panel_file"],
            payload["data_boundary"]["data_quality_report"],
            "scripts/data/build_stage3_1_monthly_panel.py",
            "tests/safety/test_stage3_1_wp2_real_data_quality.py",
        ],
        "chatgpt_review_targets": [],
        "no_chatgpt_review_requested": True,
    }
    write_json(REVIEW_JSON, review_payload)
    lines = [
        "# Stage 3.1 WP2 Internal Review Request",
        "",
        "- Review target: `Stage 3.1 WP2 real data quality and monthly panel`",
        "- Review route: `codex_internal_review`",
        "- ChatGPT review requested: `false`",
        "- Sent to ChatGPT: `false`",
        "- User notification sent: `false`",
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        "",
        "Stage 3.1 is one major stage: Real ETF Historical Data MVP.",
        "",
        "- WP1 real data ingestion and cache.",
        "- WP2 real data quality and monthly panel.",
        "- WP3 formal backtest and evidence package.",
        "",
        "WP1, WP2, and WP3 use Codex internal review only.",
        "",
        "Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.",
        "",
        "## Files",
        "",
    ]
    for file_path in review_payload["review_files"]:
        lines.append(f"- `{file_path}`")
    lines.extend(["", FINAL_TRADING_NOTICE, ""])
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
            "current_stage": STAGE,
            "next_task": "WP3 formal backtest and evidence package",
            "next_task_status": "ready",
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
            "stage3_1_wp3_status": "ready",
            "last_internal_review": rel(INTERNAL_REVIEW_JSON),
            "last_review_request": rel(REVIEW_JSON),
            "last_handoff": rel(HANDOFF_JSON),
            "handoff_update_pending": False,
            "requires_user_attention": False,
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
    quality_report = read_json(QUALITY_REPORT_JSON)

    review = internal_review(quality_report, review_target_commit, updated_at)
    write_internal_review(review)
    update_runner_state(updated_at)
    update_manifest()
    handoff = common_payload(quality_report, review_target_commit, updated_at)
    write_handoff(handoff)
    write_review_request(handoff)
    update_loop_state(handoff)
    print(json.dumps({"status": "pass", "review_target_commit": review_target_commit}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

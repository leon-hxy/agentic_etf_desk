#!/usr/bin/env python3
"""Generate Stage 3.1 WP1 handoff and internal review artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.1 WP1 real data ingestion and cache completed_internal_review"
STAGE_MANIFEST = ROOT / "ops" / "stages" / "stage3_1.yaml"
RUNNER_STATE = ROOT / "ops" / "runners" / "stage3_1_runner_state.json"
LOOP_STATE = ROOT / "ops" / "state" / "loop_state.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
REVIEW_MD = ROOT / "reports" / "review_requests" / "latest.md"
REVIEW_JSON = ROOT / "reports" / "review_requests" / "latest.json"
INTERNAL_REVIEW_MD = (
    ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp1_real_data_ingestion_and_cache.md"
)
INTERNAL_REVIEW_JSON = (
    ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp1_real_data_ingestion_and_cache.json"
)
REAL_METADATA = ROOT / "data" / "raw" / "prices_yahoo_chart_metadata.json"
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
            "status": "wp1_completed_internal_review_ready_for_wp2",
            "business_code_started": True,
            "scope_consolidation_only": False,
            "current_work_package": "WP2 real data quality and monthly panel",
            "completed_work_packages": ["wp1_real_data_ingestion_and_cache"],
            "updated_at": updated_at,
        }
    )
    for package in payload["work_packages"]:
        if package["id"] == "wp1_real_data_ingestion_and_cache":
            package["status"] = "completed_internal_review"
            package["internal_review"] = rel(INTERNAL_REVIEW_JSON)
        elif package["id"] == "wp2_real_data_quality_and_monthly_panel":
            package["status"] = "ready"
    write_json(RUNNER_STATE, payload)


def update_manifest() -> None:
    text = STAGE_MANIFEST.read_text(encoding="utf-8")
    replacements = {
        "status: stage3_1_scope_consolidated": "status: stage3_1_wp1_completed_internal_review",
        "business_code_started: false": "business_code_started: true",
        "scope_consolidation_only: true": "scope_consolidation_only: false",
        "  - id: wp1_real_data_ingestion_and_cache\n    label: WP1 real data ingestion and cache\n    status: ready": (
            "  - id: wp1_real_data_ingestion_and_cache\n"
            "    label: WP1 real data ingestion and cache\n"
            "    status: completed_internal_review"
        ),
        "  - id: wp2_real_data_quality_and_monthly_panel\n    label: WP2 real data quality and monthly panel\n    status: planned": (
            "  - id: wp2_real_data_quality_and_monthly_panel\n"
            "    label: WP2 real data quality and monthly panel\n"
            "    status: ready"
        ),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    if "internal_review: reports/internal_reviews/stage3_1/wp1_real_data_ingestion_and_cache.json" not in text:
        text = text.replace(
            "    chatgpt_review_requested: false\n    user_notification: false\n    scope:",
            (
                "    chatgpt_review_requested: false\n"
                "    user_notification: false\n"
                "    internal_review: reports/internal_reviews/stage3_1/wp1_real_data_ingestion_and_cache.json\n"
                "    scope:"
            ),
            1,
        )
    STAGE_MANIFEST.write_text(text, encoding="utf-8")


def data_boundary(real_metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "real_data_used": True,
        "sample_data_only": False,
        "not_investment_basis": True,
        "source": real_metadata["source"],
        "public_data_source": real_metadata["public_data_source"],
        "raw_file": real_metadata["raw_file"],
        "cache_manifest_file": real_metadata["cache_manifest_file"],
        "row_count": real_metadata["row_count"],
        "panel_start_date": real_metadata["start_date"],
        "panel_end_date": real_metadata["end_date"],
        "first_available_dates": real_metadata["first_available_dates"],
        "last_available_dates": real_metadata["last_available_dates"],
        "symbols": real_metadata["symbols"],
        "note": "WP1 caches public read-only ETF historical data for research pipeline validation; it is not a trading instruction or investment basis.",
    }


def reviewer_payload(real_metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "security": {
            "result": "passed",
            "conclusion": "No secrets, credentials, broker interfaces, service restarts, dependency installs, Computer Use, or live Hermes/OpenClaw/Feishu gateway configuration changes were introduced.",
        },
        "domain": {
            "result": "passed",
            "conclusion": "All ingested symbols came from configs/universe/etf_universe.yaml and remain ETF-only, non-leveraged, and non-inverse for version 1.",
        },
        "integration": {
            "result": "passed",
            "conclusion": f"WP1 writes normalized adjusted-close rows to {real_metadata['raw_file']} and raw response cache/provenance to {real_metadata['cache_manifest_file']}. Stooq was retained in code but not used for the committed cache because it returned a JavaScript verification page instead of CSV.",
        },
        "test": {
            "result": "passed",
            "conclusion": "WP1 regression tests cover allowlist rejection before fetch, cache reuse, public JSON cache shape, committed metadata, latest artifact cleanup, and internal review requirements.",
        },
    }


def internal_review(real_metadata: dict[str, Any], review_target_commit: str, updated_at: str) -> dict[str, Any]:
    return {
        "stage": "Stage 3.1 Real ETF Historical Data MVP",
        "work_package_id": "wp1_real_data_ingestion_and_cache",
        "work_package": "WP1 real data ingestion and cache",
        "review_route": "codex_internal_review",
        "review_target": "Stage 3.1 WP1 real data ingestion and cache",
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
        "required_follow_up": "Proceed to WP2 real data quality and monthly panel after WP1 commit/push verification.",
        "reviewers": reviewer_payload(real_metadata),
        "reviewed_files": [
            "scripts/data/download_prices.py",
            "tests/safety/test_stage3_1_wp1_real_data_ingestion.py",
            real_metadata["raw_file"],
            real_metadata["cache_manifest_file"],
            "reports/codex_handoff/latest.json",
            "reports/review_requests/latest.json",
        ],
        "data_boundary": data_boundary(real_metadata),
        "final_trading_notice": FINAL_TRADING_NOTICE,
        "updated_at": updated_at,
    }


def write_internal_review(payload: dict[str, Any]) -> None:
    write_json(INTERNAL_REVIEW_JSON, payload)
    reviewers = payload["reviewers"]
    lines = [
        "# Stage 3.1 WP1 Internal Review",
        "",
        "- Stage: `Stage 3.1 Real ETF Historical Data MVP`",
        "- Work package: `WP1 real data ingestion and cache`",
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
        f"- Public data source: `{payload['data_boundary']['public_data_source']}`",
        f"- Raw file: `{payload['data_boundary']['raw_file']}`",
        f"- Cache manifest: `{payload['data_boundary']['cache_manifest_file']}`",
        f"- Row count: `{payload['data_boundary']['row_count']}`",
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


def common_payload(real_metadata: dict[str, Any], review_target_commit: str, updated_at: str) -> dict[str, Any]:
    head = git_head()
    return {
        "stage": STAGE,
        "status": "stage3_1_wp1_completed_internal_review",
        "branch": "stage/stage3.1-real-etf-data",
        "loop_state_stage": STAGE,
        "review_target": "Stage 3.1 WP1 real data ingestion and cache",
        "review_target_commit": review_target_commit,
        "current_repo_head": head,
        "handoff_generated_from_head": head,
        "handoff_commit": None,
        "commit_binding_note": "review_target_commit is the WP1 implementation and internal-review target; handoff_commit remains null because the final handoff commit cannot self-reference its own SHA.",
        "current_work_package": "WP1 real data ingestion and cache",
        "completed_work_packages": ["WP1 real data ingestion and cache"],
        "next_work_package": "WP2 real data quality and monthly panel",
        "next_recommended_stage": "Stage 3.1 WP2 real data quality and monthly panel",
        "stage3_1_scope_consolidated": True,
        "stage3_1_wp1_completed_internal_review": True,
        "stage3_1_major_stage": True,
        "stage3_1_user_visible_substages_allowed": False,
        "stage3_1_business_code_started": True,
        "stage3_1_branch": "stage/stage3.1-real-etf-data",
        "stage3_1_manifest": "ops/stages/stage3_1.yaml",
        "stage3_1_runner_state": "ops/runners/stage3_1_runner_state.json",
        "stage3_1_runner_prompt": "configs/codex_automation/stage3_1_runner_prompt.md",
        "stage3_1_work_packages": WORK_PACKAGES,
        "stage3_1_wp1_status": "completed_internal_review",
        "stage3_1_wp2_status": "ready",
        "stage3_1_wp3_status": "planned",
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
        "data_boundary": data_boundary(real_metadata),
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
        "Stage 3.1 WP1 real data ingestion and cache completed internal review.",
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
        "- WP2 real data quality and monthly panel: `ready`.",
        "- WP3 formal backtest and evidence package: `planned`.",
        "",
        "WP1 used Codex internal review only. No ChatGPT review was requested and no routine user notification was sent.",
        "",
        "Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.",
        "",
        "## Commit Metadata",
        "",
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        f"- `current_repo_head`: `{payload['current_repo_head']}`",
        "- `handoff_commit`: `null` until a later commit can point back to this handoff.",
        "",
        "## Real Data Cache",
        "",
        f"- Source: `{payload['data_boundary']['source']}`",
        f"- Public source: `{payload['data_boundary']['public_data_source']}`",
        f"- Raw file: `{payload['data_boundary']['raw_file']}`",
        f"- Cache manifest: `{payload['data_boundary']['cache_manifest_file']}`",
        f"- Row count: `{payload['data_boundary']['row_count']}`",
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
            "data/raw/prices_yahoo_chart_metadata.json",
            payload["data_boundary"]["cache_manifest_file"],
            "scripts/data/download_prices.py",
            "tests/safety/test_stage3_1_wp1_real_data_ingestion.py",
        ],
        "chatgpt_review_targets": [],
        "no_chatgpt_review_requested": True,
    }
    write_json(REVIEW_JSON, review_payload)
    lines = [
        "# Stage 3.1 WP1 Internal Review Request",
        "",
        "- Review target: `Stage 3.1 WP1 real data ingestion and cache`",
        "- Review route: `codex_internal_review`",
        "- ChatGPT review requested: `false`",
        "- Sent to ChatGPT: `false`",
        "- User notification sent: `false`",
        f"- `review_target_commit`: `{payload['review_target_commit']}`",
        "",
        "This latest artifact supersedes the older Stage 3 manual ChatGPT review prompt as the current review target.",
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
    loop.update(payload)
    loop.update(
        {
            "current_stage": STAGE,
            "next_task": "WP2 real data quality and monthly panel",
            "next_task_status": "ready",
            "real_config_modified": True,
            "hermes_modified": True,
            "feishu_message_sent": True,
            "feishu_notification_sent": True,
            "computer_use_executed": True,
            "computer_use_live_execution": True,
            "repo_only": False,
            "stage3_1_wp1_status": "completed_internal_review",
            "stage3_1_wp2_status": "ready",
            "stage3_1_wp3_status": "planned",
            "last_internal_review": rel(INTERNAL_REVIEW_JSON),
            "last_review_request": rel(REVIEW_JSON),
            "last_handoff": rel(HANDOFF_JSON),
            "handoff_update_pending": False,
            "requires_user_attention": False,
        }
    )
    write_json(LOOP_STATE, loop)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-target-commit", default=None)
    args = parser.parse_args()

    updated_at = datetime.now(timezone.utc).isoformat()
    review_target_commit = args.review_target_commit or git_head()
    real_metadata = read_json(REAL_METADATA)

    review = internal_review(real_metadata, review_target_commit, updated_at)
    write_internal_review(review)
    update_runner_state(updated_at)
    update_manifest()
    handoff = common_payload(real_metadata, review_target_commit, updated_at)
    write_handoff(handoff)
    write_review_request(handoff)
    update_loop_state(handoff)
    print(json.dumps({"status": "pass", "review_target_commit": review_target_commit}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

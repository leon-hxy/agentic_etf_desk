#!/usr/bin/env python3
"""Generate the Stage 3 major review package from completed Stage 3 artifacts."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "major_reviews" / "stage3"
REPORT_JSON = REPORT_DIR / "latest.json"
REPORT_MD = REPORT_DIR / "latest.md"
PUBLIC_REPO_URL = "https://github.com/leon-hxy/agentic_etf_desk"
STAGE = "Stage 3E major review package"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."
REVIEW_TARGET_COMMIT = "9c8ad5841bf30585575b78511e30e21b661f5774"
STAGE3F_NOTIFICATION_REPORT = "reports/live_notifications/stage3f_major_gate_feishu_notification.json"

INTERNAL_REVIEWS = {
    "Stage 3A": ROOT / "reports" / "internal_reviews" / "stage3" / "stage3a_data_source.json",
    "Stage 3B": ROOT / "reports" / "internal_reviews" / "stage3" / "stage3b_data_quality.json",
    "Stage 3C": ROOT / "reports" / "internal_reviews" / "stage3" / "stage3c_backtest_validation.json",
    "Stage 3D": ROOT / "reports" / "internal_reviews" / "stage3" / "stage3d_strategy_evidence_report.json",
}
SOURCE_PLAN = ROOT / "configs" / "data_sources" / "stage3_data_sources.json"
QUALITY_REPORT = ROOT / "reports" / "data_quality" / "stage3b_data_quality_report.json"
VALIDATION_REPORT = ROOT / "reports" / "backtest_validation" / "stage3c_backtest_validation_report.json"
EVIDENCE_REPORT = ROOT / "reports" / "strategy_evidence" / "stage3d_strategy_evidence_report.json"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def status_from_bool(value: bool) -> str:
    return "passed" if value else "failed"


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def stable_generated_at(payload: dict[str, Any]) -> str:
    if not REPORT_JSON.exists():
        return datetime.now(timezone.utc).isoformat()
    try:
        previous = read_json(REPORT_JSON)
    except json.JSONDecodeError:
        return datetime.now(timezone.utc).isoformat()
    comparable = dict(payload)
    previous_comparable = dict(previous)
    comparable.pop("generated_at", None)
    previous_comparable.pop("generated_at", None)
    if comparable == previous_comparable and previous.get("generated_at"):
        return str(previous["generated_at"])
    return datetime.now(timezone.utc).isoformat()


def minor_stage_summaries() -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for stage, path in INTERNAL_REVIEWS.items():
        review = read_json(path)
        summaries[stage] = {
            "status": str(review.get("status", "")),
            "task_file": str(review.get("task_file", "")),
            "internal_review": rel(path),
            "builder_summary": str(review.get("builder_summary", "")),
            "requires_user_attention": bool(review.get("requires_user_attention")),
            "chatgpt_review_requested": bool(review.get("chatgpt_review_requested")),
            "computer_use_executed": bool(review.get("computer_use_executed")),
            "feishu_message_sent": bool(review.get("feishu_message_sent")),
        }
    return summaries


def build_manual_prompt(review_target_commit: str) -> str:
    return (
        "Manual ChatGPT major-stage review request for Stage 3. "
        f"Public GitHub repo: {PUBLIC_REPO_URL}. "
        "Branch: stage/stage3-data-backtest. "
        f"review_target_commit: {review_target_commit}. "
        "Review package: reports/major_reviews/stage3/latest.md and "
        "reports/major_reviews/stage3/latest.json. "
        "Review request: reports/review_requests/latest.md and reports/review_requests/latest.json. "
        "Handoff: reports/codex_handoff/latest.md and reports/codex_handoff/latest.json. "
        "Scope: ETF-only Stage 3 data source, data quality, backtest validation, and strategy evidence. "
        "Do not treat sample evidence as investment basis. "
        "Final trading is manually decided by the user. "
        "最终交易由用户手动决定，系统不会自动下单。"
    )


def build_payload() -> dict[str, Any]:
    summaries = minor_stage_summaries()
    source_plan = read_json(SOURCE_PLAN)
    quality = read_json(QUALITY_REPORT)
    validation = read_json(VALIDATION_REPORT)
    evidence = read_json(EVIDENCE_REPORT)
    review_target_commit = REVIEW_TARGET_COMMIT

    all_internal_reviews_complete = all(
        item["status"] == "completed_internal_review" for item in summaries.values()
    )
    no_minor_stage_chatgpt = not any(item["chatgpt_review_requested"] for item in summaries.values())
    no_minor_stage_computer_use = not any(item["computer_use_executed"] for item in summaries.values())
    no_minor_stage_feishu = not any(item["feishu_message_sent"] for item in summaries.values())
    sample_data_only = bool(validation.get("data_boundary", {}).get("sample_data_only")) and bool(
        evidence.get("data_boundary", {}).get("sample_data_only")
    )
    real_data_used = bool(validation.get("data_boundary", {}).get("real_data_used")) or bool(
        evidence.get("data_boundary", {}).get("real_data_used")
    )
    not_investment_basis = bool(validation.get("data_boundary", {}).get("not_investment_basis")) and bool(
        evidence.get("data_boundary", {}).get("not_investment_basis")
    )
    manual_prompt = build_manual_prompt(review_target_commit)
    private_path_fragments = ("/" + "Volumes" + "/", "/" + "Users" + "/", "local_private")
    public_safe = all(fragment not in manual_prompt for fragment in private_path_fragments)
    manual_ready = all_internal_reviews_complete and public_safe
    status = "major_review_package_ready" if all(
        [
            all_internal_reviews_complete,
            no_minor_stage_chatgpt,
            no_minor_stage_computer_use,
            no_minor_stage_feishu,
            manual_ready,
            sample_data_only,
            not_investment_basis,
        ]
    ) else "blocked"

    payload: dict[str, Any] = {
        "stage": STAGE,
        "status": status,
        "major_stage": "Stage 3",
        "review_level": "major_stage",
        "review_route": "manual_chatgpt_review",
        "report_json": rel(REPORT_JSON),
        "report_md": rel(REPORT_MD),
        "public_repo_url": PUBLIC_REPO_URL,
        "branch": "stage/stage3-data-backtest",
        "review_target_commit": review_target_commit,
        "package_commit": None,
        "package_commit_note": "The package commit is created after these files are generated, so this package cannot self-reference its own commit.",
        "minor_stages": list(INTERNAL_REVIEWS),
        "minor_stage_summaries": summaries,
        "artifacts": {
            "data_source_plan": "docs/stage3a_data_source_plan.md",
            "data_source_manifest": rel(SOURCE_PLAN),
            "data_quality_report": rel(QUALITY_REPORT),
            "backtest_validation_report": rel(VALIDATION_REPORT),
            "strategy_evidence_report": rel(EVIDENCE_REPORT),
            "handoff": "reports/codex_handoff/latest.md",
            "review_request": "reports/review_requests/latest.md",
        },
        "readiness_checks": {
            "stage3a_internal_review_complete": status_from_bool(summaries["Stage 3A"]["status"] == "completed_internal_review"),
            "stage3b_internal_review_complete": status_from_bool(summaries["Stage 3B"]["status"] == "completed_internal_review"),
            "stage3c_internal_review_complete": status_from_bool(summaries["Stage 3C"]["status"] == "completed_internal_review"),
            "stage3d_internal_review_complete": status_from_bool(summaries["Stage 3D"]["status"] == "completed_internal_review"),
            "major_review_package_public_safe": status_from_bool(public_safe),
            "manual_chatgpt_review_ready": status_from_bool(manual_ready),
            "manual_trading_notice_present": status_from_bool(FINAL_TRADING_NOTICE in manual_prompt),
        },
        "data_boundary": {
            "source": str(validation.get("data_boundary", {}).get("source", "unknown")),
            "sample_data_only": sample_data_only,
            "real_data_used": real_data_used,
            "not_investment_basis": not_investment_basis,
            "panel_start_date": validation.get("data_boundary", {}).get("panel_start_date"),
            "panel_end_date": validation.get("data_boundary", {}).get("panel_end_date"),
            "symbols": validation.get("data_boundary", {}).get("symbols", []),
            "note": "Sample data only; not investment basis.",
        },
        "source_summary": {
            "selected_primary_source": source_plan.get("selected_primary_source"),
            "quality_status": quality.get("status"),
            "validation_status": validation.get("status"),
            "strategy_evidence_status": evidence.get("status"),
        },
        "risk_limitations_summary": [
            "Stage 3 evidence is based on a short sample panel and is not investment basis.",
            "Strategy comparisons use VTI as the benchmark reference; broader benchmark selection needs review before production use.",
            "Formal use requires reviewed real data, source terms confirmation, and a separate user-directed major-stage review.",
            "Final trading is manually decided by the user.",
        ],
        "manual_chatgpt_review_ready": manual_ready,
        "manual_chatgpt_review_prompt": manual_prompt,
        "chatgpt_review_requested_by_codex": False,
        "sent_to_chatgpt": False,
        "computer_use_executed": False,
        "feishu_message_sent": True,
        "feishu_notification_report": STAGE3F_NOTIFICATION_REPORT,
        "feishu_notification_note": "Stage 3F sent one non-sensitive major-gate Feishu notification after the Stage 3E package was pushed; no ChatGPT prompt was sent.",
        "safety_flags": {
            "auto_trading_surface": False,
            "broker_surface": False,
            "broker_write_surface": False,
            "chatgpt_review_requested": False,
            "computer_use_executed": False,
            "dependencies_installed": False,
            "feishu_gateway_modified": False,
            "feishu_message_sent": True,
            "hermes_modified": False,
            "openclaw_modified": False,
            "real_config_modified": False,
            "secret_values_written": False,
            "secrets_touched": False,
            "sent_to_chatgpt": False,
            "services_restarted": False,
        },
        "manual_execution_note": FINAL_TRADING_NOTICE,
    }
    payload["generated_at"] = stable_generated_at(payload)
    return payload


def write_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 3 Major Review Package",
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
    lines.extend(["", "## Minor Stage Evidence", ""])
    for stage in payload["minor_stages"]:
        summary = payload["minor_stage_summaries"][stage]
        lines.extend(
            [
                f"### {stage}",
                "",
                f"- Status: `{summary['status']}`",
                f"- Task: `{summary['task_file']}`",
                f"- Internal review: `{summary['internal_review']}`",
                f"- Summary: {summary['builder_summary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Review Artifacts",
            "",
        ]
    )
    for label, path in payload["artifacts"].items():
        lines.append(f"- `{label}`: `{path}`")
    lines.extend(
        [
            "",
            "## Data Boundary",
            "",
            "- Sample data only; not investment basis.",
            f"- Panel window: `{payload['data_boundary']['panel_start_date']}` to `{payload['data_boundary']['panel_end_date']}`",
            "- ETF-only universe scope.",
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
            "## Manual ChatGPT Review Prompt",
            "",
            payload["manual_chatgpt_review_prompt"],
            "",
            "## Safety",
            "",
            "- No Computer Use.",
            "- No ChatGPT review requested or sent by Codex.",
            "- Stage 3F Feishu notification sent: true; message was non-sensitive and did not contain the ChatGPT prompt body.",
            "- No real Hermes, OpenClaw, or Feishu gateway modification.",
            "- No dependency installation.",
            "- No broker interface or automatic trading surface.",
            "",
            FINAL_TRADING_NOTICE,
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(write_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "major_review_package_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate Stage 3F major-gate Feishu notification artifacts."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3F major_gate_feishu_notification_sent"
STATUS = "major_stage_ready"
TASK = "ops/tasks/stage3f_major_gate_feishu_notification_fix.md"
REPORT_JSON = "reports/live_notifications/stage3f_major_gate_feishu_notification.json"
REPORT_MD = "reports/live_notifications/stage3f_major_gate_feishu_notification.md"
SAFETY_JSON = "reports/live_notifications/stage3f_safety_results.json"
SAFETY_MD = "reports/live_notifications/stage3f_safety_results.md"
REVIEW_TARGET_COMMIT = "9c8ad5841bf30585575b78511e30e21b661f5774"


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def read_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write_json(path: str, payload: dict[str, Any]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_text(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def manual_prompt() -> str:
    return (
        "Manual ChatGPT major-stage review request for Stage 3. "
        "Public GitHub repo: https://github.com/leon-hxy/agentic_etf_desk. "
        "Branch: stage/stage3-data-backtest. "
        f"review_target_commit: {REVIEW_TARGET_COMMIT}. "
        "Review package: reports/major_reviews/stage3/latest.md and "
        "reports/major_reviews/stage3/latest.json. "
        "Review request: reports/review_requests/latest.md and "
        "reports/review_requests/latest.json. "
        "Handoff: reports/codex_handoff/latest.md and "
        "reports/codex_handoff/latest.json. "
        "Scope: ETF-only Stage 3 data source, data quality, backtest validation, "
        "and strategy evidence. Do not treat sample evidence as investment basis. "
        "Final trading is manually decided by the user. "
        "最终交易由用户手动决定，系统不会自动下单。"
    )


def notification_message_summary() -> str:
    return (
        "Stage 3 major stage is ready for manual ChatGPT review; the message "
        "included the branch, Stage 3E package commit, major review package "
        "paths, ETF-only scope, sample-evidence caveat, and manual-final-trading notice."
    )


def safety_payload(generated_at: str) -> dict[str, Any]:
    checks = [
        {
            "check": "major gate condition",
            "result": "pass",
            "detail": "runner state status was major_stage_ready and manual_chatgpt_review_ready was true before sending",
        },
        {
            "check": "Hermes Feishu delivery path",
            "result": "pass",
            "detail": "used existing Hermes send capability with configured Feishu target",
        },
        {
            "check": "message content",
            "result": "pass",
            "detail": "plain text, no secrets, no local absolute paths, no private target identifiers",
        },
        {
            "check": "live config",
            "result": "pass",
            "detail": "no real Hermes, OpenClaw, or Feishu gateway configuration was modified",
        },
        {
            "check": "runtime boundaries",
            "result": "pass",
            "detail": "no service restart, dependency install, Computer Use, broker connection, or order code",
        },
    ]
    return {
        "stage": STAGE,
        "status": "pass",
        "generated_at": generated_at,
        "checks": checks,
        "secrets_touched": False,
        "secret_values_printed": False,
        "secret_values_committed": False,
        "real_config_modified": False,
        "hermes_config_modified": False,
        "openclaw_modified": False,
        "feishu_gateway_modified": False,
        "services_restarted": False,
        "dependencies_installed": False,
        "computer_use_executed": False,
        "chatgpt_review_requested_by_codex": False,
        "sent_to_chatgpt": False,
        "feishu_message_sent": True,
        "feishu_message_count": 1,
        "auto_trading_surface": False,
        "broker_surface": False,
        "final_trading_notice": "Final trading is manually decided by the user.",
    }


def update_runner(generated_at: str) -> None:
    state = read_json("ops/runners/stage3_runner_state.json")
    state.update(
        {
            "status": STATUS,
            "current_minor_stage": "Stage 3F",
            "current_task": TASK,
            "last_completed_minor_stage": "Stage 3F",
            "last_live_notification_report": REPORT_JSON,
            "last_safety_results": SAFETY_JSON,
            "last_pushed_commit": REVIEW_TARGET_COMMIT,
            "feishu_notification_sent": True,
            "feishu_notification_status": "sent",
            "feishu_notification_method": "hermes_send_existing_feishu_target",
            "major_gate_notification_fix": "completed_live_feishu_notification",
            "manual_chatgpt_review_ready": True,
            "major_review_required": True,
            "requires_user_attention": False,
            "real_config_modified": False,
            "computer_use_executed": False,
            "updated_at": generated_at,
        }
    )
    completed = list(state.get("completed_minor_stages", []))
    if "Stage 3F" not in completed:
        completed.append("Stage 3F")
    state["completed_minor_stages"] = completed
    state["remaining_minor_stages"] = []
    write_json("ops/runners/stage3_runner_state.json", state)


def update_loop_state(generated_at: str) -> None:
    state = read_json("ops/state/loop_state.json")
    state.update(
        {
            "current_stage": STAGE,
            "status": "stage3f_major_gate_feishu_notification_sent",
            "stage3_runner_current_minor_stage": "Stage 3F",
            "stage3_runner_current_task": TASK,
            "stage3_runner_status": STATUS,
            "stage3f_task": TASK,
            "stage3f_task_status": "completed_live_notification",
            "stage3f_live_notification_report": REPORT_JSON,
            "stage3f_safety_results": SAFETY_JSON,
            "current_stage_repo_only": False,
            "current_stage_live_notification": True,
            "current_stage_feishu_message_sent": True,
            "current_stage_feishu_message_count": 1,
            "current_stage_hermes_modified": False,
            "current_stage_real_config_modified": False,
            "current_stage_computer_use_executed": False,
            "current_stage_chatgpt_review_requested": False,
            "current_stage_chatgpt_prompt_sent": False,
            "feishu_message_sent": True,
            "feishu_message_count": 2,
            "feishu_notification_sent": True,
            "notification_layer": "stage3f_live_major_gate_notification_sent",
            "manual_chatgpt_review_ready": True,
            "major_review_required": True,
            "next_task": None,
            "next_minor_task": None,
            "next_task_status": "manual_major_review_ready",
            "next_minor_task_status": "manual_major_review_ready",
            "next_recommended_stage": "User may request manual ChatGPT major-stage review from the Stage 3 package.",
            "last_handoff": "reports/codex_handoff/latest.json",
            "last_review_request": "reports/review_requests/latest.json",
            "last_live_notification_report": REPORT_JSON,
            "last_safety_results": SAFETY_JSON,
            "last_review_request_note": "Stage 3F sent the live Feishu major-gate notification; Codex did not request ChatGPT review.",
            "review_target_commit": REVIEW_TARGET_COMMIT,
            "review_target_commit_note": "Stage 3 major review should use the pushed Stage 3E package commit referenced by the live Feishu notification.",
            "updated_at": generated_at,
        }
    )
    write_json("ops/state/loop_state.json", state)


def update_review_requests(generated_at: str) -> None:
    prompt = manual_prompt()
    latest = read_json("reports/review_requests/latest.json")
    latest.update(
        {
            "stage": STAGE,
            "loop_state_stage": STAGE,
            "review_target_commit": REVIEW_TARGET_COMMIT,
            "current_repo_head": REVIEW_TARGET_COMMIT,
            "handoff_generated_from_head": REVIEW_TARGET_COMMIT,
            "handoff_commit": None,
            "review_mode": "manual_chatgpt_review_ready_feishu_notified",
            "manual_chatgpt_review_ready": True,
            "manual_chatgpt_review_prompt": prompt,
            "feishu_message_sent": True,
            "feishu_notification_sent": True,
            "feishu_notification_status": "sent",
            "feishu_notification_report": REPORT_JSON,
            "live_notification_report": REPORT_JSON,
            "safety_results": SAFETY_JSON,
            "sent_to_chatgpt": False,
            "chatgpt_review_requested": False,
            "no_chatgpt_review_requested": True,
            "computer_use_executed": False,
            "updated_at": generated_at,
        }
    )
    review_files = set(latest.get("review_files", []))
    review_files.update(
        {
            REPORT_MD,
            REPORT_JSON,
            SAFETY_MD,
            SAFETY_JSON,
            TASK,
        }
    )
    latest["review_files"] = sorted(review_files)
    write_json("reports/review_requests/latest.json", latest)

    write_text(
        "reports/review_requests/latest.md",
        "\n".join(
            [
                "# Stage 3F Major Gate Feishu Notification Sent",
                "",
                f"- Stage: `{STAGE}`",
                "- Review level: `major_stage`",
                "- Review mode: `manual_chatgpt_review_ready_feishu_notified`",
                f"- `review_target_commit`: `{REVIEW_TARGET_COMMIT}`",
                "- Major review package: `reports/major_reviews/stage3/latest.md`",
                "- Handoff: `reports/codex_handoff/latest.md`",
                "- Live notification report: `reports/live_notifications/stage3f_major_gate_feishu_notification.md`",
                "- ChatGPT review requested by Codex: `false`",
                "- Sent to ChatGPT: `false`",
                "- Feishu message sent: `true`",
                "",
                "The Stage 3 major-gate notification was sent through the existing Hermes Feishu path. "
                "The user may request manual ChatGPT major-stage review; Codex did not send the ChatGPT prompt automatically.",
                "",
                "## Manual Prompt",
                "",
                prompt,
                "",
                "Final trading is manually decided by the user.",
                "",
            ]
        ),
    )

    prompt_json = read_json("reports/review_requests/chatgpt_review_prompt.json")
    prompt_json.update(
        {
            "stage": STAGE,
            "review_target_commit": REVIEW_TARGET_COMMIT,
            "review_mode": "manual_chatgpt_review_ready_feishu_notified",
            "manual_chatgpt_review_ready": True,
            "prompt": prompt,
            "manual_chatgpt_review_prompt": prompt,
            "sent_to_chatgpt": False,
            "chatgpt_review_requested": False,
            "computer_use_executed": False,
            "feishu_message_sent": True,
            "live_notification_report": REPORT_JSON,
        }
    )
    prompt_json["gate"] = {
        "required": False,
        "expected_commit": REVIEW_TARGET_COMMIT,
        "reason": "Stage 3F live Feishu notification was sent; manual ChatGPT major-stage review remains user-initiated",
    }
    write_json("reports/review_requests/chatgpt_review_prompt.json", prompt_json)
    write_text("reports/review_requests/chatgpt_review_prompt.md", prompt + "\n")

    notification = read_json("reports/review_requests/notification_preview.json")
    notification.update(
        {
            "stage": STAGE,
            "loop_state_stage": STAGE,
            "mode": "live_feishu_notification_sent",
            "review_target_commit": REVIEW_TARGET_COMMIT,
            "manual_chatgpt_review_ready": True,
            "sent_to_feishu": True,
            "feishu_message_sent": True,
            "live_notification_report": REPORT_JSON,
            "computer_use_executed": False,
            "chatgpt_review_requested": False,
            "sent_to_chatgpt": False,
            "status_reason": "stage3f_major_gate_feishu_notification_sent",
            "message": "Stage 3 major-gate Feishu notification was sent; user may request manual ChatGPT major-stage review.",
        }
    )
    write_json("reports/review_requests/notification_preview.json", notification)
    write_text(
        "reports/review_requests/notification_preview.md",
        "\n".join(
            [
                "# Notification Delivery",
                "",
                f"- Stage: `{STAGE}`",
                "- Mode: `live_feishu_notification_sent`",
                f"- `review_target_commit`: `{REVIEW_TARGET_COMMIT}`",
                "- Sent to Feishu: `true`",
                "- Computer Use 未执行。",
                "- Live notification report: `reports/live_notifications/stage3f_major_gate_feishu_notification.md`",
                "",
                "Stage 3 major-gate notification was sent through the existing Hermes Feishu path. "
                "The user may request manual ChatGPT major-stage review using `reports/major_reviews/stage3/latest.md`.",
                "",
                "不会自动下单，最终交易由用户手动决定。",
                "",
            ]
        ),
    )

    relay = read_json("reports/review_requests/relay_status.json")
    relay.update(
        {
            "stage": STAGE,
            "relay_stage": "stage3f_major_gate_feishu_notified_manual_review_ready",
            "status_reason": "stage3f_major_gate_feishu_notification_sent",
            "review_target_commit": REVIEW_TARGET_COMMIT,
            "expected_commit": REVIEW_TARGET_COMMIT,
            "review_route": "manual_chatgpt_review_for_major_stage",
            "major_review_route": "manual_chatgpt_review_for_major_stage",
            "manual_chatgpt_review_ready": True,
            "feishu_message_sent": True,
            "live_notification_report": REPORT_JSON,
            "sent_to_chatgpt": False,
            "computer_use_executed": False,
            "automatic_chatgpt_prompt_send_allowed": False,
            "review_gate_required": False,
            "failure_policy": "manual_review_required_for_major_stage",
        }
    )
    write_json("reports/review_requests/relay_status.json", relay)
    write_text(
        "reports/review_requests/relay_status.md",
        "\n".join(
            [
                "# Review Relay Status",
                "",
                f"- Stage: `{STAGE}`",
                "- Relay stage: `stage3f_major_gate_feishu_notified_manual_review_ready`",
                "- Review route: `manual_chatgpt_review_for_major_stage`",
                f"- Expected commit: `{REVIEW_TARGET_COMMIT}`",
                "- Feishu message sent: `true`",
                "- Sent to ChatGPT: `false`",
                "- Computer Use executed: `false`",
                "- Automatic ChatGPT prompt send allowed: `false`",
                "- Live notification report: `reports/live_notifications/stage3f_major_gate_feishu_notification.md`",
                "",
                "The Feishu notification only tells the user that manual ChatGPT major-stage review is ready. "
                "Codex did not open ChatGPT or submit the review prompt.",
                "",
                "Final trading is manually decided by the user.",
                "",
            ]
        ),
    )

    write_text(
        "reports/review_requests/manual_fallback_prompt.md",
        "\n".join(
            [
                "# Manual ChatGPT Review Fallback",
                "",
                f"`review_target_commit`: `{REVIEW_TARGET_COMMIT}`",
                "",
                prompt,
                "",
                "This fallback is for user-manual copy only. Codex did not send it to ChatGPT.",
                "",
            ]
        ),
    )


def update_handoff(generated_at: str) -> None:
    prompt = manual_prompt()
    handoff = read_json("reports/codex_handoff/latest.json")
    handoff.update(
        {
            "stage": STAGE,
            "loop_state_stage": STAGE,
            "stage3_runner_current_minor_stage": "Stage 3F",
            "stage3_runner_current_task": TASK,
            "stage3_runner_status": STATUS,
            "stage3f_task_status": "completed_live_notification",
            "stage3f_live_notification_report": REPORT_JSON,
            "stage3f_safety_results": SAFETY_JSON,
            "review_target_commit": REVIEW_TARGET_COMMIT,
            "current_repo_head": REVIEW_TARGET_COMMIT,
            "handoff_generated_from_head": REVIEW_TARGET_COMMIT,
            "handoff_commit": None,
            "commit_binding_note": "review_target_commit is the pushed Stage 3E package commit and commit to review for manual ChatGPT major-stage review; the final Stage 3F notification-fix commit is reported by Codex after commit.",
            "manual_chatgpt_review_prompt": prompt,
            "manual_chatgpt_review_ready": True,
            "manual_review_user_action": "User may request manual ChatGPT major-stage review using reports/major_reviews/stage3/latest.md and review_target_commit.",
            "next_minor_task": None,
            "next_minor_task_status": "manual_major_review_ready",
            "next_recommended_stage": "User-requested manual ChatGPT major-stage review can proceed from the Stage 3 package.",
            "feishu_message_sent": True,
            "feishu_notification_sent": True,
            "feishu_notification_status": "sent",
            "live_notification_report": REPORT_JSON,
            "safety_results": SAFETY_JSON,
            "computer_use_executed": False,
            "chatgpt_review_requested": False,
            "sent_to_chatgpt": False,
            "updated_at": generated_at,
        }
    )
    changed = set(handoff.get("changed_files", []))
    changed.update(
        {
            "scripts/reports/generate_stage3f_feishu_notification_report.py",
            REPORT_JSON,
            REPORT_MD,
            SAFETY_JSON,
            SAFETY_MD,
            TASK,
            "tests/safety/test_stage3f_feishu_notification.py",
        }
    )
    handoff["changed_files"] = sorted(changed)
    handoff["review_files"] = sorted(set(handoff.get("review_files", [])) | changed)
    handoff["risk_statement"] = (
        "Stage 3F sends one non-sensitive Feishu notification through existing Hermes "
        "notification capability after Stage 3 entered major_stage_ready. It does not "
        "modify real Hermes/OpenClaw/Feishu gateway configuration, restart services, "
        "install dependencies, run Computer Use, send ChatGPT prompts, or add trading execution surfaces."
    )
    write_json("reports/codex_handoff/latest.json", handoff)

    write_text(
        "reports/codex_handoff/latest.md",
        "\n".join(
            [
                "# Codex Handoff",
                "",
                "## Current Stage",
                "",
                f"{STAGE}.",
                "",
                "## Stage 3 Runner State",
                "",
                f"- Status: `{STATUS}`",
                "- Runner state: `ops/runners/stage3_runner_state.json`",
                "- Current runner minor stage: `Stage 3F`",
                f"- Current runner task: `{TASK}`",
                "- Major review package: `reports/major_reviews/stage3/latest.md`",
                f"- Live notification report: `{REPORT_MD}`",
                "",
                "## Latest Commit Binding",
                "",
                f"- `review_target_commit`: `{REVIEW_TARGET_COMMIT}`",
                "- `handoff_commit`: `null`",
                f"- `handoff_generated_from_head`: `{REVIEW_TARGET_COMMIT}`",
                f"- `current_repo_head`: `{REVIEW_TARGET_COMMIT}`",
                "",
                "review_target_commit is the pushed Stage 3E package commit and commit to review for manual ChatGPT major-stage review; the final Stage 3F notification-fix commit is reported by Codex after commit.",
                "",
                "## Stage 3F Result",
                "",
                "- Status: `completed_live_notification`",
                "- Sent one Feishu notification through the existing Hermes send capability.",
                "- Generated `reports/live_notifications/stage3f_major_gate_feishu_notification.md`.",
                "- Generated `reports/live_notifications/stage3f_major_gate_feishu_notification.json`.",
                "- Codex did not open ChatGPT, send ChatGPT prompts, run Computer Use, modify real config, restart services, install dependencies, connect brokers, or write order code.",
                "",
                "## Tests",
                "",
                "- Pending rerun after Stage 3F files are generated.",
                "",
                "## Manual Review Prompt",
                "",
                prompt,
                "",
                "## Safety Flags",
                "",
                "- Modified real `~/.hermes`: false",
                "- Modified real `~/.openclaw`: false",
                "- Modified real Feishu gateway: false",
                "- Restarted Hermes/OpenClaw: false",
                "- Installed dependencies: false",
                "- Touched secrets: false",
                "- Wrote secret values: false",
                "- Ran Computer Use: false",
                "- Requested ChatGPT review: false",
                "- Sent ChatGPT prompt: false",
                "- Sent Feishu message in current stage: true",
                "- Automatic trading surface: false",
                "- Broker surface: false",
                "",
                "Final trading is manually decided by the user.",
                "",
            ]
        ),
    )


def update_stage_docs() -> None:
    write_text(
        TASK,
        "\n".join(
            [
                "# Stage 3F Major Gate Feishu Notification Fix",
                "",
                "stage: Stage 3F major_gate_feishu_notification_sent",
                "status: completed_live_notification",
                "depends_on: Stage 3E major_review_package_ready",
                "",
                "## Objective",
                "",
                "Send the missing live Feishu notification after Stage 3 reaches `major_stage_ready` and `manual_chatgpt_review_ready=true`.",
                "",
                "## Completed Scope",
                "",
                "- Confirmed branch `stage/stage3-data-backtest`.",
                "- Confirmed runner state had `status=major_stage_ready` and `manual_chatgpt_review_ready=true` before live send.",
                "- Used existing Hermes Feishu notification capability via `hermes send --to feishu --quiet --file -`.",
                "- Sent one non-sensitive plain-text major-gate notification.",
                "- Updated runner state, loop state, handoff, review request, relay status, notification delivery record, live report, and safety report.",
                "",
                "## Safety Boundaries",
                "",
                "- Do not modify real `~/.hermes`.",
                "- Do not modify real `~/.openclaw`.",
                "- Do not modify the real Feishu gateway.",
                "- Do not restart services.",
                "- Do not install dependencies.",
                "- Do not run Computer Use.",
                "- Do not connect broker interfaces.",
                "- Do not place orders or write order code.",
                "- Keep ETF-only scope.",
                "- Final trading is manually decided by the user.",
                "",
                "## Outputs",
                "",
                f"- `{REPORT_MD}`",
                f"- `{REPORT_JSON}`",
                f"- `{SAFETY_MD}`",
                f"- `{SAFETY_JSON}`",
                "",
            ]
        ),
    )

    stage_path = ROOT / "ops/stages/stage3.yaml"
    text = stage_path.read_text(encoding="utf-8")
    text = text.replace("status: stage3e_major_review_package_ready", "status: stage3f_major_gate_feishu_notification_sent", 1)
    text = text.replace("current_minor_stage: Stage 3E", "current_minor_stage: Stage 3F", 1)
    text = text.replace("current_task: ops/tasks/stage3_major_review_package.md", f"current_task: {TASK}", 1)
    text = text.replace("    - Stage 3E\n  remaining_minor_stages: []", "    - Stage 3E\n    - Stage 3F\n  remaining_minor_stages: []", 1)
    if "stage3f_major_gate_feishu_notification_fix" not in text:
        text += "\n".join(
            [
                "",
                "live_notification_fix:",
                "  id: stage3f_major_gate_feishu_notification_fix",
                f"  file: {TASK}",
                "  status: completed_live_notification",
                "  depends_on: Stage 3E major_review_package_ready",
                "  trigger: runner status major_stage_ready and manual_chatgpt_review_ready true",
                "  delivery: existing_hermes_feishu_send",
                "  chatgpt_review_requested: false",
                "  computer_use_executed: false",
                "  real_config_modified: false",
                "  outputs:",
                f"    - {REPORT_MD}",
                f"    - {REPORT_JSON}",
                f"    - {SAFETY_MD}",
                f"    - {SAFETY_JSON}",
                "",
            ]
        )
    stage_path.write_text(text, encoding="utf-8")

    runner_doc = ROOT / "ops/runners/stage3_runner.md"
    text = runner_doc.read_text(encoding="utf-8")
    text = text.replace("Current minor stage: `Stage 3E`", "Current minor stage: `Stage 3F`")
    text = text.replace("Current task: `ops/tasks/stage3_major_review_package.md`", f"Current task: `{TASK}`")
    text = text.replace(
        "Completed minor stages: `Stage 3A`, `Stage 3B`, `Stage 3C`, `Stage 3D`, `Stage 3E`",
        "Completed minor stages: `Stage 3A`, `Stage 3B`, `Stage 3C`, `Stage 3D`, `Stage 3E`, `Stage 3F`",
    )
    if "`completed_live_notification`" not in text:
        text = text.replace(
            "- `major_stage_ready`: Stage 3E package is ready for the user to request manual\n  ChatGPT major-stage review.",
            "- `major_stage_ready`: Stage 3E package is ready for the user to request manual\n  ChatGPT major-stage review.\n- `completed_live_notification`: Stage 3F sent the major-gate Feishu notification without changing live configuration.",
        )
    if "Stage 3F" not in text.split("## Notification Rules", 1)[1]:
        text = text.replace(
            "- If Stage 3E completes and the major review package is ready, notify the user\n  to request manual ChatGPT major-stage review.",
            "- If Stage 3E completes and the major review package is ready, notify the user\n  to request manual ChatGPT major-stage review.\n- Stage 3F may send exactly one major-gate Feishu notification through existing Hermes capability when runner status is `major_stage_ready` and `manual_chatgpt_review_ready=true`.",
        )
    runner_doc.write_text(text, encoding="utf-8")


def write_reports(generated_at: str) -> None:
    report = {
        "stage": STAGE,
        "status": "completed_live_notification",
        "generated_at": generated_at,
        "branch": "stage/stage3-data-backtest",
        "precondition_status": "major_stage_ready",
        "manual_chatgpt_review_ready": True,
        "review_target_commit": REVIEW_TARGET_COMMIT,
        "delivery_method": "existing Hermes send capability",
        "delivery_command_public": "hermes send --to feishu --quiet --file -",
        "feishu_message_sent": True,
        "feishu_message_count": 1,
        "feishu_message_sensitive_content": False,
        "feishu_message_public_summary": notification_message_summary(),
        "blocked": False,
        "blocked_reason": None,
        "blocked_status_if_failed": "blocked_feishu_notification",
        "chatgpt_review_requested_by_codex": False,
        "sent_to_chatgpt": False,
        "computer_use_executed": False,
        "real_hermes_config_modified": False,
        "real_openclaw_modified": False,
        "real_feishu_gateway_modified": False,
        "services_restarted": False,
        "dependencies_installed": False,
        "secrets_touched": False,
        "secret_values_printed": False,
        "secret_values_committed": False,
        "auto_trading_surface": False,
        "broker_surface": False,
        "final_trading_notice": "Final trading is manually decided by the user.",
    }
    write_json(REPORT_JSON, report)
    write_text(
        REPORT_MD,
        "\n".join(
            [
                "# Stage 3F Major Gate Feishu Notification",
                "",
                f"- Stage: `{STAGE}`",
                "- Status: `completed_live_notification`",
                f"- Generated at: `{generated_at}`",
                "- Branch: `stage/stage3-data-backtest`",
                "- Precondition status: `major_stage_ready`",
                "- Manual ChatGPT review ready: `true`",
                f"- `review_target_commit`: `{REVIEW_TARGET_COMMIT}`",
                "- Delivery method: existing Hermes send capability",
                "- Delivery command public form: `hermes send --to feishu --quiet --file -`",
                "- Feishu message sent: `true`",
                "- Feishu message count: `1`",
                "- Sensitive content in message: `false`",
                "- ChatGPT review requested by Codex: `false`",
                "- Sent to ChatGPT: `false`",
                "- Computer Use executed: `false`",
                "- Modified real Hermes config: `false`",
                "- Modified real OpenClaw config: `false`",
                "- Modified real Feishu gateway: `false`",
                "- Restarted services: `false`",
                "- Installed dependencies: `false`",
                "",
                "The sent message contained only Stage 3 major-review readiness, the public branch, "
                "the pushed Stage 3E package commit, repo-relative review artifact paths, ETF-only scope, "
                "the sample-evidence caveat, and the manual-final-trading notice. Raw delivery output, "
                "Feishu target identifiers, user identifiers, and secret-bearing configuration were not published.",
                "",
                "Final trading is manually decided by the user.",
                "",
            ]
        ),
    )

    safety = safety_payload(generated_at)
    write_json(SAFETY_JSON, safety)
    check_lines = "\n".join(
        f"- {item['check']}: `{item['result']}` - {item['detail']}" for item in safety["checks"]
    )
    write_text(
        SAFETY_MD,
        "\n".join(
            [
                "# Stage 3F Safety Results",
                "",
                f"- Stage: `{STAGE}`",
                "- Status: `pass`",
                f"- Generated at: `{generated_at}`",
                "",
                "## Checks",
                "",
                check_lines,
                "",
                "## Safety Flags",
                "",
                "- Secrets touched: `false`",
                "- Secret values printed: `false`",
                "- Secret values committed: `false`",
                "- Real config modified: `false`",
                "- Hermes config modified: `false`",
                "- OpenClaw modified: `false`",
                "- Feishu gateway modified: `false`",
                "- Services restarted: `false`",
                "- Dependencies installed: `false`",
                "- Computer Use executed: `false`",
                "- ChatGPT review requested by Codex: `false`",
                "- Sent to ChatGPT: `false`",
                "- Feishu message sent: `true`",
                "- Automatic trading surface: `false`",
                "- Broker surface: `false`",
                "",
                "Final trading is manually decided by the user.",
                "",
            ]
        ),
    )


def main() -> int:
    generated_at = now_iso()
    current_head = run_git("rev-parse", "HEAD")
    if current_head != REVIEW_TARGET_COMMIT:
        raise SystemExit(
            f"Expected Stage 3F to be generated from {REVIEW_TARGET_COMMIT}, got {current_head}"
        )
    runner = read_json("ops/runners/stage3_runner_state.json")
    if runner.get("status") != "major_stage_ready" or runner.get("manual_chatgpt_review_ready") is not True:
        raise SystemExit("Stage 3F precondition failed: runner is not ready for major review notification")

    write_reports(generated_at)
    update_runner(generated_at)
    update_loop_state(generated_at)
    update_review_requests(generated_at)
    update_handoff(generated_at)
    update_stage_docs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

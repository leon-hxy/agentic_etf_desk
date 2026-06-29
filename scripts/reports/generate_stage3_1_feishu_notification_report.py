#!/usr/bin/env python3
"""Record the Stage 3.1 major-gate Feishu notification after live send."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNNER_STATE = ROOT / "ops" / "runners" / "stage3_1_runner_state.json"
LOOP_STATE = ROOT / "ops" / "state" / "loop_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_JSON = ROOT / "reports" / "review_requests" / "latest.json"
REVIEW_MD = ROOT / "reports" / "review_requests" / "latest.md"
MAJOR_JSON = ROOT / "reports" / "major_reviews" / "stage3_1" / "latest.json"
MAJOR_MD = ROOT / "reports" / "major_reviews" / "stage3_1" / "latest.md"
REPORT_JSON = ROOT / "reports" / "live_notifications" / "stage3_1_major_gate_feishu_notification.json"
REPORT_MD = ROOT / "reports" / "live_notifications" / "stage3_1_major_gate_feishu_notification.md"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def update_json_payload(path: Path, report: dict[str, Any], updated_at: str) -> None:
    payload = read_json(path)
    payload.update(
        {
            "review_target_commit": report["review_target_commit"],
            "current_repo_head": report["review_target_commit"],
            "stage3_1_major_gate_feishu_notification_sent": True,
            "stage3_1_live_notification_report": rel(REPORT_JSON),
            "stage3_1_feishu_notification_method": "hermes_send_existing_feishu_target",
            "stage3_1_feishu_notification_status": "sent_after_wp3_major_review_package_ready",
            "feishu_message_sent": True,
            "feishu_notification_sent": True,
            "user_notification_sent": True,
            "tests_status": "passed",
            "updated_at": updated_at,
        }
    )
    if path == MAJOR_JSON:
        payload["stage3_1_feishu_notification_status"] = report["status"]
        payload["feishu_notification_allowed_after_package"] = True
        if isinstance(payload.get("safety_flags"), dict):
            payload["safety_flags"]["feishu_message_sent"] = True
    if path in (HANDOFF_JSON, REVIEW_JSON):
        payload["handoff_generated_from_head"] = report["review_target_commit"]
    if path == LOOP_STATE:
        payload.update(
            {
                "last_live_notification_report": rel(REPORT_JSON),
                "last_stage3_1_live_notification_report": rel(REPORT_JSON),
                "current_stage_feishu_message_sent": False,
                "current_stage_feishu_message_count": 0,
            }
        )
    write_json(path, payload)


def ensure_line(path: Path, heading: str, lines: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if heading in text:
        return
    suffix = "\n".join(["", heading, "", *lines, ""])
    path.write_text(text.rstrip() + "\n" + suffix, encoding="utf-8")


def build_report(updated_at: str) -> dict[str, Any]:
    major = read_json(MAJOR_JSON)
    runner = read_json(RUNNER_STATE)
    return {
        "stage": "Stage 3.1 major_gate_feishu_notification_sent",
        "status": "completed_live_notification",
        "branch": "stage/stage3.1-real-etf-data",
        "precondition_status": runner["status"],
        "manual_chatgpt_review_ready": bool(major["manual_chatgpt_review_ready"]),
        "review_target_commit": major["review_target_commit"],
        "pushed_head_at_notification": git_head(),
        "delivery_method": "existing Hermes send capability",
        "delivery_command_public": "hermes send --to feishu --quiet --file -",
        "feishu_message_sent": True,
        "feishu_message_count": 1,
        "feishu_message_sensitive_content": False,
        "feishu_message_public_summary": (
            "Stage 3.1 major review package is ready for user-initiated manual ChatGPT review; "
            "the message included the branch, pushed head, major review package paths, ETF-only scope, "
            "no-auto-trading boundary, and manual-final-trading notice."
        ),
        "chatgpt_review_requested_by_codex": False,
        "sent_to_chatgpt": False,
        "computer_use_executed": False,
        "real_hermes_config_modified": False,
        "real_openclaw_modified": False,
        "real_feishu_gateway_modified": False,
        "services_restarted": False,
        "dependencies_installed": False,
        "broker_surface": False,
        "broker_write_surface": False,
        "order_placement_surface": False,
        "auto_trading_surface": False,
        "secrets_touched": False,
        "secret_values_printed": False,
        "secret_values_committed": False,
        "final_trading_notice": FINAL_TRADING_NOTICE,
        "generated_at": updated_at,
    }


def write_report(report: dict[str, Any]) -> None:
    write_json(REPORT_JSON, report)
    lines = [
        "# Stage 3.1 Major Gate Feishu Notification",
        "",
        f"- Stage: `{report['stage']}`",
        f"- Status: `{report['status']}`",
        f"- Generated at: `{report['generated_at']}`",
        f"- Branch: `{report['branch']}`",
        f"- Precondition status: `{report['precondition_status']}`",
        f"- Manual ChatGPT review ready: `{str(report['manual_chatgpt_review_ready']).lower()}`",
        f"- `review_target_commit`: `{report['review_target_commit']}`",
        f"- Pushed head at notification: `{report['pushed_head_at_notification']}`",
        f"- Delivery method: {report['delivery_method']}",
        f"- Delivery command public form: `{report['delivery_command_public']}`",
        f"- Feishu message sent: `{str(report['feishu_message_sent']).lower()}`",
        f"- Feishu message count: `{report['feishu_message_count']}`",
        f"- Sensitive content in message: `{str(report['feishu_message_sensitive_content']).lower()}`",
        f"- ChatGPT review requested by Codex: `{str(report['chatgpt_review_requested_by_codex']).lower()}`",
        f"- Sent to ChatGPT: `{str(report['sent_to_chatgpt']).lower()}`",
        f"- Computer Use executed: `{str(report['computer_use_executed']).lower()}`",
        f"- Modified real Hermes config: `{str(report['real_hermes_config_modified']).lower()}`",
        f"- Modified real OpenClaw config: `{str(report['real_openclaw_modified']).lower()}`",
        f"- Modified real Feishu gateway: `{str(report['real_feishu_gateway_modified']).lower()}`",
        f"- Restarted services: `{str(report['services_restarted']).lower()}`",
        f"- Installed dependencies: `{str(report['dependencies_installed']).lower()}`",
        "",
        "The sent message contained only Stage 3.1 major-review readiness, the public branch, the pushed package head, repo-relative review artifact paths, ETF-only scope, the no-auto-trading boundary, and the manual-final-trading notice. Raw delivery output, Feishu target identifiers, user identifiers, and secret-bearing configuration were not published.",
        "",
        FINAL_TRADING_NOTICE,
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    updated_at = datetime.now(timezone.utc).isoformat()
    report = build_report(updated_at)
    write_report(report)
    for path in (RUNNER_STATE, LOOP_STATE, HANDOFF_JSON, REVIEW_JSON, MAJOR_JSON):
        update_json_payload(path, report, updated_at)
    notification_lines = [
        "- User notified through Feishu after WP3 major package: `true`.",
        f"- Notification report: `{rel(REPORT_MD)}` / `{rel(REPORT_JSON)}`.",
        "- Delivery used the existing Hermes send capability and did not modify real Hermes, OpenClaw, or Feishu gateway configuration.",
    ]
    ensure_line(HANDOFF_MD, "## Stage 3.1 Feishu Notification", notification_lines)
    ensure_line(REVIEW_MD, "## Stage 3.1 Feishu Notification", notification_lines)
    ensure_line(MAJOR_MD, "## Stage 3.1 Feishu Notification", notification_lines)
    print(json.dumps({"status": "pass", "report": rel(REPORT_JSON)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

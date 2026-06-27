#!/usr/bin/env python3
"""Shared helpers for repo-only ChatGPT review relay previews."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPO = "leon-hxy/agentic_etf_desk"
PUBLIC_REPO_URL = "https://github.com/leon-hxy/agentic_etf_desk"
LATEST_REVIEW = ROOT / "reports" / "review_requests" / "latest.json"
GATE_PATH = ROOT / "local_private" / "review_gate.json"
PROMPT_MD = ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.md"
PROMPT_JSON = ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.json"
FALLBACK_MD = ROOT / "reports" / "review_requests" / "manual_fallback_prompt.md"
STATUS_MD = ROOT / "reports" / "review_requests" / "relay_status.md"
STATUS_JSON = ROOT / "reports" / "review_requests" / "relay_status.json"

PUBLIC_REVIEW_FILES = [
    "reports/review_requests/latest.md",
    "reports/review_requests/latest.json",
    "reports/codex_handoff/latest.md",
    "reports/codex_handoff/latest.json",
    "AGENTS.md",
    "docs/security_policy.md",
]
COMMIT_BINDING_NOTE = (
    "review_target_commit is the commit to review; handoff may be committed later "
    "and therefore cannot self-reference its own final SHA in the same commit."
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def latest_review() -> dict[str, Any]:
    return load_json(LATEST_REVIEW)


def review_target_commit(review: dict[str, Any]) -> str:
    return str(review.get("review_target_commit") or review.get("commit") or "")


def current_repo_head() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def default_status() -> dict[str, Any]:
    return {
        "relay_stage": "draft_only",
        "computer_use_executed": False,
        "chatgpt_prompt_generated": PROMPT_MD.exists(),
        "manual_fallback_available": FALLBACK_MD.exists(),
        "review_gate_required": True,
        "review_gate_seen": False,
        "review_gate_valid": False,
        "sent_to_chatgpt": False,
        "status_reason": "waiting_for_user_confirmation",
    }


def check_gate(review: dict[str, Any] | None = None) -> dict[str, Any]:
    review_payload = review or latest_review()
    target_commit = review_target_commit(review_payload)
    status = default_status()
    status["expected_repo"] = REPO
    status["expected_commit"] = target_commit
    status["gate_path"] = "local_private/review_gate.json"

    if not GATE_PATH.exists():
        return status

    status["review_gate_seen"] = True
    try:
        gate = load_json(GATE_PATH)
    except json.JSONDecodeError:
        status["status_reason"] = "gate_json_invalid"
        return status

    failures: list[str] = []
    if gate.get("approved") is not True:
        failures.append("approved_not_true")

    gate_commit = gate.get("commit") or gate.get("review_target_commit")
    gate_nonce = gate.get("one_time_nonce") or gate.get("nonce")
    uses_live_skill_schema = "review_target_commit" in gate

    if gate.get("approved_action") not in (None, "chatgpt_review_relay"):
        failures.append("approved_action_mismatch")
    if gate.get("repo") not in (None, REPO):
        failures.append("repo_mismatch")
    if gate_commit != target_commit:
        failures.append("commit_mismatch")
    if gate.get("review_request") not in (None, "reports/review_requests/latest.json"):
        failures.append("review_request_mismatch")
    if gate.get("used") not in (None, False):
        failures.append("gate_already_used")
    if not gate_nonce:
        failures.append("missing_nonce")
    if not uses_live_skill_schema and gate.get("approved_action") is None:
        failures.append("approved_action_missing")

    expires_at = parse_time(gate.get("expires_at"))
    if expires_at is None:
        failures.append("expires_at_invalid")
    elif expires_at <= now_utc():
        failures.append("gate_expired")

    if failures:
        status["status_reason"] = ",".join(failures)
        return status

    status["review_gate_valid"] = True
    status["status_reason"] = "gate_valid"
    return status


def render_prompt(review: dict[str, Any]) -> str:
    review_files = review.get("review_files", [])
    review_lines = "\n".join(f"- `{path}`" for path in review_files) or "- latest.json 中未列出。"
    public_files = "\n".join(f"- `{path}`" for path in PUBLIC_REVIEW_FILES)
    target_commit = review_target_commit(review)
    stage = str(review.get("stage", "latest stage"))
    return "\n".join(
        [
            "请审核公开 GitHub repo：",
            "",
            PUBLIC_REPO_URL,
            "",
            "请读取：",
            "",
            public_files,
            "",
            f"请审核 `review_target_commit`：`{target_commit}`。",
            "",
            f"请根据 `reports/review_requests/latest.json` 中的 `review_target_commit` 和 review_files 审核 {stage}。",
            "不要把旧阶段 commit 当作本阶段的审核目标。",
            "",
            f"{stage} review_files：",
            "",
            review_lines,
            "",
            "重点检查：",
            "",
            "- ETF-only 是否保持。",
            "- 是否有自动下单 surface。",
            "- 是否有 secrets 泄漏。",
            "- 是否有真实 `~/.hermes` / `~/.openclaw` 修改迹象。",
            "- safety tests 和 smoke tests 是否合理。",
            "- public repo hygiene 是否保持。",
            "- 是否可以进入下一阶段。",
            "",
            "请输出：",
            "",
            "- 通过/不通过。",
            "- 高风险问题。",
            "- 必须修复项。",
            "- 建议下一步。",
            "",
            "提示：repo 是 public，不需要 GitHub connector。",
            "提醒：本系统不会自动下单，最终交易由用户手动决定。",
            "",
        ]
    )


def write_status(status: dict[str, Any]) -> None:
    write_json(STATUS_JSON, status)
    lines = [
        "# Review Relay Status",
        "",
        f"- Expected repo: `{status.get('expected_repo', REPO)}`",
        f"- Expected commit: `{status.get('expected_commit', '')}`",
        f"- Relay stage: `{status['relay_stage']}`",
        f"- Computer Use executed: `{str(status['computer_use_executed']).lower()}`",
        f"- ChatGPT prompt generated: `{str(status['chatgpt_prompt_generated']).lower()}`",
        f"- Manual fallback available: `{str(status['manual_fallback_available']).lower()}`",
        f"- Review gate required: `{str(status['review_gate_required']).lower()}`",
        f"- Review gate seen: `{str(status['review_gate_seen']).lower()}`",
        f"- Review gate valid: `{str(status['review_gate_valid']).lower()}`",
        f"- Sent to ChatGPT: `{str(status['sent_to_chatgpt']).lower()}`",
        f"- Status reason: `{status['status_reason']}`",
        "",
        "Draft-only status. No Computer Use action was executed. This relay不会自动下单，最终交易由用户手动决定。",
        "",
    ]
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


def public_payload(review: dict[str, Any], prompt: str, gate_status: dict[str, Any]) -> dict[str, Any]:
    target_commit = review_target_commit(review)
    return {
        "repo": REPO,
        "public_repo_url": PUBLIC_REPO_URL,
        "review_target_commit": target_commit,
        "handoff_commit": review.get("handoff_commit"),
        "handoff_generated_from_head": review.get("handoff_generated_from_head"),
        "current_repo_head": review.get("current_repo_head") or current_repo_head(),
        "commit_binding_note": review.get("commit_binding_note") or COMMIT_BINDING_NOTE,
        "review_request": "reports/review_requests/latest.json",
        "handoff": "reports/codex_handoff/latest.json",
        "public_files": PUBLIC_REVIEW_FILES,
        "prompt": prompt,
        "gate": gate_status,
        "sent_to_chatgpt": False,
        "computer_use_executed": False,
    }

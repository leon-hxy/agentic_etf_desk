#!/usr/bin/env python3
"""Shared helpers for repo-only ChatGPT review relay previews."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPO = "leon-hxy/agentic_etf_desk"
PUBLIC_REPO_URL = "https://github.com/leon-hxy/agentic_etf_desk"
LATEST_REVIEW = ROOT / "reports" / "review_requests" / "latest.json"
GATE_PATH = ROOT / "local_private" / "review_gate.json"
CHATGPT_TARGET_PATH = ROOT / "local_private" / "chatgpt_review_target.json"
PROMPT_MD = ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.md"
PROMPT_JSON = ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.json"
FALLBACK_MD = ROOT / "reports" / "review_requests" / "manual_fallback_prompt.md"
STATUS_MD = ROOT / "reports" / "review_requests" / "relay_status.md"
STATUS_JSON = ROOT / "reports" / "review_requests" / "relay_status.json"
STAGE2E1_STAGE = "Stage 2E.1 ChatGPT relay target and input delivery hardened"
STAGE2E1_RELAY_STAGE = "stage2e1_relay_hardening_repo_only"
SUPPORTED_TARGET_MODES = ["dedicated_review_thread", "existing_conversation_url"]
DEFAULT_TARGET_MODE = "dedicated_review_thread"
MAX_SHORT_PROMPT_CHARS = 900
FAILURE_STOP_CONDITIONS = [
    "target_conversation_mismatch",
    "input_box_residual_draft_detected",
    "prompt_split_detected",
    "sent_message_not_confirmed",
]

PUBLIC_REVIEW_FILES = [
    "reports/review_requests/latest.md",
    "reports/review_requests/latest.json",
    "reports/codex_handoff/latest.md",
    "reports/codex_handoff/latest.json",
]
COMMIT_BINDING_NOTE = (
    "review_target_commit is the commit to review; handoff may be committed later "
    "and therefore cannot self-reference its own final SHA in the same commit."
)
FORBIDDEN_PROMPT_PATTERNS = [
    ("absolute user path", re.compile(re.escape("/" + "Users" + "/"))),
    ("absolute volume path", re.compile(re.escape("/" + "Volumes" + "/"))),
    ("local private path", re.compile(r"\blocal_private\b")),
    ("Feishu credential surface", re.compile(r"(?i)\bfeishu\b")),
    ("OpenAI key surface", re.compile(r"(?i)openai api key")),
    ("token assignment", re.compile(r"(?i)\btoken\s*=")),
    ("secret assignment", re.compile(r"(?i)\bsecret\s*=")),
    ("auth assignment", re.compile(r"(?i)\bauth\s*=")),
]


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
        "stage": "draft_only",
        "computer_use_executed": False,
        "chatgpt_prompt_generated": PROMPT_MD.exists(),
        "manual_fallback_available": FALLBACK_MD.exists(),
        "review_gate_required": True,
        "review_gate_seen": False,
        "review_gate_valid": False,
        "sent_to_chatgpt": False,
        "status_reason": "waiting_for_user_confirmation",
    }


def target_conversation_status() -> dict[str, Any]:
    status: dict[str, Any] = {
        "target_conversation_mode": DEFAULT_TARGET_MODE,
        "recommended_target_mode": DEFAULT_TARGET_MODE,
        "supported_target_modes": SUPPORTED_TARGET_MODES,
        "existing_conversation_url_source": "local_private/chatgpt_review_target.json",
        "existing_conversation_url_public_value": None,
        "existing_conversation_url_present": False,
        "target_config_seen": CHATGPT_TARGET_PATH.exists(),
        "target_selection_status": "pass",
        "target_selection_reason": "dedicated_review_thread_default",
    }

    if not CHATGPT_TARGET_PATH.exists():
        return status

    try:
        payload = load_json(CHATGPT_TARGET_PATH)
    except json.JSONDecodeError:
        status["target_selection_status"] = "fail"
        status["target_selection_reason"] = "target_config_json_invalid"
        return status

    mode = str(payload.get("mode") or DEFAULT_TARGET_MODE)
    if mode not in SUPPORTED_TARGET_MODES:
        status["target_selection_status"] = "fail"
        status["target_selection_reason"] = "unsupported_target_conversation_mode"
        return status

    status["target_conversation_mode"] = mode
    if mode == DEFAULT_TARGET_MODE:
        status["target_selection_reason"] = "dedicated_review_thread_selected"
        return status

    url = str(payload.get("existing_conversation_url") or "")
    status["existing_conversation_url_present"] = bool(url)
    if not url.startswith("https://chatgpt.com/c/"):
        status["target_selection_status"] = "fail"
        status["target_selection_reason"] = "existing_conversation_url_missing_or_invalid"
        return status

    status["target_selection_reason"] = "existing_conversation_url_loaded_from_local_private"
    return status


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
    public_files = ", ".join(f"`{path}`" for path in PUBLIC_REVIEW_FILES)
    target_commit = review_target_commit(review)
    return "\n".join(
        [
            f"请审核公开 repo {PUBLIC_REPO_URL} 的 `review_target_commit`: `{target_commit}`。",
            f"请只读取这些公开路径：{public_files}。",
            "重点检查 ETF-only、安全边界、无自动下单/券商写接口、无敏感信息泄漏、测试是否足够。",
            "请输出 pass/fail、高风险问题、必须修复项、下一步建议。",
            "repo 是 public，不需要 GitHub connector。最终交易由用户手动决定，系统不会自动下单。",
        ]
    )


def validate_public_prompt(prompt: str) -> dict[str, Any]:
    findings = [
        {"reason": reason}
        for reason, pattern in FORBIDDEN_PROMPT_PATTERNS
        if pattern.search(prompt)
    ]
    if len(prompt) > MAX_SHORT_PROMPT_CHARS:
        findings.append({"reason": "prompt_too_long_for_reliable_delivery"})
    for required in [PUBLIC_REPO_URL, *PUBLIC_REVIEW_FILES]:
        if required not in prompt:
            findings.append({"reason": f"missing_required_reference:{required}"})
    return {
        "status": "pass" if not findings else "fail",
        "prompt_chars": len(prompt),
        "max_prompt_chars": MAX_SHORT_PROMPT_CHARS,
        "findings": findings,
    }


def input_delivery_contract(prompt_check: dict[str, Any]) -> dict[str, Any]:
    return {
        "prompt_kind": "short_review_prompt",
        "prompt_entry_method": "paste_or_clipboard_insert",
        "long_prompt_typing_forbidden": True,
        "pre_send_safety_check_required": True,
        "pre_send_safety_check_status": prompt_check["status"],
        "max_prompt_chars": MAX_SHORT_PROMPT_CHARS,
        "prompt_chars": prompt_check["prompt_chars"],
        "send_confirmation_required": True,
        "residual_draft_check_required": True,
        "prompt_split_check_required": True,
    }


def relay_status_for_review(
    review: dict[str, Any],
    prompt: str,
    gate_status: dict[str, Any],
) -> dict[str, Any]:
    prompt_check = validate_public_prompt(prompt)
    target_status = target_conversation_status()
    status = dict(gate_status)
    status.update(target_status)
    status.update(
        {
            "stage": STAGE2E1_STAGE,
            "relay_stage": STAGE2E1_RELAY_STAGE,
            "expected_repo": REPO,
            "expected_commit": review_target_commit(review),
            "review_target_commit": review_target_commit(review),
            "chatgpt_prompt_generated": True,
            "manual_fallback_available": True,
            "sent_to_chatgpt": False,
            "computer_use_executed": False,
            "chatgpt_repo_access_observed": False,
            "chatgpt_review_started": False,
            "chatgpt_review_completed": False,
            "input_delivery_quality": "not_sent_repo_only_hardened",
            "input_delivery_contract": input_delivery_contract(prompt_check),
            "prompt_safety_check": prompt_check,
            "failure_stop_conditions": FAILURE_STOP_CONDITIONS,
            "failure_policy": "mark_failed_and_stop",
            "status_reason": "repo_only_relay_hardening_ready_no_live_send",
        }
    )
    if prompt_check["status"] != "pass":
        status["status_reason"] = "prompt_safety_check_failed"
    elif target_status["target_selection_status"] != "pass":
        status["status_reason"] = "target_selection_failed"
    return status


def write_status(status: dict[str, Any]) -> None:
    write_json(STATUS_JSON, status)
    lines = [
        "# Review Relay Status",
        "",
        f"- Stage: `{status.get('stage', '')}`",
        f"- Expected repo: `{status.get('expected_repo', REPO)}`",
        f"- Expected commit: `{status.get('expected_commit', '')}`",
        f"- Review target commit: `{status.get('review_target_commit', status.get('expected_commit', ''))}`",
        f"- Relay stage: `{status['relay_stage']}`",
        f"- Target conversation mode: `{status.get('target_conversation_mode', '')}`",
        f"- Recommended target mode: `{status.get('recommended_target_mode', '')}`",
        f"- Existing conversation URL source: `{status.get('existing_conversation_url_source', '')}`",
        f"- Existing conversation URL public value: `{status.get('existing_conversation_url_public_value')}`",
        f"- Computer Use executed: `{str(status['computer_use_executed']).lower()}`",
        f"- ChatGPT prompt generated: `{str(status['chatgpt_prompt_generated']).lower()}`",
        f"- Manual fallback available: `{str(status['manual_fallback_available']).lower()}`",
        f"- Review gate required: `{str(status['review_gate_required']).lower()}`",
        f"- Review gate seen: `{str(status['review_gate_seen']).lower()}`",
        f"- Review gate valid: `{str(status['review_gate_valid']).lower()}`",
        f"- Sent to ChatGPT: `{str(status['sent_to_chatgpt']).lower()}`",
        f"- Input delivery method: `{status.get('input_delivery_contract', {}).get('prompt_entry_method', '')}`",
        f"- Long prompt typing forbidden: `{str(status.get('input_delivery_contract', {}).get('long_prompt_typing_forbidden', False)).lower()}`",
        f"- Pre-send safety check: `{status.get('input_delivery_contract', {}).get('pre_send_safety_check_status', '')}`",
        f"- Failure policy: `{status.get('failure_policy', '')}`",
        f"- Status reason: `{status['status_reason']}`",
        "",
        "No Computer Use action was executed in Stage 2E.1. This relay不会自动下单，最终交易由用户手动决定。",
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
        "stage": STAGE2E1_STAGE,
        "relay_stage": STAGE2E1_RELAY_STAGE,
        "target_conversation": target_conversation_status(),
        "input_delivery_contract": input_delivery_contract(validate_public_prompt(prompt)),
        "prompt_safety_check": validate_public_prompt(prompt),
        "sent_to_chatgpt": False,
        "computer_use_executed": False,
    }

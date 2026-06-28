#!/usr/bin/env python3
"""Shared helpers for repo-only manual ChatGPT review prompts."""

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
PROMPT_MD = ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.md"
PROMPT_JSON = ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.json"
FALLBACK_MD = ROOT / "reports" / "review_requests" / "manual_fallback_prompt.md"
STATUS_MD = ROOT / "reports" / "review_requests" / "relay_status.md"
STATUS_JSON = ROOT / "reports" / "review_requests" / "relay_status.json"
CURRENT_REVIEW_STAGE = "Stage 2F review governance refactor completed"
CURRENT_RELAY_STAGE = "stage2f_review_governance_manual_only"
REVIEW_GOVERNANCE_MODE = "small_stage_codex_self_review_major_stage_chatgpt_manual"
MAX_SHORT_PROMPT_CHARS = 900

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
            f"Request manual major-stage ChatGPT review for public GitHub repo {PUBLIC_REPO_URL}.",
            f"Review `review_target_commit`: `{target_commit}`.",
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
        "prompt_kind": "manual_major_review_prompt",
        "prompt_entry_method": "user_manual_copy_only",
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
    status = dict(gate_status)
    status.pop("gate_path", None)
    status.update(
        {
            "stage": CURRENT_REVIEW_STAGE,
            "relay_stage": CURRENT_RELAY_STAGE,
            "expected_repo": REPO,
            "expected_commit": review_target_commit(review),
            "review_target_commit": review_target_commit(review),
            "review_governance_mode": REVIEW_GOVERNANCE_MODE,
            "review_route": "codex_self_review_for_small_stage",
            "major_review_route": "manual_chatgpt_review_for_major_stage",
            "chatgpt_computer_use_auto_review_deprecated": True,
            "chatgpt_review_is_manual": True,
            "codex_self_review_required_for_small_stage": True,
            "major_chatgpt_review_required_for_major_stage": True,
            "automatic_chatgpt_prompt_send_allowed": False,
            "chatgpt_prompt_generated": True,
            "manual_fallback_available": True,
            "review_gate_required": False,
            "review_gate_seen": False,
            "review_gate_valid": False,
            "sent_to_chatgpt": False,
            "computer_use_executed": False,
            "chatgpt_repo_access_observed": False,
            "chatgpt_review_started": False,
            "chatgpt_review_completed": False,
            "input_delivery_quality": "not_sent_manual_major_review_only",
            "input_delivery_contract": input_delivery_contract(prompt_check),
            "prompt_safety_check": prompt_check,
            "failure_policy": "manual_review_required_for_major_stage",
            "status_reason": "chatgpt_computer_use_auto_review_deprecated",
        }
    )
    if prompt_check["status"] != "pass":
        status["status_reason"] = "prompt_safety_check_failed"
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
        f"- Review governance mode: `{status.get('review_governance_mode', '')}`",
        f"- Review route: `{status.get('review_route', '')}`",
        f"- Major review route: `{status.get('major_review_route', '')}`",
        f"- ChatGPT Computer Use automatic review deprecated: `{str(status.get('chatgpt_computer_use_auto_review_deprecated', False)).lower()}`",
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
        "No Computer Use action was executed in Stage 2F. ChatGPT review is manual and user-initiated. This review route不会自动下单，最终交易由用户手动决定。",
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
        "stage": CURRENT_REVIEW_STAGE,
        "relay_stage": CURRENT_RELAY_STAGE,
        "review_governance_mode": REVIEW_GOVERNANCE_MODE,
        "review_route": "codex_self_review_for_small_stage",
        "major_review_route": "manual_chatgpt_review_for_major_stage",
        "chatgpt_computer_use_auto_review_deprecated": True,
        "automatic_chatgpt_prompt_send_allowed": False,
        "input_delivery_contract": input_delivery_contract(validate_public_prompt(prompt)),
        "prompt_safety_check": validate_public_prompt(prompt),
        "sent_to_chatgpt": False,
        "computer_use_executed": False,
    }

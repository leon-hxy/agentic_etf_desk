#!/usr/bin/env python3
"""Validate Stage 2A.6 notification and review relay safety."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


REPO = "leon-hxy/agentic_etf_desk"


def dangerous_terms() -> list[str]:
    return [
        "_".join(("place", "order")),
        "_".join(("submit", "order")),
        "_".join(("buy", "market")),
        "_".join(("sell", "market")),
        ".".join(("ib", "place" + "Order")),
        ".".join(("alpaca", "_".join(("submit", "order")))),
        "_".join(("execution", "agent")),
        "_".join(("order", "agent")),
        "_".join(("broker", "agent")),
        "_".join(("auto", "trade")),
        "_".join(("live", "trader")),
    ]


def forbidden_prompt_terms() -> list[str]:
    return [
        "/" + "Users" + "/",
        "/" + "Volumes" + "/",
        "Feishu App Secret=",
        "OpenAI API key=",
        "token" + "=",
        "secret" + "=",
        "auth" + "=",
    ]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def add(findings: list[dict[str, str]], file: str, reason: str) -> None:
    findings.append({"file": file, "reason": reason})


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def scan(root: Path) -> dict[str, object]:
    findings: list[dict[str, str]] = []

    for rel in ("local_private/review_gate.json", "local_private/notification_state.json"):
        if (root / rel).exists():
            ignored = git(root, "check-ignore", "-q", rel)
            tracked = git(root, "ls-files", "--error-unmatch", rel)
            if ignored.returncode != 0:
                add(findings, rel, "local private runtime state must be gitignored")
            if tracked.returncode == 0:
                add(findings, rel, "local private runtime state must not be tracked")

    example = root / "ops" / "review_gate" / "review_gate.example.json"
    if not example.exists():
        add(findings, "ops/review_gate/review_gate.example.json", "missing example gate")
    else:
        payload = json.loads(example.read_text(encoding="utf-8"))
        if payload.get("repo") != REPO:
            add(findings, str(example.relative_to(root)), "repo mismatch")
        if payload.get("commit") != "PLACEHOLDER_COMMIT_SHA":
            add(findings, str(example.relative_to(root)), "example commit must be placeholder")
        if payload.get("one_time_nonce") != "PLACEHOLDER_NONCE":
            add(findings, str(example.relative_to(root)), "example nonce must be placeholder")
        serialized = json.dumps(payload)
        if re.search(r"(?i)(user[_-]?id|chat[_-]?id|token|secret)\s*[:=]\s*['\"]?(?!PLACEHOLDER)", serialized):
            add(findings, str(example.relative_to(root)), "example contains private-looking value")

    prompt_path = root / "reports" / "review_requests" / "chatgpt_review_prompt.md"
    if prompt_path.exists():
        prompt = text(prompt_path)
        for term in forbidden_prompt_terms():
            if term in prompt:
                add(findings, str(prompt_path.relative_to(root)), f"prompt contains {term}")
        if "https://github.com/leon-hxy/agentic_etf_desk" not in prompt:
            add(findings, str(prompt_path.relative_to(root)), "missing public GitHub URL")
        if len(prompt) > 900:
            add(findings, str(prompt_path.relative_to(root)), "prompt is too long for relay")
        for forbidden in ("local_private", "reports/relay_smoke", "review_files"):
            if forbidden in prompt:
                add(findings, str(prompt_path.relative_to(root)), f"prompt contains {forbidden}")
    else:
        add(findings, str(prompt_path.relative_to(root)), "missing generated ChatGPT prompt")

    status_path = root / "reports" / "review_requests" / "relay_status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("relay_stage") in {
            "stage2f_review_governance_manual_only",
            "stage2f1_branch_governance_manual_only",
            "stage3a_codex_self_review_no_chatgpt",
            "stage3b_codex_self_review_no_chatgpt",
            "stage3ab_internal_review_no_chatgpt",
            "stage3c_internal_review_no_chatgpt",
            "stage3d_internal_review_no_chatgpt",
        }:
            if status.get("chatgpt_computer_use_auto_review_deprecated") is not True:
                add(findings, str(status_path.relative_to(root)), "Computer Use auto review must be deprecated")
            if status.get("review_route") != "codex_self_review_for_small_stage":
                add(findings, str(status_path.relative_to(root)), "small stages must use Codex self-review")
            if status.get("major_review_route") != "manual_chatgpt_review_for_major_stage":
                add(findings, str(status_path.relative_to(root)), "major stages must use manual ChatGPT review")
            if status.get("automatic_chatgpt_prompt_send_allowed") is not False:
                add(findings, str(status_path.relative_to(root)), "automatic ChatGPT prompt send must be disabled")
            if status.get("review_gate_required") is not False:
                add(findings, str(status_path.relative_to(root)), "review gate must not be required for deprecated relay")
            if status.get("computer_use_executed") is not False or status.get("sent_to_chatgpt") is not False:
                add(findings, str(status_path.relative_to(root)), "small-stage self-review must stay repo-only")
        elif status.get("relay_stage") == "stage3e_major_review_ready_manual_only":
            if status.get("chatgpt_computer_use_auto_review_deprecated") is not True:
                add(findings, str(status_path.relative_to(root)), "Computer Use auto review must be deprecated")
            if status.get("review_route") != "manual_chatgpt_review_for_major_stage":
                add(findings, str(status_path.relative_to(root)), "Stage 3E must use manual major review")
            if status.get("automatic_chatgpt_prompt_send_allowed") is not False:
                add(findings, str(status_path.relative_to(root)), "automatic ChatGPT prompt send must be disabled")
            if status.get("review_gate_required") is not False:
                add(findings, str(status_path.relative_to(root)), "manual major review package must not require live relay gate")
            if status.get("manual_chatgpt_review_ready") is not True:
                add(findings, str(status_path.relative_to(root)), "manual ChatGPT review readiness must be true")
            if status.get("computer_use_executed") is not False or status.get("sent_to_chatgpt") is not False:
                add(findings, str(status_path.relative_to(root)), "Stage 3E package must not auto-send review")
        elif status.get("relay_stage") == "stage3f_major_gate_feishu_notified_manual_review_ready":
            if status.get("chatgpt_computer_use_auto_review_deprecated") is not True:
                add(findings, str(status_path.relative_to(root)), "Computer Use auto review must be deprecated")
            if status.get("review_route") != "manual_chatgpt_review_for_major_stage":
                add(findings, str(status_path.relative_to(root)), "Stage 3F must keep manual major review")
            if status.get("automatic_chatgpt_prompt_send_allowed") is not False:
                add(findings, str(status_path.relative_to(root)), "automatic ChatGPT prompt send must be disabled")
            if status.get("review_gate_required") is not False:
                add(findings, str(status_path.relative_to(root)), "manual major review must not require live relay gate")
            if status.get("manual_chatgpt_review_ready") is not True:
                add(findings, str(status_path.relative_to(root)), "manual ChatGPT review readiness must be true")
            if status.get("feishu_message_sent") is not True:
                add(findings, str(status_path.relative_to(root)), "Stage 3F must record live Feishu notification")
            if status.get("computer_use_executed") is not False or status.get("sent_to_chatgpt") is not False:
                add(findings, str(status_path.relative_to(root)), "Stage 3F notification must not auto-send review")
        elif status.get("relay_stage") == "stage2e1_relay_hardening_repo_only":
            if status.get("target_conversation_mode") != "dedicated_review_thread":
                add(findings, str(status_path.relative_to(root)), "target mode must default to dedicated_review_thread")
            if status.get("existing_conversation_url_source") != "local_private/chatgpt_review_target.json":
                add(findings, str(status_path.relative_to(root)), "existing conversation URL must use local_private source")
            if status.get("existing_conversation_url_public_value") is not None:
                add(findings, str(status_path.relative_to(root)), "existing conversation URL value must not be public")
            contract = status.get("input_delivery_contract", {})
            if contract.get("prompt_entry_method") != "paste_or_clipboard_insert":
                add(findings, str(status_path.relative_to(root)), "prompt entry method must avoid long typed input")
            if contract.get("long_prompt_typing_forbidden") is not True:
                add(findings, str(status_path.relative_to(root)), "long prompt typing must be forbidden")
            if contract.get("pre_send_safety_check_status") != "pass":
                add(findings, str(status_path.relative_to(root)), "pre-send safety check must pass")
            if status.get("failure_policy") != "mark_failed_and_stop":
                add(findings, str(status_path.relative_to(root)), "failure policy must stop on relay mismatch")
            for condition in (
                "target_conversation_mismatch",
                "input_box_residual_draft_detected",
                "prompt_split_detected",
                "sent_message_not_confirmed",
            ):
                if condition not in status.get("failure_stop_conditions", []):
                    add(findings, str(status_path.relative_to(root)), f"missing stop condition {condition}")
            if status.get("computer_use_executed") is not False or status.get("sent_to_chatgpt") is not False:
                add(findings, str(status_path.relative_to(root)), "Stage 2E.1 must stay repo-only")

    fallback_path = root / "reports" / "review_requests" / "manual_fallback_prompt.md"
    if not fallback_path.exists():
        add(findings, str(fallback_path.relative_to(root)), "missing manual fallback prompt")

    relay_dir = root / "scripts" / "review_relay"
    for path in relay_dir.glob("*.py"):
        lowered = text(path).lower()
        for term in dangerous_terms():
            if term.lower() in lowered:
                add(findings, str(path.relative_to(root)), f"dangerous term {term}")
        if "path.home()" in lowered:
            add(findings, str(path.relative_to(root)), "must not read home directory")
        if "brokerage" in lowered or "broker.com" in lowered:
            add(findings, str(path.relative_to(root)), "must not access broker systems")

    output_text = ""
    for rel in (
        "reports/review_requests/relay_status.md",
        "reports/review_requests/manual_fallback_prompt.md",
        "reports/review_requests/chatgpt_review_prompt.md",
    ):
        path = root / rel
        if path.exists():
            output_text += "\n" + text(path)
    if "不会自动下单" not in output_text and "最终交易由用户手动决定" not in output_text:
        add(findings, "reports/review_requests", "relay outputs must include manual-trading warning")

    automation_prompt = root / "configs" / "codex_automation" / "chatgpt_review_relay_prompt.md"
    if automation_prompt.exists():
        prompt = text(automation_prompt)
        if "ChatGPT Computer Use automatic review route is deprecated" not in prompt:
            add(findings, str(automation_prompt.relative_to(root)), "missing deprecated relay notice")
        for required in (
            "Do not run Computer Use",
            "Do not open ChatGPT automatically",
            "Do not send ChatGPT prompts automatically",
            "Small-stage Codex self-review",
            "Major-stage ChatGPT review",
        ):
            if required not in prompt:
                add(findings, str(automation_prompt.relative_to(root)), f"missing governance rule {required}")

    return {"status": "pass" if not findings else "fail", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    payload = scan(Path(args.root).resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

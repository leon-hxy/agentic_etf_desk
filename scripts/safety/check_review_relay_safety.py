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
    else:
        add(findings, str(prompt_path.relative_to(root)), "missing generated ChatGPT prompt")

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
        allowed_hosts = ["chatgpt.com", "github.com", "raw.githubusercontent.com"]
        for host in allowed_hosts:
            if host not in prompt:
                add(findings, str(automation_prompt.relative_to(root)), f"missing allowed host {host}")

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

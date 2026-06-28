#!/usr/bin/env python3
"""Validate review relay and handoff commit binding consistency."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


PREVIOUS_STAGE_COMMITS = {
    "8a1b03f" + "8078c9593f4730cf87785b4663ed05855",
    "c837110" + "53e6570bb447315e603c0a0701b9086b2",
    "83eeec" + "88ddda138b310aa7d41078919ee0f9b12d",
    "d40315a" + "ea238db28b1bdf857efa4052b250634c4",
    "acd9995" + "d7c48c24f1d381158ac72afb7579e0039",
    "3991a8c" + "083d73a42ff2879b53ad009a022d7ed02",
    "630433a" + "5cef96756811950738f4cf8dd8b4c820e",
    "a60f314" + "c39bf73274ffb6daff5ad902bf63b9293",
    "6db0e41" + "9622fefbcac9554900b1efb36890a959e",
    "9f06d64" + "67fb0bb5194affa43d5230c4d1f8c057b",
    "3a8076c" + "14c1918ad0e2225356c2acade63ba42c3",
    "336f28e" + "40fbb7fde70a63e55caebd346d28cb34a",
    "1d82b80" + "83c86613d9d516958aee704d0d8c65b2c",
    "59374cc" + "173da8cf57dfd1b8f98d27ef3338573e5",
    "88e31e9" + "daedcabb070469600f4fe2437a42c150c",
    "7dc1f0a" + "0dd7287105ba9add47588b2e37943d997",
    "d30169e" + "512f260dd5b29eb328d0f41c73cc927a9",
    "74215dd" + "69814c07fd5c3fd3937ccee15f9be8e8f",
    "23cebeb" + "ed1d07f0b35e66b284ec0891b427d8716",
    "9ac1dd8" + "b96fe98bae4bd676966293f03e0908047",
    "5a5d68e" + "2e34c6203ee2ab784dbbe3fa9a1cf1a6d",
    "f7fa73b" + "79ab1e3886c69bfd6ca5874a662acbb75",
    "2006d60" + "f237a9b47f34236fd7dd299e9bbdb4f86",
    "2371423" + "0ebda5bbaa16c27fac9efdf8d76663911",
    "78b6e39" + "9b041dc988208261db4d3ec55f0c74749",
    "945dc00" + "2ed39ee64e36a7ad51714dd8d48fe0903",
    "3e90368" + "d332749f731177688f532f1127206845f",
}
EXPECTED_STAGE = "Stage 3E major_review_package_ready"
JSON_TARGET_PATHS = [
    "reports/review_requests/latest.json",
    "reports/codex_handoff/latest.json",
    "reports/review_requests/chatgpt_review_prompt.json",
]
TEXT_TARGET_PATHS = [
    "reports/review_requests/chatgpt_review_prompt.md",
    "reports/review_requests/manual_fallback_prompt.md",
    "reports/review_requests/latest.md",
    "reports/codex_handoff/latest.md",
]
STATUS_JSON = "reports/review_requests/relay_status.json"
STATUS_MD = "reports/review_requests/relay_status.md"


def load_json(root: Path, path: str) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def read_text(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def add(findings: list[dict[str, str]], path: str, reason: str) -> None:
    findings.append({"file": path, "reason": reason})


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def validate_git_commit(root: Path, commit: str, findings: list[dict[str, str]], label: str) -> None:
    result = git(root, "cat-file", "-e", f"{commit}^{{commit}}")
    if result.returncode != 0:
        add(findings, label, "not a valid git commit")
        return

    subject = git(root, "show", "-s", "--format=%s", commit)
    if subject.returncode != 0:
        add(findings, label, "cannot read git commit subject")
        return

    lowered = subject.stdout.lower()
    if "stage2a" in lowered:
        add(findings, label, "review target points to an old stage")


def scan(root: Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []

    try:
        review = load_json(root, "reports/review_requests/latest.json")
        handoff = load_json(root, "reports/codex_handoff/latest.json")
        prompt_json = load_json(root, "reports/review_requests/chatgpt_review_prompt.json")
        relay_status = load_json(root, STATUS_JSON)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return {"status": "fail", "findings": [{"file": "reports", "reason": str(exc)}]}

    target = review.get("review_target_commit")
    if not isinstance(target, str) or not target:
        add(findings, "reports/review_requests/latest.json", "missing review_target_commit")
        target = ""
    if target in PREVIOUS_STAGE_COMMITS:
        add(findings, "reports/review_requests/latest.json", "review_target_commit points to old stage")
    validate_git_commit(root, str(target), findings, "review_target_commit")

    expected_stage = EXPECTED_STAGE
    expected_loop_state_stage = EXPECTED_STAGE
    for path, payload in (
        ("reports/review_requests/latest.json", review),
        ("reports/codex_handoff/latest.json", handoff),
    ):
        if payload.get("stage") != expected_stage:
            add(findings, path, f"stage must be {EXPECTED_STAGE}")
        if payload.get("loop_state_stage") != expected_loop_state_stage:
            add(
                findings,
                path,
                f"loop_state_stage must be {EXPECTED_STAGE}",
            )
        if payload.get("review_target_commit") != target:
            add(findings, path, "review_target_commit mismatch")
        if payload.get("handoff_commit") is not None:
            add(findings, path, "handoff_commit must be null before self-reference is possible")
        if payload.get("current_repo_head") != payload.get("handoff_generated_from_head"):
            add(findings, path, "current_repo_head must equal handoff_generated_from_head")
        current_repo_head = str(payload.get("current_repo_head") or "")
        if git(root, "cat-file", "-e", f"{current_repo_head}^{{commit}}").returncode != 0:
            add(findings, path, "current_repo_head is not a valid git commit")

    if prompt_json.get("review_target_commit") != target:
        add(findings, "reports/review_requests/chatgpt_review_prompt.json", "review_target_commit mismatch")
    if prompt_json.get("gate", {}).get("expected_commit") != target:
        add(findings, "reports/review_requests/chatgpt_review_prompt.json", "gate expected_commit mismatch")
    if relay_status.get("review_target_commit") != target:
        add(findings, STATUS_JSON, "review_target_commit mismatch")
    if relay_status.get("expected_commit") != target:
        add(findings, STATUS_JSON, "expected_commit mismatch")
    if relay_status.get("relay_stage") != "stage3e_major_review_ready_manual_only":
        add(findings, STATUS_JSON, "relay_stage mismatch")
    if relay_status.get("chatgpt_computer_use_auto_review_deprecated") is not True:
        add(findings, STATUS_JSON, "ChatGPT Computer Use auto review must be deprecated")
    if relay_status.get("sent_to_chatgpt") is not False:
        add(findings, STATUS_JSON, "Stage 3E package must not send to ChatGPT")
    if relay_status.get("computer_use_executed") is not False:
        add(findings, STATUS_JSON, "Stage 3E package must not execute Computer Use")

    for path in TEXT_TARGET_PATHS:
        content = read_text(root, path)
        if "review_target_commit" not in content:
            add(findings, path, "missing review_target_commit label")
        if str(target) not in content:
            add(findings, path, "missing review_target_commit value")

    status_md = read_text(root, STATUS_MD)
    if str(target) not in status_md:
        add(findings, STATUS_MD, "missing expected commit value")

    for path in JSON_TARGET_PATHS + TEXT_TARGET_PATHS + [STATUS_JSON, STATUS_MD]:
        content = read_text(root, path)
        for old_commit in PREVIOUS_STAGE_COMMITS:
            if old_commit in content:
                add(findings, path, "contains previous stage commit")

    if '"commit"' in read_text(root, "reports/review_requests/chatgpt_review_prompt.json"):
        add(findings, "reports/review_requests/chatgpt_review_prompt.json", "top-level commit field is ambiguous")

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

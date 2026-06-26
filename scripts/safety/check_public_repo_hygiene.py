#!/usr/bin/env python3
"""Scan public repo files for local-private metadata and secret-shaped values."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}
MAX_TEXT_BYTES = 1_000_000

SAFE_VALUES = {
    "false",
    "true",
    "null",
    "none",
    "no",
    "yes",
    "present",
    "absent",
    "placeholder",
    "changeme",
    "change_me",
    "replace_me",
    "example",
    "dummy",
    "redacted",
    "<redacted>",
}


def private_key_pattern() -> re.Pattern[str]:
    marker = "PRIVATE" + " KEY"
    return re.compile(r"-----BEGIN [A-Z ]*" + re.escape(marker) + r"-----")


def feishu_secret_assignment_pattern() -> re.Pattern[str]:
    key_name = "FEISHU" + "_APP" + "_SECRET"
    return re.compile(re.escape(key_name) + r"\s*=")


def path_patterns() -> list[tuple[str, re.Pattern[str]]]:
    users_path = "/" + "Users" + "/"
    volumes_path = "/" + "Volumes" + "/"
    launch_agents = "Library" + "/" + "LaunchAgents"
    return [
        ("absolute user path", re.compile(re.escape(users_path))),
        ("absolute volume path", re.compile(re.escape(volumes_path))),
        (
            "real launch agent path",
            re.compile(
                r"(?:"
                + re.escape(users_path)
                + r"[^`\s]+|"
                + re.escape(volumes_path)
                + r"[^`\s]+/[^`\s]+)"
                + re.escape("/" + launch_agents + "/")
            ),
        ),
        ("local username path fragment", re.compile(r"(?i)(?:^|/)" + "leon" + r"(?:/|$)")),
        ("local volume-user fragment", re.compile(r"(?i)" + "macos" + "/" + "leon")),
    ]


ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|token|auth|password|secret)\b\s*[:=]\s*['\"]?([^'\"\s,#}]+)"
)
PID_PATTERN = re.compile(r"(?im)^.*\bpid\b[^\n]*\b[1-9][0-9]{1,6}\b.*$")
PID_REASON = "real " + "pid" + " line"
SAMPLE_CHARS = 80


def iter_candidate_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if path.is_dir():
            continue
        if path.stat().st_size > MAX_TEXT_BYTES:
            continue
        files.append(path)
    return files


def read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def safe_assignment_value(value: str) -> bool:
    cleaned = value.strip().strip(",").strip()
    lowered = cleaned.lower()
    return (
        lowered in SAFE_VALUES
        or cleaned.startswith("$")
        or cleaned.startswith("${")
        or (cleaned.startswith("<") and cleaned.endswith(">"))
    )


def scan_file(root: Path, path: Path) -> list[dict[str, str]]:
    text = read_text(path)
    if text is None:
        return []

    rel = str(path.relative_to(root))
    findings: list[dict[str, str]] = []

    for reason, pattern in path_patterns():
        if pattern.search(text):
            findings.append({"file": rel, "reason": reason})

    for line in PID_PATTERN.findall(text):
        findings.append({"file": rel, "reason": PID_REASON, "sample": line[:SAMPLE_CHARS]})

    if feishu_secret_assignment_pattern().search(text):
        findings.append({"file": rel, "reason": "Feishu app secret assignment"})

    if private_key_pattern().search(text):
        findings.append({"file": rel, "reason": "private key block"})

    for match in ASSIGNMENT_PATTERN.finditer(text):
        value = match.group(2)
        if not safe_assignment_value(value):
            findings.append({"file": rel, "reason": f"sensitive-looking {match.group(1)} value"})

    return findings


def scan(root: Path) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    for path in iter_candidate_files(root):
        findings.extend(scan_file(root, path))
    return {
        "status": "pass" if not findings else "fail",
        "files_checked": len(iter_candidate_files(root)),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    payload = scan(Path(args.root).resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

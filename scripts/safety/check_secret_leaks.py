#!/usr/bin/env python3
"""Scan repo-only output areas for accidental sensitive-value leakage."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OUTPUT_DIRS = ("logs", "reports")
CONFIG_DIR = "configs"
LEAK_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\.env",
        r"auth",
        r"token",
        r"secret",
        r"FEISHU_APP_SECRET",
    )
]
ASSIGNMENT_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|secret|auth|password)\s*[:=]\s*['\"]?([^'\"\s#]+)"
)
PLACEHOLDER_VALUES = {
    "placeholder",
    "changeme",
    "change_me",
    "replace_me",
    "example",
    "dummy",
    "redacted",
    "<redacted>",
    "${placeholder}",
}


def iter_text_files(root: Path, directory: str) -> list[Path]:
    base = root / directory
    if not base.exists():
        return []
    return [path for path in base.rglob("*") if path.is_file()]


def scan_outputs(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for directory in OUTPUT_DIRS:
        for path in iter_text_files(root, directory):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in LEAK_PATTERNS:
                if pattern.search(text):
                    findings.append(
                        {"file": str(path.relative_to(root)), "reason": f"matched {pattern.pattern}"}
                    )
                    break
    return findings


def scan_config_values(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in iter_text_files(root, CONFIG_DIR):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in ASSIGNMENT_PATTERN.finditer(text):
            value = match.group(2).strip()
            if value.lower() not in PLACEHOLDER_VALUES and not value.startswith("${"):
                findings.append(
                    {"file": str(path.relative_to(root)), "reason": "non-placeholder sensitive value"}
                )
    return findings


def scan(root: Path) -> dict[str, object]:
    findings = scan_outputs(root) + scan_config_values(root)
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


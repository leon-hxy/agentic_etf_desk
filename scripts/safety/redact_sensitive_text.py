#!/usr/bin/env python3
"""Redact sensitive-looking values from repo-visible log text."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|token|auth|password|secret)\b(\s*[:=]\s*)['\"]?([^'\"\s,#}]+)"
)
AUTHORIZATION_RE = re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,;]+")
ABSOLUTE_PATH_RE = re.compile(r"/(?:Users|Volumes)/[^`\s,'\")]+")
LOCAL_PRIVATE_RE = re.compile(r"\blocal_private/[^`\s,'\")]+")
PID_RE = re.compile(r"(?im)\bpid\b\s*[:=]?\s*[1-9][0-9]{1,6}")
PRIVATE_ID_RE = re.compile(
    r"(?i)\b((?:feishu|broker)[_-]?(?:app|chat|open|tenant|user|account)?[_-]?id)\b"
    r"(\s*[:=]\s*)['\"]?([^'\"\s,#}]+)"
)


def redact_text(text: str) -> str:
    """Return text with values unsafe for public logs replaced by placeholders."""

    redacted = ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}{match.group(2)}<redacted>", text)
    redacted = AUTHORIZATION_RE.sub(lambda match: f"{match.group(1)}<redacted>", redacted)
    redacted = PRIVATE_ID_RE.sub(lambda match: f"{match.group(1)}{match.group(2)}<redacted-id>", redacted)
    redacted = ABSOLUTE_PATH_RE.sub("<redacted-path>", redacted)
    redacted = LOCAL_PRIVATE_RE.sub("local_private/<redacted>", redacted)
    redacted = PID_RE.sub("pid: <redacted-pid>", redacted)
    return redacted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", help="Text file to redact. Defaults to stdin.")
    parser.add_argument("--output", help="Optional output path. Defaults to stdout.")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    redacted = redact_text(text)
    if args.output:
        Path(args.output).write_text(redacted, encoding="utf-8")
    else:
        sys.stdout.write(redacted)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

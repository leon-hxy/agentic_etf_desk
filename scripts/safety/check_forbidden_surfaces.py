#!/usr/bin/env python3
"""Scan repository files for policy-banned execution surfaces."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def terms() -> list[str]:
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
        "_".join(("broker", "write")),
    ]


SAFE_GOVERNANCE_FIELDS = (
    "_".join(("broker", "write", "allowed")),
    "_".join(("broker", "write", "surface")),
)
LEGACY_REVIEW_FIELD = "_".join(("broker", "write", "surface"))
UNSAFE_GOVERNANCE_LINE = re.compile(
    r"(?im)^([ \t>*-]*[\"']?(?:"
    + "|".join(re.escape(field) for field in SAFE_GOVERNANCE_FIELDS)
    + r")[\"']?[ \t]*[:=][ \t]*(?:true|yes|1)[ \t,]*(?:#.*)?)$"
)
SAFE_GOVERNANCE_LINE = re.compile(
    r"(?im)^([ \t>*-]*[\"']?(?:"
    + "|".join(re.escape(field) for field in SAFE_GOVERNANCE_FIELDS)
    + r")[\"']?[ \t]*[:=][ \t]*(?:false|no|0|null|none)?[ \t,]*(?:#.*)?)$"
)


def mask_safe_governance_fields(text: str) -> str:
    """Ignore false-valued broker-write governance fields without masking true values."""

    text = re.sub(
        re.escape(LEGACY_REVIEW_FIELD),
        "safe_governance_field",
        text,
        flags=re.IGNORECASE,
    )

    def replace(match: re.Match[str]) -> str:
        line = match.group(1)
        masked = line
        for field in SAFE_GOVERNANCE_FIELDS:
            masked = re.sub(
                re.escape(field), "safe_governance_field", masked, flags=re.IGNORECASE
            )
        return masked

    return SAFE_GOVERNANCE_LINE.sub(replace, text)


def iter_files(root: Path) -> list[Path]:
    ignored_parts = {".git", "__pycache__", ".pytest_cache"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in ignored_parts for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return files


def is_doc(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    return rel.parts[0] == "docs"


def scan(root: Path) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    danger = terms()
    for path in iter_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(root))
        for match in UNSAFE_GOVERNANCE_LINE.finditer(text):
            findings.append({"file": rel, "reason": "unsafe broker-write governance flag"})
        lowered = mask_safe_governance_fields(text).lower()
        matched = [term for term in danger if term.lower() in lowered]
        if not matched:
            continue
        if is_doc(path, root):
            label_ok = "forbidden example" in lowered or "policy-only forbidden" in lowered
            if not label_ok:
                findings.append({"file": rel, "reason": "docs match without forbidden label"})
        else:
            findings.append({"file": rel, "reason": "forbidden surface outside docs"})

    return {
        "status": "pass" if not findings else "fail",
        "checked_terms_count": len(danger),
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

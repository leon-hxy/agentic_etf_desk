#!/usr/bin/env python3
"""Verify data and strategy code routes symbols through the ETF universe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_REFERENCE = "etf_universe.yaml"
VALIDATION_REFERENCE = "validate_requested_symbols"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def scan(root: Path) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    data_scripts = [path for path in (root / "scripts" / "data").glob("*.py")]
    strategy_scripts = [path for path in (root / "strategies").rglob("*.py")]

    for path in data_scripts:
        text = read(path)
        if path.name != "load_universe.py" and REQUIRED_REFERENCE not in text and "load_universe" not in text:
            findings.append(
                {"file": str(path.relative_to(root)), "reason": "missing universe reference"}
            )
        if "--symbols" in text and VALIDATION_REFERENCE not in text:
            findings.append(
                {"file": str(path.relative_to(root)), "reason": "symbol argument lacks allowlist validation"}
            )

    for path in strategy_scripts:
        text = read(path)
        if "symbol" in text.lower() and REQUIRED_REFERENCE not in text and "load_universe" not in text:
            findings.append(
                {"file": str(path.relative_to(root)), "reason": "strategy symbol use lacks universe reference"}
            )

    return {
        "status": "pass" if not findings else "fail",
        "data_scripts_checked": len(data_scripts),
        "strategy_scripts_checked": len(strategy_scripts),
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


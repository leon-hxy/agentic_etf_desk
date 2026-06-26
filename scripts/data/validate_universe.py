#!/usr/bin/env python3
"""Validate the ETF-only universe policy."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from load_universe import REQUIRED_FIELDS, UNIVERSE_PATH, universe_entries


def validate(path: Path = UNIVERSE_PATH) -> dict[str, object]:
    entries = universe_entries(path)
    errors: list[str] = []
    seen: set[str] = set()
    allowed_count = 0
    disallowed_leveraged_or_inverse = 0

    for index, entry in enumerate(entries, start=1):
        missing = sorted(REQUIRED_FIELDS - set(entry))
        if missing:
            errors.append(f"entry {index} missing fields: {', '.join(missing)}")
            continue

        symbol = str(entry["symbol"]).upper()
        if symbol in seen:
            errors.append(f"duplicate symbol: {symbol}")
        seen.add(symbol)

        if entry["asset_class"] != "ETF":
            errors.append(f"{symbol} asset_class must be ETF")

        is_allowed = bool(entry["is_allowed"])
        is_leveraged = bool(entry["is_leveraged"])
        is_inverse = bool(entry["is_inverse"])

        if is_allowed:
            allowed_count += 1
            if is_leveraged or is_inverse:
                disallowed_leveraged_or_inverse += 1
                errors.append(f"{symbol} cannot be allowed when leveraged or inverse")
            if not str(entry["notes"]).strip():
                errors.append(f"{symbol} must include notes")
            if not str(entry["exchange"]).strip():
                errors.append(f"{symbol} must include exchange")

    return {
        "status": "pass" if not errors else "fail",
        "universe_file": "configs/universe/etf_universe.yaml",
        "total_count": len(entries),
        "allowed_count": allowed_count,
        "disallowed_leveraged_or_inverse": disallowed_leveraged_or_inverse,
        "errors": errors,
    }


def main() -> int:
    payload = validate()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)


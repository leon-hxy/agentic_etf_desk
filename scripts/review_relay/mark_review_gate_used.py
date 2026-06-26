#!/usr/bin/env python3
"""Mark the local private review gate as used after a future approved relay."""

from __future__ import annotations

import json
import sys

from relay_common import GATE_PATH, check_gate, load_json, now_utc, write_json, write_status


def main() -> int:
    status = check_gate()
    if not GATE_PATH.exists():
        status["status_reason"] = "gate_missing_no_mark"
        write_status(status)
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0

    if not status["review_gate_valid"]:
        write_status(status)
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0

    gate = load_json(GATE_PATH)
    gate["used"] = True
    gate["used_at"] = now_utc().isoformat()
    write_json(GATE_PATH, gate)
    status["status_reason"] = "gate_marked_used"
    write_status(status)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

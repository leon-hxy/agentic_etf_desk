#!/usr/bin/env python3
"""Check local private review gate status without sending anything."""

from __future__ import annotations

import json
import sys

from relay_common import check_gate, write_status


def main() -> int:
    status = check_gate()
    status["sent_to_chatgpt"] = False
    status["computer_use_executed"] = False
    write_status(status)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

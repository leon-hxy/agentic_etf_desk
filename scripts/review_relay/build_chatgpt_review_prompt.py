#!/usr/bin/env python3
"""Build the public ChatGPT review prompt preview."""

from __future__ import annotations

import json
import sys

from relay_common import (
    PROMPT_JSON,
    PROMPT_MD,
    check_gate,
    latest_review,
    public_payload,
    relay_status_for_review,
    render_prompt,
    write_json,
    write_status,
)


def main() -> int:
    review = latest_review()
    gate_status = check_gate(review)
    prompt = render_prompt(review)

    PROMPT_MD.write_text(prompt, encoding="utf-8")
    status = relay_status_for_review(review, prompt, gate_status)
    write_json(PROMPT_JSON, public_payload(review, prompt, status))
    write_status(status)

    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

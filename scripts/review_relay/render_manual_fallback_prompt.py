#!/usr/bin/env python3
"""Render a manual fallback prompt for the user."""

from __future__ import annotations

import json
import sys

from relay_common import FALLBACK_MD, check_gate, latest_review, relay_status_for_review, render_prompt, write_status


def main() -> int:
    review = latest_review()
    prompt = render_prompt(review)
    fallback = "\n".join(
        [
            "# Manual ChatGPT Review Fallback Prompt",
            "",
            "Computer Use relay is optional and draft-only. If relay is unavailable, copy the prompt below into ChatGPT.",
            "",
            "This fallback不会自动下单，最终交易由用户手动决定。",
            "",
            "```text",
            prompt.strip(),
            "```",
            "",
        ]
    )
    FALLBACK_MD.write_text(fallback, encoding="utf-8")
    status = check_gate(review)
    status = relay_status_for_review(review, prompt, status)
    write_status(status)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""Build the public ChatGPT review prompt preview."""

from __future__ import annotations

import json
import sys

from relay_common import PROMPT_JSON, PROMPT_MD, check_gate, latest_review, public_payload, render_prompt, write_json, write_status


def main() -> int:
    review = latest_review()
    gate_status = check_gate(review)
    prompt = render_prompt(review)

    PROMPT_MD.write_text(prompt, encoding="utf-8")
    write_json(PROMPT_JSON, public_payload(review, prompt, gate_status))

    gate_status["chatgpt_prompt_generated"] = True
    gate_status["manual_fallback_available"] = True
    gate_status["sent_to_chatgpt"] = False
    gate_status["computer_use_executed"] = False
    write_status(gate_status)

    print(json.dumps(gate_status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

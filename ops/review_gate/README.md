# Review Gate

This directory documents the local private review gate protocol.

The real gate file is:

- `local_private/review_gate.json`

It must not be committed. It is used only after the user explicitly replies `确认审核` through the approved Hermes/Feishu path.

## Gate Rules

- One-time use.
- Must include `expires_at`.
- Must bind to the commit SHA in `reports/review_requests/latest.json`.
- Must set `approved_action` to `chatgpt_review_relay`.
- Must match repo `leon-hxy/agentic_etf_desk`.
- If invalid, expired, mismatched, or already used, Codex relay must not send anything to ChatGPT.

The gate never grants permission to trade, modify real Hermes/OpenClaw config, restart services, install dependencies, read secrets, or access broker systems.

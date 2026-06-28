# Deprecated ChatGPT Review Relay Design

Status: deprecated by Stage 2F. See `docs/review_governance.md`.

ChatGPT Computer Use automatic review route is deprecated.

The active review model is Small-stage Codex self-review and Major-stage
ChatGPT review. ChatGPT review is manual and user-initiated.

This is a repo-only design draft. It does not use Computer Use, open Chrome, or send anything to ChatGPT in Stage 2A.6.

## Purpose

After the user confirms review through Feishu, Codex can later use a local UI relay to open ChatGPT and paste a public review prompt. The prompt contains only:

- Public GitHub URL.
- Public repo-relative paths.
- Commit SHA.
- Review request path.
- Handoff path.

No local paths, secrets, Feishu credentials, Hermes private config, OpenClaw private config, provider keys, or broker credentials may be sent to ChatGPT.

## Gate Requirement

Codex relay must read `local_private/review_gate.json`.

The gate must be valid, one-time, unexpired, unused, and bound to the same commit as `reports/review_requests/latest.json`.

If the gate is missing or invalid, Codex must not send a ChatGPT prompt.

## Computer Use Safety

Recommended setup:

- Use a separate Chrome Profile.
- The profile should log in only to ChatGPT.
- Do not log in to broker sites, email, GitHub admin pages, Feishu admin pages, or other sensitive sites in that profile.
- Allow Codex only to access `chatgpt.com`, `github.com`, and `raw.githubusercontent.com`.
- Do not enable broad Always Allow permissions.
- Before sending the prompt, Codex must confirm the current page is ChatGPT.
- If the page is wrong, login state is wrong, a permission prompt appears, or any unexpected window appears, Codex must stop and notify the user.

If Computer Use fails, use `reports/review_requests/manual_fallback_prompt.md`.

## Trading Safety

The relay cannot trade, cannot modify real Hermes/OpenClaw, cannot connect broker systems, and cannot place orders. Final trading is manually decided by the user.

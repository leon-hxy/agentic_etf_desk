# Deprecated ChatGPT Review Relay Prompt Draft

Status: deprecated by Stage 2F.

ChatGPT Computer Use automatic review route is deprecated.

This file is retained only as historical context for why the automatic UI relay
route must not be used. The active governance model is:

- Small-stage Codex self-review.
- Major-stage ChatGPT review.

## Current Rule

- Do not run Computer Use.
- Do not open ChatGPT automatically.
- Do not send ChatGPT prompts automatically.
- Do not read or publish local ChatGPT conversation URLs.
- Do not read or send secrets, tokens, auth values, Feishu credentials, Hermes
  private config, OpenClaw private config, provider keys, or broker credentials.

Major-stage ChatGPT review is manual and user-initiated. Codex may prepare a
public prompt that uses only the GitHub URL, `review_target_commit`, and
repo-relative handoff/review request paths. The user decides whether to paste it
into ChatGPT.

Final trading is manually decided by the user.

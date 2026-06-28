# Review Governance

Stage 2F replaces the previous ChatGPT Computer Use relay idea with a simpler
review governance model.

## Decision

ChatGPT Computer Use automatic review route is deprecated.

The project now uses two review levels:

- Small-stage Codex self-review.
- Major-stage ChatGPT review.

ChatGPT review is manual and user-initiated. Codex may generate public review
materials in the repo, but it must not open ChatGPT, send prompts, click UI, or
run Computer Use for review delivery without a new explicit approval and a new
task scope.

## Small-stage Codex self-review

Use this for small repo-only changes, handoff refreshes, test updates, template
changes, and narrow safety fixes.

Required evidence:

- Updated `reports/codex_handoff/latest.md`.
- Updated `reports/codex_handoff/latest.json`.
- Updated `reports/review_requests/latest.md`.
- Updated `reports/review_requests/latest.json`.
- Safety and smoke tests appropriate to the changed surface.
- `git diff --check`.
- Clean `git status` before final response.

The self-review must check ETF-only constraints, no broker/write execution
surface, no secrets, no real Hermes/OpenClaw/Feishu gateway changes unless
explicitly approved, and final manual trading language where relevant.

## Major-stage ChatGPT review

Use this for phase transitions, live integration plans, any user-approved live
runtime change, significant strategy/backtest/reporting changes, security model
changes, or any change that materially affects the review or release process.

Major-stage ChatGPT review is manual. Codex prepares:

- A public GitHub URL.
- The `review_target_commit`.
- Repo-relative handoff and review request paths.
- A concise major-review prompt.

The user decides whether and when to paste that prompt into ChatGPT.

## Deprecated automatic route

The old route attempted to use ChatGPT through Computer Use as a UI relay. That
route is no longer the default, no longer part of the active review loop, and
must not be used by Codex automation drafts.

Forbidden for the active review loop:

- Opening ChatGPT automatically.
- Running Computer Use for review delivery.
- Sending ChatGPT prompts automatically.
- Reading or publishing local ChatGPT conversation URLs.
- Reading or sending local secrets, tokens, auth values, Feishu credentials,
  Hermes private config, OpenClaw private config, provider keys, or broker
  credentials.

No automatic order placement is allowed. No broker write access is allowed.
Final trading is manually decided by the user.

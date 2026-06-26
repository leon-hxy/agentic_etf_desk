# Stage 2B Repo-Only Task

status: ready
stage: Stage 2B repo-only

## Summary

Build the next repo-only layer of the ETF research system.

## Scope

- ETF strategy templates.
- Backtest engine.
- Reports and manual trade recommendation tickets.
- OpenClaw agents draft under `configs/openclaw/`.
- Hermes Feishu router draft under `configs/hermes/`.
- Safety tests.
- Smoke tests.
- Handoff update.
- Commit and push.

## Boundaries

- Repo-only.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not restart services.
- Do not install dependencies unless the user approves.
- Do not create execution/order/broker agents.
- Do not create auto-trading or live-trading agents.
- Do not write order placement code.
- Do not connect broker write interfaces.
- Do not add stocks, options, futures, crypto assets, leveraged ETFs, or inverse ETFs unless a future explicit allowlist exists.

## Required Tests

- Safety tests.
- Smoke tests.
- Public repo hygiene test.
- `git diff --check`.
- `git status --short --untracked-files=all`.

## Completion

Update:

- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`

Then commit and push the repo-only change.

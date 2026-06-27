# Stage 2C Loop Automation Dry-Run Task

status: planned
stage: Stage 2C loop automation dry-run repo-only

## Summary

Design and test the loop automation flow as a repo-only dry run. This task is
for local files, fixtures, safety tests, and review artifacts only.

## Scope

- Define repo-only loop state transitions.
- Add dry-run command examples that read and write only repo files.
- Add safety tests for stage, task, handoff, and review request consistency.
- Keep ChatGPT review relay preview-only unless a future user approval gate is
  added.
- Update handoff and review request artifacts after the dry run.

## Boundaries

- Repo-only.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify a real Feishu gateway.
- Do not restart services.
- Do not install dependencies unless the user approves.
- Do not run Computer Use.
- Do not create execution/order/broker agents.
- Do not create auto-trading or live-trading agents.
- Do not write order placement code.
- Do not connect broker write interfaces.
- Do not add stocks, options, futures, crypto assets, leveraged ETFs, or inverse
  ETFs unless a future explicit allowlist exists.

## Required Tests

- Safety tests.
- Smoke tests.
- Public repo hygiene test.
- Handoff and review request consistency test.
- Loop state consistency test.
- `git diff --check`.
- `git status --short --untracked-files=all`.

## User Approval Required Before

- Any live Hermes or OpenClaw config change.
- Any real Feishu gateway change.
- Any service restart.
- Any dependency installation.
- Any Computer Use relay beyond repo-only prompt generation.
- Any secret, token, auth, `.env`, provider key, Feishu App Secret, or broker
  credential handling.

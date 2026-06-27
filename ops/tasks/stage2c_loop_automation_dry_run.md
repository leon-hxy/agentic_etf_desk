# Stage 2C Loop Automation Dry-Run Task

status: completed
stage: Stage 2C completed
review_target_commit: set in `reports/review_requests/latest.json` after the business commit exists

## Summary

Designed and tested the loop automation flow as a repo-only dry run. This task
used local files, fixtures, safety tests, and review artifacts only.

## Scope

- Defined repo-only loop state transitions.
- Added dry-run command examples that read and write only repo files.
- Added safety tests for stage, task, handoff, and review request consistency.
- Kept ChatGPT review relay preview-only unless a future user approval gate is
  added.
- Updated handoff and review request artifacts after the dry run.

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

## Completion

The repo-only dry run completed. It generated:

- `scripts/safety/run_loop_dry_run.py`
- `scripts/review_relay/render_notification_preview.py`
- `reports/loop_dry_run/stage2c_loop_dry_run.md`
- `reports/loop_dry_run/stage2c_loop_dry_run.json`
- `reports/review_requests/notification_preview.md`
- `reports/review_requests/notification_preview.json`

This was a repo-only dry run completed without changing real Hermes/OpenClaw
configuration, without changing a real Feishu gateway, without restarting
services, without installing dependencies, without running Computer Use, and
without touching secrets.

## User Approval Required Before

- Any live Hermes or OpenClaw config change.
- Any real Feishu gateway change.
- Any service restart.
- Any dependency installation.
- Any Computer Use relay beyond repo-only prompt generation.
- Any secret, token, auth, `.env`, provider key, Feishu App Secret, or broker
  credential handling.

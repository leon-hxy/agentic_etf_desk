# Stage 2D Safety Checks

Repo-only preparation for safety checks before any future live Hermes/Feishu
notification and local approval gate integration.

Live checks require explicit user approval before touching real systems.

This future safety run requires explicit user approval.

## Preflight Checks For Future Live Work

- Confirm the user approves the exact live Stage 2D scope.
- Confirm the repo is clean before live work starts.
- Confirm the backup plan completed before applying live changes.
- Confirm the rollback plan is available.
- Confirm the review request binds to the intended commit.
- Confirm notification preview remains draft-only until the approval gate is
  valid.
- Confirm no private credential values are printed or written.

## Safety Tests To Run

- `python3 -m unittest tests.safety.test_safety`
- `python3 -m unittest tests.safety.test_public_repo_hygiene`
- `python3 -m unittest tests.safety.test_notification_loop_safety`
- `python3 -m unittest tests.safety.test_review_relay_safety`
- `python3 -m unittest tests.safety.test_handoff_commit_consistency`
- `python3 -m unittest tests.safety.test_stage2d_preparation_plan`
- `git diff --check`
- `git status --short --untracked-files=all`

## Live Abort Conditions

- Any live path is unclear.
- Any backup is missing.
- Any private value would be exposed.
- Any Feishu send would happen without explicit approval.
- Any Hermes or gateway restart is needed but not explicitly approved.
- Any dependency installation is needed but not explicitly approved.
- Any broker access or automatic trading capability appears.
- Any ETF-only boundary is weakened.

## Explicit Non-Actions In This Commit

- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify a real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not run real Computer Use.
- Do not send Feishu messages.

Final trading is manually decided by the user.

# Codex Task Template

status: draft
stage: ""

## Objective

Describe the repo-only objective.

## Required Reading

- `AGENTS.md`
- `docs/project_context_for_chatgpt.md`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`

## Scope

List allowed repo files or areas.

## Forbidden Actions

- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not restart services.
- Do not install dependencies without user approval.
- Do not write secrets.
- Do not add broker write access.
- Do not create automatic trading or order placement code.

## Required Verification

- Safety tests.
- Smoke tests.
- Public repo hygiene test.
- `git diff --check`.
- `git status --short --untracked-files=all`.

## Required Handoff

- Update `reports/codex_handoff/latest.md`.
- Update `reports/codex_handoff/latest.json`.
- Update `reports/review_requests/latest.md`.
- Update `reports/review_requests/latest.json`.
- Commit and push.

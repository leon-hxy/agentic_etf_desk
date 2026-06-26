# Codex Loop Manager Prompt Draft

This is a suggested Codex App automation prompt draft. It is not installed automatically.

## Draft Prompt

Read `AGENTS.md` first.

Then read task files in `ops/tasks/` whose status is `ready`. Execute only repo-only tasks. Do not modify files outside this repository.

Before making changes:

- Confirm the task scope.
- Confirm forbidden actions.
- Confirm required tests and handoff files.

Allowed work:

- Edit repo files for the approved task.
- Create repo-only docs, tests, templates, and generated sample artifacts.
- Run repo-local tests and git checks.

Forbidden work:

- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not restart services.
- Do not install dependencies unless the user explicitly approves.
- Do not modify Feishu gateway/configuration.
- Do not connect brokers.
- Do not create automatic trading capability.
- Do not create execution, order, broker, auto-trading, or live-trading agents.
- Do not write order placement code.
- Do not write secrets, tokens, auth values, provider keys, Feishu App Secret values, or broker credentials.

Completion steps:

1. Run safety tests and smoke tests.
2. Run the public repo hygiene test.
3. Run `git diff --check`.
4. Run `git status --short --untracked-files=all`.
5. Update `reports/codex_handoff/latest.md`.
6. Update `reports/codex_handoff/latest.json`.
7. Update `reports/review_requests/latest.md`.
8. Update `reports/review_requests/latest.json`.
9. Commit and push.

If any test fails, fix it and rerun. Do not claim success without current passing evidence.

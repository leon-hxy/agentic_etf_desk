# Stage 2F Review Governance Refactor

status: completed
stage: Stage 2F review governance refactor completed
mode: repo-only
review_target_commit: set in `reports/review_requests/latest.json` after the business commit exists

## Objective

Deprecate the ChatGPT Computer Use automatic review route and replace it with:

- Small-stage Codex self-review.
- Major-stage ChatGPT review.

## Scope

- Create repo-only review governance design.
- Create internal Codex self-review template.
- Create major ChatGPT review template.
- Create review governance task template.
- Create Codex automation draft for choosing the review level.
- Update public handoff and review request artifacts.
- Add safety tests for the governance model.

## Forbidden actions

- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify a real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not run Computer Use.
- Do not open ChatGPT automatically.
- Do not send ChatGPT prompts automatically.
- Do not access broker, email, GitHub admin, or Feishu admin pages.
- Do not create broker write access.
- Do not create automatic order placement code.

Final trading is manually decided by the user.

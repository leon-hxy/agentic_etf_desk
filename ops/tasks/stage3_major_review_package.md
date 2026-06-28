# Stage 3E Major Review Package

status: planned
stage: Stage 3E
branch: stage/stage3-data-backtest
review_level: major_stage
depends_on: Stage 3D completed_internal_review
repo-only

## Objective

Package Stage 3A through Stage 3D evidence for major-stage review after the
small stages are complete.

## Review

Small-stage review: Codex self-review is complete before this package.

Major-stage review: manual ChatGPT review.

Stage 3E is the first Stage 3 task that prepares major-stage ChatGPT review
materials. Do not request manual ChatGPT review until after the Stage 3E package
is complete.

Feishu notification asks the user whether to request ChatGPT review. Codex may
prepare public GitHub URLs, commit SHAs, handoff paths, review-request paths,
and a concise prompt. The user decides whether to paste that prompt into
ChatGPT.

## Runner

- Runner state: `ops/runners/stage3_runner_state.json`
- Stage 3E remains `planned` until Stage 3D is
  `completed_internal_review`.
- Stage 3E must generate `reports/major_reviews/stage3/latest.md`.
- Stage 3E must generate `reports/major_reviews/stage3/latest.json`.
- Stage 3E may notify the user only after the major review package is complete
  or if the task is blocked.

## Scope

- Summarize Stage 3 data source, data quality, backtest validation, and strategy
  evidence.
- Bind the review request to the final Stage 3 review target commit.
- Update `reports/codex_handoff/latest.md`.
- Update `reports/codex_handoff/latest.json`.
- Update `reports/review_requests/latest.md`.
- Update `reports/review_requests/latest.json`.
- Create `reports/major_reviews/stage3/latest.md`.
- Create `reports/major_reviews/stage3/latest.json`.
- Include test commands and results.
- Keep the package public-repo safe.

## Safety

- Do not run Computer Use.
- Do not open ChatGPT automatically.
- Do not send ChatGPT prompts automatically.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify the real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not connect broker write interfaces.
- Do not write secrets, tokens, auth values, Feishu credentials, provider keys,
  or broker credentials.
- Final trading is manually decided by the user.

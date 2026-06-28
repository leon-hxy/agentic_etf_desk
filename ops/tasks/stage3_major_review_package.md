# Stage 3E Major Review Package

status: completed_internal_review
stage: Stage 3E major_review_package_ready
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

Stage 3E prepares major-stage ChatGPT review materials only. Codex did not
request ChatGPT review, did not open ChatGPT, and did not send prompts.
Do not request manual ChatGPT review until after the Stage 3E package is
complete.

Feishu notification is represented by repo-only notification preview only. The
Feishu notification asks the user whether to request ChatGPT review. The user
decides whether to paste the prompt into ChatGPT.

## Runner

- Runner state: `ops/runners/stage3_runner_state.json`
- Stage 3E is `completed_internal_review`.
- Stage 3E generated `reports/major_reviews/stage3/latest.md`.
- Stage 3E generated `reports/major_reviews/stage3/latest.json`.
- Stage 3E internal review artifacts: `reports/internal_reviews/stage3/stage3e_major_review_package.md` and `reports/internal_reviews/stage3/stage3e_major_review_package.json`.
- Stage 3E completion sets the runner to `major_stage_ready` and notifies the
  user to request manual ChatGPT major-stage review if desired.

## Scope

- Summarize Stage 3 data source, data quality, backtest validation, and strategy
  evidence.
- Bind the review request to the Stage 3 review target commit.
- Update `reports/codex_handoff/latest.md`.
- Update `reports/codex_handoff/latest.json`.
- Update `reports/review_requests/latest.md`.
- Update `reports/review_requests/latest.json`.
- Create `reports/major_reviews/stage3/latest.md`.
- Create `reports/major_reviews/stage3/latest.json`.
- Include test commands and results.
- Keep the package public-repo safe.

## Result

- Major review package: `reports/major_reviews/stage3/latest.md`
- Major review package JSON: `reports/major_reviews/stage3/latest.json`
- Manual ChatGPT review prompt: `reports/review_requests/chatgpt_review_prompt.md`
- Internal review: `reports/internal_reviews/stage3/stage3e_major_review_package.md`
- Runner status: `major_stage_ready`

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

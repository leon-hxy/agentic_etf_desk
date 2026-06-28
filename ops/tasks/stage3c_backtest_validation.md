# Stage 3C Backtest Validation

status: completed_internal_review
stage: Stage 3C
branch: stage/stage3-data-backtest
review_level: small_stage
depends_on: Stage 3B completed_internal_review
repo-only

## Objective

Replace sample-only reports with formal backtest validation based on the Stage 3
data source and Stage 3B quality checks.

## Review

Small-stage review: Codex self-review.

Do not request ChatGPT review for this small stage.

Major-stage review: manual ChatGPT review only after the Stage 3E package is
complete.

## Runner

- Runner state: `ops/runners/stage3_runner_state.json`
- Current runner status after execution: `completed_internal_review`
- Internal review artifacts must be written to
  `reports/internal_reviews/stage3/stage3c_backtest_validation.md` and
  `reports/internal_reviews/stage3/stage3c_backtest_validation.json`.
- Completion requires reviewer passes, rerun tests, task status update, runner
  state update, commit, and push.
- Do not execute Stage 3D from this task unless the runner state explicitly
  allows continuing in the same wake.

## Result

- Formal validation script:
  `scripts/backtest/validate_stage3c_backtest.py`.
- Validation report:
  `reports/backtest_validation/stage3c_backtest_validation_report.md`.
- Validation payload:
  `reports/backtest_validation/stage3c_backtest_validation_report.json`.
- Internal review:
  `reports/internal_reviews/stage3/stage3c_backtest_validation.md`.
- Stage 3D remains planned and is the next runner task.

## Scope

- Define formal backtest validation checks.
- replace sample-only reports with reproducible evidence.
- Compare every strategy result against a benchmark.
- Preserve auditability and rollback through git.
- Do not create Stage 3D strategy evidence summaries in this task.

## Safety

- Do not run Computer Use.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify the real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not connect broker write interfaces.
- Do not write secrets, tokens, auth values, Feishu credentials, provider keys,
  or broker credentials.
- Final trading is manually decided by the user.

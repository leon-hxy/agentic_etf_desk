# Stage 3C Backtest Validation

status: planned
stage: Stage 3C
branch: stage/stage3-data-backtest
review_level: small_stage
repo-only

## Objective

Replace sample-only reports with formal backtest validation based on the Stage 3
data source and Stage 3B quality checks.

## Review

Small-stage review: Codex self-review.

Major-stage review: manual ChatGPT review only after the Stage 3E package is
complete.

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

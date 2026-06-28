# Stage 3B Data Quality Checks

status: planned
stage: Stage 3B
branch: stage/stage3-data-backtest
review_level: small_stage
repo-only

## Objective

Add ETF data quality checks for the approved Stage 3A source plan.

## Review

Small-stage review: Codex self-review.

Major-stage review: manual ChatGPT review only after the Stage 3E package is
complete.

## Scope

- Check missing values.
- Check ETF start dates and data availability windows.
- Check adjusted prices and explain any adjustment assumptions.
- Check abnormal prices and document thresholds.
- Produce repo-only quality evidence that can be audited and rerun.
- Do not start formal backtest validation in this task.

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

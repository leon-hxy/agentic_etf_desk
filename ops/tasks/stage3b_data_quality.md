# Stage 3B Data Quality Checks

status: completed_internal_review
stage: Stage 3B completed_internal_review
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

## Completion Evidence

- Data quality script: `scripts/data/check_data_quality.py`.
- Data quality report: `reports/data_quality/stage3b_data_quality_report.md`.
- Machine-readable report: `reports/data_quality/stage3b_data_quality_report.json`.
- Formal internal review: `reports/internal_reviews/stage3/stage3b_data_quality.md`.
- Codex self-review: `reports/internal_reviews/stage3b_data_quality_codex_self_review.md`.
- Test results: `reports/stage3b_safety_test_results.md`.
- Handoff: `reports/codex_handoff/latest.md`.
- Loop state: `ops/state/loop_state.json`.

## Result

- Missing values are checked after each ETF's first available date.
- ETF start dates and availability windows are recorded per symbol.
- Adjusted prices must be numeric and positive.
- Abnormal one-day adjusted-close moves above the configured threshold are
  flagged.
- Formal backtest validation remains deferred to Stage 3C.
- ChatGPT review was not requested for this small stage.
- No Feishu message was sent for this small stage.
- Internal review status: `completed_internal_review`.

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

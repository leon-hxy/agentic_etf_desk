# Stage 3B Codex Self-review

- Stage: `Stage 3B data quality checks completed`
- Review mode: `codex_self_review`
- Scope: small-stage repo-only data quality checks
- Status: `passed`

Codex self-review completed for this small stage.

## Reviewed Files

- `scripts/data/check_data_quality.py`
- `reports/data_quality/stage3b_data_quality_report.md`
- `reports/data_quality/stage3b_data_quality_report.json`
- `ops/tasks/stage3b_data_quality.md`
- `ops/stages/stage3.yaml`
- `ops/state/loop_state.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `reports/stage3b_safety_test_results.md`
- `reports/stage3b_safety_test_results.json`
- `tests/safety/test_stage3b_data_quality.py`

## Checks

- ETF-only constraints still hold.
- The quality checker rejects symbols outside the universe allowlist.
- Missing values are checked after each ETF's first available date.
- ETF start dates and availability windows are recorded.
- Adjusted prices are required to be numeric and positive.
- Abnormal one-day price moves above the threshold are flagged.
- No formal backtest validation starts in this task.
- No secrets, tokens, auth values, `.env` values, Feishu credentials, provider
  keys, or broker credentials are written.
- No real `~/.hermes`, real `~/.openclaw`, or Feishu gateway change occurred.
- No service restart occurred.
- No dependency installation occurred.
- No Computer Use was run.
- No ChatGPT review requested.
- No Feishu message sent.

Final trading is manually decided by the user.

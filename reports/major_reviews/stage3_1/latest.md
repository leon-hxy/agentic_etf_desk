# Stage 3.1 Major Review Package

- Stage: `Stage 3.1 major review package`
- Status: `major_review_package_ready`
- Review route: `manual_chatgpt_review`
- Public repo: `https://github.com/leon-hxy/agentic_etf_desk`
- Branch: `stage/stage3.1-real-etf-data`
- `review_target_commit`: `4b0ba4f9ee0f1ed6553675a189138b32cbdc5321`
- ChatGPT delivery: manual ChatGPT review only; Codex did not send this to ChatGPT.

## Readiness Checks

- `wp1_internal_review_complete`: `passed`
- `wp2_internal_review_complete`: `passed`
- `wp3_internal_review_complete`: `passed`
- `formal_backtest_validation_passed`: `passed`
- `strategy_evidence_passed`: `passed`
- `major_review_package_public_safe`: `passed`
- `manual_chatgpt_review_ready`: `passed`
- `manual_trading_notice_present`: `passed`

## Work Packages

- WP1 real data ingestion and cache: `completed_internal_review`
- WP2 real data quality and monthly panel: `completed_internal_review`
- WP3 formal backtest and evidence package: `completed_internal_review`

## Review Artifacts

- `wp1_real_data_metadata`: `data/raw/prices_yahoo_chart_metadata.json`
- `wp2_monthly_panel`: `data/processed/stage3_1_monthly_panel.csv`
- `wp2_data_quality_report`: `reports/data_quality/stage3_1_wp2_data_quality_report.json`
- `wp3_backtest_validation_report`: `reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json`
- `wp3_strategy_evidence_report`: `reports/strategy_evidence/stage3_1_wp3_strategy_evidence_report.json`
- `handoff`: `reports/codex_handoff/latest.md`
- `review_request`: `reports/review_requests/latest.md`

## Data Boundary

- Real public ETF historical data used: true.
- Sample data only: false.
- Monthly panel: `data/processed/stage3_1_monthly_panel.csv`
- Backtest validation: `reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json`
- Strategy evidence: `reports/strategy_evidence/stage3_1_wp3_strategy_evidence_report.json`
- Benchmark: `VTI`
- Symbols: `BIL, BND, DBC, EWJ, GLD, IEF, VEA, VNQ, VTI, VWO`

## Risk And Limitations Summary

- Stage 3.1 evidence uses public historical ETF data and remains research only.
- Backtests are sensitive to public data revisions, transaction-cost assumptions, and manual execution timing.
- Every strategy is compared to VTI, but benchmark selection should be reviewed by the user before relying on conclusions.
- No broker connection, automatic trading, order routing, or order placement is included.
- Final trading is manually decided by the user.

## Manual ChatGPT Review Prompt

Manual ChatGPT major-stage review request for Stage 3.1 Real ETF Historical Data MVP. Public GitHub repo: https://github.com/leon-hxy/agentic_etf_desk. Branch: stage/stage3.1-real-etf-data. review_target_commit: 4b0ba4f9ee0f1ed6553675a189138b32cbdc5321. Review package: reports/major_reviews/stage3_1/latest.md and reports/major_reviews/stage3_1/latest.json. Scope: ETF-only real public historical data ingestion, reviewed monthly panel, formal backtest validation, and strategy evidence package. Do not treat this as automatic trading or order placement. Final trading is manually decided by the user. 最终交易由用户手动决定，系统不会自动下单。

## Safety

- No Computer Use.
- No ChatGPT review requested or sent by Codex.
- No real Hermes, OpenClaw, or Feishu gateway modification.
- No dependency installation.
- No broker interface, broker write access, order placement, or automatic trading surface.

Final trading is manually decided by the user.

# Stage 3.1 Major Review Request

- Review target: `Stage 3.1 major review package`
- Review route: `manual_chatgpt_review`
- Manual ChatGPT review ready: `true`
- User notified through Feishu after package: `true`
- ChatGPT review requested by Codex: `false`
- Sent to ChatGPT: `false`
- `review_target_commit`: `35348bc8c38df09562190f3c049142a252cbc85d`

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

WP1 real data ingestion and cache, WP2 real data quality and monthly panel, and WP3 formal backtest and evidence package all used Codex internal review only.

Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.

## Files

- `reports/major_reviews/stage3_1/latest.md`
- `reports/major_reviews/stage3_1/latest.json`
- `reports/internal_reviews/stage3_1/wp3_formal_backtest_and_evidence_package.json`

## Manual Prompt

Manual ChatGPT major-stage review request for Stage 3.1 Real ETF Historical Data MVP. Public GitHub repo: https://github.com/leon-hxy/agentic_etf_desk. Branch: stage/stage3.1-real-etf-data. review_target_commit: 35348bc8c38df09562190f3c049142a252cbc85d. Review package: reports/major_reviews/stage3_1/latest.md and reports/major_reviews/stage3_1/latest.json. Scope: ETF-only real public historical data ingestion, reviewed monthly panel, formal backtest validation, and strategy evidence package. Do not treat this as automatic trading or order placement. Final trading is manually decided by the user. 最终交易由用户手动决定，系统不会自动下单。

Final trading is manually decided by the user.

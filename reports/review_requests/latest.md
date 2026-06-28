# Stage 3.1 WP2 Internal Review Request

- Review target: `Stage 3.1 WP2 real data quality and monthly panel`
- Review route: `codex_internal_review`
- ChatGPT review requested: `false`
- Sent to ChatGPT: `false`
- User notification sent: `false`
- `review_target_commit`: `86b6e608b31d71b96f394a0659246675e87bc39f`

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

- WP1 real data ingestion and cache.
- WP2 real data quality and monthly panel.
- WP3 formal backtest and evidence package.

WP1, WP2, and WP3 use Codex internal review only.

Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.

## Files

- `reports/internal_reviews/stage3_1/wp2_real_data_quality_and_monthly_panel.json`
- `data/processed/stage3_1_monthly_panel.csv`
- `reports/data_quality/stage3_1_wp2_data_quality_report.json`
- `scripts/data/build_stage3_1_monthly_panel.py`
- `tests/safety/test_stage3_1_wp2_real_data_quality.py`

Final trading is manually decided by the user.

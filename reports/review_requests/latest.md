# Stage 3.1 WP1 Internal Review Request

- Review target: `Stage 3.1 WP1 real data ingestion and cache`
- Review route: `codex_internal_review`
- ChatGPT review requested: `false`
- Sent to ChatGPT: `false`
- User notification sent: `false`
- `review_target_commit`: `e5a2a603b4cdb2d8b439f705f84331ad297edb88`

This latest artifact supersedes the older Stage 3 manual ChatGPT review prompt as the current review target.

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

- WP1 real data ingestion and cache.
- WP2 real data quality and monthly panel.
- WP3 formal backtest and evidence package.

WP1, WP2, and WP3 use Codex internal review only.

Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.

## Files

- `reports/internal_reviews/stage3_1/wp1_real_data_ingestion_and_cache.json`
- `data/raw/prices_yahoo_chart_metadata.json`
- `data/cache/yahoo_chart_public/cache_manifest.json`
- `scripts/data/download_prices.py`
- `tests/safety/test_stage3_1_wp1_real_data_ingestion.py`

Final trading is manually decided by the user.

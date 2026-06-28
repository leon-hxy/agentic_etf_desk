# Stage 3.1 Runner Prompt

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

Run only from `stage/stage3.1-real-etf-data`, which must be created from the
latest `main`. Do not base Stage 3.1 work on `stage/stage3-data-backtest`.

## Work Packages

Stage 3.1 has exactly three internal work packages:

1. WP1 real data ingestion and cache.
2. WP2 real data quality and monthly panel.
3. WP3 formal backtest and evidence package.

Do not create user-visible Stage 3.1A, Stage 3.1B, Stage 3.1C, Stage 3.1D,
Stage 3.1E, or Stage 3.1F stages.

## Review Rules

- WP1, WP2, and WP3 use Codex internal review only.
- Do not request ChatGPT review for WP1, WP2, or WP3.
- Do not notify the user for WP1, WP2, or WP3 routine completion.
- Only after WP3 is complete and both `reports/major_reviews/stage3_1/latest.md`
  and `reports/major_reviews/stage3_1/latest.json` exist may Codex notify the
  user through Feishu that the user can request manual ChatGPT major-stage
  review.

## Safety Rules

- Do not run Computer Use.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify the real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not connect brokers.
- Do not add broker write access.
- Do not place orders or add order-placement code.
- Keep version 1 ETF-only.
- Final trading is manually decided by the user.

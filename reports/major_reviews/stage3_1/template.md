# Stage 3.1 Major Review Package Template

## Scope

- Stage: `Stage 3.1 Real ETF Historical Data MVP`
- Review route: `manual_chatgpt_review`
- Trigger: after WP3 completes.
- Required package path: `reports/major_reviews/stage3_1/latest.md`
- Required package JSON: `reports/major_reviews/stage3_1/latest.json`

## Work Package Evidence

- WP1 real data ingestion and cache internal review.
- WP2 real data quality and monthly panel internal review.
- WP3 formal backtest and evidence package internal review.

## Required Boundaries

- WP1, WP2, and WP3 are Codex internal review only.
- Do not request ChatGPT review before WP3 completion.
- Do not notify the user before the WP3 major package exists.
- Do not treat any output as an automatic trading instruction.
- Final trading is manually decided by the user.

## Required Safety Statements

- ETF-only scope.
- No broker write access.
- No order placement.
- No automatic trading.
- No secrets in reports.
- No real Hermes/OpenClaw/Feishu gateway change without explicit user approval.

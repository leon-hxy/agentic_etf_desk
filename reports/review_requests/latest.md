# Stage 3.1 Scope Consolidation

- Stage: `Stage 3.1 Real ETF Historical Data MVP scope consolidated`
- Review level: `scope_consolidation`
- Review mode: `codex_internal_governance_update`
- ChatGPT review requested: `false`
- Sent to ChatGPT: `false`
- Computer Use executed: `false`
- Historical Stage 3 package `review_target_commit`: `9c8ad5841bf30585575b78511e30e21b661f5774`

## Scope Decision

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

Do not expose Stage 3.1A, Stage 3.1B, Stage 3.1C, Stage 3.1D, Stage 3.1E, or
Stage 3.1F as user-visible stages.

## Internal Work Packages

- WP1 real data ingestion and cache.
- WP2 real data quality and monthly panel.
- WP3 formal backtest and evidence package.

WP1, WP2, and WP3 are Codex internal review only. They do not request ChatGPT
review and do not notify the user.

## Major Review Gate

Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md`
and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user
through Feishu that the user can request manual ChatGPT major-stage review.

## Next Work

- Next work package: `WP1 real data ingestion and cache`
- WP1 business code started: `false`
- Construction branch: `stage/stage3.1-real-etf-data`

## Safety

- No real `~/.hermes` modification.
- No real `~/.openclaw` modification.
- No Feishu gateway modification.
- No service restart.
- No dependency installation.
- No Computer Use.
- No broker integration.
- No order placement or automatic trading code.

Final trading is manually decided by the user.

## Verification

- `python3 -m unittest`: pass.
- `python3 scripts/safety/check_forbidden_surfaces.py`: pass.
- `python3 scripts/safety/check_secret_leaks.py`: pass.
- `python3 scripts/safety/check_public_repo_hygiene.py`: pass.
- `python3 scripts/safety/check_universe_only.py`: pass.
- `git diff --check`: pass.

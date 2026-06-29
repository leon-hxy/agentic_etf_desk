# Stage 6 WP1 Schedule Dry-Runs

This repo-only schedule dry-run plan validates the intended ETF research desk schedule without changing real Hermes, OpenClaw, Feishu, launchd, or cron configuration.

Final trading is manually decided by the user.

## Dry-Run Events

| Event | Cadence | Mode | Repo-only validation command | Live send attempted |
|---|---|---|---|---:|
| daily_market_brief | weekday_before_market_open | dry_run | `python3 scripts/reports/generate_market_brief.py` | false |
| weekly_report | weekly_after_market_close | dry_run | `python3 scripts/reports/generate_weekly_report.py` | false |
| monthly_rebalance_research_ticket | monthly_after_month_end | dry_run | `python3 scripts/reports/generate_stage5_wp5_rebalance_research_ticket.py` | false |
| universe_health_check | daily_after_data_refresh | dry_run | `python3 scripts/data/validate_universe.py` | false |
| backtest_command | monthly_research_validation | dry_run | `python3 scripts/backtest/run_backtest.py --strategy static_6040` | false |

## Safety Result

- repo-only: true.
- live send attempted: false.
- real runtime modified: false.
- service restart required: false.
- broker write surface: false.
- automatic trading surface: false.
- order placement surface: false.
- trade ticket generated: false.
- benchmark comparison required: true.
- risk_agent review: passed; no actionable trade suggestion generated.

## Next Safe Action

Proceed to `Stage 6 WP2 error recovery`.

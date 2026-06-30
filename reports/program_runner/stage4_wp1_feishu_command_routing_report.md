# Stage 4 WP1 Feishu Command Routing Report

## Summary

Stage 4 WP1 added a repo-only Feishu command router at `scripts/hermes/feishu_command_router.py`.

The router returns deterministic JSON route plans and mobile-readable Feishu reply previews for approved ETF research commands. It does not send live Feishu messages, does not modify real `~/.hermes`, does not modify real Feishu gateway config, does not restart services, does not connect broker interfaces, and does not place orders.

Final trading is manually decided by the user.

## Supported Routes

| User text | Command id | Repo-only entrypoint |
|---|---|---|
| 今天 ETF 有什么信号？ | `market_brief` | `scripts/reports/generate_market_brief.py` |
| 跑一下 GTAA 回测 | `gtaa_backtest` | `scripts/backtest/run_backtest.py --strategies gtaa_10m_sma` |
| 生成本月 ETF 再平衡建议 | `monthly_rebalance_research_ticket` | `scripts/reports/generate_rebalance_ticket.py` |
| 检查 ETF universe 有没有异常 | `universe_health_check` | `scripts/data/validate_universe.py` |
| 生成周报 | `weekly_report` | `scripts/reports/generate_weekly_report.py` |

## Rejection Rules

The router rejects unknown commands and any request involving automatic orders, broker access, individual stocks, options, futures, crypto assets, leveraged ETFs, inverse ETFs, or real runtime configuration changes. Rejected routes expose no repo entrypoint.

## Review

- Reviewer mode: `simulated_separate_pass`
- risk_agent review: passed for repo-only route planning.
- Trade-ticket outputs require risk_agent review before actionable suggestions.
- Automatic trading surface: false.
- Broker write surface: false.
- Live runtime modification: false.

## Next Safe Action

Proceed to `Stage 4 WP2 market brief command output`.

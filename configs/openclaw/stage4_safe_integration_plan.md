# Stage 4 WP7 OpenClaw Safe Integration Plan

This is a repo-only OpenClaw integration plan for the ETF research desk. It is not applied to real OpenClaw configuration.

Final trading is manually decided by the user. 最终交易由用户手动决定。

## Boundaries

- ETF-only version 1.
- No execution agent.
- No order placement.
- No broker write access.
- No automatic trading.
- Do not modify real `~/.openclaw` without explicit user approval.
- Do not restart OpenClaw without explicit user approval.

## Agents

- `market_data_agent`: Validate ETF universe and processed price panels. Broker access `write_forbidden`; order placement `forbidden`.
- `etf_research_agent`: Summarize allowed ETF research context from repo data. Broker access `write_forbidden`; order placement `forbidden`.
- `etf_strategy_agent`: Prepare ETF-only strategy template inputs and assumptions. Broker access `write_forbidden`; order placement `forbidden`.
- `backtest_agent`: Run repo-only backtests and write local reports. Broker access `write_forbidden`; order placement `forbidden`.
- `risk_agent`: Review risk limits before any recommendation ticket is shown. Broker access `write_forbidden`; order placement `forbidden`.
- `trade_ticket_agent`: Draft manual trade recommendation tickets after risk review. Broker access `write_forbidden`; order placement `forbidden`.
- `portfolio_journal_agent`: Record repo-only portfolio research journal entries. Broker access `write_forbidden`; order placement `forbidden`.
- `report_agent`: Generate Feishu-readable summaries and local report files. Broker access `write_forbidden`; order placement `forbidden`.

## Approval Required Before

- Modify real `~/.openclaw`.
- Restart OpenClaw.
- Send live Feishu gateway configuration changes.

## Next Safe Action

Proceed to `Stage 5 WP1 manual holdings CSV import`.

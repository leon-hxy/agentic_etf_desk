# Architecture

## Purpose

Agentic ETF Desk is an ETF-only investment research system. It is not a trading execution system.

## User Interface

Hermes is the only general assistant and the only daily conversational entry point. The user talks to Hermes through Feishu.

## Future Agent Coordination

OpenClaw may later coordinate specialist agents for:

- ETF universe research.
- Data ingestion and validation.
- Strategy research.
- Backtesting.
- Risk review.
- Report generation.
- Manual trade recommendation ticket generation.

The system must not include execution agents, order agents, broker agents, auto traders, live traders, broker write permissions, or order-placement calls.

## Data Flow

1. User asks Hermes a research or portfolio question in Feishu.
2. Hermes routes eligible ETF research work to the local Agentic ETF Desk flow.
3. OpenClaw may coordinate specialist research tasks after explicit implementation approval.
4. The system produces research artifacts, backtests, risk notes, reports, or manual trade recommendation tickets.
5. The user manually decides whether to trade.

## Strategy Rules

Every strategy must:

- Use ETF-only inputs.
- Exclude stocks, options, futures, crypto assets, leveraged ETFs, and inverse ETFs unless explicitly allowlisted later.
- Compare performance against a benchmark.
- Produce auditable assumptions and data provenance.
- Pass risk review before any trade recommendation ticket is presented.


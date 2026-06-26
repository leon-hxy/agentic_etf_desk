# Agentic ETF Desk

Agentic ETF Desk is an ETF-only investment research workspace. The system is intended to support research, data preparation, strategy templates, backtests, risk review, reports, and manual trade recommendation tickets.

Hermes remains the single user-facing assistant through Feishu. OpenClaw may later coordinate specialist agents for research, data, strategy, backtesting, risk, reporting, and recommendation ticket generation.

This project never places orders, never connects to broker write APIs, and never performs automatic trading. Final trading decisions and execution remain manual.

## Version 1 Scope

- Allowed asset class: ETFs only.
- Not allowed: individual stocks, options, futures, crypto assets, leveraged ETFs, inverse ETFs.
- Output types: research, backtests, risk review, reports, and trade recommendation tickets.
- Required ticket disclaimer: research advice only, not automatic order placement, final trading is manual.

## Phase 1 Status

Phase 1 initializes the repository structure, project rules, implementation plan, and a read-only current-state audit. It does not modify Hermes, OpenClaw, Feishu, broker systems, or machine services.


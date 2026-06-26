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

## Codex Handoff Protocol

Every completed Codex work round must update the repo handoff artifacts before the final user response:

- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`

The handoff must record the current stage, latest relevant commit, changed files, verification commands and results, runtime/config safety status, next recommended stage, required user approvals, and forbidden follow-up actions. The handoff update must be committed and pushed to GitHub so the user does not need to copy long Codex summaries out of chat.

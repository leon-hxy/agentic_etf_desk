# Agent Operating Rules

This project is an ETF-only investment research system. It is designed to produce research, backtests, risk reviews, reports, and manual trade recommendation tickets only.

## Hard Safety Boundaries

- ETF-only for version 1.
- No individual stocks, options, futures, crypto assets, leveraged ETFs, or inverse ETFs unless a future explicit allowlist is added.
- No execution agent.
- No order placement.
- No broker write access.
- No automatic trading.
- Do not create agents for execution, order routing, broker access, automatic trading, or live trading.
- Do not call or implement order-writing APIs or equivalent broker execution methods.
- Final trading is always manual and must be decided by the user.

## Output Rules

- All reports must say final trading is manual.
- Every trade ticket must state: this is research advice, not automatic order placement, and final trading is manually decided by the user.
- All strategies must compare against a benchmark.
- All trade tickets must pass `risk_agent` review before being shown as actionable suggestions.
- Outputs may include only research, backtests, risk review, reports, and trade recommendation tickets.

## Secrets And Logs

- No secrets in logs.
- No tokens, auth values, `.env` values, Feishu App Secret, provider keys, or broker credentials may be written to logs, reports, tickets, commits, or audit output.
- Audit reports may mention secret key names and file paths only, never secret values.

## Local Runtime Boundaries

- Do not modify real `~/.hermes` or `~/.openclaw` without explicit user confirmation.
- Do not restart Hermes or OpenClaw without explicit user confirmation.
- Do not modify Feishu configuration without explicit user confirmation.
- Do not install dependencies without explaining the necessity and waiting for user approval.
- Do not connect broker write interfaces.

## Verification

- Run safety tests before the final response after any code or policy change.
- All changes must be auditable and rollbackable through git.

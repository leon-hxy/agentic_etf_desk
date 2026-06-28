# Stage 3.1 Work Package Internal Review Template

## Work Package

- Stage: `Stage 3.1 Real ETF Historical Data MVP`
- Work package: `WP1/WP2/WP3`
- Review route: `codex_internal_review`
- ChatGPT review requested: `false`
- User notification sent: `false`

## Required Reviewer Passes

- Security reviewer.
- Domain reviewer.
- Integration reviewer.
- Test reviewer.

## Required Checks

- ETF-only scope preserved.
- No individual stocks, options, futures, crypto assets, leveraged ETFs, or inverse ETFs unless future explicit allowlist is added.
- No broker connection, broker write access, order placement, live trading, or automatic trading surface.
- No secrets, tokens, auth values, `.env` values, Feishu App Secret, or broker credentials in logs, reports, commits, or tickets.
- No real `~/.hermes`, real `~/.openclaw`, or real Feishu gateway modification.
- No service restart, dependency installation, or Computer Use.
- Final trading is manually decided by the user.

## Decision

- Result: `pending`
- Findings: `pending`
- Required follow-up: `pending`

# Security Policy

## Non-Negotiable Boundaries

- No automatic order placement.
- No broker write access.
- No execution agent, order agent, broker agent, auto trader, or live trader.
- No code paths that submit orders or simulate live broker writes as if they were production execution.
- Final trading must be performed manually by the user.

## Asset Scope

Version 1 is ETF-only.

Forbidden unless a future explicit allowlist is added:

- Individual stocks.
- Options.
- Futures.
- Crypto assets.
- Leveraged ETFs.
- Inverse ETFs.

## Secret Handling

Never write these values to logs, reports, tickets, commits, or audit output:

- `.env` values.
- Tokens.
- Auth credentials.
- Provider API keys.
- Feishu App Secret.
- Broker credentials.

Audits may report whether a key exists and where a file is located. Audits must not print values.

## Runtime Safety

Do not modify real `~/.hermes` or `~/.openclaw` without explicit user confirmation.

Do not restart Hermes, restart OpenClaw, modify Feishu configuration, install dependencies, or connect broker write interfaces without explicit user confirmation.

## Required Review

All trade recommendation tickets must pass risk review before delivery. Each ticket must clearly state that it is research advice only, not automatic order placement, and that final trading is manually decided by the user.

## Repo Safety Tests

Stage 2A adds repo-only safety checks for:

- Policy-banned execution surfaces outside documentation.
- Documentation mentions of forbidden examples without a clear forbidden-example label.
- Secret-like strings in `logs/` and `reports/`.
- Non-placeholder sensitive-looking values in `configs/`.
- Data and strategy code that uses symbols without routing through `configs/universe/etf_universe.yaml`.
- Report templates missing the final-manual-trading disclaimer.

Run:

```bash
python3 -m unittest tests.safety.test_safety
```


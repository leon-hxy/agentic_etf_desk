# Internal Codex Self-review Template

review_mode: codex_self_review
scope: small_stage
reviewer: Codex

## Use When

- Repo-only handoff refresh.
- Template or documentation update.
- Narrow safety test update.
- Small bugfix with limited blast radius.

## Required Checks

- ETF-only constraints still hold.
- No individual stocks, options, futures, crypto assets, leveraged ETFs, or
  inverse ETFs are introduced unless explicitly allowlisted later.
- No execution agent, order agent, broker agent, auto trader, or live trader is
  introduced.
- No broker write API or order-placement call is introduced.
- No secrets, tokens, auth values, `.env` values, Feishu credentials, provider
  keys, or broker credentials are written to reports, logs, commits, or prompts.
- No real `~/.hermes`, `~/.openclaw`, or Feishu gateway change occurred unless
  explicitly approved.
- No Computer Use.
- Safety and smoke tests were run.
- `git diff --check` passed.

Final trading is manually decided by the user.

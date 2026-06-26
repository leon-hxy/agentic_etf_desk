# Project Context For ChatGPT

This file is the repo handoff context for a new ChatGPT conversation using the GitHub connector. It is intentionally repo-only and must not be treated as approval to change live Hermes, OpenClaw, Feishu, broker, or secret configuration.

## 1. Project Goal

Agentic ETF Desk is an ETF-only investment research workspace. It exists to produce research, ETF universe validation, sample data artifacts, backtests, risk reviews, reports, and manual trade recommendation tickets.

It is not a trading execution system. It must never place orders, connect broker write APIs, or perform automatic trading. Final trading decisions and execution always remain manual and are made by the user.

## 2. Current Architecture

Current repo architecture is staged and repo-only:

- `AGENTS.md` defines project operating rules and hard safety boundaries.
- `docs/` contains architecture, security policy, implementation plan, runbook, strategy playbook, audit results, hardening notes, and this handoff context.
- `configs/universe/etf_universe.yaml` is the ETF-only allowlist source.
- `scripts/data/` contains repo-only universe loading, validation, sample price generation, and price panel building.
- `scripts/safety/` contains safety scans for forbidden execution surfaces, secret leakage, and ETF-only routing.
- `tests/safety/` and `tests/smoke/` validate safety and data behavior.
- `reports/` contains Stage 2A smoke output, trade ticket template, and Codex handoff artifacts.

## 3. Hermes, Feishu, And OpenClaw Roles

- Hermes is the only general assistant and the only daily user-facing assistant.
- The user normally talks to Hermes through Feishu.
- Feishu is the user interaction channel, not a trading execution surface.
- OpenClaw may later coordinate specialist research-only agents for ETF universe research, data validation, strategy research, backtesting, risk review, reporting, and manual recommendation ticket generation.
- OpenClaw must not be given broker write credentials or execution responsibilities.
- No live Hermes, Feishu, or OpenClaw integration should be changed without explicit user approval.

## 4. ETF-Only Constraint

Version 1 allows ETFs only.

Forbidden unless a future explicit allowlist is added:

- Individual stocks.
- Options.
- Futures.
- Crypto assets.
- Leveraged ETFs.
- Inverse ETFs.
- Any symbol not in `configs/universe/etf_universe.yaml`.

All strategies must read symbols from the approved universe and compare against a benchmark.

## 5. No Automatic Order Placement Constraint

The system may output only:

- Research.
- Backtests.
- Risk reviews.
- Reports.
- Manual trade recommendation tickets.

Forbidden:

- Execution agents.
- Order agents.
- Broker agents.
- Auto-trading agents.
- Live-trading agents.
- Broker write access.
- Order placement calls or equivalents.
- Any code path that places, submits, routes, or executes orders.

Every trade ticket must state that it is research advice only, not automatic order placement, and final trading is manually decided by the user. Every trade ticket must pass risk review before being shown as an actionable suggestion.

## 6. Real Hermes And OpenClaw Modification Rules

Do not modify real `~/.hermes` or `~/.openclaw` without explicit user confirmation.

Do not:

- Restart Hermes.
- Restart OpenClaw.
- Change Feishu configuration.
- Run doctor fix commands.
- Install dependencies.
- Store or write secrets.
- Add broker access.

Read-only inspection may be done only when the user asks for an audit or diagnosis and secrets are never printed.

## 7. Stage 1 Completed Items

Stage 1 initialized the repo and produced a read-only local audit.

Completed:

- Project directory structure.
- `AGENTS.md`.
- `README.md`.
- Core docs under `docs/`.
- `docs/implementation_plan.md`.
- `docs/current_state_audit.md`.
- Local read-only inspection of macOS, Python, Node, npm/pnpm, Docker, Homebrew, Hermes, OpenClaw, gateway status, cron/launchctl/process surfaces, and dangerous trading API terms.

Stage 1 did not modify real Hermes, OpenClaw, Feishu, broker systems, launchd, crontab, services, or secrets.

## 8. Stage 1 Audit Risk

Overall audit risk: high.

Reason:

- No automatic trading or broker write implementation was found.
- Trading automation risk was low.
- However, OpenClaw doctor reported plaintext secret-bearing config field paths in the real OpenClaw config.
- OpenClaw state directory permissions were too open according to doctor output.
- Hermes and OpenClaw gateway runtime ownership showed process/service drift.
- OpenClaw Feishu group allowlist state may silently drop group messages.
- OpenClaw legacy config and cron storage need manual review before any live integration.

No secret values were printed in the audit report.

## 9. Stage 2A Completed Items

Stage 2A created a repo-only ETF universe, sample data pipeline, smoke report, and safety test foundation.

Completed:

- ETF-only allowlist at `configs/universe/etf_universe.yaml`.
- Universe loader and validator.
- Repo-only sample price generation.
- Adjusted-close price panel builder.
- Stage 2A smoke report writer.
- Trade ticket template with manual-trading disclaimer.
- Safety scripts for forbidden execution surfaces, secret leakage, and universe-only routing.
- Unit and smoke tests for safety and data behavior.
- Reproducible generated metadata behavior.
- Codex handoff protocol under `reports/codex_handoff/`.

## 10. Important Files Already Created

Read these files first when taking over:

- `AGENTS.md`
- `README.md`
- `docs/architecture.md`
- `docs/security_policy.md`
- `docs/implementation_plan.md`
- `docs/current_state_audit.md`
- `docs/stage2b_plan.md`
- `docs/project_context_for_chatgpt.md`
- `configs/universe/etf_universe.yaml`
- `scripts/data/load_universe.py`
- `scripts/data/validate_universe.py`
- `scripts/data/download_prices.py`
- `scripts/data/build_price_panel.py`
- `scripts/safety/check_forbidden_surfaces.py`
- `scripts/safety/check_secret_leaks.py`
- `scripts/safety/check_universe_only.py`
- `tests/safety/test_safety.py`
- `tests/smoke/test_universe_and_data.py`
- `reports/trade_ticket_template.md`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`

## 11. Tests That Have Passed

Known passing checks:

- `python3 -m unittest tests.safety.test_safety tests.smoke.test_universe_and_data`
- `git diff --check`
- `git status --short --untracked-files=all`

The unittest suite covers:

- Forbidden execution surface scan.
- Secret leakage scan.
- Universe-only scan.
- Manual-trading disclaimer in ticket template.
- Universe validation.
- Sample data pipeline and price panel generation.
- Rejection of non-universe symbol input such as `AAPL`.
- Smoke report generation with manual-trading disclaimer.

## 12. Still Forbidden Operations

Still forbidden:

- Modifying real `~/.hermes`.
- Modifying real `~/.openclaw`.
- Restarting Hermes or OpenClaw.
- Changing Feishu configuration.
- Installing dependencies without prior user approval.
- Writing secrets, tokens, auth values, provider keys, Feishu App Secret, `.env` values, or broker credentials into repo files, logs, reports, tickets, commits, or audit output.
- Adding broker write access.
- Adding automatic order placement.
- Creating execution, order, broker, auto-trading, or live-trading agents.
- Expanding beyond ETF-only scope without an explicit future allowlist.

## 13. Stage 2B Recommended Scope

Recommended Stage 2B scope is repo-only:

- Add transparent ETF strategy templates.
- Add a local backtest engine.
- Add benchmark comparison scaffolding.
- Add risk summary outputs.
- Add report and manual recommendation ticket templates.
- Add suggested Hermes/OpenClaw config templates only under `configs/`, not real home directories.
- Expand safety tests for benchmark comparison, risk review gates, and manual-ticket disclaimers.

Stage 2B should not modify live Hermes/OpenClaw/Feishu settings. It should not install dependencies unless the user approves first.

## 14. Priority Files For The Next ChatGPT Conversation

The next ChatGPT conversation should read in this order:

1. `AGENTS.md`
2. `docs/project_context_for_chatgpt.md`
3. `reports/codex_handoff/latest.md`
4. `reports/codex_handoff/latest.json`
5. `docs/implementation_plan.md`
6. `docs/stage2b_plan.md`
7. `docs/current_state_audit.md`
8. `configs/universe/etf_universe.yaml`
9. `tests/safety/test_safety.py`
10. `tests/smoke/test_universe_and_data.py`

## 15. New Conversation Startup Prompt

Use this prompt in a new ChatGPT conversation:

```text
You are taking over the GitHub repo leon-hxy/agentic_etf_desk through the GitHub connector.

First read:
- AGENTS.md
- docs/project_context_for_chatgpt.md
- reports/codex_handoff/latest.md
- reports/codex_handoff/latest.json
- docs/implementation_plan.md
- docs/stage2b_plan.md
- docs/current_state_audit.md

Important constraints:
- This is an ETF-only investment research system.
- Do not create automatic trading, execution, order, broker, auto-trader, or live-trader code.
- Do not add broker write access or order placement APIs.
- Do not modify real ~/.hermes or ~/.openclaw.
- Do not restart Hermes or OpenClaw.
- Do not install dependencies without explaining why and getting user approval.
- Do not write secrets into logs, reports, commits, or tickets.
- Final trading is always manual and decided by the user.

Continue only with repo-only work unless the user explicitly approves live integration changes.
After each work round, update reports/codex_handoff/latest.md and latest.json, run safety tests, commit, and push.
```

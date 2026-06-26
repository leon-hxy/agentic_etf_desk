# Current State Audit

Date: 2026-06-26
Scope: public-safe read-only audit summary for Agentic ETF Desk Stage 1
Workspace: `$PROJECT_ROOT`

This document is the sanitized public summary. It intentionally avoids user-specific absolute paths, local usernames, process identifiers, exact service state details, and secret values. Local private audit detail belongs under `local_private/`, which is ignored by git except for its README and `.gitkeep`.

No live Hermes, OpenClaw, Feishu, broker, launchd, crontab, or service configuration was modified during the audit.

## Executive Summary

Overall risk level: **high**

Reason: no automatic trading or broker write implementation was found in the scanned project/config surface, but the local OpenClaw health check reported secret-bearing config field paths and overly broad state-directory permissions. Hermes and OpenClaw gateway ownership also showed runtime drift that needs deliberate operator review before any live integration.

Trading automation risk: **low**

Reason: the scanned repository and related local agent configuration surfaces contained policy-only references to forbidden trading and order terms. No order-placement API implementation, broker write script, automatic trading process, or broker write interface was found in the scanned surface.

## 1. Local Platform Summary

- Platform: macOS on arm64.
- Python: installed.
- Node.js and npm: installed.
- pnpm: not installed at audit time.
- Docker: installed.
- Homebrew: installed.

Exact local versions were recorded only in private audit notes and are not included in this public repo summary.

## 2. Hermes Summary

- Hermes: installed.
- Hermes config home: `$HERMES_HOME`.
- Key files checked read-only:
  - `$HERMES_HOME/config.yaml`
  - `$HERMES_HOME/.env`
  - `$HERMES_HOME/SOUL.md`
  - `$HERMES_HOME/memories`
  - `$HERMES_HOME/skills`
- Hermes doctor: completed with warnings; no automatic fix was run.
- Hermes gateway: local gateway state showed service/process ownership drift; no restart was performed.

Configuration key names were inspected without values. Sensitive-looking key names were mentioned only as key names. No secret, token, auth value, Feishu App Secret, provider key, or broker credential value was printed.

## 3. Hermes Feishu Configuration Summary

Checked key existence only in `$HERMES_HOME/.env`:

- `FEISHU_APP_ID`: present.
- `FEISHU_DOMAIN`: present.
- `FEISHU_CONNECTION_MODE`: present.
- `FEISHU_ALLOWED_USERS`: present.
- `FEISHU_HOME_CHANNEL`: present.
- `FEISHU_GROUP_POLICY`: present.
- `FEISHU_REQUIRE_MENTION`: present.

No Feishu value, token, App Secret, auth value, user ID, channel ID, or allowlist value was printed.

## 4. OpenClaw Summary

- OpenClaw: installed.
- OpenClaw config home: `$OPENCLAW_HOME`.
- Key files and directories checked read-only:
  - `$OPENCLAW_HOME`
  - `$OPENCLAW_HOME/openclaw.json`
  - `$OPENCLAW_HOME/agents`
  - `$OPENCLAW_HOME/skills`
  - `$OPENCLAW_HOME/workspace`
  - `$OPENCLAW_HOME/cron`
  - `$OPENCLAW_HOME/heartbeat`
  - `$OPENCLAW_HOME/gateway`
- OpenClaw doctor: completed with warnings; no automatic fix was run.
- OpenClaw gateway: local gateway was reachable during the audit, but service ownership showed runtime drift; no restart was performed.

Notable OpenClaw warnings:

- Legacy config and cron storage need review.
- Some model/fallback settings need review.
- State-directory permissions were reported as too open.
- Secret-bearing config field paths were reported. Values were not printed.
- Feishu group allowlist policy may need review before live routing.
- Stale or orphaned local state was reported and should be handled only in an approved maintenance phase.

## 5. Cron, Launchd, And Process Summary

Read-only checks were performed for terms related to trading, broker access, execution, order placement, and auto trading.

Results:

- No dangerous trading term matches were found in user crontab entries.
- A system service false positive containing a generic broker-like word was observed and assessed as unrelated to trading.
- No dangerous trading process matches were found after excluding the audit command itself.

No launchd, crontab, service, process, permission, or gateway state was changed.

## 6. Dangerous API And Auto-Trading Surface Search

Scanned surfaces:

- Current repository.
- `$OPENCLAW_HOME/openclaw.json`.
- `$OPENCLAW_HOME/cron`.
- `$HERMES_HOME/config.yaml`.
- `$HERMES_HOME/cron`.

Excluded:

- `.git`.
- `.env` values.
- logs.
- sessions.
- dependency caches.

Search terms included forbidden execution, order, broker, auto-trader, live-trader, order-placement, and broker-write concepts.

Findings:

- Hits in the current repository were policy-only references in project rules and documentation.
- No dangerous order-placement API implementation was found.
- No broker write interface was found.
- No automatic trading implementation was found.

## 7. Risk Rating

Overall risk: **high**

Primary reasons:

- Local OpenClaw config contains secret-bearing field paths according to health-check output.
- Local OpenClaw state-directory permissions were reported as too open.
- Hermes and OpenClaw gateway ownership showed runtime drift.
- OpenClaw Feishu group policy may silently drop group messages.
- Legacy OpenClaw config and cron storage need manual review before live integration.

Offsetting factors:

- No automatic order-placement code was found.
- No broker write interface was found.
- No dangerous trading process or cron entry was found.
- Hermes Feishu configuration key names required by the audit were present.
- No secret values were printed into this report.

## 8. Recommended Next Steps

Before Stage 2B:

1. Keep work repo-only.
2. Do not connect Hermes/OpenClaw routing yet.
3. Do not modify `$HERMES_HOME` or `$OPENCLAW_HOME` until the user explicitly approves a live maintenance phase.
4. Continue expanding safety tests for forbidden APIs, ETF-only universe constraints, benchmark requirements, risk review gates, and manual-trading disclaimers.

Before Hermes/OpenClaw router work:

1. Ask the user for explicit approval to inspect and remediate OpenClaw secret storage and permissions.
2. Ask the user before running any `doctor --fix`.
3. Ask the user before restarting Hermes or OpenClaw.
4. Review OpenClaw Feishu allowlist policy.
5. Resolve gateway ownership drift deliberately, not as part of repo-only strategy/backtest work.

Trading safety:

1. Continue to prohibit execution, order, broker, auto-trading, and live-trading agents.
2. Continue to prohibit order-placement APIs.
3. Keep all tickets as research recommendations only.
4. Require risk review before any ticket is shown as actionable.
5. Require final manual user decision for all trades.

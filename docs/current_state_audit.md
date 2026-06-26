# Current State Audit

Date: 2026-06-26  
Scope: local read-only audit for Agentic ETF Desk phase 1  
Workspace: `/Volumes/macos/leon/Desktop/agentic-etf-desk`

No live Hermes, OpenClaw, Feishu, broker, launchd, crontab, or service configuration was modified.

## Executive Summary

Overall risk level: **high**

Reason: no automatic trading or broker write interface was found in the scanned project/config surface, but `openclaw doctor` reported plaintext secret-bearing config field paths in the real OpenClaw config and OpenClaw state directory permissions that are too open. Gateway service state is also split between a running process and an unloaded launchd job.

Trading automation risk: **low**

Reason: repository and related config scan found only policy documentation references to forbidden trading/order terms. No order-placement API implementation or broker write script was found in the scanned surface.

## 1. macOS And CPU

- macOS: 26.5.1
- Build: 25F80
- CPU architecture: arm64
- CPU brand: Apple M4

## 2. Local Toolchain

- Python: Python 3.14.4
- Node.js: v23.11.0
- npm: 10.9.2
- pnpm: not installed
- Docker CLI: Docker version 29.4.0, build 9d7ad9f
- Docker daemon/server: 29.4.0
- Homebrew: 6.0.2

## 3. Hermes Installation

- `which hermes`: `/Volumes/macos/leon/.local/bin/hermes`
- `hermes --version`: Hermes Agent v0.16.0 (2026.6.5)
- Hermes runtime Python: 3.11.15
- Hermes project path: `/Volumes/macos/leon/.local/share/uv/tools/hermes-agent/lib/python3.11/site-packages`
- Hermes update status reported by CLI: 1 commit behind

### `hermes doctor`

Result: completed with warnings; no automatic fix was run.

Notable findings:

- Security advisories: none active.
- `~/.hermes/.env`: exists.
- API key or custom endpoint: configured.
- `~/.hermes/config.yaml`: exists.
- Config version: up to date, v27.
- `~/.hermes/SOUL.md`: exists.
- `~/.hermes/memories`: exists.
- `~/.hermes/skills`: exists.
- Optional or gated tools missing include Telegram, browser-cdp, computer_use, Discord token, some web search keys, and x_search key.
- Auth providers not logged in include Nous Portal, OpenAI Codex, Google Gemini OAuth, MiniMax OAuth, and xAI OAuth.
- Venv entry point warning: `hermes` not found in venv/bin or .venv/bin.

No secrets were printed into this report.

## 4. Hermes Configuration

Read-only path checks:

- `/Volumes/macos/leon/.hermes/config.yaml`: present
- `/Volumes/macos/leon/.hermes/.env`: present
- `/Volumes/macos/leon/.hermes/SOUL.md`: present
- `/Volumes/macos/leon/.hermes/memories`: present
- `/Volumes/macos/leon/.hermes/skills`: present

Configuration key names were inspected without values. Notable key names present include:

- `_config_version`
- `agent`
- `approvals`
- `cron`
- `dashboard`
- `delegation`
- `feishu`
- `gateway`
- `goals`
- `memory`
- `model`
- `providers`
- `runtime_footer`
- `security`
- `skills`
- `tools`
- `web`

Sensitive-looking key names such as `api_key`, `secret`, `secrets`, `password`, and `password_hash` were present as key names only. Values were not read into the report.

## 5. Hermes Feishu Configuration

Checked in `~/.hermes/.env` for key existence only:

- `FEISHU_APP_ID`: present
- `FEISHU_DOMAIN`: present
- `FEISHU_CONNECTION_MODE`: present
- `FEISHU_ALLOWED_USERS`: present
- `FEISHU_HOME_CHANNEL`: present
- `FEISHU_GROUP_POLICY`: present
- `FEISHU_REQUIRE_MENTION`: present

No Feishu value, token, App Secret, or auth value was printed.

## 6. Hermes Gateway

`hermes gateway status` result:

- Launchd plist: `/Volumes/macos/leon/Library/LaunchAgents/ai.hermes.gateway.plist`
- Service definition matches current Hermes install.
- Gateway service is not loaded.
- A gateway process is running for this profile.
- Running PID reported by Hermes: 1413

Assessment: Hermes gateway appears to be running as a process, but launchd does not own an active loaded service for it. This is a runtime ownership drift risk. No restart was performed.

## 7. OpenClaw Installation

- `which openclaw`: `/opt/homebrew/bin/openclaw`
- `openclaw --version`: OpenClaw 2026.6.6 (8c802aa)

### `openclaw doctor`

Result: completed with warnings; no automatic fix was run.

Notable findings:

- Legacy config keys detected.
- Doctor preview suggests config migrations, but they were not applied.
- Feishu group policy warning: `groupPolicy` is allowlist while relevant allowlist fields are empty, which may silently drop group messages.
- Several agent model objects have no explicit `fallbacks` key.
- Managed npm OpenClaw host peer links need repair.
- State directory permissions are too open for `~/.openclaw`.
- Stale Codex session routing state found.
- Orphan transcript files found under `~/.openclaw/agents/main/sessions`.
- Cron model override detected at `~/.openclaw/cron/jobs.json`.
- Legacy cron job storage detected at `~/.openclaw/cron/jobs.json`.
- Security warning: `openclaw.json` contains plaintext secret-bearing config field paths. Reported field paths include gateway auth token, model provider API keys, and Feishu app secret path names. Values were not printed.
- Fetch timeout observed while checking `https://chatgpt.com/backend-api/codex/models`.
- TaskFlow recovery warnings found for blocked flows pointing at missing tasks.

## 8. OpenClaw Configuration

Read-only path checks:

- `/Volumes/macos/leon/.openclaw`: present
- `/Volumes/macos/leon/.openclaw/openclaw.json`: present
- `/Volumes/macos/leon/.openclaw/agents`: present
- `/Volumes/macos/leon/.openclaw/skills`: absent as a directory
- `/Volumes/macos/leon/.openclaw/workspace`: present
- `/Volumes/macos/leon/.openclaw/cron`: present
- `/Volumes/macos/leon/.openclaw/heartbeat`: absent as a directory
- `/Volumes/macos/leon/.openclaw/gateway`: absent as a directory

Top-level `openclaw.json` key existence:

- `agents`: present
- `skills`: present
- `workspace`: absent
- `cron`: absent
- `heartbeat`: absent
- `gateway`: present

Top-level key names found:

- `agents`
- `auth`
- `bindings`
- `channels`
- `commands`
- `gateway`
- `messages`
- `meta`
- `models`
- `plugins`
- `secrets`
- `session`
- `skills`
- `tools`
- `wizard`

No values were printed.

## 9. OpenClaw Gateway

`openclaw gateway status` result:

- LaunchAgent service: not loaded.
- Service file: `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
- Working directory: `~/.openclaw`
- Config path: `~/.openclaw/openclaw.json`
- Gateway bind: loopback, `127.0.0.1`
- Port: 18789
- Dashboard: `http://127.0.0.1:18789/`
- CLI version: 2026.6.6
- Gateway version: 2026.6.6
- Connectivity probe: ok
- Capability: admin-capable
- Listening: `127.0.0.1:18789`, `[::1]:18789`

Assessment: OpenClaw gateway is locally reachable, but launchd does not have the service loaded. This is a runtime ownership drift risk. No restart was performed.

## 10. Crontab, Launchctl, And Process Checks

Danger terms checked:

- `trading`
- `broker`
- `alpaca`
- `ibkr`
- `order`
- `execution`
- `submit_order`
- `place_order`
- `auto_trade`

Results:

- `crontab -l`: 2 lines present; no dangerous term matches.
- `launchctl list`: one match, `com.apple.SpeechRecognitionCore.brokerd`; assessed as an Apple system service false positive, not a trading broker process.
- `ps`: no dangerous term matches after excluding the audit command itself.

## 11. Dangerous API And Auto-Trading Surface Search

The terms in this section are policy-only forbidden example terms from the read-only audit query, not executable trading code.

Scanned surfaces:

- Current repository.
- `~/.openclaw/openclaw.json`
- `~/.openclaw/cron`
- `~/.hermes/config.yaml`
- `~/.hermes/cron`

Excluded:

- `.git`
- `.env`
- logs
- sessions
- node_modules

Search terms included:

- `execution_agent`
- `order_agent`
- `broker_agent`
- `auto_trader`
- `live_trader`
- `place_order`
- `submit_order`
- `buy_market`
- `sell_market`
- `ib.placeOrder`
- `alpaca.submit_order`
- `auto_trade`
- `automatic trading`
- `automatic order`
- `broker write`
- Chinese equivalents for automatic order/trading and broker write concepts

Findings:

- Hits in the current repository are policy-only references inside `AGENTS.md`, `README.md`, and `docs/`.
- No dangerous order-placement API implementation was found in the scanned repository surface.
- No dangerous order-placement API implementation was found in the scanned Hermes/OpenClaw config surface.

## 12. Risk Rating

Overall risk: **high**

Primary reasons:

- Real OpenClaw config contains plaintext secret-bearing field paths according to `openclaw doctor`.
- OpenClaw state directory permissions are too open according to `openclaw doctor`.
- Hermes and OpenClaw gateway runtime ownership both show process/service drift.
- OpenClaw Feishu group allowlist state may silently drop group messages.
- OpenClaw legacy config and cron storage need manual review before any future integration.

Offsetting factors:

- No automatic order-placement code was found.
- No broker write interface was found.
- No dangerous trading process or cron entry was found.
- Hermes Feishu keys required by the audit are present.

## 13. Recommended Next Steps

Before Phase 2:

1. Keep Phase 2 repo-only: ETF universe schema, data module interfaces, and safety tests only.
2. Do not connect Hermes/OpenClaw routing yet.
3. Do not modify `~/.hermes` or `~/.openclaw` until the user explicitly approves a remediation phase.
4. Add formal safety tests early in Phase 2 or Phase 6 to enforce forbidden APIs, ETF-only universe constraints, benchmark requirements, risk review requirements, and manual-trading disclaimers.

Before Hermes/OpenClaw router work:

1. Ask the user for explicit approval to inspect and remediate OpenClaw secret storage and permissions.
2. Ask the user before running any `doctor --fix`.
3. Ask the user before restarting Hermes or OpenClaw.
4. Review OpenClaw Feishu allowlist policy so group messages do not silently drop.
5. Resolve gateway launchd ownership drift deliberately, not as part of the current phase.

Trading safety:

1. Continue to prohibit execution/order/broker/auto-trader agents.
2. Continue to prohibit order-placement APIs.
3. Keep all tickets as research recommendations only.
4. Require risk review before any ticket is shown as actionable.
5. Require final manual user decision for all trades.

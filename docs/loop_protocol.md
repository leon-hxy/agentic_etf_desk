# Codex Loop Protocol

The loop protocol is a repo-only coordination draft. It does not install automation and does not modify live Hermes, OpenClaw, Feishu, launchd, crontab, broker, or secret configuration.

## Goal

Reduce manual copy/paste between ChatGPT and Codex:

1. The user approves a repo-only task.
2. Codex reads task files under `ops/tasks/`.
3. Codex reads `AGENTS.md` before work.
4. Codex changes only repo files.
5. Codex runs safety and smoke tests.
6. Codex updates `reports/codex_handoff/latest.md` and `latest.json`.
7. Codex updates `reports/review_requests/latest.md` and `latest.json`.
8. Codex commits and pushes.
9. The user asks ChatGPT to review the latest repo handoff.

## Stage 2A.6 Review Loop Draft

The expanded review loop remains repo-only and draft-only:

1. Codex task runner completes a repo task.
2. Codex updates `reports/codex_handoff/latest.md` and `latest.json`.
3. Codex updates `reports/review_requests/latest.md` and `latest.json`.
4. A future Hermes notification watcher detects the new review request.
5. Hermes sends the user a Feishu notification: `Codex 已完成任务，测试结果为 X，是否审核？`
6. The user replies with one of:
   - `确认审核`
   - `暂不审核`
   - `只看状态`
   - `开始下一阶段`
   - `暂停 loop`
7. If the user replies `确认审核`, a future approved Hermes skill writes `local_private/review_gate.json`.
8. Codex ChatGPT Review Relay automation reads the gate file.
9. If the gate is valid and not expired, Codex may use Computer Use or Chrome to open ChatGPT and paste the generated public review prompt.
10. If Computer Use fails, Hermes sends the user the one-line manual fallback prompt from `reports/review_requests/manual_fallback_prompt.md`.

The current ChatGPT conversation cannot be awakened directly by an external API. Computer Use is a UI relay, not an API integration.

The relay is best-effort. It depends on the local Chrome/ChatGPT login state and Codex Computer Use permissions. All real review evidence remains the public GitHub repo, the review request files, and the handoff files.

## Hard Boundaries

- No automatic trading.
- No broker write access.
- No order placement.
- No execution, order, broker, auto-trading, or live-trading agents.
- No modification to real `~/.hermes`.
- No modification to real `~/.openclaw`.
- No service restarts.
- No dependency installation unless the user explicitly approves.
- No secret, token, auth value, provider key, Feishu App Secret value, or broker credential in repo files.
- The relay must not execute trades.
- The relay must not modify real Hermes/OpenClaw configuration.
- The relay must not connect broker systems.
- The relay must send only public GitHub URLs, public repo-relative paths, commit SHAs, and review request/handoff paths to ChatGPT.

## Live Integration Boundary

Real Hermes/OpenClaw integration remains a future step requiring explicit user approval. Stage 2B should stay repo-only unless the user approves a separate live integration or remediation task.

## Review Gate Rules

`local_private/review_gate.json` is the only local approval gate for the ChatGPT UI relay. It is ignored by git and must not be committed.

The gate must:

- Be one-time use.
- Have `expires_at`.
- Bind to the exact commit SHA in `reports/review_requests/latest.json`.
- Set `approved` to true.
- Set `approved_action` to `chatgpt_review_relay`.
- Match repo `leon-hxy/agentic_etf_desk`.
- Have `used` set to false.

If any gate validation fails, Codex relay must not send a prompt to ChatGPT.

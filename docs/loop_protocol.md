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
7. Stage 2F deprecates ChatGPT Computer Use automatic review.
8. Small stages use Codex self-review recorded in the repo.
9. Major stages generate a manual ChatGPT review prompt.
10. The user decides whether to paste the major-stage prompt into ChatGPT.

The current ChatGPT conversation cannot be awakened directly by an external API. Computer Use is no longer part of the active review governance loop.

All real review evidence remains the public GitHub repo, the review request files, and the handoff files.

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
- The review loop must not execute trades.
- The review loop must not modify real Hermes/OpenClaw configuration.
- The review loop must not connect broker systems.
- Major-stage ChatGPT prompts must use only public GitHub URLs, public repo-relative paths, commit SHAs, and review request/handoff paths.

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

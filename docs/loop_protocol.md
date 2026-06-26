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

## Live Integration Boundary

Real Hermes/OpenClaw integration remains a future step requiring explicit user approval. Stage 2B should stay repo-only unless the user approves a separate live integration or remediation task.

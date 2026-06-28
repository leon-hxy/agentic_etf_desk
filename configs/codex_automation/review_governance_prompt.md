# Review Governance Automation Draft

This is a repo-only Codex automation draft. It is not installed and must not
run live automation without future explicit user approval.

ChatGPT Computer Use automatic review route is deprecated.

## Behavior

1. Read `reports/review_requests/latest.json`.
2. Read `reports/codex_handoff/latest.json`.
3. Determine review level:
   - Small-stage Codex self-review for narrow repo-only work.
   - Major-stage ChatGPT review for phase transitions, live integration plans,
     security model changes, or broad behavior changes.
4. For small stages, run Codex self-review using
   `ops/templates/internal_codex_self_review_template.md`.
5. For major stages, prepare a manual ChatGPT review prompt using
   `ops/templates/major_chatgpt_review_template.md`.
6. Do not run Computer Use.
7. Do not open ChatGPT automatically.
8. Do not send ChatGPT prompts automatically.

## Required Safety

- Use only public GitHub URL, commit SHA, and repo-relative paths in any major
  review prompt.
- Do not read or send local secrets, tokens, auth values, Feishu credentials,
  Hermes private config, OpenClaw private config, provider keys, or broker
  credentials.
- Do not access broker, email, GitHub admin, or Feishu admin pages.
- Do not create execution, order, broker, auto-trading, or live-trading agents.
- Final trading is manually decided by the user.

Small-stage Codex self-review and Major-stage ChatGPT review are the only active
review governance modes.

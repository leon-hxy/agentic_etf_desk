# Major ChatGPT Review Template

review_mode: major_chatgpt_review
scope: major_stage
reviewer: ChatGPT, user-initiated

Use this template only for manual ChatGPT review. Codex prepares public review
materials, and the user decides whether to paste them into ChatGPT.

## Prompt Shape

Please review the public GitHub URL:

`https://github.com/leon-hxy/agentic_etf_desk`

Please review `review_target_commit`:

`<commit-sha>`

Please read these repo-relative paths:

- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`

Check ETF-only constraints, no automatic order placement, no broker write
surface, no secrets leakage, no unauthorized live Hermes/OpenClaw/Feishu
gateway changes, and whether the listed tests are sufficient.

Output pass/fail, high-risk issues, required fixes, and suggested next step.

Final trading is manually decided by the user.

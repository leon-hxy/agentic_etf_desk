# Review Governance Task Template

stage: <stage-name>
review_level: small_stage | major_stage
review_mode: codex_self_review | major_chatgpt_review
status: planned

## Required artifacts

- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`

## Review selection

- `small_stage`: Codex self-review is required before commit/push.
- `major_stage`: Codex prepares public major ChatGPT review materials; user
  initiates ChatGPT review manually.

## forbidden_actions

- Do not run Computer Use.
- Do not open ChatGPT automatically.
- Do not send ChatGPT prompts automatically.
- Do not modify real `~/.hermes` or `~/.openclaw` unless explicitly approved.
- Do not modify a real Feishu gateway unless explicitly approved.
- Do not restart services.
- Do not install dependencies.
- Do not write secrets.
- Do not create broker write access or automatic order placement code.

Final trading is manually decided by the user.

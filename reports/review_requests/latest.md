# Review Request

## Current Stage

Stage 2F review governance refactor completed.

## Loop State Stage

Stage 2F review governance refactor completed.

## Review Governance

- Review level: `small_stage`
- Small-stage route: `Codex self-review`
- Major-stage route: `manual ChatGPT review`
- ChatGPT Computer Use automatic review route is deprecated: `true`

## Review Target Commit

`2006d60f237a9b47f34236fd7dd299e9bbdb4f86`

Please review this `review_target_commit` for Stage 2F if a manual major-stage ChatGPT review is requested by the user.

## Current Repo Head

`2006d60f237a9b47f34236fd7dd299e9bbdb4f86`

## Handoff Commit

`null`

The handoff update is committed after generation, so it cannot self-reference its own final SHA in the same commit.

## Files For Review

- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `docs/review_governance.md`
- `ops/tasks/stage2f_review_governance.md`
- `ops/templates/internal_codex_self_review_template.md`
- `ops/templates/major_chatgpt_review_template.md`
- `ops/templates/review_governance_task_template.md`
- `configs/codex_automation/review_governance_prompt.md`
- `configs/codex_automation/chatgpt_review_relay_prompt.md`
- `ops/notifications/feishu_message_templates.md`
- `reports/review_requests/chatgpt_review_prompt.md`
- `reports/review_requests/chatgpt_review_prompt.json`
- `reports/review_requests/relay_status.md`
- `reports/review_requests/relay_status.json`
- `ops/state/loop_state.json`
- `scripts/review_relay/relay_common.py`
- `tests/safety/test_stage2f_review_governance.py`
- `tests/safety/test_review_relay_safety.py`
- `tests/safety/test_handoff_commit_consistency.py`
- `tests/safety/test_loop_state_consistency.py`
- `tests/safety/test_notification_loop_safety.py`

## Test Result Summary

- `python3 -m unittest tests.safety.test_stage2f_review_governance tests.safety.test_review_relay_safety`: passed; Stage 2F governance and review safety tests.
- `python3 scripts/safety/check_review_relay_safety.py`: passed; no review governance safety findings.
- `python3 scripts/safety/check_public_repo_hygiene.py`: passed; no local path or secret findings.
- `python3 scripts/safety/check_handoff_commit_consistency.py`: passed; review_target_commit binds to Stage 2F business commit.
- `python3 -m unittest tests.safety.test_safety tests.safety.test_public_repo_hygiene tests.safety.test_notification_loop_safety tests.safety.test_review_relay_safety tests.safety.test_handoff_commit_consistency tests.safety.test_strategy_templates_safety tests.safety.test_backtest_safety tests.safety.test_openclaw_agents_safety tests.safety.test_hermes_router_safety tests.safety.test_loop_state_consistency tests.safety.test_loop_automation_dry_run tests.safety.test_stage2d_preparation_plan tests.safety.test_stage2d1_live_preflight tests.safety.test_stage2d2a_live_install tests.safety.test_stage2d2b_live_smoke tests.safety.test_stage2e0_relay_smoke tests.safety.test_stage2e1_relay_hardening tests.safety.test_stage2f_review_governance tests.smoke.test_universe_and_data tests.smoke.test_backtest_smoke tests.smoke.test_reports_smoke`: passed; 91 tests OK.
- `git diff --check`: passed; no whitespace errors.

## Risk Statement

Stage 2F is repo-only review governance refactor. It deprecates the ChatGPT Computer Use automatic review route and replaces it with small-stage Codex self-review plus manual, user-initiated major-stage ChatGPT review. It does not run Computer Use, does not send ChatGPT prompts, does not modify real Hermes/OpenClaw/Feishu gateway, does not restart services, does not install dependencies, does not touch secrets, and adds no broker or auto-trading surface.

Final trading is manually decided by the user.

## Manual Major-stage ChatGPT Prompt

Manual major-stage ChatGPT review only: review public GitHub repo https://github.com/leon-hxy/agentic_etf_desk at review_target_commit 2006d60f237a9b47f34236fd7dd299e9bbdb4f86; read reports/review_requests/latest.md, reports/review_requests/latest.json, reports/codex_handoff/latest.md, reports/codex_handoff/latest.json.

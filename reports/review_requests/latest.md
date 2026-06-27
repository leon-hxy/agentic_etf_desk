# Review Request

## Current Stage

Stage 2E.1 ChatGPT relay target and input delivery hardened.

## Loop State Stage

Stage 2E.1 ChatGPT relay target and input delivery hardened.

## Review Target Commit

`23cebebed1d07f0b35e66b284ec0891b427d8716`

Please review this `review_target_commit` for Stage 2E.1.

## Current Repo Head

`23cebebed1d07f0b35e66b284ec0891b427d8716`

## Handoff Commit

`null`

The handoff update is committed after generation, so it cannot self-reference its own final SHA in the same commit.

## Target Conversation Modes

- Recommended: `dedicated_review_thread`
- Supported: `dedicated_review_thread`, `existing_conversation_url`
- Existing conversation URL source: `local_private/chatgpt_review_target.json`
- Existing conversation URL values must not be committed or written to public artifacts.

## Files For ChatGPT To Review

- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `reports/review_requests/chatgpt_review_prompt.md`
- `reports/review_requests/chatgpt_review_prompt.json`
- `reports/review_requests/manual_fallback_prompt.md`
- `reports/review_requests/relay_status.md`
- `reports/review_requests/relay_status.json`
- `reports/review_requests/notification_preview.md`
- `reports/review_requests/notification_preview.json`
- `reports/relay_smoke/stage2e1_relay_hardening_report.md`
- `reports/relay_smoke/stage2e1_relay_hardening_report.json`
- `ops/state/loop_state.json`
- `scripts/review_relay/relay_common.py`
- `scripts/review_relay/build_chatgpt_review_prompt.py`
- `scripts/review_relay/render_manual_fallback_prompt.py`
- `scripts/review_relay/render_notification_preview.py`
- `scripts/safety/check_review_relay_safety.py`
- `scripts/safety/check_handoff_commit_consistency.py`
- `tests/safety/test_stage2e1_relay_hardening.py`
- `tests/safety/test_review_relay_safety.py`
- `tests/safety/test_handoff_commit_consistency.py`
- `tests/safety/test_loop_state_consistency.py`
- `tests/safety/test_notification_loop_safety.py`

## Test Result Summary

- `python3 -m unittest tests.safety.test_stage2e1_relay_hardening tests.safety.test_review_relay_safety`: pending final verification.
- `python3 scripts/safety/check_review_relay_safety.py`: pending final verification.
- `python3 scripts/safety/check_public_repo_hygiene.py`: pending final verification.
- `python3 scripts/safety/check_handoff_commit_consistency.py`: pending final verification.
- `python3 -m unittest tests.safety.test_safety tests.safety.test_public_repo_hygiene tests.safety.test_notification_loop_safety tests.safety.test_review_relay_safety tests.safety.test_handoff_commit_consistency tests.safety.test_strategy_templates_safety tests.safety.test_backtest_safety tests.safety.test_openclaw_agents_safety tests.safety.test_hermes_router_safety tests.safety.test_loop_state_consistency tests.safety.test_loop_automation_dry_run tests.safety.test_stage2d_preparation_plan tests.safety.test_stage2d1_live_preflight tests.safety.test_stage2d2a_live_install tests.safety.test_stage2d2b_live_smoke tests.safety.test_stage2e0_relay_smoke tests.safety.test_stage2e1_relay_hardening tests.smoke.test_universe_and_data tests.smoke.test_backtest_smoke tests.smoke.test_reports_smoke`: pending final verification.
- `git diff --check`: pending final verification.

## Risk Statement

Stage 2E.1 is repo-only hardening for ChatGPT relay target selection and input delivery. It does not run Computer Use, does not send a ChatGPT message, does not modify real Hermes/OpenClaw/Feishu gateway, does not restart services, does not install dependencies, does not touch secrets, and adds no broker or auto-trading surface. The hardened relay defaults to a dedicated review thread; an existing ChatGPT conversation URL may only be read from local_private/chatgpt_review_target.json and is never written to public artifacts.

Final trading is manually decided by the user.

## Short Prompt For ChatGPT

请审核公开 repo https://github.com/leon-hxy/agentic_etf_desk 的 review_target_commit 23cebebed1d07f0b35e66b284ec0891b427d8716；只读取 reports/review_requests/latest.md、reports/review_requests/latest.json、reports/codex_handoff/latest.md、reports/codex_handoff/latest.json。

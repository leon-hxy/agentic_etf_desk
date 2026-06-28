# Codex Handoff

## Current Stage

Stage 2F review governance refactor completed.

## Loop State Stage

Stage 2F review governance refactor completed.

## Review Target Commit

`review_target_commit`

`2006d60f237a9b47f34236fd7dd299e9bbdb4f86`

This is the Stage 2F business commit that should be reviewed when review is required.

## Review Governance

- Small-stage Codex self-review: active.
- Major-stage ChatGPT review: manual and user-initiated.
- ChatGPT Computer Use automatic review route is deprecated.

## Current Repo Head

`2006d60f237a9b47f34236fd7dd299e9bbdb4f86`

## Handoff Commit

`null`

## Files Changed This Round

- `docs/review_governance.md`
- `docs/chatgpt_review_relay_design.md`
- `docs/loop_protocol.md`
- `ops/tasks/stage2f_review_governance.md`
- `ops/templates/internal_codex_self_review_template.md`
- `ops/templates/major_chatgpt_review_template.md`
- `ops/templates/review_governance_task_template.md`
- `configs/codex_automation/review_governance_prompt.md`
- `configs/codex_automation/chatgpt_review_relay_prompt.md`
- `ops/notifications/feishu_message_templates.md`
- `scripts/review_relay/relay_common.py`
- `tests/safety/test_stage2f_review_governance.py`
- `tests/safety/test_review_relay_safety.py`
- `tests/safety/test_handoff_commit_consistency.py`
- `tests/safety/test_loop_state_consistency.py`
- `tests/safety/test_notification_loop_safety.py`
- `tests/safety/test_loop_automation_dry_run.py`
- `tests/safety/test_stage2d_preparation_plan.py`
- `tests/safety/test_stage2e1_relay_hardening.py`
- `ops/state/loop_state.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/review_requests/chatgpt_review_prompt.md`
- `reports/review_requests/chatgpt_review_prompt.json`
- `reports/review_requests/manual_fallback_prompt.md`
- `reports/review_requests/notification_preview.md`
- `reports/review_requests/notification_preview.json`
- `reports/review_requests/relay_status.md`
- `reports/review_requests/relay_status.json`

## Test Commands

- `python3 -m unittest tests.safety.test_stage2f_review_governance tests.safety.test_review_relay_safety`
- `python3 scripts/safety/check_review_relay_safety.py`
- `python3 scripts/safety/check_public_repo_hygiene.py`
- `python3 scripts/safety/check_handoff_commit_consistency.py`
- `python3 -m unittest tests.safety.test_safety tests.safety.test_public_repo_hygiene tests.safety.test_notification_loop_safety tests.safety.test_review_relay_safety tests.safety.test_handoff_commit_consistency tests.safety.test_strategy_templates_safety tests.safety.test_backtest_safety tests.safety.test_openclaw_agents_safety tests.safety.test_hermes_router_safety tests.safety.test_loop_state_consistency tests.safety.test_loop_automation_dry_run tests.safety.test_stage2d_preparation_plan tests.safety.test_stage2d1_live_preflight tests.safety.test_stage2d2a_live_install tests.safety.test_stage2d2b_live_smoke tests.safety.test_stage2e0_relay_smoke tests.safety.test_stage2e1_relay_hardening tests.safety.test_stage2f_review_governance tests.smoke.test_universe_and_data tests.smoke.test_backtest_smoke tests.smoke.test_reports_smoke`
- `git diff --check`

## Test Results

- passed; Stage 2F governance and review safety tests.
- passed; no review governance safety findings.
- passed; no local path or secret findings.
- passed; review_target_commit binds to Stage 2F business commit.
- passed; 91 tests OK.
- passed; no whitespace errors.

## Runtime And Safety Checklist

- Modified real `~/.hermes`: false.
- Modified real `~/.openclaw`: false.
- Modified real Feishu gateway: false.
- Restarted services: false.
- Installed dependencies: false.
- Printed or committed secret values: false.
- Sent real Feishu messages in this stage: false.
- Used Computer Use in this stage: false.
- Sent to ChatGPT in this stage: false.
- Automatic trading surface present: false.
- Broker write surface present: false.

## Next Recommended Stage

Use Codex self-review for small stages; request user-initiated ChatGPT review only for major stages.

## Requires User Approval

- Any live Computer Use action
- Any user-initiated major-stage ChatGPT review outside repo materials
- Any Hermes/OpenClaw restart
- Any real Feishu gateway or router change
- Any live Hermes or OpenClaw config change
- Any dependency installation
- Any secret migration or credential storage
- Any broker integration or trading execution surface

## Forbidden To Continue Automatically

- Running ChatGPT Computer Use automatic review
- Opening ChatGPT automatically
- Sending ChatGPT prompts automatically
- Modifying real ~/.hermes or ~/.openclaw
- Restarting Hermes or OpenClaw
- Modifying real Feishu gateway
- Installing dependencies
- Sending secrets, local paths, tokens, auth values, Feishu credentials, provider keys, or broker credentials
- Accessing broker, email, GitHub admin, or Feishu admin pages
- Creating execution, order, broker, auto-trading, or live-trading agents
- Adding automatic order placement code or broker write access

Final trading is manually decided by the user.

# Codex Handoff

## Current Stage

Stage 2F.1 branch governance and Stage 3 task plan completed.

## Latest Commit Binding

- `review_target_commit`: `b6defd4376a8767b197cdcc8062238d1701a530a`
- `handoff_commit`: `null`
- `handoff_generated_from_head`: `b6defd4376a8767b197cdcc8062238d1701a530a`
- `current_repo_head`: `b6defd4376a8767b197cdcc8062238d1701a530a`

`review_target_commit` is the commit to review. The handoff may be committed
later and therefore cannot self-reference its own final SHA in the same commit.
This field will be refreshed after the Stage 2F.1 business commit is created.

## This Round Changed Files

- `docs/branching_policy.md`
- `docs/review_governance.md`
- `ops/stages/stage3.yaml`
- `ops/tasks/stage3a_data_source.md`
- `ops/tasks/stage3b_data_quality.md`
- `ops/tasks/stage3c_backtest_validation.md`
- `ops/tasks/stage3d_strategy_evidence_report.md`
- `ops/tasks/stage3_major_review_package.md`
- `reports/internal_reviews/README.md`
- `reports/major_reviews/README.md`
- `configs/codex_automation/review_governance_prompt.md`
- `configs/codex_automation/chatgpt_review_relay_prompt.md`
- `scripts/review_relay/relay_common.py`
- `scripts/safety/check_handoff_commit_consistency.py`
- `scripts/safety/check_review_relay_safety.py`
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
- `tests/safety/test_branch_governance.py`
- `tests/safety/test_stage2f_review_governance.py`
- `tests/safety/test_handoff_commit_consistency.py`
- `tests/safety/test_loop_state_consistency.py`
- `tests/safety/test_notification_loop_safety.py`
- `tests/safety/test_loop_automation_dry_run.py`
- `tests/safety/test_stage2d_preparation_plan.py`
- `tests/safety/test_stage2e0_relay_smoke.py`
- `tests/safety/test_stage2e1_relay_hardening.py`
- `tests/safety/test_review_relay_safety.py`

## Tests

- `python3 -m unittest tests.safety.test_branch_governance`: passed; 4 tests OK.
- `python3 -m unittest tests.safety.test_safety tests.safety.test_public_repo_hygiene tests.safety.test_notification_loop_safety tests.safety.test_review_relay_safety tests.safety.test_handoff_commit_consistency tests.safety.test_strategy_templates_safety tests.safety.test_backtest_safety tests.safety.test_openclaw_agents_safety tests.safety.test_hermes_router_safety tests.safety.test_loop_state_consistency tests.safety.test_loop_automation_dry_run tests.safety.test_stage2d_preparation_plan tests.safety.test_stage2d1_live_preflight tests.safety.test_stage2d2a_live_install tests.safety.test_stage2d2b_live_smoke tests.safety.test_stage2e0_relay_smoke tests.safety.test_stage2e1_relay_hardening tests.safety.test_stage2f_review_governance tests.safety.test_branch_governance tests.smoke.test_universe_and_data tests.smoke.test_backtest_smoke tests.smoke.test_reports_smoke`: passed; 95 tests OK.
- `python3 scripts/safety/check_review_relay_safety.py`: passed; no findings.
- `python3 scripts/safety/check_public_repo_hygiene.py`: passed; no findings.
- `python3 scripts/safety/check_handoff_commit_consistency.py`: passed; no findings.
- `git diff --check`: passed; no whitespace errors.

## Safety Flags

- Modified real `~/.hermes`: false
- Modified real `~/.openclaw`: false
- Modified real Feishu gateway: false
- Restarted Hermes/OpenClaw: false
- Installed dependencies: false
- Touched secrets: false
- Wrote secret values: false
- Ran Computer Use: false
- Sent ChatGPT prompt: false
- Sent Feishu message: false
- Automatic trading surface: false
- Broker surface: false
- Stage 3 business code started: false

## Governance Summary

- `main` is the stable branch for major-stage reviewed states.
- `stage/stage3-data-backtest` is the Stage 3 construction branch.
- Stage 3 small stages use Codex self-review.
- Stage 3 major review uses manual ChatGPT review after the Stage 3E package.
- Codex does not request ChatGPT review for small stages.
- Codex does not use Computer Use to send review requests to ChatGPT.
- ChatGPT Computer Use automatic review route is deprecated.

## Next Recommended Stage

Start Stage 3A on `stage/stage3-data-backtest`.

## Requires User Approval

- Any live Computer Use action.
- Any user-initiated major-stage ChatGPT review outside repo materials.
- Any Hermes/OpenClaw restart.
- Any real Feishu gateway or router change.
- Any live Hermes or OpenClaw config change.
- Any dependency installation.
- Any secret migration or credential storage.
- Any broker integration or trading execution surface.

## Forbidden To Continue Automatically

- Starting Stage 3 business code on `main`.
- Running ChatGPT Computer Use automatic review.
- Opening ChatGPT automatically.
- Sending ChatGPT prompts automatically.
- Modifying real `~/.hermes` or `~/.openclaw`.
- Restarting Hermes or OpenClaw.
- Modifying real Feishu gateway.
- Installing dependencies.
- Sending secrets, local paths, tokens, auth values, Feishu credentials,
  provider keys, or broker credentials.
- Accessing broker, email, GitHub admin, or Feishu admin pages.
- Adding automatic order placement code or broker write access.

Final trading is manually decided by the user.

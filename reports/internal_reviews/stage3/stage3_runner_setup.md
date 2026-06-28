# Stage 3 Runner Setup Internal Review

- `minor_stage`: Stage 3 Runner Setup
- `task_file`: attached Stage 3 Runner Setup request
- `status`: completed_internal_runner_setup
- `branch`: stage/stage3-data-backtest

## Builder Summary

Created a repo-only Stage 3 runner state machine, checklist, and Codex App
automation prompt so future wakes can resume Stage 3C, Stage 3D, and Stage 3E in
order. The setup keeps small-stage review internal to Codex and reserves manual
ChatGPT review for the Stage 3E major review package.

## Changed Files

- `ops/runners/stage3_runner.md`
- `ops/runners/stage3_runner_state.json`
- `ops/runners/stage3_runner_checklist.md`
- `configs/codex_automation/stage3_runner_automation_prompt.md`
- `ops/stages/stage3.yaml`
- `ops/tasks/stage3c_backtest_validation.md`
- `ops/tasks/stage3d_strategy_evidence_report.md`
- `ops/tasks/stage3_major_review_package.md`
- `tests/safety/test_stage_runner_governance.py`
- `reports/internal_reviews/stage3/stage3_runner_setup.md`
- `reports/internal_reviews/stage3/stage3_runner_setup.json`

## Security Reviewer

- `result`: pass
- `reviewer_mode`: setup_internal_pass
- `secrets_touched`: false
- `real_config_modified`: false
- `computer_use_executed`: false
- `auto_trading_surface`: false
- `broker_write_surface`: false
- `public_repo_hygiene_expected`: true

## Domain Reviewer

- `result`: pass
- ETF-only scope is preserved.
- The runner is a governance mechanism only and does not change research logic.
- Final trading is manually decided by the user.
- No individual stocks, options, futures, crypto assets, leveraged ETFs, or
  inverse ETFs are introduced.

## Integration Reviewer

- `result`: pass
- Runner state points at `stage/stage3-data-backtest`.
- Stage 3C is ready after Stage 3B completed internal review.
- Stage 3D depends on Stage 3C completed internal review.
- Stage 3E depends on Stage 3D completed internal review.
- Small stages do not request ChatGPT review.
- Stage 3E is the first stage that prepares the major review package.

## Test Reviewer

- `result`: pass
- Added `tests/safety/test_stage_runner_governance.py`.
- `python3 -m unittest tests.safety.test_stage_runner_governance`: red run
  failed as expected before runner artifacts existed; green run passed, 4 tests
  OK.
- `python3 -m unittest`: passed, 108 tests OK.
- `python3 scripts/safety/check_forbidden_surfaces.py`: passed.
- `python3 scripts/safety/check_secret_leaks.py`: passed.
- `python3 scripts/safety/check_public_repo_hygiene.py`: passed.
- `python3 scripts/safety/check_universe_only.py`: passed.
- `git diff --check`: passed.

## Automation Creation

The repo prompt is prepared at
`configs/codex_automation/stage3_runner_automation_prompt.md`. Codex App
automation is application state outside the repo and should be created only
after this runner setup commit is pushed.

## Promotion

- `runner_ready`: true
- `stage3c_can_start_after_push`: true
- `requires_user_attention`: false

Final trading is manually decided by the user.

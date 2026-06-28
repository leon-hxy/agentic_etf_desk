# Review Request

## Current Stage

Stage 2F.1 branch governance and Stage 3 task plan completed.

## Review Target

- `review_target_commit`: `b6defd4376a8767b197cdcc8062238d1701a530a`
- `handoff_commit`: `null`
- `handoff_generated_from_head`: `b6defd4376a8767b197cdcc8062238d1701a530a`
- `current_repo_head`: `b6defd4376a8767b197cdcc8062238d1701a530a`

Please review this `review_target_commit` for Stage 2F.1 if a manual
major-stage ChatGPT review is requested by the user. This field will be
refreshed after the Stage 2F.1 business commit is created.

## Public Review Paths

- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `docs/branching_policy.md`
- `ops/stages/stage3.yaml`
- `ops/tasks/stage3a_data_source.md`
- `ops/tasks/stage3b_data_quality.md`
- `ops/tasks/stage3c_backtest_validation.md`
- `ops/tasks/stage3d_strategy_evidence_report.md`
- `ops/tasks/stage3_major_review_package.md`
- `reports/internal_reviews/README.md`
- `reports/major_reviews/README.md`
- `tests/safety/test_branch_governance.py`

## Review Focus

- Branch governance: `main`, `stage/*`, and optional `task/*` roles.
- Stage 3 task plan and the Stage 3 construction branch.
- Small-stage Codex self-review and major-stage manual ChatGPT review split.
- Deprecated ChatGPT Computer Use automatic review route.
- ETF-only, no automatic trading, no broker write surface, and manual final
  trading constraints.
- Public repo hygiene and secret-safety constraints.

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

## Next Recommended Stage

Start Stage 3A on `stage/stage3-data-backtest`.

Final trading is manually decided by the user.

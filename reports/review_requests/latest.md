# Review Request

## Current Stage

Stage 2F.1 branch governance and Stage 3 task plan completed.

## Review Target

- `review_target_commit`: `REVIEW_TARGET_COMMIT_PENDING_STAGE2F1`
- `handoff_commit`: `null`
- `handoff_generated_from_head`: `23714230ebda5bbaa16c27fac9efdf8d76663911`
- `current_repo_head`: `23714230ebda5bbaa16c27fac9efdf8d76663911`

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

- `python3 -m unittest tests.safety.test_branch_governance`: pending after Stage 2F.1 implementation.
- `python3 -m unittest full safety/smoke suite`: pending after `review_target_commit` is bound to the Stage 2F.1 business commit.
- `git diff --check`: pending.

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

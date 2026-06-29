# Program Internal Review: Autonomous Program Runner Setup

## Metadata

- major_stage: Program Runner Setup
- work_package: Autonomous Program Runner Setup
- commit: pending in the commit that adds this review; a commit cannot self-reference its final SHA
- changed_files:
  - `docs/branching_policy.md`
  - `configs/codex_automation/program_runner_heartbeat_prompt.md`
  - `configs/codex_automation/program_runner_manual_trigger_prompt.md`
  - `ops/program_runner/README.md`
  - `ops/program_runner/roadmap.yaml`
  - `ops/program_runner/program_runner_state.json`
  - `ops/program_runner/program_runner.md`
  - `ops/program_runner/approval_queue.json`
  - `ops/program_runner/heartbeat_log.md`
  - `ops/program_runner/blocked_reason.md`
  - `ops/templates/program_internal_review_template.md`
  - `ops/templates/program_internal_review_template.json`
  - `reports/program_reviews/README.md`
  - `reports/program_reviews/final/README.md`
  - `reports/internal_reviews/program/README.md`
  - `reports/internal_reviews/program/program_runner_setup.md`
  - `reports/internal_reviews/program/program_runner_setup.json`
  - `scripts/safety/check_forbidden_surfaces.py`
  - `tests/safety/test_program_runner_governance.py`
- reviewer_mode: subagents

## Security Reviewer

- result: pass after fixes
- findings:
  - Missing `risk_agent` gate in the autonomous runner.
  - Approval queue conflicted with mandatory git push.
  - The broker-write allowed scanner exception was value-blind.
- fixes_required: completed
- fixes_applied:
  - Added `risk_agent` trade-ticket gate to runner, templates, prompts, and roadmap.
  - Added a safe git push exception only after public repo hygiene, secret, forbidden-surface, and relevant safety checks pass.
  - Reworked the forbidden-surface scanner to mask only false or blank broker-write governance fields and added a true-value regression test.
- secrets_touched: false
- live_configs_modified: false
- automatic_trading_surface: false
- broker_write_surface: false

## Domain / Quant Reviewer

- result: pass after fixes
- findings:
  - Final-review-only governance needed migration language in the branch policy.
  - Trade-ticket risk review, benchmark comparison, and ETF allowlist imports were too implicit.
  - Final package evidence wording needed to avoid formal investment-proof framing.
- fixes_required: completed
- fixes_applied:
  - Added Program Runner final-only review policy to `docs/branching_policy.md`.
  - Added required benchmark comparison and `risk_agent` review obligations to the roadmap and templates.
  - Added manual holdings/trades allowlist rejection to the roadmap.
  - Clarified final package evidence as research/backtest/scenario evidence, not formal investment proof.
- etf_only_maintained: true
- benchmark_comparison_present: true
- research_limitations_clear: true
- risk_agent_review_required_for_trade_tickets: true
- trade_tickets_actionable_without_risk_agent_review: false

## Integration Reviewer

- result: pass after fixes
- findings:
  - Stage 3.1 prerequisite could be bypassed by a ready runner state.
  - No branch guard before automated commit/push.
  - Intermediate runner states were not resumable in automation prompts.
  - Runner state update occurred after commit/push in the original contract.
  - Approval queue lacked stable item fields and a concise notification slot.
- fixes_required: completed
- fixes_applied:
  - Added `stage/v1-autonomous-completion` branch guard to state and prompts.
  - Added Stage 3.1 main-merge verification before Stage 3.2 business work.
  - Added resume instructions for intermediate states.
  - Changed workflow language so runner state is updated before committing and pushing the complete package.
  - Extended approval item schema with id, status, created time, work package, next safe action, and notification message.
- Hermes/Feishu boundary respected: true
- OpenClaw boundary respected: true
- no real runtime modification without approval: true

## Test / Reproducibility Reviewer

- result: pass after fixes
- findings:
  - Program Runner files were untracked during review; staging and commit are required before completion.
  - Safety-boundary key drift existed between roadmap and runner state.
  - Roadmap tests were too string-fragment oriented.
  - Scanner exception lacked a red regression test.
- fixes_required: completed except final staging/commit
- fixes_applied:
  - Standardized on `auto_trading_allowed`.
  - Added lightweight structural roadmap block parsing to the governance test.
  - Added scanner red/green coverage for the broker-write allowed governance flag.
  - Final staging, commit, and push are performed after verification.
- tests_run:
  - `python3 -m unittest tests.safety.test_program_runner_governance`
  - `python3 -m unittest`
  - `python3 scripts/safety/check_forbidden_surfaces.py --root .`
  - `python3 scripts/safety/check_secret_leaks.py --root .`
  - `python3 scripts/safety/check_public_repo_hygiene.py --root .`
  - `python3 scripts/safety/check_universe_only.py --root .`
  - `git diff --check`

## Public Repo Hygiene Reviewer

- result: pass after fixes
- findings:
  - The broker-write allowed scanner exception could mask a future unsafe true value.
  - No local-private paths, real tokens, secrets, auth values, or private IDs were found in runner files.
- fixes_required: completed
- fixes_applied:
  - Added value-aware scanner masking and true-value regression coverage.
- no local-private paths: true
- no secrets or credentials: true
- public repo safe: true

## Findings

- findings: all reviewer findings above were addressed in repo-only files.
- fixes_applied: see reviewer sections.
- tests: final full verification passed before commit.
- pass/fail: pass after fixes; final verification passed; pending git push.
- requires_user_attention: false
- promote_to_next_work_package: false

Final trading is manually decided by the user.

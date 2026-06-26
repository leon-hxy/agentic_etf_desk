# Codex Handoff

## Current Stage

Stage 2A.5 completed.

## Latest Commit SHA

`c1619fc00778a8707db6966c0a393ebbb07b21c5`

Note: this SHA is the repository HEAD when this handoff update began. The final pushed commit for this handoff is reported by Git after commit and push.

## Files Changed This Round

- `.gitignore`
- `configs/codex_automation/loop_manager_prompt.md`
- `docs/current_state_audit.md`
- `docs/git_history_sanitization_plan.md`
- `docs/github_public_repo_security.md`
- `docs/loop_protocol.md`
- `docs/public_repo_policy.md`
- `docs/real_config_hardening_plan.md`
- `docs/runbook.md`
- `local_private/.gitkeep`
- `local_private/README.md`
- `ops/README.md`
- `ops/state/loop_state.json`
- `ops/tasks/README.md`
- `ops/tasks/stage2b_repo_only.md`
- `ops/templates/chatgpt_review_request_template.md`
- `ops/templates/codex_task_template.md`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `scripts/safety/check_public_repo_hygiene.py`
- `tests/safety/test_public_repo_hygiene.py`
- `tests/safety/test_safety.py`

## Test Commands

- `python3 -m unittest tests.safety.test_safety tests.safety.test_public_repo_hygiene tests.smoke.test_universe_and_data`
- `git diff --check`
- `git status --short --untracked-files=all`

## Test Results

- `python3 -m unittest tests.safety.test_safety tests.safety.test_public_repo_hygiene tests.smoke.test_universe_and_data`: passed, 11 tests OK.
- `git diff --check`: passed, no whitespace errors.
- `git status --short --untracked-files=all`: changes limited to Stage 2A.5 repo-only hygiene, loop scaffolding, review request, handoff, and tests.

## Runtime And Safety Checklist

- Modified real `~/.hermes`: false.
- Modified real `~/.openclaw`: false.
- Restarted services: false.
- Installed dependencies: false.
- Touched secrets: false.
- Automatic trading surface present: false.
- Public repo hygiene completed: true.
- Loop manager draft completed: true.

## Next Recommended Stage

Stage 2B repo-only.

## Requires User Approval

- Entering `/goal` long-running work for Stage 2B.
- Any modification to real `~/.hermes`.
- Any modification to real `~/.openclaw`.
- Any Hermes or OpenClaw restart.
- Any Feishu router or configuration change.
- Any dependency installation.
- Any secret migration or credential storage.
- Any broker integration, including read-only broker account access.
- Any expansion beyond ETF-only scope or addition of leveraged/inverse ETFs.
- Any git history rewrite or repository recreation.

## Forbidden To Continue Automatically

- Modifying real `~/.hermes`.
- Modifying real `~/.openclaw`.
- Restarting Hermes or OpenClaw.
- Running `hermes doctor --fix` or `openclaw doctor --fix`.
- Modifying Feishu gateway/configuration.
- Modifying launchd or crontab.
- Running chmod/chown on real Hermes/OpenClaw directories.
- Installing dependencies without user approval.
- Writing secrets, tokens, auth values, `.env` values, Feishu App Secret, provider keys, or broker credentials.
- Creating execution, order, broker, auto-trading, or live-trading agents.
- Adding automatic order placement code.
- Adding broker write access.
- Adding individual stocks, options, futures, crypto assets, leveraged ETFs, or inverse ETFs unless explicitly allowlisted later.

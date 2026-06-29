# Runbook

## Phase 1

Phase 1 is local initialization and read-only audit only.

Allowed:

- Initialize git if needed.
- Create project directories and documentation.
- Run read-only local environment checks.
- Write `docs/current_state_audit.md`.
- Run safety checks against the repository.

Not allowed:

- Modify real `~/.hermes`.
- Modify real `~/.openclaw`.
- Restart Hermes or OpenClaw.
- Modify Feishu configuration.
- Install dependencies.
- Connect broker APIs.
- Add automatic order placement.

## Future Approval Gates

Ask for explicit user approval before:

- Entering a long-running `/goal` implementation phase.
- Changing Hermes configuration.
- Changing OpenClaw configuration.
- Restarting Hermes or OpenClaw.
- Installing dependencies.
- Adding scheduled jobs.
- Adding new ETF allowlist rules.
- Adding any external data provider that needs credentials.

## Safety Check

The following command contains forbidden example terms for policy scanning. These are documentation-only bans, not executable trading code.

Before a final response after code or policy changes, scan for forbidden execution surfaces and secret leakage. The first safety check can be a repository-only read:

```bash
rg -n -i "execution_agent|order_agent|broker_agent|auto_trader|live_trader|place_order|submit_order|buy_market|sell_market|ib\\.placeOrder|alpaca\\.submit_order|broker write|auto_trade|automatic order|FEISHU_APP_SECRET|APP_SECRET|TOKEN_NAME|SECRET_NAME|AUTH_NAME" .
```

Any hit must be reviewed. Policy documentation may mention forbidden terms only to prohibit them.

## Stage 2A Repo-Only Data Flow

Validate the ETF universe:

```bash
python3 scripts/data/validate_universe.py
```

Generate sample public-price data without installing dependencies:

```bash
python3 scripts/data/download_prices.py --source sample --start 2024-01-02 --end 2024-01-31
```

Build the adjusted-close price panel:

```bash
python3 scripts/data/build_price_panel.py
```

Write the Stage 2A smoke report:

```bash
python3 scripts/reports/write_stage2a_smoke_report.py
```

Run safety and smoke tests:

```bash
python3 -m unittest tests.safety.test_safety tests.smoke.test_universe_and_data
```

These commands are repo-only. They must not modify real Hermes, OpenClaw, Feishu, launchd, crontab, or broker configuration.

## Stage 6 Long-Term Operating Runbook

This section is the steady-state operating guide for the autonomous ETF research desk after Stage 6 hardening. It is repo-only and does not require live runtime changes.

Final trading is manually decided by the user.

### Operating Loop

- Run the Program Runner heartbeat: Every 10 to 30 minutes, or manually trigger the same prompt when recovering a paused thread.
- Every wake must verify the branch is `stage/v1-autonomous-completion` before implementation.
- Every wake must read `ops/program_runner/program_runner_state.json`, `ops/program_runner/roadmap.yaml`, `AGENTS.md`, `docs/security_policy.md`, and `docs/branching_policy.md`.
- Complete at most one work package per wake unless runner state explicitly allows continuing.

### Status And Notification Gates

- Continue autonomously only from `ready`, `running`, `next_work_package_ready`, or resumable in-progress states.
- Notify the user only for blocked, approval_required, or final_review_ready states.
- Do not notify for `work_package_completed`, `tests_passed`, or `internal_review_completed`.
- If live Hermes/Feishu send would require real configuration edits or service restarts, generate notification preview files instead.

### Safety Verification

- Keep the system ETF-only.
- Keep all strategy outputs benchmark-aware.
- Keep trade tickets behind `risk_agent` review before they can be actionable suggestions.
- Run safety and smoke tests before ending any wake that changes code, policy, reports, runner state, or runbook content.

Required baseline commands:

```bash
python3 -m unittest tests.safety.test_safety
python3 -m unittest discover tests/safety
python3 -m unittest discover tests/smoke
python3 scripts/safety/check_forbidden_surfaces.py --root .
python3 scripts/safety/check_secret_leaks.py --root .
python3 scripts/safety/check_public_repo_hygiene.py --root .
python3 scripts/safety/check_universe_only.py
git diff --check
```

### Runtime Boundaries

- Do not modify real `~/.hermes` without explicit user confirmation.
- Do not modify real `~/.openclaw` without explicit user confirmation.
- Do not modify real Feishu gateway configuration without explicit user confirmation.
- Do not restart Hermes or OpenClaw without explicit user confirmation.
- Do not install dependencies without explicit user approval.
- Do not connect broker write interfaces.
- Do not place orders.
- Do not add automatic trading behavior.

### Incident Recovery

- For `blocked`, update `ops/program_runner/blocked_reason.md` and generate `reports/program_runner/notification_preview.md` plus `reports/program_runner/notification_preview.json` when live send is not approved.
- For `approval_required`, update `ops/program_runner/approval_queue.json` and include `next_safe_action` in the notification preview.
- Never include secrets, auth values, local-private paths, Feishu IDs, provider keys, broker account data, or broker credentials in reports or notifications.
- Resume from runner state rather than redoing completed work packages.

### Final Review Transition

- After this runbook package, prepare the Final v1.0 review package under `reports/program_reviews/final/latest.md` and `reports/program_reviews/final/latest.json`.
- Move to `final_review_ready` only after the final package exists, passes internal review, and preserves the ETF-only, no-auto-trading, no-broker-write, and manual-final-trading boundaries.
- The only allowed user-facing final readiness message is: `v1.0 final review package is ready. 是否请求 ChatGPT 最终审核？`

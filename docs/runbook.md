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

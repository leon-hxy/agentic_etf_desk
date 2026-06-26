# Stage 2B Plan

Stage 2B should build on the repo-only foundation from Stage 2A. It should still avoid live Hermes and OpenClaw changes unless the user explicitly approves a separate integration step.

## ETF Strategy Templates

Repo-only work:

- Benchmark buy and hold.
- Static 60/40 ETF allocation.
- Equal-weight ETF allocation.
- GTAA 10-month simple moving average.
- Dual momentum.
- Time-series momentum with volatility target.
- Inverse-volatility allocation.
- ETF mean-reversion sandbox.

Required controls:

- Every strategy reads symbols from `configs/universe/etf_universe.yaml`.
- Every strategy compares against a benchmark.
- Every strategy records assumptions, rebalance cadence, data dates, and risk limits.
- No strategy writes orders or connects to broker write APIs.

## Backtest Engine

Repo-only work:

- Portfolio accounting from adjusted close or total return data.
- Rebalance calendar.
- Transaction-cost assumptions.
- Benchmark comparison.
- Drawdown, volatility, turnover, and exposure metrics.
- Machine-readable backtest metadata.

Outputs:

- `backtests/<strategy>/<run_id>/results.json`
- `backtests/<strategy>/<run_id>/equity_curve.csv`
- `backtests/<strategy>/<run_id>/risk_summary.json`

## Reports And Trade Recommendation Tickets

Repo-only work:

- Markdown and JSON report templates.
- Feishu-readable short summary format.
- Manual recommendation ticket template.
- Risk review gate.
- Benchmark comparison section.

Required ticket disclaimer:

This is research advice only, not automatic order placement. Final trading is manually decided by the user.

## OpenClaw Agents Draft

Repo-only suggested config templates may be added under `configs/openclaw/`.

Suggested research-only roles:

- Universe researcher.
- Data validator.
- Strategy researcher.
- Backtest runner.
- Risk reviewer.
- Report writer.

Rules:

- No execution, order-routing, broker-access, automatic-trading, or live-trading roles.
- Agents must not receive broker write credentials.
- Agents may output only research artifacts, risk review, reports, and manual recommendation tickets.

Real OpenClaw integration requires approval before writing to `~/.openclaw` or restarting any service.

## Hermes Feishu Router Draft

Repo-only suggested config templates may be added under `configs/hermes/`.

Router behavior:

- Hermes remains the only general assistant.
- Route only ETF research requests into the repo workflow.
- Reject non-ETF assets by default.
- Return concise Feishu-readable summaries.
- Never imply that a trade was placed.

Real Hermes integration requires approval before writing to `~/.hermes`, changing Feishu settings, or restarting Hermes.

## Still Repo-Only

- Strategy code.
- Backtest engine.
- Report templates.
- Recommendation ticket templates.
- Suggested OpenClaw config files.
- Suggested Hermes router config files.
- Safety tests and smoke tests.

## Requires Explicit Approval

- Live Hermes config changes.
- Live OpenClaw config changes.
- Hermes or OpenClaw restart.
- Feishu gateway/router changes.
- Launchd changes.
- Crontab changes.
- Dependency installation.
- Secret migration.
- Any broker integration, including read-only broker account access.


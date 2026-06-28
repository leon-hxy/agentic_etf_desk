# Implementation Plan

## Phase 1: Read-Only Audit

Goal: initialize the repository structure, write project operating rules, and document the local machine state without changing live Hermes, OpenClaw, Feishu, broker, or service configuration.

Deliverables:

- Project directory structure.
- `AGENTS.md`.
- Core documentation.
- `docs/current_state_audit.md`.

Allowed actions:

- Read local tool versions.
- Check file and directory existence.
- Check whether processes or launch agents are present.
- Search current project and related local agent configuration for dangerous trading surfaces.

Forbidden actions:

- Modify real `~/.hermes`.
- Modify real `~/.openclaw`.
- Restart Hermes or OpenClaw.
- Modify Feishu configuration.
- Install dependencies.
- Connect broker systems.
- Add order-placement code.

## Phase 2: ETF Universe And Data Module

Goal: define an ETF-only universe and local data interfaces.

Planned work:

- Create ETF allowlist schema.
- Create exclusion checks for stocks, options, futures, crypto assets, leveraged ETFs, and inverse ETFs.
- Add data source abstraction.
- Add data provenance records.
- Add validation for missing prices, stale data, splits, distributions, and benchmark coverage.

Needs user approval before:

- Adding paid or credentialed data sources.
- Storing provider credentials.
- Expanding beyond ETF-only scope.
- Adding leveraged or inverse ETFs to a future explicit allowlist.

## Phase 3: ETF Strategy Templates

Goal: implement transparent ETF-only strategy templates.

Initial templates:

- Benchmark buy and hold.
- Static 60/40.
- Equal-weight ETF.
- GTAA 10-month simple moving average.
- Dual momentum.
- Time-series momentum with volatility target.
- Inverse-volatility allocation.
- ETF mean-reversion sandbox.

Requirements:

- Every strategy must compare against a benchmark.
- Every strategy must expose assumptions, universe, rebalance cadence, and risk limits.
- No strategy may call execution, broker write, or order-placement APIs.

### Stage 3 Closeout

Stage 3 completed as sample-data pipeline validation only.

- Stage 3 is not production backtest.
- Stage 3 is not investment evidence.
- Stage 3 used sample data to validate repository pipeline wiring, safety boundaries, data-quality reporting, backtest validation plumbing, and strategy-evidence report generation.
- The next stage is Stage 3.1 real ETF historical data integration and formal backtesting.

## Phase 4: Backtest Engine

Goal: create a local backtest engine for ETF strategy research.

Planned work:

- Portfolio accounting.
- Rebalance simulation.
- Transaction cost assumptions.
- Benchmark comparison.
- Risk metrics.
- Drawdown analysis.
- Reproducible report artifacts.

Forbidden:

- Live trading.
- Broker write integration.
- Any automatic order submission.

## Phase 5: Reports And Trade Recommendation Tickets

Goal: produce Feishu-readable reports and manual trade recommendation tickets.

Requirements:

- Reports must say final trading is manual.
- Tickets must state that they are research advice, not automatic order placement.
- Tickets must pass risk review before delivery.
- Tickets must include benchmark comparison and risk summary.
- Tickets must not contain secrets.

## Phase 6: Safety Tests

Goal: enforce project safety boundaries with tests and repository scans.

Planned checks:

- Forbidden agent names.
- Forbidden order-placement APIs.
- Broker write interfaces.
- Secret leakage patterns.
- Missing manual-trading disclaimers in reports or ticket templates.
- Strategy outputs missing benchmark comparison.
- Tickets missing risk review status.

## Phase 7: Minimal Hermes Feishu Router Integration

Goal: connect Hermes to the project through a minimal, auditable router after explicit user approval.

Planned work:

- Define a narrow routing contract.
- Route only ETF research requests.
- Return concise Feishu-readable summaries.
- Keep Hermes as the only general assistant.
- Keep OpenClaw as later specialist-agent coordinator.

Needs user approval before:

- Modifying real Hermes configuration.
- Modifying real OpenClaw configuration.
- Restarting Hermes or OpenClaw.
- Changing Feishu configuration.
- Installing dependencies.
- Adding scheduled jobs.

## Requires Explicit User Approval

- Entering a long-running `/goal` implementation phase.
- Any live Hermes configuration change.
- Any live OpenClaw configuration change.
- Any Hermes or OpenClaw restart.
- Any Feishu configuration change.
- Any dependency installation.
- Any new credential or secret storage.
- Any new scheduled job.
- Any expansion beyond ETF-only scope.
- Any broker integration, even read-only.

## Forbidden To Execute Automatically

- Order placement.
- Broker write access.
- Automatic trading.
- Live trading.
- Creation of execution/order/broker/auto-trader agents.
- Writing secrets into logs or reports.
- Modifying `~/.hermes` or `~/.openclaw` without explicit user confirmation.

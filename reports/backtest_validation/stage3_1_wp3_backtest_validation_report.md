# Stage 3.1 WP3 Backtest Validation Report

- Stage: `Stage 3.1 WP3 formal backtest and evidence package completed_internal_review`
- Status: `passed`
- Monthly panel: `data/processed/stage3_1_monthly_panel.csv`
- Benchmark: `VTI`
- Backtest months: `89`

## Validation Checks

- `wp2_quality_passed`: `passed`
- `universe_allowlist_passed`: `passed`
- `all_strategies_have_benchmarks`: `passed`
- `all_strategies_have_required_metrics`: `passed`
- `manual_trading_notice_present`: `passed`

## Benchmark Comparisons

| Strategy | Benchmark | Strategy CAGR | Benchmark CAGR | Excess CAGR | Max Drawdown | Benchmark Max Drawdown |
|---|---|---:|---:|---:|---:|---:|
| benchmark_buy_hold | VTI | 15.59% | 15.59% | -0.00% | -24.82% | -24.82% |
| static_6040 | VTI | 10.31% | 15.59% | -5.28% | -19.30% | -24.82% |
| gtaa_10m_sma | VTI | 11.15% | 15.59% | -4.43% | -19.48% | -24.82% |
| dual_momentum | VTI | 15.97% | 15.59% | 0.38% | -25.47% | -24.82% |

## Safety

- No Computer Use.
- No ChatGPT review requested.
- No broker interface, broker write access, order placement, or automatic trading surface.

Final trading is manually decided by the user.

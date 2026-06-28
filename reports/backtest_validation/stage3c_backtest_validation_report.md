# Stage 3C Backtest Validation Report

- Stage: `Stage 3C backtest validation`
- Status: `passed`
- Backtest report: `reports/stage2b_backtest_report.json`
- Stage 3B quality report: `reports/data_quality/stage3b_data_quality_report.json`
- Data boundary: Sample data only; not investment basis.

## Validation Checks

- `stage3b_quality_passed`: `passed`
- `reference_smoke_report_loaded`: `passed`
- `all_strategies_have_benchmarks`: `passed`
- `all_strategies_have_required_metrics`: `passed`
- `manual_trading_notice_present`: `passed`
- `sample_data_boundary_documented`: `passed`

## Strategy Benchmark Comparisons

| Strategy | Benchmark | Strategy CAGR | Benchmark CAGR | Excess CAGR | Strategy Max DD | Benchmark Max DD |
|---|---|---:|---:|---:|---:|---:|
| benchmark_buy_hold | VTI | 0.848364 | 0.871744 | -0.023380 | 0.000000 | 0.000000 |
| dual_momentum | VTI | 0.801962 | 0.871744 | -0.069782 | 0.000000 | 0.000000 |
| equal_weight_etf | VTI | 0.603632 | 0.871744 | -0.268112 | 0.000000 | 0.000000 |
| etf_mean_reversion_sandbox | VTI | 0.726807 | 0.871744 | -0.144938 | 0.000000 | 0.000000 |
| gtaa_10m_sma | VTI | 0.846294 | 0.871744 | -0.025451 | 0.000000 | 0.000000 |
| inverse_volatility_allocation | VTI | 0.563655 | 0.871744 | -0.308090 | 0.000000 | 0.000000 |
| static_6040 | VTI | 0.762727 | 0.871744 | -0.109018 | 0.000000 | 0.000000 |
| time_series_momentum_vol_target | VTI | 0.846294 | 0.871744 | -0.025451 | 0.000000 | 0.000000 |

## Safety

- No Computer Use.
- No ChatGPT review requested.
- No Feishu message sent.
- No real Hermes, OpenClaw, or Feishu gateway modification.
- No dependency installation.
- No broker interface or automatic trading surface.

Final trading is manually decided by the user.

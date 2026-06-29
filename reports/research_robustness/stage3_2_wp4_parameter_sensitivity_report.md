# Stage 3.2 WP4 Parameter Sensitivity Report

- Work package: `Stage 3.2 WP4 parameter sensitivity scenarios`
- Status: `passed`
- Benchmark: `VTI`
- Strategies: `dual_momentum, gtaa_10m_sma, static_6040`

## Parameter Scenarios

### static_6040

- `base`: CAGR `0.103067`, excess CAGR vs benchmark `-0.052813`
- `defensive_tilt`: CAGR `0.089836`, excess CAGR vs benchmark `-0.066044`
- `equity_tilt`: CAGR `0.116169`, excess CAGR vs benchmark `-0.039711`

### gtaa_10m_sma

- `lookback_8m`: CAGR `0.132561`, excess CAGR vs benchmark `-0.023319`
- `base`: CAGR `0.111547`, excess CAGR vs benchmark `-0.044334`
- `lookback_12m`: CAGR `0.114431`, excess CAGR vs benchmark `-0.041450`

### dual_momentum

- `lookback_9m`: CAGR `0.142928`, excess CAGR vs benchmark `-0.012953`
- `base`: CAGR `0.159715`, excess CAGR vs benchmark `0.003834`
- `lookback_15m_threshold_1pct`: CAGR `0.128940`, excess CAGR vs benchmark `-0.026941`

## Validation Checks

- `parameter_scenarios`: `passed` - Parameter sensitivity scenarios were generated for the Stage 3.1 parameterized strategies.
- `benchmark_comparison_preserved`: `passed` - Each parameter scenario keeps the VTI benchmark comparison.
- `base_case_reconciled`: `passed` - Base parameter scenarios reconcile to the Stage 3.1 formal backtest outputs.
- `universe_allowlist`: `passed` - All replay symbols are present in configs/universe/etf_universe.yaml.
- `research_only_boundary`: `passed` - The artifact is a research robustness report only and creates no trade ticket or execution surface.

## Limitations

- This report replays committed public ETF research artifacts only; it is not live trading evidence.
- Parameter sensitivity scenarios are research robustness checks, not trade tickets or automatic order placement.
- Final trading is manually decided by the user.

Final trading is manually decided by the user.

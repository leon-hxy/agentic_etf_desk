# Stage 3.2 WP6 In-Sample / Out-of-Sample Report

- Work package: `Stage 3.2 WP6 in-sample / out-of-sample split`
- Status: `passed`
- Benchmark: `VTI`
- In-sample window: `2019-01` to `2023-06`
- Out-of-sample window: `2023-07` to `2026-06`
- Strategies: `dual_momentum, gtaa_10m_sma, static_6040`

## Split Scenarios

### static_6040

- `full_window` `2019-01` to `2026-06`: CAGR `0.103067`, excess CAGR vs benchmark `-0.052813`
- `in_sample` `2019-01` to `2023-06`: CAGR `0.082244`, excess CAGR vs benchmark `-0.047202`
- `out_of_sample` `2023-07` to `2026-06`: CAGR `0.130044`, excess CAGR vs benchmark `-0.057276`

### gtaa_10m_sma

- `full_window` `2019-01` to `2026-06`: CAGR `0.111547`, excess CAGR vs benchmark `-0.044334`
- `in_sample` `2019-01` to `2023-06`: CAGR `0.087587`, excess CAGR vs benchmark `-0.041859`
- `out_of_sample` `2023-07` to `2026-06`: CAGR `0.159108`, excess CAGR vs benchmark `-0.028212`

### dual_momentum

- `full_window` `2019-01` to `2026-06`: CAGR `0.159715`, excess CAGR vs benchmark `0.003834`
- `in_sample` `2019-01` to `2023-06`: CAGR `0.100306`, excess CAGR vs benchmark `-0.029140`
- `out_of_sample` `2023-07` to `2026-06`: CAGR `0.228353`, excess CAGR vs benchmark `0.041033`

## Validation Checks

- `split_scenarios`: `passed` - Full, in-sample, and out-of-sample windows were generated for each Stage 3.1 strategy.
- `benchmark_comparison_preserved`: `passed` - Each split-window scenario keeps the VTI benchmark comparison.
- `full_window_reconciled`: `passed` - Full-window scenarios reconcile to the Stage 3.1 formal backtest outputs.
- `universe_allowlist`: `passed` - All replay symbols are present in configs/universe/etf_universe.yaml.
- `research_only_boundary`: `passed` - The artifact is a research robustness report only and creates no trade ticket or execution surface.

## Limitations

- This report replays committed public ETF research artifacts only; it is not live trading evidence.
- In-sample and out-of-sample scenarios are research robustness checks, not trade tickets or automatic order placement.
- Final trading is manually decided by the user.

Final trading is manually decided by the user.

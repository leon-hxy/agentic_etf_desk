# Stage 3.2 WP5 Start-Window Robustness Report

- Work package: `Stage 3.2 WP5 start-window robustness tests`
- Status: `passed`
- Benchmark: `VTI`
- Window offsets: `0 months, 6 months, 12 months, 24 months`
- Window end month: `2026-06`
- Strategies: `dual_momentum, gtaa_10m_sma, static_6040`

## Start-Window Scenarios

### static_6040

- `base_full_window` starting `2019-01`: CAGR `0.103067`, excess CAGR vs benchmark `-0.052813`
- `start_plus_6m` starting `2019-07`: CAGR `0.098194`, excess CAGR vs benchmark `-0.052543`
- `start_plus_12m` starting `2020-01`: CAGR `0.095360`, excess CAGR vs benchmark `-0.053325`
- `start_plus_24m` starting `2021-01`: CAGR `0.086535`, excess CAGR vs benchmark `-0.051617`

### gtaa_10m_sma

- `base_full_window` starting `2019-01`: CAGR `0.111547`, excess CAGR vs benchmark `-0.044334`
- `start_plus_6m` starting `2019-07`: CAGR `0.115766`, excess CAGR vs benchmark `-0.034971`
- `start_plus_12m` starting `2020-01`: CAGR `0.102753`, excess CAGR vs benchmark `-0.045931`
- `start_plus_24m` starting `2021-01`: CAGR `0.065820`, excess CAGR vs benchmark `-0.072332`

### dual_momentum

- `base_full_window` starting `2019-01`: CAGR `0.159715`, excess CAGR vs benchmark `0.003834`
- `start_plus_6m` starting `2019-07`: CAGR `0.147453`, excess CAGR vs benchmark `-0.003284`
- `start_plus_12m` starting `2020-01`: CAGR `0.171323`, excess CAGR vs benchmark `0.022638`
- `start_plus_24m` starting `2021-01`: CAGR `0.135060`, excess CAGR vs benchmark `-0.003091`

## Validation Checks

- `start_window_scenarios`: `passed` - Start-window replays were generated across the configured offsets with enough monthly observations.
- `benchmark_comparison_preserved`: `passed` - Each start-window scenario keeps the VTI benchmark comparison.
- `base_window_reconciled`: `passed` - Full-window scenarios reconcile to the Stage 3.1 formal backtest outputs.
- `universe_allowlist`: `passed` - All replay symbols are present in configs/universe/etf_universe.yaml.
- `research_only_boundary`: `passed` - The artifact is a research robustness report only and creates no trade ticket or execution surface.

## Limitations

- This report replays committed public ETF research artifacts only; it is not live trading evidence.
- Start-window robustness scenarios are research checks, not trade tickets or automatic order placement.
- Final trading is manually decided by the user.

Final trading is manually decided by the user.

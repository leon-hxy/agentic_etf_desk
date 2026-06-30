# Stage 3.2 WP3 Transaction Cost Scenario Report

- Work package: `Stage 3.2 WP3 transaction cost sensitivity scenarios`
- Status: `passed`
- Benchmark: `VTI`
- Transaction cost scenarios: `0 bps, 2 bps, 5 bps, 10 bps, 25 bps`

## Transaction Cost Scenarios

- `0bps`: 0bps applies 0 basis points of transaction cost to each unit of turnover.
- `2bps`: 2bps applies 2 basis points of transaction cost to each unit of turnover.
- `5bps`: 5bps applies 5 basis points of transaction cost to each unit of turnover.
- `10bps`: 10bps applies 10 basis points of transaction cost to each unit of turnover.
- `25bps`: 25bps applies 25 basis points of transaction cost to each unit of turnover.

## Validation Checks

- `transaction_cost_scenarios`: `passed` - Transaction-cost sensitivity replays were generated across configured cost bands.
- `benchmark_comparison_preserved`: `passed` - Each transaction-cost scenario result keeps the VTI benchmark comparison.
- `universe_allowlist`: `passed` - All replay symbols are present in configs/universe/etf_universe.yaml.
- `research_only_boundary`: `passed` - The artifact is a research robustness report only and creates no trade ticket or execution surface.

## Limitations

- This report replays committed public ETF research artifacts only; it is not a live trading cost quote.
- Transaction-cost scenarios are sensitivity analysis, not trade tickets or automatic order placement.
- Final trading is manually decided by the user.

Final trading is manually decided by the user.

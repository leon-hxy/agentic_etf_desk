# Stage 3.2 WP2 Price / Cash Scenario Report

- Work package: `Stage 3.2 WP2 price discrepancy and cash assumption scenarios`
- Status: `passed`
- Benchmark: `VTI`
- Cash proxy: `BIL`
- Short Treasury proxy: `IEF`

## Price Tolerance Scenarios

- `1 bps`: `passed`; breaches `0` of `1800` comparisons.
- `5 bps`: `passed`; breaches `0` of `1800` comparisons.
- `10 bps`: `passed`; breaches `0` of `1800` comparisons.

## Cash Assumption Scenarios

- `base_bil_cash_proxy`: base_bil_cash_proxy uses committed BIL total-return history for defensive or cash-like allocations.
- `zero_return_cash`: zero_return_cash replaces BIL returns with 0.0 monthly return while preserving strategy weights.
- `short_treasury_ief_proxy`: short_treasury_ief_proxy replaces BIL returns with IEF monthly total returns while preserving strategy weights.

## Validation Checks

- `price_discrepancy_tolerances`: `passed` - Reviewed month-end panel prices match committed raw prices across configured tolerance bands.
- `cash_assumption_scenarios`: `passed` - Base BIL, zero-return cash, and IEF proxy scenario replays were generated for every reviewed strategy.
- `benchmark_comparison_preserved`: `passed` - Each scenario result keeps the VTI benchmark comparison.
- `universe_allowlist`: `passed` - All panel symbols and cash-proxy symbols are present in configs/universe/etf_universe.yaml.
- `research_only_boundary`: `passed` - The artifact is a research robustness report only and creates no trade ticket or execution surface.

## Limitations

- This report uses committed public ETF research artifacts only; it is not a live vendor certification.
- Cash scenarios are assumption replays for robustness analysis, not trade tickets or automatic order placement.
- Final trading is manually decided by the user.

Final trading is manually decided by the user.

# Stage 5 WP3 Portfolio Weight Calculation Report

## Summary

Stage 5 WP3 added a repo-only portfolio weight calculation from the latest manual ETF holdings snapshot.

The calculator revalidates holdings symbols through `configs/universe/etf_universe.yaml`, rejects out-of-universe holdings, computes weights from manually supplied market values, and writes a normalized weight snapshot for drift checks.

Final trading is manually decided by the user.

## Safety Result

- Asset scope: ETF-only.
- Universe allowlist enforced: true.
- Broker write surface: false.
- Automatic trading surface: false.
- Repo-only calculation: true.
- risk_agent review: passed for non-actionable portfolio-state artifact scope.
- Trade tickets remain blocked from actionable delivery until risk_agent review passes.

## Artifacts

- Source holdings JSON: `data/portfolio/manual_holdings_latest.json`
- Portfolio weights CSV: `data/portfolio/portfolio_weights_latest.csv`
- Portfolio weights JSON: `data/portfolio/portfolio_weights_latest.json`
- Calculation script: `scripts/portfolio/calculate_portfolio_weights.py`
- Internal review: `reports/internal_reviews/program/stage5_wp3_portfolio_weights.json`

## Metrics

- Symbol count: 3
- Total market value: 4410.0
- Total weight: 1.0
- Largest position: VTI
- Smallest position: BIL

## Next Safe Action

Proceed to `Stage 5 WP4 drift checks`.

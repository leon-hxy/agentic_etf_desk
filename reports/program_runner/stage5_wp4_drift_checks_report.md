# Stage 5 WP4 Drift Checks Report

## Summary

Stage 5 WP4 added repo-only portfolio drift checks for the latest manual ETF portfolio weights.

The checker compares `data/portfolio/portfolio_weights_latest.json` against the `static_6040` target weights, preserves the VTI benchmark comparison context, and records whether any allocation drift breaches the configured threshold.

No trade ticket is generated in this work package. Rebalance research remains a later manual-review workflow.

Final trading is manually decided by the user.

## Safety Result

- Asset scope: ETF-only.
- Universe allowlist enforced: true.
- Broker write surface: false.
- Automatic trading surface: false.
- Trade ticket generated: false.
- Repo-only drift check: true.
- risk_agent review: passed for non-actionable drift monitoring scope.
- Trade tickets remain blocked from actionable delivery until risk_agent review passes.

## Drift Table

| Symbol | Current weight | Target weight | Drift | Direction | Breaches threshold |
|---|---:|---:|---:|---|---|
| BIL | 10.42% | 10.00% | 0.42% | above_target | false |
| BND | 32.88% | 30.00% | 2.88% | above_target | false |
| VTI | 56.70% | 60.00% | -3.30% | below_target | false |

## Metrics

- Target strategy: static_6040
- Benchmark symbol: VTI
- benchmark comparison: preserved.
- Drift status: within_threshold
- Drift threshold: 5.00%
- Max drift symbol: VTI
- Max absolute drift: 3.30%

## Artifacts

- Source weights JSON: `data/portfolio/portfolio_weights_latest.json`
- Drift JSON: `data/portfolio/portfolio_drift_latest.json`
- Drift script: `scripts/portfolio/check_portfolio_drift.py`
- Internal review: `reports/internal_reviews/program/stage5_wp4_drift_checks.json`

## Next Safe Action

Proceed to `Stage 5 WP5 rebalance research ticket`.

# Stage 5 WP1 Manual Holdings CSV Import Report

## Summary

Stage 5 WP1 added a repo-only manual holdings CSV import for the ETF research desk.

The importer normalizes user-supplied ETF symbols through `configs/universe/etf_universe.yaml`, rejects anything outside the allowlist, writes current holdings artifacts, and calculates portfolio weights from manually supplied market values.

Final trading is manually decided by the user. 最终交易由用户手动决定。

## Safety Result

- Asset scope: ETF-only.
- Universe allowlist enforced: true.
- Broker write surface: false.
- Automatic trading surface: false.
- Repo-only import: true.
- risk_agent review: passed for non-actionable holdings import scope.
- Trade tickets remain blocked from actionable delivery until risk_agent review passes.

## Artifacts

- Sample input: `data/portfolio/manual_holdings_sample.csv`
- Normalized holdings CSV: `data/portfolio/manual_holdings_latest.csv`
- Normalized holdings JSON: `data/portfolio/manual_holdings_latest.json`
- Import script: `scripts/portfolio/import_manual_holdings.py`
- Internal review: `reports/internal_reviews/program/stage5_wp1_manual_holdings_import.json`

## Next Safe Action

Proceed to `Stage 5 WP2 manual trades CSV import`.

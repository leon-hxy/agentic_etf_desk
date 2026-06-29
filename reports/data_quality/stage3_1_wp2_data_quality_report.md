# Stage 3.1 WP2 Data Quality Report

- Stage: `Stage 3.1 WP2 real data quality and monthly panel completed_internal_review`
- Status: `passed`
- Source: `yahoo_chart_public`
- Input file: `data/raw/prices_yahoo_chart.csv`
- Monthly panel: `data/processed/stage3_1_monthly_panel.csv`
- Benchmark symbol: `VTI`
- Months: `90`
- Monthly rows: `900`

## Quality Checks

- `universe_allowlist`: `passed`
- `daily_missing_data`: `passed`
- `monthly_missing_data`: `passed`
- `stale_prices`: `passed`
- `adjusted_price_coverage`: `passed`
- `benchmark_availability`: `passed`

## Symbol Coverage

| Symbol | Daily Rows | First Available | Last Available | Daily Missing | Monthly Missing | Stale Days |
|---|---:|---|---|---:|---:|---:|
| BIL | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| BND | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| DBC | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| EWJ | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| GLD | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| IEF | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| VEA | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| VNQ | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| VTI | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |
| VWO | 1881 | 2019-01-02 | 2026-06-26 | 0 | 0 | 3 |

## Safety

- No Computer Use.
- No ChatGPT review requested.
- No Feishu message sent.
- No real Hermes, OpenClaw, or Feishu gateway modification.
- No dependency installation.
- No broker surface, order placement surface, or automatic trading surface.

Final trading is manually decided by the user.

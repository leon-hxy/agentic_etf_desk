# Stage 3B Data Quality Report

- Stage: `Stage 3B data quality checks completed`
- Status: `passed`
- Input file: `data/raw/prices_sample.csv`
- Source plan: `configs/data_sources/stage3_data_sources.json`
- Primary source from Stage 3A: `stooq_daily_csv`
- Row count: `41`

## Quality Checks

- `missing_values`: `passed`
- `start_dates`: `passed`
- `adjusted_prices`: `passed`
- `abnormal_prices`: `passed`

## Symbols

| Symbol | Rows | First Available | Last Available | Missing Values |
|---|---:|---|---|---:|
| BIL | 5 | 2024-01-02 | 2024-01-08 | 0 |
| BND | 4 | 2024-01-03 | 2024-01-08 | 0 |
| DBC | 5 | 2024-01-02 | 2024-01-08 | 0 |
| EWJ | 5 | 2024-01-02 | 2024-01-08 | 0 |
| GLD | 4 | 2024-01-03 | 2024-01-08 | 0 |
| IEF | 3 | 2024-01-04 | 2024-01-08 | 0 |
| VEA | 4 | 2024-01-03 | 2024-01-08 | 0 |
| VNQ | 3 | 2024-01-04 | 2024-01-08 | 0 |
| VTI | 5 | 2024-01-02 | 2024-01-08 | 0 |
| VWO | 3 | 2024-01-04 | 2024-01-08 | 0 |

## Safety

- No Computer Use.
- No ChatGPT review requested.
- No Feishu message sent.
- No real Hermes, OpenClaw, or Feishu gateway modification.
- No dependency installation.
- No broker surface or automatic trading surface.

Final trading is manually decided by the user.

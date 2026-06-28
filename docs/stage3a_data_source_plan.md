# Stage 3A Data Source Plan

Status: completed for Stage 3A planning and wiring.

This plan selects a read-only public ETF data path for the next data quality
stage. It does not fetch live data in Stage 3A, does not add a broker surface,
and does not create order-writing behavior. Final trading is manually decided
by the user.

## Decision

Primary source: Stooq daily CSV.

Use Stooq as the Stage 3B primary candidate because it can be queried as public
read-only historical daily CSV, does not require repo-stored credentials, and
can be wrapped with local cache files for reproducible data quality checks.

Stage 3B should still treat the source as an external public feed, not a
canonical exchange feed. The quality job must cache raw responses, record the
download date, and fail closed if a requested ticker is outside the ETF-only
universe allowlist.

## Candidate Sources

| Source | Role | Strengths | Caveats |
|---|---|---|---|
| Stooq daily CSV | Primary for Stage 3B | Public read-only CSV, simple daily OHLCV access, no repo secret required | No formal project-specific service agreement in this repo; impose a conservative rate-limit and cache raw files |
| Alpha Vantage | Future fallback | Official API docs include adjusted daily time series; useful if Stooq coverage fails | Requires an API key, so Stage 3A stores no key and does not enable this path |
| SEC EDGAR | ETF metadata and filing cross-check only | Official public filings API for issuer/fund metadata | Not a price source and not a substitute for adjusted price history |
| Yahoo Finance | Manual reference only | Useful for human spot-checks | Not selected for automated ingestion because API and licensing terms need explicit review before automation |

## Source Selection Criteria

- Source must provide read-only public ETF data.
- Source must not require broker login, broker write access, or order routing.
- Source must keep all requested symbols inside `configs/universe/etf_universe.yaml`.
- Source must reject individual stocks, options, futures, crypto assets,
  leveraged ETFs, inverse ETFs, and symbols outside the allowlist.
- Source must support reproducible raw-data caching before processed panels are
  generated.
- Source must document rate-limit assumptions and retry behavior before any
  downloader is enabled.
- Source must document a licensing caveat in every data report that uses it.
- No secrets are stored in repo. If a future fallback requires an API key, the
  key must stay in untracked local runtime state and must never appear in logs,
  reports, tickets, commits, or audit output.

## Stage 3B Wiring Contract

Stage 3B may add a repo-only data quality script that reads this manifest:

- `configs/data_sources/stage3_data_sources.json`

The Stage 3B script should:

- Load the ETF-only universe allowlist first.
- Select `stooq_daily_csv` as the default source.
- Write raw fetched files under a repo data path before building derived panels.
- Record source id, request window, symbols, row counts, first available dates,
  missing values, abnormal prices, and adjustment assumptions.
- Avoid secrets, service restarts, Computer Use, real Hermes/OpenClaw changes,
  Feishu gateway changes, broker connections, and automatic trading behavior.

## Reproducibility Notes

Stage 3B should write deterministic metadata next to raw and processed outputs:

- source id
- source URL template or documented access method
- requested symbol list
- start and end dates
- downloaded-at timestamp
- row counts by symbol
- first and last available date by symbol
- adjustment assumption and quality thresholds

Generated sample artifacts must stay reproducible. If a public download changes
from one run to the next, the data quality report must state that the external
source changed and preserve the raw snapshot used by the report.

## Safety Review

- ETF-only universe allowlist remains the only approved symbol source.
- No broker write access.
- No automatic trading.
- No execution agent, order agent, broker agent, or live trader is introduced.
- No Computer Use was run.
- No real `~/.hermes`, `~/.openclaw`, or Feishu gateway was modified.
- No services were restarted.
- No dependencies were installed.
- No secrets are stored in repo.

Final trading is manually decided by the user.

## Source References

- Stooq historical data page: https://stooq.com/db/h/
- Stooq CSV endpoint pattern: https://stooq.com/q/d/l/?s=spy.us&i=d
- Alpha Vantage documentation: https://www.alphavantage.co/documentation/
- Alpha Vantage premium and rate-limit page: https://www.alphavantage.co/premium/
- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Yahoo Terms of Service: https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html

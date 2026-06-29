# Stage 3.2 WP1 Source Validation Report

- Work package: `Stage 3.2 WP1 research robustness source validation`
- Status: `passed`
- Source: `yahoo_chart_public`
- Raw rows: `18810`
- Monthly rows: `900`
- Benchmark: `VTI`

## Validation Checks

- `cache_manifest_integrity`: `passed` - Cache files, hashes, row counts, symbols, and source metadata match the committed raw price file.
- `cache_to_raw_price_match`: `passed` - Adjusted closes reconstructed from committed raw cache JSON match normalized raw CSV prices within tolerance.
- `raw_to_monthly_panel_match`: `passed` - Month-end values in the reviewed monthly panel match the committed normalized raw CSV rows.
- `universe_allowlist`: `passed` - Raw and monthly-panel symbols are all present in configs/universe/etf_universe.yaml.
- `benchmark_preserved`: `passed` - The Stage 3.1 reviewed monthly panel preserves VTI as benchmark for downstream robustness work.

## Limitations

- This is an internal consistency check against committed Yahoo Chart public JSON cache and derived repo artifacts, not a live second-vendor market-data certification.
- The report supports ETF research robustness only and is not investment advice, automatic trading, or order placement.

Final trading is manually decided by the user.

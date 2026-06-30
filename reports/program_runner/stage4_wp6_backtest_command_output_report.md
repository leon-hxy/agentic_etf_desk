# Stage 4 WP6 Backtest Command Output Report

## Summary

Stage 4 WP6 generated the repo-only GTAA backtest output for the approved Feishu command `跑一下 GTAA 回测`.

The command routes to `scripts/backtest/run_backtest.py --strategies gtaa_10m_sma` and reads repo data/universe inputs only. Asset scope remains ETF-only. It does not send live Feishu messages, does not modify real Hermes/OpenClaw/Feishu configuration, does not connect broker interfaces, does not place orders, and does not add automatic trading.

Final trading is manually decided by the user. 最终交易由用户手动决定。

## Backtest

- Strategy: `gtaa_10m_sma`
- Data source: `data/processed/price_panel.csv`
- Universe source: `configs/universe/etf_universe.yaml`
- Local report path: `reports/stage2b_backtest_report.md`
- benchmark comparison: preserved against `VTI`
- CAGR: `0.8463`
- Sharpe: `411.6711`
- Max drawdown: `0.0000`
- Trade count: `1`

## Review

- Reviewer mode: `simulated_separate_pass`
- risk_agent review: not applicable because this command produces no trade ticket or actionable trade suggestion.
- Trade-ticket outputs still require risk_agent review before actionable suggestions.
- Automatic trading surface: false.
- Broker write surface: false.
- Live runtime modification: false.

## Next Safe Action

Proceed to `Stage 4 WP7 OpenClaw agents draft or safe integration plan`.

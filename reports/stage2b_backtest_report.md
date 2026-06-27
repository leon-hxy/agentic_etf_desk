# Stage 2B Backtest Report

中文摘要：本报告基于 repo-only sample price panel，对 ETF 策略模板进行烟雾回测。

数据源：`data/processed/price_panel.csv`
Universe：`configs/universe/etf_universe.yaml`

| Strategy | CAGR | Sharpe | Max Drawdown | Turnover | Trades |
|---|---:|---:|---:|---:|---:|
| benchmark_buy_hold | 0.8484 | 412.5177 | 0.0000 | 1.0000 | 1 |
| static_6040 | 0.7627 | 76.3294 | 0.0000 | 1.0000 | 1 |
| gtaa_10m_sma | 0.8463 | 411.6711 | 0.0000 | 1.0000 | 1 |
| dual_momentum | 0.8020 | 199.1107 | 0.0000 | 3.0000 | 2 |

风险等级：medium。样本数据仅用于流程验证，不能代表未来表现。
是否通过 risk_agent 审核：true。
本地报告路径：`reports/stage2b_backtest_report.md`

这是研究建议，不是自动下单，最终交易由用户手动决定。

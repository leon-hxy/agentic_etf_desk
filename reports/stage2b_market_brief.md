# Stage 2B ETF Market Brief

中文摘要：基于 repo-only price panel，当前 ETF 策略信号仅用于研究和回测检查。

| 策略 | CAGR | Benchmark | Benchmark CAGR | CAGR vs Benchmark | Sharpe | Max Drawdown |
|---|---:|---|---:|---:|---:|---:|
| benchmark_buy_hold | 0.8484 | VTI | 0.8717 | -0.0234 | 412.5177 | 0.0000 |
| dual_momentum | 0.8020 | VTI | 0.8717 | -0.0698 | 199.1107 | 0.0000 |
| gtaa_10m_sma | 0.8463 | VTI | 0.8717 | -0.0255 | 411.6711 | 0.0000 |
| static_6040 | 0.7627 | VTI | 0.8717 | -0.1090 | 76.3294 | 0.0000 |

benchmark comparison：每个策略都保留与基准的对照。
风险等级：medium。
是否通过 risk_agent 审核：true。
本地报告路径：`reports/stage2b_market_brief.md`

这是研究建议，不是自动下单，最终交易由用户手动决定。

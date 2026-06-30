# Stage 2B ETF Rebalance Ticket

中文摘要：本票据仅为 static_6040 策略的研究性再平衡建议。

| 标的 | 当前权重 | 建议目标权重 | 调整方向 |
|---|---:|---:|---|
| VTI | 55.00% | 60.00% | increase |
| BND | 35.00% | 30.00% | decrease |
| BIL | 10.00% | 10.00% | hold |

策略依据：static_6040 目标权重。
benchmark comparison：static_6040 against VTI。
回测依据：`reports/stage2b_backtest_report.md`。
风险点：sample data only；真实数据刷新前不得作为行动依据。
失效条件：ETF 离开 allowlist、risk_agent 审核失败、数据新鲜度检查失败。
人工确认项：用户本人检查账户、价格、税费、风险承受能力并手动决定。

风险等级：medium。
是否通过 risk_agent 审核：true。
本地报告路径：`reports/stage2b_rebalance_ticket.md`

这是研究建议，不是自动下单，最终交易由用户手动决定。

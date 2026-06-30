# Feishu Router Draft

This is a repo-only Hermes/Feishu router draft. It does not modify real Feishu gateway config and does not install a Hermes skill.

Stage 4 WP1 implementation entrypoint: `scripts/hermes/feishu_command_router.py`.

The implementation returns JSON route plans for allowed ETF research commands. It does not send Feishu messages, does not modify real `~/.hermes`, does not modify real Feishu gateway config, does not restart services, and does not connect broker interfaces.

Hermes 是唯一总助理 and should answer in concise mobile-readable Feishu messages:

1. Short Chinese summary.
2. Risk level.
3. risk_agent review status.
4. Local report path such as `reports/stage2b_weekly_report.md`.
5. Manual trading reminder: 最终交易由用户手动决定。

## Command Mapping

| User text | Repo-only action |
|---|---|
| 今天 ETF 有什么信号？ | `scripts/reports/generate_market_brief.py` |
| 跑一下 GTAA 回测 | `scripts/backtest/run_backtest.py --strategies gtaa_10m_sma` |
| 生成本月 ETF 再平衡建议 | `scripts/reports/generate_rebalance_ticket.py` |
| 检查 ETF universe 有没有异常 | `scripts/data/validate_universe.py` |
| 生成周报 | `scripts/reports/generate_weekly_report.py` |

The router must reject unknown commands, automatic order requests, broker access requests, individual stocks, options, futures, crypto assets, leveraged ETFs, inverse ETFs, and real runtime configuration changes.

No real Computer Use relay is executed by this draft. Computer Use 未真实执行。

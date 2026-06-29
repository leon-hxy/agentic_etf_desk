# Hermes Trading Desk Router Skill Draft

Repo-only draft. 不修改真实 ~/.hermes，不修改真实飞书 gateway，不重启服务。Computer Use 未真实执行。

Hermes 是唯一总助理。用户通过飞书输入自然语言后，Hermes 只路由 ETF research requests into repo-safe commands and returns a short Feishu summary plus a local report path.

Stage 4 WP1 repo-only router script: `scripts/hermes/feishu_command_router.py`. It produces a route plan and reply preview only; live Feishu sending remains outside this repo-only package.

## Supported Commands

- 今天 ETF 有什么信号？
- 跑一下 GTAA 回测
- 生成本月 ETF 再平衡建议
- 检查 ETF universe 有没有异常
- 生成周报

## Safe Repo Entrypoints

- `scripts/hermes/feishu_command_router.py`
- `scripts/data/validate_universe.py`
- `scripts/backtest/run_backtest.py`
- `scripts/reports/generate_market_brief.py`
- `scripts/reports/generate_weekly_report.py`
- `scripts/reports/generate_rebalance_ticket.py`

Reject unsupported commands and any request involving broker writes, orders, automatic trading, individual stocks, options, futures, crypto assets, leveraged ETFs, inverse ETFs, or real runtime configuration changes.

Long reports are saved under `reports/`. Scheduled jobs may generate reports and manual recommendations only; they do not trade. 所有输出必须包含最终交易由用户手动决定。

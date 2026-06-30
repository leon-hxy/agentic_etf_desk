# Hermes Draft Configs

These files are repo-only drafts and 不修改真实 ~/.hermes. They do not modify the real Feishu gateway and do not restart Hermes.

Hermes 是唯一总助理. The router draft may call repo-safe scripts that generate research, backtests, risk review, reports, and manual recommendation tickets.

Stage 4 WP1 adds the repo-only command router at `scripts/hermes/feishu_command_router.py`. It returns a deterministic JSON route plan and Feishu reply preview; it does not send a live Feishu message, does not edit runtime config, and does not run broker or order-writing interfaces.

Supported Feishu commands:

- 今天 ETF 有什么信号？
- 跑一下 GTAA 回测
- 生成本月 ETF 再平衡建议
- 检查 ETF universe 有没有异常
- 生成周报

All returned summaries must include a local report path and the reminder: 最终交易由用户手动决定。Computer Use 未真实执行。

Unsupported requests, broker/order language, non-ETF assets, leveraged ETFs, inverse ETFs, and live runtime modification requests must be rejected without a repo entrypoint.

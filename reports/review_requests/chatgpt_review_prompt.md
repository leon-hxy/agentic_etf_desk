请审核公开 GitHub repo：

https://github.com/leon-hxy/agentic_etf_desk

请读取：

- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `AGENTS.md`
- `docs/security_policy.md`

请审核 `review_target_commit`：`d40315aea238db28b1bdf857efa4052b250634c4`。

请根据 `reports/review_requests/latest.json` 中的 `review_target_commit` 和 review_files 审核 Stage 2B completed。
不要把旧阶段 commit 当作本阶段的审核目标。

Stage 2B completed review_files：

- `strategies/benchmark_buy_hold/README.md`
- `strategies/benchmark_buy_hold/strategy.yaml`
- `strategies/static_6040/README.md`
- `strategies/static_6040/strategy.yaml`
- `strategies/equal_weight_etf/README.md`
- `strategies/equal_weight_etf/strategy.yaml`
- `strategies/gtaa_10m_sma/README.md`
- `strategies/gtaa_10m_sma/strategy.yaml`
- `strategies/dual_momentum/README.md`
- `strategies/dual_momentum/strategy.yaml`
- `strategies/time_series_momentum_vol_target/README.md`
- `strategies/time_series_momentum_vol_target/strategy.yaml`
- `strategies/inverse_volatility_allocation/README.md`
- `strategies/inverse_volatility_allocation/strategy.yaml`
- `strategies/etf_mean_reversion_sandbox/README.md`
- `strategies/etf_mean_reversion_sandbox/strategy.yaml`
- `scripts/backtest/run_backtest.py`
- `scripts/backtest/metrics.py`
- `scripts/backtest/portfolio.py`
- `scripts/backtest/strategies.py`
- `scripts/backtest/report_writer.py`
- `scripts/reports/generate_market_brief.py`
- `scripts/reports/generate_weekly_report.py`
- `scripts/reports/generate_rebalance_ticket.py`
- `scripts/reports/generate_portfolio_journal.py`
- `configs/openclaw/openclaw_agents_draft.json`
- `configs/openclaw/README.md`
- `configs/hermes/trading_desk_router_skill.md`
- `configs/hermes/feishu_router_draft.md`
- `configs/hermes/README.md`
- `reports/stage2b_backtest_report.md`
- `reports/stage2b_backtest_report.json`
- `reports/stage2b_backtest_report.html`
- `reports/stage2b_market_brief.md`
- `reports/stage2b_weekly_report.md`
- `reports/stage2b_rebalance_ticket.md`
- `journals/stage2b_portfolio_journal.md`
- `reports/trade_ticket_template.md`
- `journals/portfolio_journal_template.md`
- `tests/safety/test_strategy_templates_safety.py`
- `tests/safety/test_backtest_safety.py`
- `tests/safety/test_openclaw_agents_safety.py`
- `tests/safety/test_hermes_router_safety.py`
- `tests/smoke/test_backtest_smoke.py`
- `tests/smoke/test_reports_smoke.py`

重点检查：

- ETF-only 是否保持。
- 是否有自动下单 surface。
- 是否有 secrets 泄漏。
- 是否有真实 `~/.hermes` / `~/.openclaw` 修改迹象。
- safety tests 和 smoke tests 是否合理。
- public repo hygiene 是否保持。
- 是否可以进入下一阶段。

请输出：

- 通过/不通过。
- 高风险问题。
- 必须修复项。
- 建议下一步。

提示：repo 是 public，不需要 GitHub connector。
提醒：本系统不会自动下单，最终交易由用户手动决定。

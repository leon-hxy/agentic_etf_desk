# Trade Recommendation Ticket Template

Status: draft template for research review only.

## 标的

ETF symbols must be present in `configs/universe/etf_universe.yaml` with `is_allowed=true`.

## 当前权重

Record current portfolio weights from the user's manually supplied portfolio state.

## 建议目标权重

Record strategy target weights after benchmark comparison and risk review.

## 调整方向

Use increase, decrease, or hold. Do not generate order instructions.

## 策略依据

Name the strategy, signal date, universe source, and benchmark.

## 回测依据

Reference `reports/stage2b_backtest_report.md` or another repo report path.

## 风险点

List concentration, drawdown, data freshness, transaction-cost, and model-risk notes.

## 失效条件

Examples: ETF leaves allowlist, data fails validation, risk_agent review fails, or market regime changes.

## 人工确认项

The user must manually confirm symbol eligibility, account constraints, prices, tax impact, and suitability.

## Required Disclaimer

This is research advice only, not automatic order placement. Final trading is manually decided by the user.

这是研究建议，不是自动下单，最终交易由用户手动决定。

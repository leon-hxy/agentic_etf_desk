# Stage 3D Strategy Evidence Report

- Stage: `Stage 3D strategy evidence report`
- Status: `passed`
- Source validation report: `reports/backtest_validation/stage3c_backtest_validation_report.json`
- Data boundary: Sample data only; not investment basis.

## Validation Checks

- `stage3c_validation_passed`: `passed`
- `required_strategies_present`: `passed`
- `benchmark_comparison_present`: `passed`
- `sample_boundary_documented`: `passed`
- `manual_trading_notice_present`: `passed`
- `risk_and_limitations_documented`: `passed`

## Strategy Evidence

| Strategy | Benchmark | Strategy CAGR | Benchmark CAGR | Excess CAGR | Drawdown Gap | Trades | Turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| Buy-and-Hold Benchmark | VTI | 84.84% | 87.17% | -2.34% | 0.00% | 1 | 1.00 |
| 60/40 Static Allocation | VTI | 76.27% | 87.17% | -10.90% | 0.00% | 1 | 1.00 |
| GTAA 10-Month SMA | VTI | 84.63% | 87.17% | -2.55% | 0.00% | 1 | 1.00 |
| Dual Momentum | VTI | 80.20% | 87.17% | -6.98% | 0.00% | 2 | 3.00 |

## Risk And Limitations

### Buy-and-Hold Benchmark

Buy-and-Hold Benchmark produced 84.84% sample CAGR versus 87.17% for VTI, with -2.34% excess CAGR and 0.00% drawdown gap.

Risk notes:
- Backtest evidence depends on a short sample panel and may not represent live market regimes.
- Benchmark comparison is against VTI only; broader benchmark selection should be reviewed before production use.
- Buy-and-Hold benchmark remains fully exposed to broad ETF market drawdowns.

Limitation notes:
- Sample data only; not investment basis.
- Smoke evidence validates reporting and comparison plumbing, not investment merit.
- Formal use requires reviewed real data, source terms confirmation, and a separate major-stage review.

### 60/40 Static Allocation

60/40 Static Allocation produced 76.27% sample CAGR versus 87.17% for VTI, with -10.90% excess CAGR and 0.00% drawdown gap.

Risk notes:
- Backtest evidence depends on a short sample panel and may not represent live market regimes.
- Benchmark comparison is against VTI only; broader benchmark selection should be reviewed before production use.
- Static allocation may dilute equity upside and remains exposed to bond-equity correlation shifts.

Limitation notes:
- Sample data only; not investment basis.
- Smoke evidence validates reporting and comparison plumbing, not investment merit.
- Formal use requires reviewed real data, source terms confirmation, and a separate major-stage review.

### GTAA 10-Month SMA

GTAA 10-Month SMA produced 84.63% sample CAGR versus 87.17% for VTI, with -2.55% excess CAGR and 0.00% drawdown gap.

Risk notes:
- Backtest evidence depends on a short sample panel and may not represent live market regimes.
- Benchmark comparison is against VTI only; broader benchmark selection should be reviewed before production use.
- Signal timing can lag rapid reversals and may underperform during choppy markets.

Limitation notes:
- Sample data only; not investment basis.
- Smoke evidence validates reporting and comparison plumbing, not investment merit.
- Formal use requires reviewed real data, source terms confirmation, and a separate major-stage review.

### Dual Momentum

Dual Momentum produced 80.20% sample CAGR versus 87.17% for VTI, with -6.98% excess CAGR and 0.00% drawdown gap.

Risk notes:
- Backtest evidence depends on a short sample panel and may not represent live market regimes.
- Benchmark comparison is against VTI only; broader benchmark selection should be reviewed before production use.
- Higher turnover increases sensitivity to transaction costs and implementation assumptions.
- Signal timing can lag rapid reversals and may underperform during choppy markets.

Limitation notes:
- Sample data only; not investment basis.
- Smoke evidence validates reporting and comparison plumbing, not investment merit.
- Formal use requires reviewed real data, source terms confirmation, and a separate major-stage review.

## Safety

- No Computer Use.
- No ChatGPT review requested.
- No Feishu message sent.
- No real Hermes, OpenClaw, or Feishu gateway modification.
- No dependency installation.
- No broker interface or automatic trading surface.

Final trading is manually decided by the user.

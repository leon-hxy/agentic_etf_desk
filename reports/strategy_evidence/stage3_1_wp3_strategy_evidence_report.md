# Stage 3.1 WP3 Strategy Evidence Package

- Status: `passed`
- Source backtest report: `reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json`
- Data boundary: real public ETF monthly panel; research validation only.

## Strategy Evidence

### Benchmark Buy Hold

Benchmark Buy Hold generated 15.59% CAGR versus 15.59% for VTI, with -0.00% excess CAGR.

Risk notes:
- Real public historical data can contain vendor revisions and should be independently reviewed before production use.
- Backtest evidence is research only and does not authorize automatic trading or order placement.
- Benchmark buy-and-hold remains fully exposed to broad equity ETF drawdowns.

Limitation notes:
- Evidence uses public ETF historical data cached in the repo and remains subject to public-source availability and terms.
- No broker connection, live execution, or order-routing capability is included.
- Final trading is manually decided by the user.

### Static 6040

Static 6040 generated 10.31% CAGR versus 15.59% for VTI, with -5.28% excess CAGR.

Risk notes:
- Real public historical data can contain vendor revisions and should be independently reviewed before production use.
- Backtest evidence is research only and does not authorize automatic trading or order placement.
- Static 60/40 allocation can be exposed to bond-equity correlation shifts.

Limitation notes:
- Evidence uses public ETF historical data cached in the repo and remains subject to public-source availability and terms.
- No broker connection, live execution, or order-routing capability is included.
- Final trading is manually decided by the user.

### Gtaa 10M Sma

Gtaa 10M Sma generated 11.15% CAGR versus 15.59% for VTI, with -4.43% excess CAGR.

Risk notes:
- Real public historical data can contain vendor revisions and should be independently reviewed before production use.
- Backtest evidence is research only and does not authorize automatic trading or order placement.
- Higher turnover increases sensitivity to transaction costs, slippage, and manual execution timing.
- Trend and momentum signals can lag reversals and may underperform in sideways markets.

Limitation notes:
- Evidence uses public ETF historical data cached in the repo and remains subject to public-source availability and terms.
- No broker connection, live execution, or order-routing capability is included.
- Final trading is manually decided by the user.

### Dual Momentum

Dual Momentum generated 15.97% CAGR versus 15.59% for VTI, with 0.38% excess CAGR.

Risk notes:
- Real public historical data can contain vendor revisions and should be independently reviewed before production use.
- Backtest evidence is research only and does not authorize automatic trading or order placement.
- Higher turnover increases sensitivity to transaction costs, slippage, and manual execution timing.
- Trend and momentum signals can lag reversals and may underperform in sideways markets.

Limitation notes:
- Evidence uses public ETF historical data cached in the repo and remains subject to public-source availability and terms.
- No broker connection, live execution, or order-routing capability is included.
- Final trading is manually decided by the user.

## Safety

- No Computer Use.
- No ChatGPT review requested.
- No broker interface, broker write access, order placement, or automatic trading surface.

Final trading is manually decided by the user.

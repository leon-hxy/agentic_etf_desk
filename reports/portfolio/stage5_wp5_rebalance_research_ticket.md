# Stage 5 WP5 Rebalance Research Ticket

This ticket is research advice, not automatic order placement. Final trading is manually decided by the user.

## Recommendation Table

| Symbol | Current weight | Target weight | Suggested action | Estimated value |
|---|---:|---:|---|---:|
| BIL | 10.42% | 10.00% | decrease | $18.50 |
| BND | 32.88% | 30.00% | decrease | $127.00 |
| VTI | 56.70% | 60.00% | increase | $145.50 |

## Risk Gate

- risk_agent review: passed.
- Actionable suggestion shown only after risk_agent review: true.
- Broker write surface: false.
- Automatic trading surface: false.
- Order placement surface: false.
- Universe allowlist enforced: true.

## Strategy Context

- Strategy: static_6040.
- Benchmark symbol: VTI.
- benchmark comparison: preserved.
- Drift status: within_threshold.
- Drift threshold: 5.00%.
- Max drift symbol: VTI.
- Max absolute drift: 3.30%.

## Manual Checks

- User must manually verify account holdings, prices, tax impact, liquidity, and risk tolerance before acting.
- The repo does not connect broker write interfaces and does not place orders.

Final trading is manually decided by the user.

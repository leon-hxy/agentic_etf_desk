# Stage 3.2 WP7 Strategy Conclusion Grading Report

- Work package: `Stage 3.2 WP7 strategy conclusion grading`
- Status: `passed`
- Benchmark: `VTI`
- Next work package: `Stage 4 WP1 Feishu command routing for ETF research`

## Strategy Grades

### dual_momentum

- Grade: `C`
- Conclusion bucket: `watchlist_only`
- Robustness score: `54`
- Benchmark result: `mixed_or_benchmark_lagging_evidence`
- Full-window excess CAGR vs benchmark: `0.003834`
- Out-of-sample excess CAGR vs benchmark: `0.041033`
- Actionable trade ticket: `false`
- Decision boundary: manual user decision required

### gtaa_10m_sma

- Grade: `D`
- Conclusion bucket: `do_not_prioritize`
- Robustness score: `23`
- Benchmark result: `benchmark_lagging_evidence`
- Full-window excess CAGR vs benchmark: `-0.044334`
- Out-of-sample excess CAGR vs benchmark: `-0.028212`
- Actionable trade ticket: `false`
- Decision boundary: manual user decision required

### static_6040

- Grade: `D`
- Conclusion bucket: `do_not_prioritize`
- Robustness score: `19`
- Benchmark result: `benchmark_lagging_evidence`
- Full-window excess CAGR vs benchmark: `-0.052813`
- Out-of-sample excess CAGR vs benchmark: `-0.057276`
- Actionable trade ticket: `false`
- Decision boundary: manual user decision required

## Validation Checks

- `strategy_grades`: `passed` - Every Stage 3.1 strategy received a non-actionable research grade.
- `benchmark_comparison_preserved`: `passed` - Strategy grading uses VTI benchmark-relative evidence from the robustness reports.
- `robustness_inputs_present`: `passed` - WP1 through WP6 source reports are present and passed.
- `universe_allowlist`: `passed` - All symbols referenced by the grading inputs are present in configs/universe/etf_universe.yaml.
- `research_only_boundary`: `passed` - The grading report creates no trade ticket, execution path, or automatic order placement.

## Safety Boundary

- This is research advice, not automatic order placement, and final trading is manually decided by the user.
- No broker write access, execution agent, order placement, real runtime configuration change, or Feishu send was performed.

## Limitations

- This report grades strategy research evidence only; it is not live trading evidence.
- No strategy is promoted to an actionable trade ticket by this work package.
- This is research advice, not automatic order placement, and final trading is manually decided by the user.
- Final trading is manually decided by the user.

Final trading is manually decided by the user.

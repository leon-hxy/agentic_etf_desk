# Codex Handoff

## Current Stage

Stage 3.1 WP2 real data quality and monthly panel completed internal review.

## Scope

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

It must not be split into user-visible Stage 3.1A, Stage 3.1B, Stage 3.1C, Stage 3.1D, Stage 3.1E, or Stage 3.1F stages.

## Work Package Result

- WP1 real data ingestion and cache: `completed_internal_review`.
- WP2 real data quality and monthly panel: `completed_internal_review`.
- WP3 formal backtest and evidence package: `ready`.

WP2 used Codex internal review only. No ChatGPT review was requested and no routine user notification was sent.

Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.

## Commit Metadata

- `review_target_commit`: `f8b9967c01d563fa197b6aba734364eb68d356c7`
- `current_repo_head`: `f8b9967c01d563fa197b6aba734364eb68d356c7`
- `handoff_commit`: `null` until a later commit can point back to this handoff.

## Monthly Panel

- Source: `yahoo_chart_public`
- Public source: `Yahoo Chart public JSON`
- Monthly panel: `data/processed/stage3_1_monthly_panel.csv`
- Data quality report: `reports/data_quality/stage3_1_wp2_data_quality_report.json`
- Benchmark symbol: `VTI`
- Month count: `90`
- Monthly rows: `900`
- Symbols: `BIL, BND, DBC, EWJ, GLD, IEF, VEA, VNQ, VTI, VWO`

## Artifacts

- Stage manifest: `ops/stages/stage3_1.yaml`
- Runner state: `ops/runners/stage3_1_runner_state.json`
- Runner prompt: `configs/codex_automation/stage3_1_runner_prompt.md`
- Internal review: `reports/internal_reviews/stage3_1/wp2_real_data_quality_and_monthly_panel.json`

## Safety Checklist

- Modified real `~/.hermes`: false.
- Modified real `~/.openclaw`: false.
- Modified real Feishu gateway: false.
- Restarted Hermes/OpenClaw: false.
- Installed dependencies: false.
- Ran Computer Use: false.
- Connected broker: false.
- Added broker write access: false.
- Added order placement code: false.
- Added automatic trading surface: false.

Final trading is manually decided by the user.

## Verification

- Final verification pending in this Codex run before commit/push.

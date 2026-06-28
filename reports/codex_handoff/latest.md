# Codex Handoff

## Current Stage

Stage 3.1 WP1 real data ingestion and cache completed internal review.

## Scope

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

It must not be split into user-visible Stage 3.1A, Stage 3.1B, Stage 3.1C, Stage 3.1D, Stage 3.1E, or Stage 3.1F stages.

## Work Package Result

- WP1 real data ingestion and cache: `completed_internal_review`.
- WP2 real data quality and monthly panel: `ready`.
- WP3 formal backtest and evidence package: `planned`.

WP1 used Codex internal review only. No ChatGPT review was requested and no routine user notification was sent.

Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.

## Commit Metadata

- `review_target_commit`: `e5a2a603b4cdb2d8b439f705f84331ad297edb88`
- `current_repo_head`: `e5a2a603b4cdb2d8b439f705f84331ad297edb88`
- `handoff_commit`: `null` until a later commit can point back to this handoff.

## Real Data Cache

- Source: `yahoo_chart_public`
- Public source: `Yahoo Chart public JSON`
- Raw file: `data/raw/prices_yahoo_chart.csv`
- Cache manifest: `data/cache/yahoo_chart_public/cache_manifest.json`
- Row count: `18810`
- Symbols: `VTI, VEA, VWO, EWJ, BND, IEF, BIL, GLD, VNQ, DBC`

## Artifacts

- Stage manifest: `ops/stages/stage3_1.yaml`
- Runner state: `ops/runners/stage3_1_runner_state.json`
- Runner prompt: `configs/codex_automation/stage3_1_runner_prompt.md`
- Internal review: `reports/internal_reviews/stage3_1/wp1_real_data_ingestion_and_cache.json`

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

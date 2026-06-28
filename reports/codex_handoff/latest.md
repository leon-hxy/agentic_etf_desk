# Codex Handoff

## Current Stage

Stage 3.1 Real ETF Historical Data MVP scope consolidated.

## Scope

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

It must not be split into user-visible Stage 3.1A, Stage 3.1B, Stage 3.1C,
Stage 3.1D, Stage 3.1E, or Stage 3.1F stages.

## Internal Work Packages

- WP1 real data ingestion and cache.
- WP2 real data quality and monthly panel.
- WP3 formal backtest and evidence package.

WP1, WP2, and WP3 use Codex internal review only. Codex must not request
ChatGPT review for WP1, WP2, or WP3. Codex must not notify the user for routine
work package completion.

Only after WP3 completes and both `reports/major_reviews/stage3_1/latest.md`
and `reports/major_reviews/stage3_1/latest.json` exist may Codex notify the
user through Feishu that the user can request manual ChatGPT major-stage review.

## Artifacts

- Stage manifest: `ops/stages/stage3_1.yaml`
- Runner state: `ops/runners/stage3_1_runner_state.json`
- Runner prompt: `configs/codex_automation/stage3_1_runner_prompt.md`
- Internal review template: `reports/internal_reviews/stage3_1/wp_internal_review_template.md`
- Internal review template JSON: `reports/internal_reviews/stage3_1/wp_internal_review_template.json`
- Major review template: `reports/major_reviews/stage3_1/template.md`
- Major review template JSON: `reports/major_reviews/stage3_1/template.json`

## Base

- Base branch: `main`
- Base main head: `d62f301ce7d6ca993fb29bc3a545104661b29ab4`
- Historical Stage 3 package `review_target_commit`: `9c8ad5841bf30585575b78511e30e21b661f5774`
- Historical Stage 3 `latest_branch_head`: `207f5957fa2cc6b5dadd6eb535f78139225b113d`
  includes finalization fixes.
- Historical Stage 3 `current_branch_head`: `207f5957fa2cc6b5dadd6eb535f78139225b113d`
  includes finalization fixes.
- Historical Stage 3 package `review_target_commit` is the Stage 3 major package audit target.
- Stage 3 closeout remains sample-data pipeline validation only, not formal investment evidence, and not investment basis.
- Construction branch: `stage/stage3.1-real-etf-data`
- WP1 business code started: false.

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
- Final trading is manually decided by the user.

## Tests

- `python3 -m unittest`: pass.
- `python3 scripts/safety/check_forbidden_surfaces.py`: pass.
- `python3 scripts/safety/check_secret_leaks.py`: pass.
- `python3 scripts/safety/check_public_repo_hygiene.py`: pass.
- `python3 scripts/safety/check_universe_only.py`: pass.
- `git diff --check`: pass.

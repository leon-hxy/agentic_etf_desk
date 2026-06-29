# Codex Handoff

## Current Stage

Stage 3.1 major review package is ready.

Stage 3.1 is one major stage: Real ETF Historical Data MVP.

## Program Runner

- Program Runner status: `next_work_package_ready`.
- Current major stage: `Stage 5`.
- Current work package: `Stage 5 WP2 manual trades CSV import`.
- Last completed work package: `Stage 5 WP1 manual holdings CSV import`.
- Stage 3.1 prerequisite recovered: true.
- Reconciliation report: `reports/program_runner/stage3_1_prereq_reconciliation.json`.
- Next safe action: resume Stage 5 WP2 manual trades CSV import.

## Work Package Result

- WP1 real data ingestion and cache: `completed_internal_review`.
- WP2 real data quality and monthly panel: `completed_internal_review`.
- WP3 formal backtest and evidence package: `completed_internal_review`.

WP3 used Codex internal review only. No ChatGPT review was requested or sent by Codex.

Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.

The Stage 3.1 major review package is ready for the user to request manual ChatGPT major-stage review.

## Commit Metadata

- `review_target_commit`: `35348bc8c38df09562190f3c049142a252cbc85d`
- `current_repo_head`: `35348bc8c38df09562190f3c049142a252cbc85d`

## Stage 5 WP1 Result

- Manual holdings importer: `scripts/portfolio/import_manual_holdings.py`.
- Normalized holdings: `data/portfolio/manual_holdings_latest.json`.
- Work package report: `reports/program_runner/stage5_wp1_manual_holdings_import_report.json`.
- Internal review: `reports/internal_reviews/program/stage5_wp1_manual_holdings_import.json`.
- Codex requested ChatGPT review: false.
- User notification sent: false.

## Safety Checklist

- Modified real `~/.hermes`: false.
- Modified real `~/.openclaw`: false.
- Modified real Feishu gateway: false.
- Restarted Hermes/OpenClaw: false.
- Installed dependencies: false.
- Ran Computer Use: false.
- Connected broker: false.
- Added broker write surface: false.
- Added order placement code: false.
- Added automatic trading surface: false.

Final trading is manually decided by the user.

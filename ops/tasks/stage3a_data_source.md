# Stage 3A Data Source Plan

status: completed_internal_review
stage: Stage 3A completed_internal_review
branch: stage/stage3-data-backtest
review_level: small_stage
repo-only

## Objective

Create the real ETF data source integration plan using read-only public ETF data.
This stage is planning and wiring only; it must not start live trading, broker
integration, or any order-writing behavior.

## Review

Small-stage review: Codex self-review.

Major-stage review: manual ChatGPT review only after the Stage 3E package is
complete.

## Scope

- Identify candidate read-only public ETF data sources.
- Define source selection criteria, rate-limit notes, reproducibility needs,
  and licensing caveats.
- Keep data access read-only and public.
- Preserve ETF-only constraints.
- Do not implement Stage 3B, 3C, or 3D work in this task.

## Completion Evidence

- Data source plan: `docs/stage3a_data_source_plan.md`.
- Machine-readable source manifest: `configs/data_sources/stage3_data_sources.json`.
- Formal internal review: `reports/internal_reviews/stage3/stage3a_data_source.md`.
- Codex self-review: `reports/internal_reviews/stage3a_data_source_codex_self_review.md`.
- Test results: `reports/stage3a_safety_test_results.md`.
- Handoff: `reports/codex_handoff/latest.md`.
- Loop state: `ops/state/loop_state.json`.

## Result

- Primary Stage 3B source candidate: Stooq daily CSV.
- Future fallback candidate: Alpha Vantage daily adjusted API, not enabled in
  this stage because it requires a local API key.
- Metadata-only supplement: SEC EDGAR APIs.
- Manual reference only: Yahoo Finance.
- ChatGPT review was not requested for this small stage.
- No Feishu message was sent for this small stage.
- Internal review status: `completed_internal_review`.

## Safety

- Do not run Computer Use.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify the real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not connect broker write interfaces.
- Do not write secrets, tokens, auth values, Feishu credentials, provider keys,
  or broker credentials.
- Final trading is manually decided by the user.

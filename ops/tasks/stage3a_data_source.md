# Stage 3A Data Source Plan

status: planned
stage: Stage 3A
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

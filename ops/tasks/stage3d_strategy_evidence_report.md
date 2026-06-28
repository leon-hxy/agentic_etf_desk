# Stage 3D Strategy Evidence Report

status: planned
stage: Stage 3D
branch: stage/stage3-data-backtest
review_level: small_stage
repo-only

## Objective

Create the Stage 3 evidence package comparing GTAA, Dual Momentum, 60/40, and
Buy-and-Hold using the validated Stage 3 data and backtest path.

## Review

Small-stage review: Codex self-review.

Major-stage review: manual ChatGPT review only after the Stage 3E package is
complete.

## Scope

- Produce comparable evidence for GTAA.
- Produce comparable evidence for Dual Momentum.
- Produce comparable evidence for 60/40.
- Produce comparable evidence for Buy-and-Hold.
- Include benchmark comparison for every strategy.
- Include risk and limitation notes.
- Do not ask ChatGPT for review until Stage 3E.

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

# Review Governance

Stage 2F replaces the previous ChatGPT Computer Use relay idea with a simpler
review governance model.

Stage 2F.1 adds branch governance for Stage 3. `main` remains the stable branch
for major-stage reviewed states, `stage/*` branches hold major-stage
construction, and optional `task/*` branches hold isolated small-stage work.

## Decision

ChatGPT Computer Use automatic review route is deprecated.

The project now uses two review levels plus one internal finalization process:

- Small-stage Codex self-review.
- Major package finalization by Codex.
- Major-stage ChatGPT review.

ChatGPT review is manual and user-initiated. Codex may generate public review
materials in the repo, but it must not open ChatGPT, send prompts, click UI, or
run Computer Use for review delivery without a new explicit approval and a new
task scope.

## Minor Stages

Minor stages are the construction slices that build Stage 3 evidence. In Stage 3
these are Stage 3A through Stage 3D. Codex reviews each minor stage internally
and does not ask ChatGPT to review them one by one.

Required evidence:

- Updated `reports/codex_handoff/latest.md`.
- Updated `reports/codex_handoff/latest.json`.
- Updated `reports/review_requests/latest.md`.
- Updated `reports/review_requests/latest.json`.
- Safety and smoke tests appropriate to the changed surface.
- `git diff --check`.
- Clean `git status` before final response.

The self-review must check ETF-only constraints, no broker/write execution
surface, no secrets, no real Hermes/OpenClaw/Feishu gateway changes unless
explicitly approved, and final manual trading language where relevant.

## Major Package Finalization

Major package finalization is an internal Codex process that starts after the
major review package is generated and before the user is asked whether to
request ChatGPT review. It is not a user-review stage and it is not a ChatGPT
review target.

Finalization includes repo-only fixes such as:

- Feishu major-gate notification preparation or repair.
- Handoff refreshes.
- Review request refreshes.
- Notification preview refreshes.
- `review_target_commit` consistency fixes.
- Major review package consistency or safety repairs.

Stage 3F and Stage 3F.1 are classified as `major_gate_finalization` fixes. They
must be internally reviewed by Codex, not exposed as independent stages for the
user or ChatGPT to approve.

Codex must complete consistency checks before any major-gate Feishu notification
is considered current:

- The major review package, handoff, review request, prompt, notification
  preview, and relay status must all use the same `review_target_commit`.
- The major review package must remain the only ChatGPT major-stage review
  target.
- Finalization fixes may be included as context, but the prompt must not ask
  ChatGPT to review each finalization fix separately.
- Computer Use must not be used for review delivery.

If a Feishu notification was already sent and a later finalization fix changes
the major package or `review_target_commit`, Codex must either send a
replacement notification after approval or mark the previous notification as
superseded in repo artifacts. A superseded notification must not be presented as
the current major-gate notification.

## Major Review Gate

The major review gate is the user-facing state after finalization has passed.
Only then may Codex tell the user that manual ChatGPT major-stage review is
ready.

At the gate:

- ChatGPT reviews only the Stage 3 major review package.
- The review target is the unified `review_target_commit`.
- Finalization fixes are context only and remain Codex-internal review items.
- The user decides whether and when to request ChatGPT review.

## Major-stage ChatGPT review

Use this for phase transitions, live integration plans, any user-approved live
runtime change, significant strategy/backtest/reporting changes, security model
changes, or any change that materially affects the review or release process.

Major-stage ChatGPT review is manual. Codex prepares:

- A public GitHub URL.
- The `review_target_commit`.
- Repo-relative handoff and review request paths.
- A concise major-review prompt.

The user decides whether and when to paste that prompt into ChatGPT.

## Branch governance

- `main` is stable and should only carry major-stage reviewed states plus narrow
  repo-only governance or handoff fixes.
- `stage/*` branches are major-stage construction branches.
- `task/*` branches are optional small-stage construction branches.
- Stage 3 construction branch: `stage/stage3-data-backtest`.
- Stage 3A through Stage 3D are minor stages and use Codex self-review.
- Stage 3E creates the major-stage review package.
- Stage 3F and Stage 3F.1 are major-gate finalization fixes, not independent
  ChatGPT review targets.
- Codex asks the user whether to request manual ChatGPT review only after major
  package finalization has passed.

## Deprecated automatic route

The old route attempted to use ChatGPT through Computer Use as a UI relay. That
route is no longer the default, no longer part of the active review loop, and
must not be used by Codex automation drafts.

Forbidden for the active review loop:

- Opening ChatGPT automatically.
- Running Computer Use for review delivery.
- Sending ChatGPT prompts automatically.
- Reading or publishing local ChatGPT conversation URLs.
- Reading or sending local secrets, tokens, auth values, Feishu credentials,
  Hermes private config, OpenClaw private config, provider keys, or broker
  credentials.

No automatic order placement is allowed. No broker write access is allowed.
Final trading is manually decided by the user.

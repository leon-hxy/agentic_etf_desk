# Stage 3 Minor-Stage Runner

This runner is the repo-only supervisor for `stage/stage3-data-backtest`. It
keeps Stage 3 recoverable across Codex wakes while preserving ETF-only research,
manual final trading, no broker write capability, and no automatic ordering.

## Runner State

- State file: `ops/runners/stage3_runner_state.json`
- Current branch: `stage/stage3-data-backtest`
- Current minor stage: `Stage 3F.1`
- Current task: `ops/tasks/stage3f1_review_target_commit_consistency.md`
- Completed minor stages: `Stage 3A`, `Stage 3B`, `Stage 3C`, `Stage 3D`, `Stage 3E`, `Stage 3F`, `Stage 3F.1`
- Remaining minor stages: none
- Runner status: `major_stage_ready`
- Small-stage route: `codex_internal_review`
- Major-stage route: `manual_chatgpt_review`

## Minor-Stage Statuses

- `planned`: task exists but is waiting on its dependency.
- `ready`: dependency is complete and Codex may start the task.
- `in_progress`: implementation or artifact work is underway.
- `build_completed`: implementation is complete and initial tests were run.
- `internal_review_in_progress`: reviewer passes are running or being written.
- `completed_internal_review`: internal review passed, tests passed, and the
  stage was committed and pushed.
- `major_stage_ready`: Stage 3E package is ready for the user to request manual
  ChatGPT major-stage review.
- `completed_live_notification`: Stage 3F sent the major-gate Feishu notification without changing live configuration.
- `completed_consistency_fix`: Stage 3F.1 unified the Stage 3 major review target commit across review artifacts.
- `blocked`: Codex cannot continue without user action or external state.
- `skipped`: the stage was intentionally bypassed with a documented reason.

## Ordered Workflow

Each minor stage must complete these steps in order:

1. Confirm the branch is `stage/stage3-data-backtest`.
2. Read the runner state file.
3. Read the task file.
4. Confirm no step requires real `~/.hermes`, real `~/.openclaw`, real Feishu
   gateway changes, service restarts, dependency installation, Computer Use,
   broker interfaces, or order placement.
5. Implement the minor-stage scope only.
6. Run tests.
7. Mark the stage `build_completed` only after implementation and initial tests.
8. Spawn four read-only reviewer subagents when the environment supports them:
   Security Reviewer, Domain Reviewer, Integration Reviewer, and Test Reviewer.
9. If subagents are unavailable, run four separate reviewer passes and label
   each section with `reviewer_mode="simulated_separate_pass"`.
10. Generate `reports/internal_reviews/stage3/<minor>.md`.
11. Generate `reports/internal_reviews/stage3/<minor>.json`.
12. Fix reviewer findings without letting reviewer passes directly edit code.
13. Run tests again.
14. Update the task status.
15. Update `ops/runners/stage3_runner_state.json`.
16. Update handoff and loop-state files when the stage status changes.
17. Commit and push.
18. If the next minor stage is `ready`, continue only when time is sufficient
   and the state file allows it; otherwise wait for the next automation wake.

Tests passing is not internal review passing. Every small stage needs explicit
reviewer conclusions before it can be marked `completed_internal_review`.

## Notification Rules

- Do not notify the user for routine small-stage completion.
- If a stage is `blocked`, stop and require Hermes/Feishu notification to the
  user; do not continue to the next minor stage.
- If Stage 3E completes and the major review package is ready, notify the user
  to request manual ChatGPT major-stage review.
- Stage 3F may send exactly one major-gate Feishu notification through existing Hermes capability when runner status is `major_stage_ready` and `manual_chatgpt_review_ready=true`.
- Stage 3F.1 may update repo-only review artifacts so every `review_target_commit`
  points to the same manual major-review target; it must not resend Feishu.
- Do not request ChatGPT review for Stage 3A, Stage 3B, Stage 3C, or Stage 3D.

## Safety Rules

- Do not run Computer Use.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify the real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not connect broker interfaces.
- Do not place orders.
- Do not add an execution-role agent, order-routing agent, broker-facing agent,
  automatic trader role, or live trading role.
- Keep version 1 ETF-only.
- Final trading is manually decided by the user.

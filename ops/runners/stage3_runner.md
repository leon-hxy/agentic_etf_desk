# Stage 3 Minor-Stage Runner

This runner is the repo-only supervisor for `stage/stage3-data-backtest`. It
keeps Stage 3 recoverable across Codex wakes while preserving ETF-only research,
manual final trading, no broker write capability, and no automatic ordering.

## Runner State

- State file: `ops/runners/stage3_runner_state.json`
- Current branch: `stage/stage3-data-backtest`
- Current minor stage: `Stage 3 completed`
- Current task: none
- Completed minor stages: `Stage 3A`, `Stage 3B`, `Stage 3C`, `Stage 3D`
- Major package stage: `Stage 3E`
- Major gate finalization fixes: `Stage 3F`, `Stage 3F.1`
- Remaining minor stages: none
- Runner status: `major_stage_ready`
- Finalization status: `completed`
- Small-stage route: `codex_internal_review`
- Finalization route: `codex_internal_review`
- Major-stage route: `manual_chatgpt_review`

## Minor-Stage Statuses

- `planned`: task exists but is waiting on its dependency.
- `ready`: dependency is complete and Codex may start the task.
- `in_progress`: implementation or artifact work is underway.
- `build_completed`: implementation is complete and initial tests were run.
- `internal_review_in_progress`: reviewer passes are running or being written.
- `completed_internal_review`: internal review passed, tests passed, and the
  stage was committed and pushed.
- `major_package_generated`: the Stage 3 major review package exists, but
  finalization may still be running.
- `finalization_in_progress`: Codex is repairing handoff, notification,
  review-target, or package consistency before the major review gate.
- `finalization_consistency_checks`: Codex is checking that all human-readable
  and machine-readable review artifacts point to the same target and do not
  expose finalization fixes as independent ChatGPT review targets.
- `finalization_internal_review`: Security, Domain, Integration, and Test
  reviewer passes are reviewing the finalization fixes.
- `major_gate_notification_ready`: finalization passed and a single
  major-gate Feishu notification may be prepared or sent if allowed.
- `major_gate_notification_sent`: a current non-sensitive major-gate Feishu
  notification was sent after finalization passed.
- `manual_chatgpt_review_ready`: the user may request manual ChatGPT review of
  the Stage 3 major review package only.
- `major_stage_ready`: finalization is complete and the Stage 3 package is
  ready for user-initiated manual ChatGPT major-stage review.
- `blocked`: Codex cannot continue without user action or external state.
- `skipped`: the stage was intentionally bypassed with a documented reason.

## Major Gate Finalizer State Machine

Major gate finalization is internal runner work, not a user-review stage. Stage
3F and Stage 3F.1 are recorded as finalization fixes under
`major_gate_finalization`; they must not become ChatGPT review targets.

State order:

1. `major_package_generated`
2. `finalization_in_progress`
3. `finalization_consistency_checks`
4. `finalization_internal_review`
5. `major_gate_notification_ready`
6. `major_gate_notification_sent`
7. `manual_chatgpt_review_ready`

Forbidden during finalization:

- Do not notify the user to request ChatGPT review while
  `finalization_in_progress`.
- Do not notify the user while consistency checks are failing or incomplete.
- Do not notify the user while `review_target_commit` is inconsistent.
- Do not request ChatGPT review for Stage 3F, Stage 3F.1, or any other
  finalization fix.
- Do not expose finalization fixes as independent stages requiring user or
  ChatGPT approval.

If a Feishu notification was sent before finalization completed and a later
finalization fix changed the major package or review target, mark the previous
notification as superseded or prepare a replacement notification preview. Do not
send the replacement without an explicit live-send task.

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
- If Stage 3E completes, start major gate finalization before notifying the
  user.
- Send or mark current exactly one major-gate Feishu notification only after
  `finalization_status=completed`, consistency checks pass, and
  `manual_chatgpt_review_ready=true`.
- Stage 3F and Stage 3F.1 are finalization fixes. They may update repo-only
  review artifacts, notification previews, and consistency reports, but they
  must not request ChatGPT review or become user-facing review stages.
- Do not request ChatGPT review for Stage 3A, Stage 3B, Stage 3C, or Stage 3D.
- Do not request ChatGPT review for major gate finalization fixes.

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

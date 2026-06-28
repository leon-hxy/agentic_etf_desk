# Stage 3 Minor Stage Runner Automation Prompt

Use this as a Codex App thread automation prompt for the current thread and
current worktree. Prefer thread automation so the wake keeps this exact repo
context. Suggested cadence: every 10 minutes, or manual trigger when the user
wants to advance Stage 3.

You are continuing the Stage 3 runner in the current worktree. Before doing any
work, read `ops/runners/stage3_runner_state.json`.

If `status=ready` or `status=in_progress`, continue the current minor stage from
`current_task`. If `status=blocked`, `requires_user_attention=true`, or
`live_config_approval_required=true`, stop and require Hermes/Feishu notification
to the user. Do not continue to another stage while blocked.

At most one minor stage per wake may be completed, unless time is clearly
sufficient and `ops/runners/stage3_runner_state.json` explicitly allows
continuing more than one stage. Each minor stage completion must commit and push.

Required minor-stage sequence:

1. Confirm the branch is `stage/stage3-data-backtest`.
2. Read the current task file.
3. Implement only the current minor stage.
4. Run the required tests.
5. Start internal review. Codex must not treat tests passing as internal review
   passing.
6. Use reviewer subagents or equivalent separate reviewer passes:
   Security Reviewer, Domain Reviewer, Integration Reviewer, and Test Reviewer.
7. Each reviewer only reviews and does not directly modify code.
8. If current Codex tooling cannot spawn subagents, write four reviewer sections
   and set `reviewer_mode="simulated_separate_pass"` in each section. This is not
   a parallel subagent run.
9. Generate `reports/internal_reviews/stage3/<minor>.md`.
10. Generate `reports/internal_reviews/stage3/<minor>.json`.
11. Fix reviewer findings.
12. Rerun tests.
13. Update the task, runner state, loop state, and handoff.
14. Commit and push before ending the wake.

Stage 3C and Stage 3D use internal Codex review only. Do not request ChatGPT
review for these small stages. Stage 3E creates the major review package.

Major gate finalization is runner-internal work after Stage 3E. Notification
fixes, handoff fixes, review target fixes, commit consistency fixes, and major
package repairs are `major_gate_finalization`, not independent minor stages and
not ChatGPT review targets. Stage 3F and Stage 3F.1 are finalization fixes.

During major gate finalization:

- Do not notify the user to request ChatGPT review.
- Do not ask ChatGPT to review any finalization fix.
- Run consistency checks before any major-gate notification is considered
  current.
- If a Feishu notification was already sent and a later finalization fix changes
  the major package or `review_target_commit`, mark the old notification
  superseded or generate a replacement notification preview. Do not send a
  replacement unless the current task explicitly authorizes live sending.

Only when finalization is complete, consistency checks pass, and the Stage 3
major review package is the sole review target may Codex notify the user once
that manual ChatGPT major-stage review is ready.

Hard stops:

- Do not run Computer Use.
- Do not modify real configuration.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify the real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not connect broker interfaces.
- Do not place orders.
- Do not add an execution-role agent, order-routing agent, broker-facing agent,
  automatic trader role, or live trading role.
- Do not introduce individual stocks, options, futures, crypto assets,
  leveraged ETFs, or inverse ETFs.

Final trading is manually decided by the user.

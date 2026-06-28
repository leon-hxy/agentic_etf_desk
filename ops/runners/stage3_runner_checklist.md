# Stage 3 Runner Checklist

Use this checklist at the start and end of every Stage 3 automation wake.

## Wake Start

- [ ] Confirm `git branch --show-current` is `stage/stage3-data-backtest`.
- [ ] Read `ops/runners/stage3_runner_state.json`.
- [ ] Stop if `status` is `blocked` or `requires_user_attention` is true.
- [ ] Stop if the current task is not the expected next Stage 3 task.
- [ ] Confirm the wake does not require Computer Use, real config changes,
  service restarts, dependency installation, broker interfaces, or order
  placement.
- [ ] Read the current task file before editing.

## Minor-Stage Execution

- [ ] Implement only the current minor stage.
- [ ] Run the required test commands.
- [ ] Run Security Reviewer as a read-only pass.
- [ ] Run Domain Reviewer as a read-only pass.
- [ ] Run Integration Reviewer as a read-only pass.
- [ ] Run Test Reviewer as a read-only pass.
- [ ] If subagents are unavailable, label each reviewer section with
  `reviewer_mode="simulated_separate_pass"`.
- [ ] Generate the internal review `.md` artifact.
- [ ] Generate the internal review `.json` artifact.
- [ ] Fix reviewer findings.
- [ ] Rerun tests.

## Wake End

- [ ] Update the task status.
- [ ] Update `ops/runners/stage3_runner_state.json`.
- [ ] Update loop-state and handoff files when status changed.
- [ ] Confirm no ChatGPT review was requested for small stages.
- [ ] Confirm no Feishu notification was sent unless blocked or Stage 3 major
  package is ready.
- [ ] Confirm no Computer Use ran.
- [ ] Confirm no real config changed.
- [ ] Commit and push the minor-stage result.
- [ ] Leave the next stage ready or planned according to dependencies.

Final trading is manually decided by the user.

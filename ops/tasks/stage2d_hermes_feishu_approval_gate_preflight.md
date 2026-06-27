# Stage 2D Hermes Feishu Approval Gate Preflight Task

status: planned_requires_user_approval
stage: Stage 2D Hermes Feishu approval gate preparation
review_target_commit: set in `reports/review_requests/latest.json` after the plan commit exists

## Goal

Prepare a safe, reviewable plan for real Hermes/Feishu notification and local
approval gate integration. This task is only a repo-only preparation package.

## Scope

- Produce an installation plan.
- Produce a backup plan.
- Produce a rollback plan.
- Produce safety checks for a later user-approved live integration.
- Keep existing notification and review relay artifacts as draft-only previews.
- Keep all trading output as research, risk review, reports, backtests, and
  manual recommendation tickets only.

## Boundaries

- Repo-only preparation.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify a real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not run real Computer Use.
- Do not read, print, or store private credential values.
- No secrets may be written to logs, reports, tickets, commits, or review
  prompts.
- Do not add broker integrations or automatic trading capability.
- Final trading is manually decided by the user.

## Required Plans

- `docs/stage2d_hermes_feishu_approval_gate_preflight/installation_plan.md`
- `docs/stage2d_hermes_feishu_approval_gate_preflight/backup_plan.md`
- `docs/stage2d_hermes_feishu_approval_gate_preflight/rollback_plan.md`
- `docs/stage2d_hermes_feishu_approval_gate_preflight/safety_checks.md`

## Required User Approval Before Any Live Work

- Approval to inspect real Hermes configuration paths.
- Approval to inspect real Feishu gateway configuration paths.
- Approval to create local backups outside the repo.
- Approval to copy repo drafts into a live Hermes or gateway location.
- Approval before any Hermes or gateway restart.
- Approval before any Computer Use relay beyond repo-only preview generation.

## Completion Criteria For This Repo-Only Preparation

- Task file exists and remains `planned_requires_user_approval`.
- Installation, backup, rollback, and safety check plans exist.
- Safety tests pass.
- Handoff and review request point to the Stage 2D preparation commit.
- No real config, service, dependency, secret, or Computer Use action occurred.

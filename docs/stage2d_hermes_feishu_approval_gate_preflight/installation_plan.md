# Stage 2D Installation Plan

Repo-only preparation for a future Hermes/Feishu notification and local approval
gate integration.

The future live installation requires explicit user approval before every
real-system step.

## Purpose

Connect the repo-only notification draft and local approval gate protocol to the
real Hermes/Feishu path only after a future approval. This plan describes the
sequence to follow later; it does not modify any live system now.

## Inputs To Review Before Future Live Work

- `configs/hermes/feishu_loop_notifier_skill.md`
- `configs/hermes/feishu_review_command_skill.md`
- `ops/review_gate/README.md`
- `ops/review_gate/review_gate.example.json`
- `reports/review_requests/latest.json`
- `reports/review_requests/notification_preview.md`

## Installation Steps For A Future Approved Session

1. Confirm the user explicitly approves live Stage 2D installation.
2. Re-read `AGENTS.md` and this plan.
3. Run safety tests before touching any live path.
4. Locate real Hermes and Feishu gateway configuration paths without printing
   private values.
5. Run the backup plan and verify the backup manifest is complete.
6. Compare repo draft files with the live Hermes/Feishu routing model.
7. Prepare a minimal live change set that only enables notification and local
   approval gate handling.
8. Show the exact live change set to the user for approval before applying it.
9. Apply only the approved change set.
10. Run the safety checks after applying the live change.
11. Restart services only if the user explicitly approves the restart in that
    future session.

## Explicit Non-Actions In This Commit

- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify a real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not run real Computer Use.
- Do not read, print, or store private credential values.
- Do not send Feishu messages.
- Do not create broker access or automatic trading capability.

Final trading is manually decided by the user.

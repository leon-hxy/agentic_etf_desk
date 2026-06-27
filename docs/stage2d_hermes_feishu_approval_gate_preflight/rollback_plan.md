# Stage 2D Rollback Plan

Repo-only preparation for rollback after a future user-approved live
Hermes/Feishu notification and local approval gate integration.

This future rollback run requires explicit user approval.

## Rollback Goals

- Restore the pre-change Hermes configuration if the approved live integration
  fails safety checks.
- Restore the pre-change Feishu gateway configuration if the approved live
  integration fails safety checks.
- Avoid repeated live edits when rollback is required.
- Keep the system in manual-trading mode at all times.

## Future Rollback Triggers

- Notification routing does not match the approved scope.
- Local approval gate validation fails.
- Feishu messages would be sent without the approved gate.
- Any private value appears in logs, reports, tickets, or prompts.
- Any automatic trading capability appears.
- User asks to abort or revert.

## Future Rollback Steps

1. Stop making live changes.
2. Confirm the user approves rollback.
3. Restore the approved backup files from the backup manifest.
4. Re-run safety checks.
5. Restart services only if the user explicitly approves the restart in that
   future session.
6. Record the rollback result in a repo handoff without private values.

## Explicit Non-Actions In This Commit

- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify a real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not run real Computer Use.
- Do not touch broker systems.

Final trading is manually decided by the user.

# Stage 2D Backup Plan

Repo-only preparation for future backups before live Hermes/Feishu notification
and local approval gate integration.

This future backup run requires explicit user approval.

## Backup Goals

- Preserve the current live Hermes configuration before any approved change.
- Preserve the current live Feishu gateway configuration before any approved
  change.
- Record file paths and checksums without recording private values.
- Keep backups outside the public repo.

## Future Backup Steps

1. Confirm the user approves backup creation.
2. Create a timestamped backup directory outside the repo.
3. Copy the real Hermes configuration files selected by the user.
4. Copy the real Feishu gateway configuration files selected by the user.
5. Store a manifest that lists relative file labels, sizes, and checksums.
6. Verify the manifest does not include private credential values.
7. Confirm the backup can be read before any live installation step.

## Backup Manifest Rules

- Record only file labels, checksums, sizes, timestamps, and redacted key names.
- Do not record secret values, tokens, private credential values, `.env` values,
  provider keys, Feishu App Secret values, or broker credentials.
- Do not commit the backup directory or manifest to this repo.
- Do not print private values to terminal output, logs, reports, tickets, or
  review prompts.

## Explicit Non-Actions In This Commit

- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not modify a real Feishu gateway.
- Do not restart services.
- Do not install dependencies.
- Do not run real Computer Use.

Final trading is manually decided by the user.

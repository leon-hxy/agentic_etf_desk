# Stage 2D.1 Backup Checklist

- Stage: `Stage 2D.1 read-only live preflight completed`
- Mode: ``

## Sanitized JSON

```json
{
  "backup_created": false,
  "final_trading_notice": "Final trading is manually decided by the user.",
  "future_backup_items": [
    "~/.hermes/config.yaml",
    "~/.hermes/.env",
    "~/.hermes/skills",
    "real Feishu gateway config path selected by user"
  ],
  "manifest_rules": [
    "Record file labels, checksums, sizes, timestamps, and capability labels only",
    "If detailed key names are needed, write them only under gitignored local_private",
    "Do not record secret values",
    "Do not commit backup files to this repo"
  ],
  "requires_user_approval_before_backup": true,
  "stage": "Stage 2D.1 read-only live preflight completed"
}
```

No secret values, raw command output, absolute local paths, service restarts, dependency installs, Feishu sends, or Computer Use actions are included.

Final trading is manually decided by the user.

# Stage 6 WP3 Log Redaction

This repo-only log redaction policy defines how Program Runner diagnostics are sanitized before any text is written to public repo logs, reports, tickets, handoff files, or review artifacts.

Final trading is manually decided by the user.

## Redaction Rules

| Rule | Action | Description |
|---|---|---|
| secret_assignment_values | replace value with <redacted> | Mask values assigned to sensitive-looking key names before log text becomes repo-visible. |
| authorization_headers | replace bearer value with <redacted> | Mask authorization header bearer values in copied command output. |
| absolute_local_paths | replace path with <redacted-path> | Mask absolute local user and volume paths from public logs and reports. |
| local_private_references | replace detail with local_private/<redacted> | Keep local-private storage references generic when logs mention private approval files. |
| process_identifiers | replace numeric process id with <redacted-pid> | Mask process identifiers that describe local runtime state. |
| feishu_or_broker_private_identifiers | replace private identifier value with <redacted-id> | Mask Feishu or broker private identifier values when copied from diagnostics. |

## Validation

- synthetic samples redacted: true.
- original sensitive values retained: false.
- redaction placeholder: `<redacted>`.
- private path placeholder: `<redacted-path>`.
- process id placeholder: `<redacted-pid>`.

## Safety Result

- repo-only: true.
- live send attempted: false.
- real runtime modified: false.
- services restarted: false.
- broker write surface: false.
- automatic trading surface: false.
- order placement surface: false.
- trade ticket generated: false.
- risk_agent review: passed; no actionable trade suggestion generated.

## Next Safe Action

Proceed to `Stage 6 WP4 public repo hygiene`.

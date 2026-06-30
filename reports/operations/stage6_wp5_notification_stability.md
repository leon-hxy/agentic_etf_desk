# Stage 6 WP5 Hermes/Feishu Notification Stability

This repo-only policy defines the Program Runner notification stability contract for Hermes/Feishu user messages without sending a live message or changing runtime configuration.

Final trading is manually decided by the user.

## Stability Checks

| Check | Description | Verification |
|---|---|---|
| idempotent_notification_preview | Notification previews carry a deterministic work-package/status idempotency key so repeated wakes update the same preview intent instead of duplicating sends. | repo-only policy artifact and Program Runner state fields |
| allowed_status_only | User-facing Hermes/Feishu notification content is generated only for blocked, approval_required, or final_review_ready states. | configs/codex_automation/program_runner_heartbeat_prompt.md |
| blocked_or_approval_next_safe_action | Blocked and approval-required notifications must include next_safe_action before any preview is considered valid. | notification contract in this artifact |
| secret_free_message_body | Notification message bodies must exclude secrets, tokens, auth values, local-private paths, Feishu IDs, provider keys, and broker credentials. | public repo hygiene and secret scans |
| repo_only_live_send_fallback | When live sending would require real Hermes/Feishu configuration changes or service restarts, generate repo-only preview artifacts instead. | reports/program_runner/notification_preview.md and .json fallback contract |
| delivery_status_audit_fields | Notification previews and reports record live_send_attempted, real_runtime_modified, services_restarted, and delivery_status fields. | program report and policy fields |

## Notification Contract

- send gate statuses: blocked, approval_required, final_review_ready.
- send on work_package_completed: false.
- send on internal_review_completed: false.
- send on tests_passed: false.
- preview required when live send is not allowed: true.
- blocked and approval-required previews require next_safe_action.

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

Proceed to `Stage 6 WP6 OpenClaw agent boundary checks`.

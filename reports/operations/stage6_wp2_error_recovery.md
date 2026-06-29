# Stage 6 WP2 Error Recovery

This repo-only error recovery playbook defines safe handling for Program Runner failures without changing real Hermes, OpenClaw, Feishu, launchd, cron, broker, or provider configuration.

Final trading is manually decided by the user.

## Recovery Scenarios

| Scenario | Status after detection | Next safe action | Service restart allowed |
|---|---|---|---:|
| missing_or_stale_data_artifact | fixing_findings | regenerate repo-only data or report artifact, then rerun targeted tests | false |
| failed_repo_only_report_generation | fixing_findings | fix the repo-only generator and rerun targeted plus safety tests | false |
| failed_safety_or_smoke_test | fixing_findings | keep work in repo, fix findings, and rerun the full verification suite | false |
| blocked_live_runtime_or_secret_requirement | approval_required | write approval queue item and stop without live runtime changes | false |
| notification_send_unavailable_without_runtime_change | blocked | generate notification preview artifact and stop for user review | false |

## Safety Result

- repo-only: true.
- live send attempted: false.
- real runtime modified: false.
- services restarted: false.
- broker write surface: false.
- automatic trading surface: false.
- order placement surface: false.
- trade ticket generated: false.
- default runtime action: do_not_restart_or_modify_real_services.
- risk_agent review: passed; no actionable trade suggestion generated.

## Next Safe Action

Proceed to `Stage 6 WP3 log redaction`.

# Program Internal Review Template

## Metadata

- major_stage:
- work_package:
- commit:
- changed_files:
- reviewer_mode:

## Security Reviewer

- result:
- findings:
- fixes_required:
- secrets_touched:
- live_configs_modified:
- automatic_trading_surface:
- broker_write_surface:

## Domain / Quant Reviewer

- result:
- findings:
- etf_only_maintained:
- benchmark_comparison_present:
- research_limitations_clear:
- risk_agent_review_required_for_trade_tickets:
- trade_tickets_actionable_without_risk_agent_review:

## Integration Reviewer

- result:
- findings:
- Hermes/Feishu boundary respected:
- OpenClaw boundary respected:
- no real runtime modification without approval:

## Test / Reproducibility Reviewer

- result:
- findings:
- tests_run:
- reproducible_outputs:

## Public Repo Hygiene Reviewer

- result:
- findings:
- no local-private paths:
- no secrets or credentials:
- public repo safe:

## Findings

- findings:
- fixes_applied:
- tests:
- pass/fail:
- requires_user_attention:
- promote_to_next_work_package:

Final trading is manually decided by the user.

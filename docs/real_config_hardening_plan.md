# Real Config Hardening Plan

Scope: planning only. This phase must not execute any real remediation.

This plan is based on `docs/current_state_audit.md`. It covers the live Hermes and OpenClaw risks found during the read-only audit, but every command that changes real state requires explicit user approval before use.

## Risks

### OpenClaw Plaintext Secret-Bearing Fields

`openclaw doctor` reported plaintext secret-bearing field paths in the real OpenClaw config. The reported path names included gateway authentication material, model provider API key locations, and the Feishu app secret field path.

Risk:

- Any local tool with access to the config file may read sensitive values.
- Logs, transcripts, or agent workspaces could accidentally expose values if files are copied or summarized.
- Config drift is harder to audit when sensitive values live inline instead of through secret references.

### OpenClaw Directory Permissions

`openclaw doctor` reported that `~/.openclaw` permissions are too open.

Risk:

- Other local processes or users may have broader read access than needed.
- Plaintext config values become more dangerous when directory permissions are loose.

### Gateway Ownership Drift

Hermes and OpenClaw both showed a gateway process reachable locally while the related launchd job was not loaded.

Risk:

- The running process may not match the intended launchd-managed service.
- Restart behavior after reboot is ambiguous.
- Operators may misdiagnose whether the service is healthy, manually owned, or launchd owned.

## Files To Back Up Before Any Real Fix

Back up these files and directories before any approved remediation:

- `~/.openclaw/openclaw.json`
- `~/.openclaw/cron/jobs.json`
- `~/.openclaw/secrets` if present
- `~/.openclaw/agents`
- `~/.hermes/config.yaml`
- `~/.hermes/.env`
- `~/.hermes/SOUL.md`
- `$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist`
- `$HOME/Library/LaunchAgents/ai.hermes.gateway.plist`
- Any alternate user LaunchAgents path discovered during an approved private audit.

Backups must redact sensitive values before being copied into this repo, shared in chat, or attached to reports.

## Values That Need Redaction

Always redact:

- Provider API keys.
- Gateway authentication values.
- Feishu app identifiers when combined with auth material.
- Feishu app secret values.
- User/channel allowlists if they expose private IDs.
- OAuth tokens.
- Session cookies.
- Any value stored in `.env`.

## Recommended Remediation Sequence

Do not execute this sequence in Stage 2A. It is a future approved-maintenance plan.

1. Confirm the user approves a live config maintenance window.
2. Capture read-only preflight evidence: current versions, gateway status, process ownership, and config key names.
3. Create local backups of the files listed above.
4. Redact copies of backup summaries before writing anything into this repo.
5. Move OpenClaw inline sensitive values into the tool's secret-reference mechanism.
6. Re-run a read-only secret audit command for OpenClaw.
7. Review and tighten `~/.openclaw` permissions.
8. Decide whether Hermes and OpenClaw gateways should be launchd-owned or manually owned.
9. Stop only the unintended gateway owner after explicit approval.
10. Load or restart the approved launchd service after explicit approval.
11. Verify local connectivity and Feishu behavior after restart.
12. Document exact before/after evidence in an audit note that contains no sensitive values.

## Rollback Plan

1. Stop the newly started service only after explicit approval.
2. Restore the backed-up config file or launchd plist.
3. Restore prior directory permissions if they were changed.
4. Start the previous approved gateway owner after explicit approval.
5. Verify local gateway health and Feishu message path.
6. Record rollback evidence without sensitive values.

## Commands Requiring Explicit User Approval

The following command categories must not run without explicit approval:

- Any `doctor --fix` command for Hermes or OpenClaw.
- Any command that starts, stops, restarts, loads, unloads, or bootstraps Hermes or OpenClaw.
- Any `launchctl` command that changes service state.
- Any `chmod` or `chown` command touching `~/.openclaw` or `~/.hermes`.
- Any command that writes to `~/.openclaw` or `~/.hermes`.
- Any command that changes Feishu configuration.
- Any command that creates, updates, or deletes real secrets.

## Stage 2A Boundary

Stage 2A is repo-only. This plan must remain documentation only until the user explicitly approves a live remediation phase.

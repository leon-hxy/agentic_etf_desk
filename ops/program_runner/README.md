# Autonomous Program Runner

This directory defines the autonomous runner for completing the remaining v1.0 ETF research desk roadmap.

The runner replaces manual small-stage prompting with Codex-managed work packages. Codex may implement, run internal reviewer passes, fix findings, test, commit, push, and continue without user notification until a block, an approval-required action, or final v1.0 review readiness.

## Operating Mode

- Program: `agentic_etf_desk`
- Mode: `autonomous_until_final_review`
- Current starting stage: `Stage 3.2`
- Required branch: `stage/v1-autonomous-completion`
- Prerequisite: Stage 3.1 must be merged into `main` before any Stage 3.2 business work begins
- ChatGPT review policy: final v1.0 program review only
- Internal work package review policy: Codex internal review
- User notifications: blocked, approval required, or final review ready

## Safety Boundaries

- ETF-only remains mandatory.
- Final trading is manually decided by the user.
- Outputs remain limited to research, backtests, risk reviews, reports, and manual trade recommendation tickets.
- Do not run Computer Use.
- Do not modify real runtime configuration without explicit approval.
- Do not restart Hermes or OpenClaw without explicit approval.
- Do not modify Feishu gateway configuration without explicit approval.
- Do not install dependencies without explicit approval.
- Do not connect broker write interfaces.
- Do not place orders.
- Every trade recommendation ticket must pass `risk_agent` review before it can be shown as an actionable suggestion.
- Every strategy must compare against a benchmark.
- Manual holdings and trades imports must reject symbols outside `configs/universe/etf_universe.yaml`.
- Do not write secrets, tokens, auth values, provider keys, Feishu secrets, or broker credentials to repo files, logs, reports, tickets, commits, or audit output.

## Files

- `roadmap.yaml` lists the four remaining internal major stages.
- `program_runner_state.json` is the current runner state.
- `program_runner.md` defines the state machine and work package contract.
- `approval_queue.json` is the explicit approval queue for live, sensitive, or external actions.
- `heartbeat_log.md` records automation wakeups.
- `blocked_reason.md` records active blocks, if any.

This setup does not generate the final review package. The final package is generated only when the roadmap reaches `final_review_ready`.

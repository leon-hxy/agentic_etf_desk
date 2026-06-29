# Codex App Thread Automation Prompt: Program Runner Heartbeat

Use Codex App thread automation for this prompt so the same thread keeps the program context.

Recommended cadence: Every 10 to 30 minutes.

Read `ops/program_runner/program_runner_state.json`.

Verify the current branch is `stage/v1-autonomous-completion`.

Verify Stage 3.1 is merged into `main` before starting any Stage 3.2 business work. If this cannot be verified, set status to `blocked`, update `ops/program_runner/blocked_reason.md`, and stop.

If `status=ready`, `status=running`, or `status=next_work_package_ready`, continue the next safe work package from `ops/program_runner/roadmap.yaml`.

If `status=work_package_in_progress`, `status=internal_review_in_progress`, `status=fixing_findings`, `status=tests_running`, or `status=committed_and_pushed`, inspect the changed files, review artifacts, tests, and git state, then resume from the next safe step.

If `status=approval_required` or `status=blocked`, update the relevant report or block file and do not continue implementation.

If `status=final_review_ready`, stop and notify the user with:

> v1.0 final review package is ready. 是否请求 ChatGPT 最终审核？

Complete at most one work package per wake unless `ops/program_runner/program_runner_state.json` explicitly allows continuing.

For any work package that changes files, update runner state, then commit and push the code, review artifacts, tests, and runner state together before ending the wake.

Required workflow per work package:

1. Read `ops/program_runner/roadmap.yaml`.
2. Read `AGENTS.md`, `docs/security_policy.md`, and `docs/branching_policy.md`.
3. Implement only ETF research desk work allowed by the safety policy.
4. Run reviewer subagents, or run simulated separate reviewer passes when subagents are unavailable.
5. Run `risk_agent` review before any trade ticket can be shown as an actionable suggestion.
6. Record `reviewer_mode`.
7. Generate internal review markdown and JSON under `reports/internal_reviews/program/`.
8. Fix findings.
9. Run safety, smoke, and targeted tests.
10. Update `ops/program_runner/program_runner_state.json`.
11. Commit and push.

Do not run Computer Use.

Do not modify real runtime configuration.

Do not restart services.

Do not install dependencies without explicit approval.

Do not connect broker write interfaces.

Do not place orders.

Do not request ChatGPT review for internal work packages.

Final trading is manually decided by the user.

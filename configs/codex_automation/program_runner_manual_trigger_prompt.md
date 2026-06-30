# Manual Trigger Prompt: Program Runner

Read `ops/program_runner/program_runner_state.json`.

Resume the autonomous v1.0 Program Runner from the recorded status.

Verify the current branch is `stage/v1-autonomous-completion`.

Verify Stage 3.1 is merged into `main` before starting any Stage 3.2 business work. If this cannot be verified, set status to `blocked`, update `ops/program_runner/blocked_reason.md`, and stop.

If status is `ready`, `running`, or `next_work_package_ready`, select the next work package from `ops/program_runner/roadmap.yaml` and complete at most one work package in this turn unless the state explicitly allows continuing.

If status is `work_package_in_progress`, `internal_review_in_progress`, `fixing_findings`, `tests_running`, or `committed_and_pushed`, inspect the changed files, review artifacts, tests, and git state, then resume from the next safe step.

If status is `approval_required` or `blocked`, update `ops/program_runner/approval_queue.json`, `ops/program_runner/blocked_reason.md`, or the relevant report. Do not continue implementation.

If status is `final_review_ready`, stop and notify the user that the final package is ready.

Do not request ChatGPT review until final_review_ready.

Do not run Computer Use.

Do not modify real runtime configuration.

Do not restart services.

Do not install dependencies without explicit approval.

Do not connect broker write interfaces.

Do not place orders.

Do not expose secrets, tokens, auth values, private runtime paths, or private identifiers.

Every trade ticket must pass `risk_agent` review before it can be shown as an actionable suggestion.

Final trading is manually decided by the user.

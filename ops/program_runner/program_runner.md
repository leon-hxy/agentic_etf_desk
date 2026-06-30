# Program Runner State Machine

This runner advances the remaining v1.0 ETF research desk roadmap autonomously until the final review package is ready.

Final trading is manually decided by the user.

## States

- `ready`: Runner can select the next work package from `ops/program_runner/roadmap.yaml`.
- `running`: Runner is active in the current Codex thread.
- `work_package_in_progress`: Implementation work is being performed.
- `internal_review_in_progress`: Independent internal review is being performed.
- `fixing_findings`: Findings are being addressed before tests.
- `tests_running`: Safety, smoke, and targeted tests are running.
- `committed_and_pushed`: The completed work package was committed and pushed.
- `next_work_package_ready`: No block exists and the next work package can begin.
- `approval_required`: Work cannot continue until the user approves an explicit queue item.
- `blocked`: Work cannot continue because of a non-approval blocker.
- `final_review_ready`: The final v1.0 review package is ready and the user may decide whether to request ChatGPT final review.
- `final_review_ready_waiting_for_release`: The final v1.0 review package has a final review verdict and automation is paused until release/merge.
- `completed`: The program is complete.

## Work Package Contract

Every work package must run this sequence:

1. Read `ops/program_runner/roadmap.yaml`.
2. Read `AGENTS.md`, `docs/security_policy.md`, and `docs/branching_policy.md`.
3. Verify the current branch is `stage/v1-autonomous-completion`.
4. Verify Stage 3.1 is merged into `main` before any Stage 3.2 business work begins.
5. Implement the work package.
6. Spawn reviewer subagents:
   - Security Reviewer
   - Domain / Quant Reviewer
   - Integration Reviewer
   - Test / Reproducibility Reviewer
   - Public Repo Hygiene Reviewer
7. For any work package that creates or changes a trade recommendation ticket, run `risk_agent` review before the ticket can be shown as an actionable suggestion.
8. If subagents are unavailable, run simulated separate reviewer passes.
9. Record `reviewer_mode` as `subagents` or `simulated_separate_passes`.
10. Generate internal review markdown and JSON under `reports/internal_reviews/program/`.
11. Fix findings.
12. Run the full safety and smoke test suite.
13. Update `ops/program_runner/program_runner_state.json` with the work package result.
14. Commit and push the code, review artifacts, tests, and runner state together.
15. Continue to the next work package without user notification unless state is `blocked`, `approval_required`, or `final_review_ready`.

If a wake resumes from `work_package_in_progress`, `internal_review_in_progress`, `fixing_findings`, `tests_running`, or `committed_and_pushed`, inspect the changed files, review artifacts, tests, and git state, then continue from the next safe step instead of starting a new package.

## Approval Queue

If a work package requires live runtime changes, private credentials, external sends, private data, git history rewrite, broker account access, or any account-changing capability, stop and write an item to `ops/program_runner/approval_queue.json`.

Approval items must include:

- `reason`
- `requested_action`
- `files_or_services_touched`
- `risks`
- `rollback_plan`
- `default_action_if_not_approved`

The default action when approval is not granted is `skip_or_defer`.

Git pushes to the configured repository remote are allowed after public repo
hygiene, secret, forbidden-surface, and relevant safety tests pass. Other real
external sends must enter the approval queue.

## Notification Policy

Hermes/Feishu notification is allowed only when:

- status is `blocked`
- status is `approval_required`
- status is `final_review_ready`

For `status=blocked`, `status=approval_required`, and `status=final_review_ready`,
the runner must generate Hermes/Feishu user notification content. The notification
content must include `next_safe_action` and must not include secrets, tokens,
auth values, local-private paths, Feishu IDs, OpenAI keys, broker account data,
or broker credentials.

If the current environment cannot send a real Feishu message without modifying
real Hermes/Feishu gateway configuration or restarting services, the runner must
generate `reports/program_runner/notification_preview.md` and
`reports/program_runner/notification_preview.json`, and state why the live send
was not attempted.

When status is `final_review_ready` or `final_review_ready_waiting_for_release`, the allowed user-facing message is:

> v1.0 final review package is ready. 是否请求 ChatGPT 最终审核？

Do not notify the user for `work_package_completed`, `tests_passed`, or
`internal_review_completed` status events.

Do not request ChatGPT review for internal work packages. Do not run Computer Use. Do not modify real runtime configuration without explicit approval. Do not connect broker write interfaces. Do not place orders.

## Completion Rule

The program may move to `final_review_ready_waiting_for_release` only after `reports/program_reviews/final/latest.md` and `reports/program_reviews/final/latest.json` have been generated, internally reviewed, and reconciled as the latest release target.

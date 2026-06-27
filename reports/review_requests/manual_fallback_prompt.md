# Manual ChatGPT Review Fallback Prompt

Computer Use relay is optional and draft-only. If relay is unavailable, copy the prompt below into ChatGPT.

This fallback不会自动下单，最终交易由用户手动决定。

```text
请审核公开 GitHub repo：

https://github.com/leon-hxy/agentic_etf_desk

请读取：

- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `AGENTS.md`
- `docs/security_policy.md`

请审核 `review_target_commit`：`1d82b8083c86613d9d516958aee704d0d8c65b2c`。

请根据 `reports/review_requests/latest.json` 中的 `review_target_commit` 和 review_files 审核 Stage 2D.2A minimal live Hermes skills install completed。
不要把旧阶段 commit 当作本阶段的审核目标。

Stage 2D.2A minimal live Hermes skills install completed review_files：

- `reports/live_install/stage2d2a_live_install_report.md`
- `reports/live_install/stage2d2a_live_install_report.json`
- `reports/live_install/stage2d2a_rollback_manifest.md`
- `reports/live_install/stage2d2a_rollback_manifest.json`
- `reports/live_install/stage2d2a_safety_test_results.md`
- `reports/live_install/stage2d2a_safety_test_results.json`
- `scripts/review_relay/render_notification_preview.py`
- `scripts/safety/check_public_repo_hygiene.py`
- `scripts/safety/check_handoff_commit_consistency.py`
- `ops/state/loop_state.json`
- `tests/safety/test_loop_automation_dry_run.py`
- `tests/safety/test_loop_state_consistency.py`
- `tests/safety/test_notification_loop_safety.py`
- `tests/safety/test_review_relay_safety.py`
- `tests/safety/test_stage2d_preparation_plan.py`
- `tests/safety/test_stage2d2a_live_install.py`
- `tests/safety/test_handoff_commit_consistency.py`

重点检查：

- ETF-only 是否保持。
- 是否有自动下单 surface。
- 是否有 secrets 泄漏。
- 是否有真实 `~/.hermes` / `~/.openclaw` 修改迹象。
- safety tests 和 smoke tests 是否合理。
- public repo hygiene 是否保持。
- 是否可以进入下一阶段。

请输出：

- 通过/不通过。
- 高风险问题。
- 必须修复项。
- 建议下一步。

提示：repo 是 public，不需要 GitHub connector。
提醒：本系统不会自动下单，最终交易由用户手动决定。
```

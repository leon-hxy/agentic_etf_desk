请审核公开 GitHub repo：

https://github.com/leon-hxy/agentic_etf_desk

请读取：

- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `AGENTS.md`
- `docs/security_policy.md`

请审核 `review_target_commit`：`c83711053e6570bb447315e603c0a0701b9086b2`。

请根据 `reports/review_requests/latest.json` 中的 `review_target_commit` 和 review_files 审核 Stage 2A.6。
不要把 Stage 2A.5 commit 当作 Stage 2A.6 的审核目标。

Stage 2A.6 review_files：

- `docs/loop_protocol.md`
- `docs/chatgpt_review_relay_design.md`
- `configs/hermes/feishu_loop_notifier_skill.md`
- `configs/hermes/feishu_review_command_skill.md`
- `configs/codex_automation/chatgpt_review_relay_prompt.md`
- `ops/notifications/feishu_message_templates.md`
- `ops/review_gate/README.md`
- `ops/review_gate/review_gate.example.json`
- `ops/state/loop_state.json`
- `local_private/README.md`
- `scripts/review_relay/build_chatgpt_review_prompt.py`
- `scripts/review_relay/check_review_gate.py`
- `scripts/review_relay/mark_review_gate_used.py`
- `scripts/review_relay/relay_common.py`
- `scripts/review_relay/render_manual_fallback_prompt.py`
- `scripts/safety/check_review_relay_safety.py`
- `tests/safety/test_notification_loop_safety.py`
- `tests/safety/test_review_relay_safety.py`
- `reports/review_requests/chatgpt_review_prompt.md`
- `reports/review_requests/chatgpt_review_prompt.json`
- `reports/review_requests/manual_fallback_prompt.md`
- `reports/review_requests/relay_status.md`
- `reports/review_requests/relay_status.json`
- `reports/codex_handoff/latest.md`
- `reports/codex_handoff/latest.json`
- `reports/review_requests/latest.md`
- `reports/review_requests/latest.json`

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

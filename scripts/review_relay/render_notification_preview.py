#!/usr/bin/env python3
"""Render a repo-only notification preview for the latest review request."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LATEST_REVIEW = ROOT / "reports" / "review_requests" / "latest.json"
LOOP_STATE = ROOT / "ops" / "state" / "loop_state.json"
PREVIEW_JSON = ROOT / "reports" / "review_requests" / "notification_preview.json"
PREVIEW_MD = ROOT / "reports" / "review_requests" / "notification_preview.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def payload() -> dict[str, Any]:
    review = load_json(LATEST_REVIEW)
    loop_state = load_json(LOOP_STATE)
    loop_stage = str(loop_state["current_stage"])
    review_stage = str(review.get("stage") or "")
    review_loop_stage = str(review.get("loop_state_stage") or "")
    computer_use_executed = bool(loop_state.get("computer_use_executed"))
    display_stage = review_stage or loop_stage
    target = (
        str(review.get("review_target_commit") or "")
        if review_stage == loop_stage or review_loop_stage == loop_stage
        else "pending_review_target_commit_for_current_stage"
    )
    computer_use_text = "Computer Use 已执行一次 relay smoke" if computer_use_executed else "Computer Use 未执行"
    message = (
        f"Codex dry-run 阶段 `{display_stage}` 已生成 repo-only 预览。"
        f" review_target_commit: `{target}`。"
        f" {computer_use_text}；不会自动下单，最终交易由用户手动决定。"
    )
    return {
        "stage": display_stage,
        "loop_state_stage": loop_stage,
        "review_stage": review_stage,
        "review_target_commit": target,
        "mode": "repo_only_preview",
        "sent_to_feishu": False,
        "computer_use_executed": computer_use_executed,
        "real_gateway_modified": False,
        "message": message,
        "allowed_user_replies": [
            "确认审核",
            "暂不审核",
            "只看状态",
            "开始下一阶段",
            "暂停 loop",
        ],
    }


def render_markdown(data: dict[str, Any]) -> str:
    replies = "\n".join(f"- {reply}" for reply in data["allowed_user_replies"])
    return "\n".join(
        [
            "# Notification Preview",
            "",
            f"- Stage: `{data['stage']}`",
            f"- Review stage: `{data.get('review_stage')}`",
            f"- review_target_commit: `{data['review_target_commit']}`",
            f"- Mode: `{data['mode']}`",
            f"- Sent to Feishu: `{str(data['sent_to_feishu']).lower()}`",
            f"- Computer Use executed: `{str(data['computer_use_executed']).lower()}`",
            f"- Real gateway modified: `{str(data['real_gateway_modified']).lower()}`",
            "",
            "## Preview Message",
            "",
            data["message"],
            "",
            "## Allowed User Replies",
            "",
            replies,
            "",
        ]
    )


def main() -> int:
    try:
        data = payload()
        PREVIEW_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        PREVIEW_MD.write_text(render_markdown(data), encoding="utf-8")
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class NotificationLoopSafetyTest(unittest.TestCase):
    def read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_notification_and_review_command_drafts_exist(self) -> None:
        required = [
            "configs/hermes/feishu_loop_notifier_skill.md",
            "configs/hermes/feishu_review_command_skill.md",
            "ops/notifications/feishu_message_templates.md",
        ]
        for path in required:
            self.assertTrue((ROOT / path).exists(), path)

    def test_notification_drafts_are_repo_only_and_manual(self) -> None:
        combined = "\n".join(
            [
                self.read("configs/hermes/feishu_loop_notifier_skill.md"),
                self.read("configs/hermes/feishu_review_command_skill.md"),
                self.read("ops/notifications/feishu_message_templates.md"),
            ]
        )
        self.assertIn("local_private/notification_state.json", combined)
        self.assertIn("local_private/review_gate.json", combined)
        self.assertIn("确认审核", combined)
        self.assertIn("暂不审核", combined)
        self.assertIn("只看状态", combined)
        self.assertIn("不会自动下单", combined)
        self.assertIn("最终交易由用户手动决定", combined)
        self.assertIn("不得修改真实 ~/.hermes", combined)

    def test_private_notification_state_is_not_committed(self) -> None:
        self.assertFalse((ROOT / "local_private" / "notification_state.json").exists())
        self.assertFalse((ROOT / "local_private" / "review_gate.json").exists())

    def test_loop_state_declares_completed_stage_with_draft_layers(self) -> None:
        payload = json.loads((ROOT / "ops" / "state" / "loop_state.json").read_text())
        self.assertEqual(
            payload["current_stage"],
            "Stage 2D.1.1 public live preflight minimization completed",
        )
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["stage2b_task_status"], "completed")
        self.assertEqual(payload["stage2c_task_status"], "completed")
        self.assertEqual(payload["stage2d_task_status"], "planned_requires_user_approval")
        self.assertEqual(payload["stage2d1_task_status"], "completed_read_only")
        self.assertIsNone(payload["next_task"])
        self.assertEqual(payload["next_task_status"], "requires_user_approval_for_live_write")
        self.assertEqual(payload["notification_layer"], "drafted")
        self.assertEqual(payload["review_gate_layer"], "drafted")
        self.assertEqual(payload["chatgpt_review_relay"], "drafted")
        self.assertFalse(payload["computer_use_live_execution"])
        self.assertTrue(payload["manual_chatgpt_review_mode"])
        self.assertTrue(payload["public_repo_review_mode"])


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_STAGE = "Stage 3.1 major review package ready"


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
        import subprocess

        for rel in ("local_private/notification_state.json", "local_private/review_gate.json"):
            tracked = subprocess.run(
                ["git", "ls-files", "--error-unmatch", rel],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(tracked.returncode, 0, rel)
            if (ROOT / rel).exists():
                ignored = subprocess.run(
                    ["git", "check-ignore", "-q", rel],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(ignored.returncode, 0, rel)

    def test_loop_state_declares_completed_stage_with_draft_layers(self) -> None:
        payload = json.loads((ROOT / "ops" / "state" / "loop_state.json").read_text())
        self.assertEqual(payload["current_stage"], EXPECTED_STAGE)
        self.assertEqual(payload["status"], "stage3_1_major_review_package_ready")
        self.assertEqual(payload["stage2b_task_status"], "completed")
        self.assertEqual(payload["stage2c_task_status"], "completed")
        self.assertEqual(payload["stage2d_task_status"], "planned_requires_user_approval")
        self.assertEqual(payload["stage2d1_task_status"], "completed_read_only")
        self.assertEqual(payload["stage2d2a_task_status"], "completed_minimal_live_install")
        self.assertEqual(
            payload["stage2d2b_task_status"],
            "review_gate_confirmed_locally",
        )
        self.assertEqual(
            payload["stage2e0_task_status"],
            "completed_with_degraded_input_delivery",
        )
        self.assertEqual(
            payload["stage2e1_task_status"],
            "completed_repo_only_relay_hardening",
        )
        self.assertEqual(
            payload["stage2f_task_status"],
            "completed_repo_only_review_governance_refactor",
        )
        self.assertEqual(
            payload["stage2f1_task_status"],
            "completed_repo_only_branch_governance_stage3_plan",
        )
        self.assertEqual(payload["next_task"], "Manual ChatGPT major-stage review by user")
        self.assertEqual(
            payload["next_task_status"],
            "ready_for_user",
        )
        self.assertEqual(
            payload["notification_layer"],
            "major_gate_finalization_completed_replacement_preview_ready",
        )
        self.assertEqual(payload["review_gate_layer"], "confirmed_local_private_gate")
        self.assertTrue(payload["feishu_message_sent"])
        self.assertTrue(payload["review_gate_written"])
        self.assertTrue(payload["feishu_confirmation_observed"])
        self.assertEqual(payload["chatgpt_review_relay"], "deprecated_by_stage2f1")
        self.assertTrue(payload["computer_use_live_execution"])
        self.assertFalse(payload["current_stage_computer_use_executed"])
        self.assertFalse(payload["stage2e1_computer_use_executed"])
        self.assertFalse(payload["stage2f_computer_use_executed"])
        self.assertFalse(payload["stage2f1_computer_use_executed"])
        self.assertFalse(payload["current_stage_computer_use_executed"])
        self.assertFalse(payload["current_stage_feishu_message_sent"])
        self.assertFalse(payload["current_stage_chatgpt_review_requested"])
        self.assertTrue(payload["chatgpt_computer_use_auto_review_deprecated"])
        self.assertTrue(payload["manual_chatgpt_review_mode"])
        self.assertTrue(payload["public_repo_review_mode"])


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3F major_gate_feishu_notification_sent"
CURRENT_STAGE = "Stage 3F.1 review_target_commit_consistency_fixed"
REVIEW_TARGET_COMMIT = "9c8ad5841bf30585575b78511e30e21b661f5774"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class Stage3FFeishuNotificationTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_live_notification_report_records_success_without_private_content(self) -> None:
        report = read_json("reports/live_notifications/stage3f_major_gate_feishu_notification.json")
        safety = read_json("reports/live_notifications/stage3f_safety_results.json")

        self.assertEqual(report["stage"], STAGE)
        self.assertEqual(report["status"], "completed_live_notification")
        self.assertEqual(report["precondition_status"], "major_stage_ready")
        self.assertTrue(report["manual_chatgpt_review_ready"])
        self.assertEqual(report["review_target_commit"], REVIEW_TARGET_COMMIT)
        self.assertTrue(report["feishu_message_sent"])
        self.assertEqual(report["feishu_message_count"], 1)
        self.assertFalse(report["feishu_message_sensitive_content"])
        self.assertEqual(report["delivery_command_public"], "hermes send --to feishu --quiet --file -")
        self.assertFalse(report["chatgpt_review_requested_by_codex"])
        self.assertFalse(report["sent_to_chatgpt"])
        self.assertFalse(report["computer_use_executed"])
        self.assertFalse(report["real_hermes_config_modified"])
        self.assertFalse(report["real_openclaw_modified"])
        self.assertFalse(report["real_feishu_gateway_modified"])
        self.assertFalse(report["services_restarted"])
        self.assertFalse(report["dependencies_installed"])
        self.assertFalse(report["secrets_touched"])
        self.assertFalse(report["secret_values_printed"])
        self.assertFalse(report["secret_values_committed"])
        self.assertFalse(report["auto_trading_surface"])
        self.assertFalse(report["broker_surface"])

        self.assertEqual(safety["stage"], STAGE)
        self.assertEqual(safety["status"], "pass")
        self.assertTrue(safety["feishu_message_sent"])
        self.assertEqual(safety["feishu_message_count"], 1)
        for field in (
            "secrets_touched",
            "secret_values_printed",
            "secret_values_committed",
            "real_config_modified",
            "hermes_config_modified",
            "openclaw_modified",
            "feishu_gateway_modified",
            "services_restarted",
            "dependencies_installed",
            "computer_use_executed",
            "chatgpt_review_requested_by_codex",
            "sent_to_chatgpt",
            "auto_trading_surface",
            "broker_surface",
        ):
            self.assertFalse(safety[field], field)

        public_text = read_text("reports/live_notifications/stage3f_major_gate_feishu_notification.md")
        for forbidden in (
            "/" + "Users" + "/",
            "/" + "Volumes" + "/",
            "token" + "=",
            "secret" + "=",
            "auth" + "=",
        ):
            self.assertNotIn(forbidden, public_text)
        self.assertIn("Final trading is manually decided by the user.", public_text)

    def test_runner_loop_handoff_and_review_request_record_stage3f1_after_notification(self) -> None:
        runner = read_json("ops/runners/stage3_runner_state.json")
        loop_state = read_json("ops/state/loop_state.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review = read_json("reports/review_requests/latest.json")
        notification = read_json("reports/review_requests/notification_preview.json")
        relay = read_json("reports/review_requests/relay_status.json")

        self.assertEqual(runner["status"], "major_stage_ready")
        self.assertEqual(runner["current_minor_stage"], "Stage 3F.1")
        self.assertEqual(runner["current_task"], "ops/tasks/stage3f1_review_target_commit_consistency.md")
        self.assertIn("Stage 3F", runner["completed_minor_stages"])
        self.assertIn("Stage 3F.1", runner["completed_minor_stages"])
        self.assertEqual(runner["remaining_minor_stages"], [])
        self.assertTrue(runner["feishu_notification_sent"])
        self.assertEqual(runner["feishu_notification_status"], "sent")
        self.assertFalse(runner["real_config_modified"])
        self.assertFalse(runner["computer_use_executed"])
        self.assertFalse(runner["requires_user_attention"])

        self.assertEqual(loop_state["current_stage"], CURRENT_STAGE)
        self.assertEqual(loop_state["status"], "stage3f1_review_target_commit_consistency_fixed")
        self.assertEqual(loop_state["stage3f_task_status"], "completed_live_notification")
        self.assertEqual(loop_state["stage3f1_task_status"], "completed_consistency_fix")
        self.assertFalse(loop_state["current_stage_feishu_message_sent"])
        self.assertFalse(loop_state["current_stage_real_config_modified"])
        self.assertFalse(loop_state["current_stage_hermes_modified"])
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])
        self.assertEqual(loop_state["review_target_commit"], REVIEW_TARGET_COMMIT)

        for payload in (handoff, review):
            self.assertEqual(payload["stage"], CURRENT_STAGE)
            self.assertEqual(payload["loop_state_stage"], CURRENT_STAGE)
            self.assertEqual(payload["review_target_commit"], REVIEW_TARGET_COMMIT)
            self.assertTrue(payload["manual_chatgpt_review_ready"])
            self.assertTrue(payload["feishu_message_sent"])
            self.assertFalse(payload["chatgpt_review_requested"])
            self.assertFalse(payload["sent_to_chatgpt"])
            self.assertFalse(payload["computer_use_executed"])

        self.assertEqual(notification["mode"], "live_feishu_notification_sent")
        self.assertTrue(notification["sent_to_feishu"])
        self.assertEqual(relay["relay_stage"], "stage3f1_review_target_commit_consistent_manual_review_ready")
        self.assertTrue(relay["feishu_message_sent"])
        self.assertEqual(relay["review_target_consistency_status"], "passed")
        self.assertFalse(relay["sent_to_chatgpt"])
        self.assertFalse(relay["computer_use_executed"])

    def test_stage3f_generator_is_guarded_by_major_gate_precondition(self) -> None:
        script = read_text("scripts/reports/generate_stage3f_feishu_notification_report.py")
        self.assertIn('runner.get("status") != "major_stage_ready"', script)
        self.assertIn('runner.get("manual_chatgpt_review_ready") is not True', script)
        self.assertIn("blocked_feishu_notification", script)
        self.assertIn("hermes send --to feishu --quiet --file -", script)

    def test_stage3f_safety_scripts_pass(self) -> None:
        for command in (
            ["scripts/safety/check_handoff_commit_consistency.py", "--root", str(ROOT)],
            ["scripts/safety/check_review_relay_safety.py", "--root", str(ROOT)],
        ):
            result = self.run_cmd(command)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertFalse(payload["findings"])


if __name__ == "__main__":
    unittest.main()

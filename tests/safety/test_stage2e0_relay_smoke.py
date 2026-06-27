import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "relay_smoke"
STAGE = "Stage 2E.0 Computer Use ChatGPT relay smoke completed with degraded input delivery"
D2B_RELAY_TARGET = "d30169e512f260dd5b29eb328d0f41c73cc927a9"

JSON_FILES = {
    "relay": REPORT_DIR / "stage2e0_chatgpt_relay_smoke_report.json",
    "safety": REPORT_DIR / "stage2e0_safety_test_results.json",
}
MD_FILES = {
    "relay": REPORT_DIR / "stage2e0_chatgpt_relay_smoke_report.md",
    "safety": REPORT_DIR / "stage2e0_safety_test_results.md",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Stage2E0RelaySmokeTest(unittest.TestCase):
    def test_stage2e0_reports_exist(self) -> None:
        for label, path in JSON_FILES.items():
            self.assertTrue(path.exists(), label)
        for label, path in MD_FILES.items():
            self.assertTrue(path.exists(), label)

    def test_relay_report_records_actual_ui_result(self) -> None:
        payload = read_json(JSON_FILES["relay"])
        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["relay_target_commit"], D2B_RELAY_TARGET)
        self.assertTrue(payload["review_gate_valid_before_relay"])
        self.assertTrue(payload["computer_use_executed"])
        self.assertTrue(payload["sent_to_chatgpt"])
        self.assertTrue(payload["chatgpt_conversation_created"])
        self.assertTrue(payload["chatgpt_repo_access_observed"])
        self.assertTrue(payload["chatgpt_review_started"])
        self.assertFalse(payload["chatgpt_review_completed"])
        self.assertEqual(payload["input_delivery_quality"], "degraded_split_prompt")
        self.assertTrue(payload["unsent_draft_left_in_chatgpt_input"])
        self.assertFalse(payload["secrets_sent"])
        self.assertFalse(payload["local_paths_sent"])
        self.assertFalse(payload["broker_or_trading_site_accessed"])
        self.assertFalse(payload["openclaw_modified"])
        self.assertFalse(payload["hermes_modified"])
        self.assertFalse(payload["feishu_gateway_modified"])
        self.assertFalse(payload["services_restarted"])
        self.assertFalse(payload["dependencies_installed"])
        self.assertFalse(payload["auto_trading_surface"])

    def test_relay_status_records_sent_but_no_trading_surface(self) -> None:
        status = read_json(ROOT / "reports" / "review_requests" / "relay_status.json")
        self.assertEqual(status["relay_stage"], "stage2e0_chatgpt_relay_smoke")
        self.assertTrue(status["computer_use_executed"])
        self.assertTrue(status["sent_to_chatgpt"])
        self.assertEqual(status["expected_commit"], D2B_RELAY_TARGET)
        self.assertEqual(status["status_reason"], "sent_with_degraded_split_prompt")
        self.assertFalse(status["auto_trading_surface"])
        self.assertFalse(status["broker_or_trading_site_accessed"])

    def test_safety_results_record_forbidden_actions_absent(self) -> None:
        payload = read_json(JSON_FILES["safety"])
        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["status"], "passed_with_relay_delivery_warning")
        self.assertTrue(payload["computer_use_executed"])
        self.assertTrue(payload["sent_to_chatgpt"])
        self.assertFalse(payload["secrets_sent"])
        self.assertFalse(payload["local_paths_sent"])
        self.assertFalse(payload["openclaw_modified"])
        self.assertFalse(payload["hermes_modified"])
        self.assertFalse(payload["feishu_gateway_modified"])
        self.assertFalse(payload["services_restarted"])
        self.assertFalse(payload["dependencies_installed"])
        self.assertFalse(payload["auto_trading_surface"])
        self.assertFalse(payload["broker_or_trading_site_accessed"])

    def test_public_reports_do_not_expose_private_paths_or_secret_values(self) -> None:
        combined = "\n".join(read_text(path) for path in [*JSON_FILES.values(), *MD_FILES.values()])
        forbidden_fragments = [
            "/" + "Users" + "/",
            "/" + "Volumes" + "/",
            "FEISHU" + "_APP" + "_SECRET",
            "OpenAI API key",
            "token=",
            "secret=",
            "auth=",
            "chat_id",
            "user_id",
            "one_time_nonce",
        ]
        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, combined)
        self.assertIn("Final trading is manually decided by the user", combined)


if __name__ == "__main__":
    unittest.main()

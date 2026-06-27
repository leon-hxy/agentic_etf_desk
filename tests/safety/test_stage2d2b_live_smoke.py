import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "live_smoke"
STAGE = "Stage 2D.2B live notification smoke completed; review gate pending"
SKILL_IDS = ["feishu-loop-notifier", "feishu-review-command"]

JSON_FILES = {
    "smoke": REPORT_DIR / "stage2d2b_smoke_test_report.json",
    "gate": REPORT_DIR / "stage2d2b_review_gate_validation_report.json",
    "rollback": REPORT_DIR / "stage2d2b_rollback_note.json",
    "safety": REPORT_DIR / "stage2d2b_safety_test_results.json",
}
MD_FILES = {
    "smoke": REPORT_DIR / "stage2d2b_smoke_test_report.md",
    "gate": REPORT_DIR / "stage2d2b_review_gate_validation_report.md",
    "rollback": REPORT_DIR / "stage2d2b_rollback_note.md",
    "safety": REPORT_DIR / "stage2d2b_safety_test_results.md",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Stage2D2BLiveSmokeTest(unittest.TestCase):
    def test_live_smoke_reports_exist(self) -> None:
        for label, path in JSON_FILES.items():
            self.assertTrue(path.exists(), label)
        for label, path in MD_FILES.items():
            self.assertTrue(path.exists(), label)

    def test_smoke_report_records_only_approved_live_scope(self) -> None:
        payload = read_json(JSON_FILES["smoke"])
        self.assertEqual(payload["stage"], STAGE)
        self.assertTrue(payload["approved_live_smoke"])
        self.assertTrue(payload["hermes_skill_load_checked"])
        self.assertTrue(payload["hermes_skills_enabled"])
        self.assertEqual(payload["installed_skill_ids"], SKILL_IDS)
        self.assertTrue(payload["feishu_message_sent"])
        self.assertEqual(payload["feishu_message_count"], 1)
        self.assertFalse(payload["feishu_message_sensitive_content"])
        self.assertTrue(payload["gateway_status_checked"])
        self.assertFalse(payload["openclaw_modified"])
        self.assertFalse(payload["feishu_gateway_modified"])
        self.assertFalse(payload["services_restarted"])
        self.assertFalse(payload["dependencies_installed"])
        self.assertFalse(payload["computer_use_executed"])
        self.assertFalse(payload["secret_values_printed"])
        self.assertFalse(payload["secret_values_committed"])
        self.assertFalse(payload["auto_trading_surface"])

    def test_review_gate_validation_records_pending_confirmation(self) -> None:
        payload = read_json(JSON_FILES["gate"])
        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["review_gate_status"], "pending_feishu_confirmation")
        self.assertFalse(payload["feishu_confirmation_observed"])
        self.assertFalse(payload["review_gate_written"])
        self.assertFalse(payload["review_gate_file_present"])
        self.assertTrue(payload["local_private_gitignored"])
        self.assertEqual(payload["allowed_confirmation_phrase"], "确认审核")
        self.assertEqual(payload["gate_path_public"], "local_private/review_gate.json")
        self.assertFalse(payload["review_gate_committed"])

    def test_rollback_note_records_no_new_live_file_changes(self) -> None:
        payload = read_json(JSON_FILES["rollback"])
        self.assertEqual(payload["stage"], STAGE)
        self.assertFalse(payload["rollback_executed"])
        self.assertFalse(payload["new_live_files_created"])
        self.assertEqual(payload["new_live_config_changes"], [])
        self.assertEqual(payload["rollback_action"], "none_required_for_stage2d2b_send_smoke")
        self.assertTrue(payload["stage2d2a_rollback_manifest_still_applies"])

    def test_safety_results_record_forbidden_actions_absent(self) -> None:
        payload = read_json(JSON_FILES["safety"])
        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertTrue(payload["feishu_message_sent"])
        self.assertFalse(payload["openclaw_modified"])
        self.assertFalse(payload["feishu_gateway_modified"])
        self.assertFalse(payload["services_restarted"])
        self.assertFalse(payload["dependencies_installed"])
        self.assertFalse(payload["computer_use_executed"])
        self.assertFalse(payload["secret_values_printed"])
        self.assertFalse(payload["secret_values_committed"])
        self.assertFalse(payload["auto_trading_surface"])
        self.assertFalse(payload["broker_surface"])

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
            "private_backup_path",
            "chat_id",
            "user_id",
            "services_restarted: true",
            "dependencies_installed: true",
            "computer_use_executed: true",
        ]
        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, combined)
        self.assertIn("Final trading is manually decided by the user", combined)


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "live_preflight"
TASK = ROOT / "ops" / "tasks" / "stage2d1_read_only_live_preflight.md"
JSON_FILES = {
    "preflight": REPORT_DIR / "stage2d1_live_preflight_report.json",
    "minimal_change": REPORT_DIR / "stage2d1_minimal_change_list.json",
    "backup": REPORT_DIR / "stage2d1_backup_checklist.json",
    "rollback": REPORT_DIR / "stage2d1_rollback_checklist.json",
    "safety": REPORT_DIR / "stage2d1_safety_test_results.json",
}
MD_FILES = {
    "preflight": REPORT_DIR / "stage2d1_live_preflight_report.md",
    "minimal_change": REPORT_DIR / "stage2d1_minimal_change_list.md",
    "backup": REPORT_DIR / "stage2d1_backup_checklist.md",
    "rollback": REPORT_DIR / "stage2d1_rollback_checklist.md",
    "safety": REPORT_DIR / "stage2d1_safety_test_results.md",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Stage2D1LivePreflightTest(unittest.TestCase):
    def test_task_and_reports_exist(self) -> None:
        self.assertTrue(TASK.exists())
        task = read_text(TASK)
        self.assertIn("status: completed_read_only", task)
        self.assertIn("stage: Stage 2D.1 read-only live preflight completed", task)
        self.assertIn("Do not modify real `~/.hermes`", task)
        self.assertIn("Do not modify real `~/.openclaw`", task)
        self.assertIn("Do not send real Feishu messages", task)

        for label, path in JSON_FILES.items():
            self.assertTrue(path.exists(), label)
        for label, path in MD_FILES.items():
            self.assertTrue(path.exists(), label)

    def test_live_preflight_report_is_read_only_and_redacted(self) -> None:
        payload = read_json(JSON_FILES["preflight"])
        self.assertEqual(payload["stage"], "Stage 2D.1 read-only live preflight completed")
        self.assertEqual(payload["mode"], "read_only_live_preflight")
        self.assertTrue(payload["approval_scope"]["read_only_live_preflight"])

        for field in (
            "real_config_modified",
            "hermes_modified",
            "openclaw_modified",
            "feishu_gateway_modified",
            "services_restarted",
            "dependencies_installed",
            "secrets_touched",
            "secret_values_written",
            "feishu_message_sent",
            "computer_use_executed",
            "auto_trading_surface",
        ):
            self.assertIs(payload["safety_flags"][field], False, field)

        self.assertIn("~/.hermes/config.yaml", payload["hermes"]["config_paths"])
        self.assertIn("~/.hermes/.env", payload["hermes"]["config_paths"])
        self.assertIn("~/.hermes/skills", payload["installable_points"])
        self.assertIn("FEISHU_APP_ID", payload["feishu_gateway"]["expected_key_names"])
        self.assertIn("FEISHU_APP_SECRET", payload["feishu_gateway"]["expected_key_names"])

    def test_change_backup_rollback_and_safety_outputs_are_gate_only(self) -> None:
        minimal = read_json(JSON_FILES["minimal_change"])
        backup = read_json(JSON_FILES["backup"])
        rollback = read_json(JSON_FILES["rollback"])
        safety = read_json(JSON_FILES["safety"])

        self.assertEqual(minimal["mode"], "planned_only")
        self.assertTrue(minimal["requires_user_approval_before_live_change"])
        self.assertFalse(minimal["live_changes_applied"])
        self.assertFalse(backup["backup_created"])
        self.assertTrue(backup["requires_user_approval_before_backup"])
        self.assertFalse(rollback["rollback_executed"])
        self.assertTrue(rollback["requires_user_approval_before_rollback"])
        self.assertEqual(safety["status"], "passed")
        self.assertFalse(safety["live_actions_detected"])

    def test_reports_do_not_contain_private_values_or_live_action_artifacts(self) -> None:
        combined = "\n".join(read_text(path) for path in [TASK, *JSON_FILES.values(), *MD_FILES.values()])
        forbidden_fragments = [
            "/" + "Users" + "/",
            "/" + "Volumes" + "/",
            "FEISHU" + "_APP" + "_SECRET=",
            "OpenAI API key=",
            "token=",
            "secret=",
            "auth=",
            "sent_to_feishu: true",
            "computer_use_executed: true",
            "services_restarted: true",
            "dependencies_installed: true",
        ]
        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, combined)
        self.assertIn("Final trading is manually decided by the user", combined)


if __name__ == "__main__":
    unittest.main()

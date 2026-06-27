import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "live_install"
JSON_FILES = {
    "install": REPORT_DIR / "stage2d2a_live_install_report.json",
    "rollback": REPORT_DIR / "stage2d2a_rollback_manifest.json",
    "safety": REPORT_DIR / "stage2d2a_safety_test_results.json",
}
MD_FILES = {
    "install": REPORT_DIR / "stage2d2a_live_install_report.md",
    "rollback": REPORT_DIR / "stage2d2a_rollback_manifest.md",
    "safety": REPORT_DIR / "stage2d2a_safety_test_results.md",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Stage2D2ALiveInstallTest(unittest.TestCase):
    def test_live_install_reports_exist(self) -> None:
        for label, path in JSON_FILES.items():
            self.assertTrue(path.exists(), label)
        for label, path in MD_FILES.items():
            self.assertTrue(path.exists(), label)

    def test_live_install_report_records_only_approved_scope(self) -> None:
        payload = read_json(JSON_FILES["install"])
        self.assertEqual(
            payload["stage"],
            "Stage 2D.2A minimal live Hermes skills install completed",
        )
        self.assertTrue(payload["approved_live_install"])
        self.assertTrue(payload["backup_created"])
        self.assertTrue(payload["backup_outside_public_repo"])
        self.assertEqual(payload["backup_path_public"], "outside_public_repo_private_backup")
        self.assertTrue(payload["live_hermes_skills_modified"])
        self.assertFalse(payload["openclaw_modified"])
        self.assertFalse(payload["services_restarted"])
        self.assertFalse(payload["dependencies_installed"])
        self.assertFalse(payload["feishu_message_sent"])
        self.assertFalse(payload["computer_use_executed"])
        self.assertFalse(payload["secret_values_printed"])
        self.assertFalse(payload["secret_values_committed"])
        self.assertFalse(payload["auto_trading_surface"])
        self.assertEqual(
            payload["installed_skill_ids"],
            ["feishu-loop-notifier", "feishu-review-command"],
        )

    def test_rollback_manifest_uses_private_backup_without_public_paths(self) -> None:
        payload = read_json(JSON_FILES["rollback"])
        self.assertTrue(payload["rollback_available"])
        self.assertFalse(payload["rollback_executed"])
        self.assertEqual(payload["backup_path_public"], "outside_public_repo_private_backup")
        self.assertEqual(
            payload["installed_skill_target_labels"],
            [
                "~/.hermes/skills/feishu-loop-notifier/SKILL.md",
                "~/.hermes/skills/feishu-review-command/SKILL.md",
            ],
        )

    def test_safety_results_record_no_forbidden_live_actions(self) -> None:
        payload = read_json(JSON_FILES["safety"])
        self.assertEqual(payload["status"], "passed")
        self.assertTrue(payload["approved_hermes_skills_install"])
        self.assertFalse(payload["openclaw_modified"])
        self.assertFalse(payload["services_restarted"])
        self.assertFalse(payload["dependencies_installed"])
        self.assertFalse(payload["feishu_message_sent"])
        self.assertFalse(payload["computer_use_executed"])
        self.assertFalse(payload["secret_values_printed"])
        self.assertFalse(payload["secret_values_committed"])
        self.assertFalse(payload["auto_trading_surface"])

    def test_public_reports_do_not_expose_private_paths_or_secret_values(self) -> None:
        combined = "\n".join(read_text(path) for path in [*JSON_FILES.values(), *MD_FILES.values()])
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

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "reports" / "loop_dry_run" / "stage2c_loop_dry_run.json"
REPORT_MD = ROOT / "reports" / "loop_dry_run" / "stage2c_loop_dry_run.md"
NOTIFICATION_JSON = ROOT / "reports" / "review_requests" / "notification_preview.json"
NOTIFICATION_MD = ROOT / "reports" / "review_requests" / "notification_preview.md"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class LoopAutomationDryRunTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_stage2c_dry_run_check_passes(self) -> None:
        result = self.run_cmd(["scripts/safety/run_loop_dry_run.py", "--check", "--root", str(ROOT)])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["findings"])

    def test_stage2c_report_is_repo_only_and_dry_run(self) -> None:
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())
        payload = read_json(REPORT_JSON)
        self.assertEqual(payload["stage"], "Stage 2C completed")
        self.assertEqual(payload["mode"], "repo_only_dry_run")
        self.assertTrue(payload["dry_run_only"])
        self.assertEqual(payload["state_transition"]["from"], "Stage 2B completed")
        self.assertEqual(payload["state_transition"]["to"], "Stage 2C completed")
        self.assertIsNone(payload["state_transition"]["next_task"])
        self.assertEqual(payload["state_transition"]["next_task_status"], "requires_user_direction")

        for path in payload["repo_only_writes"]:
            self.assertFalse(path.startswith("/"), path)
            self.assertFalse(path.startswith("~"), path)
            self.assertNotIn("local_private", path)

        for field in (
            "real_config_modified",
            "hermes_modified",
            "openclaw_modified",
            "feishu_gateway_modified",
            "services_restarted",
            "dependencies_installed",
            "secrets_touched",
            "auto_trading_surface",
            "computer_use_executed",
        ):
            self.assertIs(payload["safety_flags"][field], False, field)

    def test_loop_state_and_task_mark_stage2c_completed(self) -> None:
        loop_state = read_json(ROOT / "ops" / "state" / "loop_state.json")
        self.assertEqual(loop_state["current_stage"], "Stage 2D.1 read-only live preflight completed")
        self.assertEqual(loop_state["status"], "completed")
        self.assertEqual(loop_state["stage2c_task"], "ops/tasks/stage2c_loop_automation_dry_run.md")
        self.assertEqual(loop_state["stage2c_task_status"], "completed")
        self.assertEqual(loop_state["stage2d_task"], "ops/tasks/stage2d_hermes_feishu_approval_gate_preflight.md")
        self.assertEqual(loop_state["stage2d1_task"], "ops/tasks/stage2d1_read_only_live_preflight.md")
        self.assertEqual(loop_state["next_task_status"], "requires_user_approval_for_live_write")

        task = (ROOT / "ops" / "tasks" / "stage2c_loop_automation_dry_run.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("status: completed", task)
        self.assertIn("stage: Stage 2C completed", task)
        self.assertIn("repo-only dry run completed", task)

    def test_notification_preview_is_draft_only_and_manual(self) -> None:
        self.assertTrue(NOTIFICATION_JSON.exists())
        self.assertTrue(NOTIFICATION_MD.exists())
        payload = read_json(NOTIFICATION_JSON)
        self.assertEqual(payload["stage"], "Stage 2D.1 read-only live preflight completed")
        self.assertFalse(payload["sent_to_feishu"])
        self.assertFalse(payload["computer_use_executed"])
        self.assertEqual(payload["mode"], "repo_only_preview")

        preview = NOTIFICATION_MD.read_text(encoding="utf-8")
        self.assertIn("不会自动下单", preview)
        self.assertIn("最终交易由用户手动决定", preview)
        self.assertIn("Computer Use 未执行", preview)


if __name__ == "__main__":
    unittest.main()

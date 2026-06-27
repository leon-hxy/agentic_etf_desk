import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT / "ops/tasks/stage2d_hermes_feishu_approval_gate_preflight.md"
PLAN_DIR = ROOT / "docs/stage2d_hermes_feishu_approval_gate_preflight"
PLAN_FILES = {
    "installation": PLAN_DIR / "installation_plan.md",
    "backup": PLAN_DIR / "backup_plan.md",
    "rollback": PLAN_DIR / "rollback_plan.md",
    "safety": PLAN_DIR / "safety_checks.md",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def loop_state() -> dict:
    return json.loads((ROOT / "ops/state/loop_state.json").read_text(encoding="utf-8"))


class Stage2DPreparationPlanTest(unittest.TestCase):
    def test_stage2d_task_file_exists_and_requires_approval(self) -> None:
        self.assertTrue(TASK.exists())
        task = read(TASK)
        self.assertIn("status: planned_requires_user_approval", task)
        self.assertIn("stage: Stage 2D Hermes Feishu approval gate preparation", task)
        self.assertIn("Do not modify real `~/.hermes`", task)
        self.assertIn("Do not modify a real Feishu gateway", task)
        self.assertIn("Do not restart services", task)
        self.assertIn("Do not install dependencies", task)
        self.assertIn("Do not run real Computer Use", task)
        self.assertIn("No secrets may be written", task)

    def test_install_backup_rollback_and_safety_plans_exist(self) -> None:
        for label, path in PLAN_FILES.items():
            self.assertTrue(path.exists(), label)
            text = read(path)
            self.assertIn("Repo-only preparation", text, label)
            self.assertIn("requires explicit user approval", text, label)
            self.assertIn("Do not modify real `~/.hermes`", text, label)
            self.assertIn("Do not modify a real Feishu gateway", text, label)
            self.assertIn("Do not restart services", text, label)

    def test_loop_state_points_to_stage2d_preparation_without_live_action(self) -> None:
        payload = loop_state()
        self.assertIn(
            payload["current_stage"],
            {
                "Stage 2D preparation plan completed",
                "Stage 2D.1 read-only live preflight completed",
                "Stage 2D.1.1 public live preflight minimization completed",
                "Stage 2D.2A minimal live Hermes skills install completed",
            },
        )
        self.assertEqual(payload["stage2d_task"], "ops/tasks/stage2d_hermes_feishu_approval_gate_preflight.md")
        self.assertEqual(payload["stage2d_task_status"], "planned_requires_user_approval")
        self.assertIn(
            payload["next_task_status"],
            {
                "requires_user_approval",
                "requires_user_approval_for_live_write",
                "requires_user_approval_for_any_live_followup",
            },
        )
        if payload["current_stage"] == "Stage 2D.2A minimal live Hermes skills install completed":
            self.assertTrue(payload["real_config_modified"])
            self.assertTrue(payload["hermes_modified"])
        else:
            self.assertFalse(payload["real_config_modified"])
            self.assertFalse(payload["hermes_modified"])
        for field in (
            "openclaw_modified",
            "feishu_gateway_modified",
            "services_restarted",
            "dependencies_installed",
            "secrets_touched",
            "auto_trading_surface",
            "computer_use_executed",
            "computer_use_live_execution",
        ):
            self.assertIs(payload[field], False, field)

    def test_stage2d_plan_files_do_not_contain_private_or_live_execution_artifacts(self) -> None:
        combined = "\n".join(read(path) for path in [TASK, *PLAN_FILES.values()])
        forbidden_fragments = [
            "/" + "Users" + "/",
            "/" + "Volumes" + "/",
            "FEISHU" + "_APP" + "_SECRET=",
            "OpenAI API key=",
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

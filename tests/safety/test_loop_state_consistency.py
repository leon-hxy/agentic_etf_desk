import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class LoopStateConsistencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.handoff = read_json("reports/codex_handoff/latest.json")
        self.review = read_json("reports/review_requests/latest.json")
        self.loop_state = read_json("ops/state/loop_state.json")

    def expected_loop_stage(self) -> str:
        return str(self.handoff.get("loop_state_stage") or self.handoff["stage"])

    def test_loop_state_matches_handoff_and_review_completed_stage(self) -> None:
        expected_stage = self.expected_loop_stage()
        if self.loop_state.get("handoff_update_pending"):
            self.assertEqual(self.loop_state["current_stage"], "Stage 2C completed")
            self.assertNotEqual(expected_stage, self.loop_state["current_stage"])
        else:
            self.assertEqual(expected_stage, "Stage 2C completed")
            self.assertEqual(self.review.get("loop_state_stage", expected_stage), expected_stage)
            self.assertEqual(self.loop_state["current_stage"], expected_stage)
        self.assertEqual(self.loop_state["status"], "completed")

    def test_loop_state_points_to_current_handoff_review_and_next_task(self) -> None:
        self.assertEqual(self.loop_state["last_handoff"], "reports/codex_handoff/latest.json")
        self.assertEqual(self.loop_state["last_review_request"], "reports/review_requests/latest.json")
        self.assertEqual(
            self.loop_state["next_task"],
            None,
        )
        self.assertEqual(
            self.loop_state["stage2b_task"],
            "ops/tasks/stage2b_repo_only.md",
        )
        self.assertEqual(
            self.loop_state["stage2c_task"],
            "ops/tasks/stage2c_loop_automation_dry_run.md",
        )

    def test_stage2b_task_is_marked_completed(self) -> None:
        task = read_text("ops/tasks/stage2b_repo_only.md")
        self.assertIn("status: completed", task)
        self.assertIn("stage: Stage 2B completed", task)
        self.assertIn("review_target_commit", task)

    def test_stage2c_dry_run_task_is_completed_repo_only_work(self) -> None:
        task_path = ROOT / "ops/tasks/stage2c_loop_automation_dry_run.md"
        self.assertTrue(task_path.exists())
        task = task_path.read_text(encoding="utf-8")
        self.assertIn("status: completed", task)
        self.assertIn("stage: Stage 2C completed", task)
        self.assertIn("Repo-only", task)
        self.assertIn("Do not modify real `~/.hermes`", task)
        self.assertIn("Do not modify real `~/.openclaw`", task)
        self.assertIn("Do not run Computer Use", task)

    def test_repo_only_safety_flags_remain_false(self) -> None:
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
            "computer_use_live_execution",
        ):
            self.assertIs(self.loop_state[field], False, field)


if __name__ == "__main__":
    unittest.main()

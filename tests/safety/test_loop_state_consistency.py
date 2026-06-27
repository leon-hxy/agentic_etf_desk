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
        return str(self.handoff["stage"])

    def test_loop_state_matches_handoff_and_review_completed_stage(self) -> None:
        expected_stage = self.expected_loop_stage()
        self.assertEqual(
            expected_stage,
            "Stage 2D.2B review gate confirmed locally",
        )
        self.assertFalse(self.loop_state.get("handoff_update_pending"))
        self.assertEqual(self.review["stage"], expected_stage)
        self.assertEqual(self.handoff.get("loop_state_stage"), expected_stage)
        self.assertEqual(self.review.get("loop_state_stage"), expected_stage)
        self.assertEqual(self.loop_state["current_stage"], expected_stage)
        self.assertEqual(
            self.loop_state["status"],
            "review_gate_confirmed_waiting_for_relay_approval",
        )

    def test_loop_state_binds_same_review_target_as_latest_artifacts(self) -> None:
        expected_commit = "d30169e512f260dd5b29eb328d0f41c73cc927a9"
        stale_commit = "88e31e9daedcabb070469600f4fe2437a42c150c"
        self.assertEqual(self.handoff["review_target_commit"], expected_commit)
        self.assertEqual(self.review["review_target_commit"], expected_commit)
        self.assertEqual(self.loop_state["review_target_commit"], expected_commit)
        self.assertNotEqual(self.loop_state["review_target_commit"], stale_commit)
        self.assertIn("Stage 2D.2B.1", self.loop_state["review_target_commit_note"])

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
        self.assertEqual(
            self.loop_state["stage2d_task"],
            "ops/tasks/stage2d_hermes_feishu_approval_gate_preflight.md",
        )
        self.assertEqual(
            self.loop_state["stage2d1_task"],
            "ops/tasks/stage2d1_read_only_live_preflight.md",
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

    def test_only_approved_live_install_flags_are_true(self) -> None:
        self.assertFalse(self.loop_state["repo_only"])
        self.assertTrue(self.loop_state["real_config_modified"])
        self.assertTrue(self.loop_state["hermes_modified"])
        self.assertEqual(
            self.loop_state["stage2d2a_task_status"],
            "completed_minimal_live_install",
        )
        self.assertEqual(
            self.loop_state["stage2d2b_task_status"],
            "review_gate_confirmed_locally",
        )
        self.assertTrue(self.loop_state["feishu_message_sent"])
        self.assertTrue(self.loop_state["review_gate_written"])
        self.assertTrue(self.loop_state["feishu_confirmation_observed"])
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
            self.assertIs(self.loop_state[field], False, field)


if __name__ == "__main__":
    unittest.main()

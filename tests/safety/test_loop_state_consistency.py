import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_STAGE = "Stage 3.1 WP2 real data quality and monthly panel completed_internal_review"


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
        self.assertEqual(expected_stage, EXPECTED_STAGE)
        self.assertFalse(self.loop_state.get("handoff_update_pending"))
        self.assertEqual(self.review["stage"], expected_stage)
        self.assertEqual(self.handoff.get("loop_state_stage"), expected_stage)
        self.assertEqual(self.review.get("loop_state_stage"), expected_stage)
        self.assertEqual(self.loop_state["current_stage"], expected_stage)
        self.assertEqual(self.loop_state["status"], "stage3_1_wp2_completed_internal_review")

    def test_loop_state_binds_same_review_target_as_latest_artifacts(self) -> None:
        expected_commit = self.handoff["review_target_commit"]
        stale_commits = {
            "d30169e512f260dd5b29eb328d0f41c73cc927a9",
            "74215dd69814c07fd5c3fd3937ccee15f9be8e8f",
            "23cebebed1d07f0b35e66b284ec0891b427d8716",
            "9ac1dd8b96fe98bae4bd676966293f03e0908047",
            "5a5d68e2e34c6203ee2ab784dbbe3fa9a1cf1a6d",
            "2006d60f237a9b47f34236fd7dd299e9bbdb4f86",
            "23714230ebda5bbaa16c27fac9efdf8d76663911",
        }
        self.assertEqual(self.handoff["review_target_commit"], expected_commit)
        self.assertEqual(self.review["review_target_commit"], expected_commit)
        self.assertEqual(self.loop_state["review_target_commit"], expected_commit)
        self.assertNotIn(self.loop_state["review_target_commit"], stale_commits)
        self.assertIn("WP2", self.loop_state["commit_binding_note"])

    def test_loop_state_points_to_current_handoff_review_and_next_task(self) -> None:
        self.assertEqual(self.loop_state["last_handoff"], "reports/codex_handoff/latest.json")
        self.assertEqual(self.loop_state["last_review_request"], "reports/review_requests/latest.json")
        self.assertEqual(self.loop_state["next_task"], "WP3 formal backtest and evidence package")
        self.assertEqual(self.loop_state["next_task_status"], "ready")
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
        self.assertTrue(self.loop_state["current_stage_repo_only"])
        self.assertFalse(self.loop_state["current_stage_live_notification"])
        self.assertTrue(self.loop_state["real_config_modified"])
        self.assertFalse(self.loop_state["current_stage_real_config_modified"])
        self.assertTrue(self.loop_state["hermes_modified"])
        self.assertFalse(self.loop_state["current_stage_hermes_modified"])
        self.assertEqual(
            self.loop_state["stage2d2a_task_status"],
            "completed_minimal_live_install",
        )
        self.assertEqual(
            self.loop_state["stage2d2b_task_status"],
            "review_gate_confirmed_locally",
        )
        self.assertEqual(
            self.loop_state["stage2e0_task_status"],
            "completed_with_degraded_input_delivery",
        )
        self.assertEqual(
            self.loop_state["stage2e1_task_status"],
            "completed_repo_only_relay_hardening",
        )
        self.assertEqual(
            self.loop_state["stage2f_task_status"],
            "completed_repo_only_review_governance_refactor",
        )
        self.assertEqual(
            self.loop_state["stage2f1_task_status"],
            "completed_repo_only_branch_governance_stage3_plan",
        )
        self.assertEqual(
            self.loop_state["stage3_stage_branch"],
            "stage/stage3-data-backtest",
        )
        self.assertTrue(self.loop_state["stage3_business_code_started"])
        self.assertEqual(
            self.loop_state["stage3a_task_status"],
            "completed_internal_review",
        )
        self.assertEqual(
            self.loop_state["stage3b_task_status"],
            "completed_internal_review",
        )
        self.assertIsNone(self.loop_state["stage3_next_task"])
        self.assertEqual(self.loop_state["stage3e_task_status"], "completed_internal_review")
        self.assertEqual(self.loop_state["stage3f_task_status"], "finalization_fix_internal_reviewed")
        self.assertEqual(self.loop_state["stage3f1_task_status"], "finalization_fix_internal_reviewed")
        self.assertEqual(self.loop_state["stage3_major_gate_finalization_status"], "completed")
        self.assertTrue(self.loop_state["stage3_finalization_fixes_internal_reviewed"])
        self.assertFalse(self.loop_state["major_review_required"])
        self.assertFalse(self.loop_state["manual_chatgpt_review_ready"])
        self.assertTrue(self.loop_state["feishu_message_sent"])
        self.assertTrue(self.loop_state["review_gate_written"])
        self.assertTrue(self.loop_state["feishu_confirmation_observed"])
        self.assertTrue(self.loop_state["computer_use_executed"])
        self.assertTrue(self.loop_state["computer_use_live_execution"])
        self.assertFalse(self.loop_state["current_stage_computer_use_executed"])
        self.assertFalse(self.loop_state["stage2e1_computer_use_executed"])
        self.assertFalse(self.loop_state["stage2f_computer_use_executed"])
        self.assertFalse(self.loop_state["stage2f1_computer_use_executed"])
        self.assertFalse(self.loop_state["current_stage_computer_use_executed"])
        self.assertFalse(self.loop_state["current_stage_feishu_message_sent"])
        self.assertFalse(self.loop_state["current_stage_chatgpt_review_requested"])
        self.assertEqual(
            self.loop_state["chatgpt_review_relay"],
            "deprecated_by_stage2f1",
        )
        self.assertTrue(self.loop_state["chatgpt_computer_use_auto_review_deprecated"])
        self.assertEqual(
            self.loop_state["review_governance_mode"],
            "small_stage_codex_self_review_major_stage_chatgpt_manual",
        )
        for field in (
            "openclaw_modified",
            "feishu_gateway_modified",
            "services_restarted",
            "dependencies_installed",
            "secrets_touched",
            "auto_trading_surface",
        ):
            self.assertIs(self.loop_state[field], False, field)


if __name__ == "__main__":
    unittest.main()

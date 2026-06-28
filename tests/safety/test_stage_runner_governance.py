import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_DIR = ROOT / "ops" / "runners"
PROMPT_PATH = ROOT / "configs" / "codex_automation" / "stage3_runner_automation_prompt.md"
STAGE3_PATH = ROOT / "ops" / "stages" / "stage3.yaml"
TASK_3C = ROOT / "ops" / "tasks" / "stage3c_backtest_validation.md"
TASK_3D = ROOT / "ops" / "tasks" / "stage3d_strategy_evidence_report.md"
TASK_3E = ROOT / "ops" / "tasks" / "stage3_major_review_package.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalized_lower(text: str) -> str:
    return " ".join(text.lower().split())


def stage_block(text: str, stage_id: str) -> str:
    pattern = rf"  - id: {re.escape(stage_id)}\n(?P<body>(?:    .*\n|      .*\n)*)"
    match = re.search(pattern, text)
    if not match:
        return ""
    return match.group("body")


class StageRunnerGovernanceTest(unittest.TestCase):
    def test_stage3_runner_files_and_state_exist(self) -> None:
        runner_doc = RUNNER_DIR / "stage3_runner.md"
        runner_state = RUNNER_DIR / "stage3_runner_state.json"
        checklist = RUNNER_DIR / "stage3_runner_checklist.md"
        setup_review = ROOT / "reports" / "internal_reviews" / "stage3" / "stage3_runner_setup.md"

        for path in (runner_doc, runner_state, checklist, PROMPT_PATH, setup_review):
            self.assertTrue(path.exists(), str(path))

        state = read_json(runner_state)
        self.assertEqual(state["major_stage"], "Stage 3")
        self.assertEqual(state["branch"], "stage/stage3-data-backtest")
        self.assertEqual(state["status"], "major_stage_ready")
        self.assertEqual(state["current_minor_stage"], "Stage 3F.1")
        self.assertEqual(state["current_task"], "ops/tasks/stage3f1_review_target_commit_consistency.md")
        self.assertEqual(state["completed_minor_stages"], ["Stage 3A", "Stage 3B", "Stage 3C", "Stage 3D", "Stage 3E", "Stage 3F", "Stage 3F.1"])
        self.assertEqual(state["remaining_minor_stages"], [])
        self.assertEqual(
            state["last_pushed_commit"],
            "9c8ad5841bf30585575b78511e30e21b661f5774",
        )
        self.assertTrue(state["feishu_notification_sent"])
        self.assertEqual(state["feishu_notification_status"], "sent")
        self.assertEqual(state["review_target_consistency_status"], "passed")
        self.assertTrue(state["major_review_required"])
        self.assertEqual(state["minor_review_route"], "codex_internal_review")
        self.assertEqual(state["major_review_route"], "manual_chatgpt_review")
        self.assertEqual(
            state["notify_user_only_on"],
            ["blocked", "major_stage_ready", "live_config_approval_required"],
        )
        self.assertFalse(state["computer_use_allowed"])
        self.assertFalse(state["real_config_changes_allowed"])

    def test_runner_doc_defines_ordered_internal_review_workflow(self) -> None:
        text = read_text(RUNNER_DIR / "stage3_runner.md")
        lowered = normalized_lower(text)
        for status in (
            "planned",
            "ready",
            "in_progress",
            "build_completed",
            "internal_review_in_progress",
            "completed_internal_review",
            "blocked",
            "skipped",
        ):
            self.assertIn(f"- `{status}`", text)

        for reviewer in ("Security Reviewer", "Domain Reviewer", "Integration Reviewer", "Test Reviewer"):
            self.assertIn(reviewer, text)

        for required in (
            "read the task file",
            "run tests",
            "generate `reports/internal_reviews/stage3/<minor>.md`",
            "generate `reports/internal_reviews/stage3/<minor>.json`",
            "commit and push",
            "wait for the next automation wake",
        ):
            self.assertIn(required, lowered)

    def test_automation_prompt_has_thread_runner_and_review_guards(self) -> None:
        text = read_text(PROMPT_PATH)
        lowered = normalized_lower(text)

        for required in (
            "thread automation",
            "current worktree",
            "every 10 minutes",
            "ops/runners/stage3_runner_state.json",
            "status=ready",
            "status=in_progress",
            "at most one minor stage per wake",
            "commit and push",
            "hermes/feishu notification",
            "stage 3e",
            "manual chatgpt major review",
            "reviewer_mode=\"simulated_separate_pass\"",
        ):
            self.assertIn(required, lowered)

        self.assertIn("must not treat tests passing as internal review passing", lowered)
        self.assertRegex(lowered, r"subagents|separate reviewer passes")
        self.assertIn("each reviewer only reviews", lowered)
        self.assertIn("do not run computer use", lowered)
        self.assertIn("do not modify real configuration", lowered)
        self.assertIn("do not connect broker interfaces", lowered)
        self.assertIn("do not place orders", lowered)

    def test_stage3_yaml_and_tasks_define_minor_stage_progression(self) -> None:
        stage_text = read_text(STAGE3_PATH)
        stage3c = stage_block(stage_text, "stage3c_backtest_validation")
        stage3d = stage_block(stage_text, "stage3d_strategy_evidence_report")
        self.assertIn("status: completed_internal_review", stage3c)
        self.assertIn("depends_on: Stage 3B completed_internal_review", stage3c)
        self.assertIn("status: completed_internal_review", stage3d)
        self.assertIn("depends_on: Stage 3C completed_internal_review", stage3d)
        self.assertIn("status: major_review_package_ready", stage_text)
        self.assertIn("depends_on: Stage 3D completed_internal_review", stage_text)
        self.assertIn("reports/major_reviews/stage3/latest.md", stage_text)
        self.assertIn("reports/major_reviews/stage3/latest.json", stage_text)

        task_3c = read_text(TASK_3C)
        task_3d = read_text(TASK_3D)
        task_3e = read_text(TASK_3E)
        task_3e_lowered = normalized_lower(task_3e)
        self.assertIn("status: completed_internal_review", task_3c)
        self.assertIn("depends_on: Stage 3B completed_internal_review", task_3c)
        self.assertIn("status: completed_internal_review", task_3d)
        self.assertIn("depends_on: Stage 3C completed_internal_review", task_3d)
        self.assertIn("status: completed_internal_review", task_3e)
        self.assertIn("depends_on: Stage 3D completed_internal_review", task_3e)

        for small_task in (task_3c, task_3d):
            self.assertIn("Do not request ChatGPT review for this small stage.", small_task)
            self.assertIn("Small-stage review: Codex self-review.", small_task)

        self.assertIn("reports/major_reviews/stage3/latest.md", task_3e)
        self.assertIn("reports/major_reviews/stage3/latest.json", task_3e)
        self.assertIn("manual ChatGPT review", task_3e)
        self.assertIn("after the stage 3e package is complete", task_3e_lowered)


if __name__ == "__main__":
    unittest.main()

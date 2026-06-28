import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3D completed_internal_review"
STAGE_BRANCH = "stage/stage3-data-backtest"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read(path))


class BranchGovernanceTest(unittest.TestCase):
    def test_branching_policy_declares_stable_and_work_branches(self) -> None:
        text = read("docs/branching_policy.md")
        required = [
            "main is the stable branch",
            "only contain major-stage states that have passed manual ChatGPT review",
            "stage/* branches are major-stage construction branches",
            "task/* branches are optional small-stage construction branches",
            "Small-stage review is Codex self-review",
            "Major-stage review is manual ChatGPT review",
            "Codex does not request ChatGPT review for small stages",
            "Codex does not use Computer Use to send review requests to ChatGPT",
            "ChatGPT Computer Use automatic review route is deprecated",
        ]
        for fragment in required:
            self.assertIn(fragment, text)

    def test_stage3_manifest_and_tasks_exist_with_review_modes(self) -> None:
        required_paths = [
            "ops/stages/stage3.yaml",
            "ops/tasks/stage3a_data_source.md",
            "ops/tasks/stage3b_data_quality.md",
            "ops/tasks/stage3c_backtest_validation.md",
            "ops/tasks/stage3d_strategy_evidence_report.md",
            "ops/tasks/stage3_major_review_package.md",
        ]
        for path in required_paths:
            self.assertTrue((ROOT / path).exists(), path)

        manifest = read("ops/stages/stage3.yaml")
        for fragment in (
            "stage: Stage 3 data and backtest evidence",
            f"construction_branch: {STAGE_BRANCH}",
            "stable_branch: main",
            "business_code_started: true",
            "small_stage_review: codex_self_review",
            "major_stage_review: manual_chatgpt_review",
            "chatgpt_computer_use_auto_review: deprecated",
            "stage3a_data_source",
            "stage3b_data_quality",
            "stage3c_backtest_validation",
            "stage3d_strategy_evidence_report",
            "stage3e_major_review_package",
        ):
            self.assertIn(fragment, manifest)

        shared_required = [
            "repo-only",
            "Small-stage review: Codex self-review",
            "Major-stage review: manual ChatGPT review",
            "Do not run Computer Use",
            "Do not modify real `~/.hermes`",
            "Do not modify real `~/.openclaw`",
            "Do not connect broker write interfaces",
            "Final trading is manually decided by the user",
        ]
        task_specific = {
            "ops/tasks/stage3a_data_source.md": [
                "Stage 3A",
                "read-only public ETF data",
                "real ETF data source integration plan",
            ],
            "ops/tasks/stage3b_data_quality.md": [
                "Stage 3B",
                "missing values",
                "ETF start dates",
                "adjusted prices",
                "abnormal prices",
            ],
            "ops/tasks/stage3c_backtest_validation.md": [
                "Stage 3C",
                "formal backtest validation",
                "replace sample-only reports",
            ],
            "ops/tasks/stage3d_strategy_evidence_report.md": [
                "Stage 3D",
                "GTAA",
                "Dual Momentum",
                "60/40",
                "Buy-and-Hold",
            ],
        }
        for path, fragments in task_specific.items():
            text = read(path)
            for fragment in shared_required + fragments:
                self.assertIn(fragment, text, path)

        major_review = read("ops/tasks/stage3_major_review_package.md")
        for fragment in (
            "Stage 3E",
            "repo-only",
            "Major-stage review: manual ChatGPT review",
            "Small-stage review: Codex self-review is complete before this package",
            "Feishu notification asks the user whether to request ChatGPT review",
            "Do not run Computer Use",
        ):
            self.assertIn(fragment, major_review)

    def test_review_folders_document_small_and_major_stage_rules(self) -> None:
        internal = read("reports/internal_reviews/README.md")
        major = read("reports/major_reviews/README.md")
        self.assertIn("Codex self-review", internal)
        self.assertIn("small stages", internal)
        self.assertIn("Do not request ChatGPT review for small stages", internal)
        self.assertIn("manual ChatGPT review", major)
        self.assertIn("major stages", major)
        self.assertIn("Do not use Computer Use to send review requests to ChatGPT", major)

    def test_latest_state_records_stage3d_strategy_evidence(self) -> None:
        loop_state = read_json("ops/state/loop_state.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review = read_json("reports/review_requests/latest.json")

        self.assertEqual(loop_state["current_stage"], STAGE)
        self.assertEqual(handoff["stage"], STAGE)
        self.assertEqual(review["stage"], STAGE)
        self.assertEqual(loop_state["status"], "stage3d_completed_internal_review")
        self.assertEqual(loop_state["stage2f1_task_status"], "completed_repo_only_branch_governance_stage3_plan")
        self.assertEqual(loop_state["stage3_stage_branch"], STAGE_BRANCH)
        self.assertTrue(loop_state["stage3_business_code_started"])
        self.assertEqual(loop_state["stage3a_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3b_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3c_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3d_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3_next_task"], "ops/tasks/stage3_major_review_package.md")
        self.assertEqual(loop_state["small_stage_review_route"], "codex_self_review")
        self.assertEqual(loop_state["major_stage_review_route"], "manual_chatgpt_review")
        self.assertTrue(loop_state["chatgpt_computer_use_auto_review_deprecated"])
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])


if __name__ == "__main__":
    unittest.main()

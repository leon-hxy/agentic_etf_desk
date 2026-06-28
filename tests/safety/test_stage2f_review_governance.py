import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3F major_gate_feishu_notification_sent"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read(path))


class Stage2FReviewGovernanceTest(unittest.TestCase):
    def test_governance_design_declares_new_review_model(self) -> None:
        text = read("docs/review_governance.md")
        self.assertIn("Small-stage Codex self-review", text)
        self.assertIn("Major-stage ChatGPT review", text)
        self.assertIn("ChatGPT Computer Use automatic review route is deprecated", text)
        self.assertIn("ChatGPT review is manual and user-initiated", text)
        self.assertIn("Final trading is manually decided by the user", text)
        self.assertIn("No automatic order placement", text)

    def test_task_and_templates_exist_with_required_modes(self) -> None:
        required = {
            "ops/tasks/stage2f_review_governance.md": [
                "status: completed",
                "stage: Stage 2F review governance refactor completed",
                "repo-only",
                "Do not run Computer Use",
            ],
            "ops/templates/internal_codex_self_review_template.md": [
                "review_mode: codex_self_review",
                "scope: small_stage",
                "reviewer: Codex",
                "No Computer Use",
            ],
            "ops/templates/major_chatgpt_review_template.md": [
                "review_mode: major_chatgpt_review",
                "scope: major_stage",
                "manual ChatGPT review",
                "public GitHub URL",
            ],
            "ops/templates/review_governance_task_template.md": [
                "review_level",
                "small_stage",
                "major_stage",
                "forbidden_actions",
            ],
        }
        for path, fragments in required.items():
            text = read(path)
            for fragment in fragments:
                self.assertIn(fragment, text, path)

    def test_codex_automation_draft_deprecates_computer_use_relay(self) -> None:
        governance = read("configs/codex_automation/review_governance_prompt.md")
        deprecated = read("configs/codex_automation/chatgpt_review_relay_prompt.md")
        for text in (governance, deprecated):
            self.assertIn("ChatGPT Computer Use automatic review route is deprecated", text)
            self.assertIn("Do not run Computer Use", text)
            self.assertIn("Do not open ChatGPT automatically", text)
            self.assertIn("Do not send ChatGPT prompts automatically", text)
            self.assertIn("Small-stage Codex self-review", text)
            self.assertIn("Major-stage ChatGPT review", text)

    def test_latest_state_records_stage3_small_stage_governance(self) -> None:
        loop_state = read_json("ops/state/loop_state.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review = read_json("reports/review_requests/latest.json")
        relay_status = read_json("reports/review_requests/relay_status.json")

        self.assertEqual(loop_state["current_stage"], STAGE)
        self.assertEqual(handoff["stage"], STAGE)
        self.assertEqual(review["stage"], STAGE)
        self.assertEqual(relay_status["stage"], STAGE)
        self.assertEqual(loop_state["review_governance_mode"], "small_stage_codex_self_review_major_stage_chatgpt_manual")
        self.assertEqual(loop_state["stage2f_task_status"], "completed_repo_only_review_governance_refactor")
        self.assertEqual(
            loop_state["stage2f1_task_status"],
            "completed_repo_only_branch_governance_stage3_plan",
        )
        self.assertTrue(relay_status["chatgpt_computer_use_auto_review_deprecated"])
        self.assertFalse(relay_status["computer_use_executed"])
        self.assertFalse(relay_status["sent_to_chatgpt"])
        if relay_status["stage"] in {
            "Stage 3E major_review_package_ready",
            "Stage 3F major_gate_feishu_notification_sent",
        }:
            self.assertEqual(relay_status["review_route"], "manual_chatgpt_review_for_major_stage")
            self.assertTrue(relay_status["manual_chatgpt_review_ready"])
        else:
            self.assertEqual(relay_status["review_route"], "codex_self_review_for_small_stage")
        self.assertEqual(relay_status["major_review_route"], "manual_chatgpt_review_for_major_stage")
        self.assertEqual(loop_state["stage3b_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3c_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3d_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3e_task_status"], "completed_internal_review")

    def test_public_review_prompt_is_manual_major_review_only(self) -> None:
        prompt = read("reports/review_requests/chatgpt_review_prompt.md")
        self.assertIn("major-stage review", prompt)
        self.assertIn("Public GitHub repo", prompt)
        self.assertIn("reports/review_requests/latest.md", prompt)
        self.assertIn("reports/codex_handoff/latest.md", prompt)
        forbidden = [
            "Computer Use",
            "local_private",
            "/" + "Users" + "/",
            "/" + "Volumes" + "/",
            "token=",
            "secret=",
            "auth=",
        ]
        for fragment in forbidden:
            self.assertNotIn(fragment, prompt)


if __name__ == "__main__":
    unittest.main()

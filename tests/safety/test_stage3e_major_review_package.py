import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAJOR_JSON = ROOT / "reports" / "major_reviews" / "stage3" / "latest.json"
MAJOR_MD = ROOT / "reports" / "major_reviews" / "stage3" / "latest.md"
INTERNAL_REVIEW_JSON = ROOT / "reports" / "internal_reviews" / "stage3" / "stage3e_major_review_package.json"
REQUIRED_MINOR_STAGES = ["Stage 3A", "Stage 3B", "Stage 3C", "Stage 3D"]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Stage3EMajorReviewPackageTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_stage3e_major_review_script_generates_public_package(self) -> None:
        payload = read_json(MAJOR_JSON)

        self.assertEqual(payload["stage"], "Stage 3 major review package")
        self.assertEqual(payload["status"], "major_review_package_ready")
        self.assertEqual(payload["review_level"], "major_stage")
        self.assertEqual(payload["review_route"], "manual_chatgpt_review")
        self.assertEqual(payload["report_json"], "reports/major_reviews/stage3/latest.json")
        self.assertEqual(payload["report_md"], "reports/major_reviews/stage3/latest.md")
        self.assertEqual(payload["public_repo_url"], "https://github.com/leon-hxy/agentic_etf_desk")
        self.assertEqual(payload["branch"], "stage/stage3-data-backtest")
        self.assertTrue(payload["manual_chatgpt_review_ready"])
        self.assertFalse(payload["chatgpt_review_requested_by_codex"])
        self.assertFalse(payload["sent_to_chatgpt"])
        self.assertFalse(payload["computer_use_executed"])
        self.assertTrue(payload["feishu_message_sent"])
        self.assertEqual(payload["manual_execution_note"], "Final trading is manually decided by the user.")
        self.assertEqual(payload["major_gate_finalization"]["status"], "completed")
        self.assertFalse(payload["major_gate_finalization"]["request_chatgpt_review_for_finalization_fixes"])

        self.assertEqual(payload["minor_stages"], REQUIRED_MINOR_STAGES)
        for stage in REQUIRED_MINOR_STAGES:
            summary = payload["minor_stage_summaries"][stage]
            self.assertEqual(summary["status"], "completed_internal_review")
            self.assertTrue(summary["internal_review"])

        for check in (
            "stage3a_internal_review_complete",
            "stage3b_internal_review_complete",
            "stage3c_internal_review_complete",
            "stage3d_internal_review_complete",
            "major_review_package_public_safe",
            "manual_chatgpt_review_ready",
            "manual_trading_notice_present",
        ):
            self.assertEqual(payload["readiness_checks"][check], "passed")

        data_boundary = payload["data_boundary"]
        self.assertTrue(data_boundary["sample_data_only"])
        self.assertFalse(data_boundary["real_data_used"])
        self.assertTrue(data_boundary["not_investment_basis"])

        prompt = payload["manual_chatgpt_review_prompt"]
        self.assertIn("https://github.com/leon-hxy/agentic_etf_desk", prompt)
        self.assertIn(payload["review_target_commit"], prompt)
        self.assertIn("reports/major_reviews/stage3/latest.md", prompt)
        self.assertNotIn("/" + "Volumes" + "/", prompt)
        self.assertNotIn("/" + "Users" + "/", prompt)
        self.assertNotIn("local_private", prompt)

        for flag in (
            "auto_trading_surface",
            "broker_surface",
            "broker_write_surface",
            "chatgpt_review_requested",
            "computer_use_executed",
            "real_config_modified",
            "secret_values_written",
            "secrets_touched",
        ):
            self.assertFalse(payload["safety_flags"][flag], flag)

        text = MAJOR_MD.read_text(encoding="utf-8")
        self.assertIn("Stage 3 Major Review Package", text)
        self.assertIn("manual ChatGPT review", text)
        self.assertIn("Stage 3A", text)
        self.assertIn("Stage 3B", text)
        self.assertIn("Stage 3C", text)
        self.assertIn("Stage 3D", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_stage3e_updates_governance_state_after_internal_review(self) -> None:
        task = read("ops/tasks/stage3_major_review_package.md")
        runner = read_json(ROOT / "ops" / "runners" / "stage3_runner_state.json")
        loop_state = read_json(ROOT / "ops" / "state" / "loop_state.json")
        handoff = read_json(ROOT / "reports" / "codex_handoff" / "latest.json")
        review_request = read_json(ROOT / "reports" / "review_requests" / "latest.json")
        review = read_json(INTERNAL_REVIEW_JSON)

        self.assertIn("status: completed_internal_review", task)
        self.assertIn("reports/major_reviews/stage3/latest.md", task)
        self.assertEqual(runner["status"], "major_stage_ready")
        self.assertEqual(runner["completed_minor_stages"], ["Stage 3A", "Stage 3B", "Stage 3C", "Stage 3D"])
        self.assertEqual(runner["major_package_status"], "major_package_generated")
        self.assertEqual(runner["finalization_status"], "completed")
        self.assertEqual(runner["finalization_fixes"], ["Stage 3F", "Stage 3F.1"])
        self.assertEqual(runner["remaining_minor_stages"], [])
        self.assertTrue(runner["major_review_required"])
        self.assertFalse(runner["computer_use_executed"])
        self.assertTrue(runner["feishu_notification_sent"])
        self.assertFalse(runner["requires_user_attention"])

        self.assertEqual(loop_state["current_stage"], "Stage 3.1 WP1 real data ingestion and cache completed_internal_review")
        self.assertEqual(loop_state["status"], "stage3_1_wp1_completed_internal_review")
        self.assertEqual(loop_state["stage3e_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3f_task_status"], "finalization_fix_internal_reviewed")
        self.assertFalse(loop_state["major_review_required"])
        self.assertFalse(loop_state["manual_chatgpt_review_ready"])
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertFalse(loop_state["current_stage_feishu_message_sent"])

        self.assertEqual(handoff["stage"], "Stage 3.1 WP1 real data ingestion and cache completed_internal_review")
        self.assertEqual(handoff["stage3e_task_status"], "completed_internal_review")
        self.assertFalse(handoff["manual_chatgpt_review_ready"])
        self.assertFalse(handoff["chatgpt_review_requested"])
        self.assertFalse(handoff["computer_use_executed"])
        self.assertFalse(handoff["feishu_message_sent"])

        self.assertEqual(review_request["stage"], "Stage 3.1 WP1 real data ingestion and cache completed_internal_review")
        self.assertEqual(review_request["review_target"], "Stage 3.1 WP1 real data ingestion and cache")
        self.assertFalse(review_request["request_chatgpt_review_for_finalization_fixes"])
        self.assertEqual(review_request["review_level"], "work_package_internal_review")
        self.assertFalse(review_request["manual_chatgpt_review_ready"])
        self.assertFalse(review_request["chatgpt_review_requested"])
        self.assertFalse(review_request["sent_to_chatgpt"])

        self.assertEqual(review["minor_stage"], "Stage 3E")
        self.assertEqual(review["status"], "completed_internal_review")
        self.assertEqual(review["task_file"], "ops/tasks/stage3_major_review_package.md")
        self.assertEqual(review["major_review_package"], "reports/major_reviews/stage3/latest.json")
        for section in ("security_reviewer", "domain_reviewer", "integration_reviewer", "test_reviewer"):
            self.assertEqual(review[section]["result"], "pass")
            self.assertIn(review[section]["reviewer_mode"], {"subagent_read_only", "simulated_separate_pass"})
        self.assertFalse(review["requires_user_attention"])
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["computer_use_executed"])
        self.assertFalse(review["feishu_message_sent"])


if __name__ == "__main__":
    unittest.main()

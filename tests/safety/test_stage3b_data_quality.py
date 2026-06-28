import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3B data quality checks completed"
GOVERNANCE_STAGE = "Stage 3D completed_internal_review"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read(path))


class Stage3BDataQualityTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_data_quality_script_generates_auditable_report(self) -> None:
        result = self.run_cmd(["scripts/data/check_data_quality.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        payload = json.loads(result.stdout)
        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["source_plan"]["selected_primary_source"], "stooq_daily_csv")
        self.assertEqual(payload["input_file"], "data/raw/prices_sample.csv")
        self.assertEqual(payload["source_plan_file"], "configs/data_sources/stage3_data_sources.json")
        self.assertFalse(payload["unknown_symbols"])
        self.assertFalse(payload["non_positive_prices"])
        self.assertFalse(payload["abnormal_price_points"])
        self.assertTrue(payload["quality_checks"]["missing_values"]["passed"])
        self.assertTrue(payload["quality_checks"]["start_dates"]["passed"])
        self.assertTrue(payload["quality_checks"]["adjusted_prices"]["passed"])
        self.assertTrue(payload["quality_checks"]["abnormal_prices"]["passed"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["sent_to_chatgpt"])
        self.assertFalse(payload["safety_flags"]["broker_surface"])

        report_json = ROOT / "reports" / "data_quality" / "stage3b_data_quality_report.json"
        report_md = ROOT / "reports" / "data_quality" / "stage3b_data_quality_report.md"
        self.assertTrue(report_json.exists())
        self.assertTrue(report_md.exists())
        self.assertEqual(read_json("reports/data_quality/stage3b_data_quality_report.json"), payload)
        self.assertIn("Final trading is manually decided by the user", report_md.read_text())

    def test_stage3b_internal_review_records_codex_self_review(self) -> None:
        review = read_json("reports/internal_reviews/stage3b_data_quality_codex_self_review.json")
        self.assertEqual(review["stage"], STAGE)
        self.assertEqual(review["review_mode"], "codex_self_review")
        self.assertEqual(review["status"], "passed")
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["sent_to_chatgpt"])
        self.assertFalse(review["feishu_message_sent"])
        self.assertFalse(review["computer_use_executed"])
        self.assertIn("scripts/data/check_data_quality.py", review["reviewed_files"])

        text = read("reports/internal_reviews/stage3b_data_quality_codex_self_review.md")
        self.assertIn("Codex self-review", text)
        self.assertIn("No ChatGPT review requested", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_stage3b_updates_task_manifest_handoff_and_loop_state(self) -> None:
        task = read("ops/tasks/stage3b_data_quality.md")
        self.assertIn("status: completed", task)
        self.assertIn("stage: Stage 3B completed_internal_review", task)
        self.assertIn("reports/data_quality/stage3b_data_quality_report.md", task)

        manifest = read("ops/stages/stage3.yaml")
        self.assertIn("id: stage3a_data_source", manifest)
        self.assertIn("id: stage3b_data_quality", manifest)
        self.assertIn("reports/data_quality/stage3b_data_quality_report.md", manifest)
        self.assertIn("id: stage3c_backtest_validation", manifest)

        handoff = read_json("reports/codex_handoff/latest.json")
        loop_state = read_json("ops/state/loop_state.json")
        review = read_json("reports/review_requests/latest.json")
        self.assertEqual(handoff["stage"], GOVERNANCE_STAGE)
        self.assertEqual(handoff["loop_state_stage"], GOVERNANCE_STAGE)
        self.assertEqual(loop_state["current_stage"], GOVERNANCE_STAGE)
        self.assertEqual(review["stage"], GOVERNANCE_STAGE)
        self.assertEqual(loop_state["status"], "stage3d_completed_internal_review")
        self.assertEqual(loop_state["stage3a_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3b_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3_next_task"], "ops/tasks/stage3_major_review_package.md")
        self.assertEqual(loop_state["next_minor_task"], "ops/tasks/stage3_major_review_package.md")
        self.assertEqual(loop_state["next_minor_task_status"], "planned")
        self.assertEqual(
            loop_state["last_internal_review"],
            "reports/internal_reviews/stage3/stage3d_strategy_evidence_report.json",
        )
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertFalse(loop_state["current_stage_feishu_message_sent"])
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])


if __name__ == "__main__":
    unittest.main()

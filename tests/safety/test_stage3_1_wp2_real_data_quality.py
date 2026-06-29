import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.1 WP2 real data quality and monthly panel completed_internal_review"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage31Wp2RealDataQualityTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp2_builds_reviewed_monthly_panel_from_real_wp1_data(self) -> None:
        result = self.run_cmd(["scripts/data/build_stage3_1_monthly_panel.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["stage"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["input_file"], "data/raw/prices_yahoo_chart.csv")
        self.assertEqual(payload["input_metadata_file"], "data/raw/prices_yahoo_chart_metadata.json")
        self.assertEqual(payload["monthly_panel_file"], "data/processed/stage3_1_monthly_panel.csv")
        self.assertEqual(payload["source"], "yahoo_chart_public")
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertEqual(payload["monthly_row_count"], 900)
        self.assertEqual(payload["month_count"], 90)
        self.assertFalse(payload["unknown_symbols"])
        self.assertTrue(payload["quality_checks"]["universe_allowlist"]["passed"])
        self.assertTrue(payload["quality_checks"]["daily_missing_data"]["passed"])
        self.assertTrue(payload["quality_checks"]["monthly_missing_data"]["passed"])
        self.assertTrue(payload["quality_checks"]["stale_prices"]["passed"])
        self.assertTrue(payload["quality_checks"]["adjusted_price_coverage"]["passed"])
        self.assertTrue(payload["quality_checks"]["benchmark_availability"]["passed"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["sent_to_chatgpt"])
        self.assertFalse(payload["safety_flags"]["broker_surface"])
        self.assertFalse(payload["safety_flags"]["order_placement_surface"])

        report = read_json("reports/data_quality/stage3_1_wp2_data_quality_report.json")
        metadata = read_json("data/processed/stage3_1_monthly_panel_metadata.json")
        self.assertEqual(report, payload)
        self.assertEqual(metadata["monthly_panel_file"], payload["monthly_panel_file"])
        self.assertEqual(metadata["benchmark_symbol"], "VTI")

        with (ROOT / "data" / "processed" / "stage3_1_monthly_panel.csv").open(
            newline="",
            encoding="utf-8",
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 900)
        self.assertEqual(rows[0]["month"], "2019-01")
        self.assertEqual(rows[0]["symbol"], "BIL")
        self.assertEqual(rows[-1]["month"], "2026-06")
        self.assertEqual(rows[-1]["symbol"], "VWO")
        self.assertTrue(all(row["benchmark_symbol"] == "VTI" for row in rows))

    def test_wp2_internal_review_and_latest_artifacts_are_internal_only(self) -> None:
        review = read_json("reports/internal_reviews/stage3_1/wp2_real_data_quality_and_monthly_panel.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review_request = read_json("reports/review_requests/latest.json")
        runner = read_json("ops/runners/stage3_1_runner_state.json")
        loop_state = read_json("ops/state/loop_state.json")

        self.assertEqual(review["work_package_id"], "wp2_real_data_quality_and_monthly_panel")
        self.assertEqual(review["decision"], "passed")
        self.assertEqual(review["reviewers"]["security"]["result"], "passed")
        self.assertEqual(review["reviewers"]["domain"]["result"], "passed")
        self.assertEqual(review["reviewers"]["integration"]["result"], "passed")
        self.assertEqual(review["reviewers"]["test"]["result"], "passed")
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["user_notification_sent"])
        self.assertFalse(review["computer_use_executed"])

        self.assertEqual(handoff["stage"], "Stage 3.1 major review package ready")
        self.assertEqual(handoff["stage3_1_wp2_status"], "completed_internal_review")
        self.assertEqual(handoff["current_work_package"], "Stage 3.1 major review package ready")
        self.assertIsNone(handoff["next_work_package"])
        self.assertEqual(review_request["review_target"], "Stage 3.1 major review package")
        self.assertFalse(handoff["chatgpt_review_requested"])
        self.assertFalse(review_request["chatgpt_review_requested"])
        self.assertFalse(handoff["sent_to_chatgpt"])
        self.assertFalse(review_request["sent_to_chatgpt"])
        self.assertEqual(runner["current_work_package"], "Stage 3.1 major review package ready")
        self.assertEqual(runner["status"], "wp3_completed_major_review_package_ready")
        self.assertEqual(loop_state["current_stage"], "Stage 3.1 major review package ready")
        self.assertEqual(loop_state["last_internal_review"], "reports/internal_reviews/stage3_1/wp3_formal_backtest_and_evidence_package.json")
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertFalse(loop_state["current_stage_feishu_message_sent"])
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])


if __name__ == "__main__":
    unittest.main()

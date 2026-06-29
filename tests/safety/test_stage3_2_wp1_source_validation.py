import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.2 WP1 research robustness source validation"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage32Wp1SourceValidationTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp1_generates_source_validation_report_from_committed_cache(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp1_source_validation.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["major_stage"], "Stage 3.2")
        self.assertEqual(payload["work_package"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["source"], "yahoo_chart_public")
        self.assertEqual(payload["primary_raw_file"], "data/raw/prices_yahoo_chart.csv")
        self.assertEqual(payload["cache_manifest_file"], "data/cache/yahoo_chart_public/cache_manifest.json")
        self.assertEqual(payload["monthly_panel_file"], "data/processed/stage3_1_monthly_panel.csv")
        self.assertEqual(payload["symbol_count"], 10)
        self.assertEqual(payload["raw_row_count"], 18810)
        self.assertEqual(payload["monthly_row_count"], 900)
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertFalse(payload["unknown_symbols"])
        self.assertEqual(payload["discrepancy_tolerance"], 0.0001)
        self.assertEqual(payload["price_discrepancies"], [])
        self.assertEqual(payload["monthly_panel_discrepancies"], [])
        self.assertTrue(payload["validation_checks"]["cache_manifest_integrity"]["passed"])
        self.assertTrue(payload["validation_checks"]["cache_to_raw_price_match"]["passed"])
        self.assertTrue(payload["validation_checks"]["raw_to_monthly_panel_match"]["passed"])
        self.assertTrue(payload["validation_checks"]["universe_allowlist"]["passed"])
        self.assertTrue(payload["validation_checks"]["benchmark_preserved"]["passed"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["sent_to_chatgpt"])
        self.assertFalse(payload["safety_flags"]["broker_write_surface"])
        self.assertFalse(payload["safety_flags"]["order_placement_surface"])
        self.assertIn("Final trading is manually decided by the user.", payload["final_trading_notice"])

        report = read_json("reports/research_robustness/stage3_2_wp1_source_validation_report.json")
        self.assertEqual(report, payload)

    def test_wp1_internal_review_and_runner_state_advance_without_user_notification(self) -> None:
        review = read_json("reports/internal_reviews/program/stage3_2_wp1_source_validation.json")
        state = read_json("ops/program_runner/program_runner_state.json")

        self.assertEqual(review["major_stage"], "Stage 3.2")
        self.assertEqual(review["work_package"], STAGE)
        self.assertEqual(review["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(review["pass_fail"], "passed")
        self.assertEqual(review["security_reviewer"]["result"], "passed")
        self.assertEqual(review["domain_quant_reviewer"]["result"], "passed")
        self.assertEqual(review["integration_reviewer"]["result"], "passed")
        self.assertEqual(review["test_reproducibility_reviewer"]["result"], "passed")
        self.assertEqual(review["public_repo_hygiene_reviewer"]["result"], "passed")
        self.assertTrue(review["domain_quant_reviewer"]["etf_only_maintained"])
        self.assertTrue(review["domain_quant_reviewer"]["benchmark_comparison_present"])
        self.assertTrue(review["domain_quant_reviewer"]["research_limitations_clear"])
        self.assertFalse(review["domain_quant_reviewer"]["trade_tickets_actionable_without_risk_agent_review"])
        self.assertFalse(review["security_reviewer"]["secrets_touched"])
        self.assertFalse(review["integration_reviewer"]["real_runtime_modified"])
        self.assertFalse(review["requires_user_attention"])
        self.assertEqual(review["promote_to_next_work_package"], "Stage 3.2 WP2 price discrepancy and cash assumption scenarios")

        self.assertEqual(state["current_major_stage"], "Stage 3.2")
        self.assertEqual(state["current_work_package"], "Stage 3.2 WP2 price discrepancy and cash assumption scenarios")
        self.assertEqual(state["status"], "next_work_package_ready")
        self.assertEqual(state["last_completed_work_package"], STAGE)
        self.assertFalse(state["stage3_2"]["user_notification_sent"])
        self.assertEqual(
            state["stage3_2"]["completed_work_packages"],
            ["stage3_2_wp1_source_validation"],
        )


if __name__ == "__main__":
    unittest.main()

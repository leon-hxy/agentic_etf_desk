import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.2 WP6 in-sample / out-of-sample split"
NEXT_WORK_PACKAGE = "Stage 3.2 WP7 strategy conclusion grading"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage32Wp6InSampleOutOfSampleTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp6_generates_in_sample_out_of_sample_report(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp6_in_sample_out_of_sample.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["major_stage"], "Stage 3.2")
        self.assertEqual(payload["work_package"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["monthly_panel_file"], "data/processed/stage3_1_monthly_panel.csv")
        self.assertEqual(
            payload["source_backtest_report"],
            "reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json",
        )
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertEqual(payload["symbol_count"], 10)
        self.assertEqual(payload["unknown_symbols"], [])
        self.assertEqual(payload["split_policy"]["in_sample_fraction"], 0.6)
        self.assertEqual(
            sorted(payload["split_scenarios"]),
            ["dual_momentum", "gtaa_10m_sma", "static_6040"],
        )
        self.assertTrue(payload["validation_checks"]["split_scenarios"]["passed"])
        self.assertTrue(payload["validation_checks"]["benchmark_comparison_preserved"]["passed"])
        self.assertTrue(payload["validation_checks"]["full_window_reconciled"]["passed"])
        self.assertTrue(payload["validation_checks"]["universe_allowlist"]["passed"])
        self.assertTrue(payload["validation_checks"]["research_only_boundary"]["passed"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["broker_write_surface"])
        self.assertFalse(payload["safety_flags"]["order_placement_surface"])
        self.assertFalse(payload["safety_flags"]["real_config_modified"])

        for strategy_id, scenarios in payload["split_scenarios"].items():
            self.assertEqual(
                [scenario["scenario_id"] for scenario in scenarios],
                ["full_window", "in_sample", "out_of_sample"],
                strategy_id,
            )
            self.assertEqual({scenario["benchmark_symbol"] for scenario in scenarios}, {"VTI"})
            self.assertGreater(scenarios[1]["months"], scenarios[2]["months"])
            self.assertEqual(scenarios[0]["window_start_month"], payload["full_window"]["start_month"])
            self.assertEqual(scenarios[0]["window_end_month"], payload["full_window"]["end_month"])
            self.assertEqual(scenarios[1]["window_end_month"], payload["split_policy"]["in_sample_end_month"])
            self.assertEqual(scenarios[2]["window_start_month"], payload["split_policy"]["out_of_sample_start_month"])
            self.assertLess(scenarios[1]["window_end_month"], scenarios[2]["window_start_month"])
            for scenario in scenarios:
                self.assertIn("metrics", scenario)
                self.assertIn("benchmark_metrics", scenario)
                self.assertIn("excess_cagr_vs_benchmark", scenario)
                self.assertIn("max_drawdown_difference_vs_benchmark", scenario)
                self.assertGreaterEqual(scenario["months"], 24)

        self.assertIn("Final trading is manually decided by the user.", payload["final_trading_notice"])

        report = read_json("reports/research_robustness/stage3_2_wp6_in_sample_out_of_sample_report.json")
        self.assertEqual(report, payload)
        report_md = (ROOT / "reports/research_robustness/stage3_2_wp6_in_sample_out_of_sample_report.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Final trading is manually decided by the user.", report_md)

    def test_wp6_internal_review_and_runner_state_advance_without_user_notification(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp6_in_sample_out_of_sample.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        review = read_json("reports/internal_reviews/program/stage3_2_wp6_in_sample_out_of_sample.json")
        state = read_json("ops/program_runner/program_runner_state.json")

        self.assertEqual(review["major_stage"], "Stage 3.2")
        self.assertEqual(review["work_package"], STAGE)
        self.assertEqual(review["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(review["pass_fail"], "passed")
        self.assertEqual(review["security_reviewer"]["result"], "passed")
        self.assertEqual(review["domain_quant_reviewer"]["result"], "passed")
        self.assertEqual(review["risk_agent_review"]["result"], "passed")
        self.assertTrue(review["risk_agent_review"]["no_actionable_trade_tickets_generated"])
        self.assertEqual(review["integration_reviewer"]["result"], "passed")
        self.assertEqual(review["test_reproducibility_reviewer"]["result"], "passed")
        self.assertEqual(review["public_repo_hygiene_reviewer"]["result"], "passed")
        self.assertTrue(review["domain_quant_reviewer"]["etf_only_maintained"])
        self.assertTrue(review["domain_quant_reviewer"]["benchmark_comparison_present"])
        self.assertTrue(review["domain_quant_reviewer"]["split_scenarios_reviewed"])
        self.assertTrue(review["domain_quant_reviewer"]["full_window_reconciled"])
        self.assertFalse(review["security_reviewer"]["secrets_touched"])
        self.assertFalse(review["integration_reviewer"]["real_runtime_modified"])
        self.assertFalse(review["requires_user_attention"])
        self.assertEqual(review["promote_to_next_work_package"], NEXT_WORK_PACKAGE)

        self.assertEqual(state["current_major_stage"], "Stage 5")
        self.assertEqual(state["current_work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(state["status"], "next_work_package_ready")
        self.assertEqual(state["last_completed_work_package"], "Stage 5 WP4 drift checks")
        self.assertEqual(
            state["last_internal_review"],
            "reports/internal_reviews/program/stage5_wp4_drift_checks.json",
        )
        self.assertEqual(
            state["last_report"],
            "reports/program_runner/stage5_wp4_drift_checks_report.json",
        )
        self.assertIn("stage3_2_wp6_in_sample_out_of_sample", state["stage3_2"]["completed_work_packages"])
        self.assertEqual(state["stage4"]["current_work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")
        self.assertFalse(state["stage3_2"]["user_notification_sent"])
        self.assertFalse(state["stage3_2"]["chatgpt_review_requested"])


if __name__ == "__main__":
    unittest.main()

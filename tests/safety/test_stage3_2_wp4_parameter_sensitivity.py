import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.2 WP4 parameter sensitivity scenarios"
NEXT_WORK_PACKAGE = "Stage 3.2 WP5 start-window robustness tests"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage32Wp4ParameterSensitivityTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp4_generates_parameter_sensitivity_report(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp4_parameter_sensitivity.py"])
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
        self.assertEqual(
            sorted(payload["parameter_sensitivity_scenarios"]),
            ["dual_momentum", "gtaa_10m_sma", "static_6040"],
        )
        self.assertTrue(payload["validation_checks"]["parameter_scenarios"]["passed"])
        self.assertTrue(payload["validation_checks"]["benchmark_comparison_preserved"]["passed"])
        self.assertTrue(payload["validation_checks"]["base_case_reconciled"]["passed"])
        self.assertTrue(payload["validation_checks"]["universe_allowlist"]["passed"])
        self.assertTrue(payload["validation_checks"]["research_only_boundary"]["passed"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["broker_write_surface"])
        self.assertFalse(payload["safety_flags"]["order_placement_surface"])
        self.assertFalse(payload["safety_flags"]["real_config_modified"])

        for strategy_id, scenarios in payload["parameter_sensitivity_scenarios"].items():
            self.assertGreaterEqual(len(scenarios), 3)
            scenario_ids = {scenario["scenario_id"] for scenario in scenarios}
            self.assertIn("base", scenario_ids)
            cagr_values = {scenario["metrics"]["cagr"] for scenario in scenarios}
            self.assertGreater(len(cagr_values), 1, strategy_id)
            for scenario in scenarios:
                self.assertEqual(scenario["benchmark_symbol"], "VTI")
                self.assertIn("parameter_overrides", scenario)
                self.assertIn("metrics", scenario)
                self.assertIn("benchmark_metrics", scenario)
                self.assertIn("excess_cagr_vs_benchmark", scenario)
                self.assertIn("max_drawdown_difference_vs_benchmark", scenario)
                self.assertGreaterEqual(scenario["months"], 1)

        self.assertIn("Final trading is manually decided by the user.", payload["final_trading_notice"])

        report = read_json("reports/research_robustness/stage3_2_wp4_parameter_sensitivity_report.json")
        self.assertEqual(report, payload)
        report_md = (ROOT / "reports/research_robustness/stage3_2_wp4_parameter_sensitivity_report.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Final trading is manually decided by the user.", report_md)

    def test_wp4_internal_review_and_runner_state_advance_without_user_notification(self) -> None:
        review = read_json("reports/internal_reviews/program/stage3_2_wp4_parameter_sensitivity.json")
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
        self.assertTrue(review["domain_quant_reviewer"]["parameter_scenarios_reviewed"])
        self.assertFalse(review["security_reviewer"]["secrets_touched"])
        self.assertFalse(review["integration_reviewer"]["real_runtime_modified"])
        self.assertFalse(review["requires_user_attention"])
        self.assertEqual(review["promote_to_next_work_package"], NEXT_WORK_PACKAGE)

        self.assertEqual(state["current_major_stage"], "Stage 4")
        self.assertEqual(state["current_work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")
        self.assertEqual(state["status"], "next_work_package_ready")
        self.assertEqual(state["last_completed_work_package"], "Stage 4 WP6 backtest command output")
        self.assertEqual(
            state["last_internal_review"],
            "reports/internal_reviews/program/stage4_wp6_backtest_command_output.json",
        )
        self.assertEqual(
            state["last_report"],
            "reports/program_runner/stage4_wp6_backtest_command_output_report.json",
        )
        self.assertIn("stage3_2_wp4_parameter_sensitivity", state["stage3_2"]["completed_work_packages"])
        self.assertEqual(state["stage4"]["current_work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")
        self.assertFalse(state["stage3_2"]["user_notification_sent"])
        self.assertFalse(state["stage3_2"]["chatgpt_review_requested"])


if __name__ == "__main__":
    unittest.main()

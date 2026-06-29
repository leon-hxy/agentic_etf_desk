import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.2 WP7 strategy conclusion grading"
NEXT_MAJOR_STAGE = "Stage 4"
NEXT_WORK_PACKAGE = "Stage 4 WP1 Feishu command routing for ETF research"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage32Wp7StrategyConclusionGradingTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp7_generates_strategy_conclusion_grading_report(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp7_strategy_conclusion_grading.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["major_stage"], "Stage 3.2")
        self.assertEqual(payload["work_package"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertEqual(
            sorted(payload["strategy_grades"]),
            ["dual_momentum", "gtaa_10m_sma", "static_6040"],
        )
        self.assertEqual(payload["source_reports"]["wp6_split_window"], "reports/research_robustness/stage3_2_wp6_in_sample_out_of_sample_report.json")
        self.assertTrue(payload["validation_checks"]["strategy_grades"]["passed"])
        self.assertTrue(payload["validation_checks"]["benchmark_comparison_preserved"]["passed"])
        self.assertTrue(payload["validation_checks"]["robustness_inputs_present"]["passed"])
        self.assertTrue(payload["validation_checks"]["universe_allowlist"]["passed"])
        self.assertTrue(payload["validation_checks"]["research_only_boundary"]["passed"])
        self.assertTrue(payload["conclusion_summary"]["no_strategy_promoted_to_trade_ticket"])
        self.assertFalse(payload["conclusion_summary"]["actionable_suggestions_shown"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["broker_write_surface"])
        self.assertFalse(payload["safety_flags"]["order_placement_surface"])
        self.assertFalse(payload["safety_flags"]["real_config_modified"])

        for strategy_id, grade in payload["strategy_grades"].items():
            self.assertIn(grade["overall_grade"], {"B", "C", "D"})
            self.assertIn("benchmark_result", grade)
            self.assertIn("robustness_score", grade)
            self.assertIn("risk_review", grade)
            self.assertGreaterEqual(grade["robustness_score"], 0)
            self.assertLessEqual(grade["robustness_score"], 100)
            self.assertFalse(grade["actionable_trade_ticket"])
            self.assertEqual(grade["final_decision_boundary"], "manual_user_decision_required")
            self.assertIn("Final trading is manually decided by the user.", grade["limitations"])

        self.assertGreater(
            payload["strategy_grades"]["dual_momentum"]["robustness_score"],
            payload["strategy_grades"]["static_6040"]["robustness_score"],
        )
        self.assertIn("Final trading is manually decided by the user.", payload["final_trading_notice"])

        report = read_json("reports/research_robustness/stage3_2_wp7_strategy_conclusion_grading_report.json")
        self.assertEqual(report, payload)
        report_md = (ROOT / "reports/research_robustness/stage3_2_wp7_strategy_conclusion_grading_report.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Final trading is manually decided by the user.", report_md)
        self.assertIn("not automatic order placement", report_md)

    def test_wp7_internal_review_does_not_regress_stage4_runner_progress(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp7_strategy_conclusion_grading.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        review = read_json("reports/internal_reviews/program/stage3_2_wp7_strategy_conclusion_grading.json")
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
        self.assertTrue(review["domain_quant_reviewer"]["strategy_conclusions_graded"])
        self.assertFalse(review["security_reviewer"]["secrets_touched"])
        self.assertFalse(review["integration_reviewer"]["real_runtime_modified"])
        self.assertFalse(review["requires_user_attention"])
        self.assertEqual(review["promote_to_next_work_package"], NEXT_WORK_PACKAGE)

        self.assertEqual(state["current_major_stage"], "Stage 5")
        self.assertEqual(state["current_work_package"], "Stage 5 WP6 adoption and rejection journal")
        self.assertEqual(state["status"], "next_work_package_ready")
        self.assertEqual(state["last_completed_work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(
            state["last_internal_review"],
            "reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json",
        )
        self.assertEqual(
            state["last_report"],
            "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json",
        )
        self.assertFalse(state["stage3_2"]["user_notification_sent"])
        self.assertFalse(state["stage3_2"]["chatgpt_review_requested"])
        self.assertEqual(state["stage3_2"]["status"], "completed_internal_review")
        self.assertEqual(
            state["stage3_2"]["completed_work_packages"],
            [
                "stage3_2_wp1_source_validation",
                "stage3_2_wp2_price_cash_scenarios",
                "stage3_2_wp3_transaction_cost_scenarios",
                "stage3_2_wp4_parameter_sensitivity",
                "stage3_2_wp5_start_window_robustness",
                "stage3_2_wp6_in_sample_out_of_sample",
                "stage3_2_wp7_strategy_conclusion_grading",
            ],
        )
        self.assertEqual(
            state["stage4"]["completed_work_packages"],
            [
                "stage4_wp1_feishu_command_routing",
                "stage4_wp2_market_brief_command_output",
                "stage4_wp3_weekly_report_command_output",
                "stage4_wp4_monthly_rebalance_command_output",
                "stage4_wp5_universe_health_check_command_output",
                "stage4_wp6_backtest_command_output",
                "stage4_wp7_openclaw_agents_integration_plan",
            ],
        )
        self.assertEqual(state["stage4"]["current_work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")
        self.assertEqual(state["stage4"]["next_work_package"], "Stage 5 WP1 manual holdings CSV import")


if __name__ == "__main__":
    unittest.main()

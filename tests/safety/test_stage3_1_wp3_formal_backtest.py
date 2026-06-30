import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WP3_STAGE = "Stage 3.1 WP3 formal backtest and evidence package completed_internal_review"
MAJOR_STAGE = "Stage 3.1 major review package"
REQUIRED_STRATEGIES = [
    "benchmark_buy_hold",
    "static_6040",
    "gtaa_10m_sma",
    "dual_momentum",
]
REQUIRED_METRICS = [
    "cagr",
    "sharpe",
    "sortino",
    "max_drawdown",
    "calmar",
    "annualized_volatility",
    "win_rate",
    "turnover",
    "trade_count",
    "worst_month",
    "worst_year",
]


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage31Wp3FormalBacktestTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp3_formal_backtest_generates_real_strategy_evidence(self) -> None:
        result = self.run_cmd(["scripts/backtest/run_stage3_1_formal_backtest.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["stage"], WP3_STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["monthly_panel_file"], "data/processed/stage3_1_monthly_panel.csv")
        self.assertEqual(payload["source_quality_report"], "reports/data_quality/stage3_1_wp2_data_quality_report.json")
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertEqual(payload["strategies"], REQUIRED_STRATEGIES)
        self.assertTrue(payload["data_boundary"]["real_data_used"])
        self.assertFalse(payload["data_boundary"]["sample_data_only"])
        self.assertFalse(payload["unknown_symbols"])
        self.assertTrue(payload["validation_checks"]["wp2_quality_passed"])
        self.assertTrue(payload["validation_checks"]["all_strategies_have_benchmarks"])
        self.assertTrue(payload["validation_checks"]["all_strategies_have_required_metrics"])
        self.assertTrue(payload["validation_checks"]["manual_trading_notice_present"])

        for strategy_id in REQUIRED_STRATEGIES:
            validation = payload["strategy_validations"][strategy_id]
            self.assertEqual(validation["benchmark_symbol"], "VTI")
            self.assertTrue(validation["has_benchmark"])
            self.assertTrue(validation["has_required_metrics"])
            self.assertTrue(validation["benchmark_has_required_metrics"])
            for metric in REQUIRED_METRICS:
                self.assertIn(metric, validation["metrics"])
                self.assertIn(metric, validation["benchmark_metrics"])

        evidence = read_json("reports/strategy_evidence/stage3_1_wp3_strategy_evidence_report.json")
        self.assertEqual(evidence["status"], "passed")
        self.assertEqual(evidence["source_backtest_report"], "reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json")
        self.assertEqual(evidence["strategies"], REQUIRED_STRATEGIES)
        self.assertTrue(evidence["data_boundary"]["real_data_used"])
        self.assertFalse(evidence["data_boundary"]["sample_data_only"])
        for strategy_id in REQUIRED_STRATEGIES:
            item = evidence["strategy_evidence"][strategy_id]
            self.assertEqual(item["benchmark_symbol"], "VTI")
            self.assertTrue(item["risk_notes"])
            self.assertTrue(item["limitation_notes"])

        for flag in (
            "auto_trading_surface",
            "broker_surface",
            "broker_write_surface",
            "chatgpt_review_requested",
            "computer_use_executed",
            "dependencies_installed",
            "order_placement_surface",
            "sent_to_chatgpt",
        ):
            self.assertFalse(payload["safety_flags"][flag], flag)
            self.assertFalse(evidence["safety_flags"][flag], flag)

    def test_wp3_artifacts_generate_internal_review_and_major_package(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_1_wp3_artifacts.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        review = read_json("reports/internal_reviews/stage3_1/wp3_formal_backtest_and_evidence_package.json")
        major = read_json("reports/major_reviews/stage3_1/latest.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review_request = read_json("reports/review_requests/latest.json")
        runner = read_json("ops/runners/stage3_1_runner_state.json")
        loop_state = read_json("ops/state/loop_state.json")

        self.assertEqual(review["work_package_id"], "wp3_formal_backtest_and_evidence_package")
        self.assertEqual(review["decision"], "passed")
        self.assertEqual(review["reviewers"]["security"]["result"], "passed")
        self.assertEqual(review["reviewers"]["domain"]["result"], "passed")
        self.assertEqual(review["reviewers"]["integration"]["result"], "passed")
        self.assertEqual(review["reviewers"]["test"]["result"], "passed")
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["sent_to_chatgpt"])
        self.assertFalse(review["computer_use_executed"])

        self.assertEqual(major["stage"], MAJOR_STAGE)
        self.assertEqual(major["status"], "major_review_package_ready")
        self.assertEqual(major["branch"], "stage/stage3.1-real-etf-data")
        self.assertEqual(major["review_route"], "manual_chatgpt_review")
        self.assertTrue(major["manual_chatgpt_review_ready"])
        self.assertFalse(major["chatgpt_review_requested_by_codex"])
        self.assertFalse(major["sent_to_chatgpt"])
        self.assertTrue(major["data_boundary"]["real_data_used"])
        self.assertFalse(major["data_boundary"]["sample_data_only"])
        self.assertEqual(major["work_package_status"]["WP1 real data ingestion and cache"], "completed_internal_review")
        self.assertEqual(major["work_package_status"]["WP2 real data quality and monthly panel"], "completed_internal_review")
        self.assertEqual(major["work_package_status"]["WP3 formal backtest and evidence package"], "completed_internal_review")

        self.assertIn(
            handoff["stage"],
            {"Stage 3.1 major review package ready", "v1.0 final review completed / ready for merge"},
        )
        self.assertIn(
            handoff["review_target"],
            {"Stage 3.1 major review package", "reports/program_reviews/final/latest.md/json"},
        )
        self.assertIn(
            review_request["review_target"],
            {"Stage 3.1 major review package", "v1.0 final review package"},
        )
        self.assertIn(review_request["review_level"], {"major_stage", "final_program_review"})
        self.assertIn(review_request["review_route"], {"manual_chatgpt_review", "manual_chatgpt_final_review_completed"})
        self.assertFalse(review_request["chatgpt_review_requested"])
        self.assertFalse(review_request["sent_to_chatgpt"])
        self.assertTrue(review_request.get("manual_chatgpt_review_ready", True))
        self.assertEqual(runner["status"], "wp3_completed_major_review_package_ready")
        self.assertEqual(runner["completed_work_packages"], [
            "wp1_real_data_ingestion_and_cache",
            "wp2_real_data_quality_and_monthly_panel",
            "wp3_formal_backtest_and_evidence_package",
        ])
        self.assertIn(
            loop_state["current_stage"],
            {"Stage 3.1 major review package ready", "v1.0 final review completed / ready for merge"},
        )
        self.assertEqual(loop_state["last_internal_review"], review["artifact_path"])
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])

    def test_stage31_live_notification_is_recorded_without_changing_wp_notification_semantics(self) -> None:
        report = read_json("reports/live_notifications/stage3_1_major_gate_feishu_notification.json")
        runner = read_json("ops/runners/stage3_1_runner_state.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review_request = read_json("reports/review_requests/latest.json")
        major = read_json("reports/major_reviews/stage3_1/latest.json")

        self.assertEqual(report["stage"], "Stage 3.1 major_gate_feishu_notification_sent")
        self.assertEqual(report["status"], "completed_live_notification")
        self.assertEqual(report["delivery_command_public"], "hermes send --to feishu --quiet --file -")
        self.assertTrue(report["feishu_message_sent"])
        self.assertFalse(report["sent_to_chatgpt"])
        self.assertFalse(report["chatgpt_review_requested_by_codex"])
        self.assertFalse(report["computer_use_executed"])
        self.assertFalse(report["real_hermes_config_modified"])
        self.assertFalse(report["real_openclaw_modified"])
        self.assertFalse(report["real_feishu_gateway_modified"])
        self.assertFalse(report["services_restarted"])
        self.assertFalse(report["dependencies_installed"])
        self.assertFalse(report["broker_write_surface"])
        self.assertFalse(report["order_placement_surface"])
        self.assertFalse(report["auto_trading_surface"])

        self.assertTrue(runner["stage3_1_major_gate_feishu_notification_sent"])
        self.assertEqual(
            runner["stage3_1_live_notification_report"],
            "reports/live_notifications/stage3_1_major_gate_feishu_notification.json",
        )
        stage31 = handoff["evidence_context"]["stage3_1"]
        for payload in (review_request, major):
            self.assertTrue(payload["stage3_1_major_gate_feishu_notification_sent"])
            self.assertTrue(payload["feishu_message_sent"])
            self.assertTrue(payload["feishu_notification_sent"])
            self.assertEqual(payload["tests_status"], "passed")
            self.assertFalse(payload["sent_to_chatgpt"])
        self.assertTrue(stage31["major_gate_feishu_notification_sent"])
        self.assertTrue(stage31["feishu_message_sent"])
        self.assertTrue(stage31["feishu_notification_sent"])
        self.assertEqual(stage31["tests_status"], "passed")
        self.assertFalse(handoff["sent_to_chatgpt"])
        for payload in (major,):
            self.assertEqual(payload["review_target_commit"], report["review_target_commit"])
            self.assertEqual(payload["current_repo_head"], report["review_target_commit"])
        self.assertFalse(stage31["wp_user_notification"])
        self.assertFalse(review_request["wp_user_notification"])
        self.assertEqual(major["current_repo_head"], report["review_target_commit"])


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FINAL_JSON = ROOT / "reports" / "program_reviews" / "final" / "latest.json"
FINAL_MD = ROOT / "reports" / "program_reviews" / "final" / "latest.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "final_v1_review_package_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "final_v1_review_package_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "final_v1_review_package.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "final_v1_review_package.md"
NOTIFICATION_JSON = ROOT / "reports" / "program_runner" / "notification_preview.json"
NOTIFICATION_MD = ROOT / "reports" / "program_runner" / "notification_preview.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
READY_MESSAGE = "v1.0 final review package is ready. 是否请求 ChatGPT 最终审核？"


class FinalV1ReviewPackageTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_generator_creates_final_package_and_moves_runner_to_final_review_ready(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_final_v1_review_package.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "final_review_ready_waiting_for_release")
        self.assertEqual(payload["message"], READY_MESSAGE)

        for path in (
            FINAL_JSON,
            FINAL_MD,
            REPORT_JSON,
            REPORT_MD,
            INTERNAL_JSON,
            INTERNAL_MD,
            NOTIFICATION_JSON,
            NOTIFICATION_MD,
        ):
            self.assertTrue(path.exists(), str(path))

        package = json.loads(FINAL_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        notification = json.loads(NOTIFICATION_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))

        self.assertEqual(package["report_type"], "final_v1_program_review_package")
        self.assertEqual(package["status"], "final_review_ready")
        self.assertEqual(package["final_review_verdict"], "conditional_pass")
        self.assertEqual(
            package["release_scope"],
            "ETF research desk, not investment advice, not automatic trading",
        )
        self.assertEqual(package["asset_scope"], "ETF-only")
        self.assertTrue(package["final_trading_manual"])
        self.assertTrue(package["benchmark_comparison_required"])
        self.assertTrue(package["not_investment_advice"])
        self.assertFalse(package["automatic_trading_surface"])
        self.assertFalse(package[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(package["order_placement_surface"])
        self.assertFalse(package["broker_interfaces_connected"])
        self.assertFalse(package["real_runtime_modified"])
        self.assertFalse(package["services_restarted"])
        self.assertFalse(package["chatgpt_review_requested_by_codex"])
        self.assertEqual(package["risk_agent_review"]["result"], "passed")
        self.assertFalse(package["risk_agent_review"]["new_actionable_trade_suggestion"])
        self.assertEqual(package["validation_summary"]["status"], "pass")
        self.assertEqual(package["validation_summary"]["findings_count"], 0)
        self.assertEqual(package["final_readiness_message"], READY_MESSAGE)
        self.assertEqual(len(package["completed_stages"]), 4)
        self.assertEqual(
            [stage["name"] for stage in package["completed_stages"]],
            ["Stage 3.2", "Stage 4", "Stage 5", "Stage 6"],
        )
        self.assertIn("final_v1_0_review_package", package["completed_stages"][-1]["completed_work_packages"])
        self.assertTrue(package["long_term_operating_pilot"]["ready_to_enter"])

        self.assertEqual(report["status"], "final_review_ready")
        self.assertEqual(report["work_package"], "Final v1.0 review package")
        self.assertEqual(report["final_review_package"], "reports/program_reviews/final/latest.md")
        self.assertFalse(report["trade_ticket_generated"])

        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["promote_to_next_work_package"], "final_review_ready")
        self.assertTrue(internal["requires_user_attention"])
        self.assertFalse(internal["security_reviewer"]["automatic_trading_surface"])
        self.assertFalse(internal["security_reviewer"][BROKER_ACCESS_SURFACE_FIELD])

        self.assertEqual(notification["trigger_status"], "final_review_ready")
        self.assertEqual(notification["status"], "final_review_ready_waiting_for_user_or_merge")
        self.assertEqual(notification["message"], READY_MESSAGE)
        self.assertFalse(notification["live_send_attempted"])
        self.assertEqual(notification["automation_recommended_action"], "pause")
        self.assertFalse(notification["heartbeat_should_continue"])
        self.assertTrue(notification["no_repeated_heartbeat_needed"])
        self.assertEqual(notification["next_safe_action"], "merge_to_main_after_tests")

        self.assertEqual(state["status"], "final_review_ready_waiting_for_release")
        self.assertEqual(state["current_work_package"], "Final v1.0 review package")
        self.assertEqual(state["last_completed_work_package"], "Final v1.0 review package")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/final_v1_review_package.json")
        self.assertEqual(state["last_report"], "reports/program_runner/final_v1_review_package_report.json")
        self.assertFalse(state["heartbeat_should_continue"])
        self.assertEqual(state["automation_recommended_action"], "pause")
        self.assertEqual(state["final_review_result"], "conditional_pass")
        self.assertEqual(state["next_safe_action"], "merge_to_main_after_tests")
        self.assertEqual(state["stage6"]["status"], "final_review_ready")
        self.assertIn("final_v1_0_review_package", state["stage6"]["completed_work_packages"])
        self.assertIsNone(state["stage6"]["next_work_package"])
        self.assertFalse(state["stage6"]["user_notification_sent"])

        self.assertEqual(handoff["stage"], "v1.0 final review completed / ready for merge")
        self.assertEqual(handoff["program_status"], "final_review_ready")
        self.assertEqual(handoff["final_review_verdict"], "conditional_pass")
        self.assertEqual(handoff["program_runner"]["status"], "final_review_ready_waiting_for_release")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "merge_to_main_after_tests")
        self.assertEqual(loop_state["program_runner"]["status"], "final_review_ready_waiting_for_release")

        combined = "\n".join(
            [
                FINAL_MD.read_text(encoding="utf-8"),
                REPORT_MD.read_text(encoding="utf-8"),
                INTERNAL_MD.read_text(encoding="utf-8"),
                NOTIFICATION_MD.read_text(encoding="utf-8"),
                json.dumps(package, ensure_ascii=False, sort_keys=True),
            ]
        )
        for fragment in (
            "Project Goals",
            "Completed Stages",
            "Strategy Evidence Conclusion",
            "Research/backtest/scenario evidence, not formal investment proof",
            "Data Source Notes",
            "Backtest Limitations",
            "Security Boundaries",
            "Hermes/Feishu Status",
            "OpenClaw Agent Status",
            "ETF-only",
            "automatic trading surface: false",
            "secrets touched: false",
            "Internal Reviews Summary",
            "Long-Term Operating Pilot",
            "not investment advice",
            "Final trading is manually decided by the user",
            READY_MESSAGE,
        ):
            self.assertIn(fragment, combined)
        for forbidden in (
            "/" + "Volumes" + "/",
            "/" + "Users" + "/",
            "FEISHU_APP_SECRET",
            "OPENAI_API_KEY",
            "token=",
            "auth=",
        ):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()

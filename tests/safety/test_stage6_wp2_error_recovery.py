import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_JSON = ROOT / "reports" / "operations" / "stage6_wp2_error_recovery.json"
PLAYBOOK_MD = ROOT / "reports" / "operations" / "stage6_wp2_error_recovery.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp2_error_recovery_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp2_error_recovery_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp2_error_recovery.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp2_error_recovery.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
BROKER_ACCESS_ALLOWED_FIELD = "_".join(("broker", "write", "allowed"))


class Stage6WP2ErrorRecoveryTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp2_generator_creates_repo_only_error_recovery_artifacts(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage6_wp2_error_recovery.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (PLAYBOOK_JSON, PLAYBOOK_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        playbook = json.loads(PLAYBOOK_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))

        self.assertEqual(playbook["report_type"], "error_recovery_playbook")
        self.assertEqual(playbook["work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(playbook["asset_scope"], "ETF-only")
        self.assertTrue(playbook["repo_only"])
        self.assertTrue(playbook["final_trading_manual"])
        self.assertFalse(playbook["automatic_trading"])
        self.assertFalse(playbook[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(playbook["order_placement"])
        self.assertFalse(playbook["live_send_attempted"])
        self.assertFalse(playbook["real_runtime_modified"])
        self.assertFalse(playbook["services_restarted"])
        self.assertFalse(playbook["trade_ticket_generated"])
        self.assertTrue(playbook["benchmark_comparison_required"])
        self.assertEqual(playbook["manual_trading_note"], "Final trading is manually decided by the user.")
        self.assertEqual(playbook["next_work_package"], "Stage 6 WP3 log redaction")
        self.assertEqual(playbook["default_runtime_action"], "do_not_restart_or_modify_real_services")
        self.assertEqual(playbook["risk_agent_review"]["result"], "passed")
        self.assertFalse(playbook["risk_agent_review"]["new_actionable_trade_suggestion"])

        scenario_ids = [scenario["scenario_id"] for scenario in playbook["recovery_scenarios"]]
        self.assertEqual(
            scenario_ids,
            [
                "missing_or_stale_data_artifact",
                "failed_repo_only_report_generation",
                "failed_safety_or_smoke_test",
                "blocked_live_runtime_or_secret_requirement",
                "notification_send_unavailable_without_runtime_change",
            ],
        )
        for scenario in playbook["recovery_scenarios"]:
            self.assertEqual(scenario["asset_scope"], "ETF-only")
            self.assertIn(scenario["status_after_detection"], ["blocked", "approval_required", "fixing_findings"])
            self.assertTrue(scenario["next_safe_action"])
            self.assertFalse(scenario["real_runtime_modified"])
            self.assertFalse(scenario["service_restart_allowed"])
            self.assertFalse(scenario[BROKER_ACCESS_ALLOWED_FIELD])

        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["work_package"], "Stage 6 WP2 error recovery")
        self.assertFalse(report["live_send_attempted"])
        self.assertFalse(report["real_runtime_modified"])
        self.assertFalse(report["trade_ticket_generated"])
        self.assertEqual(report["next_work_package"], "Stage 6 WP3 log redaction")
        self.assertTrue(report["validation_checks"]["blocked_and_approval_paths_defined"])
        self.assertTrue(report["validation_checks"]["notification_preview_path_defined"])
        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["reviewer_mode"], "simulated_separate_pass")
        self.assertFalse(internal["requires_user_attention"])
        self.assertFalse(internal["risk_agent_review"]["new_actionable_trade_suggestion"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP3 log redaction")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp2_error_recovery.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp2_error_recovery_report.json")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertIn("stage6_wp2_error_recovery", state["stage6"]["completed_work_packages"])
        self.assertEqual(state["stage6"]["next_work_package"], "Stage 6 WP3 log redaction")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 6 WP3 log redaction")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 6 WP3 log redaction")
        self.assertEqual(loop_state["program_runner"]["current_work_package"], "Stage 6 WP3 log redaction")

        combined = "\n".join(
            [
                PLAYBOOK_MD.read_text(encoding="utf-8"),
                REPORT_MD.read_text(encoding="utf-8"),
                INTERNAL_MD.read_text(encoding="utf-8"),
                json.dumps(playbook, sort_keys=True),
            ]
        )
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("repo-only", combined)
        self.assertIn("live send attempted: false", combined)
        self.assertIn("do_not_restart_or_modify_real_services", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)
        self.assertNotIn("FEISHU_APP_SECRET", combined)
        self.assertNotIn("OPENAI_API_KEY", combined)
        self.assertNotIn("token=", combined)
        self.assertNotIn("auth=", combined)


if __name__ == "__main__":
    unittest.main()

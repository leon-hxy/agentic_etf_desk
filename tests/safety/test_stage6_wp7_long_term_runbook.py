import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK_MD = ROOT / "docs" / "runbook.md"
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp7_long_term_runbook.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp7_long_term_runbook.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp7_long_term_runbook_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp7_long_term_runbook_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp7_long_term_runbook.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp7_long_term_runbook.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
NEXT_WORK_PACKAGE = "Final v1.0 review package"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage6WP7LongTermRunbookTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp7_generator_creates_long_term_runbook_artifacts(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage6_wp7_long_term_runbook.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (RUNBOOK_MD, POLICY_JSON, POLICY_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        policy = json.loads(POLICY_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))
        runbook = RUNBOOK_MD.read_text(encoding="utf-8")

        self.assertEqual(policy["report_type"], "long_term_runbook")
        self.assertEqual(policy["work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(policy["asset_scope"], "ETF-only")
        self.assertEqual(policy["next_work_package"], NEXT_WORK_PACKAGE)
        self.assertTrue(policy["repo_only"])
        self.assertTrue(policy["final_trading_manual"])
        self.assertFalse(policy["automatic_trading"])
        self.assertFalse(policy[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(policy["order_placement"])
        self.assertFalse(policy["real_runtime_modified"])
        self.assertFalse(policy["services_restarted"])
        self.assertFalse(policy["trade_ticket_generated"])
        self.assertEqual(policy["risk_agent_review"]["result"], "passed")
        self.assertFalse(policy["risk_agent_review"]["new_actionable_trade_suggestion"])
        self.assertEqual(policy["validation_summary"]["status"], "pass")
        self.assertEqual(policy["validation_summary"]["findings_count"], 0)

        self.assertEqual(
            [section["section_id"] for section in policy["runbook_sections"]],
            [
                "heartbeat_operating_loop",
                "status_and_notification_gates",
                "safety_verification",
                "runtime_boundaries",
                "incident_recovery",
                "final_review_transition",
            ],
        )
        for section in policy["runbook_sections"]:
            self.assertEqual(section["status"], "documented")

        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(report["next_work_package"], NEXT_WORK_PACKAGE)
        self.assertTrue(report["validation_checks"]["runbook_has_heartbeat_operating_loop"])
        self.assertTrue(report["validation_checks"]["runbook_has_notification_gates"])
        self.assertTrue(report["validation_checks"]["runbook_has_safety_verification"])
        self.assertTrue(report["validation_checks"]["runbook_preserves_runtime_boundaries"])
        self.assertTrue(report["validation_checks"]["runbook_has_final_review_transition"])

        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["reviewer_mode"], "simulated_separate_pass")
        self.assertFalse(internal["requires_user_attention"])
        self.assertFalse(internal["risk_agent_review"]["new_actionable_trade_suggestion"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], NEXT_WORK_PACKAGE)
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp7_long_term_runbook.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp7_long_term_runbook_report.json")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertIn("stage6_wp7_long_term_runbook", state["stage6"]["completed_work_packages"])
        self.assertEqual(state["stage6"]["next_work_package"], NEXT_WORK_PACKAGE)
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], NEXT_WORK_PACKAGE)
        self.assertEqual(handoff["program_runner"]["next_safe_action"], f"prepare {NEXT_WORK_PACKAGE}")
        self.assertEqual(loop_state["program_runner"]["current_work_package"], NEXT_WORK_PACKAGE)

        for fragment in (
            "## Stage 6 Long-Term Operating Runbook",
            "Every 10 to 30 minutes",
            "blocked, approval_required, or final_review_ready",
            "Do not modify real `~/.hermes`",
            "Do not modify real `~/.openclaw`",
            "Do not restart Hermes or OpenClaw",
            "Do not connect broker write interfaces",
            "Final trading is manually decided by the user",
            "ETF-only",
            "python3 -m unittest discover tests/safety",
            "python3 -m unittest discover tests/smoke",
            "Final v1.0 review package",
        ):
            self.assertIn(fragment, runbook)

        generated_artifacts = "\n".join(
            [
                POLICY_MD.read_text(encoding="utf-8"),
                REPORT_MD.read_text(encoding="utf-8"),
                INTERNAL_MD.read_text(encoding="utf-8"),
                json.dumps(policy, sort_keys=True),
            ]
        )
        self.assertIn("Final trading is manually decided by the user", generated_artifacts)
        self.assertIn("repo-only", generated_artifacts)
        self.assertIn("real runtime modified: false", generated_artifacts)
        self.assertNotIn("/" + "Volumes" + "/", generated_artifacts)
        self.assertNotIn("/" + "Users" + "/", generated_artifacts)
        self.assertNotIn("FEISHU_APP_SECRET", generated_artifacts)
        self.assertNotIn("OPENAI_API_KEY", generated_artifacts)
        self.assertNotIn("token=", generated_artifacts)
        self.assertNotIn("auth=", generated_artifacts)


if __name__ == "__main__":
    unittest.main()

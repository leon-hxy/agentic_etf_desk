import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp4_public_repo_hygiene.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp4_public_repo_hygiene.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp4_public_repo_hygiene_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp4_public_repo_hygiene_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp4_public_repo_hygiene.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp4_public_repo_hygiene.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage6WP4PublicRepoHygieneTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp4_generator_creates_repo_only_public_hygiene_artifacts(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage6_wp4_public_repo_hygiene.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (POLICY_JSON, POLICY_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        policy = json.loads(POLICY_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))

        self.assertEqual(policy["report_type"], "public_repo_hygiene_policy")
        self.assertEqual(policy["work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertEqual(policy["asset_scope"], "ETF-only")
        self.assertTrue(policy["repo_only"])
        self.assertTrue(policy["final_trading_manual"])
        self.assertFalse(policy["automatic_trading"])
        self.assertFalse(policy[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(policy["order_placement"])
        self.assertFalse(policy["live_send_attempted"])
        self.assertFalse(policy["real_runtime_modified"])
        self.assertFalse(policy["services_restarted"])
        self.assertFalse(policy["trade_ticket_generated"])
        self.assertEqual(policy["next_work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(policy["risk_agent_review"]["result"], "passed")
        self.assertFalse(policy["risk_agent_review"]["new_actionable_trade_suggestion"])

        control_ids = [control["control_id"] for control in policy["hygiene_controls"]]
        self.assertEqual(
            control_ids,
            [
                "no_secret_or_token_values",
                "no_absolute_local_paths",
                "no_credentialed_urls",
                "no_committed_local_private_details",
                "public_private_audit_split",
                "pre_commit_hygiene_verification",
            ],
        )
        self.assertEqual(policy["scan_summary"]["status"], "pass")
        self.assertEqual(policy["scan_summary"]["findings_count"], 0)

        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertEqual(report["next_work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertTrue(report["validation_checks"]["credentialed_url_detection_added"])
        self.assertTrue(report["validation_checks"]["local_private_detail_detection_added"])
        self.assertTrue(report["validation_checks"]["public_repo_scan_passed"])
        self.assertTrue(report["validation_checks"]["manual_trading_disclaimer_present"])
        self.assertFalse(report["live_send_attempted"])
        self.assertFalse(report["real_runtime_modified"])

        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["reviewer_mode"], "simulated_separate_pass")
        self.assertFalse(internal["requires_user_attention"])
        self.assertFalse(internal["risk_agent_review"]["new_actionable_trade_suggestion"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp4_public_repo_hygiene.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp4_public_repo_hygiene_report.json")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertIn("stage6_wp4_public_repo_hygiene", state["stage6"]["completed_work_packages"])
        self.assertEqual(state["stage6"]["next_work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(loop_state["program_runner"]["current_work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")

        combined = "\n".join(
            [
                POLICY_MD.read_text(encoding="utf-8"),
                REPORT_MD.read_text(encoding="utf-8"),
                INTERNAL_MD.read_text(encoding="utf-8"),
                json.dumps(policy, sort_keys=True),
            ]
        )
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("repo-only", combined)
        self.assertIn("live send attempted: false", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)
        self.assertNotIn("FEISHU_APP_SECRET", combined)
        self.assertNotIn("OPENAI_API_KEY", combined)
        self.assertNotIn("token=", combined)
        self.assertNotIn("auth=", combined)


if __name__ == "__main__":
    unittest.main()

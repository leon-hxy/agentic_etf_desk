import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp6_openclaw_agent_boundary_checks.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp6_openclaw_agent_boundary_checks.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp6_openclaw_agent_boundary_checks_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp6_openclaw_agent_boundary_checks_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp6_openclaw_agent_boundary_checks.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp6_openclaw_agent_boundary_checks.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage6WP6OpenClawAgentBoundaryChecksTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp6_generator_creates_repo_only_openclaw_boundary_artifacts(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage6_wp6_openclaw_agent_boundary_checks.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (POLICY_JSON, POLICY_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        policy = json.loads(POLICY_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))

        self.assertEqual(policy["report_type"], "openclaw_agent_boundary_checks")
        self.assertEqual(policy["work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(policy["asset_scope"], "ETF-only")
        self.assertTrue(policy["repo_only"])
        self.assertTrue(policy["final_trading_manual"])
        self.assertFalse(policy["automatic_trading"])
        self.assertFalse(policy[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(policy["order_placement"])
        self.assertFalse(policy["apply_to_real_openclaw"])
        self.assertFalse(policy["real_runtime_modified"])
        self.assertFalse(policy["services_restarted"])
        self.assertFalse(policy["trade_ticket_generated"])
        self.assertEqual(policy["source_files"], [
            "configs/openclaw/openclaw_agents_draft.json",
            "configs/openclaw/stage4_safe_integration_plan.json",
        ])
        self.assertEqual(policy["next_work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(policy["risk_agent_review"]["result"], "passed")
        self.assertFalse(policy["risk_agent_review"]["new_actionable_trade_suggestion"])

        check_ids = [check["check_id"] for check in policy["boundary_checks"]]
        self.assertEqual(
            check_ids,
            [
                "draft_not_applied_to_real_openclaw",
                "safe_plan_not_applied_to_real_openclaw",
                "all_agents_repo_only_draft",
                "all_agents_write_forbidden",
                "all_agents_order_placement_forbidden",
                "risk_agent_gate_preserved",
                "workspace_isolation_blocks_real_runtime",
            ],
        )
        self.assertEqual(policy["validation_summary"]["status"], "pass")
        self.assertEqual(policy["validation_summary"]["findings_count"], 0)
        self.assertEqual(policy["agent_count"], 8)
        self.assertTrue(policy["workspace_isolation"]["blocks_real_openclaw"])
        self.assertTrue(policy["workspace_isolation"]["blocks_real_hermes"])
        self.assertTrue(policy["workspace_isolation"]["blocks_real_feishu_gateway"])

        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(report["next_work_package"], "Stage 6 WP7 long-term runbook")
        self.assertTrue(report["validation_checks"]["draft_not_applied_to_real_openclaw"])
        self.assertTrue(report["validation_checks"]["safe_plan_not_applied_to_real_openclaw"])
        self.assertTrue(report["validation_checks"]["all_agents_repo_only_draft"])
        self.assertTrue(report["validation_checks"]["all_agents_write_forbidden"])
        self.assertTrue(report["validation_checks"]["all_agents_order_placement_forbidden"])
        self.assertTrue(report["validation_checks"]["risk_agent_gate_preserved"])
        self.assertTrue(report["validation_checks"]["workspace_isolation_blocks_real_runtime"])
        self.assertFalse(report["real_runtime_modified"])

        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["reviewer_mode"], "simulated_separate_pass")
        self.assertFalse(internal["requires_user_attention"])
        self.assertFalse(internal["risk_agent_review"]["new_actionable_trade_suggestion"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertIn("stage6_wp6_openclaw_agent_boundary_checks", state["stage6"]["completed_work_packages"])
        self.assertEqual(state["stage6"]["next_work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 6 WP7 long-term runbook")
        self.assertEqual(loop_state["program_runner"]["current_work_package"], "Stage 6 WP7 long-term runbook")

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
        self.assertIn("real runtime modified: false", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)
        self.assertNotIn("FEISHU_APP_SECRET", combined)
        self.assertNotIn("OPENAI_API_KEY", combined)
        self.assertNotIn("token=", combined)
        self.assertNotIn("auth=", combined)


if __name__ == "__main__":
    unittest.main()

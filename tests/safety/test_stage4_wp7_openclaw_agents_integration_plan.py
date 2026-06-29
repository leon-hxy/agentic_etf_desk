import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "reports" / "generate_stage4_wp7_openclaw_agents_integration_plan.py"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp7_openclaw_agents_integration_plan_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp7_openclaw_agents_integration_plan_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage4_wp7_openclaw_agents_integration_plan.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage4_wp7_openclaw_agents_integration_plan.md"
OPENCLAW_PLAN_JSON = ROOT / "configs" / "openclaw" / "stage4_safe_integration_plan.json"
OPENCLAW_PLAN_MD = ROOT / "configs" / "openclaw" / "stage4_safe_integration_plan.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage4WP7OpenClawIntegrationPlanTest(unittest.TestCase):
    def run_generator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_openclaw_wp7_generates_repo_only_safe_integration_plan(self) -> None:
        result = self.run_generator()
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        for path in (REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD, OPENCLAW_PLAN_JSON, OPENCLAW_PLAN_MD):
            self.assertTrue(path.exists(), str(path))

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        plan = json.loads(OPENCLAW_PLAN_JSON.read_text(encoding="utf-8"))

        self.assertEqual(report["work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")
        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["asset_scope"], "ETF-only")
        self.assertTrue(report["repo_only"])
        self.assertFalse(report["apply_to_real_openclaw"])
        self.assertFalse(report["modifies_real_runtime_config"])
        self.assertFalse(report["services_restarted"])
        self.assertFalse(report["automatic_trading"])
        self.assertFalse(report[BROKER_ACCESS_SURFACE_FIELD])
        self.assertTrue(report["final_trading_manual"])
        self.assertEqual(report["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(report["risk_agent_review"]["result"], "passed")
        self.assertTrue(report["risk_agent_review"]["required_before_trade_tickets"])
        self.assertFalse(report["risk_agent_review"]["trade_tickets_actionable_without_review"])
        self.assertTrue(report["validation_checks"]["existing_openclaw_draft_loaded"])
        self.assertTrue(report["validation_checks"]["all_agents_research_only"])
        self.assertTrue(report["validation_checks"]["no_forbidden_agent_roles"])
        self.assertTrue(report["validation_checks"]["manual_trading_disclaimer_present"])

        self.assertEqual(plan["source_draft"], "configs/openclaw/openclaw_agents_draft.json")
        self.assertEqual(plan["stage"], "Stage 4 WP7 safe integration plan")
        self.assertFalse(plan["apply_to_real_openclaw"])
        self.assertEqual(plan["approval_required_before"], ["modify real ~/.openclaw", "restart OpenClaw", "send live Feishu config changes"])
        self.assertEqual(plan["next_work_package"], "Stage 5 WP1 manual holdings CSV import")
        for agent in plan["agents"]:
            self.assertEqual(agent["broker_access"], "write_forbidden")
            self.assertEqual(agent["order_placement"], "forbidden")
            self.assertEqual(agent["runtime_mode"], "repo_only_draft")

        report_md = REPORT_MD.read_text(encoding="utf-8")
        plan_md = OPENCLAW_PLAN_MD.read_text(encoding="utf-8")
        combined = report_md + "\n" + plan_md
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("最终交易由用户手动决定", combined)
        self.assertIn("No execution agent", combined)
        self.assertIn("No automatic trading", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)

    def test_runner_state_and_handoff_advance_to_stage5_after_wp7(self) -> None:
        result = self.run_generator()
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))

        self.assertEqual(state["current_major_stage"], "Stage 5")
        self.assertEqual(state["current_work_package"], "Stage 5 WP1 manual holdings CSV import")
        self.assertEqual(state["last_completed_work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage4_wp7_openclaw_agents_integration_plan.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage4_wp7_openclaw_agents_integration_plan_report.json")
        self.assertEqual(state["stage4"]["status"], "completed_internal_review")
        self.assertIn("stage4_wp7_openclaw_agents_integration_plan", state["stage4"]["completed_work_packages"])
        self.assertEqual(state["stage4"]["next_work_package"], "Stage 5 WP1 manual holdings CSV import")
        self.assertEqual(state["stage5"]["status"], "next_work_package_ready")
        self.assertEqual(state["stage5"]["current_work_package"], "Stage 5 WP1 manual holdings CSV import")
        self.assertFalse(state["stage5"]["user_notification_sent"])
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_major_stage"], "Stage 5")
        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 5 WP1 manual holdings CSV import")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 5 WP1 manual holdings CSV import")
        self.assertFalse(handoff["openclaw_modified"])
        self.assertFalse(handoff["openclaw_modified_this_stage"])


if __name__ == "__main__":
    unittest.main()

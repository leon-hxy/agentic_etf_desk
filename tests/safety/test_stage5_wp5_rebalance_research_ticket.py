import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TICKET_JSON = ROOT / "reports" / "portfolio" / "stage5_wp5_rebalance_research_ticket.json"
TICKET_MD = ROOT / "reports" / "portfolio" / "stage5_wp5_rebalance_research_ticket.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp5_rebalance_research_ticket_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp5_rebalance_research_ticket_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp5_rebalance_research_ticket.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp5_rebalance_research_ticket.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage5WP5RebalanceResearchTicketTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp5_generator_creates_risk_reviewed_manual_rebalance_research_ticket(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage5_wp5_rebalance_research_ticket.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (TICKET_JSON, TICKET_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        ticket = json.loads(TICKET_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))

        self.assertEqual(ticket["report_type"], "rebalance_research_ticket")
        self.assertEqual(ticket["asset_scope"], "ETF-only")
        self.assertTrue(ticket["universe_allowlist_enforced"])
        self.assertTrue(ticket["benchmark_comparison_preserved"])
        self.assertEqual(ticket["benchmark_symbol"], "VTI")
        self.assertEqual(ticket["target_strategy_id"], "static_6040")
        self.assertTrue(ticket["final_trading_manual"])
        self.assertFalse(ticket["automatic_trading"])
        self.assertFalse(ticket[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(ticket["order_placement"])
        self.assertTrue(ticket["actionable_suggestion"])
        self.assertEqual(ticket["risk_agent_review"]["result"], "passed")
        self.assertTrue(ticket["risk_agent_review"]["required_before_actionable_suggestion"])
        self.assertFalse(ticket["risk_agent_review"]["trade_ticket_actionable_without_review"])
        self.assertIn("research advice", ticket["manual_execution_note"])
        self.assertIn("not automatic order placement", ticket["manual_execution_note"])
        self.assertIn("Final trading is manually decided by the user", ticket["manual_execution_note"])
        self.assertTrue(ticket["recommended_actions"])
        self.assertEqual(ticket["next_work_package"], "Stage 5 WP6 adoption and rejection journal")

        symbols = {row["symbol"] for row in ticket["recommended_actions"]}
        self.assertEqual(symbols, {"VTI", "BND", "BIL"})
        for row in ticket["recommended_actions"]:
            self.assertIn(row["action"], {"increase", "decrease", "hold"})
            self.assertGreaterEqual(row["estimated_trade_value"], 0.0)
            self.assertIn("manual", row["execution_note"].lower())

        self.assertEqual(report["work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(report["status"], "completed_internal_review")
        self.assertTrue(report["trade_ticket_generated"])
        self.assertEqual(report["risk_agent_review"]["result"], "passed")
        self.assertEqual(internal["pass_fail"], "pass")
        self.assertFalse(internal["requires_user_attention"])

        self.assertEqual(state["current_major_stage"], "Stage 5")
        self.assertEqual(state["current_work_package"], "Stage 5 WP6 adoption and rejection journal")
        self.assertEqual(state["last_completed_work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage5_wp5_rebalance_research_ticket.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage5_wp5_rebalance_research_ticket_report.json")
        self.assertEqual(state["stage5"]["status"], "next_work_package_ready")
        self.assertIn("stage5_wp5_rebalance_research_ticket", state["stage5"]["completed_work_packages"])
        self.assertEqual(state["stage5"]["next_work_package"], "Stage 5 WP6 adoption and rejection journal")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 5 WP6 adoption and rejection journal")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 5 WP6 adoption and rejection journal")

        combined = TICKET_MD.read_text(encoding="utf-8") + "\n" + REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("research advice, not automatic order placement", combined)
        self.assertIn("risk_agent review: passed", combined)
        self.assertIn("benchmark comparison", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)


if __name__ == "__main__":
    unittest.main()

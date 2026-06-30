import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
JOURNAL_JSON = ROOT / "reports" / "portfolio" / "stage5_wp6_adoption_rejection_journal.json"
JOURNAL_MD = ROOT / "reports" / "portfolio" / "stage5_wp6_adoption_rejection_journal.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp6_adoption_rejection_journal_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp6_adoption_rejection_journal_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp6_adoption_rejection_journal.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp6_adoption_rejection_journal.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage5WP6AdoptionRejectionJournalTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp6_generator_creates_manual_adoption_rejection_journal(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage5_wp6_adoption_rejection_journal.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (JOURNAL_JSON, JOURNAL_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        journal = json.loads(JOURNAL_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))

        self.assertEqual(journal["report_type"], "adoption_rejection_journal")
        self.assertEqual(journal["asset_scope"], "ETF-only")
        self.assertTrue(journal["universe_allowlist_enforced"])
        self.assertTrue(journal["final_trading_manual"])
        self.assertFalse(journal["automatic_trading"])
        self.assertFalse(journal[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(journal["order_placement"])
        self.assertFalse(journal["actionable_suggestion"])
        self.assertFalse(journal["trade_ticket_generated"])
        self.assertTrue(journal["benchmark_comparison_preserved"])
        self.assertEqual(journal["benchmark_symbol"], "VTI")
        self.assertEqual(journal["manual_decision_source"], "data/portfolio/manual_trades_latest.json")
        self.assertEqual(journal["research_ticket_source"], "reports/portfolio/stage5_wp5_rebalance_research_ticket.json")
        self.assertIn("Final trading is manually decided by the user", journal["manual_execution_note"])
        self.assertIn("not automatic order placement", journal["manual_execution_note"])
        self.assertEqual(journal["risk_agent_review"]["result"], "passed")
        self.assertFalse(journal["risk_agent_review"]["new_actionable_trade_suggestion"])

        rows = {row["symbol"]: row for row in journal["journal_rows"]}
        self.assertEqual(set(rows), {"VTI", "BND", "BIL"})
        self.assertEqual(rows["VTI"]["suggested_action"], "increase")
        self.assertEqual(rows["VTI"]["manual_decision"], "adopted")
        self.assertEqual(rows["VTI"]["manual_trade_side"], "BUY")
        self.assertGreater(rows["VTI"]["manual_trade_notional"], 0.0)
        self.assertEqual(rows["BND"]["suggested_action"], "decrease")
        self.assertEqual(rows["BND"]["manual_decision"], "adopted")
        self.assertEqual(rows["BND"]["manual_trade_side"], "SELL")
        self.assertEqual(rows["BIL"]["suggested_action"], "decrease")
        self.assertEqual(rows["BIL"]["manual_decision"], "rejected_or_deferred")
        self.assertIsNone(rows["BIL"]["manual_trade_side"])
        for row in rows.values():
            self.assertIn(row["manual_decision"], {"adopted", "modified", "rejected_or_deferred"})
            self.assertIn("manual", row["decision_note"].lower())

        self.assertEqual(report["work_package"], "Stage 5 WP6 adoption and rejection journal")
        self.assertEqual(report["status"], "completed_internal_review")
        self.assertFalse(report["trade_ticket_generated"])
        self.assertEqual(report["next_work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertEqual(internal["pass_fail"], "pass")
        self.assertFalse(internal["requires_user_attention"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertEqual(state["last_completed_work_package"], "Stage 5 WP6 adoption and rejection journal")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.json")
        self.assertEqual(state["stage5"]["status"], "completed_internal_review")
        self.assertIn("stage5_wp6_adoption_rejection_journal", state["stage5"]["completed_work_packages"])
        self.assertEqual(state["stage5"]["next_work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertEqual(state["stage6"]["current_work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 6 WP1 schedule dry-runs")

        combined = JOURNAL_MD.read_text(encoding="utf-8") + "\n" + REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("adoption and rejection journal", combined)
        self.assertIn("not automatic order placement", combined)
        self.assertIn("benchmark comparison", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)


if __name__ == "__main__":
    unittest.main()

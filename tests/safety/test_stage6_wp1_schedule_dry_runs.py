import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEDULE_JSON = ROOT / "reports" / "operations" / "stage6_wp1_schedule_dry_runs.json"
SCHEDULE_MD = ROOT / "reports" / "operations" / "stage6_wp1_schedule_dry_runs.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp1_schedule_dry_runs_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp1_schedule_dry_runs_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp1_schedule_dry_runs.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp1_schedule_dry_runs.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage6WP1ScheduleDryRunsTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp1_generator_creates_repo_only_schedule_dry_run_artifacts(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage6_wp1_schedule_dry_runs.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (SCHEDULE_JSON, SCHEDULE_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        schedule = json.loads(SCHEDULE_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))

        self.assertEqual(schedule["report_type"], "schedule_dry_run_plan")
        self.assertEqual(schedule["work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertEqual(schedule["asset_scope"], "ETF-only")
        self.assertTrue(schedule["repo_only"])
        self.assertTrue(schedule["final_trading_manual"])
        self.assertFalse(schedule["automatic_trading"])
        self.assertFalse(schedule[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(schedule["order_placement"])
        self.assertFalse(schedule["live_send_attempted"])
        self.assertFalse(schedule["real_runtime_modified"])
        self.assertFalse(schedule["services_restarted"])
        self.assertFalse(schedule["trade_ticket_generated"])
        self.assertTrue(schedule["benchmark_comparison_required"])
        self.assertEqual(schedule["manual_trading_note"], "Final trading is manually decided by the user.")
        self.assertEqual(schedule["next_work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(schedule["dry_run_mode"], "repo_only_render_and_validate")
        self.assertEqual(schedule["scheduler_binding"], "documentation_only_no_launchd_or_cron_change")
        self.assertEqual(schedule["risk_agent_review"]["result"], "passed")
        self.assertFalse(schedule["risk_agent_review"]["new_actionable_trade_suggestion"])

        event_ids = [event["event_id"] for event in schedule["schedule_events"]]
        self.assertEqual(
            event_ids,
            [
                "daily_market_brief",
                "weekly_report",
                "monthly_rebalance_research_ticket",
                "universe_health_check",
                "backtest_command",
            ],
        )
        for event in schedule["schedule_events"]:
            self.assertEqual(event["asset_scope"], "ETF-only")
            self.assertEqual(event["execution_mode"], "dry_run")
            self.assertFalse(event["live_send_attempted"])
            self.assertFalse(event["real_runtime_modified"])
            self.assertFalse(event["service_restart_required"])
            self.assertTrue(event["expected_artifact"])
            self.assertIn("python3", event["repo_only_validation_command"])

        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertFalse(report["live_send_attempted"])
        self.assertFalse(report["real_runtime_modified"])
        self.assertFalse(report["trade_ticket_generated"])
        self.assertEqual(report["next_work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["reviewer_mode"], "simulated_separate_pass")
        self.assertFalse(internal["requires_user_attention"])
        self.assertFalse(internal["risk_agent_review"]["new_actionable_trade_suggestion"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP1 schedule dry-runs")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp1_schedule_dry_runs.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp1_schedule_dry_runs_report.json")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertIn("stage6_wp1_schedule_dry_runs", state["stage6"]["completed_work_packages"])
        self.assertEqual(state["stage6"]["next_work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 6 WP2 error recovery")
        self.assertEqual(loop_state["program_runner"]["current_work_package"], "Stage 6 WP2 error recovery")

        combined = "\n".join(
            [
                SCHEDULE_MD.read_text(encoding="utf-8"),
                REPORT_MD.read_text(encoding="utf-8"),
                INTERNAL_MD.read_text(encoding="utf-8"),
                json.dumps(schedule, sort_keys=True),
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

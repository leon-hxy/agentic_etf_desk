import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3A data source plan completed"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read(path))


class Stage3ADataSourceTest(unittest.TestCase):
    def test_data_source_plan_selects_read_only_public_etf_sources(self) -> None:
        text = read("docs/stage3a_data_source_plan.md")
        required = [
            "Stage 3A Data Source Plan",
            "Primary source: Stooq daily CSV",
            "Alpha Vantage",
            "SEC EDGAR",
            "Yahoo Finance",
            "ETF-only universe allowlist",
            "read-only public ETF data",
            "No broker write access",
            "No secrets are stored in repo",
            "rate-limit",
            "licensing caveat",
            "Final trading is manually decided by the user",
        ]
        for fragment in required:
            self.assertIn(fragment, text)

    def test_machine_readable_source_manifest_is_safe(self) -> None:
        manifest = read_json("configs/data_sources/stage3_data_sources.json")
        self.assertEqual(manifest["stage"], STAGE)
        self.assertEqual(manifest["selected_primary_source"], "stooq_daily_csv")
        self.assertEqual(
            manifest["etf_only_symbol_policy"]["allowlist_file"],
            "configs/universe/etf_universe.yaml",
        )
        self.assertTrue(manifest["etf_only_symbol_policy"]["reject_symbols_outside_allowlist"])
        self.assertFalse(manifest["broker_access_write_allowed"])
        self.assertFalse(manifest["automatic_trading_allowed"])
        self.assertFalse(manifest["stores_secret_values"])

        sources = {source["id"]: source for source in manifest["sources"]}
        self.assertIn("stooq_daily_csv", sources)
        self.assertIn("alpha_vantage_daily_adjusted", sources)
        self.assertIn("sec_edgar_metadata", sources)
        self.assertIn("yahoo_finance_manual_reference", sources)
        self.assertTrue(sources["stooq_daily_csv"]["selected_for_stage3b"])
        self.assertTrue(sources["stooq_daily_csv"]["read_only"])
        self.assertTrue(sources["stooq_daily_csv"]["public_data"])
        self.assertFalse(sources["stooq_daily_csv"]["requires_secret"])
        self.assertFalse(sources["alpha_vantage_daily_adjusted"]["selected_for_stage3b"])
        self.assertTrue(sources["alpha_vantage_daily_adjusted"]["requires_secret"])

    def test_stage3a_internal_review_records_pass_without_chatgpt_or_feishu(self) -> None:
        review = read_json("reports/internal_reviews/stage3a_data_source_codex_self_review.json")
        self.assertEqual(review["stage"], STAGE)
        self.assertEqual(review["review_mode"], "codex_self_review")
        self.assertEqual(review["status"], "passed")
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["sent_to_chatgpt"])
        self.assertFalse(review["feishu_message_sent"])
        self.assertFalse(review["computer_use_executed"])
        self.assertFalse(review["broker_surface"])
        self.assertFalse(review["auto_trading_surface"])
        self.assertFalse(review["secret_values_written"])
        self.assertIn("docs/stage3a_data_source_plan.md", review["reviewed_files"])

        text = read("reports/internal_reviews/stage3a_data_source_codex_self_review.md")
        self.assertIn("Codex self-review", text)
        self.assertIn("No ChatGPT review requested", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_stage3a_updates_stage_manifest_task_handoff_and_loop_state(self) -> None:
        task = read("ops/tasks/stage3a_data_source.md")
        self.assertIn("status: completed", task)
        self.assertIn("stage: Stage 3A completed_internal_review", task)
        self.assertIn("docs/stage3a_data_source_plan.md", task)
        self.assertIn("reports/internal_reviews/stage3a_data_source_codex_self_review.md", task)

        manifest = read("ops/stages/stage3.yaml")
        self.assertIn("id: stage3a_data_source", manifest)
        self.assertIn("status: completed", manifest)
        self.assertIn("id: stage3b_data_quality", manifest)
        self.assertIn("status: stage3f_major_gate_feishu_notification_sent", manifest)

        loop_state = read_json("ops/state/loop_state.json")
        self.assertIn(
            loop_state["current_stage"],
            {
                STAGE,
                "Stage 3B data quality checks completed",
                "Stage 3B completed_internal_review",
                "Stage 3C completed_internal_review",
                "Stage 3D completed_internal_review",
                "Stage 3E major_review_package_ready",
                "Stage 3F major_gate_feishu_notification_sent",
            },
        )
        self.assertEqual(loop_state["stage3a_task_status"], "completed_internal_review")
        self.assertIn(
            loop_state["stage3_next_task"],
            {
                "ops/tasks/stage3b_data_quality.md",
                "ops/tasks/stage3c_backtest_validation.md",
                "ops/tasks/stage3d_strategy_evidence_report.md",
                "ops/tasks/stage3_major_review_package.md",
                None,
            },
        )
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertTrue(loop_state["current_stage_feishu_message_sent"])
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])
        self.assertFalse(loop_state["auto_trading_surface"])
        self.assertFalse(loop_state["broker_surface"])


if __name__ == "__main__":
    unittest.main()

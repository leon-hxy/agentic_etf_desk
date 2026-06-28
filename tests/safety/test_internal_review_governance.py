import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_DIR = ROOT / "reports" / "internal_reviews" / "stage3"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class InternalReviewGovernanceTest(unittest.TestCase):
    def assert_common_review_contract(self, review: dict, minor_stage: str, task_file: str) -> None:
        self.assertEqual(review["minor_stage"], minor_stage)
        self.assertEqual(review["task_file"], task_file)
        self.assertEqual(review["status"], "completed_internal_review")
        self.assertIsInstance(review["builder_summary"], str)
        self.assertTrue(review["builder_summary"])
        self.assertIsInstance(review["changed_files"], list)
        self.assertTrue(review["changed_files"])

        for section in (
            "security_reviewer",
            "domain_reviewer",
            "integration_reviewer",
            "test_reviewer",
        ):
            self.assertIn(section, review)
            self.assertEqual(review[section]["result"], "pass", section)

        security = review["security_reviewer"]
        self.assertFalse(security["secrets_touched"])
        self.assertFalse(security["real_config_modified"])
        self.assertFalse(security["auto_trading_surface"])
        self.assertFalse(security["broker_write_surface"])

        self.assertFalse(review["requires_user_attention"])
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["computer_use_executed"])
        self.assertFalse(review["feishu_message_sent"])

    def test_stage3a_internal_review_artifacts_exist_and_pass(self) -> None:
        md_path = REVIEW_DIR / "stage3a_data_source.md"
        json_path = REVIEW_DIR / "stage3a_data_source.json"
        self.assertTrue(md_path.exists())
        self.assertTrue(json_path.exists())

        review = read_json(json_path)
        self.assert_common_review_contract(
            review,
            minor_stage="Stage 3A",
            task_file="ops/tasks/stage3a_data_source.md",
        )
        self.assertTrue(review["promote_to_next_minor_stage"])
        self.assertTrue(review["security_reviewer"]["public_repo_hygiene_passed"])
        self.assertTrue(review["domain_reviewer"]["etf_only_maintained"])
        self.assertTrue(review["domain_reviewer"]["read_only_public_data"])
        self.assertTrue(review["domain_reviewer"]["terms_and_license_caveat_documented"])
        for source in ("Yahoo", "Stooq", "Alpha Vantage", "SEC"):
            self.assertIn(source, review["domain_reviewer"]["source_use_and_limits"])

        text = md_path.read_text(encoding="utf-8")
        self.assertIn("completed_internal_review", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_stage3b_internal_review_artifacts_exist_and_pass(self) -> None:
        md_path = REVIEW_DIR / "stage3b_data_quality.md"
        json_path = REVIEW_DIR / "stage3b_data_quality.json"
        self.assertTrue(md_path.exists())
        self.assertTrue(json_path.exists())

        review = read_json(json_path)
        self.assert_common_review_contract(
            review,
            minor_stage="Stage 3B",
            task_file="ops/tasks/stage3b_data_quality.md",
        )
        self.assertTrue(review["promote_to_next_minor_stage"])
        self.assertEqual(review["next_minor_stage"], "Stage 3C backtest validation")
        domain = review["domain_reviewer"]
        self.assertTrue(domain["missing_values_covered"])
        self.assertTrue(domain["etf_start_dates_covered"])
        self.assertTrue(domain["adjusted_prices_covered"])
        self.assertTrue(domain["abnormal_prices_covered"])
        self.assertTrue(domain["sample_real_data_boundary_clear"])
        self.assertTrue(domain["sample_smoke_not_investment_basis"])

        text = md_path.read_text(encoding="utf-8")
        self.assertIn("completed_internal_review", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_stage3d_internal_review_artifacts_exist_and_pass(self) -> None:
        md_path = REVIEW_DIR / "stage3d_strategy_evidence_report.md"
        json_path = REVIEW_DIR / "stage3d_strategy_evidence_report.json"
        self.assertTrue(md_path.exists())
        self.assertTrue(json_path.exists())

        review = read_json(json_path)
        self.assert_common_review_contract(
            review,
            minor_stage="Stage 3D",
            task_file="ops/tasks/stage3d_strategy_evidence_report.md",
        )
        self.assertTrue(review["promote_to_next_minor_stage"])
        self.assertEqual(review["next_minor_stage"], "Stage 3E major review package")
        self.assertEqual(
            review["evidence_report"],
            "reports/strategy_evidence/stage3d_strategy_evidence_report.json",
        )
        domain = review["domain_reviewer"]
        self.assertTrue(domain["strategy_coverage_complete"])
        self.assertTrue(domain["benchmark_comparison_complete"])
        self.assertTrue(domain["sample_data_boundary_clear"])
        self.assertTrue(domain["sample_evidence_not_investment_basis"])
        self.assertTrue(domain["manual_trading_notice_present"])

        text = md_path.read_text(encoding="utf-8")
        self.assertIn("completed_internal_review", text)
        self.assertIn("Stage 3D Strategy Evidence Report", text)
        self.assertIn("Final trading is manually decided by the user", text)


if __name__ == "__main__":
    unittest.main()

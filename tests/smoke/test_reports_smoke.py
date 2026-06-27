import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUAL_NOTE = "这是研究建议，不是自动下单，最终交易由用户手动决定。"


class ReportsSmokeTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_stage2b_report_scripts_generate_manual_outputs(self) -> None:
        setup = self.run_cmd(
            [
                "scripts/backtest/run_backtest.py",
                "--strategies",
                "benchmark_buy_hold,static_6040,gtaa_10m_sma,dual_momentum",
            ]
        )
        self.assertEqual(setup.returncode, 0, msg=setup.stdout + setup.stderr)

        commands = [
            "scripts/reports/generate_market_brief.py",
            "scripts/reports/generate_weekly_report.py",
            "scripts/reports/generate_rebalance_ticket.py",
            "scripts/reports/generate_portfolio_journal.py",
        ]
        for command in commands:
            result = self.run_cmd([command])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        output_paths = [
            "reports/stage2b_market_brief.md",
            "reports/stage2b_weekly_report.md",
            "reports/stage2b_rebalance_ticket.md",
            "journals/stage2b_portfolio_journal.md",
        ]
        for rel in output_paths:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("风险等级", text, rel)
            self.assertIn("本地报告路径", text, rel)
            self.assertIn("最终交易由用户手动决定", text, rel)

    def test_trade_ticket_and_journal_templates_include_required_sections(self) -> None:
        ticket = (ROOT / "reports" / "trade_ticket_template.md").read_text(encoding="utf-8")
        for section in (
            "标的",
            "当前权重",
            "建议目标权重",
            "调整方向",
            "策略依据",
            "回测依据",
            "风险点",
            "失效条件",
            "人工确认项",
        ):
            self.assertIn(section, ticket)
        self.assertIn(MANUAL_NOTE, ticket)

        journal = (ROOT / "journals" / "portfolio_journal_template.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("组合复盘", journal)
        self.assertIn("最终交易由用户手动决定", journal)

    def test_rebalance_ticket_json_records_risk_review(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_rebalance_ticket.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads((ROOT / "reports" / "stage2b_rebalance_ticket.json").read_text())
        self.assertTrue(payload["risk_agent_review"]["passed"])
        self.assertIn("research advice", payload["manual_execution_note"])


if __name__ == "__main__":
    unittest.main()

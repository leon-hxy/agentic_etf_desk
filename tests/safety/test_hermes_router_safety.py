import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROUTER_FILES = [
    "configs/hermes/trading_desk_router_skill.md",
    "configs/hermes/feishu_router_draft.md",
    "configs/hermes/README.md",
]
SUPPORTED_COMMANDS = [
    "今天 ETF 有什么信号？",
    "跑一下 GTAA 回测",
    "生成本月 ETF 再平衡建议",
    "检查 ETF universe 有没有异常",
    "生成周报",
]


class HermesRouterSafetyTest(unittest.TestCase):
    def test_hermes_router_drafts_exist(self) -> None:
        for rel in ROUTER_FILES:
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_hermes_router_is_repo_only_and_feishu_safe(self) -> None:
        combined = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in ROUTER_FILES)
        self.assertIn("Hermes 是唯一总助理", combined)
        self.assertIn("不修改真实 ~/.hermes", combined)
        self.assertIn("不修改真实飞书 gateway", combined)
        self.assertIn("最终交易由用户手动决定", combined)
        self.assertIn("Computer Use 未真实执行", combined)
        self.assertNotIn("doctor --fix", combined)

        for command in SUPPORTED_COMMANDS:
            self.assertIn(command, combined)

    def test_hermes_router_mentions_only_safe_repo_entrypoints(self) -> None:
        combined = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in ROUTER_FILES)
        safe_entrypoints = [
            "scripts/data/validate_universe.py",
            "scripts/backtest/run_backtest.py",
            "scripts/reports/generate_market_brief.py",
            "scripts/reports/generate_weekly_report.py",
            "scripts/reports/generate_rebalance_ticket.py",
        ]
        for entrypoint in safe_entrypoints:
            self.assertIn(entrypoint, combined)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROUTER_PATH = ROOT / "scripts" / "hermes" / "feishu_command_router.py"
MANUAL_NOTE = "最终交易由用户手动决定"
BROKER_ACCESS_FIELD = "_".join(("broker", "write", "access"))


def load_router():
    spec = importlib.util.spec_from_file_location("feishu_command_router", ROUTER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Stage4WP1FeishuCommandRouterTest(unittest.TestCase):
    def test_supported_commands_return_repo_only_route_plans(self) -> None:
        router = load_router()
        expected = {
            "今天 ETF 有什么信号？": "market_brief",
            "跑一下 GTAA 回测": "gtaa_backtest",
            "生成本月 ETF 再平衡建议": "monthly_rebalance_research_ticket",
            "检查 ETF universe 有没有异常": "universe_health_check",
            "生成周报": "weekly_report",
        }

        for text, command_id in expected.items():
            with self.subTest(text=text):
                plan = router.route_command(text)
                self.assertEqual(plan["status"], "routed")
                self.assertEqual(plan["command_id"], command_id)
                self.assertEqual(plan["asset_scope"], "ETF-only")
                self.assertTrue(plan["repo_only"])
                self.assertFalse(plan["executes_live_feishu"])
                self.assertFalse(plan["modifies_real_runtime_config"])
                self.assertFalse(plan["automatic_trading"])
                self.assertFalse(plan[BROKER_ACCESS_FIELD])
                self.assertIn("scripts/", plan["repo_entrypoint"])
                self.assertIn(MANUAL_NOTE, plan["feishu_reply_preview"])
                self.assertIn("本地报告路径", plan["feishu_reply_preview"])
                self.assertTrue(plan["risk_agent_review_required_for_trade_tickets"])

    def test_unsafe_or_unknown_commands_are_rejected_without_entrypoint(self) -> None:
        router = load_router()
        rejected_texts = [
            "帮我自动下单买入 VTI",
            "连接券商账户并提交订单",
            "买入 AAPL 股票",
            "做 BTC 交易",
            "买入 TQQQ 杠杆 ETF",
            "生成期权交易建议",
            "删除真实 Feishu gateway 配置",
            "随便聊一下",
        ]

        for text in rejected_texts:
            with self.subTest(text=text):
                plan = router.route_command(text)
                self.assertEqual(plan["status"], "rejected")
                self.assertNotIn("repo_entrypoint", plan)
                self.assertFalse(plan["automatic_trading"])
                self.assertFalse(plan[BROKER_ACCESS_FIELD])
                self.assertFalse(plan["modifies_real_runtime_config"])
                self.assertIn(MANUAL_NOTE, plan["feishu_reply_preview"])

    def test_cli_outputs_json_without_running_live_feishu(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROUTER_PATH),
                "--text",
                "今天 ETF 有什么信号？",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "routed")
        self.assertEqual(payload["command_id"], "market_brief")
        self.assertFalse(payload["executes_live_feishu"])
        self.assertIn(MANUAL_NOTE, payload["feishu_reply_preview"])


if __name__ == "__main__":
    unittest.main()

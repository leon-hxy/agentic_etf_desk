import csv
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "data"))

import download_prices  # noqa: E402
from load_universe import allowed_symbols  # noqa: E402


STOOQ_SAMPLE = """Date,Open,High,Low,Close,Volume
2024-01-02,100.00,101.00,99.00,100.50,1000
2024-01-03,101.00,102.00,100.00,101.50,1200
2024-01-04,102.00,103.00,101.00,102.50,1300
"""

YAHOO_SAMPLE = json.dumps(
    {
        "chart": {
            "result": [
                {
                    "meta": {
                        "symbol": "VTI",
                        "instrumentType": "ETF",
                        "currency": "USD",
                    },
                    "timestamp": [1704153600, 1704240000, 1704326400],
                    "indicators": {
                        "quote": [{"close": [100.0, 101.0, 102.0]}],
                        "adjclose": [{"adjclose": [99.5, 100.5, 101.5]}],
                    },
                }
            ],
            "error": None,
        }
    }
)


class Stage31Wp1RealDataIngestionTest(unittest.TestCase):
    def test_stooq_ingestion_rejects_symbols_outside_universe_before_fetch(self) -> None:
        calls: list[str] = []

        def fetcher(symbol: str, _url: str) -> str:
            calls.append(symbol)
            return STOOQ_SAMPLE

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with self.assertRaisesRegex(ValueError, "not allowed by universe"):
                download_prices.write_outputs(
                    source="stooq_daily_csv",
                    symbols="AAPL",
                    start=date(2024, 1, 2),
                    end=date(2024, 1, 4),
                    raw_csv=tmp_path / "prices.csv",
                    metadata_json=tmp_path / "metadata.json",
                    cache_dir=tmp_path / "cache",
                    cache_manifest_json=tmp_path / "cache" / "manifest.json",
                    as_of_date=date(2024, 1, 5),
                    fetcher=fetcher,
                )

        self.assertEqual(calls, [])

    def test_stooq_ingestion_writes_cache_normalized_prices_and_provenance(self) -> None:
        fetched: list[str] = []

        def fetcher(symbol: str, _url: str) -> str:
            fetched.append(symbol)
            return STOOQ_SAMPLE

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            metadata = download_prices.write_outputs(
                source="stooq_daily_csv",
                symbols="VTI,BND",
                start=date(2024, 1, 2),
                end=date(2024, 1, 4),
                raw_csv=tmp_path / "prices.csv",
                metadata_json=tmp_path / "metadata.json",
                cache_dir=tmp_path / "cache",
                cache_manifest_json=tmp_path / "cache" / "manifest.json",
                as_of_date=date(2024, 1, 5),
                fetcher=fetcher,
            )

            with (tmp_path / "prices.csv").open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            cache_files = sorted((tmp_path / "cache").glob("*.csv"))
            manifest = json.loads((tmp_path / "cache" / "manifest.json").read_text())

        self.assertEqual(fetched, ["VTI", "BND"])
        self.assertEqual(metadata["source"], "stooq_daily_csv")
        self.assertEqual(metadata["symbols"], ["VTI", "BND"])
        self.assertEqual(metadata["universe_file"], "configs/universe/etf_universe.yaml")
        self.assertEqual(metadata["public_data_source"], "Stooq daily CSV")
        self.assertTrue(metadata["read_only_public_source"])
        self.assertFalse(metadata["requires_secret"])
        self.assertFalse(metadata["broker_surface"])
        self.assertEqual(metadata["cache_manifest_file"], str(tmp_path / "cache" / "manifest.json"))
        self.assertEqual(len(cache_files), 2)
        self.assertEqual(manifest["source"], "stooq_daily_csv")
        self.assertEqual(manifest["symbols"], ["VTI", "BND"])
        self.assertTrue(all(item["cache_sha256"] for item in manifest["cache_entries"]))
        self.assertEqual({row["symbol"] for row in rows}, {"VTI", "BND"})
        self.assertEqual(rows[0]["source"], "stooq_daily_csv")
        self.assertEqual(rows[0]["adjusted_close"], "100.5000")
        self.assertEqual(rows[0]["total_return_index"], "100.0000")

    def test_stooq_cache_reuse_skips_network_for_existing_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cache_dir = tmp_path / "cache"

            download_prices.write_outputs(
                source="stooq_daily_csv",
                symbols="VTI",
                start=date(2024, 1, 2),
                end=date(2024, 1, 4),
                raw_csv=tmp_path / "first.csv",
                metadata_json=tmp_path / "first.json",
                cache_dir=cache_dir,
                cache_manifest_json=cache_dir / "manifest.json",
                as_of_date=date(2024, 1, 5),
                fetcher=lambda _symbol, _url: STOOQ_SAMPLE,
            )

            def failing_fetcher(_symbol: str, _url: str) -> str:
                raise AssertionError("cache reuse should not fetch")

            metadata = download_prices.write_outputs(
                source="stooq_daily_csv",
                symbols="VTI",
                start=date(2024, 1, 2),
                end=date(2024, 1, 4),
                raw_csv=tmp_path / "second.csv",
                metadata_json=tmp_path / "second.json",
                cache_dir=cache_dir,
                cache_manifest_json=cache_dir / "manifest.json",
                as_of_date=date(2024, 1, 5),
                fetcher=failing_fetcher,
            )

        self.assertEqual(metadata["cache_entries"][0]["cache_status"], "hit")

    def test_yahoo_chart_public_ingestion_writes_real_cache_shape(self) -> None:
        fetched: list[str] = []

        def fetcher(symbol: str, _url: str) -> str:
            fetched.append(symbol)
            return YAHOO_SAMPLE

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            metadata = download_prices.write_outputs(
                source="yahoo_chart_public",
                symbols="VTI",
                start=date(2024, 1, 2),
                end=date(2024, 1, 4),
                raw_csv=tmp_path / "prices.csv",
                metadata_json=tmp_path / "metadata.json",
                cache_dir=tmp_path / "cache",
                cache_manifest_json=tmp_path / "cache" / "manifest.json",
                as_of_date=date(2024, 1, 5),
                fetcher=fetcher,
            )

            with (tmp_path / "prices.csv").open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            manifest = json.loads((tmp_path / "cache" / "manifest.json").read_text())

        self.assertEqual(fetched, ["VTI"])
        self.assertEqual(metadata["source"], "yahoo_chart_public")
        self.assertEqual(metadata["public_data_source"], "Yahoo Chart public JSON")
        self.assertEqual(metadata["symbols"], ["VTI"])
        self.assertTrue(metadata["read_only_public_source"])
        self.assertFalse(metadata["requires_secret"])
        self.assertFalse(metadata["broker_surface"])
        self.assertEqual(manifest["source"], "yahoo_chart_public")
        self.assertEqual(rows[0]["source"], "yahoo_chart_public")
        self.assertEqual(rows[0]["adjusted_close"], "99.5000")
        self.assertEqual(rows[0]["total_return_index"], "100.0000")

    def test_committed_real_data_metadata_uses_only_universe_symbols(self) -> None:
        metadata_path = ROOT / "data" / "raw" / "prices_yahoo_chart_metadata.json"
        self.assertTrue(metadata_path.exists())
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        allowed = set(allowed_symbols())

        self.assertEqual(payload["source"], "yahoo_chart_public")
        self.assertEqual(payload["universe_file"], "configs/universe/etf_universe.yaml")
        self.assertTrue(set(payload["symbols"]).issubset(allowed))
        self.assertFalse(payload["unknown_symbols"])
        self.assertTrue(payload["read_only_public_source"])
        self.assertFalse(payload["requires_secret"])
        self.assertFalse(payload["broker_surface"])

    def test_latest_artifacts_are_wp1_internal_review_only(self) -> None:
        handoff = json.loads((ROOT / "reports" / "codex_handoff" / "latest.json").read_text())
        review_request = json.loads((ROOT / "reports" / "review_requests" / "latest.json").read_text())
        latest_md = (ROOT / "reports" / "codex_handoff" / "latest.md").read_text()

        self.assertEqual(handoff["review_target"], "Stage 3.1 WP1 real data ingestion and cache")
        self.assertEqual(review_request["review_target"], "Stage 3.1 WP1 real data ingestion and cache")
        self.assertEqual(handoff["current_work_package"], "WP1 real data ingestion and cache")
        self.assertFalse(handoff["chatgpt_review_requested"])
        self.assertFalse(review_request["chatgpt_review_requested"])
        self.assertFalse(handoff["sent_to_chatgpt"])
        self.assertFalse(review_request["sent_to_chatgpt"])
        self.assertNotIn("manual_chatgpt_review_prompt", handoff)
        self.assertNotIn("manual_chatgpt_review_prompt", review_request)
        self.assertNotIn("stage/stage3-data-backtest", latest_md)

    def test_wp1_internal_review_has_required_reviewer_conclusions(self) -> None:
        review_json = ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp1_real_data_ingestion_and_cache.json"
        review_md = ROOT / "reports" / "internal_reviews" / "stage3_1" / "wp1_real_data_ingestion_and_cache.md"
        self.assertTrue(review_json.exists())
        self.assertTrue(review_md.exists())

        payload = json.loads(review_json.read_text(encoding="utf-8"))
        self.assertEqual(payload["work_package_id"], "wp1_real_data_ingestion_and_cache")
        self.assertEqual(payload["decision"], "passed")
        self.assertFalse(payload["chatgpt_review_requested"])
        self.assertFalse(payload["user_notification_sent"])
        self.assertEqual(payload["reviewers"]["security"]["result"], "passed")
        self.assertEqual(payload["reviewers"]["domain"]["result"], "passed")
        self.assertEqual(payload["reviewers"]["integration"]["result"], "passed")
        self.assertEqual(payload["reviewers"]["test"]["result"], "passed")

        text = review_md.read_text(encoding="utf-8")
        self.assertIn("Security reviewer: passed", text)
        self.assertIn("Domain reviewer: passed", text)
        self.assertIn("Integration reviewer: passed", text)
        self.assertIn("Test reviewer: passed", text)
        self.assertIn("Final trading is manually decided by the user", text)


if __name__ == "__main__":
    unittest.main()

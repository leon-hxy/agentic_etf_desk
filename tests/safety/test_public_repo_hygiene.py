import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PublicRepoHygieneTest(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "scripts/safety/check_public_repo_hygiene.py",
                "--root",
                str(root),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_public_repo_hygiene_passes(self) -> None:
        result = self.run_script(ROOT)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")

    def test_public_repo_hygiene_detects_private_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.md").write_text(
                "local path: /" + "Users" + "/example/.tool\npid: 12345\n",
                encoding="utf-8",
            )
            result = self.run_script(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        reasons = {finding["reason"] for finding in payload["findings"]}
        self.assertIn("absolute user path", reasons)
        self.assertIn("real pid line", reasons)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_publication.py"
SPEC = importlib.util.spec_from_file_location("check_publication", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PublicationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "content" / "drafts").mkdir(parents=True)
        (self.root / "content" / "ready").mkdir(parents=True)
        (self.root / "content" / "drafts" / "article.md").write_text(
            "# Draft\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_ready(self, body: str) -> Path:
        path = self.root / "content" / "ready" / "article.md"
        path.write_text(body, encoding="utf-8")
        return path

    def valid_text(self) -> str:
        return """# Final title

> Status: Ready
> Prepared: 2026-08-19
> Target: WeChat Official Account
> Source Draft: [Draft](../drafts/article.md)
> User Approval: 2026-08-19
> Publication Check: Passed

Final body.
"""

    def test_valid_ready_file_passes(self) -> None:
        path = self.write_ready(self.valid_text())
        self.assertEqual([], MODULE.validate_ready_file(self.root, path))

    def test_missing_user_approval_fails(self) -> None:
        path = self.write_ready(
            self.valid_text().replace("> User Approval: 2026-08-19\n", "")
        )
        self.assertIn(
            "缺少元数据：User Approval",
            MODULE.validate_ready_file(self.root, path),
        )

    def test_unresolved_marker_and_local_path_fail(self) -> None:
        path = self.write_ready(
            self.valid_text() + "\n[待核实] See D:\\private\\notes.md\n"
        )
        errors = MODULE.validate_ready_file(self.root, path)
        self.assertTrue(any("待核实" in error for error in errors))
        self.assertTrue(any("本地绝对路径" in error for error in errors))

    def test_unc_and_posix_local_paths_fail(self) -> None:
        local_paths = (
            r"\\server\private-share\notes.md",
            "/home/user/private-notes.md",
        )
        for local_path in local_paths:
            with self.subTest(local_path=local_path):
                path = self.write_ready(self.valid_text() + f"\nSee {local_path}\n")
                errors = MODULE.validate_ready_file(self.root, path)
                self.assertTrue(any("本地绝对路径" in error for error in errors))

    def test_missing_source_draft_fails(self) -> None:
        path = self.write_ready(
            self.valid_text().replace("article.md", "missing.md")
        )
        self.assertTrue(
            any("Source Draft 不存在" in error for error in MODULE.validate_ready_file(self.root, path))
        )


if __name__ == "__main__":
    unittest.main()

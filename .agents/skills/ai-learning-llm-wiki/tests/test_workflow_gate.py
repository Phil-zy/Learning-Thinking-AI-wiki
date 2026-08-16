import subprocess
import sys
import tempfile
import unittest
import hashlib
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = SKILL_ROOT / "scripts" / "check_workflow.py"
FINALIZE_SCRIPT = SKILL_ROOT / "scripts" / "finalize_ingest.py"


class WorkflowGateCliTests(unittest.TestCase):
    def run_check(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), str(root), *args],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def run_finalize(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(FINALIZE_SCRIPT), str(root), *args],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def test_repository_rejects_noncanonical_raw_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw" / "topic").mkdir(parents=True)
            (root / "wiki").mkdir()
            (root / "wiki" / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
            (root / "wiki" / "log.md").write_text("# Wiki Log\n", encoding="utf-8")
            (root / "raw" / "topic" / "bad.md").write_text(
                "# Source\n\n- **来源**: example\n- **发布时间**: 2026-08-10\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RAW_METADATA", result.stdout)

    def test_repository_accepts_optional_fields_in_raw_metadata_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw" / "topic").mkdir(parents=True)
            (root / "wiki").mkdir()
            (root / "wiki" / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
            (root / "wiki" / "log.md").write_text("# Wiki Log\n", encoding="utf-8")
            (root / "raw" / "topic" / "source.md").write_text(
                "# Source\n\n"
                "> Source: local\n"
                "> Author: Example\n"
                "> Collected: 2026-08-10\n"
                "> Published: Unknown\n"
                "> media_id: example\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_rejects_pending_review_with_logged_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "wiki").mkdir()
            (root / "reviews").mkdir()
            (root / "wiki" / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
            (root / "wiki" / "log.md").write_text(
                "# Wiki Log\n\n"
                "## [2026-08-10] ingest | Example\n"
                "- Batch: batch-a\n",
                encoding="utf-8",
            )
            (root / "reviews" / "batch-a.md").write_text(
                "# Ingest Review: Example\n\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Pending approval\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BATCH_STATE", result.stdout)

    def test_repository_rejects_logged_batch_without_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "wiki").mkdir()
            (root / "reviews").mkdir()
            (root / "wiki" / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
            (root / "wiki" / "log.md").write_text(
                "# Wiki Log\n\n"
                "## [2026-08-10] ingest | Example\n"
                "- Batch: missing-review\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BATCH_STATE", result.stdout)

    def test_repository_rejects_malformed_schema_one_pending_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "wiki").mkdir()
            (root / "reviews").mkdir()
            (root / "wiki" / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
            (root / "wiki" / "log.md").write_text("# Wiki Log\n", encoding="utf-8")
            (root / "reviews" / "batch-a.md").write_text(
                "# Ingest Review: Example\n\n"
                "> Workflow-Schema: 1\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Pending approval\n"
                "> Approved: —\n"
                "> Completed: —\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BATCH_FORMAT", result.stdout)

    def test_repository_rejects_approved_batch_without_approval_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "wiki").mkdir()
            (root / "reviews").mkdir()
            (root / "wiki" / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
            (root / "wiki" / "log.md").write_text("# Wiki Log\n", encoding="utf-8")
            (root / "reviews" / "batch-a.md").write_text(
                "# Ingest Review: Example\n\n"
                "> Workflow-Schema: 1\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Approved\n"
                "> Approved: —\n"
                "> Completed: —\n\n"
                "## Proposed Formal Wiki Changes\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BATCH_STATE", result.stdout)
            self.assertIn("Approved date", result.stdout)

    def test_repository_rejects_completed_batch_without_lint_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "wiki").mkdir()
            (root / "reviews").mkdir()
            (root / "wiki" / "index.md").write_text("# Knowledge Base Index\n", encoding="utf-8")
            (root / "wiki" / "log.md").write_text(
                "# Wiki Log\n\n"
                "## [2026-08-10] ingest | Example\n"
                "- Batch: batch-a\n",
                encoding="utf-8",
            )
            (root / "reviews" / "batch-a.md").write_text(
                "# Ingest Review: Example\n\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Completed\n"
                "> Approved: 2026-08-10\n"
                "> Completed: 2026-08-10\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("LINT_LOG", result.stdout)

    def test_repository_rechecks_completed_schema_one_target_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("raw/topic", "wiki/topic", "reviews"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "raw" / "topic" / "source.md").write_text(
                "# Source\n\n"
                "> Source: local\n"
                "> Collected: 2026-08-10\n"
                "> Published: Unknown\n\nSupported body.\n",
                encoding="utf-8",
            )
            target = root / "wiki" / "topic" / "page.md"
            target.write_text(
                "# Page\n\n"
                "> Sources: Local, 2026-08-10\n"
                "> Raw: [Source](../../raw/topic/source.md)\n"
                "> Updated: 2026-08-10\n\n"
                "## Overview\n\nChanged after completion.\n",
                encoding="utf-8",
            )
            (root / "wiki" / "index.md").write_text(
                "# Knowledge Base Index\n\n## topic\n\nDescription.\n\n"
                "| Article | Summary | Updated |\n|---|---|---|\n"
                "| [Page](topic/page.md) | Summary | 2026-08-10 |\n",
                encoding="utf-8",
            )
            (root / "wiki" / "log.md").write_text(
                "# Wiki Log\n\n"
                "## [2026-08-10] ingest | Page\n- Batch: batch-a\n\n"
                "## [2026-08-10] lint | 0 issues found, 0 auto-fixed\n- Batch: batch-a\n",
                encoding="utf-8",
            )
            (root / "reviews" / "batch-a.md").write_text(
                "# Ingest Review: Example\n\n"
                "> Workflow-Schema: 1\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Completed\n"
                "> Approved: 2026-08-10\n"
                "> Completed: 2026-08-10\n\n"
                "## Proposed Formal Wiki Changes\n\n"
                "| Target Wiki page | Action | Staging draft | Source files | Base state | Staging SHA-256 | Index summary |\n"
                "|---|---|---|---|---|---|---|\n"
                f"| [Page](../wiki/topic/page.md) | Update | [Page](../staging/topic/page.md) | `raw/topic/source.md` | SHA-256: `{'1' * 64}` | SHA-256: `{'0' * 64}` | Summary |\n",
                encoding="utf-8",
            )

            result = self.run_check(root, "--phase", "repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FORMAL_TARGET", result.stdout)

    def test_premerge_rejects_changed_formal_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("raw/topic", "staging/topic", "wiki/topic", "reviews"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            raw = root / "raw" / "topic" / "source.md"
            raw.write_text(
                "# Source\n\n"
                "> Source: local\n"
                "> Collected: 2026-08-10\n"
                "> Published: Unknown\n\n"
                "Supported body.\n",
                encoding="utf-8",
            )
            article = (
                "# Page\n\n"
                "> Sources: Local, 2026-08-10\n"
                "> Raw: [Source](../../raw/topic/source.md)\n"
                "> Updated: 2026-08-10\n\n"
                "## Overview\n\nSupported body.\n"
            )
            staging = root / "staging" / "topic" / "page.md"
            staging.write_text(article, encoding="utf-8")
            (root / "wiki" / "topic" / "page.md").write_text(
                article + "Unexpected concurrent edit.\n", encoding="utf-8"
            )
            staging_hash = hashlib.sha256(staging.read_bytes()).hexdigest().upper()
            review = root / "reviews" / "batch-a.md"
            review.write_text(
                "# Ingest Review: Example\n\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Approved\n"
                "> Approved: 2026-08-10\n"
                "> Completed: —\n\n"
                "## Proposed Formal Wiki Changes\n\n"
                "| Target Wiki page | Action | Staging draft | Source files | Base state | Staging SHA-256 | Index summary |\n"
                "|---|---|---|---|---|---|---|\n"
                f"| [Page](../wiki/topic/page.md) | Update | [Page](../staging/topic/page.md) | `raw/topic/source.md` | SHA-256: `{'0' * 64}` | SHA-256: `{staging_hash}` | Summary |\n",
                encoding="utf-8",
            )

            result = self.run_check(
                root, "--phase", "premerge", "--batch", "reviews/batch-a.md"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BASE_HASH", result.stdout)

    def test_postmerge_rejects_missing_lint_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("raw/topic", "wiki/topic", "reviews"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "raw" / "topic" / "source.md").write_text(
                "# Source\n\n"
                "> Source: local\n"
                "> Collected: 2026-08-10\n"
                "> Published: Unknown\n\n"
                "Supported body.\n",
                encoding="utf-8",
            )
            article = (
                "# Page\n\n"
                "> Sources: Local, 2026-08-10\n"
                "> Raw: [Source](../../raw/topic/source.md)\n"
                "> Updated: 2026-08-10\n\n"
                "## Overview\n\nSupported body.\n"
            )
            target = root / "wiki" / "topic" / "page.md"
            target.write_text(article, encoding="utf-8")
            target_hash = hashlib.sha256(target.read_bytes()).hexdigest().upper()
            (root / "wiki" / "index.md").write_text(
                "# Knowledge Base Index\n\n"
                "## topic\n\nDescription.\n\n"
                "| Article | Summary | Updated |\n"
                "|---|---|---|\n"
                "| [Page](topic/page.md) | Summary | 2026-08-10 |\n",
                encoding="utf-8",
            )
            (root / "wiki" / "log.md").write_text(
                "# Wiki Log\n\n"
                "## [2026-08-10] ingest | Page\n"
                "- Batch: batch-a\n",
                encoding="utf-8",
            )
            (root / "reviews" / "batch-a.md").write_text(
                "# Ingest Review: Example\n\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Completed\n"
                "> Approved: 2026-08-10\n"
                "> Completed: 2026-08-10\n\n"
                "## Proposed Formal Wiki Changes\n\n"
                "| Target Wiki page | Action | Staging draft | Source files | Base state | Staging SHA-256 | Index summary |\n"
                "|---|---|---|---|---|---|---|\n"
                f"| [Page](../wiki/topic/page.md) | Update | [Page](../staging/topic/page.md) | `raw/topic/source.md` | SHA-256: `{'0' * 64}` | SHA-256: `{target_hash}` | Summary |\n",
                encoding="utf-8",
            )

            result = self.run_check(
                root, "--phase", "postmerge", "--batch", "reviews/batch-a.md"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("LINT_LOG", result.stdout)

    def test_finalize_hash_conflict_preserves_target_and_staging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("raw/topic", "staging/topic", "wiki/topic", "reviews"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "raw" / "topic" / "source.md").write_text(
                "# Source\n\n"
                "> Source: local\n"
                "> Collected: 2026-08-10\n"
                "> Published: Unknown\n\n"
                "Supported body.\n",
                encoding="utf-8",
            )
            staging_text = (
                "# Page\n\n"
                "> Sources: Local, 2026-08-10\n"
                "> Raw: [Source](../../raw/topic/source.md)\n"
                "> Updated: 2026-08-10\n\n"
                "## Overview\n\nSupported body.\n"
            )
            staging = root / "staging" / "topic" / "page.md"
            staging.write_text(staging_text, encoding="utf-8")
            target = root / "wiki" / "topic" / "page.md"
            original_target = "# Concurrent edit\n"
            target.write_text(original_target, encoding="utf-8")
            staging_hash = hashlib.sha256(staging.read_bytes()).hexdigest().upper()
            (root / "reviews" / "batch-a.md").write_text(
                "# Ingest Review: Example\n\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Approved\n"
                "> Approved: 2026-08-10\n"
                "> Completed: —\n\n"
                "## Proposed Formal Wiki Changes\n\n"
                "| Target Wiki page | Action | Staging draft | Source files | Base state | Staging SHA-256 | Index summary |\n"
                "|---|---|---|---|---|---|---|\n"
                f"| [Page](../wiki/topic/page.md) | Update | [Page](../staging/topic/page.md) | `raw/topic/source.md` | SHA-256: `{'0' * 64}` | SHA-256: `{staging_hash}` | Summary |\n",
                encoding="utf-8",
            )

            result = self.run_finalize(root, "--batch", "reviews/batch-a.md")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BASE_HASH", result.stdout)
            self.assertTrue(staging.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), original_target)

    def test_finalize_completes_batch_and_rerun_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("raw/topic", "staging/topic", "wiki", "reviews"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "raw" / "topic" / "source.md").write_text(
                "# Source\n\n"
                "> Source: local\n"
                "> Collected: 2026-08-10\n"
                "> Published: Unknown\n\n"
                "Supported body.\n",
                encoding="utf-8",
            )
            article = (
                "# Page\n\n"
                "> Sources: Local, 2026-08-10\n"
                "> Raw: [Source](../../raw/topic/source.md)\n"
                "> Updated: 2026-08-10\n\n"
                "## Overview\n\nSupported body.\n"
            )
            staging = root / "staging" / "topic" / "page.md"
            staging.write_text(article, encoding="utf-8")
            staging_hash = hashlib.sha256(staging.read_bytes()).hexdigest().upper()
            (root / "wiki" / "index.md").write_text(
                "# Knowledge Base Index\n\n"
                "## topic\n\nDescription.\n\n"
                "| Article | Summary | Updated |\n"
                "|---|---|---|\n",
                encoding="utf-8",
            )
            (root / "wiki" / "log.md").write_text("# Wiki Log\n", encoding="utf-8")
            review = root / "reviews" / "batch-a.md"
            review.write_text(
                "# Ingest Review: Example\n\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Approved\n"
                "> Approved: 2026-08-10\n"
                "> Completed: —\n\n"
                "## Summary\n\n"
                "- Disposition: New 1; Update 0; No material 0; Disputed 0\n\n"
                "## Proposed Formal Wiki Changes\n\n"
                "| Target Wiki page | Action | Staging draft | Source files | Base state | Staging SHA-256 | Index summary |\n"
                "|---|---|---|---|---|---|---|\n"
                f"| [Page](../wiki/topic/page.md) | New | [Page](../staging/topic/page.md) | `raw/topic/source.md` | New target | SHA-256: `{staging_hash}` | Summary |\n",
                encoding="utf-8",
            )

            first = self.run_finalize(root, "--batch", "reviews/batch-a.md")

            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            target = root / "wiki" / "topic" / "page.md"
            self.assertEqual(target.read_text(encoding="utf-8"), article)
            self.assertFalse(staging.exists())
            self.assertIn("> Status: Completed", review.read_text(encoding="utf-8"))
            self.assertIn("[Page](topic/page.md)", (root / "wiki" / "index.md").read_text(encoding="utf-8"))
            log = (root / "wiki" / "log.md").read_text(encoding="utf-8")
            self.assertIn("ingest | Page", log)
            self.assertIn("lint |", log)
            self.assertGreaterEqual(log.count("- Batch: batch-a"), 2)
            self.assertLess(log.index("ingest | Page"), log.index("lint |"))
            repository_check = self.run_check(root, "--phase", "repository")
            self.assertEqual(
                repository_check.returncode,
                0,
                repository_check.stdout + repository_check.stderr,
            )
            snapshot = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }

            second = self.run_finalize(root, "--batch", "reviews/batch-a.md")

            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("already completed", second.stdout)
            self.assertEqual(
                snapshot,
                {
                    path.relative_to(root).as_posix(): path.read_bytes()
                    for path in root.rglob("*")
                    if path.is_file()
                },
            )

    def test_finalize_midway_failure_keeps_staging_and_marks_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("raw/topic", "staging/topic", "wiki", "reviews"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "raw" / "topic" / "source.md").write_text(
                "# Source\n\n"
                "> Source: local\n"
                "> Collected: 2026-08-10\n"
                "> Published: Unknown\n\nSupported body.\n",
                encoding="utf-8",
            )
            article = (
                "# Page\n\n"
                "> Sources: Local, 2026-08-10\n"
                "> Raw: [Source](../../raw/topic/source.md)\n"
                "> Updated: 2026-08-10\n\n"
                "## Overview\n\nSupported body.\n"
            )
            staging = root / "staging" / "topic" / "page.md"
            staging.write_text(article, encoding="utf-8")
            staging_hash = hashlib.sha256(staging.read_bytes()).hexdigest().upper()
            (root / "wiki" / "index.md").write_text(
                "# Knowledge Base Index\n\n"
                "## topic\n\nDescription.\n\n"
                "| Article | Summary | Updated |\n|---|---|---|\n",
                encoding="utf-8",
            )
            (root / "wiki" / "log.md").write_text("broken log heading\n", encoding="utf-8")
            review = root / "reviews" / "batch-a.md"
            review.write_text(
                "# Ingest Review: Example\n\n"
                "> Batch: batch-a\n"
                "> Created: 2026-08-10\n"
                "> Status: Approved\n"
                "> Approved: 2026-08-10\n"
                "> Completed: —\n\n"
                "## Proposed Formal Wiki Changes\n\n"
                "| Target Wiki page | Action | Staging draft | Source files | Base state | Staging SHA-256 | Index summary |\n"
                "|---|---|---|---|---|---|---|\n"
                f"| [Page](../wiki/topic/page.md) | New | [Page](../staging/topic/page.md) | `raw/topic/source.md` | New target | SHA-256: `{staging_hash}` | Summary |\n",
                encoding="utf-8",
            )

            result = self.run_finalize(root, "--batch", "reviews/batch-a.md")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MERGE_INCOMPLETE", result.stdout)
            self.assertTrue(staging.exists())
            self.assertTrue((root / "wiki" / "topic" / "page.md").exists())
            self.assertIn("> Status: Merge incomplete", review.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

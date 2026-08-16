#!/usr/bin/env python3
"""Finalize one explicitly approved wiki ingest batch."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from datetime import date
from pathlib import Path

from workflow_gate import (
    BatchReview,
    lint_findings,
    parse_batch,
    postmerge_findings,
    premerge_findings,
    render_index,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--batch", required=True)
    return parser.parse_args()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def update_review_state(path: Path, status: str, completed: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(
        r"(?m)^> Status: .+$", f"> Status: {status}", text, count=1
    )
    if count != 1:
        raise ValueError("review report has no Status field")
    if completed is not None:
        text, count = re.subn(
            r"(?m)^> Completed: .+$", f"> Completed: {completed}", text, count=1
        )
        if count != 1:
            raise ValueError("review report has no Completed field")
    atomic_write(path, text)


def add_log_section(log_path: Path, section: str) -> None:
    text = log_path.read_text(encoding="utf-8") if log_path.is_file() else "# Wiki Log\n"
    if section in text:
        return
    lines = text.splitlines()
    if not lines or lines[0] != "# Wiki Log":
        raise ValueError("wiki/log.md must start with # Wiki Log")
    remainder = "\n".join(lines[1:]).lstrip("\n")
    merged = "# Wiki Log\n\n" + section.rstrip() + "\n"
    if remainder:
        merged += "\n" + remainder + "\n"
    atomic_write(log_path, merged)


def add_lint_after_ingest(log_path: Path, batch_id: str, section: str) -> None:
    text = log_path.read_text(encoding="utf-8")
    batch_marker = f"- Batch: {batch_id}"
    lines = text.splitlines()
    for start, line in enumerate(lines):
        if not re.match(r"^## \[[^\]]+\] ingest \|", line):
            continue
        end = next(
            (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
            len(lines),
        )
        if batch_marker not in lines[start:end]:
            continue
        lines[end:end] = ["", *section.rstrip().splitlines()]
        atomic_write(log_path, "\n".join(lines) + "\n")
        return
    raise ValueError(f"cannot place lint log: ingest entry for {batch_id} is missing")


def ingest_section(root: Path, batch: BatchReview) -> str:
    action = "; ".join(dict.fromkeys(change.action for change in batch.changes))
    lines = [
        f"## [{date.today().isoformat()}] ingest | {batch.changes[0].title}",
        f"- Batch: {batch.batch_id}",
        f"- Disposition: {action}",
    ]
    sources: list[Path] = []
    for change in batch.changes:
        for source in change.sources:
            if source not in sources:
                sources.append(source)
    lines.extend(f"- Raw: {source.relative_to(root).as_posix()}" for source in sources)
    lines.extend(f"- Updated: {change.title}" for change in batch.changes)
    return "\n".join(lines)


def lint_section(batch: BatchReview, issue_count: int, orphan_count: int) -> str:
    return "\n".join(
        [
            f"## [{date.today().isoformat()}] lint | {issue_count} issues found, 0 auto-fixed",
            f"- Batch: {batch.batch_id}",
            f"- Mechanical and workflow findings: {issue_count - orphan_count}",
            f"- Judgment: {orphan_count} orphan pages",
        ]
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    batch_path = Path(args.batch)
    batch, parse_findings = parse_batch(root, batch_path)
    if parse_findings or batch is None:
        for finding in parse_findings:
            print(finding.render())
        return 1
    if batch.status == "Completed":
        findings = postmerge_findings(root, batch_path)
        if findings:
            for finding in findings:
                print(finding.render())
            return 1
        print(f"OK batch {batch.batch_id} already completed")
        return 0
    findings = premerge_findings(root, Path(args.batch))
    if findings:
        for finding in findings:
            print(finding.render())
        print("BLOCKED no files were changed")
        return 1
    index_text, index_findings = render_index(root, batch)
    if index_findings or index_text is None:
        for finding in index_findings:
            print(finding.render())
        print("BLOCKED no files were changed")
        return 1

    update_review_state(batch.path, "Merge incomplete")
    try:
        for change in batch.changes:
            atomic_write_bytes(change.target, change.staging.read_bytes())
        atomic_write(root / "wiki" / "index.md", index_text)
        add_log_section(root / "wiki" / "log.md", ingest_section(root, batch))

        lint_issues, orphans = lint_findings(root)
        issue_count = len(lint_issues) + len(orphans)
        add_lint_after_ingest(
            root / "wiki" / "log.md",
            batch.batch_id,
            lint_section(batch, issue_count, len(orphans)),
        )
        post_findings = postmerge_findings(root, batch_path)
        if post_findings:
            for finding in post_findings:
                print(finding.render())
            print("INCOMPLETE staging retained for safe retry")
            return 1

        update_review_state(batch.path, "Completed", date.today().isoformat())
        for change in batch.changes:
            change.staging.unlink()
        final_findings = postmerge_findings(root, batch_path)
        if final_findings:
            for finding in final_findings:
                print(finding.render())
            print("INCOMPLETE completion verification failed")
            return 1
    except Exception as error:
        print(f"MERGE_INCOMPLETE {error}")
        print("staging retained for safe retry")
        return 2
    print(f"OK completed batch {batch.batch_id}; lint issues: {issue_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

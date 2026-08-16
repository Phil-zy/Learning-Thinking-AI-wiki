#!/usr/bin/env python3
"""Workflow invariants shared by the wiki gate command-line tools."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import check_evidence


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.code} {self.path}: {self.message}"


@dataclass(frozen=True)
class Change:
    title: str
    action: str
    target: Path
    staging: Path
    sources: tuple[Path, ...]
    base_hash: str | None
    staging_hash: str
    index_summary: str


@dataclass(frozen=True)
class BatchReview:
    path: Path
    batch_id: str
    status: str
    approved: str | None
    completed: str | None
    changes: tuple[Change, ...]


def _metadata_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        title_index = next(index for index, line in enumerate(lines) if line.startswith("# "))
    except StopIteration:
        return []
    index = title_index + 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    metadata: list[str] = []
    while index < len(lines) and lines[index].startswith("> "):
        metadata.append(lines[index])
        index += 1
    return metadata


def raw_metadata_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    raw_root = root / "raw"
    if not raw_root.is_dir():
        return [Finding("RAW_METADATA", "raw", "raw/ directory is missing")]
    for path in sorted(raw_root.rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        metadata = _metadata_lines(path)
        parsed: dict[str, list[str]] = {}
        for line in metadata:
            key, separator, value = line.removeprefix("> ").partition(":")
            if separator:
                parsed.setdefault(key.strip(), []).append(value.strip())
        if any(len(parsed.get(key, [])) != 1 for key in ("Source", "Collected", "Published")):
            findings.append(
                Finding(
                    "RAW_METADATA",
                    relative,
                    "expected exactly one Source, Collected, and Published field in the metadata block after H1",
                )
            )
            continue
        source = parsed["Source"][0]
        collected = parsed["Collected"][0]
        published = parsed["Published"][0]
        if not source or not DATE_RE.fullmatch(collected) or not (
            published == "Unknown" or DATE_RE.fullmatch(published)
        ):
            findings.append(
                Finding(
                    "RAW_METADATA",
                    relative,
                    "Source must be non-empty and dates must use YYYY-MM-DD or Published: Unknown",
                )
            )
    return findings


def _blockquote_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in _metadata_lines(path):
        key, separator, value = line.removeprefix("> ").partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def _link_target(cell: str) -> str | None:
    match = re.search(r"\[[^\]]*\]\(([^)]+)\)", cell)
    return match.group(1) if match else None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def parse_batch(root: Path, batch_path: Path) -> tuple[BatchReview | None, list[Finding]]:
    path = batch_path if batch_path.is_absolute() else root / batch_path
    path = path.resolve()
    if not path.is_file():
        return None, [Finding("BATCH_FORMAT", str(batch_path), "review report does not exist")]
    fields = _blockquote_fields(path)
    batch_id = fields.get("Batch", "")
    status = fields.get("Status", "")
    findings: list[Finding] = []
    relative = path.relative_to(root).as_posix() if _inside(path, root) else str(path)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", batch_id):
        findings.append(Finding("BATCH_FORMAT", relative, "missing or invalid Batch field"))
    if status not in {"Pending approval", "Approved", "Merge incomplete", "Completed"}:
        findings.append(Finding("BATCH_FORMAT", relative, f"invalid Status: {status or '(missing)'}"))
    approved = fields.get("Approved", "")
    completed = fields.get("Completed", "")
    if status in {"Approved", "Merge incomplete", "Completed"} and not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", approved
    ):
        findings.append(
            Finding("BATCH_STATE", relative, f"{status} status requires an Approved date")
        )
    if status == "Completed" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", completed):
        findings.append(Finding("BATCH_STATE", relative, "Completed status requires a Completed date"))

    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        heading = lines.index("## Proposed Formal Wiki Changes")
    except ValueError:
        return None, findings + [
            Finding("BATCH_FORMAT", relative, "missing Proposed Formal Wiki Changes section")
        ]
    rows: list[list[str]] = []
    for line in lines[heading + 1 :]:
        if line.startswith("## "):
            break
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] != "Target Wiki page" and not all(
            re.fullmatch(r":?-+:?", cell) for cell in cells
        ):
            rows.append(cells)
    changes: list[Change] = []
    for row in rows:
        if len(row) != 7:
            findings.append(
                Finding("BATCH_FORMAT", relative, "change rows must contain exactly 7 columns")
            )
            continue
        target_link = _link_target(row[0])
        staging_link = _link_target(row[2])
        source_links = tuple(re.findall(r"`([^`]+\.md)`", row[3]))
        base_match = re.search(r"([A-Fa-f0-9]{64})", row[4])
        staging_match = re.search(r"([A-Fa-f0-9]{64})", row[5])
        if not target_link or not staging_link or not source_links or not staging_match:
            findings.append(Finding("BATCH_FORMAT", relative, "malformed change row"))
            continue
        target = (path.parent / target_link).resolve()
        staging = (path.parent / staging_link).resolve()
        sources = tuple((root / source).resolve() for source in source_links)
        if not _inside(target, root / "wiki") or not _inside(staging, root / "staging"):
            findings.append(Finding("BATCH_FORMAT", relative, "target or staging path escapes its root"))
            continue
        if any(not _inside(source, root / "raw") for source in sources):
            findings.append(Finding("BATCH_FORMAT", relative, "source path escapes raw/"))
            continue
        if row[4] != "New target" and not base_match:
            findings.append(Finding("BATCH_FORMAT", relative, "Base state must be New target or SHA-256"))
            continue
        changes.append(
            Change(
                title=re.sub(r"^\[|\]\([^)]+\)$", "", row[0]),
                action=row[1],
                target=target,
                staging=staging,
                sources=sources,
                base_hash=base_match.group(1).upper() if base_match else None,
                staging_hash=staging_match.group(1).upper(),
                index_summary=row[6],
            )
        )
    if not changes:
        findings.append(Finding("BATCH_FORMAT", relative, "no valid formal changes found"))
    if findings:
        return None, findings
    return (
        BatchReview(
            path=path,
            batch_id=batch_id,
            status=status,
            approved=approved,
            completed=completed,
            changes=tuple(changes),
        ),
        [],
    )


def premerge_findings(root: Path, batch_path: Path) -> list[Finding]:
    batch, findings = parse_batch(root, batch_path)
    if findings or batch is None:
        return findings
    relative = batch.path.relative_to(root).as_posix()
    if batch.status not in {"Approved", "Merge incomplete"}:
        findings.append(
            Finding("BATCH_STATE", relative, f"premerge requires Approved status, found {batch.status}")
        )
    findings.extend(raw_metadata_findings(root))
    for change in batch.changes:
        staging_rel = change.staging.relative_to(root).as_posix()
        target_rel = change.target.relative_to(root).as_posix()
        if not change.staging.is_file():
            findings.append(Finding("STAGING_MISSING", staging_rel, "approved staging draft is missing"))
            continue
        actual_staging_hash = _sha256(change.staging)
        if actual_staging_hash != change.staging_hash:
            findings.append(
                Finding(
                    "STAGING_HASH",
                    staging_rel,
                    f"expected {change.staging_hash}, found {actual_staging_hash}",
                )
            )
        misses, errors = check_evidence.check_article(change.staging, root)
        findings.extend(
            Finding("EVIDENCE_SUSPECT", staging_rel, miss) for miss in misses
        )
        findings.extend(
            Finding("EVIDENCE_ERROR", staging_rel, error) for error in errors
        )
        for source in change.sources:
            if not source.is_file():
                findings.append(
                    Finding("RAW_MISSING", source.relative_to(root).as_posix(), "source file is missing")
                )
        if change.base_hash is None:
            if change.target.exists() and _sha256(change.target) != actual_staging_hash:
                findings.append(Finding("BASE_HASH", target_rel, "New target already exists with different content"))
        elif not change.target.is_file():
            findings.append(Finding("BASE_HASH", target_rel, "formal target is missing"))
        else:
            actual_target_hash = _sha256(change.target)
            if actual_target_hash not in {change.base_hash, actual_staging_hash}:
                findings.append(
                    Finding(
                        "BASE_HASH",
                        target_rel,
                        f"expected baseline {change.base_hash}, found {actual_target_hash}",
                    )
                )
    return findings


def render_index(root: Path, batch: BatchReview) -> tuple[str | None, list[Finding]]:
    index_path = root / "wiki" / "index.md"
    if not index_path.is_file():
        return None, [Finding("INDEX_STATE", "wiki/index.md", "index file is missing")]
    text = index_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[Finding] = []
    for change in batch.changes:
        index_rel = change.target.relative_to(root / "wiki").as_posix()
        article_date = _article_date(change.staging)
        if not article_date:
            findings.append(
                Finding(
                    "INDEX_STATE",
                    change.staging.relative_to(root).as_posix(),
                    "staging draft has no Updated or Archived date",
                )
            )
            continue
        row_index = next(
            (
                index
                for index, line in enumerate(lines)
                if re.search(r"\]\(" + re.escape(index_rel) + r"\)", line)
            ),
            None,
        )
        if row_index is not None:
            lines[row_index] = re.sub(
                r"\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*$",
                f"| {article_date} |",
                lines[row_index],
            )
            continue
        topic = change.target.parent.name
        try:
            section_index = lines.index(f"## {topic}")
        except ValueError:
            findings.append(
                Finding(
                    "INDEX_STATE",
                    "wiki/index.md",
                    f"topic section {topic!r} is missing; add its description before finalizing",
                )
            )
            continue
        next_section = next(
            (index for index in range(section_index + 1, len(lines)) if lines[index].startswith("## ")),
            len(lines),
        )
        table_rows = [
            index
            for index in range(section_index + 1, next_section)
            if lines[index].startswith("|")
        ]
        if len(table_rows) < 2:
            findings.append(
                Finding("INDEX_STATE", "wiki/index.md", f"topic {topic!r} has no article table")
            )
            continue
        insert_at = table_rows[-1] + 1
        lines.insert(
            insert_at,
            f"| [{change.title}]({index_rel}) | {change.index_summary} | {article_date} |",
        )
    if findings:
        return None, findings
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), []


def _logged_batch_kinds(root: Path) -> dict[str, set[str]]:
    log_path = root / "wiki" / "log.md"
    if not log_path.is_file():
        return {}
    kinds: dict[str, set[str]] = {}
    current_kind: str | None = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^## \[[^\]]+\] (ingest|lint) \|", line)
        if heading:
            current_kind = heading.group(1)
            continue
        batch = re.match(r"^- Batch: ([A-Za-z0-9][A-Za-z0-9._-]*)\s*$", line)
        if batch and current_kind:
            kinds.setdefault(batch.group(1), set()).add(current_kind)
    return kinds


def _article_date(path: Path) -> str | None:
    match = re.search(
        r"(?m)^> (?:Updated|Archived): (\d{4}-\d{2}-\d{2})\s*$",
        path.read_text(encoding="utf-8"),
    )
    return match.group(1) if match else None


def postmerge_findings(root: Path, batch_path: Path) -> list[Finding]:
    batch, findings = parse_batch(root, batch_path)
    if findings or batch is None:
        return findings
    relative = batch.path.relative_to(root).as_posix()
    if batch.status not in {"Approved", "Merge incomplete", "Completed"}:
        findings.append(
            Finding("BATCH_STATE", relative, f"postmerge cannot inspect status {batch.status}")
        )
    if batch.status == "Completed" and (
        not batch.completed or batch.completed == "—"
    ):
        findings.append(Finding("BATCH_STATE", relative, "Completed status requires Completed date"))

    findings.extend(raw_metadata_findings(root))
    index_path = root / "wiki" / "index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    for change in batch.changes:
        target_rel = change.target.relative_to(root).as_posix()
        if not change.target.is_file():
            findings.append(Finding("FORMAL_TARGET", target_rel, "merged target is missing"))
            continue
        actual_hash = _sha256(change.target)
        if actual_hash != change.staging_hash:
            findings.append(
                Finding(
                    "FORMAL_TARGET",
                    target_rel,
                    f"expected approved staging hash {change.staging_hash}, found {actual_hash}",
                )
            )
        index_rel = change.target.relative_to(root / "wiki").as_posix()
        index_line = next(
            (
                line
                for line in index_text.splitlines()
                if re.search(r"\]\(" + re.escape(index_rel) + r"\)", line)
            ),
            None,
        )
        article_date = _article_date(change.target)
        if index_line is None:
            findings.append(Finding("INDEX_STATE", target_rel, "formal target is missing from wiki/index.md"))
        elif article_date and not re.search(rf"\|\s*{re.escape(article_date)}\s*\|\s*$", index_line):
            findings.append(Finding("INDEX_STATE", target_rel, "index date does not match article metadata"))
        if batch.status == "Completed" and change.staging.exists():
            findings.append(
                Finding(
                    "STAGING_CLEANUP",
                    change.staging.relative_to(root).as_posix(),
                    "completed batch still has an approved staging draft",
                )
            )

    kinds = _logged_batch_kinds(root).get(batch.batch_id, set())
    if "ingest" not in kinds:
        findings.append(Finding("INGEST_LOG", "wiki/log.md", f"missing ingest entry for {batch.batch_id}"))
    if "lint" not in kinds:
        findings.append(Finding("LINT_LOG", "wiki/log.md", f"missing lint entry for {batch.batch_id}"))
    return findings


def index_and_link_findings(root: Path) -> list[Finding]:
    wiki_root = root / "wiki"
    index_path = wiki_root / "index.md"
    if not index_path.is_file():
        return [Finding("INDEX_STATE", "wiki/index.md", "index file is missing")]
    index_text = index_path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    articles = list(check_evidence.iter_articles(wiki_root))
    for article in articles:
        relative = article.relative_to(wiki_root).as_posix()
        row = next(
            (
                line
                for line in index_text.splitlines()
                if re.search(r"\]\(" + re.escape(relative) + r"\)", line)
            ),
            None,
        )
        if row is None:
            findings.append(Finding("INDEX_STATE", relative, "article is missing from index"))
        else:
            date = _article_date(article)
            if date and not re.search(rf"\|\s*{re.escape(date)}\s*\|\s*$", row):
                findings.append(Finding("INDEX_STATE", relative, "index date does not match article"))
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", article.read_text(encoding="utf-8")):
            target_text = match.group(1).split("#", 1)[0]
            if not target_text or re.match(r"^(?:https?://|mailto:)", target_text):
                continue
            target = (article.parent / target_text).resolve()
            if not target.is_file():
                findings.append(
                    Finding("LINK_STATE", relative, f"broken link: {target_text}")
                )
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+\.md)\)", index_text):
        target = (wiki_root / match.group(1)).resolve()
        if not target.is_file():
            findings.append(
                Finding("INDEX_STATE", "wiki/index.md", f"missing target: {match.group(1)}")
            )
    return findings


def orphan_pages(root: Path) -> list[str]:
    wiki_root = root / "wiki"
    articles = list(check_evidence.iter_articles(wiki_root))
    inbound = {article.resolve(): 0 for article in articles}
    for article in articles:
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", article.read_text(encoding="utf-8")):
            target_text = match.group(1).split("#", 1)[0]
            if not target_text or re.match(r"^(?:https?://|mailto:)", target_text):
                continue
            target = (article.parent / target_text).resolve()
            if target in inbound:
                inbound[target] += 1
    return [
        article.relative_to(wiki_root).as_posix()
        for article in articles
        if inbound[article.resolve()] == 0
    ]


def lint_findings(root: Path) -> tuple[list[Finding], list[str]]:
    findings = index_and_link_findings(root)
    for article in check_evidence.iter_articles(root / "wiki"):
        misses, errors = check_evidence.check_article(article, root)
        relative = article.relative_to(root).as_posix()
        findings.extend(Finding("EVIDENCE_SUSPECT", relative, miss) for miss in misses)
        findings.extend(Finding("EVIDENCE_ERROR", relative, error) for error in errors)
    findings.extend(
        Finding("UNREFERENCED_RAW", path, "Raw file is not referenced by a formal article")
        for path in check_evidence.unreferenced_raws(root)
    )
    return findings, orphan_pages(root)


def batch_state_findings(root: Path) -> list[Finding]:
    reviews_root = root / "reviews"
    if not reviews_root.is_dir():
        return []
    logged_kinds = _logged_batch_kinds(root)
    findings: list[Finding] = []
    seen_batches: dict[str, Path] = {}
    for path in sorted(reviews_root.glob("*.md")):
        fields = _blockquote_fields(path)
        batch = fields.get("Batch")
        status = fields.get("Status")
        if not batch or not status:
            continue
        relative = path.relative_to(root).as_posix()
        if batch in seen_batches:
            findings.append(
                Finding(
                    "BATCH_STATE",
                    relative,
                    f"duplicate Batch ID also used by {seen_batches[batch].relative_to(root).as_posix()}",
                )
            )
        else:
            seen_batches[batch] = path
        schema_findings: list[Finding] = []
        if fields.get("Workflow-Schema") == "1":
            _, schema_findings = parse_batch(root, path.relative_to(root))
            findings.extend(schema_findings)
        kinds = logged_kinds.get(batch, set())
        if status == "Pending approval" and kinds:
            findings.append(
                Finding(
                    "BATCH_STATE",
                    relative,
                    f"batch {batch} is Pending approval but already appears in wiki/log.md",
                )
            )
        elif status == "Approved" and kinds:
            findings.append(
                Finding(
                    "BATCH_STATE",
                    relative,
                    f"batch {batch} has merge logs but is not Merge incomplete or Completed",
                )
            )
        elif status == "Approved" and not schema_findings and fields.get("Workflow-Schema") == "1":
            findings.extend(premerge_findings(root, path.relative_to(root)))
        elif status == "Merge incomplete":
            findings.append(
                Finding(
                    "BATCH_STATE",
                    relative,
                    f"batch {batch} has an incomplete merge and must be finalized or repaired",
                )
            )
        elif status == "Completed":
            if "ingest" not in kinds:
                findings.append(
                    Finding("INGEST_LOG", relative, f"completed batch {batch} has no ingest log")
                )
            if "lint" not in kinds:
                findings.append(
                    Finding("LINT_LOG", relative, f"completed batch {batch} has no lint log")
                )
            if not fields.get("Completed") or fields.get("Completed") == "—":
                findings.append(
                    Finding("BATCH_STATE", relative, "Completed status requires Completed date")
                )
            if fields.get("Workflow-Schema") == "1" and not schema_findings:
                findings.extend(postmerge_findings(root, path.relative_to(root)))
    for batch in sorted(set(logged_kinds) - set(seen_batches)):
        findings.append(
            Finding(
                "BATCH_STATE",
                "wiki/log.md",
                f"logged batch {batch} has no lifecycle review report",
            )
        )
    return findings


def repository_findings(root: Path) -> list[Finding]:
    return raw_metadata_findings(root) + batch_state_findings(root) + index_and_link_findings(root)

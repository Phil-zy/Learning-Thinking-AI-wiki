#!/usr/bin/env python3
"""Mechanical publication-readiness gate for content/ready Markdown files."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LOCAL_PATH_RE = re.compile(
    r"(?i)(?:\b[A-Z]:[\\/]|file://|\\\\[^\\/\s]+[\\/][^\\/\s]+|"
    r"(?<![\w:])/(?:Users|home|private|tmp|var|etc)/[^\s<]+)"
)
CREDENTIAL_RE = re.compile(
    r"(?i)(?:api[_ -]?key|access[_ -]?token|password|secret)\s*[:=]\s*[^\s<]{6,}"
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
UNRESOLVED_RE = re.compile(r"(?i)(?:\[待核实\]|\bTODO\b|\bTBD\b)")


def _metadata(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines()[1:20]:
        if not line.startswith(">"):
            if result and line.strip():
                break
            continue
        body = line[1:].strip()
        if ":" in body:
            key, value = body.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def validate_ready_file(project_root: Path, ready_file: Path) -> list[str]:
    project_root = project_root.resolve()
    ready_file = ready_file.resolve()
    errors: list[str] = []

    if not ready_file.is_file():
        return [f"文件不存在：{ready_file}"]

    ready_root = (project_root / "content" / "ready").resolve()
    try:
        ready_file.relative_to(ready_root)
    except ValueError:
        return [f"待发布文件必须位于 content/ready/：{ready_file}"]

    text = ready_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or not re.match(r"^#\s+\S", lines[0]):
        errors.append("缺少非空的一级标题")

    meta = _metadata(text)
    required = (
        "Status",
        "Prepared",
        "Target",
        "Source Draft",
        "User Approval",
        "Publication Check",
    )
    for key in required:
        if not meta.get(key):
            errors.append(f"缺少元数据：{key}")

    if meta.get("Status") and meta["Status"] != "Ready":
        errors.append("Status 必须为 Ready")
    if meta.get("Prepared") and not DATE_RE.fullmatch(meta["Prepared"]):
        errors.append("Prepared 必须使用 YYYY-MM-DD")
    if meta.get("User Approval") and not DATE_RE.fullmatch(meta["User Approval"]):
        errors.append("User Approval 必须记录 YYYY-MM-DD")
    if meta.get("Publication Check") and meta["Publication Check"] != "Passed":
        errors.append("Publication Check 必须为 Passed")

    source_value = meta.get("Source Draft", "")
    link_match = LINK_RE.fullmatch(source_value)
    if source_value and not link_match:
        errors.append("Source Draft 必须是一个 Markdown 相对链接")
    elif link_match:
        target_text = unquote(link_match.group(1).split("#", 1)[0])
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target_text):
            errors.append("Source Draft 必须指向仓库内草稿")
        else:
            draft_path = (ready_file.parent / target_text).resolve()
            drafts_root = (project_root / "content" / "drafts").resolve()
            try:
                draft_path.relative_to(drafts_root)
            except ValueError:
                errors.append("Source Draft 必须位于 content/drafts/")
            else:
                if not draft_path.is_file():
                    errors.append(f"Source Draft 不存在：{target_text}")

    if UNRESOLVED_RE.search(text):
        errors.append("仍包含待核实、TODO 或 TBD 标记")
    if LOCAL_PATH_RE.search(text):
        errors.append("检测到本地绝对路径或 file:// 地址")
    if CREDENTIAL_RE.search(text) or PRIVATE_KEY_RE.search(text):
        errors.append("检测到疑似凭据或私钥")

    return errors


def _collect_files(project_root: Path, args: list[str]) -> list[Path]:
    if args:
        return [
            (project_root / item if not Path(item).is_absolute() else Path(item))
            for item in args
        ]
    ready_root = project_root / "content" / "ready"
    return sorted(ready_root.rglob("*.md")) if ready_root.is_dir() else []


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "Usage: check_publication.py <project-root> [content/ready/file.md ...]",
            file=sys.stderr,
        )
        return 2

    project_root = Path(argv[1]).resolve()
    files = _collect_files(project_root, argv[2:])
    failures = 0
    for path in files:
        errors = validate_ready_file(project_root, path)
        if errors:
            failures += 1
            try:
                label = path.resolve().relative_to(project_root)
            except ValueError:
                label = path
            print(f"FAIL {label}")
            for error in errors:
                print(f"  - {error}")

    if failures:
        print(f"Publication gate failed: {failures} file(s).", file=sys.stderr)
        return 1

    print(f"Publication gate passed: {len(files)} ready file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

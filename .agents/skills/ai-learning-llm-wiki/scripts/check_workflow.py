#!/usr/bin/env python3
"""Read-only completion gate for the AI learning wiki workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from workflow_gate import postmerge_findings, premerge_findings, repository_findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument(
        "--phase",
        choices=("premerge", "postmerge", "repository"),
        required=True,
    )
    parser.add_argument("--batch")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if args.phase == "repository":
        findings = repository_findings(root)
    elif args.phase == "premerge":
        if not args.batch:
            print("BATCH_FORMAT --batch is required for premerge")
            return 2
        findings = premerge_findings(root, Path(args.batch))
    else:
        if not args.batch:
            print("BATCH_FORMAT --batch is required for postmerge")
            return 2
        findings = postmerge_findings(root, Path(args.batch))
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"FAILED {len(findings)} workflow issue(s)")
        return 1
    print(f"OK {args.phase} workflow checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

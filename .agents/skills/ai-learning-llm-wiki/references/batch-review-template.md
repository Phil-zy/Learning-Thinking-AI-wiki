# Ingest Review: {Batch Title}

> Workflow-Schema: 1
> Batch: {YYYY-MM-DD-unique-batch-slug}
> Created: {YYYY-MM-DD}
> Status: Pending approval
> Approved: —
> Completed: —

## Summary

- Sources requested: {N}
- Raw saved: {N}
- Fetch failures: {N}
- Disposition: New {N}; Update {N}; No material {N}; Disputed {N}

## Proposed Formal Wiki Changes

| Target Wiki page | Action | Staging draft | Source files | Base state | Staging SHA-256 | Index summary |
|---|---|---|---|---|---|---|
| [{Title}](../wiki/{topic}/{article}.md) | New / Update | [{Title}](../staging/{topic}/{article}.md) | `raw/{topic}/{file}.md` | New target / SHA-256: `{formal hash}` | SHA-256: `{staging hash}` | {One-line summary without a pipe character} |

## Review Required

- {Conflicts, low-confidence claims, sensitive-content concerns, or `None`.}

## Approval Scope

- Approve all: {staging paths to merge and remove after success}
- Hold: {staging paths to retain}
- No material: {Raw paths retained without a staging draft}

## Notes

{Fetch failures, duplicate candidates, new-topic index description requirements, or other context needed for a decision.}

Status lifecycle: `Pending approval` → `Approved` → `Merge incomplete` → `Completed`. `Merge incomplete` is normally transient and remains visible when a started merge does not pass post-merge verification. Never mark `Completed` manually; `scripts/finalize_ingest.py` owns that transition.

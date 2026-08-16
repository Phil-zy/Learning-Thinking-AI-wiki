# ima Incremental Ingest

Use this reference only when the source is a user's authorized ima knowledge base.

## Preconditions

1. Read `config/ima-ingest.local.json` from the project root.
2. Reject missing or invalid configuration and placeholder values.
3. Discover available ima connector tools at runtime. Do not require a fixed MCP server or tool name.
4. Require capabilities equivalent to:
   - list accessible knowledge bases;
   - list entries in one knowledge base;
   - fetch one entry's content and metadata.
5. Resolve `knowledge_base_name` to exactly one accessible knowledge base. Do not guess among duplicate names.
6. Never write connector credentials, account identifiers, OAuth tokens, cookies, or internal knowledge-base IDs to the repository.

## Local state

Use `.local/ima-ingest-state.json`. The whole `.local/` directory is local-only and ignored by Git.

Recommended schema:

```json
{
  "schema": 1,
  "knowledge_base_name": "user supplied name",
  "last_successful_run": "ISO-8601 timestamp",
  "max_create_time": 0,
  "items": {
    "opaque-media-id": {
      "create_time": 0,
      "remote_version": "optional opaque value",
      "last_seen_update_marker": "optional text",
      "raw_versions": ["raw/topic/file.md"]
    }
  }
}
```

Do not put this example's placeholder values into a real batch report.

## Candidate selection

Use two dimensions:

1. **New item**: the primary identity (`media_id` when available) is absent from state. `create_time > max_create_time` is a useful fast path, not the only source of truth.
2. **Updated item**: identity already exists, but a remote version/update field changed, or the remote wording contains a configured update marker.

Do not rely only on `create_time`; some systems retain the original creation time after editing.

If an entry lacks a stable identity, derive a conservative identity from the connector's immutable identifier. Do not use title alone when duplicate titles are possible.

## Fetch and copyright handling

- Fetch only selected candidates, up to `max_items_per_run`.
- Default `copyright_mode` is `metadata-and-summary`: save canonical Raw metadata, necessary claim summaries, a stable opaque source identity when allowed, and source limitations. Do not store a full copyrighted article unless the user has provided it or explicitly confirmed the right to retain it.
- Every Raw file must use the canonical `Source`, `Collected`, and `Published` fields from `raw-template.md`.
- Never overwrite Raw. For updated sources, use a new suffix such as `-v2` or `-v3`.

## Triage and review

- New candidates normally triage as New, but still search wiki/ and staging/ before deciding.
- Updated candidates triage as Update, No material, and/or Disputed after comparing the newly fetched version with existing Raw and Wiki content.
- Include an update difference summary in the batch report.
- Create one unique batch report per run.
- Stop at Pending approval. Automation cannot approve its own output.

## State commit rule

Treat local state as a commit marker:

1. Fetch candidates.
2. Write all Raw files, staging drafts, and the batch report.
3. Run evidence and applicable premerge checks.
4. Only after every required artifact succeeds, replace `.local/ima-ingest-state.json` atomically.

On failure, retain the prior state so the next run can safely retry. Report partial artifacts and do not claim the failed candidates as consumed.

## Completion report

Report:

- accessible and selected knowledge-base resolution;
- total remote entries examined;
- selected New and Updated candidates;
- New, Update, No material, and Disputed dispositions;
- fetch failures and retry safety;
- Raw, staging, and review files created;
- exact items waiting for user approval.

Never run Approval Merge, delete staging drafts, commit Git, or push a remote from an unattended ingest Automation.

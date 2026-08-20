---
name: ai-learning-llm-wiki
description: "Build and maintain the template's external-source AI-learning wiki, including staged source ingest, review and approval, evidence linting, querying, archiving, and incremental ingestion from an authorized ima knowledge base in WorkBuddy. Use for requests such as 'add to wiki', 'import from ima', 'set up ima ingestion', 'what do I know about', '导入知识库', '从 ima 摄取', '批量导入', and '检查知识库'. Do not use it to mature personal thoughts or write public articles; use ai-thinking-writing for that."
---

# AI Learning LLM Wiki

Build and maintain a personal knowledge base using LLMs. You manage `raw/` (immutable source material), `staging/` (review drafts), `reviews/` (batch review reports), and `wiki/` (approved knowledge articles). Sources go into raw/, compilation defaults to staging/, and only user-approved changes enter wiki/.

This Skill owns the external-knowledge pipeline. Personal experiences, viewpoints, content seeds, drafts, and publication versions belong to `ai-thinking-writing`; do not create or upgrade them as a side effect of Ingest or Query.

Core ideas from Karpathy:
- "The LLM writes and maintains the wiki; the human reads and asks questions."
- "The wiki is a persistent, compounding artifact."

## Architecture

Four working areas, all under the user's project root:

**raw/** — Immutable source material. You read, never modify. Organized by topic subdirectories (e.g., `raw/machine-learning/`).

**wiki/** — Compiled knowledge articles. You have full ownership. Organized by topic subdirectories, one level only: `wiki/<topic>/<article>.md`. Contains two special files:
- `wiki/index.md` — Global index. One row per article, grouped by topic, with link + summary + Updated date.
- `wiki/log.md` — Append-only operation log.

**staging/** — Review drafts that mirror their intended `wiki/` paths, for example `staging/ai-knowledge/article.md` maps to `wiki/ai-knowledge/article.md`. Never use staging/ as a second long-term wiki.

**reviews/** — Batch review reports. These are temporary decision artifacts, not source material or formal knowledge pages.

Every new review uses a unique Batch ID and `Workflow-Schema: 1`. The review report is the source of truth for batch lifecycle state; `wiki/log.md` is an append-only audit projection and must agree with it.

**SKILL.md** (this file) — Schema layer. Defines structure and workflow rules.

Templates live in `references/` relative to this file. Read them when you need the exact format for raw files, articles, archive pages, or the index.

### Initialization

Triggers only on the first Ingest. Check whether `raw/` and `wiki/` exist. Create only what is missing; never overwrite existing files:

- `raw/` directory (with `.gitkeep`)
- `wiki/` directory (with `.gitkeep`)
- `wiki/index.md` — heading `# Knowledge Base Index`, empty body
- `wiki/log.md` — heading `# Wiki Log`, empty body

Create `staging/` and `reviews/` only when a draft or a batch review report is required.

If Query or Lint cannot find the wiki structure, tell the user: "Run an ingest first to initialize the wiki." Do not auto-create.

## The Grounding Invariant

Every load-bearing fact in wiki/ — numbers, dates, direct quotes — exists verbatim in the raw/ files linked by that article's Raw field. Compile *establishes* this invariant (locate before you write); lint *verifies* it (`scripts/check_evidence.py` greps the high-signal literals — suffixed or large numbers, decimals, ISO dates, longer quotes — in the linked raws; the compile-time locate-before-write rule covers the rest). Because raw/ is immutable, a verified article stays verified; the script re-checks the whole wiki in seconds, so there is no incremental state to maintain.

---

## Ingest

Fetch a source into raw/, then compile it into staging/ — unless the source adds nothing new. Always fetch; whether to compile depends on the triage below. Do not modify formal wiki/ pages until the user explicitly approves a merge.

When the source is an ima knowledge base, read `references/ima-ingest.md` before fetching. Use it for connector discovery, local configuration, incremental state, update detection, copyright handling, and failure recovery. WorkBuddy Automation must stop after creating Raw, staging drafts, and the batch report; it must never approve or merge a batch by itself.

### Fetch (raw/)

1. Get the source content using whatever web or file tools your environment provides. If nothing can reach the source, ask the user to paste it directly.

2. Pick a topic directory. Check existing `raw/` subdirectories first; reuse one if the topic is close enough. Create a new subdirectory only for genuinely distinct topics.

3. Save as `raw/<topic>/YYYY-MM-DD-descriptive-slug.md`.
   - Slug from source title, kebab-case, max 60 characters.
   - Published date unknown → omit the date prefix from the file name (e.g., `descriptive-slug.md`). The metadata Published field still appears; set it to `Unknown`.
   - If a file with the same name already exists, append a numeric suffix (e.g., `descriptive-slug-2.md`).
   - Include metadata header: source URL, collected date, published date.
   - Preserve original text. Clean formatting noise. Do not rewrite opinions.

   See `references/raw-template.md` for the exact format.

### Triage

After saving the raw file and before creating drafts, search both wiki/ and staging/ with the source's key entities and synonyms, then state the disposition:

- **New** — creates one or more new staged articles.
- **Update** — prepares staged changes to existing article(s).
- **Disputed** — contradicts existing content; may combine with New or Update (see Compile for conflict annotation).
- **No material** — adds no knowledge beyond what the wiki already holds. Keep the raw file, list it in the batch review report, and stop. Do not force an article out of a thin source.

New, Update, and Disputed may be combined. No material is exclusive.

### Compile (staging/)

Determine where the new content belongs:

- **Same core thesis as existing article** → Create or update its mirrored staging draft. Add the new source to Sources/Raw and update affected sections in the draft.
- **New concept** → Create a new draft in the most relevant staging topic directory. Name the file after the concept, not the raw file.
- **Spans multiple topics** → Place the primary draft in the most relevant staging directory. Add See Also cross-references to related pages or staged drafts where they already exist.

These are not mutually exclusive. A single source may warrant merging into one article while also creating a separate article for a distinct concept it introduces. In all cases, check for factual conflicts: if the new source contradicts existing content, mark the contested claims with a **Status: Disputed** block (see `references/article-template.md`). When the conflicting content lives in separate articles, mark both and cross-link them.

**Source fidelity.** Every number, date, and direct quote must be located in the raw file (grep or read) *before* it is written; write the value exactly as found — if the source says 42K, write 42K, not 42,000. Derived values (sums, deltas, counts you computed) must show their components so each component is findable in raw. If you cannot locate a value, do not write its exact form; drop it or state it without precision.

See `references/article-template.md` for article format. Key points:
- Sources field: author, organization, or publication name + date, semicolon-separated.
- Raw field: markdown links to raw/ files, semicolon-separated.
- Relative paths from `staging/<topic>/` and `wiki/<topic>/` use `../../raw/<topic>/<file>.md` (two levels up to project root).

### Cascade Updates

After the primary draft, check for ripple effects. Do not rely on the index alone: search the full wiki and staging for the source's key entities, aliases, and the claims it touches, then create or update a mirrored staging draft for every non-archive article whose content is materially affected. Each affected draft gets its Updated date refreshed.

When the new source supersedes or contradicts an existing claim, keep the old claim for the record but mark it with a Status block (see `references/article-template.md`): **Outdated** when something newer replaces it, **Disputed** when sources disagree. Never silently rewrite history.

Archive pages are never cascade-updated (they are point-in-time snapshots).

### Batch Review Report

For every ingest request, create one report at `reviews/YYYY-MM-DD-ingest-<batch-slug>.md`. A single-source ingest is a batch of one. Read `references/batch-review-template.md` for the required format.

The report must include:

- source totals and any fetch failures;
- New, Update, No material, and Disputed counts;
- every proposed new or updated formal Wiki page, linked to its staging draft;
- for every update, the SHA-256 hash of the formal target when its draft was created; use `New target` when the formal page did not yet exist;
- the SHA-256 hash of every staging draft and the one-line index summary to publish;
- a unique Batch ID plus `Pending approval`, `Approved`, `Merge incomplete`, or `Completed` lifecycle metadata;
- conflicts, low-confidence claims, sensitive-content concerns, and items requiring user input;
- the exact staging drafts proposed for merge and removal.

Do not update formal `wiki/index.md` or `wiki/log.md` while the batch is awaiting approval. For No material sources, retain the Raw file and list it in the report; do not create a staging article.

### Workflow Completion Gate

For `Workflow-Schema: 1` batches, use the local gate scripts; do not reproduce their checks manually:

```powershell
python3 <skill-dir>/scripts/check_workflow.py <project-root> --phase premerge --batch reviews/<report>.md
python3 <skill-dir>/scripts/finalize_ingest.py <project-root> --batch reviews/<report>.md
python3 <skill-dir>/scripts/check_workflow.py <project-root> --phase repository
```

State transitions are `Pending approval` → `Approved` → `Merge incomplete` → `Completed`. `finalize_ingest.py` uses the incomplete state after preflight and before all post-merge checks pass; it is normally transient. A failure keeps the staging drafts and the incomplete state for a safe retry. A completed batch is idempotent: rerunning the finalizer verifies it and performs no writes.

The gate verifies canonical Raw metadata, batch/report/log agreement, staging and formal SHA-256 hashes, Raw links and evidence, index dates, internal links, ingest and lint log entries, and staging cleanup. `reviews/` is authoritative for state; never infer approval from a formal file or log entry alone.

### Approval Merge

Merge only after the user explicitly approves a whole batch or identifies selected staged pages. Record `Status: Approved` and the Approved date in the report, then run `finalize_ingest.py`. Treat an approval as authorization to remove the corresponding staging drafts only after the completion gate succeeds, unless the user asks to retain them.

The finalizer performs these steps for each approved draft:

1. Verify the draft's Raw links and compare the formal target's current SHA-256 hash with the batch report baseline. If it changed, report the conflict and do not overwrite it without a new user decision.
2. Create or update the mirrored target in wiki/.
3. Update `wiki/index.md` for every changed formal article. When adding a new topic section, include a one-line description. The Updated date reflects when the article's knowledge content last changed, not the file system timestamp. See `references/index-template.md` for format.
4. Append one ingest entry to `wiki/log.md` for the approved batch. List the Raw files and every cascade-updated formal article:

   ```
   ## [YYYY-MM-DD] ingest | <primary article title>
   - Batch: <unique Batch ID>
   - Disposition: <New; Update; Disputed>
   - Raw: <raw file path>
   - Updated: <cascade-updated article title>
   ```

5. Run the full Lint workflow after all approved drafts are merged.
6. Run the postmerge gate, mark the review `Completed`, and only then remove successfully merged staging drafts. Keep unapproved, conflicted, or incomplete drafts in staging/.

Leave the batch report in reviews/ unless the user explicitly asks to remove it. Reports are not formal Wiki pages and must not be indexed.

### Direct Formal Update

When the user explicitly asks to bypass staging/, compile directly into wiki/ and follow the ordinary index, log, source-fidelity, and Lint requirements. State that the review gate was bypassed in the completion report.

### Research (multi-source ingest)

Use only when the user explicitly asks to research a topic or gather sources into the wiki. Ordinary knowledge questions go to Query, which never writes files.

1. Split the topic into a few angles. For each, search with a wide net — official names, abbreviations, and synonyms, not just the literal keywords.
2. For any core claim you expect to conclude, deliberately search the opposing side: failures, criticism, failed replications.
3. Save selected sources to raw/ as usual. Searching may run in parallel; compilation must not — compile one source at a time, because staging drafts, review reports, and cascade updates are shared state.

---

## Query

Search the wiki and answer questions. Examples of triggers:
- "What do I know about X?"
- "Summarize everything related to Y"
- "Compare A and B based on my wiki"

### Steps

1. Read `wiki/index.md` to locate candidate articles, then full-text search wiki/ with the topic's key terms *and their synonyms*. Never claim the wiki has no relevant content until both the index and the full-text search come back empty — and say that you searched.
2. Read the articles you found and synthesize an answer.
3. Prefer wiki content over your own training knowledge. Cite sources with markdown links: `[Article Title](wiki/topic/article.md)` (project-root-relative paths for in-conversation citations; within wiki/ files, use paths relative to the current file).
4. Output the answer in the conversation. Do not write files unless asked.

### Archiving

When the user explicitly asks to archive or save the answer to the wiki:

1. Write the answer as a new wiki page. See `references/archive-template.md`. When converting conversation citations to the archive page, rewrite project-root-relative paths (e.g., `wiki/topic/article.md`) to file-relative paths (e.g., `../topic/article.md` or `article.md` for same-directory).
   - Sources: markdown links to the wiki articles cited in the answer.
   - No Raw field (content does not come from raw/).
   - File name reflects the query topic, e.g., `transformer-architectures-overview.md`.
   - Place in the most relevant topic directory.
2. Always create a new page. Never merge into existing articles (archive content is a synthesized answer, not raw material).
3. Update `wiki/index.md`. Prefix the Summary with `[Archived]`.
4. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] query | Archived: <page title>
   ```

---

## Lint

Quality checks on the wiki. Three categories with different authority levels.

### Safe Fixes (auto-fix)

Fix these automatically:

**Index consistency** — compare `wiki/index.md` against actual wiki/ files (excluding index.md and log.md):
- File exists but missing from index → add entry with `(no summary)` placeholder. For Updated, use the article's metadata Updated date if present (for archive pages, the Archived date); otherwise fall back to file's last modified date.
- Index entry points to nonexistent file → mark as `[MISSING]` in the index. Do not delete the entry; let the user decide.
- Index entry's Updated differs from the article's metadata Updated (or Archived, for archive pages) → update the index entry to match the article.

**Internal links** — for every markdown link in wiki/ article files (body text and Sources metadata), excluding Raw field links (validated by Raw references below), excluding See Also section links (handled by the See Also rule below), and excluding index.md/log.md (handled above):
- Target does not exist → search wiki/ for a file with the same name elsewhere.
  - Exactly one match → fix the path.
  - Zero or multiple matches → report to the user.

**Raw references** — every link in a Raw field must point to an existing raw/ file:
- Target does not exist → search raw/ for a file with the same name elsewhere.
  - Exactly one match → fix the path.
  - Zero or multiple matches → report to the user.

**See Also** — within each topic directory:
- Target of a See Also link does not exist → search wiki/ for a file with the same name elsewhere.
  - Exactly one match → fix the path.
  - Zero matches → remove the link (a dead cross-reference is not load-bearing).
  - Multiple matches → report to the user.

### Mechanical Reports (no fixes)

Run these mechanically with `python3 <skill-dir>/scripts/check_evidence.py <project-root>` (optionally followed by project-root-relative article paths to limit scope). Default scope is the whole wiki; the script is fast. Report findings; never auto-fix facts.

**Source fidelity** — reported suspects are candidates, not verdicts: derived values and product names may appear. Judge each against the raw context and report only real mismatches.

**Evidence errors** — articles the script cannot verify (missing Raw field, unresolvable Raw links, or Raw links escaping `raw/`). These always need a decision, not a fix from the script.

**Unreferenced raw files** — files logged with a No material disposition are excluded; everything else is a genuine backlog reminder.

### Judgment Reports (no fixes)

These rely on your judgment. Report findings without auto-fixing:

- Factual contradictions across articles
- Outdated claims superseded by newer sources but still presented without a Status block
- Missing conflict annotations where sources disagree
- Obviously missing cross-references between related articles (suggest them; do not add silently)
- Malformed Status blocks (Outdated missing its date, or either block missing its explanation; format reference: `references/article-template.md`)
- Orphan pages with no inbound links from other wiki articles
- Missing cross-topic references
- Concepts frequently mentioned but lacking a dedicated page
- Archive pages whose cited source articles have been substantially updated since archival

### Post-Lint

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] lint | <N> issues found, <M> auto-fixed
- Batch: <unique Batch ID>
```

At repository handoff and before commits, run:

```powershell
python3 <skill-dir>/scripts/check_workflow.py <project-root> --phase repository
```

---

## Conventions

- Standard markdown with relative links throughout.
- wiki/ supports one level of topic subdirectories only. No deeper nesting.
- Today's date for log entries, Collected dates, and Archived dates. Updated dates reflect when the article's knowledge content last changed. Published dates come from the source (use `Unknown` when unavailable).
- Inside wiki/ files, all markdown links use paths relative to the current file. In conversation output, use project-root-relative paths (e.g., `wiki/topic/article.md`).
- Ingest updates both `wiki/index.md` and `wiki/log.md` (a No material ingest updates only the log). Archive (from Query) updates both. Lint updates `wiki/log.md` (and `wiki/index.md` only when auto-fixing index entries). Plain queries do not write any files.

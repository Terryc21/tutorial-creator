# Vocab Surface — tutorial-creator v2

**Status:** Shipped in v2.0.0. Full vocab surface with state machine, review, and gap radar.
**Loaded by:** `SKILL.md` when the user routes to `vocab <subcommand>` or chooses `[3]` from the gateway.
**Source of truth for the schema:** `SCHEMAS.md` Schema 2 (`vocabulary.yaml`).

---

## Surface contract

The vocab surface is independent of tutorial generation. Users can add terms outside lessons, review what they know, find what they're confused about, and inspect their full vocabulary state — all without writing a tutorial.

**Why this matters.** v1.1 coupled vocabulary capture to lesson production: the only way a term entered VOCABULARY.md was by being introduced in a generated tutorial. v2 decouples them so:

- A term encountered in a code review can be captured immediately
- A term read in someone else's tutorial can be added to your reference
- Terms accumulate genuine status (mastered / confused) through tests, not just by appearing
- The vocab list becomes a learning artifact in its own right

## File locations

In the user's project (created at first run if missing):

```
{tutorials_dir}/
├── vocabulary.yaml       (source of truth — Schema 2)
└── VOCABULARY.md         (generated view — never edit by hand)
```

Where `{tutorials_dir}` comes from `.claude/tutorial-config.yaml`.

## Subcommand reference

| Subcommand | Purpose |
|---|---|
| `vocab add <term>` | Draft definition; user confirms; saved |
| `vocab ingest <source>` | Batch-extract terms + phrases from a source (session transcript, URL, file, memory files, pasted text); each gets a definition and use case, added with confirmation |
| `vocab list [--status=<s>] [--source=<match>] [--date=…]` | Browse the full vocabulary, filterable by status, source, and/or date |
| `vocab show <term>` | Full record for one term |
| `vocab edit <term>` | Update fields (definition, use_case, type, related_terms, notes) |
| `vocab merge <a> <b>` | Collapse duplicates |
| `vocab review [--strict]` | Spaced-repetition test session |
| `vocab gap` | Show terms with `status: confused`, ranked by staleness |
| `vocab flashcards [--status=<s>] [--source=<match>] [--date=…] [--count=N]` | Export vocabulary.yaml as Markdown, Anki `.apkg`, or a duplex-print PDF; same filters as `vocab list` |
| `vocab regen-md` | Regenerate VOCABULARY.md from vocabulary.yaml |
| `vocab undo` | Revert last `vocab add` or `vocab ingest` (within 24h soft-stage; Phase 6 wires the broader undo) |

---

## `vocab add <term>`

### Procedure

1. **Read existing vocabulary.yaml.** If the file doesn't exist, create it with `[]` and continue.
2. **Check for duplicates.** Case-insensitive match on `term`. If a term with the same name exists:
   ```
   "<term>" already exists in your vocabulary (status: <existing_status>).
   [show]  show the existing record
   [edit]  update the existing record (vocab edit <term>)
   [skip]  cancel
   ```
   If user picks `show` or `edit`, route to that subcommand instead.
3. **Draft the definition.** Use AskUserQuestion (or plain prompt) to gather:
   - **Type** — best guess from a list (swift-keyword / swift-attribute / api / concept / pattern / idiom; or language-specific equivalents). Show 4 candidate types with one-line explanations; user picks one or types `other` to enter free-form.
   - **Definition** — AI drafts a 1-3 sentence definition based on the term and the user's project context (active language from config). Show the draft with this prompt:
     ```
     Drafting definition...
     Type:       <chosen-type>
     Definition: <ai-drafted text>
     Use case:   <ai-drafted 1-2 sentence scenario, optional>
     Source file (optional): _
     Context:    vocab add
     Related terms (suggested): <list of 2-4 related terms from existing vocabulary>

     Accept this draft? [y / edit / skip use case / cancel]
     ```
   - **Use case** — optional. AI drafts a concrete scenario ("when/why would I reach for this") distinct from the definition ("what is this"). User can accept, edit, or skip (leaves the field empty per Schema 2 default).
   - **Source file** — optional. User can paste a file path, optionally with `:line` suffix.
   - **Related terms** — AI suggests by scanning existing vocabulary.yaml for terms with similar tags, types, or vocabulary near the new term. User accepts, edits, or clears.
4. **On confirm:**
   - Append a new entry to vocabulary.yaml per Schema 2:
     ```yaml
     - term: "<term>"
       type: <type>
       definition: |
         <definition text>
       use_case: |
         <use case text, or omit the field entirely if skipped>
       first_encountered:
         source_file: "<path-or-empty>"
         context: vocab add
         date: "<today ISO date>"
       status: new
       test_history: []
       applied_test_history: []
       related_terms: [<list>]
       notes: ""
     ```
   - Write a 24h soft-stage marker file: `<tutorials_dir>/vocabulary.yaml.add-<ISO-timestamp>` containing the term name. Used by `vocab undo` (within 24h). The sentinel is the disambiguator that distinguishes standalone adds from tutorial-time adds; the latter are already captured by the session-log snapshot system in `SKILL.md` § Recovery and do NOT write a sentinel.
   - Regenerate VOCABULARY.md.
   - Print confirmation: `Added "<term>" (status: new). Undo within 24h via: /skill tutorial-creator vocab undo`
5. **On `edit`:** drop into editable interactive editor for the four AI-drafted fields, then return to step 4.
6. **On `cancel`:** stop. No file written.

### Error handling

- If user provides a `source_file` path that doesn't exist in the project, warn but allow (user might be referring to an external file).
- If `vocabulary.yaml` is malformed (yaml parse error), refuse to write. Tell the user: `vocabulary.yaml is malformed: <error>. Run vocab regen-md or fix manually.` Do not corrupt the file with a partial append.

---

## `vocab ingest <source>`

Batch-extract vocabulary terms and phrases from an arbitrary source — a session transcript, a URL, a local file, a memory file, pasted text — and add each one to vocabulary.yaml with a definition and use case, all under a single confirmation step. This is the vocab-only counterpart to `SKILL.md` Entry [f] (External source): entry [f] produces a full Day-N tutorial *and* files new vocab as a side effect; `vocab ingest` produces *only* the vocabulary entries, with no tutorial artifact. Use `vocab ingest` when the goal is building the glossary; use entry [f] when the goal is a synthesis document that also happens to grow the glossary.

### Accepted source types

Same as Entry [f] — see `SKILL.md` § "Entry [f] — External source" § "Accepted source types" for the authoritative list (URL, file path, pasted text). This section does not repeat those rules; where this procedure says "fetch the source" or "handle the citation," it means exactly what Entry [f] means, including:

- The fetch-failure fallback (offer file path or paste instead of guessing at URL contents)
- The pasted-content citation rule (ask for a public URL; never fetch a URL provided alongside a paste; never fabricate a citation when none exists)
- The ~50,000 character paste-size limit (suggest a file instead)

**One addition specific to `vocab ingest`:** a session transcript is a first-class source, not just "pasted text" or "a file." If the user says "this session" or names another session, and the runtime has a way to access that transcript (this session's own context, or a session log path), treat it as already-fetched content — no fetch step, no citation prompt (a transcript has no public URL; note the source as `"session transcript, <date>"` in `first_encountered.context` instead of asking for one).

### Procedure

1. **Read config + existing vocabulary.yaml.** Need `language`, `project_dir` for the codebase-mapping step, and the full existing term list for duplicate detection.
2. **Resolve the source**, per "Accepted source types" above. For a session transcript, use the available content directly (this session) or read the named session's transcript/log file.
3. **Extract candidate terms and phrases.** Scan the source for:
   - Technical terms and jargon (identifiers, API names, keywords — same signal Entry [f] step 4 uses)
   - Multi-word phrases that function as a unit of jargon (e.g., "confidence floor," "token propagation delay," "spread-gate hide") — vocabulary.yaml's `term` field is not restricted to single words; a phrase is a valid term
   - Concepts that were *explained* in the source (a definition-shaped sentence: "X is...", "X means...", "X refers to...") are higher-confidence candidates than concepts merely *named* in passing
4. **Filter against existing vocabulary.** Case-insensitive match each candidate against vocabulary.yaml. Split into two groups, same shape as Entry [f] step 5:
   - **Already in your vocabulary** — shown with current status; not re-added, but the source can be appended to `notes` if the term's use in this source adds something the existing entry lacks (offer this per-term, don't do it silently)
   - **New to your vocabulary** — candidates for a new entry
5. **Show the extraction with confirmation.** Format:
   ```
   Scanned <source description> — found N candidate terms.

   Already in your vocabulary (won't re-add):
     - <term> (status: <status>)
     - ...

   New to your vocabulary:
     1. <term>          <one-line hint of where/how it appeared>
     2. <term>          ...
     ...

   Add which ones? [all / 1,3,5 / none / cancel]
   ```
   Cap the "new" list at 20 shown candidates; if more exist, say `+N more not shown — narrow the source or run ingest again after this batch` rather than silently truncating (per the no-silent-caps rule).
6. **For each selected term, draft definition + use case.** Same drafting shape as `vocab add` step 3 — AI drafts both fields from the term's actual usage *in the source* (not generic knowledge about the term), so the definition reflects how the source actually used it. Show all drafts together for one bulk confirmation rather than one prompt per term (batch ingest should not become N individual confirmations):
   ```
   Drafted entries (3):

   1. confidence floor
      Definition: A threshold check that hides a valuation range when too
                   few comps exist or their spread is too wide, rather than
                   showing an unreliable number.
      Use case:    Prevents showing a fake-looking "$15-$45" range for a
                   thrift item when only 2 noisy comps were found.

   2. token propagation delay
      Definition: ...
      Use case:    ...

   3. ...

   Accept all as drafted? [y / edit <N> / drop <N> / cancel]
   ```
7. **On confirm:** for each accepted term, append to vocabulary.yaml per Schema 2 (same shape as `vocab add` step 4), with:
   - `first_encountered.context`: `"vocab ingest"` (or `"session transcript, <date>"` for a session source, per "Accepted source types" above)
   - `first_encountered.source_file`: the file path if the source was a file; empty for URL/paste/session sources (the source description lives in `notes` instead, since `source_file` is specifically for in-project file references)
   - `notes`: one line naming the source, e.g. `"Ingested from session transcript, 2026-08-31."` or `"Ingested from https://example.com/article."`
   - Write **one** 24h soft-stage marker covering the whole batch (not one per term) — `<tutorials_dir>/vocabulary.yaml.add-<ISO-timestamp>` containing the list of added term names. `vocab undo` on this marker reverts the entire batch as a unit, matching the "one ingest = one undoable action" mental model.
   - Regenerate VOCABULARY.md.
8. **On `none` or `cancel`:** stop. No file written.

### Honesty rules (cross-cutting, inherited from Entry [f])

- Definitions and use cases are drafted from the source's actual content, not generic knowledge — if the source doesn't explain a term well enough to draft an honest definition, say so per-term rather than filling in from general knowledge: `"<term>" appeared in the source but wasn't explained there. Draft from general knowledge instead, or skip it?`
- Never fabricate a citation for pasted content with no public URL, per Entry [f]'s pasted-content rule.
- If extraction finds zero candidates (source has no jargon-shaped content), say so plainly: `No new vocabulary terms found in this source.` Do not force a result.

---

## `vocab flashcards [--status=<status>] [--source=<match>] [--date=<YYYY-MM-DD>] [--date-from=<YYYY-MM-DD>] [--date-to=<YYYY-MM-DD>] [--count=N]`

Export vocabulary.yaml entries as flashcards, front = term, back = definition + use case. Read-only against vocabulary.yaml (writes only the export file, never modifies the vocabulary itself).

### Procedure

1. **Read vocabulary.yaml.** If empty: `Your vocabulary is empty. Add terms with vocab add or vocab ingest first.` Stop.
2. **Filter** by `--status`, `--source`, and/or the date flags exactly as `vocab list` does — see that command's Procedure steps 2-5 for the matching rules and composition behavior (filters AND together). This makes "flashcards from just this one URL" or "flashcards from what I learned this week" first-class exports, not just first-class lists. If the combined filter matches zero terms: `No terms match that filter — nothing to export.` Stop.
3. **Select count.** If `--count=N` is set, pick N terms prioritized the same way `vocab review`'s tier system does (confused/stale first — reviewing the gaps is more valuable practice than drilling what's already mastered), applied *within* the filtered set from step 2. Without `--count`, export every term matching the filter.
4. **Build one card per term:**
   - **Front:** the term, verbatim.
   - **Back:** `definition`, followed by a blank line, followed by `use_case` if non-empty (formatted as "Example: <use_case text>"). If `use_case` is empty for a term, the back is definition-only — do not fabricate a use case at export time; that's `vocab ingest`/`vocab edit`'s job, not export's.
5. **Ask export format:**
   ```
   Exporting N cards. Format?
     [md]     Markdown (front/back pairs, portable, human-readable)
     [apkg]   Anki package (.apkg, importable directly into Anki)
     [print]  Print-ready PDF for physical cards (duplex, cut guides)
     [both]   md + apkg (print is opt-in separately -- see below)
   ```
6. **Markdown export.** Same front/back/separator format as flashcard-generator's Markdown export (`front\n---\nback\n===`), for consistency with the sibling tool users may already know. Write to `{tutorials_dir}/flashcards-<ISO-date>.md`.
7. **APKG export.** Reuse the same genanki-based generation approach documented in the `flashcard-generator` skill (front/back → `genanki.Note`, packaged via `genanki.Package`) — see that skill's SKILL.md § "Anki APKG Export" for the exact script shape; the card content here is sourced from vocabulary.yaml instead of AI-summarized text, so the summarize/chunk steps in that skill do not apply. Write to `{tutorials_dir}/flashcards-<ISO-date>.apkg`. If `genanki`/`mistune` aren't installed, install via pip same as that skill does; if installation fails, fall back to Markdown-only and say so.
8. **Print export.** See "Print export (`[print]`)" below — a distinct procedure, since it needs a duplex-convention answer from the user and real page-layout math, not just a format conversion.
9. **Confirm:**
   ```
   Exported N cards from your vocabulary (filters: <status/source/date summary, or "none">).
     - {tutorials_dir}/flashcards-<date>.md
     - {tutorials_dir}/flashcards-<date>.apkg   (if requested)
     - {tutorials_dir}/flashcards-print-<date>.pdf   (if requested)

   Import .apkg into Anki: File > Import > select the file.
   Print the PDF: open it, print pages 1-N (fronts) first, then reload the
   SAME sheets into the printer/copier and print pages N+1-2N (backs) on
   the reverse side. See the PDF's own first page for duplex-orientation
   instructions specific to your answer below.
   ```

### Print export (`[print]`)

Produces a print-ready PDF laid out so that, after duplex printing and cutting, each physical card shows its term on one side and definition + use case on the flip side — cut once, both sides align.

**Why this is a distinct procedure, not just another output format:** unlike Markdown and APKG (which are pure reformatting of the same front/back pairs), a print layout has to solve a real geometry problem — content printed on the back of a duplex sheet is NOT in the same left-to-right, top-to-bottom order as the front, because physically flipping a sheet mirrors it. Getting this wrong doesn't produce an error; it produces cards that look fine in the PDF preview and are silently wrong once printed and cut — term A's front paired with term B's back. This procedure exists specifically to prevent that failure mode.

#### Ask the duplex convention first

Before generating anything, ask:

```
How does your printer/copier handle two-sided printing?
  [long-edge]   Flips like a book page (left edge stays fixed) -- the
                 common default for most home/office printers and copiers.
  [short-edge]  Flips like a calendar page (top edge stays fixed) -- less
                 common; check your printer's duplex setting if unsure.
  [unsure]      I don't know -- guide me
```

On `[unsure]`: say `Print one test page single-sided first, hold it up to a light source with the printed side toward you, then flip it left-to-right like a book page. If the back of the sheet (now facing you) would show the SAME orientation as if you'd just flipped a book page, that's long-edge -- the common default. If your printer's settings mention "flip on short edge" or "calendar flip," pick short-edge instead.` and default the layout to `long-edge` (the more common default) unless corrected.

**Get this wrong and the deck misprints — see the derivation below before changing this logic.**

#### Grid geometry and the mirror transform

Layout: US Letter or A4 (ask which, default Letter), portrait, a fixed grid of index-card-sized cells — 2 columns × 4 rows (8 cards/page) fits a standard 3×5 index card size with margin; use this as the default grid unless the card content is unusually long, in which case drop to 2×3 (6 cards/page) rather than shrinking text below readable size.

Pages come in **front/back pairs**: page 1 = fronts for cards 1-8, page 2 = backs for cards 1-8 (to be printed on the reverse of page 1's physical sheet), page 3 = fronts for cards 9-16, page 4 = backs for cards 9-16, and so on.

**The back page's card order is NOT the same as the front page's.** It must be transformed per the chosen duplex convention, derived geometrically (not guessed) as follows — R = grid rows, C = grid columns, 0-indexed positions:

- **Long-edge flip** (mirrors about the sheet's VERTICAL center line): a card at front position `(row r, col c)` must be printed on the back page at `(row r, col C-1-c)`. **Rows unchanged, columns reverse.** This is the standard "flip like a book page" case and will be the default for most users.
- **Short-edge flip** (mirrors about the sheet's HORIZONTAL center line): a card at front position `(row r, col c)` must be printed on the back page at `(row R-1-r, col c)`. **Columns unchanged, rows reverse.**

*Derivation, for anyone re-verifying this later:* model the sheet as a coordinate plane, front content at position `x` becomes visible at `(sheet_width - x)` after a 180° rotation about the vertical center line (long-edge case; substitute height/vertical-axis for short-edge). Solving for what must be printed at each back-page position to land under the matching front position gives exactly the column-reversal (long-edge) / row-reversal (short-edge) rule above. This was verified with a coordinate simulation, including the degenerate single-row case (short-edge flip on a 1-row grid correctly produces no change, since there's nothing to reverse) — do not re-derive this from intuition alone if revisiting; re-run the same coordinate check.

Applying the transform: build the front grid in normal reading order (card 1 at `(0,0)`, card 2 at `(0,1)`, ... wrapping to the next row), then build the back grid by placing each card at its transformed position per the rule above, so that page N+1 (the back) — printed on the reverse of page N's physical sheet — lines up correctly once flipped.

#### Card content and cut guides

- Each cell: the term (front) or definition + use case (back), centered, font size scaled to fit the cell without truncation — if content doesn't fit at a readable minimum size, drop to the smaller grid (2×3) for that card's page rather than shrinking text further.
- Draw a thin dashed border around every cell as a cut guide.
- Add a one-line footer on the PDF's first page (front-page 1 only, not repeated) stating the chosen duplex convention and grid size, so the physical printout carries a record of how it was generated.

#### PDF generation

Generate via a Python script using `reportlab` (install via pip if missing, same pattern as `genanki`/`mistune` in the APKG step) — reportlab gives precise point-level page-layout control, which HTML-to-PDF conversion does not reliably provide across print drivers, and precision is exactly what this feature depends on. Write to `{tutorials_dir}/flashcards-print-<ISO-date>.pdf`.

#### Verification caveat — say this explicitly, every time

After generating the PDF, always include this line in the output, not as an optional aside:

> ⚠️ This layout is generated from a geometric derivation, not verified against an actual printed-and-cut sheet. Print and cut ONE test page before running a full deck through your printer — confirm the flip actually lines up front-to-back for your specific printer's duplex behavior before committing paper/ink to the rest.

Do not omit this caveat even on repeat exports once "verified once" — a different printer, different duplex setting, or different paper size changes the physical behavior being relied on.

### Why this doesn't write to vocabulary.yaml

Flashcard export is a *read* of the vocabulary, not a learning event. Unlike `vocab review` (which appends to `test_history` and can change `status`), running `vocab flashcards` — or later studying the exported deck in Anki — does not feed back into tutorial-creator's own spaced-repetition state. Anki has its own SRS scheduling; tutorial-creator's `test_history` stays the source of truth for *this* skill's state machine. Keeping them separate avoids two systems fighting over one term's mastery state.

---

## `vocab list [--status=<status>] [--source=<match>] [--date=<YYYY-MM-DD>] [--date-from=<YYYY-MM-DD>] [--date-to=<YYYY-MM-DD>]`

### Procedure

1. **Read vocabulary.yaml.**
2. **Filter by status** if `--status` flag is set. Valid values: `new`, `reviewing`, `mastered`, `confused`. Invalid value → list all and warn.
3. **Filter by source** if `--source=<match>` is set. Case-insensitive substring match against three fields, in order, first hit wins: `first_encountered.context`, `first_encountered.source_file`, `notes`. This covers every shape a source takes today — a `vocab ingest`/`vocab add` context string (e.g. `"session transcript, 2026-08-31"`, `"vocab ingest"`, `"external source"`), an in-project file path, or a URL folded into `notes` (per the `vocab ingest` procedure's citation handling, and Entry [f]'s `external source` context). `--source=stuffolio.app` matches a file-path source; `--source=iosweeklybrief.com` matches a URL folded into notes; `--source=session` matches any session-transcript ingest regardless of date.
4. **Filter by date** if any of `--date`, `--date-from`, `--date-to` are set. Matches against `first_encountered.date`.
   - `--date=<YYYY-MM-DD>` — exact match only. Mutually exclusive with `--date-from`/`--date-to`; if both forms are passed, `--date` wins and the range flags are ignored with a warning: `--date and --date-from/--date-to both set; using --date, ignoring the range.`
   - `--date-from=<YYYY-MM-DD>` alone — everything on or after.
   - `--date-to=<YYYY-MM-DD>` alone — everything on or before.
   - Both `--date-from` and `--date-to` — inclusive range.
   - Malformed date (not `YYYY-MM-DD`) → warn and ignore that flag, continue with any other filters still set: `--date value "<value>" isn't YYYY-MM-DD; ignoring.`
5. **Filters compose.** `--status`, `--source`, and the date filters all narrow the same result set together (AND, not OR) — `vocab list --source=stuffolio.app --date-from=2026-08-01` means "from that source AND added since August."
6. **Sort** alphabetically by `term` (case-insensitive).
7. **Render as a table:**
   ```
   Vocabulary  (N terms total · showing N matching filter)

   ┌──────────────────────┬───────────────────┬───────────┬──────────────┐
   │ Term                 │ Type              │ Status    │ Last test    │
   ├──────────────────────┼───────────────────┼───────────┼──────────────┤
   │ @MainActor           │ swift-attribute   │ mastered  │ 2026-04-28   │
   │ actor isolation      │ concept           │ confused  │ 2026-05-04   │
   │ guard let            │ swift-keyword     │ reviewing │ 2026-04-15   │
   │ ...                  │                   │           │              │
   └──────────────────────┴───────────────────┴───────────┴──────────────┘

   Run vocab show <term> for full details.
   ```
   When any of `--source`/`--date`/`--date-from`/`--date-to` narrowed the result, name the active filter(s) in the header line so it's clear what's being shown: `Vocabulary  (221 terms total · showing 14 matching source="session" date=2026-08-31)`.
8. **Empty state** (zero terms, or zero terms matching the combined filter): `Your vocabulary is empty. Start with: vocab add <term>` (no terms at all) or `No terms match that filter.` (terms exist, none match).

### Truncation

If a term name is longer than 20 characters, truncate with `...` in the table cell. The full term is always available via `vocab show`.

### Why source/date filter on existing fields, not new ones

`first_encountered.source_file`, `first_encountered.context`, and `first_encountered.date` are already required fields on every entry (Schema 2) — every term has always carried this data, it just wasn't queryable as a first-class filter until now. No schema change was needed; this is a read-side addition only.

---

## `vocab show <term>`

### Procedure

1. Read vocabulary.yaml.
2. Find term (case-insensitive). If not found: `"<term>" not in vocabulary. List all with: vocab list`.
3. Render full record:
   ```
   Term:        @MainActor
   Type:        swift-attribute
   Status:      mastered
   First seen:  Sources/Models/AppSchema.swift:42 (Day 5 tutorial, 2026-04-01)

   Definition:
     Property wrapper that constrains a type or method to run on the main thread.

   Use case:
     Applied to a ViewModel class so every property/method touching UI state
     is guaranteed to run on the main thread, without manually dispatching.

   Related terms:    actor, Sendable, isolation, nonisolated

   Test history (3 entries):
     2026-04-05  correct  Day 5 post-test
     2026-04-12  correct  Day 8 pre-test
     2026-04-28  correct  vocab review

   Applied test history (post-test grading; reserved for v2.x):  empty

   Notes:
     Earned mastered via 3 consecutive correct results.
   ```

Omit the "Use case:" block entirely when `use_case` is empty — most terms added before this field existed have none, and an empty labeled block reads as broken rather than absent.

### Multi-match handling

If `<term>` is ambiguous (multiple case-insensitive matches), show a numbered list and prompt the user to pick.

---

## `vocab edit <term>`

### Editable fields

- `definition`
- `use_case`
- `type`
- `related_terms`
- `notes`
- `first_encountered.source_file` (sometimes the user wants to update this when a better example surfaces)

### Non-editable fields

- `term` — to rename, use `vocab merge <old> <new>` (which is technically a rename + merge if `<new>` already exists).
- `status` — earned through tests. The only manual transition is via the `--reset-mastery` flag (see below).
- `test_history` and `applied_test_history` — never user-editable. If a test result needs correction, edit the file by hand (and accept the consequences).
- `first_encountered.context` and `first_encountered.date` — historical record; preserved.

### Procedure

1. Read vocabulary.yaml; find the term (case-insensitive).
2. Show current values for editable fields; allow user to update each one. AskUserQuestion per field, or one big prompt with default-values pre-filled.
3. **Recompute status** — only if `--reset-mastery` flag was passed AND current status is `mastered`:
   - Set status to `reviewing`
   - Append no new test_history entry
   - Print: `Reset mastered status for "<term>". Status now: reviewing. Mastered status will be re-earned through correct test results.`
4. Write back to vocabulary.yaml.
5. Regenerate VOCABULARY.md.

### Refuse `--reset-mastery` on non-mastered

If `--reset-mastery` is passed on a term whose status isn't `mastered`, refuse:
```
"<term>" is not currently mastered (status: <status>). --reset-mastery only applies to mastered terms.
```

---

## `vocab merge <term-a> <term-b>`

Used to collapse duplicates (`@Observable` and `Observable macro`) or to consolidate similar concepts. Destructive — confirms before write.

### Procedure

1. Read vocabulary.yaml; find both terms (case-insensitive). Refuse if either is missing.
2. **Show preview:**
   ```
   Merge preview:

   Source (will be deleted):     <term-b>
     status: <b_status>, test_history: <N> entries

   Target (will be updated):     <term-a>
     status: <a_status>, test_history: <M> entries

   After merge:
     term:               <term-a>     (target keeps its name)
     definition:         <a_definition>     (target keeps its definition)
     status:             <recomputed>     (recomputed from merged history)
     test_history:       <M+N> entries
     applied_test_history: <combined>
     related_terms:      <a_related ∪ b_related, deduped>
     notes:              <a_notes>
                         ---
                         (merged from <term-b>)
                         <b_notes>

   Proceed? [y/n]
   ```
3. **On confirm:**
   - Concatenate `test_history` (target's first, then source's, sorted by date)
   - Concatenate `applied_test_history` similarly
   - Union `related_terms`; remove `<term-a>` and `<term-b>` from the result if they appear (a term shouldn't be related to itself)
   - Concatenate `notes` with separator
   - **Recompute status** from the merged `test_history` (apply state-machine rules)
   - Update target term's record; remove source term from yaml
   - Update any other vocabulary entries that reference `<term-b>` in their `related_terms` to point at `<term-a>` instead
   - Regenerate VOCABULARY.md
4. **On cancel:** stop. No file written.

### Edge case: merging into a `mastered` target

If target is `mastered` but source has recent partial/wrong test results, the recomputed status may downgrade to `reviewing` or `confused`. This is correct: the merged history represents the user's actual command of the concept. Surface this in the preview:
```
Note: Target is currently mastered, but source has 2 partial results from
the last 3 tests. Recomputed status will be: reviewing.
```

---

## `vocab review [--strict]`

Spaced-repetition test session. Prioritizes confused and stale terms, lenient grading by default.

### Selection logic

Pick 5 terms (or fewer if vocabulary has < 5 terms). Priority tiers:

1. **Tier 1: confused** — terms with `status: confused`. If more than 5 exist, pick the 5 with the longest staleness (most-stale first). If 5 confused exist, fill the slate entirely from this tier.
2. **Tier 2: due for review** — terms with `status: reviewing` whose last `test_history` entry is older than 14 days (or never tested). Fill remaining slots with most-stale-first ranking.
3. **Tier 3: random reviewing** — randomly pick from `status: reviewing` regardless of staleness.
4. **Tier 4: random new** — randomly pick from `status: new`. (Including new terms in review pulls them into the test loop and progresses status from `new` → `reviewing`.)

### Procedure

For each selected term:

1. **Prompt:**
   ```
   [<index>/<total>] What is "<term>"?

   Type your definition (or "skip" to skip, "stop" to end session):
   > _
   ```
2. **Read user's answer.**
3. **Grade:**
   - **Lenient (default):** matches if the user's answer captures the concept, even with different wording. Specifically, the answer must contain the key concept-words from the stored definition (or close synonyms). AI compares the user's answer to the stored definition and assigns one of three results:
     - `correct` — captures the concept's central idea
     - `partial` — captures part of the concept but misses a key element
     - `wrong` — doesn't match or is misleading
   - **Strict (`--strict` flag):** requires verbatim or near-verbatim match. Word-level similarity threshold > 80%. Only `correct` or `wrong` (no partial).
4. **Show result with explanation:**
   ```
   Result: <result>

   Stored definition:
     <definition>

   Your answer:
     <user's answer>

   <one-sentence explanation of why the result was assigned>
   ```
5. **Append to `test_history`** with:
   - `date`: today
   - `result`: graded result
   - `source`: `vocab review` (or `vocab review --strict`)
6. **Recompute status** per state machine.

### After all terms

Show summary:
```
Review session complete.

Tested:    5 terms
Results:   3 correct, 1 partial, 1 wrong

Status changes:
  guard let: reviewing -> mastered (3 consecutive correct)
  actor isolation: confused -> reviewing (1 correct)

Next review available: in N days, or run vocab review again to re-pick.
```

Save vocabulary.yaml; regenerate VOCABULARY.md.

### Stop / skip semantics

- `skip` — current term is skipped; no test_history entry added; session continues with the next term
- `stop` — session ends immediately; results so far are saved (test_history entries committed); status recomputed for tested terms only

### Edge case: vocabulary has < 5 terms

Prompt: `Your vocabulary has only N terms. Review all N? [y/n]`. If yes, run as above with N terms. If no, stop.

### Edge case: zero terms in tier 1-2

If no confused terms and no stale reviewing terms, prompt: `No terms are due for review or confused. Test recently-added terms anyway? [y/n]`. If yes, fall through to tiers 3-4.

---

## `vocab gap`

Read-only view of confused terms, ranked by staleness. Feeds tutorial entry [e] (gap-driven).

### Procedure

1. Read vocabulary.yaml.
2. Filter `status: confused`.
3. For each, compute staleness: days since the most recent `test_history` entry (or since `first_encountered.date` if test_history is empty — but a confused term should always have test history; treat absent test_history as a yaml inconsistency and warn once).
4. Sort by staleness (longest-confused first).
5. **Render:**
   ```
   Confused terms (4):

     1. actor isolation         confused 18 days   (last test: 2026-04-21, partial)
     2. nonisolated(unsafe)     confused  9 days   (last test: 2026-04-30, wrong)
     3. consume                 confused  7 days   (last test: 2026-05-02, partial)
     4. SchemaMigrationPlan     confused  5 days   (last test: 2026-05-04, wrong)

   Generate a tutorial for one of these? [1-4 / no]
   ```
6. **On selection:** route to tutorial entry [e] (gap-driven) — see `SKILL.md` § `Entry [e] — Gap-driven`. The chosen term becomes the topic; that entry's procedure takes over from its step 3 (file-finding), since the term has already been selected here.
7. **On `no` or empty input:** stop without action.

### Empty state

If no confused terms: `No confused vocabulary right now. Run vocab review to test what you've learned.`

---

## `vocab regen-md [--import]`

Regenerate `VOCABULARY.md` from `vocabulary.yaml`. Used as a manual safety net after editing yaml by hand, or as a one-time migration from v1.1.

### Without `--import` (default)

1. Read vocabulary.yaml.
2. Generate VOCABULARY.md per the template in SKILL.md ("VOCABULARY.md template (generated view)"), grouping terms by `first_encountered.context`:
   - Group 1: terms with context starting `Day N tutorial` (sorted by day number)
   - Group 2: terms with context `vocab add` (sorted by date added)
   - Group 3: terms with context `vocab review` (rare; means added during a review session)
   - Group 4: terms with context `external source` or `vocab ingest` or starting `session transcript` (sorted by date) — these three all mean "batch-ingested from a non-project source" and share a group; the distinction between them lives in each term's `notes` field, not the grouping
3. Write VOCABULARY.md atomically (write to `.tmp` file, then rename).
4. Print: `Regenerated VOCABULARY.md from N terms in vocabulary.yaml.`

### With `--import`

One-time migration from v1.1 Markdown table to v2 yaml. Used by users who shipped tutorials under v1.1 and now need to migrate.

1. Refuse if `vocabulary.yaml` already exists with non-empty content. Tell the user: `vocabulary.yaml already has N entries. Migration would overwrite. Back up vocabulary.yaml first if you want to proceed.`
2. Read existing `VOCABULARY.md`.
3. Parse out per-tutorial sections (header pattern `## Day N: <Topic>`); for each, parse the `| Term | Quick Definition |` table that follows.
4. For each row, build a yaml entry:
   - `term`: cell 1
   - `definition`: cell 2 (single-line; user can polish later)
   - `type`: heuristic (swift-keyword if matches the Swift keyword list at the bottom of this file; else `concept`)
   - `first_encountered.source_file`: empty (not recoverable from v1.1 Markdown)
   - `first_encountered.context`: `Day <N> tutorial` (from section header)
   - `first_encountered.date`: looked up from PROGRESS.md Score Log row for Day N if available; else today
   - `status`: `reviewing` (no test history exists in v1.1)
   - `test_history`: `[]`
   - `applied_test_history`: `[]`
   - `related_terms`: `[]`
   - `notes`: `Migrated from v1.1 VOCABULARY.md.`
5. Write vocabulary.yaml.
6. Regenerate VOCABULARY.md (without `--import` this time, to verify the round-trip).
7. Print: `Migrated N terms from VOCABULARY.md to vocabulary.yaml. Review with: vocab list`.

### Error handling

If yaml is malformed: refuse with `vocabulary.yaml is malformed: <error>. Fix the yaml; this command does not write back.`

If VOCABULARY.md doesn't exist (during `--import`): refuse with `No VOCABULARY.md to import from.`

---

## `vocab undo`

24-hour soft-stage reversal of the last *standalone* `vocab add` or `vocab ingest` (an invocation that wasn't part of a tutorial generation). Tutorial-time vocab adds are reverted by the broader session-log undo (`/skill tutorial-creator undo`); see `SKILL.md` § Recovery for that path.

### Marker file shape

A `vocab add` marker contains one term name (single-term add). A `vocab ingest` marker contains a **list** of term names — one marker per ingest batch, not one per term, so undoing an ingest reverts the whole batch as a unit rather than requiring N separate undos. Both shapes live in the same `<tutorials_dir>/vocabulary.yaml.add-<ISO-timestamp>` naming scheme; the procedure below handles either.

### Procedure

1. List soft-stage markers: `<tutorials_dir>/vocabulary.yaml.add-<ISO-timestamp>` files.
2. Filter to those within 24 hours of now.
3. **No markers in window:** `No vocab add or vocab ingest to undo within the last 24 hours. (For tutorial-time adds, use /skill tutorial-creator undo instead.)`
4. **One marker:** show details — term name (single-add) or the full term list + count (ingest batch) — and when added; prompt confirm. On yes, remove the term(s) from vocabulary.yaml + delete the marker; regenerate VOCABULARY.md.
5. **Multiple markers:** show a numbered list — each row labeled `<term>` for a single add or `<N> terms from vocab ingest (<source>)` for a batch — user picks which to undo (or `cancel`). Only one marker is undone per invocation; run `vocab undo` again for another.

Markers older than 24h are silently pruned at the start of any vocab subcommand.

### Why two undo paths

Tutorial generation is reversible as a unit: snapshots of vocabulary.yaml + PROGRESS.md + VOCABULARY.md + tutorial-config.yaml are taken before the generation runs, and `/skill tutorial-creator undo` restores them. Standalone vocab adds don't get a snapshot (they're a single-line yaml change with no ripple effect), so the 24h sentinel is the simpler approach. Both surfaces are user-facing; the skill chooses which one applies based on whether a session yaml exists for the change.

---

## State machine — full specification

Per `SCHEMAS.md` Schema 2:

```
new ──any test──► reviewing
                      │
       ┌──3 consecutive correct──► mastered ──manual reset──► reviewing
       │
       └──2 of last 3 partial/wrong──► confused
                                          │
                                          └──1 correct──► reviewing
```

### Status recomputation algorithm

Run after every `test_history` append (in `vocab review`) and after every `vocab merge`.

```
1. If test_history is empty:                    status = "new"
2. Else look at last 3 entries (or fewer if test_history shorter):
   a. If all 3 are "correct":                   status = "mastered"
   b. Else if 2 or more are "partial" or "wrong":  status = "confused"
   c. Else:                                     status = "reviewing"
3. Manual mastered -> reviewing override (via `vocab edit --reset-mastery`)
   wins until the next test result lands.
```

### Why no manual `mastered`

The user can claim mastery, but the system can't validate it without test results. Allowing manual `mastered` introduces wishful thinking — terms that the user *thinks* they know but tests would prove otherwise. The state machine forces tests to be the gate, which keeps the `mastered` count honest.

The one allowed manual transition is `mastered → reviewing` (the user notices they've forgotten something and demotes their own mastery). The reverse is not symmetric: getting back to mastered requires re-earning it through tests.

### `confused → reviewing` (single correct)

The asymmetry is deliberate: getting confused requires repeated wrong/partial results (2 of 3); recovering from confused requires only 1 correct. This biases the system toward "give the user the benefit of the doubt when they show progress." Without this bias, users could get stuck in `confused` indefinitely after one bad streak.

If they then get another partial/wrong, the recomputation puts them back to `confused` because the test_history still has the older partials. This is correct: the state reflects the actual track record, not just the latest result.

---

## Lenient vs strict grading — algorithm

Default is lenient (per design decision D3, ratified 2026-05-09). `--strict` flag enforces verbatim matching.

### Lenient grading

Compare user's answer to the stored definition. Result is one of:

- **`correct`** — captures the central concept. Specifically, all of:
  - At least one key concept-word from the definition appears (literal or close synonym)
  - The user's answer doesn't introduce a contradiction or misconception
  - Length-appropriate (not just a single word that happens to match)
- **`partial`** — captures part of the concept. Specifically:
  - Some key concept-words appear, but a load-bearing element is missing
  - OR the answer is correct but oversimplified (misses a critical edge case mentioned in the definition)
  - OR the answer is correct but for a *related* concept, not the term being tested
- **`wrong`** — doesn't capture the concept, or contradicts it

The grading is performed by Claude (the runtime LLM) at test time. When in doubt between `correct` and `partial`, prefer `partial`. When in doubt between `partial` and `wrong`, prefer `partial` (the user gets credit for trying).

### Strict grading

- **`correct`** — word-level similarity > 80% with the stored definition. Synonyms not credited.
- **`wrong`** — anything else.
- No `partial` tier.

The strict mode exists for users who want to drill verbatim definitions (e.g., preparing for technical interviews). It is not the default because writing-to-learn is the audience and rewarding concept comprehension reinforces it.

---

## Round-trip with VOCABULARY.md

`VOCABULARY.md` is **always** a generated view of `vocabulary.yaml`. v2 never reads from VOCABULARY.md as a source. Operations that modify yaml always regenerate the Markdown view at the end:

- `vocab add` → regen
- `vocab edit` → regen
- `vocab merge` → regen
- `vocab review` → regen (status changes invalidate the old view)
- `vocab undo` → regen
- `vocab regen-md` → explicit regen

Read-only operations don't touch the Markdown:

- `vocab list` — reads yaml directly
- `vocab show` — reads yaml directly
- `vocab gap` — reads yaml directly

If a user edits `vocabulary.yaml` by hand (legitimate use case), they should run `vocab regen-md` afterwards to keep the Markdown in sync. The skill doesn't auto-detect yaml changes; that would require filesystem watching, which is out of scope.

If a user edits `VOCABULARY.md` by hand, those edits will be lost on the next regen. Refuse to support this case; the Markdown is generated.

---

## Swift keyword list (for `vocab regen-md --import` heuristic)

Used to set `type: swift-keyword` during v1.1 import:

```
associatedtype, async, await, break, case, catch, class, continue, defer,
deinit, do, else, enum, extension, fallthrough, false, fileprivate, final,
for, func, guard, if, import, in, inout, internal, is, lazy, let, mutating,
nil, nonisolated, open, operator, optional, override, private, protocol,
public, repeat, required, rethrows, return, self, Self, sendable, static,
struct, subscript, super, switch, throw, throws, true, try, typealias, var,
weak, where, while
```

Terms matching `^@\w+$` are typed `swift-attribute` (e.g., `@MainActor`, `@Observable`).

For other languages, the import heuristic falls back to `concept` for everything — the user can `vocab edit <term>` to set a more specific type. v2.0 only ships the Swift keyword heuristic because Stuffolio is the demo and v1.1 was Swift-only in practice.

---

## Implementation notes

This file is the spec; the runtime LLM follows the procedures above when the user invokes a `vocab <subcommand>`. There is no separate vocab "executable" — the skill's behavior is the LLM faithfully executing this spec against the user's vocabulary.yaml.

This file's job is the spec for the vocab surface itself. The broader session-log recovery system lives in `SKILL.md` § Recovery; tutorial-time vocab adds are reverted via that path. Standalone vocab adds (this file) keep the 24h sentinel approach.

### Honesty rule (cross-cutting)

When the user asks about a term and the system can answer authoritatively from the yaml (status, test history, definition), give the authoritative answer. When the system has to draft (an AI-drafted definition during `vocab add`, a grading judgment during `vocab review`), say so explicitly. Don't blur the line between "this is what your record says" and "this is my best guess."

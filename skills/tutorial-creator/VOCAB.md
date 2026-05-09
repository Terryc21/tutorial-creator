# Vocab Surface — tutorial-creator v2

**Status:** Phase 4 implementation. Full vocab surface with state machine, review, and gap radar.
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
| `vocab list [--status=<s>]` | Browse the full vocabulary |
| `vocab show <term>` | Full record for one term |
| `vocab edit <term>` | Update fields (definition, type, related_terms, notes) |
| `vocab merge <a> <b>` | Collapse duplicates |
| `vocab review [--strict]` | Spaced-repetition test session |
| `vocab gap` | Show terms with `status: confused`, ranked by staleness |
| `vocab regen-md` | Regenerate VOCABULARY.md from vocabulary.yaml |
| `vocab undo` | Revert last `vocab add` (within 24h soft-stage; Phase 6 wires the broader undo) |

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
     Source file (optional): _
     Context:    vocab add
     Related terms (suggested): <list of 2-4 related terms from existing vocabulary>

     Accept this draft? [y / edit / cancel]
     ```
   - **Source file** — optional. User can paste a file path, optionally with `:line` suffix.
   - **Related terms** — AI suggests by scanning existing vocabulary.yaml for terms with similar tags, types, or vocabulary near the new term. User accepts, edits, or clears.
4. **On confirm:**
   - Append a new entry to vocabulary.yaml per Schema 2:
     ```yaml
     - term: "<term>"
       type: <type>
       definition: |
         <definition text>
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
   - Write a 24h soft-stage marker file: `<tutorials_dir>/vocabulary.yaml.add-<ISO-timestamp>` containing the term name. Used by `vocab undo` (within 24h).
   - Regenerate VOCABULARY.md.
   - Print confirmation: `Added "<term>" (status: new). Undo within 24h via: /skill tutorial-creator vocab undo`
5. **On `edit`:** drop into editable interactive editor for the four AI-drafted fields, then return to step 4.
6. **On `cancel`:** stop. No file written.

### Error handling

- If user provides a `source_file` path that doesn't exist in the project, warn but allow (user might be referring to an external file).
- If `vocabulary.yaml` is malformed (yaml parse error), refuse to write. Tell the user: `vocabulary.yaml is malformed: <error>. Run vocab regen-md or fix manually.` Do not corrupt the file with a partial append.

---

## `vocab list [--status=<status>]`

### Procedure

1. **Read vocabulary.yaml.**
2. **Filter** by status if `--status` flag is set. Valid values: `new`, `reviewing`, `mastered`, `confused`. Invalid value → list all and warn.
3. **Sort** alphabetically by `term` (case-insensitive).
4. **Render as a table:**
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
5. **Empty state** (zero terms): `Your vocabulary is empty. Start with: vocab add <term>`.

### Truncation

If a term name is longer than 20 characters, truncate with `...` in the table cell. The full term is always available via `vocab show`.

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

   Related terms:    actor, Sendable, isolation, nonisolated

   Test history (3 entries):
     2026-04-05  correct  Day 5 post-test
     2026-04-12  correct  Day 8 pre-test
     2026-04-28  correct  vocab review

   Applied test history (post-test grading; reserved for v2.x):  empty

   Notes:
     Earned mastered via 3 consecutive correct results.
   ```

### Multi-match handling

If `<term>` is ambiguous (multiple case-insensitive matches), show a numbered list and prompt the user to pick.

---

## `vocab edit <term>`

### Editable fields

- `definition`
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

Read-only view of confused terms, ranked by staleness. Feeds tutorial entry [3e] (gap-driven, Phase 3def).

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
6. **On selection:** route to tutorial entry [3e] (gap-driven). Phase 3def implements the entry; for now, route stub returns: `Entry [e] gap-driven coming in Phase 3def.`
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
   - Group 4: terms with context `external source` (sorted by date)
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

24-hour soft-stage reversal of the last `vocab add`. Phase 6 wires this into the broader undo system; Phase 4 ships the local-only version.

### Procedure

1. List soft-stage markers: `<tutorials_dir>/vocabulary.yaml.add-<ISO-timestamp>` files.
2. Filter to those within 24 hours of now.
3. **No markers in window:** `No vocab add to undo within the last 24 hours.`
4. **One marker:** show details (term name, when added) and prompt confirm. On yes, remove the term from vocabulary.yaml + delete the marker; regenerate VOCABULARY.md.
5. **Multiple markers:** show a numbered list, user picks which to undo (or `cancel`).

Markers older than 24h are silently pruned at the start of any vocab subcommand.

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

## Phase 4 implementation notes

This file is the spec; the runtime LLM follows the procedures above when the user invokes a `vocab <subcommand>`. There is no separate vocab "executable" — the skill's behavior is the LLM faithfully executing this spec against the user's vocabulary.yaml.

Phase 4's job is the spec. Phase 6 wires `vocab undo` into the broader session-log undo system; until then, vocab add's 24h soft-stage is the only undo mechanism.

### Honesty rule (cross-cutting)

When the user asks about a term and the system can answer authoritatively from the yaml (status, test history, definition), give the authoritative answer. When the system has to draft (an AI-drafted definition during `vocab add`, a grading judgment during `vocab review`), say so explicitly. Don't blur the line between "this is what your record says" and "this is my best guess."

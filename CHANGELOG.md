# Changelog

All notable changes to `tutorial-creator` are documented here. This project adheres to [Semantic Versioning](https://semver.org/) and the format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.1.0] — 2026-09-29

Adds batch vocabulary capture and flashcard export, and fixes several ways terms were lost or rewritten on their way into your vocabulary. Plugin installs stayed on 2.0.1 while these changes reached GitHub, because the plugin's version string didn't change. Updating the plugin now brings them in.

### Added

- **`vocab ingest <source>` adds many terms at once.** Give it a session transcript, a URL, a file, or pasted text. It drafts a definition and use case for each new term from how the source uses it, and you accept the batch in one confirmation instead of one prompt per term. `vocab undo` reverses the whole batch within 24 hours. It follows Entry [f]'s source rules: no guessing at a page it couldn't fetch, and no invented citation for pasted text.
- **`vocab flashcards` exports your vocabulary for study outside the skill**, as Markdown, an Anki package (`.apkg`), or a print-ready PDF. The PDF is laid out for two-sided printing. It asks which way your printer flips the sheet, so that after cutting, each card's term backs onto its own definition, and it tells you to print and cut one test page before printing a whole deck. `--count=N` picks the terms most worth practicing. Exporting never changes vocabulary.yaml.
- **Filter by source and date.** `vocab list` and `vocab flashcards` now take `--source=<match>`, `--date`, `--date-from`, and `--date-to` alongside `--status`, and the filters combine, so "flashcards from this article, from this week" is one command. The filters read fields every entry already has, so nothing needs migrating.
- **An optional `use_case` field** on vocabulary entries says when you'd reach for a term, next to the definition that says what it is. It prints on the back of flashcards. Existing entries leave it empty.
- **Entry [f] asks for a citation after a paste.** Pasted text used to reach the tutorial with no source, so nobody, including you later, could check the tutorial against it. The skill now asks for a public URL and puts it in the header without fetching it (the pasted text stays the content). If there is no URL, the tutorial says so instead of inventing one.
- **Entry [f] cites its source in PROGRESS.md and ends with a follow-up check suited to outside material.** The first time a source adds concepts under a phase heading, a one-line citation goes under that heading. In place of Entry [b]'s bridge-tutorial proposals, the skill offers more material only when the source skipped a concept your vocabulary marks `confused`, or when a claim is cheap to verify on the spot. Otherwise it says nothing.

### Changed

- **The README was rewritten** for the people the skill is for. New examples show the opening screen, a Day 22 tutorial written from a real incident, and a print-ready flashcard deck.

### Fixed

- **Terms from new tutorials now reach vocabulary.yaml.** Entries [a] through [e] updated only VOCABULARY.md, a leftover from 1.1 when that file held the vocabulary, and Entry [f] didn't say which file to write. Those terms never showed up in `vocab review`, `vocab list`, or flashcards, and rebuilding the view dropped them. Every entry point now appends its new terms to vocabulary.yaml with all required fields, reads the file back, and names any term that didn't save before calling the tutorial finished.
- **`vocab regen-md` updates VOCABULARY.md in place instead of rebuilding it.** Every vocab command that ended in a regen (`add`, `ingest`, `edit`, `merge`, `review`, `undo`) threw away what exists only in the view: section titles, Source lines, row order, and terms repeated under a later Day. Now it refreshes each term's definition from vocabulary.yaml, adds missing rows, and leaves the rest as written. A row whose term is no longer in vocabulary.yaml is listed for you to decide on, never removed silently, and when nothing needs changing the file is left byte-for-byte as it was. Each command now touches only its own rows, and `vocab review` doesn't touch the view at all. One thing still doesn't survive: a definition edited in VOCABULARY.md is replaced by the one in vocabulary.yaml, so change definitions with `vocab edit`.
- **Older VOCABULARY.md files update cleanly.** `vocab regen-md` reads sections placed below the Cumulative Count table instead of adding their terms a second time, puts a new Day section among the others in day order, and matches rows written in bold or backticks instead of adding a plain duplicate beside them.
- **Writes to vocabulary.yaml change only the lines involved.** `vocab edit`, `merge`, `review`, and `undo` didn't say how to save the file, which left a runtime free to reload and re-dump it. The data survived but the formatting didn't: on one real 4,638-line file, a default dump changed 8,161 diff lines. Each command now changes only its own lines, reads the file back, and restores it if the write failed.
- **Terms can be renamed.** `vocab edit` sent renames to `vocab merge`, which refuses when the new name doesn't exist yet, so a rename had no working path. `vocab edit` now changes the term itself, updates `related_terms` references and the term's rows in VOCABULARY.md, and suggests a merge when the new name is already taken.
- **Merging no longer demotes untested terms.** Merging two entries with no test history reset the result to `new`, so a `reviewing` term (where every term migrated from 1.1 starts) dropped back a step. With no test history, the status now stays as it was.
- **Entry [f] advances the day counter**, so the tutorial after an external-source one no longer reuses its Day number.
- **`tutorials_dir` resolves against the project root, never `.claude/`.** An ambiguous reading of the old wording once created a second vocabulary.yaml inside `.claude/`.

## [2.0.1] — 2026-08-09

A documentation and correctness patch. No new features; the surfaces, entry points, and schemas are unchanged from 2.0.0. Every item below was found by an audit pass over the shipped spec.

### Fixed

- **`vocab gap` selection now generates a tutorial.** Picking a confused term from the gap radar returned `Entry [e] gap-driven coming in Phase 3def` — a stub left over from the v2.0 build order, even though entry [e] shipped in v2.0.0. Selection now routes to the gap-driven entry as documented.
- **Manual install instructions produced a skill Claude Code couldn't load.** The README's `git clone` put `SKILL.md` two directories below `~/.claude/skills/`. Plugin install is now the documented primary path; the manual path clones the repo and symlinks `skills/tutorial-creator`.
- `NOTICE` carried the repo's pre-rename project name (`code-smarter`).
- **`renumber` no longer leaves `undo` broken.** Renaming a day rewrote references in PROGRESS.md, VOCABULARY.md, and other tutorials, but not the `output` path or `day_number` stored in retained session records. A later `undo` of that session looked for the pre-rename filename, hit the "already missing; skipping" branch, and reported success while leaving the tutorial on disk — and the status dashboard's "Last lesson" line read the stale day number. `renumber` now updates matching session records and shows those updates as a separate block in its confirmation diff. `undo` no longer skips a missing output silently: it looks for the same tutorial under another day number and asks before deleting.
- **Entry [f] no longer has an undefined path when a URL can't be fetched.** The spec named a web fetch tool but gave no branch for the tool being unavailable, the fetch failing, or permission being denied — leaving the runtime free to improvise, including generating a synthesis from what it guessed the page said. It now offers the file-path and paste source types instead, and is told explicitly not to generate from an unfetched URL.
- **The venue drift-check command in `venues/_schema.yaml` didn't work.** Its first match was the comment block documenting it, and it printed no venue names, so the numbers it emitted couldn't be attributed. Replaced with two commands that label each venue and show a venue's front-matter and calibration table together.

### Changed

- **Audience artifacts now say they aren't undoable at the point they're written.** Path 2 deliberately has no recovery hook (audience-facing artifacts carry no learning state to roll back), but that was documented author-side only. A user who learned that `undo` reverts generations could reasonably expect it to cover a Reddit post; it would instead revert their last tutorial. The write step now states this in one line.

- **Venue budget duplication is now a stated contract.** Each venue's length budget and honest-machine section name live in three places: `venues/_schema.yaml`, the venue file's front-matter, and the venue file's `## Length budget calibration` table. All three are kept — the front-matter makes a venue file reviewable standalone, and the calibration table pairs each tier with what changes at it. `_schema.yaml` is now documented as authoritative on conflict, each venue file carries a reciprocal edit warning, and `_schema.yaml` records a dependency-free drift check. All 18 copies verified in agreement 08/09/2026.

- **`--mode both` removed.** It was listed as a valid mode but no surface, routing rule, or session-log `mode` value ever existed for it (Schema 3 enumerates only `writing-to-learn | audience-facing`). Unknown `--mode` values now refuse with the valid list instead of falling through to the gateway. Use `--mode learn` or `--mode audience`; to produce both a lesson and an audience artifact from one source, run the two paths in sequence.

## [2.0.0] — 2026-05-10

A ground-up redesign that turns `tutorial-creator` from a single-mode tutorial generator into a three-surface learning workflow. v1.1 was a useful side-project; v2.0 is what it should have been from the start.

### Added

- **Three top-level surfaces**, gateway-mediated. Bare invocation now asks what you want to do (`[1]` write a tutorial for myself, `[2]` write a tutorial for others, `[3]` manage vocabulary, `[4]` inspect learning state). The `--mode learn|audience|both|vocab|status` flag skips the gateway.
- **Six writing-to-learn entry points**: `[a]` daily progression, `[b]` topic + file, `[c]` topic only (skill ranks candidate files by pedagogical fit), `[d]` question-led (with honest-machine ambiguity surfacing), `[e]` gap-driven (reads from vocab gap radar), `[f]` external source (fetches a public artifact and produces a writing-to-learn synthesis).
- **Audience-facing path** with five entry points (annotated source / incident-grounded / synthesized / external / documentation-grounded) that hand off to **six venue templates**: `reddit`, `book-chapter`, `apple-developer-article`, `medium`, `blog`, `repo-doc`. Each venue has its own voice register, length budget, and honest-machine section convention. Audience routing also asks for target audience (beginner / intermediate / senior / mixed), honest-machine opt-in, and length budget (S / M / L / X).
- **Vocabulary as a first-class object**. `vocabulary.yaml` is the source of truth; `VOCABULARY.md` is a regenerated view. Subcommands: `vocab add`, `list`, `show`, `edit`, `merge`, `review`, `gap`, `regen-md`, `undo`. Status state machine: `new → reviewing → mastered | confused`, with `mastered → reviewing` as the only allowed manual transition. Status is earned through tests, never user-set.
- **`vocab review`** — spaced-repetition test session. Picks 5 terms (confused > stale > random); grades leniently by default (`--strict` available). Each result appends to `test_history` and recomputes status.
- **`vocab gap`** — radar of confused terms, ranked by staleness. Feeds entry [e] gap-driven directly.
- **Status dashboard** (`/skill tutorial-creator status`) — read-only view: tutorials shipped, last lesson, streak, vocab counts by status, due-for-review count, gap radar, suggested next lesson combining vocab gap and progression. Cold-start state renders a friendly empty-state message instead of the dashboard scaffolding.
- **Recovery surface**: per-generation session log under `.claude/tutorial-sessions/`, snapshot save before generation, `undo` (revert most recent generation), `renumber <old> <new>` (rewrites Day-N filename and cross-references atomically), 24-hour soft-stage for `vocab add` with `vocab undo`. Last 10 sessions retained; older silently pruned.
- **Project resolution from any cwd**: `--project-dir` flag for one-shot override, `TUTORIAL_CREATOR_PROJECT_DIR` env var, ancestor walk from cwd (same model as `git status` finding `.git/`), registry at `~/.claude/tutorial-creator/registry.yaml`, and `open` / `forget` subcommands to manage registered projects.
- **Externalized progressions** for Swift, TypeScript, Python, and Rust under `progressions/<lang>.yaml`. Custom progressions go via `progression_override` in `tutorial-config.yaml`.
- **Schemas locked** in `SCHEMAS.md`: tutorial-config, vocabulary, session-log, progressions. Schema fields reserved for post-test scoring (populated null in v2.0; activated in a future release) so the data model can grow without a migration.
- **`vocabulary-example.yaml`** in `examples/` showing the v2.0 vocabulary format with all four status values represented.

### Changed

- Bare invocation no longer assumes tutorial-generation intent. The gateway question runs first; pass `--mode <surface>` to skip it.
- `VOCABULARY.md` is no longer the source of truth; `vocabulary.yaml` is. `VOCABULARY.md` is regenerated on demand from yaml via `vocab regen-md`. Direct edits to `VOCABULARY.md` will be overwritten the next time the view is regenerated.
- The legacy v1.1 invocation (`/skill tutorial-creator <topic> <source>`) still works and routes to writing-to-learn entry [b] with v1.1-compatible output.

### Migration from v1.1

After installing v2.0, run a one-time import to convert your existing `VOCABULARY.md` to the v2.0 `vocabulary.yaml` source of truth:

```
/skill tutorial-creator vocab regen-md --import
```

Migrated terms enter v2.0 with `status: reviewing` (no v1.1 test history exists to derive a status from). Use `vocab edit` to add types, `vocab merge` to collapse duplicates, and `vocab review` to start earning mastered status.

## [1.1.0]

Earlier history is in the git log. v1.1.0 was the last single-mode release before the v2.0 redesign.

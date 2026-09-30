# Changelog

All notable changes to `tutorial-creator` are documented here. This project adheres to [Semantic Versioning](https://semver.org/) and the format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.1.2] — 2026-09-30

### Fixed

- **Flashcards no longer show "Example:" twice.** The back of a card puts an "Example:" label in front of a term's use case. Some use cases already contain their own "Example:", so those cards read "Example: ... Example: ...". When the use case already has one, the card now shows it as written.

### Changed

- **The plugin listing and the skill's own description use plainer words.** They now say what the skill does for you (lessons from your own files, a quiz, remembered vocabulary, flashcards, help writing for other readers) instead of how it is built.
- **The command guide ([USAGE.md](USAGE.md)) reads more plainly, and four details now match the skill.** `vocab undo` undoes your last `vocab add` or `vocab ingest`, not any vocabulary change. Starts `[b]`, `[c]`, and `[f]` let you pick the topic and still record the lesson; they don't ignore your history. The page no longer says every example is Swift (the React hook example is TypeScript). `vocab add` and `vocab ingest` draft a note on when you'd use each word, not a code example.
- **The skill's own notes describe how a word's status changes in everyday words**, instead of calling it a "state machine." Wording only; nothing works differently.

## [2.1.1] — 2026-09-30

### Fixed

- **The command to start the skill now works.** The README, USAGE.md, and the skill's own messages said to type `/skill tutorial-creator`, which Claude Code doesn't recognize. If you installed tutorial-creator as a plugin, type `/tutorial-creator:tutorial-creator`. If you installed it by hand, type `/tutorial-creator`. You can also just ask in plain words. When the skill shows you a command, such as how to undo a change, it now uses the same form you started it with.

### Changed

- **The README uses plainer words** and corrects three details: the React hook example is TypeScript, not Swift; a word drops to confused when two of your last three answers are wrong or only half right; and pulling in vocabulary drafts a note on when you'd use each term, not a code example.

## [2.1.0] — 2026-09-29

Two new ways to use the terms you're learning, and fixes for several ways terms went missing or got scrambled. If you use tutorial-creator as a plugin, updating didn't pick these changes up until this release, because the version number hadn't changed. Update the plugin to get them.

### Added

- **`vocab ingest <source>` adds many terms at once.** Point it at a chat session, a web page, a file, or text you paste. It finds the terms worth learning, writes what each one means and when you'd use it, and lets you approve them all in one step instead of one at a time. `vocab undo` removes the whole batch within 24 hours. It follows the same rules as option `[f]`: it won't guess at a page it couldn't open, and it won't make up a source for pasted text.
- **`vocab flashcards` turns your vocabulary into flashcards**, as a text file, a deck for the Anki flashcard app (`.apkg`), or a PDF you print on both sides and cut into cards. The PDF asks how your printer flips the page, so each card's front and back line up after cutting, and it reminds you to print one test page first. `--count=N` picks the terms you most need to practice. Making flashcards never changes your vocabulary.
- **Choose which terms to list or study.** `vocab list` and `vocab flashcards` take `--source=` plus part of a source's name, to get only the terms from, say, one article. They also take `--date`, `--date-from`, and `--date-to` for terms from certain days. You can use them together. Your existing terms already have this information, so nothing needs converting.
- **Each term can say when you'd use it** (`use_case`), next to what it means. It shows on the back of your flashcards. Terms you already have simply leave it blank.
- **Pasted text keeps its source.** When you build a lesson from pasted text (option `[f]`), the skill asks where the text came from and puts that link at the top of the lesson, without re-downloading it. If there's no link, the lesson says so instead of making one up.
- **Lessons from outside sources note their source in your progress file**, and suggest a follow-up only when there's a clear reason: the source skipped a term your vocabulary marks as confused, or a claim is quick to check.

### Changed

- **The README was rewritten** for the people the skill is for, with new examples: the opening menu, a lesson built from a real problem, and a printable flashcard deck.

### Fixed

- **Terms from your lessons now show up everywhere.** Lessons made with options `[a]` through `[e]` saved their new terms only to `VOCABULARY.md`, left over from version 1.1, and option `[f]` didn't say where to save them. So quizzes, lists, and flashcards never saw those terms. Now every lesson saves its terms to `vocabulary.yaml`, checks that they saved, and tells you by name if any didn't.
- **`VOCABULARY.md` keeps your layout.** `vocab regen-md`, and the commands that run it (`add`, `ingest`, `edit`, `merge`, `review`, `undo`), used to rebuild the whole file, throwing away your section titles, source notes, the order of your terms, and terms repeated under a later day. Now they change only what needs changing, and if nothing needs changing, the file isn't touched. If a term appears in `VOCABULARY.md` but not in your vocabulary, the skill asks what to do instead of deleting it. Definitions still come from `vocabulary.yaml`, so change those with `vocab edit`.
- **Older `VOCABULARY.md` files update without duplicates**, including ones with sections below the count table or terms written in bold or code style. A new day's section goes in day order.
- **Saving your vocabulary no longer reformats the whole file.** The data was always kept, but one save could change thousands of lines that should have stayed the same. Now only the lines that changed are touched, and a failed save is undone.
- **You can rename a term.** `vocab edit` used to send you to `vocab merge`, which only works when the new name already exists. Now `vocab edit` renames the term everywhere it appears, and suggests a merge if the new name is taken.
- **Combining two terms keeps their progress.** `vocab merge` no longer sends an untested term from reviewing back to new.
- **Lessons from outside sources (option `[f]`) move you to the next day**, so your following lesson doesn't reuse the same day number.
- **Your vocabulary file stays in your tutorials folder**, never inside the hidden `.claude/` folder. Unclear wording once led to a second copy there.

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

# Changelog

All notable changes to `tutorial-creator` are documented here. This project adheres to [Semantic Versioning](https://semver.org/) and the format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

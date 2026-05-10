# tutorial-creator v2 — Data Schemas

This document is the source of truth for every persistent data shape v2 reads
or writes. SKILL.md, VOCAB.md, and STATUS.md all reference these schemas;
when a schema changes, update this file first, then the surfaces that touch it.

**Status:** v2.0 baseline. Versioned at the bottom of each schema.
**Last updated:** 2026-05-10 (Phase 6.5: Schema 5 added for cross-project registry; `$PROJECT_ROOT` clarified throughout).

---

## Files at a glance

| File | Purpose | Source of truth | Owner |
|---|---|---|---|
| `tutorial-config.yaml` | Per-project config (paths, language, level) | This file | User (created in setup) |
| `vocabulary.yaml` | All vocabulary entries with status + test history | This file | Generated; user can edit via `vocab edit` |
| `VOCABULARY.md` | Human-readable view of vocabulary.yaml | **Generated** from vocabulary.yaml | Never edit by hand |
| `PROGRESS.md` | Progression tracker, score log, mastery checklist | This file | Generated; user can edit narrative sections |
| `tutorial-sessions/<ts>.yaml` | Per-generation session record (for undo) | This file | Generated; never edit by hand |
| `progressions/<lang>.yaml` | Built-in language progressions | This file (skill repo) | Skill author; users override via config |
| `~/.claude/tutorial-creator/registry.yaml` | Cross-project registry (multi-project discovery) | This file (Schema 5) | Skill writes; user may edit by hand |

**File locations** (relative to `$PROJECT_ROOT`, the directory selected by `## Project resolution` in SKILL.md):

```
$PROJECT_ROOT/
├── .claude/
│   ├── tutorial-config.yaml
│   └── tutorial-sessions/
│       └── <ISO-timestamp>.yaml
└── {tutorials_dir}/                    (default: ./tutorials/)
    ├── PROGRESS.md
    ├── VOCABULARY.md                   (generated view)
    ├── vocabulary.yaml                 (source of truth)
    └── DayN-<Topic>-Annotated.md       (generated tutorials)

~/.claude/tutorial-creator/
└── registry.yaml                       (cross-project; Schema 5)
```

**`$PROJECT_ROOT` resolution.** `$PROJECT_ROOT` is determined by the discovery chain in SKILL.md `## Project resolution`. It is NOT always cwd. The skill walks the chain on every invocation: `--project-dir` flag → `TUTORIAL_CREATOR_PROJECT_DIR` env var → cwd's `.claude/tutorial-config.yaml` → ancestor walk → registry → first-run setup. All paths in this schemas document are relative to `$PROJECT_ROOT` unless otherwise stated.

---

## Schema 1 — `tutorial-config.yaml`

Created on first run. Per-project. v2 adds three fields beyond v1.1.

```yaml
schema_version: 2

# v1.1 fields (unchanged)
tutorials_dir: ./tutorials/
language: swift
framework: swiftui
project_dir: .
next_day: 1

# v2 fields
experience_level: intermediate          # beginner | intermediate | advanced
vocab_format: yaml-with-md-view         # yaml-with-md-view (only valid value in v2.0)
recovery_enabled: true                  # session log + undo

# Optional v2 field — point at custom progression yaml outside the skill
# When unset, skill uses progressions/<language>.yaml from the skill bundle
progression_override: null              # absolute path or null
```

### Field rules

- `schema_version`: integer. v2 writes `2`. v1.1 writes nothing (absence treated as `1`).
- `tutorials_dir`: relative path from project root, or absolute path. Skill creates if missing.
- `language`: lowercase string. Must match a `progressions/<lang>.yaml` filename or `progression_override` must be set.
- `experience_level`: one of `beginner`, `intermediate`, `advanced`. Default: `intermediate`.
- `next_day`: positive integer. Skill increments after each tutorial. Manual edit allowed (e.g., user resets to 1 after archiving).
- `recovery_enabled`: bool. When false, skill skips session log writes (smaller filesystem footprint, no undo available).

### v1.1 → v2 migration

v1.1 configs without `schema_version` are treated as v1. On first v2 invocation:
1. Read existing `tutorial-config.yaml`
2. Add v2 fields with defaults: `schema_version: 2`, `experience_level: intermediate` (or prompt), `vocab_format: yaml-with-md-view`, `recovery_enabled: true`
3. Write back; preserve all v1.1 fields verbatim

---

## Schema 2 — `vocabulary.yaml`

The first-class vocabulary store. Replaces `VOCABULARY.md` as source of truth.
`VOCABULARY.md` becomes a regenerable view.

```yaml
- term: "@MainActor"
  type: swift-attribute
  definition: |
    Property wrapper that constrains a type or method to run on the main thread.
  first_encountered:
    source_file: "Sources/Models/AppSchema.swift:42"
    context: "Day 5 tutorial"
    date: "2026-04-01"
  status: reviewing
  test_history:
    - { date: "2026-04-05", result: correct, source: "Day 5 post-test" }
    - { date: "2026-04-12", result: partial, source: "Day 8 pre-test" }
  applied_test_history: []
  related_terms: ["actor", "Sendable", "isolation"]
  notes: "Confused this with @MainActor.assumeIsolated for two weeks."
```

### Field rules

- `term` (required): string. Unique within vocabulary.yaml. Quote terms with leading `@`, `:`, or other yaml-special characters.
- `type` (required): one of `swift-keyword`, `swift-attribute`, `api`, `concept`, `pattern`, `idiom`, plus the language-specific equivalents for ts/python/rust (e.g., `ts-keyword`, `python-decorator`, `rust-trait`). New types can be added; this enum is informational, not enforced.
- `definition` (required): string. Multi-line yaml block scalar (`|`) preferred for readability.
- `first_encountered` (required): object with three sub-fields:
  - `source_file` (string, may be empty): file path with optional `:line` suffix
  - `context` (string): one of `"Day N tutorial"`, `"vocab add"`, `"review session"`, `"external source"`, or free-form
  - `date` (string): ISO date `YYYY-MM-DD`
- `status` (required): one of `new`, `reviewing`, `mastered`, `confused`. See state machine below.
- `test_history` (required, may be empty list): list of test results from `vocab review` sessions. Each entry: `{ date, result, source }`. `result` is one of `correct`, `partial`, `wrong`.
- `applied_test_history` (required, may be empty list): **reserved for UNFORGET S49** (post-test scoring). v2.0 leaves this empty. When S49 lands, tutorial post-test results that test this term get logged here, distinct from `test_history`.
- `related_terms` (optional, default `[]`): list of strings; should be other terms in this file.
- `notes` (optional, default `""`): free-form string. Multi-line block scalar OK.

### Status state machine

Status is **earned through tests**, not user-editable directly. The only manual transition is `mastered → reviewing` (user can reset mastery via `vocab edit --reset-mastery <term>`).

```
new ──any test──► reviewing
                      │
       ┌──3 consecutive correct──► mastered ──manual reset──► reviewing
       │
       └──2 of last 3 partial/wrong──► confused
                                          │
                                          └──1 correct──► reviewing
```

### `result` semantics

- `correct`: matches the stored definition's concept (lenient by default)
- `partial`: captures part of the concept but misses a key element
- `wrong`: doesn't match or is misleading

The `--strict` flag for `vocab review` upgrades to verbatim matching; `correct` requires word-level accuracy.

### Status recomputation

After every test_history append (and on `vocab merge`), recompute status:

1. If test_history is empty → `new`
2. Else look at last 3 entries (or fewer if test_history is shorter):
   - All 3 are `correct` → `mastered`
   - 2+ of last 3 are `partial` or `wrong` → `confused`
   - Otherwise → `reviewing`
3. Manual `mastered → reviewing` overrides this only until the next test result lands.

### v1.1 → v2 migration

The bundled v1.1 example tutorials reference vocabulary as Markdown tables in
`VOCABULARY.md`. The migration script:

1. Parse v1.1 `VOCABULARY.md` (per-tutorial `## Day N: <Topic>` sections, each containing a `| Term | Quick Definition |` table)
2. For each row:
   - `term`: cell 1
   - `definition`: cell 2
   - `type`: heuristic (swift-keyword if matches Swift keyword list, else `concept`)
   - `first_encountered`: from the `## Day N: <Topic>` section header
   - `status`: `reviewing` (no test history exists in v1.1)
   - `test_history: []`
   - `applied_test_history: []`
   - `related_terms`: empty (could be inferred but not in v2.0 migration)
   - `notes`: empty
3. Write `vocabulary.yaml`; regenerate `VOCABULARY.md` from yaml
4. The user can rename, edit definitions, add `related_terms`, or merge duplicates after migration

This migration is invoked manually via `vocab regen-md --import` per the v2 README.

---

## Schema 3 — `tutorial-sessions/<ISO-timestamp>.yaml`

Session log written before each tutorial generation; consumed by `undo`.

```yaml
schema_version: 2
session_id: "2026-05-09T14-32-00"
mode: writing-to-learn                  # writing-to-learn | audience-facing
entry: gap-driven                       # gateway entry letter or name
gap_term: "actor isolation"             # populated when entry == gap-driven
file: "Sources/Managers/CloudSyncManager.swift"
day_number: 15
output: "tutorials/Day15-ActorIsolation-Annotated.md"
vocab_added:
  - "actor isolation"
  - "isolated"
  - "nonisolated"
  - "isolation domain"
progress_updated: true

# Snapshots for undo (paths relative to project root)
snapshots:
  - { path: "tutorials/PROGRESS.md", saved_to: ".claude/tutorial-sessions/2026-05-09T14-32-00/PROGRESS.md" }
  - { path: "tutorials/VOCABULARY.md", saved_to: ".claude/tutorial-sessions/2026-05-09T14-32-00/VOCABULARY.md" }
  - { path: "tutorials/vocabulary.yaml", saved_to: ".claude/tutorial-sessions/2026-05-09T14-32-00/vocabulary.yaml" }
  - { path: ".claude/tutorial-config.yaml", saved_to: ".claude/tutorial-sessions/2026-05-09T14-32-00/tutorial-config.yaml" }

# Reserved for UNFORGET S49 (deferred). v2.0 leaves all four null.
post_test_score: null                   # int correct
post_test_total: null                   # int total questions
score_band: null                        # "ready" | "review" | "re-read" | null
graded_at: null                         # ISO timestamp of self-grade entry
```

### Field rules

- `schema_version`: `2` for v2.0.
- `session_id`: ISO-8601 timestamp with `:` replaced by `-` (filesystem-safe).
- `mode`: which gateway path was taken.
- `entry`: which entry point under that path. Use the design-doc letter (`a`-`f`) or the human-readable name (`daily-progression`, `topic+file`, `topic-only`, `question-led`, `gap-driven`, `external-source`).
- `gap_term`: only populated when `entry == gap-driven`. Otherwise omit (yaml `null`).
- `file`: source file annotated, when applicable. Empty for synthesized examples.
- `day_number`: integer (whole or half-step like `7.5`).
- `output`: relative path of generated tutorial file.
- `vocab_added`: list of terms added to vocabulary.yaml as part of this generation.
- `progress_updated`: bool; whether PROGRESS.md was modified (false for some audience-facing modes).
- `snapshots`: list of pre-generation file snapshots; consumed by `undo`. v2.0 always includes the four files listed; future modes may add more.
- `post_test_*` and `graded_at`: **reserved for UNFORGET S49.** Stay `null` in v2.0.

### Retention

Last 10 sessions kept on disk. Older sessions silently pruned at the start of the next generation. Pruning deletes both the session yaml AND its corresponding snapshot directory under `.claude/tutorial-sessions/<id>/`.

---

## Schema 4 — `progressions/<lang>.yaml`

Built-in language progressions. Lives in the skill bundle, not the user project.
Users override via `tutorial-config.yaml#progression_override`.

```yaml
language: swift
framework: swiftui                      # optional; some languages don't need a framework

phases:
  - number: 1
    name: Utilities
    concepts:
      - optionals
      - guard let
      - closures
```

### Field rules

- `language` (required): lowercase. Should match the filename (`swift.yaml` → `language: swift`).
- `framework` (optional): lowercase. Used in tutorial header rendering.
- `phases` (required): list, ordered by `number`.
  - `number` (required): integer, 1-indexed, sequential.
  - `name` (required): human-readable phase name.
  - `concepts` (required): list of strings. Order is recommended-teaching-order; not enforced.

### Custom progressions

A user with a custom progression sets `progression_override: /absolute/path/to/my-progression.yaml` in `tutorial-config.yaml`. The custom file must conform to this same schema.

---

## Schema 5 — `~/.claude/tutorial-creator/registry.yaml`

Cross-project registry. Lives in the user's home `~/.claude/`, NOT in any single project. Lets the skill find tutorial-creator projects from any cwd. Populated by `tutorial-creator open <path>`, the offer-to-register prompt at the end of first-run setup, and `tutorial-creator forget <path>` (removal). The skill auto-updates `last_invoked` timestamps; users may hand-edit anything else.

```yaml
schema_version: 1

projects:
  - path: /Volumes/2 TB Drive/Coding/GitHub/Tutorials
    name: stuffolio-learning           # optional; user-provided friendly label
    last_invoked: 2026-05-10T12:34:00Z

  - path: /Users/me/Code/learn-rust
    name: rust-fundamentals
    last_invoked: 2026-04-15T08:21:00Z

# Optional: which project to use when the discovery chain reaches the
# registry step and there are multiple entries. Set by `tutorial-creator open`
# (interactive form) or by passing `--default` to the path form.
default: /Volumes/2 TB Drive/Coding/GitHub/Tutorials
```

### Field rules

- `schema_version`: integer. Always `1` for v2.0. Future bumps follow the policy below.
- `projects`: list of registered project entries. Order does not matter; the picker UI sorts by `last_invoked` desc.
- `projects[].path`: absolute filesystem path. Must contain `.claude/tutorial-config.yaml` to be considered valid by the resolution chain. The registry does NOT validate this on every read — it only refuses to *register* invalid paths (`open` checks). A registered project whose config disappears later silently falls through the resolution chain to the next step; periodic `tutorial-creator forget` cleanup is on the user.
- `projects[].name`: optional string. Free-form label. Shown in the multi-project picker prompt for human readability when many projects share similar paths.
- `projects[].last_invoked`: ISO-8601 UTC timestamp, updated by the skill on successful resolution. New entries default to the current timestamp at registration time.
- `default`: optional absolute path. Must match one of `projects[].path` exactly. Used when the resolution chain reaches step 5 (registry lookup) and finds multiple projects. If `default` is unset and there are multiple projects, the skill prompts the user to pick.

### Operations

- **`tutorial-creator open <path>`** — append to `projects` if not already present; if first project, also set as `default`.
- **`tutorial-creator open` (interactive)** — show registered projects, set chosen one as `default`.
- **`tutorial-creator forget <path>`** — remove from `projects`; if it was the `default`, clear `default`.
- **Successful resolution (any step that picks a registered project)** — update that project's `last_invoked`. Side-effect only; no user interaction.

### Concurrency

The registry is a single-writer file. The skill does not currently take a lock when writing. In practice this is fine because tutorial-creator invocations are interactive and humans don't run two simultaneously. If two writes do race, last-write-wins. The risk of corruption is bounded (yaml is self-contained per write); a future v2.x could add atomic-rename-on-write if it becomes a problem.

### Why not just walk to a known location?

An earlier design considered "always look at `~/.claude/tutorial-creator/<project-name>/` for configs." The registry is a cleaner separation: configs stay with their projects (so a project moves with a `git mv` or `mv` of the project directory), and the registry is just a pointer table. Same separation `git` uses between `.git/` directories and a hypothetical `git config --global` registry — except `git` doesn't actually need a registry because it always operates on cwd. tutorial-creator does need one because invocations from arbitrary cwds are the common case (`/skill tutorial-creator status` from anywhere should work).

### v1 → future migration

v2.0 ships at registry `schema_version: 1`. Adding fields like `tags`, `last_active_concept`, or `archived: true` would be additive and stay at version 1. A breaking change (e.g., restructuring `projects` from a list to a map) would bump to version 2 with a documented migration.

---

## Versioning policy

- **Breaking schema changes** bump `schema_version`. v2.0 ships at version `2`.
- **Additive changes** (new optional fields) do NOT bump `schema_version`. Old readers ignore unknown fields.
- **Reserved fields** (like `applied_test_history`, `post_test_*`) are documented when added; they don't bump `schema_version`. Populating them in a future v2.x is a non-breaking change.
- A v3 schema with breaking changes would ship its own migration recipe alongside the v2 → v3 upgrade.

---

## Validation

Phase 1 ships these schema definitions but no in-skill validator. Validation is a post-v2.0 candidate:

- `vocab doctor` — checks vocabulary.yaml for schema violations, dangling `related_terms` references, status/test_history inconsistency
- `tutorial doctor` — checks tutorial-config.yaml + session logs

Until then, the design relies on the skill itself producing schema-valid output and users not hand-editing yaml in ways that break the schema. `vocab regen-md` is a partial safety net: it regenerates the human-readable VOCABULARY.md from yaml, and crashes loudly if yaml is malformed.

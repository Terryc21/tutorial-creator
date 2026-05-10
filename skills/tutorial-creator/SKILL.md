---
name: tutorial-creator
description: Generate annotated code reading tutorials from your own codebase. Three surfaces - tutorial generation, vocabulary management, and learning-state inspection. Tracks vocabulary with status state machine, supports six writing-to-learn entry points and five audience-facing entry points.
version: 2.0.0-phase7-partial
author: Terry Nyberg, Coffee & Code LLC
license: Apache-2.0
---

# tutorial-creator

Three surfaces, gateway-mediated:

- **`tutorial`** — generate a lesson (six writing-to-learn entries, five audience-facing entries)
- **`vocab`** — manage vocabulary independent of lesson generation
- **`status`** — inspect your learning state (read-only dashboard)

> **v2.0 in development.** Phases 1-6 fully shipped. Phase 7 is **partially shipped**: the audience-facing routing layer, AUDIENCE.md procedures, and 3 of 6 venue templates (`reddit`, `book-chapter`, `apple-developer-article`) are live. The remaining 3 venue templates (`medium`, `blog`, `repo-doc`) are not yet shipped; selecting them at the venue-selection prompt returns a "venue not yet available" message rather than rendering. Phase 7 will be redeclared as fully shipped (and the version bumped to `2.0.0-phase7`) when the remaining 3 venue files land. Phase 8 (polish, CHANGELOG, demo bundles, v2.0.0 release) follows. See `~/.claude/plans/tutorial-creator-v2-implementation.md` and `~/.claude/plans/tutorial-creator-v2-resume.md`.
>
> The legacy v1.1 invocation (`/skill tutorial-creator <topic> <source>`) routes to entry [b] (topic + file) and produces v1.1-shaped output until v2.0 ships.

## Usage

```
/skill tutorial-creator                         # opens gateway question
/skill tutorial-creator <topic> <source>        # legacy v1.1 path → entry [b]
/skill tutorial-creator tutorial <args>         # tutorial surface
/skill tutorial-creator vocab <subcommand>      # vocab surface
/skill tutorial-creator status                  # status surface
/skill tutorial-creator undo                    # revert last generation
/skill tutorial-creator undo --session <id>     # revert a specific session (rare)
/skill tutorial-creator renumber <old> <new>    # rename Day-N + rewrite cross-references
/skill tutorial-creator --mode learn|audience|both|vocab|status [args]
                                                 # skip gateway, route directly
/skill tutorial-creator open <path>             # register a tutorial-creator project
                                                 #  in ~/.claude/tutorial-creator/registry.yaml
                                                 #  so future invocations from any cwd find it
/skill tutorial-creator open                    # list registered projects + pick one
                                                 #  (sets it as the registry default)
/skill tutorial-creator forget <path>           # remove a project from the registry
                                                 #  (no filesystem changes; project files stay)
/skill tutorial-creator --project-dir <path> [args]
                                                 # one-shot override; resolves config
                                                 #  from <path>/.claude/tutorial-config.yaml
                                                 #  instead of the default discovery rule
```

**Where the project lives.** `.claude/tutorial-config.yaml` and `.claude/tutorial-sessions/` live in the **resolved project root**, not necessarily cwd. The skill walks a discovery chain on every invocation; see `## Project resolution`. This means you can keep a tutorial-creator project at `/Volumes/.../Tutorials/` and invoke `/skill tutorial-creator status` from any working directory and it Just Works — same mental model as `git status` walking up from cwd to find `.git/`.

## Routing logic

Every invocation runs through this dispatch:

0. **Resolve the project root** (NEW in this revision). Run `## Project resolution` first to determine which `.claude/tutorial-config.yaml` this invocation should read or write to. The resolved path becomes `$PROJECT_ROOT` for the rest of the invocation; all subsequent file operations described in this document use `$PROJECT_ROOT/.claude/`, `$PROJECT_ROOT/{tutorials_dir}/`, etc. Steps 1–4 below assume this has run.
1. **Read `--mode` flag if present.** If set, echo it back to the user as a one-line confirmation, then jump directly to that surface or path. Skip the gateway question. Mode values: `learn`, `audience`, `both`, `vocab`, `status`.
2. **Else, recognize first-positional subcommand keywords.** If the first positional arg is one of:
   - `tutorial` → tutorial surface (Path 1 unless `--mode audience` follows)
   - `vocab` → vocab surface; the second positional is the subcommand (`add`, `list`, `show`, `edit`, `merge`, `review`, `gap`, `regen-md`, `undo`)
   - `status` → status surface (`STATUS.md`)
   - `undo` → recovery `undo` route (see `## Recovery` § `undo` command). May be followed by `--session <id>`
   - `renumber` → recovery `renumber` route (see `## Recovery` § `renumber`). Requires two more positional args: `<old> <new>` (e.g., `renumber 8 7.5`)
   - `open` → registry route (see `## Project resolution` § `open` command). May be followed by an optional `<path>` positional
   - `forget` → registry route (see `## Project resolution` § `forget` command). Requires one positional arg: `<path>`
   Route directly. Skip the gateway question.
3. **Else, parse two-positional legacy form.** If the user invoked with two positional args matching `<topic> <source>` AND the source is an existing file in the project, treat as **entry [b] legacy path** — produce a v1.1-shaped tutorial. This preserves the v1.1 invocation contract for users who haven't seen the v2 changes.
4. **Else, ask the gateway question.** Present the four-option menu (below). Route based on answer.

### Gateway question

Use AskUserQuestion (or plain-text prompt if AskUserQuestion is unavailable):

```
What do you want to do?

[1] Write a tutorial for myself      (writing-to-learn)
[2] Write a tutorial for others      (audience-facing)
[3] Manage vocabulary                 (jump to vocab surface)
[4] Inspect my learning state         (jump to status surface)
```

- **Answer [1]** → tutorial surface, Path 1 (writing-to-learn). Ask the entry-point question (six options; see `## Tutorial surface — entry points`).
- **Answer [2]** → tutorial surface, Path 2 (audience-facing). Load `AUDIENCE.md` and run the Path 2 routing flow (entry-point question, audience question, honest-machine opt-in, length budget, venue selection, then handoff to the chosen `venues/<name>.md`).
- **Answer [3]** → vocab surface (load `VOCAB.md`).
- **Answer [4]** → status surface (load `STATUS.md`).

### Mode-mismatch detection

If the user picked Path 2 (audience-facing) AND their topic phrasing matches one of these patterns, soft-nudge once:

- starts with `I want to understand`
- starts with `I'm confused about`
- starts with `why does my`
- starts with `what is`

Nudge text:

> This phrasing reads like writing-to-learn. Confirm audience-facing, or switch to writing-to-learn?

**Single-fire per session.** A session-scoped flag (`mode_mismatch_nudge_fired: true`) flips after the first surface. Subsequent matching topics in the same session do NOT re-nudge. The user has demonstrated awareness.

Not blocking. The user always has final say. The nudge is purely advisory; either answer proceeds without delay.

## Tutorial surface — entry points

After gateway answer = [1] (writing-to-learn), ask:

```
Where does the lesson start?

[a] Daily progression       — pick what's next based on my progress
[b] Topic + file            — I have both ("closures in helpers.ts")
[c] Topic only              — I have a topic, find the best file
[d] Question                — I'm stuck on something specific
[e] Gap-driven              — show me my "confused" vocabulary, pick from there
[f] External source         — I read this; help me consolidate
```

After gateway answer = [2] (audience-facing), ask:

```
Where does the tutorial start?

[a] Annotated source         — file in my codebase that demonstrates the pattern
[b] Incident-grounded        — a real failure or decision I want to write about
[c] Synthesized example      — contrived minimal example for the concept
[d] External source          — public repo, Apple sample, blog post
[e] Documentation-grounded   — Apple Developer docs, RFCs, etc.
```

After the entry letter is picked, the Path 2 flow runs four more AskUserQuestion prompts in this order, then hands off to a venue template:

1. **Audience question.** Options: `beginner` / `intermediate` / `senior` / `mixed`. Drives in-voice content shifts (definitions vs. tradeoffs).
2. **Honest-machine opt-in.** Y / N. When Y, the venue template appends a section on what the article does NOT cover (section name varies by venue; resolved from `venues/_schema.yaml#venues.<name>.honest_machine_section_name`).
3. **Length budget.** Options: `S` / `M` / `L` / `X`. Each option label includes the venue's word target and ceiling, looked up from `venues/_schema.yaml#venues.<name>.length_budget`.
4. **Venue selection.** Options: `reddit` / `book-chapter` / `apple-developer-article` / `medium` / `blog` / `repo-doc`.

   **Partial-Phase-7 guard:** the venue-selection question must label the three not-yet-shipped venues (`medium`, `blog`, `repo-doc`) as `(not yet available)` in their option text. If the user selects any of those three regardless, the skill MUST refuse with this exact message and stop, NOT attempt the venue handoff:

   > Venue `<name>` is not yet shipped in `2.0.0-phase7-partial`. Available venues right now: `reddit`, `book-chapter`, `apple-developer-article`. Pick one of those, or wait for the next release.

   The runtime must NOT attempt to load `venues/<name>.md` for an unshipped venue under any circumstance; the file does not exist and the open will fail.

The full procedure for each Path 2 entry, the venue handoff payload schema, the audience × budget interaction rules, and the recovery-asymmetry rationale all live in `AUDIENCE.md`. SKILL.md is the routing surface; AUDIENCE.md is the procedure surface.

### Implementation status

**All six writing-to-learn entries are implemented** (Phases 3abc + 3def):

- **[a] daily progression** — see `## Entry [a] — Daily progression`
- **[b] topic + file** — see `## Entry [b] — Tutorial Format (topic + file)` (this is also the legacy v1.1 path)
- **[c] topic only** — see `## Entry [c] — Topic only (skill finds the file)`
- **[d] question-led** — see `## Entry [d] — Question-led`
- **[e] gap-driven** — see `## Entry [e] — Gap-driven`
- **[f] external source** — see `## Entry [f] — External source`

**All five audience-facing entries are implemented** (Phase 7), but only 3 of 6 venue templates are shipped (Phase 7 is partial):

- **[a] annotated source** — see `AUDIENCE.md` § Entry [a]
- **[b] incident-grounded** — see `AUDIENCE.md` § Entry [b]
- **[c] synthesized example** — see `AUDIENCE.md` § Entry [c]
- **[d] external source** — see `AUDIENCE.md` § Entry [d]
- **[e] documentation-grounded** — see `AUDIENCE.md` § Entry [e]

**Venue templates available right now:**

| Venue | File | Status |
|---|---|---|
| `reddit` | `venues/reddit.md` | ✅ shipped |
| `book-chapter` | `venues/book-chapter.md` | ✅ shipped |
| `apple-developer-article` | `venues/apple-developer-article.md` | ✅ shipped |
| `medium` | `venues/medium.md` | ⚠️ not yet shipped |
| `blog` | `venues/blog.md` | ⚠️ not yet shipped |
| `repo-doc` | `venues/repo-doc.md` | ⚠️ not yet shipped |

The five Path 2 entries `[a]`-`[e]` share letters with the Path 1 entries but are different procedures; do not conflate them. Path 1 produces artifacts for the user (writing-to-learn); Path 2 produces artifacts for an audience (Reddit posts, book chapters, articles, blog posts, repo docs). After the entry is chosen, Path 2 hands off to one of the 3 currently-shipped venue templates in `venues/`. Selecting an unshipped venue triggers the partial-Phase-7 guard described in the venue-selection step above.

## Entry [a] — Daily progression

Use when the user wants the next concept in their learning sequence and doesn't have a specific topic or file in mind.

### Procedure

1. **Read config.** `.claude/tutorial-config.yaml`. Required fields for entry [a]: `language`, `next_day`, `experience_level`, `tutorials_dir`. If `progression_override` is set, use that path; otherwise load `progressions/<language>.yaml` from the skill bundle.
2. **Determine current phase.** Read `PROGRESS.md`. Look for the most recent Score Log row to find the last-shipped phase number. If PROGRESS.md is empty (first day), current phase = 1.
3. **Read the active progression.** Parse the matching `progressions/*.yaml`. Extract the current phase's `concepts` list.
4. **Identify uncovered concepts in this phase.** Cross-reference `concepts` against the Concepts Mastery Checklist in PROGRESS.md (entries marked `- [ ]` or `- [x]`). Concepts NOT yet appearing in the checklist are the candidates.
5. **Recommend the next concept.** Pick the first uncovered concept in the phase's list (the list order is teaching order). Show the user one candidate with brief reasoning:
   ```
   Next in your progression:
     Concept: <concept name>
     Phase:   <phase number>. <phase name>
     Reason:  First uncovered concept in this phase. <covered_in_phase>/<total_in_phase> concepts done.
   Generate a tutorial for this? [yes / pick different concept / advance to next phase / cancel]
   ```
6. **Handle user response.**
   - `yes`: proceed to step 7
   - `pick different concept`: list all uncovered concepts in current phase, let user choose
   - `advance to next phase`: increment phase number; re-run from step 4 with the next phase. If the user is already in the last phase (phase 6 in built-in progressions), say: "You're in the last built-in phase. Use entry [c] (topic only) for advanced topics, or define a custom progression in `tutorial-config.yaml#progression_override`." Stop.
   - `cancel`: stop without generating
7. **Find a source file.** With concept chosen, scan the project for files demonstrating it. Use the same ranking heuristic as Entry [c] below ("pedagogical fit beats density"). Show 1-3 candidates; user picks one.
8. **Generate the tutorial.** Follow the tutorial format in `## Entry [b] — Tutorial Format`. The chosen concept becomes the topic; the chosen file becomes the source.

### Cold-start handling

If `next_day == 1` AND PROGRESS.md doesn't exist yet AND no tutorials have been written:

- The user has just completed first-run setup
- Phase = 1; pick the first concept of phase 1 ("optionals" for Swift, "basic types" for TypeScript, etc.)
- Note in the recommendation: "First lesson — picking the foundational concept for your language."

### Honesty rule

If no source file in the project demonstrates the recommended concept (scan returns zero candidates above the quality threshold defined in Entry [c]), say so explicitly:

> No good example of `<concept>` in your codebase. Two options:
>   1. Pick a different concept from this phase (I can list them)
>   2. Use audience-facing path [c] (synthesized minimal example) if you want a contrived example

Do not silently fall back to a synthesized example or pick a marginal file. The user's confidence in the recommendation is load-bearing.

## Project resolution

Runs as step 0 of every invocation, before routing. Determines `$PROJECT_ROOT` — the directory whose `.claude/tutorial-config.yaml` this invocation reads from and writes to. Resolution must succeed before any other step runs; if it doesn't, the skill either runs first-run setup (if no project anywhere) or refuses (if multiple registered projects can't be disambiguated).

### Discovery chain (highest precedence first)

1. **`--project-dir <path>` flag.** If set on the invocation, treat `<path>` as `$PROJECT_ROOT` and stop. The path must be absolute or resolvable relative to cwd. If `<path>/.claude/tutorial-config.yaml` does not exist, the skill **does not** auto-create it from this flag — say `--project-dir <path> has no tutorial-creator config. Run "/skill tutorial-creator open <path>" first, or invoke from <path> to trigger first-run setup.` and stop. The `--project-dir` flag is for picking among already-set-up projects, not for bootstrapping new ones in unusual locations.
2. **Environment variable `TUTORIAL_CREATOR_PROJECT_DIR`.** If set and points to a directory with `.claude/tutorial-config.yaml`, use it as `$PROJECT_ROOT`. If the env var is set but the path is invalid, warn (`TUTORIAL_CREATOR_PROJECT_DIR=<path> doesn't have a tutorial-creator config; ignoring`) and fall through to the next step.
3. **Cwd's `.claude/tutorial-config.yaml`.** If `./.claude/tutorial-config.yaml` exists in the current working directory, use cwd as `$PROJECT_ROOT`. This preserves backward compatibility with v1.1 / v2.0-pre-resolution behavior — if you're already in your project, nothing changes.
4. **Ancestor walk from cwd.** Walk up from cwd one directory at a time until either: (a) a `.claude/tutorial-config.yaml` exists at that level — use that directory as `$PROJECT_ROOT`; (b) the filesystem root is reached — fall through to the next step. Stop at filesystem root, do NOT cross into another user's home directory or into `/`.
5. **Registry lookup.** Read `~/.claude/tutorial-creator/registry.yaml` (per SCHEMAS.md Schema 5). If the file exists and:
   - has exactly one project entry → use it as `$PROJECT_ROOT`
   - has a `default` field pointing at a registered project → use it
   - has multiple projects with no default → prompt the user to pick one (and offer to set it as default for next time):
     ```
     Multiple tutorial-creator projects registered. Pick one for this invocation:
       [1] /Volumes/.../Tutorials      (last invoked: 2026-05-10)
       [2] /Users/me/Code/learn-rust   (last invoked: 2026-04-15)
       [3] /Users/me/code-smarter      (last invoked: 2026-03-22)
     Choose [1-3]; add `--default` to also set this as the registry default.
     ```
   - registry file is missing or empty → fall through to the next step
6. **First-run setup in cwd.** No project found anywhere in the chain. Run `## First-Run Setup` against cwd; ask the user to confirm cwd is where they want the project to live, or to type a different path. After setup, offer to register the new project:
   ```
   Add this project to the registry so future invocations from any cwd find it? [yes/no]
   ```
   If yes, append to `~/.claude/tutorial-creator/registry.yaml` and set `default: <new path>` if no default exists yet.

### When to refuse vs prompt

- Step 1 (`--project-dir`) without a config at the path → refuse. The flag is explicit; honoring it would silently bootstrap somewhere the user didn't ask for.
- Step 2 (env var) without a config at the path → warn, fall through. The env var may be stale or wrong; falling through to discovery is forgiving.
- Step 5 (registry) with multiple projects no default → prompt. This is the common multi-project case and the user just needs to pick.
- Step 6 (no project anywhere) → run setup. This is the cold-start case the skill was already designed for; the resolution chain just adds the new escape hatches above it.

### Side effect: registry update on success

After successful resolution (steps 1–5), if the project is in the registry, update its `last_invoked` timestamp to now. This makes the multi-project pick prompt order entries by recency. Step 6 may also write a new registry entry (with user consent).

### `open` command

Registers a tutorial-creator project so the resolution chain finds it from any cwd. Two forms:

```
/skill tutorial-creator open                    # interactive: list registered, pick + set as default
/skill tutorial-creator open <path>             # add <path> to the registry
```

**Form 1 — list and pick.** Read `~/.claude/tutorial-creator/registry.yaml`. If empty, say `No projects registered. Use "/skill tutorial-creator open <path>" to add one.` and stop. Otherwise, list registered projects with their `last_invoked` timestamps, ask the user to pick one, and write that project as the registry's `default`. Confirm: `Default set to <path>. Future invocations from any cwd will use this project unless you pass --project-dir.`

**Form 2 — add a path.** Verify `<path>` exists and contains `.claude/tutorial-config.yaml`. If the config is missing, refuse: `<path> has no tutorial-creator config. Either run setup at <path> first by invoking the skill from there, or pass a path to an already-set-up project.` On success, append to the registry. If this is the first registered project, also write it as the `default`. Confirm: `Registered <path>. Now reachable from any cwd via the resolution chain.`

The `open` command does NOT create a config; it only registers an existing one. This is deliberate — bootstrapping a new project should happen via first-run setup, which has its own confirmation flow ("Where should tutorials be saved?", language detection, etc.). Splitting the two prevents accidental misconfig.

### `forget` command

```
/skill tutorial-creator forget <path>
```

Removes `<path>` from the registry. Filesystem changes: none. The project's files (`.claude/tutorial-config.yaml`, `tutorials_dir`, etc.) are untouched. If `<path>` was the default, the registry's `default` field is cleared. If `<path>` is not in the registry, say `<path> is not registered.` and stop.

Use `forget` when a project moves (`forget` the old path, `open` the new one) or when a project is archived and shouldn't surface in the multi-project picker anymore.

### Why this design

The previous behavior (`tutorial-config.yaml` pinned to cwd) created the same hostility `git` would have if `.git/` only worked from the exact directory you ran `git init` in. Tutorial projects often outlive any single coding session — the user's tutorials live at `/Volumes/.../Tutorials/` for years; the codebase they're learning from changes weekly. The discovery chain decouples "where the learning artifacts live" from "where I happen to be running the skill from right now," same as `git` decouples the working tree from the .git directory location.

The registry exists for the case where neither cwd nor an ancestor reveals a project. Without it, a user who keeps their tutorials at `~/Code/learn-rust/` and wants to invoke `/skill tutorial-creator status` from `~/`, `/tmp/`, or any other arbitrary cwd would have to type `--project-dir ~/Code/learn-rust` every time. The registry makes "I have one tutorial project" the zero-friction case.

### Cwd-relative paths in resolved configs

Once `$PROJECT_ROOT` is resolved, `tutorials_dir`, `project_dir`, and `progression_override` in the config are interpreted relative to `$PROJECT_ROOT`, NOT cwd. So a config that says `tutorials_dir: ./tutorials/` always means `$PROJECT_ROOT/tutorials/` regardless of where the skill was invoked from. This is the same convention `git` uses for paths in `.gitignore` and `.gitconfig`.

If the existing config has `project_dir: .` (the v1.1 default meaning "the cwd at setup time"), v2 treats `.` as `$PROJECT_ROOT`. This is technically a behavior change for users who set up tutorial-creator in a project root and then invoked from a subdirectory expecting `project_dir` to follow cwd — but that mode was never coherent (the config is per-project, not per-invocation), and no shipped feature relies on the old reading.

## First-Run Setup

Triggered from `## Project resolution` step 6 (no project found anywhere in the discovery chain). Confirms cwd is where the project should live, then prompts for setup details:

```
Welcome to tutorial-creator! Let's set up your learning environment.
```

Ask via AskUserQuestion:

1. **Confirm the project root.** Default: cwd. Show the resolved cwd path verbatim, ask "Use this directory as your tutorial-creator project? [yes / pick different path / cancel]". If the user picks a different path, that becomes `$PROJECT_ROOT` for the rest of setup. Refuse paths that don't exist; refuse paths inside another already-registered project (would create nested configs).
2. **Where should tutorials be saved?** Default: `$PROJECT_ROOT/tutorials/` (config written as `./tutorials/`, interpreted relative to `$PROJECT_ROOT`). User can pick an absolute path elsewhere if they want tutorial files outside the project root for some reason.
3. **What language/framework are you learning?** Auto-detect from project files (`package.json` = JS/TS, `Package.swift` = Swift, `Cargo.toml` = Rust, etc.) at `$PROJECT_ROOT`; user confirms or overrides.
4. **What's your experience level?** beginner / intermediate / advanced.
5. **What's your project directory?** (the codebase you're learning from) Default: `$PROJECT_ROOT` itself. User picks a different path if their tutorials track a *different* codebase than the one hosting the config (e.g., tutorials live at `~/Tutorials/`, codebase being studied lives at `~/Code/myapp/`).

Save config to `$PROJECT_ROOT/.claude/tutorial-config.yaml` per `SCHEMAS.md` Schema 1:

```yaml
schema_version: 2
tutorials_dir: ./tutorials/
language: swift
framework: swiftui
project_dir: .
next_day: 1
experience_level: intermediate
vocab_format: yaml-with-md-view
recovery_enabled: true
progression_override: null
```

Create initial files (relative to `$PROJECT_ROOT`):
- `{tutorials_dir}/PROGRESS.md` (template at end of this file)
- `{tutorials_dir}/VOCABULARY.md` (regenerated view)
- `{tutorials_dir}/vocabulary.yaml` (empty list `[]`)

If `$PROJECT_ROOT/.claude/` doesn't exist, create it.

After setup completes, offer to register the new project in `~/.claude/tutorial-creator/registry.yaml`:

> Add this project to the registry so future invocations from any cwd find it? [yes/no]

If yes, append an entry per SCHEMAS.md Schema 5. If this is the first registered project, also write it as the registry's `default`. See `## Project resolution` § "Discovery chain" for how the registry feeds future invocations.

## Entry [b] — Tutorial Format (topic + file)

When invoked as entry [b] (topic + file), produce a tutorial with these sections in this order. **This is also the legacy v1.1 invocation path** — when the user invokes `/skill tutorial-creator <topic> <source>` with two positional arguments and an existing source file, route here directly without the gateway question. The format is preserved verbatim from v1.1 so existing users see no behavior change.

### Before Writing

1. **Read the config:** `.claude/tutorial-config.yaml`
2. **Read PROGRESS.md** — use next available day; check covered concepts.
3. **Read vocabulary.yaml** (or VOCABULARY.md if yaml absent) — reference existing terms.
4. **Read the source file** to annotate.

### Required Sections

1. **Header**
   ```markdown
   # Day N: [Topic Title] -- [Subtitle]

   *Source: `[file path]` ([scope description])*
   *Day N -- [Date] -- [Phase name] (Phase N)*
   ```

2. **What You'll Learn** — 1-2 sentences in plain language.

3. **Vocabulary** — only new terms (not in earlier tutorials). One-line definitions. End with: `> Full vocabulary list: [VOCABULARY.md](VOCABULARY.md)`

4. **Pre-Test** — 5-8 questions answerable from the vocabulary table alone; tests intuition, not memorization.

5. **The Core Pattern** — explain the concept with simplified examples first, then build up. Calibrate depth to `experience_level`:
   - **beginner:** explain syntax, name types, define every keyword
   - **intermediate:** skip basic syntax, focus on "why this pattern" and alternatives
   - **advanced:** focus on tradeoffs, edge cases, performance implications

6. **Real Code from [Project]** — actual source, annotated with `// <--` or `// ^^^` arrows. Simplify if needed; note what was removed.

7. **Common Mistakes** — 3-5 errors with what happens and how to fix.

8. **Post-Test** — 5-8 harder questions; require applying the concept.

9. **Answer Key** — full explanations for both tests.

10. **New Concepts Introduced**
    ```markdown
    | Concept | Where in Code | Key Takeaway |
    |---------|---------------|--------------|
    | [name]  | [Line N]      | [one-sentence summary] |
    ```
    Aim for 6-12 rows. Every concept here MUST also appear in the Vocabulary table at the top.

### Before Writing (pre-write hook)

Run `## Recovery` § "Always-on: pre-write hook" first. Skip if `recovery_enabled: false` in config; otherwise the hook stages the session id, snapshots PROGRESS.md / VOCABULARY.md / vocabulary.yaml / tutorial-config.yaml, and stages the session yaml. The generation procedure below assumes that hook ran.

### After Writing

1. **Save** to `{tutorials_dir}/DayN-[Topic]-Annotated.md`
2. **Update PROGRESS.md** — add Score Log row (day, date, file, test counts) and Concepts Mastery Checklist entries (`- [ ] [Concept name] (Day N)`).
3. **Update VOCABULARY.md** — add new section `## Day N: [Topic]`; only genuinely new terms; update Cumulative Count.
4. **Increment** `next_day` in config.
5. **Run the post-write hook** (`## Recovery` § "Always-on: post-write hook") — populates and writes the session yaml, prunes old sessions per retention. Skipped if `recovery_enabled: false`.
6. **Gap analysis** — review the new tutorial; if it depends on uncovered concepts, propose half-step bridge tutorials (e.g., Day 7.5) with topic, what they bridge, and why. Ask whether to create now or defer.

## Entry [c] — Topic only (skill finds the file)

Use when the user has a topic in mind but doesn't have a specific source file. The skill scans the project, ranks candidate files by pedagogical fit, and proposes 1-3 candidates. The user picks one, asks for more, or switches to a synthesized example.

### Procedure

1. **Read config.** Same fields as Entry [a]; also need `project_dir`.
2. **Scan the project for candidate files.** Walk `project_dir`:
   - Respect `.gitignore`
   - Skip these directories regardless of `.gitignore`: `node_modules`, `.git`, `build`, `dist`, `.build`, `DerivedData`, `target`, `__pycache__`, `.venv`, `venv`, `.next`, `.nuxt`, `coverage`, `.pytest_cache`
   - Include only files matching the configured language: `*.swift` for Swift, `*.ts`/`*.tsx` for TypeScript, `*.py` for Python, `*.rs` for Rust
   - Exclude test files (heuristic: filename matches `*Tests.swift`, `*.test.ts`, `*.test.tsx`, `*.spec.ts`, `*_test.py`, `tests/*` paths) — tests can be useful for some topics but rarely for first-encounter teaching; show them as fallback only if no non-test candidates exist
3. **Find topic occurrences.** For each candidate file, search for the topic. Topic-matching heuristic by language:
   - **Swift attributes** (e.g., `@MainActor`, `@Observable`): grep for the literal `@<name>`
   - **Swift keywords** (e.g., `guard`, `defer`, `consume`): grep for the keyword as a whole word (`\bguard\b`)
   - **API names** (e.g., `URLSession`, `useState`): grep for the identifier as a whole word
   - **Concepts** (e.g., "actor isolation", "render props"): if no direct symbol matches, fall back to filename + comment search; lower confidence
   - Record per-file: line numbers of matches, total match count, and tightest line range covering 2+ consecutive matches
4. **Rank by pedagogical fit.** For each file with at least 1 match, compute a score:
   - **File size** (fewer lines = better, log-scaled): `+ 1.0 / log(line_count + 10)`
   - **Match concentration** (consecutive matches in tight range = better): `+ 0.5` if 2+ matches within 30 lines of each other; `- 0.3` if matches are scattered across more than 60% of the file
   - **Match count** (some examples = better than zero, but more is not always better): `+ 0.3` for 2-5 matches, `+ 0.2` for 1 match, `- 0.2` for >10 matches (too noisy)
   - **Comment ratio** (well-commented files teach better): `+ 0.2` if at least 10% of lines are comments
   - **Penalty for large files**: `- 0.5` if line_count > 500, `- 1.0` if line_count > 1000
5. **Show top 1-3 candidates with evidence.** Format:
   ```
   I scanned the project for "<topic>". Top candidates:

   1. Sources/Models/AppSchema.swift  (123 lines, 5 matches at lines 42, 47, 89-91)
      Reason: Compact file with concentrated examples; well-commented.
   2. Sources/Managers/CloudSyncManager.swift  (340 lines, 7 matches throughout)
      Reason: More examples but spread across the file; useful if you want to see usage variety.
   3. Sources/Views/SettingsView.swift  (210 lines, 2 matches at lines 89, 94)
      Reason: Smaller scope; the two examples are adjacent and tightly coupled.

   [1-3] generate tutorial for that file
   [more] show 3 more candidates
   [synthesized] switch to a contrived minimal example (audience-facing path [c])
   [cancel] stop
   ```
6. **Quality threshold for the no-good-example fallback.** If the top candidate's score is below `1.0` (heuristic floor) OR no file has 1+ match, do NOT silently pick the best-of-bad. Instead say:
   ```
   No good example of "<topic>" in your codebase. The closest match was
   <file> with score <N> (threshold is 1.0). Two options:

   [synthesized]  Switch to audience-facing path [c] (contrived minimal example)
   [different]    Pick a different topic
   [proceed]      Use <file> anyway (low pedagogical fit; expect a noisier tutorial)
   [cancel]       Stop
   ```
7. **On selection (1-3 or proceed).** Hand off to Entry [b] with the chosen topic + file. The procedure from there is identical to Entry [b]'s.

### Honesty rule

The "Reason" line in step 5's output must reflect the actual ranking signals. Don't write generic reasons like "this is a great example"; say what the heuristic saw. If the file has 1 match, say "single example in scope"; if matches are scattered, say "spread across the file." This keeps the user's mental model of the ranker accurate, which matters when they're deciding whether to trust it.

### Cap on candidate enumeration

If 50+ files match the topic, do not enumerate all of them. Cap at top 3 + offer "more" (next 3). Still rank every match; just present incrementally. Ranking is fast (per-file score is one pass over each file's grep output); enumeration is the expensive part.

## Entry [d] — Question-led

Use when the user is stuck on something specific and the goal is "the lesson that resolves this question." This is the highest-value, highest-risk entry: most likely to delight when the question maps cleanly to a concept, most likely to disappoint when the question is ambiguous.

The honest-machine voice is load-bearing here. When the skill is uncertain, it must surface the uncertainty rather than pick one interpretation and proceed.

### Procedure

1. **Read config + vocabulary.yaml.** Need `language`, `project_dir`, and the user's existing vocabulary state to assess whether the question has already been addressed in past tutorials.
2. **Receive the question.** The user provides a free-form question, e.g.:
   - "Why does my SwiftData fetch sometimes return zero results?"
   - "How is `@MainActor` different from `@MainActor.assumeIsolated`?"
   - "What's the difference between `consume` and `borrow`?"
3. **Extract candidate concepts.** Identify 1-N concepts the question plausibly involves. Use:
   - Direct identifier matches (e.g., `@MainActor`, `consume`) → high confidence
   - Concept-noun phrases (e.g., "fetch", "ModelContext") → mid confidence
   - Generic verbs ("returns", "differs") → ignore
4. **Match against existing vocabulary.** For each candidate concept, check if it already exists in `vocabulary.yaml`. If a confused-status term matches, prefer it (the user is asking about something they're already tracking).
5. **Confidence assessment.** One of three outcomes:
   - **High confidence** — exactly one candidate concept clearly dominates (e.g., the question literally names one identifier). Proceed to step 6.
   - **Medium confidence** — 2-3 candidate concepts could explain the question. Surface the ambiguity:
     ```
     I see two ways to interpret this question. Which fits?

     [1] You're asking about <concept-A>: <one-sentence framing>
     [2] You're asking about <concept-B>: <one-sentence framing>
     [3] Something else — let me describe it differently
     ```
   - **Low confidence** — no clear concept extraction. Ask the user to refine:
     ```
     I'm not sure what concept this question is targeting. A few possibilities:
       - <vague candidate>
       - <vague candidate>

     Can you say more about what's confusing you? Or rephrase the question
     to name the specific feature/keyword/API you're stuck on.
     ```
     Do not pick one and proceed. The honest-machine answer is "I don't know yet."
6. **Find a source file demonstrating the chosen concept.** Use Entry [c]'s ranking heuristic (pedagogical fit beats density). Show 1-3 candidates with evidence; user picks one.
7. **Frame the lesson around the question.** The tutorial's "What You'll Learn" section should explicitly answer the user's question. The Core Pattern and Real Code sections build toward that answer. The Common Mistakes section includes the specific failure mode the user described, if it's a debugging question.
8. **Generate via Entry [b]'s format** with the chosen concept as topic and the chosen file as source. Mark the session log with `entry: question-led` and include the original question in the session record (so undo/audit can reconstruct what the user actually asked).

### Honesty rules (load-bearing for entry [d])

- If the question is ambiguous, **always** surface the ambiguity. Never pick one interpretation silently.
- If no source file demonstrates the concept well, **always** offer the synthesized-example fallback (audience-facing path [c]). Do not generate a tutorial against a marginal file just to satisfy the request.
- If the question's actual answer is "you can't do this" or "this is the wrong question," say so directly. Do not generate a tutorial that papers over a fundamental misunderstanding.

### Why entry [d] disappoints when it disappoints

The skill is doing concept extraction and file matching with the runtime LLM as the only tool. Both are imperfect. The honesty rules above ensure that imperfect detection produces a *visible* disappointment ("I don't know what concept you mean — clarify?") instead of an *invisible* one (a generated tutorial that's subtly off-topic). Visible disappointment is recoverable; invisible disappointment is not.

## Entry [e] — Gap-driven

Use when the user wants to learn what they're worst at. Read directly from `vocab gap` view and generate a tutorial targeted at one of the user's confused terms.

This entry is the closure of the writing-to-learn loop: terms get tested in `vocab review`, fall to `confused` after repeated partial/wrong results, surface in `vocab gap`, and become the source for new tutorials. Each tutorial that addresses a confused term increases the chance of a correct test result, which shifts the term out of `confused`.

### Procedure

1. **Run `vocab gap` internally.** Produce the same ranked list of confused terms (longest-confused first) that the standalone `vocab gap` command would produce.
2. **Show the list with selection prompt.** Format identical to standalone `vocab gap` output:
   ```
   Confused terms (4):

     1. actor isolation         confused 18 days   (last test: 2026-04-21, partial)
     2. nonisolated(unsafe)     confused  9 days   (last test: 2026-04-30, wrong)
     3. consume                 confused  7 days   (last test: 2026-05-02, partial)
     4. SchemaMigrationPlan     confused  5 days   (last test: 2026-05-04, wrong)

   Which would you like to address? [1-4 / cancel]
   ```
3. **On selection:** the chosen term becomes the topic. Hand off to Entry [c]'s file-finding logic (pedagogical fit ranking) to find a source file demonstrating it. Show 1-3 file candidates; user picks one.
4. **Generate via Entry [b]'s format** with the term as topic and the chosen file as source. The tutorial's framing should acknowledge the gap directly:
   - "What You'll Learn" section: "You've been getting `<term>` partially right — here's what we'll fix."
   - Pre-Test should test the *specific aspect* the user has been getting wrong (look at the term's `test_history` for the most recent partial/wrong result; the question that produced it tells you what gap to target).
5. **Mark the session log** with `entry: gap-driven` and `gap_term: <term>` (per SCHEMAS.md Schema 3).

### Empty-state handling

If `vocab gap` returns zero confused terms:
```
No confused vocabulary right now. Two paths:

[review]   Run vocab review to test what you've learned (may surface new gaps)
[topic]    Switch to entry [c] (topic only) — pick what you want to learn
[cancel]   Stop
```

Do not silently fall back. The user invoked `gap` for a reason; if there's no gap, the honest answer is "you have no gap to address — pick a different way in."

### Single-confused-term shortcut

If exactly one term has `status: confused`, skip the selection step and go directly to "I see one confused term: `<term>`. Generate a tutorial for it? [y/n]". One less prompt for the common case.

## Entry [f] — External source

Use when the user has read external content (Apple doc, blog post, GitHub repo, RFC, video transcript) and wants to consolidate their understanding of it through writing-to-learn. The user's project becomes the *consumer* — the tutorial maps the external concepts onto the user's codebase — instead of the *source*.

This entry is the writing-to-learn equivalent of "synthesizing notes after a meeting." The artifact is "what this external thing said + what it left out + what I'd want to verify in my own code."

### Accepted source types

- **URL** — Apple Developer doc, blog post (Medium, Substack, dev.to, personal blog), Stack Overflow answer, GitHub README/wiki/issue, RFC
- **File path** — local Markdown file, downloaded HTML, PDF (skill notes that PDF parsing is best-effort)
- **Pasted text** — user pastes the content directly when the source isn't fetchable

### Procedure

1. **Read config.** Need `language`, `project_dir` for the "how this applies to my codebase" mapping step.
2. **Receive the source.** AskUserQuestion (or plain prompt):
   ```
   Where's the external source?
   [1] URL
   [2] File path
   [3] I'll paste the content directly
   [cancel]
   ```
3. **Fetch / read the content.** For URL: use the runtime's available web fetch tool (e.g., WebFetch). For file path: read directly. For pasted: prompt the user to paste, terminate on a sentinel like `END` on its own line.
4. **Extract key concepts.** From the source content, identify 3-8 concepts that the source teaches or references. Group them:
   - **Already in your vocabulary** — show terms that already exist in `vocabulary.yaml` (with current status). The tutorial reinforces these.
   - **New to you** — concepts the source introduces that aren't in your vocabulary yet. The tutorial captures these as new vocab entries.
5. **Show the extraction with confirmation:**
   ```
   This source covers:

   Concepts you already know:
     - @MainActor (status: mastered) — source touches it briefly
     - actor isolation (status: confused) — source goes deep on this

   Concepts new to your vocabulary:
     - GlobalActor protocol — source defines it explicitly
     - isolation domains — source uses this term but doesn't define it formally
     - Sendable closures — source has 3 examples

   Generate a writing-to-learn tutorial covering these? [y / pick subset / cancel]
   ```
6. **On `pick subset`:** user selects which concepts to include. Default to all.
7. **Map concepts to the user's codebase.** For each concept, scan `project_dir` (Entry [c]'s heuristic) to find files that demonstrate the concept. Surface 0-1 example file per concept; the tutorial uses these as "here's where this shows up in your code." If no example exists locally, the tutorial says so explicitly ("the source mentions X but there's no example of X in your codebase yet — flagging as a gap").
8. **Generate the tutorial.** Different shape from Entries [a]-[e] because the source is external:
   - **Header:** `# Day N: <Source Title> — Notes & Synthesis` with link/path to source
   - **What You'll Learn:** "Reading [source title] taught me X. After writing this, I should be able to Y."
   - **Concepts from the source** (replaces "Vocabulary"): table of concepts with brief definitions paraphrased from the source (not verbatim — the user's paraphrase IS the writing-to-learn beat)
   - **Pre-Test:** 3-5 questions testing what the user thinks they know *before* writing the synthesis
   - **What the source says:** user's summary of the source's main argument (NOT a copy-paste of the source)
   - **What the source leaves out:** load-bearing for honest-machine voice. What questions does the source not answer? What edge cases does it skip? What would you need to verify in your own code?
   - **Where this shows up in my codebase:** for each concept that mapped to a file, annotated example. For concepts that didn't map, "no example here yet — flag as gap."
   - **What I'd ask to verify:** 3-5 specific things the user would experiment with or test to confirm they understood correctly
   - **Post-Test:** harder questions that require applying the concept beyond what the source explicitly said
   - **Answer Key:** explanations for both tests
   - **New Concepts Introduced:** standard table; concepts from the source feed `vocab add` automatically (skill confirms before writing each one)
9. **Before writing:** run `## Recovery` § "Always-on: pre-write hook" (snapshots + staged session yaml), unless `recovery_enabled: false`.
10. **After writing:**
    - Save to `{tutorials_dir}/DayN-External-<SourceShort>-Annotated.md`
    - Update PROGRESS.md (Score Log row + concepts added)
    - For each new concept, write a vocab entry (context: `external source`, source_file: empty, related_terms: extracted from the source if mentioned). These adds are tutorial-time; they go into the session's `vocab_added` list, not into the standalone sentinel system.
    - Run `## Recovery` § "Always-on: post-write hook" — populates the session yaml with `entry: external-source`, the source URL/path in a free-form note, the populated `vocab_added` list, and `output`.

### Honesty rule (cross-cutting)

The "What the source leaves out" section is non-negotiable. If the user can't think of anything the source left out, the skill prompts: "Every source leaves something out. What's an edge case the source didn't address? What audience is this NOT written for? What does it assume you already know?" The act of identifying gaps is the writing-to-learn beat; without it, the artifact is a passive recap, not a synthesis.

### Pasted-content size limit

If the user pastes content longer than ~50,000 characters, suggest they save it to a local file first and pass the file path instead. Long inline pastes consume the context window and reduce the skill's ability to reason about the user's codebase.

## Vocab surface

Routes to `VOCAB.md`. **Phase 4 — fully implemented.** Subcommands:

```
vocab add <term>                  # draft definition; user confirms; saved
vocab list [--status=<s>]         # browse (filter by status: new|reviewing|mastered|confused)
vocab show <term>                 # full record incl. test history
vocab edit <term> [--reset-mastery]   # update fields (status NOT user-editable except via --reset-mastery)
vocab merge <a> <b>               # collapse duplicates; preserve test history
vocab review [--strict]           # spaced-repetition test session (lenient by default per D3)
vocab gap                         # show "confused" terms ranked by staleness; feeds entry [3e]
vocab regen-md [--import]         # regenerate VOCABULARY.md from yaml; --import migrates v1.1
vocab undo                        # revert last vocab add (within 24h soft-stage)
```

See `VOCAB.md` for the full procedure spec, state machine, and grading rules.

## Status surface

Routes to `STATUS.md`. **Phase 5 — fully implemented.** Read-only dashboard. Invocation forms:

```
/skill tutorial-creator status                  # direct invocation
/skill tutorial-creator                         # gateway question, then [4]
/skill tutorial-creator --mode status           # skip gateway, route directly
```

The dashboard aggregates `tutorial-config.yaml`, `vocabulary.yaml`, the last 10 session logs, generated `Day*.md` files, and the active progression. It shows:

- **Daily practice:** tutorials shipped, last lesson, streak, suggested-next-lesson short form
- **Vocabulary:** status counts (mastered / reviewing / confused / new), due-for-review count, recent additions
- **Gap radar:** top 3-5 confused terms sorted by staleness
- **Suggested next lesson:** one recommendation with candidate file, reason, and one-line action

Cold-start projects (no vocabulary, no tutorials) get a friendly empty-state message instead of an empty scaffold. The surface writes nothing and mutates nothing; it is safe to invoke as often as wanted.

See `STATUS.md` for the procedure spec, aggregate logic, and suggested-next-lesson tiebreak.

## Recovery

**Phase 6 — fully implemented.** Every tutorial generation is reversible. Vocab additions made standalone are reversible within 24h. Day-N renumbering rewrites every reference atomically. The recovery system has three commands and one always-on hook.

### Always-on: pre-write hook + session log

Before any tutorial generation writes a file, the skill runs the **pre-write hook**:

1. **Check `recovery_enabled`** in `tutorial-config.yaml` (default `true`). If false, skip the rest of this hook entirely. The user opted out of the filesystem footprint and has no undo available; proceed directly to generation.
2. **Compute session id.** ISO-8601 timestamp with `:` replaced by `-` (filesystem-safe), e.g. `2026-05-09T14-32-00`.
3. **Create the session directory.** `$PROJECT_ROOT/.claude/tutorial-sessions/<session_id>/`. `$PROJECT_ROOT` is the directory the resolution chain (`## Project resolution`) selected for this invocation — NOT necessarily cwd. For a project registered at `/Volumes/.../Tutorials/` invoked from anywhere else, the session directory lives at `/Volumes/.../Tutorials/.claude/tutorial-sessions/<id>/`.
4. **Snapshot the four files that will be modified.** All paths below are relative to `$PROJECT_ROOT`. For each, copy the *current* contents into the session directory before any modification:
   - `{tutorials_dir}/PROGRESS.md` → `.claude/tutorial-sessions/<session_id>/PROGRESS.md`
   - `{tutorials_dir}/VOCABULARY.md` → `.claude/tutorial-sessions/<session_id>/VOCABULARY.md`
   - `{tutorials_dir}/vocabulary.yaml` → `.claude/tutorial-sessions/<session_id>/vocabulary.yaml`
   - `.claude/tutorial-config.yaml` → `.claude/tutorial-sessions/<session_id>/tutorial-config.yaml`

   If a source file does not exist yet (e.g., first-run cold-start has no PROGRESS.md), record its absence in the snapshot manifest below as `path: ..., absent: true` and skip the copy. On undo, an absent snapshot means "the file did not exist; deleting it on revert is the correct action."
5. **Stage the session yaml.** Build the session record per `SCHEMAS.md` Schema 3 (mode, entry, gap_term, file, day_number, output, vocab_added empty list for now, snapshots manifest, four S49-reserved fields all `null`). Do NOT write the yaml to disk yet — `vocab_added` and `output` are populated by post-write hook.

### Always-on: post-write hook

After tutorial generation writes successfully:

1. **Populate session record.** Set `output` to the generated tutorial's relative path. Set `vocab_added` to the list of terms added during this generation (deduped). Set `progress_updated` to whether PROGRESS.md was modified (always true for entries [a-e]; may be false for some Path 2 audience-facing modes).
2. **Write the session yaml** to `.claude/tutorial-sessions/<session_id>.yaml`.
3. **Prune old sessions** (retention rule below).

If generation **fails** mid-write (e.g., the tool errors after some files have been modified but before all are):

1. Do NOT write the session yaml. The session directory contains pre-write snapshots; without the yaml, the directory is orphaned but harmless and will be pruned by retention.
2. Tell the user: `Generation failed mid-write. Pre-write snapshots are at .claude/tutorial-sessions/<session_id>/. Run "/skill tutorial-creator undo --session <session_id>" to manually revert.`

### Retention

Last 10 sessions retained on disk. At the start of every post-write hook (after the new yaml is written), enumerate session yamls sorted by `session_id` descending, keep the first 10, and silently delete:

- The session yaml `.claude/tutorial-sessions/<old_id>.yaml`
- The corresponding snapshot directory `.claude/tutorial-sessions/<old_id>/` (if it exists)

Pruning is silent. Retention applies to session yamls; standalone vocab-add sentinels (per `VOCAB.md`) prune separately on their own 24h schedule.

### `undo` command

Reverts the most recent tutorial generation. Invoked as:

```
/skill tutorial-creator undo                    # most recent session
/skill tutorial-creator undo --session <id>     # specific session (rare; for orphaned mid-write recovery)
```

#### Procedure

1. **Find the session.** Without `--session`, pick the session yaml with the lexicographically-largest `session_id`. With `--session`, find that specific yaml. If no session exists or the requested one is missing, say: `No session to undo.` and stop.

2. **Show what will revert.** Read the session yaml. Display:
   ```
   Undo session <session_id>?
     Mode:           <writing-to-learn | audience-facing>
     Entry:          <entry name>
     Generated:      <output path>
     Vocab added:    <count> terms (<list, capped at 5 with ellipsis>)
     Files affected: <count> files
   Type "yes" to revert, anything else to cancel.
   ```

3. **Defensive: snapshot the current state.** Before any restore, copy each currently-on-disk file in the session's `snapshots` manifest into a *new* sub-directory `.claude/tutorial-sessions/<session_id>/.pre-undo/`. This is the safety net: if the restore goes wrong halfway, the user has the pre-undo state too.

4. **Restore each snapshot.** For each entry in the manifest:
   - If `absent: true`, delete the on-disk file (it shouldn't exist post-revert).
   - Otherwise, copy `saved_to` over `path`.
   - On any I/O error: stop. Do NOT continue restoring other files. Tell the user: `Restore failed at <path>. Pre-undo snapshots are at .claude/tutorial-sessions/<session_id>/.pre-undo/. Inspect both directories before retrying.` Leave both `<session_id>/` and `<session_id>/.pre-undo/` in place untouched.

5. **Delete the generated tutorial file.** Whatever path is in the session's `output` field. If it's missing (user already deleted it manually), warn but continue: `Tutorial output already missing; skipping.`

6. **Clean up the session.** On full success, delete:
   - `.claude/tutorial-sessions/<session_id>.yaml`
   - `.claude/tutorial-sessions/<session_id>/` (the snapshot directory)
   - `.claude/tutorial-sessions/<session_id>/.pre-undo/` (the safety-net directory)

7. **Confirm to user.** `Reverted session <session_id>. Removed <output>; restored <count> files.`

#### Refusal cases

The skill refuses to undo (rather than guessing) when:
- The session yaml is missing or malformed (cannot parse). `Session yaml is unreadable; refusing to guess. Inspect .claude/tutorial-sessions/<id>.yaml manually.`
- Any `saved_to` path in the manifest does not exist on disk. `Snapshot file <path> is missing; refusing partial restore.`
- A file in the manifest has been modified since the session ran (compare the on-disk content against what the session yaml expects to find — for v2.0 the simple check is "does the file currently exist where the manifest says it should": if `absent: true` says "did not exist" but the file now exists with different content, warn before restoring).

The session log is the single source of truth for what to revert. If it's missing or malformed, refuse rather than guess.

### `renumber <old> <new>` command

Renames a Day-N tutorial file and rewrites every cross-reference. Supports whole-number days (`Day 8`) and half-step days (`Day 7.5`).

```
/skill tutorial-creator renumber 8 7.5
/skill tutorial-creator renumber 7.5 8
```

#### Procedure

1. **Find the source file.** Search `{tutorials_dir}` for any `Day<old>-*.md`. If zero matches, say `No file matches Day<old>-*.md` and stop. If multiple matches (shouldn't happen, but defend), show all and refuse.
2. **Compute the destination.** Replace `Day<old>` with `Day<new>` in the filename, preserving the rest of the path. If the destination already exists, refuse: `Day<new>-*.md already exists. Use 'undo' to revert that file first, or pick a different number.`
3. **Find all references.** Scan these files for the literal strings `Day<old>` and `Day <old>` (with and without space):
   - The source tutorial file itself (occasional self-reference)
   - `{tutorials_dir}/PROGRESS.md`
   - `{tutorials_dir}/VOCABULARY.md`
   - All other `{tutorials_dir}/Day*.md` files
4. **Show the diff.** Render a diff per file: `<file>: N references will change Day<old> → Day<new>`. List each line that will change with line numbers. Total summary at top: `Will rename 1 file and update N references across M files.`
5. **Confirm.** `Type "yes" to apply, anything else to cancel.`
6. **Apply atomically.** Either all changes apply or none:
   - First, write modified contents to all reference-holding files
   - Then, rename the source file (the rename is the last step)
   - On any I/O error mid-way, attempt to restore modified files to their pre-rename contents from in-memory copies you held; if that also fails, tell the user exactly which files are in inconsistent state and which paths to inspect
7. **Confirm to user.** `Renamed Day<old> → Day<new>; updated N references across M files.`

`renumber` does NOT write a session log entry — it's a structural rename, not a generation. To revert, run `renumber <new> <old>`.

### `vocab undo` integration

Standalone `vocab add` (outside tutorial generation) writes a 24h sentinel marker per `VOCAB.md`. `vocab undo` reverts these within 24h. See `VOCAB.md` § `vocab undo`.

Vocab additions that happen *during* tutorial generation are recorded in the session yaml's `vocab_added` field. When `undo` reverts a session, those terms are removed by the snapshot restore (vocabulary.yaml is restored to its pre-generation state). No double-bookkeeping: tutorial-time adds do NOT also write sentinels.

## Writing Style

For all generated content:

- Use "you" — speak directly to the reader.
- Explain like a patient mentor, not a textbook.
- Connect new concepts to ones already covered in previous days.
- Use real code from the reader's project, not hypothetical examples.
- Keep annotations conversational: "This line is doing X because Y."
- Calibrate depth to `experience_level` per the Core Pattern section above.

## PROGRESS.md template

Created on first run:

```markdown
# Code Reading -- Progress Tracker

**Started:** [date]
**Goal:** Read one annotated file per session, building from simple to complex.

## Progression Path

| Phase | Focus | Files |
|-------|-------|-------|
| 1 | [Phase 1 name] | |
| 2 | [Phase 2 name] | |
| 3 | [Phase 3 name] | |

## Score Log

| Day | Date | File | Pre-Test | Post-Test | Delta | Concepts to Revisit |
|-----|------|------|----------|-----------|-------|---------------------|
| 1 | | | / | / | | |

## Scoring Guide

- **7-8 correct:** You've got this concept down. Move on.
- **5-6 correct:** Good foundation. Review the missed questions.
- **3-4 correct:** Re-read the annotated sections for missed concepts.
- **0-2 correct:** Spend extra time on this file. Try writing similar code from scratch.

## Concepts Mastery Checklist

Check off when you feel confident (not just "saw it once"):

### Phase 1: [Phase name]
- [ ] (populated as tutorials are created)
```

## VOCABULARY.md template (generated view)

Created on first run; regenerable from vocabulary.yaml:

```markdown
# Tutorial Vocabulary

Terms introduced in each tutorial, in order of appearance.

> Source of truth: `vocabulary.yaml` (this file is a generated view; do not edit by hand).

---

(Sections added as tutorials are created)

---

## Cumulative Count

| Day | New Terms | Running Total |
|-----|-----------|---------------|

---

*Updated: [date]*
```

## Phase Progressions

Built-in progressions live in `progressions/<language>.yaml` (loaded from the skill bundle, not the user's project). v2.0 ships with Swift, TypeScript, Python, and Rust. Custom progressions go via `progression_override` in `tutorial-config.yaml`.

See `SCHEMAS.md` Schema 4 for the progression yaml format.

## Schemas

All persistent data shapes (tutorial-config, vocabulary, session-log, progressions) are documented in `SCHEMAS.md`. When in doubt, that file is the source of truth.

## What's coming next

| Phase | Adds | Status |
|---|---|---|
| 1 | Externalized progressions, schemas, vocab example | ✅ shipped |
| 2 | Surfaces split, gateway question, --mode flag, stubs | ✅ shipped |
| 3a/b/c | Writing-to-learn entries [a] daily, [b] topic+file, [c] topic-only | ✅ shipped |
| 4 | Full vocab surface (add, list, review, gap radar, state machine) | ✅ shipped |
| 3d/e/f | Writing-to-learn entries [d] question, [e] gap, [f] external | ✅ shipped |
| 5 | Status dashboard | ✅ shipped |
| 6 | Recovery (undo, renumber, 24h soft-stage) | ✅ shipped (this) |
| 6.5 | Project resolution: `--project-dir`, env var, ancestor walk, registry, `open`/`forget` subcommands | ✅ shipped (2026-05-10) |
| 7 | Audience-facing path with 6 venue templates | ⚠️ partial (this): routing + AUDIENCE.md + 3 of 6 venues shipped (`reddit`, `book-chapter`, `apple-developer-article`); `medium`, `blog`, `repo-doc` pending |
| 7 (final) | Remaining 3 venue templates (`medium`, `blog`, `repo-doc`) | ⏳ pending |
| 8 | Polish, CHANGELOG, demo bundles, v2.0.0 release | ⏳ pending |
| 8 | Polish, README rewrite, v2.0.0 release | ⏳ pending |

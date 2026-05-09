---
name: tutorial-creator
description: Generate annotated code reading tutorials from your own codebase. Three surfaces - tutorial generation, vocabulary management, and learning-state inspection. Tracks vocabulary with status state machine, supports six writing-to-learn entry points and five audience-facing entry points.
version: 2.0.0-phase2
author: Terry Nyberg, Coffee & Code LLC
license: Apache-2.0
---

# tutorial-creator

Three surfaces, gateway-mediated:

- **`tutorial`** — generate a lesson (six writing-to-learn entries, five audience-facing entries)
- **`vocab`** — manage vocabulary independent of lesson generation
- **`status`** — inspect your learning state (read-only dashboard)

> **v2.0 in development.** Phase 2 of 8 ships the router + gateway question + surface stubs. Phases 3+ ship the actual generation, vocab management, status, recovery, and audience-facing paths. See `~/.claude/plans/tutorial-creator-v2-implementation.md`.
>
> The legacy v1.1 invocation (`/skill tutorial-creator <topic> <source>`) routes to entry [b] (topic + file) and produces v1.1-shaped output until later phases land.

## Usage

```
/skill tutorial-creator                         # opens gateway question
/skill tutorial-creator <topic> <source>        # legacy v1.1 path → entry [b]
/skill tutorial-creator tutorial <args>         # tutorial surface
/skill tutorial-creator vocab <subcommand>      # vocab surface
/skill tutorial-creator status                  # status surface
/skill tutorial-creator undo                    # revert last generation (Phase 6)
/skill tutorial-creator --mode learn|audience|both|vocab|status [args]
                                                 # skip gateway, route directly
```

## Routing logic

Every invocation runs through this dispatch:

1. **Read `--mode` flag if present.** If set, echo it back to the user as a one-line confirmation, then jump directly to that surface or path. Skip the gateway question. Mode values: `learn`, `audience`, `both`, `vocab`, `status`.
2. **Else, parse positional arguments.** If the user invoked with two positional args matching `<topic> <source>` AND the source is an existing file in the project, treat as **entry [b] legacy path** — produce a v1.1-shaped tutorial. This preserves the v1.1 invocation contract for users who haven't seen the v2 changes.
3. **Else, ask the gateway question.** Present the four-option menu (below). Route based on answer.

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
- **Answer [2]** → tutorial surface, Path 2 (audience-facing). Ask the entry-point question (five options; Phase 7 stub).
- **Answer [3]** → vocab surface (load `VOCAB.md`).
- **Answer [4]** → status surface (load `STATUS.md`).

### Mode-mismatch detection

If the user picked Path 2 (audience-facing) but their topic phrasing reads "I want to understand X" or "I'm confused about Y," soft-nudge once:

> This phrasing reads like writing-to-learn. Confirm audience-facing, or switch to writing-to-learn?

One nudge per session. Not blocking. The user always has final say. (Implemented in Phase 7.)

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

### Phase 2 status

Only **entry [b] legacy path** (writing-to-learn, topic + file) is implemented. It produces v1.1-shaped output by following the "Tutorial Format" specification below. All other entries return:

> Entry [<letter>] is not yet implemented in v2.0-phase2. Coming in Phase 3 or 7. See `~/.claude/plans/tutorial-creator-v2-implementation.md`.

## First-Run Setup

On first invocation in a new project, check for `.claude/tutorial-config.yaml`. If missing, run setup:

```
Welcome to tutorial-creator! Let's set up your learning environment.
```

Ask via AskUserQuestion:

1. **Where should tutorials be saved?** Default: `./tutorials/`
2. **What language/framework are you learning?** Auto-detect from project files (`package.json` = JS/TS, `Package.swift` = Swift, `Cargo.toml` = Rust, etc.); user confirms or overrides.
3. **What's your experience level?** beginner / intermediate / advanced.
4. **What's your project directory?** Default: current working directory.

Save config to `.claude/tutorial-config.yaml` per `SCHEMAS.md` Schema 1:

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

Create initial files:
- `{tutorials_dir}/PROGRESS.md` (template at end of this file)
- `{tutorials_dir}/VOCABULARY.md` (regenerated view)
- `{tutorials_dir}/vocabulary.yaml` (empty list `[]`)

If `.claude/` doesn't exist, create it.

## Entry [b] — Tutorial Format (legacy v1.1 path)

When invoked as entry [b] (topic + file), produce a tutorial with these sections in this order. This is the v1.1 format preserved verbatim.

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

### After Writing

1. **Save** to `{tutorials_dir}/DayN-[Topic]-Annotated.md`
2. **Update PROGRESS.md** — add Score Log row (day, date, file, test counts) and Concepts Mastery Checklist entries (`- [ ] [Concept name] (Day N)`).
3. **Update VOCABULARY.md** — add new section `## Day N: [Topic]`; only genuinely new terms; update Cumulative Count.
4. **Increment** `next_day` in config.
5. **Gap analysis** — review the new tutorial; if it depends on uncovered concepts, propose half-step bridge tutorials (e.g., Day 7.5) with topic, what they bridge, and why. Ask whether to create now or defer.

## Vocab surface

Routes to `VOCAB.md`. Phase 4 implements full surface; Phase 2 ships stubs:

```
vocab add <term>            # not yet implemented (Phase 4)
vocab list [--status=<s>]   # not yet implemented
vocab show <term>           # not yet implemented
vocab edit <term>           # not yet implemented
vocab merge <a> <b>         # not yet implemented
vocab review                # not yet implemented
vocab gap                   # not yet implemented
vocab regen-md              # not yet implemented
```

See `VOCAB.md` for the loaded surface.

## Status surface

Routes to `STATUS.md`. Phase 5 implements aggregate dashboard; Phase 2 ships stub.

See `STATUS.md` for the loaded surface.

## Undo

Routes to recovery logic. Phase 6 implements; Phase 2 returns stub:

> `undo` is not yet implemented in v2.0-phase2. Coming in Phase 6.

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
| 2 | Surfaces split, gateway question, --mode flag, stubs | ✅ shipped (this) |
| 3 | All six writing-to-learn entry points | ⏳ pending |
| 4 | Full vocab surface (add, list, review, gap radar) | ⏳ pending |
| 5 | Status dashboard | ⏳ pending |
| 6 | Recovery (undo, renumber, 24h soft-stage) | ⏳ pending |
| 7 | Audience-facing path with 6 venue templates | ⏳ pending |
| 8 | Polish, README rewrite, v2.0.0 release | ⏳ pending |

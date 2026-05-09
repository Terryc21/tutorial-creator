# Vocab Surface — tutorial-creator v2

**Status:** Phase 2 stub. Full implementation in Phase 4.
**Loaded by:** `SKILL.md` when the user routes to `vocab <subcommand>` or chooses `[3]` from the gateway.
**Source of truth for the schema:** `SCHEMAS.md` Schema 2 (`vocabulary.yaml`).

---

## Phase 2 behavior

In Phase 2, every vocab subcommand returns a "not yet implemented" message that points the user at the implementation plan. Specifically:

```
$ /skill tutorial-creator vocab add "@MainActor"

Vocab surface is not yet implemented in v2.0-phase2.
Coming in Phase 4 (~5 hr scope).

Plan:    ~/.claude/plans/tutorial-creator-v2-implementation.md
Design:  ~/.claude/plans/tutorial-creator-robust-design.md
Schema:  skills/tutorial-creator/SCHEMAS.md (Schema 2)

Until Phase 4 lands, vocabulary is managed via the v1.1 path:
generate a tutorial via entry [b], which writes to VOCABULARY.md
in your tutorials directory.
```

Same response for: `vocab list`, `vocab show`, `vocab edit`, `vocab merge`, `vocab review`, `vocab gap`, `vocab regen-md`. Subcommand name is echoed back so the user can confirm the parser saw their intent.

## Phase 4 plan (preview, NOT for execution in Phase 2)

When Phase 4 begins, this file expands to the full vocab surface specification. The Phase 4 surface includes:

- **`vocab add <term>`** — AI drafts a definition; user accepts/edits/cancels. Writes to `vocabulary.yaml` per Schema 2. 24-hour soft-stage marker for `vocab undo`.
- **`vocab list [--status=<status>]`** — render vocabulary.yaml as a table sorted by term; filter by status if flag.
- **`vocab show <term>`** — full record including test_history, applied_test_history (empty in v2.0), related_terms, notes.
- **`vocab edit <term>`** — interactive edit of `definition`, `type`, `related_terms`, `notes`. Status is NOT user-editable; it's earned through tests.
- **`vocab merge <term-a> <term-b>`** — combine duplicates. New term keeps `term-a`'s name; test histories concatenate; status recomputes from merged history.
- **`vocab review [--strict]`** — spaced-repetition test session. Picks 5 terms prioritizing confused > due-for-review > fresh. Lenient grading by default; `--strict` enforces verbatim.
- **`vocab gap`** — show terms with `status: confused` ranked by staleness (longest-confused first). Suggest "generate a tutorial for one of these?" — feeds tutorial entry [3e] (gap-driven).
- **`vocab regen-md`** — regenerate `VOCABULARY.md` from `vocabulary.yaml`. Manual safety net after yaml edits. `--import` flag converts an existing v1.1 `VOCABULARY.md` Markdown table into yaml.

## State machine (reference; implemented Phase 4)

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

Status is **earned through tests, not set directly.** The only user-controllable transition is `mastered → reviewing` via `vocab edit --reset-mastery <term>`.

## Why this stub exists

Phase 2 ships a router with surface stubs so:

1. The gateway question routes to all four destinations cleanly (no dead routes)
2. `--mode vocab` is testable end-to-end (it loads VOCAB.md and gets the stub response)
3. Phase 4's job is purely "fill in the implementation"; structure is already in place

Without this stub, Phase 2 would either fail when routing to vocab (broken UX) or silently absorb the route (dishonest UX). The stub is the honest-machine answer: "this isn't ready yet; here's where it's tracked."

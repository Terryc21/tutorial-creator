# Status Surface — tutorial-creator v2

**Status:** Phase 2 stub. Full implementation in Phase 5.
**Loaded by:** `SKILL.md` when the user invokes `status` or chooses `[4]` from the gateway.

---

## Phase 2 behavior

```
$ /skill tutorial-creator status

Status surface is not yet implemented in v2.0-phase2.
Coming in Phase 5 (~2 hr scope).

The status dashboard will aggregate:
  - Tutorials shipped, last lesson, streak, suggested next
  - Vocabulary counts by status (mastered / reviewing / confused / new)
  - Due for review (terms unreviewed > 14 days)
  - Gap radar (top 3-5 confused terms with staleness)
  - Suggested next lesson (vocab gap + progression candidate)

Plan:    ~/.claude/plans/tutorial-creator-v2-implementation.md
Design:  ~/.claude/plans/tutorial-creator-robust-design.md
```

## Phase 5 plan (preview, NOT for execution in Phase 2)

When Phase 5 begins, this file expands to the full status implementation. Output format is a text dashboard per design decision D2:

```
────────────────────────────────────────────────────────────
  tutorial-creator — learning state
  Project: <name>  ·  Language: <lang>  ·  Level: <level>
────────────────────────────────────────────────────────────

Daily practice
  Tutorials shipped:    N
  Last lesson:          Day N (date) — topic
  Streak:               N days
  Suggested next:       <concept> (Phase N of progression)

Vocabulary  (N terms)
  ┌─────────────────┬─────┐
  │ status          │ N   │
  ├─────────────────┼─────┤
  │ mastered        │ ... │
  │ reviewing       │ ... │
  │ confused        │ ... │  ← see "Gap radar" below
  │ new             │ ... │
  └─────────────────┴─────┘

  Due for review: N terms (last reviewed > 14 days)
  Recent additions: N in last week

Gap radar
  1. <term>          confused N days
  ...

  Suggested next lesson:    <term>
    Candidate file:         <path>
    Reason:                 <heuristic explanation>
    Action:                 /skill tutorial-creator gap → 1
```

### Aggregate query

Phase 5 reads:

- `.claude/tutorial-config.yaml` — project metadata
- `{tutorials_dir}/vocabulary.yaml` — all vocab status
- `.claude/tutorial-sessions/*.yaml` — session history (for streak, last lesson, last 10 sessions)
- `{tutorials_dir}/Day*.md` — to count tutorials shipped
- `progressions/<lang>.yaml` (or override) — for "suggested next" within progression

### Empty-state handling

If a project has no vocab and no tutorials yet, status renders a friendly cold-start message:

```
You haven't shipped any tutorials yet. Start with:
  /skill tutorial-creator                  # opens the gateway question
or
  /skill tutorial-creator <topic> <file>   # legacy v1.1 invocation
```

## Why this stub exists

Same rationale as `VOCAB.md`: Phase 2 ships a router with stubs at every destination so all routes are reachable, the contract is honest about what's ready and what isn't, and Phase 5 has nothing to wire — only an implementation to write.

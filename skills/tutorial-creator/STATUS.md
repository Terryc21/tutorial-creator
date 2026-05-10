# Status Surface — tutorial-creator v2

**Status:** Phase 5 implementation. Read-only learning-state dashboard.
**Loaded by:** `SKILL.md` when the user invokes `status`, chooses `[4]` from the gateway, or passes `--mode status`.
**Source of truth for the schemas:** `SCHEMAS.md` (Schemas 1-4).

---

## Surface contract

The status surface is read-only. It writes nothing. It mutates nothing. Invoking it twice in a row produces identical output (modulo time-since-last-lesson).

The surface aggregates four data sources into one text dashboard:

1. Project metadata (`tutorial-config.yaml`)
2. Vocabulary state (`vocabulary.yaml`)
3. Session history (`tutorial-sessions/*.yaml`)
4. The active progression (`progressions/<lang>.yaml` or override)

The output answers four questions a learner asks themselves:

- How long is my streak, and what was my last lesson?
- What's my vocabulary looking like — what do I know, what am I confused about?
- What should I review or generate next?
- Am I caught up, or am I behind?

If the user has no data yet (no vocabulary, no tutorials), the surface short-circuits to a friendly cold-start message instead of rendering an empty scaffold.

## File locations (read paths)

```
.claude/tutorial-config.yaml                  # project metadata (Schema 1)
{tutorials_dir}/vocabulary.yaml               # Schema 2
.claude/tutorial-sessions/*.yaml              # Schema 3 (last 10 retained)
{tutorials_dir}/Day*.md                       # generated tutorial files
progressions/<language>.yaml                  # Schema 4 (skill bundle)
```

`{tutorials_dir}` and `language` come from `tutorial-config.yaml`. If `progression_override` is set, that path replaces the bundled progression yaml.

## Procedure

### 1. Read inputs

Before rendering anything, gather:

- **`.claude/tutorial-config.yaml`** — `tutorials_dir`, `language`, `experience_level`, `next_day`, `progression_override`. Treat missing fields as defaults per Schema 1.
- **`{tutorials_dir}/vocabulary.yaml`** — full term list. For each term, you need: `term`, `status`, `test_history`, `first_encountered.date`, `related_terms`. If the file is missing, treat vocab as empty.
- **`.claude/tutorial-sessions/*.yaml`** — sort filenames descending by `session_id`. The first item is the last lesson. Walk consecutive days backward from today to compute streak. Total session count is one input to "tutorials shipped"; cross-check it against the next bullet.
- **`{tutorials_dir}/Day*.md`** — count files matching `Day<n>-*.md` (whole or half-step day numbers like `Day7.5-*.md`). Cross-check against session log count. If they disagree, prefer the lower number and surface a one-line warning under the dashboard ("Note: 5 session logs but 4 Day*.md files; one tutorial may have been deleted manually.").
- **`progressions/<language>.yaml`** (or `progression_override` from config) — the list of phases and their concept arrays.

### 2. Empty-state branch

If **both** are true:

- `vocabulary.yaml` is missing OR contains zero terms
- No `Day*.md` files exist in `{tutorials_dir}`

Then render the cold-start block below and **stop**. Do not render the dashboard scaffolding, do not run the suggested-next-lesson logic.

```
You haven't shipped any tutorials yet. Start with:
  /skill tutorial-creator                  # opens the gateway question
or
  /skill tutorial-creator <topic> <file>   # legacy v1.1 invocation
```

### 3. Compute aggregates

Compute these values before rendering. Use today's date (`YYYY-MM-DD`) as the reference point throughout.

- **Vocab status counts.** Count terms by `status` field: `mastered`, `reviewing`, `confused`, `new`. Each count appears in the box-drawing table.
- **Due for review.** Count terms where `status == reviewing` AND (`test_history` is empty OR the most recent `test_history.date` is more than 14 days ago). "Due" applies only to the `reviewing` tier — `mastered` terms are not "due"; `new` terms have not yet been tested; `confused` terms are surfaced via gap radar instead.
- **Recent additions.** Count terms whose `first_encountered.date` is within 7 days of today.
- **Gap radar.** Filter to `status == confused`. Sort by staleness descending: staleness = days since the most recent `test_history.date`, or if `test_history` is empty, days since `first_encountered.date`. Take the top 3-5 (5 if available; otherwise as many as exist). Render each as `<term>          confused N days`.
- **Streak.** Count consecutive days ending today that have at least one session-log entry. Today counts only if at least one session log exists for today's date. One missed day breaks the streak; the streak starts from the most recent unbroken run ending today.
- **Last lesson.** Most-recent session log. Extract `output` (strip directory prefix), `day_number`, and the date portion of `session_id` (drop the time portion).
- **Tutorials shipped.** Reconciled count from step 1.

### 4. Suggested next lesson

Pick exactly one suggestion using the tiebreak below.

- **Candidate (a) — vocab gap.** The top-1 confused term from gap radar (the same first row of step 3's gap radar). Reason line: `addressing your most-confused term`. Candidate file: scan `project_dir` for files whose contents reference the term (the smallest match under 300 lines wins; if the term is something like `@MainActor`, prefer files with multiple references over single-mention files).
- **Candidate (b) — progression.** Read the active progression yaml. Find the current phase by inferring from `next_day`: if `next_day == 1`, use phase 1; otherwise, use the phase that contains the concept the user most recently shipped (look at the last lesson's title or `vocab_added`), or fall back to the highest phase where any concept is still unshipped. Pick the next concept in that phase that does NOT yet appear as a heading in any `Day*.md` file. Reason line: `next concept in your progression`. Candidate file: same scan heuristic as (a).

Tiebreak:

- If `confused` count > 0, use (a).
- Else if (b) produces a candidate, use (b).
- Else render the all-caught-up line: `Suggested next lesson: All caught up. Try a question-led entry: /skill tutorial-creator --mode learn → [d]`.

If the chosen candidate's file scan returns no good match (zero files under 300 lines, or no files at all reference the term/concept), still render the suggestion but replace the candidate-file line with `Candidate file: (no obvious match — let the skill scan when you start)` and replace the action line with `Action: /skill tutorial-creator <term-or-concept>`.

### 5. Render the dashboard

Use this exact layout. Box-drawing characters in the vocabulary table are non-negotiable (per design decision D2).

```
────────────────────────────────────────────────────────────
  tutorial-creator — learning state
  Project: <name>  ·  Language: <lang>  ·  Level: <level>
────────────────────────────────────────────────────────────

Daily practice
  Tutorials shipped:    N
  Last lesson:          Day N (date) — <topic>
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
  2. <term>          confused N days
  ...

  Suggested next lesson:    <term-or-concept>
    Candidate file:         <path>
    Reason:                 <addressing your most-confused term | next concept in your progression>
    Action:                 /skill tutorial-creator <term-or-concept>
```

Substitution rules:

- `<name>` is the directory basename of `project_dir` (or `tutorials_dir`'s parent if `project_dir == .`).
- `<lang>` and `<level>` come from `tutorial-config.yaml` directly (`language`, `experience_level`).
- The "Daily practice → Suggested next" line and the "Suggested next lesson" block reference the SAME suggestion. Daily practice shows the short form (concept + phase); the bottom block shows the full reasoning. Do not pick two different suggestions.
- If gap radar has fewer than 3 confused terms, render only the rows that exist; do not pad with placeholders. If gap radar is empty, omit the "Gap radar" block entirely and write "Gap radar: no confused terms (great)" on a single line above the suggested-next-lesson block.
- If a session-log/Day*.md count mismatch was detected in step 1, append a single italic line below the dashboard: `_Note: <warning text>._`

### 6. Stop

The status surface is done. No prompts, no follow-up questions, no offers to generate something. The user reads the dashboard and decides what to do next.

## Performance notes

- Reading 30 vocabulary terms + 10 session logs + 4 progression yamls is well under any context concern.
- The candidate-file scan in step 4 is the only operation that touches user code. Bound it: scan up to 50 files, prefer files under 300 lines, stop after the first 3 plausible matches and pick the smallest.
- If the project has thousands of files, the scan should respect `.gitignore` and skip `node_modules`, `Pods`, `.build`, `DerivedData`, and similar build directories — same heuristic the writing-to-learn entry [c] uses.

## Out of scope (do NOT do here)

- Writing files. Status is read-only.
- Modifying vocabulary status. That's done by `vocab review`.
- Recommending more than one next lesson. Pick one.
- Showing every confused term. Cap gap radar at 5.
- Showing every session ever logged. The dashboard's history surface is "last lesson + streak"; full history is queryable via `vocab show <term>` for individual terms.

## Why this surface exists

`tutorial-creator` v1.1 told users what to do (generate a tutorial) but not where they stood. Status answers the second question without coupling it to the first. A user can open status, glance at gap radar, and decide whether the right next move is `vocab review`, a gap-driven tutorial, or simply continuing the daily progression. The dashboard is the cheapest way to make the writing-to-learn loop legible to its owner.

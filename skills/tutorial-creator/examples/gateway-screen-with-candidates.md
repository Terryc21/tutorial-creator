# Gateway screen — with topic candidates

> [!NOTE]
> This is a **sample of what the skill shows you on invocation**, not a tutorial it produced.
> The other examples in this directory are finished tutorials; this one is the screen you see
> *before* choosing what to write. Captured verbatim from a real session on
> [Stuffolio](https://stuffolio.app), the source project the skill was extracted from.

---

## What you're looking at

Invoking `/skill tutorial-creator` with no arguments opens the gateway question — four surfaces,
pick one. That part is fixed and documented in `SKILL.md` § "Gateway question".

What this example shows is the gateway rendered **at the end of a working session**, where the
skill had the session's own material in context and could name specific candidates instead of
handing over an empty prompt. The four options are the same; the candidate table is the part
worth studying.

---

## The screen

> ## Introductory screen for Tutorial-Creator
>
> You invoked `/tutorial-creator`. What would you like to do?
>
> **[1] Write a tutorial for myself** — for my own learning
> **[2] Write a tutorial for others** — preparing a lesson for others to learn
> **[3] Manage vocabulary** — edit vocabulary
> **[4] Inspect my learning state** — see progress and what you're forgetting
>
> ---
>
> Worth noting: this session left unusually good raw material behind, all with **measured
> evidence** already written down.
>
> | Candidate | Why it's strong |
> |---|---|
> | **The unfollowed cursor** | The app saw 100 of 2,420 records, silently, for weeks — because `records(matching:)` returns one page and the cursor was declared but never read |
> | **The bug behind the bug** | Fixing pagination immediately exposed a 400-ID fetch cap that had been *unreachable* while the first bug existed |
> | **The correct fix that caused damage** | A verified-correct fix landed on an inconsistent data model and duplicated a 1,129-item library |
>
> The third is the most interesting and the least written-about. It's a CloudKit-specific story
> with a general lesson: a fix can be right in isolation and still be wrong to ship, if the data
> it newly exposes was never reconciled.

---

## Why the candidates are shaped that way

Three properties make the difference between a useful suggestion and noise:

**Every candidate carries a measurement.** "100 of 2,420 records", "1,129-item library",
"400-ID cap". Not "a sync bug" or "an interesting CloudKit issue". A candidate you can't
quantify usually turns out to be a candidate you can't write, because the specifics that make
a tutorial worth reading were never captured.

**The recommendation is ranked, with a reason.** The third candidate is called out as strongest
*and why* — "the least written-about", plus the general lesson under the specific bug. A list of
three equal options pushes the choice back to the user unaided, which is the thing the gateway
is supposed to help with.

**The general lesson is separated from the specific bug.** The closing line names what the
third candidate is *about* beyond CloudKit — "a fix can be right in isolation and still be wrong
to ship." A candidate that is only a war story gives the user nothing to decide with; naming the
transferable claim is what makes it look writable.

---

## What it does NOT do

It does not pick for you. The four options are unchanged and unweighted — the candidate table
sits below them as advice, not as a fifth option or a pre-selection. If none of the three appeal,
`[1]`–`[4]` behave exactly as they always do, and the entry-point question follows normally.

It also does not fabricate candidates to fill the table. This screen appeared because the session
genuinely produced three findings with measured evidence. A session that ended without material
worth writing up shows the four options alone — which is the honest output, and the common one.

---

## Reproducing this shape

Nothing in the skill generates this table automatically today; it comes from the runtime having
the session's own findings in context when the gateway fires. If you want it, the conditions are:

1. Invoke the gateway **at the end of substantive work**, not the start of a fresh session.
2. Have the findings **written down with numbers** — a ledger row, an incident file, a commit
   body. Prose recollection produces vague candidates.
3. Ask for the gateway plainly (`/skill tutorial-creator`), rather than jumping straight to a
   surface with `--mode`. Skipping the gateway skips this.

Invoked cold in a fresh session, the same command shows the four options and nothing else. That
is correct behaviour, not a degraded one.

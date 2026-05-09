---
venue: reddit
voice: punchy
sectioning: minimal
code_blocks: inline-heavy
front_matter:
  title_only: true
length_budget:
  S: { words: 200, ceiling: 350 }
  M: { words: 600, ceiling: 900 }
  L: { words: 1500, ceiling: 2200 }
  X: { words: 3000, ceiling: 4500 }
honest_machine_section_name: Edit
---

# Venue: reddit

Renders an audience-facing tutorial as a Reddit post. The reader is scrolling a subreddit feed and decides in the first two lines whether to keep reading. Optimize for that decision.

## Voice signature

- One-thread arc with a payoff. The post sets up a problem in the first paragraph and pays it off by the end. No nested headers competing for the reader's attention.
- Conversational, first-person, occasionally self-deprecating. "I spent three days on this. Here's what fixed it." Not "An analysis of the cancellation behavior of `.task(id:)`."
- Inline code with backticks for short symbols (`Task.detached`, `@MainActor`); fenced code blocks only when a multi-line example is unavoidable. Reddit's markdown handles fences but readers skim past long ones.
- Minimal sectioning. At most one or two `**bold subheads**` mid-post if the structure genuinely needs them. Never `##` headers; those read as overworked for the medium.
- Closing line is a takeaway or a question, not a summary. "If you've hit this, the fix is one line." Or "Anyone else seen this fire on iOS 26 only?"

## Sectioning

Reddit posts are flat. The structure is:

1. Opening hook (1-2 sentences): the symptom or the surprise
2. Setup (1-3 paragraphs): what you tried, what you expected
3. The reveal (1-2 paragraphs): the actual cause
4. The fix (often 1 short fenced block + 1 sentence)
5. Closing: takeaway, caveat, or question

No table of contents. No `## Conclusion`. The reader doesn't want navigation; they want to finish the post.

## Code blocks

- Prefer inline backticks for symbols, type names, and short expressions
- Use fenced blocks (```swift) only for the actual fix or the actual bug-line. One block per post is the target; two is acceptable; three is too many for the medium.
- Strip imports, framework boilerplate, and unrelated lines. Reddit readers infer context.
- If the fix is a one-line diff, write it as `// before` and `// after` comments inside one fenced block, not two blocks.

## Front matter

Reddit posts have a title only (no subtitle, no chapter number, no tags from the venue's perspective; tags are subreddit-side). The skill emits a single `# Title` line at the top.

Title conventions:

- Pose the problem or the surprise. "SwiftData's `migrationPlan` re-introduced a crash I'd already fixed."
- Avoid "TIL" / "PSA" / "Hot take"; those signal low-effort to most subreddits the skill is likely to target (`r/swift`, `r/iOSProgramming`, `r/swiftui`).
- Length: 60-100 chars. Reddit truncates titles in feeds past ~80 on mobile.

## Length budget calibration

| Tier | Words | Ceiling | What changes at this tier |
|---|---|---|---|
| S | 200 | 350 | Single example. No setup paragraph; jump to symptom + fix. One fenced block max. |
| M | 600 | 900 | Standard post. Setup, reveal, fix, closing. One or two fenced blocks. The default. |
| L | 1500 | 2200 | Long-form post. Two examples or two failure modes contrasted. Up to three fenced blocks. Mid-post `**subheads**` permitted. |
| X | 3000 | 4500 | Reddit "essay post." Rare on the medium; the skill should warn the user that L is usually a better fit and X risks reading like a Medium piece pasted into a comment box. |

When budget is S, the model drops the second example entirely rather than abbreviating both. When budget is X, the model adds a second contrasting failure mode rather than padding the original.

## Audience interaction

- **beginner**: shift content toward setup ("for context, `.task(id:)` is SwiftUI's way to bind an async task to a view's identity"). Add one parenthetical definition per unfamiliar symbol.
- **intermediate**: default voice. Assume the reader recognizes the symbols; explain the gotcha.
- **senior**: shift toward tradeoffs ("the obvious alternative is a manual `Task` with cancellation, but you lose the identity-binding semantics"). Drop introductory definitions.
- **mixed**: write for intermediate. The post will lose senior readers in the setup if you over-explain, and lose beginner readers everywhere if you under-explain; pick a single audience.

## Honest-machine section

When `honest_machine_optin: true`, append an "Edit:" section at the bottom (not a `## What this does NOT cover` header, which reads academic). Reddit convention is "Edit: clarifying X" or "Edit: things this post doesn't cover." Use the latter framing for the honest-machine section.

Format:

> **Edit:** what this doesn't cover:
> - <gap 1, one line>
> - <gap 2, one line>
> - <gap 3, one line, optional>

Three bullets max. Reddit readers will downvote a post that buries them in caveats.

## Voice exemplar (V3 schema migration, audience=intermediate, budget=M, hm=on)

> # SwiftData's `migrationPlan:` parameter re-introduced a crash I'd already fixed.
>
> Shipped a schema change for v3 of my app last week. Wired up a `VersionedSchema` and a `SchemaMigrationPlan` with a single `MigrationStage`. Tested in the simulator with seeded v2 data: clean migration, three runs in a row.
>
> Cold-relaunched on a real device. Crash on app launch: `Duplicate version checksums detected`.
>
> Spent two days on this. Tried fork-A, fork-B, fork-C of the v3 schema. Same crash every time. The `VersionedSchema` contract was rejecting the migration plan at the point where SwiftData computes a checksum across all `versionedSchemaIdentifiers`, because v2 and v3 referenced the same Swift types: same checksums, "duplicate."
>
> The fix turned out to be: stop passing the migration plan at all.
>
> ```swift
> // before (the plan that crashed)
> let container = try ModelContainer(
>     for: Item.self,
>     migrationPlan: AppMigrationPlan.self,
>     configurations: ModelConfiguration()
> )
>
> // after (implicit lightweight migration)
> let container = try ModelContainer(
>     for: Item.self,
>     configurations: ModelConfiguration()
> )
> ```
>
> SwiftData's lightweight migration handles additive schema changes (new optional properties, new model classes, new optional relationships) without a `SchemaMigrationPlan` at all. If your change is additive, omitting `migrationPlan:` is the working answer. The `VersionedSchema` machinery is only needed for non-additive changes (renames, type changes, cardinality flips).
>
> Symptom-to-cause was inverted on this one: the framework's "official" migration path was the bug, not my schema.
>
> **Edit:** what this doesn't cover:
> - The Bucket B/C path (renames, deletes) genuinely need `VersionedSchema` and a 2-3 day migration spike.
> - Pre-iOS 17 lightweight migration (Core Data territory; same idea, different APIs).
> - How to detect that you're in the additive bucket before you commit; I'm working on a script for that.

The exemplar above is ~280 words including the title and the "Edit" section. That's M-tier (target 600, ceiling 900), below the target on purpose. Reddit posts are usually shorter than the budget allows. Treat the budget as a ceiling, not a floor.

## What reddit is NOT

- Not a tutorial. Reddit posts pose-and-resolve; tutorials teach a technique end-to-end. If the user wants a tutorial, audience-facing path [a] (annotated source) into the `book-chapter` or `apple-developer-article` venue is a better fit.
- Not a bug report. Reddit posts that read as bug reports get redirected to the project's issue tracker. Frame the post as a story or a finding, not a request for help (unless the post genuinely IS a request for help, in which case the title should signal that explicitly).
- Not a marketing post. If the source happens to mention a paid product, the skill must not let the post drift into pitch territory. Reddit communities downvote pitches and the user loses karma.

## Recovery hook interaction

Reddit posts (like all Path 2 audience-facing artifacts) do NOT trigger the recovery system. They don't update PROGRESS.md, vocabulary.yaml, or write a session yaml. The artifact is a standalone file the user copies into Reddit's editor; the skill's job ends at the file write. If the user wants the post tracked, they should pair it with a Path 1 entry (writing-to-learn) on the same source.

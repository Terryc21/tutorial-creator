---
venue: medium
voice: magazine-essay
sectioning: light-headers
code_blocks: fenced-sparingly
front_matter:
  title: required
  subtitle: optional
  lede: required
length_budget:
  S: { words: 600, ceiling: 900 }
  M: { words: 1500, ceiling: 2200 }
  L: { words: 3000, ceiling: 4500 }
  X: { words: 6000, ceiling: 8500 }
honest_machine_section_name: "What this leaves out"
---

# Venue: medium

Renders an audience-facing tutorial as a piece for Medium, Substack, or any general-audience essay platform where the reader is browsing a curated feed of writers, not searching for an answer. The reader has clicked the title because it promised something interesting, and the first paragraph has a few seconds to convert that click into reading.

## Voice signature

This is the magazine-essay venue: more developed than a blog post, less ceremonial than a book chapter, more readable to a non-specialist than an Apple Developer article. The reader is a generalist who happens to be technical, or a technical reader looking for prose rather than reference material.

- Magazine-essay voice. The piece reads like a feature article, not a tutorial. There is a thesis or an observation the writer is developing, and the code is in service of that observation. Code listings are evidence; prose is the argument.
- The lede does the work. The first paragraph (or first two short paragraphs) sets up the piece's tension or surprise. A reader who finishes the lede should know what the piece is about and want to keep reading. A reader who does not finish the lede has clicked away.
- Conversational but structured. Sentences vary in length. Paragraphs run 3-5 sentences typically; a one-sentence paragraph for emphasis is a permitted move. The piece is easier to read than a book chapter and harder to skim than a Reddit post; it expects the reader's attention but works to keep it.
- Selective code. Code blocks are fenced and load-bearing when they appear, but they appear sparingly. A 1500-word Medium piece typically has two to four code blocks; one is too few to ground the piece, five is too many for the venue.
- The writer's voice is present but not central. First-person is permitted ("I spent two days on this"), as is third-person observational ("Anyone who ships a schema migration learns..."). Pick one register and hold it. The reader is interested in what the writer noticed, not in the writer.

## Sectioning

Light headers, in the magazine-essay style. A typical M-tier (1500 words) Medium piece has:

- `# Title` (single h1, set in front-matter)
- `## Subtitle` (optional; renders as Medium's subtitle field on import)
- The `lede` paragraph (no header; the first paragraph after the title)
- 2-4 `## section` headers, named for what the section covers (not numbered, not generic)
- No `### subsections`. If a section needs subdivision, the piece is trying to do too much; either tighten the section or split into two.

Medium itself accepts headers via Markdown import but renders them in a flatter visual hierarchy than a book chapter. The skill emits standard `##` headers and trusts the platform's rendering.

Section title conventions:

- Pose a question or name an observation. "What the migration plan was hiding" lands; "Migration plans" is a category, not a section.
- 3-7 words. Long enough to have shape; short enough that the reader's eye picks it out while scrolling.
- Avoid generic titles ("Conclusion", "Background", "The Problem"). Medium readers skim section titles to decide whether to keep reading; generic titles are skipped.

## Code blocks

- Fenced blocks with the language tag, sparing
- Each code block is preceded by a sentence that names what the code shows ("Here is the change that fixed it:") and followed by a sentence that names what to notice ("The difference is the parameter that is no longer there.")
- Strip imports and boilerplate. Medium readers are not copy-pasting into Xcode; they are reading the code as evidence for the prose.
- When two related code blocks compare alternatives, write the comparison in prose rather than expecting the reader to diff visually. "The original passed a migration plan; the working version omits it." then the two blocks. Medium's mobile rendering of code is narrow and often introduces line wrapping; the prose carries the comparison so the visual diff is supplementary.
- Avoid long code blocks (40+ lines). Medium's mobile reader will scroll past them. If the code is genuinely long, link to a Gist or a repo file and embed only the relevant excerpt.

## Front matter

Medium pieces have a title (required), an optional subtitle that surfaces in Medium's preview cards and below the title in the article view, and a lede (required) that is the first paragraph. The front-matter block:

```markdown
# <Title>

## <Optional subtitle>

<Lede paragraph: 2-4 sentences setting up the piece's tension.>
```

Title conventions:

- 6-12 words is the typical range for Medium. Long enough to convey the piece's angle; short enough to render fully in feed cards.
- Pose a question, name a tension, or surface a counterintuitive observation. "The framework's official path was the bug" or "What I learned from a schema migration that crashed at launch" are titles; "SwiftData migration plans" is a topic.
- Avoid clickbait register ("You won't believe what...", "10 things every iOS developer..."). Medium's audience associates the register with low-quality posts; the skill's pieces should read as deliberate.
- Title case is the platform default; the skill uses title case unless the user has a configured house style.

Subtitle conventions:

- Optional but recommended for M-tier and longer. Medium's subtitle is what surfaces beneath the title in feed cards and at the top of the article.
- 8-15 words. Extends the title's claim with a specific detail ("A two-day debug that ended in deleting four lines and adding none.").
- Reads as a journalist's deck, not as a summary. The subtitle is part of the click decision, not a recap.

Lede conventions:

- 2-4 sentences. Long enough to set up the tension; short enough that the reader is committed before they have scrolled.
- Names the observation or the surprise. "The migration plan was right. The crash was real. The fix was to delete the migration plan." is a lede; "This article discusses SwiftData migration plans." is not.
- Establishes the writer's voice in the first sentence. Medium readers decide within seconds whether the piece's voice matches their interest.

## Length budget calibration

| Tier | Words | Ceiling | What changes at this tier |
|---|---|---|---|
| S | 600 | 900 | A short Medium piece, the equivalent of a long Twitter thread or a substantial Substack note. One observation, one supporting case, no subsections. Ranges between newsletter-length and a "quick take" essay. |
| M | 1500 | 2200 | Standard Medium piece. One central observation developed across 2-3 sections, two to four code blocks, an optional contrasting case. The default for this venue. |
| L | 3000 | 4500 | A long-form essay. Two or three observations woven together, or a single observation developed with substantial historical or comparative context. Three to five sections, four to six code blocks. |
| X | 6000 | 8500 | A long-read feature, rare on Medium and approaching the ceiling for the platform's reading patterns. The skill warns the user that X-tier Medium pieces are usually better as a series of two or three M-tier pieces with a shared throughline. |

When budget is S, the piece drops the contrasting case and keeps only the central observation and the supporting code block. When budget is X, the piece adds a historical or comparative section ("The same lesson appears in...") that grounds the central observation in a longer pattern.

## Audience interaction

- **beginner**: extend the lede into a one-paragraph background that establishes the framework or platform vocabulary the piece assumes. Add brief parenthetical glosses for unfamiliar symbols on first appearance ("`@MainActor` (Swift's annotation for code that must run on the main thread)"). The piece should still develop its central observation; do not omit the argument, slow the entry into it.
- **intermediate**: default voice. The reader recognizes the framework and is reading the piece for the writer's observation about it.
- **senior**: tighten the lede; the senior reader is impatient with setup. Add a "Trade-offs" or "Where this fails" section near the close that addresses edge cases and second-order considerations. The senior reader should leave the piece with a question worth thinking about, not a recap of fundamentals.
- **mixed**: write for intermediate. Medium's audience itself is mixed, and the platform's reading patterns reward writing that addresses the largest middle band. Pieces that try to address all three audiences in the same article tend to lose the senior reader in the setup and the beginner reader in the trade-offs.

## Honest-machine section

When `honest_machine_optin: true`, append a `## What this leaves out` section near the end of the piece. The section runs 100-200 words, is in the piece's voice (not a bulleted appendix), and acknowledges what the piece does NOT address.

Format: a short prose paragraph or two, with optional bullets when the gaps are list-shaped. The section reads as the writer reflecting on the piece's scope, not as a disclaimer or a legal hedge. Examples of the right register: "The case study above covers only the additive bucket. Readers whose schema change involves a rename or a delete are in genuinely different territory; that territory deserves its own piece."

The section is not the closing of the piece. The piece's closing reflection (one or two paragraphs after `## What this leaves out`) carries the central observation home. The honest-machine section is the second-to-last beat, not the final word.

## Voice exemplar (V3 schema migration, audience=intermediate, budget=M, hm=on)

> # The framework's official path was the bug
>
> ## A two-day debug that ended in deleting four lines and adding none.
>
> The migration plan was wired up correctly. The version stages were declared. The simulator runs were clean: cold relaunch with seeded V2 data, three times in a row, no warnings. By every diagnostic available before shipping, the schema change was ready.
>
> Then the cold relaunch on a real device, and the crash on launch: `Duplicate version checksums detected`.
>
> ## The shape of the failure
>
> The crash refers to SwiftData's version-checksum reconciliation. The framework computes a checksum across each `VersionedSchema`'s `versionedSchemaIdentifiers` and refuses a migration plan when two schemas produce identical checksums. The plan in question declared a V2 and a V3 schema referencing the same underlying Swift `@Model` types, which produces identical checksums by construction. The framework was working as designed.
>
> Three forks of V3 over two days. Each fork attempted to differentiate V3 from V2 in some structural way: a renamed wrapper, a duplicated type, a sub-typed schema declaration. Each fork failed for a different reason, and each failure was downstream of the same constraint: the framework's checksum is computed before the migration logic runs, and the migration logic is the only place where the framework knows what the developer intends. Telling the framework "these are different schemas" required a structural change the developer had no good reason to make.
>
> ## The working answer
>
> The fix was to delete the migration plan.
>
> ```swift
> let container = try ModelContainer(
>     for: Item.self,
>     configurations: ModelConfiguration()
> )
> ```
>
> SwiftData provides an implicit lightweight migration path that handles additive schema changes (new optional properties, new model classes, new optional relationships) without any `SchemaMigrationPlan`. When the change is additive, the framework infers the migration; when a migration plan is supplied for an additive change, the framework runs the version-checksum reconciliation, and the reconciliation is the source of the crash described above.
>
> The schema change in question was additive. The framework's recommended path, the one the documentation centers and the one the tutorials teach, was calibrated for the harder case. Applying it to the easier case introduced the failure mode the easier case did not have on its own.
>
> ## What the case is really about
>
> The lesson is older than SwiftData. Frameworks accumulate machinery for their hard cases, and the documented path is often the hard-case path because the easy case is, by the framework's design, supposed to need no documentation. When the developer reads the documented path and applies it without checking whether their case is the easy one or the hard one, the easy case acquires the hard case's failure modes.
>
> The same pattern appears in Core Data's persistent history tracking, in Realm's manual migration callback, in half the database migration libraries written in any language. The remedy is not to distrust the documentation; the remedy is to check whether the developer's case is the case the documentation is calibrated for, and when it isn't, to ask whether the simpler path is sufficient.
>
> In SwiftData's case, for additive changes, the simpler path is.
>
> ## What this leaves out
>
> The case described above covers only the additive bucket. Renames, deletes, type changes, and cardinality flips are non-additive and genuinely require an explicit `SchemaMigrationPlan`; the implicit path will not migrate them, and attempting to add a non-additive change to an additive container will produce data loss, not a crash. Detecting which bucket a proposed change falls into is, at the time of writing, a manual review.
>
> The piece also takes for granted that the reader has access to a real device for the cold-relaunch test. The crash described above did not appear in the simulator. Teams without device access until users have it have a different problem from the one this piece addresses.
>
> ## A closing observation
>
> The four lines that fixed the crash were the four lines the framework had told the developer to add. Sometimes the working answer is to take the framework's invitation a little less literally than it was offered.

The exemplar above is approximately 1100 words, below the M-tier target of 1500. A real Medium piece at M would extend the second supporting section ("The shape of the failure") with a comparative observation, perhaps a Core Data parallel or a Realm migration that hit a similar structural mismatch. Treat the exemplar as a calibration of voice rather than as a length target.

## What medium is NOT

- Not a tutorial. Tutorials walk the reader through reproducing a working example; Medium pieces argue an observation. If the user wants step-by-step, the apple-developer-article or repo-doc venue is a better fit.
- Not a Reddit post. Both can have a personal voice and a story arc, but the Reddit post resolves in one screen, and the Medium piece develops over multiple sections. Same content shaped for both venues should have different rhythm.
- Not a book chapter. The book chapter is read by a reader who has committed to the book; the Medium piece is read by a reader who clicked from a feed. The Medium piece must do the work of converting the click in its first paragraph; the book chapter has already converted the reader by the time they reach the chapter.

## Recovery hook interaction

Medium pieces (like all Path 2 audience-facing artifacts) do NOT trigger the recovery system. The artifact is a standalone Markdown file the user pastes into Medium's editor (or imports via Medium's Markdown-import feature, or republishes via Substack or another platform that accepts Markdown); the skill's job ends at the file write.

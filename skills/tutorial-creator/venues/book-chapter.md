---
venue: book-chapter
voice: narrative
sectioning: nested-headers
code_blocks: fenced-with-context
front_matter:
  chapter_number: optional
  title: required
  epigraph: optional
length_budget:
  S: { words: 1500, ceiling: 2000 }
  M: { words: 4000, ceiling: 5500 }
  L: { words: 8000, ceiling: 11000 }
  X: { words: 15000, ceiling: 20000 }
honest_machine_section_name: "Limits and open questions"
---

# Venue: book-chapter

Renders an audience-facing tutorial as a chapter in a technical or essayistic book. The reader is sitting down to read for thirty minutes or more, has chosen this book deliberately, and expects argument to develop over the chapter, not just description.

## Voice signature

This is the highest-ceremony venue and the slowest-paced. The reader has committed time; the chapter must reward the commitment with depth, not just surface coverage.

- Narrative voice with an arc. The chapter opens with a scene, a question, or a tension; develops through 2-4 nested sections; lands a thesis that the opening tension was set up to deliver.
- Long-form prose. Paragraphs run 4-8 sentences. Code is embedded in narrative, not the other way around. A chapter where the reader scrolls past blocks of code to find the next paragraph has the ratio inverted; this venue puts prose first and code in service of prose.
- Sentence rhythm matters. Vary length deliberately. A short sentence after three long ones lands. Three short sentences in a row reads as a list of bullet points typed out as prose; restructure if that pattern emerges.
- Personal voice is permitted but not required. First-person works ("I spent three days on this and the fix was the inverse of what I'd assumed"), as does third-person essayistic ("Anyone who has shipped a schema migration knows the moment when..."). Pick one register and hold it.
- The reader expects to be taught something they will remember in six months, not a snippet they will copy-paste tomorrow. Code is illustrative; the lesson is conceptual.

## Sectioning

Nested headers, in the academic-essay style. A typical M-tier (4000 words) chapter has:

- `# Chapter title` (single h1, set in front-matter)
- 2-4 `## section` headers
- 1-3 `### subsection` headers per section, where needed
- Code blocks introduced by a sentence and followed by an analytical paragraph; never standalone

Avoid `####` and deeper. If the structure pushes past three levels, the chapter is trying to do too much; either split into two chapters or collapse the deepest level into prose with `**bold inline phrases**` for emphasis.

The chapter does NOT use bullet lists for its argument. Bullets are appropriate for actual enumerations (a list of three trade-offs, a checklist of cases) but not for content that prose can carry. When a chapter feels like it wants to bullet, that is usually a signal the prose has not been thought through yet.

## Code blocks

- Fenced blocks with the language tag (```swift, ```typescript)
- Surrounded by sentences that name what the code does and what to notice in it. The reader should be able to skim the chapter and read only the prose, missing nothing essential; code is the evidence, prose is the argument.
- Strip what is not relevant to the lesson, but include enough surrounding context that the code is recognizable as the kind of code the reader writes themselves. Pure pseudocode loses the chapter's grounding in real practice.
- When two related code blocks compare alternatives (the broken approach and the working approach), introduce them in parallel sentence structure: "The first attempt..." / "The working version...". The reader's eye will find the parallel and the comparison will land without needing diff syntax.

## Front matter

The chapter has a title (required) and may have a chapter number (when the chapter is part of a numbered book) and an epigraph (a short quotation that frames the chapter's tension). The skill's front-matter block:

```markdown
# <title>
<optional: *Chapter <N>*>
<optional epigraph: a single italicized line, attribution on the next line>
```

Title conventions:

- Pose a question or name a tension, not just a topic. "What the migration plan was hiding" lands better than "SwiftData migration plans."
- Length: 4-9 words. Long enough to have shape; short enough to be remembered.
- Avoid colons in the title unless the colon is doing real work. "The migration plan: a story" is a colon for ceremony; "Migration plans, and what they hide" is a comma doing the same job in better voice.

## Length budget calibration

| Tier | Words | Ceiling | What changes at this tier |
|---|---|---|---|
| S | 1500 | 2000 | A short chapter or essay. Single section after the opening; one or two code examples max. Argument runs in one continuous arc without subsections. |
| M | 4000 | 5500 | Standard book chapter. 2-3 sections, possibly with one subsection level. Two to four code examples. The default for this venue. |
| L | 8000 | 11000 | Long chapter. 3-4 sections with nested subsections. Five or more code examples. Sustains a developed argument with multiple supporting cases. |
| X | 15000 | 20000 | A novella-length chapter, rare in technical books. Suitable when the chapter is doing the work of a small book within a book (e.g., a chapter that introduces an entire framework or a 30-page case study). The skill should warn the user that X is unusual for this venue and ask whether they intend a chapter or a separate book. |

When budget is S, the chapter drops the second supporting case and resolves the central tension with one example. When budget is X, the chapter develops a counter-case and addresses a likely objection from a thoughtful reader before resolving.

## Audience interaction

- **beginner**: extend the opening section into a "Background" subsection that establishes vocabulary the reader needs before the central tension lands. Add parenthetical glosses for symbols on first appearance. Do not omit the chapter's main argument; instead, slow the entry into it.
- **intermediate**: default voice. The reader knows the framework's basics; the chapter teaches a non-obvious application or a counter-intuitive failure mode.
- **senior**: tighten the introduction; the senior reader is impatient with setup. Add a "Trade-offs" or "When this approach fails" subsection before the close. The chapter should leave a senior reader thinking about edge cases, not feeling re-taught fundamentals.
- **mixed**: write for intermediate. The book-chapter venue is the hardest of the six to write for mixed audiences; the chapter's depth assumes a single register. The skill offers the user a heads-up: "Mixed-audience book chapters tend to please neither end of the audience; consider picking one and writing two chapters if both audiences matter."

## Honest-machine section

When `honest_machine_optin: true`, append a `## Limits and open questions` section near the end of the chapter (not the absolute last section; the chapter should still close on its own argument, with the limits section preceding the closing reflection). The section runs 100-300 words and is in the chapter's voice (not a bulleted appendix).

Format: prose paragraph(s) with 2-4 acknowledgments of what the chapter does not address, what the author is uncertain about, and what readers who want to push further should look into. Bullets are permitted only when the limits are genuinely list-shaped (three specific cases the chapter does not handle); prefer prose otherwise.

## Voice exemplar (V3 schema migration, audience=intermediate, budget=M, hm=on)

> # Migration plans, and what they hide
>
> *Chapter 9*
>
> *"The framework's official path is sometimes the bug, not your code."*
>
> There is a moment, after a schema migration ships, when the code is correct, the simulator runs are clean, and the build is green. The migration plan is wired up. The version stages are declared. The author of the change writes the release notes and prepares to move on.
>
> Then the cold relaunch on a real device, and the crash on launch.
>
> This chapter is about that moment. More precisely, it is about the kind of failure that happens when the framework's recommended path turns out to be the source of the failure, and the working answer is to not take the recommended path at all. The case study is SwiftData, and a schema migration that crashed at launch with a `Duplicate version checksums detected` error after every available diagnostic in the simulator passed.
>
> ## What the migration plan was supposed to do
>
> SwiftData's migration story, as documented and as taught, is built around two protocols. A `VersionedSchema` declares a version of the data model, identified by a `versionedSchemaIdentifiers` static property. A `SchemaMigrationPlan` declares a list of `MigrationStage` values that move data from one versioned schema to the next. The framework reads both, computes a checksum across the schemas, and dispatches the migration when the on-disk store's version does not match the latest declared version.
>
> A migration in the simplest case looks like this:
>
> ```swift
> enum AppMigrationPlan: SchemaMigrationPlan {
>     static var schemas: [any VersionedSchema.Type] {
>         [SchemaV2.self, SchemaV3.self]
>     }
>     static var stages: [MigrationStage] {
>         [.lightweight(fromVersion: SchemaV2.self, toVersion: SchemaV3.self)]
>     }
> }
> ```
>
> The reader who has migrated a database in any framework before will recognize the shape. There is a path, the path is enumerated, and the framework walks it.
>
> The case in this chapter is one where the path was correct, the enumeration was correct, and the framework refused to walk it.
>
> ## The crash
>
> Three forks of the V3 schema were attempted over two days. Each fork passed every simulator check (cold relaunch with seeded V2 data, three runs in a row, no warnings). Each fork crashed on the first cold relaunch on a real device with the same error: `Duplicate version checksums detected`. The error refers to the framework's checksum across `versionedSchemaIdentifiers`. SwiftData computes that checksum and, when it sees two schemas with the same checksum, refuses the migration plan as ambiguous.
>
> The crash was not in the user's schema. The crash was in the framework's reconciliation of the schema versions, because V2 and V3 referenced the same Swift types (the same `@Model` classes, the same property names, the same relationship inverses), and identical Swift types produce identical checksums. The migration plan was internally consistent and externally indistinguishable from a no-op.
>
> ## The working answer
>
> The fix turned out to be: omit the migration plan entirely.
>
> ```swift
> // The original, with the migration plan that crashed:
> let container = try ModelContainer(
>     for: Item.self,
>     migrationPlan: AppMigrationPlan.self,
>     configurations: ModelConfiguration()
> )
>
> // The working version, with implicit lightweight migration:
> let container = try ModelContainer(
>     for: Item.self,
>     configurations: ModelConfiguration()
> )
> ```
>
> SwiftData provides an implicit lightweight migration path that handles additive schema changes (new optional properties, new model classes, new optional relationships) without any `SchemaMigrationPlan` at all. When the change is additive, the framework infers the migration; when the migration plan is supplied for an additive change, the framework runs the version-checksum reconciliation and, in the case described above, fails it.
>
> The `VersionedSchema` machinery is genuinely needed for non-additive changes (renames, type changes, cardinality flips). But for additive changes, the recommended path is more than the change requires, and the more is what causes the crash. The chapter's central observation is this: the framework's recommended path is sometimes calibrated for the harder case, and applying the harder case's machinery to the easier case introduces the failure mode the easier case did not have on its own.
>
> ## What this case is, and is not
>
> The case is not a bug in SwiftData. The framework is doing what it is documented to do, and the documentation is correct. The case is a mismatch between the user's mental model (the migration plan is the canonical migration path; therefore I should use it) and the framework's actual semantics (the migration plan is the canonical path for changes that need it; for additive changes, omitting it is the canonical path).
>
> The lesson is older than SwiftData. Frameworks accumulate machinery for their hard cases. When the documented path is the hard-case path, applying it to the easy case can introduce failure modes the easy case did not have. The same lesson applies to Core Data's persistent history tracking, to Realm's migrations callback, and to half the database migration libraries written in any language.
>
> ## Limits and open questions
>
> The case study above covers only the additive bucket. Renames, deletes, type changes, and cardinality flips are non-additive and genuinely require the `SchemaMigrationPlan` machinery. The chapter does not address how to detect that a proposed change is in the additive bucket before committing to it; that detection is, at the time of writing, a manual review. There is room for a tool that walks a proposed `@Model` diff and classifies it.
>
> The chapter also does not cover Core Data's lightweight migration, which is conceptually similar but operationally different (Core Data uses a model-version-bundle on disk; SwiftData uses runtime schema introspection). A reader transitioning from Core Data should treat SwiftData's lightweight migration as a different mechanism that happens to share a name.
>
> Finally, the chapter takes for granted that the reader can reach a real device for the cold-relaunch test. Teams without device access (web-only CI, simulator-only labs) will not encounter the crash described here until users do. The chapter argues, by implication, that simulator-only schema testing is insufficient for SwiftData; that argument deserves its own chapter.

The exemplar above is approximately 1100 words including front matter, which is below the M-tier target of 4000. A real chapter at M would extend the central case with one or two more supporting examples (perhaps a Core Data migration that hit a parallel failure mode, or a different additive change that the framework handled correctly to contrast against). Treat the exemplar as a calibration of voice rather than as a length target.

## What book-chapter is NOT

- Not a tutorial. Tutorials walk the reader through reproducing a result step-by-step. Book chapters argue a thesis the reader will remember conceptually. If the user wants step-by-step, the apple-developer-article venue is a better fit.
- Not a Reddit post. Both can have a story arc, but the Reddit post resolves in one screen; the book chapter develops over multiple sections. If the topic genuinely fits one screen, do not pad it for this venue; recommend reddit instead.
- Not a research paper. The chapter argues from observation and experience, not from systematic study. Citations appear sparingly, in service of the chapter's argument, not as a literature review.

## Recovery hook interaction

Book chapters (like all Path 2 audience-facing artifacts) do NOT trigger the recovery system. They are standalone files the user copies into their book draft (Markdown source for a static-site book, Pages or Word for a traditionally-published book, plain text for an essayist's working file); the skill's job ends at the file write.

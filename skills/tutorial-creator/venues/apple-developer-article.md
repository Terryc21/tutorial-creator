---
venue: apple-developer-article
voice: declarative-reference
sectioning: docc-flat
code_blocks: fenced-frequent
front_matter:
  title: required
  summary: required
  symbol_links: optional
length_budget:
  S: { words: 400, ceiling: 600 }
  M: { words: 1000, ceiling: 1500 }
  L: { words: 2500, ceiling: 3500 }
  X: { words: 5000, ceiling: 7000 }
honest_machine_section_name: "See Also and open questions"
---

# Venue: apple-developer-article

Renders an audience-facing tutorial in the voice and structure of an Apple Developer article: the kind of page that lives at `developer.apple.com/documentation/...` or surfaces in Xcode's documentation viewer. The reader is looking up how a specific framework, type, or pattern works, often in the middle of writing code, and expects the article to answer the question precisely with code listings they can read or copy.

## Voice signature

- Declarative reference voice. Sentences state facts; verbs are present-indicative ("returns", "calls", "throws") rather than narrative past ("I tried", "we found"). The reader is not interested in the author's experience; they are interested in what the API does.
- Code listings are frequent and load-bearing. The reader scrolls to find the code block that matches their use case and reads outward from there into the surrounding prose for context. Prose paragraphs between code blocks should be short (2-4 sentences) and serve the next code block.
- Symbol-precise language. When the article references a Swift symbol, it uses the exact spelling and casing (`URLSession`, not "the URL session class"; `@MainActor`, not "the main actor attribute"). On first appearance in a section, the symbol is rendered as a code-formatted link if the venue supports DocC links, or as plain backtick code if not.
- Neutral tone. The article does not editorialize, rate, or compare to non-Apple frameworks. It explains how the Apple-platform feature works, in the Apple-platform vocabulary, for developers writing Apple-platform code.
- No first-person. "I" does not appear. "You" appears sparingly, only when describing what the developer's code should do ("you call `Task.detached(...)` to..."), not the developer's experience.

## Sectioning

DocC-flat: a single h1 title (in front matter), a one-paragraph summary, then a flat sequence of `## section` headers. Subsections are rare; if a section needs subsections, the section is probably trying to be two articles.

Standard section conventions, in this order when applicable:

- `## Overview` (always; 1-3 paragraphs setting up what the article covers)
- `## <Specific aspect>` headers (1-N; each focused on one aspect with at least one code listing)
- `## Topics` (optional; bulleted links to related symbols or articles)
- `## See Also` (optional; links to related Apple documentation)

Avoid narrative section titles like "Why we do this" or "The story behind...". Section titles are noun phrases naming the aspect ("Configuring the session", "Handling errors", "Cancelling the task").

## Code blocks

- Fenced blocks with the language tag, frequent (one per 100-200 words is typical for this venue)
- Each code listing is preceded by a sentence that names what the listing demonstrates and followed by a 1-2 sentence explanation of what to notice
- Listings include enough context to compile in isolation (imports, type declarations) when reasonable; if context is omitted, the omission is noted ("Assuming `session` is configured as shown above...")
- Placeholder values use the Apple convention: `<#expression#>` style angle-bracketed hash placeholders for values the reader fills in
- Avoid pseudocode entirely. Either the listing is real Swift (the standard) or it is a precise structural diagram (rare; use sparingly)

## Front matter

DocC-flavored front matter:

```markdown
# <Title: a noun phrase naming the topic>

<Summary: one sentence, 15-25 words, that the docs viewer surfaces in
search results and the table of contents>
```

Title conventions:

- Noun phrases. "Cancelling tasks bound to view identity" rather than "How to cancel a task" or "Task cancellation is tricky".
- Length: 4-8 words. Long enough to disambiguate from sibling articles; short enough to render in Xcode's narrow doc panel.
- Capitalize like an Apple Developer article title (sentence case for most; the first word and proper nouns are capitalized).

Summary conventions:

- One sentence. The summary is what surfaces in `developer.apple.com` search and Xcode's quick-look popovers.
- 15-25 words. Long enough to convey scope; short enough to fit in narrow viewports.
- States the article's subject in the present tense. "Discusses how `.task(id:)` binds an asynchronous task to a SwiftUI view's identity, and explains the cancellation semantics this enables."

## Length budget calibration

| Tier | Words | Ceiling | What changes at this tier |
|---|---|---|---|
| S | 400 | 600 | A short reference article. One Overview paragraph, one or two `## section` headers, two or three code listings. No `## See Also`. |
| M | 1000 | 1500 | Standard reference article. Overview, three to five `## section` headers, four to seven code listings, optional `## See Also`. The default for this venue. |
| L | 2500 | 3500 | Long-form reference article. Multiple aspects covered with subsections. Eight or more code listings. `## Topics` and `## See Also` both present. |
| X | 5000 | 7000 | An article-length guide rather than a single reference page. Approaching DocC-tutorial territory; consider whether the content should be a multi-page tutorial in DocC instead, or split into multiple sibling articles. The skill warns the user. |

When budget is S, the article drops the `## See Also` section and tightens the Overview to a single paragraph. When budget is X, the article adds an `## Advanced usage` section after the standard sections and considers a `## Topics` index of related symbols.

## Audience interaction

- **beginner**: extend the `## Overview` to two or three paragraphs; add a "Before you begin" or "Prerequisites" subsection if the article assumes framework or platform knowledge the beginner may not have. Each code listing's explanatory paragraph is one or two sentences longer.
- **intermediate**: default voice. The reader recognizes Apple-platform vocabulary; the article explains how this specific API or pattern works.
- **senior**: tighten the `## Overview` to one paragraph; the senior reader skims to the code listings. Add an `## Advanced considerations` or `## When to use this` section near the end discussing edge cases and tradeoffs the basic usage glosses.
- **mixed**: write for intermediate. Apple Developer's own articles tend to write for intermediate developers and rely on linked subordinate articles ("Getting Started with...") and on the senior-specific articles ("Advanced ...") for the other audiences. The skill suggests the user split the article rather than write a mixed-audience one.

## Honest-machine section

When `honest_machine_optin: true`, append a `## See Also and open questions` section. This is the apple-developer-article venue's adaptation of the standard `## See Also` section: the first part lists related Apple documentation (the venue convention), and the second part lists open questions the article does not resolve.

Format:

```markdown
## See Also and open questions

### Related documentation
- [<Symbol or article title>](<URL placeholder>)
- [<Symbol or article title>](<URL placeholder>)

### Open questions
- <Question or limitation, one to two sentences>
- <Question or limitation, one to two sentences>
```

The two subsections are themselves uncharacteristic for this venue (subsections are rare in DocC-flat sectioning), but the honest-machine adaptation justifies them. URLs are placeholders; the user fills in the actual references when they place the article in their docs site.

## Voice exemplar (V3 schema migration, audience=intermediate, budget=M, hm=on)

> # Migrating SwiftData schemas with implicit lightweight migration
>
> Discusses when the framework's implicit lightweight migration handles a schema change, and when an explicit `SchemaMigrationPlan` is required.
>
> ## Overview
>
> SwiftData provides two paths for evolving a persistent schema. Additive changes (new optional properties, new model classes, new optional relationships) are handled by an implicit lightweight migration that runs automatically when the on-disk store's schema does not match the latest declared schema. Non-additive changes (renames, type changes, cardinality flips, deletions) require an explicit `SchemaMigrationPlan` declaring the migration stages.
>
> The implicit path requires no migration plan in the `ModelContainer` initializer. Supplying a migration plan for a change that the implicit path would handle can produce a `Duplicate version checksums detected` error at launch on a real device, because the framework's checksum across `versionedSchemaIdentifiers` cannot distinguish two `VersionedSchema` types that reference the same underlying Swift `@Model` types.
>
> ## Configuring a container without a migration plan
>
> When the schema change is additive, omit the `migrationPlan:` parameter from `ModelContainer(...)`:
>
> ```swift
> let container = try ModelContainer(
>     for: Item.self,
>     configurations: ModelConfiguration()
> )
> ```
>
> The framework reads the on-disk store's schema, compares it to `Item.self`'s current schema, and applies the additive changes automatically. New optional properties are initialized to `nil`. New model classes are added to the store with no rows. New optional relationships are initialized as empty sets or `nil` depending on the cardinality.
>
> ## Configuring a container with an explicit migration plan
>
> When the schema change is non-additive, supply a `SchemaMigrationPlan` that declares the migration stages:
>
> ```swift
> enum AppMigrationPlan: SchemaMigrationPlan {
>     static var schemas: [any VersionedSchema.Type] {
>         [SchemaV2.self, SchemaV3.self]
>     }
>     static var stages: [MigrationStage] {
>         [.custom(
>             fromVersion: SchemaV2.self,
>             toVersion: SchemaV3.self,
>             willMigrate: { context in <#pre-migration setup#> },
>             didMigrate:  { context in <#post-migration cleanup#> }
>         )]
>     }
> }
>
> let container = try ModelContainer(
>     for: Item.self,
>     migrationPlan: AppMigrationPlan.self,
>     configurations: ModelConfiguration()
> )
> ```
>
> Each `VersionedSchema` type declares its own `versionedSchemaIdentifiers` to distinguish it from sibling schemas. When two `VersionedSchema` types reference the same underlying `@Model` Swift types, their `versionedSchemaIdentifiers` may produce identical checksums, which the framework rejects as ambiguous. Distinguishing the schemas at the `VersionedSchema` level (by giving them distinct sub-types or by changing the underlying `@Model` definitions) is required for the migration plan to register.
>
> ## Detecting whether a change is additive
>
> A schema change is additive if and only if every difference between the old and new schemas is one of:
>
> - A new optional property on an existing `@Model` class
> - A new `@Model` class
> - A new optional relationship between existing or new `@Model` classes
>
> Renaming a property, changing a property's type, marking an optional property required (or vice versa), changing a relationship's cardinality, or deleting a property or class are non-additive and require an explicit migration plan.
>
> ## See Also and open questions
>
> ### Related documentation
> - [`ModelContainer`](<placeholder>)
> - [`VersionedSchema`](<placeholder>)
> - [`SchemaMigrationPlan`](<placeholder>)
> - [`MigrationStage`](<placeholder>)
>
> ### Open questions
> - The framework's behavior when an additive change is supplied as part of a `SchemaMigrationPlan` for a separately non-additive change in the same migration stage is not documented and varies between iOS releases. Splitting the additive and non-additive parts into separate stages is the safer pattern.
> - The implicit migration path's behavior on a schema with a custom `Codable` property whose `init(from:)` throws is not documented; testing on a real device with seeded data is required before relying on it.

The exemplar above is approximately 700 words including front matter, which is at the M-tier ceiling. A real article at M might trim the "Detecting whether a change is additive" section into a `## Topics` linked page; this exemplar keeps it inline to demonstrate the section convention.

## What apple-developer-article is NOT

- Not an opinion piece. The article does not argue that the implicit path is "better" or "easier"; it states when each path applies. If the user wants to argue, the medium or blog venue is a better fit.
- Not a tutorial. Tutorials walk the reader through reproducing a working example; reference articles describe how an API works. DocC has a separate `@Tutorial` directive for tutorials; if the user's content is genuinely step-by-step (do this, then this, then this), recommend they author a DocC tutorial instead and use this venue only for the reference article that supports it.
- Not a Reddit post. Reddit's first-person, single-thread voice is the inverse of this venue's neutral, declarative voice. Same content shaped for both venues should look like two different writers wrote it.

## Recovery hook interaction

Apple Developer articles (like all Path 2 audience-facing artifacts) do NOT trigger the recovery system. The artifact is a standalone Markdown file the user copies into their DocC catalog (`Sources/<Module>/<Module>.docc/Articles/<title>.md`) or their developer documentation site; the skill's job ends at the file write.

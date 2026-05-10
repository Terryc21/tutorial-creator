---
venue: repo-doc
voice: terse-instructional
sectioning: structured-headers
code_blocks: fenced-minimal-prose
front_matter:
  title: required
  tldr: required
length_budget:
  S: { words: 200, ceiling: 350 }
  M: { words: 500, ceiling: 800 }
  L: { words: 1200, ceiling: 1800 }
  X: { words: 2500, ceiling: 3500 }
honest_machine_section_name: "Out of scope"
---

# Venue: repo-doc

Renders an audience-facing tutorial as a document inside a code repository: a `README.md`, a `docs/<topic>.md`, an `ADR` (architecture decision record), or a `RUNBOOK.md`. The reader is a developer who has cloned the repo (or is browsing it on the web) and needs to find the answer to a specific operational or architectural question quickly. They are not reading for pleasure.

## Voice signature

This is the most mechanical of the six venues and the lowest-ceremony. The reader scans, locates the section that matches their question, reads the code block, and returns to their work.

- Terse, instructional, second-person where action is described ("Run `swift test`. The suite takes 90 seconds."). First-person is rare and reserved for ADR-style "Decision" sections where the document records a stance.
- Sentences are short and declarative. Compound sentences are uncommon. The reader is skimming; long sentences cost them more than they pay back.
- Code blocks carry the load. Prose introduces a block in one sentence, the block does the work, and a follow-up sentence (often optional) names the gotcha or the variant. Pages where prose outweighs code are usually drifting toward the blog or medium venue and should be redirected.
- Bullet lists are normal, not avoided. Repo docs are list-shaped: dependencies, steps, flags, environment variables, tradeoffs. Use bullets when the content enumerates; use prose only when the content reasons.
- No narrative arc. The doc does not open with a scene or a tension; it opens with a TL;DR and a table of contents (implicit, via the heading hierarchy). The reader who knows what they need reads only one section and leaves.

## Sectioning

Structured headers, with consistent conventions across the venue. A typical M-tier (500 words) repo-doc has:

- `# <Title>` (single h1, set in front-matter)
- `**TL;DR:**` line directly under the title (1-2 sentences, the doc's executive answer)
- 3-6 `## section` headers in a recognized order
- Occasional `### subsection` headers for grouped variants

Recognized section orders (pick the one that fits the document type):

- **Operational doc** (RUNBOOK, deploy guide): `Prerequisites` → `Procedure` → `Verification` → `Rollback` → `Troubleshooting`
- **Reference doc** (CONTRIBUTING, dev setup): `Quick start` → `Detailed setup` → `Common tasks` → `Troubleshooting`
- **ADR** (architecture decision record): `Context` → `Decision` → `Consequences` → `Alternatives considered`
- **API or schema doc**: `Overview` → `Schema` → `Examples` → `Migration notes`

The structure is recognizable to developers who have read other repo docs. Inventing a custom section order is permitted but should be a deliberate choice; the conventions exist because readers find documents faster when they match.

## Code blocks

- Fenced blocks with the language tag, frequent and load-bearing
- Most blocks are shell commands, configuration excerpts, or short code listings (10-30 lines)
- Long code listings (40+ lines) are rare and usually a signal the doc should link to the source file rather than embed it. Embed when the code is itself the answer; link when the code is supporting context.
- Shell blocks use `bash` or `sh` as the language tag, even when the commands are platform-agnostic. The reader's eye recognizes the prompt structure.
- Output blocks (stdout, error messages) use no language tag or `text`. The reader reads them as evidence, not as code to copy.
- Side-by-side or before/after comparisons use two consecutive blocks with a one-sentence sentence between them, not a single combined block. Repo readers diff visually; consecutive blocks support that.

## Front matter

The repo-doc venue has a title (required) and a TL;DR (required). The TL;DR is a load-bearing convention: a developer scanning the file in a directory listing or skimming the first viewport must learn the document's answer in the first 1-2 sentences after the title. The skill's front-matter rendering:

```markdown
# <Title>

**TL;DR:** <one to two sentences naming the answer or the action.>
```

Title conventions:

- Noun phrases or imperative phrases. "Schema migration runbook" or "Migrating SwiftData schemas safely" are both correct. "How we handle migrations" is too narrative; "Migrations" is too short to disambiguate.
- Length: 3-7 words. Long enough to identify the doc's subject in a `docs/` directory listing; short enough to render as a sidebar entry.
- Avoid verbs in the gerund form unless the topic is a process. "Migrating..." is correct for a runbook; "Configuring CI" is correct for a setup guide. "How to migrate" is too informal for the venue.

TL;DR conventions:

- One sentence is the target. Two sentences is permitted when the document has a critical caveat that the reader must see before reading further (e.g., "**TL;DR:** Use `lightweight` migration for additive changes. Custom migrations require a real-device cold-relaunch test before merging.").
- States the operational or architectural answer, not the topic. "Use `migrationPlan:` only for non-additive changes" is a TL;DR; "This document covers schema migrations" is not.
- Bold the prefix `**TL;DR:**` so readers scanning the document recognize it without reading further.

## Length budget calibration

| Tier | Words | Ceiling | What changes at this tier |
|---|---|---|---|
| S | 200 | 350 | A single-purpose doc: one decision, one runbook procedure, one schema reference. Two or three sections, two or three code blocks, no `### subsections`. |
| M | 500 | 800 | Standard repo doc. Three to six sections, four to eight code blocks, occasional `### subsections` for variant cases. The default for this venue. |
| L | 1200 | 1800 | A long repo doc that covers multiple related procedures or a non-trivial decision with several alternatives weighed. Six to ten sections, ten or more code blocks, regular `### subsections`. |
| X | 2500 | 3500 | A document approaching the size of a small handbook (e.g., a CONTRIBUTING.md for a multi-team monorepo). The skill warns the user that X-tier repo docs are rarely read end-to-end and suggests splitting into sibling docs with a shared index. |

When budget is S, the doc drops the `Verification` or `Alternatives considered` sections (whichever is least load-bearing for the doc's type) and keeps only the answer and the procedure. When budget is X, the doc adds an explicit `## Index` near the top so readers can navigate to their section without scrolling.

## Audience interaction

- **beginner**: extend the `Prerequisites` or `Quick start` section. Add explicit version numbers, exact filenames, and a "Before you begin" callout naming what the reader needs installed. Do not extend the procedural sections; the reader's blocker is usually setup, not the steps themselves.
- **intermediate**: default voice. The reader knows the project's stack and is reading the doc to learn the project-specific operational pattern.
- **senior**: tighten the `Quick start` to a single block. Add or extend an `## Alternatives considered` (for ADRs) or a `## When this doesn't apply` (for runbooks) section. The senior reader is checking whether the doc's recommendation matches their judgment; give them the reasoning, not the recipe.
- **mixed**: write for intermediate. Repo docs that try to address all three audiences in the same document tend to bury the answer in caveats. The skill suggests the user split: a short `quick-start.md` for the beginner-oriented entry, and a longer `<topic>.md` for the intermediate/senior reader who needs the full picture.

## Honest-machine section

When `honest_machine_optin: true`, append a `## Out of scope` section as the last section of the document (after `## Troubleshooting` or `## Alternatives considered`, whichever is the doc's natural final section). The section is brief: 50-150 words, formatted as a bulleted list of what the document does NOT cover.

Format:

```markdown
## Out of scope

- <thing the doc does not cover, one line>
- <thing the doc does not cover, one line>
- <thing the doc does not cover, one line>
- <pointer to where the missing thing is covered, if known>
```

Three to five bullets is the target. The list is operational, not editorial: the reader uses it to decide whether the doc answers their question or whether they need to look elsewhere. Avoid hedging language ("we may or may not cover...") and prefer precise statements ("Does not cover macOS Sonoma; see `docs/macos-sonoma.md`.").

## Voice exemplar (V3 schema migration, audience=intermediate, budget=M, hm=on)

> # SwiftData migration runbook
>
> **TL;DR:** Use implicit lightweight migration (omit `migrationPlan:`) for additive schema changes. Use an explicit `SchemaMigrationPlan` only for renames, type changes, or deletes. Always cold-relaunch on a real device before merging.
>
> ## Prerequisites
>
> - Xcode 15.0+ with SwiftData (iOS 17+)
> - A real device for cold-relaunch testing (the simulator does not catch the duplicate-checksum case)
> - A copy of production data in a debug-signed build for migration testing
>
> ## Decision: which migration path?
>
> | Schema change | Path |
> |---|---|
> | Add an optional property | Implicit lightweight |
> | Add a new `@Model` class | Implicit lightweight |
> | Add an optional relationship | Implicit lightweight |
> | Rename a property | Explicit `SchemaMigrationPlan` |
> | Change a property's type | Explicit `SchemaMigrationPlan` |
> | Make optional → required | Explicit `SchemaMigrationPlan` |
> | Change relationship cardinality | Explicit `SchemaMigrationPlan` |
> | Delete a property or class | Explicit `SchemaMigrationPlan` |
>
> ## Procedure: implicit lightweight migration
>
> 1. Edit the `@Model` class. Add the new property as optional, or add the new class.
> 2. Verify the `ModelContainer` initializer does NOT pass `migrationPlan:`:
>
>    ```swift
>    let container = try ModelContainer(
>        for: Item.self,
>        configurations: ModelConfiguration()
>    )
>    ```
>
> 3. Build and run on the simulator with seeded V_N data. Verify the app launches and the new property reads as `nil` (or the new class reads as empty).
> 4. Cold-relaunch on a real device with the same seeded data. Verify no `Duplicate version checksums detected` crash.
> 5. Merge.
>
> ## Procedure: explicit migration plan
>
> 1. Define a new `VersionedSchema` for V_(N+1) with distinct underlying types from V_N (rename the `@Model` class internally if needed; the framework's checksum requires structural distinction).
> 2. Define a `SchemaMigrationPlan` with a `MigrationStage` from V_N to V_(N+1):
>
>    ```swift
>    enum AppMigrationPlan: SchemaMigrationPlan {
>        static var schemas: [any VersionedSchema.Type] {
>            [SchemaV_N.self, SchemaV_N1.self]
>        }
>        static var stages: [MigrationStage] {
>            [.custom(
>                fromVersion: SchemaV_N.self,
>                toVersion: SchemaV_N1.self,
>                willMigrate: { context in <#pre-migration setup#> },
>                didMigrate:  { context in <#post-migration cleanup#> }
>            )]
>        }
>    }
>    ```
>
> 3. Pass the plan to the container:
>
>    ```swift
>    let container = try ModelContainer(
>        for: Item.self,
>        migrationPlan: AppMigrationPlan.self,
>        configurations: ModelConfiguration()
>    )
>    ```
>
> 4. Cold-relaunch on a real device with seeded V_N data.
> 5. Merge only after a successful real-device migration.
>
> ## Verification
>
> - Simulator: cold relaunch with seeded V_N data, three runs in a row, no warnings.
> - Real device: cold relaunch with seeded V_N data, no `Duplicate version checksums detected` crash, all V_N rows readable as V_(N+1).
> - Production-shadow: migrate a snapshot of production data in a debug build before merging the schema PR.
>
> ## Rollback
>
> If a migration ships and corrupts data, revert the schema PR and ship a hotfix. Do NOT attempt a corrective migration in production; data corruption from a failed migration is rarely recoverable in-place.
>
> ## Out of scope
>
> - Pre-iOS 17 Core Data migrations (different API; see `docs/core-data-migration.md`).
> - Migrations that span more than one schema version in a single user upgrade (chained `MigrationStage` values; see `docs/multi-step-migrations.md`).
> - CloudKit-backed schemas (the migration path is the same, but the timing of remote schema updates is not covered here).
> - Recovery from a partially-applied migration on a single device (a separate runbook).

The exemplar above is approximately 600 words, at the M-tier target. A real runbook may include screenshots of Xcode dialogs, additional troubleshooting entries, or links to internal CI dashboards; the exemplar omits those because the venue file demonstrates voice and structure, not project-specific detail.

## What repo-doc is NOT

- Not a tutorial. Tutorials teach a technique to a reader who is learning; repo-docs answer a question for a reader who is operating. If the user wants the reader to come away having learned something, the apple-developer-article or book-chapter venue is a better fit.
- Not a blog post. Repo-docs do not have a date, a personal voice, or a closing reflection. If the doc has those, the user is drifting into the blog venue.
- Not a Reddit post. Repo-docs are findable by directory listing and section header; Reddit posts are findable by feed scroll and title hook. The two venues optimize for opposite reading patterns.

## Recovery hook interaction

Repo docs (like all Path 2 audience-facing artifacts) do NOT trigger the recovery system. They are standalone Markdown files the user commits to their repo (typically into `README.md`, `docs/<topic>.md`, or `docs/adr/<NNNN>-<slug>.md` for ADRs); the skill's job ends at the file write.

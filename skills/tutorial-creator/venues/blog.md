---
venue: blog
voice: conversational-personal
sectioning: optional-headers
code_blocks: fenced-as-needed
front_matter:
  title: required
  date: required
  tags: optional
length_budget:
  S: { words: 400, ceiling: 700 }
  M: { words: 1000, ceiling: 1500 }
  L: { words: 2200, ceiling: 3200 }
  X: { words: 4500, ceiling: 6500 }
honest_machine_section_name: "Caveats"
---

# Venue: blog

Renders an audience-facing tutorial as a post on the writer's personal blog: a Jekyll/Hugo/Eleventy site, an Astro garden, a hand-rolled site, or a personal Substack written for known readers. The reader is a subscriber, an RSS follower, or someone who arrived from another post on the same site, and they already know the writer's voice. They are not deciding whether to keep reading; they are reading because they read this writer.

## Voice signature

The blog venue is conversational and personal, with a lower ceiling on ceremony than the medium venue and a higher floor on developed thought than a Reddit post. The writer is talking to people who already follow them.

- First-person is the default register. "I shipped a schema change last week" is a typical opening; "Anyone who ships a schema change knows..." reads as a magazine pitch and is the wrong register for the venue.
- Sentences vary in length, but the rhythm is closer to spoken thought than to magazine prose. A sentence may run on for a clause longer than it strictly needs to, the way a person would write to a notebook. Short sentences land. Lists, parentheticals, and asides are welcome.
- The piece does not need a thesis. A blog post can be a working note, an observation in progress, a debugging story without a generalization, or a "here is what I am thinking about" entry. The medium venue requires an observation worth developing; the blog venue accepts the observation in its raw form.
- Code is fenced as needed, not as a regular cadence. A debugging post may have one fenced block (the fix); a how-it-works post may have four; a reflection post may have none. The piece's shape determines the code, not a venue convention.
- The writer's voice is central, not incidental. The reader is here for the writer's perspective; what happened, how it felt, what the writer thinks now. Removing the voice removes the reason the reader is on the site.

## Sectioning

Optional headers. Many blog posts have no headers at all, especially shorter ones. The skill's defaults:

- `# Title` (single h1, set in front-matter)
- The body, which may be:
  - One unbroken arc of prose with no `## section` headers (typical for S-tier and many M-tier posts)
  - 2-4 light `## section` headers (typical for M-tier and L-tier posts that benefit from navigation)
  - 4-6 `## section` headers with no `### subsections` (typical for L-tier posts that cover multiple aspects)

`### subsections` are rare in this venue and usually a signal the post is reaching for the medium or book-chapter venue's structure. If the post needs subsections, consider whether it should be a different venue.

When the post has headers, the headers are conversational, not formal. "What I tried first" and "What actually worked" are blog-shaped headers; "Background" and "Implementation" are not.

## Code blocks

- Fenced blocks with the language tag, used when the post needs them
- Each code block is preceded by a sentence in the writer's voice ("Here is what the fix looked like:") and followed by a sentence that names the gotcha or the variant in the writer's voice ("Two days for those four lines.")
- The post does not need to provide enough context for the reader to compile the example. The reader is reading for the writer's perspective, and the writer can elide what is not interesting.
- Output, error messages, and shell sessions are common in the blog venue, more so than in any other venue. The reader is following the debugging story, and the actual error message ("Duplicate version checksums detected") is part of the story, not a footnote.
- Side-by-side comparisons are written in narrative order: "First I had this:" / block / "Then I had this:" / block. The reader is following the writer's path, so the chronology is the comparison's structure.

## Front matter

The blog venue requires a title and a date. The date is the publication date and is part of the post's identity; readers refer to old posts by date as often as by title. Tags are optional but supported for blogs that organize posts that way.

```markdown
# <Title>

*<Date in the blog's house format, e.g., 2026-05-10 or "May 10, 2026">*

<Optional tags line, e.g., *Tags: swift, swiftdata, debugging*>
```

Title conventions:

- 4-10 words is the typical range. Long enough to identify the post in an archive list; short enough to render in the browser tab.
- Conversational, not formal. "Two days for four lines" or "A schema migration that crashed only on the device" are blog titles. "An analysis of SwiftData migration failure modes" is not.
- May include a question mark, a colon used informally, or a phrase fragment. The blog title is the writer's voice in title form, not a journal article header.
- Avoid generic titles. "Notes on SwiftData" identifies the topic but tells the reader nothing about the post; the writer's archive will fill with such titles and become unbrowsable.

Date conventions:

- Published date, formatted in the blog's house style. The skill emits ISO format (`2026-05-10`) by default and the writer adjusts to match their site if needed.
- The date renders below the title and above the body, italicized.
- Updated-date is a separate convention some blogs adopt; the skill does not emit one by default. The writer adds an "Updated:" line manually when republishing.

Tags conventions:

- Optional. Many blogs do not use tags at all.
- When present, render as an italicized line directly below the date: `*Tags: swift, swiftdata, debugging*`.
- 2-5 tags is typical. More than 5 reads as keyword stuffing.

## Length budget calibration

| Tier | Words | Ceiling | What changes at this tier |
|---|---|---|---|
| S | 400 | 700 | A short blog post: a working note, a quick observation, a one-incident debugging story. No section headers; one unbroken arc of prose. Zero or one code block. |
| M | 1000 | 1500 | Standard blog post. Two or three light section headers when the post benefits from them; otherwise unbroken prose. One to three code blocks. The default for this venue. |
| L | 2200 | 3200 | A long blog post. Four to six section headers, three to five code blocks, possibly a comparison or a contrasting case. Approaching the medium venue's territory; consider whether the piece is genuinely a blog post (the writer's voice is central) or a magazine essay (the observation is central). |
| X | 4500 | 6500 | A long-form blog post or essay published on the writer's own site. Rare; usually a working paper or a year-end retrospective. The skill does not warn at this tier (the writer's site is theirs to fill), but suggests the piece may also fit the medium venue if the writer wants wider readership. |

When budget is S, the post drops any framing context and starts with the observation. When budget is X, the post acquires sub-stories or supporting cases that the M-tier version would have to elide.

## Audience interaction

- **beginner**: extend any framing context. The blog venue's reader knows the writer but may not know the framework; a parenthetical gloss for unfamiliar symbols on first appearance is welcome ("`@MainActor` (Swift's annotation that says: this code runs on the main thread)"). The post should still be in the writer's voice; the explanation is part of the conversation, not a tutorial detour.
- **intermediate**: default voice. The reader recognizes the framework and is reading for what the writer noticed about it.
- **senior**: tighten any framing; the senior reader is here for the writer's observation, not the recap. Add a "What I'm thinking about now" or "Where I'm not sure" section near the end. Senior readers of personal blogs respond well to uncertainty named explicitly; it gives them something to think about rather than a settled conclusion to nod to.
- **mixed**: write for intermediate. The blog venue's audience is, by construction, the writer's audience: they self-select, and over time they tend to converge on the writer's typical register. A post that tries to address all three audiences in the same piece tends to read as if the writer doesn't know who they are talking to.

## Honest-machine section

When `honest_machine_optin: true`, append a `## Caveats` section near the end of the post. The section is in the writer's voice, brief (50-150 words), and acknowledges what the post does NOT cover. The register matches the rest of the post: a personal acknowledgment, not a disclaimer.

Format: prose, with optional bullets when the caveats are list-shaped. The section reads as the writer naming the limits of what they figured out, not as a legal hedge. Examples of the right register: "I have only run this on iOS 26 and only on the additive case. Renames and deletes are a different problem and I haven't solved that one yet."

The section is not the closing of the post. The post closes on a personal note (often one or two sentences) after `## Caveats`. The honest-machine section is the writer being honest about the post's scope; the closing is the writer being themselves.

## Voice exemplar (V3 schema migration, audience=intermediate, budget=M, hm=on)

> # Two days for four lines
>
> *2026-05-08*
>
> *Tags: swift, swiftdata, migration*
>
> Shipped a schema change for v3 of the app last week. Wired up a `VersionedSchema` and a `SchemaMigrationPlan` with one `MigrationStage`. Tested in the simulator with seeded v2 data. Three runs in a row, clean. Sent it.
>
> Cold-relaunched on my own iPhone the next morning and the app crashed on launch.
>
> ```text
> Duplicate version checksums detected
> ```
>
> ## What I tried first
>
> The error refers to SwiftData's checksum across each `VersionedSchema`'s `versionedSchemaIdentifiers`. The framework computes a checksum for each declared schema and refuses the migration plan when two checksums collide. My V2 and V3 referenced the same Swift `@Model` types, so the checksums were identical by construction.
>
> Fork A: rename the V3 wrapper. Same crash.
>
> Fork B: duplicate the underlying type and reference the duplicate from V3. Worked, but broke every `KeyPath` reference in the inverse-relationship declarations elsewhere in the model.
>
> Fork C: subclass the V3 schema declaration. SwiftData rejected the subclass at runtime. Different crash. Worse.
>
> Two days. Three forks. The framework was correctly refusing every migration plan I gave it because every migration plan was, from the framework's perspective, a no-op masquerading as a migration.
>
> ## What actually worked
>
> Delete the migration plan.
>
> ```swift
> // Before
> let container = try ModelContainer(
>     for: Item.self,
>     migrationPlan: AppMigrationPlan.self,
>     configurations: ModelConfiguration()
> )
>
> // After
> let container = try ModelContainer(
>     for: Item.self,
>     configurations: ModelConfiguration()
> )
> ```
>
> SwiftData has an implicit lightweight migration path that handles additive schema changes (new optional properties, new model classes, new optional relationships) without any `SchemaMigrationPlan` at all. My change was additive. The migration plan was the bug. Deleting it fixed the crash.
>
> Two days for those four lines, and the four lines were the four lines I had originally added.
>
> ## What I'm chewing on
>
> The framework's documented path is calibrated for the harder case (renames, deletes, type changes). My case was the easy one. Applying the harder case's machinery to the easier case introduced the failure mode the easier case did not have on its own. I keep wanting to call this a bug in the framework, and it isn't; the framework is doing what it is documented to do, and the documentation is correct. The mismatch is in my head: I read the documented path as the canonical path and applied it to a case that the framework had a simpler path for.
>
> I think the lesson is something like: when a framework offers two paths and the easier one is the default (no migration plan needed), the easier path is probably the one the framework's authors expect most users to take. The documented hard path is documented because it needs documentation; the easy path is invisible because it doesn't.
>
> Or maybe the lesson is just: ship to a real device before declaring victory. I had three clean simulator runs. The simulator caught nothing.
>
> ## Caveats
>
> This only covers the additive case. If your schema change is a rename, a delete, a type change, or a cardinality flip, the implicit path will not migrate your data and you genuinely need the `SchemaMigrationPlan` machinery. I haven't done one of those yet on a shipping app and I am not looking forward to it.
>
> I also haven't tested this on iOS 25 or earlier; my devices are all on iOS 26. Mileage may vary on older runtimes.
>
> Going to take the rest of the day off.

The exemplar above is approximately 700 words, below the M-tier target of 1000 and well within the ceiling of 1500. A real blog post at M might extend "What I'm chewing on" with a related observation from a previous incident, or might be shorter still if the writer's blog tends toward terse posts. Treat the exemplar as a calibration of voice rather than as a length target.

## What blog is NOT

- Not a magazine essay. The blog venue's reader knows the writer; the medium venue's reader is being introduced to the writer in the lede. The blog venue can skip the introduction.
- Not a Reddit post. Reddit posts are read by strangers in a feed; blog posts are read by subscribers on the writer's site. The Reddit post must convert the click in the first two lines; the blog post starts with the writer's voice already established.
- Not a tutorial. Tutorials walk a reader through reproducing a result; blog posts share what the writer did. The reader of a blog post is interested in the writer's experience, not in repeating it.
- Not a runbook. A runbook is a repository document that operators read while doing the operation; a blog post is read by people who are not currently doing what the post describes. If the post is structured as steps to follow, it is reaching for the repo-doc venue.

## Recovery hook interaction

Blog posts (like all Path 2 audience-facing artifacts) do NOT trigger the recovery system. They are standalone Markdown files the writer commits to their static-site source (Jekyll's `_posts/`, Hugo's `content/posts/`, Eleventy's configured posts directory) or pastes into a Substack editor; the skill's job ends at the file write.

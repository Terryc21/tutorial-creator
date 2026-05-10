# tutorial-creator v2: Audience-facing path (Path 2)

This file holds the procedures for the **audience-facing** path. SKILL.md handles routing into this file; this file handles what each entry actually does and how it hands off to a venue template.

The audience-facing path produces artifacts intended for **other readers**: Reddit posts, book chapters, Apple Developer articles, Medium essays, blog posts, GitHub repo docs. It is distinct from the writing-to-learn path (Path 1, in SKILL.md), which produces artifacts for the user themselves to learn from.

> **Relationship to Path 1.** The five Path 2 entries `[a]`-`[e]` share letters with Path 1 entries but are different procedures. `Path 1 [a]` (Daily progression) and `Path 2 [a]` (Annotated source) have nothing in common except the letter. Do not conflate them.

---

## Asymmetries with Path 1 (intentional, not bugs)

Future audits may flag these as "missing"; they are deliberate choices for Path 2:

- **No `### Cold-start handling`.** Path 1 entries depend on accumulated state (PROGRESS.md, vocabulary.yaml). Path 2 entries are stateless: each invocation produces one standalone artifact for an audience. Cold-start has nothing to handle.
- **No recovery-system hook.** Path 1's tutorial generation calls the pre-write and post-write hooks (`SKILL.md:252` and `SKILL.md:260`), which snapshot files into `.claude/tutorial-sessions/<id>/` for `undo`. Path 2 does NOT call these hooks. Audience-facing artifacts do not update PROGRESS.md or vocabulary.yaml; there is no learning-state to roll back. The artifact is a standalone file the user copies into the target venue (Reddit editor, book draft, blog CMS); the skill's job ends at the file write. If the user wants the artifact tracked in their learning record, they should pair it with a Path 1 entry on the same source.
- **No vocabulary write.** Path 1 entries add new terms to `vocabulary.yaml`. Path 2 reads `vocabulary.yaml` (to align audience-facing terminology with the user's own vocabulary, if they have one) but never writes to it.
- **No `next_day` increment.** Path 2 artifacts are not days in the user's progression.

---

## Entry [a]: Annotated source

**Use when** the user has a specific file in their codebase that demonstrates a pattern worth writing about for an audience.

**Distinguishing from Path 1 [b]:** Path 1 [b] teaches the user about the file. Path 2 [a] teaches the audience about the file. The framing inverts: Path 1 says "Day 12: I learned X by reading this file." Path 2 says "Here's a real-world example of X."

### Procedure

1. **Read config.** `.claude/tutorial-config.yaml`. Required fields: `language`, `project_dir`. `experience_level` is read but the audience-facing render uses the audience answer (step 4) instead.
2. **Receive topic + source.** The user provides both. If only one is provided, route them to entry [c] (synthesized example) for topic-only, or ask for a topic for source-only.
3. **Read the source file.** Identify the line range that demonstrates the topic (use the same matching heuristic as SKILL.md Entry [c] step 3, but skip the candidate-ranking step; the user has already chosen the file).
4. **Ask the four routing questions.** Via AskUserQuestion, in this order:
   - **Audience:** beginner / intermediate / senior / mixed
   - **Honest-machine opt-in:** Y / N (asks "Append a section on what this article does NOT cover and what's still uncertain?")
   - **Length budget:** S / M / L / X (show the venue's word count for each tier, resolved from `venues/_schema.yaml`)
   - **Venue:** reddit / book-chapter / apple-developer-article / medium *(not yet available)* / blog *(not yet available)* / repo-doc *(not yet available)*

   **Partial-Phase-7 guard (load-bearing).** If the user selects `medium`, `blog`, or `repo-doc`, refuse with this exact message and stop, do NOT proceed to step 5:

   > Venue `<name>` is not yet shipped in `2.0.0-phase7-partial`. Available venues right now: `reddit`, `book-chapter`, `apple-developer-article`. Pick one of those, or wait for the next release.

   The runtime must NOT attempt to load `venues/<name>.md` for an unshipped venue under any circumstance; the file does not exist and the open will fail with no graceful path.
5. **Hand off to venue template.** Open `venues/<chosen>.md` and render the article using the venue's voice signature, supplying:
   - `topic` (string)
   - `source` (file path + line range)
   - `audience` (one of the 4 values)
   - `length_budget` (one of S/M/L/X, with resolved word target + ceiling)
   - `honest_machine_optin` (boolean)
   - The user's `vocabulary.yaml` (for terminology alignment)
6. **Write the artifact.** Save to a path the user picks (default: `./audience-artifacts/<venue>-<topic-slug>.md`). The skill does not insert the artifact into a venue's CMS or post it; the user does that step manually.

### Honesty rule

If the source file is too small to support a meaningful audience artifact at the chosen length budget (heuristic: the topic-relevant line range is < 5 lines AND the budget is M+), surface that mismatch explicitly:

> The source's `<topic>` example is only `<N>` lines. At budget M (target `<N>` words), the article will pad with framing and tangent material. Two options:
>
> [shorter] Use budget S instead (target `<N>` words; tighter fit)
> [different] Pick a different source with more material
> [proceed] Generate at M anyway (expect padding)

Do not silently pad. The reader of the audience artifact is the one who pays the cost of padding; the skill must make the user aware of it before they ship the artifact.

---

## Entry [b]: Incident-grounded

**Use when** the user has a real failure or decision they want to write about: a production crash, a debugging story, an architecture choice, a deprecation that bit them.

**Distinguishing from entry [a]:** Entry [a] is "here's a file." Entry [b] is "here's what happened." Entry [b] articles often reference one or more files but the spine is the narrative, not the code.

### Procedure

1. **Read config.** Same fields as entry [a].
2. **Receive the incident.** The user provides a free-form description of what happened. Capture:
   - The symptom (what the user observed)
   - The diagnosis (what they found)
   - The fix (what they changed)
   - Any source files involved (optional; for inline code in the artifact)
3. **Identify the topic.** Extract a single technical concept from the incident. The article will be framed around this concept ("here's how I learned X the hard way") even when the user pitched the request as a story.
4. **Ask the four routing questions** (same as entry [a] step 4).
5. **Hand off to venue template** (same as entry [a] step 5), with the incident's symptom-diagnosis-fix structure as the article's spine.
6. **Write the artifact** (same as entry [a] step 6).

### Honesty rule

If the user's diagnosis in step 2 looks contradicted by the source (e.g., they say "the bug was in `X.swift`" but `X.swift` doesn't contain the symptom they describe), surface the mismatch:

> The symptom you described (`<symptom>`) doesn't match what's in `<file>` at the lines you pointed to. Two possibilities:
>
> [different-file] You meant a different file
> [different-symptom] The symptom is more nuanced than the description
> [proceed] Generate the article from your description as-is (the artifact will reflect what you said, not what's in the source)

Audience-facing artifacts that contradict their own source code damage the user's reputation with the audience. The skill must surface the mismatch before generating, even if it slows the workflow.

---

## Entry [c]: Synthesized example

**Use when** the user has a topic in mind but no real source file demonstrates it well, or the real example is too tangled to teach from. The skill generates a contrived minimal example for the article.

**Distinguishing from entry [a]:** Entry [a] uses real code from the user's project. Entry [c] uses code the skill writes. The article must signal this to the audience explicitly (see honesty rule below).

### Procedure

1. **Read config.** `language` is the only strictly-required field; the synthesized example follows the project's language even when no project file is referenced.
2. **Receive topic.** The user provides a free-form topic.
3. **Generate the minimal example.** The example must:
   - Compile (the skill verifies this when possible by checking syntax)
   - Be the smallest example that demonstrates the topic (usually 5-30 lines)
   - Have no extraneous concepts (no unrelated frameworks, no project-specific types)
   - Be idiomatic for the language at the chosen audience level
4. **Ask the four routing questions** (same as entry [a] step 4).
5. **Hand off to venue template** (same as entry [a] step 5), with the synthesized example as the source. The venue template MUST be told this is synthesized (one of the venue file's responsibilities is rendering the "this is a synthesized example" disclosure in voice).
6. **Write the artifact** (same as entry [a] step 6).

### Honesty rule (load-bearing)

Every artifact generated through entry [c] must include an explicit, in-voice disclosure that the example is synthesized. The disclosure goes near the top of the article (before the example itself) and is rendered in the venue's voice:

- **reddit:** "Quick disclaimer: this is a contrived example, not real production code."
- **book-chapter:** integrated into the framing paragraph; e.g., "The example below is intentionally simplified. A production codebase would..."
- **apple-developer-article:** "The following is an illustrative example. See [related sample code] for production patterns." (The bracketed link is left as a placeholder for the user to fill in.)
- **medium:** integrated into the lede paragraph; e.g., "Imagine a reduced version of the problem: ..."
- **blog:** "Heads up: the code below is a sketch, not a full app."
- **repo-doc:** A boxed callout: "**Note:** Example is illustrative; for production usage, see `<actual file path>`."

Do not omit the disclosure under any audience or budget setting. The reader's trust depends on knowing whether they're looking at battle-tested code or a teaching example.

---

## Entry [d]: External source

**Use when** the user wants to write an audience-facing article about code they didn't write themselves: a public repo, an Apple sample, a blog post, an open-source library.

**Distinguishing from entry [a]:** Entry [a] is the user's own code. Entry [d] is someone else's. The honesty rule (attribution) is the load-bearing difference.

### Procedure

1. **Read config.** `language` is needed for syntax-aware rendering.
2. **Receive the external source.** The user provides:
   - The URL or local path to the source
   - The license of the source (the skill asks if not provided)
   - The author or project name (for attribution)
3. **Read the source.** If a URL, the skill MUST verify the source is accessible (HEAD request or equivalent) before proceeding; broken links damage the artifact.
4. **Ask the four routing questions** (same as entry [a] step 4).
5. **Hand off to venue template** (same as entry [a] step 5), supplying additionally:
   - `external_attribution` (object with `author`, `project`, `url`, `license`)
   - The venue template MUST render attribution in voice (each venue file specifies how)
6. **Write the artifact** (same as entry [a] step 6).

### Honesty rule (load-bearing)

Three sub-rules, all enforced:

1. **License compatibility.** If the external source's license forbids derivative works (e.g., NoDerivatives), the skill must refuse to generate an article that quotes the source extensively. Offer entry [c] (synthesized example using the same concept) as a fallback. Surface the refusal explicitly: "Source license `<license>` does not permit derivative quoting at the length budget you chose. Two options: [c-fallback] Synthesize an equivalent example. [smaller-budget] Use budget S (which quotes only short snippets, generally fair use)."
2. **Attribution placement.** Attribution appears **before** the first quote from the external source, not as a footnote. Each venue file specifies the attribution format in voice.
3. **No silent paraphrase.** If the article paraphrases the external source's prose (not just code), the venue template MUST mark it as a paraphrase ("paraphrasing the original:..." or similar). Do not blend the external author's reasoning into the user's voice without flagging it.

---

## Entry [e]: Documentation-grounded

**Use when** the user wants to write an audience-facing article grounded in official documentation: Apple Developer docs, RFCs, language specifications, framework reference manuals.

**Distinguishing from entry [d]:** Entry [d] is third-party code. Entry [e] is normative reference text. The honesty rule (citation precision) is the load-bearing difference.

### Procedure

1. **Read config.** `language` for syntax-aware rendering.
2. **Receive the documentation reference.** The user provides:
   - URL(s) to the doc page(s)
   - Optional: the section anchor or paragraph the article is built around
3. **Fetch the doc page.** The skill verifies the URL resolves and reads the relevant section. If the page has shifted (the anchor no longer exists, or the paragraph no longer matches what the user described), surface the discrepancy before generating.
4. **Ask the four routing questions** (same as entry [a] step 4).
5. **Hand off to venue template** (same as entry [a] step 5), supplying additionally:
   - `doc_citations` (list of `{url, anchor, accessed_date}` objects)
   - Each venue file renders citations in its native style (footnote, inline parenthetical, See Also section)
6. **Write the artifact** (same as entry [a] step 6).

### Honesty rule (load-bearing)

1. **Cite the version.** Documentation changes; an article quoting "the Apple Developer docs" without specifying iOS version or accessed date is wrong within months. Every doc citation includes the version and access date.
2. **Quote, don't paraphrase, normative claims.** When the article makes a claim about behavior ("`Task.detached` does not inherit actor isolation"), the supporting citation MUST be a direct quote, not a paraphrase. Paraphrasing normative documentation introduces drift between what the article claims and what the source actually says.
3. **No claims beyond the docs.** If the user wants to add a claim the docs don't directly support ("in practice this also means..."), the article must mark that claim as the user's own observation, not as documentation.

---

## Audience and length budget interaction

Audience and length budget interact at generation time, **not** as a 4×4×6 matrix encoded in venue files. Two rules govern the interaction; venues apply them within their voice:

- **Beginner audience shifts content toward setup and definition.** The article spends more words establishing context, defining symbols, and naming what the example is doing. Less ratio of code-to-prose; more parenthetical definitions.
- **Senior audience shifts content toward tradeoffs and alternatives.** The article spends more words on "the obvious alternative is X but it loses Y," "this works for the additive case but breaks for the renamed-property case," "the reason this is non-obvious is..." Less introductory definition; more "why this and not that."
- **Intermediate is the default voice the venue file's exemplar shows.**
- **Mixed audience defaults to intermediate.** The skill offers a one-line heads-up to the user: "Mixed-audience articles tend to lose senior readers in the setup and lose beginner readers everywhere; consider choosing a single audience for sharper voice." User can proceed anyway.

The length budget moderates **how much room** the audience-shift gets. At budget S, beginner content shifts only the opening paragraph toward setup. At budget X, beginner content shifts the entire first half of the article toward setup. The shift direction is constant; the magnitude scales with budget.

Venues apply these shifts within their own voice. Reddit at audience=beginner adds parenthetical definitions; book-chapter at audience=beginner adds a full "Background" section. Each venue's exemplar (in `venues/<name>.md`) shows the intermediate baseline; the audience shift moves around that baseline.

---

## Honest-machine opt-in

When the user answers Y to the honest-machine question, the venue template appends a section listing what the article does NOT cover and what's still uncertain. The section name varies by venue (resolved from `venues/_schema.yaml#venues.<name>.honest_machine_section_name`):

| Venue | Section name |
|---|---|
| reddit | `Edit` |
| book-chapter | `Limits and open questions` |
| apple-developer-article | `See Also and open questions` |
| medium | `What this leaves out` |
| blog | `Caveats` |
| repo-doc | `Out of scope` |

The section's content is generated per-article: 2-5 bullets naming gaps, edge cases the article doesn't handle, related concepts the user hasn't decided on, or open questions the user wants reader feedback on. When `honest_machine_optin: false`, the section is omitted entirely (no header, no placeholder).

Each venue file specifies the in-voice format (Reddit's "Edit:" convention; book-chapter's nested-headers; apple-developer's bulleted "See Also" list; etc.). The intent is constant across venues: signal explicitly what the article doesn't claim, so the reader can calibrate trust.

---

## Venue rendering handoff (the contract)

Every entry [a]-[e] ends with a handoff to `venues/<chosen>.md`. The handoff supplies a single payload:

```yaml
topic: <string>
source:
  kind: <annotated | incident | synthesized | external | doc>
  path_or_url: <string>
  line_range: <string, e.g., "42-89", or null for synthesized/incident-only>
  attribution: <object, only for kind: external; null otherwise>
  citations: <list, only for kind: doc; null otherwise>
audience: <beginner | intermediate | senior | mixed>
length_budget:
  tier: <S | M | L | X>
  words_target: <int, from venues/_schema.yaml>
  words_ceiling: <int, from venues/_schema.yaml>
honest_machine_optin: <bool>
vocabulary_alignment: <list of terms from user's vocabulary.yaml, or empty list>
```

The venue file is responsible for:

1. Rendering the article in voice
2. Respecting `length_budget.words_ceiling` (the article should not exceed the ceiling; if it would, the venue file must drop content rather than exceed)
3. Applying the audience shift per the rules above
4. Inserting the honest-machine section when `honest_machine_optin: true`, omitting it when `false`
5. For `kind: synthesized`, inserting the synthesized-example disclosure (per entry [c] honesty rule)
6. For `kind: external`, inserting attribution before the first quote (per entry [d] honesty rule)
7. For `kind: doc`, inserting version + access-date citations (per entry [e] honesty rule)

The skill does NOT post-process the venue file's output. What the venue file emits is the artifact.

---

## Mode-mismatch detection (single-fire)

This is wired into SKILL.md's routing layer (the prose has been at `SKILL.md:71-73` since Phase 6). For reference, the trigger is:

- The user picked Path 2 (gateway answer `[2]` or `--mode audience`)
- AND their topic phrasing matches one of: starts with `I want to understand`, starts with `I'm confused about`, starts with `why does my`, starts with `what is`

The nudge fires once per session (a session-scoped flag flips after first surface). It never blocks; the user always has final say. The exact prose is in SKILL.md.

If the user confirms audience-facing despite the nudge, do not nudge again for the rest of the session, even if the next topic also matches. The user has demonstrated awareness.

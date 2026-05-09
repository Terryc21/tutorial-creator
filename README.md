# tutorial-creator

**Generate personalized coding lessons from your own codebase.** A Claude Code skill that turns the files you actually work on every day into annotated tutorials, tracks the vocabulary you've learned, and shows you where you're confused.

Built for [Stuffolio](https://stuffolio.app), an iOS/macOS inventory management app — and now for any Swift, TypeScript, Python, or Rust project.

<a href="https://buymeacoffee.com/stuffolio"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="120"></a>

If this skill saves you time, a [coffee](https://buymeacoffee.com/stuffolio) is appreciated. [Sponsoring](https://github.com/sponsors/Terryc21) supports further development.

> **v2.0 in development.** Path 1 (writing-to-learn) is feature-complete on the `feature/v2-robust` branch. Phases 5-8 (status dashboard, recovery, audience-facing path, polish) are remaining. Until v2.0 merges to `main`, the shipping version is **v1.1.0** and the install instructions below describe v1.1 behavior.

---

## Why this exists

Most AI coding tools optimize for speed: generate code faster, scaffold features faster, ship faster.

But many developers are now generating code faster than they can comfortably *read* or *understand* it.

`tutorial-creator` explores a different idea: AI should help developers build fluency and understanding, not just produce more code.

While building Stuffolio, I realized something uncomfortable: Claude Code was helping me generate Swift code faster than I was developing fluency reading it. Traditional tutorials taught syntax using toy examples like `let x = 5`, but real projects don't look like that. Real projects contain async workflows, state management, dependency injection, conditional rendering, architectural patterns, edge cases, and accumulated design decisions.

I didn't want to stop building and go study disconnected tutorial exercises. I wanted to learn from the actual code appearing in my own project every day. So I built a Claude Code skill that turns real project files into personalized annotated lessons.

This skill:

- Generates personalized coding lessons from your own codebase
- Tracks vocabulary and concept progression across sessions
- Detects missing prerequisites and proposes bridge tutorials automatically
- Helps you learn naturally while continuing to ship real software
- *(v2.0)* Manages vocabulary as a first-class object, not a side effect of writing tutorials
- *(v2.0)* Shows you which terms you're confused about and proposes targeted lessons
- *(v2.0)* Supports six entry points to learning (daily progression, topic + file, topic only, question, gap-driven, external source)

---

## v2.0 — Three surfaces, gateway-mediated

> Available on the `feature/v2-robust` branch; not yet merged to `main`.

v2.0 splits the skill into three top-level surfaces, with a gateway question that asks you what you actually want to do before assuming you want to write a tutorial.

| Surface | Purpose | Subcommands |
|---|---|---|
| **`tutorial`** | Generate a lesson | 6 entry points (writing-to-learn) + 5 (audience-facing, Phase 7) |
| **`vocab`** | Manage your vocabulary | `add`, `list`, `show`, `edit`, `merge`, `review`, `gap`, `regen-md`, `undo` |
| **`status`** | Inspect your learning state | Read-only dashboard (Phase 5) |

Bare invocation opens the gateway:

```
/skill tutorial-creator

What do you want to do?

[1] Write a tutorial for myself      (writing-to-learn)
[2] Write a tutorial for others      (audience-facing)
[3] Manage vocabulary                 (jump to vocab surface)
[4] Inspect my learning state         (jump to status surface)
```

The legacy v1.1 invocation (`/skill tutorial-creator <topic> <source>`) still works and routes to entry [b] (topic + file).

### Six entry points for writing-to-learn

The skill doesn't assume you have a topic + file in mind. Pick the entry that matches where you are:

| Entry | Use when… |
|---|---|
| **[a] Daily progression** | You want the next concept in your learning sequence |
| **[b] Topic + file** | You have both ("closures in `helpers.ts`") |
| **[c] Topic only** | You have a topic; let the skill find the best file |
| **[d] Question-led** | You're stuck on something specific ("why does my SwiftData fetch return zero?") |
| **[e] Gap-driven** | Show me what I'm confused about; pick from there |
| **[f] External source** | I read this Apple doc / blog post / RFC; help me consolidate |

Entry [c] ranks candidate files by **pedagogical fit** (small file with concentrated examples beats large file with scattered ones), shows evidence (line counts, line ranges, brief reasons), and lets you pick. If no good example exists in your codebase, it offers a synthesized minimal example instead of silently picking a marginal file.

Entry [d] is the highest-value, highest-risk entry. When the question is ambiguous, the skill surfaces the ambiguity ("I see two ways to interpret this; which fits?") rather than picking one and proceeding. The honest-machine voice is load-bearing here.

Entry [e] reads from the vocab gap view (terms with `status: confused`) and generates a tutorial targeted at one of them. The tutorial's framing acknowledges the gap directly — Pre-Test targets the specific aspect the user has been getting wrong.

### Vocabulary as a first-class object

In v1.1, vocabulary was a side effect of writing tutorials: the only way a term entered `VOCABULARY.md` was by being introduced in a generated tutorial. v2.0 decouples them.

Now you can:

- **`vocab add <term>`** — capture a term outside a lesson (encountered in a code review, read in someone else's tutorial, mentioned in a meeting). The skill drafts a definition; you accept or edit.
- **`vocab review`** — spaced-repetition test session. The skill picks 5 terms, prioritizing confused > stale > random. You write each definition; the skill grades leniently by default (concept match, not verbatim) and updates status.
- **`vocab gap`** — see exactly which terms you've been getting wrong, ranked by how long you've been stuck. Feeds entry [e] gap-driven directly.
- **`vocab list --status=confused`** — filter by any status (new / reviewing / mastered / confused).
- **`vocab merge <a> <b>`** — collapse duplicates (`@Observable` and `Observable macro`) while preserving test history.

Status is **earned through tests, not user-set**. Mastered requires 3 consecutive correct results; confused requires 2 of last 3 partial/wrong. The one allowed manual transition is `mastered → reviewing` (you noticed you've forgotten something). Getting back to mastered requires re-earning it.

### Status dashboard *(Phase 5)*

A read-only at-a-glance view of your learning state:

- Tutorials shipped, last lesson, streak, suggested next concept
- Vocabulary counts by status (mastered / reviewing / confused / new)
- Due for review (terms unreviewed > 14 days)
- Gap radar (top 3-5 confused terms with staleness)
- Suggested next lesson (combines vocab gap + progression)

### Recovery / undo *(Phase 6)*

Every tutorial generation logs a session record and snapshots the four files it modifies. `undo` reverts the last generation cleanly. Vocab additions are revertable for 24 hours via `vocab undo`. Day numbers can be retroactively renumbered via `renumber <old> <new>`, which rewrites references across PROGRESS.md, VOCABULARY.md, and other tutorials.

### Audience-facing path *(Phase 7)*

v2.0 adds a second gateway path for users who want to publish what they've learned. Instead of writing-to-learn, you're writing-to-teach. Five entry points (annotated source / incident-grounded / synthesized example / external source / documentation-grounded), six venue templates (blog, Reddit, Medium, Apple Developer-style article, book chapter, repo doc), with venue-aware voice calibration.

---

## What you get (every tutorial)

Each generated tutorial includes:

- **Vocabulary table:** only new terms, no repetitive definitions
- **Pre-test:** determine what you already know
- **Core pattern explanation:** simple conceptual overview first
- **Annotated real code:** inline explanations of your actual source file
- **Common mistakes:** realistic failure modes and fixes
- **Post-test:** apply the concepts at a deeper level
- **Answer key:** full explanations for both tests
- **New Concepts Introduced:** quick-reference table feeding the Concepts Mastery Checklist

Plus cumulative tracking across tutorials:

- `vocabulary.yaml` (v2.0 source of truth) + auto-generated `VOCABULARY.md` view
- `PROGRESS.md` with score log + concepts mastery checklist
- Concept progression tracking
- Learning gap analysis

### Gap analysis

After each tutorial, the skill asks: *"Does this lesson depend on concepts that haven't been taught yet?"* If so, it proposes prerequisite tutorials automatically.

This prevents the common experience of understanding Tutorial 1, surviving Tutorial 2, and getting completely lost in Tutorial 3.

A real example. I asked `tutorial-creator` to write Day 16, a tutorial about a SwiftUI captured-`self` staleness bug. After it finished, the skill checked whether the new lesson leaned on anything I hadn't covered in earlier days. It found two prerequisite gaps, ranked which ones to fill first, and named them as half-step tutorials (Day 15.5 and Day 9.5) so they would slot between existing days without renumbering anything:

![tutorial-creator gap analysis showing prerequisite mapping and proposed bridge tutorials](images/tutorial-creator-gap-analysis.png)

I wrote both bridge tutorials in the same session. Without the gap analysis I'd have shipped Day 16 with two unstated prerequisites and slowly accumulated learning debt. With it, the curriculum stays self-consistent automatically.

### Traditional tutorials vs tutorial-creator

| Traditional tutorials | tutorial-creator |
|:--|:--|
| Toy examples | Your real codebase |
| Static curriculum | Adaptive progression |
| Generic vocabulary | Vocabulary from your project |
| No continuity | Persistent progress tracking |
| Assumes prerequisites | Detects missing concepts |
| Read-only | Tested via spaced-repetition review *(v2.0)* |
| One mode | Six entry points + audience-facing path *(v2.0)* |
| Separate from production work | Integrated into active development |

### Example workflow

```
Your code  ──►  tutorial-creator  ──►  Annotated lesson
                       ▲                       │
                       │                       ▼
                  Gap radar  ◄─────  Vocabulary tracking
                       │                       │
                       └────  Status dashboard ◄
```

### Usage

```
# v1.1 invocation (still works in v2)
/skill tutorial-creator [topic] [source]

# v2 invocations
/skill tutorial-creator                        # opens gateway question
/skill tutorial-creator vocab review           # spaced-rep test
/skill tutorial-creator vocab gap              # show confused terms
/skill tutorial-creator status                 # learning-state dashboard
/skill tutorial-creator --mode learn           # skip gateway -> writing-to-learn
/skill tutorial-creator --mode audience        # skip gateway -> audience-facing
```

### First-run setup

On first use, the skill asks:

1. Where to save tutorials
2. Your language/framework
3. Your experience level
4. Your project directory

Configuration is saved to `.claude/tutorial-config.yaml`. Edit anytime to adjust progression or preferences.

### Supported languages

Built-in learning progressions exist for:

| Language | Progression |
|:--|:--|
| **Swift / SwiftUI** | Utilities → Models → ViewModels → Views → Managers → Serialization |
| **TypeScript / React** | Utilities → Hooks → Components → State Management → API Layer → Testing |
| **Python / Django** | Utilities → Models → Views → Serializers → Middleware → Testing |
| **Rust** | Ownership → Traits → Error Handling → Async → Unsafe → Architecture |

Swift gets the deepest curation — the bundled examples and the daily-practice demo are Swift. The other three languages have built-in progressions and work, but the examples are Swift-only. Custom progressions can be defined in `.claude/tutorial-config.yaml#progression_override`.

### Example tutorials

Three complete generated tutorials are included, showing how the skill scales from a beginner's first SwiftUI view to an advanced bug-driven case study to a non-Swift hook:

**Starter:** [Day 3 — ScoutResultsLookupView.swift](skills/tutorial-creator/examples/Day3-ScoutResultsLookupView-Annotated.md). The first SwiftUI view a Stuffolio reader walked through. They could read the file before, but reading it didn't *teach* them anything. The annotated tutorial points at what each line is doing and why, builds a vocabulary table from terms the reader hadn't formally learned (`@Environment`, `@Query`, key paths, `NavigationStack`), and ends with a pre/post-test pair so the reader knows whether the lesson actually landed.

**Advanced:** [Day 16 — Captured-Self Staleness](skills/tutorial-creator/examples/Day16-CapturedSelfStaleness-Annotated.md). Built around a real production bug where a SwiftUI macOS app's window vanished on save. The bug was three lines and looked dumb in retrospect; the lesson is everything you'd want to know to never write it. Demonstrates the full format: vocabulary, pre-test, core pattern, annotated source, common mistakes, post-test, answer key, and connections back to earlier tutorials. This is also the tutorial whose gap analysis is shown in the screenshot above.

**Non-Swift (TypeScript / React):** [useDebouncedValue: A Custom React Hook](skills/tutorial-creator/examples/useDebouncedValue-Annotated.md). Demonstrates that the format ports cleanly to other languages. Annotates a real-world custom hook (debouncing a search input) with vocabulary, pre-test, line-by-line walkthrough, common mistakes, and a post-test calibrated to React's `useEffect` cleanup semantics and TypeScript generics. Useful as a sanity check that the skill isn't iOS-specific.

**v2 schema example:** [vocabulary-example.yaml](skills/tutorial-creator/examples/vocabulary-example.yaml) shows the v2.0 vocabulary format with all four status values represented (new / reviewing / mastered / confused).

---

## Philosophy

Many AI coding tools optimize for generation, automation, and acceleration.

`tutorial-creator` focuses more heavily on:

- Comprehension
- Fluency
- Workflow understanding
- Architectural awareness
- Long-term developer growth

AI can generate code instantly. Understanding it still takes time. This skill is designed to help close that gap.

The v2.0 redesign extends this philosophy: vocabulary as a first-class learning artifact (review, gap radar, status earned through tests rather than self-claimed); honest-machine voice when the skill can't confidently answer your question (surface ambiguity, don't pick silently); recovery so wrong choices are easily revertable.

---

## Install

```bash
git clone https://github.com/Terryc21/tutorial-creator.git
```

**Global install** (all projects):

```bash
mkdir -p ~/.claude/skills && cp -r tutorial-creator/skills/* ~/.claude/skills/
```

**Project-specific install** (one project only):

```bash
mkdir -p /path/to/project/.claude/skills && cp -r tutorial-creator/skills/* /path/to/project/.claude/skills/
```

### Migrating from v1.1 to v2.0

Once v2.0 merges to `main`, users with existing v1.1 vocabulary need a one-time migration:

```bash
# After installing v2.0:
/skill tutorial-creator vocab regen-md --import
```

This converts your existing `VOCABULARY.md` Markdown table into the v2.0 `vocabulary.yaml` source-of-truth file. Migrated terms get `status: reviewing` (no v1.1 test history exists). You can `vocab edit` to add types, `vocab merge` to collapse duplicates, and `vocab review` to start earning mastered status.

---

## Related Claude Code skills

Other skills built during development of Stuffolio:

- [**prompter**](https://github.com/Terryc21/prompter): rewrite Claude Code prompts for clarity before execution. Originally bundled with this repo; split into its own home so the audience that wants prompt rewriting can find it without first finding a tutorial-generation tool.
- [**bug-echo**](https://github.com/Terryc21/bug-echo): after fixing a bug, locate and rate similar patterns elsewhere in the codebase
- [**workflow-audit**](https://github.com/Terryc21/workflow-audit): multi-layer behavioral audit of SwiftUI user workflows
- [**radar-suite**](https://github.com/Terryc21/radar-suite): behavioral audit suite for iOS/macOS Swift projects
- [**unforget**](https://github.com/Terryc21/unforget): single source of truth for deferred work; nothing slips between releases

These tools focus on workflow behavior and user experience, not just static code inspection.

---

## History

This repo (then named `code-smarter`) originally bundled two skills: `tutorial-creator` and `prompter`. The `prompter` skill was extracted into its own repo at [github.com/Terryc21/prompter](https://github.com/Terryc21/prompter) (with full commit history preserved) so each focused tool can be discovered independently. The repo was renamed from `code-smarter` to `tutorial-creator` so the repo name matches the skill name. The old URL still redirects.

**v2.0** (in development on `feature/v2-robust`): vocabulary as a first-class object with state machine and review mode; six entry points instead of one; audience-facing path for users who want to publish what they've learned; status dashboard; recovery / undo. The redesign reframes Stuffolio's daily practice (the original use case) as a demo and treats other users — anyone learning Swift, TypeScript, Python, or Rust — as the target audience.

---

## Author

Created by **Terry Nyberg**, [Coffee & Code LLC](https://stuffolio.app/).

## License

Apache 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

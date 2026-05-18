# tutorial-creator

![Version](https://img.shields.io/github/v/tag/Terryc21/tutorial-creator?label=version) ![Last commit](https://img.shields.io/github/last-commit/Terryc21/tutorial-creator) ![Stars](https://img.shields.io/github/stars/Terryc21/tutorial-creator?style=flat) ![Issues](https://img.shields.io/github/issues/Terryc21/tutorial-creator) ![License](https://img.shields.io/github/license/Terryc21/tutorial-creator)

**Generate personalized coding lessons from your own codebase.** A Claude Code skill that turns the files you actually work on every day into annotated tutorials, tracks the vocabulary you've learned, and shows you where you're confused.

Works with any Swift, TypeScript, Python, or Rust project. Originally built during development of [Stuffolio](https://stuffolio.app), a real iOS/macOS app whose codebase serves as the bundled demo.

*~9 min read · scan the TL;DR if you only have 30 seconds*

## TL;DR

- **What:** Generate annotated lessons from your own code, track vocabulary you've learned across sessions, and see exactly what you're confused about.
- **Why:** Traditional tutorials teach syntax with toy examples; real projects have async workflows, state management, and accumulated design decisions. tutorial-creator builds fluency from the code you ship every day.
- **Install:** `git clone` into `~/.claude/skills/`; then `/skill tutorial-creator` in any session.
- **Try first:** `/skill tutorial-creator` — opens the gateway question. Pick "Write a tutorial for myself" → "Topic + file" → point it at any file. ~10 min to a real annotated lesson.
- **Example output:** [Day 16 — captured-self staleness in SwiftUI](skills/tutorial-creator/examples/Day16-CapturedSelfStaleness-Annotated.md), a real production-bug walkthrough with pre/post tests and gap analysis.
- **Maturity:** v2.0.0 (released 2026-05-10); used through Stuffolio's daily practice; deeper curation for Swift, working built-in progressions for TypeScript / Python / Rust.

## Newer to Claude Code?

A **skill** is a markdown file Claude Code knows how to run. When you type `/skill tutorial-creator`, Claude follows the instructions in this skill, asks what you want to do, then either generates a lesson, manages your vocabulary, or shows you your learning state. You don't have to memorize anything — the skill walks you through each choice.

## Install

Clone into your Claude Code skills directory:

```bash
git clone https://github.com/Terryc21/tutorial-creator ~/.claude/skills/tutorial-creator
```

Then in any Claude Code session:

```
/skill tutorial-creator
```

First-run setup prompts you for the project to learn from, your language (Swift / TypeScript / Python / Rust auto-detected), and your experience level. The skill creates `.claude/tutorial-config.yaml` and a tutorials directory in the project you point it at.

<details>
<summary><strong>Project-specific install (one project only)</strong></summary>

```bash
mkdir -p /path/to/project/.claude/skills && git clone https://github.com/Terryc21/tutorial-creator /path/to/project/.claude/skills/tutorial-creator
```

</details>

<details>
<summary><strong>Migrating from v1.1 to v2.0</strong></summary>

If you used v1.1 and have an existing `VOCABULARY.md`, run a one-time import after installing v2.0:

```
/skill tutorial-creator vocab regen-md --import
```

This converts your existing `VOCABULARY.md` Markdown table into the v2.0 `vocabulary.yaml` source-of-truth file. Migrated terms get `status: reviewing` (no v1.1 test history exists). You can `vocab edit` to add types, `vocab merge` to collapse duplicates, and `vocab review` to start earning mastered status.

</details>

See [CHANGELOG.md](CHANGELOG.md) for full release notes and the v1.1 → v2.0 changelog.

## What gets generated

![tutorial-creator gap analysis showing prerequisite mapping and proposed bridge tutorials](images/tutorial-creator-gap-analysis.png)

*Above: real gap analysis after generating Day 16. The skill found two prerequisite gaps in the user's earlier curriculum and proposed half-step bridge tutorials (Day 15.5 and Day 9.5) that slot between existing days without renumbering.*

Three sample outputs are checked into `skills/tutorial-creator/examples/`:

- **[Day 3 — `ScoutResultsLookupView`](skills/tutorial-creator/examples/Day3-ScoutResultsLookupView-Annotated.md)** — early-progression Swift tutorial annotating a single SwiftUI view file. Pre-test, annotated source, post-test, vocabulary table.
- **[Day 16 — Captured-self staleness](skills/tutorial-creator/examples/Day16-CapturedSelfStaleness-Annotated.md)** — later-progression deep dive on a subtle Swift concurrency bug pattern in the user's own codebase.
- **[`useDebouncedValue` hook](skills/tutorial-creator/examples/useDebouncedValue-Annotated.md)** — non-Swift example: TypeScript / React custom hook, same tutorial shape.

Each is a real tutorial generated from a real codebase, not a fabricated illustration.

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
- Manages vocabulary as a first-class object, not a side effect of writing tutorials
- Shows you which terms you're confused about and proposes targeted lessons
- Supports six entry points to learning (daily progression, topic + file, topic only, question, gap-driven, external source)

---

## Three surfaces, gateway-mediated

v2.0 splits the skill into three top-level surfaces, with a gateway question that asks you what you actually want to do before assuming you want to write a tutorial.

| Surface | Purpose | Subcommands |
|---|---|---|
| **`tutorial`** | Generate a lesson | 6 entry points (writing-to-learn) + 5 (audience-facing) into 6 venue templates |
| **`vocab`** | Manage your vocabulary | `add`, `list`, `show`, `edit`, `merge`, `review`, `gap`, `regen-md`, `undo` |
| **`status`** | Inspect your learning state | Read-only dashboard |

Bare invocation opens the gateway:

```
/skill tutorial-creator

What do you want to do?

[1] Write a tutorial for myself      (for my own learning)
[2] Write a tutorial for others      (preparing a lesson for others to learn)
[3] Manage vocabulary                 (edit vocabulary)
[4] Inspect my learning state         (see my progress and what I'm forgetting)
```

The legacy v1.1 invocation (`/skill tutorial-creator <topic> <source>`) still works and routes to entry [b] (topic + file).

### Six entry points for writing-to-learn

The skill doesn't assume you have a topic + file in mind. Pick the entry that matches where you are:

| Entry | Use when… |
|---|---|
| **[a] Daily progression** | You want the next concept in your learning sequence |
| **[b] Topic + file** | You have both a topic and a source file |
| **[c] Topic only** | You have a topic; let the skill find the best file |
| **[d] Question-led** | You're stuck on something specific ("why does my SwiftData fetch return zero?") |
| **[e] Gap-driven** | Show me what I'm confused about; pick from there |
| **[f] Notes & synthesis** | From a doc, post, video, or past session — help me consolidate |

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

### Status dashboard

A read-only at-a-glance view of your learning state:

- Tutorials shipped, last lesson, streak, suggested next concept
- Vocabulary counts by status (mastered / reviewing / confused / new)
- Due for review (terms unreviewed > 14 days)
- Gap radar (top 3-5 confused terms with staleness)
- Suggested next lesson (combines vocab gap + progression)

### Recovery / undo

Every tutorial generation logs a session record and snapshots the four files it modifies. `undo` reverts the last generation cleanly. Vocab additions are revertable for 24 hours via `vocab undo`. Day numbers can be retroactively renumbered via `renumber <old> <new>`, which rewrites references across PROGRESS.md, VOCABULARY.md, and other tutorials.

### Audience-facing path

v2.0 adds a second gateway path for users who want to publish what they've learned. Instead of writing-to-learn, you're writing-to-teach. Five entry points (annotated source / incident-grounded / synthesized example / external source / documentation-grounded) feed into six venue templates with venue-aware voice calibration.

After picking an entry, the skill asks four routing questions in order: audience (beginner / intermediate / senior / mixed), honest-machine opt-in (Y / N), length budget (S / M / L / X), and venue. Each answer shapes the rendered artifact: the audience setting shifts content toward setup-and-definition or tradeoffs-and-alternatives, the honest-machine opt-in adds a venue-specific section listing what the article does NOT cover, and the length budget caps the artifact's word count using per-venue tier targets.

**Venue templates:**

| Venue | Voice |
|---|---|
| `reddit` | Punchy single-thread arc, conversational first-person, one fenced block per post, "Edit:" honest-machine convention |
| `book-chapter` | Narrative essayistic, nested headers, long-form paragraphs (4-8 sentences), code in service of prose |
| `apple-developer-article` | Declarative reference voice, frequent code listings, DocC-flat sectioning, no first-person |
| `medium` | Magazine-essay register, lede-first front matter, light headers, fenced code sparingly |
| `blog` | Conversational personal-blog voice, optional headers, date-stamped front matter, code as the story needs it |
| `repo-doc` | Terse instructional README / runbook / ADR voice, structured headers, TL;DR-first front matter, fenced-minimal-prose code |

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

A real example: I asked `tutorial-creator` to write Day 16, a tutorial about a SwiftUI captured-`self` staleness bug. The screenshot at the top of this README shows what happened next — the skill checked whether the new lesson leaned on anything I hadn't covered in earlier days, found two prerequisite gaps, ranked which ones to fill first, and named them as half-step tutorials (Day 15.5 and Day 9.5) so they would slot between existing days without renumbering anything.

I wrote both bridge tutorials in the same session. Without the gap analysis I'd have shipped Day 16 with two unstated prerequisites and slowly accumulated learning debt. With it, the curriculum stays self-consistent automatically.

### Traditional tutorials vs tutorial-creator

| Traditional tutorials | tutorial-creator |
|:--|:--|
| Toy examples | Your real codebase |
| Static curriculum | Adaptive progression |
| Generic vocabulary | Vocabulary from your project |
| No continuity | Persistent progress tracking |
| Assumes prerequisites | Detects missing concepts |
| Read-only | Tested via spaced-repetition review |
| One mode | Six entry points + audience-facing path |
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

# Multi-project (invoke from any cwd; the skill walks up to find the project)
/skill tutorial-creator open <path>            # register a tutorial-creator project
/skill tutorial-creator open                   # list registered projects, set default
/skill tutorial-creator forget <path>          # remove a project from the registry
/skill tutorial-creator --project-dir <path>   # one-shot override for any subcommand
```

### Scoping a run

tutorial-creator scopes by **surface + entry point + project**. You pick what you're doing (tutorial / vocab / status), how the lesson should be sourced (daily progression / topic + file / question-led / gap-driven / notes / audience-facing), and which project's progression and vocab to use.

| Goal | Command |
|---|---|
| Generate a lesson, walking through choices | `/skill tutorial-creator` (opens gateway) |
| Lesson on a known topic + file | `/skill tutorial-creator <topic> <file>` (legacy v1.1, routes to entry [b]) |
| Lesson on a topic, skill picks the file | `/skill tutorial-creator --mode learn` then pick entry [c] |
| Lesson targeting a confused vocabulary term | `/skill tutorial-creator --mode learn` then pick entry [e] |
| Public-facing article from a file | `/skill tutorial-creator --mode audience` |
| Spaced-repetition test of your vocabulary | `/skill tutorial-creator vocab review` |
| See what you've been getting wrong | `/skill tutorial-creator vocab gap` |
| Inspect your learning state | `/skill tutorial-creator status` |
| Work on a project different from cwd | `/skill tutorial-creator --project-dir <path>` |

**Fresh vs prior history.** tutorial-creator is **history-aware by default** — it reads your existing progression (PROGRESS.md), vocabulary (vocabulary.yaml), and prior tutorials before generating a new lesson. That's the whole point: Day 16 knows what Days 1-15 already taught, and the gap-analysis pass after each generation flags prerequisites you never covered. Two ways to override:

- **Per-session fresh:** delete or rename `.claude/tutorial-config.yaml`, PROGRESS.md, and `vocabulary.yaml` for that project, then run `/skill tutorial-creator` — the skill treats the project as never-onboarded.
- **Per-tutorial fresh:** entries [b] (topic + file), [c] (topic only), and [f] (notes & synthesis) can generate a lesson independent of your progression. They still *update* vocabulary and PROGRESS.md afterwards; they just don't consult them as constraints.

Vocabulary status (mastered / reviewing / confused / new) is earned through `vocab review`, not user-set. The one allowed manual transition is `mastered → reviewing` when you notice you've forgotten something. `vocab undo` is revertable for 24 hours after a vocab change; `undo` reverts the last tutorial generation cleanly.

### First-run setup

On first use, the skill asks:

1. Confirm the project root (defaults to current working directory)
2. Where to save tutorials within that project
3. Your language/framework (auto-detected; you confirm)
4. Your experience level
5. Your project directory (the codebase you're learning from; can differ from project root)

Configuration is saved to `.claude/tutorial-config.yaml` *inside the resolved project root*, NOT necessarily the directory you invoked from. After setup, the skill offers to register the project in `~/.claude/tutorial-creator/registry.yaml` so future invocations from any cwd find it. This is the same model `git status` uses to find `.git/` from a subdirectory — your tutorials live in one place; the skill reaches them from anywhere.

Edit `tutorial-config.yaml` anytime to adjust progression or preferences. See SKILL.md `## Project resolution` for the full discovery chain (`--project-dir` flag → env var → cwd → ancestor walk → registry → first-run setup).

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

## Maturity

v2.0.0 (released 2026-05-10). v1.x line shipped through Stuffolio's daily Swift-learning practice for over six months before the v2 rewrite consolidated vocabulary as a first-class object.

**Validated shape.** Swift / SwiftUI — deepest curation, bundled examples, the daily-practice demo. Used through real production-bug case studies (Day 16 captured-self staleness, Day 3 SwiftUI scaffolding).

**Less-tested shapes.** Built-in progressions exist and work for TypeScript / React, Python / Django, and Rust, but the bundled examples are Swift-only. Audience-facing venue templates (`reddit`, `book-chapter`, `apple-developer-article`, `medium`, `blog`, `repo-doc`) have voice calibration but limited real-world use beyond Stuffolio's own publishing.

**What would sharpen it most.** Feedback from non-Swift projects using `vocab review` for a few weeks — does spaced-repetition lenient grading work for TypeScript hooks or Python decorators the way it does for SwiftUI property wrappers? [Open an issue](https://github.com/Terryc21/tutorial-creator/issues) if you try it.

---

## Sibling skills

- [**bug-echo**](https://github.com/Terryc21/bug-echo) — sibling-bug scan after a fix
- [**bug-prospector**](https://github.com/Terryc21/bug-prospector) — forward-looking bug hunt before a release
- [**workflow-audit**](https://github.com/Terryc21/workflow-audit) — 5-layer SwiftUI flow audit
- [**unforget**](https://github.com/Terryc21/unforget) — one-file deferred-work ledger
- [**radar-suite**](https://github.com/Terryc21/radar-suite) — 6-skill iOS audit family
- [**prompter**](https://github.com/Terryc21/prompter) — prompt rewriting before execution
- [**skill-reviewer**](https://github.com/Terryc21/skill-reviewer) — candid reviews of other Claude Code skills

---

## History

This repo (then named `code-smarter`) originally bundled two skills: `tutorial-creator` and `prompter`. The `prompter` skill was extracted into its own repo at [github.com/Terryc21/prompter](https://github.com/Terryc21/prompter) (with full commit history preserved) so each focused tool can be discovered independently. The repo was renamed from `code-smarter` to `tutorial-creator` so the repo name matches the skill name. The old URL still redirects.

**v2.0** (released 2026-05-10): vocabulary as a first-class object with state machine and review mode; six entry points instead of one; audience-facing path for users who want to publish what they've learned; status dashboard; recovery / undo. The redesign reframes Stuffolio's daily practice (the original use case) as a demo and treats other users, anyone learning Swift, TypeScript, Python, or Rust, as the target audience. See [CHANGELOG.md](CHANGELOG.md) for the full release notes.

---

## Feedback, suggestions, and discussion

Two channels, depending on what you've got:

| Channel | Use it for |
|:--|:--|
| [**GitHub Discussions**](https://github.com/Terryc21/tutorial-creator/discussions) | Open-ended feedback, design questions, "is this how it's supposed to work?", suggestions for new entry points / venues / progressions, sharing how you're using the skill. The right home for "I'm not sure if this is a bug." |
| [**GitHub Issues**](https://github.com/Terryc21/tutorial-creator/issues) | Concrete defect reports (it crashed, it produced wrong output, the install instructions don't work on my OS, a documented command does the wrong thing). Reproduce-able problems that need a fix. |

Pull requests welcome. For non-trivial changes please open a Discussion first so the design intent stays aligned.

---

## Author

Terry Nyberg, [Coffee & Code LLC](https://stuffolio.app/). If tutorial-creator has helped you build fluency on a real codebase, [a coffee](https://buymeacoffee.com/stuffolio) is appreciated. Issue reports about what worked or didn't on a non-Swift project are more useful.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/stuffolio)

## License

Apache 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

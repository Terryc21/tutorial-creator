# code-smarter

**Claude Code skills that help you work smarter -- auto-fix your prompts, generate personalized coding lessons from your own codebase, and more.**

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| **create-tutorial** | `/skill create-tutorial [topic] [source]` | Generate personalized coding lessons from your own codebase |
| **prompter** | `/skill prompter` | Rewrite prompts for clarity and actionability before execution |

## Install

```bash
git clone https://github.com/Terryc21/code-smarter.git
cp -r code-smarter/skills/* ~/.claude/skills/

# Or for a specific project
cp -r code-smarter/skills/* /path/to/your/project/.claude/skills/
```

---

## create-tutorial

**Learn to read code by reading *your* code -- not textbook examples.**

Most coding tutorials use toy examples (`let x = 5`). You learn the syntax but can't connect it to real code. This skill flips that -- it takes a file from your project and annotates it line by line, explaining each concept in context. Each lesson is tailored to your experience level and tracks what you've already learned.

### What You Get

Each tutorial includes:

- **Vocabulary table** -- new terms introduced (only new ones, not repeats)
- **Pre-test** -- do you already know this? (5-8 questions)
- **Core pattern** -- the concept explained simply before real code
- **Annotated real code** -- your actual source file with inline explanations
- **Common mistakes** -- what goes wrong and how to fix it
- **Post-test** -- can you apply this? (5-8 harder questions)
- **Answer key** -- full explanations for both tests

Plus cumulative tracking:

- **VOCABULARY.md** -- every term from every tutorial, in order
- **PROGRESS.md** -- score log, concepts checklist, learning progression
- **Gap analysis** -- after each tutorial, identifies prerequisite concepts you might be missing

### Usage

```bash
# First run -- setup wizard configures your learning environment
/skill create-tutorial closures src/utils/helpers.ts

# Subsequent runs
/skill create-tutorial hooks src/components/Dashboard.tsx
/skill create-tutorial error handling src/api/client.rs
/skill create-tutorial protocols Sources/Protocols/BackupManaging.swift
```

If you don't specify a source file, the skill finds one in your project that demonstrates the topic.

### First-Run Setup

On first use, the skill asks:

1. **Where to save tutorials** (default: `./tutorials/`)
2. **Your language/framework** (auto-detected from project files)
3. **Your experience level** (beginner / intermediate / advanced)
4. **Your project directory** (default: current directory)

Config saved to `.claude/tutorial-config.yaml`. Edit anytime to adjust.

### Supported Languages

Built-in learning progressions for:

| Language | Phases |
|----------|--------|
| **Swift/SwiftUI** | Utilities -> Models -> ViewModels -> Views -> Managers -> Serialization |
| **TypeScript/React** | Utilities -> Hooks -> Components -> State Management -> API Layer -> Testing |
| **Python/Django** | Utilities -> Models -> Views -> Serializers -> Middleware -> Testing |
| **Rust** | Ownership -> Traits -> Error Handling -> Async -> Unsafe -> Architecture |

Custom progressions can be defined in the config file. The skill works with any language -- these are just default phase orderings.

### Gap Analysis

After creating each tutorial, the skill checks: *"Does this tutorial use concepts not covered by any earlier tutorial?"*

If so, it proposes gap-filling tutorials (numbered as Day N.5) to bridge the prerequisite knowledge. This prevents the "I understood Day 3 but Day 4 lost me" problem.

### Example Output

Here's what a generated tutorial looks like (Swift example):

```markdown
# Day 9: Making Views Actionable -- Buttons, Gestures, and Conditional Interactivity

*Source: `Sources/Views/Detail/EnhancedItemDetailView+Helpers.swift` (DetailKeyValueRow)*
*Day 9 -- April 5, 2026 -- Views (Phase 3)*

## What You'll Learn
How to make any SwiftUI view respond to taps, how to make interactivity
conditional, and how to give users visual hints that something is tappable.

## Vocabulary
| Term | Quick Definition |
|------|-----------------|
| `Button` | A view that performs an action when tapped |
| `(() -> Void)?` | An optional closure -- a function that might not exist |
| `.contentShape(Rectangle())` | Makes the entire frame tappable |
...
```

---

## prompter

**Auto-fix your prompts before Claude Code acts on them.**

Typos, vague wording, and ambiguous references slow down AI interactions. Prompter fixes them automatically -- it rewrites your prompt for clarity, shows you the rewrite, and waits for approval before proceeding.

### Usage

```bash
/skill prompter
```

On first run, it asks how long to stay active:

- **This session only** -- rewrite prompts for this conversation
- **Add to CLAUDE.md** -- persist across all future sessions
- **Remove from CLAUDE.md** -- turn off persistent rewriting

Once active, every prompt you type gets rewritten and shown for approval before execution. Permission responses (yes/no) and option selections are skipped automatically.

---

## Origin

These skills were built during development of [Stuffolio](https://stuffolio.app), an iOS/macOS inventory management app. The developer wanted to build Swift reading fluency to review AI-generated code -- so we built a system that generates tutorials from the actual codebase being worked on.

14 tutorials later (with 134 tracked vocabulary terms), the approach proved effective enough to generalize.

## Also By This Author

### [Radar Suite](https://github.com/Terryc21/radar-suite)

**7 audit skills for Claude Code that find bugs before your users do.**

If code-smarter helps you *understand* your code, Radar Suite helps you *trust* it. It traces data through complete user flows -- backup/restore round-trips, navigation paths, schema migrations, deferred operations -- and catches bugs that file-level pattern matching misses.

| Skill | What It Catches |
|-------|----------------|
| **data-model-radar** | Schema gaps, serialization loss, relationship integrity |
| **time-bomb-radar** | Deferred operations that crash weeks after release |
| **ui-path-radar** | Dead-end navigation, unreachable features, broken deep links |
| **roundtrip-radar** | Data that doesn't survive backup -> restore or export -> import |
| **ui-enhancer-radar** | Visual quality, accessibility, design system violations |
| **capstone-radar** | Ship/no-ship decision with A-F grading across all domains |

```bash
git clone https://github.com/Terryc21/radar-suite.git
cp -r radar-suite/skills/* ~/.claude/skills/
```

## Support

If these skills save you time, consider [sponsoring](https://github.com/sponsors/Terryc21) further development.

## Author

Created by **Terry Nyberg** ([Coffee & Code LLC](https://stuffolio.app))

## License

MIT -- see [LICENSE](LICENSE).

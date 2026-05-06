# code-smarter

**Claude Code skills that help you work smarter.** Auto-fix your prompts, generate personalized coding lessons from your own codebase, and more.

Built for [Stuffolio](https://stuffolio.app), an iOS/macOS inventory management app.

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://buymeacoffee.com/stuffolio)

If these skills save you time, a [coffee](https://buymeacoffee.com/stuffolio) is appreciated. [Sponsoring](https://github.com/sponsors/Terryc21) supports further development.

---

## Why this exists

Most AI coding tools optimize for speed: generate code faster, scaffold features faster, ship faster.

But many developers are now generating code faster than they can comfortably *read* or *understand* it.

`code-smarter` explores a different idea: AI should help developers build fluency and understanding, not just produce more code.

While building Stuffolio, I realized something uncomfortable: Claude Code was helping me generate Swift code faster than I was developing fluency reading it. Traditional tutorials taught syntax using toy examples like `let x = 5`, but real projects don't look like that. Real projects contain async workflows, state management, dependency injection, conditional rendering, architectural patterns, edge cases, and accumulated design decisions.

I didn't want to stop building and go study disconnected tutorial exercises. I wanted to learn from the actual code appearing in my own project every day. So I built a Claude Code skill that turns real project files into personalized annotated lessons, plus a companion skill that improves my prompts before Claude acts on them.

These skills:

- Generate personalized coding lessons from your own codebase
- Improve prompt clarity before execution
- Help you learn naturally while continuing to ship real software

---

## Skills

| Skill | Command | Purpose |
|:--|:--|:--|
| **tutorial-creator** | `/skill tutorial-creator [topic] [source]` | Learn programming concepts from your own codebase |
| **prompter** | `/skill prompter` | Rewrite prompts for clarity before execution |

---

## tutorial-creator

### Learn to read code by reading your code

Most coding tutorials teach concepts in isolation. `tutorial-creator` teaches concepts using the actual files you already work with every day.

Instead of disconnected exercises, toy snippets, and abstract examples, you learn directly from:

- Your SwiftUI views
- Your React components
- Your Rust APIs
- Your Django models
- Your real architecture

The result is a different kind of learning: contextual, cumulative, project-aware, and immediately practical. While Claude continues helping you build, you gradually develop the fluency to review, understand, and challenge the code it generates.

### What you get

Each generated tutorial includes:

- **Vocabulary table:** only new terms, no repetitive definitions
- **Pre-test:** determine what you already know
- **Core pattern explanation:** simple conceptual overview first
- **Annotated real code:** inline explanations of your actual source file
- **Common mistakes:** realistic failure modes and fixes
- **Post-test:** apply the concepts at a deeper level
- **Answer key:** full explanations for both tests

Plus cumulative tracking across tutorials:

- `VOCABULARY.md`
- `PROGRESS.md`
- Concept progression tracking
- Learning gap analysis

### Gap analysis

After each tutorial, the skill asks: *"Does this lesson depend on concepts that haven't been taught yet?"* If so, it proposes prerequisite tutorials automatically.

This prevents the common experience of understanding Tutorial 1, surviving Tutorial 2, and getting completely lost in Tutorial 3.

**Example output** from a real `tutorial-creator` run:

![tutorial-creator gap analysis showing prerequisite mapping and proposed bridge tutorials](images/tutorial-creator-gap-analysis.png)

The skill identifies concepts the new tutorial leans on, checks which were covered by earlier days, and proposes numbered bridge tutorials (15.5, 9.5) where prerequisites are missing.

### Traditional tutorials vs tutorial-creator

| Traditional tutorials | tutorial-creator |
|:--|:--|
| Toy examples | Your real codebase |
| Static curriculum | Adaptive progression |
| Generic vocabulary | Vocabulary from your project |
| No continuity | Persistent progress tracking |
| Assumes prerequisites | Detects missing concepts |
| Separate from production work | Integrated into active development |

### Example workflow

```
Your Swift file
      ↓
tutorial-creator
      ↓
Annotated lesson
      ↓
Vocabulary tracking
      ↓
Gap analysis
      ↓
Progressive fluency
```

### Usage

```
/skill tutorial-creator [topic] [source]
```

If no source file is specified, the skill searches your project for a good example of the requested topic.

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
| **Swift / SwiftUI** | Utilities → Models → ViewModels → Views → Managers |
| **TypeScript / React** | Utilities → Hooks → Components → State Management |
| **Python / Django** | Utilities → Models → Views → Serializers |
| **Rust** | Ownership → Traits → Error Handling → Async |

Custom learning progressions can also be defined.

### Example tutorial

A complete generated tutorial example is included at:

```
skills/tutorial-creator/examples/Day3-ModelContextLogging-Annotated.md
```

It demonstrates vocabulary tracking, annotated production Swift code, testing, progressive learning structure, and gap analysis.

---

## prompter

### Improve prompts before Claude acts on them

Small prompt problems create surprisingly large downstream problems: ambiguity, vague references, overloaded requests, unclear goals, missing constraints.

`prompter` intercepts prompts before execution, rewrites them for clarity, then asks for approval before continuing. Over time, this becomes a subtle feedback loop: you start internalizing what makes prompts effective simply by watching them improve.

### Usage

```
/skill prompter
```

Activation modes:

- Current session only
- Persist via `CLAUDE.md`
- Remove persistent rewriting

### Example rewrite

**Original:**

> fix dashboard thing maybe make it cleaner

**Rewritten:**

> Refactor the dashboard layout to improve visual hierarchy and reduce clutter. Preserve existing functionality and navigation behavior. Focus specifically on spacing, grouping, and discoverability of primary actions.

### Example rewrites

A larger collection of example rewrites is available at:

```
skills/prompter/examples/Prompter-Examples.md
```

---

## Philosophy

Many AI coding tools optimize for generation, automation, and acceleration.

`code-smarter` focuses more heavily on:

- Comprehension
- Fluency
- Workflow understanding
- Architectural awareness
- Long-term developer growth

AI can generate code instantly. Understanding it still takes time. These skills are designed to help close that gap.

---

## Install

```bash
git clone https://github.com/Terryc21/code-smarter.git
```

**Global install** (all projects):

```bash
cp -r code-smarter/skills/* ~/.claude/skills/
```

**Project-specific install** (one project only):

```bash
cp -r code-smarter/skills/* /path/to/project/.claude/skills/
```

---

## Other Claude Code skills

Additional repositories built during development of Stuffolio:

- [**bug-echo**](https://github.com/Terryc21/bug-echo): after fixing a bug, locate and rate similar patterns elsewhere in the codebase
- [**workflow-audit**](https://github.com/Terryc21/workflow-audit): multi-layer behavioral audit of SwiftUI user workflows
- [**radar-suite**](https://github.com/Terryc21/radar-suite): behavioral audit suite for iOS/macOS Swift projects

These tools focus on workflow behavior and user experience, not just static code inspection.

---

## Author

Created by **Terry Nyberg**, [Coffee & Code LLC](https://stuffolio.app/).

## License

Apache 2.0. See [LICENSE](LICENSE).

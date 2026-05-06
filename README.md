# code-smarter

Built for [Stuffolio](https://stuffolio.app), an iOS/macOS inventory management app.

**Claude Code skills that help you work smarter -- auto-fix your prompts, generate personalized coding lessons from your own codebase, and more.**

If these skills save you time, a [coffee](https://buymeacoffee.com/stuffolio) is appreciated. [Sponsoring](https://github.com/sponsors/Terryc21) supports further development.

<a href="https://buymeacoffee.com/stuffolio">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="150">
</a>
### **Claude Code skills focused on developer understanding — not just code generation.**

### Most AI coding tools optimize for speed:
### - generate code faster
### - scaffold features faster
### - ship faster

### But many developers are now generating code faster than they can comfortably *read* or *understand* it.

### `code-smarter` explores a different idea:

### > AI should help developers build fluency and understanding — not just produce more code.

### These skills:
### - generate personalized coding lessons from your own codebase
### - improve prompt clarity before execution
### - help you learn naturally while continuing to ship real software

### If these skills save you time, a [coffee](https://buymeacoffee.com/stuffolio) is appreciated. [Sponsoring](https://github.com/sponsors/Terryc21) supports further development.

### <a href="https://buymeacoffee.com/stuffolio">
###   <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="150">
### </a>

### ---

### # Why This Exists

### While building Stuffolio, I realized something uncomfortable:

### Claude Code was helping me generate Swift code faster than I was developing fluency reading it.

### Traditional tutorials taught syntax using toy examples:

### ```swift
### let x = 5
But real projects don’t look like that.
Real projects contain:
* async workflows
* state management
* dependency injection
* conditional rendering
* architectural patterns
* edge cases
* accumulated design decisions

⠀I didn’t want to stop building and go study disconnected tutorial exercises.
I wanted to learn from the actual code appearing in my own project every day.
So I built a Claude Code skill that turns real project files into personalized annotated lessons.

# Skills
| **Skill** | **Command** | **Purpose** |
|:-:|:-:|:-:|
| **tutorial-creator** | /skill tutorial-creator [topic] [source] | Learn programming concepts from your own codebase |
| **prompter** | /skill prompter | Rewrite prompts for clarity before execution |

# tutorial-creator
# Learn to read code by readingyour code
Most coding tutorials teach concepts in isolation.
### tutorial-creator teaches concepts using the actual files you already work with every day.
Instead of:
* disconnected exercises
* toy snippets
* abstract examples

⠀you learn directly from:
* your SwiftUI views
* your React components
* your Rust APIs
* your Django models
* your real architecture

⠀The result is a very different kind of learning:
* contextual
* cumulative
* project-aware
* immediately practical

⠀While Claude continues helping you build, you gradually develop the fluency to review, understand, and challenge the code it generates.

# What You Get
Each generated tutorial includes:
* **Vocabulary table** — only new terms, no repetitive definitions
* **Pre-test** — determine what you already know
* **Core pattern explanation** — simple conceptual overview first
* **Annotated real code** — inline explanations of your actual source file
* **Common mistakes** — realistic failure modes and fixes
* **Post-test** — apply the concepts at a deeper level
* **Answer key** — full explanations for both tests

⠀Plus cumulative tracking across tutorials:
* VOCABULARY.md
* PROGRESS.md
* concept progression tracking
* learning gap analysis

⠀
# Gap Analysis
After each tutorial, the skill asks:
“Does this lesson depend on concepts that haven’t been taught yet?”
If so, it proposes prerequisite tutorials automatically.
This prevents the common experience of:
* understanding Tutorial 1
* surviving Tutorial 2
* getting completely lost in Tutorial 3

⠀
# Traditional Tutorials vs tutorial-creator
| **Traditional Tutorials** | **tutorial-creator** |
|:-:|:-:|
| Toy examples | Your real codebase |
| Static curriculum | Adaptive progression |
| Generic vocabulary | Vocabulary from your project |
| No continuity | Persistent progress tracking |
| Assumes prerequisites | Detects missing concepts |
| Separate from production work | Integrated into active development |

# Example Workflow
### Your Swift File
###        ↓
### tutorial-creator
###        ↓
### Annotated Lesson
###        ↓
### Vocabulary Tracking
###        ↓
### Gap Analysis
###        ↓
### Progressive Fluency

# Usage
### # First run
### /skill tutorial-creator closures src/utils/helpers.ts

### # Additional tutorials
### /skill tutorial-creator protocols Sources/Protocols/BackupManaging.swift
### /skill tutorial-creator hooks src/components/Dashboard.tsx
### /skill tutorial-creator error-handling src/api/client.rs
If no source file is specified, the skill searches your project for a good example of the requested topic.

# First-Run Setup
On first use, the skill asks:
1. Where to save tutorials
2. Your language/framework
3. Your experience level
4. Your project directory

⠀Configuration is saved to:
### .claude/tutorial-config.yaml
Edit anytime to adjust progression or preferences.

# Supported Languages
Built-in learning progressions exist for:
| **Language** | **Progression** |
|:-:|:-:|
| **Swift / SwiftUI** | Utilities → Models → ViewModels → Views → Managers |
| **TypeScript / React** | Utilities → Hooks → Components → State Management |
| **Python / Django** | Utilities → Models → Views → Serializers |
| **Rust** | Ownership → Traits → Error Handling → Async |
Custom learning progressions can also be defined.

# Example Tutorial
A complete generated tutorial example is included here:
### ~skills/tutorial-creator/examples/Day3-ModelContextLogging-Annotated.md~
It demonstrates:
* vocabulary tracking
* annotated production Swift code
* testing
* progressive learning structure
* gap analysis

⠀
# prompter
# Improve prompts before Claude acts on them
Small prompt problems create surprisingly large downstream problems:
* ambiguity
* vague references
* overloaded requests
* unclear goals
* missing constraints

⠀prompter intercepts prompts before execution, rewrites them for clarity, then asks for approval before continuing.
Over time, this becomes a subtle feedback loop: you start internalizing what makes prompts effective simply by watching them improve.

# Usage
### /skill prompter
Activation modes:
* Current session only
* Persist via CLAUDE.md
* Remove persistent rewriting

⠀
# Example Rewrite
### Original
### fix dashboard thing maybe make it cleaner
### Rewritten
### Refactor the dashboard layout to improve visual hierarchy and reduce clutter.
### Preserve existing functionality and navigation behavior.
### Focus specifically on spacing, grouping, and discoverability of primary actions.

# Example Rewrites
A larger collection of example rewrites is available here:
### ~skills/prompter/examples/Prompter-Examples.md~

# Philosophy
Many AI coding tools optimize for:
* generation
* automation
* acceleration

⠀code-smarter focuses more heavily on:
* comprehension
* fluency
* workflow understanding
* architectural awareness
* long-term developer growth

⠀AI can generate code instantly.
Understanding it still takes time.
These skills are designed to help close that gap.

# Other Claude Code Skills
Additional repositories built during development of Stuffolio:
* ~[bug-echo](https://github.com/Terryc21/bug-echo)~ — after fixing a bug, locate and rate similar patterns elsewhere in the codebase
* ~[workflow-audit](https://github.com/Terryc21/workflow-audit)~ — multi-layer behavioral audit of SwiftUI user workflows
* ~[radar-suite](https://github.com/Terryc21/radar-suite)~ — behavioral audit suite for iOS/macOS Swift projects

⠀These tools focus on workflow behavior and user experience — not just static code inspection.

# Install
### git clone https://github.com/Terryc21/code-smarter.git

### # Global install
### cp -r code-smarter/skills/* ~/.claude/skills/

### # Project-specific install
### cp -r code-smarter/skills/* /path/to/project/.claude/skills/

# Author
Created by **Terry Nyberg** ~[Coffee & Code LLC](https://stuffolio.app/)~

# License
Apache 2.0 — see ~LICENSE~
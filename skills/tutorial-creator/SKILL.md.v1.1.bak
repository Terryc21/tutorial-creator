---
name: tutorial-creator
description: Generate annotated code reading tutorials from your own codebase -- builds incremental learning with vocabulary tracking, pre/post tests, and gap analysis
version: 1.1.0
author: Terry Nyberg, Coffee & Code LLC
license: Apache-2.0
---

# Create Tutorial

Generate annotated code reading tutorials using real code from your project. Each tutorial teaches one concept, tests comprehension, and tracks vocabulary across sessions.

## Usage

```
/skill tutorial-creator [topic] [source file or component]
```

**Examples:**
- `/skill tutorial-creator closures src/utils/helpers.ts`
- `/skill tutorial-creator optional chaining Sources/Models/User.swift`
- `/skill tutorial-creator hooks src/components/Dashboard.tsx`
- `/skill tutorial-creator ownership src/main.rs`

If no source file is given, find one in the project that best demonstrates the topic.

## First-Run Setup

On first invocation, check for `.claude/tutorial-config.yaml` in the project root. If it doesn't exist, run the setup wizard:

```
Welcome to tutorial-creator! Let's set up your learning environment.
```

Ask these questions using AskUserQuestion:

1. **Where should tutorials be saved?**
   Default: `./tutorials/`

2. **What language/framework are you learning?**
   Auto-detect from project files (package.json = JS/TS, Package.swift = Swift, Cargo.toml = Rust, etc.)
   Let user confirm or override.

3. **What's your experience level?**
   - Beginner (explain everything -- syntax, types, control flow)
   - Intermediate (skip basic syntax, focus on patterns and idioms)
   - Advanced (focus on architecture, gotchas, performance)

4. **What's your project directory?** (for finding real code examples)
   Default: current working directory

Save config to `.claude/tutorial-config.yaml`:

```yaml
tutorials_dir: ./tutorials/
language: swift
framework: swiftui
experience_level: intermediate
project_dir: .
next_day: 1
```

Create initial files:
- `{tutorials_dir}/VOCABULARY.md` -- cumulative term reference
- `{tutorials_dir}/PROGRESS.md` -- score tracker + concepts checklist

## Before Writing

1. **Read the config:** `.claude/tutorial-config.yaml`

2. **Read the progress tracker:** `{tutorials_dir}/PROGRESS.md`
   - Use the next available day number
   - Check which concepts have been covered -- don't re-explain unless building on them
   - Check the progression phase

3. **Read the vocabulary file:** `{tutorials_dir}/VOCABULARY.md`
   - Reference terms already defined
   - Only introduce genuinely new terms

4. **Read the source file** from the project to annotate

## Tutorial Format (Required Sections)

Every tutorial MUST include these sections in this order:

### Header
```markdown
# Day N: [Topic Title] -- [Subtitle]

*Source: `[file path]` ([scope description])*
*Day N -- [Date] -- [Phase name] (Phase N)*
```

### What You'll Learn
One or two sentences describing the concept in plain language.

### Vocabulary
| Term | Quick Definition |
New terms introduced in this tutorial only -- terms not covered by any earlier tutorial. Keep definitions to one line. End the vocabulary section with a link:
`> Full vocabulary list: [VOCABULARY.md](VOCABULARY.md)`

### Pre-Test
5-8 questions testing whether the reader already knows the concept BEFORE reading. Questions should be answerable from the vocabulary table alone -- they test intuition, not memorization.

### The Core Pattern
Explain the concept using simplified code examples BEFORE showing real project code. Start with the simplest version, then build up. Calibrate depth to the configured experience level.

### Real Code from [Your Project]
The actual source file, annotated with inline comments explaining each concept. Use `// <--` or `// ^^^` arrows to draw attention to key lines. Simplify the code if the full file is too long -- note what was removed.

### Common Mistakes
| Mistake | What happens | Fix |
3-5 common errors related to this concept.

### Post-Test
5-8 questions testing comprehension AFTER reading. Should be harder than pre-test -- require applying the concept, not just recalling definitions.

### Answer Key
Answers for both pre-test and post-test. Full explanations, not just "true/false".

### New Concepts Introduced
A summary table at the end listing the new concepts this tutorial taught, anchored to the file with line references where helpful. Format:

```markdown
| Concept | Where in Code | Key Takeaway |
|---------|---------------|--------------|
| [concept name] | [Line N or "throughout"] | [one-sentence summary] |
```

This table is the reader's quick-reference card after they finish the tutorial. It also feeds the Concepts Mastery Checklist update in PROGRESS.md (see "After Writing" below). Every concept in this table MUST also appear in the Vocabulary table at the top of the tutorial; new entries here without matching vocabulary entries are inconsistent.

The table should be derivable from the tutorial's content -- if a concept isn't taught well enough in the body to summarize in one sentence, either teach it better or remove it from the table. Aim for 6-12 rows depending on the tutorial's depth.

## After Writing

1. **Save the tutorial** to `{tutorials_dir}/DayN-[Topic]-Annotated.md`

2. **Update PROGRESS.md:**
   - Add a row to the Score Log table with the day number, date, file name, and test counts
   - Add new concepts to the Concepts Mastery Checklist under the appropriate phase. The concepts to add are the ones listed in the tutorial's "New Concepts Introduced" table -- format each as `- [ ] [Concept name] (Day N)`. The brief takeaway from the table can be omitted in PROGRESS.md; readers will follow the day reference back to the tutorial if they need more detail.

3. **Update VOCABULARY.md:**
   - Add a new section for this tutorial's terms (format: `## Day N: [Topic]` with vocabulary table)
   - Update the Cumulative Count table at the bottom
   - Only add terms that are genuinely new -- not repeats of earlier tutorials

4. **Update config:** Increment `next_day` in `.claude/tutorial-config.yaml`

5. **Gap analysis:** Review the tutorial you just wrote. If it uses concepts not covered by any earlier tutorial, propose gap-filling tutorials (numbered as N.5 between existing days) to bridge the prerequisite knowledge. List each proposed gap tutorial with its topic, which days it bridges, and why the gap matters. Ask whether to create them now or defer.

## Phase Progression Defaults

The skill uses language-appropriate learning progressions:

**Swift/SwiftUI:**
1. Utilities (optionals, guard, closures, extensions)
2. Models (enums, structs, Codable, protocols)
3. ViewModels (@Observable, async/await, error handling)
4. Views (@State, @Binding, navigation, modifiers)
5. Managers (dependency injection, singletons, networking)
6. Serialization (Codable, JSON, backup/restore)

**TypeScript/React:**
1. Utilities (types, interfaces, generics, utility functions)
2. Hooks (useState, useEffect, useContext, custom hooks)
3. Components (props, children, composition, render patterns)
4. State Management (context, reducers, external stores)
5. API Layer (fetch, error handling, caching, optimistic updates)
6. Testing (unit tests, component tests, mocking)

**Python/Django:**
1. Utilities (types, decorators, generators, context managers)
2. Models (ORM, migrations, relationships, managers)
3. Views (class-based, function-based, mixins, permissions)
4. Serializers (DRF, validation, nested serialization)
5. Middleware (request/response processing, authentication)
6. Testing (pytest, fixtures, factories, mocking)

**Rust:**
1. Ownership (borrowing, lifetimes, moves, clones)
2. Traits (definition, implementation, trait objects, bounds)
3. Error Handling (Result, Option, ?, custom errors)
4. Async (tokio, futures, streams, channels)
5. Unsafe (raw pointers, FFI, transmute, when to use)
6. Architecture (modules, crates, workspace organization)

Custom progressions can be defined in the config file.

## Writing Style

- Use "you" -- speak directly to the reader
- Explain like a patient mentor, not a textbook
- Connect new concepts to ones already covered in previous days
- Use real code from the reader's project, not hypothetical examples
- Keep annotations conversational: "This line is doing X because Y"
- Calibrate explanation depth to the configured experience level:
  - **Beginner:** Explain syntax, name types, define every keyword
  - **Intermediate:** Skip basic syntax, focus on "why this pattern" and alternatives
  - **Advanced:** Focus on tradeoffs, edge cases, performance implications

## PROGRESS.md Template

Created on first run:

```markdown
# Code Reading -- Progress Tracker

**Started:** [date]
**Goal:** Read one annotated file per session, building from simple to complex.

## Progression Path

| Phase | Focus | Files |
|-------|-------|-------|
| 1 | [Phase 1 name] | |
| 2 | [Phase 2 name] | |
| 3 | [Phase 3 name] | |

## Score Log

| Day | Date | File | Pre-Test | Post-Test | Delta | Concepts to Revisit |
|-----|------|------|----------|-----------|-------|---------------------|
| 1 | | | / | / | | |

## Scoring Guide

- **7-8 correct:** You've got this concept down. Move on.
- **5-6 correct:** Good foundation. Review the missed questions.
- **3-4 correct:** Re-read the annotated sections for missed concepts.
- **0-2 correct:** Spend extra time on this file. Try writing similar code from scratch.

## Concepts Mastery Checklist

Check off when you feel confident (not just "saw it once"):

### Phase 1: [Phase name]
- [ ] (populated as tutorials are created)
```

## VOCABULARY.md Template

Created on first run:

```markdown
# Tutorial Vocabulary

Terms introduced in each tutorial, in order of appearance.

---

(Sections added as tutorials are created)

---

## Cumulative Count

| Day | New Terms | Running Total |
|-----|-----------|---------------|

---

*Updated: [date]*
```

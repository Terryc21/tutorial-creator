# Using tutorial-creator

Every command, setting, and option. If you just want to try the skill, the
[README](README.md) is enough — start there and come back when you need a detail.

**Contents**

- [Commands](#commands)
- [Picking where a lesson starts](#picking-where-a-lesson-starts)
- [Vocabulary](#vocabulary)
- [Your learning dashboard](#your-learning-dashboard)
- [Writing for other people](#writing-for-other-people)
- [First-time setup](#first-time-setup)
- [Working across several projects](#working-across-several-projects)
- [Undoing things](#undoing-things)
- [Languages](#languages)
- [Upgrading from version 1.1](#upgrading-from-version-11)

---

## Commands

Type `/skill tutorial-creator` on its own and the skill asks what you want. Everything
below is a shortcut for people who already know.

```
/skill tutorial-creator                        # ask me what I want to do
/skill tutorial-creator vocab review           # quiz me on words I've learned
/skill tutorial-creator vocab gap              # what am I getting wrong?
/skill tutorial-creator status                 # how am I doing overall?
/skill tutorial-creator --mode learn           # skip the menu, write me a lesson
/skill tutorial-creator --mode audience        # skip the menu, write for others
```

Working on more than one project:

```
/skill tutorial-creator open <path>            # remember this project
/skill tutorial-creator open                   # list projects, pick a default
/skill tutorial-creator forget <path>          # stop remembering one
/skill tutorial-creator --project-dir <path>   # use this project, just this once
```

The old version 1.1 form still works and behaves like choosing "topic + file":

```
/skill tutorial-creator [topic] [file]
```

### By what you want to do

| I want to… | Type this |
|---|---|
| Be walked through the choices | `/skill tutorial-creator` |
| Write about a topic in a file I've picked | `/skill tutorial-creator <topic> <file>` |
| Write about a topic, let the skill find the file | `--mode learn`, then pick **[c]** |
| Write about a word I keep getting wrong | `--mode learn`, then pick **[e]** |
| Turn a file into an article for other people | `--mode audience` |
| Be quizzed on what I've learned | `vocab review` |
| Pull several words in from a source, not one at a time | `vocab ingest <source>` |
| Get flashcards — Markdown, Anki, or print — from my vocabulary | `vocab flashcards` |
| See what I'm confused about | `vocab gap` |
| See my overall progress | `status` |
| Work on a different project than the folder I'm in | `--project-dir <path>` |

---

## Picking where a lesson starts

You don't need a topic and a file ready. Pick whichever of these matches your situation.

| Start from | Pick this when |
|---|---|
| **[a] What's next for me** | You want the next thing in your learning sequence |
| **[b] A topic and a file** | You know both already |
| **[c] Just a topic** | You know the topic; let the skill find a good file |
| **[d] A question** | You're stuck ("why does my fetch return nothing?") |
| **[e] Something I'm confused about** | Show me what I keep getting wrong, and teach that |
| **[f] Notes I've collected** | A doc, post, video, or past session you want to pull together |

**How [c] picks a file.** It looks for a file that teaches well, not the file with the
most examples — a short file with two clear cases beats a long one with twelve scattered
through it. You see the candidates and choose. If nothing in your project is a decent
example, the skill says so and offers to write a small made-up one instead of quietly
settling for a bad file.

**How [d] handles a vague question.** If your question could mean two things, the skill
asks which one you meant rather than guessing and writing the wrong lesson.

**How [e] uses your mistakes.** It reads the words you've been getting wrong and builds
the lesson around one of them. The opening quiz targets the exact part you've been
missing.

---

## Vocabulary

The skill keeps a list of terms you've met, and how well you know each one.

| Command | What it does |
|---|---|
| `vocab add <term>` | Add a word you ran into anywhere. The skill drafts a definition and a real example; you fix it or accept it. |
| `vocab ingest <source>` | Pull several words at once — from a URL, a file, or this conversation. The skill finds the candidates, drafts each one, and adds whichever you pick in one go. |
| `vocab review` | Quiz on 5 terms, favouring ones you're shaky on. You write the definition from memory. |
| `vocab gap` | The terms you keep missing, worst first. |
| `vocab list --status=confused` | Filter by how well you know things. |
| `vocab list --source=<match> --date=<date>` | Filter by where a word came from, or when you added it. Combine with `--status` and each other. |
| `vocab flashcards` | Turn your vocabulary into flashcards — Markdown, an Anki deck, or a print-ready PDF. Takes the same `--source`, `--date`, and `--status` filters as `vocab list`. |
| `vocab merge <a> <b>` | Two entries for the same idea become one, keeping your quiz history. |

### How a word's status changes

Four states: **new → reviewing → mastered**, with **confused** for ones giving you
trouble.

**You don't set these yourself — you earn them by taking the quiz.** Three correct
answers in a row gets you to mastered. Two wrong or partial out of your last three drops
you to confused.

The one thing you *can* change by hand is mastered back to reviewing, for when you
realise you've forgotten something. Getting back to mastered means earning it again.

> **Why it works this way:** marking your own understanding is the thing people are
> worst at judging. A word you *feel* solid on and a word you *can define from memory*
> are different, and only the second one is measurable.

### Pulling words in from outside your project

`vocab ingest` reads whatever you point it at — a session, a URL, a file, or text you
paste in — and finds the words and phrases worth keeping. It shows you what it found
before adding anything, drafts a definition and a real example for each one, and you
accept, edit, or drop them as a group. Nothing gets added silently.

This is different from `vocab add`: `add` is one word you already have in mind; `ingest`
is "here's a source, find what's in it."

### Studying without the quiz

`vocab review` is graded — the skill checks your answer against the real definition.
`vocab flashcards` skips that: it exports your words so you can study however you want.

- **Markdown** — plain text, front and back, readable anywhere.
- **Anki deck (`.apkg`)** — import it into Anki and let its own spaced-repetition
  scheduling take over.
- **Print** — a PDF laid out for two-sided printing. Cut along the guides and each
  card's word lines up with its definition on the back. The skill asks how your printer
  handles two-sided pages before generating it, since guessing wrong misaligns every
  card — print one test page before you commit a full deck to paper.

None of the three feed back into your quiz history. They're a read of your vocabulary,
not a learning event — `vocab review`'s grading stays the only thing that moves a word
toward mastered.

---

## Your learning dashboard

`/skill tutorial-creator status` is read-only — it changes nothing, it just shows you:

- Lessons written, the last one, your streak, what to do next
- How many words are in each state
- Words you haven't been quizzed on in over two weeks
- Your top few problem words
- A suggested next lesson, based on both your gaps and your sequence

---

## Writing for other people

The second path on the main menu is for publishing what you've learned rather than
learning it.

**Start from** one of: a file in your project, something that went wrong and you want to
write about, a small made-up example, someone else's public code, or official
documentation.

**Then four questions** shape the result:

1. **Who's reading?** Beginner, intermediate, senior, or mixed. Beginners get more setup
   and definitions; senior readers get tradeoffs and alternatives.
2. **Say what it doesn't cover?** Yes adds a section naming the limits of what you wrote.
3. **How long?** Small, medium, large, or extra — each venue has its own word targets.
4. **Where's it going?** Picks the writing style.

| Publishing to | Reads like |
|---|---|
| `reddit` | Punchy, first person, one code block, "Edit:" for follow-ups |
| `book-chapter` | Long paragraphs, essay style, code supporting the prose |
| `apple-developer-article` | Reference documentation, lots of code, no "I" |
| `medium` | Magazine essay, strong opening, light on headings |
| `blog` | Personal and conversational, dated, code where the story needs it |
| `repo-doc` | Terse README or runbook, summary first, minimal prose |

---

## First-time setup

The first time you run it, the skill asks five things:

1. Which project folder to use (defaults to where you are)
2. Where inside it to save lessons
3. Your language and framework (it guesses; you confirm)
4. How experienced you are
5. Which code you're learning from, if that's a different folder

Your answers go in `.claude/tutorial-config.yaml`. Edit it any time.

One thing to know: that file goes **in the project folder you chose**, which isn't
necessarily the folder you were sitting in when you ran the command. The skill then
offers to remember the project so you can run it from anywhere.

---

## Working across several projects

The skill finds your project the way `git` finds a repository: it looks in the current
folder, then the folder above it, and so on up.

If that finds nothing, it checks the projects you've told it to remember
(`~/.claude/tutorial-creator/registry.yaml`). One project, it uses that. Several, it
asks. None, it offers to set one up.

To skip all of that for a single command, use `--project-dir <path>`.

Full details of the search order live in `SKILL.md`, under "Project resolution."

### Starting fresh vs. building on what you've done

**By default the skill remembers everything.** Before writing a new lesson it reads your
progress, your vocabulary, and your earlier lessons. That's the whole point — lesson 16
knows what lessons 1 through 15 covered, and afterwards it checks whether the new lesson
depended on anything you were never taught.

Two ways to opt out:

- **Start over completely:** delete or rename `.claude/tutorial-config.yaml`,
  `PROGRESS.md`, and `vocabulary.yaml`. The skill treats the project as brand new.
- **Just this one lesson:** starts **[b]**, **[c]**, and **[f]** can write a standalone
  lesson. They still record the results afterwards, they just don't let your history
  constrain what they write.

---

## Undoing things

| Command | Undoes |
|---|---|
| `undo` | The last lesson it wrote |
| `vocab undo` | A vocabulary change, up to 24 hours after |
| `renumber <old> <new>` | Renumbers a lesson and fixes every reference to it |

Every lesson it writes is logged, and the four files it changes are backed up first, so
`undo` is a clean revert rather than a guess.

---

## Languages

| Language | Order it teaches in |
|---|---|
| **Swift / SwiftUI** | Utilities → Models → ViewModels → Views → Managers → Serialization |
| **TypeScript / React** | Utilities → Hooks → Components → State → API → Testing |
| **Python / Django** | Utilities → Models → Views → Serializers → Middleware → Testing |
| **Rust** | Ownership → Traits → Error handling → Async → Unsafe → Architecture |

Swift is the most developed — the bundled examples and the demo project are Swift. The
other three have working sequences, but the examples you can read are Swift only.

To teach in a different order, set `progression_override` in
`.claude/tutorial-config.yaml`.

---

## Upgrading from version 1.1

If you used version 1.1 and have a `VOCABULARY.md`, run this once:

```
/skill tutorial-creator vocab regen-md --import
```

It converts your old file into the newer `vocabulary.yaml`. Imported words start at
`reviewing`, since there's no quiz history for them yet. From there, `vocab edit` to
adjust, `vocab merge` to combine duplicates, and `vocab review` to start earning
mastered.

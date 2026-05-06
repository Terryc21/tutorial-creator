# Day 3: ScoutResultsLookupView.swift

*Source: `Sources/Features/StuffScout/ScoutResultsLookupView.swift`*
*Day 3 -- March 25, 2026 -- Your First SwiftUI View*

> [!NOTE]
> This is a **sample tutorial output** demonstrating what `tutorial-creator` produces. The real skill writes one of these from your own project's source code. The example below uses a real file from [Stuffolio](https://stuffolio.app), the source project the skill was extracted from.

---

## Vocabulary

| Term | Quick Definition |
|------|-----------------|
| `struct ... : View` | Every SwiftUI screen is a struct conforming to View |
| `body` | Required property — what appears on screen |
| `some View` | "Returns a View but I won't say which type" |
| `@Environment` | Read system/parent values (dismiss, modelContext) |
| `@Query` | Auto-fetch + auto-watch database records |
| key path (`\Type.prop`) | Points to a property — used in sorting, predicates |
| `NavigationStack` | Container providing nav bar, title, toolbar |
| `Group` | Invisible container — apply modifiers to alternatives |
| `#if os(iOS)` | Compile-time platform check — code doesn't exist on other platform |
| `.toolbar` | Add buttons to the navigation bar |
| `ToolbarItem(placement:)` | Semantic button placement (`.cancellationAction`, `.confirmationAction`) |
| `ContentUnavailableView` | Built-in empty state (iOS 17+) — icon, title, description |
| `dismiss()` | Close the current sheet/modal |
| `#Preview` | Define an Xcode canvas preview |
| `.modelContainer(inMemory:)` | Temporary database for previews |

---

## Pre-Test

Answer these before reading the annotated code.

1. What is `@Environment(\.dismiss)` and when would you use it?
2. What is the difference between `@Query` and a regular array property?
3. What does `NavigationStack` do?
4. What is a `Group` in SwiftUI?
5. What does `#if os(iOS)` mean?
6. What is `ContentUnavailableView` for?
7. What does `.toolbar` do?

---

## What This File Does (Big Picture)

When a user taps "View Scout Results" on an item, the app needs to find and display the Stuff Scout research that was done when the item was added. This view:

1. Takes a session ID (a UUID)
2. Searches two different databases (recent scans and bookmarks) for a match
3. Shows the results if found, or an explanation if not

It's a **lookup view** — it doesn't create data, it finds and displays it.

---

## Lines 11-12: Imports

```swift
import SwiftUI
import SwiftData
```

Two imports because this view does two things: display UI (SwiftUI) and read from the database (SwiftData). If a file only shows UI with no database access, it only needs `import SwiftUI`.

---

## Line 14: `@available(iOS 17.0, macOS 14.0, *)`

This line tells the compiler: "This code requires iOS 17+ or macOS 14+." The `*` means "and any future platforms at any version." SwiftData was introduced in iOS 17, so any file using `@Query` or `@Model` needs this.

You'll see this on most files in Stuffolio. It's not something you write every time — once your app's minimum deployment target is iOS 17+, Xcode adds it where needed.

---

## Line 15: `struct ScoutResultsLookupView: View`

Every screen in SwiftUI is a **struct** that conforms to the **View** protocol. The `View` protocol requires exactly one thing: a `body` property.

You saw structs and protocols in Days 1-2. The new concept here: a struct *is* the screen. There's no separate "view controller" — the struct itself defines what appears on screen.

---

## Lines 16-17: Environment Properties

```swift
@Environment(\.modelContext) private var modelContext
@Environment(\.dismiss) private var dismiss
```

`@Environment` reads values provided by the system or parent views. Think of it as "ask the app for something" instead of "store something yourself."

- **`\.modelContext`** — The database workspace. Needed for any SwiftData operations. This view doesn't use it directly, but it's available if needed.
- **`\.dismiss`** — A function the system gives you to close this view. When the user taps "Done", `dismiss()` slides the sheet away. You don't need to know *how* dismissal works — just call it.

**Why `private`?** These are internal implementation details. No parent view needs to know this view uses dismiss.

---

## Line 19: The Input

```swift
let scoutSessionId: UUID?
```

This is the one piece of data the view needs from outside — a UUID that identifies which Scout session to look up. It's optional (`UUID?`) because some items weren't added via Stuff Scout and have no session ID.

**`let` not `var`** — the session ID never changes after the view is created. The parent view sets it once.

---

## Lines 22-26: @Query — The Database Reads

```swift
@Query(sort: \ScoutRecentScan.scannedAt, order: .reverse)
private var recentScans: [ScoutRecentScan]

@Query(sort: \ScoutBookmark.createdAt, order: .reverse)
private var bookmarks: [ScoutBookmark]
```

This is the biggest new concept in Day 3. `@Query` does three things automatically:

1. **Fetches** all records of that type from the database
2. **Sorts** them (here by date, newest first)
3. **Watches** for changes — if a record is added or deleted, the view updates automatically

The `\ScoutRecentScan.scannedAt` syntax is a **key path** — it points to a specific property on a type. Read it as "the scannedAt property on ScoutRecentScan." The backslash `\` is Swift's key path syntax.

**Two queries, not one.** Scout results can live in two places (recent scans or bookmarks), so we query both and search them in `findSession()`.

**Why not query just the one we need?** `@Query` doesn't support "fetch where ID = X" directly with a variable. It fetches all records, then the code filters. For small collections (max 25 recent scans) this is fine.

---

## Lines 28-54: The Body — What Appears on Screen

```swift
var body: some View {
    NavigationStack {
        Group {
            if let session = findSession() {
                ScoutResultView(
                    session: session,
                    onSaveComplete: { dismiss() }
                )
            } else if scoutSessionId == nil {
                noSessionIdView
            } else {
                sessionNotFoundView
            }
        }
        .navigationTitle("Scout Results")
        #if os(iOS)
        .navigationBarTitleDisplayMode(.inline)
        #endif
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Done") {
                    dismiss()
                }
            }
        }
    }
}
```

Let's break this down layer by layer:

### NavigationStack (line 29)

Wraps the content in a navigation container. This gives you:
- A navigation bar at the top
- The ability to set a title (`.navigationTitle`)
- A place to put toolbar buttons (`.toolbar`)

### Group (line 30)

`Group` is an invisible container. It doesn't add any visual element — it just lets you apply modifiers to multiple views at once. Here, `.navigationTitle` and `.toolbar` apply to whichever of the three possible views is shown.

**Why not just use `VStack`?** VStack adds layout (stacking vertically). Group adds nothing visual — it's purely organizational.

### The if/else Chain (lines 31-40)

Three possible states, handled in order:

1. **Found it** — `if let session = findSession()` unwraps the result. If findSession() returns a ScoutSession (not nil), show it in ScoutResultView. The `onSaveComplete: { dismiss() }` is a **closure** — code that runs when the user saves from inside that view.

2. **No ID provided** — `scoutSessionId == nil` means the item wasn't added via Stuff Scout. Show a helpful explanation.

3. **ID exists but no match** — The session was probably cleaned up. Show an explanation with guidance on bookmarking.

This is a common SwiftUI pattern: the body handles every possible state. No state is left unhandled.

### Platform-Specific Code (lines 43-45)

```swift
#if os(iOS)
.navigationBarTitleDisplayMode(.inline)
#endif
```

`.inline` makes the title small (in the bar) instead of large. This modifier only exists on iOS — macOS doesn't have this concept. `#if os(iOS)` makes the compiler skip this line entirely on macOS. It's not a runtime check — the code literally doesn't exist in the macOS build.

### Toolbar (lines 46-52)

```swift
.toolbar {
    ToolbarItem(placement: .cancellationAction) {
        Button("Done") {
            dismiss()
        }
    }
}
```

`.toolbar` adds buttons to the navigation bar. `placement: .cancellationAction` puts the button in the standard "cancel/close" position (leading side on iOS, varies by platform). The system decides exactly where — you just say what *kind* of action it is.

---

## Lines 58-72: findSession() — The Logic

```swift
private func findSession() -> ScoutSession? {
    guard let targetId = scoutSessionId else { return nil }

    if let recentScan = recentScans.first(where: { $0.scanId == targetId }) {
        return recentScan.toSession()
    }

    if let bookmark = bookmarks.first(where: { $0.bookmarkId == targetId }) {
        return bookmark.toSession()
    }

    return nil
}
```

This function searches two collections for a matching ID. You've seen all these patterns before:

- **`guard let`** — Day 1. If scoutSessionId is nil, stop early.
- **`.first(where:)`** — Day 1 vocabulary. Find the first element matching a condition.
- **`$0`** — Day 1. Shorthand for the first parameter in the closure.
- **`.toSession()`** — A method on ScoutRecentScan/ScoutBookmark that converts to a common ScoutSession type. This is a **bridge** pattern — two different types converted to one shared type so ScoutResultView can work with either.

The search order matters: recent scans first (more common), bookmarks as fallback.

---

## Lines 76-98: Computed View Properties

```swift
private var noSessionIdView: some View {
    ContentUnavailableView(
        "No Scout Data",
        systemImage: "sparkle.magnifyingglass",
        description: Text("This item wasn't added via Stuff Scout.")
    )
}
```

These are **computed properties** (Day 1) that return views. They break the body into named, readable pieces instead of one giant if/else.

`ContentUnavailableView` is a built-in SwiftUI view (iOS 17+) for "nothing to show" states. It renders a centered icon, title, and description — the standard iOS empty state pattern. You give it a title, an SF Symbol name, and a description.

The second one (`sessionNotFoundView`) nests a `ContentUnavailableView` inside a `VStack` and adds an extra `Text` below it. Notice the modifiers chained on that Text:

```swift
.font(.caption)              // Small text
.foregroundStyle(.secondary) // Gray, deemphasized
.multilineTextAlignment(.center)
.padding(.horizontal)        // Space on left/right edges
```

Each modifier returns a new modified view. They chain naturally — read top to bottom.

---

## Lines 101-104: Preview

```swift
#Preview {
    ScoutResultsLookupView(scoutSessionId: UUID())
        .modelContainer(for: [ScoutRecentScan.self, ScoutBookmark.self], inMemory: true)
}
```

The preview creates the view with a random UUID (which won't match anything, so you'll see the "not found" state). `.modelContainer(... inMemory: true)` creates a temporary database that exists only in the preview — no real data is touched.

---

## Post-Test

1. What is the difference between `@State` and `@Query`?
2. Why does this view use `Group` instead of `VStack`?
3. What would happen if you removed the `#if os(iOS)` check around `.navigationBarTitleDisplayMode(.inline)`?
4. This view has two `@Query` properties. Could you combine them into one? Why or why not?
5. Why is `findSession()` a function and not a computed property?
6. What does `placement: .cancellationAction` do — and why not just use `.leading`?
7. How does `dismiss()` know which sheet to close?

---

## Post-Test Answers

1. **@State** holds data the view *owns and creates*. **@Query** holds data from the *database*. @State is for UI state (is a sheet showing?). @Query is for persistent data (what items exist?). Both trigger view updates when they change.

2. **Group** adds no layout. If this used VStack, the three possible views would stack on top of each other (though only one shows at a time due to the if/else, so it wouldn't matter visually). Group is more correct semantically — it says "these are alternatives, not stacked items."

3. **The macOS build would fail to compile.** `.navigationBarTitleDisplayMode` doesn't exist on macOS — it's an iOS-only API. The `#if os(iOS)` check prevents the compiler from even seeing that line on macOS.

4. **No.** ScoutRecentScan and ScoutBookmark are different `@Model` types stored in different database tables. `@Query` fetches one type at a time. You'd need a shared protocol or manual fetching to combine them.

5. **Either would work.** A computed property (`var session: ScoutSession?`) would be called every time the body is evaluated. A function makes the "I'm doing a search" intent clearer. In practice, SwiftUI may call the body multiple times per second during animations, so the distinction matters for expensive operations — but this search over 25 items is trivial.

6. **`.cancellationAction` is semantic**, not positional. It tells the system "this is a dismiss/cancel button" and the system places it in the correct position per platform and context. `.leading` would always put it on the left, which might be wrong in some contexts (like right-to-left languages). Use semantic placements — let the system handle positioning.

7. **`dismiss()` uses the environment.** When a view is presented as a sheet, SwiftUI sets up the `\.dismiss` environment value to close *that specific sheet*. The view doesn't need to know — it just calls `dismiss()` and the system handles it. This is why `@Environment` is powerful — views don't need to know about their presentation context.

---

## New Concepts Introduced in Day 3

| Concept | Where in Code | Key Takeaway |
|---------|--------------|--------------|
| struct as a View | Line 15 | Every screen is a struct conforming to View |
| @Environment | Lines 16-17 | Ask the system for values (dismiss, modelContext) |
| @Query | Lines 22-26 | Auto-fetch + auto-update from the database |
| Key paths (`\Type.property`) | Lines 22, 25 | Point to a property on a type — used in sorting, predicates |
| NavigationStack | Line 29 | Container that provides nav bar, title, toolbar |
| Group | Line 30 | Invisible container — apply modifiers to multiple views |
| `if let` in body | Line 31 | Conditional views based on optional values |
| `#if os(iOS)` | Line 43 | Compile-time platform check — code doesn't exist on other platforms |
| .toolbar + ToolbarItem | Lines 46-52 | Add buttons to the navigation bar with semantic placement |
| ContentUnavailableView | Lines 77, 86 | Built-in empty state view (iOS 17+) |
| Computed view properties | Lines 76, 84 | Break body into named pieces for readability |
| #Preview with modelContainer | Lines 101-104 | Preview with a temporary in-memory database |

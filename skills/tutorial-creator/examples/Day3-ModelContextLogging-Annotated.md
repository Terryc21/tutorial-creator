# Day 3: Wrapping Throws with Logging — Why a Tiny Extension Pays for Itself

*Source: `Sources/Utilities/Extensions/ModelContext+Logging.swift` (full file, 75 lines)*
*Day 3 — 2026-05-03 — Utilities (Phase 1)*

> [!NOTE]
> This is a **sample tutorial output** demonstrating what `tutorial-creator` produces. The real skill writes one of these from your own project's source code. The example below uses a real file from [Stuffolio](https://stuffolio.app), the source project the skill was extracted from.

## What You'll Learn

How to replace silent `try?` calls with a wrapper that logs failures and returns a sensible default — and why that small change makes you safer in production. Along the way: Swift extensions, `do/catch` with annotated source location, generics constrained to a protocol, and `@discardableResult`.

## Vocabulary

| Term | Quick Definition |
|---|---|
| **extension** | Adds methods or properties to an existing type without modifying the original definition. |
| **do/catch** | Swift's structured error handling. `do` runs code that can throw; `catch` handles the error. |
| **try?** | Tries an operation. If it throws, returns `nil` and silently discards the error. Convenient and dangerous. |
| **`@discardableResult`** | Attribute that lets the caller ignore the return value without compiler warning. |
| **`@MainActor`** | Marks a function that must run on the main thread. Used for UI work like haptics and toasts. |
| **`StaticString`** | A string that's known at compile time. Used by `#file` and `#function` to avoid heap allocations. |
| **`#file` / `#line`** | Compiler-injected literals: filename and line number where the call site lives. Auto-filled. |
| **generic constraint (`<T: P>`)** | Generic type parameter that must conform to protocol `P`. Lets one method work on many concrete types. |
| **`PersistentModel`** | SwiftData protocol marking types stored in a `ModelContainer`. The base for `@Model` classes. |
| **`FetchDescriptor`** | SwiftData query object describing what to fetch (predicate, sort, fetch limit). |

> Full vocabulary list: [VOCABULARY.md](../VOCABULARY.md)

## Pre-Test

Answer from intuition before reading the rest. Write down your answers; you'll grade them at the end.

1. What does `try?` return when the operation throws an error?
2. If a save fails inside a `try?` call, where does the error go?
3. What's the difference between a function declared `func save()` and one declared `func save() throws`?
4. Why might you write a function as a wrapper around another function that does almost the same thing?
5. What does `@discardableResult` mean for the caller?
6. If a function has parameters `file: StaticString = #file, line: UInt = #line`, what value does the compiler put there at the call site?
7. In `func fetchWithLogging<T: PersistentModel>(...)`, what does `T: PersistentModel` constrain?
8. What does `(try? fetch(descriptor)) ?? []` evaluate to if the fetch throws?

## The Core Pattern

The pattern is: **wrap a throwing operation in a function that converts the failure mode to one you actually want**.

The simplest version. Suppose you have a function that can throw:

```swift
func dangerousOperation() throws -> String {
    // might fail
}
```

You can call it three ways:

```swift
// Option A: propagate the error upward
let result = try dangerousOperation()  // calling function must throw or be in do/catch

// Option B: silently swallow with try?
let result = try? dangerousOperation()  // returns String? — nil on failure, no record of why

// Option C: catch and decide what to do
do {
    let result = try dangerousOperation()
    // use result
} catch {
    // log, fall back, retry, or rethrow
}
```

Option B is the easiest to write and the most dangerous. Failures vanish. Six months later you're staring at a screen with no items on it, and there's no way to know whether the user has no items or whether the fetch failed.

The wrapper pattern turns Option C into a one-liner the rest of the codebase can call. **The wrapper does the do/catch once; every caller benefits.** That's what `ModelContext+Logging.swift` does for every SwiftData `save()` and `fetch()` in the project.

## Real Code from Stuffolio

```swift
//
//  ModelContext+Logging.swift
//  Stuffolio
//
//  Extension replacing silent try? context.save() calls with logged saves.
//  Use saveWithLogging() instead of try? save() so errors surface in Sentry.
//

import SwiftData

@available(iOS 17.0, macOS 14.0, *)  // <-- annotation: this code requires SwiftData,
                                     //     which only ships in iOS 17 / macOS 14 and later.
                                     //     Compiler refuses to call this from older targets.
extension ModelContext {              // <-- extension: we're adding methods to SwiftData's
                                     //     existing ModelContext type. Original Apple
                                     //     definition is untouched.

    /// Saves the context and logs any error via SFLogger.
    ///
    /// Use instead of `try? save()` so save failures are visible in crash reports.
    /// Returns `true` on success, `false` on failure. Callers that need error
    /// propagation should use `try save()` directly.
    @discardableResult                 // <-- @discardableResult: callers can write
                                       //     `context.saveWithLogging()` without using the Bool
                                       //     return. Without this, the compiler warns about
                                       //     the unused result.
    func saveWithLogging(
        file: StaticString = #file,    // <-- StaticString = #file: when you call
        line: UInt = #line             //     saveWithLogging(), the compiler auto-fills
    ) -> Bool {                        //     the path of the calling file and line number.
                                       //     You don't pass them; they show up for free.
        do {
            try save()                 // <-- the actual throwing call. If save() succeeds,
                                       //     control flows to `return true`. If it throws,
                                       //     control jumps to `catch`.
            return true
        } catch {                      // <-- catch with no pattern: binds the error to a
                                       //     local constant named `error` automatically.
            SFLogger.general.error(
                "ModelContext save failed [\(file):\(line)]: \(error)"
            )                          // ^^ the failure no longer vanishes. SFLogger sends
                                       //    this to Sentry; on next session, an engineer
                                       //    sees exactly which save call site failed and why.
            return false
        }
    }

    /// Saves the context, shows success haptic + toast on success,
    /// or error haptic + toast on failure.
    ///
    /// Use for user-initiated saves where feedback is expected.
    @MainActor                         // <-- @MainActor: this function must run on the main
                                       //     thread. Required because HapticManager and
                                       //     ToastManager update UI.
    func saveWithFeedback(
        successMessage: String = "Saved",
        file: StaticString = #file,
        line: UInt = #line
    ) {
        if saveWithLogging(file: file, line: line) {  // <-- composition: builds on the wrapper
                                                      //     above. saveWithFeedback doesn't
                                                      //     re-implement the do/catch; it just
                                                      //     adds UI feedback on top.
            HapticManager.shared.success()
            ToastManager.shared.success(successMessage)
        } else {
            HapticManager.shared.error()
            ToastManager.shared.error("Save failed. Please try again.")
        }
    }

    /// Fetches models and logs any error via SFLogger.
    ///
    /// Use instead of `(try? fetch(descriptor)) ?? []` so fetch failures surface in Sentry.
    /// Returns an empty array on failure rather than throwing.
    func fetchWithLogging<T: PersistentModel>(           // <-- generic with constraint:
                                                         //     T must conform to PersistentModel
                                                         //     (the SwiftData protocol all @Model
                                                         //     types adopt). One method, but it
                                                         //     works for Item, Tag, RMARecord,
                                                         //     anything @Model.
        _ descriptor: FetchDescriptor<T>,                // <-- the underscore makes the first
                                                         //     argument unlabeled at call site.
                                                         //     You write fetchWithLogging(d), not
                                                         //     fetchWithLogging(descriptor: d).
        file: StaticString = #file,
        line: UInt = #line
    ) -> [T] {
        do {
            return try fetch(descriptor)
        } catch {
            SFLogger.general.error(
                "ModelContext fetch failed [\(file):\(line)]: \(error)"
            )
            return []                                    // <-- design choice: empty array, not
                                                         //     nil. Callers iterate over [T];
                                                         //     forEach over empty array is a
                                                         //     no-op. Returning nil would force
                                                         //     every caller to unwrap.
        }
    }

    /// Fetches a count and logs any error via SFLogger.
    func fetchCountWithLogging<T: PersistentModel>(
        _ descriptor: FetchDescriptor<T>,
        file: StaticString = #file,
        line: UInt = #line
    ) -> Int {
        do {
            return try fetchCount(descriptor)
        } catch {
            SFLogger.general.error(
                "ModelContext fetchCount failed [\(file):\(line)]: \(error)"
            )
            return 0                                     // <-- same idea: 0 is the safe default.
                                                         //     Caller showing "items: \(count)"
                                                         //     just shows zero rather than
                                                         //     crashing on a force-unwrapped nil.
        }
    }
}
```

**Whole-file shape**: one extension, four methods, each with the same shape: `do { try realCall() } catch { SFLogger.error("..."); return safeDefault }`. The pattern is repetitive on purpose — once you read one, you've read them all. Repetition is the point.

## Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| Using `try?` because the linter doesn't warn | Errors silently disappear; users see empty screens with no log trace | Replace with the corresponding `*WithLogging` wrapper. The grep is `try? context.save\|try? context.fetch`. |
| Forgetting `@MainActor` on `saveWithFeedback` | Compiles fine; crashes at runtime when called from a background thread because `HapticManager.shared.success()` touches UIKit | Always mark functions that touch UI with `@MainActor`. |
| Logging `\(error)` and assuming it's enough | Without `#file`/`#line`, the log shows which line of `saveWithLogging` logged the error — not which caller invoked it | Always include `\(file):\(line)` so the log points to the *caller*, not the wrapper. |
| Returning `nil` instead of `[]` from `fetchWithLogging` | Every caller has to write `if let items = ... else { items = [] }` | Return the empty default. The whole point of the wrapper is to absorb the error so the caller's code path stays simple. |
| Re-implementing do/catch at every call site | 200 copies of the same boilerplate; one of them inevitably forgets the log | Use the wrapper. The whole reason it exists is to centralize the failure handling. |

## Post-Test

After reading, try these. They should be harder than the pre-test — they ask you to apply the pattern, not just recite the definition.

1. You're calling `try? settings.save()` somewhere in your codebase. Why is the wrapper better, and what would the log line look like at the moment of failure?
2. Your team adds a new `@Model` class called `Receipt`. Without changing `fetchWithLogging`, how does it know what to do with a `FetchDescriptor<Receipt>`?
3. The `saveWithFeedback` method calls `saveWithLogging` rather than calling `save()` directly. Why might that be a deliberate choice rather than a shortcut?
4. Suppose `SFLogger.general.error()` itself were to throw. Would the catch block still return `false`, or would the error propagate? Walk through the control flow.
5. A junior teammate proposes adding `@discardableResult` to `fetchWithLogging`. Should you accept the change? Why or why not?
6. Where does the `#file` literal get evaluated — at the wrapper's definition or at the call site? Why does that matter?
7. The wrapper's design returns `[]` on fetch failure. Name a concrete situation where that choice is wrong, and propose what to do instead.
8. The four methods in this file all share a near-identical shape. Sketch what an even more general wrapper might look like that took a `() throws -> T` closure and a default value. What does the project lose by *not* doing that?

## Answer Key

### Pre-Test answers

1. **`try?` returns the optional form of the function's return type, with `nil` indicating failure.** If `dangerousOperation()` returns `String`, then `try? dangerousOperation()` returns `String?`. The error itself is silently discarded.

2. **The error goes nowhere.** It is not logged, not rethrown, and not stored. The caller has only `nil` to indicate something went wrong, with no diagnostic information.

3. **`func save() throws` declares that the function might throw an error; the caller must handle it (with `try`/`do-catch`/`try?`/`try!`).** A non-throwing `func save()` cannot fail in a recoverable way; if it can fail, the failure is by crash or by silent silencing inside.

4. **A wrapper centralizes a decision you'd otherwise repeat at every call site.** In this case: "what to do when the operation fails." Repeating that decision 200 times means 200 chances for one to be wrong, missed, or out of sync.

5. **It tells the caller the return value is optional to use.** Without `@discardableResult`, `let _ = context.saveWithLogging()` would compile but `context.saveWithLogging()` (no `let _ =`) would generate a warning. With it, both compile cleanly.

6. **The compiler injects the literal value at the call site, not at the wrapper's definition.** So if `saveWithLogging` is called from `Backup.swift:45`, the wrapper sees `file == "Backup.swift"`, `line == 45`. That's what makes the log line meaningful.

7. **`T` is constrained to types that conform to `PersistentModel`.** The body of the function can call any method declared on that protocol. Concrete types passed at call sites get checked at compile time: a non-conforming type produces a compile error.

8. **Empty array `[]`.** `try?` returns `nil` on throw, so `(try? fetch(d))` is `[T]?`. The `??` provides `[]` as the fallback, so the whole expression is `[T]`. The wrapper does the same thing but logs why.

### Post-Test answers

1. **The wrapper logs the failure to Sentry with the file and line of the *caller*, so on a crash report a developer can see exactly which save attempt failed.** A typical log line looks like: `ModelContext save failed [SettingsViewModel.swift:142]: ConstraintViolation(field: "email")`. With `try?`, the log is empty and no one knows the save failed at all — until users write in.

2. **`fetchWithLogging<T: PersistentModel>` works on `Receipt` automatically because Swift's generic system resolves `T` at compile time from the type of `descriptor`.** The new `Receipt` model adopts `PersistentModel` (via `@Model`), satisfies the constraint, and the compiler generates a specialized version of the function. No source change in `ModelContext+Logging.swift` needed.

3. **Composition over duplication.** If `saveWithFeedback` re-implemented `do { try save() } catch { ... }` directly, the next change to the wrapper (say, adding a Sentry breadcrumb) would have to be made twice. By calling `saveWithLogging`, the feedback method inherits every future improvement to logging for free.

4. **The catch block runs `SFLogger.general.error(...)` first, then `return false`.** If `SFLogger.general.error` itself threw — which it doesn't in this codebase, but if it did — the error would propagate out of the function because the catch block isn't inside another do/catch. The wrapper's signature returns `Bool`, not `Bool throws`, so a throw from inside catch would be a compile error in some configurations and a runtime trap in others. The point: catch handlers should themselves be defensive.

5. **Yes, accept the change.** `fetchWithLogging` returns `[T]`; callers that don't care about the result can already ignore the array (`_ = context.fetchWithLogging(d)` works without warning). But adding `@discardableResult` makes ignoring it intentional rather than awkward, matching `saveWithLogging`'s pattern. Consistency across the file is itself a reason.

6. **`#file` evaluates at the call site.** That's the whole magic. If it evaluated at the wrapper's definition, every log line would say "ModelContext+Logging.swift:30" — useless, since it always says that. Evaluation at the call site is what gives the log line diagnostic value.

7. **Empty array is wrong when callers depend on the distinction between "no data" and "fetch failed."** Example: a settings screen reading user accounts. Empty array = "user has no accounts yet" (correct UX: show empty-state with "create your first account" button). Fetch failure = "we couldn't read your accounts" (correct UX: show "we're having trouble loading your accounts; tap to retry"). Conflating them silently degrades trust. For those cases, prefer `Result<[T], Error>` or a separate `tryFetch` that throws and let the caller decide.

8. **A general wrapper would look like:**

   ```swift
   func runLogged<T>(
       default fallback: T,
       _ operation: () throws -> T,
       file: StaticString = #file,
       line: UInt = #line
   ) -> T {
       do { return try operation() }
       catch {
           SFLogger.general.error("Operation failed [\(file):\(line)]: \(error)")
           return fallback
       }
   }
   ```

   What the project loses by not doing this: **specificity at the call site**. `context.saveWithLogging()` reads as "this is a save; success or failure has known consequences." `context.runLogged(default: false) { try save() }` is more general but harder to scan for in a code review. The four named methods give the codebase four named operations; a general wrapper gives it one. For a file this small (75 lines), four named methods are clearer.

## Where to Go Next

This pattern — wrapping a throwing call in a function that converts failure to a sensible return — appears all over Stuffolio. Once you've read this file, look for `try?` in any view model or manager. Each one is a candidate for either using a wrapper that already exists or extracting one that doesn't.

The next tutorial in the Utilities phase will look at `Locale+Currency.swift`, where the same "wrap one tricky thing once" idea applies to currency formatting across regions.

---

*Tutorial generated by [tutorial-creator](https://github.com/Terryc21/code-smarter) on 2026-05-03. Source code from [Stuffolio](https://stuffolio.app), licensed Apache-2.0.*

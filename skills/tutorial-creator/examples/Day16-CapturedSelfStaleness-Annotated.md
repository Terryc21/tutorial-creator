# Day 16: Captured-Self Staleness -- Why Your SwiftUI Closure Reads the Wrong Value

*Source: `Sources/Features/StuffScout/StuffScoutView.swift` (lines 124-159, 242-260)*
*Day 16 -- May 6, 2026 -- Views & Navigation (Phase 3)*

> [!NOTE]
> This is a **sample tutorial output** demonstrating what `tutorial-creator` produces. The real skill writes one of these from your own project's source code. The example below uses a real file from [Stuffolio](https://stuffolio.app), the source project the skill was extracted from.

---

## What You'll Learn

When a closure inside a SwiftUI view's `body` references a stored property of the view, it doesn't grab the *current* value -- it grabs `self` and reads the property *later, when the closure runs*. On a view that re-renders, "later" can be against a `self` that's missing data. The fix is to snapshot the value into a body-local `let` before constructing the closure. This single trick prevents an entire class of macOS bug where the app's window vanishes for no apparent reason.

---

## Vocabulary

| Term | Quick Definition |
|------|-----------------|
| Captured `self` | When a closure references properties of the enclosing struct, Swift attaches a copy of `self` to the closure so it can read those properties later |
| Stale capture | A captured `self` whose values no longer match the live `self` -- the closure is reading from an outdated snapshot |
| Body-local `let` | A constant declared inside `var body` (or a builder scope) that captures a computed value at body-time |
| Eager resolution | Doing the computation NOW, before the closure is built, so the closure captures the result instead of `self` |
| Lazy resolution | Doing the computation LATER, inside the closure, when it actually runs -- this is what causes staleness |
| `??` operator | Nil-coalescing: `lhs ?? rhs` returns `lhs` if it's non-nil, otherwise `rhs`. The closure-literal RHS is constructed at the same time as the surrounding expression. |
| Re-render | When SwiftUI calls `body` again to recompute the view tree -- happens often, anytime watched state changes |
| Sibling bug | A bug in a different file or function that shares the exact same root cause as a known bug |

> Full vocabulary list: [VOCABULARY.md](VOCABULARY.md)

---

## Pre-Test

Test your intuition before reading. Answers at the bottom.

1. When you write `{ self.foo }` in Swift, when does Swift read the value of `foo` -- at the point you write the closure, or when the closure runs?

2. SwiftUI views are structs (value types). When SwiftUI re-renders, does it create a new struct instance or modify the existing one?

3. If a closure captures `self` from a struct, and that struct is later replaced by a different struct value, does the closure see the new struct or the old one?

4. In SwiftUI, calling `dismiss()` from `@Environment(\.dismiss)` always closes the parent sheet. True or false?

5. Why would you assign a closure expression to a `let` constant before passing it as a parameter, instead of passing the expression directly?

6. The expression `myOptional ?? { defaultAction() }` -- when is the `{ defaultAction() }` closure constructed? When it is *evaluated*?

7. If a SwiftUI view stores `var saveOverride: (() -> Void)? = nil` and the parent passes one in via a modifier, can the parent's value go missing across re-renders?

---

## The Core Pattern

### What is "captured self"?

In Swift, a closure can use values from outside itself. When those values come from `self` (the enclosing struct or class), Swift attaches a reference to `self` to the closure so it can find them.

```swift
struct Counter {
    var count: Int = 0

    func makePrinter() -> () -> Void {
        return {
            print(self.count)   // <-- this closure captures self
        }
    }
}
```

The closure doesn't bake in the current value of `count`. It bakes in `self`, and reads `self.count` whenever it runs.

For classes, that means the closure sees live changes to the instance. For **structs**, it's more subtle: when the closure was created, Swift copied the struct value (since structs are value types). The closure captures *that copy*. If the original is later mutated or replaced, the closure still references the old copy.

```swift
var counter = Counter()
let printer = counter.makePrinter()   // captures snapshot of counter
counter.count = 99                    // counter struct is replaced
printer()                             // prints 0, not 99
```

This is fine when you understand it. It's a footgun in SwiftUI, where you don't control when struct re-creation happens.

### Why SwiftUI makes this a footgun

SwiftUI views are structs. SwiftUI re-creates the struct *constantly*. Every time anything the view watches changes, SwiftUI:

1. Calls `body` on the current struct instance.
2. Diffs the result against last time.
3. Updates the displayed UI.
4. Often, the view struct is replaced wholesale with a fresh value.

If `body` constructed a closure that captures `self`, and that closure is stored somewhere (passed to a child view, attached to a Button), that closure holds onto the `self` that existed *when body ran*. Subsequent `body` calls produce new closures with new captured `self` values. SwiftUI usually picks up the latest one.

But sometimes it doesn't.

The S12 bug we'll annotate below is exactly that: an old closure with an old captured `self` outlives its render, and the old `self` is missing a stored property that the live `self` has set.

### The fix: eager vs lazy resolution

**Lazy** (broken):

```swift
ChildView(callback: optionalProp ?? { defaultAction() })
//                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//                  closure captures self -- reads optionalProp later
```

When the closure runs, it reads `self.optionalProp`. If captured `self` is stale (optionalProp was nil at the moment the closure was created), it falls through to `defaultAction()`.

**Eager** (fixed):

```swift
let resolved: () -> Void = optionalProp ?? { defaultAction() }
ChildView(callback: resolved)
```

The `??` evaluates *now*, at body-time. `resolved` holds the result. We pass `resolved` -- a captured *value*, not a captured `self`. The closure no longer touches `self`.

The fix is one extra line. The understanding of *why* takes hours.

---

## Real Code from Stuffolio

Here's the simplified file structure with the fix applied. The actual file has more code; what's shown is the part that demonstrates the pattern.

```swift
@available(iOS 17.0, macOS 14.0, *)
struct StuffScoutView: View {
    @Environment(\.dismiss) private var dismiss
    @State internal var viewModel: StuffScoutViewModel

    /// macOS inline override: when set, called instead of dismiss() after a successful save.
    /// Required because on macOS, StuffScoutView may be shown inline in NavigationSplitView
    /// (not as a sheet), where dismiss() closes the window rather than navigating away.
    var saveCompletionOverride: (() -> Void)? = nil
    // ^^^ Stored property. Optional. Set by the parent via a modifier (.overridingSaveCompletion).
    //     This is what becomes "stale" when captured.

    var dismissOverride: (() -> Void)? = nil
    // ^^^ Same shape, different purpose. Used by the Done button. Same bug class.

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    if let session = viewModel.currentSession, viewModel.showingResult {

                        // S12 fix: snapshot the override at body-time into a local.
                        // The previous form `onSaveComplete: saveCompletionOverride ?? { dismiss() }`
                        // evaluated lazily and captured `self`, which on SwiftUI re-renders could be
                        // stale (override = nil) -- causing the env dismiss to fire and close the
                        // macOS window when StuffScoutView was inline in NavigationSplitView.
                        // Resolving eagerly into a `let` captures the value, not `self`.
                        let resolvedOnSaveComplete: () -> Void = saveCompletionOverride ?? { dismiss() }
                        // ^^^ THIS LINE IS THE FIX.
                        //     `??` runs NOW, at body-time, against the LIVE self.
                        //     `resolvedOnSaveComplete` holds a closure VALUE, not a self-capture.

                        ScoutResultView(
                            session: session,
                            // ... other parameters ...
                            onSaveComplete: resolvedOnSaveComplete,
                            // ^^^ We pass the local. If the child stores it and calls it later,
                            //     it calls the closure we resolved now.
                        )
                    }
                }
            }
            .toolbar {
                // S12 sibling fix: same pattern, different property (dismissOverride),
                // same fix shape -- snapshot into a local before the Button action.
                let resolvedDismiss: () -> Void = dismissOverride ?? { dismiss() }
                // ^^^ Same trick at the toolbar level.

                ToolbarItem(placement: .cancellationAction) {
                    Button {
                        resolvedDismiss()
                        // ^^^ Was: `(dismissOverride ?? { dismiss() })()`
                        //     The Button action closure used to capture `self` and resolve `??`
                        //     at tap-time. Now it just calls a captured value. No staleness.
                    } label: {
                        #if os(iOS)
                        Image(systemName: "xmark.circle.fill")
                        #else
                        Text("Done")
                        #endif
                    }
                }
            }
        }
    }
}
```

### What the original code looked like

For comparison, the broken version was just:

```swift
ScoutResultView(
    // ...
    onSaveComplete: saveCompletionOverride ?? { dismiss() },
    //              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    //              At first glance: "use the override if set, else dismiss." Looks fine.
    //              In reality: SwiftUI hands the *result* of `??` to ScoutResultView.
    //              That result is a closure. If `saveCompletionOverride` was non-nil at
    //              body-time, the result IS the override closure, which doesn't capture self.
    //              If `saveCompletionOverride` was nil at body-time, the result is the
    //              `{ dismiss() }` closure, which captures self for the dismiss action.
    //              That's not actually the bug -- the bug is more subtle.
)
```

The actual diagnosed mechanism: ScoutResultView stored the closure (`onSaveComplete`), and on later body re-renders SwiftUI didn't re-pass it. The closure ScoutResultView held was from an earlier render. Reading `self.saveCompletionOverride` at runtime via the captured `self` produced nil even though the live View had it set.

### Why this is a macOS bug specifically

On iOS, `dismiss()` on a sheet closes the sheet. Annoying when accidental, but recoverable -- the user can re-open it.

On macOS, when `StuffScoutView` is shown **inline** in a `NavigationSplitView` detail pane (Day 7, Day 8 territory) -- not as a sheet -- there's no sheet to dismiss. SwiftUI's `dismiss()` falls back to dismissing the *next* dismissible thing in the chain, which is the **window itself**. The window vanishes. The user clicks the dock icon. Nothing happens.

This is also why `saveCompletionOverride` exists in the first place: the parent passes in `{ selectedSection = .myProducts }` so saving navigates to My Stuff instead of dismissing anything. When the staleness bug hits, the override is nil, the env dismiss fires, the window closes.

### How to spot this pattern in any codebase

Grep regex:

```
\w+\s*\?\?\s*\{[^}]*dismiss\(\)
```

Translation: "an identifier, then `??`, then a closure literal that calls `dismiss()`."

In Stuffolio that found three matches: two in StuffScoutView (one already the fix, one the sibling -- both fixed) and one in ScoutResultView (which is OK because it lives inside a regular function, not a re-render path). The OK case demonstrates that the fix isn't *always* needed -- only when the resolution happens inside something SwiftUI can re-render.

### Why a body-local `let` works inside a `@ToolbarContentBuilder`

This part is subtle. SwiftUI's `body` and `.toolbar { ... }` are `@ViewBuilder` and `@ToolbarContentBuilder` closures respectively. You might expect that you can't put a free `let` declaration in there because builders only accept content statements. But Swift's result builders allow `let` declarations as a documented part of their grammar. The `let` runs once per body invocation, before the content is assembled. That's exactly when we want the snapshot to happen.

---

## Common Mistakes

| Mistake | What happens | Fix |
|---------|--------------|-----|
| Resolving `??` inline at the call site every time | Closure captures `self` lazily; on re-renders the captured `self` may have nil where the live one has a value | Snapshot the resolved closure into a body-local `let` first |
| Trying to assign the `let` outside `body` (e.g., as a stored property) | Stored properties on a `View` struct can't reference `self.dismiss` (Environment is only available inside body) | Keep the `let` inside `body` -- it has access to environment values |
| Capturing the optional property directly: `let action = saveOverride` then `action ?? { dismiss() }` | Just moves the `??` later -- still resolves lazily wherever the `??` is | Resolve the `??` itself into the `let`, not just the optional |
| Assuming SwiftUI re-renders are rare | They happen on every state change. A view that constructs closures in body may be doing so dozens of times per second | Treat closure construction in body as a hot path. Capture *values*, not `self`. |
| Using `[weak self]` to "fix" it | `[weak self]` is for reference-cycle prevention with classes. View structs aren't reference-counted; weak doesn't apply | The fix is structural (snapshot the value), not lifecycle-related |

---

## Post-Test

Test your understanding after reading. Answers at the bottom.

1. The expression `let resolved = optionalProp ?? { dismiss() }` runs once per body call. What value does `resolved` hold if `optionalProp` is non-nil? What if it's nil?

2. Why does the OK case in `ScoutResultView.swift:274` (`let dismissAction = onSaveComplete ?? { dismiss() }` inside `func saveDirectly()`) not have the staleness bug?

3. If the parent applies `.overridingSaveCompletion { selectedSection = .myProducts }` and then *removes* it on a subsequent render, what does the body-local `let resolvedOnSaveComplete` hold across the two renders?

4. The Done button fix introduces `let resolvedDismiss` inside `.toolbar { ... }`. Why does Swift allow a `let` declaration inside a `@ToolbarContentBuilder` closure?

5. On iOS, the staleness bug still exists in the same code, but the user-visible effect is much milder. Why?

6. You see this code in a different file:
   ```swift
   .sheet(isPresented: $showing) {
       MyView(onClose: closeAction ?? { showing = false })
   }
   ```
   Is this safe? Why or why not?

7. Why doesn't `[weak self]` solve this kind of bug?

8. The bug-echo skill found this sibling automatically by running a regex against 596 files. The regex was inferred from the original fix's diff. What does this tell you about how to make a fix easier to scan for?

---

## Answer Key

### Pre-Test

1. **Swift reads `self.foo` when the closure runs, not when you write the closure.** The closure captures `self` (or a copy of `self` for value types) and dereferences `.foo` at call time.

2. **SwiftUI creates a new struct instance.** Views are value types. SwiftUI replaces the struct on each re-render. `@State` and `@StateObject` are special wrappers that survive re-creation; everything else is rebuilt.

3. **For class types, the closure sees the new instance (because it captured a reference). For struct types, the closure sees the OLD value (because it captured a copy).** SwiftUI views are structs.

4. **False.** `dismiss()` dismisses the *nearest dismissible context*: a sheet, a popover, or -- on macOS, when none of those exist -- the host window. Inside a `NavigationSplitView` detail pane on macOS, `dismiss()` closes the window.

5. **To force eager evaluation.** If the expression is `optionalProp ?? { defaultClosure }` and you assign it to a `let`, the `??` resolves immediately. Passing the expression directly defers evaluation until the consumer reads it -- which can happen against a different version of `self`.

6. **The closure is constructed when the surrounding expression is constructed (eagerly).** It is *evaluated* (called) when somebody invokes it.

7. **Yes.** A stored optional on a struct can be observed as nil by a captured-`self` closure even if the parent's modifier set it to non-nil on the live `self`. This is exactly the S12 bug.

### Post-Test

1. **If non-nil, `resolved` holds the override closure. If nil, `resolved` holds the `{ dismiss() }` fallback closure.** Either way, `resolved` is a concrete `() -> Void` value, not a self-capture.

2. **It runs inside a function call (`saveDirectly()`), not inside a SwiftUI body.** The function executes once when the user taps Save. The `??` resolves at that moment against the live `self` (because the function is called on the live struct instance, not a captured snapshot). The result is assigned to a local and used immediately. There's no closure that survives across re-renders to go stale.

3. **Render 1: `resolvedOnSaveComplete` is the override closure.** **Render 2: `resolvedOnSaveComplete` is `{ dismiss() }` because the override is now nil at body-time.** Each body call recomputes `let resolvedOnSaveComplete` against the current `self`. The user-visible behavior changes correctly between renders -- which is what we want.

4. **Swift's result builder feature allows `let` declarations as part of the builder grammar.** The `let` runs before the builder collects its content into a single result. It executes once per body invocation, in the right order, and the bound name is in scope for the rest of the builder body.

5. **iOS dismiss closes a sheet (recoverable -- the user re-opens it).** macOS dismiss inline in NavigationSplitView closes the *window* (catastrophic -- the user can't get back without `applicationShouldHandleReopen`, which is also missing by default). Same code, dramatically different consequence depending on platform context.

6. **It depends.** If `closeAction` and `showing` are `@State` on the parent and the parent never removes the `.sheet` modifier, the closure inside the sheet builder runs once when the sheet presents and the staleness window is small. But strictly speaking, this has the same shape as the bug. The defensive fix is `let resolvedClose = closeAction ?? { showing = false }; MyView(onClose: resolvedClose)`. The cost is one line; the upside is you don't need to reason about whether SwiftUI's re-render pattern will trip you up.

7. **`[weak self]` weakens a *reference*. View structs are value types -- there are no references to weaken.** `[weak self]` is the right fix for reference-cycle bugs in classes (e.g., a Combine subscription holding a strong reference to a view controller). For struct value-capture staleness, you have to change *what* gets captured: capture the resolved value, not `self`.

8. **A fix that produces a distinctive, grep-able shape can be scanned for across an entire codebase to find sibling instances.** The S12 fix's distinctive shape was `??` followed by `{ ... dismiss() ... }`. That regex found the sibling in two minutes. If the fix had been a sweeping refactor (rename a property, restructure the View) it would have been impossible to template into a search. **Fix in a way that leaves a fingerprint, and finding the next instance becomes a script.**

---

## Notes on Connection to Earlier Days

- **Day 4.5** (Property Wrappers): `@State` survives re-renders; ordinary stored properties don't have wrapper-based persistence. This is the substrate that makes captured-`self` staleness possible.
- **Day 7.5** (Platform Conditionals): The bug manifests on macOS specifically because `dismiss()` falls through to the window. iOS has different sheet semantics.
- **Day 8** (Sheet vs Inline Navigation): Inline-in-NavigationSplitView is exactly the case where `dismiss()` becomes destructive. This tutorial extends Day 8 with the closure-staleness consequence.
- **Day 8.5** (Closures as Parameters): `() -> Void` and optional closures with `= nil`. The S12 closure shape is exactly what Day 8.5 set up. The new lesson: **how** the closure captures the surrounding scope determines whether it stays correct across re-renders.
- **Day 11** (ForEach Identity / UUID Trap): Day 11 was the first time we hit "body runs more often than you think." This tutorial is the same lesson on a different surface: anything that body computes can be re-computed, and any closure body constructs is a snapshot of the moment of construction.

---

## New Concepts Introduced in Day 16

| Concept | Where in Code | Key Takeaway |
|---------|---------------|--------------|
| Captured `self` (in struct closures) | Throughout | A closure inside a struct's body holds a copy of `self` and reads its properties when the closure runs, not when it's written. |
| Stale capture | The bug, lines 124-159 | The captured `self` can become out of date with the live `self` between re-renders, causing closures to see old values. |
| Eager vs lazy resolution | Pre-Test #5, the fix | Resolving an expression *now* (eager, into a `let`) captures the current state; deferring to closure-call-time (lazy) re-reads through the staleness window. |
| Body-local `let` | The fix, lines 242-260 | A `let` inside `var body` runs once per body invocation against the current `self`. Use it to snapshot a value before constructing a closure. |
| `??` constructs the RHS eagerly | Vocabulary, Pre-Test #6 | `optional ?? { closure }` constructs the closure when the surrounding expression is built, not when the result is invoked. The RHS captures `self`. |
| Re-render value-replacement model | Pre-Test #2, Post-Test #3 | SwiftUI replaces struct view instances on re-render; non-`@State` stored properties are reset from the new instance, leaving captured-`self` references pointing at the old shape. |
| Sibling bug (and how to find it) | Post-Test #8 | A fix that leaves a distinctive grep-able fingerprint can be templated into a regex and used to find every other instance of the same pattern across the codebase (this is what the bug-echo skill automates). |
| `dismiss()` platform divergence | Pre-Test #4, Post-Test #5 | On iOS `dismiss()` closes a sheet; on macOS inline in `NavigationSplitView`, it falls through and closes the host window. Same code, dramatically different consequence per platform.

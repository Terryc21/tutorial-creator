# useDebouncedValue: A Custom React Hook

*Source: `src/hooks/useDebouncedValue.ts` (TypeScript / React 18)*
*Topic: Custom hooks, useEffect cleanup, dependency arrays*

> [!NOTE]
> This is a **synthesized tutorial output** demonstrating that `tutorial-creator` works for any language, not just Swift. The skill produces this format from a file in your own project. The source file annotated below is a real-world pattern (a debounce hook every web app eventually needs) but the file itself was written for this example.

---

## Vocabulary

| Term | Quick Definition |
|------|-----------------|
| Custom hook | A function whose name starts with `use` and that calls other hooks. Reusable stateful logic across components. |
| `useState<T>(initial)` | React hook returning `[value, setValue]`. The component re-renders when `setValue` is called with a new value. |
| `useEffect(fn, deps)` | Runs `fn` after render. If `deps` change, runs again. If `fn` returns a function, that's the cleanup, called before the next run or on unmount. |
| Dependency array | The second argument to `useEffect`. React compares each item to its previous value with `Object.is`; if any changed, the effect re-runs. |
| Cleanup function | The function returned from inside `useEffect`. Runs before the next effect run, and on component unmount. Used to undo what the effect set up. |
| Closure | A function that "remembers" the variables in the scope where it was defined. Cleanup functions are closures over the effect's locals. |
| Debounce | "Wait until input stops changing for N milliseconds, then act on the latest value." Distinguishes a deliberate input from a typing storm. |
| `setTimeout(fn, ms)` | Schedules `fn` to run after `ms` milliseconds. Returns a numeric handle. |
| `clearTimeout(handle)` | Cancels a previously scheduled `setTimeout`. Safe to call even if the timer already fired. |
| Stale closure | A closure that captured an outdated value because it was created before that value changed and never recreated. The classic React hook bug. |
| Generic (`<T>`) | A TypeScript type parameter. Lets one hook handle a `string` value, a `number` value, an object — without losing type safety. |

---

## Pre-Test

Test your intuition before reading. Answers at the bottom.

1. If `useEffect(() => {...}, [value])` runs on every render where `value` changed, what does the cleanup function (the returned function) do, and *when* does it run?

2. A user types "hello" rapidly into a search box wired to a debounce hook with 300ms delay. How many times does the network request fire? Why?

3. The dependency array for `useEffect` is `[value, delay]`. If `value` changes but `delay` doesn't, does the effect re-run?

4. A `setTimeout` was scheduled with `setTimeout(fn, 500)`. The component unmounts 200ms later. What happens to `fn`? Does it run? Should it?

5. If you forgot to return a cleanup function from `useEffect`, what specifically goes wrong?

6. The hook stores its result in `useState`. Why not just compute the debounced value directly and return it from the function?

7. Why is `T` (the generic type parameter) needed? Why not just use `unknown` or `any`?

---

## What This File Does (Big Picture)

When a user types into a search box, you usually don't want to fire a network request on every keystroke — that floods your backend and produces flickering results. Instead, you want to wait until they pause typing.

`useDebouncedValue` takes a value (typically the live value of a search input) and returns a "calmed-down" version of it. The returned value lags the input by a configurable delay; it only updates after the input has stopped changing for that long.

Used like this in a component:

```tsx
const [search, setSearch] = useState('');
const debouncedSearch = useDebouncedValue(search, 300);

useEffect(() => {
  // Fires only after the user stops typing for 300ms
  fetchSearchResults(debouncedSearch);
}, [debouncedSearch]);
```

Two pieces of state — `search` (live, updates on every keystroke) and `debouncedSearch` (lagged). The user sees their typing in the input box but the backend only sees the calmed-down version.

---

## Lines 1: Imports

```typescript
import { useEffect, useState } from 'react';
```

Two hooks. `useState` to store the lagged value. `useEffect` to schedule the timer that updates it. Nothing else from React is needed — this hook is pure logic.

---

## Lines 3-7: The Function Signature

```typescript
export function useDebouncedValue<T>(
  value: T,
  delay: number = 300
): T {
```

Read this carefully — there's a lot in three lines.

- **`<T>`** — generic type parameter. The hook works on any type. If you pass a `string`, `T` is `string` and the return type is `string`. If you pass an object, `T` is that object's type. TypeScript figures it out from the call site.
- **`value: T`** — the live input. Whatever changes triggers the debounce.
- **`delay: number = 300`** — milliseconds to wait. Default 300, the standard "feels responsive but not chatty" value.
- **`: T`** — the return type. Same shape as the input.

Without `<T>`, you'd have to either pick one type (only works for strings, say) or return `any`/`unknown`, which puts the type-cast burden on every caller. Generics let one implementation serve every type with full type safety.

---

## Line 8: The Internal State

```typescript
const [debounced, setDebounced] = useState<T>(value);
```

This is where the lagged value lives. We initialize it to the current `value`, so on first render the hook returns the input unchanged (no delay on initial render — that would be a bug).

The `<T>` after `useState` is usually inferred, but writing it explicitly is a hint to readers and catches type errors earlier.

**`debounced` updates only when `setDebounced` is called.** That's the whole game — the effect below decides when to call `setDebounced`.

---

## Lines 10-14: The Effect

```typescript
useEffect(() => {
  const timer = setTimeout(() => {
    setDebounced(value);
  }, delay);
```

Here's the heart of the hook.

When `value` (or `delay`) changes, this effect runs. It schedules a timer for `delay` milliseconds. If the timer fires, it calls `setDebounced(value)`, which updates the state and triggers a re-render with the new debounced value.

**The trick:** if `value` changes again *before* the timer fires, the cleanup (next section) cancels this timer before it has a chance to run. So a rapid typing storm produces many scheduled timers but only the *last* one — the one that survived the typing — actually fires.

Read it as: "every time the input changes, set a fresh delay; the only timer that survives is the one that wasn't cancelled."

---

## Line 15: The Cleanup

```typescript
  return () => clearTimeout(timer);
}, [value, delay]);
```

The function returned from the effect is the **cleanup**. React calls it before the next effect run and on unmount.

This single line does most of the work. Every time `value` changes:

1. The previous cleanup runs first → previous timer cancelled
2. The new effect runs → new timer scheduled

If the user is typing rapidly, the cleanup keeps cancelling the in-flight timer before it can fire. Only when typing stops for `delay` ms does the latest timer survive long enough to call `setDebounced`.

The dependency array `[value, delay]` says "re-run this effect any time the value or delay changes." If you forget `delay`, changing `delay` won't take effect until `value` next changes. If you forget `value`, the timer is never re-scheduled and the hook is broken. Both items belong.

**`clearTimeout` is safe even if the timer already fired** — it's a no-op in that case. So you don't need to guard the cleanup.

---

## Line 17: The Return

```typescript
  return debounced;
}
```

The hook returns the lagged state. Callers see this value update only after the input has been stable for `delay` ms.

---

## Common Mistakes (and Why They're Worth Knowing)

### Mistake 1: Computing instead of stating

```typescript
// WRONG
export function useDebouncedValue<T>(value: T, delay: number) {
  let debounced = value;
  setTimeout(() => { debounced = value; }, delay);
  return debounced;
}
```

This mutates a local variable that disappears at the end of the function call. It also returns the live value immediately — no debouncing happens. The reason `useState` is required is that the *re-render* is the mechanism by which the calling component sees the lagged value. Mutating a local doesn't trigger a render.

### Mistake 2: Missing the cleanup

```typescript
// WRONG
useEffect(() => {
  setTimeout(() => setDebounced(value), delay);
}, [value, delay]);
```

Without `clearTimeout`, every keystroke schedules a new timer and *none of them are cancelled*. After typing "hello", five timers are in flight. Each fires in sequence at 300ms, 301ms, 302ms... and the state flickers through "h", "he", "hel", "hell", "hello" — exactly what debounce is supposed to prevent.

### Mistake 3: Wrong dependency array

```typescript
// WRONG
useEffect(() => {
  const timer = setTimeout(() => setDebounced(value), delay);
  return () => clearTimeout(timer);
}, []); // empty array
```

Empty array means the effect runs once on mount and never again. The closure captures the initial `value` and `delay`. Forever after, `value` will be the value at mount time, not the current one. This is the **stale closure bug** — the most common React hook mistake. ESLint's `react-hooks/exhaustive-deps` rule catches it.

---

## Post-Test

1. Why is the dependency array `[value, delay]` and not just `[value]`?

2. If you typed "hello" with 100ms between keystrokes and the delay is 300ms, how many timers are scheduled total, and how many actually fire?

3. The effect calls `setDebounced(value)`. What value is `value` at the moment the timer fires?

4. The hook returns `debounced`, not `value`. Why does that matter for the calling component?

5. What would happen if you replaced `setTimeout` with `setInterval`?

6. Could you implement this hook without `useState`? Why or why not?

7. Why does `clearTimeout` not need to check whether the timer has already fired?

8. Suppose you wanted a `leading-edge` debounce: fire immediately on the first keystroke, then wait. How would you change the hook?

---

## Post-Test Answers

1. **Both belong because both affect what the timer should do.** `value` is what gets set after the delay. `delay` is how long to wait. If `delay` changes from 300 to 500 mid-stream, the next timer should use 500. The dependency array tells React when to re-run the effect; both items must trigger a re-run.

2. **5 scheduled, 1 fires.** Each keystroke triggers an effect run. The previous cleanup cancels the prior timer; the new effect schedules a new one. After "hello" the last timer is the only un-cancelled one, and it fires 300ms after the final keystroke.

3. **The value captured by the effect closure when this particular timer was scheduled.** Because the effect re-runs every time `value` changes, each scheduled timer captures the `value` that was current when it was scheduled. The surviving timer captures the latest typed value.

4. **The component re-renders only when `debounced` changes.** The live `value` (e.g., the search input's `useState`) is owned by the parent component. When the user types, the parent re-renders to update the input. But the parent's effect that triggers the network call depends on `debounced`, not `value`. So the network effect runs only after typing stops.

5. **`setInterval` runs forever every `delay` ms.** Wrong primitive — the hook would call `setDebounced(value)` every 300ms continuously, even when nothing changes. Re-renders would cascade. `setTimeout` is one-shot, which is what debounce needs.

6. **Not really.** `useState` is the bridge between the hook's internal logic and the parent's render cycle. Without state, you have no way to make the parent re-render with the new debounced value. You could use `useRef` for the timer handle, but the *value* itself needs `useState` to trigger renders.

7. **`clearTimeout` is a no-op on already-fired or already-cleared timers.** The Web API specification guarantees this. You don't need a guard.

8. **Track whether the leading edge has fired** with a `useRef<boolean>`. On effect run, if the ref is `false`, set it to `true` and call `setDebounced(value)` immediately. Schedule the trailing edge as before. Reset the ref when sufficient idle time has passed (you'd also need a separate timeout for this). It's noticeably more complex than trailing-edge debounce, which is why `useDebouncedValue` is usually the trailing version.

---

## New Concepts Introduced

| Concept | Where in Code | Key Takeaway |
|---------|--------------|--------------|
| Custom hook naming convention | Line 3 (`useDebouncedValue`) | Hook name must start with `use`. React's lint rules enforce this. |
| Generic type parameter `<T>` | Line 3 | One hook handles any value type with full type safety. |
| Default parameter | Line 5 (`delay: number = 300`) | TypeScript syntax for a parameter with a fallback value. |
| `useState<T>(initial)` | Line 8 | State that persists across renders and triggers re-renders on update. |
| `useEffect(fn, deps)` | Lines 10-15 | Runs side effects after render, re-runs when deps change. |
| Cleanup function pattern | Line 15 | Effect returns a function that runs before the next effect (or on unmount). |
| Dependency array | Line 15 | Tells React when to re-run the effect. Wrong contents → bugs. |
| `setTimeout` / `clearTimeout` | Lines 11, 15 | The Web API for one-shot scheduling. Cancellable, cancellation is idempotent. |
| Stale closure pattern | "Mistake 3" | The most common React hook bug. ESLint catches it via exhaustive-deps. |
| Trailing-edge debounce | Whole file | Wait for stillness, then act. Different from leading-edge or throttle. |

---

## Where This Comes Up

You'll write something like `useDebouncedValue` in nearly every web app:

- Search inputs (the canonical case)
- Form auto-save (don't save on every keystroke)
- Window resize handlers (don't re-layout 60 times per second)
- Drag end detection (debounce mouse movement)
- "User stopped editing" detection in collaborative editors

Once you understand this 18-line file, the cleanup-and-cancel pattern transfers to every effect that schedules anything: subscriptions, event listeners, network requests with `AbortController`, animation frames. The principle is always: "set up something with a way to undo it; cleanup undoes it."

---

*This tutorial was generated by `tutorial-creator` from a single TypeScript file. The skill works the same way on any language: you point it at a real file from your project, it produces a vocabulary list, pre-test, annotated walkthrough, and post-test calibrated to that specific code.*

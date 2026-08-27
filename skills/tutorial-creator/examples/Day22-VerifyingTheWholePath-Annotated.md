# Day 22: Verifying the Half You Can See

*Source: builds 121 and 123 — two shipped regressions, three days apart, same root cause*
*Commits: `aa03bd93` → `ba37848c` (cutover, rolled back) · `1fd0dbb4` → `cf0291ae` (pagination, reverted)*
*Day 22 — 08/27/2026 — Phase 6 (off-progression): Verification Practice*

> [!NOTE]
> This is a **sample tutorial output** demonstrating what `tutorial-creator` produces. The real
> skill writes one of these from your own project's source code. This example is unusual in its
> subject: its annotated source is a **passing test file**, read as evidence rather than as code.
> It uses real commits from [Stuffolio](https://stuffolio.app), the source project the skill was
> extracted from.

---

## What You'll Learn

This is not an API tutorial. There is no new CloudKit symbol to memorize here.

It is about a failure mode that shipped **twice in three days** in your own app, past a
passing test suite and a manual device check both times. The concepts are:

- What a green test actually proves, and where its evidence stops
- Why "I verified it" is an incomplete sentence without naming *which path*
- The difference between a **negative control** (does this test discriminate?) and a
  **coverage question** (does this test reach the code that broke?)
- Why a correct fix can be the thing that causes the damage

---

## Pre-Test

Answer before reading on. Write your answers down; the point is to catch where your
intuition is confident and wrong.

**1.** A device log prints `Fetched 2420 of 2420`. The pre-fix behaviour was `Fetched 100`.
What has this proven?

**2.** A test suite has five tests. All pass. One of them is a negative control that fails
when you restore the old buggy behaviour. How much confidence should that give you?

**3.** Sync has two halves: upload and download. Build 121 changed where records live.
The developer verified downloads worked. What is the missing question?

**4.** Here is a real comment from the build-123 fix:

```
// Uploads were healthy in the same run (146/146 succeeded), which is why this hid
// for so long — the write half worked, so sync reported success.
```

The author diagnosed *exactly* the failure mode of the previous incident, in writing,
while introducing the next one. How is that possible?

---

## The two incidents

### Build 121 — the zone cutover

`aa03bd93` moved item records from CloudKit's default zone into a custom zone. This
changes the record's *address*: a `CKRecord.ID` carries a zone, so every read and every
write has to agree about which zone it means.

**Verified:** the read path. Records were enumerated from the new zone, they came back,
the count was right.

**Not verified:** the write path. Deletions built record IDs through a second, separate
code site that still pointed at the old zone.

Sync ran for 2.5 days before the mismatch surfaced. Rolled back in `ba37848c`.

### Build 123 — the pagination fix

`1fd0dbb4` fixed a genuine, serious bug. `CKDatabase.records(matching:)` returns **one
page** — roughly 100 records — plus a `queryCursor` for the rest. The cursor was declared
and never read. The app had been seeing at most 100 of 2,420 server records, silently,
for weeks.

**Verified:** the fetch. Device log read `Fetched 2420 of 2420`. Five unit tests passed.

**Not verified:** what the merge did with 2,320 records it had never seen before.

Result: **380 duplicate items, 51 duplicated `cloudSyncID`s**, across three devices.
Reverted in `cf0291ae`.

---

## Annotated: the test suite that passed

This is `SyncPaginationTests.swift` as it shipped in build 123. Read it as if reviewing
a pull request, and ask one question throughout: *what code does this execute?*

```swift
private func chunk(_ count: Int, by size: Int) -> [[Int]] {
    // a local helper — builds [Int] and slices it
}
```

> **First signal, and it is the whole story.** The test's subject is a helper defined
> *inside the test file*. It does not import the fetch. It does not construct a
> `CKRecord`. Every assertion below runs against arrays of integers.

```swift
@Test("A 2,420-record fetch is split below CloudKit's 400-ID request cap")
func chunkingRespectsFetchCap() {
    #expect(chunks.count == 13)
    #expect(chunks.allSatisfy { $0.count <= 400 }, "no chunk may exceed CloudKit's hard cap")
    #expect(chunks.allSatisfy { $0.count <= 200 }, "chunks use the conservative batch size")
}
```

> Correct, and worth having. It encodes a real CloudKit constraint (400 IDs per
> `CKFetchRecordsOperation`) that is easy to violate. But it is **arithmetic about
> arithmetic** — it proves 2420 ÷ 200 = 13 batches, nothing about CloudKit.

```swift
@Test("Chunking never drops or duplicates a record ID")
func chunkingIsLossless() {
    #expect(flat.count == total, "\(total) ids must survive chunking")
    #expect(Set(flat).count == total, "no duplicates for \(total)")
}
```

> ⚠️ **Read this test's name against what actually happened.** "Never drops or
> duplicates." Build 123 duplicated 380 items. The test is not wrong — chunking really
> was lossless — but its *name* claims a property at a scope the test never reached.
> Duplication happened one layer down, in the merge. A reader skimming names would
> reasonably conclude duplication was covered.

```swift
@Test("Pagination accumulates every page, not just the first")
func paginationAccumulatesAllPages() {
    #expect(accumulated == total, "every page must be accumulated")
    #expect(pages == 25, "2420 records at 100/page is 25 pages")
    #expect(accumulated != pageSize, "the pre-fix behaviour (first page only) must not pass")
}
```

> 🔑 **The last line is a negative control** — it asserts the old broken behaviour would
> fail this test. That is genuinely good practice, and it is *why the suite felt
> trustworthy.* A negative control answers "does this test discriminate?" It cannot
> answer "does this test reach the code that broke?"
>
> Those are different questions. The suite answered the first one well and never asked
> the second.

```swift
@Test("The page cap is a stuck-cursor guard, not a library-size limit")
func pageCapIsGenerous() {
    #expect(capacity > 2420 * 4, "the cap must not bind on a realistic library")
}
```

> Sensible. Still arithmetic.

**Five tests. All correct. All passing. Combined coverage of the merge: zero.**

---

## The comment that predicted the bug

Inside the build-123 fix, describing why the *pagination* bug hid for so long:

```swift
// Measured on a Debug build 08/26: "Fetched 100 remote records" against a zone holding
// 1,137. Uploads were healthy in the same run (146/146 succeeded), which is why this hid
// for so long — the write half worked, so sync reported success.
```

Read that back slowly. It says: *one half worked, so the system reported success, so
nobody looked at the other half.*

That is a precise diagnosis of build 121 — and it was written **while shipping build
123, which failed the same way on a different axis.** Naming a failure mode is not the
same as being protected from it. The author had the concept, in words, on the screen, and
still verified one half.

Fifteen lines above, in the same file:

```swift
/// The change token is deliberately NOT persisted here: this method answers "what is in the
/// zone right now", and the existing merge path expects a full picture.
```

**"The existing merge path expects a full picture."**

The merge had *never once* received a full picture. It was written against a window of
~100 records and had only ever run against that window. Pagination gave it the full
picture for the first time — 2,320 records it had never seen, carrying three generations
of key format (`legacy-…`, numeric, UUID). Matching none of them locally, it did the
straightforward thing: inserted them as new items.

> 🔑 **The fix was correct. The fix caused the damage.** Both are true, and the second
> does not make the first false. Correctness is a property of code in isolation;
> shipping safety is a property of code meeting data that already exists.

---

## The pattern

Each verification proved something real. Each one stopped at the boundary of what was
easy to observe.

| Build | Change | Verified | Never asked | Result |
|---|---|---|---|---|
| 121 | Records move to a custom zone | Reads work | Do *writes* use the same zone? | Deletes broke for 2.5 days |
| 123 | Fetch follows the cursor | Fetch returns 2,420 | What does the *merge* do with them? | 380 duplicates on 3 devices |

The shape is identical:

1. Change something in a two-sided system
2. Verify the side that produces a visible, satisfying signal
3. The other side is silent — and silence reads as success
4. Ship

Note what is *not* on that list: haste, carelessness, skipped tests. Both builds had
tests. Build 123's tests included a negative control. The gap was never rigor. It was
**scope** — and scope is invisible from inside a passing suite, because a passing test
looks the same whether it covers the risk or not.

---

## The technique: name the paths first

The fix is not "test more." It is one question asked *before* verifying:

> **What are the paths through this change, and which one am I about to look at?**

Applied to build 121:

- Path A: read a record from the new zone ✅ verified
- Path B: write a record to the new zone ❓
- Path C: **delete** a record in the new zone ❓ ← broke

Applied to build 123:

- Path A: fetch pages until the cursor is nil ✅ verified
- Path B: merge a record that **matches** a local item ❓
- Path C: merge a record that **matches nothing** ❓ ← broke

Path C is in both lists, and in both cases it is the one nobody looked at. That is not a
coincidence — Path C is the *unfamiliar* case in each, the one with no existing habit
attached, which is exactly why it needs naming before it can be checked.

Enumerating takes about a minute. Neither list requires knowing the bug in advance; both
fall out of asking "what does this change touch?" instead of "did my change work?"

---

## Post-Test

**1.** Your suite has 5 passing tests including a negative control. What does the
negative control prove, and what does it not?

**2.** In your own words: why is "the fix was correct" compatible with "the fix caused
380 duplicates"?

**3.** You change a function that writes to disk *and* one that reads from it. You verify
the read. Name the two questions still open.

**4.** A test is named `chunkingIsLossless` and passes. Duplicates appear in production.
Give two explanations, and say which is more likely.

**5.** ⚠️ Hardest. The build-123 author wrote a comment correctly diagnosing build 121's
failure mode, then repeated it. What would have to change for the *knowledge* to become a
*habit*? (No single right answer. A good one names a mechanism, not an intention.)

---

## Vocabulary

| Term | Meaning |
|---|---|
| **Negative control** | Deliberately break the code, confirm the test fails for the right reason, restore. Proves a test *discriminates*. |
| **Coverage question** | Does this test execute the code that could break? Distinct from, and not answered by, a negative control. |
| **Path enumeration** | Listing the routes through a change before verifying, so the unverified ones are named rather than assumed. |
| **Silent failure** | A wrong result indistinguishable from a right one at the observation point. A short page looks exactly like a small library. |
| **`queryCursor`** | CloudKit's continuation token. `records(matching:)` returns one page plus a cursor; following it is the caller's job. |
| **Bug-hiding-a-bug** | A defect whose presence makes a second one unreachable. The 400-ID cap could not fire while only 100 records were ever fetched. |

---

## Connections

- **[Day 16 (Captured-Self Staleness)](Day16-CapturedSelfStaleness-Annotated.md)** — also a
  "verified the visible half" bug. The captured value looked right at capture time.
- **Day 12 (Time Bomb Pattern)** *(not in this examples set)* — code correct today, wrong under
  future conditions. This is its sibling: code correct in isolation, wrong against data that
  already exists.
- **Day 20 (Swift Testing / XCTest coexistence)** *(not in this examples set)* — mechanics of
  writing tests. This is about what a written test is *evidence for*.

> Cross-references like these are normal in real output: the skill links a new lesson to earlier
> ones in the same curriculum. Only Day 16 happens to be checked in here.

---

## The one-sentence version

**A passing test tells you the code it ran is correct; it says nothing at all about the
code it never reached — and from inside the green checkmark, those two look identical.**

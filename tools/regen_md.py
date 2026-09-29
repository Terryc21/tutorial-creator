#!/usr/bin/env python3
"""regen_md.py: a reference implementation of `vocab regen-md` in its default, in-place mode.

It brings a tutorial-creator VOCABULARY.md in step with its vocabulary.yaml by following
`skills/tutorial-creator/VOCAB.md`, section `vocab regen-md`, "Without --import", steps 2 to 7:

- A row belongs to the entry whose term it shows, ignoring case, backticks and ** bold.
- Each entry's home row takes the yaml definition. Repeat rows keep their own wording.
- An entry with no row gets one, in a new section headed by its context if it needs one.
- Rows whose term is not in the yaml are orphans. They are kept or removed, never dropped silently.
- The Cumulative Count is recomputed, and the *Updated:* line changes only when something else did.

Lines the run does not change are written back byte for byte, so a view that already matches
the yaml is left untouched.

Status: a tool for testing the spec, and a starting point for moving vocabulary writes into a
script. The skill itself still follows the prose in VOCAB.md; nothing in the skill calls this.

Not implemented here (the prose covers them):
- building VOCABULARY.md from scratch when it does not exist;
- the orphan question's [add] answer, and answering per row (this takes one answer for all).

Beyond the spec, for safety: a section with no `| Term |` table is left exactly as it is (never
counted or dropped), extra table columns are kept, the file's closing *Updated:* line stays last
when a section is added at the end, and --write backs the old view up first.

Verified 09/29/2026: on a real 305-term view it changes nothing. On add, edit, orphan and new-Day
scenarios it matches the test harness it was cleaned up from, except that it updates only the
file's closing *Updated:* line (the harness rewrote every such line, including a stray one inside
a section). On a real pre-09/28 view it reproduces, byte for byte, what a fresh model session
produced by following the spec (14 rows added, 44 definitions refreshed, 47 orphan rows kept,
none removed).

Usage:
    python3 tools/regen_md.py <tutorials-dir>                    # dry run: summary and diff
    python3 tools/regen_md.py <tutorials-dir> --write            # back up, then write
    python3 tools/regen_md.py <tutorials-dir> --orphans remove   # default is keep

Requires PyYAML (pip3 install pyyaml).
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import os
import re
import shutil
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("regen_md.py needs PyYAML: pip3 install pyyaml")

COUNT_HEADING = "## Cumulative Count"
NEW_TABLE = ["| Term | Quick Definition |", "|------|-----------------|"]
_DAY = re.compile(r"Day (\d+(?:\.\d+)?)\b")


class ReconcileError(Exception):
    pass


def day_of(text: str) -> str | None:
    """The day a heading or context starts with: "Day 7.5: ..." gives "7.5"."""
    m = _DAY.match(text)
    return m.group(1) if m else None


def key(term: str) -> str:
    """How a row is matched to an entry (VOCAB.md step 3): ignoring case, backticks and ** bold."""
    return re.sub(r"\s+", " ", term.replace("`", "").replace("**", "")).strip().lower()


def cell(text) -> str:
    """A yaml definition as a table cell: collapsed to one line, with pipes escaped."""
    return re.sub(r"\s+", " ", str(text)).strip().replace("|", "\\|")


def split_row(line: str) -> list[str] | None:
    """The cells of a table row (escaped pipes stay inside a cell), or None for anything else."""
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
    return cells if len(cells) >= 2 else None


class Row:
    """One table row. Its original line is written back unless the run changed it."""

    def __init__(self, raw: str | None, cells: list[str] | None):
        self.raw, self.cells, self.dirty = raw, cells, raw is None

    @property
    def term(self) -> str | None:
        return self.cells[0] if self.cells else None

    def line(self) -> str:
        return self.raw if not self.dirty else "| " + " | ".join(self.cells) + " |"


class Section:
    """A `## ` heading with a `| Term |` table: the lines before it, the table, the lines after."""

    def __init__(self, heading: str, heading_line: str, pre, table_head, rows, post):
        self.heading, self.heading_line = heading, heading_line
        self.pre, self.table_head, self.rows, self.post = pre, table_head, rows, post

    def lines(self) -> list[str]:
        return [self.heading_line, *self.pre, *self.table_head, *(r.line() for r in self.rows), *self.post]


class CountBlock:
    """The Cumulative Count section. Its table rows are recomputed; everything else is kept."""

    def __init__(self, top, rows, rest):
        self.top, self.rows, self.rest, self.new_rows = top, rows, rest, None

    def lines(self) -> list[str]:
        return [*self.top, *(self.rows if self.new_rows is None else self.new_rows), *self.rest]


class Opaque:
    """A section without a `| Term |` table. Written back exactly as it was."""

    def __init__(self, lines):
        self._lines = lines

    def lines(self) -> list[str]:
        return list(self._lines)


def parse(text: str):
    """Split a view into the lines above the first section, then one block per `## ` heading."""
    lines = text.split("\n")
    starts = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    head = lines[: starts[0]] if starts else lines
    blocks = []
    for a, b in zip(starts, starts[1:] + [len(lines)]):
        body = lines[a + 1 : b]
        if lines[a].rstrip() == COUNT_HEADING:
            t = next((k for k, ln in enumerate(body) if ln.startswith("|")), None)
            if t is None or t + 1 >= len(body):
                blocks.append(Opaque(lines[a:b]))
                continue
            k = t + 2
            while k < len(body) and body[k].startswith("|"):
                k += 1
            blocks.append(CountBlock([lines[a], *body[: t + 2]], body[t + 2 : k], body[k:]))
            continue
        t = next((k for k, ln in enumerate(body) if ln.startswith("| Term")), None)
        if t is None or t + 1 >= len(body):
            blocks.append(Opaque(lines[a:b]))
            continue
        rows, k = [], t + 2
        while k < len(body) and body[k].startswith("|"):
            rows.append(Row(body[k], split_row(body[k])))
            k += 1
        blocks.append(Section(lines[a][3:].strip(), lines[a], body[:t], body[t : t + 2], rows, body[k:]))
    return head, blocks


def _insert_section(blocks: list, new: Section) -> None:
    """A Day section goes among the Day sections in day order; any other after the last section."""
    secs = [i for i, b in enumerate(blocks) if isinstance(b, Section)]
    d = day_of(new.heading)
    days = [i for i in secs if d and day_of(blocks[i].heading)]
    if days:
        before = [i for i in days if float(day_of(blocks[i].heading)) < float(d)]
        at = before[-1] + 1 if before else days[0]
    elif secs:
        at = secs[-1] + 1
    else:
        at = next((i for i, b in enumerate(blocks) if isinstance(b, CountBlock)), len(blocks))
    blocks.insert(at, new)
    _keep_footer_last(blocks, at)


def _keep_footer_last(blocks: list, at: int) -> None:
    """If a new last section went in after the one holding the file's closing *Updated:* line
    (older views keep sections below the Cumulative Count), move that line and what follows it to
    the new section, so the footer stays at the end of the file. The spec is silent on this; a fresh
    session following it did the same."""
    if at != len(blocks) - 1 or at == 0:
        return
    prev = blocks[at - 1]
    tail = prev.post if isinstance(prev, Section) else prev.rest if isinstance(prev, CountBlock) else None
    i = next((k for k, ln in enumerate(tail or []) if ln.startswith("*Updated:")), None)
    if i is not None:
        blocks[at].post += tail[i:]
        del tail[i:]


def reconcile(entries: list[dict], blocks: list, orphans: str = "keep") -> dict:
    """VOCAB.md steps 3 to 5, applied to the parsed blocks in place. Returns what changed."""
    log = {"added": [], "refreshed": [], "orphans": [], "removed": [], "new_sections": []}

    def sections():
        return [b for b in blocks if isinstance(b, Section)]

    def home_section(e):
        ctx = str((e.get("first_encountered") or {}).get("context") or "")
        for s in sections():
            if s.heading.lower() == ctx.lower():
                return s
        d = day_of(ctx)
        return next((s for s in sections() if d and day_of(s.heading) == d), None)

    def free_row(rows, k, taken):
        return next((r for r in rows if r.cells and key(r.term) == k and id(r) not in taken), None)

    # Step 3: every entry claims one home row: in its home section if it has one there, else its
    # first unclaimed row anywhere. Its other rows are repeat rows.
    home, taken = {}, set()
    for e in entries:
        k, s = key(e["term"]), home_section(e)
        r = (free_row(s.rows, k, taken) if s else None) or free_row(
            [r for s2 in sections() for r in s2.rows], k, taken)
        if r is not None:
            home[id(e)] = r
            taken.add(id(r))

    # Step 4: refresh home rows from the yaml; leave repeat rows' wording alone.
    for e in entries:
        r = home.get(id(e))
        want = cell(e.get("definition", ""))
        if r is not None and r.cells[1] != want:
            r.cells[1], r.dirty = want, True
            log["refreshed"].append(r.term)

    # Step 4: add a row for each entry that has none, making its section if needed.
    for e in entries:
        if id(e) in home:
            continue
        s = home_section(e)
        if s is None:
            ctx = str((e.get("first_encountered") or {}).get("context") or "") or "Other"
            heading = ctx[:1].upper() + ctx[1:]
            s = Section(heading, "## " + heading, [""], list(NEW_TABLE), [], ["", "---", ""])
            _insert_section(blocks, s)
            log["new_sections"].append(heading)
        r = Row(None, [e["term"], cell(e.get("definition", ""))])
        s.rows.append(r)
        home[id(e)] = r
        log["added"].append(e["term"])

    # Step 4: orphans (rows whose term matches no entry) are listed, and removed only if asked.
    known = {key(e["term"]) for e in entries}
    found = [(s, r) for s in sections() for r in s.rows if r.cells and key(r.term) not in known]
    log["orphans"] = [r.term for _, r in found]
    if found and orphans == "remove":
        emptied = []
        for s, r in found:
            s.rows.remove(r)
            log["removed"].append(r.term)
            if not s.rows:
                emptied.append(s)
        blocks[:] = [b for b in blocks if not any(b is s for s in emptied)]

    # Step 5: recompute the Cumulative Count from home rows, one row per section in file order.
    home_rows = {id(r) for r in home.values()}
    total, count_rows = 0, []
    for s in sections():
        n = sum(1 for r in s.rows if id(r) in home_rows)
        total += n
        count_rows.append(f"| {day_of(s.heading) or s.heading.split(': ', 1)[-1]} | {n} | {total} |")
    if total != len(entries):
        missing = [e["term"] for e in entries if id(e) not in home]
        raise ReconcileError(f"Running total {total} does not equal {len(entries)} entries; "
                             f"entries without a home row: {missing[:10]}")
    count = next((b for b in blocks if isinstance(b, CountBlock)), None)
    if count is not None:
        count.new_rows = count_rows
    return log


def regen(entries: list[dict], text: str, orphans: str = "keep", today: dt.date | None = None):
    """Steps 2 to 6 on a view's text. Returns the new text and what changed."""
    head, blocks = parse(text)
    log = reconcile(entries, blocks, orphans)
    out = "\n".join([*head, *(ln for b in blocks for ln in b.lines())])
    if out != text:  # step 6: the Updated line changes only when something else did
        d = today or dt.date.today()
        stamps = list(re.finditer(r"^\*Updated: .*\*$", out, flags=re.M))
        if stamps:  # the file's closing line only; any other *Updated:* line is part of the view
            last = stamps[-1]
            out = f"{out[: last.start()]}*Updated: {d:%B} {d.day}, {d.year}*{out[last.end():]}"
    return out, log


def _n(count: int, noun: str) -> str:
    return f"{count} {noun}{'' if count == 1 else 's'}"


def summary(log: dict, changed: bool) -> str:
    """Step 7's report, plus the orphans the run found."""
    lines = []
    if not changed:
        lines.append("VOCABULARY.md already matches vocabulary.yaml.")
    else:
        refreshed = log["refreshed"]
        names = f" ({', '.join(repr(t) for t in refreshed[:5])}{', ...' if len(refreshed) > 5 else ''})" if refreshed else ""
        lines.append(f"VOCABULARY.md: {_n(len(log['added']), 'row')} added, "
                     f"{_n(len(refreshed), 'definition')} refreshed{names}, {len(log['removed'])} removed.")
        if log["new_sections"]:
            lines.append(f"New sections: {', '.join(log['new_sections'])}")
    if log["orphans"]:
        verb = "removed" if log["removed"] else "kept; rerun with --orphans remove to drop them"
        shown = ", ".join(log["orphans"][:8]) + (", ..." if len(log["orphans"]) > 8 else "")
        count = len(log["orphans"])
        lines.append(f"{_n(count, 'row')} {'has' if count == 1 else 'have'} no entry in vocabulary.yaml "
                     f"({verb}): {shown}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="In-place `vocab regen-md` for a tutorial-creator project. "
                                             "A dry run unless --write is given.")
    ap.add_argument("tutorials_dir", help="the folder that holds vocabulary.yaml and VOCABULARY.md")
    ap.add_argument("--orphans", choices=("keep", "remove"), default="keep",
                    help="rows whose term is not in vocabulary.yaml: keep them (default) or remove them")
    ap.add_argument("--write", action="store_true", help="back up VOCABULARY.md, then write the result")
    args = ap.parse_args(argv)

    ypath = os.path.join(args.tutorials_dir, "vocabulary.yaml")
    mpath = os.path.join(args.tutorials_dir, "VOCABULARY.md")
    if not os.path.exists(ypath):
        return _fail(f"No vocabulary.yaml in {args.tutorials_dir}")
    if not os.path.exists(mpath):
        return _fail("There is no VOCABULARY.md. Building one from scratch is not implemented here; "
                     "use the skill's `vocab regen-md`.")
    try:
        with open(ypath, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []
    except yaml.YAMLError as ex:
        return _fail(f"vocabulary.yaml is malformed: {ex}")
    if not isinstance(entries, list) or not all(isinstance(e, dict) and isinstance(e.get("term"), str)
                                                for e in entries):
        return _fail("vocabulary.yaml must be a list of entries, each with a string `term`.")
    with open(mpath, encoding="utf-8") as f:
        before = f.read()
    try:
        after, log = regen(entries, before, orphans=args.orphans)
    except ReconcileError as ex:
        return _fail(str(ex))

    print(summary(log, changed=after != before))
    if after == before:
        return 0
    if not args.write:
        sys.stdout.writelines(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                   "VOCABULARY.md", "VOCABULARY.md (regenerated)"))
        print("\nDry run: nothing written. Add --write to apply.")
        return 0
    backup = f"{mpath}.bak-{dt.datetime.now():%Y-%m-%dT%H-%M-%S}"
    shutil.copy2(mpath, backup)
    tmp = mpath + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(after)
    os.replace(tmp, mpath)
    print(f"Wrote {mpath} (backup: {backup})")
    return 0


def _fail(message: str) -> int:
    print(f"regen_md.py: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

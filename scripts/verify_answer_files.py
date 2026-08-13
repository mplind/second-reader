#!/usr/bin/env python3
"""Structural verification of blinded tester answer files.

Run this on the parent (orchestrator) side BEFORE accepting a tester
deliverable. A bare "completed" summary from a subagent is never evidence: the
file must exist at the real path, parse, and satisfy the exact structural
contract that build_tester_brief.py's preamble instructed the tester to follow.

Place in the exam pipeline (step 5 of 5):
    1. verify_exam_seed.py    structurally checks the writer's claim ledger and exam
    2. build_tester_brief.py  strips the exam into a blinded tester brief
    3. split_brief_chunks.py  splits the brief into chunks plus controls
    4. the blinded tester answers each chunk file
    5. verify_answer_files.py (this script) checks the answer files before grading

For each answer file you pass, state its expected range:
    python3 verify_answer_files.py --file f1.md:QT:1:9 --file f2.md:QT:10:18 --file c.md:NC:1:6

Each --file spec is  <path>:<PREFIX>:<first>:<last>  where PREFIX is QT or NC.

Checks per file:
- Exists and non-empty.
- Exactly one '## <PREFIX><n>' header for every contiguous n in [first..last], no extras.
- No foreign block headers (a '## NC3' inside a QT file is a contract breach).
- INSIDE each block: exactly one '**ANSWER:**' and one '**WIKI SOURCE:**'
  line, each with a non-empty value. Counted per block, never globally: a
  file where one block carries two answers and another carries none has a
  clean global count and two broken blocks.

This catches the classic silent-truncation failure: a subagent that hit a
budget cutoff writes a partial file that "looks fine" if you only check counts
near the top.

Exits nonzero on any failure so it can gate a downstream dispatch.
"""
import argparse, re, sys, os

ANS = "**ANSWER:**"
SRC = "**WIKI SOURCE:**"


HEADER = re.compile(r"^## ([A-Za-z]+)(\d+)\b")


def check(path, prefix, first, last):
    problems = []
    if not os.path.exists(path):
        return [f"{path}: FILE MISSING"]
    lines = open(path, encoding="utf-8").read().split("\n")

    # Index every block header, whatever its prefix. A block ends at the
    # next header of ANY prefix, so a foreign block never donates its
    # lines to the block before it.
    starts = []
    for i, l in enumerate(lines):
        m = HEADER.match(l)
        if m:
            starts.append((i, m.group(1), int(m.group(2))))

    foreign = [f"{p}{n}" for _, p, n in starts if p != prefix]
    if foreign:
        problems.append(
            f"{path}: foreign block header(s) {', '.join(foreign)} "
            f"(this file's contract is {prefix} only)")

    hdrs = {}
    for _, p, n in starts:
        if p == prefix:
            hdrs[n] = hdrs.get(n, 0) + 1
    expected = list(range(first, last + 1))
    if sorted(hdrs) != expected:
        problems.append(
            f"{path}: headers {sorted(hdrs)} != expected {expected}"
        )
    dups = [n for n in sorted(hdrs) if hdrs[n] > 1]
    if dups:
        problems.append(
            f"{path}: duplicate headers (contract is exactly one per question): "
            + ", ".join(f"{prefix}{n} x{hdrs[n]}" for n in dups)
        )

    # Per-block field check: exactly one non-empty ANSWER and one non-empty
    # WIKI SOURCE inside every block. Never counted globally.
    for idx, (start, p, n) in enumerate(starts):
        if p != prefix:
            continue
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        block = lines[start:end]
        shared = [l for l in block if ANS in l and SRC in l]
        if shared:
            problems.append(
                f"{path}: {prefix}{n}: ANSWER and WIKI SOURCE share one line "
                f"(the contract is one field per line)")
        for marker, label in ((ANS, "ANSWER"), (SRC, "WIKI SOURCE")):
            hits = [l for l in block if marker in l]
            if len(hits) != 1:
                problems.append(
                    f"{path}: {prefix}{n}: {label} lines {len(hits)} != 1")
            elif not hits[0].split(marker, 1)[1].strip():
                problems.append(
                    f"{path}: {prefix}{n}: {label} value is empty")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", action="append", required=True,
                    help="path:PREFIX:first:last e.g. out.md:QT:1:9")
    a = ap.parse_args()
    all_problems = []
    for spec in a.file:
        # rsplit keeps colons inside the path out of the PREFIX:first:last tail
        parts = spec.rsplit(":", 3)
        if len(parts) != 4:
            all_problems.append(f"bad spec {spec}: need path:PREFIX:first:last")
            continue
        try:
            path, prefix, first, last = parts[0], parts[1], int(parts[2]), int(parts[3])
        except ValueError:
            all_problems.append(f"bad spec {spec}: need path:PREFIX:first:last")
            continue
        all_problems += check(path, prefix, first, last)
    if all_problems:
        print("VERIFY FAILED:")
        for p in all_problems:
            print("  -", p)
        sys.exit(1)
    total = 0
    for spec in a.file:
        parts = spec.rsplit(":", 3)
        total += int(parts[3]) - int(parts[2]) + 1
    print(f"VERIFY OK: all files structurally complete ({total} graded sections)")


if __name__ == "__main__":
    main()

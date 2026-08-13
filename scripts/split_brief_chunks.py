#!/usr/bin/env python3
"""Split a validated, blinded tester brief into bounded question chunks plus one controls file.

Long blinded tester runs are dispatched as small sequential chunks (for example
QT1..8, 9..16, 17..24, 25..32, then 33) plus a SEPARATE negative-controls file, so a tool
or budget cutoff cannot lose the whole run, and so the negative-control honesty
screen is scored independently of the real questions.

Place in the exam pipeline (step 3 of 5):
    1. verify_exam_seed.py    structurally checks the writer's claim ledger and exam
    2. build_tester_brief.py  strips the exam into a blinded tester brief
    3. split_brief_chunks.py  (this script) splits the brief into chunks plus controls
    4. the blinded tester answers each chunk file
    5. verify_answer_files.py checks the tester's answer files before grading

Input: a brief produced by build_tester_brief.py, already stripped of answer
keys, source locations, claim IDs, and [NEGATIVE CONTROL] labels. Block headers
are '## QT1 ...' and '## NC1 ...'. The preamble (everything before the first
block) is copied verbatim into every output so each chunk is self-contained.

Usage:
    python3 split_brief_chunks.py <brief.md> [--chunk-size N] [--out-dir DIR]
                                  [--prefix NAME] [--verify-only]

Defaults: chunk size 8, out-dir is the input's directory, prefix is the input's
basename minus '.md'. --verify-only writes nothing and re-checks the existing
output files against the brief, for re-gating outputs you suspect were damaged
after the split.

Writes:
    <out-dir>/<prefix>-chunk-1..K.md   real questions, contiguous QT runs of --chunk-size
    <out-dir>/<prefix>-controls.md     all NC blocks in their original order

Prints the QT/NC header list of every output file. Exits nonzero if any source
block (QT or NC) is missing from the outputs, duplicated, or out of range. The
check reads ONLY the output files this run is responsible for, never the input
brief and never stale files that happen to share the prefix, so a dropped block
cannot be masked by that block's presence elsewhere in the directory.

Never split the raw exam file: it still contains answer keys. Split only a
brief that build_tester_brief.py reported CLEAN. Observed in the campaign that
hardened this skill: a 33-question brief split into chunks of 8 (final chunk
smaller: 8/8/8/8/1) plus 7 negative controls, with no block lost across the run.
"""
import argparse
import os
import re
import sys

BLOCK = re.compile(r"^## (QT|NC)(\d+)")


def strip_trailing_separator(text):
    """Drop trailing '---' separator lines; write_file adds its own separators."""
    kept = text.rstrip().split("\n")
    while kept and re.fullmatch(r"[-_]{3,}", kept[-1].strip()):
        kept.pop()
    return "\n".join(kept).rstrip()


def parse_blocks(lines):
    """Return (preamble_text, blocks) where each block is (prefix, num, text)."""
    starts = []
    for i, line in enumerate(lines):
        m = BLOCK.match(line)
        if m:
            starts.append((m.group(1), int(m.group(2)), i))
    if not starts:
        return None, []
    preamble = strip_trailing_separator("\n".join(lines[: starts[0][2]]))
    blocks = []
    for idx, (prefix, num, start) in enumerate(starts):
        end = starts[idx + 1][2] if idx + 1 < len(starts) else len(lines)
        blocks.append((prefix, num,
                       strip_trailing_separator("\n".join(lines[start:end]))))
    return preamble, blocks


def output_paths(out_dir, prefix, n_qt, chunk_size, has_nc):
    """The exact set of files a split with these parameters produces."""
    n_chunks = (n_qt + chunk_size - 1) // chunk_size if n_qt else 0
    paths = [os.path.join(out_dir, f"{prefix}-chunk-{k}.md")
             for k in range(1, n_chunks + 1)]
    if has_nc:
        paths.append(os.path.join(out_dir, f"{prefix}-controls.md"))
    return paths


def write_file(path, preamble, blocks):
    parts = ([preamble] if preamble else []) + [text for _, _, text in blocks]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(parts) + "\n")


def normalize(text):
    """Whitespace-insensitive block identity: trailing space per line and
    leading/trailing blank lines carry no meaning; every other byte does."""
    return "\n".join(l.rstrip() for l in text.split("\n")).strip()


def expected_assignment(paths, qts, ncs, chunk_size):
    """The exact block sequence each output file must carry: chunk k gets the
    k-th contiguous slice of the QT sequence, the controls file gets every NC.
    """
    expected = {}
    chunk_paths = [p for p in paths if "-chunk-" in os.path.basename(p)]
    for k, start in enumerate(range(0, len(qts), chunk_size)):
        expected[chunk_paths[k]] = qts[start:start + chunk_size]
    if ncs:
        expected[paths[-1]] = list(ncs)
    return expected


def verify_outputs(paths, preamble, qts, ncs, chunk_size):
    """Check that every output file carries exactly its assigned blocks, in
    order, byte-equal after whitespace normalization, under the source
    brief's own preamble. Header presence alone is NOT enough: a truncated
    or edited body, an edited preamble (it carries the tester's closed-book
    contract), or a block parked in the wrong file must all fail here.

    Returns a list of problems (empty means clean).
    """
    problems = []
    expected = expected_assignment(paths, qts, ncs, chunk_size)
    for path in paths:
        if not os.path.exists(path):
            problems.append(f"{path}: output file missing")
            continue
        lines = open(path, encoding="utf-8").read().split("\n")
        got_preamble, blocks = parse_blocks(lines)
        if preamble and normalize(got_preamble or "") != normalize(preamble):
            problems.append(
                f"{path}: preamble differs from the brief "
                f"(it carries the tester's contract and must be verbatim)")
        want = expected.get(path, [])
        got_ids = [(pr, n) for pr, n, _ in blocks]
        want_ids = [(pr, n) for pr, n, _ in want]
        if got_ids != want_ids:
            problems.append(
                f"{path}: blocks {[f'{pr}{n}' for pr, n in got_ids]} != assigned "
                f"{[f'{pr}{n}' for pr, n in want_ids]}")
        want_bodies = {(pr, n): normalize(text) for pr, n, text in want}
        for pr, n, text in blocks:
            key = (pr, n)
            if key in want_bodies and normalize(text) != want_bodies[key]:
                problems.append(
                    f"{path}: {pr}{n} body differs from the brief "
                    f"(truncated or edited under an intact header)")
        print(f"  {os.path.basename(path)}: "
              f"QT {[n for pr, n in got_ids if pr == 'QT']} "
              f"NC {[n for pr, n in got_ids if pr == 'NC']}")
    return problems


def main():
    ap = argparse.ArgumentParser(
        description="Split a blinded tester brief into chunks plus a controls file.")
    ap.add_argument("brief", help="blinded brief produced by build_tester_brief.py")
    ap.add_argument("--chunk-size", type=int, default=8,
                    help="real (QT) questions per chunk (default 8)")
    ap.add_argument("--out-dir", default=None,
                    help="output directory (default: the brief's directory)")
    ap.add_argument("--prefix", default=None,
                    help="output filename prefix (default: brief basename minus .md)")
    ap.add_argument("--verify-only", action="store_true",
                    help="write nothing; re-check existing outputs against the brief")
    args = ap.parse_args()

    if not os.path.exists(args.brief):
        raise SystemExit(f"brief not found: {args.brief}")
    if args.chunk_size < 1:
        raise SystemExit("--chunk-size must be >= 1")
    out_dir = args.out_dir or (os.path.dirname(args.brief) or ".")
    prefix = args.prefix
    if prefix is None:
        prefix = os.path.basename(args.brief)
        if prefix.endswith(".md"):
            prefix = prefix[:-3]

    lines = open(args.brief, encoding="utf-8").read().split("\n")
    preamble, blocks = parse_blocks(lines)
    if not blocks:
        print("no ## QT/NC blocks found in brief")
        sys.exit(2)
    qts = [b for b in blocks if b[0] == "QT"]
    ncs = [b for b in blocks if b[0] == "NC"]

    paths = output_paths(out_dir, prefix, len(qts), args.chunk_size, bool(ncs))
    if not args.verify_only:
        os.makedirs(out_dir, exist_ok=True)
        chunk_paths = [p for p in paths if "-chunk-" in os.path.basename(p)]
        for k, start in enumerate(range(0, len(qts), args.chunk_size)):
            write_file(chunk_paths[k], preamble, qts[start:start + args.chunk_size])
        if ncs:
            write_file(paths[-1], preamble, ncs)

    print(f"source QT {len(qts)} / NC {len(ncs)} -> "
          f"{len(paths) - (1 if ncs else 0)} chunk file(s)"
          f"{' + controls' if ncs else ''} in {out_dir}")
    problems = verify_outputs(paths, preamble, qts, ncs, args.chunk_size)
    if problems:
        for p in problems:
            print(p)
        sys.exit(1)
    print("SPLIT OK: every source block present exactly once across the outputs")
    sys.exit(0)


if __name__ == "__main__":
    main()

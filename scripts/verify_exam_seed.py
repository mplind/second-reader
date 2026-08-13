#!/usr/bin/env python3
"""Parent-side structural verification of a WRITER's exam seed (ledger + exam).

The orchestrator must NOT rely on a subagent's "done" summary. Before building
the blinded brief, verify the two writer deliverables at their real paths:

1. The claim LEDGER is valid JSON with sequential/unique IDs, a kind on every
   claim (assertion, or qualifier whose 'conditions' names a real claim ID),
   tier counts that
   sum to total_claims, and every source_line/source_end inside the
   durable-text bounds.
2. The EXAM has contiguous ## QT# and ## NC# ranges, and every block carries
   real, answerable question PROSE plus exactly one each of Target claim IDs /
   Check / Correct (PASS|FAIL) / Wrong (FAIL): the prompt-presence gate. A
   block with only headers, tier metadata, and separators is NOT a usable
   question. Observed in the campaign that hardened this skill: a prose-less
   exam reached a tester, who answered topic headings and scored 14/32 on a
   structurally invalid test, voiding the run.

Place in the exam pipeline (step 1 of 5):
    1. verify_exam_seed.py    (this script) checks the writer's ledger and exam
    2. build_tester_brief.py  strips the exam into a blinded tester brief
    3. split_brief_chunks.py  splits the brief into chunks plus controls
    4. the blinded tester answers each chunk file
    5. verify_answer_files.py checks the tester's answer files before grading

Usage:
    python3 verify_exam_seed.py <ledger.json> <exam.md> [<durable.txt>]

Exit 0 = structurally sound seed. Exit 1 = any defect, printed to stdout.
Exit 2 = usage error.

This is a STRUCTURAL gate only. It does not check that figures are correct;
the grader does that against the durable source. It only guarantees the seed
is complete and well-formed enough that a blinded tester can actually answer
every question and a grader can grade every answer.
"""
import json
import re
import sys
import os


def verify_ledger(path, dur_lines=None):
    errs = []
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return [f"LEDGER {path}: not valid JSON ({e})"]
    claims = d.get("claims", [])
    n = d.get("total_claims")
    if n != len(claims):
        errs.append(f"LEDGER: total_claims {n} != len(claims) {len(claims)}")
    tiers = d.get("tiers", {})
    from collections import Counter
    # JSON tier-declaration keys are always strings; compare str(tier) so an
    # integer tier value in a claim still matches its declared count. Claims
    # with no 'tier' at all are excluded here (no crash) and named by the
    # missing-key check below.
    actual = Counter(str(c["tier"]) for c in claims if "tier" in c)
    if dict(sorted(actual.items())) != dict(sorted(tiers.items())):
        errs.append(f"LEDGER: tier counts {dict(actual)} != declared {tiers}")
    if sum(tiers.values()) != len(claims):
        errs.append(f"LEDGER: tiers sum {sum(tiers.values())} != {len(claims)}")
    ids = [c.get("id") for c in claims]
    if len(set(ids)) != len(ids):
        errs.append("LEDGER: duplicate claim IDs present")
    # sequential with a common numeric suffix (e.g. C001, C002, ...)
    nums = []
    for i in ids:
        m = re.search(r"(\d+)$", str(i))
        nums.append(int(m.group(1)) if m else None)
    if nums and any(x is None for x in nums):
        errs.append("LEDGER: some IDs lack a trailing numeric index")
    elif nums and nums != list(range(1, len(nums) + 1)):
        errs.append(f"LEDGER: IDs not sequential 1..{len(nums)} -> {nums}")
    if dur_lines:
        bad = [c.get("id") for c in claims
               if not (1 <= c.get("source_line", 0) <= c.get("source_end", 0) <= dur_lines)]
        if bad:
            errs.append(f"LEDGER: source_line/end out of durable bounds for {bad}")
    for k in ["id", "chapter", "claim", "source_line", "source_end", "tier", "kind"]:
        missing = [c.get("id") for c in claims if k not in c]
        if missing:
            errs.append(f"LEDGER: missing key '{k}' in {missing}")
    bad_kind = [c.get("id") for c in claims
                if "kind" in c and c["kind"] not in ("assertion", "qualifier")]
    if bad_kind:
        errs.append(f"LEDGER: kind must be 'assertion' or 'qualifier' in {bad_kind}")
    dangling = [c.get("id") for c in claims
                if c.get("kind") == "qualifier"
                and (c.get("conditions") not in {x.get("id") for x in claims}
                     or c.get("conditions") == c.get("id"))]
    if dangling:
        errs.append(f"LEDGER: qualifier 'conditions' must name a different existing claim ID in {dangling}")
    stray = [c.get("id") for c in claims
             if c.get("kind") == "assertion" and "conditions" in c]
    if stray:
        errs.append(f"LEDGER: 'conditions' is only legal on qualifiers, found on assertions {stray}")
    return errs


def verify_exam(path):
    errs = []
    lines = open(path, encoding="utf-8").read().split("\n")
    q_block = re.compile(r"^## (QT|NC)(\d+)")
    # Index of every block start
    starts = []
    for i, ln in enumerate(lines):
        m = q_block.match(ln)
        if m:
            starts.append((i, m.group(1), int(m.group(2))))
    if not starts:
        return [f"EXAM {path}: no ## QT/NC blocks found"]
    # Contiguity within each prefix
    from collections import defaultdict
    by_pref = defaultdict(list)
    for _, p, num in starts:
        by_pref[p].append(num)
    for p, nums in sorted(by_pref.items()):
        if nums != list(range(1, max(nums) + 1)):
            errs.append(f"EXAM: {p} range not contiguous 1..{max(nums)} -> {nums}")
    # Block completeness + prompt-presence + field presence
    for idx, (start, p, num) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        body = "\n".join(lines[start:end])
        # substantive prose beyond header/tier/separators
        prose = [ln.strip() for ln in lines[start + 1:end]
                 if ln.strip()
                 and not re.fullmatch(r"(?:\*\*)?Tier(?:\*\*)?:.*", ln.strip(), re.I)
                 and not re.fullmatch(r"[-_]{3,}", ln.strip())
                 and not ln.strip().startswith(("- **Target claim IDs:**",
                                                "- **Source location:**",
                                                "- **Check:**", "- **Correct",
                                                "- **Wrong (FAIL)**"))]
        if len(prose) < 1:
            errs.append(f"EXAM: {p}{num} has no question prose")
        for field in ["Target claim IDs", "Source location", "**Check:**",
                      "Correct (PASS", "Wrong (FAIL"]:
            if field not in body:
                errs.append(f"EXAM: {p}{num} missing field '{field}'")
    # NC blocks should carry the negative-control label in a real exam
    for start, p, num in starts:
        if p == "NC" and "[NEGATIVE CONTROL]" not in lines[start]:
            errs.append(f"EXAM: NC{num} missing '[NEGATIVE CONTROL]' header label")
    return errs


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    ledger, exam = sys.argv[1], sys.argv[2]
    dur_lines = None
    errs = []
    if len(sys.argv) > 3:
        dur = sys.argv[3]
        if os.path.exists(dur):
            dur_lines = sum(1 for _ in open(dur, encoding="utf-8", errors="ignore"))
        else:
            # A silently skipped bounds check would report SEED OK on an
            # unverified ledger; a missing durable text is an error.
            errs.append(f"{os.path.basename(dur)}: DURABLE {dur}: file not found, "
                        f"source_line/end bounds not checked")
    # Prefix each error with the file it came from, not the ledger for all.
    errs += [f"{os.path.basename(ledger)}: {e}" for e in verify_ledger(ledger, dur_lines)]
    errs += [f"{os.path.basename(exam)}: {e}" for e in verify_exam(exam)]
    if errs:
        print("SEED VERIFICATION FAILED:")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print(f"SEED OK: {os.path.basename(ledger)} ledger + {os.path.basename(exam)} "
          f"structurally sound")
    sys.exit(0)


if __name__ == "__main__":
    main()

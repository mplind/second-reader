#!/usr/bin/env python3
"""Parent-side structural verification of a WRITER's exam seed (ledger + exam).

The orchestrator must NOT rely on a subagent's "done" summary. Before building
the blinded brief, verify the two writer deliverables at their real paths:

1. The claim LEDGER is valid JSON with sequential/unique IDs, a kind on every
   claim (assertion, or qualifier whose 'conditions' names a real claim ID),
   coverage-tier counts that sum to total_claims, and every
   source_line/source_end inside the durable-text bounds. The canonical field
   names are 'coverage_tier' (per claim) and 'coverage_tiers' (the declared
   count map); the bare legacy names 'tier'/'tiers' are still read, but a
   ledger carrying both names with different values is ambiguous and fails.
2. The EXAM has contiguous ## QT# and ## NC# ranges, at least one NC block
   (no controls means no honesty screen), every Target claim ID resolving to
   a claim the ledger defines, and every block carrying
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
    try:
        return _verify_ledger_parsed(path, dur_lines)
    except Exception as e:
        # A malformed ledger is a finding, not a crash: a traceback here
        # would exit without the structured report downstream tooling gates on.
        return [f"LEDGER: malformed structure ({type(e).__name__}: {e})"]


def _verify_ledger_parsed(path, dur_lines=None):
    errs = []
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return [f"LEDGER {path}: not valid JSON ({e})"]
    if not isinstance(d, dict):
        return ["LEDGER: top level must be a JSON object"]
    claims = d.get("claims", [])
    if not isinstance(claims, list) or not all(isinstance(c, dict) for c in claims):
        return ["LEDGER: 'claims' must be a list of objects"]
    n = d.get("total_claims")
    if n != len(claims):
        errs.append(f"LEDGER: total_claims {n} != len(claims) {len(claims)}")
    # coverage_tier/coverage_tiers are canonical; tier/tiers are the legacy
    # names, still read. Both present with different values is ambiguous:
    # silently preferring one would hide a real disagreement.
    if ("coverage_tiers" in d and "tiers" in d
            and d["coverage_tiers"] != d["tiers"]):
        errs.append("LEDGER: 'coverage_tiers' and legacy 'tiers' disagree")
    tiers = d.get("coverage_tiers", d.get("tiers", {}))
    if not isinstance(tiers, dict):
        return errs + ["LEDGER: 'coverage_tiers' must be an object of "
                       "coverage tier -> count"]
    conflicted = [c.get("id") for c in claims
                  if "coverage_tier" in c and "tier" in c
                  and c["coverage_tier"] != c["tier"]]
    if conflicted:
        errs.append("LEDGER: 'coverage_tier' and legacy 'tier' disagree "
                    f"in {conflicted}")

    def claim_tier(c):
        return c.get("coverage_tier", c.get("tier"))

    from collections import Counter
    # JSON tier-declaration keys are always strings; compare str(tier) so an
    # integer tier value in a claim still matches its declared count. Claims
    # carrying neither name are excluded here (no crash) and named by the
    # missing-key check below.
    actual = Counter(str(claim_tier(c)) for c in claims
                     if claim_tier(c) is not None)
    if dict(sorted(actual.items())) != dict(sorted(tiers.items())):
        errs.append(f"LEDGER: coverage-tier counts {dict(actual)} != declared {tiers}")
    if sum(tiers.values()) != len(claims):
        errs.append(f"LEDGER: coverage-tiers sum {sum(tiers.values())} != {len(claims)}")
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
    if dur_lines is not None:
        bad = [c.get("id") for c in claims
               if not (1 <= c.get("source_line", 0) <= c.get("source_end", 0) <= dur_lines)]
        if bad:
            errs.append(f"LEDGER: source_line/end out of durable bounds for {bad}")
    for k in ["id", "chapter", "claim", "source_line", "source_end", "kind"]:
        missing = [c.get("id") for c in claims if k not in c]
        if missing:
            errs.append(f"LEDGER: missing key '{k}' in {missing}")
    untier = [c.get("id") for c in claims if claim_tier(c) is None]
    if untier:
        errs.append(f"LEDGER: missing key 'coverage_tier' (or legacy 'tier') in {untier}")
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
    try:
        return _verify_exam_parsed(path)
    except Exception as e:
        # Same principle as the ledger: malformed or unreadable input is a
        # finding with a structured report, never a traceback.
        return [f"EXAM: unreadable or malformed ({type(e).__name__}: {e})"]


def _verify_exam_parsed(path):
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
    if "NC" not in by_pref:
        errs.append("EXAM: no negative control (NC) blocks; "
                    "the honesty screen cannot run without them")
    if "QT" not in by_pref:
        errs.append("EXAM: no real (QT) question blocks; "
                    "an exam of only controls tests nothing")
    return errs


def verify_exam_targets(exam_path, ledger_path):
    """Foreign-key check: every 'Target claim IDs' entry in the exam must
    name a claim that exists in the ledger. The ledger is the denominator
    of the whole coverage gate; an exam aimed at IDs the ledger never
    defined tests nothing while looking complete.
    """
    try:
        d = json.load(open(ledger_path, encoding="utf-8"))
        ids = {str(c.get("id")) for c in d.get("claims", []) if isinstance(c, dict)}
    except Exception:
        return []   # the ledger checks already report this failure
    if not ids:
        return []
    try:
        text = open(exam_path, encoding="utf-8").read()
    except OSError:
        return []   # the exam checks already report an unreadable file
    targets, malformed = [], []
    for m in re.finditer(r"Target claim IDs:\*\*\s*([^\n]+)", text):
        for tok in re.split(r"[,\s]+", m.group(1).strip()):
            if not tok:
                continue
            if re.fullmatch(r"[A-Za-z]+\d+", tok):
                targets.append(tok)
            else:
                malformed.append(tok)
    errs = []
    if malformed:
        # A token that cannot be a claim ID is reported, never dropped:
        # dropping it turns a typo into a silently untested claim.
        errs.append("EXAM: malformed target claim ID token(s): "
                    + ", ".join(sorted(set(malformed))))
    unknown = sorted(set(targets) - ids)
    if unknown:
        errs.append(f"EXAM: target claim IDs not in ledger: {', '.join(unknown)}")
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
    errs += [f"{os.path.basename(exam)}: {e}" for e in verify_exam_targets(exam, ledger)]
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

#!/usr/bin/env python3
"""Build a BLINDED tester brief from a closed-book accuracy-exam file.

Strips everything that could tell the tester the answer or which questions are
negative controls: answer keys (Check:/Correct (PASS/FAIL)), Target-claim and
Source-location metadata, [NEGATIVE CONTROL] header labels, and control-tell
words that appear in question bodies.

Place in the exam pipeline (step 2 of 5):
    1. verify_exam_seed.py    structurally checks the writer's claim ledger and exam
    2. build_tester_brief.py  (this script) strips the exam into a blinded tester brief
    3. split_brief_chunks.py  splits the brief into chunks plus controls
    4. the blinded tester answers each chunk file
    5. verify_answer_files.py checks the tester's answer files before grading

Input: the writer's exam file, blocks headed '## QT<n>' / '## NC<n>', each
carrying question prose followed by answer-key metadata.
Output: a brief safe to hand to a source-blind tester. The brief's preamble
instructs the tester to answer in exactly the format verify_answer_files.py
parses, so step 5 can gate the deliverable mechanically.

Usage:
    python3 build_tester_brief.py <exam.md> [<out.md>]
Default out: <exam>-tester-brief.md (same dir).

It ASSERTS zero leak of tell-words AND that every block in the source exam
survived into the brief, counted per prefix (QT/NC). An NC block silently
dropped has nothing to leak, so atmosphere-leak checking alone cannot catch it.
Exits nonzero on a leak, a count mismatch, or a block left without question
prose.
"""
import re
import sys
import os
from collections import Counter

# Fragments that mark ANSWER KEY / metadata content. Ends the question body
# when seen on a line. This list must cover EVERY key/metadata field the exam
# format defines, in any order the writer emits them: the seed gate does not
# enforce field order, so a reordered key (a Wrong (FAIL) line first) must
# still end the body. Control-tell WORDS ("bait", "adjacent real", ...) are
# deliberately NOT here: a tell in a body line is rewritten below, never used
# to silently drop the line and everything after it.
BODY_ENDS = re.compile(
    r"Target claim|Source location|Check:|Correct \(|Wrong \("
    r"|\*\*Correct\*\*|\*\*ANSWER:|\*\*WIKI SOURCE:"
    r"|(?:\*\*)?Tier(?:\*\*)?\s*:",
    re.I,
)
# Prefix-matching is deliberate: "Correct (" instead of "Correct (PASS)" and an
# unanchored Tier, because a malformed key line (a missing paren, a mid-line
# tier tag) must still end the body. The cost is that question prose containing
# one of these fragments truncates the body and fails the prose gate loudly,
# which is the correct direction for a blinding gate to fail.
NC_HEADER = re.compile(r"\s*\[NEGATIVE CONTROL\]\s*")
Q_BLOCK = re.compile(r"^## (QT|NC)\d+")  # adapt to your exam's header scheme


def build_tester_brief(exam, out):
    lines = open(exam, encoding="utf-8").read().splitlines()
    blocks, cur = [], None
    for ln in lines:
        if Q_BLOCK.match(ln):
            if cur:
                blocks.append(cur)
            cur = [ln]
        elif cur is not None:
            cur.append(ln)
    if cur:
        blocks.append(cur)
    if not blocks:
        print(f"no ## QT/NC blocks found in {exam}")
        sys.exit(2)

    # Per-prefix block counts in the SOURCE (QT/NC): the denominator the
    # brief must reproduce. A brief missing every NC block looks clean (no
    # leak) but means the honesty screen never ran.
    src_counts = Counter()
    for blk in blocks:
        m = Q_BLOCK.match(blk[0])
        if m:
            src_counts[m.group(1)] += 1

    out_q, brief_counts = [], Counter()
    missing_prose = []
    for blk in blocks:
        # Replace the label with a space, then collapse runs, so stripping
        # '## NC1 [NEGATIVE CONTROL] Title' never glues the title onto the
        # block ID ('## NC1Title', or 'NC11885' for a digit-leading title).
        hdr = re.sub(r"\s+", " ", NC_HEADER.sub(" ", blk[0])).strip()
        body = []
        for ln in blk[1:]:
            if BODY_ENDS.search(ln):  # answer key / metadata has begun
                break
            body.append(ln)
        # A block with only its header, tier metadata, and separators is not a
        # usable question. Preserve the block for diagnostics but fail closed
        # below instead of silently turning a malformed brief into a topic-only
        # exam.
        prose = [
            ln.strip() for ln in body
            if ln.strip() and not re.fullmatch(r"(?:\*\*)?Tier(?:\*\*)?:.*", ln.strip(), re.I)
            and not re.fullmatch(r"[-_]{3,}", ln.strip())
        ]
        if not prose:
            m = Q_BLOCK.match(blk[0])
            missing_prose.append(m.group(0) if m else blk[0])
        # Remove control-tell wording from question bodies while preserving the
        # underlying question. NC prompts often contain words such as "bait";
        # leaving them in tells the tester which blocks are controls.
        q = (hdr + "\n" + "\n".join(body)).strip()
        q = re.sub(r"\bno sourced answer expected\b", "", q, flags=re.I)
        q = re.sub(r"\bplausible bait\b", "scenario", q, flags=re.I)
        q = re.sub(r"\bbait\b", "scenario", q, flags=re.I)
        q = re.sub(r"\badjacent real\b", "another question", q, flags=re.I)
        q = re.sub(r"\bnone as stated\b", "not stated", q, flags=re.I)
        if q:
            out_q.append(q)
            m = Q_BLOCK.match(blk[0])
            if m:
                brief_counts[m.group(1)] += 1

    # The answer format below is the exact contract verify_answer_files.py
    # parses: one '## <question id>' header, one '**ANSWER:**' line, and one
    # '**WIKI SOURCE:**' line per question. Change them together or not at all.
    pre = (
        "CLOSED-BOOK ACCURACY EXAM. TESTER BRIEF.\n\n"
        "Answer every question using ONLY the artifact (start at its index, follow "
        "links as a reader). Do NOT open the source, claim ledger, exam file, or use "
        "general knowledge. For each question give the precise figure/range/position "
        "the ARTIFACT states and where you found it. If it does not contain the "
        "answer, say exactly 'the artifact does not state this' and never supply a "
        "plausible answer from memory. Answer all questions.\n\n"
        "Write your answers to one Markdown file, one section per question, in "
        "exactly this format:\n\n"
        "## <question id, e.g. QT4>\n"
        "**ANSWER:** <the precise figure/range/position the artifact states, or "
        "'the artifact does not state this'>\n"
        "**WIKI SOURCE:** <the artifact page and section where you found it, or "
        "'none'>\n\n"
        "Emit exactly one **ANSWER:** line and one **WIKI SOURCE:** line per "
        "question; the deliverable is machine-checked and any deviation voids the "
        "run.\n\n---\n\n"
    )
    text = pre + "\n\n---\n\n".join(out_q)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)

    # Verdict 1: assert zero leak of any control/answer tell.
    # Observed in the campaign that hardened this skill: a writer once labeled
    # a control "[CONTROL-TELL]", which leaked past the canonical
    # "[NEGATIVE CONTROL]" strip and was not in this list. Catch any residual
    # [-TELL] / control-ish marker too, so a future non-canonical control label
    # fails the gate instead of reaching the tester.
    leaked = [
        t for t in ["NEGATIVE CONTROL", "CONTROL-TELL", "Target claim", "Source location",
                    "Correct (", "Wrong (", "**Check:**", "bait", "claim ID"]
        if t.lower() in text.lower()
    ]
    if re.search(r"(?i)(?:\*\*)?Tier(?:\*\*)?\s*:", text):
        leaked.append("Tier: metadata")
    if not leaked and re.search(r"\[[^\]\n]*TELL\]", text, re.I):
        leaked.append("bracket-[*-TELL]-marker")
    # Verdict 2: assert every source block survived, per prefix. This is the
    # loaded check: a script that strips [NEGATIVE CONTROL] tags AND deletes
    # the whole NC block leaves zero leak (nothing to leak) but a QT-only brief.
    mismatches = [
        f"{p}: {src_counts[p]} source / {brief_counts[p]} brief"
        for p in sorted(set(src_counts) | set(brief_counts))
        if src_counts[p] != brief_counts[p]
    ]
    print(f"brief blocks {dict(brief_counts)} <- source {dict(src_counts)} -> {out} ({len(text)} bytes)")
    if leaked:
        print("LEAK (TEST VOIDED):", leaked)
        sys.exit(1)
    if mismatches:
        print("BLOCK-COUNT MISMATCH (TEST VOIDED, honesty screen not reproduced):",
              ", ".join(mismatches))
        sys.exit(1)
    if missing_prose:
        print("MISSING QUESTION PROSE (TEST VOIDED, headings/metadata are not questions):",
              ", ".join(missing_prose))
        sys.exit(1)
    total = sum(brief_counts.values())
    print(f"CLEAN: no answer-key/control-tell leaked; all {total} blocks "
          f"({dict(brief_counts)}) preserved")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    ex = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else \
        os.path.splitext(ex)[0] + "-tester-brief.md"
    build_tester_brief(ex, out)

# Validation lessons

Three durable lessons from the campaign that hardened this skill. Each one was earned the
expensive way: a defect fired in production, the loop caught it, and the fix became a
standing rule. Each entry states the lesson, the failure it prevents, and the rule.

These lessons are linked from the known-failure-modes section of quality-loop.md.

---

## Lesson 1: the answer key gets a second read

### The lesson

A closed-book accuracy exam grades the vault against an answer key. That key is written by
a single writer from that writer's reading of the source. It is therefore an unverified
input to every downstream determination: what the grader grades against, what the vault is
judged against. In the campaign that hardened this skill, wrong key values were found in
shipped exams. Precedent is established: a key can be wrong, and when it is, every exam
that used it proved nothing.

### The failure it prevents

A wrong key silently fails right answers and silently passes wrong ones. The exam looks
rigorous, the verdict looks earned, and the whole apparatus of blinding and independent
grading is wasted because the reference itself was bad. Worse, the failure is invisible:
nothing in the grading process ever re-touches the key.

### The rule

The answer key is an input like any other and gets a second read. Before an exam's verdict
is relied on as strong evidence, a fresh reader independently re-verifies the key's values
against the durable source, blind to the writer's key.

**Scope.** Audit the high-stakes keys, not every question: the keys that bear on values
the owner acts on (quantities, caps, dates, load-bearing figures). Mechanics and trivia
keys can be sampled or skipped. When in doubt, include: the audit is cheap relative to a
poisoned key.

**The blind method.** The ordering is the whole point:

1. For each target question, read only the topic line or target claim IDs, not the key's
   answer.
2. Go to the authoritative durable source (`ops/text/<source>.txt`) and derive the value
   yourself: grep the exact figure or phrase, read the actual source line, write it down.
3. Only after deriving your own independent value, read the writer's key and compare.
4. Record per item: writer-key value vs independently derived value, with the durable line
   that settles it, then MATCH or MISMATCH.

If the reader looks at the key first, the key anchors the read and the second read is
contaminated: you read the source to confirm what the key already told you. Derive first,
compare second.

**What counts as a mismatch.**

- The key states a figure the durable source does not state: MISMATCH (key invented, or
  ported from elsewhere).
- The key states a figure the durable source states differently: MISMATCH.
- Attribution sensitivity applies. A value that exists somewhere in the vault but is
  attributed to a different source does not satisfy this source's key. Confirm the durable
  source carries the value in the key's role, quantity, and unit, not a
  same-digits-different-quantity collision (a weekly distance range vs a daily stage range
  with the same numbers, for example).
- Owner-state keys are correct when they match the owner's settled recorded facts, even if
  a source page phrases the topic differently. A key that reflects the owner's recorded
  constraint is a MATCH against that constraint, not a mismatch against the book.

**The inverse case: no key to audit.** Before auditing, confirm the exam actually carries
an inline answer key (search the exam file for the key marker and check the count). Some
exam files are question-only instruments with no key anywhere and no separate answers
file. In the hardening campaign, one exam returned zero key matches. For those: say so
plainly in the audit report rather than fabricating a comparison, mark each row "no writer
key to audit", and do not count it toward MATCH/MISMATCH totals. Absence on the key side
is as disabling as absence on the source side. Neither lets you certify the exam, and both
must be named, not papered over. The same holds when a durable text is absent for a target
exam: say so rather than guessing. Never "confirm" a key against a source you cannot read.

**Outcome interpretation.**

- KEYS-CLEAN: the exam's verdicts rest on verified input; the evidence stands as strong.
- KEYS-HAVE-MISMATCH: the impacted exams prove nothing until the key is corrected and the
  affected grades re-derived. Correct the key against the durable source, re-run only the
  affected questions, and record the correction in `ops/incident-log.md`.

Run the audit as a fresh reader in an isolated pass, with the blind method encoded
verbatim in the brief: the same independence discipline as every other role in the
pipeline. The writer's key is a map, not the sole authority.

---

## Lesson 2: fabricated vs inherited wrong content

### The lesson

A blinded vault-only tester does not always invent. When the vault itself asserts a wrong
figure, the tester is blinded to the source and will faithfully copy the vault. A wrong
answer on an exam item can therefore originate in the vault, not in the tester, and the
grading taxonomy must reflect the root cause, not the mere presence of a wrong number.

### The failure it prevents

Two opposite mistakes. First, blaming the tester for a defect the vault handed it, which
sends remediation to the wrong place. Second, and more dangerous, reading "the tester
fabricated nothing" as "the run is healthy". A clean-integrity reading is not
FABRICATION = 0. It is FABRICATION = 0 AND WRONG-CONTENT = 0. A run with zero fabrications
and one inherited wrong figure means the vault carries a bad number and the honest tester
surfaced it whole. That is a vault accuracy defect to fix, not a pass.

### The rule

When a grader finds wrong content, classify it before remediating:

- **The tester reproduced the vault's wrong value at the exact vault-stated figure:
  WRONG-CONTENT.** The vault's defect. The tester is not to blame, but the item still
  fails: accuracy grading fails the wrong number regardless of who wrote it. Remediation:
  correct the vault page against the durable source.
- **The tester supplied a number or claim the vault does not contain: FABRICATION.** The
  tester's fault (or the fault of an artifact upstream of it). Remediation: fix the tester
  or the upstream artifact, not the vault page.

These are different severities with completely different remediation paths, so the
verdict report carries exactly one taxonomy label per failed item, a vault-vs-source quote
pair for the offending text, per-category counts, and the required vault changes. The
grader names the fix; it never modifies vault pages itself.

**The flagship catch.** In the campaign that hardened this skill, a run scored
FABRICATION = 0, WRONG-CONTENT = 1: negative controls 6/6, and one real question failed
against the source (the full report, with both exam scores and the adjudication list, is
the worked example in examples/coverage-report.md). The single fail: a vault page confidently asserted that a long-distance ride of
1,913 kilometres was completed "in 7 days". The tester repeated it faithfully. The
blinded grader, re-reading the source cold, found the source's own completion phrasing:
the distance was covered in about five and a half days. The 7-day figure was the event
window, the period the attempt was framed within, and the vault had imported the window
label as the completion time. The number was real, the units were real, and the claim was still wrong.
Only a source-cold re-read caught it.

**The spot-verify pattern.** When a "how long / in what time" figure is up for grading,
distinguish (a) the category or window the feat is framed within from (b) the actual
completion metric the source states. Grep the durable text for the exact completion
phrasing ("after N hours", "by N a.m."), not just the category header.

**Two adjacent findings from the same run, kept because they generalize:**

- A qualification clause may be source-sourced rather than vault interpretation. When a
  task flags a qualifier as one or the other, grep the durable line first and check
  whether the vault holds it before grading.
- An honest non-answer is not a failure. When the vault legitimately omits a recommendation
  and the tester says so instead of inventing one, that is a correct decline. Do not
  penalize it.

---

## Lesson 3: the source-identity pre-check

### The lesson

Before any digest, confirm the converted text actually is the claimed work. A mislabeled
or corrupt file produces an excellent, fully cited, internally consistent synthesis of the
wrong thing, and every downstream safeguard then verifies the digest against the wrong
reference. Observed twice in one session of the hardening campaign; the class stopped
recurring once identity was checked first.

### The failure it prevents

The digest brief names one work; the durable file on disk is another. The brief's
required-coverage list then describes content the durable source does not contain. The
writer-side safeguards (serve the verifiable version; promote displaced items to negative
controls) catch it every time, but catching it in the writer is the expensive path: a full
cold read spent discovering a filing error.

Two distinguishable flavors, with different signatures:

**Flavor A: whole-work mislabel.** The brief says Book A by one author; the durable file
is a completely different work, Book B by a different author in a different domain. The
tell: grep the durable file for the brief's claimed author name and the claimed domain's
signature jargon. Zero hits across both means the coverage list describes a work the vault
does not hold. Recovery: confirm identity from the file's own title, copyright, and front
matter; cross-check the vault's source page (often already tagged correctly); rebuild the
coverage list around the real source. Do not slot-fill.

**Flavor B: same author, different edition or sibling volume.** The brief and the vault
source page agree on the durable file, but the coverage list was lifted from the same
author's other work in the same series. Book C's coverage list applied to its sibling. The
tell: grep the durable file for the other volume's signature terms and program names. Zero
hits means the coverage list belongs to the sibling. Identity was never the issue, only
content domain. Recovery: rebuild the coverage list around the real content, and promote
each displaced checklist item to a negative control ("this work prescribes X"). The wrong
coverage list is itself a ready-made list of likely cross-work baits. Use it defensively,
do not delete it.

### The rule

Before writing any source's required-coverage list:

1. Confirm identity from the vault source page's frontmatter (`author`, `year`, `title`,
   `source_type`). This is the fast correct first check, and the vault page is almost
   always tagged right.
2. Grep the durable text's head and front matter (title, copyright or edition year,
   author) and confirm it matches step 1.
3. Grep the brief's planned signature terms against that durable file and require real
   hits.
4. Log every recurrence as a defect-class entry in `ops/incident-log.md`.

The writer's cold re-read remains the backstop, not the primary guard. In the hardening
campaign, pre-verification proved out on the very next source: identity checked first, no
mismatch, and the defect class never fired again.

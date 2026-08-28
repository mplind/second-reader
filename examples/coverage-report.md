# Coverage report: Book B

A report from a real ingest. The domain and every figure are invented replacements
(the private vault's actual subject and sources stay private); the defect pattern, the
cycle structure, and the verdict language are exactly what the loop produced. Book B
stands in for a ~300-page long-distance cycling memoir.

Format per `references/coverage-instrument.md`, Report format section. This file is what
lands in `ops/ledger/<source>-claims.md` at bookkeep time, and it is never deleted.

---

```text
SOURCE       Book B - raw/books/book-b.epub
INGESTION    conversion verified | 214 claims extracted (31 qualifier-class)
CONTENT      strict 94.1% / adjudicated 97.1% | qualifiers 100% (7/7) | controls 6/6
VALIDATION   2 cycles | independence: level 2 (isolated subagent) | blind reader: 0 new findings
RESIDUALS    1, named below | 1 adjudicated up, listed
STATUS       SIGN-OFF - protocol 0.2, lint 0.2.0
```

---

## Cycle 1: VERDICT NEEDS-ANOTHER-PASS

**Extractor claim count:** 214 atomic claims, of which 31 qualifier-class
(exceptions, boundary conditions, caveats conditioning another claim)
**Tier distribution:** CORE 96 / CONTEXT 87 / ARCHIVE 31
**Density precondition:** 38 claims per 1000 lines, 9.5 sentences per claim. In norm
(Book B is the 9.5 calibration point in the instrument's worked examples).

**Five counters:**

| Counter | Value | Verdict |
|---|---|---|
| missing | 2 | FAIL |
| blocking_numeric_errors | 0 | clean |
| derived_unlabelled | 1 | FAIL |
| wiki_wrong | 1 | FAIL |
| not_answerable | 0 | clean |

**Closed-book exam:** 34 real questions. Strict score 88.2% (30 full, 3 partial,
1 fail). Adjudicated score 94.1% (32/34: the 2 partials named below adjudicated up).
Below the 95% target; the named-residual test was not attempted because counter
failures already block. Negative controls: 6/6.

**Qualifier-class coverage:** 7 of 34 questions target qualifier claims: 5 full, 1
partial (Q27), 1 fail. Separate strict score 71.4% (5/7), well below the bar. The
wiki_wrong finding and the failed question both concern the same qualifier claim: the
completion-time caveat. This line exists because an aggregate 88.2% can hide exactly
this.

**Adjudication list (cycle 1):**

- Q11 (CONTEXT): partial adjudicated up; the answer named the mechanism and missed the
  year, which the page carries as a dated fact. Not material.
- Q19 (ARCHIVE): partial adjudicated up; anecdote detail, page cites the source location.
  Not material.
- Q27 (CORE): partial NOT adjudicated; the missing half is the claim the wiki_wrong
  finding concerns. Material, fail stands.

**Blind reader findings:** 3 items a wiki reader would not know. Two resolve with the
missing-claims fixes below; one judged ARCHIVE-tier and logged to `open-loops.md` with a
cross-reference from the affected page.

**Defect findings (verdict 2, by failure mode):**

1. **Over-firming (mode 3), blocking.** Grader taxonomy per
   `references/validation-lessons.md`: FABRICATION = 0, WRONG-CONTENT = 1.
   `wiki/concepts/distance-record.md:12` states the
   ride as "1,913 kilometres in 7 days". Source (Book B, ch. 7) states the distance was
   covered in about five and a half days. The 7-day figure is the event window the
   attempt was framed within; the page imported the window as the completion time. The
   citation resolves; the claim is still wrong. Classified per
   `references/validation-lessons.md`: inherited from the digest's chapter notes, not
   invented at page-writing time, so the remediation is a chapter re-read, not a spot
   fix.
2. **Missing (coverage), blocking, two elements.** The source's stated rationale for
   the second attempt (ch. 9) appears nowhere in the vault; the concept page covers the
   attempt but not why it was made. And the stage-by-stage distance table (ch. 11
   appendix) has no representation, not even a source-page summary note. A reader of
   the wiki would need the source for both.
3. **Unlabelled interpretation (mode 5).** `wiki/concepts/maintenance-schedule.md:31`
   presents a per-week average the source never computes. Correct arithmetic, sourced
   inputs, but derived and unlabelled. Relabel as a calculation with its basis stated.

**THIN items:** 1 (the ch. 9 rationale, raised by the candidate generator). Closed by
the cycle 2 fix; no second-auditor immateriality call needed.

**Instruction to the next digest pass:** re-read ch. 7, ch. 9, and the ch. 11 appendix completely; fix the
three findings above; touch nothing else without re-validation.

## Cycle 2: VERDICT SIGN-OFF

**Five counters:** missing 0, blocking_numeric_errors 0, derived_unlabelled 0,
wiki_wrong 0, not_answerable 0. All clean, asserted per check.

**Closed-book exam:** 34 real questions. Strict score 94.1% (32 full, 2 partial,
0 fail). Adjudicated score 97.1% (33/34). Above target with the residual named.
Negative controls: 6/6.

- Q31 (CONTEXT): partial adjudicated up; the answer resolved a figure by pointer to the
  source's appendix table, which the page records as a pointer fact. Not material.
- Q19 (ARCHIVE): partial NOT adjudicated; named residual. Anecdote detail, judged
  immaterial to the owner, reason on record. This is the named-residual test doing its
  job: the score stops at 97.1% and the shortfall is on the record, not in an average.

**Qualifier-class coverage:** the same 7 questions: 7 full. Separate score 100%
(7/7). The caveat the cycle 1 exam caught missing is now on the page that acts on it.

**Blind reader:** re-run fresh. No new findings, asserted clean.

**THIN items:** 0.

**Lint:** clean (run after the cycle 2 fixes, before this validation).

**Cycles run:** 2 of 5.

**Provenance seal** (two-step: the exam run writes the MANIFEST line via
`python3 scripts/manifest_hash.py <vault>`; whoever commits replaces `pending`
with the commit id from the vault's own history):

```
MANIFEST sha256:b0cdec11b180be364fe5991bd6b146f4e2be2fdfd666c84a1d5253a0083b8296
COMMIT 3f81c2e
```

---

What this report is for: six months from now, the owner can open this file and see what
was checked, what failed, what the fix was, and what the residual is. A vault you can
audit is a vault you can trust.

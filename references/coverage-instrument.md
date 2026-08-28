# The coverage instrument

How we MEASURE whether a reader of the wiki could skip the source, and, critically,
whether the extraction was *thorough*, not just fluent. This replaces the unfalsifiable
question "would a reader need the source?", which produced opinion, not evidence, and
let validators wave gaps through as "non-blocking." The output here is evidence, and it
is comparable across sources because it has a denominator.

Read this before any ingest. A source is not signed off until the acceptance gate and the
closed-book exam both pass on a SINGLE iteration.

## Contents

- [Why this exists](#why-this-exists)
- [The acceptance gate](#the-acceptance-gate-single-iteration-all-of-the-following-conditions-must-hold)
- [Part 1: Candidate generation](#part-1-candidate-generation-aiming-the-exam)
- [Part 2: Closed-book exam](#part-2-closed-book-exam-retrievability-and-correctness)
- [Exam pipeline tooling](#exam-pipeline-tooling)
- [Part 3: Tiering](#part-3-tiering-weight-by-relevance-kept)
- [Blind reader test](#blind-reader-test-mandatory-every-source)
- [Thin items (two-auditor rule)](#thin-items-two-auditor-rule)
- [No-subagent fallback](#no-subagent-fallback)
- [Why a percentage matters](#why-a-percentage-matters-and-how-it-got-dropped-the-error-on-the-record)
- [Named gap list vs scores](#resolving-report-a-named-gap-list-vs-report-scores)
- [Persisting the coverage report](#persisting-the-coverage-report-never-deleted)
- [Report format](#report-format-mandatory-every-source-no-exceptions)
- [Conversion ledger contract](#conversion-ledger-contract)

---

## Why this exists

The old bar was unfalsifiable. A validator could always decide a gap was "not core" and
wave it through. Exactly that happened on Book A, where ten coverage gaps passed as
"non-blocking" (nine were later shown to be false positives, one was a real, blocking
missing table). A standard that cannot be proven wrong will be satisfied by opinion.

The corrected fix has TWO parts, and both are mandatory:

1. **Five zero-tolerance counters** that must all read 0: the structural-coverage
   check, the numeric-accuracy check, the derived-unlabelled check, the misleading-content
   check, and the answerability check. These are the *completeness/accuracy* gate.
2. **A closed-book exam with a percentage target (95%) bound by a named-residual test.**
   The percentage is the *retrievability/denominator* signal. It is the only way to
   compare a thorough extraction against a shallow one across sources.

**A percentage is NOT rejected. It is KEPT (95%) and BOUND by a named-residual test.**
The two work together: the percentage gives a comparable signal; the named-residual test
prevents a number from hiding a material gap. The history of this error is recorded at the
bottom of this file so a future run does not drop the number again.

---

## THE ACCEPTANCE GATE (single iteration, all of the following conditions must hold)

**PRECONDITION, DENSITY-VS-CLAIMS (MANDATORY, before the counters and the exam).**
The extractor is the one component nothing else audits, and it is the ceiling on everything
downstream (matcher, exam, blind reader are all bounded by what the extractor captured). The
density check is the first mechanical check ON the extractor. Run it BEFORE any counter or
exam. **Never run the counters on a bad denominator.** Two signals, BOTH must be in norm:

```
claims_per_thousand_lines = (extractor_claim_count / source_line_count) * 1000   # volume signal
sentences_per_claim        = (sentence_boundaries / extractor_claim_count)        # granularity signal
```

- **Corpus norm:** for a book-length source, ~30–43 claims per 1000 lines AND ~7.5–9.5
  sentences per claim (the fine-extraction cluster measured across Book B at 9.5, Book C
  at 8.5, Book D re-extracted at 7.5). These numbers were calibrated on one corpus;
  recalibrate on your own first two or three sources before treating the band as binding.
- **`sentences_per_claim` is the sharper discriminator of the two.** A coarse/thin extractor
  shows up as a HIGH sentences-per-claim ratio (a handful of claims each aggregating dozens of
  sentences) even when its claims-per-1000 falls inside the volume norm. Always compute BOTH.
- **Flag if:** claims/1000 is materially below norm (~≤15), OR sentences/claim is materially
  above norm (~≥15–20, i.e. one claim per 15+ sentences of prose). Either is a thin/coarse
  extraction: **re-extract before running anything else.** Never run the counters on a bad
  denominator.

**WORKED EXAMPLES (from the campaign that hardened this skill):**
- **Book D, caught by the volume signal.** 105 claims / 11,395 lines = 9.2 cpk and
  35.3 sent/claim, vs the ~43/7.5 cluster. Both signals flagged. Re-extracted to 492 claims
  (43 cpk, 7.5 sent/claim), inside norm.
- **Book E, caught by the GRANULARITY signal only.** Its claims/1000 (32) was
  inside the volume norm and looked fine, but **sentences/claim = 45.2** (5x the 8.5 norm),
  one claim per ~45 sentences, i.e. a handful of claims each aggregating a huge block of prose.
  Volume-only checking would have missed it; the granularity check caught it. Re-extraction
  required.
- Lesson: without BOTH signals, the next thin extraction passes unnoticed under a plausible
  claims-per-1000. This check is standing because it is the only mechanical guard on the
  extractor's universe.

A source is DONE only when the acceptance gate returns, on a SINGLE iteration:

```
missing = 0
  No structural element of the source unaccounted for. Chapter, major section, table,
  protocol, worked example. Map the source's own structure and verify each element has
  representation in the wiki.
blocking_numeric_errors = 0
  No figure in the wiki that does not match the source.
derived_unlabelled = 0
  No calculated figure presented as though it were sourced.
wiki_wrong = 0
  Nothing misleading, and no asserted contradiction that is not real.
not_answerable = 0
  On material content, in the closed-book exam.

CLOSED-BOOK EXAM: TARGET 95%, BOUND BY A NAMED-RESIDUAL TEST.
  - PARTIAL answers are permitted below 95%, but ONLY where each remaining partial is
    individually named in the result with a stated reason it is immaterial to the owner.
  - A source at 92% with every shortfall named and genuinely immaterial PASSES.
    A source at 96% with one material failure DOES NOT.
  - You cannot pass a source by asserting immateriality without naming the item.
  - The judgement goes on the record, not into an average, so the owner can audit the calls.

QUALIFIER COVERAGE: REPORTED SEPARATELY, SAME BAR.
  - The exam score for qualifier-class claims (qualifications, exceptions, boundary
    conditions, counterarguments) is computed and reported as its own number, holding
    the same 95% + named-residual standard. An aggregate score can hide a vault that
    kept every headline and lost every caveat; the separate number cannot.

THIN ITEMS: either closed, or corroborated as immaterial by a SECOND INDEPENDENT
AUDITOR with its reason recorded. Never silently dropped. Two auditors, not one.
```

**The judgment (what to close, what is immaterial, and why) goes on the record**, in
the report, so the owner can audit each call. It does NOT vanish into an average.

**The exam target and the counters hold at every tier.** Tiering (below) changes what
*closing* a gap requires; it never changes the bar.

---

## Part 1: Candidate generation (aiming the exam)

Completeness and retrievability in this instrument form ONE composed process: a matcher
that GENERATES candidates, an exam that ADJUDICATES them. They are not two independent
passes run in parallel against the whole source; that was the original design and it was
too heavy and too blind.

### Roles

- **Extractor** (subagent A): reads the source, extracts factual claims, frameworks,
  protocols, and specific recommendations into a structured claim list. Each claim gets
  a unique ID and a source location, and each claim is marked as one of two kinds:
  **assertion** (a claim standing on its own) or **qualifier** (a qualification,
  exception, boundary condition, or counterargument that conditions another claim; it
  records the ID of the claim it conditions). The extractor NEVER looks at the wiki.
  **The claim count the extractor returns is the denominator of the whole gate. Report
  it, with the qualifier-class count broken out.** Qualifiers get their own dimension
  because they are exactly what gist-style compression silently drops, and exactly what
  changes a decision (see `references/evidence.md`, section 7).
- **Candidate generator** (subagent B, the former "matcher"): reads the claim list and
  the wiki, and flags claims that look thin or ABSENT. It does NOT produce final
  verdicts and does NOT need to be accurate. It is cheap: chunked so it cannot time out.
  Its only job is to point the exam at likely gaps. Noise is acceptable here because the
  exam adjudicates it.
- **Exam writer** (subagent C): has read the source. Writes exam questions that TARGET
  the generator's candidates, plus a few CONTROL questions on claims the generator
  scored covered (to catch a generator that is over-flagging). Qualifier-class claims
  get at least their proportional share of questions; an exam that tests only headline
  assertions certifies a vault that has lost its exceptions.
- **Tester** (subagent D): has NOT read the source. Answers the exam using ONLY the wiki,
  navigating as a reader would.
- **Blind reader** (subagent E): a FRESH subagent who has read the source but gets NO
  claim list, no candidate flags, and no tier tags. One instruction: "Name ten things in
  this book that a reader of the wiki would not know." This is the only check NOT bounded
  by what the extractor happened to find, and the extractor's universe is the one thing
  nothing else audits. **Run it on every source.**
- **Auditor** (orchestrator): reconciles exam failures into the wiki or `open-loops.md`.

### BOUND EVERY SUBAGENT: design for the ceiling

A 4,950-line book is potentially thousands of claims. The digest that crashed at 30
minutes was unbounded. **Every pass must be chunked so it returns well before the
timeout**: extractor section by section, generator in claim-list chunks, exam writer in
question batches. A pass that times out loses only its chunk, not the audit. On the first
calibration run, a single matcher subagent classifying all 485 claims at once timed out;
chunking fixes that.

### Why matcher → exam must be COMPOSED, not parallel

The original design ran matcher and exam in parallel and independent. Two failures
followed: the matcher was too heavy (timed out on the full claim list), and the exam
sampled blind (the single CONTEXT gap it found was luck of question selection, not aim).

Composing them fixes both. The matcher becomes a cheap candidate generator whose noise
stops mattering, because the exam adjudicates it. And the exam stops sampling blind: it is
aimed exactly where gaps are likely. **Adversarial, not random:** the generator proposes
where the wiki is weakest, and the writer attacks those points rather than guessing.

### Inputs and outputs

- **Input:** source text (converted), wiki pages, the CORE/CONTEXT/ARCHIVE tags.
- **Output (generator):** a candidate list: claim IDs the exam should test, with reasons
  (thin / absent / tier).
- **Output (exam):** coverage report: question, target claim, verdict (COVERED /
  COVERED-BY-POINTER / UNCOVERED / PARTIAL), source page or "not found".
- **COVERED-BY-POINTER verdict:** a claim resolved by a pointer is COVERED, not partial
  and not a gap. If the wiki answers with a typed page field `pointer: <fact> -> <where>`
  telling the reader exactly where to get the current value (e.g. "ask the owner"), then
  a reader of the wiki knows precisely how to obtain the fact, which is what the coverage
  bar actually asks. This is the third verdict beside covered/uncovered; a pointer is
  deliberately NOT an open-loops item (open-loops is for gaps, unanswered questions, and
  material to retrieve; a pointer is the opposite of a gap). A pointer verdict is only
  valid if the `pointer:` field actually names where to get the fact; a pointer with no
  destination is partial.
- **Output (blind reader):** a list of (up to ten) things a wiki reader would not know.
  These are the triage for how much remediation is needed. The blind reader determines
  how much REMEDIATION is needed; it does NOT determine whether to run the gate.
- **Pass condition:** the acceptance gate above: all five counters = 0, the exam
  passes the 95% + named-residual test, qualifier-class coverage passes the same bar
  separately, and THIN items are closed or twice-audited immaterial.

### CALIBRATION NOTE: what the first run actually established

The bounded extractor completed clean in ~24 minutes on the exact book that crashed one
digest at 30 min, and the exam proved it discriminates (found one real CONTEXT gap the
old sign-off missed). But restate the outcome with discipline:

- **The exam discriminates.** It found one real CONTEXT gap (a specific mechanism from
  the source had not been distilled onto any page) that the old sign-off missed.
- **CORE passed on the SAMPLED topics.** All 8 CORE exam questions were answerable.
- **Completeness is UNVERIFIED.** The matcher (the entire completeness half) timed out,
  and the mechanical word-ratio substitute was too noisy. 8 exam questions against 485
  claims is a ~3% sample. There was NO basis to claim "zero CORE gaps" from that run.
  This is why the corrected gate REQUIRES the `missing = 0` structural counter and the
  blind reader: they audit the completeness universe the old sampled exam could not.

---

## Part 2: Closed-book exam (retrievability AND correctness)

A wiki can contain every claim and still be unusable: the right fact on the wrong page,
under a title no one would look under. Retrievability is separate from completeness, and
the exam measures it. Under the composed design, the exam does NOT sample blindly: it is
aimed at the generator's candidates, so its questions test exactly where gaps are likely.

**The exam grades CORRECTNESS, not just answerability.**
The historical exam scored "was the question answerable and where was the answer found";
nobody graded the answer against the source, so a wiki full of confidently wrong content
scored 100% and never failed. Four changes:

1. **Grade correctness.** The question writer, who has read the source, marks each
   returned answer **right or wrong against the source**. A wrong answer is a failure,
   not a pass. Answerability alone proves nothing.
2. **Blind the question writer.** The writer must NOT be the digest and must never see
   the digest's self-map (nor the extractor's claim list's "what was captured" framing).
   Questions asked by the agent that knows what it captured produce exactly the observed
   signature: 100% forever. The writer is an independent pass over the source + the
   candidate list.
3. **Negative controls.** Include questions the wiki *should not* be able to answer (a
   plausible-sounding non-fact, a figure from the source the wiki deliberately must not
   have, a fabrication bait). A tester that never fails is indistinguishable from a
   tester that always says yes. Correctly declining a negative control is a pass; it also
   detects the model that gold-plates every answer.
4. **Minimum question count**, scaled to claim count (e.g. ~1 question per 10–15 claims,
   with a hard floor of ~15, and a difficulty floor: questions must be provenance-level,
   not headline-echo), so a huge source can't be waved through on a tiny easy sample.

- **Writer** (subagent C): an INDEPENDENT pass that HAS read the source but did NOT build
  the wiki and does NOT see the digest self-map. Writes exam questions that TARGET the
  candidate list, plus a set of **negative controls**, plus CONTROL questions on claims
  the generator scored covered. Each question carries the source location that resolves it.
  Phrase questions as a reader would ask them for the owner's actual goal.
- **Tester** (subagent D): has NOT read the source and has NOT seen the questions before.
  Answers using ONLY the wiki, navigating it as a reader would (start at index, follow
  links, no deliberate string search). The tester must not be the author of the wiki
  pages or the writer of the exam.
- **Grade** (writer C, or a fresh grader): mark each answer RIGHT or WRONG against the
  source at its location. Score = number correct / total real questions; negative
  controls are scored separately as the honesty screen and never enter the
  denominator. A wrong answer is a failure regardless of whether the right fact exists
  elsewhere if the tester didn't reach it.
- **Score:** **two numbers, always reported**: the **strict score** (machine/keyword-answerable
  percentage) AND the **adjudicated score** (after allowing each flagged miss to be resolved
  on the record). The strict score is the default, unadjudicated number; the adjudicated
  score is what passes the exam. Both go in the report, every time, alongside each other.
- **Adjudication rule (from the owner's review):** the named-residual rule says a source
  cannot pass by asserting immateriality without naming the item. The SAME applies to
  adjudicating an exam failure into a pass: **every exam item that is not
  strictly-answerable must be individually named with its reason** (keyword phrasing,
  en-dash tokenization, genuinely partial, etc.) before it can be adjudicated UP to the
  passing score. You cannot resolve a strict failure into a pass without naming the item
  and the reason. If the strict and adjudicated scores diverge a lot, that is a signal
  about the exam's construction (ambiguous questions, phrasing brittleness): report it
  visibly rather than resolving it silently.
- **Named-residual:** every question not fully answered (the residual) is individually
  named with a stated reason it is immaterial to the owner, OR it is a material failure,
  in which case the source does NOT pass. A source at 92% with every shortfall named and
  genuinely immaterial PASSES. A source at 96% with one material failure DOES NOT.
  Partial answers are permitted only where each is individually named with a reason.

The designer, generator, writer, and tester must be four independent subagents. The
tester must not be the author of the wiki pages or the writer of the exam. The blind
reader is a FIFTH independent subagent, kept separate from the extractor so its attention
is not captured by the extractor's claim list.

---

## Exam pipeline tooling

Four scripts in `scripts/` operationalize the exam pipeline, with a dispatch step between them. They are deterministic,
stdlib-only structural gates, and every one exits non-zero on failure so it can gate the
next dispatch. **Scripts are run, not read into context.** They are tools; treat their
output as the deliverable.

**One run, one directory.** Every exam run writes its artifacts (brief, chunks,
controls, answer files) into its own directory, unique per source and seed revision,
e.g. `ops/exam/<source>-<revision>/`. Two runs sharing a directory is how one run's
stale chunk becomes another run's evidence. The scripts enforce this: an output that
already exists is refused (exit 2) unless `--overwrite` says the clobber is
deliberate, files are written atomically (temp file, then rename, so a cut-off run
leaves no torn half), and each writing step records a run manifest
(`<out>.run.json` for the brief, `<prefix>-run.json` for the split) carrying the
sha256 of its input and of every output. The manifests chain: exam to brief, brief
to chunks, so any artifact resolves back to the exact seed it came from.

`scripts/run_structural_gates.py` runs steps 1-3 below as one command into a fresh
run directory and stops before dispatch and grading; `references/runbook.md` holds
the operator's full order with the artifacts that prove each step.

Run order for one source:

1. **`verify_exam_seed.py <ledger.json> <exam.md> [<durable.txt>]`**, the seed gate. Run
   it on the orchestrator side the moment the exam writer reports done, before anything
   downstream. A subagent's "completed" summary is never evidence: the files must exist
   at the real path, parse, and satisfy the format contract below. This is a structural
   gate only; it does not check that figures are correct. The grader does that against
   the source. Observed in the campaign that hardened this skill: a writer once delivered
   an exam whose blocks were headers and metadata with no question prose; the tester
   answered topic headings and scored 14/32 on a structurally invalid test. The
   prompt-presence check exists because of that run.
2. **`build_tester_brief.py <exam.md> [<out.md>]`**, the blinding step. Builds the
   tester brief from the validated exam by stripping everything that could tell the
   tester an answer or reveal which questions are controls: answer keys (`Check:`,
   `Correct (PASS/FAIL)`), `Target claim` / `Source location` metadata, `[NEGATIVE
   CONTROL]` header labels, and control-tell wording inside question bodies ("bait"
   becomes "scenario"). It asserts two verdicts and voids the test on either failure:
   zero leak of any tell, and per-prefix block survival (every QT and NC block in the
   exam appears in the brief, counted separately). The count assert is load-bearing: a
   brief that silently drops every NC block shows zero leaks, because there is nothing
   left to leak, but the honesty screen never runs. Also observed in the hardening
   campaign: a writer labeled a control with a non-canonical `[CONTROL-TELL]` tag that
   slipped past the standard strip, so the leak check now fails on any residual
   bracketed `-TELL` marker as well.
3. **`split_brief_chunks.py <brief.md> [--chunk-size 8] [--out-dir DIR] [--prefix P]`**,
   the bounding step. Splits the validated brief into contiguous chunks of real
   questions (default 8 per chunk) plus ONE separate controls file holding all negative
   controls, so a tool or budget cutoff loses only a chunk, never the run, and the
   honesty screen is scored independently. Its dropped-block check reads back exactly
   the output files it wrote, never a directory scan, so a shared prefix or a stale
   file cannot mask a drop; `--verify-only` re-gates existing outputs. Never split the
   raw exam file: it still contains answer keys. Observed in the hardening campaign: 33
   real questions split into chunks of 8 (final chunk smaller) plus 7 controls.
   Tell-words appearing in question prose are rewritten in place by the brief builder;
   the run is voided only if a tell survives rewriting.
4. **Dispatch** each chunk to the blinded tester as its own bounded task. Administer the
   controls file separately and score it independently.
5. **`verify_answer_files.py --file <path>:<PREFIX>:<first>:<last> ...`**, the
   acceptance gate on the tester's output. Run it on the orchestrator side BEFORE
   accepting any tester deliverable or dispatching the grader. It catches the classic
   silent-truncation failure: a subagent that hit a budget cutoff writes a partial file
   that looks fine if you only check counts near the top.

### File format contract

The scripts and the briefs they gate agree on one contract. Writers, testers, and graders
must produce files in exactly this shape:

- **Claim ledger** (`<source>-claims.json`): valid JSON with keys `total_claims`
  (must equal the length of `claims`), `coverage_tiers` (a coverage-tier-to-count map
  whose values sum to `total_claims` and match the actual per-claim counts), and
  `claims`, an array where every claim carries `id`, `chapter`, `claim`,
  `source_line`, `source_end`, `coverage_tier`, and `kind` (`assertion`, or
  `qualifier` with a `conditions` field naming the ID of an existing claim it
  qualifies). `coverage_tier` is a closed enumeration: `CORE`, `CONTEXT`, `ARCHIVE`.
  The numeric aliases `1`/`2`/`3` map onto them so existing ledgers still verify;
  they are deprecated, and new ledgers use the names. Any other value fails the seed
  gate. The bare legacy names `tier`/`tiers` are still read for existing ledgers; a
  ledger carrying both names with different values fails as ambiguous. A claim may
  also carry `sensitivity`; its vocabulary belongs to the vault owner (Part 3), so
  the seed gate checks shape only: a non-empty string. IDs are unique and end in a sequential
  numeric index running 1..N (e.g. `BK001`..`BK492`). Every `source_line`/`source_end` pair must satisfy
  1 ≤ source_line ≤ source_end ≤ the durable text's line count.
- **Exam file**: question blocks headed `## QT<n>` (real questions) and `## NC<n>`
  (negative controls), each prefix contiguous from 1. Every NC header carries the literal
  label `[NEGATIVE CONTROL]`. Every block contains substantive question prose (headers,
  tier metadata, and separators do not count) plus exactly one each of the fields
  `Target claim IDs`, `Source location`, `Check:`, `Correct (PASS)`, and `Wrong (FAIL)`.
- **Tester brief**: the exam minus every answer key, metadata field, control label, and
  tell word, with a preamble instructing the tester to answer from the artifact alone
  and to say "the artifact does not state this" rather than supply an answer from
  memory. Per-prefix block counts must equal the exam's.
- **Answer files**: for the stated range, exactly one `## QT<n>` (or `## NC<n>`) header
  per question, and exactly one `**ANSWER:**` and one `**WIKI SOURCE:**` line per
  question. Contiguity and counts are checked at the tail too, not just the top.

---

## Part 3: Tiering (weight by relevance; kept)

**Vocabulary.** "Tier" in this instrument always means COVERAGE depth: the
CORE/CONTEXT/ARCHIVE tags below, carried in ledgers and reports as
`coverage_tier`. It is not a sensitivity classification. A vault that classifies
material by who may read it uses a separate field with its own closed enumeration,
e.g. `sensitivity: public | personal | restricted`, and never overloads
`coverage_tier` for it: the two answer different questions (how deep to capture vs
who gets access), and one field serving both is how an access rule silently becomes
a depth decision. The `sensitivity` enumeration is defined by the owner in the
vault, not by this instrument; the seed gate therefore validates its shape only (a
non-empty string per claim) and leaves the vocabulary to the vault's own contract.

Not all material deserves the same depth. Apply the CORE/CONTEXT/ARCHIVE tags to WHAT
CLOSING A GAP requires:

- **CORE** (directly serves the owner's actual goal): full faithful capture, zero
  exceptions. A caveat missing from a recommendation page is a blocking gap.
- **CONTEXT** (useful background): a named gap may be closed by a summary rather than
  full capture.
- **ARCHIVE** (specialist material not applicable to the owner): summary coverage on the
  source page is sufficient, and the summary must say what it is summarising so a future
  reader knows what is not there.

**A CORE-tier shortfall is material by definition.** It can never be adjudicated
immaterial and never passes the named-residual test; the residual mechanism exists for
CONTEXT and ARCHIVE items only. The owner's core theses and the claims that serve their
actual goal are covered fully or the source is not signed off.

**Tiering changes the remedy, never the bar.** The five counters hold at every tier
(`missing = 0` means no *structural element of the source* is unaccounted-for; a
structural element that is ARCHIVE is accounted for by its source-page summary note, but
it is still named, not dropped). The exam target (95% + named-residual) holds at every
tier. `not_answerable = 0` applies to material content regardless of tier.

**Reasoning behind the tiers (do not collapse them back into one).** Sources arrive as
provided, not as curated: a vault will ingest books whose chapters include deep
specialist protocols the owner will never follow. Chasing full capture of that ARCHIVE
material spends the expensive instrument on knowledge the owner will never use. The tags
exist so the instrument concentrates on what the owner acts on. Tiering begins where the
counters end: structural completeness is absolute (missing = 0), then tiering decides the
DEPTH of each element's capture.

---

## Blind reader test (MANDATORY, every source)

- **Subagent:** fresh, independent. Gets the source text and the wiki. NO claim list, NO
  candidate flags, NO tier tags.
- **Instruction (verbatim):** "Name ten things in this book that a reader of the wiki
  would not know."
- **Purpose:** the only completeness check NOT bounded by the extractor's universe. The
  extractor decides what counts as a claim; if it never noticed something, no downstream
  pass (matcher, exam) will either. The blind reader audits that exact blind spot.
- **Use:** triage for remediation. Whatever the blind reader names that is genuinely
  absent or thin is remediation work. The blind reader determines how much remediation
  is needed; it does NOT determine whether to run the gate. Every source gets the five
  counters and the exam regardless of what the blind reader finds.

---

## THIN ITEMS (two-auditor rule)

A THIN item is either (a) **closed**, given faithful capture, or (b) corroborated as
**immaterial** to the owner by a SECOND INDEPENDENT AUDITOR, with its reason recorded.
Never silently dropped. Two auditors, not one: the primary validator's judgment is not
enough to retire a thin item; a second, independent auditor must agree it is immaterial
and say why. The corroboration and its reason go on the record.

**How to get a genuine second auditor:** independence is defined by the second auditor
being a FRESH, separate context that forms its own view from source + wiki alone, not by
*who* spawns it, and NOT by auditing a report. The second auditor receives
**source + wiki + gate spec** and is explicitly told **the wiki may contain recent edits of
unknown quality** (the remediation pass may have introduced defects). It forms its own view
from scratch. It NEVER sees the first auditor's report and NEVER sees the remediation notes.
Its job is to audit the CURRENT STATE OF THE WIKI against the source, not to check whether
the first auditor's findings were addressed. Duplicate findings are acceptable and even
good; a missed regression is not. The audited party (parent orchestrator) both remediates
and dispatches, so nobody else checks those edits; this is the mechanism that closes that
gap. Two valid topologies:
- **Parent-orchestrated (safest):** the parent dispatches the second auditor as a separate
  top-level delegation with the clean current-state prompt above.
- **Per-source orchestrator (where your runtime allows nested delegation):** a neutral
  per-source orchestrator runs the gate and dispatches the second auditor as a fresh
  sibling with the same clean current-state prompt (source + wiki + gate, explicitly
  flagging recent-edits-of-unknown-quality).
Guardrail that holds in both: **the audited party never grades its own work.** The first
auditor / orchestrator must never be the one to approve its own THIN-item calls or spawn
its own "second opinion." A self-graded second opinion is not an independent auditor.

**Topology split, what stays at parent level (from the owner's review):** your runtime's
spawn-depth and concurrency allowances exist for **parallelism and routine per-source
work** only; respect its limits when fanning out. Two decisions stay at PARENT level
always, guarded by topology, not by a rule you have to remember:
1. **THIN-item immateriality adjudication**: the final call that a thin item is genuinely
   immaterial to the owner rests with the parent, informed by the second auditor's
   independent judgment, never with the source's first auditor.
2. **Final sign-off**: only the parent commits on sign-off. A source-orchestrator may run
   the gate and remediate, but it cannot self-close a source.
This mirror-topology guard is the defense against rule-based guarding failing (the same
error class recurred twice in the hardening campaign under exactly that kind of
rule-based guarding).

---

## No-subagent fallback

This instrument names six independent contexts: extractor, candidate generator, exam
writer, tester, blind reader, second auditor. When the runtime cannot spawn parallel
subagents, independence degrades per the capability ladder in
`references/quality-loop.md`: run each role as a SEQUENTIAL fresh-context pass, where
each pass starts a new context that receives ONLY that role's permitted inputs (the
tester never sees the source, the blind reader never sees the claim list, the second
auditor never sees the first auditor's report or the remediation notes). A single
continuous context playing every role is a degraded audit; label it degraded in the
report, and never describe it as independent. What compensates in degraded mode is a
stricter stance on borderline calls, because blindness between sequential passes is
simulated rather than enforced: every borderline verdict resolves toward the gap. An
answer that might be covered is PARTIAL, a thin item that might be immaterial stays open,
an answer whose correctness is uncertain grades WRONG. See quality-loop's fallback
section for the full ladder; do not restate or relax it here.

---

## Why a percentage matters, AND how it got dropped (the error, on the record)

A raw percentage hides the distribution of uncovered claims. "94% covered" does not say
"the uncovered 6% includes the one caveat on the page the owner actually reads." That is
why the percentage must be BOUND by the named-residual test: the residual names every
shortfall so the number cannot hide a material gap.

But the percentage itself is not the enemy. **Without a denominator there is no comparable
signal across sources.** Every ingest reports "clean" and nothing distinguishes a thorough
extraction from a shallow one. That is the room in which surface-checking hides, and
removing the number is what created it.

**The porting error:** this instrument's design was first written in a different vault
and later ported to this one. The port was written from a summary of the design rather
than re-validated against the original page, and it inverted a rule: "a percentage alone
is insufficient" became "a percentage is rejected." It also dropped the five
zero-tolerance counters entirely; one of them, `missing = 0`, is the structural-coverage
check that was later re-proposed as if new, though it had been in the original design all
along. The original design KEPT 95%: when the target proved costly, lowering it to 93%
or 90% was on the table and was declined; the shape of the test was tightened instead,
and the named-residual test was added ON TOP as a binding constraint, not as a
replacement.

**The general lesson:** porting a wiki page between vaults is an ingest, not a copy.
Re-validate the ported page against the destination's sources, or against the original
page treated as the source, exactly as you would validate any new ingest. A port that
skips the gate can silently invert a load-bearing rule, and the inversion reads fluently,
so nobody catches it until the rule fails.

**Why it is written here:** so a future run (and any future auditor) knows the number is
deliberate. The percentage is the denominator, the cross-source comparable, and the score
the owner audits. Do not drop it. If the 95% target ever proves costly, the recorded
options are to tighten the shape of the test (the chosen path), not to silently remove
the number.

---

## Resolving "report a named gap list" vs "report scores"

The instrument says both "Do not report a score; report a named gap list" and "report
strict and adjudicated scores." Both are right, stated plainly:

- **The named gap list is the gate.** A source passes or fails on it. The verdict rests
  on whether every material gap is named and either closed or genuinely immaterial, item
  by item.
- **The strict score is a comparability signal**, reported always, never adjudicated away.
  It is how you detect an instrument that has stopped discriminating (the "100% forever"
  signature). A falling strict score is a warning about the exam, not something to hide.
- **Adjudication of a strict failure is done by the second auditor, item by item, named.**
  The orchestrator may not argue its own failures up to 100%. If the writer/orchestrator
  must resolve a strict miss, that miss goes to the independent second auditor; the
  author of the content never grades its own correctness.

## Persisting the coverage report (never deleted)

Claim lists are generated at real cost (thousands of claims per book) and have historically
been used once and deleted, so "passed the gate" reverted to an assertion. **Every coverage
report is written to `ops/ledger/<source>-claims.md` (or `.json`) and NEVER deleted.** It
carries, per claim, the claim ID, its source location, the tier, the verdict/evidence. This
is the audit trail; it makes re-verification cheap and enables cross-source claim
comparison.

- **Reconciliation at write time:** claim IDs must be contiguous (no silent gaps), and each
  section of the source must be accounted for with per-section counts. A section that
  silently returned short is detectable at write time, not later. Report the reconciliation
  in the coverage report.
- The vault gate re-runs the reconciliation from the persisted ledger (see
  `references/vault-gate.md`). A source whose gate claimed a claim count but has no ledger
  is not fully signed off.

### The provenance seal (two-step, because the commit id does not exist yet)

The exam runs before the commit, so a report that records only a commit hash records
something the run could not have known, and a placeholder left in that field turns
"committed" into an assertion. Every report therefore carries a two-step record:

```
MANIFEST sha256:<64 hex>
COMMIT pending
```

- **Step 1, written by the exam run itself:** the MANIFEST line, computed by
  `python3 scripts/manifest_hash.py <vault>` (sha256 over the sorted per-file hash
  lines `<sha256(file)>  <relpath>` for `AGENTS.md` and everything under `wiki/`).
  It is immutable evidence of the exact content the exam examined, and nobody edits
  it afterwards.
- **Step 2, appended by whoever commits:** replace `pending` with the commit id.
  **Sign-off is not valid evidence while `pending` remains**; a report claiming
  SIGN-OFF over a placeholder fails the seal check.
- `python3 scripts/verify_report_seal.py <report.md>` enforces the structure: one
  well-formed MANIFEST line, one COMMIT line, and no SIGN-OFF over a pending commit.
  To audit the manifest itself, re-run `manifest_hash.py` against the vault at the
  recorded commit and compare.

---

## Report format (MANDATORY, every source, no exceptions)

Every report opens with the verdict card: six lines a reader can absorb in ten
seconds, with the full evidence underneath. The card never replaces the detail;
it fronts it.

```text
SOURCE       <title> - <raw/ path>
INGESTION    conversion verified | <N> claims extracted (<q> qualifier-class)
CONTENT      strict <s>% / adjudicated <a>% | qualifiers <q>% | controls <k>/<k>
VALIDATION   <c> cycles | independence: level <n> (<rung>) | blind reader: <m> findings
RESIDUALS    <count>, each named below | <count> adjudicated up, listed
STATUS       <SIGN-OFF or NEEDS-ANOTHER-PASS> - protocol <v>, lint <lint version>
```

Below the card, every source report contains, without exception:

- claim count from the extractor, with the qualifier-class count broken out
- tier distribution: CORE / CONTEXT / ARCHIVE
- the five counter values (missing / blocking_numeric_errors / derived_unlabelled /
  wiki_wrong / not_answerable)
- exam question count, **strict score (%) AND adjudicated score (%)**, the named residual
  list AND the adjudication list (every non-strictly-answerable item individually named
  with its reason for being adjudicated up), each marked material=fail where applicable
- qualifier-class coverage: question count aimed at qualifier claims, their separate
  score, and any qualifier residuals individually named
- blind reader findings, itemised
- THIN items and which second auditor cleared them (with reason)
- cycles run, and the provenance seal (below): the `MANIFEST sha256:` line the exam
  run wrote and the `COMMIT` line appended at commit time
- the independence record, per role (next section); the card's `independence: level
  N (<rung>)` is the MINIMUM level across the roles
- the protocol version (from `SKILL.md` frontmatter) and `lint.py --version` output

### The independence record (per role, verdict at the minimum)

One recorded level cannot say WHICH role ran weak. "Level 2" over a whole gate hides
a tester that shared the writer's session, and that is the role whose independence
the exam's meaning rests on. The report therefore records every role separately:

| Role | Provider | Model id | Context | Permitted inputs | Relation to writer | Level |
|---|---|---|---|---|---|---|

One row per role the instrument names (extractor, candidate generator, exam writer,
tester, blind reader, second auditor). Per column:

- **Provider / Model id:** the exact id string the runtime reports, never a family
  name; "same model" blind spots are only auditable from exact ids.
- **Context:** what isolated it: a fresh subagent (with its identity if the runtime
  gives one), a forked context, or the same continuous session.
- **Permitted inputs:** what the role was actually given, so a blinding breach is
  visible in the record rather than remembered.
- **Relation to writer:** none, same provider, same model, same session; the writer
  here is whoever built the wiki content under audit.
- **Level:** the quality-loop ladder rung this role actually ran at.

**The verdict's level is the minimum across the rows**: one role that shared the
writer's context caps the whole audit at level 0, whatever the other five achieved.

## Conversion ledger contract

The conversion precondition (INGEST step 0) writes
`ops/ledger/<source>-conversion.md`. Conversion sits inside the trusted chain: a
perfect loop over a damaged conversion validates the damage. The entry therefore
records, for every source:

- the original file's SHA-256, byte size, and (where the format exposes it) page count
- the converter used and its version
- the durable text's SHA-256 and line count
- page anchors: the durable text preserves source position markers as
  `<!-- p.N -->` comment lines at every page or chapter boundary the format
  exposes, so citations and exam source bounds resolve to a place a human can check
- extraction warnings: every page under ~50 extracted characters (the image-only
  signature), repeated header/footer strings, suspected encoding loss
- the table and figure inventory, each with its preservation decision
- the reconciliation sample: which distinctive values were checked against the
  original, and the result

**A verdict without these numbers is not a verdict.** The exam reports BOTH scores and
the full adjudication list; a strict failure resolved into a pass is named item-by-item,
never silent. If a source cannot reach the gate, say what is short and why rather than
softening the bar. The contract's own words: "Do not soften a criterion to reach it; if it
cannot be met, say what is short."

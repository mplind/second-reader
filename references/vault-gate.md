# The vault gate

Every per-source gate (INGEST) examines one source; the VAULT GATE examines the vault as
a whole: the cross-source defects that no single-source pass can see (index, synthesis,
bookkeeping, contradictions, currency).

Run it before any major downstream use of the vault (a briefing, a persona file, anything
the owner acts on) and on a schedule. It does NOT look at any single source.

## Status after review: TWO hard checks, SEVEN deferred

An owner review during the campaign that hardened this skill cut the gate to the two
checks that are real today. The other seven are recorded as **deferred, method needed**,
NOT deleted: each stub names what a real method would have to solve, so whoever builds it
knows the problem. Shipping a check with no working method is false assurance, which is
worse than no check.

### HARD CHECK 1: index set-difference (implemented)

The index is the canonical entry a reader, tester, or QUERY starts at. Report **TWO
SETS**, not one count and not a "difference of zero" that can hide one omission plus one
phantom:

- **SET A, pages absent from the index:** content pages (any page under a `wiki/`
  subfolder: entities, concepts, sources, decisions) that are NOT linked from `index.md`.
- **SET B, index entries with no page:** `[[links]]` in `index.md` that resolve to no
  existing page (phantoms).

A "difference of zero" is not a pass: it must be **SET A empty AND SET B empty**. This is
the **direct** check (linked-from-index), not the transitive reachability check.
Transitive reachability is a separate and weaker property: it is what lint's orphan check
covers, and it must never be substituted for this one, because a page reachable through
three hops of concept links is still missing from the canonical entry. Mechanical
enforcement: `ops/lint.py` `check_index_completeness` (the index set-difference, each missing page named).

### HARD CHECK 2: bookkeeping truth, in BOTH directions (implemented)

Forward (page to entry): every page that claims something is "logged in contradictions"
or "in open-loops" must have a real entry behind it. Including **collective** claims: a
page asserting "these are logged in X" must ENUMERATE the items or the claim fails. A
collective completeness claim is only falsifiable for the whole set, and a spot-check of
any single item passes while the set fails.

Reverse (entry to page), the check earlier versions of this gate never had, added after
the gap surfaced in the campaign that hardened this skill: when an item is marked
RESOLVED or closed, find every page that cites it and verify NONE still describes its
subject as open. A resolved open-loops item is exactly the signal that some page is now
stale, and without this direction it is not being used as one.

Mechanical piece: `ops/lint.py` `check_bookkeeping_truth` (forward). The reverse direction
and the collective-enumeration check are run by the vault gate's fresh agent at gate time
(they need page-citation resolution across the whole vault).

### DEFERRED: method needed (recorded intent; do not implement as a false pass)

- **Cross-page value consistency.** Would detect two pages giving different values for the
  same attribute. Problem to solve: needs attribute extraction AND entity resolution across
  the vault; if entity names vary, it silently under-reports (which the name-variance
  backstop partially covers, but not value-consistency). No working method yet; do not gate
  on it.
- **Currency / review horizon.** The as-of lint backstop already flags dated figures
  stated without `as_of`/`PENDING`. What does NOT exist is a review-horizon concept: no
  definition of how long a dated fact stays current, who sets it, whether per-fact or
  per-class, or where it is stored. Build that first, then gate on it.
- **Contradiction propagation.** Verify every contradiction's "Bears on" names every page
  that acts on the disputed claim. Problem: requires knowing which pages act on disputed
  claims, which means citation resolution plus semantic match. Partially covered by lint
  cross-ref; the propagation-failure case needs a method. Deferred.
- **Synthesis truth, falsity half.** Lint's `Synthesis currency` already proves every
  source in sources.md is cited. What is NOT implemented: detecting that synthesis asserts
  something false about the vault's own state (e.g. "X not yet ingested" when X is). Needs
  a method to check assertions against the page inventory. Deferred.
- **Relational/causal-structure coverage.** Would verify the vault preserves the
  relationships between claims (causal chains, evidential support, goal structure), not
  only the claims themselves. The retention literature shows integrated structure is
  what durable comprehension is made of, and isolated-proposition coverage understates
  it (see `references/evidence.md`, section 7). Problem to solve: needs a method for
  extracting and comparing relational structure between source and vault without
  degenerating into a second full ingest. No working method yet; do not gate on it.
- **Judgment/transfer benchmark.** Would test whether decisions made from the vault
  match decisions made from the full source, which coverage alone cannot establish (the
  one relevant clinical trial found a specialty where full text beat summaries for
  decisions). Problem to solve: needs decision tasks with gradable outcomes per
  subject domain. No working method yet; do not gate on it.
- **Open-loops volume plausible against claim volume.** Problem to solve: must NOT be a
  bare word/claim ratio. Calibration work in the campaign that hardened this skill
  established that ratio heuristics are untrustworthy. Needs a real definition of
  "plausible volume" or it silently reimports the heuristic. Deferred (do not gate on it).

A vault that fails either hard check is not ready to be used for anything the owner acts
on. A deferred check that is not yet implemented is recorded as such; it is NOT a pass.

## Assert clean, or fail

Every check returns a per-check verdict, stated explicitly. Absence of a finding must be
asserted **"clean"**, never implied by omission. "Test run" is not a verdict. For the hard
checks, report the named sets and items; a check that silently passes because it was not
run is the same defect as a failing check.

## Loop-close enforcement

The gate checks, via `wiki/log.md`, that the **last recorded event for each ingested
source is a clean validation**, not a fix or a "corrected" pass standing in for a clean
round. A remediation with no subsequent clean round does not count as signed off.

## Relationship to per-source INGEST

INGEST proves one source is faithfully captured. The VAULT GATE proves the captured
sources compose into a sound whole. They are complements. A vault with twelve clean
ingests and a stale index or synthesis fails the gate and is not used for anything the
owner acts on.

## Ledger reconciliation

Reconcile each `ops/ledger/<source>-claims.md/json`: contiguous claim IDs and per-section
counts against the source. A source whose gate claimed a claim count but has no ledger is
not fully signed off.

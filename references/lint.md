# The lint instrument

`ops/lint.py` is the mechanical gate every source (and every ingest round) and the vault
gate rely on. It is specified HERE so a silently weakened lint is detectable, not a
filename run and trusted. "Lint CLEAN" is only meaningful if this specification holds.

The shipped implementation is `ops/lint.py`. It ships with the skill and is installed
into each vault's `ops/` directory at SCAFFOLD time, so every vault carries its own copy
and every gate can run it locally.

## Non-negotiable: the fixture test

**A deliberately broken sample vault must exist, and `ops/lint.py` MUST FAIL on it.**
A lint that passes the broken fixture is broken. The skill repo carries two fixture
vaults:

- `fixtures/clean-vault/`: a small, valid vault. Lint must PASS it with zero findings.
- `fixtures/dirty-vault/`: a small, synthetic vault that deliberately violates every
  check below that can have one (a broken link, an illegal frontmatter
  `type`, a template placeholder, an index that omits a page, a synthesis that misses a
  processed source, an undated dated-fact, a name-variance dup, a split wikilink, a
  contradiction entry with an illegal `Kind`, a stub bookkeeping file, an untrue
  bookkeeping claim, an orphan page unreachable from the index, a filename pair
  differing only in separator style, an illegal source status). Lint must FAIL it and
  report the documented findings: every plant is listed with its location in the
  fixture's own `PLANTED.md`, and the exact expected output of both runs is recorded
  verbatim in `fixtures/EXPECTED.md`. The dirty vault also carries two planted defects
  lint must NOT flag (a prompt-injection passage quoted inertly, and a flat assertion
  where the source hedges); they exist for the semantic validator, and a lint that
  flags them is over-reaching.

After ANY modification to `ops/lint.py`, run it against both fixtures before trusting a
single result: `fixtures/clean-vault` must pass, `fixtures/dirty-vault` must fail with
the documented findings. If either assertion inverts, lint is broken. The pair catches
both false-negatives (missed defects) and false-positives (a check that flags
everything).

## The checks (every one, no silent omission)

1. **Wikilink resolution.** Every `[[link]]` target resolves to an existing page by
   filename, frontmatter `title`, or alias, case-insensitive.
2. **Line-broken wikilinks.** Every `[[wikilink]]` on a single line.
3. **Frontmatter completeness.** Every content page has `sources:` (with at least one
   real entry; an empty list is NOT "present") and `updated:`; `type`/`title`/`confidence`
   where the schema requires them.
4. **Template placeholders.** No scaffold placeholder strings remain in any body.
5. **Bookkeeping cross-reference truth.** Every page claiming something is "logged in
   contradictions" or "in open-loops" has a real entry; must not match only literal
   exactly-typed phrases (prose variants must be caught). Lint is a backstop here; the
   validator and vault gate own the real check.
6. **Bookkeeping non-stub.** Index, sources, log, contradictions, open-loops, synthesis
   are populated, not scaffold stubs.
7. **Index completeness (page to index).** The count of unique pages linked from
   `index.md` equals the count of content pages. **Report the difference (how many
   missing, which), not a boolean.** This is the direction that used to never fire: a page
   omitted from the index still had inbound links from concept pages, so the link-to-page
   test passed while the page was missing from the canonical entry.
8. **Synthesis currency (vault-gate support).** Synthesis references every source in
   `sources.md`; its `confidence` is not `low` when the evidence no longer warrants it.
9. **Currency as-of (the facts-carry-time rule).** Any fact carrying `as_of:` is dated;
   alert on page bodies that state measured or time-bound figures (a measured value, a
   current status, a dated quantity) that are neither `as_of`-dated nor `PENDING`-marked.
   A shelf-life alert on dated facts held too long is deliberately NOT implemented: the
   vault gate records the review-horizon concept as deferred because no horizon
   definition exists yet, and alerting on an undefined horizon would be false assurance.
10. **Name variance (lint-owned, auto, every run; a vault-gate cross-page check is deferred).** Flag two different renderings of
    the same entity or concept used as if distinct across pages.
11. **Contradiction kind.** Every `###` entry in `contradictions.md` carries a `Kind:`
    field whose value is one of `direct-conflict`, `temporal-change`, `granularity`. A
    missing or out-of-list value fails. Also flag any `temporal-change` or `granularity`
    entry still marked `Status: unresolved`, since both kinds resolve when written and a
    stale `unresolved` makes the reverse-direction gate read them as live disputes.
12. **Orphan detection.** Flag every content page unreachable from `index.md` by
    following wikilinks transitively. This is deliberately separate from check 7 and does
    not replace it: a page can be reachable through three hops of concept links yet
    missing from the index (check 7 fires, this one does not), and a page in a
    disconnected cluster is invisible to any reader who starts at the canonical entry
    (this one fires). Report the unreachable pages by name.
13. **Filename collision.** Two pages whose filenames differ only in case or in
    word-separator style (hyphen, underscore, space; e.g. `Working-Memory.md` and
    `working memory.md`) are flagged as probable duplicates. Case-insensitive wikilink
    resolution (check 1) makes the pair silently interchangeable, so half the vault's
    links can land on one copy and half on the other while both drift.
14. **Source status legality.** Every data row in `sources.md` carries a status from
    `unprocessed`, `in-progress`, `processed`. Anything else fails. This exists to
    protect check 8, which keys off `processed`: an unrecognized status would silently
    exempt a source from the synthesis-currency check, and a silent exemption is the
    exact failure mode this instrument exists to prevent.

15. **Vault walk integrity (`vault-walk`).** Directory symlinks under `wiki/` are
    reported as `symlinked directory not scanned` and never followed, so content behind a
    symlink can never lint CLEAN invisibly. Pages that are not valid UTF-8 are reported
    as `unreadable file (invalid UTF-8)` rather than crashing the run. An unexpected
    internal error exits 2, never 1: exit 1 always means findings.

## Known implementation traps (observed in a real lint; avoid all of these)

Every one of these is the same mistake: **the check measured the neighbourhood of the
answer instead of the answer.** Before writing a check, state the literal string a passing
result contains. If you cannot state it, you are writing a proxy, and a proxy that passes
tells you nothing. Every trap below passed while the thing it was meant to prove was
false.

This is why the fixture pair is non-negotiable: a check that cannot fail on the dirty
fixture is a check that measures nothing, and its clean result is the most dangerous
output in the system.

- **Hardcoding wiki subdirectories.** A new content subfolder must be auto-covered. If
  lint hardcodes `['entities','concepts','sources','decisions']`, a new subfolder is
  invisible to every check. Discover subdirectories under `wiki/` (skip `.obsidian`,
  dotdirs).
- **Frontmatter parsing that skips `- item` lines.** A YAML block list
  (`sources:\n  - "x"`) parsed line-by-line by `key: value` makes the `sources:` key
  present-but-empty even when the list is empty. `"sources" in fm` then reports present
  and the check passes. Parse list items; an empty or missing list fails.
- **Cross-reference checks matching only literal strings.** `if "[[open-loops]]" in body`
  or `"see [[contradictions]]"` misses prose variants ("logged in open-loops", "see
  contradictions", "tracked on the open-loops page"). Match on intent, not one exact
  phrase.
- **`break` after the first hit per page.** `break` after one matched pattern understates
  defect counts and hides a page that violates two checks. Collect all hits.
- **Bare substring matching on numbers.** `"24" in text` matches a date, an item count, a
  page number, giving false assurance. Match numbers with context and word boundaries
  (`\b24\b` plus the surrounding label, e.g. "the 24-item cap").

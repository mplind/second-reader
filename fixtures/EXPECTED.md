# Expected lint output on the fixture vaults

Recorded verbatim from a real run of `ops/lint.py` (Python 3, stdlib only). These are
the assertions the fixture pair exists to make: the clean vault must exit 0 with every
check asserting clean, and the dirty vault must exit 1 reporting every plant documented
in `dirty-vault/PLANTED.md`. After ANY change to `ops/lint.py`, re-run both commands
and compare against this file. If either output drifts, either lint or a fixture
changed behaviour, and the change does not ship until this file is re-verified and
re-recorded.

Run from the repository root.

## `python3 ops/lint.py fixtures/clean-vault`

```
lint: fixtures/clean-vault
 1. wikilink-resolution    clean
 2. split-wikilinks        clean
 3. frontmatter            clean
 4. template-placeholders  clean
 5. bookkeeping-truth      clean
 6. bookkeeping-stubs      clean
 7. index-completeness     clean
 8. synthesis-currency     clean
 9. as-of-dating           clean
10. name-variance          clean
11. contradiction-kind     clean
12. orphan-pages           clean
13. filename-collision     clean
14. source-status          clean
15. vault-walk             clean
result: CLEAN (15 checks, 0 findings)
exit code: 0
```

## `python3 ops/lint.py fixtures/dirty-vault`

```
lint: fixtures/dirty-vault
 1. wikilink-resolution    1 finding
      wiki/queries/when-did-chain-drive-appear.md:21: unresolved wikilink [[Boneshaker Era]]
 2. split-wikilinks        1 finding
      wiki/synthesis.md:19: wikilink split across a line break
 3. frontmatter            1 finding
      wiki/concepts/penny-farthing.md:3: illegal type 'musing' (legal: concept, decision, entity, query-output, source, synthesis)
 4. template-placeholders  1 finding
      wiki/concepts/pneumatic-tires.md:21: unreplaced {{...}} placeholder
 5. bookkeeping-truth      1 finding
      wiki/queries/when-did-chain-drive-appear.md:19: claims an entry in contradictions.md but no entry names this page
 6. bookkeeping-stubs      1 finding
      wiki/log.md:1: scaffold stub: 0 content lines beyond headings
 7. index-completeness     2 findings
      wiki/index.md:1: content page not linked from index: wiki/concepts/gearing-ratios.md
      wiki/index.md:1: content page not linked from index: wiki/concepts/workshop-notes.md
 8. synthesis-currency     1 finding
      wiki/synthesis.md:1: processed source not referenced in synthesis: raw/inbox/tire-market-note.md
 9. as-of-dating           1 finding
      wiki/concepts/pneumatic-tires.md:19: measured/current figure with no as_of date or PENDING mark
10. name-variance          1 finding
      wiki/concepts/gearing-ratios.md:1: 'safety bicycle' claimed by more than one page: wiki/concepts/gearing-ratios.md (alias), wiki/concepts/safety-bicycle.md (filename/title)
11. contradiction-kind     1 finding
      wiki/contradictions.md:22: entry 'Solid vs pneumatic ride comfort' has illegal Kind 'hunch' (legal: direct-conflict, granularity, temporal-change)
12. orphan-pages           1 finding
      wiki/concepts/workshop-notes.md:1: unreachable from wiki/index.md
13. filename-collision     1 finding
      wiki/concepts/velocipede-history.md:1: filename collision (case/separator variants): wiki/concepts/velocipede-history.md, wiki/concepts/velocipede_history.md
14. source-status          1 finding
      wiki/sources.md:20: illegal status 'pending' for raw/inbox/cycling-growth-note.md (legal: in-progress, processed, unprocessed)
15. vault-walk             clean
result: FAIL (15 findings across 14 of 15 checks)
exit code: 1
```

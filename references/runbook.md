# Operator runbook: the deterministic gates

The commands, in order, for one source's exam run, and the artifacts that prove each
step happened. Everything runs on `python3` (3.9+, standard library only), from the
repository root; lint alone also runs from inside a vault, since every vault carries
its own copy in `ops/`.

## Order of operations

```sh
# 1. Content-phase lint, before any validation.
python3 ops/lint.py <vault> --phase content

# 2. The writer delivers ledger + exam. Run every structural gate with one command:
#    seed check, blinded brief, chunk split. It stops before dispatch and grading.
python3 scripts/run_structural_gates.py <ledger.json> <exam.md> <durable.txt> \
        --run-dir ops/exam/<source>-<revision>

# 3. Dispatch each chunk file to the blinded tester; administer the controls file
#    separately. This is agent work; no script does it.

# 4. Gate the tester's deliverables before anyone grades them.
python3 scripts/verify_answer_files.py --file <answers.md>:QT:<first>:<last> ...

# 5. Grade, write the coverage report, and seal it: the exam run writes the
#    MANIFEST line, the committer replaces 'pending' with the commit id.
python3 scripts/manifest_hash.py <vault>          # paste output into the report
python3 scripts/verify_report_seal.py <report.md> # after the commit id is in

# 6. Final-phase lint at the bookkeeping gate.
python3 ops/lint.py <vault>
```

The run directory is fresh per source and seed revision; the scripts refuse a
directory holding an earlier run's artifacts. `run_structural_gates.py` never
grades: grading needs independent contexts, and a script that carried on into it
would collapse the independence the pipeline protects.

## What proves completion

| Step | Proof |
|---|---|
| Seed gate | `SEED OK` from verify_exam_seed.py |
| Blinding | `CLEAN` from build_tester_brief.py, plus `tester-brief.md` and `tester-brief.md.run.json` in the run directory |
| Bounding | `SPLIT OK`, plus the chunk files, the controls file, and the split's run manifest (written only after a clean verify) |
| Tester deliverables | `VERIFY OK` from verify_answer_files.py |
| Report | `SEAL OK` from verify_report_seal.py on the persisted report |
| Vault | `result: CLEAN` from the final-phase lint |

A missing proof means the step did not happen, whatever a summary says. The
manifests chain the artifacts to their seed by sha256, so any file in the run
directory can be tied back to the exact exam it came from.

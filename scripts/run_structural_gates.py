#!/usr/bin/env python3
"""Run the exam pipeline's structural gates, in order, and stop.

One entry point for the deterministic half of the pipeline, so the operator
runs one command instead of remembering three (and so the order is enforced
by code, not by memory):

    1. verify_exam_seed.py     the writer's ledger and exam
    2. build_tester_brief.py   the blinded brief, into the run directory
    3. split_brief_chunks.py   chunks plus the controls file

It stops there, deliberately. Dispatching the blinded tester and grading the
answers need independent contexts; a script that carried on into grading
would collapse the independence the pipeline exists to protect. After the
tester delivers, run verify_answer_files.py yourself; the runbook
(references/runbook.md) has the full order.

Non-destructive by design: there is no overwrite option. Each run gets its
own fresh --run-dir (one per source and seed revision); a directory holding
artifacts from an earlier run is refused by the underlying scripts. The exam,
ledger, and durable text are only read.

Usage:
    python3 scripts/run_structural_gates.py <ledger.json> <exam.md> <durable.txt>
            --run-dir DIR [--chunk-size N]

Exit code: the first failing gate's, unchanged. 0 means every structural gate
passed and the run directory holds the brief, the chunks, the controls file,
and their run manifests.
"""
import argparse
import os
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))


def gate(title, argv):
    print(f"== {title} ==")
    r = subprocess.run([sys.executable, *argv])
    print()
    if r.returncode != 0:
        print(f"GATE FAILED ({title}), exit {r.returncode}: nothing after "
              "this step ran")
        sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser(
        description="Run the structural exam gates in order; stop before grading.")
    ap.add_argument("ledger", help="the writer's claim ledger (JSON)")
    ap.add_argument("exam", help="the writer's exam file")
    ap.add_argument("durable", help="the durable source text")
    ap.add_argument("--run-dir", required=True,
                    help="fresh directory for this run's artifacts, one per "
                         "source and seed revision")
    ap.add_argument("--chunk-size", type=int, default=8,
                    help="QT questions per chunk (default 8)")
    args = ap.parse_args()

    # The fresh-run contract: an absent or empty directory is acceptable,
    # anything else is refused before the first gate runs. The underlying
    # scripts refuse their own filenames; this refuses everything, because a
    # run directory holding any earlier artifact is not this run's directory.
    if os.path.isdir(args.run_dir) and os.listdir(args.run_dir):
        print(f"REFUSED: run directory is not empty: {args.run_dir}")
        print("Each run gets its own fresh directory, one per source and "
              "seed revision.")
        sys.exit(2)
    os.makedirs(args.run_dir, exist_ok=True)
    brief = os.path.join(args.run_dir, "tester-brief.md")

    gate("gate 1: seed (verify_exam_seed.py)",
         [os.path.join(SCRIPTS, "verify_exam_seed.py"),
          args.ledger, args.exam, args.durable])
    gate("gate 2: blinding (build_tester_brief.py)",
         [os.path.join(SCRIPTS, "build_tester_brief.py"), args.exam, brief])
    gate("gate 3: bounding (split_brief_chunks.py)",
         [os.path.join(SCRIPTS, "split_brief_chunks.py"), brief,
          "--chunk-size", str(args.chunk_size)])

    print("STRUCTURAL GATES OK, stopping before dispatch and grading.")
    print(f"Artifacts in {args.run_dir}: tester-brief.md (+.run.json), "
          "chunk and controls files (+run manifest).")
    print("Next: dispatch each chunk to the blinded tester, then gate the "
          "answers with verify_answer_files.py before any grading.")
    sys.exit(0)


if __name__ == "__main__":
    main()

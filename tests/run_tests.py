#!/usr/bin/env python3
"""The repository's test entry point: python3 tests/run_tests.py

Two stages, both required:

1. Fixture contract. Runs every command recorded in fixtures/EXPECTED.md and
   compares output and exit code verbatim. EXPECTED.md stays the human-readable
   contract; this stage makes drifting from it a test failure instead of a
   documentation bug.
2. Unit tests. Discovers tests/test_*.py (stdlib unittest, no dependencies).

Exit 0 only when both stages pass.
"""
import os
import re
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = os.path.join(REPO, "fixtures", "EXPECTED.md")


def parse_expected(path):
    """Yield (command, expected_output, expected_exit) from EXPECTED.md.

    Each recorded run is a '## `<command>`' heading followed by one fenced
    block whose last line is 'exit code: N'.
    """
    text = open(path, encoding="utf-8").read()
    runs = []
    for m in re.finditer(r"^## `([^`]+)`\n+```\n(.*?)```", text, re.S | re.M):
        command, block = m.group(1), m.group(2)
        lines = block.rstrip("\n").split("\n")
        exit_m = re.fullmatch(r"exit code: (\d+)", lines[-1])
        if not exit_m:
            raise SystemExit(
                f"EXPECTED.md block for `{command}` has no 'exit code: N' line")
        runs.append((command, "\n".join(lines[:-1]), int(exit_m.group(1))))
    if not runs:
        raise SystemExit("no recorded runs found in fixtures/EXPECTED.md")
    return runs


def fixture_stage():
    failures = 0
    for command, want_out, want_exit in parse_expected(EXPECTED):
        argv = command.split()
        if argv[0] == "python3":
            argv[0] = sys.executable
        r = subprocess.run(argv, capture_output=True, text=True, cwd=REPO)
        got_out = r.stdout.rstrip("\n")
        ok = got_out == want_out and r.returncode == want_exit
        print(f"[{'ok' if ok else 'FAIL'}] {command} (exit {r.returncode})")
        if not ok:
            failures += 1
            if r.returncode != want_exit:
                print(f"  exit code {r.returncode} != expected {want_exit}")
            if got_out != want_out:
                print("  output drifted from fixtures/EXPECTED.md; diff:")
                import difflib
                for dl in difflib.unified_diff(
                        want_out.split("\n"), got_out.split("\n"),
                        "EXPECTED.md", "actual", lineterm=""):
                    print("    " + dl)
    return failures


def main():
    print("== stage 1: fixture contract (fixtures/EXPECTED.md) ==")
    fixture_failures = fixture_stage()
    print()
    print("== stage 2: unit tests ==")
    suite = unittest.defaultTestLoader.discover(
        os.path.join(REPO, "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    failed = fixture_failures + len(result.failures) + len(result.errors)
    if failed or not result.testsRun:
        print(f"\nRESULT: FAIL ({fixture_failures} fixture, "
              f"{len(result.failures) + len(result.errors)} unit)")
        return 1
    print(f"\nRESULT: PASS (fixture contract + {result.testsRun} unit tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

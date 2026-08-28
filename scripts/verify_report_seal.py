#!/usr/bin/env python3
"""Structural check on a coverage report's provenance seal.

The report's provenance record is two-step, because the commit id cannot
exist when the exam runs: the exam happens first, the commit follows
sign-off. A report that records only a commit hash is therefore recording
something the run could not have known, and a placeholder left in that field
turns "committed" into an assertion. The two-step record closes both holes:

1. `MANIFEST sha256:<hex>`, written by the exam run itself
   (`python3 scripts/manifest_hash.py <vault>`): immutable evidence of the
   exact content examined.
2. `COMMIT <id>`, appended by whoever commits, replacing `pending`.

This script checks the record's structure:

- exactly one MANIFEST line, carrying a full 64-hex sha256
- exactly one COMMIT line, carrying `pending` or a 7-40 hex commit id
- a STATUS line exists, and no STATUS reads SIGN-OFF while COMMIT is still
  `pending`: sign-off is not valid evidence until the commit id is on the
  record

It does NOT recompute the manifest hash (that needs the vault; re-run
manifest_hash.py to audit it) and does not judge the report's content.

Usage:
    python3 scripts/verify_report_seal.py <report.md>

Exit 0 = seal structurally sound. Exit 1 = findings. Exit 2 = usage error.
"""
import re
import sys
import os

MANIFEST = re.compile(r"^MANIFEST sha256:[0-9a-f]{64}$")
COMMIT = re.compile(r"^COMMIT (pending|[0-9a-f]{7,40})$")
STATUS = re.compile(r"^\s*STATUS\s+(\S+)", re.M)


def verify_seal(path):
    if not os.path.exists(path):
        return [f"{path}: file not found"]
    text = open(path, encoding="utf-8").read()
    errs = []
    manifests = re.findall(r"^MANIFEST\b.*$", text, re.M)
    if len(manifests) != 1:
        errs.append(f"MANIFEST lines: {len(manifests)} != 1 "
                    "(the exam run writes exactly one)")
    elif not MANIFEST.match(manifests[0]):
        errs.append(f"MANIFEST line malformed: '{manifests[0]}' "
                    "(want 'MANIFEST sha256:<64 hex>')")
    commits = re.findall(r"^COMMIT\b.*$", text, re.M)
    if len(commits) != 1:
        errs.append(f"COMMIT lines: {len(commits)} != 1")
        commit_value = None
    elif not COMMIT.match(commits[0]):
        errs.append(f"COMMIT line malformed: '{commits[0]}' "
                    "(want 'COMMIT pending' or 'COMMIT <7-40 hex id>')")
        commit_value = None
    else:
        commit_value = COMMIT.match(commits[0]).group(1)
    statuses = STATUS.findall(text)
    if not statuses:
        errs.append("no STATUS line found (a report without a verdict card "
                    "is not a report)")
    if "SIGN-OFF" in statuses and commit_value == "pending":
        errs.append("STATUS is SIGN-OFF but COMMIT is still pending: "
                    "sign-off is not valid evidence until the commit id "
                    "replaces the placeholder")
    return errs


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    errs = verify_seal(sys.argv[1])
    if errs:
        print("SEAL VERIFICATION FAILED:")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print(f"SEAL OK: {os.path.basename(sys.argv[1])} provenance record "
          "structurally sound")
    sys.exit(0)


if __name__ == "__main__":
    main()

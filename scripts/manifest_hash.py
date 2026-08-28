#!/usr/bin/env python3
"""Immutable pre-commit manifest hash for a coverage report.

A coverage report's provenance record is two-step (see
references/coverage-instrument.md, persisting the coverage report):

1. `MANIFEST sha256:<hex>`, written by the exam run itself, before any commit
   exists: a hash over the vault content the exam examined.
2. `COMMIT <id>`, appended by whoever commits, replacing `pending`.

This script computes step 1. The hash is sha256 over the sorted per-file hash
lines `<sha256(file)>  <relpath>` for `AGENTS.md` and every file under
`wiki/`, dot-entries skipped. Sorting is by POSIX relpath, so the result is
independent of walk order, platform, and mtimes: the same content always
hashes the same, and one changed byte anywhere changes it.

Usage:
    python3 scripts/manifest_hash.py <vault>

Prints the MANIFEST line verbatim, ready to paste into the report. The file
count goes to stderr so stdout stays paste-clean.
"""
import hashlib
import sys
from pathlib import Path


def manifest_hash(root):
    files = []
    contract = root / "AGENTS.md"
    if contract.is_file():
        files.append(contract)
    for path in (root / "wiki").rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        files.append(path)
    files.sort(key=lambda p: p.relative_to(root).as_posix())
    lines = ["%s  %s" % (hashlib.sha256(p.read_bytes()).hexdigest(),
                         p.relative_to(root).as_posix())
             for p in files]
    digest = hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()
    return digest, len(files)


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = Path(argv[1])
    if not (root / "wiki").is_dir():
        sys.stderr.write("manifest_hash.py: not a vault (no wiki/): %s\n" % root)
        return 2
    digest, count = manifest_hash(root)
    print("MANIFEST sha256:%s" % digest)
    sys.stderr.write("%d files hashed (AGENTS.md + wiki/)\n" % count)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

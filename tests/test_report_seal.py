"""Regression tests for the coverage report's provenance seal.

The report's provenance record is two-step: a MANIFEST hash written by the
exam run before any commit exists, and a COMMIT id appended by whoever
commits. verify_report_seal.py is the structural gate on that record;
manifest_hash.py computes the first half. A sign-off whose COMMIT is still
the placeholder is not valid evidence, and these tests keep that rule
mechanical.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

HEX64 = "a" * 64


def run(script, *args):
    return subprocess.run(
        [PY, os.path.join(REPO, "scripts", script), *args],
        capture_output=True, text=True, cwd=REPO)


def report(status="SIGN-OFF", manifest=f"MANIFEST sha256:{HEX64}",
           commit="COMMIT 3f81c2e"):
    lines = ["# Coverage report", "",
             "```text",
             "SOURCE       Book X - raw/books/book-x.epub",
             f"STATUS       {status} - protocol 0.2, lint 0.2.0",
             "```", ""]
    if manifest:
        lines.append(manifest)
    if commit:
        lines.append(commit)
    return "\n".join(lines) + "\n"


class TestReportSeal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sr-seal-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def seal(self, text):
        path = os.path.join(self.tmp, "report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return run("verify_report_seal.py", path)

    def test_sealed_sign_off_passes(self):
        r = self.seal(report())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sign_off_with_pending_commit_fails(self):
        r = self.seal(report(commit="COMMIT pending"))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("pending", r.stdout)

    def test_needs_another_pass_may_stay_pending(self):
        r = self.seal(report(status="NEEDS-ANOTHER-PASS",
                             commit="COMMIT pending"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_manifest_fails(self):
        r = self.seal(report(manifest=None))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("MANIFEST", r.stdout)

    def test_malformed_manifest_fails(self):
        r = self.seal(report(manifest="MANIFEST sha256:deadbeef"))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_duplicate_manifest_fails(self):
        text = report() + f"MANIFEST sha256:{'b' * 64}\n"
        r = self.seal(text)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_placeholder_shaped_commit_fails(self):
        r = self.seal(report(commit="COMMIT TBD"))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_shipped_example_report_is_sealed(self):
        # The example is the format's reference rendering; it must pass the
        # gate it documents.
        r = run("verify_report_seal.py",
                os.path.join(REPO, "examples", "coverage-report.md"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestManifestHash(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sr-manifest-test-")
        os.makedirs(os.path.join(self.tmp, "wiki", "concepts"))
        self.write("AGENTS.md", "# Contract\n")
        self.write("wiki/index.md", "# Index\n")
        self.write("wiki/concepts/a.md", "# A\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, rel, text):
        with open(os.path.join(self.tmp, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def hash(self):
        r = run("manifest_hash.py", self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = r.stdout.strip()
        self.assertRegex(line, r"^MANIFEST sha256:[0-9a-f]{64}$")
        return line

    def test_deterministic_across_runs(self):
        self.assertEqual(self.hash(), self.hash())

    def test_content_change_changes_hash(self):
        before = self.hash()
        self.write("wiki/concepts/a.md", "# A, revised\n")
        self.assertNotEqual(before, self.hash())

    def test_mtime_change_does_not_change_hash(self):
        before = self.hash()
        path = os.path.join(self.tmp, "wiki", "index.md")
        os.utime(path, (0, 0))
        self.assertEqual(before, self.hash())


if __name__ == "__main__":
    unittest.main()

"""Regression tests for the exam pipeline scripts.

Every test here encodes a defect class that was found in review and fixed:
each one plants the defect and asserts the script catches it. If a test in
this file fails, a silent-false-negative class has come back.

The canonical fixture (tests/fixtures/exam/) is a valid seed: ledger, exam
and durable text that pass verify_exam_seed.py as written. Tests mutate
copies of it in a temp directory; the fixture itself is never modified.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(REPO, "tests", "fixtures", "exam")
PY = sys.executable


def run(script, *args, cwd=REPO):
    return subprocess.run(
        [PY, os.path.join(REPO, "scripts", script), *args],
        capture_output=True, text=True, cwd=cwd)


# Every marker that belongs to the exam's answer key or metadata. None of
# these may ever appear in a blinded tester brief or its split chunks. The
# **ANSWER:**/**WIKI SOURCE:** markers are NOT in this list: they are the
# tester's own output format, taught by the brief's preamble on purpose.
KEY_MARKERS = ["Wrong (FAIL", "Correct (PASS", "Target claim",
               "Source location", "**Check:**", "Tier:"]


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sr-exam-test-")
        for name in ("exam.md", "ledger.json", "durable.txt"):
            shutil.copy(os.path.join(FIX, name), self.tmp)
        self.exam = os.path.join(self.tmp, "exam.md")
        self.ledger = os.path.join(self.tmp, "ledger.json")
        self.durable = os.path.join(self.tmp, "durable.txt")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self, path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def write(self, path, text):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def build_brief(self):
        brief = os.path.join(self.tmp, "brief.md")
        r = run("build_tester_brief.py", self.exam, brief)
        return brief, r

    def make_answers(self, path, blocks):
        """blocks: list of (header, answer_lines) tuples."""
        parts = []
        for hdr, lines in blocks:
            parts.append(hdr + "\n" + "\n".join(lines))
        self.write(path, "\n\n".join(parts) + "\n")


class TestBriefBlinding(Workspace):
    def test_brief_never_carries_key_markers(self):
        # Reorder QT1's answer key so the Wrong (FAIL) line comes first.
        # The seed gate does not enforce field order, so this is a legal
        # writer output, and the brief must still carry zero key markers.
        text = self.read(self.exam)
        text = text.replace(
            "- **Target claim IDs:** C001\n"
            "- **Source location:** durable lines 1-1\n"
            "- **Check:** exact figure with unit\n"
            "- **Correct (PASS)**: 42 kilometres\n"
            "- **Wrong (FAIL)**: 40 kilometres, or any figure without a unit",
            "- **Wrong (FAIL)**: 40 kilometres, or any figure without a unit\n"
            "- **Target claim IDs:** C001\n"
            "- **Source location:** durable lines 1-1\n"
            "- **Check:** exact figure with unit\n"
            "- **Correct (PASS)**: 42 kilometres")
        self.write(self.exam, text)
        brief, r = self.build_brief()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        content = self.read(brief)
        for marker in KEY_MARKERS:
            self.assertNotIn(marker, content,
                             "key/metadata marker leaked into blinded brief")

    def test_malformed_key_marker_still_blocked(self):
        # A key line missing its closing paren must not slip past the cut or
        # the self-scan: matching is on the stable prefix, not the full token.
        text = self.read(self.exam)
        text = text.replace(
            "Tier: 1\n- **Target claim IDs:** C001",
            "- **Correct (PASS**: 42 kilometres\nTier: 1\n- **Target claim IDs:** C001")
        self.write(self.exam, text)
        brief, r = self.build_brief()
        if r.returncode == 0:
            self.assertNotIn("Correct (", self.read(brief),
                             "malformed key marker leaked into blinded brief")

    def test_midline_tier_never_reaches_brief(self):
        # Tier metadata embedded mid-line in prose must never reach a tester:
        # either the builder strips it or it refuses the brief loudly.
        text = self.read(self.exam)
        text = text.replace(
            "What distance does the artifact state the first recorded ride covered?",
            "What distance does the artifact state the first recorded ride "
            "covered? (Tier: 1 difficulty)")
        self.write(self.exam, text)
        brief, r = self.build_brief()
        leaked = r.returncode == 0 and "Tier:" in self.read(brief)
        self.assertFalse(leaked, "mid-line Tier metadata leaked into a CLEAN brief")

    def test_canonical_brief_is_clean_and_complete(self):
        brief, r = self.build_brief()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        content = self.read(brief)
        for marker in KEY_MARKERS:
            self.assertNotIn(marker, content)
        for hdr in ("## QT1", "## QT2", "## QT3", "## NC1"):
            self.assertIn(hdr, content)
        self.assertNotIn("[NEGATIVE CONTROL]", content)


class TestAnswerFiles(Workspace):
    def canonical_answers(self, path, prefix="QT", n=3):
        blocks = []
        for i in range(1, n + 1):
            blocks.append((f"## {prefix}{i}",
                           ["**ANSWER:** 42 kilometres",
                            "**WIKI SOURCE:** wiki/concepts/first-ride.md, Key points"]))
        self.make_answers(path, blocks)

    def test_canonical_answer_file_passes(self):
        path = os.path.join(self.tmp, "answers.md")
        self.canonical_answers(path)
        r = run("verify_answer_files.py", "--file", f"{path}:QT:1:3")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_per_block_counts(self):
        # QT1 carries two ANSWER lines, QT2 none: global counts still add up,
        # so a global counter passes a file where two blocks are broken.
        path = os.path.join(self.tmp, "answers.md")
        self.make_answers(path, [
            ("## QT1", ["**ANSWER:** 42 kilometres",
                        "**ANSWER:** 40 kilometres",
                        "**WIKI SOURCE:** wiki/a.md"]),
            ("## QT2", ["**WIKI SOURCE:** wiki/b.md"]),
            ("## QT3", ["**ANSWER:** 700 machines a year",
                        "**WIKI SOURCE:** wiki/c.md"]),
        ])
        r = run("verify_answer_files.py", "--file", f"{path}:QT:1:3")
        self.assertEqual(r.returncode, 1,
                         "two broken blocks with a clean global count must fail")
        self.assertIn("QT1", r.stdout)
        self.assertIn("QT2", r.stdout)

    def test_rejects_foreign_block(self):
        # A stray NC block inside a QT answer file, carrying no ANSWER lines,
        # is invisible to prefix-scoped header matching and global counts.
        path = os.path.join(self.tmp, "answers.md")
        self.canonical_answers(path)
        self.write(path, self.read(path) + "\n## NC1\nstray control block\n")
        r = run("verify_answer_files.py", "--file", f"{path}:QT:1:3")
        self.assertEqual(r.returncode, 1, "foreign block must be rejected")
        self.assertIn("NC1", r.stdout)

    def test_rejects_combined_marker_line(self):
        # One line satisfying both marker counts is two broken fields, not one
        # complete block.
        path = os.path.join(self.tmp, "answers.md")
        self.make_answers(path, [
            ("## QT1", ["**ANSWER:** 42 kilometres",
                        "**WIKI SOURCE:** wiki/a.md"]),
            ("## QT2", ["**ANSWER:** **WIKI SOURCE:** none"]),
            ("## QT3", ["**ANSWER:** 700 machines a year",
                        "**WIKI SOURCE:** wiki/c.md"]),
        ])
        r = run("verify_answer_files.py", "--file", f"{path}:QT:1:3")
        self.assertEqual(r.returncode, 1,
                         "ANSWER and WIKI SOURCE sharing one line must fail")

    def test_rejects_empty_answer_value(self):
        path = os.path.join(self.tmp, "answers.md")
        self.make_answers(path, [
            ("## QT1", ["**ANSWER:**",
                        "**WIKI SOURCE:** wiki/a.md"]),
            ("## QT2", ["**ANSWER:** 1885 to 1892",
                        "**WIKI SOURCE:** wiki/b.md"]),
            ("## QT3", ["**ANSWER:** 700 machines a year",
                        "**WIKI SOURCE:** wiki/c.md"]),
        ])
        r = run("verify_answer_files.py", "--file", f"{path}:QT:1:3")
        self.assertEqual(r.returncode, 1, "empty ANSWER value must fail")


class TestSplitIntegrity(Workspace):
    def split(self, *extra):
        brief, r = self.build_brief()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run("split_brief_chunks.py", brief, "--chunk-size", "2", *extra)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        chunk1 = os.path.join(self.tmp, "brief-chunk-1.md")
        chunk2 = os.path.join(self.tmp, "brief-chunk-2.md")
        controls = os.path.join(self.tmp, "brief-controls.md")
        for p in (chunk1, chunk2, controls):
            self.assertTrue(os.path.exists(p), p)
        return brief, chunk1, chunk2, controls

    def verify_only(self, brief):
        return run("split_brief_chunks.py", brief, "--chunk-size", "2",
                   "--verify-only")

    def test_detects_body_truncation(self):
        brief, chunk1, _, _ = self.split()
        text = self.read(chunk1).rstrip()
        lines = text.split("\n")
        # Drop the final non-empty body line; every header survives.
        while lines and not lines[-1].strip():
            lines.pop()
        self.assertFalse(lines[-1].startswith("## "), "fixture shape changed")
        lines.pop()
        self.write(chunk1, "\n".join(lines) + "\n")
        r = self.verify_only(brief)
        self.assertEqual(r.returncode, 1,
                         "truncated body under an intact header must fail")

    def test_rejects_block_moved_between_files(self):
        brief, _, chunk2, controls = self.split()
        # Move NC1 from the controls file into a QT chunk. Every block is
        # still present exactly once across the outputs, so an aggregate
        # header census passes while per-file purity is violated.
        ctext = self.read(controls)
        m = re.search(r"(## NC1.*)", ctext, re.S)
        self.assertIsNotNone(m, "fixture shape changed")
        nc_block = m.group(1).rstrip() + "\n"
        self.write(controls, ctext[:m.start()].rstrip() + "\n")
        self.write(chunk2, self.read(chunk2).rstrip() + "\n\n---\n\n" + nc_block)
        r = self.verify_only(brief)
        self.assertEqual(r.returncode, 1,
                         "a control block inside a QT chunk must fail")

    def test_rejects_block_moved_between_chunks(self):
        brief, chunk1, chunk2, _ = self.split()
        # Move QT3 (chunk-2's only block) into chunk-1. Prefix purity and the
        # aggregate census both still hold; the per-file assignment does not.
        c2 = self.read(chunk2)
        m = re.search(r"(## QT3.*)", c2, re.S)
        self.assertIsNotNone(m, "fixture shape changed")
        block = m.group(1).rstrip() + "\n"
        self.write(chunk2, c2[:m.start()].rstrip() + "\n")
        self.write(chunk1, self.read(chunk1).rstrip() + "\n\n---\n\n" + block)
        r = self.verify_only(brief)
        self.assertEqual(r.returncode, 1,
                         "a QT block in the wrong chunk file must fail")

    def test_detects_preamble_tampering(self):
        brief, chunk1, _, _ = self.split()
        self.write(chunk1, self.read(chunk1).replace(
            "Do NOT open the source",
            "You may open the source freely"))
        r = self.verify_only(brief)
        self.assertEqual(r.returncode, 1,
                         "an edited preamble carries the tester's contract and must fail")

    def test_detects_altered_body(self):
        brief, chunk1, _, _ = self.split()
        self.write(chunk1, self.read(chunk1).replace(
            "first recorded ride", "first documented ride"))
        r = self.verify_only(brief)
        self.assertEqual(r.returncode, 1,
                         "altered question wording under an intact header must fail")


class TestSeedGate(Workspace):
    def seed(self, *args):
        return run("verify_exam_seed.py", self.ledger, self.exam, self.durable,
                   *args)

    def test_canonical_seed_passes(self):
        r = self.seed()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_exam_target_must_exist_in_ledger(self):
        self.write(self.exam, self.read(self.exam).replace(
            "- **Target claim IDs:** C001\n",
            "- **Target claim IDs:** C009\n"))
        r = self.seed()
        self.assertEqual(r.returncode, 1,
                         "exam targeting a claim absent from the ledger must fail")
        self.assertIn("C009", r.stdout)

    def test_empty_durable_text_fails_bounds(self):
        self.write(self.durable, "")
        r = self.seed()
        self.assertEqual(r.returncode, 1,
                         "0-line durable text cannot satisfy any source bounds")

    def test_requires_negative_controls(self):
        text = self.read(self.exam)
        text = text[:text.index("## NC1")].rstrip() + "\n"
        self.write(self.exam, text)
        r = self.seed()
        self.assertEqual(r.returncode, 1,
                         "an exam with no negative controls must fail")
        self.assertIn("negative control", r.stdout.lower())

    def test_malformed_target_token_reported(self):
        # A token that cannot be a claim ID must be reported, never dropped:
        # dropping it turns a typo into a silently untested claim.
        self.write(self.exam, self.read(self.exam).replace(
            "- **Target claim IDs:** C001\n",
            "- **Target claim IDs:** C0O1\n"))
        r = self.seed()
        self.assertEqual(r.returncode, 1,
                         "a malformed target token must be a finding")
        self.assertIn("C0O1", r.stdout)

    def test_requires_real_questions(self):
        text = self.read(self.exam)
        text = text[:text.index("## QT1")] + text[text.index("## NC1"):]
        self.write(self.exam, text)
        r = self.seed()
        self.assertEqual(r.returncode, 1,
                         "an exam with no QT blocks tests nothing")

    def test_missing_exam_file_is_finding_not_traceback(self):
        r = run("verify_exam_seed.py", self.ledger,
                os.path.join(self.tmp, "no-such-exam.md"), self.durable)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("EXAM", r.stdout)

    def test_malformed_ledger_is_finding_not_traceback(self):
        self.write(self.ledger,
                   '{"total_claims": 1, "tiers": [1],'
                   ' "claims": [{"id": "C001", "tier": 1}]}')
        r = self.seed()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr,
                         "malformed input must produce findings, not a crash")
        self.assertIn("LEDGER", r.stdout)


if __name__ == "__main__":
    unittest.main()

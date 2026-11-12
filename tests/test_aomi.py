"""Tests for Aomi's command line. Run with: python3 -m unittest discover -s tests -v

The tests are deliberately behavioural: each one runs the tool the way a person
or a build would, and checks the output a person would read.
"""
from __future__ import annotations

import importlib.util
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / "fixtures"


sys.path.insert(0, str(ROOT))
from aomi import cli as cli_module  # noqa: E402
from aomi import engine  # noqa: E402


def run(argv):
    """Run a command, returning (exit code, stdout)."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = cli_module.main(argv)
    return code, buffer.getvalue()


class ContrastTest(unittest.TestCase):
    def test_black_on_white_is_twenty_one(self):
        self.assertEqual(engine.contrast("#000000", "#ffffff"), 21.0)

    def test_identical_colours_are_one(self):
        self.assertEqual(engine.contrast("#3366cc", "#3366CC"), 1.0)

    def test_short_hex_is_expanded(self):
        self.assertEqual(engine.contrast("#000", "#fff"), 21.0)

    def test_declared_pairs_report_failures(self):
        code, out = run(["contrast", str(FIXTURES / "tokens.json")])
        self.assertEqual(code, 1, "a faint ink pair should fail the gate")
        self.assertIn("faint on ground", out)
        self.assertIn("FAIL", out)

    def test_named_tokens_resolve(self):
        doc = json.loads((FIXTURES / "tokens.json").read_text())
        self.assertEqual(engine.resolve("ground", doc), "#F7F4EE")
        self.assertEqual(engine.resolve("#FFFFFF", doc), "#FFFFFF")

    def test_missing_pairs_and_no_ground_returns_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "tokens.json"
            path.write_text(json.dumps({"ink": "#000000"}))
            code, _ = run(["contrast", str(path)])
        self.assertEqual(code, 2)

    def test_auto_pairing_uses_the_ground_role(self):
        doc = {"ground": "#FFFFFF", "ink": "#111111", "ink-muted": "#555555"}
        pairs = engine.collect_pairs(doc)
        self.assertEqual({p["bg"] for p in pairs}, {"ground"})
        self.assertEqual(len(pairs), 2)


class ParityTest(unittest.TestCase):
    def test_mixed_priority_and_partial_credit(self):
        code, out = run(["parity", str(FIXTURES / "features_mixed.csv")])
        # must 3+3, should 2, could 1 => earned 3 + 1.5 + 0 + 0 = 4.5 of 9
        self.assertEqual(code, 1, "an unfinished must-have must block")
        self.assertIn("50.0", out)
        self.assertIn("Time zone detection", out)

    def test_reference_no_is_not_scored(self):
        code, out = run(["parity", "--json", str(FIXTURES / "features_mixed.csv")])
        report = json.loads(out)
        self.assertEqual(report["rows"], 5)
        self.assertNotIn("extra", report["areas"])

    def test_everything_done_scores_one_hundred(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "features.csv"
            path.write_text(
                "area,feature,priority,reference,clone,notes\n"
                "core,Sign up,must,yes,yes,\n"
                "core,Reset password,should,yes,yes,\n"
            )
            code, out = run(["parity", str(path)])
        self.assertEqual(code, 0)
        self.assertIn("100.0", out)

    def test_unknown_priority_is_skipped_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "features.csv"
            path.write_text(
                "area,feature,priority,reference,clone,notes\n"
                "core,Sign up,must,yes,yes,\n"
                "core,Vague thing,whatever,yes,no,\n"
            )
            code, out = run(["parity", str(path)])
        self.assertEqual(code, 0)
        self.assertIn("100.0", out)


class AuditTest(unittest.TestCase):
    def test_clean_page_is_clear(self):
        code, out = run(["audit", str(FIXTURES / "clean")])
        self.assertEqual(code, 0)
        self.assertIn("No signals fired", out)

    def test_slop_page_is_blocked_and_names_the_signals(self):
        code, out = run(["audit", str(FIXTURES / "slop")])
        self.assertEqual(code, 1)
        for signal in ("SG01", "SG05", "SG07", "SG08", "SG15"):
            self.assertIn(signal, out)
        self.assertIn("BLOCKED", out)

    def test_json_report_has_the_same_score(self):
        _, out = run(["audit", "--json", str(FIXTURES / "slop")])
        report = json.loads(out)
        self.assertEqual(report["score"], 0)
        self.assertEqual(report["verdict"], "blocked")
        self.assertTrue(all(s["weight"] >= 1 for s in report["signals"]))

    def test_waiver_removes_a_signal_and_lifts_the_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = pathlib.Path(tmp)
            shutil.copy(FIXTURES / "slop" / "page.html", page / "page.html")
            (page / "aomi").mkdir()
            (page / "aomi" / "overrides.json").write_text(json.dumps([
                {"signal": "SG01", "reason": "brand",
                 "note": "the logo is #6d4aa6, inherited on purpose"},
                {"signal": "SG15", "reason": "we will fix it later", "note": "no reason given"},
            ]))
            code, out = run(["audit", "--json", str(page)])
            report = json.loads(out)
        waived = [s["id"] for s in report.get("waived", [])]
        self.assertIn("SG01", waived)
        self.assertNotIn("SG15", waived, "a waiver without an allowed reason is ignored")
        self.assertTrue(any("SG15" in p for p in report["override_problems"]))
        blocked = {s["id"]: s["weight"] for s in report["signals"]}
        self.assertNotIn("SG01", blocked)
        expected = max(0, 100 - 7 * sum(blocked.values()))
        self.assertEqual(report["score"], expected)

    def test_missing_directory_exits_two(self):
        code, _ = run(["audit", str(FIXTURES / "does-not-exist")])
        self.assertEqual(code, 2)

    def test_empty_directory_is_not_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run(["audit", tmp])
        self.assertEqual(code, 0)
        self.assertIn("nothing to audit", out.lower())


class DoctorTest(unittest.TestCase):
    def test_repository_is_healthy(self):
        code, out = run(["doctor", "--root", str(ROOT)])
        self.assertEqual(code, 0, out)

    def test_broken_link_is_an_error(self):
        code, out = run(["doctor", "--root", str(FIXTURES / "links")])
        self.assertEqual(code, 1)
        self.assertIn("E110", out)
        self.assertIn("nonexistent.md", out)

    def test_missing_license_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n")
            code, out = run(["doctor", "--root", str(root)])
        self.assertEqual(code, 1)
        self.assertIn("E120", out)


class InitTest(unittest.TestCase):
    def test_creates_the_artifacts_then_keeps_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run(["init", tmp])
            self.assertEqual(code, 0)
            created = sorted(p.name for p in (pathlib.Path(tmp) / "aomi").iterdir())
            self.assertEqual(
                created, ["brief.md", "decisions.md", "features.csv", "handoff.md", "proof.md"]
            )

            brief = pathlib.Path(tmp) / "aomi" / "brief.md"
            brief.write_text("# my own brief\n")
            code, out = run(["init", tmp])
            self.assertEqual(brief.read_text(), "# my own brief\n", "init must not overwrite work")
            self.assertIn("kept", out)


class DocumentedWeightsTest(unittest.TestCase):
    """The weights in design/slop-gate.md and in the code must agree.

    A gate whose documentation and implementation disagree is worse than none:
    the score becomes an argument about which one is right.
    """

    def test_every_implemented_signal_is_documented_with_the_same_weight(self):
        doc = (ROOT / "design" / "slop-gate.md").read_text()
        documented = {
            m.group(1): int(m.group(2))
            for m in __import__("re").finditer(r"\| (SG\d\d) \|[^|]*\| (\d) \|", doc)
        }
        implemented = {sid: weight for sid, (weight, _title, _measured)
                       in engine.SIGNALS.items()}
        self.assertEqual(documented, implemented)


if __name__ == "__main__":
    unittest.main(verbosity=2)

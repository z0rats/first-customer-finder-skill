"""End-to-end tests for generate_report.py run as a command, the way the skill invokes it.

Run with: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "first-customer-finder" / "scripts" / "generate_report.py"
FIXTURE = ROOT / "tests" / "fixtures" / "sample_report.json"
REPORT_DOC = ROOT / "first-customer-finder" / "references" / "report-artifact.md"


def run_generator(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def test_writes_html_and_reports_its_path(self):
        out = self.tmp / "report.html"
        result = run_generator(FIXTURE, out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Created report:", result.stdout)
        html_out = out.read_text(encoding="utf-8")
        self.assertTrue(html_out.startswith("<!doctype html>"))
        self.assertIn("Acme Gym", html_out)
        self.assertIn("Клуб «Ритм»", html_out)

    def test_creates_missing_output_directories(self):
        out = self.tmp / "outputs" / "nested" / "report.html"
        csv_out = self.tmp / "outputs" / "other" / "report.csv"
        result = run_generator(FIXTURE, out, "--csv", csv_out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(out.is_file())
        self.assertTrue(csv_out.is_file())

    def test_csv_has_bom_and_round_trips_non_ascii(self):
        csv_out = self.tmp / "report.csv"
        run_generator(FIXTURE, self.tmp / "report.html", "--csv", csv_out)
        raw = csv_out.read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), "Excel needs the UTF-8 BOM for Cyrillic")
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        self.assertEqual([r["name"] for r in rows], ["Acme Gym", "Клуб «Ритм»", "Beta Studio"])
        self.assertEqual([r["rank"] for r in rows], ["1", "2", "3"])
        self.assertEqual([r["score"] for r in rows], ["90", "70", "42"])
        self.assertEqual(rows[2]["source_url"], "", "javascript: URLs must be blanked")

    def test_no_csv_written_unless_requested(self):
        run_generator(FIXTURE, self.tmp / "report.html")
        self.assertEqual([p.name for p in self.tmp.iterdir()], ["report.html"])

    def test_warnings_go_to_stderr_and_report_is_still_written(self):
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["prospects"][0]["score"] = 12  # disagrees with dimensions
        bad = self.tmp / "bad.json"
        bad.write_text(json.dumps(data), encoding="utf-8")
        out = self.tmp / "report.html"
        result = run_generator(bad, out)
        self.assertEqual(result.returncode, 0)
        self.assertIn("warning: Acme Gym", result.stderr)
        self.assertNotIn("warning:", result.stdout)
        self.assertIn('data-score="90"', out.read_text(encoding="utf-8"))

    def test_clean_fixture_prints_no_warnings(self):
        result = run_generator(FIXTURE, self.tmp / "report.html")
        self.assertEqual(result.stderr, "")

    def test_non_object_json_is_rejected(self):
        bad = self.tmp / "list.json"
        bad.write_text("[]", encoding="utf-8")
        result = run_generator(bad, self.tmp / "report.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("top level", result.stderr)
        self.assertFalse((self.tmp / "report.html").exists())

    def test_invalid_json_fails_without_writing_output(self):
        bad = self.tmp / "broken.json"
        bad.write_text("{not json", encoding="utf-8")
        result = run_generator(bad, self.tmp / "report.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.tmp / "report.html").exists())

    def test_missing_input_fails(self):
        result = run_generator(self.tmp / "nope.json", self.tmp / "report.html")
        self.assertNotEqual(result.returncode, 0)

    def test_output_is_deterministic(self):
        first, second = self.tmp / "a.html", self.tmp / "b.html"
        run_generator(FIXTURE, first)
        run_generator(FIXTURE, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())


class RenderedReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        out = Path(cls._tmp.name) / "report.html"
        run_generator(FIXTURE, out)
        cls.html = out.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_one_card_per_prospect_in_input_order(self):
        names = re.findall(r'<article class="prospect[^"]*"[^>]*data-name="([^"]*)"', self.html)
        self.assertEqual(names, ["Acme Gym", "Клуб «Ритм»", "Beta Studio"])

    def test_stale_badge_only_on_old_signal(self):
        cards = self.html.split('<article class="prospect')[1:]
        stale = ["Stale" in card.split("</header>")[0] for card in cards]
        self.assertEqual(stale, [False, True, False])

    def test_unsafe_source_url_never_becomes_a_link(self):
        self.assertNotIn("javascript:", self.html)

    def test_outbound_links_do_not_leak_referrer(self):
        for tag in re.findall(r"<a [^>]*target=\"_blank\"[^>]*>", self.html):
            self.assertIn("noreferrer", tag)

    def test_filter_options_cover_every_stage_and_source(self):
        for value in ("High intent", "Problem aware", "Trigger present", "Public forum", "Job posting"):
            self.assertIn(f'<option value="{value}">', self.html)

    def test_page_is_self_contained(self):
        # A shareable report must not depend on the network.
        self.assertNotRegex(self.html, r'<(script|link|img)[^>]+(src|href)="https?://')

    def test_rejected_section_and_limits_rendered(self):
        self.assertIn("Considered, not qualified", self.html)
        self.assertIn("Other Gym Co", self.html)
        self.assertIn("not confirmed buyers", self.html)


class DocumentedSchemaTests(unittest.TestCase):
    """The JSON example in report-artifact.md is what a model copies; it must actually work."""

    @staticmethod
    def _example():
        text = REPORT_DOC.read_text(encoding="utf-8")
        blocks = re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)
        assert blocks, "report-artifact.md has no ```json example"
        return json.loads(blocks[0])

    def test_example_is_valid_json_object(self):
        self.assertIsInstance(self._example(), dict)

    def test_example_generates_without_warnings_and_keeps_its_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            example = Path(tmp) / "example.json"
            example.write_text(json.dumps(self._example()), encoding="utf-8")
            result = run_generator(example, Path(tmp) / "report.html", "--csv", Path(tmp) / "report.csv")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "", "the documented example must not trigger warnings")
            self.assertIn('data-score="90"', (Path(tmp) / "report.html").read_text(encoding="utf-8"))

    def test_every_field_the_example_uses_is_read_by_the_generator(self):
        source = SCRIPT.read_text(encoding="utf-8")
        prospect = self._example()["prospects"][0]
        unused = [key for key in prospect if f'"{key}"' not in source and f"'{key}'" not in source]
        self.assertEqual(unused, [], "documented prospect fields the generator never reads")


if __name__ == "__main__":
    unittest.main()

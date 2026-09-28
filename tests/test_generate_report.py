"""Unit tests for first-customer-finder/scripts/generate_report.py.

Run with: python3 -m unittest discover -s tests
No third-party dependencies — mirrors the script itself, which is stdlib-only.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "first-customer-finder"
    / "scripts"
    / "generate_report.py"
)
_SPEC = importlib.util.spec_from_file_location("generate_report", MODULE_PATH)
generate_report = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(generate_report)


class EscTests(unittest.TestCase):
    def test_escapes_html(self):
        self.assertEqual(generate_report.esc("<b>&"), "&lt;b&gt;&amp;")

    def test_none_becomes_empty_string(self):
        self.assertEqual(generate_report.esc(None), "")


class ClampTests(unittest.TestCase):
    def test_within_range(self):
        self.assertEqual(generate_report.clamp(42), 42)

    def test_clamps_high(self):
        self.assertEqual(generate_report.clamp(500), 100)

    def test_clamps_low(self):
        self.assertEqual(generate_report.clamp(-10), 0)

    def test_respects_custom_maximum(self):
        self.assertEqual(generate_report.clamp(9, maximum=5), 5)

    def test_non_numeric_defaults_to_zero(self):
        self.assertEqual(generate_report.clamp("not-a-number"), 0)
        self.assertEqual(generate_report.clamp(None), 0)

    def test_rounds_to_nearest_int(self):
        self.assertEqual(generate_report.clamp(41.6), 42)


class ItemsTests(unittest.TestCase):
    def test_none_returns_empty_list(self):
        self.assertEqual(generate_report.items(None), [])

    def test_list_passthrough(self):
        self.assertEqual(generate_report.items([1, 2]), [1, 2])

    def test_scalar_is_wrapped(self):
        self.assertEqual(generate_report.items("x"), ["x"])


class SafeUrlTests(unittest.TestCase):
    def test_accepts_https(self):
        self.assertEqual(generate_report.safe_url("https://example.com/a"), "https://example.com/a")

    def test_accepts_http(self):
        self.assertEqual(generate_report.safe_url("http://example.com"), "http://example.com")

    def test_rejects_javascript_scheme(self):
        self.assertEqual(generate_report.safe_url("javascript:alert(1)"), "#")

    def test_rejects_empty(self):
        self.assertEqual(generate_report.safe_url(""), "#")
        self.assertEqual(generate_report.safe_url(None), "#")

    def test_rejects_scheme_without_host(self):
        self.assertEqual(generate_report.safe_url("https://"), "#")


class StageClassTests(unittest.TestCase):
    def test_high_intent_is_hot(self):
        self.assertEqual(generate_report.stage_class("High intent"), "hot")

    def test_problem_aware_is_warm(self):
        self.assertEqual(generate_report.stage_class("Problem aware"), "warm")

    def test_trigger_present_is_warm(self):
        self.assertEqual(generate_report.stage_class("Trigger present"), "warm")

    def test_unknown_defaults_cool(self):
        self.assertEqual(generate_report.stage_class("Potential fit"), "cool")
        self.assertEqual(generate_report.stage_class(None), "cool")


class ConfidenceClassTests(unittest.TestCase):
    def test_high(self):
        self.assertEqual(generate_report.confidence_class("High"), "hot")

    def test_low(self):
        self.assertEqual(generate_report.confidence_class("Low"), "cool")

    def test_medium_and_unknown_default_warm(self):
        self.assertEqual(generate_report.confidence_class("Medium"), "warm")
        self.assertEqual(generate_report.confidence_class(""), "warm")
        self.assertEqual(generate_report.confidence_class(None), "warm")


class ParseDateTests(unittest.TestCase):
    def test_parses_iso_date(self):
        self.assertEqual(generate_report.parse_date("2026-07-01"), date(2026, 7, 1))

    def test_parses_datetime_prefix(self):
        self.assertEqual(generate_report.parse_date("2026-07-01T10:00:00Z"), date(2026, 7, 1))

    def test_invalid_returns_none(self):
        self.assertIsNone(generate_report.parse_date("not a date"))
        self.assertIsNone(generate_report.parse_date(""))
        self.assertIsNone(generate_report.parse_date(None))
        self.assertIsNone(generate_report.parse_date("date unavailable"))


class IsStaleTests(unittest.TestCase):
    def test_recent_signal_not_stale(self):
        self.assertFalse(generate_report.is_stale("2026-07-01", "2026-08-02"))

    def test_old_signal_is_stale(self):
        self.assertTrue(generate_report.is_stale("2024-01-01", "2026-08-02"))

    def test_missing_or_invalid_dates_never_flag_stale(self):
        self.assertFalse(generate_report.is_stale(None, "2026-08-02"))
        self.assertFalse(generate_report.is_stale("2026-07-01", None))
        self.assertFalse(generate_report.is_stale("bad", "2026-08-02"))
        self.assertFalse(generate_report.is_stale("date unavailable", "2026-08-02"))

    def test_exactly_at_threshold_is_not_stale(self):
        generated = date(2026, 8, 2)
        signal = generated - timedelta(days=generate_report.STALE_THRESHOLD_DAYS)
        self.assertFalse(generate_report.is_stale(signal.isoformat(), generated.isoformat()))

    def test_one_day_past_threshold_is_stale(self):
        generated = date(2026, 8, 2)
        signal = generated - timedelta(days=generate_report.STALE_THRESHOLD_DAYS + 1)
        self.assertTrue(generate_report.is_stale(signal.isoformat(), generated.isoformat()))


class RenderFilterOptionsTests(unittest.TestCase):
    def test_dedupes_and_covers_default(self):
        prospects = [{"stage": "Warm"}, {"stage": "Hot"}, {"stage": "Warm"}, {}]
        html_out = generate_report.render_filter_options(prospects, "stage", "Potential fit")
        self.assertEqual(html_out.count("<option"), 3)
        self.assertIn('value="Hot"', html_out)
        self.assertIn('value="Warm"', html_out)
        self.assertIn('value="Potential fit"', html_out)


class RenderRejectedTests(unittest.TestCase):
    def test_renders_name_and_reason(self):
        out = generate_report.render_rejected([{"name": "Acme <Co>", "reason": "No corroborating source"}])
        self.assertIn("Acme &lt;Co&gt;", out)
        self.assertIn("No corroborating source", out)

    def test_empty_list_renders_nothing(self):
        self.assertEqual(generate_report.render_rejected([]), "")


class RenderDimensionsTests(unittest.TestCase):
    def test_renders_all_five_dimensions_with_defaults(self):
        out = generate_report.render_dimensions({"pain_strength": 5, "product_fit": 3})
        for label in generate_report.DIMENSIONS.values():
            self.assertIn(label, out)
        self.assertIn("5/5", out)
        self.assertIn("0/5", out)  # timing/reachability/evidence_quality missing -> default 0


class BuildHtmlTests(unittest.TestCase):
    @staticmethod
    def _minimal_data(**overrides):
        data = {
            "title": "Test Report",
            "generated_at": "2026-08-02",
            "prospects": [],
            "patterns": [],
        }
        data.update(overrides)
        return data

    def test_handles_empty_report_without_error(self):
        html_out = generate_report.build_html(self._minimal_data())
        self.assertIn("<!doctype html>", html_out)
        self.assertIn("No qualified prospects supplied.", html_out)

    def test_confidence_badge_rendered(self):
        data = self._minimal_data(prospects=[{
            "name": "Acme",
            "score": 80,
            "confidence": "High",
            "signal_date": "2026-07-01",
        }])
        html_out = generate_report.build_html(data)
        self.assertIn("Confidence: High", html_out)

    def test_no_confidence_badge_when_field_absent(self):
        data = self._minimal_data(prospects=[{"name": "Acme", "score": 80}])
        html_out = generate_report.build_html(data)
        self.assertNotIn("Confidence:", html_out)

    def test_stale_badge_rendered_for_old_signal(self):
        data = self._minimal_data(prospects=[{
            "name": "Old Co",
            "score": 60,
            "signal_date": "2024-01-01",
        }])
        html_out = generate_report.build_html(data)
        self.assertIn("Stale", html_out)

    def test_fresh_signal_has_no_stale_badge(self):
        data = self._minimal_data(prospects=[{
            "name": "Fresh Co",
            "score": 60,
            "signal_date": "2026-07-01",
        }])
        html_out = generate_report.build_html(data)
        self.assertNotIn("Stale", html_out)

    def test_rejected_section_only_rendered_when_present(self):
        without = generate_report.build_html(self._minimal_data())
        self.assertNotIn("Considered, not qualified", without)
        with_rejected = generate_report.build_html(
            self._minimal_data(rejected=[{"name": "X", "reason": "Y"}])
        )
        self.assertIn("Considered, not qualified", with_rejected)

    def test_escapes_untrusted_prospect_fields(self):
        data = self._minimal_data(prospects=[{
            "name": "<script>alert(1)</script>",
            "score": 10,
        }])
        html_out = generate_report.build_html(data)
        self.assertNotIn("<script>alert(1)</script>", html_out)
        self.assertIn("&lt;script&gt;", html_out)

    def test_rejects_unsafe_product_url(self):
        data = self._minimal_data(product_url="javascript:alert(1)")
        html_out = generate_report.build_html(data)
        self.assertNotIn('href="javascript:alert(1)"', html_out)


FULL_DIMENSIONS = {
    "pain_strength": 5,
    "product_fit": 5,
    "timing": 4,
    "reachability": 4,
    "evidence_quality": 4,
}  # 25 + 25 + 16 + 12 + 12 = 90


class DeriveScoreTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(sum(generate_report.WEIGHTS.values()), 100)

    def test_all_fives_is_100_and_all_zeros_is_0(self):
        self.assertEqual(generate_report.derive_score({"dimensions": {k: 5 for k in generate_report.WEIGHTS}}), 100)
        self.assertEqual(generate_report.derive_score({"dimensions": {k: 0 for k in generate_report.WEIGHTS}}), 0)

    def test_matches_framework_formula(self):
        self.assertEqual(generate_report.derive_score({"dimensions": FULL_DIMENSIONS}), 90)

    def test_rounds_half_up(self):
        dims = {k: 0 for k in generate_report.WEIGHTS}
        dims["timing"] = 2.5  # 10.0 exactly
        dims["reachability"] = 0.5  # 1.5 -> 11.5 -> 12
        self.assertEqual(generate_report.derive_score({"dimensions": dims}), 12)

    def test_incomplete_or_invalid_dimensions_return_none(self):
        self.assertIsNone(generate_report.derive_score({}))
        self.assertIsNone(generate_report.derive_score({"dimensions": "x"}))
        self.assertIsNone(generate_report.derive_score({"dimensions": {"pain_strength": 5}}))
        bad = {**FULL_DIMENSIONS, "timing": "n/a"}
        self.assertIsNone(generate_report.derive_score({"dimensions": bad}))
        self.assertIsNone(generate_report.derive_score({"dimensions": {**FULL_DIMENSIONS, "timing": True}}))

    def test_out_of_range_dimensions_are_clamped(self):
        dims = {k: 99 for k in generate_report.WEIGHTS}
        self.assertEqual(generate_report.derive_score({"dimensions": dims}), 100)

    def test_apply_replaces_score_only_when_dimensions_complete(self):
        data = {"prospects": [
            {"name": "A", "score": 10, "dimensions": FULL_DIMENSIONS},
            {"name": "B", "score": 77},
        ]}
        out = generate_report.apply_derived_scores(data)
        self.assertEqual([p["score"] for p in out["prospects"]], [90, 77])
        self.assertEqual(data["prospects"][0]["score"], 10)  # input not mutated


class CollectWarningsTests(unittest.TestCase):
    def test_flags_score_mismatch(self):
        data = {"prospects": [{"name": "A", "score": 82, "dimensions": FULL_DIMENSIONS, "signal_date": "2026-07-01"}]}
        warnings = generate_report.collect_warnings(data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("82", warnings[0])
        self.assertIn("90", warnings[0])

    def test_consistent_prospect_has_no_warnings(self):
        data = {"prospects": [{"name": "A", "score": 90, "dimensions": FULL_DIMENSIONS, "signal_date": "2026-07-01"}]}
        self.assertEqual(generate_report.collect_warnings(data), [])

    def test_flags_incomplete_dimensions(self):
        warnings = generate_report.collect_warnings({"prospects": [{"name": "A", "score": 70}]})
        self.assertEqual(len(warnings), 1)
        self.assertIn("incomplete dimensions", warnings[0])

    def test_flags_high_timing_without_signal_date(self):
        data = {"prospects": [{"name": "A", "score": 90, "dimensions": FULL_DIMENSIONS}]}
        warnings = generate_report.collect_warnings(data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("signal_date", warnings[0])

    def test_low_timing_without_signal_date_is_fine(self):
        dims = {**FULL_DIMENSIONS, "timing": 2}
        score = generate_report.derive_score({"dimensions": dims})
        data = {"prospects": [{"name": "A", "score": score, "dimensions": dims, "signal_date": "date unavailable"}]}
        self.assertEqual(generate_report.collect_warnings(data), [])


class CsvTests(unittest.TestCase):
    def test_cell_neutralizes_formulas(self):
        for value in ("=SUM(A1)", "+1", "-1", "@cmd", "  =x", "\tx", "\rx"):
            self.assertTrue(generate_report.csv_cell(value).startswith("'"), value)

    def test_cell_passes_normal_text_and_none(self):
        self.assertEqual(generate_report.csv_cell("Acme"), "Acme")
        self.assertEqual(generate_report.csv_cell(None), "")
        self.assertEqual(generate_report.csv_cell(5), "5")

    def _rows(self, data):
        import csv as csv_module
        import io as io_module
        return list(csv_module.DictReader(io_module.StringIO(generate_report.build_csv(data))))

    def test_header_only_for_empty_report(self):
        text = generate_report.build_csv({"prospects": []})
        self.assertEqual(text.strip().split(","), generate_report.CSV_COLUMNS)

    def test_rows_use_derived_score_rank_and_dimensions(self):
        rows = self._rows({"prospects": [
            {"name": "A", "score": 1, "dimensions": FULL_DIMENSIONS, "source_url": "https://example.com/a"},
            {"name": "B", "score": 50},
        ]})
        self.assertEqual([r["rank"] for r in rows], ["1", "2"])
        self.assertEqual(rows[0]["score"], "90")
        self.assertEqual(rows[0]["timing"], "4")
        self.assertEqual(rows[1]["score"], "50")

    def test_unsafe_urls_are_blanked_and_formulas_escaped(self):
        rows = self._rows({"prospects": [{
            "name": "=HYPERLINK(\"http://evil\")",
            "source_url": "javascript:alert(1)",
            "contact_url": "https://example.com/contact",
        }]})
        self.assertEqual(rows[0]["source_url"], "")
        self.assertEqual(rows[0]["contact_url"], "https://example.com/contact")
        self.assertTrue(rows[0]["name"].startswith("'="))

    def test_rank_skips_malformed_entries_without_gaps(self):
        rows = self._rows({"prospects": [{"name": "A"}, "junk", {"name": "B"}]})
        self.assertEqual([r["rank"] for r in rows], ["1", "2"])

    def test_multiline_and_comma_fields_round_trip(self):
        rows = self._rows({"prospects": [{"name": "A", "opener": "Hi, there\nsecond line"}]})
        self.assertEqual(rows[0]["opener"], "Hi, there\nsecond line")


class NewFieldRenderTests(unittest.TestCase):
    def _html(self, **prospect):
        return generate_report.build_html({"generated_at": "2026-08-02", "prospects": [{"name": "Acme", "score": 70, **prospect}]})

    def test_target_role_and_basis_rendered(self):
        out = self._html(target_role="Head of billing", role_basis="inferred")
        self.assertIn("Who: Head of billing (inferred)", out)

    def test_contact_route_link_rendered_only_when_safe(self):
        self.assertIn("Verified contact route", self._html(contact_url="https://example.com/contact"))
        self.assertNotIn("Verified contact route", self._html(contact_url="javascript:alert(1)"))
        self.assertNotIn("Verified contact route", self._html())

    def test_checked_at_rendered_next_to_source_date(self):
        self.assertIn("checked 2026-08-01", self._html(signal_date="2026-07-01", checked_at="2026-08-01"))

    def test_top_prospect_and_average_follow_derived_scores(self):
        data = {"generated_at": "2026-08-02", "prospects": [
            {"name": "Inflated", "score": 99, "dimensions": {k: 1 for k in generate_report.WEIGHTS}},
            {"name": "Honest", "score": 90, "dimensions": FULL_DIMENSIONS},
        ]}
        out = generate_report.build_html(data)
        self.assertIn("<h2>Honest</h2>", out)
        self.assertIn("55/100", out)  # (20 + 90) / 2


class CliTests(unittest.TestCase):
    def _run_cli(self, input_path: Path, output_path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), str(input_path), str(output_path)],
            capture_output=True,
            text=True,
        )

    def test_generates_report_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "analysis.json"
            output_path = Path(tmp) / "report.html"
            input_path.write_text(json.dumps({
                "title": "CLI Test",
                "generated_at": "2026-08-02",
                "prospects": [],
                "patterns": [],
            }))
            result = self._run_cli(input_path, output_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            self.assertIn("CLI Test", output_path.read_text())

    def test_rejects_non_object_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "analysis.json"
            output_path = Path(tmp) / "report.html"
            input_path.write_text(json.dumps([1, 2, 3]))
            result = self._run_cli(input_path, output_path)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output_path.exists())

    def test_creates_missing_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "analysis.json"
            output_path = Path(tmp) / "nested" / "dir" / "report.html"
            input_path.write_text(json.dumps({"title": "Nested"}))
            result = self._run_cli(input_path, output_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())


    def test_csv_flag_writes_bom_prefixed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "analysis.json"
            output_path = Path(tmp) / "report.html"
            csv_path = Path(tmp) / "out" / "prospects.csv"
            input_path.write_text(json.dumps({"prospects": [{"name": "Привет", "score": 60}]}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(input_path), str(output_path), "--csv", str(csv_path)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            raw = csv_path.read_bytes()
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
            self.assertIn("Привет", raw.decode("utf-8-sig"))

    def test_no_csv_written_without_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "analysis.json"
            input_path.write_text(json.dumps({"title": "x"}))
            self._run_cli(input_path, Path(tmp) / "report.html")
            self.assertEqual([p.name for p in Path(tmp).iterdir() if p.suffix == ".csv"], [])

    def test_warnings_go_to_stderr_but_do_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "analysis.json"
            output_path = Path(tmp) / "report.html"
            input_path.write_text(json.dumps({"prospects": [
                {"name": "A", "score": 82, "dimensions": FULL_DIMENSIONS, "signal_date": "2026-07-01"}
            ]}))
            result = self._run_cli(input_path, output_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("warning:", result.stderr)
            self.assertIn("90", output_path.read_text())


if __name__ == "__main__":
    unittest.main()

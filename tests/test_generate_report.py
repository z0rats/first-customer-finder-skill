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


if __name__ == "__main__":
    unittest.main()

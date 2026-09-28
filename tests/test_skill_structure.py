"""Structural checks for the skill and plugin packaging.

SKILL.md is prompt text, so its behavior can't be unit tested (see TESTING.md), but the
things around it can drift silently: broken reference links, mismatched versions, a
frontmatter the loader would reject. Those are checked here.

Run with: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "first-customer-finder"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Skill loader limits (Claude Code skill spec).
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"{path} has no YAML frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()
    return fields


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class SkillFrontmatterTests(unittest.TestCase):
    def setUp(self):
        self.fields = frontmatter(SKILL_MD)

    def test_name_matches_directory_and_spec(self):
        name = self.fields["name"]
        self.assertEqual(name, SKILL_DIR.name)
        self.assertRegex(name, NAME_PATTERN)
        self.assertLessEqual(len(name), MAX_NAME_LENGTH)

    def test_description_present_and_within_limit(self):
        description = self.fields["description"]
        self.assertTrue(description)
        self.assertLessEqual(len(description), MAX_DESCRIPTION_LENGTH)

    def test_description_says_when_to_use_it(self):
        # The description is what triggers the skill; it needs both what and when.
        self.assertIn("Use when", self.fields["description"])

    def test_no_unexpected_frontmatter_keys(self):
        allowed = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
        self.assertLessEqual(set(self.fields), allowed)


class MarkdownLinkTests(unittest.TestCase):
    def test_relative_links_resolve(self):
        broken = []
        for path in [ROOT / "README.md", ROOT / "TESTING.md", *SKILL_DIR.rglob("*.md")]:
            text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
            for target in LINK.findall(text):
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                file_part = target.split("#", 1)[0]
                if file_part and not (path.parent / file_part).exists():
                    broken.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [])

    def test_every_reference_file_is_linked_from_skill_md(self):
        skill_text = SKILL_MD.read_text(encoding="utf-8")
        orphans = [
            p.name for p in (SKILL_DIR / "references").glob("*.md")
            if f"references/{p.name}" not in skill_text
        ]
        self.assertEqual(orphans, [], "reference files SKILL.md never tells the model to read")

    def test_paths_mentioned_in_backticks_exist(self):
        # e.g. `scripts/generate_report.py` in report-artifact.md is relative to the skill dir.
        missing = []
        for path in SKILL_DIR.rglob("*.md"):
            for mention in re.findall(r"`((?:scripts|references)/[\w./-]+)`", path.read_text(encoding="utf-8")):
                if not (SKILL_DIR / mention).exists():
                    missing.append(f"{path.relative_to(ROOT)} -> {mention}")
        self.assertEqual(missing, [])


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.package = load_json(ROOT / "package.json")
        self.plugin = load_json(ROOT / ".claude-plugin" / "plugin.json")
        self.marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")

    def test_versions_agree(self):
        self.assertEqual(self.plugin["version"], self.package["version"])
        self.assertRegex(self.package["version"], r"^\d+\.\d+\.\d+$")

    def test_plugin_points_at_the_skill_directory(self):
        for entry in self.plugin["skills"]:
            self.assertTrue((ROOT / entry / "SKILL.md").is_file(), entry)
        self.assertEqual(self.plugin["name"], frontmatter(SKILL_MD)["name"])

    def test_marketplace_lists_this_plugin(self):
        names = [p["name"] for p in self.marketplace["plugins"]]
        self.assertIn(self.plugin["name"], names)
        for plugin in self.marketplace["plugins"]:
            self.assertTrue((ROOT / plugin["source"]).is_dir(), plugin["source"])

    def test_repository_urls_agree(self):
        slug = "z0rats/first-customer-finder-skill"
        self.assertIn(slug, self.package["repository"]["url"])
        self.assertIn(slug, self.plugin["homepage"])

    def test_package_files_entries_exist(self):
        for entry in self.package["files"]:
            if not entry.startswith("!"):
                self.assertTrue((ROOT / entry).exists(), entry)

    def test_bin_target_exists_and_has_shebang(self):
        for target in self.package["bin"].values():
            first_line = (ROOT / target).read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(first_line, "#!/usr/bin/env node")

    def test_test_script_runs_every_test_file(self):
        script = self.package["scripts"]["test"]
        for path in sorted((ROOT / "tests").glob("*.test.js")):
            self.assertIn(f"tests/{path.name}", script, f"{path.name} is never run by `npm test`")

    def test_gitignore_keeps_report_outputs_out_of_git(self):
        self.assertIn("outputs/", (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    unittest.main()

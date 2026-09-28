"use strict";

// Checks what `npm publish` would actually ship, since a wrong `files` list is invisible
// until someone installs the published package.

const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");

function packedFiles() {
  const npm = process.platform === "win32" ? "npm.cmd" : "npm";
  const result = spawnSync(npm, ["pack", "--dry-run", "--json", "--ignore-scripts"], {
    cwd: ROOT,
    encoding: "utf8",
    shell: process.platform === "win32",
  });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout)[0].files.map((file) => file.path);
}

test("published package contains the skill, installer and plugin manifests", () => {
  const files = packedFiles();
  for (const expected of [
    "package.json",
    "README.md",
    "LICENSE",
    "scripts/install.js",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "first-customer-finder/SKILL.md",
    "first-customer-finder/scripts/generate_report.py",
    "first-customer-finder/references/research-framework.md",
    "first-customer-finder/references/report-artifact.md",
    "first-customer-finder/references/locale-playbooks.md",
  ]) {
    assert.ok(files.includes(expected), `${expected} is missing from the package`);
  }
});

test("published package leaves out tests, outputs, caches and dev files", () => {
  const leaked = packedFiles().filter((file) =>
    /^(tests|outputs|node_modules|\.github|\.claude\/)/.test(file) ||
    /(__pycache__|\.pyc$|\.DS_Store|package-lock\.json|TESTING\.md)/.test(file),
  );
  assert.deepEqual(leaked, []);
});

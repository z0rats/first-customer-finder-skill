"use strict";

const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const INSTALLER = path.resolve(__dirname, "..", "scripts", "install.js");

function install(skillsDir) {
  return spawnSync(process.execPath, [INSTALLER, "--skills-dir", skillsDir], { encoding: "utf8" });
}

function tempDir(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "fcf-install-"));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

test("installs the skill and leaves no staging directory behind", (t) => {
  const skillsDir = path.join(tempDir(t), "skills");
  const result = install(skillsDir);
  assert.equal(result.status, 0, result.stderr);
  assert.ok(fs.existsSync(path.join(skillsDir, "first-customer-finder", "SKILL.md")));
  assert.deepEqual(fs.readdirSync(skillsDir), ["first-customer-finder"]);
});

test("reinstall replaces the previous copy and drops stale files", (t) => {
  const skillsDir = path.join(tempDir(t), "skills");
  assert.equal(install(skillsDir).status, 0);
  const stale = path.join(skillsDir, "first-customer-finder", "stale.txt");
  fs.writeFileSync(stale, "old");
  assert.equal(install(skillsDir).status, 0);
  assert.ok(!fs.existsSync(stale));
  assert.deepEqual(fs.readdirSync(skillsDir), ["first-customer-finder"]);
});

test("does not copy Python bytecode caches", (t) => {
  const skillsDir = path.join(tempDir(t), "skills");
  const cache = path.resolve(__dirname, "..", "first-customer-finder", "scripts", "__pycache__");
  const created = !fs.existsSync(cache);
  fs.mkdirSync(cache, { recursive: true });
  fs.writeFileSync(path.join(cache, "generate_report.cpython-39.pyc"), "x");
  t.after(() => { if (created) fs.rmSync(cache, { recursive: true, force: true }); });
  assert.equal(install(skillsDir).status, 0);
  assert.ok(!fs.existsSync(path.join(skillsDir, "first-customer-finder", "scripts", "__pycache__")));
});

test("refuses to overwrite a symlinked installation", (t) => {
  const root = tempDir(t);
  const skillsDir = path.join(root, "skills");
  const checkout = path.join(root, "checkout");
  fs.mkdirSync(skillsDir);
  fs.mkdirSync(checkout);
  fs.symlinkSync(checkout, path.join(skillsDir, "first-customer-finder"));
  const result = install(skillsDir);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /symlink/);
  assert.ok(fs.lstatSync(path.join(skillsDir, "first-customer-finder")).isSymbolicLink());
  assert.deepEqual(fs.readdirSync(checkout), []);
});

function run(args, env = {}) {
  return spawnSync(process.execPath, [INSTALLER, ...args], {
    encoding: "utf8",
    env: { ...process.env, ...env },
  });
}

test("--help prints usage and installs nothing", (t) => {
  const home = tempDir(t);
  const result = run(["--help"], { HOME: home, USERPROFILE: home, CLAUDE_CONFIG_DIR: "" });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /Usage:/);
  assert.deepEqual(fs.readdirSync(home), []);
});

test("rejects unknown options and a missing --skills-dir value", () => {
  const unknown = run(["--nope"]);
  assert.notEqual(unknown.status, 0);
  assert.match(unknown.stderr, /Unknown option: --nope/);

  const missing = run(["--skills-dir"]);
  assert.notEqual(missing.status, 0);
  assert.match(missing.stderr, /--skills-dir requires a value/);
});

test("installs the complete skill tree, script included", (t) => {
  const skillsDir = path.join(tempDir(t), "skills");
  assert.equal(install(skillsDir).status, 0);
  const dest = path.join(skillsDir, "first-customer-finder");
  for (const file of [
    "SKILL.md",
    "references/research-framework.md",
    "references/report-artifact.md",
    "references/locale-playbooks.md",
    "scripts/generate_report.py",
  ]) {
    assert.ok(fs.existsSync(path.join(dest, file)), `${file} missing from install`);
  }
});

test("defaults to $CLAUDE_CONFIG_DIR/skills when set", (t) => {
  const home = tempDir(t);
  const config = path.join(home, "custom-claude");
  const result = run([], { HOME: home, USERPROFILE: home, CLAUDE_CONFIG_DIR: config });
  assert.equal(result.status, 0, result.stderr);
  assert.ok(fs.existsSync(path.join(config, "skills", "first-customer-finder", "SKILL.md")));
});

test("defaults to ~/.claude/skills without CLAUDE_CONFIG_DIR", (t) => {
  const home = tempDir(t);
  const result = run([], { HOME: home, USERPROFILE: home, CLAUDE_CONFIG_DIR: "" });
  assert.equal(result.status, 0, result.stderr);
  assert.ok(fs.existsSync(path.join(home, ".claude", "skills", "first-customer-finder", "SKILL.md")));
});

test("expands a leading ~ in --skills-dir", (t) => {
  const home = tempDir(t);
  const result = run(["--skills-dir", "~/my-skills"], { HOME: home, USERPROFILE: home });
  assert.equal(result.status, 0, result.stderr);
  assert.ok(fs.existsSync(path.join(home, "my-skills", "first-customer-finder", "SKILL.md")));
});

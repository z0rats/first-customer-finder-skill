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

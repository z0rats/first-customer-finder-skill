"use strict";

// Runs the generated report's inline filter/sort script in jsdom. That script is the only
// client-side logic we ship, and Python tests can't execute it.

const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { JSDOM, VirtualConsole } = require("jsdom");

const ROOT = path.resolve(__dirname, "..");
const GENERATOR = path.join(ROOT, "first-customer-finder", "scripts", "generate_report.py");
const FIXTURE = path.join(__dirname, "fixtures", "sample_report.json");

function generate(input) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "fcf-report-"));
  try {
    const out = path.join(dir, "report.html");
    const result = spawnSync("python3", [GENERATOR, input, out], { encoding: "utf8" });
    assert.equal(result.status, 0, result.stderr);
    return fs.readFileSync(out, "utf8");
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

const html = generate(FIXTURE);

function openReport(source = html) {
  const errors = [];
  const dom = new JSDOM(source, {
    runScripts: "dangerously",
    virtualConsole: new VirtualConsole().on("jsdomError", (e) => errors.push(e)),
  });
  const { document } = dom.window;
  const $ = (id) => document.getElementById(id);
  const set = (id, value, eventName = "input") => {
    $(id).value = value;
    $(id).dispatchEvent(new dom.window.Event(eventName, { bubbles: true }));
  };
  const visible = () =>
    [...document.querySelectorAll(".prospect")]
      .filter((card) => card.style.display !== "none")
      .sort((a, b) => Number(a.style.order) - Number(b.style.order))
      .map((card) => card.dataset.name);
  return { dom, document, errors, $, set, visible, click: (id) => $(id).click() };
}

test("script runs without errors and shows every prospect", () => {
  const page = openReport();
  assert.deepEqual(page.errors, []);
  assert.equal(page.$("resultCount").textContent, "Showing 3 of 3 prospects");
  assert.deepEqual(page.visible(), ["Acme Gym", "Клуб «Ритм»", "Beta Studio"]);
});

test("min score hides lower-scored prospects and renumbers the rest", () => {
  const page = openReport();
  page.set("minScore", "60");
  assert.deepEqual(page.visible(), ["Acme Gym", "Клуб «Ритм»"]);
  assert.equal(page.$("resultCount").textContent, "Showing 2 of 3 prospects");
  const ranks = [...page.document.querySelectorAll(".prospect")]
    .filter((card) => card.style.display !== "none")
    .map((card) => card.querySelector(".rank").textContent);
  assert.deepEqual(ranks, ["01", "02"]);
});

test("stage and source filters combine", () => {
  const page = openReport();
  page.set("stageFilter", "Problem aware", "change");
  assert.deepEqual(page.visible(), ["Клуб «Ритм»"]);
  page.set("sourceFilter", "Public forum", "change");
  assert.deepEqual(page.visible(), []);
  assert.notEqual(page.$("noResults").style.display, "none");
});

test("search is case-insensitive, including Cyrillic", () => {
  const page = openReport();
  page.set("searchInput", "aCmE");
  assert.deepEqual(page.visible(), ["Acme Gym"]);
  page.set("searchInput", "РИТМ");
  assert.deepEqual(page.visible(), ["Клуб «Ритм»"]);
});

test("sorting by score ascending and by name", () => {
  const page = openReport();
  page.set("sortSelect", "score-asc", "change");
  assert.deepEqual(page.visible(), ["Beta Studio", "Клуб «Ритм»", "Acme Gym"]);
  page.set("sortSelect", "name-asc", "change");
  assert.equal(page.visible()[0], "Acme Gym");
});

test("reset restores the default view", () => {
  const page = openReport();
  page.set("searchInput", "zzz");
  page.set("minScore", "90");
  page.set("sortSelect", "score-asc", "change");
  assert.deepEqual(page.visible(), []);
  page.click("resetFilters");
  assert.equal(page.$("searchInput").value, "");
  assert.equal(page.$("minScore").value, "0");
  assert.deepEqual(page.visible(), ["Acme Gym", "Клуб «Ритм»", "Beta Studio"]);
  assert.equal(page.$("noResults").style.display, "none");
});

test("report with no prospects renders no toolbar and no script errors", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "fcf-empty-"));
  try {
    const input = path.join(dir, "empty.json");
    fs.writeFileSync(input, JSON.stringify({ title: "Empty", generated_at: "2026-07-12" }));
    const page = openReport(generate(input));
    assert.deepEqual(page.errors, []);
    assert.equal(page.document.getElementById("searchInput"), null);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("hostile prospect fields cannot inject markup or scripts", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "fcf-xss-"));
  try {
    const payload = '"><img src=x onerror="window.pwned=1"><script>window.pwned=1</script>';
    const input = path.join(dir, "xss.json");
    fs.writeFileSync(
      input,
      JSON.stringify({
        title: payload,
        prospects: [
          { name: payload, stage: payload, source_type: payload, pain_signal: payload, opener: payload, score: 50 },
        ],
      }),
    );
    const page = openReport(generate(input));
    assert.deepEqual(page.errors, []);
    assert.equal(page.dom.window.pwned, undefined);
    assert.equal(page.document.querySelectorAll("img").length, 0);
    assert.equal(page.visible().length, 1);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

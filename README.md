# Claude First Customer Finder Skill

A Claude Code skill that turns a startup URL or product idea into a qualified shortlist of potential first customers using recent public pain, demand, and timing signals.

It defines the ideal customer profile, researches public sources, links the evidence behind every prospect, ranks fit and timing, drafts a source-based opener with a concrete manual CTA, and creates a polished HTML report. It never sends outreach automatically.

## What It Does

- Analyzes a startup URL, repository, or product description
- Defines the primary and adjacent ideal customer profiles
- Finds explicit demand, pain, workaround, switching, and timing signals
- Qualifies prospects with an evidence-based score
- Links every primary prospect to the original public source
- Drafts respectful, source-based outreach openers with concrete manual CTAs
- Recommends official/public contact routes without private enrichment
- Checks each candidate for counter-evidence (already solved, seller not buyer, wrong buyer) before qualifying it
- Recomputes every score from its five dimensions so totals can't drift from the breakdown
- Creates a responsive standalone HTML report, plus an optional spreadsheet-safe CSV
- Keeps all outreach manual by default
- Avoids private contact enrichment and sensitive personal data

## Installation

**npm installer** (fastest):

```bash
npx --yes first-customer-finder-skill@latest
```

This installs the skill into:

```text
~/.claude/skills/first-customer-finder
```

**Claude Code plugin** (this repo is its own marketplace):

```text
/plugin marketplace add z0rats/first-customer-finder-skill
/plugin install first-customer-finder@z0rats
```

Restart Claude Code after installation.

## How long it takes

This is a deep-research skill, not a chat answer — it searches, and in `standard`/`deep` mode fetches and verifies real pages, before anything reaches the shortlist. Expect roughly **10–15 minutes for a `standard` run** in Claude Code; `deep` mode (up to twenty prospects) takes noticeably longer.

To speed things up:

- Say **"quick mode"** — five prospects instead of ten roughly halves the research.
- You can shrink scope **mid-run**: say *"quick mode is fine — wrap up with what's verified"* and the skill re-plans instead of finishing every search bucket.
- If your environment prompts for fetch/browse permission per domain, approving "allow all for this site" once avoids repeat prompts — research tends to cluster on a handful of domains, so prompts stop quickly.

## Usage

Claude Code activates the skill automatically when a request matches its description. Just ask naturally, for example:

```text
Find ten evidence-backed potential first customers for https://example.com and create the final HTML report.
```

Find design partners:

```text
Find first customers in design-partners mode for this startup: [URL]. Prioritize people publicly describing the problem and likely to give product feedback.
```

B2B research:

```text
Find first customers in b2b mode for [URL]. Find public business triggers, qualify the relevant companies, and draft one opener per prospect without sending anything.
```

Skip companies you've already contacted:

```text
Find first customers for [URL]. Exclude these from the results: acme.com, Example Corp, contoso.io.
```

Get the shortlist as a CSV too:

```text
Find first customers for [URL] and also export the shortlist as a CSV.
```

Go deeper on one prospect after the report is done:

```text
Expand on prospect 3 in the last report — find more evidence and update it.
```

Ask for more without repeats (the skill reads earlier reports' JSON from `outputs/`):

```text
Find more first customers for [URL] — skip everyone from the last report, and avoid enterprise buyers.
```

## Output

The report includes:

1. Early-customer verdict
2. Primary ICP and disqualifiers
3. Highest-confidence prospect
4. Evidence-backed prospect shortlist
5. Fit and timing scores, plus a confidence rating per prospect
6. Source links and signal dates, with a stale-signal flag when a signal is over a year old
7. Personalized outreach openers with concrete CTAs
8. Repeated pain patterns
9. Notable candidates considered but not qualified, with the reason
10. Seven-day manual outreach plan
11. Research limitations

Each prospect can also carry the date it was checked, the target role (observed or inferred), and a verified public contact route.

Prospects are hypotheses based on public signals, not confirmed customers or guaranteed buyers.

## Modes

- `quick`: up to five strong prospects
- `standard`: up to ten prospects across several source types
- `deep`: up to twenty prospects and repeated-pattern analysis
- `design-partners`: feedback-oriented early adopters
- `b2b`: companies and public business triggers
- `community`: explicit requests and public discussion signals

## Development

`scripts/generate_report.py` and the installer have no runtime dependencies. The only dev dependency is `jsdom`, used to run the report's filter script in a fake browser. Install it once, then run everything:

```bash
npm ci
npm test
# or separately:
python3 -m unittest discover -s tests
node --test tests/install.test.js tests/package.test.js tests/report-filters.test.js
```

What the tests cover:

- `tests/test_generate_report.py` — unit tests for the generator's helpers (scoring, escaping, CSV, staleness).
- `tests/test_cli.py` — runs the generator as a command against `tests/fixtures/sample_report.json`, and checks that the JSON example in `report-artifact.md` still generates cleanly.
- `tests/test_skill_structure.py` — `SKILL.md` frontmatter, relative links, and that the versions and URLs in `package.json` and `.claude-plugin/` agree.
- `tests/install.test.js` — the installer, including default paths, `~` expansion, and refusing to overwrite a symlink.
- `tests/package.test.js` — what `npm pack` would publish (and that tests and `outputs/` stay out).
- `tests/report-filters.test.js` — the report's search, filter, sort, and reset behavior, plus a script-injection check.

GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs `npm test` on every push to `main` and every pull request, on Linux and macOS with Python 3.9 (the macOS system version) and 3.14 and Node 22, 24, and 26.

The `SKILL.md` workflow itself isn't covered by automated tests — it's a behavior spec, not code. Validate changes to it by running the golden scenarios in [TESTING.md](TESTING.md) against a real Claude Code session.

## Manual Installation

```bash
git clone https://github.com/z0rats/first-customer-finder-skill.git
mkdir -p ~/.claude/skills
cp -R first-customer-finder-skill/first-customer-finder ~/.claude/skills/first-customer-finder
```

Restart Claude Code after installation.

## Credits

This repo started as a fork of [codex-first-customer-finder-skill](https://github.com/Kappaemme-git/codex-first-customer-finder-skill) by Francesco Mistero (the Codex-agent original) — see `LICENSE` for that project's copyright. Later revisions also borrowed structure, wording, and workflow ideas from [carolinacherry/claude-first-customer-finder-skill](https://github.com/carolinacherry/claude-first-customer-finder-skill) by Daniel An. Evidence-hygiene rules (separate checked date, counter-evidence check, contact-route verification, CSV formula escaping, safer installer) were adapted from the upstream Codex repo's v2 workflow; its local history/state machinery was deliberately not adopted. This fork adds locale playbooks for non-English markets (starting with CIS/Russian-speaking) and other workflow changes on top of both.

## License

MIT

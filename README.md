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
- Creates a responsive standalone HTML report
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

Go deeper on one prospect after the report is done:

```text
Expand on prospect 3 in the last report — find more evidence and update it.
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

Prospects are hypotheses based on public signals, not confirmed customers or guaranteed buyers.

## Modes

- `quick`: up to five strong prospects
- `standard`: up to ten prospects across several source types
- `deep`: up to twenty prospects and repeated-pattern analysis
- `design-partners`: feedback-oriented early adopters
- `b2b`: companies and public business triggers
- `community`: explicit requests and public discussion signals

## Development

`scripts/generate_report.py` has no third-party dependencies, and neither do its tests. Run them with:

```bash
npm test
# or directly:
python3 -m unittest discover -s tests
```

The `SKILL.md` workflow itself isn't covered by automated tests — it's a behavior spec, not code. Validate changes to it by running the golden scenarios in [TESTING.md](TESTING.md) against a real Claude Code session.

## Manual Installation

```bash
git clone https://github.com/z0rats/first-customer-finder-skill.git
mkdir -p ~/.claude/skills
cp -R first-customer-finder-skill/first-customer-finder ~/.claude/skills/first-customer-finder
```

Restart Claude Code after installation.

## Credits

This repo started as a fork of [codex-first-customer-finder-skill](https://github.com/Kappaemme-git/codex-first-customer-finder-skill) by Francesco Mistero (the Codex-agent original) — see `LICENSE` for that project's copyright. Later revisions also borrowed structure, wording, and workflow ideas from [carolinacherry/claude-first-customer-finder-skill](https://github.com/carolinacherry/claude-first-customer-finder-skill) by Daniel An. This fork adds locale playbooks for non-English markets (starting with CIS/Russian-speaking) and other workflow changes on top of both.

## License

MIT

# Claude First Customer Finder Skill

A Claude Code skill that turns a startup URL or product idea into a qualified shortlist of potential first customers using recent public pain, demand, and timing signals.

It defines the ideal customer profile, researches public sources, links the evidence behind every prospect, ranks fit and timing, drafts a source-based opener, and creates a polished HTML report. It never sends outreach automatically.

## What It Does

- Analyzes a startup URL, repository, or product description
- Defines the primary and adjacent ideal customer profiles
- Finds explicit demand, pain, workaround, switching, and timing signals
- Qualifies prospects with an evidence-based score
- Links every primary prospect to the original public source
- Drafts respectful, source-based outreach openers
- Creates a responsive standalone HTML report
- Keeps all outreach manual by default
- Avoids private contact enrichment and sensitive personal data

## Installation

```bash
npx --yes claude-first-customer-finder-skill@latest
```

This installs the skill into:

```text
~/.claude/skills/first-customer-finder
```

Restart Claude Code after installation.

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

## Output

The report includes:

1. Early-customer verdict
2. Primary ICP and disqualifiers
3. Highest-confidence prospect
4. Evidence-backed prospect shortlist
5. Fit and timing scores
6. Source links and signal dates
7. Personalized outreach openers
8. Repeated pain patterns
9. Seven-day manual outreach plan
10. Research limitations

Prospects are hypotheses based on public signals, not confirmed customers or guaranteed buyers.

## Modes

- `quick`: up to five strong prospects
- `standard`: up to ten prospects across several source types
- `deep`: up to twenty prospects and repeated-pattern analysis
- `design-partners`: feedback-oriented early adopters
- `b2b`: companies and public business triggers
- `community`: explicit requests and public discussion signals

## Manual Installation

```bash
git clone https://github.com/z0rats/claude-first-customer-finder-skill.git
mkdir -p ~/.claude/skills
cp -R claude-first-customer-finder-skill/first-customer-finder ~/.claude/skills/first-customer-finder
```

Restart Claude Code after installation.

## License

MIT

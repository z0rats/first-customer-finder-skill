# Manual Test Scenarios

`SKILL.md` is a behavior spec for an LLM, not deterministic code — it can't be covered by
`tests/` (see [README.md](README.md#development) for what those cover). The way to catch a
regression here is to run the skill against a handful of golden scenarios in an actual Claude
Code session and check the output against the checklist below.

Run these after any change to `SKILL.md` or `references/*.md`, not just before a release —
prompt-level regressions are easy to introduce and easy to miss without running the thing.

Each scenario costs real time and tokens (`standard` mode runs ~10-15 minutes per the README) —
budget for that rather than running all six on every tiny wording tweak. Scenario 1 alone is
a reasonable smoke test for most changes; run the full set before publishing a release.

## 1. Baseline — English SaaS product, standard mode

```text
Find first customers for [a real English-language SaaS product URL] in standard mode.
```

Checks the core pipeline end to end. Verify:

- [ ] ICP (primary + adjacent) is stated with disqualifiers
- [ ] Every shortlisted prospect has a fetched, working source URL (open a few yourself)
- [ ] Every prospect has `score`, `confidence`, and a `dimensions` breakdown
- [ ] Report opens as HTML with working search/stage/source filters
- [ ] Any prospect with a signal older than ~12 months shows the "Stale" badge

## 2. CIS / Russian-language product

```text
Find first customers for [a real Russian-language product/landing page URL] in standard mode.
```

Checks that `locale-playbooks.md` actually gets applied, not just referenced. Verify:

- [ ] `search_scope` names the actual RU sources searched (not the English default)
- [ ] At least one non-Habr/VC.ru source shows up (Klerk.ru, Cossa.ru, Отзовик, hh.ru vacancies,
      a registry page, etc. — whichever fits the product)
- [ ] Openers are drafted in Russian, not auto-translated to English
- [ ] If the product is Western-owned and a prospect is Russia-based, the `caution` field flags
      the jurisdiction/sanctions check rather than silently drafting outreach
- [ ] If the seven-day plan's window lands in Jan 1-15 or May 1-15, the plan flags the possible
      holiday overlap instead of assuming a plain Mon-Fri cadence

## 3. Quick mode + mid-run "hurry up"

```text
Find first customers for [any product URL] in standard mode.
```

After it starts researching, interrupt with:

```text
Quick mode is fine, wrap up with what's verified.
```

Verify:

- [ ] It stops queuing new search buckets and ships with what's already verified
- [ ] The report or response notes which buckets were cut short
- [ ] It doesn't fabricate prospects to hit a target count

## 4. Exclusion list

```text
Find first customers for [any product URL]. Exclude these from the results:
[a company/domain you're confident would otherwise show up, or a made-up one for a clean test].
```

Verify:

- [ ] The excluded entity does not appear in the shortlist
- [ ] The report or response notes an exclusion list was applied

## 5. Drill-down follow-up

After any completed report, ask:

```text
Expand on prospect [N] — find more evidence and update it.
```

Verify:

- [ ] It re-researches only that one prospect, not the whole pipeline
- [ ] The same report file (`outputs/...`) is regenerated in place — same path, updated content
      — not a second report
- [ ] The response states what changed for that prospect

## 6. Two-sided marketplace

```text
Find first customers for [a real two-sided marketplace product, e.g. a marketplace connecting
buyers and sellers] in standard mode.
```

Verify:

- [ ] The shortlist is filtered to one primary ICP (not a mix of both sides scored together)
- [ ] The adjacent side is mentioned under patterns/limits, not blended into the shortlist

## If something fails

Fix the wording in `SKILL.md` or the relevant `references/*.md` file, then re-run just that
scenario — don't assume a fix for one scenario didn't affect another; a quick re-run of
Scenario 1 after any `research-framework.md` or `report-artifact.md` change is cheap insurance.

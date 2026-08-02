# Research and Qualification Framework

Use this framework to keep prospect research evidence-based, current, and respectful.

## Research sequence

### Product brief

Define:

- product and promised outcome
- primary user and economic buyer
- urgent job to be done
- current alternative or workaround
- likely adoption trigger
- geography or language constraint
- clear disqualifiers

Do not begin broad lead collection until this brief is specific enough to reject weak matches.

### Query buckets

Search several buckets rather than repeating one query:

1. **Explicit demand:** "looking for," "recommend a tool," "alternative to," "does anything exist."
2. **Pain:** "takes hours," "manual," "frustrating," "hate," "difficult," "keeps breaking."
3. **Workaround:** spreadsheets, copy-paste, virtual assistants, scripts, templates, or repeated manual steps.
4. **Switching:** cancellation, migration, missing feature, pricing complaint, or competitor frustration.
5. **Timing:** public launch, hiring, expansion, new workflow, regulation, integration, or process change relevant to the product.

Adapt wording to the audience's language. Search the original public page and do not qualify from a search snippet alone.

### Source mix

Useful public sources include:

- forums and public community discussions
- public social posts and replies
- product reviews and app marketplace reviews
- GitHub issues and public feature requests
- public company pages, job posts, changelogs, or announcements
- public "looking for a tool" posts and directories

Avoid private groups, gated communities, data brokers, scraped contact databases, and sources that prohibit access.

## Verification rule

Qualify only from the original public page, fetched and read — not from a search snippet, an aggregator summary, or memory. Each signal that reaches the shortlist needs: source URL, source title, source type, visible publication date (or "date unavailable"), and a note of what was directly observed versus inferred.

Some high-value sources block server-side fetching (Reddit, G2/TrustRadius, Cloudflare-fronted job boards, among others). Do not drop a candidate for that alone — verify through an alternate legitimate route: a browser session, an official API (e.g., HN Algolia for Hacker News), or the site's RSS feed. Third-party archives and cached copies can run months stale; prefer the live page and record which route verified it.

## Freshness window

Default to a 12-month lookback across query buckets unless the user states otherwise or the mode implies a different window (e.g., a slower-moving `deep`-mode market may reasonably look further back). State whatever window was actually used in the report's `search_scope` field so the reader knows the cutoff, not just the sources searched.

A signal older than the window can still qualify — an explicit request from 18 months ago is real evidence — but it must carry its `signal_date` and a visible freshness caveat rather than being included as if current. The generated HTML report flags any prospect whose signal is more than 12 months older than the report date automatically; write accurate dates so that flag is meaningful.

## Deduplication

Merge duplicates before scoring, not after — a duplicate that reaches scoring risks being counted as two separate prospects or inflating a pattern's count.

1. **Canonicalize the URL** before comparing candidates: strip tracking parameters (`utm_*`, `ref`, `fbclid`, `gclid`, session IDs), normalize the scheme to `https`, drop trailing slashes, and treat `www.`, `m.`, and `amp.` subdomains of the same host as the same page.
2. **Match by entity, not just URL.** The same company or person can surface through two different URLs — a forum thread and a comment on it, a company's own post and a news mention of it. Compare normalized display names (case-insensitive, legal suffixes like ООО/ИП/LLC/Inc stripped, whitespace collapsed) combined with the same source domain or platform; treat a match on both as the same entity.
3. **Merge, don't discard.** When two candidates resolve to the same entity, keep the richer combination — the most complete evidence and the most recent date — and fold any additional signal in as extra evidence rather than dropping it. An entity with two independent corroborating signals is stronger evidence than either alone; this feeds directly into `confidence` below.
4. Run this pass across all query-bucket results together, including everything separate subagents returned, before scoring — parallel buckets frequently surface the same entity from different angles.

## Qualification score

Score every dimension from 0 to 5:

- **Pain strength (25%)** — directness, severity, repetition, and cost of the stated problem.
- **Product fit (25%)** — how directly the startup solves the evidenced job.
- **Timing (20%)** — freshness and presence of a current trigger.
- **Public reachability (15%)** — a natural, relevant public or professional contact path exists.
- **Evidence quality (15%)** — specificity, source reliability, and confidence that the signal belongs to the prospect.

Calculate:

```text
score = pain_strength/5*25
      + product_fit/5*25
      + timing/5*20
      + reachability/5*15
      + evidence_quality/5*15
```

Interpretation:

- **80–100:** strong first-customer candidate
- **65–79:** promising, validate quickly
- **50–64:** plausible but missing a material signal
- **Below 50:** do not include in the primary shortlist

An old explicit request can still be relevant, but reduce timing and label the date. A company that merely matches the industry without an evidenced trigger is not a qualified prospect.

### Track near-misses

Keep a short list of candidates that were seriously considered but did not qualify — scored below 50, failed verification, or were disqualified for a specific reason (wrong buyer, jurisdiction caution, dead link, duplicate of a stronger entry). This is not the full search log; it's the handful of candidates a reader would reasonably ask about ("what about the company that posted X?"). Record the entity name and a one-line reason. It goes into the report's `rejected` list (see [report-artifact.md](report-artifact.md)) — it costs little to track and materially increases confidence that the search was thorough rather than cherry-picked.

## Confidence

Score and confidence answer different questions: score is how good a fit this prospect is; confidence is how sure you are that the evidence is real, current, and attached to the right entity. A prospect can score 85 on thin evidence (one post that reads as plausible but couldn't be corroborated) or 85 on solid evidence (two independent public signals, both directly fetched) — flag the difference instead of collapsing it into one number.

Set confidence to one of:

- **High** — two or more independent public signals for the same entity (see Deduplication above), or a single signal from a highly reliable primary source (the company's own page, an official filing or registry) that was directly fetched and verified.
- **Medium** — one directly verified signal from a single source; the default when nothing pushes it up or down.
- **Low** — evidence relies on an unverifiable route (a directory summary that couldn't be corroborated on the live page), a stale cache/archive copy, or the entity attribution itself is uncertain (an anonymous account, a common name with no confirming detail).

Confidence below High does not automatically exclude a prospect, but it must be visible in the report and should push the reader toward validating that specific prospect before outreach rather than treating it as ready.

## Prospect stages

- **High intent:** publicly requesting a solution or actively switching.
- **Problem aware:** clearly describing the pain or expensive workaround.
- **Trigger present:** a current business event makes the product relevant.
- **Potential fit:** ICP match with incomplete evidence; keep outside the primary shortlist.

## Outreach rules

Draft one opener using this shape:

1. mention the public context naturally
2. connect it to the buyer's exact business problem
3. offer a concrete next step
4. ask one low-friction CTA that can be answered, forwarded, or declined

Good CTAs are specific: "Worth sending to whoever owns billing?", "Should I send the teardown?", or "Is a 10-minute workflow review useful this week?" Weak CTAs ask only whether the product "would be useful" without giving the prospect a clear next action.

For each prospect, make the outreach recommendation cover:

- target role or function
- official/public contact route
- primary CTA
- likely objection or risk

Translate the product into the prospect's language. Avoid implementation details, platform mechanics, or internal jargon unless the public source shows the prospect already cares about those details.

Keep the opener under 90 words by default. Never claim the message was sent. Do not include private emails, phone numbers, personal addresses, family information, or sensitive traits.

## Evidence ledger

For each qualified prospect record:

- displayed company, project, or public professional name
- source title and URL
- visible publication date or "date unavailable"
- source type
- concise pain or timing signal
- observed evidence versus inference
- score breakdown
- confidence (High/Medium/Low, see above)
- freshness warning when relevant

Cite sources in the chat response whenever web research was performed.

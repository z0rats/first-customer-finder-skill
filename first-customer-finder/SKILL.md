---
name: first-customer-finder
description: Find and qualify evidence-backed potential first customers, early adopters, design partners, or beta users for a startup using recent public pain and buying signals. Use when analyzing a product URL or idea, defining an ideal customer profile, researching public discussions and business pages, identifying first-user prospects, ranking lead fit and timing, preparing source-based outreach drafts, or creating a shareable early-customer prospecting report without sending messages automatically.
---

# First Customer Finder

Turn a startup URL or product description into a short, evidence-backed list of plausible first customers. Use public signals, preserve privacy, and distinguish a prospect from a confirmed buyer.

Read [references/research-framework.md](references/research-framework.md) before researching or scoring prospects. Read [references/report-artifact.md](references/report-artifact.md) before creating the final report. Read [references/locale-playbooks.md](references/locale-playbooks.md) whenever the product's buyer, language, or stated geography is not English-language/US-EU-centric, and apply the matching playbook before building the search plan.

## Workflow

### 1. Understand the product

- Inspect the supplied URL, repository, landing-page copy, or product description.
- Identify the product, outcome, buyer, user, price or buying motion, geography, and strongest use case.
- Define one primary ICP, one adjacent ICP, pain triggers, positive signals, and disqualifiers.
- Infer missing context when safe and label the inference. Ask one concise question only when ambiguity would materially change the search.
- Determine the buyer's likely language and market. If it is not English-language/US-EU-centric (e.g., CIS, Russian- or Ukrainian-speaking), read [references/locale-playbooks.md](references/locale-playbooks.md) and use the matching playbook for the rest of the workflow.

### 2. Build a public-signal search plan

Search current public sources for:

- explicit tool or alternative requests
- first-person descriptions of the target problem
- manual workflows and repeated workaround complaints
- migration, churn, or competitor-frustration signals
- public company changes that create timing, such as hiring, launching, expanding, or adopting a relevant workflow

Use the query buckets and source mix from the applicable locale playbook when one applies; otherwise use the base buckets above with general web search. When subagent delegation is available, run each query bucket as its own parallel research subagent — one bucket per agent, each returning candidate signals with source URLs, dates, and a summary close to the original wording. Give every agent the product brief and ICP so it can reject weak matches at the source, and instruct it to fetch and quote what it cites; an agent may not return a URL it did not open. Work the buckets sequentially instead if the environment has no subagent support. Prefer original pages over search snippets. Record the source URL, source type, publication date when visible, and the exact evidence supporting qualification.

### 3. Research safely

- Use public, intentionally shared professional or business information only.
- Do not bypass login walls, paywalls, access controls, rate limits, or robots restrictions.
- Do not use data brokers, leaked datasets, private groups, personal email discovery, phone enrichment, or sensitive personal information.
- Do not infer protected traits or target people using health, financial hardship, political belief, sexuality, religion, or other sensitive attributes.
- Prefer companies, public professional profiles, public requests, and community posts relevant to the product.
- Quote minimally and paraphrase by default. Link every material pain or timing signal.

### 4. Verify before you qualify

Fetch the original page for every candidate signal before it can enter the shortlist. A search snippet, an aggregator summary, or a subagent's unquoted paraphrase is not evidence. Confirm the page exists, the signal says what was claimed, and the date. Drop anything that fails this check.

Some high-value sources block server-side fetching (e.g., Reddit, G2/TrustRadius, Cloudflare-fronted job boards). Do not drop a candidate for that reason alone — verify through an alternate legitimate route instead: a browser session, an official API (e.g., HN Algolia for Hacker News), or the site's RSS feed. Third-party archives can run months stale, so prefer the live page and note which route confirmed it. When a subagent already fetched and quoted a source, spot-check its work, and always re-verify the top three prospects yourself before they reach the report.

### 5. Qualify and deduplicate

Score each prospect using the bundled framework:

- pain strength
- product fit
- timing
- public reachability
- evidence quality

Remove duplicates and weak matches. A prospect without a cited pain, need, or timing signal is only a speculative fit and must not appear in the primary shortlist.

Never claim that a prospect is interested, has consented, or will buy. Label the output "potential customer based on public signals."

### 6. Draft outreach, never send it

- Recommend the most natural public or professional channel already associated with the source. Prefer concrete official/public routes such as a company form, public business email, relevant public thread, or professional profile. If no direct public route is found, say so instead of guessing.
- Identify the likely target role or function, not just the company name.
- Translate the product into the buyer's problem language. Do not lead with implementation-layer terms unless the source proves that audience already cares about them.
- Make the next step concrete enough to accept, reject, or forward, such as a scenario, teardown, worksheet, checklist, benchmark, mockup, or sandbox walkthrough.
- Write one short opener grounded only in the cited public context.
- Include a specific CTA, preferably a routing or yes/no ask tied to that next step.
- Note the likely target function and objection when useful for manual outreach planning.
- Avoid pretending to know the person, overstating familiarity, or mentioning unrelated personal details.
- Do not send messages, submit forms, connect, follow, comment, or create CRM records unless the user separately requests and authorizes that action.

### 7. Produce the report

Lead with the most actionable evidence. Use this order:

1. **Verdict** — whether the startup has reachable early-customer signals.
2. **ICP** — buyer, job, trigger, and disqualifiers.
3. **Top prospect** — strongest evidence-backed candidate and why now.
4. **Prospect shortlist** — source, pain signal, fit score, stage, why now, channel, and opener with a concrete CTA.
5. **Repeated patterns** — pains and triggers appearing across prospects.
6. **Seven-day outreach plan** — a manual, low-volume validation sequence.
7. **Limits** — missing evidence and what must be confirmed through real conversations.

Create a standalone HTML report unless the user explicitly requests chat-only output:

1. Write structured JSON using `references/report-artifact.md`.
2. Run `python3 scripts/generate_report.py <analysis.json> <report.html>`.
3. Save the report in the workspace `outputs/` directory (create it if missing).
4. Verify prospect cards, source links, scores, concrete contact routes, CTAs, patterns, outreach plan, and limitations.
5. Return a clickable absolute file link (`file://...`) in the final response, or publish it as an Artifact if the user is working in an environment that supports that.

## Modes

- **quick**: Find and qualify up to five strong prospects.
- **standard**: Find up to ten prospects across several public source types.
- **deep**: Research up to twenty prospects and map repeated pain patterns.
- **design-partners**: Prioritize users willing to test and give feedback over immediate buyers.
- **b2b**: Prioritize companies, public business triggers, and relevant decision roles.
- **community**: Prioritize public discussion and explicit request signals.

Use `standard` by default. State the mode explicitly in the request, e.g. "find first customers for https://example.com in deep mode".

## Gotchas

- **Fabrication is the failure mode that kills this skill.** A plausible prospect with a dead or mismatched link is worse than no prospect — step 4's verification is not optional, even in quick mode.
- **Two-sided products** (e.g., marketplaces) return a mixed bag of both sides from research. Filter to the primary ICP before scoring; note the adjacent side under patterns instead of blending both into one shortlist.
- **Old signals** can still qualify — an explicit request from 18 months ago is fine to include — but cut its timing score and print the date next to it so the reader can judge freshness themselves.
- **Ten strong beats thirty generic.** If verification leaves you with four great prospects instead of ten mediocre ones, ship four and say why.
- **Respect impatience.** If the user asks you to hurry or wrap up mid-run, switch to quick mode immediately: stop waiting on unfinished search buckets, verify and score what you already have, and ship the report with a note about which buckets were cut short.

## Quality bar

- Link every prospect to at least one meaningful public signal.
- Prefer ten strong matches over a long generic lead list.
- Make uncertainty and stale evidence visible.
- Personalize from the source, not from invented assumptions.
- Make the manual next step operationally clear: who should receive it, what to ask, and what answer the outreach needs.
- Keep outreach manual and respectful.
- Treat the shortlist as a research hypothesis, not a customer database.

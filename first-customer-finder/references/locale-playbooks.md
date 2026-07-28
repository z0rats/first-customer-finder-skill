# Locale Playbooks

The default query buckets and source mix in `research-framework.md` are written for English-language, US/EU-centric products. Apply a locale playbook whenever the product's buyer, language, or stated geography points elsewhere, so the search plan does not default to English-only sources.

## Detecting the locale

Infer from, in order of priority:

1. an explicit geography or language stated by the user
2. the product's own language (landing page copy, README, UI strings)
3. the TLD, company registration, or pricing currency
4. the language prospects are likely to complain in, which may differ from the product's language

Label the inference. If signals conflict (e.g., English product copy but a CIS-only pricing page), search both the product's language and the buyer's likely language.

## CIS / Russian-speaking market

Use this playbook when the buyer or product geography is Russia, Ukraine, Belarus, Kazakhstan, or another Russian- or Ukrainian-speaking market.

### Query buckets (Russian-language equivalents)

Search these alongside, not instead of, the English buckets if the audience is bilingual:

1. **Explicit demand:** "ищу сервис", "посоветуйте инструмент", "кто чем пользуется для", "аналог [competitor]", "есть что-то для".
2. **Pain:** "задолбался вручную", "занимает часы", "бесит когда", "неудобно", "постоянно ломается", "костыль".
3. **Workaround:** таблицы (Google Sheets/Excel), копипаста между сервисами, боты в Telegram "на коленке", фрилансер/VA для рутины.
4. **Switching:** "отказался от [конкурент]", "подорожал", "перестал устраивать", жалобы на цены/поддержку/блокировку.
5. **Timing:** вакансии на hh.ru под смежную роль, анонсы запуска/расширения в Telegram-каналах компании, посты о найме или пивоте.

### Source mix

- **Habr (habr.com)** — technical/product audience; strong for developer tools, SaaS, infra pain posts and comments.
- **VC.ru** — startup/business audience; launch posts, business-model discussions, comment threads with pain signals.
- **Pikabu** — broad consumer audience; useful for consumer-facing products, less reliable for B2B.
- **hh.ru** — vacancies as a timing signal (a company hiring for a role your product supports is a trigger); job descriptions also reveal current workflow and tooling.
- **TenChat** — closest RU-market analog to LinkedIn-style professional posts; use for professional/business signals.
- **VK public pages and communities** — company pages, industry groups; treat like public company pages, not private groups.
- **Telegram public channels and chats** — browse via the public web preview (`t.me/s/<channel>`) or a public directory (e.g., TGStat, Telemetr) rather than trying to search inside the app; only cite channels/messages that are openly public, not invite-only groups.
- **DOU.ua** — Ukraine-specific tech community; use instead of or alongside Habr when the buyer is Ukraine-based.

### Platform caveats

- **LinkedIn is formally blocked in Russia** (Roskomnadzor, since 2016), but VPN use is widespread enough among the professional/tech audience that it remains a usable source — do not exclude it by default. Treat it as secondary to TenChat/VK/Habr for Russia-based prospects rather than off-limits, and expect lower coverage for less tech-savvy or non-VPN audiences.
- **Telegram and VK content is often not indexed by general web search.** Do not assume a WebSearch query surfaces relevant channels or posts; fetch known public channels/communities directly, or use a public directory site to discover them first.
- **Private/closed Telegram groups and VK communities remain off-limits**, same as any other private group under the base research-safety rules — do not join, request access, or use a member list to enrich contacts.

### Reporting and outreach adjustments

- Set `search_scope` in the report JSON to reflect the actual scope searched, e.g. `"Public Russian-language sources (Habr, VC.ru, hh.ru, Telegram), last 12 months"` instead of the English-language default.
- Draft the opener in the same language as the cited public source, not automatically in English.

## Adding another locale

Follow the same shape: translated query buckets, a ranked source mix specific to that market, platform caveats (blocked/unreliable platforms, search-indexing gaps), and any reporting-language adjustment. Keep each playbook self-contained so the workflow can read only the one that applies.

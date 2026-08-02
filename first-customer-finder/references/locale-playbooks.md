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

Use this playbook when the buyer or product geography is Russia, Ukraine, Belarus, Kazakhstan, or another Russian-speaking market.

### Query buckets (Russian-language equivalents)

Search these alongside, not instead of, the English buckets if the audience is bilingual:

1. **Explicit demand:** "ищу сервис", "посоветуйте инструмент", "кто чем пользуется для", "аналог [competitor]", "есть что-то для".
2. **Pain:** "задолбался вручную", "занимает часы", "бесит когда", "неудобно", "постоянно ломается", "костыль".
3. **Workaround:** таблицы (Google Sheets/Excel), копипаста между сервисами, боты в Telegram "на коленке", фрилансер/VA для рутины.
4. **Switching:** "отказался от [конкурент]", "подорожал", "перестал устраивать", жалобы на цены/поддержку/блокировку.
5. **Timing:** вакансии на hh.ru под смежную роль, анонсы запуска/расширения в Telegram-каналах компании, посты о найме или пивоте.

Russian is heavily inflected — a single fixed phrase per bucket misses most matches. Vary case and person rather than searching one form only: "ищу" / "ищем" / "искали" / "ищет кто-нибудь", "задолбался" / "задолбались" / "задолбало", "аналог Notion" / "аналоги Notion" / "альтернатива Notion". Treat each bucket as a cluster of word forms, not a single string.

### Source mix

When the environment allows choosing a search engine, also try Yandex alongside the default: it indexes Habr comments, VK public pages, and Russian-language forums more completely than Google in some cases.

- **Habr (habr.com)** — technical/product audience; strong for developer tools, SaaS, infra pain posts and comments.
- **VC.ru** — startup/business audience; launch posts, business-model discussions, comment threads with pain signals.
- **Pikabu** — broad consumer audience; useful for consumer-facing products, less reliable for B2B.
- **Отзовик (otzovik.com) / iRecommend (irecommend.ru)** — consumer review sites; useful for B2C products and services, weak coverage for B2B tooling.
- **Klerk.ru** — accountants and small-business owners; forum and articles surface pain around bookkeeping, reporting, and finance workflows well.
- **Cossa.ru** — marketing/advertising industry publication and forum; comment threads are a good source for marketing-tech and adtech pain signals.
- **dev.by** — Belarusian tech community, the closest analog to Habr for Belarus; use alongside Habr when the geography is Belarus specifically.
- **hh.ru** — vacancies as a timing signal (a company hiring for a role your product supports is a trigger); job descriptions also reveal current workflow and tooling.
- **TenChat** — closest RU-market analog to LinkedIn-style professional posts; use for professional/business signals.
- **VK public pages and communities** — company pages, industry groups; treat like public company pages, not private groups.
- **Telegram public channels and chats** — two-step process, since this content is not indexed by general web search:
  1. **Discover** using a public directory's own keyword search (e.g., TGStat, Telemetr search) with the same word-form clusters as the query buckets — not just their channel-ranking or directory pages.
  2. **Verify** by opening the actual post through the public web preview (`t.me/s/<channel>/<id>`) before citing it — directory search results are often summaries or stale copies, not the live message. Only cite channels/messages that are openly public, not invite-only groups.
- **Public company registries** — a strong, underused timing source. For Russia: `rusprofile.ru` or `list-org.com` (registration date, OKVED activity codes, leadership/ownership changes, active/liquidation status). For Kazakhstan: `stat.gov.kz` business registry data or `egov.kz` business services. For Belarus: `egr.gov.by` (Unified State Register of Legal Entities and Individual Entrepreneurs). A recent registration, a leadership change, or a newly added activity code relevant to the product is a legitimate timing signal — cite the registry page itself, not a summary.

### Payment rails and product fit

Stripe and PayPal do not operate inside Russia, which affects `product_fit` and reachability for any product whose buying motion assumes them (checkout, subscription billing, payouts). When qualifying a Russia-based prospect for a product billed through Stripe/PayPal, note this as a disqualifier or a material caveat rather than silently scoring fit as if global checkout worked normally. Local alternatives prospects may already use — useful for recognizing existing workarounds under the "workaround" query bucket — include ЮKassa, CloudPayments, Т-Банк (Tinkoff) Acquiring, and Robokassa. This constraint is Russia-specific; Ukraine, Kazakhstan, and Belarus each have their own separate payment-rail landscape and shouldn't be assumed to share it.

### Compliance caution

When the product/company is based in a jurisdiction with export controls or sanctions programs (e.g., US, EU, UK) and a prospect is Russia-based, sanctions or export-control restrictions may prohibit selling or providing services to that prospect, depending on the product category, the specific entity, and current regulations. This is not something to resolve automatically — flag it, don't decide it:

- Do not silently draft outreach to a Russia-based prospect for a Western-owned product without surfacing this.
- Set the prospect's `caution` field to note the jurisdiction mismatch and that sanctions/export-control screening should happen before any outreach.
- This is a flag for the user to verify, not legal advice — never assert that a prospect is or isn't compliant to contact.

### Platform caveats

- **LinkedIn is formally blocked in Russia** (Roskomnadzor, since 2016), but VPN use is widespread enough among the professional/tech audience that it remains a usable source — do not exclude it by default. Treat it as secondary to TenChat/VK/Habr for Russia-based prospects rather than off-limits, and expect lower coverage for less tech-savvy or non-VPN audiences.
- **Telegram and VK content is often not indexed by general web search.** Do not assume a WebSearch query surfaces relevant channels or posts; fetch known public channels/communities directly, or use a public directory site to discover them first.
- **Private/closed Telegram groups and VK communities remain off-limits**, same as any other private group under the base research-safety rules — do not join, request access, or use a member list to enrich contacts.

### Regional business calendar

CIS business calendars have long non-working stretches that a standard Mon–Fri cadence doesn't account for — most notably early January (New Year and Orthodox Christmas, commonly a one-to-two-week stretch) and early-to-mid May (Victory Day, with a second cluster around May 9). Exact non-working days shift every year — in Russia they're set by government decree and published for that specific year — so do not hardcode specific dates here or assume last year's calendar still applies.

Instead, check the current date against the month, not a fixed date range: if the seven-day outreach window would fall in the first half of January or the first half of May, flag this explicitly in the plan rather than silently assuming standard business days. Either look up that year's official non-working-day calendar for the relevant country before proposing exact days, or state in the plan that the window may overlap a national holiday period and the cadence should be confirmed once the actual dates are known.

Country calendars are not interchangeable within the CIS umbrella — Russia, Belarus, Kazakhstan, and Ukraine each publish their own non-working-day calendar and don't share exact dates. Match the calendar check to the prospect's country, not the product's or the user's.

### Reporting and outreach adjustments

- Set `search_scope` in the report JSON to reflect the actual scope searched, e.g. `"Public Russian-language sources (Habr, VC.ru, hh.ru, Telegram), last 12 months"` instead of the English-language default.
- Draft the opener in the same language as the cited public source, not automatically in English.
- Base the seven-day outreach plan's cadence on the prospect's local business hours, not the product's home timezone. Russia, Belarus, and most of Kazakhstan sit roughly UTC+3 to UTC+6 (Moscow Time and east of it); Ukraine is UTC+2/+3. Note the relevant timezone in the plan when it would otherwise default to a Western business-hours assumption. Also check the regional business calendar above before proposing the plan's exact days.

## Adding another locale

Follow the same shape: translated query buckets, a ranked source mix specific to that market, platform caveats (blocked/unreliable platforms, search-indexing gaps), and any reporting-language adjustment. Keep each playbook self-contained so the workflow can read only the one that applies.

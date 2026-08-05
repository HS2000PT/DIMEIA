# Estudo de mercado para a reconstrucao do painel (v4)

> **Origem.** Gerado por quatro agentes de investigacao na sessao 49 (2026-08-04) e extraido
> para o repositorio na sessao 51, porque so existia numa pasta temporaria de uma maquina.
>
> ⚠️ **Os quatro cepticos que deviam contestar isto morreram no limite mensal de gasto.**
> Ou seja: **estas conclusoes nao passaram por contraditorio**. Tratar como material de
> partida, nao como veredicto. Onde ha numeros deste projecto, sao medidos e verificaveis;
> onde ha afirmacoes sobre produtos de terceiros, foram observadas pelos agentes em 2026-08
> e devem ser reconfirmadas antes de entrarem na tese.

> **Restricoes que nao se negoceiam**, e que qualquer ideia daqui tem de respeitar:
> **H2** zero numeros previstos · **H4** nenhum score que a medicao nao sustente ·
> so APIs gratuitas · um dyno de 512 MB · a app arranca sem chaves de API.

---

## Produtos reais do mercado

*O que doze produtos fazem, e o que um leigo extrai em dez segundos.*

### Sintese

FIVE SESSIONS, WALKED MINUTE BY MINUTE. I read the live code first (`app/dashboard.py`, `app/verdict.py`, `app/ui_tokens.py`, `docs/design/v3_backlog.md`) so every "this is in the way" below points at a real line, not an imagined one.

WHAT THE PAGE IS TODAY (so the frustrations are checkable): a header strip (brand · MARKET OPEN/CLOSED · clock · "N flagged · what is this?" · "N alerts sent"), then a 4×3 grid of card links sorted by rarity. A card = logo, company name, ticker, big % move, an UNUSUAL pill if flagged, one plain-English verdict sentence, and for flagged cards a 30-day sparkline plus chips ("z +2.14 vs 20-day norm", "3.3x usual volume", "alert sent"). Click a card → `?t=NVDA` → a detail page ordered: big % + z → range radio (default 1M) → chart with three marker layers → WHY IT MOVED decomposition bar → HAS THIS HAPPENED BEFORE (precedents) → captured news table (filter/sort/paginate) → alerts-sent feed. `?view=method` holds the evaluation. Measured: cold grid 5.5–6.2 s, first detail of a session ~3.0 s, warm card click ~0.75 s.

═══ JOURNEY 1 — LONG-TERM HOLDER · TUESDAY 08:02 · PHONE · OWNS AAPL, MSFT, JNJ, XOM ═══

08:02:00 A friend's message says "markets are down". I am not a trader; I own four things and I am about to spend the whole commute deciding whether to be worried. I tap the bookmark.
08:02:01–08:02:07 Blank. Streamlit boots, the grid is cold. On 4G this is worse than the measured 5.5 s. Seven seconds of nothing is where the anxiety compounds — I am staring at white while imagining the number.
08:02:08 The page paints. Header says MARKET CLOSED. **This is the first real wound: it is 08:02 ET, the US market opens in 88 minutes, and every number on this page is yesterday's close — but nothing says so.** My friend is talking about futures/Asia/Europe *right now*. I will read yesterday's −1.4% as today's and act on it. The page needs to say, in words, "showing yesterday's close · US opens in 1h 28m".
08:02:09–08:02:40 Twelve one-column cards on a 390 px screen ≈ five screenfuls of thumb-scroll. **My four are scattered**, because the sort is by rarity and the product has no idea which ones are mine. I scroll past NVDA, TSLA, META, AMD — companies I do not own — hunting for JNJ. This is the single largest cost in this journey and it is not a rendering problem, it is a personalisation problem.
08:02:41 I find AAPL: "Quiet — 203 of the last 249 trading days moved as much or more." **This sentence is the best thing in the product.** It is the whole thesis in one line, it needs no glossary, and it is exactly the permission-to-do-nothing this persona came for. Whatever gets rebuilt, this survives.
08:03:10 I have now read four verdict sentences in four different places and assembled the answer in my own head. The product made me do the aggregation. **What I needed in the first three seconds was one line**: "The market itself fell 1.1% yesterday. Ten of your twelve are ordinary. Nine of the twelve moves were the market, not the company. Nothing here needs you." Every ingredient of that sentence is already computed — SPY is fetched for the Vasicek decomposition, `flagged` is per row, the driver is per ticker. Nobody has ever summed them.
08:03:20 XOM is flagged, UNUSUAL. My pulse goes up. The card tells me it stood out and gives me "z +2.31 vs 20-day norm" — and to learn whether it was oil-sector-wide or Exxon-specific I have to tap in, wait ~3 s for the first detail of the session, and scroll past a chart to the WHY IT MOVED bar. **The one fact that would calm me is two interactions and four seconds away.** The driver sentence deliberately stays silent when the driver is the company itself, which is right; but when the driver is the market or the sector it should be *on the card*, because that is precisely the case where a holder can stop reading.
08:03:45 I close the tab. Relieved-not-anxious would have taken 8 seconds, not 105.

WHAT MADE IT WORSE: no "as of", no market-level line, no way to say which four are mine, 5–7 s to first paint, a 60 s auto-refresh that can reorder cards under my thumb mid-scroll (the sort key is rarity, which changes intraday), and — on the detail page — three tables built from fixed-pixel columns (58+78+82+52 px) that leave roughly 60 px for the headline on a 360 px phone, so the headline column is functionally destroyed.

═══ JOURNEY 2 — ACTIVE INVESTOR · 14:30 · DESKTOP · MARKET OPEN · TELEGRAM ALERT ON NVDA ═══

14:30:14 The Telegram alert lands. It is good: the move, the sector check, the precedents, the honest framing. **It contains no link.** (Verified: no URL is emitted anywhere in `scripts/run_alerts.py` or the explainer.) So: alt-tab, find the tab or the bookmark, load the grid (5.5 s cold), scan twelve cards for NVDA, click, wait ~3 s for the first detail. Somewhere between 20 and 30 seconds and four actions to reach a page the alert could have opened directly. At 14:30 with the thing moving, that is the difference between context arriving *with* the alert and context arriving after I have already looked somewhere else.
14:30:45 The detail page loads. Top line: −4.62%, z −2.88. Good. Then the range radio, defaulted to **1M**. So the chart is a month of daily bars and *today is a single candle on the right edge*. I cannot see whether this was a 09:35 gap-down or a slow bleed since noon — and those are completely different stories. I click 1D, pay another server round-trip (~0.65 s and a full-page repaint). The recorded reason for the 1M default is honest and correct (event markers do not exist inside one day, so 1D opened empty), but the fix chosen was to hide today rather than to give today its own treatment.
14:31:10 **Where is the headline?** This is the question. The news panel below shows captured headlines *with measured +1D/+5D outcomes* — and impact needs five trading days to exist, so by construction **today's news can never appear there**. The panel that looks like the news panel is structurally incapable of telling me what happened this morning. I end up in another tab, on a news site, which is exactly the failure the product exists to prevent.
14:31:40 The decomposition answers "market or company" well. But it is a bar chart under a chart under a header; I want it as one sentence beside the price, at the top: "Company-specific: the market is flat and semis are down 0.9%."
14:32:00 AMD is in the watchlist. When NVDA moves 4.6% I want AMD's number **on this page**, right now. Instead: back to the grid, find AMD, click in, lose my place. There is no peer strip, no compare, no keyboard way to step from NVDA to AMD.

INTOLERABLE HERE, IN ORDER: (1) full-page repaint on every interaction — changing a range, turning a page in a table, or the 60 s fragment refresh rebuilds and can throw away my scroll position and filter state; this *is* the "laggy / static / old-school" verdict, and it is architectural, not cosmetic; (2) a price with no "as of HH:MM:SS · 15-min delayed" stamp — an unlabelled number during market hours is untrustworthy by default; (3) pagination where I want to scan; (4) nothing clickable through to a source article anywhere in the product.

═══ JOURNEY 3 — SAME INVESTOR · THIRD VISIT · ~16:45 ═══

16:45 I have been here at 09:20 and 14:31. The page is **byte-identical in structure** to both. It is completely stateless about me by design (URL-only state), which is excellent for sharing and hostile to repeat visits.
What I want now is a **diff, not a state**: "Since 14:31 — NVDA −4.62% → −3.10%; META newly flagged; nothing else changed." The product knows everything needed and remembers nothing.
What is now noise that was valuable at 09:00: the "what is this?" affordance; the promise/disclaimer footer; the two explanatory lines under the precedent table ("Cases can come from other companies on purpose…", "Outcomes are what followed then, measured after the fact") — correct, load-bearing, and on the third read they are three lines pushing the data down the screen; the alerts-sent feed (I received those on Telegram, I know them); and the verdict sentence for tickers whose story I read at lunch. None of this should be deleted — it should **fade**: first visit shows everything, later visits collapse the explainers behind a persistent "explain" toggle that remembers my choice.
16:45 also changes the question. After the close, "what is happening" becomes "did it hold, and what do I need to remember". A closing-state line — "The session is over. Two of the twelve ended flagged; both were sector-wide." — would be a genuinely different screen for a genuinely different moment, and the data is already there.

═══ JOURNEY 4 — COMPLETE BEGINNER · FIRST VISIT EVER · ARRIVED FROM A SHARED LINK ═══

00:00 A friend sent a link. It may well be a deep link (`?t=NVDA`), so I may land on a *detail page* with no idea what the site is. There is no "what is this" on the detail page at all — the explainer lives in the header of the grid.
00:03 I see a dark, monospaced, numeric screen. My honest first read is "this is for people who know things I do not", and my thumb is already near the back button. Dark+numeric is right for persona 2 and is the wrong first handshake for me.
00:05 I look for the answer to three questions in this order: *what is this, who is it for, is it going to sell me something?* The header gives me a brand mark, MARKET OPEN, a clock, "3 flagged · what is this?" and "241 alerts sent". "Flagged" is jargon I have not been taught yet; "241 alerts sent" is a statistic about the system, not about me.
00:07 **"what is this?" is a `title=` attribute** — a hover tooltip. On my phone it does not exist. The text inside it (FLAG_EXPLAINER) is genuinely excellent, plain, and exactly what I need — and it is delivered through the one mechanism a touch user can never trigger. It also navigates to the method page, which is an evaluation page: I asked "what is this?" and got a research report.
00:12 On a card I read "z +2.14 vs 20-day norm". The gloss is real and it still contains two things I do not know ("z", "20-day norm"). I feel stupid. Two centimetres away, the verdict sentence says "Only 4 of the last 249 trading days moved this much or more" — **which is the same fact in language I can use.** The beginner-safe version already exists and is already computed; the expert version is what is shown by default on the flagged cards, which are the exact cards a newcomer looks at first.
00:20 What stops me bouncing: one sentence under the brand — "12 US companies, watched every day. We tell you whether today's move is unusual *for that company*, whether it was the market or the company, and what happened after similar news in the past. We never predict prices. Free, no signup." The last two clauses are the trust purchase; the never-predicting stance is a *feature to lead with*, not a caveat to bury in the footer.
00:30 And one worked example — a single real flagged day (AAPL −7.64% is in the corpus) shown as "here is what this looks like when something happens" — teaches more than any tour.

═══ JOURNEY 5 — THE STUDENT, 3 MINUTES, IN FRONT OF A JURY ═══

0:00 Grid on the projector. Needed: the *whole* watchlist visible with no scrolling, one flagged and one quiet card in the same eyeful, because the quiet card is the argument. **Two concrete risks here.** (a) The 3-column breakpoint fires at ≤1279 px and the most common projector is 1280×720 — one pixel of margin, and at 720 px tall a 4×3 grid plus header plus browser chrome will scroll. (b) Most of the supporting type is 11.5–12.5 px in FG_DIM/FG_MUTE grey on near-black; that is unreadable from the back of a room. A presentation mode that bumps the type scale and pauses the 60 s refresh is cheap insurance.
0:25 Click a card. Warm it is 0.75 s; **the first detail of a session is ~3.0 s**, and in a 180-second demo a three-second dead screen at second 25 is a wound. Pre-warm before walking in, or prefetch on card hover.
0:40 "This move was the market, not the company" — the decomposition. This is RQ1/RQ2 made visible and it lands.
1:10 Precedents with measured outcomes plus the topic≠direction framing. This is the intellectual-honesty moment the jury will remember. It must be one scroll away at most, and it must be legible on a projector.
2:00 `?view=method`, including where the method lost. Juries reward that.
2:40 Back to the grid: live, 60 s cycle, 512 MB dyno, no paid APIs.
**The catastrophic risk nobody has covered: if the market is calm on defence day, there is no flagged card to click and the demo has no story.** The product is honest enough that a quiet day genuinely produces twelve quiet cards. A frozen replay (`?d=2026-05-14`) driven by the existing `detect_all` replay, plus a cached offline snapshot for a room with bad wifi, converts the highest-stakes 3 minutes of this project from a gamble into a rehearsal.

═══ THE TEN REQUIREMENTS, RANKED (each traced to a moment above) ═══
1. Sub-second first paint with a skeleton, and interactions that do not repaint the page — J2 14:30:45 / J1 08:02:01. This is the actual rejection cause across seven versions.
2. Answer-first line above the grid: market move + how many are ordinary + how many moves were the market — J1 08:03:10, J4 00:20, J5 0:00.
3. "Mine": mark 4 of the 12, pinned to the top, browser-local, no quantities — J1 08:02:09.
4. Deep link from the Telegram alert straight to `?t=NVDA` — J2 14:30:14.
5. Detail opens on *today*, with an intraday shape and an "as of · delayed" stamp — J2 14:30:45.
6. Today's headline visible above the fold, explicitly marked "no measured outcome yet" — J2 14:31:10.
7. Plain-language first, statistics behind a sticky toggle — J4 00:12, J3 16:45.
8. "What changed since you last looked" — J3 16:45.
9. Peer strip + keyboard navigation (←/→ between companies, `/` to search, Esc back) — J2 14:32:00.
10. Demo mode: frozen date, presentation type scale, paused refresh, offline snapshot — J5 throughout.

Full detail, precedents, costs and three explicit rejections are in the findings.

### As tres recomendacoes principais

1. Perceived speed is the actual product defect, not the styling: first paint must be a skeleton grid inside ~1 s and interactions (range switch, table paging, auto-refresh) must never rebuild the page. Every 'laggy / static / old-school' complaint in seven rejections traces to Streamlit's server round-trip per interaction — J2 14:30:45 and J1 08:02:01. No CSS fixes this; a client-side interaction layer does.

2. Answer the question before showing the data: one line above the grid ('The market itself fell 1.1%. Ten of twelve are ordinary. Nine of the twelve moves were the market, not the company.') plus the ability to mark which 4 of the 12 are mine and pin them. J1's entire 105-second session collapses to about 8 seconds, and every ingredient is already computed (SPY is fetched for the decomposition; flagged and driver are per ticker). Nobody has ever summed them.

3. Close the alert-to-answer loop: put a deep link in the Telegram alert (`?t=NVDA`), open the detail on today with an intraday shape and an 'as of · delayed' stamp, and show today's headline above the fold marked 'no measured outcome yet — that takes five trading days'. J2 loses 20-30 seconds and four actions to a missing URL, then lands on a month chart where today is one candle, next to a news panel that structurally cannot contain today's news.

### Achados (17)

#### First paint in under a second, with a skeleton — and interactions that never repaint the page

- **O que e:** Two separable things. (a) Perceived load: render the 12 card frames with company name, logo and a shimmer placeholder immediately from a cached snapshot, then fill each card as its data resolves. Never show an empty viewport. (b) Interaction cost: range switching, table paging/filtering, sorting and the 60 s refresh must happen client-side against data already in the browser, not via a server round-trip that rebuilds header, chart, decomposition, two tables and a feed.
- **Fonte:** Journey 2, 14:30:45 (range switch) and Journey 1, 08:02:01 (7 s of blank on 4G). Measured in docs/design/v3_backlog.md: cold grid 5.45-6.20 s, first detail ~3.0 s. Precedents: Linear (linear.app) optimistic updates; Vercel/Next.js App Router streaming with loading skeletons; GitHub's deferred-content pattern; Robinhood's chart range tabs, which switch instantly because the series is already client-side.
- **Porque funciona:** Perceived latency is dominated by time-to-first-something and by whether a click causes visible reconstruction. A skeleton at 200 ms feels faster than a real render at 2 s. And a range tab that swaps a client-side series feels like an app; one that rebuilds the DOM feels like a 2009 web page — which is exactly the word the student used, 'old-school and static'.
- **Aplica-se aqui:** 12 tickers is a tiny payload. A day's snapshot for all 12 (move, z, exceedance count, driver, vol ratio, 30-day sparkline series) is a few KB of JSON; a year of daily bars for 12 tickers is a few hundred KB. The whole grid can be client-resident. This is the finding that argues hardest for the FastAPI-plus-front-end option in the v4 brief: it is not achievable by optimising Streamlit, because the repaint is Streamlit's execution model.
- **Custo:** High if it means leaving Streamlit (the brief explicitly authorises this): roughly a JSON snapshot endpoint plus a single-page front end. Risk: a rewrite weeks before submission. Mitigation demanded by the brief itself — prototype the grid alone, measure first paint against 5.5 s, and only then decide. The 512 MB dyno favours this direction: serving static assets plus a cached JSON is cheaper than Streamlit's per-session Python process.
- **Veredicto:** adopt

#### One answer line above the grid, before any card

- **O que e:** A single sentence spanning the whole watchlist, above the fold: 'Market itself: S&P 500 -1.14%. 10 of 12 ordinary. 9 of 12 moves came from the market, not the company. 2 flagged.' Plus, when the market is shut, an explicit 'showing Monday's close · US opens in 1h 28m'.
- **Fonte:** Journey 1, 08:03:10 (the user assembles this in their head from four cards) and Journey 1, 08:02:08 (MARKET CLOSED with no 'as of what'). Precedents: Google Finance's index strip above the watchlist; Robinhood's single market-summary line on the home screen; worldmonitor.app's top-level state line.
- **Porque funciona:** The long-term holder arrives with a market-level question ('markets are down') and today receives twelve company-level answers. Answering at the altitude of the question is what turns a five-screen scroll into a three-second read — and 'nine of twelve moves were the market' is the permission-to-do-nothing message, stated once, at portfolio altitude, instead of twelve times.
- **Aplica-se aqui:** Every ingredient exists: SPY is already fetched for the Vasicek decomposition, flagged is per row, driver is per ticker. This is an aggregation of computed values, not a new data source, and it introduces no forward-looking number — it is a description of a day that already happened, so H2 is untouched.
- **Custo:** Low. One aggregation function plus one line of layout, and a market-state label that distinguishes 'closed, showing yesterday' from 'closed, showing today'. Risk: the decomposition currently only runs for flagged tickers on the grid, so 'N of 12 moves came from the market' needs the driver for all 12 — check the cost before promising it, since the V6' precedent-count lesson (7.5 s for one chip) is exactly this trap.
- **Veredicto:** adopt

#### 'Mine' — mark which of the 12 you follow, pinned to the top, stored in the browser

- **O que e:** A small toggle on each card; marked companies pin to the top of the grid in their own band ('Yours'), the rest collapse below under 'The other 8'. Stored in localStorage. No quantities, no cost basis, no P&L, no account, nothing leaves the device.
- **Fonte:** Journey 1, 08:02:09 — five screenfuls of thumb-scroll hunting for JNJ among companies the user does not own. Precedents: Yahoo Finance portfolio tabs; Google Finance's 'Your watchlist'; TradingView watchlist pinning.
- **Porque funciona:** The holder's whole session is 'are my four OK'. Sorting by rarity is right for a stranger and wrong for an owner; owners want position, not ranking. Pinning removes the single largest cost in journey 1 without removing the rarity ordering for everyone else.
- **Aplica-se aqui:** IMPORTANT — this must not reopen a closed decision. Session 42 cut portfolio/holdings for GDPR and MiFID II advice-boundary reasons. A browser-local subset-of-12 filter is not a portfolio: no holdings, no amounts, no valuation, no personal data leaves the device, and it produces no advice. Frame it explicitly as 'which companies to show first', and say so in the code comment so a future session does not mistake it for the cut feature.
- **Custo:** Low. localStorage plus a sort key. If the front end stays Streamlit this is genuinely awkward (session_state does not survive a new browser session), which is a further argument for a client-side layer.
- **Veredicto:** adapt

#### The Telegram alert must contain a deep link to the company page

- **O que e:** Append one line to every alert: 'See the full picture: https://<app>/?t=NVDA'. Ideally also '?from=alert' so the landing page can open with the alert's own moment in view.
- **Fonte:** Journey 2, 14:30:14. Verified in the codebase: no URL is emitted anywhere in scripts/run_alerts.py or investigator/explanation_engine/explainer.py. Precedent: every alerting product that works this way — PagerDuty, Datadog, GitHub notifications — the alert is a doorway, never a dead end.
- **Porque funciona:** The product's stated value for the active persona is 'context arriving WITH the alert'. Today the alert arrives and the context is 20-30 seconds and four manual actions away, across an app boundary, on a phone. One string closes the loop, and it turns the Telegram channel into a distribution funnel for the dashboard rather than a substitute for it.
- **Aplica-se aqui:** Deep links already work (`?t=NVDA` is a signed-off criterion, V8) and the URL is stable. The only care needed: the alert text is mirrored into the dashboard's alert feed, so make sure adding a URL does not break the frozen alert-text fidelity tests or the dedup key, which hashes plain_text.
- **Custo:** Very low — one f-string, plus checking the fidelity tests and the news_key/dedup path. Highest value-per-line in this entire list.
- **Veredicto:** adopt

#### The detail page must open on today, with an intraday shape and an 'as of' stamp

- **O que e:** When the market is open, or when the company moved today, default the range to 1D with 5-minute bars, show today's session shape, and stamp the price 'as of 14:31:07 ET · 15-min delayed' (or whatever is true of the source). Keep 1M as the default when the market is closed and today is uneventful.
- **Fonte:** Journey 2, 14:30:45. Current code: RANGE_DEFAULT = '1M', so today is one candle at the right edge. The recorded reason (1D opened with no markers and an empty event table) is honest but solved the problem by hiding today. Precedents: Google Finance and Robinhood both default to 1D during the session; Bloomberg and Koyfin always stamp the quote time.
- **Porque funciona:** A gap-down at 09:35 and a slow bleed from noon are different events with different meanings, and both are invisible on a monthly candle. And an unlabelled price during market hours is a trust problem: sophisticated users assume the worst about undated numbers, and unsophisticated ones assume real-time and are misled.
- **Aplica-se aqui:** The 1D range already exists in RANGES ('1d','5m',True) and _intraday is already cached at 90 s. The real fix for the emptiness that caused the 1M default is to give the 1D view its own content — today's captured headlines and the session shape — rather than the historical marker layers, which genuinely do not exist inside one day.
- **Custo:** Low-medium. Conditional default plus a timestamp, plus deciding what the 1D view shows instead of markers. Watch the earlier bug where markers were hidden behind `if not intra` — the fix is per-range content, not a flag.
- **Veredicto:** adopt

#### Today's headline above the fold, explicitly labelled 'no measured outcome yet'

- **O que e:** On the detail page, directly under the price: the 1-3 most recent captured headlines for this ticker with their timestamps, marked 'captured today — no measured outcome yet; that takes five trading days'. On a flagged card in the grid, the single latest headline, truncated.
- **Fonte:** Journey 2, 14:31:10 and Journey 1, 08:03:20. Structural finding: the existing news panel shows only headlines with measured +1D/+5D impact, so today's news can never appear in it. Precedent: Yahoo Finance and Perplexity Finance both lead a ticker page with the newest headline; the difference here is the honesty label.
- **Porque funciona:** 'Why is my stock red?' is the most common question a price page receives, and this product captures ~38,000 headlines yet shows none of the fresh ones. The 'no outcome yet' label is not an apology — it is the thesis position made concrete, and it teaches the user why the measured table below is different and more valuable.
- **Aplica-se aqui:** The capture path already writes every relevant headline to live_pending.jsonl at capture time. The maturation delay is a property of the impact measurement, not of the headline. Separating 'what was said' (immediate) from 'what followed' (measured, 5 days later) is more honest than today's silence, and it makes the five-day wait legible instead of invisible.
- **Custo:** Medium. Reading pending (unmatured) captures into the app, plus a clear visual distinction from the measured table so the two can never be confused. Governance check needed: only headlines are persisted, never Finnhub summaries (docs/design governance §5.4).
- **Veredicto:** adopt

#### Plain language first, statistics behind a sticky 'show the numbers' toggle

- **O que e:** By default show the empirical sentence ('Only 4 of the last 249 trading days moved this much or more') and hide the z chip. One control in the header, 'show the statistics', off for a first-time visitor, remembered thereafter. Expert mode reveals z, the three decomposition components, the volume ratio and the similarity scores.
- **Fonte:** Journey 4, 00:12 (a beginner reads 'z +2.14 vs 20-day norm' and feels stupid, two centimetres from the same fact in usable English) and Journey 3, 16:45 (explanatory lines become furniture on the third read). Precedent: Stripe's dashboard advanced-fields disclosure; Apple Health's summary-then-detail hierarchy.
- **Porque funciona:** The two personas want opposite densities and the product currently serves the expert default to everyone, including on the flagged cards a newcomer looks at first. Progressive disclosure serves both without a second product. Critically, the beginner-safe version is already the more honest one — the exceedance count assumes no distribution, whereas z quietly leans on a normality intuition the tails do not support.
- **Aplica-se aqui:** Both strings are already produced by app/verdict.py (rarity_sentence and gloss_z). This is a visibility rule, not new computation, and it does not weaken traceability: the z remains one click away and remains in the method page, so the criterion 'no z without its gloss' is still satisfiable by test.
- **Custo:** Low. One preference plus conditional rendering. Keep the V4 test (z never appears naked) applying to expert mode.
- **Veredicto:** adopt

#### 'What changed since you last looked'

- **O que e:** On arrival, if a previous snapshot exists in localStorage from the same trading day: one line — 'Since 14:31 — NVDA -4.62% to -3.10%; META newly flagged; nothing else changed' — plus a subtle dot on the cards that changed. Dismissible; never blocks.
- **Fonte:** Journey 3, 16:45 — the third visit is structurally identical to the first, and the product remembers nothing. Precedents: GitHub's 'unread' notification dot; Linear's 'new since last visit' divider; Slack's unread line.
- **Porque funciona:** Repeat visits are diff-shaped, not state-shaped. Showing only the delta both reduces the reading load and, on a calm afternoon, makes 'nothing changed' an explicit, reassuring answer rather than an inference from twelve unchanged cards — which is once again the permission-to-do-nothing product.
- **Aplica-se aqui:** Perfect fit for 12 tickers: a snapshot is a dozen small numbers. Stays browser-local, so no accounts and no personal data. Also gives the auto-refresh something useful to do besides repainting.
- **Custo:** Low-medium client-side; awkward inside Streamlit for the same reason as 'Mine'. Care: define 'changed' by a meaningful threshold, or every 0.01% tick marks everything as changed and the feature becomes noise on its first day.
- **Veredicto:** adopt

#### Peer strip and keyboard navigation on the detail page

- **O que e:** A thin always-visible strip of the other 11 companies (ticker + today's move, colour-coded) at the top or bottom of the detail page; clicking one switches company without returning to the grid. Plus keyboard: left/right to step between companies, '/' to focus a search box, Esc back to the grid, '?' for a shortcut list.
- **Fonte:** Journey 2, 14:32:00 ('NVDA moved 4.6%, what did AMD do?' costs a round trip through the grid and loses the scroll position). Precedents: TradingView's watchlist rail beside the chart; Koyfin's persistent ticker sidebar; Gmail/Superhuman keyboard-first navigation.
- **Porque funciona:** Sector questions are comparison questions, and comparison requires adjacency. With only 12 names the entire universe fits in a 40-pixel strip, so the user never has to hold a number in memory across a page transition. Keyboard stepping also makes the jury demo fluid — no hunting for a card with a mouse on a projector.
- **Aplica-se aqui:** 12 is the ideal size for this: a peer strip of 60 would be a scrollbar, a strip of 11 is a glance. The snapshot data for all 12 is already loaded to render the grid, so the strip is free once the data is client-side. Note the real limit — only tech peers currently share a sector ETF, so peer context is genuinely richer for NVDA/AMD than for XOM or JNJ; say so rather than implying a sector view that the two non-tech names do not have.
- **Custo:** Low once data is client-resident; medium in Streamlit (each switch is a full rerun, which reintroduces the very lag being fixed).
- **Veredicto:** adopt

#### Demo mode: frozen date, presentation type scale, paused refresh, offline snapshot

- **O que e:** (a) `?d=2026-05-14` replays a stored day through the existing detect_all replay so the demo never depends on the market being interesting; (b) a presentation toggle that raises the base type scale roughly 25% and pauses the 60 s refresh; (c) a cached snapshot bundled with the app so a jury room with bad wifi still renders.
- **Fonte:** Journey 5, throughout — specifically the risk that on defence day all twelve cards are quiet and there is no flagged card to click, and the fact that supporting text is 11.5-12.5 px in FG_DIM/FG_MUTE grey on near-black, which does not project.
- **Porque funciona:** This is the highest-stakes three minutes of a project whose delivery date is fixed. Everything else on this list improves an average session; this one removes variance from the session that decides the grade. Frozen-date replay is also a genuine product feature — 'show me the day of the crash' is a real user desire, not just a demo crutch.
- **Aplica-se aqui:** detect_all already replays every day of a series with the same no-lookahead z-score, and backfill_kb.jsonl carries a year of measured news impact. A date parameter is mostly plumbing on top of existing capability. Also check the 3-column breakpoint: it fires at max-width 1279 px, and 1280x720 is the most common projector mode — one pixel of margin, and at 720 px tall a 4x3 grid plus header plus browser chrome may scroll.
- **Custo:** Low-medium. Biggest hidden cost is guaranteeing the frozen day renders every panel (the recorded lesson that 'an empty panel is a valid panel for the tests' applies directly — verify by screenshot at 1280x720 and 1366x768, not by test).
- **Veredicto:** adopt

#### Keep these six things — they are what is actually working

- **O que e:** 1. Verdict sentence before any technical number. 2. Empirical exceedance count instead of a probability. 3. Cards as real anchors with shareable `?t=` URLs (keyboard focusable, middle-clickable, back button works). 4. The three-layer chart: alert sent / detected-but-gated / news captured. 5. Three distinct empty-state messages instead of one. 6. The quiet card as a first-class citizen with its own proof.
- **Fonte:** Journey 1, 08:02:41 ('Quiet — 203 of the last 249 trading days moved as much or more' is the strongest sentence in the product) and Journey 5, 1:10. Precedent for the honesty of #4: almost no commercial dashboard shows what it suppressed; this one does.
- **Porque funciona:** These are the parts a redesign is most likely to throw away by accident, and every one of them is a differentiator rather than a decoration. The exceedance count in particular is the only rarity statement in the space that does not quietly assume normality, and the gated-alert layer is the only place a user can see the cost of the system's own caution.
- **Aplica-se aqui:** State this explicitly in whatever v4 acceptance document gets written, as inherited criteria. Seven redesigns have been rejected; the risk in an eighth is not that it fails to innovate but that it loses hard-won correctness in the churn.
- **Custo:** Zero — it is a constraint, not a feature. Cheaper to write down than to rediscover.
- **Veredicto:** adopt

#### WOULD LOVE, DOES NOT EXIST: clickable headlines that go to the source

- **O que e:** Every headline in the news table, the precedent table and the today block links out to the original article in a new tab, with the publisher name shown.
- **Fonte:** Journeys 2 and 4 — the user reads a headline they care about and has nowhere to go, so they leave for a news site. Precedent: every finance aggregator (Yahoo Finance, Google Finance, Finviz) links headlines out; it is table stakes and its absence is conspicuous.
- **Porque funciona:** It converts a dead-end table into a research tool, and it is a trust signal: a system that shows its sources is checkable. For a thesis product, verifiability is the whole argument.
- **Aplica-se aqui:** Finnhub company-news responses carry a url field, and RSS items carry a link — check whether the capture path retains it (NewsItem may drop it, in which case this is a schema field plus a backfill for future captures only, which is fine: new items link, old ones do not). Cost is near zero if the URL survived, and it must open in a new tab so the user does not lose the page.
- **Custo:** Low if the URL was captured; medium if it must be added to the schema and only applies going forward. No privacy cost as long as links are plain anchors and not proxied.
- **Veredicto:** adopt

#### WOULD LOVE, DOES NOT EXIST: a calm-strip showing how ordinary the last 30 days were

- **O que e:** A single row of 30 small marks above the grid, one per trading day, height or colour showing how many of the 12 were flagged that day. Hovering a mark shows the date and count; clicking it loads that day in frozen-date mode.
- **Fonte:** Journey 1 (the holder wants to know whether today is special or whether the product cries wolf) and Journey 3 (the returning user wants to place today in context). Precedent: GitHub's contribution graph as an at-a-glance density read; Apple Health's trend bars.
- **Porque funciona:** It answers a question no card can: 'is this a lot?' It also quietly makes the case for the gates — a strip showing 1-2 flags on most days proves the system is selective, which is far more persuasive than a claim of selectivity. And it is the permission-to-do-nothing argument extended from one day to a month.
- **Aplica-se aqui:** detect_all already replays the flag decision across a whole series with no lookahead, and the replay is already used for chart markers. Doubles as the entry point for frozen-date mode, so it pays for two features. It shows only what was measured, so it introduces no unsupported score (H4 safe).
- **Custo:** Medium. Twelve replays over 30 days must be precomputed and cached (the V6' lesson: never compute this on the entry-page critical path — bake it into a snapshot artefact the page just reads).
- **Veredicto:** adopt

#### WOULD LOVE, DOES NOT EXIST: 'get this on your phone' with one-tap ticker subscription

- **O que e:** On a company detail page, a single control: 'Alert me about NVIDIA' that opens the Telegram bot with /watch NVDA pre-filled via a t.me deep link.
- **Fonte:** Journeys 2 and 4 — a visitor who values the page has no way to convert into an alert subscriber. The interactive bot with /watch, /unwatch, /list, /stop already exists (investigator/telegram_bot/) and is invisible from the dashboard.
- **Porque funciona:** It closes the loop in the other direction from finding 4: the alert brings you to the page, the page signs you up for alerts. Also a small, real demonstration of a working two-way product for the jury, using a capability already built and currently unused.
- **Aplica-se aqui:** t.me/<bot>?start=watch_NVDA is a standard Telegram deep link and needs no server. Keeps the 20-tickers-per-user cap and the reversible /stop that are already implemented, so the responsible-product position is unchanged.
- **Custo:** Very low — one link per detail page plus a start-payload handler in the bot. Requires the bot process to be running, which is a deployment decision, not a code one.
- **Veredicto:** adapt

#### REJECT: real-time streaming ticks, WebSockets, and a scrolling ticker tape

- **O que e:** Live per-tick price streaming, and a marquee of prices across the top of the page.
- **Fonte:** Journey 1 (an anxious holder watching numbers twitch is the exact harm the product exists to reduce) and Journey 3 (movement is noise by the third visit). Already cut once with reasons in session 42: ~30 hours of work, answers no research question, and neither persona reported noticing 5 s versus 5 min.
- **Porque funciona:** It does not. Motion reads as urgency, and manufactured urgency is the failure mode of both personas — alarm without information for the holder, alert fatigue for the trader. A ticker tape also consumes the most valuable vertical space on the page for information nobody scans.
- **Aplica-se aqui:** Especially wrong here: the free data sources are delayed anyway, so a twitching number would be theatre over stale data — which is a small dishonesty in a product whose entire claim is honesty. If the student asks for it because it looks modern, offer the 'as of' stamp and the intraday shape instead; those are the real needs underneath.
- **Custo:** Avoided cost: substantial. Also protects the 512 MB dyno budget.
- **Veredicto:** reject

#### REJECT: a market-cap treemap or heatmap as the primary view

- **O que e:** A Finviz-style coloured treemap of the 12 companies as the landing view.
- **Fonte:** Journeys 1 and 4. Precedent considered and rejected: finviz.com/map, which is genuinely good at 500 names and pointless at 12.
- **Porque funciona:** It does not work at this scale. A treemap earns its keep by compressing hundreds of items into one glance; with 12 it conveys less than 12 cards while destroying the one thing that differentiates this product — the plain-English verdict sentence, which cannot fit inside a coloured rectangle. It also encodes only magnitude and direction, dropping rarity, driver and volume, so it is a strictly weaker view.
- **Aplica-se aqui:** Directly relevant because it is the most obvious 'make it look modern' suggestion and it would silently undo the v3 criterion that a verdict precedes every number. If a compact overview is wanted, the answer line (finding 2) plus the calm strip (finding 13) deliver it in less space and with more meaning.
- **Custo:** Avoided cost: a redesign that regresses the product's core claim while appearing more sophisticated.
- **Veredicto:** reject

#### REJECT: any confidence gauge, sentiment score, or 'AI summary' chat box

- **O que e:** A blended confidence dial, a sentiment meter, or a conversational box over the data.
- **Fonte:** Journey 4 (a beginner reads a gauge as advice, whatever the caption says). Already excluded by project rules H2 and H4, and by measurement: the fused convergence score wins in 1 of 3 budgets, event-type badges have silhouette 0.084.
- **Porque funciona:** It does not. A dial is read as a recommendation regardless of its label, and a chat box over grounded data reintroduces exactly the ungrounded-fluency failure the thesis argues against in Chapter 2. Both would convert a measured product into an opinionated one.
- **Aplica-se aqui:** Worth stating plainly in the v4 brief, because 'modern dashboard' research will surface these patterns constantly in 2026 products, and rejecting them is a defensible position with measurements behind it, not a limitation to apologise for. Lead with the refusal in the beginner's first line ('We never predict prices') — journey 4 shows it is a trust purchase, not a caveat.
- **Custo:** Avoided cost: would invalidate H2/H4 and hand a jury its easiest attack.
- **Veredicto:** reject

---

## Percursos de utilizador

*Cinco jornadas minuto a minuto, incluindo a demonstracao ao juri.*

### Sintese

I studied twelve products against one test: what does a non-professional extract in ten seconds? The honest finding is that almost nobody in this market answers "why". TradingView's own unusual-volume page ranks stocks by relative volume up to 2,841x and explains none of it; Koyfin and Bloomberg Web assume you already know what you are looking for; Finviz gives you sector colour and nothing else. The three products that genuinely serve a lay user in ten seconds all do the same structural thing: they fix a small number of NAMED slots that are always present, always in the same order, and always filled — Robinhood Cortex Digests ("Market Backdrop / Return Drivers / Top Movers"), Simply Wall St's Executive Summary (Rewards / Risks as plain-language bullets before any chart), and Stock Events (Today / Upcoming / Past with a badge set that literally includes "Key Driver"). InvestiGator already has the strongest version of this raw material of anything I looked at — three questions, measured answers, no forecast — and is spending it on a uniform 4x3 grid where every card looks equally important. That is the "too zoomed out" complaint, precisely: a flat grid has no hierarchy by construction, so the eye has nowhere to land.

On Simply Wall St specifically, the answer is split and I want to be blunt about it. The Executive Summary, the single-scroll "visual essay" page, and the named binary checks ("Are short term assets greater than short term liabilities?") are the best lay-investor patterns in this market and should be taken. The Snowflake itself should NOT be. It aggregates five incommensurable axes into one shape, its documented criticism (industry-agnostic template, cannot handle restructurings, oversimplified for real due diligence) is exactly what a jury would say, and it collides head-on with the project's own written criterion H4, "no score that measurement does not support". Their Narratives feature, which publishes community fair values ("$16.0 FV - 27% overvalued"), is a straight violation of the founding constraint and is most useful to this project as the named boundary case in Chapter 2, not as a pattern.

On "laggy": the measured numbers in v3_backlog.md say the click path is already fine (0.75s median) and the cost is cold load (5.5s) plus a ~3s first-detail penalty that I traced to parsing an 8.7 MB backfill_kb.jsonl at runtime. That is not a CSS problem and not really a Streamlit-tuning problem either. Everything on these twelve cards is batch-computed by a worker that already runs every 60 seconds. The fix that both the evidence and the constraints point to is the Observable Framework data-loader pattern: compute at cycle time, emit a static snapshot, serve a shell that paints instantly and fills in — which is demonstrably what worldmonitor.app does (my fetch of its finance lens returned only "Preparing workspace / Preparing data / Preparing analysis", i.e. a shell, not a rendered server page).

### As tres recomendacoes principais

1. THE FIXED ANSWER SKELETON. Robinhood Cortex Digests use three named sections in a constant order on every asset - 'Market Backdrop', 'Return Drivers', 'Top Movers' - and Simply Wall St puts Rewards/Risks bullets above everything else. The user learns WHERE the answer lives once, then reads in one second forever after. InvestiGator's three questions are already this skeleton but are not rendered as fixed labelled slots; make them literal, always present, always same position, including when the answer is 'nothing happened' (the product already computes that honestly). This is the cheapest single change with the biggest ten-second payoff.

2. PRECOMPUTE TO A STATIC SNAPSHOT; STOP REPAINTING ON THE SERVER. The Observable Framework data-loader pattern moves all computation to build time so the page 'loads instantly'; worldmonitor.app visibly ships a shell first and fills it. Every number on the 12 cards is already produced by the 60-second worker, and the biggest measured cost (~3s on first detail) is parsing an 8.7 MB JSONL at request time. Emitting one small JSON per ticker at cycle time and serving a static page collapses cold load, works with zero API keys, barely touches the 512 MB dyno, and is what makes View Transitions and optimistic paint possible at all. This answers 'laggy', 'not responsive' and 'static' at the root rather than with CSS.

3. THE DISTRIBUTION STRIP - MAKE 'UNUSUAL' VISIBLE, NOT READ. The product already computes the empirical exceedance count ('6 of the last 249 days moved at least this much'), which Gigerenzer's natural-frequencies research supports as the right format for lay comprehension. Render it: a single strip of ~249 tick marks with today's move marked in position. Simply Wall St does the analogous thing with its Community Fair Value histogram. It is one line tall, needs no statistics vocabulary, carries no model, and fixes the exact honesty bug logged during promotion (MSFT +4.82% called 'an ordinary day' while only 5 of 249 days moved that much) by showing the ruler instead of choosing between two rulers in silence.

### Achados (20)

#### Robinhood Cortex Digests: three named slots, always in the same order

- **O que e:** Cortex Digests are AI-written plain-English explanations of why an asset is moving, structured into three fixed named sections that appear on every asset: 'Market Backdrop' (what's driving the markets), 'Return Drivers' (what is moving your value most), 'Top Movers'. They synthesise market data, breaking news, research reports and analyst ratings. Every Digest carries the disclaimer that it is 'not a research report, a recommendation, or investment advice'. Rolled out in the US in summer 2025, UK August 2025, gated behind Robinhood Gold ($5/mo).
- **Fonte:** https://robinhood.com/us/en/support/articles/cortex-digests and https://robinhood.com/gb/en/learn/articles/cortex-digests-is-here/
- **Porque funciona:** The sections are constant, so the user pays the cost of learning the layout exactly once. After that the eye goes straight to the slot it wants. The ten-second read is not 'read the paragraph', it is 'glance at slot 2'. It also sets a contract: if a slot is present but says little, that itself is information. Robinhood reports 95% of surveyed US users liked it, with 'easy to find what they needed' cited specifically - which is a layout claim, not a content claim.
- **Aplica-se aqui:** This is InvestiGator's three questions, and InvestiGator's version is stronger because each slot is MEASURED rather than LLM-generated: slot 1 = rarity (exceedance count), slot 2 = market/sector/company decomposition, slot 3 = retrieved precedents with measured +1/+3/+5d outcomes. Today the v3 card leads with a verdict sentence but the three answers are not rendered as three persistent labelled slots, so a returning user re-reads prose every time. Make them fixed: same three labels, same order, on the card AND on the detail page, present even when the answer is 'nothing unusual' / 'moved with the market' / 'no close precedent'. Robinhood needs a disclaimer because it generates; InvestiGator does not generate, which is a defensible line to draw in Chapter 2.
- **Custo:** Low - a layout refactor of the card and detail renderer, roughly one session. No new data. Risk: the slots must be honest when empty, and 'no close precedent' has to be as visually confident as a full answer, or the design silently teaches users that empty means broken.
- **Veredicto:** adopt

#### Simply Wall St Executive Summary: plain-language Rewards/Risks bullets before any chart

- **O que e:** A Simply Wall St stock page opens with an Executive Summary of key rewards and risks as short plain-language bullets, then continues as one long scrollable page read 'top to bottom like a visual essay' - valuation, growth, health, dividends, risks, each in order. The whole analysis is one page, not tabs.
- **Fonte:** simplywall.st stock pages, as described in https://www.thestockdork.com/simply-wall-st-review/ and https://stockunlock.com/simply-wall-st-review.html
- **Porque funciona:** Verdict-before-evidence, and the verdict is in words a beginner already owns. The single-scroll essay means there is no navigation decision to make - scrolling is the only interaction, and scrolling has zero learning cost. Tabs force a choice before the user knows what the choices mean.
- **Aplica-se aqui:** This is exactly the inversion the project already committed to in dashboard_acceptance.md section 6 ('opens with a verdict, not with numbers'), so it is independent confirmation from the one competitor explicitly built for non-professionals. What is NOT yet borrowed is the single-scroll essay: v3 currently splits grid and detail across a URL change. For 12 tickers, the detail page should be one continuous scroll - verdict, then rarity strip, then decomposition, then precedents, then the chart, then the event table - with no tabs and no expanders above the fold.
- **Custo:** Low-medium. Mostly reordering existing components plus removing tab/expander affordances. Risk: a long page on mobile needs a sticky context header (see the Delta finding) or the user loses track of which ticker they are reading.
- **Veredicto:** adopt

#### Simply Wall St Snowflake: the composite score is the part to refuse

- **O que e:** The Snowflake is a five-axis radar (Value, Future Performance, Past Performance, Health, Dividends), each axis scored by 6 binary checks, 1 point per pass, so 30 checks total. Bigger and greener = more checks passed. Simply Wall St itself says it is not a buy/sell recommendation.
- **Fonte:** https://support.simplywall.st/hc/en-us/articles/360001740916-How-does-the-Snowflake-work and the published model at https://github.com/SimplyWallSt/Company-Analysis-Model/blob/master/MODEL.markdown
- **Porque funciona:** It works as a memorable brand asset and as a rough triage device - a lopsided shape tells you where to dig. It does NOT work as an answer, and the documented criticism is exactly that: the same industry-agnostic template is applied to every stock, it cannot adjust for one-time charges, M&A, spinoffs or restructurings, and reviewers call it oversimplified for serious due diligence.
- **Aplica-se aqui:** Refuse it, and say why in the thesis. Three reasons specific to this project. (1) It collides with the project's own written criterion H4, 'no score that measurement does not support' - a composite of incommensurable axes has no measured meaning. (2) The Snowflake is a standing grade on a COMPANY; InvestiGator answers about a specific DAY, so a persistent shape would be answering a question nobody asked. (3) A radar over the three questions would be actively wrong because the three answers have different types - a rarity count, an attribution split, and a precedent set - and a radar forces them onto one scale. The positional skeleton (finding 1) gets the recognisability without the fabrication. Naming this refusal is also a free paragraph of related-work differentiation.
- **Custo:** Zero to implement (it is a decision not to build). Cost is one paragraph of Chapter 2 and one of Chapter 6.
- **Veredicto:** reject

#### Simply Wall St's named binary checks map directly onto the existing gate funnel

- **O que e:** Under the Snowflake sit 30 individually named, individually readable pass/fail checks, each phrased as a question in plain English: 'Are short term assets greater than short term liabilities?', 'Has Earnings Per Share (EPS) increased in past 5 years?', 'Is the PE ratio less than the market average but still greater than 0?'.
- **Fonte:** https://github.com/SimplyWallSt/Company-Analysis-Model/blob/master/MODEL.markdown
- **Porque funciona:** Each check is auditable on its own, so the user can disagree with one without discarding the analysis. It converts a black box into a checklist, which is the same move as showing your working. This is the single most-praised element in the reviews I read, more than the Snowflake itself.
- **Aplica-se aqui:** InvestiGator already computes this and does not show it. gate_log records exactly where each ticker died - no_news, none_relevant, stale, weak_precedent, triage_suppressed, alerted - with real margins (MSFT 0.42 vs a 0.45 similarity floor). Render it on the detail page as a named checklist: 'Did anything move unusually? yes', 'Was there relevant news? yes, 4 items', 'Did we find a close enough past case? no - closest was 0.42, our floor is 0.45'. This is XAI-first made visible, it is the answer to 'why did I get no alert', and it turns the suppression rate (9 in 10 scans) from an embarrassment into the product's most honest feature. It also directly serves the long-term holder persona, whose most valuable output is permission to do nothing.
- **Custo:** Low-medium. The data exists; needs a phrasing layer (one function, testable, same pattern as app/verdict.py) plus a card component. One to two sessions. Risk: the phrasings must never imply a prediction - run them through the same allowlist sweep that verdict.py already uses.
- **Veredicto:** adopt

#### TradingView's unusual-volume screen is the anti-pattern to name explicitly

- **O que e:** TradingView's US unusual-volume page is a 12-column table sorted by 'Rel vol' (relative volume). Values run to absurd extremes - HYFM at 2,841.11x normal. Columns: Symbol, Rel vol, Price, Chg %, Vol, Mkt cap, P/E, EPS dil TTM, EPS dil growth TTM YoY, Div yield % TTM, Sector, Analyst rating. The page tells you unusual volume 'may influence future prices' and provides no cause for any row.
- **Fonte:** https://www.tradingview.com/markets/stocks-usa/market-movers-unusual-volume/
- **Porque funciona:** It does not, for a lay user. In ten seconds a beginner extracts 'some stocks I have never heard of are trading a lot' and nothing else. It is a professional's raw feed: 12 columns is roughly double the 5-9 elements that dashboard research suggests for a default view, and the one number that matters is unexplained. It works for a screener-literate trader who will do the digging.
- **Aplica-se aqui:** This is InvestiGator's foil, and it is worth naming in the thesis' competitive matrix because it is the market leader failing the exact gap the project fills. It also carries a design warning: InvestiGator computes an unusual-volume ratio too, and the temptation is to display '3.3x vol' as a badge. Session 45 already made the right call by demoting it to text; keep it demoted, and never let it become a sortable column. A ratio without a cause is exactly this page.
- **Custo:** Zero. One row in the Chapter 2 comparison table, plus a standing rule: no metric gets displayed unless the same view also carries its cause or its rarity.
- **Veredicto:** reject

#### Perplexity Finance: the follow-up question IS the drill-down affordance

- **O que e:** Perplexity Finance opens with a search bar and a handful of featured tickers - nothing else. A ticker returns price, a live trend chart, and key stats, and the primary way to go deeper is to ask a natural-language follow-up in the same thread: 'What caused the drop in April?', 'Compare AAPL to MSFT'. The market summary is AI-generated with cited news sources. A sector heatmap was added in 2025. Reviewers consistently note it loads in a few seconds and 'doesn't overwhelm you with options'.
- **Fonte:** https://techpoint.africa/guide/perplexity-finance-review/ and https://sidsaladi.substack.com/p/perplexity-finance-101-2026-the-complete
- **Porque funciona:** Two things. First, the empty-ish start page is a feature: there is exactly one thing to do. Second, follow-up questions are self-documenting navigation - the user does not have to guess what a tab called 'Analysis' contains, because the affordance is phrased as the question it answers. And the citations mean the trust chain is visible.
- **Aplica-se aqui:** Adapt, do not adopt. A multi-turn chatbot was explicitly cut from this project's scope (session 42) and re-adding it is scope creep plus an LLM dependency the 512 MB dyno and the no-keys constraint cannot carry. But the AFFORDANCE transfers with zero LLM: render 3-4 pre-baked question chips under each card - 'Was it the sector?', 'Has this happened before?', 'How rare is this?', 'Why no alert?' - each one an anchor link into the section that already answers it. That is question-shaped navigation over precomputed answers. It is also the most direct fix for 'too zoomed out': the grid currently offers one undifferentiated click, and chips turn that into four legible destinations.
- **Custo:** Low. Static anchors plus styling, under a session. Risk: chips must not promise an answer the data cannot give - 'Has this happened before?' must gracefully land on 'no close precedent, here is why' rather than an empty section.
- **Veredicto:** adapt

#### Stock Events: 'Just one look is enough', and a badge set that already includes 'Key Driver'

- **O que e:** Stock Events is a portfolio/watchlist app whose stated positioning is 'Just one look is enough' and 'Instantly Know What's Happening with Your Investments - For those who want to know more without the noise.' The main screen groups by time - Today / Upcoming / Past - and each row is a company logo, ticker, a percent change, and a type badge from a small closed set: Earnings, Economics, Key Driver, Rating. Home-screen widgets give the same read without opening the app.
- **Fonte:** https://stockevents.app/en
- **Porque funciona:** Temporal grouping is the one taxonomy every user already has. The badge vocabulary is small and closed, so it is memorable - the same reasoning that made this project cut its icon set to five. And logos as the primary row identifier beat tickers for recognition, which matters for a lay user who knows 'Apple' better than 'AAPL'.
- **Aplica-se aqui:** Three things transfer. (1) 'Key Driver' as a badge is literally InvestiGator's driver line - independent confirmation that a lay audience accepts attribution as a first-class label, not a footnote. (2) Today / Upcoming / Past is a better default sort for the card grid than alphabetical or by ticker: 'moved today' vs 'quiet' vs 'earnings coming'. (3) The logos are already built and versioned as data: URIs from session 45, so that half is done and validated. The tagline is also a usable acceptance test: if a screenshot of the grid does not answer 'anything I should look at?' without scrolling, it fails.
- **Custo:** Low - a sort/group change plus a badge component. Under a session. Risk: adding an 'Upcoming' group requires an earnings calendar, which is a new free-API dependency; skip it and use only 'moved today / quiet' unless a free source is already wired.
- **Veredicto:** adopt

#### Break the uniform grid: tile size must signal priority (bento pattern)

- **O que e:** Bento grid layout - modular tiles of deliberately different sizes, where tile size encodes priority rather than relying on colour or labels alone - is the dominant dashboard layout of 2025-26. Analytics products use it to surface 15-30 metrics without overload: KPIs as 2x1, funnels as 2x2, activity lists as 1x2. One secondary source cites a 2025 Journal of Usability Studies finding of 23% faster information-finding on modular vs linear layouts.
- **Fonte:** https://www.saasframe.io/blog/designing-bento-grids-that-actually-work-a-2026-practical-guide and https://www.orbix.studio/blogs/bento-grid-dashboard-design-aesthetics
- **Porque funciona:** A uniform grid is flat by construction - twelve identical cards assert that twelve things are equally important, which is false on almost every trading day and is precisely why the eye has nowhere to land. Size is the strongest pre-attentive priority cue available and it costs no colour, no icon and no words.
- **Aplica-se aqui:** This is the direct answer to 'too zoomed out'. On a typical day this product's own measurements say seven to nine of twelve names are calm. So: the loudest one or two names get a 2x2 tile carrying the verdict, the rarity strip and a sparkline; the rest get 1x1; and the calm block collapses into one wide strip reading '9 quiet - nothing unusual'. The ranking key already exists (the exceedance count, which is a clean rarity ordering and is honest in a way a z-score is not). Caveat I would flag: I could not verify that JUS study to a primary source, so do not cite the 23% number in the thesis.
- **Custo:** Medium. CSS grid template plus a size-assignment rule, and the card component must render at two sizes. One to two sessions. Risk: the layout reflows daily as the loud names change - which is good for engagement but must not shift positions under a click, so freeze the layout per snapshot rather than per interaction.
- **Veredicto:** adopt

#### Progressive disclosure: 12 uniform cards already exceeds the safe default

- **O que e:** The consensus pattern is that a default dashboard view shows roughly 5-9 elements and hides everything else behind drill-downs, expandable cards or filters, with the most important number given the most visible position. Chime is the standard fintech example: one number (your balance), everything else behind expandable menus.
- **Fonte:** https://www.uxpin.com/studio/blog/dashboard-design-principles/ and https://www.eleken.co/blog-posts/fintech-ux-best-practices
- **Porque funciona:** Beginners build confidence by not being forced to understand every control up front. The rule is not 'show less data', it is 'show less at once' - the data stays one click away, which is why it does not feel like a dumbed-down product.
- **Aplica-se aqui:** Twelve equal cards is 12 elements, above the range, and it explains the 'zoomed out' complaint better than any styling critique. Combined with the bento finding, the default view becomes about 4-5 elements: two loud tickers, one quiet strip, one market-wide line ('S&P -0.4%, so most of this is not company-specific'), one 'what we checked today' summary. Everything currently on a card that is not one of the three answers should move below the fold on the detail page.
- **Custo:** Low - this is subtraction, and subtraction is cheap. The risk is political rather than technical: the student has rejected seven versions, and a version that shows LESS will read as regression unless the drill-down is visibly one click away. Ship it with the question chips (Perplexity finding) so removal and access land in the same change.
- **Veredicto:** adopt

#### Architecture: precompute a static snapshot at cycle time, serve a shell that paints instantly

- **O que e:** Observable Framework's data-loader model runs all data work at BUILD time in any language (Python included), emits static snapshots, and bundles them with the page, so 'the experience for the user is an app that loads instantly' with no per-user query. CI/CD rebuilds the snapshots on a schedule. worldmonitor.app is visibly doing the shell-first version of this: fetching its finance lens returns only 'Preparing workspace / Preparing data / Preparing analysis', i.e. it ships a shell and fills it client-side, and it renders 56 layers 'as the page loads'.
- **Fonte:** https://observablehq.com/framework/data-loaders and https://github.com/observablehq/framework ; shell behaviour observed directly at https://worldmonitor.app/finance
- **Porque funciona:** It removes the server from the interaction path entirely. Every complaint in the student's list - laggy, not responsive, static - is downstream of the fact that Streamlit re-runs the script server-side on every interaction. No amount of fragments, caching or CSS changes that; the measured 5.5s cold load is network and parse, not compute (the backlog's own measurement puts detect_all at 18.6 ms).
- **Aplica-se aqui:** This fits this project almost suspiciously well. There are 12 tickers, the worker already runs every 60 seconds, and every displayed number is batch-computed. Have the worker emit one small JSON per ticker plus an index at the end of each cycle. I checked the current cost driver: data/samples/backfill_kb.jsonl is 8.7 MB and is parsed at request time - that is the ~3s first-detail penalty in the backlog. A per-ticker precomputed precedent slice is a few KB. The snapshot is committed, so the app still starts with no API keys, still runs on a 512 MB dyno (in fact it barely uses it), and a visitor still just opens a URL. This is also what unlocks View Transitions and optimistic paint, which are impossible while the server owns the DOM.
- **Custo:** High - this is the real work, and it is a presentation-layer rewrite of ~1,400 lines of app/dashboard.py. Two to four sessions for a vertical slice. The honest mitigation is the one the briefing already demands: build ONE page as a prototype against a real snapshot and measure time-to-first-paint against the 5.5s baseline before committing. investigator/ is untouched throughout - it becomes a library that writes JSON, which is a cleaner separation than today and is itself a defensible engineering contribution for the thesis.
- **Veredicto:** adopt

#### View Transitions API: native card-to-detail morphing, no library

- **O que e:** The View Transitions API animates between DOM states without a framework. Same-document transitions reached Baseline Newly Available in October 2025 (Chrome/Edge 111+, Firefox 133+, Safari 18+). Cross-document transitions work in Chrome/Edge 126+ and Safari 18.2+, but not Firefox. It is explicitly promoted for 'reducing perceived loading latency' and keeping users in context.
- **Fonte:** https://developer.chrome.com/blog/view-transitions-in-2025 and https://web.dev/blog/same-document-view-transitions-are-now-baseline-newly-available
- **Porque funciona:** Continuity beats speed for perceived responsiveness. If the card the user clicked visibly grows into the detail header, the brain reads it as 'I moved', not 'the page reloaded'. A 300 ms transition can feel faster than an instant repaint, because a repaint destroys spatial context and forces re-orientation.
- **Aplica-se aqui:** This is the specific, cheap, named fix for 'not responsive enough' and 'static' - the two complaints that CSS alone cannot address. Card grid to ticker detail is the exact canonical use case. It requires the static/client-rendered path from the previous finding; it cannot be retrofitted onto server-repainted Streamlit. Note the constraint that matters here: the project decided to keep real shareable URLs (?t=NVDA), so if navigation stays cross-document, Firefox users get an instant cut instead of a morph - which degrades gracefully and is acceptable, but should be a stated decision rather than a surprise.
- **Custo:** Very low ONCE the static path exists - a CSS view-transition-name on the card and header plus a few lines of JS. Effectively free as part of the rewrite, impossible before it.
- **Veredicto:** adopt

#### The distribution strip: render the exceedance count instead of writing it

- **O que e:** Simply Wall St added a Community Fair Value histogram in 2025 so a user can see where one estimate sits inside the spread of all estimates. The generic device is a strip/dot plot: every observation kept visible, so gaps, outliers and skew are read directly rather than inferred from a summary statistic.
- **Fonte:** https://support.simplywall.st/hc/en-us/articles/7894830045199-What-s-New (Community Fair Value histogram); strip-plot rationale from https://homepage.cs.uiowa.edu/~luke/classes/STAT4580/dists.html
- **Porque funciona:** Position in a distribution is read pre-attentively. 'Far right end of the strip' takes under a second and needs no vocabulary; '6 of the last 249 days' takes about four seconds of reading and a small arithmetic step. Showing every observation also makes the claim auditable - the reader can see there really are 249 marks.
- **Aplica-se aqui:** The product already computes exactly the right underlying quantity, and refused the dishonest alternative (a normal-theory probability) for the right reason. Turning it into a one-line visual is the highest information-per-pixel change available: a strip of ~249 ticks with today marked. It also fixes a real bug the promotion caught - MSFT at +4.82% was labelled 'an ordinary day' while only 5 of 249 days moved that much, because the 20-day ruler and the 1-year ruler disagreed and the interface silently picked the reassuring one. A strip shows the ruler instead of choosing. Keep the sentence too (see next finding); do not replace text with picture.
- **Custo:** Low. It is one small SVG or a 249-cell flex row - no chart library needed, which also removes a Plotly render from the card path. Under a session. Risk: at 12 cards it must be tiny and unlabelled on the card, with axis labels only on the detail page.
- **Veredicto:** adopt

#### Natural frequencies: the research supports the counting sentence, with a caveat worth reporting

- **O que e:** Gigerenzer and Hoffrage's line of work argues for replacing percentages and conditional probabilities with natural frequencies ('3 to 5 out of 10 patients') because they disambiguate the reference class and are easier to reason with. The clinical example is a psychiatrist whose patients badly misread 'a 30 to 50 percent chance' but understood '3 to 5 out of 10 patients'. Counter-evidence exists: a randomised pilot on fact boxes found natural frequencies 'barely understood' and percentages preferred in that format.
- **Fonte:** http://library.mpib-berlin.mpg.de/ft/gg/gg_what_2011.pdf and https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9915941/
- **Porque funciona:** A count carries its own reference class - 'of the last 249 trading days' states what the denominator is, whereas a percentage or a z-score leaves the user to supply one, and lay users usually supply the wrong one or none.
- **Aplica-se aqui:** This is peer-reviewed grounding for a decision the project already made on intuition, and it belongs in Chapter 2 next to the trust/reliance citations that are already there. The caveat should be reported honestly rather than suppressed, and it has a design consequence: do not treat count-vs-percentage as either/or. Show the strip (position), the count ('6 of the last 249 days'), and the raw percentage move together - the percentage is the fact the sentence explains, which is exactly the correction already made to criterion V2. Note the format difference: the pilot that found weak comprehension used static fact boxes with no visual, which is not this design.
- **Custo:** Zero code - the sentence already exists. Cost is one verified citation and a paragraph. Genuine thesis value at essentially no engineering cost.
- **Veredicto:** adopt

#### Robinhood's dotted previous-close line, and Delta's animated total

- **O que e:** Two small devices. Robinhood's chart draws a dotted horizontal line at the previous day's close, so 'up or down today' is answered by whether the line is above or below the price, without reading an axis. Delta's Portfolio 3.0 redesign animates the total-worth number when it refreshes or when a filter changes, and uses a sticky header that switches between 'Portfolios' and the current portfolio name as you scroll - the stated goal was 'displaying a lot of data while staying easy to understand and digestible at a glance'.
- **Fonte:** https://blog.bluechip.dev/how-to-read-the-robinhood-stock-details and https://delta.app/academy/post/your-portfolio-your-way
- **Porque funciona:** The dotted line converts a numeric comparison into a spatial one - the cheapest possible cognitive saving. The animated number is the minimum viable proof that the page is alive; a static number that silently changes reads as a stale page, which is precisely the 'old-school and static' complaint. The sticky context header solves the long-scroll orientation problem the single-page essay creates.
- **Aplica-se aqui:** All three are near-free and all three attack named complaints. The dotted previous-close line goes on every card sparkline and the detail chart. The animated count-up goes on the headline percentage whenever the 60-second snapshot changes - and because the data really does refresh every 60 seconds, the animation is truthful rather than decorative. The sticky header is required if the detail page becomes one long scroll. One warning: this project has already been burnt by an emoji rendering a green up-arrow on a -7.64% move, so any motion must be driven by the sign of the stored number, not by a separate presentation flag.
- **Custo:** Very low. A reference line is a few lines of chart config; a count-up is a small CSS/JS animation; a sticky header is CSS position:sticky. Under a session for all three. Respect prefers-reduced-motion.
- **Veredicto:** adopt

#### worldmonitor.app: instability scores, rolling-baseline anomalies, and dossiers with cited sources

- **O que e:** worldmonitor.app renders one live map with 56 layers as the page loads, showing conflicts, vessels, flights, fires and outages. It flags unusual activity as density anomalies against 'rolling baselines' per chokepoint, requires multi-source corroboration, and publishes composite scores - country instability indices fusing 12 signals (Ukraine 78, Israel 71, Iran 66) and chokepoint disruption scores (Bab el-Mandeb 82). Clicking a country opens a 'full dossier' brief with cited sources. Navigation is a Cmd-K command palette with 154 commands plus six named lenses (World, Finance, Commodity, Energy, Tech, Happy). It uses directional arrows and explicitly ships with 'no tour, no empty states'.
- **Fonte:** https://worldmonitor.app/ (fetched directly)
- **Porque funciona:** 'No empty states' is the sharpest idea here: every surface is populated on arrival, so there is never a moment where the product looks broken or unfinished. The rolling-baseline framing is the same statistical honesty InvestiGator uses. The dossier-with-citations pattern gives a drill-down that is auditable.
- **Aplica-se aqui:** Mixed, and the split matters. ADOPT 'no empty states' - a quiet day must render a confident populated card, which this project already does correctly ('203 of the last 249 trading days moved as much or more') and must not regress on. ADOPT the dossier-with-cited-sources shape for the ticker detail page. REJECT the composite instability score for the same reason as the Snowflake: fusing 12 signals into '78' is precisely what criterion H4 forbids, and the project already measured that its own convergence score won in only 1 of 3 budgets and correctly kept it out of production. ADAPT the command palette: Cmd-K is undiscoverable for a lay user, so make it a visible search box that happens to accept a ticker - keep the capability, lose the modal. The six lenses do not transfer; 12 tickers do not need lenses.
- **Custo:** Low for the empty-state discipline (mostly a test, and 20 gate tests already exist to hang it on). Low for a visible search box. Zero for the rejections.
- **Veredicto:** adapt

#### Bloomberg Terminal: group summaries by topic, not by time

- **O que e:** Bloomberg's terminal news layer has three relevant pieces: News Trends scans which companies and topics are getting the most media and reader attention plus social velocity; AI Summary produces a timestamped summary of recent company news 'grouped by financial analysis topics'; and KI (Key Insights) flags the most interesting news about a company.
- **Fonte:** https://www.bloomberg.com/professional/products/bloomberg-terminal/news/ and https://www.bloomberg.com/company/press/investors-harness-bloombergs-expanded-ai-tools-to-discover-and-summarize-news
- **Porque funciona:** Chronological news feeds force the reader to do the clustering. Topic grouping does it for them, which is the difference between 'here are 40 headlines' and 'here are 4 things going on'. Note that even Bloomberg, whose users are professionals, decided the raw feed was too much.
- **Aplica-se aqui:** InvestiGator has ~38,000 news items with measured impact and semantic embeddings, which is exactly the machinery to cluster by topic - and it already measured the relevant caveat honestly (event-type taxonomy: purity 0.712, AMI event 0.358 > ticker 0.188, but silhouette 0.084, which is why it was correctly NOT wired into retrieval). So the disciplined version is: use clustering for DISPLAY grouping of a ticker's news, where a wrong grouping costs a mildly odd heading, and keep it out of RETRIEVAL, where a wrong grouping silently discards valid precedents. That distinction is itself a good thesis paragraph - the same measurement supports one use and forbids the other.
- **Custo:** Medium. Clustering exists; the work is display grouping plus heading text. One to two sessions. Risk: headings must be descriptive, never predictive, and must survive the same 112-combination sweep verdict.py already runs.
- **Veredicto:** adapt

#### Koyfin and Yahoo: configurable dashboards are the wrong direction for a lay user

- **O que e:** Koyfin's core concept is Custom Dashboards - 'a bird's-eye view of all the data you care about most, on one screen' - built by drag-and-drop, plus reusable Custom Views (saved column sets) on watchlists, plus Market Dashboards of curated data. It is described as best for individual investors and analysts who prioritise fundamental research and customisable multi-pane dashboards. Yahoo Finance moved the opposite way in its biggest redesign in a decade: 40% fewer ads, bigger headlines, bigger photos, FEWER modules, plus a customisable dock and Compare mode.
- **Fonte:** https://www.koyfin.com/features/ and https://www.yahooinc.com/press/yahoo-finance-debuts-new-design-and-features-to-empower-everyday-investors
- **Porque funciona:** Customisation works when the user already knows what they want, which is the definition of a professional. For a beginner, an empty configurable canvas is a test they can fail. Yahoo, which serves the mass-market audience closest to this project's, went the other way and reduced module count - that is the more relevant precedent.
- **Aplica-se aqui:** Do not build dashboard configuration, saved layouts, or column pickers. It would be the eighth rejected redesign wearing a different hat, because it moves the design problem onto the user instead of solving it. The one Koyfin idea worth keeping is small: reusable named views. Applied here that means the URL is the view - ?t=NVDA already works and is shareable, and adding at most one more parameter (a time range) gives the entire benefit of saved layouts with none of the UI. Yahoo's direction of travel is the instruction: fewer modules, larger type.
- **Custo:** Zero - this is a decision not to build, and it protects several sessions.
- **Veredicto:** reject

#### Finviz treemap: correct at 500 stocks, wrong at 12

- **O que e:** The Finviz map is a treemap where box size is market capitalisation and box colour is performance, green to red. It is free, and is the most recognisable single visual in retail finance. Reviewers credit it with letting an investor grasp market sentiment instantly and with preventing a small-cap's move being weighted mentally the same as a mega-cap's.
- **Fonte:** https://finviz.com/blog/finviz-map-a-comprehensive-guide/ and https://www.oreateai.com/blog/understanding-the-finviz-heat-map-a-visual-guide-to-market-performance/ab8a45190f02837a74aef661b054a234
- **Porque funciona:** Two encodings, both pre-attentive, over hundreds of items - it is a genuine ten-second read and deserves its reputation. It works BECAUSE of scale: treemaps need many cells and wide size variance for the area encoding to carry information.
- **Aplica-se aqui:** Reject at this scale, and be explicit about why so it is not proposed again. Twelve US large caps have neither the count nor the cap dispersion a treemap needs; a 12-cell treemap is a bar chart with worse position encoding and worse labels. Worse, the treemap's colour channel would carry percent change, which is the one variable this product deliberately refuses to lead with - it leads with rarity, because +3% means different things for different names. The bento grid (finding 8) delivers the same 'size means importance' intuition while letting size encode rarity rather than market cap, which is the ordering this product actually believes in.
- **Custo:** Zero. Worth one sentence in the market study recording the rejection, since a heatmap is the most likely thing a reviewer will ask for.
- **Veredicto:** reject

#### Simply Wall St Narratives and Public.com Predictive Alpha: the boundary case, not a pattern

- **O que e:** Simply Wall St Narratives publish per-stock investment cases with explicit fair values and forecasts, displayed as '$16.0 FV - 27% overvalued' alongside '4.2% Revenue growth p.a', with Fair Value Monitoring that sends price alerts against a community fair value. Public.com's Alpha layers GPT-4 over quotes, financials, analyst recommendations and news; its Predictive Alpha / An-E product forecasts prices outright.
- **Fonte:** https://simplywall.st/features/community-narratives and https://www.thestockdork.com/predictive-alpha-review/
- **Porque funciona:** Commercially it works very well - a number to act on is what most retail users say they want, and 'overvalued by 27%' is far more satisfying than 'here is what happened last time'. That is the honest competitive pressure this project is choosing to resist.
- **Aplica-se aqui:** Both are direct violations of the founding constraint, and the correct move is to cite them rather than copy any of it - not one forward-looking probability, no fair value, no 'expected move', on any surface. There is real thesis value here: this is the sharpest available demonstration that the no-prediction stance is a deliberate position rather than a missing feature, since the two products explicitly built for non-professionals both crossed the line and this one did not. It also supplies a concrete acceptance criterion: any new UI copy must survive the existing 16-word prohibition sweep, and 'fair value', 'target' and 'overvalued' should be added to that word list before v4 copy is written.
- **Custo:** Zero code. One paragraph in Chapter 2, one in Chapter 6, and three words added to the verdict.py banned list with a test.
- **Veredicto:** reject

#### Alert fatigue evidence exists but the widely-cited numbers are unverified

- **O que e:** Trade sources repeat a claim attributed to a 2025 University of Chicago behavioural-finance study that traders receiving more than 100 unfiltered alerts per day make 22% more impulsive trades and hold losing positions 18% longer, with decision quality falling 15-25%. The practical recommendations are consistent across sources: meaningful thresholds rather than every 1% move, multi-condition alerts to cut false signals, watchlist-only scope, and a three-tier severity system mapping each tier to a delivery channel and expected response time.
- **Fonte:** https://www.tradealgo.com/trading-guides/tools/how-to-set-up-automated-trading-alerts-that-actually-work and https://pro.stockalarm.io/blog/best-stock-alert-apps-2026
- **Porque funciona:** The qualitative claim is uncontroversial and matches this project's own operating data: the gates suppress roughly 9 of 10 scans, and that suppression is the product working, not failing. The three-tier severity model matches the notable/strong/extreme levels already implemented.
- **Aplica-se aqui:** Use the argument, do not use the numbers. I could not trace the 22%/18%/15-25% figures to any primary publication, and this project's rule is that nothing enters the thesis without a verified identifier - so citing them would be exactly the kind of soft fabrication the citation audit is designed to catch. The transferable design point stands on its own and on measured local evidence: severity must be visible on the surface (a notable move and an extreme move must not look alike), and the suppression funnel should be shown rather than hidden, because 'we checked 12 names and 9 were unremarkable' is the long-term holder's most valuable output. If a citation is needed here, the existing trust-and-reliance references (Lee and See 2004, Bansal 2021) already carry the appropriate-reliance argument with verified DOIs.
- **Custo:** Zero. This is a guard against a plausible-looking citation error, plus one design rule (severity must be visually distinct, not just worded differently).
- **Veredicto:** adapt

---

## Tecnologia e desempenho

*Ficar em Streamlit ou sair, medido por tempo ate ao primeiro pintar.*

### Sintese

**Recommendation: stay on Streamlit, but upgrade it and take the network off the request path. Do not re-platform before 13 September.**\n\nThe decisive fact is a measurement, not a preference. I profiled the suspected bottlenecks: the 8.8 MB backfill parses in **0.30 s**, pandas imports in 0.97 s, plotly in 0.05 s. None of that explains a ~5.5 s cold load — and the project's own session-47 profiling reached the same conclusion, that the cold-load bottleneck is **network**, not compute, with warm clicks already at a 0.75 s median in a real browser. A FastAPI + React rewrite would move rendering off the server and inherit the identical 5 s wait, because the wait is yfinance and the alerts history over HTTP. The most expensive options do not fix the stated problem.\n\nThe second decisive fact is that the verdict was passed on the wrong software. `requirements.txt` pins `streamlit==1.41.1` from **December 2024**; current is 1.60.0 from July 2026. The nineteen intervening releases are almost entirely the 2026 performance programme: Starlette/Uvicorn replacing Tornado (1.57), `parallel=True` fragments and session-scoped caching (1.58), fragments that update any container without a full rerun plus `st.skeleton` (1.59), and Custom Components v2 with **no iframe isolation** (1.56) — that last one being the main structural reason Streamlit apps have historically been unable to look bespoke. 'Streamlit re-runs server-side on every interaction' describes 1.41 accurately and 1.60 poorly.\n\nThe third fact is structural and in the project's favour: `verdict.py`, `ui_tokens.py`, `tables.py` and `method.py` contain **zero Streamlit imports** — `card_html()` and `sparkline_svg()` are pure functions returning HTML strings, pushed through 46 `unsafe_allow_html` calls in a thin shell. Streamlit is already only transport. That cuts both ways: it means the app does not feel static *because of Streamlit* (the markup is already hand-written), and it means a future migration is perhaps 10× cheaper than the usual Streamlit escape. That optionality is worth naming in Chapter 4 as a design outcome; it is not worth exercising six weeks before submission.\n\nThe sequenced plan: (1) upgrade the pin — hours, low risk given a conservative API surface of mostly `st.markdown` and navigation state already in `st.query_params`; (2) precompute the 12-ticker snapshot to JSON in the worker that already cycles every 60 s, and have the web dyno read a file instead of making blocking calls — 1–2 days, fails open, and this is the only item that attacks the measured bottleneck; (3) add `st.skeleton` and `parallel=True` fragments so the wait is legible rather than blank — 1 day; (4) *only then*, if the detail view still drags, swap Plotly (~2 MB minified, 3 MB+ in production builds) for Lightweight Charts v5 (**35 kB** base bundle, 10k+ points at 60 FPS) via a Components-v2 component. Note the grid needs no charting library at all — it already uses hand-rolled inline SVG sparklines.\n\n**What would change my mind.** If the upgrade plus precompute lands and cold load is still above ~2.5 s with the network removed, then the cost really is Streamlit's boot and transport, and the FastAPI + HTMX path (55–65 kB first visit, no hydration delay) becomes justified — as Track B, after submission. If the student's complaint turns out on questioning to be *aesthetic* rather than temporal — 'old-school' and 'not cool' are visual words, and seven redesigns have been rejected on visual grounds with no stopping condition — then none of this is the fix, and the honest move is to write acceptance criteria for *look* the way session 46 wrote them for *behaviour*, because an aesthetic target without a stopping condition will reject an eighth redesign too. And if the jury-facing risk of touching a working deployed system six weeks out is judged higher than the UX gain, then do item (1) alone and stop: it is hours of work and reversible in one line of the `Procfile`.

### As tres recomendacoes principais

1. **Upgrade `streamlit==1.41.1` (Dec 2024) to 1.60.0 (Jul 2026) — hours of work, and it is the gate for everything else.** The 19 missed releases are precisely the 2026 performance programme: Starlette/Uvicorn replacing Tornado (1.57), `parallel=True` fragments and session-scoped caching (1.58), fragments updating any container without a full rerun plus `st.skeleton` (1.59), and Custom Components v2 with no iframe isolation (1.56). The 'Streamlit re-runs everything server-side' critique is accurate for the pinned version and outdated for the current one. Upgrade risk is low here: the API surface is 57 `st.markdown` / 20 `st.cache_data` with no exotic widgets, and navigation state already lives in `st.query_params`, which is the upgrade-safe pattern. Verify the query-param path specifically — 1.60 has breaking changes there.

2. **Precompute the 12-ticker snapshot to static JSON in the worker dyno; serve a file instead of making blocking network calls.** This is the only item that attacks the actual measured bottleneck. I profiled it: the 8.8 MB backfill parses in 0.30 s and pandas imports in 0.97 s, so the ~5.5 s cold load is network — a conclusion the project's own session-47 profiling already reached. The watchlist is fixed at 12, the worker already cycles every 60 s, and `detect_all` over a year costs 18.6 ms. Freshness is unchanged; the data simply stops being fetched while the user waits. Fail open to the current live path so a missing snapshot degrades rather than breaks. 1–2 days.

3. **Add `st.skeleton` plus `parallel=True` fragments — the highest-leverage answer to 'static and old-school', because the underlying number is network-bound and has a floor.** Skeletons that mirror the real layout convert a blank 5 s into a visibly-loading 5 s; the measured time is unchanged and the interpretation is not. The 12-card grid has a trivially derivable skeleton from the existing 4/3/2/1 column ladder, and `_grid_live` currently resolves its 12 snapshots in a sequential comprehension that `parallel=True` fixes directly. Both need the upgrade first. Then, and only if the detail view still drags at its measured 0.75 s warm click, swap Plotly (~2 MB minified) for Lightweight Charts v5 (35 kB, 10k+ points at 60 FPS) — noting the grid needs no chart library at all, since it already emits hand-rolled inline SVG sparklines.

### Achados (14)

#### The Streamlit pin is 19 months stale — the verdict was passed on a version that predates all of Streamlit's 2026 performance work

- **O que e:** `requirements.txt` pins `streamlit==1.41.1`, released December 2024. Current is 1.60.0 (21 July 2026). The intervening releases are almost entirely about the exact complaint being made: 1.57.0 (Apr 2026) replaced the Tornado server with **Starlette/Uvicorn** (ASGI); 1.58.0 (May 2026) added `parallel=True` on fragments for concurrent execution and **session-scoped caching**; 1.59.0 (Jul 2026) let fragments **write to containers defined outside the fragment** — i.e. update any part of the page without a full rerun — and added **`st.skeleton`** for loading placeholders; 1.56.0 shipped Custom Components v2 with styling isolation; 1.60.0 made Vega charts use the native resize API.
- **Fonte:** https://docs.streamlit.io/develop/quick-reference/release-notes/2026 and https://discuss.streamlit.io/t/version-1-41-0/87521 (1.41.0 = 11 Dec 2024)
- **Porque funciona:** Every structural criticism in the brief — 'server-side rerun on every interaction', 'static', 'laggy' — describes Streamlit as it was in 2024. The 2026 releases specifically attack the full-script-rerun model (fragments that update arbitrary containers), the transport (ASGI), the serialisation (direct Polars→Arrow, bypassing pandas), and the blank-screen problem (`st.skeleton`). Judging the ceiling of 'Streamlit' from 1.41.1 measures the wrong thing.
- **Aplica-se aqui:** Directly, and the upgrade risk is unusually low for this codebase. I inventoried the API surface: 57 `st.markdown`, 20 `st.cache_data`, 19 `st.caption`, and only 3 `selectbox` / 3 `radio` / 2 `text_input` / 2 `button`. There are no exotic widgets, no `st.data_editor`, no custom components. The main breaking change in the window is widget **key-only identity** (progressive 1.50→1.55), which affects widgets that reset when parameters change — and this app already keeps navigation state in `st.query_params` (real URLs), which is the upgrade-safe pattern. The 20-test promotion gate in `tests/test_dashboard_v3.py` runs the app for real, so a regression surfaces immediately rather than silently.
- **Custo:** Hours to one day: bump the pin, run the 618-test suite plus the Playwright captures at 1920×1080 and 1366×768 that session 47 already established. Risk: low-to-moderate — 1.60.0 also carries breaking security changes to host-message and query-parameter handling, and this app leans on `st.query_params`, so test that path specifically. Do it on a branch with the `Procfile` still pointing at v3, so rollback is one line.
- **Veredicto:** adopt

#### The cold-start bottleneck is network, not compute — so a rewrite would inherit it unchanged

- **O que e:** I measured the suspected culprits on this machine: the 8.8 MB `backfill_kb.jsonl` (38,214 lines) reads raw in 0.07 s and fully `json.loads` parses in **0.30 s**; `import pandas` costs 0.97 s; `import plotly` costs 0.05 s; the pure presentation modules (`verdict`, `ui_tokens`, `tables`) import in 0.755 s. None of that accounts for a ~5.5 s cold load. Session 47's own profiling reached the same conclusion in different words: the cold-load bottleneck is *rede* (network), not calculation — the first detail view pays for `_alerts()` over the network plus SPY/XLK fetches, once per process.
- **Fonte:** Local measurement (this session) plus the project's own recorded finding in CLAUDE.md session 47, which also measured warm click median 0.75 s / cold 0.78 s in a real browser
- **Porque funciona:** Perceived latency is dominated by whatever sits on the critical path of the first paint. Here that is blocking third-party HTTP (yfinance, the alerts history over `raw.githubusercontent.com`), not Python execution and not the framework's rerun model.
- **Aplica-se aqui:** This is the single most important framing correction for the decision. Rebuilding in FastAPI + React would move the *rendering* off the server and change nothing about the network calls — the new stack would show a skeleton for the same ~5 s. The measured warm interaction is already 0.75 s, which is not the reported problem. Any plan that does not remove blocking network I/O from the request path is buying nothing, regardless of language.
- **Custo:** Zero — this is a diagnosis, not a change. Its value is negative: it disqualifies the two most expensive options.
- **Veredicto:** adopt

#### Precompute the 12-ticker snapshot to static JSON and serve it — the one change that actually removes the measured bottleneck

- **O que e:** A dashboard over a fixed watchlist of 12 tickers is almost entirely precomputable. The worker dyno already runs a 60-second cycle. Have it write a snapshot artefact (per-ticker verdict, z, exceedance count, decomposition, sparkline series, recent events) to disk/branch as JSON; the web dyno reads a local file instead of making blocking outbound calls. This is exactly the pattern Observable Framework formalises as **data loaders** — 'data loaders run at build time in any language, so your dashboard loads instantly for viewers … you don't need to run queries separately for each user on load' — but it needs none of Observable's tooling to adopt.
- **Fonte:** https://observablehq.com/framework/data-loaders and https://observablehq.com/blog/data-loaders-for-the-win; Streamlit static serving supports `.json`: https://docs.streamlit.io/develop/concepts/configuration/serving-static-files
- **Porque funciona:** It converts a per-visitor network round trip into a file read. The freshness budget is unchanged (the worker already cycles every 60 s), so nothing about the product's liveness claim weakens — the data is exactly as fresh, it just isn't fetched *while the user waits*.
- **Aplica-se aqui:** Perfectly. The watchlist is fixed at 12 and lives in `config/alerts.yaml`; the ranges are a small closed set; `detect_all` over a year costs 18.6 ms (session 47 measured it). Two cautions specific to this app: (1) Streamlit's static serving deliberately does **not** render HTML — anything other than the allowlisted types is sent as `text/plain` — so precompute to JSON, not to HTML pages; (2) the snapshot must be written by the same production code paths (`mature_entry`, `detect_all`) that the thesis evaluates, or the product starts describing a system the evaluation doesn't cover. The project already has the right instinct here from the backfill work.
- **Custo:** 1–2 days. Low risk if the snapshot path fails *open* — fall back to the current live fetch when the file is missing or stale, which is the failure mode this codebase already uses throughout. Biggest win per hour of any item in this list.
- **Veredicto:** adopt

#### Plotly ships ~2–3 MB of JavaScript; Lightweight Charts v5 is a 35 kB base bundle

- **O que e:** The full plotly.js bundle is ~6 MB unminified, just over 2 MB minified, and reportedly contributes 3 MB+ to production builds; even the 'basic' partial bundle is ~999 kB minified. TradingView **Lightweight Charts v5** reduced its bundle 16% to a **35 kB base bundle**, renders 10,000+ points at 60 FPS on canvas by avoiding DOM manipulation, and added multi-pane support. uPlot is the other credible option — canvas-based, ~45 kB, explicitly optimised for fast initial load.
- **Fonte:** https://github.com/plotly/plotly.js/blob/master/dist/README.md and https://community.plotly.com/t/plotly-js-size-is-huge-3mb-in-production-build/45407; https://www.tradingview.com/blog/en/tradingview-lightweight-charts-version-5-50837 and https://github.com/tradingview/lightweight-charts
- **Porque funciona:** Megabytes of JavaScript on the critical path is the most literal possible cause of 'not responsive enough' and 'static' — the page cannot become interactive until it parses. Swapping ~2 MB for ~35 kB is a straight subtraction from time-to-interactive, and canvas rendering makes pan/zoom feel native rather than re-rendered.
- **Aplica-se aqui:** With an important nuance: **the grid page doesn't need a charting library at all, and already doesn't use one.** `verdict.py` has a hand-rolled `sparkline_svg()` that emits inline SVG — zero JS. Plotly is only needed on the detail view (`st.plotly_chart` appears twice). So the swap is scoped to one screen. Lightweight Charts is the better fit than uPlot here because the domain is financial time series with event markers, which is precisely its design centre — and the existing `x unified` crosshair + `spikemode='across'` behaviour from session 47 maps onto its native crosshair.
- **Custo:** 2–4 days via a Streamlit custom component. Real risk: the detail view's news markers, the three-layer event overlay (sent / detected-but-gated / news), and the filterable events table are genuinely non-trivial to reimplement, and session 47 already found a factor-of-100 formatting bug in that area. Do it only after the upgrade and the precompute, and only if the detail view still feels slow — which, at 0.75 s warm, it may not.
- **Veredicto:** adapt

#### The presentation layer is already framework-independent — this is the project's cheapest insurance policy

- **O que e:** `app/verdict.py`, `app/ui_tokens.py`, `app/tables.py` and `app/method.py` contain **zero Streamlit imports**. `card_html()` and `sparkline_svg()` are pure functions returning HTML/SVG strings. `dashboard.py` is a thin shell that pushes them through 46 `unsafe_allow_html=True` calls.
- **Fonte:** Direct inspection of this repository (C:\Users\henri\Desktop\DIMEIA\app\)
- **Porque funciona:** The usual reason a Streamlit migration costs months is that the UI is expressed *in* Streamlit widget calls, so nothing survives the move. Here the opposite is true: the UI is already HTML produced by testable pure Python, and Streamlit is only acting as transport plus runtime. Session 46 built it this way on purpose — 'a law you can only check by opening a browser is an intention'.
- **Aplica-se aqui:** Two consequences, and they point in opposite directions. First, it means the eventual migration to FastAPI + templates or a static generator is perhaps 10× cheaper than a typical Streamlit escape, because `card_html()` can be called from a build script or a Jinja template essentially unchanged — that is real optionality worth stating in the thesis as a design outcome. Second, and more immediately, it means **Streamlit is not what makes the app feel static** — the markup is already hand-written and would look identical served any other way. That weakens the case for re-platforming as a fix for the stated complaint.
- **Custo:** Zero — it already exists. Worth naming explicitly in Chapter 4 as an architectural property (presentation logic testable without a browser), since it is both a defensible engineering decision and the thing that de-risks any future move.
- **Veredicto:** adopt

#### FastAPI + HTMX/Alpine is the right Track B and the wrong Track A

- **O que e:** A FastAPI + HTMX + Alpine first visit is roughly 55–65 kB total: one HTML document (~15 kB gzipped), CSS (~8 kB), HTMX (~16 kB, cached), Alpine (~15 kB, cached), page JS (~4–8 kB). No hydration delay. Server-sent events via `StreamingResponse` + `hx-swap` are straightforward. The acknowledged cost: 'no component ecosystem — you're building the UI from scratch in HTML, which becomes slow work for complex dashboards with many interactive panels.'
- **Fonte:** https://devtoolswatch.com/en/htmx-vs-react-2026 and https://blakecrosley.com/guides/fastapi-htmx
- **Porque funciona:** For a content-heavy page with moderate interactivity — which is exactly what a 12-card grid is — HTMX genuinely delivers better perceived performance than either Streamlit or a SPA, because there is no hydration step and the payload is an order of magnitude smaller.
- **Aplica-se aqui:** The engine (`investigator/`) is already an installable library with a clean API, and the presentation layer already emits HTML, so the technical fit is unusually good. But the deadline is 13 September and seven redesigns have already been rejected on aesthetic grounds with no stopping condition. Rebuilding the shell means re-earning the 20-test promotion gate, re-capturing Figure 4.5, re-syncing Chapter 4 in **both** EN and PT, and re-doing the slides and study guide — the project's own session-48 record shows that documentation debt is the expensive half of any product change here. Also note it does not fix the measured bottleneck (network), so the headline complaint could survive the rewrite.
- **Custo:** 2–4 weeks realistically, plus bilingual thesis churn. Unacceptable risk profile six weeks out. Revisit after submission — it is the natural Track B, and the codebase is already shaped for it.
- **Veredicto:** reject

#### React / Svelte / SolidJS SPA — buys nothing here that HTMX doesn't, at higher cost

- **O que e:** A client-side SPA moves rendering to the browser and adds a build toolchain, a hydration step, and a JS bundle. The 2026 consensus is that islands or MPA beat SPA for dashboards where 'the shell, layout, headers and sidebar navigation don't change' — full SPA is reserved for canvas editors, collaborative spreadsheets, real-time multiplayer, or dashboards where 'every panel updates and nothing is ever just text that stays still'.
- **Fonte:** https://merge.rocks/blog/is-single-page-application-dead-in-2025-spas-vs-mpas-vs-islands and https://www.patterns.dev/vanilla/islands-architecture/
- **Porque funciona:** It doesn't, for this shape of problem. The InvestiGator grid is 12 mostly-static cards plus one chart on a secondary screen — the content-to-interaction ratio is exactly the case the sources say islands/MPA win.
- **Aplica-se aqui:** Actively wrong for this project. A SPA adds a Node build step to a Python dissertation whose reproducibility story ('one command') is a stated academic asset, introduces a second language for a solo student who is not an IA specialist and must defend every component, and the project rule is 'simplicidade defensável > sofisticação'. It also cannot be justified to a jury as engineering necessity when the measured warm interaction is 0.75 s.
- **Custo:** 4–8 weeks plus a permanent maintenance and defensibility burden. No.
- **Veredicto:** reject

#### Observable Framework / Evidence.dev / Quarto — steal the idea, not the tool

- **O que e:** Observable Framework is a static site generator for data apps: data loaders run at build time in any language (Python included) and generate static snapshots; page loaders 'pre-bake' dynamically generated pages into static Markdown so content exists on page load rather than waiting for JavaScript. Everything is handled client-side, removing server-side processing. Evidence.dev is SQL-query-driven with Markdown pages; Quarto is document-first, where 'dashboards are just an add-on' versus being Observable's core focus.
- **Fonte:** https://observablehq.com/framework/data-loaders, https://observablehq.com/framework/page-loaders, https://evidence.dev/blog/business-intelligence-tools, https://quarto.org/docs/dashboards/interactivity/observable.html
- **Porque funciona:** The precompute-at-build-time model is genuinely the right mental model for a fixed 12-ticker dashboard, and it is why these tools feel instant — there is no server work on the request path at all.
- **Aplica-se aqui:** The *idea* transfers completely and is captured in the precompute finding above. The *tools* do not. Observable would put the presentation layer in JavaScript while the engine, the retrieval over ~38k news items, the precedent lookup and the 60-second refresh remain Python — splitting a solo dissertation across two languages six weeks before submission. Evidence.dev assumes a SQL warehouse this project doesn't have. Quarto is the closest cultural fit (academic, reproducible, already a LaTeX-adjacent workflow) but its dashboards are a secondary feature and it would not deliver the live 60 s refresh. Adopting any of them also orphans the 20-test promotion gate that currently enforces the H1/H2/V-series acceptance criteria against a running app.
- **Custo:** 3–5 weeks and a second language in the stack. Reject the tools; the precompute finding already banks the benefit at a fraction of the price.
- **Veredicto:** reject

#### Skeleton states and streaming render — now first-class in Streamlit via st.skeleton

- **O que e:** Skeleton screens that mimic the layout of the final content reduce perceived wait times and provide a sense of structural stability; optimistic updates 'trick the brain into perceiving the interface as faster than the underlying API execution layer'. Streamlit 1.59.0 (July 2026) added **`st.skeleton`** as a loading placeholder primitive, and 1.58.0 added `parallel=True` fragments for concurrent execution.
- **Fonte:** https://wearepresta.com/performance-first-ux-2026-architecting-for-revenue-and-speed/ and https://docs.streamlit.io/develop/quick-reference/release-notes/2026
- **Porque funciona:** A ~5 s cold load spent staring at nothing reads as broken; the same 5 s spent watching the page's real structure fill in card-by-card reads as loading. The measured time is unchanged — the interpretation of it is not. This is the highest-leverage response to 'old-school and static' precisely because the underlying number is network-bound and hard to shrink below a floor.
- **Aplica-se aqui:** Directly, and it is the closest thing to a free win. The grid is 12 independent cards whose skeleton is trivially derivable from the existing CSS grid (the explicit 4/3/2/1 column ladder from session 47). Pair with `parallel=True` fragments so the 12 snapshots resolve concurrently rather than serially — the current `_grid_live` builds `linhas` in a sequential comprehension over `_snapshot(t)`, which is the obvious candidate. Both require the version upgrade first, which is another reason the upgrade is the gating move.
- **Custo:** 1 day after the upgrade. Very low risk — purely additive, and the failure mode is the current behaviour.
- **Veredicto:** adopt

#### Prefetch and speculation rules — Google measured 60–80% median LCP reduction on prerendered navigations

- **O que e:** Speculation Rules preload or prerender likely next pages in the background while the user is still on the current page, 'so when the navigation fires there's essentially nothing to wait for'. Google's own measurements show **median LCP drops of 60–80% on prerendered navigations** across a representative sample of commerce and news sites.
- **Fonte:** https://dev.to/aomuiz/instant-pages-with-speculation-rules-the-secret-to-lightning-fast-web-navigation-1b37 and https://webperfclinic.com/article/view-transitions-api-smooth-page-transitions-perceived-performance
- **Porque funciona:** It exploits the gap between when intent becomes predictable (hover, or simply 'this is one of only 12 possible destinations') and when the click happens — typically several hundred milliseconds, which is enough to hide most of a warm navigation.
- **Aplica-se aqui:** Unusually well, because the destination set is *tiny and known*: from the grid there are exactly 12 possible detail pages plus the method page. That is a rare case where naive eager prerendering is actually defensible rather than wasteful. Session 47 validated keeping real URLs for navigation, which is the precondition — speculation rules operate on document navigations, so this only works because the project chose URLs over `session_state`. That decision now pays a second dividend. Caveat: Streamlit serves an SPA shell, so cross-document prerendering may not apply cleanly to intra-app navigation; verify before committing, and treat hover-triggered cache warming of the detail snapshot as the fallback that definitely works.
- **Custo:** Half a day for hover-warm the cache; low risk. Full speculation rules depend on how Streamlit handles the query-param navigation — measure before believing.
- **Veredicto:** adapt

#### View Transitions — real, but keep it under 300 ms or it hurts the metric it's meant to help

- **O que e:** The View Transitions API gives GPU-accelerated crossfades between states without a framework. But 'even a 300 ms GPU-accelerated crossfade can feel slow if the new page hasn't loaded yet — you end up transitioning into a skeleton or spinner', and transitions should be kept under 300 ms because longer ones block interaction and inflate INP (Interaction to Next Paint, an official Core Web Vital since March 2024).
- **Fonte:** https://webperfclinic.com/article/view-transitions-api-smooth-page-transitions-perceived-performance and https://www.debugbear.com/blog/view-transitions-spa-without-framework
- **Porque funciona:** Motion that preserves object identity between two states removes the 'did something break?' beat that a hard cut produces. It is a large part of what 'cool UX/UI' means in practice versus 'old-school and static'.
- **Aplica-se aqui:** Applies to the grid→detail transition, which is the app's main navigation and currently a hard cut. The card could morph into the detail header. But the sources are explicit that this only helps when paired with prerender/prefetch — transitioning into a skeleton is worse than not transitioning. So it is strictly downstream of the precompute and prefetch work, not a substitute for it. Purely CSS/JS, so it survives any stack decision.
- **Custo:** 1 day, additive, degrades gracefully in unsupporting browsers. Do it last, after the thing it transitions *into* is fast.
- **Veredicto:** adapt

#### Custom Components v2 — the no-iframe escape hatch that makes 'stay on Streamlit' credible

- **O que e:** Custom Components v2 is 'a complete reimagining of how components work': **no iframe isolation** — components are part of the Streamlit page rather than sandboxed — plus multiple callbacks per component and both stateful and event-based values. Styling isolation improvements landed in 1.56.0 (March 2026).
- **Fonte:** https://docs.streamlit.io/develop/concepts/custom-components/overview and https://docs.streamlit.io/develop/quick-reference/release-notes/2026
- **Porque funciona:** The historical reason Streamlit apps look and feel dated is that anything custom was trapped in an iframe — it couldn't inherit the page's theme, couldn't size to content, and every interaction crossed a sandbox boundary. Removing the iframe removes the main structural reason a Streamlit app cannot look bespoke.
- **Aplica-se aqui:** This is what makes option 1 a real answer rather than a holding position, and it is the delivery mechanism for the Lightweight Charts swap. It also retroactively explains a session-47 finding: `st.dataframe` was rejected partly on theme-collision grounds, and the note honestly records that the theme risk turned out to be hypothetical. With v2 that class of problem largely disappears. Requires the upgrade first.
- **Custo:** Included in the chart-swap estimate. Note it needs a JS build step for the component, which is the one place a Node toolchain legitimately enters the project — scoped to a single component rather than the whole shell.
- **Veredicto:** adapt

#### Virtualised lists, service workers and optimistic UI — correctly inapplicable here

- **O que e:** Three widely-recommended 2026 perceived-speed techniques that do not fit this product. Virtualised lists pay off in the hundreds-to-thousands of rows. Service workers add offline caching and a background update lifecycle. Optimistic UI renders the assumed result of a mutation before the server confirms.
- **Fonte:** https://www.alphonsolabs.com/frontend-performance-trends-2026/ and https://shubhra.dev/tutorials/performance-first-ui-mastery-guide-2026
- **Porque funciona:** They work in their proper domains — long feeds, offline-capable PWAs, and write-heavy apps respectively.
- **Aplica-se aqui:** None of them. The grid is **12 cards**, so virtualisation would add machinery and complexity to render fewer items than fit on one screen; the events table is at most 64 rows in a 6M window (session 47 measured 64=64). Service workers add a cache-invalidation surface to an app whose entire value proposition is data freshness on a 60-second cycle — stale-while-revalidate is the wrong default when the user is asking 'is this move unusual *today*'. Optimistic UI needs mutations to be optimistic *about*, and this application is read-only by design: it has no writes, no portfolio, no holdings (cut deliberately on RGPD/MiFID II grounds in session 42). Listing these as rejected matters because they will otherwise reappear in every generic 'make it fast' checklist.
- **Custo:** N/A — the value is in not spending the time. Naming why they don't apply is itself defensible engineering judgement for the viva.
- **Veredicto:** reject

#### Memory: the 512 MB dyno has already caused one production OOM, and any option must respect it

- **O que e:** The project has prior art here: session 44 recorded an R15 with **1.4 GB on a 512 MB dyno**, crash-looping the worker, traced not to the framework but to `run_alerts` embedding all new headlines in a single batch on a fresh machine with an empty pending file. Separately, one documented FastAPI case cut base RAM from ~140 MB to ~48 MB purely by lazy-loading pandas and matplotlib. Streamlit on Heroku has a known pattern of memory growing and not being released.
- **Fonte:** https://medium.com/@bhagyarana80/optimizing-fastapi-for-low-memory-footprint-on-microservices-6bf756f5fe8f, https://discuss.streamlit.io/t/streamlit-memory-issue/79675, and this project's own session-44 record
- **Porque funciona:** On a 512 MB box the framework's baseline is a meaningful fraction of the budget, and Python's import graph is the largest lever — a single unnecessary top-level import of matplotlib or sklearn can cost tens of megabytes for the whole process lifetime.
- **Aplica-se aqui:** Two concrete checks. First, `matplotlib==3.11.0` and `scikit-learn` are in the base `requirements.txt` and are installed on the web dyno; matplotlib is only needed for thesis figures. I verified the presentation modules import cleanly without pulling matplotlib, torch or sklearn — so the separation currently holds, but it holds by luck rather than by a test, and one careless import would regress it silently. Second, session 47's fix of `_retrieval_kbs` from `cache_data` to `cache_resource` (the former was storing a serialised 19.4 MB copy) is exactly the class of bug that recurs under memory pressure. A cheap guard: a test asserting the web entrypoint's import graph excludes matplotlib/torch/sklearn — the same 'verify it fails without the fix' discipline session 46 already established.
- **Custo:** Half a day for the import-graph guard test. Relevant to every option, which is why it belongs in the decision rather than after it.
- **Veredicto:** adopt

---

## Ideias por explorar

*Padroes que o produto podia usar, sujeitos a nao-previsao e ao criterio H4.*

### Sintese

The student's verdict — "too laggy, too zoomed out, static" — has three distinct causes, and only one of them is visual. LAG is architectural: the measured 5.5 s cold load is per-render network fan-out (yfinance, GitHub raw, model loads), not Streamlit widgets; session 47 already proved warm navigation is 0.75 s. The fix is to make rendering a read of one precomputed snapshot the 60 s worker already has the data to write. ZOOMED OUT is the missing cross-section: 12 companies exist but are only ever seen one at a time, so the product's second question ("is it this company or the whole market?") is never answered at watchlist scale — a shared-axis dot plot of all 12 against SPY and the sector marks fixes it in a day. STATIC is mostly the absence of addressable state: no deep links, no keyboard path, no brushing, no way to rewind. Beyond fixing those, the genuinely unusual capabilities are already sitting in computed data with no view attached: the gate log records why each ticker was silenced and by what margin (four failed by ≤0.04) — that is a Screener page, and no commercial product shows it; the exceedance count is a picture waiting to be drawn as a GitHub-style year of dots, which simultaneously makes quiet days informative; and the news corpus is small enough to ship to the browser as Parquet and explore with DuckDB-WASM at zero dyno cost. Two things must be refused with reasons: a semantic map of the corpus (the project's own silhouette of 0.084 says the structure is not there) and a chat assistant (the narrator red team's 29 holes say the honesty surface is not closeable in five weeks). One correction to the brief, verified by counting the file: the 38,214 news items carry only 3,143 distinct (ticker, day) outcome measurements, because impact is measured per ticker-day and every headline that day shares it — any explorer must say so or it overstates the evidence.

### As tres recomendacoes principais

1. Precompute the whole grid into one snapshot artefact the worker writes every 60 s, so page render is a file read with zero network calls (Observable Framework's data-loader principle). This is the actual fix for 'laggy' — the cost is fan-out per render, not the UI framework — and it unblocks nearly everything else, because a fast stateless page can be static HTML instead of a Streamlit rerun. 1–2 days.

2. Give the 12 companies a single screen: a shared-axis dot plot of today's moves with SPY and sector-ETF reference marks, plus a GitHub-contribution-style calendar of the last 249 days per ticker. Together they answer 'is it just me?' at watchlist scale and turn the empirical exceedance count from a sentence into a picture you can count — which also makes quiet days informative instead of empty. ~2 days for both, no new computation.

3. Build the gate funnel as a Screener page: every ticker silenced today, the plain-words reason, and the margin it missed by ('best match 0.42, floor 0.45'). Gmail's 'Why is this message in Spam?' applied to financial alerts. The data is already recorded in gate_log.py; nothing commercial shows this, it is the strongest possible 'permission to do nothing' for the anxious holder, and it is the most distinctive screen in the product for the defence. 1–2 days.

### Achados (18)

#### Render becomes a file read: precompute the whole grid into one snapshot artefact

- **O que e:** The worker (already on a 60 s cycle) writes a single `snapshot.json` containing everything the 12 cards need — price, z, exceedance count, decomposition, verdict sentence, volume ratio, last news day. The web dyno's job on page load is: read one local file, paint. No yfinance fan-out, no raw.githubusercontent fetch, no model load at render time. Live-ness comes from the file's timestamp, shown honestly ("as of 14:32:05, 47 s ago").
- **Fonte:** Observable Framework data loaders (https://observablehq.com/framework/data-loaders) — the explicit design principle is "precompute static snapshots of data at build time… dashboards load instantly with no external dependency on your database". Same pattern as Next.js ISR and Grafana's recorded queries.
- **Porque funciona:** The obvious fix for "too laggy" is to optimise the UI framework. That is the wrong layer. The measured cold load of ~5.5 s is network fan-out per render, not widget rendering — session 47 already proved this by measuring warm navigation at 0.75 s median and finding the 1.8 s spike was a once-per-process cost. Moving the fan-out off the render path converts an N-network-call page into a zero-network-call page. It also removes the 512 MB dyno's worst behaviour: every visitor currently re-does work the worker already did 40 seconds ago.
- **Aplica-se aqui:** Twelve tickers is small enough that the entire snapshot is a few KB — this is the rare case where full precomputation is trivially affordable. It also fixes something worse than lag: right now two visitors 10 seconds apart can see different numbers, because each render re-fetches. A snapshot makes the page deterministic and the Telegram channel, the dashboard and the thesis figure all read the same artefact. It further unblocks nearly every other idea in this list, because a fast, stateless, file-backed page can be rendered as static HTML instead of a Streamlit rerun.
- **Custo:** 1–2 days. Low risk: additive, the current live path can stay as fallback when the snapshot is stale. Risk to name honestly: a stale snapshot must fail loudly (show its age), never silently serve yesterday's numbers — that is exactly the class of silent-wrong defect this project keeps catching.
- **Veredicto:** adopt

#### The watchlist cross-section: all 12 in one screen, ranked by how unusual today was

- **O que e:** A single strip at the top of the grid: 12 dots on a shared axis of today's return, each labelled, with SPY and the relevant sector ETF drawn as reference marks. A second row shows the same 12 ranked by exceedance rank ("5 of 249" … "203 of 249"). One glance answers: is my stock alone, or is everything red today?
- **Fonte:** FINVIZ S&P 500 map (https://finviz.com/map) for the at-a-glance market cross-section; the small-multiples/dot-plot form rather than a treemap follows Cleveland & McGill's position-on-common-scale ranking.
- **Porque funciona:** The obvious alternative is FINVIZ's treemap, but a treemap sizes by market cap, which for a fixed 12-name watchlist encodes nothing the user cares about and wastes the most accurate visual channel. A dot plot on a shared axis puts every company on one common scale, so "is it just me?" is answered by proximity, and the SPY mark makes the market-wide answer literally visible rather than stated in words.
- **Aplica-se aqui:** This is the single largest structural gap the brief names: 12 companies exist but are viewed one at a time. It is also the cheapest possible answer to question 2 ("is it this company or the whole market?") at watchlist scale — the decomposition already computes market and sector contributions per ticker, so the reference marks are real computed numbers, not decoration. And it makes the deliberate XOM/JNJ addition pay off visibly: on a tech-selloff day, ten dots cluster left and two sit right.
- **Custo:** 1 day. Pure rendering over data the snapshot already carries. No new computation.
- **Veredicto:** adopt

#### A year in 249 dots: the exceedance count drawn instead of stated

- **O que e:** Per ticker, a calendar strip of the last ~249 trading days as small squares, shaded by |z| (or by absolute move), with today outlined. The sentence "only 5 of the last 249 trading days moved this much" becomes a picture where you can count the five dark squares. Twelve of these stacked is an instant cross-company comparison of temperament: TSLA's year looks visibly stormier than JNJ's.
- **Fonte:** GitHub's contribution calendar (github.com profile heatmap) — the canonical proof that a year of one metric fits in a thumbnail and a lay audience reads it without a legend.
- **Porque funciona:** The obvious alternative is the sentence alone. But the project already discovered (session 48) that the sentence and the z-score can disagree, and that a lay reader has no way to arbitrate. A calendar makes the distribution itself visible, so the claim is auditable by eye: the user sees that most squares are pale, which is precisely what "an ordinary day" means. It also solves the quiet-day emptiness problem without inventing content — a pale year IS the content.
- **Aplica-se aqui:** Directly renders `investigator/anomaly_detector/frequency.py`, already computed and already trusted enough to appear on the card. n comes from the data, so the picture cannot drift from the number. It also makes the honest correction from session 48 legible instead of paradoxical: a day can be pale by recent standards yet in the darkest 2% of the year, and the two rulers can be shown side by side.
- **Custo:** 0.5–1 day. Static SVG, no interactivity needed in v1. Hover for the date/return is a cheap upgrade.
- **Veredicto:** adopt

#### The gate funnel as a Screener: what was suppressed, why, and by how little

- **O que e:** A page (deep-linkable) listing every ticker the scanner silenced today, each with the reason in plain words and the number that caused it: "MSFT — no strong enough precedent (best match 0.42, floor 0.45)", "AAPL — the triage model scored 0.43, below 0.50". Near-misses are grouped first, with the margin shown as a tiny bar. A Sankey or stacked bar summarises the day: 12 scanned → 9 died here → 2 there → 1 alert.
- **Fonte:** Gmail's "Why is this message in Spam?" banner (a per-item reason attached to every suppressed item) and HEY's Screener (hey.com), which makes the rejected pile a first-class, browsable place rather than a hidden filter.
- **Porque funciona:** Every commercial alerting product shows only its wins. Showing the suppressions inverts the usual trust argument: instead of asking the user to believe the filter is good, it shows the filter working and lets them audit it. The near-miss framing is what makes it interesting rather than plumbing — "four of today's twelve failed by 0.04" is a genuinely arresting fact, and it is the exact measurement session 42 recorded (MSFT 0.42 · NFLX 0.41 · GOOGL 0.44 · META 0.44 vs a 0.45 floor).
- **Aplica-se aqui:** `investigator/gate_log.py` already records stage plus the number that justified the stop, in the exact shape this page needs, and already writes in dry-run. The data exists; only the view is missing. For the long-term holder this is the strongest possible "permission to do nothing": the system says out loud that it looked at your twelve names and deliberately said nothing about nine of them, and shows its arithmetic. For the defence it is the most distinctive screen in the product.
- **Custo:** 1–2 days. The one design risk: it must read as confidence, not apology. Lead with "9 of 12 were quiet enough to ignore", not "9 alerts blocked".
- **Veredicto:** adopt

#### Ship the measured-outcome corpus to the browser: Parquet + DuckDB-WASM, with linked brushing

- **O que e:** A single ~1–2 MB Parquet file of the news corpus (headline, ticker, date, +1/+3/+5 d measured impact) loaded into DuckDB compiled to WebAssembly. The user filters by ticker, date range, or a text match on the headline, and the outcome distribution, the calendar and the headline list all update together, instantly, with zero server calls.
- **Fonte:** DuckDB-Wasm (https://motherduck.com/blog/duckdb-wasm-in-browser/) — SQL over Parquet fully client-side, no backend; and Mosaic vgplot (built on Observable Plot + DuckDB), which provides `Selection.crossfilter` for linked, coordinated views over millions of rows in the browser.
- **Porque funciona:** The obvious alternative — a server-side search page — is exactly what a 512 MB dyno cannot afford, and is why the retrieval panel already costs seconds. Pushing the corpus to the client turns the dyno's hardest page into its cheapest: after one download, every filter is sub-100 ms and costs the server nothing. Linked brushing is what makes it exploration rather than a search box: brushing a date range on the calendar filters the headlines and the outcome distribution simultaneously, which is how a person actually asks "what was going on that week?".
- **Aplica-se aqui:** `data/samples/backfill_kb.jsonl` is 8.7 MB of JSON, 38,214 rows, already versioned and already read by the app — as Parquet with dictionary encoding on ticker/date it will be roughly a tenth of that. ONE HONESTY FLAG, verified by counting: those 38,214 headlines carry only 3,143 distinct (ticker, day) outcome measurements, because impact is measured per ticker-day and every headline on a day shares it. The explorer must say "3,143 measured ticker-days, 38,214 headlines attached" or it will overstate the evidence — the same unit-of-analysis error session 42 caught in the policy sweep.
- **Custo:** 3–4 days for a good version (2 for a plain filter table without Mosaic). Needs a build step to emit Parquet and a JS island in the page — this is the point where Streamlit stops helping.
- **Veredicto:** adopt

#### Decomposition as a bridge chart, not three signed numbers

- **O que e:** One horizontal bar that starts at zero, is pushed by market, then sector, then company, and lands exactly on today's return. Each segment labelled in words ("the market pulled you down 1.7%", "the company itself added 0.2%"). The whole thing is an identity: the segments sum to the total, visibly.
- **Fonte:** The waterfall / bridge chart, standard in financial variance analysis (Tableau, Datawrapper and Excel all ship it as a named chart type); the arithmetic is the two-factor decomposition in `investigator/correlation_engine/decomposition.py`.
- **Porque funciona:** The obvious alternative is what the thesis's own D2′ amendment rejected: three signed percentages on the card. With 12 companies that is 36 competing signed numbers at first contact. A bridge is one shape, and it exploits the fact that this particular decomposition is exact — the parts genuinely add to the whole, so the picture is not a metaphor, it is the equation. A lay reader who cannot parse "β-adjusted sector contribution" can see a bar being pushed left by the market and nudged right by the company.
- **Aplica-se aqui:** Turns the project's best live example into something a non-specialist reads in a second: AMZN −1.84% = −1.66% market · −0.37% sector · +0.19% company — the stock fell but its own contribution was positive. That is the single most valuable sentence in the product for the anxious long-term holder, and today it is three numbers behind a click.
- **Custo:** 1 day. Pure rendering; the numbers exist. Keep it behind the click as D2′ requires — the card names the driver in words, the bridge is what you get when you open it.
- **Veredicto:** adopt

#### Deep links: every view is a URL, including a date

- **O que e:** `?ticker=NVDA&range=6M&date=2026-05-13&panel=precedents`. Back/forward work. Any state a user reaches can be pasted into Telegram, an email to a supervisor, or a thesis footnote, and reopens exactly.
- **Fonte:** Datasette (datasette.io) — Simon Willison's design rule that every view, filter and facet is addressable by URL; Grafana encodes time range and variables in the URL for the same reason.
- **Porque funciona:** The obvious alternative, session state, makes the product unshareable and unciteable. URL state costs almost nothing and buys three things at once: sharing, browser history as free navigation, and — uniquely valuable here — a stable citation for the thesis and the defence, so Figure 4.5 can be regenerated from a link rather than a click sequence.
- **Aplica-se aqui:** Already half-built: `?view=method` exists, and session 47 measured warm navigation at 0.75 s and explicitly validated keeping real URLs over `session_state` buttons. This just finishes the job. It is also the precondition for the command palette and for time travel — both are only useful if a target state has an address.
- **Custo:** 0.5 day for the remaining parameters. Streamlit's `st.query_params` handles it.
- **Veredicto:** adopt

#### "Since you last looked" — the digest for the person who visits rarely

- **O que e:** On open: "You were last here 23 days ago. Since then: 3 unusual days across your 12 names (NVDA twice, XOM once), 9 alerts sent, and 218 of 249 ticker-days were unremarkable." Each item is a link into the relevant day. Last-visit timestamp lives in browser localStorage.
- **Fonte:** Reddit's "new since last visit" markers, GitHub's unread-notification model, and Feedly's unread counts — the established pattern for a feed consumed at irregular intervals.
- **Porque funciona:** The obvious alternative is a fixed "today" view, which serves the active investor and abandons the long-term holder — who by definition opens the page after weeks and has no way to catch up. This is the only feature in the list that is designed for absence rather than attention, and it directly serves the persona whose most valuable output is permission to do nothing: a summary dominated by "218 of 249 unremarkable" is that permission, quantified.
- **Aplica-se aqui:** Needs no new computation — the alert history and the replay of `detect_all` over the interval already produce every number. localStorage means zero server state, no accounts, and no personal data leaving the browser, which is consistent with the project's stated privacy position (logos are embedded as data URIs precisely so the browser makes no third-party requests).
- **Custo:** 1 day. Degrades cleanly to "first visit" when storage is empty.
- **Veredicto:** adopt

#### Precedent outcomes as a dot strip, never as a forward cone

- **O que e:** Each retrieved precedent is a dot on a horizontal ±% axis at its measured +5 d outcome, coloured by direction, with the case's company and similarity on hover, and a median tick. Above it, one sentence: "4 comparable past headlines; 3 of 4 were followed by falls; median −1.9%. This describes those four cases, not this one."
- **Fonte:** The dot-plot-over-bar-chart convention (Cleveland & McGill; Datawrapper's own guidance on showing individual values when n is small) applied to the event-study outcome format.
- **Porque funciona:** The obvious alternative is a bar of the mean, which is actively misleading at n = 3–5: it hides that the cases disagree, which is precisely the finding the thesis case study CS3 rests on (a positive headline retrieving a cluster of falls, because retrieval captures theme, not direction). Dots make disagreement the visible feature rather than an averaged-away detail. CRITICAL: it must be drawn as points to the LEFT of, or on, a day-0 origin — a fan or cone opening to the right of today reads as a forecast to every finance-literate viewer and would breach the founding constraint in pixels while the caption denies it in words.
- **Aplica-se aqui:** `_precedent_panel` already retrieves cases with real similarity and measured +1/+3/+5 d outcomes and already carries `verdict.precedent_framing`. This is a rendering change to the panel that most needs one, since a table of four rows is the least legible way to show four numbers on one scale.
- **Custo:** 1 day. The design risk is entirely in the geometry, not the code — get a second pair of eyes on whether it reads as prediction.
- **Veredicto:** adopt

#### Time travel: replay what the dashboard said on any past day

- **O que e:** A date field (and a scrubber on the chart) that rewinds the entire grid to a chosen trading day: the cards, the verdicts, the exceedance counts, the alerts that fired and the ones that were suppressed, all as of that date. Explicitly labelled "replaying 13 May 2026" with a way back to live.
- **Fonte:** TradingView's Bar Replay (https://www.tradingview.com/chart/BTCUSD/qmCyeQyK-How-To-Use-The-Bar-Replay-Tool-Rewatch-Trading-History/) — the mainstream, well-understood interaction for stepping a chart back in time while hiding future data.
- **Porque funciona:** The obvious alternative is a static screenshot in the thesis. Replay makes the anti-lookahead discipline demonstrable instead of asserted: the examiner can pick a date and watch the system judge it using only prior data. TradingView's version exists for backtesting a strategy; here it exists for auditing a claim, which is a better use of the same mechanic and one no retail dashboard offers.
- **Aplica-se aqui:** The machinery exists and was built for exactly this: `detect_all` replays the same no-lookahead z-score over every day of a series, `backfill_kb.jsonl` holds 351 days of measured outcomes, and the alert history is dated. The main work is threading an `as_of` date through the render path and being ruthless that nothing reads a value dated after it — a single leak here is the classic lookahead bug and would be worse than not shipping the feature.
- **Custo:** 3–4 days, most of it correctness work and tests. Ship it read-only, no playback animation in v1 — animation is demo, the date jump is utility.
- **Veredicto:** adapt

#### Command palette and keyboard-first navigation

- **O que e:** ⌘K / Ctrl-K opens a fuzzy-searchable palette: type "nvda" to jump to the card, "quiet" to filter, "suppressed" to open the screener, "13 may" to time-travel. `j`/`k` move between companies, `?` shows the shortcut sheet, `Esc` returns to the grid.
- **Fonte:** cmdk (https://github.com/pacocoursey/cmdk) — the Vercel-authored React component used by Linear, Vercel, Raycast and Sourcegraph; ~5 kB, headless, keyboard-driven.
- **Porque funciona:** The obvious alternative — more buttons — costs screen space and still requires the user to know where things live. A palette makes every destination reachable in three keystrokes without teaching a hierarchy, and it is the single most reliable signal of a 2026-modern product to anyone who has used Linear or Raycast. It is also the natural pairing for deep links: the palette navigates, the URL records.
- **Aplica-se aqui:** With 12 companies plus a handful of views, the whole command surface is maybe 30 entries — small enough that fuzzy matching is trivially good and there is no ranking problem to solve. HONEST CAVEAT: this fights Streamlit's rerun model. A key-capture component that triggers a full server rerun on every keystroke will feel worse than no palette. It is only worth building on top of the snapshot architecture (finding 1) with a static/JS front end, or not at all.
- **Custo:** 2 days on a JS front end; do not attempt as a Streamlit custom component bolted onto the current rerun path. Flag: on its own this is polish, not utility — its value is that it makes the other capabilities reachable.
- **Veredicto:** adapt

#### Linked brushing between the chart, the event table and the news list

- **O que e:** Drag to select a range on the price chart; the event table, the news list and the precedent panel all filter to that window, and the header restates it ("11 sessions, 3 flagged, 18 news days"). Clicking a row in the table highlights its mark on the chart.
- **Fonte:** Crossfilter / coordinated views, as formalised in Mosaic vgplot's `Selection.crossfilter` and Observable's linked-brushing guide (https://observablehq.com/blog/linked-brushing).
- **Porque funciona:** The obvious alternative is separate range selectors on each panel, which lets them drift out of agreement — the exact failure the project already engineered against by having `_chart` return the window it drew so the tables consume it. Brushing extends that guarantee to the user's own selection: one gesture, one truth, no way for the chart and the table to disagree.
- **Aplica-se aqui:** Half the invariant is already built and already paid for. What is missing is the gesture. It also fixes a real navigation cost: getting from "something happened around mid-May" to the specific headlines currently means changing an interval preset and hunting a table.
- **Custo:** 2–3 days, and effectively free if the DuckDB/Mosaic explorer (finding 5) is built, since crossfilter comes with it. Not worth it as a bespoke Plotly callback chain inside Streamlit.
- **Veredicto:** adapt

#### Compare mode — but compare decompositions, not prices

- **O que e:** Select 2–4 companies; get a shared-axis overlay. The default overlay is NOT rebased price (which every site has) but the market/sector/company split side by side for the same day or window: "on 12 May, the market explained most of NVDA's move and almost none of XOM's".
- **Fonte:** Rebased-to-100 comparison is standard at Google Finance and stockanalysis.com/stocks/compare/; the differentiating layer is the project's own two-factor decomposition with Vasicek beta shrinkage.
- **Porque funciona:** A rebased price overlay is a commodity — it is on every free finance site and adds nothing to the three questions. Comparing decompositions answers a question no consumer product answers: not "which went up more" but "whose move was actually about the company". That is the same question the product already answers per ticker, extended to the axis it is currently missing.
- **Aplica-se aqui:** The XOM/JNJ addition exists precisely so the sector factor varies; comparison is where that investment cashes out. Live example already observed: XOM −0.98% while its sector was +0.93% — the sector pulling the other way — is only striking next to a tech name where the sector explained everything.
- **Custo:** 1–2 days once the cross-section (finding 2) exists. Keep the selection in the URL so a comparison is shareable.
- **Veredicto:** adapt

#### "You Draw It": make the user guess the rarity before revealing it

- **O que e:** On a flagged day, before showing the exceedance count, offer one optional interaction: "How many of the last 249 trading days do you think moved at least this much?" — the user drags a slider or draws on the calendar strip, then the true count and the real distribution are revealed against their guess.
- **Fonte:** The New York Times "You Draw It" series (2015–2017, e.g. "What Got Better or Worse During Obama's Presidency"); productised by Flourish as the "Draw the Line" chart type (https://flourish.studio/blog/draw-the-line-chart/).
- **Porque funciona:** The documented effect is that making a reader commit to a guess before the reveal makes them remember the true value — the format exists because passive reading of a statistic does not stick. Here the statistic being taught is the one concept the whole product rests on and that a lay user has no intuition for: how rare a 4.8% day actually is for this particular stock. It is also entirely retrospective, so it cannot be mistaken for a forecast.
- **Aplica-se aqui:** Perfect fit for the non-professional audience and for the thesis's stated position that the z-score means nothing to a lay reader while a count means everything. STRONG CAVEAT — this is the one entry closest to demo: it must be opt-in and once-per-concept, never a gate in front of the answer. An anxious holder on a red day who is made to play a quiz before being told what happened will not come back. Ship it on the method page first, where teaching is the point, and only then consider it in the flow.
- **Custo:** 2 days. Flag honestly: high delight, medium utility, real annoyance risk if placed wrong.
- **Veredicto:** adapt

#### Cross-company precedents: "this also happened to your other holdings"

- **O que e:** In the precedent panel, separate the retrieved cases into "from this company" and "from elsewhere in your watchlist", and say so: "3 comparable cases from AMD, 1 from NVDA — the theme travels across the sector."
- **Fonte:** The project's own retrieval behaviour, documented live in session 47: the headline "AMD Has an Agentic AI Advantage Over Nvidia" returned 3 AMD cases and 1 NVDA case, all downward.
- **Porque funciona:** The obvious presentation is one undifferentiated ranked list, which hides the most interesting property of semantic retrieval — that it crosses tickers. Surfacing the split turns a search result into an observation about the market: the same theme has hit several of your names before. It is also the honest way to show that similarity is thematic, which is the setup for the theme ≠ direction warning the panel already carries.
- **Aplica-se aqui:** Zero new computation — the ticker is already on every retrieved case, it is simply not used as a grouping. It uses the 12-name watchlist as an asset rather than a limitation, and it gives the long-term holder something genuinely new: a correlation observation across positions, stated as history, not as risk.
- **Custo:** 0.5 day. Grouping and one sentence.
- **Veredicto:** adopt

#### Worker-generated share cards (Open Graph images) for alerts

- **O que e:** When an alert is sent, the worker also renders a small PNG of that card — logo, verdict sentence, the move, the exceedance count — and the Telegram/link preview unfurls to it. The image is a static file; the link under it is a deep link to the live day.
- **Fonte:** The OG-image pattern popularised by Vercel's `@vercel/og` and GitHub's per-repository social preview images.
- **Porque funciona:** The obvious alternative is a bare URL in a Telegram message, which unfurls to nothing and gets ignored. A card that carries the verdict sentence means the alert is legible before the click, which serves the active investor's "context arrives with the alert" requirement even inside the notification. It is also, incidentally, how the thesis figures should be produced — from the same renderer as the product, so they cannot drift.
- **Aplica-se aqui:** Cheap because the layout already exists as HTML and Playwright is already installed and already used by `scripts/screenshot_app.py`. Caveat worth stating: this is distribution polish, not one of the three questions — rank it below everything above.
- **Custo:** 1–2 days including making the worker render headlessly on a 512 MB dyno, which is the part that could bite. If memory is tight, render at most one card per cycle.
- **Veredicto:** adapt

#### REJECT: a 2D semantic map of the news corpus

- **O que e:** The tempting version: UMAP/t-SNE the ~38k headline embeddings into a scatter, colour by cluster, let the user roam the 'landscape of news' and click regions to see outcomes.
- **Fonte:** The pattern itself is well established (Nomic Atlas, TensorFlow Embedding Projector). The reason to refuse it is internal: `docs/evaluation/evaluation_event_taxonomy.md` — silhouette 0.084, AMI event 0.358 vs ticker 0.188, and the explicit finding that the taxonomy is NOT fit to drive retrieval.
- **Porque funciona:** It does not. It looks spectacular and is the most demo-ish idea available. A map draws visual boundaries between clusters, and a viewer reads those boundaries as real structure. This project measured that structure and found it weak — so the map would assert with pixels what the evaluation refuses to assert with numbers.
- **Aplica-se aqui:** It is also functionally adjacent to the already-banned event-type badges, and it would fail criterion H4 ("no score the measurement does not support") in spirit if not in letter. Worth writing down as a considered rejection with the number attached, because it is the idea a reviewer or examiner is most likely to suggest — and having refused it, with the measurement, is a stronger position than never having thought of it.
- **Custo:** Would be 3–5 days. The cost of shipping it is worse: a defence question with no good answer.
- **Veredicto:** reject

#### REJECT (for this timeline): a conversational assistant over the data

- **O que e:** The 2026-obvious move: a chat box — "why did NVDA drop last Tuesday?" — answering from the decomposition, the precedents and the corpus.
- **Fonte:** The pattern is everywhere (Perplexity Finance, Bloomberg's BloombergGPT work). The reason to refuse it here is internal: the narrator red team, where a 3-adversary pass found 29 holes in a blocklist design and forced an inversion to a closed ~360-word allowlist, with 21 exploits kept as permanent regressions.
- **Porque funciona:** It would be genuinely useful, and the project is unusually well placed to do it safely — the allowlist verifier already exists and delivered 0 violations across 36 live calls. But free-form conversation re-opens the whole surface: an open-ended answer cannot be validated against a fixed evidence set the way a one-sentence alert can, and a lay user cannot audit a fluent paraphrase. The failure mode is not a wrong number, it is a plausible sentence that quietly predicts.
- **Aplica-se aqui:** Against a 13 September deadline with seven redesigns already rejected, this is the one idea that can consume the remaining time and end in a feature that must be turned off before the defence. The right move is to name it as future work with the allowlist cited as the reason it is tractable later — which is a stronger thesis statement than a half-built chatbot.
- **Custo:** Realistically 2+ weeks to do safely; unbounded to do honestly. Flag as demo-over-utility for this deadline.
- **Veredicto:** reject


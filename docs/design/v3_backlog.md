# v3_backlog.md — o que falta no painel, e porque

> **Estatuto: EXECUTADO (A, B, C, D, E + watchlist), 2026-08-03.** Quatro commits sobre
> `663919f`. Restam os dois itens de fundo (passos 6 e 7 da v3) e **duas correcções de
> dados que dependem de chaves de API**, listadas em §Estado abaixo.
>
> `app/dashboard.py` continua a ser a v3 construída **ao lado**; o `Procfile` continua a
> servir `app/streamlit_app.py` (v1), **intocada**. Promoção continua a ser uma linha, e
> continua por fazer.
>
> Veredicto do aluno sobre a v3: *"almost perfect"* — a estrutura e a funcionalidade estão
> aceites (*"I like the organization and functionality of it. it's perfect"*). O que faltava
> era densidade, legibilidade, e uma capacidade nova (tabela de eventos filtrável).

---

## Estado, item a item (2026-08-03)

| Item | Estado | Nota |
|---|---|---|
| **A1** pílula fora da linha do nome | ✅ | linha própria; "JPMorgan Chase" deixou de truncar |
| **A2** corpo de letra maior | ✅ | veredicto/nome 12,5→14 px, chips 10→11, corpo do detalhe com eles |
| **A3** margens laterais | ✅ | `max-width` 1680→1920 px |
| **A4** grelha 4×3 deliberada | ✅ | escada explícita 4/3/2/1 com `minmax(0, 1fr)` |
| **A5** "voltar" no topo | ✅ | estava no fim da página, depois de tudo o que fecha |
| **B** "what is this?" | ✅ | `verdict.FLAG_EXPLAINER`, com testes; abre pela consequência |
| **C1** mira / coluna de hover | ✅ | `x unified` + `spikemode="across"` |
| **C2** mais rápido | ⚠️ **medido, ganho pequeno** | ver §Medições |
| **D1** tabela = janela do gráfico | ✅ | `_chart` devolve a janela; chart e tabela lêem a mesma lista |
| **D2** filtros + paginação | ✅ | `app/tables.py`, puro, 30 testes |
| **E** lentidão da navegação | ✅ **premissa não se confirma** | ver §Medições |
| **watchlist 12** | ⚠️ **código feito, dados por fazer** | XOM/JNJ sem logótipo e sem notícias |
| **passo 6** precedentes | ✅ **com emenda V6′** | lista no detalhe; contagem no cartão custava 7,5 s |
| **passo 7** página do método | ✅ | `?view=method`; fecha o buraco que o B abriu |

### Medições (Playwright, browser real, não logs)

| O quê | Antes | Depois |
|---|---|---|
| Grelha a frio | 5,45 s | 5,46 / 5,49 / 6,20 s (3 corridas) |
| Troca de intervalo (1.ª) | ~0,90 s | ~0,67 s |
| Troca de intervalo (repetida) | ~0,65 s | ~0,65 s |
| Clique num cartão — **frio** | — | mediana **0,78 s** |
| Clique num cartão — **morno** | — | mediana **0,75 s** |
| 1.º detalhe da sessão (uma vez por processo) | — | ~3,0 s |

**O passo E não precisou de código, e isso é um resultado.** O plano fixava "se um clique
morno ainda passar de ~1,5 s, reconsiderar os botões". Não passa: a mediana é **0,75 s**. O
1,8 s que aparecia na medição anterior era o **primeiro** detalhe da sessão — o parse dos
7,8 MB de `backfill_kb.jsonl`, mais o `_alerts()` pela rede, mais SPY/XLK para a
decomposição — tudo partilhado por todos os tickers e pago **uma vez por processo**, não
por clique. Atribuí-lo a "navegação" era medir a coisa errada. A decisão de **manter os
URLs reais** fica portanto validada por medição, e não só por preferência.

A segunda alínea do E (garantir que as caches são `st.cache_data` e não `session_state`) já
estava satisfeita: as dez funções de dados são todas `@st.cache_data`, e o `session_state`
só guarda número de página e assinatura de filtros — que é estado de interface, e é
precisamente onde deve estar.

**O C2 também não deu o que eu ia escrever.** Ia registá-lo como ganho de velocidade;
medido, `detect_all` custa 18,6 ms sobre um ano contra 1,0 ms sobre 30 dias, portanto a
diferença é ruído ao pé do resto. O ganho real está na primeira troca de intervalo
(~0,90 → ~0,67 s). O estrangulamento da carga a frio é **rede**, não cálculo.

### O que falta, e de que depende

1. **Dois comandos numa máquina com chaves** (não é código — é o `.env`, que não existe
   nesta máquina). Sem eles, XOM e JNJ ficam meio-construídos ao lado dos outros dez:
   `python scripts/fetch_logos.py` (`POLYGON_API_KEY`) e
   `python scripts/backfill_history.py --months 12` (`FINNHUB_API_KEY`).
   Medido hoje: XOM e JNJ têm **0** registos de notícia; os outros dez têm 2.424–5.632.
2. **Promoção** — uma linha no `Procfile`. Depois dela abre a dívida de sincronizar a tese
   EN/PT + slides + guia e recapturar a Fig 4.5 (ver "Still outstanding"). A tese está
   consistente **hoje** porque a v1 é o que está no ar; a dívida é criada pela promoção,
   não pela reconstrução.

## Context

`app/dashboard.py` (v3) is built alongside the deployed `app/streamlit_app.py` (v1). v1 is
still what the `Procfile` serves; promotion is one line. The student's verdict on v3 is
"almost perfect", with a specific, actionable list. Nothing here is a rewrite — v3's
structure and functionality are explicitly signed off ("I like the organization and
functionality of it. it's perfect"). This is density, legibility and one genuinely new
capability (a filterable event table).

Two decisions taken this round, binding:

- **Watchlist grows to 12 with two non-tech names.** Nine of the current ten share one
  sector ETF, so the market/sector/company decomposition almost always gives the same
  answer to "is it the sector?". Adding sectors is a *thesis* improvement, not just a
  layout one.
- **Navigation keeps real URLs.** Cards stay links (`?t=NVDA` shareable, back button
  works); the lag gets fixed by making the reload cheap, not by abandoning deep links.

---

## The two questions answered

### Should the repo go private?

**Keep it public until after submission.** Three concrete reasons, in order of weight:

1. **It would silently break the app.** Both apps fetch history from
   `raw.githubusercontent.com` **unauthenticated** (`_raw()` in `app/dashboard.py`, and
   `alerts_history.fetch_remote`). Private → those URLs 404 → and because those paths
   *fail open by design*, the app would show an empty history with **no error at all**.
   Fixable by authenticating with the `GITHUB_TOKEN` already in Heroku config vars, but
   that is a code change plus a new failure mode to test.
2. **Actions minutes.** Public repos get unlimited; private gets 2,000 min/month, which the
   alerts cron consumes. That cron is the fallback for when Heroku is down.
3. **It does not solve the thing it feels like it solves.** The exposed credentials are in
   git *history*; making the repo private hides them from strangers but does not revoke
   them. **Rotation is still required either way** — see the pending list.

There is no academic reason to be private: `scripts/make_public_bundle.py` already exists to
produce a clean public release, and the thesis carries no repo URLs.

### Streamlit Community Cloud or Heroku?

**Heroku, and the reason is specific to this project rather than generic.**

Session 31 recorded a real, measured incident: on Streamlit Cloud's **shared IPs, yfinance
gets rate-limited**, which made the price column come back all-`None` and crashed a page.
That is this app's primary data source on every render. Add that Community Cloud
**hibernates** when idle (a cold visitor waits ~30 s — bad for a defence demo) and runs on
shared CPU.

Heroku Basic never sleeps and has its own IP. Keep Streamlit Cloud deployed as the free
fallback — it costs nothing and reads the same data branch — but Heroku is primary.

*Cost note, unchanged and worth revisiting:* both apps read the same `alerts-history`
branch, so data freshness comes from the **worker**, not the web dyno. Dropping the Heroku
*web* dyno and serving the UI from Streamlit Cloud would halve the burn ($7 vs $14/mo,
stretching $312 from ~22 to ~44 months) at the cost of hibernation. Not recommended before
the defence.

---

## The work, in priority order

### A. Legibility and density (the loudest complaints)

**A1 — "UNUSUAL" hides the company name.** The pill sits inside `.card-top`, competing for
a row that also holds logo, name, ticker and the big number. Move the state pill **out of
that row**: either onto the left border as a coloured bar with the word dropped entirely,
or onto its own line above the verdict. The company name must never truncate.
Files: `app/ui_tokens.py` (`card_css`), `app/verdict.py` (`card_html`).

**A2 — bigger type throughout.** The scale was tuned for a dense terminal and is too small
for a non-specialist. Raise one step: verdict 12.5→14 px, chips 10→11 px, card name
12.5→14 px, and the detail view's body text with it. Keep `tabular-nums`.

**A3 — reclaim the side margins.** `.block-container` is at `1.1rem` horizontal with
`max-width: 1680px`. On a wide screen there is still visible dead space at the edges.
Reduce horizontal padding and raise or drop `max-width`, verified by screenshot at
1920×1080 and 1366×768.

**A4 — 12 cards in a deliberate 4×3.** With 12 tickers, replace `auto-fit`/`minmax` with an
explicit responsive ladder so the grid lands on clean rows rather than whatever fits:
4 columns ≥1280 px, 3 ≥900 px, 2 ≥600 px, 1 below. No orphan row of one.

**A5 — "back to all companies" goes top-left**, above the detail header, where a back
control belongs. It is currently at the bottom of the page.

### B. "What is this?" is still confusing

The tooltip explains the *mechanism* (standard deviations, 20-day window) to someone who did
not ask for it. Replace with a plain two-line answer that leads with the consequence, not
the statistic — roughly: *"Flagged means today's move is unusually large for this company,
compared with its own recent behaviour. Each company is judged against itself, so 3% can be
flagged for a calm stock and ordinary for a volatile one."* Threshold and window move to the
method page, one link away.

Must not violate **H1** (the promise appears exactly once). Add the sentence as a constant
in `app/verdict.py` so it is testable alongside the existing wording tests.

### C. The chart: faster and navigable

**C1 — hover column / crosshair.** Plotly does this natively: `hovermode="x unified"` plus
`xaxis.showspikes=True`, `spikemode="across"`, `spikethickness=1`, `spikecolor=T.LINE`.
`app/streamlit_app.py` already does something similar — read it before writing new code.

**C2 — faster.** Two cheap wins before anything clever: raise `st.cache_data` TTLs on the
price frame, and stop recomputing `_replay` on every range change (it currently recomputes
over the whole series each time). Measure cold load and range switch with Playwright
timings rather than guessing.

### D. The event table (the one new capability)

**D1 — the table must show what the chart shows.** `_news_panel` currently shows 6 rows,
deduplicated to one per day, regardless of the range on screen. It must be driven by the
same window as the chart, so every marker on the chart has a row in the table.

**D2 — pagination and per-column filtering** for both the event table and the alerts list:
filter by date range, by text in the description, by move magnitude/direction; sortable by
column.

Implementation note: `st.dataframe` gives sorting and column config for free and is far less
code than hand-rolled HTML — but it brings Streamlit's own theming, which is exactly the
class of bug behind the dark-on-dark problem. **Verify its rendering against the dark theme
by screenshot before committing to it.** If it fights the theme, fall back to a hand-built
table with `st.selectbox`/`st.slider` filters above it.

### E. Navigation lag (decision: keep URLs)

Keep anchors; make the reload cheap:

- Render the detail header and chart *before* fetching precedents/news, so the page paints
  early (`st.empty()` placeholders filled in afterwards).
- Ensure every cross-request cache is `st.cache_data`/`cache_resource` (process-global, so
  it survives a page load) rather than `session_state` (which does not).
- Measure before and after; if a warm click still exceeds ~1.5 s, revisit the buttons option.

---

## Still outstanding from earlier (do not lose these)

- ~~**v3 step 6:** precedents rendered~~ — **FEITO (2026-08-03)**, com a emenda **V6′**
  (contagem no cartão fora, por custar 7,5 s na página de entrada). A lista está no
  detalhe, em `_precedent_panel`, com o desfecho medido e a moldura tema ≠ direcção.
- ~~**v3 step 7:** the method page~~ — **FEITO (2026-08-03)**, `?view=method`. Traz também
  a casa que faltava ao limiar e à janela depois do passo B, e `app/method.py` amarra cada
  número congelado ao `.md` que o produziu, com testes que partem se um valor mudar.
- **After promotion only:** coordinated thesis EN/PT + slides + guide sync, recapture
  Fig 4.5, then the parity checks. The thesis is *currently consistent* because v1 is what
  is deployed — this debt is created by promotion, not by the rebuild.
- **Human, unblockable by me:** rotate the three exposed credentials (GitHub PAT first — it
  carries `admin: true`, far wider than the write access it needs), send the PT-PT message
  at `docs/defence/mensagem_orientador.md`, claim a Student Pack domain for a clean URL.

---

## Entrega de turno — 2026-08-03, fim da sessão 47

**Onde isto ficou.** Tudo commitado e pushed (`5dcb77c`), árvore limpa, 594 testes verdes,
ruff limpo, congelados byte-iguais. **A v1 continua a ser o que está no ar e não foi
tocada.** A v3 está funcionalmente completa.

**Em que máquina.** Esta sessão correu no **portátil** (`C:\Users\ruifa`), que **não tem
`.env`** — daí os dois comandos por correr. A próxima sessão é no **desktop**, que é a
máquina do FNSPID (`C:\Users\henri`, a do cabeçalho dos congelados) e tem os dados e o
torch. Confirmar lá se existe `.env`; se não existir, é o `heroku config -s` abaixo.

### A fazer, por ordem

**1. Chaves — primeiro, porque desbloqueia o resto.**

```bash
heroku login                                        # browser, não precisa da chave antiga
heroku config -s --app investigator > .env          # o cofre devolve as 8
```

Depois disto, correr os dois comandos que fecham o buraco de dados dos dois nomes novos
(medido: XOM e JNJ têm **0** registos de notícia; os outros dez têm 2.424–5.632, e nenhum
dos dois tem ficheiro de logótipo):

```bash
python scripts/fetch_logos.py                       # POLYGON_API_KEY
python scripts/backfill_history.py --months 12      # FINNHUB_API_KEY
```

**2. Rodar as três credenciais expostas** — PAT do GitHub **primeiro** (tem `admin: true`,
muito mais largo do que o acesso de escrita de que precisa), ALPHAVANTAGE, e a chave da API
do Heroku **por último**. Cada uma actualizada em **dois** sítios: `heroku config:set` e
GitHub → Settings → Secrets → Actions. Guardar uma cópia num gestor de senhas: se a app do
Heroku for apagada, o cofre vai com ela.

> **Nota que vale a pena não perder:** os *GitHub Secrets* **não se lêem de volta** — são
> de escrita apenas, por desenho. Há maneira de os imprimir num workflow, e **não se faz**:
> este repositório é público e isso escreveria as chaves em registos visíveis a toda a
> gente. O cofre legível é o Heroku.

**3. Promover, ou não.** É uma linha no `Procfile`
(`app/streamlit_app.py` → `app/dashboard.py`). **A decisão é do aluno**, e o que ela custa
está na secção seguinte.

---

## Promoção: a lista exacta do que fica por rever na tese

> Isto **não** é dívida da reconstrução — é dívida **da promoção**. Enquanto a v1 estiver no
> ar, a tese está correcta como está. No minuto em que o `Procfile` mudar, os textos abaixo
> passam a descrever um ecrã que já não existe, e isso é exactamente o tipo de coisa que um
> arguente encontra.

**O que a tese afirma hoje sobre o painel e deixa de ser verdade com a v3:**

| Ficheiro | O quê | Porque deixa de bater |
|---|---|---|
| `thesis/ch4/chapter4.tex` (~378–410) | "one screen each"; a lista "carries the market/sector/company split **on the row itself**, so a reader learns whether a fall was the market or the company **without a click**" | A v3 é uma **grelha de cartões**, e a repartição em três números está a **um clique** (emenda **D2′**): o cartão nomeia o motor **em palavras**. A frase actual afirma o contrário. |
| `thesis/ch4/chapter4.tex` (legenda da Fig. 4.5) | Descreve linhas concretas: Amazon −1,84% com +0,19% da empresa, JPMorgan | A captura tem de ser refeita e a legenda reescrita à volta do que a nova mostrar. |
| `thesis-pt/ch4/chapter4.tex` (~387–419) | O mesmo, traduzido | **Regra de sincronia bilingue**: muda numa, muda na outra, no mesmo sítio. |
| `thesis/figures/app_dashboard.png` | A figura | `scripts/screenshot_app.py` aponta para `app/streamlit_app.py` — **tem de passar a apontar para `app/dashboard.py`**. A `thesis-pt` partilha a figura via `graphicspath`, portanto flui sozinha. |
| `slides/main.tex`, `slides/main-pt.tex`, `slides/guia_estudo/main.tex` | Usam a mesma figura | Actualizam sozinhos quando o PNG mudar; **verificar o texto à volta** de cada um. |
| `thesis/ch5/chapter5.tex` | Menciona o painel | Ler e confirmar se alguma afirmação depende da forma antiga. |

**O que CONTINUA verdade na v3 e não precisa de ser tocado** (verificado): a promessa e o
compromisso de não prever aparecem **uma** vez, no topo; a latência é medida a partir de
carimbos reais e está **ausente** quando eles não existem; os alertas são lidos do registo
partilhado e **não** recalculados.

**Portas a passar depois de mexer:** as duas teses compilam a 0 erros, 0 citações/refs
indefinidas; **paridade EN↔PT** (mesmo número de secções e de ambientes figure/table, por
capítulo); slides e guia compilam; números congelados intactos.

---

## Verification

Every step ends green or it does not land:

- `pytest` (537 currently) and `ruff check .` clean.
- `git status --porcelain models/ docs/evaluation/evaluation_{triage,results,anomaly}.md`
  empty — frozen artefacts byte-identical.
- **Rendered screenshots, not logs.** Every visual claim here must be verified by Playwright
  screenshot at 1920×1080 *and* 1366×768. This project has repeatedly shipped bugs invisible
  in logs: a 200 health check on a page that was entirely an error; dark text on dark
  panels, twice; 253 `(None, None, None)` boxes painted over a chart.
- New wording (B) gets a test in `tests/test_verdict.py`, where the H2 no-prediction sweep
  already runs over 112 generated combinations.
- Watchlist change (12 tickers) also requires `scripts/fetch_logos.py` for the two new
  logos and a `scripts/backfill_history.py` run for their year of news, or they will look
  half-built next to the other ten.
- v1 (`app/streamlit_app.py`) stays deployed and untouched throughout.

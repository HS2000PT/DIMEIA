# going_live.md — Pôr o InvestiGator a funcionar 24/7 (grátis)

> Duas coisas: (1) uma **webpage sempre disponível** (o dashboard) e (2) **alertas no telemóvel**
> (um canal de Telegram + um temporizador). **Sem servidor** para gerir. Tudo grátis.
>
> Eu (código) já deixei tudo pronto; tu fazes os passos que precisam da tua conta (criar o canal,
> definir 3 segredos, publicar o dashboard). São cliques, não consola.

## Mapa mental (o que já existe / o que falta)
| Peça | Ficheiro (feito) | Falta (humano) |
|------|------------------|----------------|
| Webpage 24/7 | `app/streamlit_app.py` | **publicar** no Streamlit Cloud |
| Alertas agendados | `scripts/run_alerts.py` + `.github/workflows/alerts.yml` | **canal + 3 segredos** |
| Definições (watchlist, limiares) | `config/alerts.yaml` | editar à vontade |

> **Não há** (nem precisa nesta fase) um servidor sempre ligado. O temporizador do GitHub acorda,
> corre a varredura, envia, e desliga. Um servidor "a ouvir" só é preciso na **Fase B** (bot interativo).

---

## Fase A — ao vivo, grátis, sem servidor

### 1) Criar o canal do Telegram
1. No Telegram: **New Channel** → público → dá-lhe um nome (ex.: *InvestiGator Alerts*) e um `@username`
   (ex.: `@investigator_alerts`).
2. Abre o canal → **Manage channel → Administrators → Add Administrator** → adiciona o **teu bot**.
3. O "id do canal" para enviar: usa o `@username` (`@investigator_alerts`) — é o mais simples. (Alternativa:
   o id numérico `-100…`, obtido reencaminhando uma mensagem do canal para o `@userinfobot`.)

### 1b) Onboarding do canal (1 clique: afixar a mensagem)
Canais do Telegram **não têm** "mensagem de boas-vindas" a novos membros (limitação da
plataforma) — o padrão certo é a **mensagem afixada** + a descrição. Copia/cola:

**Mensagem para afixar (Manage channel → depois afixa-a):**
> 🐊 **InvestiGator — explainable market alerts** (research tool, not advice)
> • Posts are **automatic**: abnormal market moves (checked every 30 min during US market
>   hours) and material news for the watchlist — each alert shows its full reasoning
>   (z-score / historical precedents).
> • Want **your own** watchlist? DM the bot: `/watch TSLA` · `/list` · `/stop`
>   (replies within ~30 min).
> • Live dashboard: <https://investigator-ddc9d8618935.herokuapp.com>
> • Everything is **evidence from the past** — never a forecast, never financial advice.

**Descrição do canal (Manage channel → Description):**
> Explainable US-market alerts, automated: abnormal moves + material news, each with its
> reasoning. Not advice. Dashboard: investigator-ddc9d8618935.herokuapp.com

### 2) Definir os segredos no GitHub (nunca no código)
Repo → **Settings → Secrets and variables → Actions → New repository secret**:
| Nome | Valor |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | o token do `@BotFather` |
| `TELEGRAM_CHAT_ID` | `@investigator_alerts` (ou `-100…`) |
| `FINNHUB_API_KEY` | só se ligares o gatilho de notícias (opcional) |
| `TIINGO_API_KEY` | **preços (2026-07-13):** conta grátis em tiingo.com — o 1.º fallback quando o Yahoo bloqueia os runners (foi a causa real de 0 alertas de mercado) |
| `POLYGON_API_KEY` | idem, polygon.io (2.º fallback; opcional mas recomendado) |
| `ALPHAVANTAGE_API_KEY` | a chave que já tens no .env (último recurso, 25/dia) |

### 3) Testar já (botão manual)
Repo → **Actions → "Alerts (scheduled scan)" → Run workflow**. Vê o log; se houver anomalia hoje, a
mensagem chega ao canal (e ao telemóvel de quem estiver no canal).
> Antes de definires os segredos, o job **corre na mesma e fica verde** — só não envia nada. Sem erros vermelhos.

### 4) O temporizador (já configurado — INTRADIÁRIO, zero-ops)
Corre **de 30 em 30 minutos durante o horário de mercado US** (cron `0,30 13-21 * * 1-5`, UTC),
mais a varredura de fecho. O runner lembra-se do que **já alertou hoje** (estado em
`data/alerts_state.json`, persistido entre corridas pela cache do Actions) — a mesma anomalia ou
manchete **nunca repete** no mesmo dia. Os **comandos do bot** (`/watch`…) também são processados
em cada corrida (resposta em ≤30 min; para respostas imediatas corre `scripts/run_bot.py`).
Muda em `.github/workflows/alerts.yml`.
> Notas honestas: o cron do GitHub é **UTC** e **best-effort** (pode atrasar alguns minutos); e **pausa
> após 60 dias sem atividade** no repo (qualquer commit volta a armá-lo).

**Histórico partilhado (sync com a app, 2026-07-08).** Cada alerta REALMENTE enviado fica registado
(`investigator/alerts_history.py`) e publicado numa branch de dados só para isso — **`alerts-history`**
(nunca a `main`, para não sujar a história do código/tese) — via um passo dedicado do workflow
(checkout à parte + commit + push; por isso o workflow tem `permissions: contents: write`, só para
essa branch). A app Streamlit lê esse ficheiro ao vivo (raw.githubusercontent.com, cache de 60s) —
nunca recalcula. A MESMA branch carrega a **KB viva** (`live_pending.jsonl` +
`live_kb.jsonl`): cada manchete relevante vista pelo scan vira precedente dias depois, com o
impacto real medido a +5d — é o que permite precedentes de 2026 em vez de só 2018-2023.
Fail-open total: se o checkout ou o push falharem, o runner e o envio ao Telegram
continuam normalmente, só o histórico partilhado fica por publicar dessa vez.

### 5) Escolher o que é vigiado (e a qualidade dos alertas)
`config/alerts.yaml`: a **watchlist** (`tickers`), a `window` e o `threshold` do z-score; e ligar/desligar
o gatilho de notícias. Sem segredos aqui. **Botões de qualidade das notícias (2026-07-11):**
`news.min_similarity` (chão: sem UM precedente com cosseno ≥ este valor, não há alerta),
`news.max_per_ticker_per_day` (teto anti-fadiga), e o filtro de relevância
(`investigator/news_fetcher/relevance.py` — a manchete tem de mencionar a empresa; boilerplate
de mercado é rejeitado; edita os aliases lá se mudares a watchlist). O canal também envia um
**resumo diário ao fecho** (1 msg ≥21h UTC) e corre aos fins de semana (só notícias).

**Triagem aprendida (opcional, off por defeito).** Se definires `news.min_materiality` (ex.: `0.4`),
cada alerta de notícia é pontuado pelo modelo treinado só-contexto (`models/triage_context_lr.joblib`,
corre na stack leve) e só é enviado se P(movimento anormal) ≥ esse valor; o alerta passa a incluir a
linha de materialidade ("triage evidence, not a forecast"). Sem o ficheiro do modelo, o gate é ignorado
com aviso — o runner nunca fica vermelho por causa da triagem.

**Loop de pós-validação (M5.5) — agora zero-ops.** Com o gatilho de notícias ligado, o runner
regista cada decisão em `predictions_log.jsonl`. Desde 2026-07-22 esse log vive na **branch
partilhada `alerts-history`** (não em `data/` gitignored), por isso PERSISTE entre corridas do
Actions e ACUMULA na nuvem. Ao **fecho** (≥21 UTC), o workflow corre `scripts/post_validate.py`:
rotula as decisões maturadas com o que REALMENTE aconteceu (janela (d, d+3] fechada, preços via a
cadeia de fallback) e regenera `live_monitoring.md` na mesma branch — a app pública mostra-o em
*"How our alerts are doing"*. Localmente continuas a poder correr `python scripts/post_validate.py`
à mão (escreve `docs/evaluation/live_monitoring.md`). Enquadramento honesto: é **monitorização**
do mecanismo de triagem (precisão das mantidas vs base rate, Brier), não avaliação nem previsão.

### 6) A webpage (painel único) sempre disponível
Publica `app/streamlit_app.py` no **Streamlit Community Cloud** — passos em
[`deployment.md`](deployment.md). Uma grelha com um cartão por empresa, os mesmos alertas
do canal, e o detalhe a um clique.
Depois cola o URL no `README.md` e na tese.
*(Opcional: uma página GitHub Pages a ligar o dashboard + o canal, com um domínio grátis do Student Pack.)*

### Experimentar na tua máquina (sem enviar)
```bash
pip install -r requirements.txt
python scripts/run_alerts.py --dry-run
```
Varre a watchlist com preços ao vivo e **imprime** os alertas (não envia). Corre na stack leve (sem torch).

---

## Fase B — bot interativo por utilizador ✅ CONSTRUÍDA (versão sem servidor)

**Já funciona, de graça e sem host**: o bot usa *long-polling*
(`getUpdates`), por isso corre em qualquer máquina atrás de NAT — não precisa de webhook nem de
servidor público.

> **Nota de durabilidade (honesta):** no modo zero-ops, a base de subscritores vive na
> **cache do GitHub Actions** — sobrevive entre corridas (é tocada todos os dias úteis), mas a
> cache é *best-effort* (LRU/7 dias sem uso podem despejá-la). Para durabilidade a sério, o
> passo seguinte é o host+BD da "evolução futura" abaixo.
>
> **Nota (um consumidor de cada vez):** com o processamento EM LOTE do Actions ligado
> (`bot.enabled: true` — o defeito atual), **não corras o `run_bot.py` ao mesmo tempo**: o
> Telegram só permite um consumidor `getUpdates`. Se acontecer, o runner apanha o erro e segue
> (fail-open), mas as respostas ficam baralhadas entre os dois. Escolhe um modo.

**Como ligar (2 passos):**
1. `python scripts/run_bot.py` (ou duplo-clique em `archive/streamlit-app/run/bot.bat`, ou a tarefa VS Code
   "Bot interativo"). Requer `TELEGRAM_BOT_TOKEN` no `.env`. Qualquer pessoa pode então falar com
   o bot: `/start`, `/watch TSLA`, `/unwatch TSLA`, `/list`, `/stop`, `/help`. As subscrições
   ficam em `data/bot_users.db` (SQLite, stdlib, gitignored).
2. Em `config/alerts.yaml`, põe `bot.enabled: true` — o runner agendado passa a entregar cada
   alerta TAMBÉM aos subscritores desse ticker (fan-out **fail-open**: sem base ou com erro, o
   runner comporta-se como sempre, só canal).

**Produto responsável (implementado):** limite de 20 tickers por utilizador (fadiga de alertas),
validação sintática dos tickers, `/stop` reversível (pausa sem apagar a watchlist), respostas
sempre com a moldura "evidência do passado, nunca previsão"; nenhum segredo sai do `.env`.

**Evolução futura (quando houver host):** webhook em vez de polling num host do Student Pack
(Fly.io/Render/DigitalOcean $200, Azure $100), a mesma base SQLite num volume pequeno (ou
MongoDB Atlas free) e um agendador no host (APScheduler) — o código atual já separa a
interpretação pura dos comandos (`investigator/telegram_bot/commands.py`) do transporte, por
isso a troca polling→webhook não mexe na lógica.

---

## Segurança & custos (honesto)
- **Fase A é grátis:** repo público ⇒ minutos do Actions grátis; Streamlit Community Cloud grátis.
- **Segredos** só em GitHub Secrets / `.env` local — **nunca** no repositório.
- **Não é conselho financeiro:** os alertas **explicam** eventos com evidência do passado; não preveem preços.

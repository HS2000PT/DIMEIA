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

### 2) Definir os segredos no GitHub (nunca no código)
Repo → **Settings → Secrets and variables → Actions → New repository secret**:
| Nome | Valor |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | o token do `@BotFather` |
| `TELEGRAM_CHAT_ID` | `@investigator_alerts` (ou `-100…`) |
| `FINNHUB_API_KEY` | só se ligares o gatilho de notícias (opcional) |

### 3) Testar já (botão manual)
Repo → **Actions → "Alerts (scheduled scan)" → Run workflow**. Vê o log; se houver anomalia hoje, a
mensagem chega ao canal (e ao telemóvel de quem estiver no canal).
> Antes de definires os segredos, o job **corre na mesma e fica verde** — só não envia nada. Sem erros vermelhos.

### 4) O temporizador (já configurado)
Corre **segunda a sexta, ~após o fecho dos EUA** (cron `30 21 * * 1-5`, em UTC). Muda em
`.github/workflows/alerts.yml`.
> Notas honestas: o cron do GitHub é **UTC** e **best-effort** (pode atrasar alguns minutos); e **pausa
> após 60 dias sem atividade** no repo (qualquer commit volta a armá-lo).

### 5) Escolher o que é vigiado
`config/alerts.yaml`: a **watchlist** (`tickers`), a `window` e o `threshold` do z-score; e ligar/desligar
o gatilho de notícias. Sem segredos aqui.

**Triagem aprendida (opcional, off por defeito).** Se definires `news.min_materiality` (ex.: `0.4`),
cada alerta de notícia é pontuado pelo modelo treinado só-contexto (`models/triage_context_lr.joblib`,
corre na stack leve) e só é enviado se P(movimento anormal) ≥ esse valor; o alerta passa a incluir a
linha de materialidade ("triage evidence, not a forecast"). Sem o ficheiro do modelo, o gate é ignorado
com aviso — o runner nunca fica vermelho por causa da triagem. Detalhes: `progress/ML_PLAN.md` (M5).

**Loop de pós-validação (M5.5).** Com o gatilho de notícias ligado, o runner regista cada decisão em
`data/predictions_log.jsonl` (local, gitignored). Dias depois corre `python scripts/post_validate.py`:
rotula as decisões maturadas com o que REALMENTE aconteceu e escreve
`docs/evaluation/live_monitoring.md`. Nota honesta: no cron do GitHub Actions o runner é efémero
(o log não persiste entre corridas) — o loop completo corre na tua máquina; persistir o log na
nuvem fica para a Fase B.

### 6) A webpage (dashboard) sempre disponível
Publica `app/streamlit_app.py` no **Streamlit Community Cloud** — passos em
[`deployment.md`](deployment.md). Depois cola o URL no `README.md` e na tese.
*(Opcional: uma página GitHub Pages a ligar o dashboard + o canal, com um domínio grátis do Student Pack.)*

### Experimentar na tua máquina (sem enviar)
```bash
pip install -r requirements.txt
python scripts/run_alerts.py --dry-run
```
Varre a watchlist com preços ao vivo e **imprime** os alertas (não envia). Corre na stack leve (sem torch).

---

## Fase B — bot interativo por utilizador ✅ CONSTRUÍDA (versão sem servidor)

**Já funciona, de graça e sem host** (P4 do `progress/PLANO_FINAL.md`): o bot usa *long-polling*
(`getUpdates`), por isso corre em qualquer máquina atrás de NAT — não precisa de webhook nem de
servidor público.

**Como ligar (2 passos):**
1. `python scripts/run_bot.py` (ou duplo-clique em `run/bot.bat`, ou a tarefa VS Code
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

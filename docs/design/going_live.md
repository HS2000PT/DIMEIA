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

## Fase B — bot interativo por utilizador (mais tarde; precisa de servidor)
Quando quiseres que **cada pessoa fale com o bot** e escolha os seus próprios tickers (`/start`,
`/watch TSLA`, `/unwatch`, `/stop`), o bot tem de **ouvir** mensagens → aí sim precisa de um **host sempre
ligado** + uma **base de dados** de utilizadores.
- **Host grátis (Student Pack):** Fly.io / Render (free), **DigitalOcean** ($200/ano de crédito),
  **Azure** ($100), **Heroku** ($13/mês × 24 meses).
- **Utilizadores:** SQLite (num volume pequeno) ou **MongoDB Atlas** (free tier / $50 de crédito).
- **Biblioteca:** `python-telegram-bot` (webhook). Rate-limit por chat; segredos no cofre do host.
- **Reutiliza** o que já existe: `send_message` → `send_to(chat_id, text)`; a lógica de varredura da Fase A;
  um agendador (APScheduler no host, ou manter o cron do GitHub) a distribuir por subscritores.
- **Produto responsável:** limitar frequência/severidade (fadiga de alertas), validar tickers, nunca
  ecoar segredos.

---

## Segurança & custos (honesto)
- **Fase A é grátis:** repo público ⇒ minutos do Actions grátis; Streamlit Community Cloud grátis.
- **Segredos** só em GitHub Secrets / `.env` local — **nunca** no repositório.
- **Não é conselho financeiro:** os alertas **explicam** eventos com evidência do passado; não preveem preços.

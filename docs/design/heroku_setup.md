# heroku_setup.md — pôr o InvestiGator a correr 24/7, passo a passo

> **Pré-requisitos:** os créditos do Student Pack já reclamados (feito) e uma conta Heroku.
> **Tempo:** ~20 minutos, quase todo à espera do build.
> **Custo:** $12/mês dos $13/mês de crédito. Sobra $1/mês.
>
> Porque é o Heroku e não a Oracle ou a DigitalOcean: ver [`hosting.md`](hosting.md). Resumo:
> a janela da DigitalOcean fechou a 31/07/26 e a Oracle está bloqueada sem prazo.

---

## O que vai ficar a correr

| Processo | Comando | Dyno | Porquê |
|---|---|---|---|
| `web` | dashboard Streamlit | **Basic** $7 | Sempre ligado; nunca hiberna |
| `worker` | vigia de alertas, ciclo de 60 s | **Eco** $5 | Substitui o cron best-effort de 1,5-2 h |

Os ficheiros já estão no repositório e testados: `Procfile`, `app.json`, `.python-version`
(3.12), e o `streamlit` foi movido para o `requirements.txt` (o Heroku só lê esse).

---

## Passo 1 — Instalar a CLI e entrar

```bash
# Windows (PowerShell, como administrador)
winget install --id=Heroku.HerokuCLI

heroku login
```

## Passo 2 — Criar a app

```bash
cd c:/Users/henri/Desktop/DIMEIA

heroku create investigator-meia --stack heroku-24
# Se o nome estiver tomado, escolhe outro: o URL será https://<nome>.herokuapp.com
```

Confirma que o remoto ficou ligado:

```bash
git remote -v          # deve aparecer um remoto "heroku"
```

## Passo 3 — Os segredos (config vars)

**Nunca no repositório.** Os nomes são exatamente os mesmos do `.env` local, por isso podes
copiar os valores de lá. A lista completa e o que cada uma faz está em [`keys.md`](keys.md).

```bash
heroku config:set \
  TELEGRAM_BOT_TOKEN="cola-aqui" \
  TELEGRAM_CHAT_ID="@InvestiGatorMEIA" \
  FINNHUB_API_KEY="cola-aqui" \
  TIINGO_API_KEY="cola-aqui" \
  POLYGON_API_KEY="cola-aqui" \
  ALPHAVANTAGE_API_KEY="cola-aqui"
```

Opcionais, só se quiseres o narrador ligado (está **off** por defeito):

```bash
heroku config:set GROQ_API_KEY="..." GEMINI_API_KEY="..."
```

Verifica:

```bash
heroku config          # confere os nomes; os valores aparecem, por isso não faças screenshot
```

## Passo 4 — Primeiro deploy

```bash
git push heroku main
```

O build demora ~3-5 minutos. No fim deve dizer `Verifying deploy... done.`

## Passo 5 — Escalar os dois processos

Por defeito o Heroku arranca **só** o `web`, e em Eco. Corrige os dois:

```bash
heroku ps:type web=basic worker=eco
heroku ps:scale web=1 worker=1
heroku ps                # confirma: web (Basic) up, worker (Eco) up
```

> ⚠️ **Este é o passo que é fácil esquecer.** Sem `worker=1` o vigia nunca arranca e continuas
> a depender do cron do GitHub. Sem `web=basic` a app hiberna ao fim de 30 minutos, que é
> exatamente o problema que estamos a resolver.

## Passo 6 — Confirmar que está vivo

```bash
heroku open                      # abre o dashboard no browser
heroku logs --tail --dyno=worker # o vigia a correr ciclos
```

No log do worker deves ver um ciclo a cada 60 segundos. Fora de horas de mercado é normal
e correto que diga que não há nada a alertar.

---

## Depois: o que verificar no primeiro dia útil

1. **O canal recebe a nota de abertura** (~14-15 UTC) e o **resumo de fecho** (~21 UTC).
2. **A latência medida desce.** A app mostra a latência **só quando foi medida**; antes disto
   mostrava ~179 min (o custo do cron). Deve passar a segundos ou poucos minutos.
3. **Não há alertas duplicados.** O workflow do GitHub Actions pode continuar ligado como rede
   de segurança: a deduplicação por histórico partilhado impede duplicados. Se preferires,
   desliga-o em Actions → Alerts → ⋯ → Disable workflow.

---

## Duas decisões que ficam por tomar

**O histórico partilhado.** O vigia pode escrever os alertas de volta para a branch de dados,
que é o que alimenta a app. Para isso:

```bash
heroku config:set INVESTIGATOR_HISTORY_GIT=1 GITHUB_TOKEN="pat-com-contents-write"
```

Sem isto o vigia envia para o Telegram na mesma, mas a app não vê os alertas novos. Alternativa
sem PAT: deixar o cron do Actions ligado, que já escreve o histórico.

**O narrador.** Continua `narrator.enabled: false` no `config/alerts.yaml`. Ligá-lo é uma linha,
e se falhar o alerta sai exatamente como hoje (é aditivo, com fallback determinístico).

---

## Se alguma coisa falhar

| Sintoma | Causa provável | Correção |
|---|---|---|
| Build falha em `pip install` | pin incompatível com o Python do stack | `heroku config:set PYTHON_VERSION=3.12` |
| App abre mas dá "Application error" | o Streamlit não apanhou o `$PORT` | confirma o `Procfile` intacto; `heroku logs --tail` |
| Worker arranca e morre logo | falta um segredo obrigatório | `heroku logs --dyno=worker`; o runner é **fail-open** e diz qual falta |
| Worker adormece | o Eco hiberna com inatividade | passa a Basic: `heroku ps:type worker=basic` (fica $14/mês, $1 acima do crédito) |
| Créditos a esgotar | dois dynos Basic | volta o worker a Eco, ou desliga o `web` e usa o Streamlit Cloud para a app |

---

## Custo, com margem

| Item | Mensal |
|---|---|
| `web` Basic | $7 |
| `worker` Eco | $5 |
| **Total** | **$12** |
| Crédito | $13 |
| **Folga** | **$1/mês, durante 24 meses** |

O crédito cobre a entrega (13 de setembro de 2026), a defesa, e mais de um ano depois disso.

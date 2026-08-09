# heroku_setup.md — pôr o InvestiGator a correr 24/7, passo a passo

> ✅ **EXECUTADO a 2026-08-02.** A app está no ar em
> <https://investigator-ddc9d8618935.herokuapp.com/> e o vigia corre de 60 em 60 s.
> Este guia foi corrigido com o que a implantação real revelou, e não com o que se previa.
>
> **Custo real:** $14/mês (não $12 — ver passo 5). Crédito: **saldo único de $312** a expirar
> 2028-07-31, ou seja **≈22 meses** de autonomia.
>
> Porque é o Heroku e não a Oracle ou a DigitalOcean: ver [`hosting.md`](hosting.md). Resumo:
> a janela da DigitalOcean fechou a 31/07/26 e a Oracle está bloqueada sem prazo.

---

## O que vai ficar a correr

| Processo | Comando | Dyno | Porquê |
|---|---|---|---|
| `web` | dashboard Streamlit | **Basic** $7 | Sempre ligado; nunca hiberna |
| `worker` | vigia de alertas, ciclo de 60 s | **Basic** $7 | Substitui o cron best-effort de 1,5-2 h |

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

heroku create investigator --stack heroku-24
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
heroku ps:scale web=1:basic worker=1:basic
heroku ps                # confirma: web (Basic) up, worker (Basic) up
```

> ⚠️ **Não se pode misturar tipos de dyno.** A tentativa `web=basic worker=eco` é rejeitada com
> *"You can't mix dyno types: Basic and Eco"*. Daí os dois em Basic, e daí $14/mês em vez dos
> $12 que o plano previa.

> ⚠️ **Este é o passo que é fácil esquecer.** Sem `worker=1` o vigia nunca arranca e continuas
> a depender do cron do GitHub. Sem `basic` a app hiberna ao fim de 30 minutos, que é
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

**O histórico partilhado.** ✅ **Ligado a 2026-08-02.**

```bash
heroku config:set INVESTIGATOR_HISTORY_API=1 GITHUB_TOKEN="<pat>"
```

⚠️ **Repara na variável: é `INVESTIGATOR_HISTORY_API`, não `INVESTIGATOR_HISTORY_GIT`.** A
antiga usa o `git` da linha de comandos e exige um *checkout* da branch de dados, que num slug
do Heroku não existe (o buildpack remove o `.git`). Como esse caminho é fail-open, ligá-la
teria parecido resolver e não escreveria nada, em silêncio. A nova fala com a API do GitHub.

O publicador **junta** em vez de substituir, para o vigia e o cron do Actions poderem escrever
os dois sem se apagarem, e envia o `sha` que leu: em caso de escrita concorrente recebe 409 e
tenta na ronda seguinte.

**O narrador.** Continua `narrator.enabled: false` no `config/alerts.yaml`. Ligá-lo é uma linha,
e se falhar o alerta sai exatamente como hoje (é aditivo, com fallback determinístico).

---

## Se alguma coisa falhar

| Sintoma | Causa provável | Correção |
|---|---|---|
| Build falha em `pip install` | pin incompatível com o Python do stack | `heroku config:set PYTHON_VERSION=3.12` |
| App abre mas dá "Application error" | o Streamlit não apanhou o `$PORT` | confirma o `Procfile` intacto; `heroku logs --tail` |
| Worker arranca e morre logo | falta um segredo obrigatório | `heroku logs --dyno=worker`; o runner é **fail-open** e diz qual falta |
| **Worker em ciclo de crash, `Error R15`** | **aconteceu mesmo**: o embebedor processava todas as manchetes novas num lote só, e numa máquina nova o ficheiro de pendentes está vazio, logo *tudo* é novo. 1,4 GB num dyno de 512 MB. | Já corrigido: o `encode` fatia em lotes de 32. Se voltar, medir com uma sonda no dyno em vez de adivinhar. |
| `You can't mix dyno types` | tentativa de Basic + Eco | os dois no mesmo tipo: `heroku ps:scale web=1:basic worker=1:basic` |
| `heroku run`/`heroku api` falha com `'C:\Program' is not recognized` | espaço no caminho de instalação da CLI no Windows | usar `cmd //c "heroku ..."`, ou a API via `curl` com `heroku auth:token` |
| `git push heroku` dá `Authentication failed` | o Gestor de Credenciais do Windows intercepta antes | `git -c credential.helper= push heroku main` com `GIT_ASKPASS` a fornecer o token |
| Créditos a esgotar | dois dynos Basic ($14/mês) | desliga o `web` (`heroku ps:scale web=0`) e serve a app pelo Streamlit Cloud: fica $7/mês, ≈44 meses |

---

## Custo, com margem

| Item | Mensal |
|---|---|
| `web` Basic | $7 |
| `worker` Basic | $7 |
| **Total** | **$14** |
| Crédito (saldo único, expira 2028-07-31) | **$312** |
| **Autonomia** | **≈22 meses** |

O crédito cobre a entrega (13 de setembro de 2026), a defesa, e mais de um ano depois disso.
Se em algum momento for preciso esticá-lo, `heroku ps:scale web=0` deixa só o vigia a $7/mês
(≈44 meses) e a app volta para o Streamlit Cloud, que é grátis e hiberna.

---

## Um URL decente (o sufixo aleatório não sai)

O Heroku acrescenta um sufixo aleatório a **todas** as apps criadas hoje, para impedir que alguém
se apodere de um subdomínio libertado. Renomear a app **não** o remove: gera outro. Foi tentado a
2026-08-02 e o resultado foi trocar `investigator-meia-fa8287a1e568` por
`investigator-ddc9d8618935`, sem ganho nenhum e com o custo de invalidar o URL anterior.

**A solução real é um domínio próprio, e é gratuita para ti.** O Student Pack inclui um domínio
`.me` (Namecheap) ou `.app` (Name.com) grátis durante um ano. Com um dyno *Basic* o Heroku aceita
domínios próprios e emite o certificado sozinho.

```bash
heroku domains:add www.investigator.me --app investigator
heroku domains          # mostra o alvo DNS a configurar no registrar
```

Depois é só criar um CNAME no registrar a apontar para o alvo que o comando devolve, e esperar a
propagação. O certificado (ACM) é automático e gratuito.

**Vale a pena antes da defesa?** Um URL bonito não muda uma nota. Mas custa dez minutos e o link
que envias ao orientador passa a ser legível, o que conta quando é a primeira coisa que ele vê.

---

## Implantar quando o `git push heroku main` falha (2026-08-04)

**O sintoma.** `git push heroku main` devolve `Authentication failed`, mesmo com a sessão do
CLI válida (`heroku auth:whoami` e `heroku auth:token` funcionam). O Heroku deixou de
aceitar autenticação básica no git e espera um *credential helper* que o `heroku login`
instala interactivamente — o que exige um browser e não se resolve por linha de comandos.

**Porque é que isto interessa mais do que parece.** O `git push origin main` envia para o
GitHub, e **o GitHub não implanta nada**. Sem esta segunda operação, uma alteração ao
`Procfile` fica no repositório e a produção continua a servir o ficheiro antigo, sem
qualquer erro. Aconteceu exactamente isso ao promover a v3: o commit estava feito e o
`heroku ps` continuava a mostrar `app/streamlit_app.py`. **Confirmar sempre com
`heroku ps`, nunca assumir que um commit é uma implantação.**

**O caminho que funciona com o token, sem browser** (API de Sources + Builds):

```sh
HK="/c/Program Files/heroku/bin/heroku.cmd"; T=$("$HK" auth:token | tr -d '\r\n')
# 1. pedir um espaço de upload
curl -s -X POST https://api.heroku.com/apps/investigator/sources \
     -H "Accept: application/vnd.heroku+json; version=3" -H "Authorization: Bearer $T" -o src.json
# 2. empacotar SÓ o que está versionado (git archive respeita o .gitignore por construção)
git archive --format=tar.gz -o app.tar.gz HEAD
# 3. carregar para o put_url e criar o build a apontar para o get_url
#    (ver scripts/ ou o histórico desta sessão para o passo em Python)
```

`git archive HEAD` em vez de empacotar a pasta: nunca inclui `.env`, `.venv`, caches nem
nada que não esteja no commit. Verificado: build `succeeded`, release **v15**, e
`heroku ps` a mostrar `streamlit run app/dashboard_v4.py`.

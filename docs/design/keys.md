# keys.md — Todas as chaves num só sítio

> **Nunca** pôr valores neste ficheiro. Ele lista **nomes**, onde os obter e onde os colar.
> Os valores vivem só no `.env` (gitignored) e nos cofres de segredos das plataformas.

---

## Bloco para copiar (cola no `.env` na raiz do repo)

```bash
# ── Telegram (obrigatório para enviar alertas) ────────────────────────────────
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# ── Notícias (obrigatório para o gatilho de notícias) ─────────────────────────
FINNHUB_API_KEY=

# ── Fallback de preços (recomendado: o Yahoo bloqueia runners partilhados) ────
TIINGO_API_KEY=
POLYGON_API_KEY=
ALPHAVANTAGE_API_KEY=

# ── Narrador LLM (opcional; sem elas sai o texto por template) ────────────────
GEMINI_API_KEY=
GROQ_API_KEY=
```

`.env` está no `.gitignore` e **nunca** é versionado. Se algum dia aparecer em
`git status`, parar e avisar antes de fazer seja o que for.

---

## O que é cada uma

| Nome | Para quê | Onde obter | Free tier | Sem ela |
|---|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | enviar mensagens | @BotFather no Telegram | ilimitado | não envia nada |
| `TELEGRAM_CHAT_ID` | para onde enviar | id do canal (`-100…`) ou `@nome` | — | não envia nada |
| `FINNHUB_API_KEY` | notícias + cotação em tempo real | [finnhub.io](https://finnhub.io) | 60 pedidos/min | sem gatilho de notícias nem intradiário |
| `TIINGO_API_KEY` | 1.º fallback de preços | [tiingo.com](https://www.tiingo.com) | ~1.000/dia | cadeia salta esta fonte |
| `POLYGON_API_KEY` | 2.º fallback de preços | [polygon.io](https://polygon.io) | 5 pedidos/min | cadeia salta esta fonte |
| `ALPHAVANTAGE_API_KEY` | último recurso de preços | [alphavantage.co](https://www.alphavantage.co) | 25/**dia** | cadeia salta esta fonte |
| `GEMINI_API_KEY` | narrador (principal) | [aistudio.google.com](https://aistudio.google.com) → *Get API key* | ~1.500/dia, 10–15/min | usa o Groq |
| `GROQ_API_KEY` | narrador (reserva) | [console.groq.com](https://console.groq.com) → *API Keys* | ~30/min, 1.000/dia | usa o texto por template |

**Nenhuma das duas do narrador pede cartão.** São duas de propósito: uma defesa ao vivo não
pode morrer num rate limit. Ordem: Gemini → Groq → template determinístico. O canal e a app
funcionam sempre, mesmo sem nenhuma.

---

## Onde cada chave tem de ser colada

O sistema corre em até quatro sítios. Cada um tem o seu cofre — **é por isso que a mesma
chave se cola mais do que uma vez**.

| Onde corre | Cofre | Como |
|---|---|---|
| **PC local** | ficheiro `.env` | copiar o bloco acima e preencher |
| **GitHub Actions** (alertas agendados) | *Settings → Secrets and variables → Actions → New repository secret* | um segredo por nome, **exatamente** o mesmo nome |
| **VM Oracle** (loop de polling) | ficheiro `.env` na VM | `deploy/setup_vm.sh` copia-o |
| **Streamlit Cloud** (app pública) | *Manage app → Settings → Secrets* | formato TOML: `GEMINI_API_KEY = "…"` |

⚠️ **Os nomes têm de bater certo em todos os cofres.** O workflow lê
`${{ secrets.GEMINI_API_KEY }}`; se o segredo se chamar `GEMINI_KEY`, o valor chega vazio e o
sistema degrada em silêncio (por desenho: fail-open). Não há erro visível — só falta a feature.

### Verificar que o GitHub as vê

No log do workflow "Alerts", uma chave presente aparece mascarada como `***`. Uma chave em
falta aparece como um vazio. É a forma mais rápida de confirmar sem expor nada.

---

## Regras de segurança (não negociáveis)

1. **Nunca** commitar o `.env`. Nunca colar valores em Markdown, em issues, ou em prompts.
2. **Nunca** pôr chaves no `config/alerts.yaml` — esse ficheiro é versionado e público.
3. Ao publicar o repositório público, `scripts/make_public_bundle.py` parte de `git ls-files`
   (portanto nunca inclui o `.env`) **e** corre um scan de segredos antes de escrever.
4. Se uma chave for exposta por acidente: revogá-la no fornecedor **primeiro**, gerar outra
   depois. Apagar do histórico do git não basta — assume-se comprometida a partir do momento
   em que sai do teu computador.
5. Todas as chaves aqui são de free tier sem cartão associado, por isso uma fuga não gera
   custo — mas gera abuso de quota, que tira o serviço a funcionar.

---

## Estado atual (atualizar quando mudar)

| Chave | `.env` local | GitHub Actions | Notas |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | ✅ | canal a funcionar |
| `TELEGRAM_CHAT_ID` | ✅ | ✅ | |
| `FINNHUB_API_KEY` | ✅ | ✅ | |
| `TIINGO_API_KEY` | ✅ | ✅ | criada 2026-07-13 |
| `POLYGON_API_KEY` | ✅ | ✅ | criada 2026-07-13 |
| `ALPHAVANTAGE_API_KEY` | ✅ | ✅ | |
| `GEMINI_API_KEY` | ⬜ | ⬜ | **por criar** |
| `GROQ_API_KEY` | ⬜ | ⬜ | **por criar** |

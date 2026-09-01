# Feedback do leitor no Telegram — o que foi construído, e como se liga

> Frente 01 do `PLANO_FINAL_2026-09-01.md`. Implementado a 2026-09-01.

## O percurso de um voto, de ponta a ponta

```
worker (dyno)                          Telegram                    web (dyno)
─────────────                          ────────                    ──────────
run_alerts.py
  news_key(ticker, texto) ──┐
  feedback.teclado(chave) ──┤
  sender.send_message(  ────┴──────►  mensagem com
      texto,                           dois botões
      reply_markup=teclado)                │
                                           │ leitor carrega
                                           ▼
                                     callback_query ──────────►  POST /telegram/webhook
                                                                    │ segredo confere?
                                                                    ▼
                                                                 webhook.processar
                                                                    ├─ 1 feedback_log.append_jsonl
                                                                    ├─ 2 answerCallbackQuery  ← sempre
                                                                    ├─ 3 editMessageReplyMarkup
                                                                    └─ 4 publish_blob(feedback.jsonl)
                                                                              │
                                     branch alerts-history  ◄────────────────┘
                                              │
                                              ▼
                                     scripts/analyse_feedback.py
                                              │
                                     docs/evaluation/evaluation_feedback.md
```

## As quatro decisões que não são óbvias

**1. Webhook e não long-polling, e isso desliga o `getUpdates`.** O Telegram não permite os
dois: com webhook registado, `getUpdates` devolve 409. Por isso o webhook trata **também** dos
comandos (`/watch`, `/list`, `/stop`) e o `process_bot_commands` do runner cala-se quando
`TELEGRAM_WEBHOOK_ENABLED=1`. Registar o webhook sem pôr essa variável deixa o `/watch` sem
resposta e enche o registo do worker de 409.

**2. A resposta ao `callback_query` acontece antes de tudo o que pode falhar.** Sem ela o
relógio continua a girar no telemóvel e o Telegram reenvia o update — um erro de escrita
transformar-se-ia numa repetição sem fim. A ordem é: gravar (escrita local, microssegundos),
responder sempre, e só depois teclado e publicação, que podem falhar sem consequência.

**3. Os votos são duráveis; as watchlists continuam a não ser.** O disco do dyno é efémero e
reinicia pelo menos uma vez por dia. Os votos vão para um JSONL publicado na branch de dados,
pelo mesmo mecanismo que já serve o `gate_log`. As watchlists dos subscritores continuam em
SQLite efémero, e continuam a perder-se — isso já era verdade antes desta alteração, o
fan-out do runner já imprimia «sem base de subscritores», e esta alteração não melhora nem
piora esse ponto. Fica escrito para que ninguém conclua o contrário ao ler o código.

**4. O identificador do votante nunca é gravado em claro.** `blake2b` com sal. A análise
precisa de distinguir pessoas — para não contar dez votos de uma como dez pessoas — e não
precisa de as identificar. É a mesma posição de minimização que a Secção 3.8.1 da dissertação
assume para as carteiras, e há um teste que a verifica no ficheiro escrito.

## Pôr no ar

```bash
# 1 — gerar o segredo e registar o webhook (imprime o segredo UMA vez)
python scripts/telegram_webhook.py registar https://investigator-ddc9d8618935.herokuapp.com

# 2 — as duas variáveis, na plataforma E no .env local
#     TELEGRAM_WEBHOOK_SECRET=<o que o passo 1 imprimiu>
#     TELEGRAM_WEBHOOK_ENABLED=1

# 3 — confirmar
python scripts/telegram_webhook.py estado     # "Último erro" vazio = está a receber
```

Sem o passo 2 a rota responde 403 **a tudo, incluindo ao Telegram**, e o `getWebhookInfo`
mostra-o em «Último erro». É o primeiro sítio a olhar quando os votos não chegam.

Para voltar atrás: `python scripts/telegram_webhook.py remover` e apagar
`TELEGRAM_WEBHOOK_ENABLED`. O comportamento antigo volta ao ciclo seguinte.

## O que a tese pode e não pode dizer com isto

**Pode:** que os alertas que o sistema decidiu enviar foram considerados úteis por N pessoas em
M votos, com o intervalo de Wilson correspondente, desde que N chegue ao mínimo pré-registado
de 20 votos efetivos.

**Não pode:** que a explicação melhora a decisão. Não há contrafactual, não há moderação, e
quem vota é quem quer. As quatro ameaças à validade estão escritas no relatório gerado, e são
as mesmas com qualquer N.

## Ficheiros

| Ficheiro | Papel |
|---|---|
| `investigator/telegram_bot/feedback.py` | Puro: teclados, `callback_data`, resumo do votante, interpretação do update |
| `investigator/telegram_bot/webhook.py` | Orquestração, com todas as saídas injetadas |
| `investigator/telegram_bot/sender.py` | Rede: envio, edição de texto, edição de teclado, resposta ao callback |
| `investigator/feedback_log.py` | Registo JSONL, um voto por pessoa e alerta na leitura |
| `investigator/evaluation/proportions.py` | Intervalo de Wilson, partilhado com o estudo moderado |
| `api/main.py` | `POST /telegram/webhook` |
| `scripts/telegram_webhook.py` | Registar, inspecionar, remover |
| `scripts/analyse_feedback.py` | Regras pré-registadas e relatório |
| `tests/test_telegram_feedback.py` · `test_telegram_webhook.py` · `test_api_webhook.py` · `test_analyse_feedback.py` | 75 testes |

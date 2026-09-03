# Feedback do leitor no Telegram

> Frente 01 do plano final. Em produção desde 2026-09-01; circuito de análise e retirada
> corrigido e fechado a 2026-09-03.

## Percurso de ponta a ponta

```text
worker/API                    Telegram                     web/API
──────────                    ────────                     ───────
alerta + chave ─────────────► mensagem com dois botões
                                      │
                                      │ leitor carrega
                                      ▼
                              callback_query ────────────► POST /telegram/webhook
                                                               │ segredo confere
                                                               ├─ acrescenta voto local
                                                               ├─ responde ao callback
                                                               ├─ atualiza contagem
                                                               └─ publish_jsonl_merge
                                                                         │
                                          branch alerts-history ◄────────┘
                                                   │
                                      feedback.jsonl + alerts_history.jsonl
                                                   │
                                      scripts/analyse_feedback.py
                                             ┌─────┴─────┐
                                             ▼           ▼
                                  relatório Markdown   fragmento LaTeX
                                                       incluído no Cap. 5
```

## Decisões que protegem a recolha

### Webhook único

O Telegram não permite webhook e `getUpdates` em simultâneo. Com o webhook registado, os
comandos (`/watch`, `/list`, `/stop`, `/deletefeedback`) também passam por esta rota e o
*poller* fica desativado. Registar o webhook sem `TELEGRAM_WEBHOOK_ENABLED=1` deixaria os
comandos sem resposta.

### Resposta antes das tarefas dispensáveis

Depois de gravar, o sistema responde sempre ao `callback_query`; só depois tenta atualizar o
teclado e publicar. Sem resposta o Telegram mostra um relógio e pode reenviar a interação. A
falha de teclado não perde o voto.

### Persistência por junção

O disco da Heroku é efémero. `publish_jsonl_merge`, e não `publish_blob`, junta linhas locais
às remotas por conteúdo exato. Substituir o ficheiro apagou seis linhas a 2026-09-01; essas
linhas foram recuperadas byte a byte do commit `a9e098cda` e repostas na branch pelo commit
`504371db0`. Não foram reconstruídas nem simuladas.

Antes do primeiro voto depois de um reinício, `seed_jsonl_once` recupera a cópia remota. Isto
impede a contagem nos botões de voltar a um apesar de a branch conservar os votos anteriores.

### Identidade minimizada

O identificador pessoal do Telegram passa por BLAKE2b com sal e só o resumo de 24 caracteres é
guardado. Nome, username e identificador pessoal em claro não entram no ficheiro. Guardam-se
também a chave do alerta, ação, hora, identificador do canal e identificador da mensagem; os
dois últimos permitem atualizar o teclado e desfazer uma eventual colisão de chave. Como a
branch é pública, a mensagem fixada revela estes campos antes da participação.

### Retirada sem uma promessa impossível

`/deletefeedback` e `/apagar` acrescentam uma marca `d` associada ao mesmo resumo. A análise
elimina todos os votos anteriores dessa pessoa; um voto posterior inicia nova participação.
As linhas antigas permanecem no histórico Git pseudonimizado. Chamar-lhe eliminação física
seria falso, por isso o comando e o consentimento dizem “retirar da análise”.

### Regras fixadas e aplicadas ao relatório e à tese

- mínimo de 20 votos efetivos antes de reportar uma proporção;
- um voto por pessoa e alerta; uma mudança só conta quando a ação muda, não quando o mesmo
  botão é repetido;
- acima de 40% por uma pessoa, repetir o cálculo sem ela; o recorte mantém o mesmo mínimo de
  20 e nunca divide por zero;
- intervalo de Wilson a 95%; não usar “significativo”;
- contar apenas chaves presentes no histórico dos alertas entregues;
- se a branch ou o histórico não puder ser lido, terminar com erro antes de substituir os
  relatórios. Uma execução explícita sem filtro só produz contagens provisórias.

## Consentimento

A versão completa da mensagem fixada está em `docs/design/telegram_channel.md`. Votar é
facultativo, não muda o serviço recebido e não testa se a explicação melhora decisões. Mede
apenas a utilidade percebida de alertas autosselecionados por leitores de um canal público.

## Gerar os resultados

```powershell
.\.venv\Scripts\python.exe scripts\analyse_feedback.py --da-branch
```

O comando obtém **os dois** ficheiros da mesma branch. Usa a API autenticada quando configurada
e, num checkout de desenvolvimento, recorre a `git fetch origin alerts-history`. Só é válido
quando imprime as linhas de votos e do histórico sem a palavra `ERRO`.

Escreve:

- `docs/evaluation/evaluation_feedback.md` — relatório verificável;
- `tese-v2/ch5/feedback_auto.tex` — subsecção incluída por
  `tese-v2/ch5/chapter5.tex`.

O texto LaTeX é correto para zero votos, abaixo do mínimo, no limiar e com um votante
dominante. Recompilar `tese-v2/main.pdf` continua a ser necessário para o fragmento chegar ao
PDF.

## O que pode e não pode ser dito

Pode dizer-se quantos votos válidos existem, quantas pessoas e alertas representam e, quando
as regras permitem, a proporção com o seu intervalo e a salvaguarda de dominância.

Não pode dizer-se que a explicação causa decisões melhores. Não há contrafactual, moderação,
amostragem do público-alvo nem independência entre votos da mesma pessoa. Também não é possível
correlacionar utilidade com a pontuação de triagem nesta recolha: esse campo não foi guardado no
histórico. O plano foi corrigido em vez de inventar uma análise retrospetiva.

## Operação

```powershell
.\.venv\Scripts\python.exe scripts\telegram_webhook.py estado
```

O estado deve mostrar o último erro vazio. Para reconfigurar, consultar
`docs/design/going_live.md`; segredos nunca entram neste documento.

## Ficheiros principais

| Ficheiro | Papel |
|---|---|
| `investigator/telegram_bot/feedback.py` | botões, chave e pseudónimo do votante |
| `investigator/telegram_bot/webhook.py` | voto, comandos e retirada |
| `investigator/feedback_log.py` | formato acrescentável, ordem temporal e resumo |
| `investigator/history_publish.py` | leitura, semente e junção da branch |
| `api/main.py` | rota segura e agregado para o painel |
| `scripts/analyse_feedback.py` | regras e duas saídas sincronizadas |
| `scripts/recover_feedback_history.py` | recuperação verificável de linhas antigas |
| `tests/test_*feedback*.py` | portas sem rede do circuito |

# ESTADO — reescrita em `tese-v2/`

> ⛳ **PRIORIDADE MÁXIMA: ler `PLANO_FINAL_2026-09-01.md` na raiz de `DIMEIA/` antes de tocar em seja o que for.** Criado a 2026-09-01. Manda sobre este ficheiro e sobre todos os outros planos do repositório, incluindo `progress/PLANO_FINAL_ENTREGA.md`, `progress/PLANO_EMERGENCIA_DEFESA_2026-08-30.md` e `INVESTIGATOR_MASTER_PLAN.md`, que ficam como registo histórico.

> Atualizar sempre no fim de cada sessão. Ler `BRIEF_REESCRITA.md` antes de começar.

## Sessão em curso

TERMINADA 01:35 (01/09) — **frente 01 do plano: feedback do leitor no Telegram, construído e testado.**

O código está todo escrito e verificado; falta **pôr no ar**, que são dois passos manuais
descritos em `docs/design/telegram_feedback.md`. Nada disto toca na tese ainda: entra no
documento quando houver dados.

**O que foi construído.** Dois botões em cada alerta, um webhook em `api/main.py` que recebe os
votos, um registo JSONL publicado na branch de dados, e um script de análise com as regras
fixadas antes de existirem dados. 75 testes novos, todos a passar.

**⚠️ A alteração com mais consequências:** o bot passa de long-polling a webhook, e **o Telegram
não permite os dois** — com webhook registado, o `getUpdates` devolve 409. Por isso o webhook
trata também dos comandos (`/watch`, `/list`, `/stop`) e o `process_bot_commands` do runner
cala-se quando `TELEGRAM_WEBHOOK_ENABLED=1`. Registar o webhook sem definir essa variável deixa
o `/watch` sem resposta e enche o registo do worker de 409.

**Durabilidade, dita como é:** os votos sobrevivem ao reinício do dyno (JSONL publicado na
branch, como o `gate_log`); as watchlists dos subscritores continuam em SQLite efémero e
continuam a perder-se. Isso já era verdade antes — o fan-out já imprimia «sem base de
subscritores» — e esta alteração não melhora nem piora esse ponto.

**Uma rota foi retirada por um teste do próprio projeto.** A primeira versão expunha
`/api/feedback`; o `test_a_api_nao_serve_nada_que_a_pagina_nao_use` apanhou-a, porque a página
ainda não a consome. A razão ficou escrita no `api/main.py` e a rota volta na revisão do painel,
no passo em que a página passar a mostrar as contagens.

**Regras pré-registadas da análise** (em `scripts/analyse_feedback.py`, e com testes que falham
se alguém as mudar): mínimo de 20 votos efetivos para reportar qualquer proporção; um voto por
pessoa por alerta, com o último a substituir; salvaguarda do votante dominante acima de 40%;
intervalos de Wilson; a palavra «significativo» nunca aparece. Alterar qualquer uma destas
depois de haver dados tem de ficar registado aqui, com a data e a razão.

**✅ NO AR desde 2026-09-01 02:08 UTC (release v51 na Heroku).** Verificado em produção:
segredo errado devolve 403, segredo certo devolve 200 com o tratador a correr, corpo ilegível
devolve 200, e o registo do worker diz «webhook ativo — comandos tratados em
/telegram/webhook, polling saltado» sem um único 409. O webhook está registado com
`allowed_updates` limitado a `message` e `callback_query`, e o `getWebhookInfo` não reporta
erros. As variáveis `TELEGRAM_WEBHOOK_SECRET` e `TELEGRAM_WEBHOOK_ENABLED` estão definidas na
plataforma e no `.env` local.

⚠️ **O código está no ramo `feat/telegram-feedback`, e a `main` não foi tocada.** A Heroku foi
servida com `git push heroku feat/telegram-feedback:main`. Para reverter em segundos:
`git push heroku main:main --force` a partir da `main`, e apagar `TELEGRAM_WEBHOOK_ENABLED`.
Para adotar: `git checkout main && git merge feat/telegram-feedback`.

**Regra 6, acrescentada depois de o sistema estar no ar e antes de haver dados reais:** só
contam votos cuja chave existe no histórico partilhado. Um voto sobre um alerta inexistente é
tráfego de teste ou uma chave antiga, e é ignorado na contagem — nunca apagado do ficheiro. Foi
esta regra que tornou seguro enviar uma mensagem de teste ao canal (message_id 637) para
verificar os botões de ponta a ponta.

**Ficheiros novos:** `investigator/telegram_bot/feedback.py`, `.../webhook.py`,
`investigator/feedback_log.py`, `investigator/evaluation/proportions.py`,
`scripts/telegram_webhook.py`, `scripts/analyse_feedback.py`,
`docs/design/telegram_feedback.md`, `docs/evaluation/evaluation_feedback.md`, e quatro
ficheiros de testes. **Alterados:** `sender.py`, `config.py`, `api/main.py`,
`scripts/run_alerts.py`, `.env.example`.

⚠️ **A VM Linux da ponte tem Python 3.10 e o projeto exige 3.11+** (`from datetime import UTC`).
Os testes foram corridos no contentor da sessão. Quem continuar: correr a suite na máquina do
aluno, com o `.venv`, antes de dar qualquer alteração por verificada.

---


TERMINADA 00:55 (01/09) — **conformidade com o modelo oficial MEIA v2, e correção do orçamento de páginas.**

O modelo oficial (`modelo-oficial/`, copiado para o repositório nesta sessão) resolveu duas coisas
que estavam erradas e uma que estava em falta.

**1. A declaração de uso de IA estava no sítio errado.** O modelo manda-a, textualmente, para «a
secção onde são abordadas as considerações éticas», e não para a página da Declaração de
Integridade — que só lhe aponta. Aplicado: a Declaração passa a ter a redação do modelo palavra
por palavra (incluindo o período das exceções), e a declaração de IA é agora a Secção 3.8.4,
`\subsection{Utilização de ferramentas de inteligência artificial}`, a seguir a «Questões éticas e
sociais» (3.8.3). A Declaração remete para ambas pelo número.

**2. ⚠️ O LIMITE DE 120 PÁGINAS NÃO É O QUE EU ANDAVA A CONTAR.** O modelo diz *«The minimum number
of pages is 60 and the maximum is 120 (not counting the Annexes). Small deviations are allowed.»*
**Os apêndices não contam.** A posição real:

| | Páginas |
|---|---|
| Pré-textuais (romanos) | 24 físicas, i–xxiv |
| **Corpo + bibliografia — o que conta** | **90** (impressas 1–90) |
| Apêndices A e B — não contam | 8 (impressas 91–98) |
| Total físico do PDF | 122 |

Contam **90 de 120**. Na leitura mais pessimista possível (todas as físicas menos anexos), 114.
Em consequência, a Figura `fig:sis_seletividade` do `ch4`, removida na sessão anterior apenas para
poupar duas páginas, **foi reposta**. Quem continuar: o número a vigiar é o das páginas impressas
do corpo, não o total físico do PDF.

**3. Faltava a Lista de Símbolos**, que a lista de verificação do modelo marca como obrigatória.
Acrescentada no fim dos pré-textuais: vinte símbolos, cada um com a equação ou secção onde é
definido, o que a torna também um índice. A Lista de Código e a Lista de Algoritmos continuam
ausentes, e corretamente — o documento não tem nenhum dos dois, e o próprio modelo manda remover
esses comandos nesse caso.

**Divergências do `meia-style.cls` face ao oficial:** cinco, todas comentadas no ficheiro e todas
defensáveis (babel PT-PT, palavras-chave próprias para o abstract EN, caminhos das imagens sem a
barra inicial, guarda do bloco do júri, `\par` antes das palavras-chave). Verificado por diff
contra o modelo nesta sessão.

**Estado:** 90 páginas contadas · 122 físicas · 38 figuras · 13 tabelas · 70 referências ·
0 pré-publicações. Compila a 0 erros, 0 referências indefinidas, 0 citações indefinidas.

---


TERMINADA 00:10 (01/09) — **aplicação de uma revisão crítica externa e reposição do limite de páginas.**

**1. O que foi aplicado.**
- `ch4`: nova subsecção «O elo em falta: arquitetura de retreino», com a Figura `fig:sis_retreino`.
  Define o gatilho condicional (PSI > 0,25 em qualquer entrada, ou três meses sem revisão), a janela
  deslizante de vinte e quatro meses com o embargo de cinco dias, e a porta de promoção que só
  aceita o modelo novo se o intervalo de confiança da diferença excluir o zero. A limitação passa a
  ser **de execução e não de desenho**, e o `ch6` remete para lá.
- `ch6`: três itens novos de trabalho futuro (eliminar a assimetria de referencial do `ret_event`;
  agrupar os precedentes por par empresa–dia antes da seleção; expor o R² da janela na própria
  mensagem); enquadramento pela forma semiforte da hipótese dos mercados eficientes na QI3, com a
  ressalva expressa de que o trabalho **não testa** essa hipótese; e atenuação da afirmação de
  explicabilidade nas Considerações finais — o trabalho estabelece que o sistema está preparado
  para sustentar explicações verificáveis, e **não** que essas explicações melhorem a decisão.
- Compressões de prosa no `ch2` (4) e no `ch5` (2), sem perda de conteúdo.

**2. O que foi recusado, e porquê.** Três pontos do relatório não foram aplicados por estarem
errados ou por a medição os contrariar. Ficam registados porque podem voltar a ser levantados:
- *«Citações na primeira pessoa».* As passagens apontadas são da **Declaração de Integridade**,
  onde a primeira pessoa é a forma correta e exigida.
- *«O `ret_event` contaminado invalida o resultado negativo».* O sinal do argumento está invertido.
  A entrada contaminada pertence aos modelos **derrotados**; a linha de base vencedora usa apenas o
  `vol20`, fechado na véspera. Corrigir a assimetria **reforça** o resultado negativo em vez de o
  desfazer. É por isso que consta como trabalho futuro, e não como ameaça à validade.
- *«Integrar os embeddings do SBERT na triagem».* Foi medido: 0,496 contra 0,542. É pior.

**3. Páginas.** As adições levaram o documento a 122, dois acima do máximo oficial de 120. Reposto
por: remoção da Figura `fig:sis_seletividade` do `ch4` (a mesma conclusão consta da
Secção `sec:av_producao` sobre uma amostra muito maior), captura de ecrã da aplicação passada a duas
`minipage` lado a lado, e eliminação no `ch5` de um parágrafo que repetia a legenda da Tabela 5.2 —
a parte útil foi dobrada na própria legenda. **120 páginas.**

**Estado:** 120 páginas, 37 figuras, 13 tabelas, 70 referências, 0 pré-publicações. Compila a
0 erros, 0 referências indefinidas, 0 citações indefinidas. `check_escrita.py` (0 achados,
autoteste a disparar), `check_floats.py` (49 flutuantes no corpo, todos invocados e com legenda
curta e longa) e `check_tex_escapes.py` (0) passam sobre `tese-v2/`.

⚠️ **120 é exatamente o máximo oficial.** Qualquer adição futura tem de vir acompanhada de um corte
equivalente. Verificar sempre `pdfinfo main.pdf | grep Pages` antes de dar uma sessão por terminada.

---

TERMINADA 20:10 (31/08) — **auditoria, correção factual, legibilidade e regras do orientador.**

**1. Auditoria crítica (três revisores contra `docs/evaluation/`, `src/`, `scripts/`, `config/`).**
Cerca de 35 correções, cada uma com fonte. As mais graves: latência (os valores vinham de um ficheiro
substituído a 30/08; a mediana de descoberta é 353 min e o ciclo de 60 s é **pior** que o agendador,
402 contra 196); critério de 0,02 declarado e depois violado em diferenças de 0,004; secção de deriva
a medir treino→teste e a afirmar treino→2026; limiar z=1,5 em produção nunca divulgado; deteção
intradiária ausente dos capítulos; os 38 214 casos descritos como recolha quando são reconstrução;
decaimento por recência nunca descrito; intervalos de confiança omitidos contra a instrução expressa
da fonte; três contagens erradas.

**2. Legibilidade.** Frases com 40+ palavras: **10,2% → 6,3%** (referência: 4,4%). Parágrafos com
140+ palavras: 18 → 13. Secção de Limitações do ch6 reestruturada numa tabela de onze linhas mais
quatro parágrafos. Pontes narrativas no início do ch3, ch5 e ch6.

**3. Regras do orientador.**
- **Zero arXiv.** As quatro pré-publicações foram substituídas por versões revistas por pares:
  FinBERT → *Contemporary Accounting Research* 40(2); Doshi-Velez e Kim → capítulo Springer 2018;
  BloombergGPT → survey do ICAIF 2023. O FinBERT do Araci, que era o artefacto medido, passou a ser
  identificado pelo ponto de controlo (`ProsusAI/finbert`) em vez de citado.
- **Capítulo 1 só com fontes recentes.** Todas as citações do capítulo são agora de 2024 a 2026.
  Kahneman 1979, Barberis 2003, Barber e Odean 2008, Fama 1970 e Brown e Warner 1985 passaram para
  remissões ao capítulo 2, onde já estavam citados. Fontes novas verificadas no Crossref:
  Cahill, Liu e Smales (*Accounting & Finance*, 2025) e Ernst e Spatt (*Annual Review of Financial
  Economics*, 2026).

**4. Figuras.** Refeito em português, em LaTeX, o gráfico da capitalização do mercado. Removidas as
duas figuras redundantes e a última figura importada em inglês. Declarada no ch4 a razão de a
interface e os alertas serem em inglês.

**5. Estado da arte.** Fechadas três lacunas: geração aumentada por recuperação (com Lewis et al.,
NeurIPS 2020, e o survey da *ACM Computing Surveys* 2026), corpora de notícias financeiras, e
validade do rótulo setorial. O ch2 passou de 12 para 14 páginas.

**Estado:** 120 páginas, 37 figuras, 13 tabelas, 70 referências, 0 pré-publicações. Compila a
0 erros, 0 referências indefinidas, 0 citações indefinidas, 0 `Overfull \vbox`, 0 `Float too large`,
0 `Overfull \hbox` acima de 20 pt.

**Por fazer:** campanha única de re-execução dos 31 avaliadores com data congelada e manifesto;
parte inferior do dashboard; slides; guia de estudo e defesa. Restam cinco lacunas de estado da arte
(enquadramento regulatório, deteção de quase-duplicados, seleção sob orçamento, geração a partir de
dados estruturados) e os 8 itens de re-execução da auditoria.

⚠️ **As portas de qualidade do projeto (`scripts/check_floats.py`, `check_tese_numeros.py`) apontam
para `tese/` e não para `tese-v2/`.** Não cobrem o documento que vai ser entregue. `check_escrita.py`
e `check_tex_escapes.py` cobrem, e passam.

<!-- Formato: "INICIADA 2026-08-31 03:10 — a escrever ch4". Apagar e substituir por
     "TERMINADA hh:mm" no fim. Se uma linha INICIADA tiver mais de 90 minutos, considerar
     abandonada e prosseguir. -->

## Estado por capítulo

| Ficheiro | Capítulo | Estado | Páginas | Figuras | Tabelas |
|---|---|---|---|---|---|
| `frontmatter/frontmatter.tex` | Resumo e Abstract | ✅ escrito (199 e 175 palavras) | — | — | — |
| `ch1/chapter1.tex` | 1 Introdução | ✅ escrito — **referência de registo** | 4 (pp. 1–4) | 2 | 0 |
| `ch2/chapter2.tex` | 2 Estado da arte | ✅ escrito e compilado (5087 palavras) | 12 (pp. 5–16) | 2 | 3 |
| `ch3/chapter3.tex` | 3 Métodos e materiais | ✅ escrito e compilado (3968 palavras) | 12 (pp. 17–28) | 6 | 2 |
| `ch4/chapter4.tex` | 4 Implementação | ⚠️ reescrito após perda (4390 palavras) | 16 (pp. 29–44) | 8 | 2 |
| `ch5/chapter5.tex` | 5 Casos de estudo | ✅ escrito e compilado (10\,610 palavras) | 26 (pp. 43–68) | 21 | 2 |
| `ch6/chapter6.tex` | 6 Conclusões | ✅ escrito e compilado (4662 palavras) | 10 (pp. 69–78) | 2 | 0 |
| `appendices/appendixA.tex` | A Reprodutibilidade | ✅ escrito e compilado (1487 palavras) | 5 (pp. 85–89) | 0 | 2 |
| `appendices/appendixB.tex` | B Plano curricular | ✅ escrito e compilado (252 palavras) | 3 (pp. 91–93) | 0 | 1 |

Total do documento: **115 páginas físicas**, 41 figuras, 12 tabelas, ≈33 300 palavras de prosa
(a contagem exclui o conteúdo das tabelas e dos ambientes de desenho).

Repartição medida no índice: front matter 22 pp · `ch1` 1–4 · `ch2` 5–16 · `ch3` 17–28 ·
`ch4` 29–42 · `ch5` 43–68 · `ch6` 69–78 · bibliografia 79–84 · apêndice A 85–89 · apêndice B 91–93.

✅ **O documento cabe no limite oficial com cinco páginas de folga**: 115 contra o máximo de 120, e
contra o alvo de ≈112 do brief. A projeção da sessão anterior apontava 116, e o desvio veio do `ch2`,
que fechou em 12 páginas e não nas 18 previstas. Os cortes de emergência identificados no `ch5`
(subsecções 5.2.5 e 5.4.6) **não foram necessários e não foram aplicados**.

⚠️ **O `ch2` ficou seis páginas abaixo do alvo do brief (12 contra 18), e é o único capítulo nessa
condição.** Cobre as sete áreas técnicas do trabalho e todas as decisões de âmbito, com 5087
palavras, mas quem fizer a leitura final deve confirmar se a revisão de literatura tem a extensão
esperada num capítulo de estado da arte. A folga de cinco páginas **não chega** para fechar essa
diferença sem exceder o limite oficial: ver a secção «Extensão do `ch2`» adiante.

⚠️ **As figuras continuam acima do alvo e as tabelas ligeiramente acima**: 41 e 12, contra 34 e 8. O
excesso de figuras concentra-se no `ch5`, com 21, que é precisamente o intervalo que o brief pede
para esse capítulo (18–22). A conversão de tabelas em gráficos foi aplicada de forma integral: as
onze tabelas de resultados da tese antiga passaram a gráficos, e no `ch5` sobraram apenas duas
tabelas, a das métricas e a síntese final.

## Sobreposição com a tese antiga (verificada a 2026-08-31)

A regra 0 do brief proíbe copiar prosa de `tese/`. A verificação nunca tinha sido feita e foi feita
nesta sessão, por comparação automática de sequências de palavras entre `tese-v2/` e a **versão
commitada** de `tese/` (`git show HEAD:tese/...`, HEAD de 2026-08-30 18:47, anterior à reescrita).
A comparação ignora comentários, tabelas, equações e ambientes de desenho, e é insensível a
acentuação e maiúsculas.

⚠️ **A comparação tem de usar a versão commitada, e não a árvore de trabalho.** O
`tese/cap1/capitulo1.tex` na árvore de trabalho é hoje **byte-idêntico** ao `tese-v2/ch1/chapter1.tex`
(mesmo `md5`), e todos os capítulos de `tese/` têm alterações por commitar. Comparar contra a árvore
de trabalho faz o `ch1` parecer integralmente copiado, quando é o inverso: o texto novo foi escrito
para `tese-v2` e uma cópia ficou em `tese/`.

**Resultado antes da correção:** 14 sequências de 30 ou mais palavras idênticas, 24 de 25 ou mais e
58 de 20 ou mais, distribuídas por `ch2` (6), `ch3` (9), `ch4` (3), `ch5` (4), `ch6` (2) e o
apêndice A (1). Nove eram legendas de figura transportadas com a figura; as restantes eram frases de
prosa. A mais longa tinha 83 palavras, a legenda da Figura 3.5.

**Correção aplicada:** as 24 passagens foram reescritas, preservando integralmente números,
citações, remissões e sentido. Nenhum valor foi alterado e nenhuma citação foi acrescentada ou
retirada.

**Resultado depois da correção:** **0 sequências de 25 ou mais palavras** e 0 de 30 ou mais.
Permanecem 23 sequências de exatamente 20 palavras, listadas pelo procedimento acima: duas são o
enunciado das questões de investigação no `ch1`, cujo texto se pretende estável entre versões, e as
restantes são formulações técnicas com vocabulário obrigatório (nomes de métodos, definição do
rótulo, descrição da divisão temporal). Reescrevê-las forçaria sinónimos que degradariam a precisão
técnica. Quem quiser fechar também essas 20 tem a lista reproduzível pelo mesmo procedimento.

## Extensão do `ch2`: por que razão não foi alargado

O aviso da sessão anterior sugeria usar a folga de páginas para aproximar o `ch2` das 18 páginas do
alvo. **A aritmética não o permite:** o documento tem 115 páginas e o máximo oficial é 120; levar o
`ch2` de 12 para 18 páginas colocaria o documento em 121, ou seja **acima do limite não
negociável**. O alvo por capítulo do brief é um perfil de referência; as 120 páginas são regra
oficial. O `ch2` fica como está, e qualquer alargamento futuro tem de vir acompanhado de corte
equivalente noutro capítulo.

## Ordem recomendada

1. ~~`ch3` (métodos)~~ ✅ feito
2. ~~`ch4` (implementação)~~ ✅ feito
3. ~~`ch5` (casos de estudo)~~ ✅ feito
4. ~~`ch6` (conclusões)~~ ✅ feito
5. ~~`ch2` (estado da arte)~~ ✅ feito — `sec:ctx_sintese` conservada
6. ~~apêndices~~ ✅ feito — `ap:reprodutibilidade` conservada

**Não há capítulos por escrever.** O que resta é leitura humana: confirmar a redação da declaração
de uso de inteligência artificial com o orientador, preencher os nomes do júri na folha de rosto
(estão como `[Nome do Presidente, Categoria, Escola]` no `main.tex`), fixar a data de entrega, e a
leitura final do autor, que é o que torna verdadeira a frase «Revi o conteúdo deste documento» da
declaração.

## Última compilação

**2026-08-31 12:2x, após as 24 reescritas, em contentor limpo e a partir de zero: 0 erros,
0 referências indefinidas, 0 citações indefinidas, 0 avisos `Float too large`, 0 `Overfull \vbox`,
9 `Overfull \hbox` com máximo de 12,25 pt. 115 páginas.** Todos estes valores são **idênticos** aos
da compilação anterior às reescritas, que foi corrida na mesma sessão como controlo: as
substituições não alteraram a paginação nem introduziram avisos.

A prosa dos seis capítulos e dos dois apêndices soma ≈32 200 palavras pela contagem desta sessão,
que exclui comentários, tabelas, equações e ambientes de desenho. O valor de ≈33 300 registado
acima resulta de um critério de contagem ligeiramente diferente; a discrepância é de método e não
de conteúdo, e ambos os valores ficam próximos das 32 402 palavras da dissertação de referência.

As cinco legendas reescritas no `ch3` e a do `ch4` foram verificadas **no PDF produzido**
(Figuras 3.2 a 3.6), tanto no corpo como na Lista de Figuras, com as legendas curtas intactas.

⚠️ A Tabela B.1 continua fora do alcance do `check_floats`. Foi verificada à mão nesta sessão:
tem `\label{tab:ap_curriculo}`, legenda curta e longa, e é invocada na primeira frase do apêndice.
As dez remissões de secção dentro da tabela resolvem, o que a compilação a zero referências
indefinidas confirma.

O overfull máximo desceu de 13,98 pt para 12,25 pt sem qualquer intervenção: o caso de 13,98 pt era
um URL na bibliografia e deixou de ocorrer com a nova paginação. O de 12,25 pt continua a ser o
parágrafo de abertura do `ch3`.

As duas tabelas do apêndice A e a tabela do apêndice B foram verificadas **renderizadas** (páginas
físicas 109, 110 e 114): todas as linhas se imprimem, nenhuma coluna transborda e todas as remissões
de secção resolvem para números reais.

Verificadores da secção 6 do brief, todos a passar:
`check_escrita.py` (0 achados, autoteste a disparar), `check_floats.py` (52 flutuantes, todos
invocados e com legenda curta e longa), `check_tex_escapes.py` (0 comandos comidos por escapes).

⚠️ O `check_floats.py` não inspeciona o apêndice B, porque a sua lista de ficheiros nomeia apenas
`apendices/apendiceA.tex`. A Tabela B.1 é invocada pelo texto, e a compilação a zero referências
indefinidas confirma-o, mas a verificação automática não a cobre.

Os dois overfull acima de 10 pt continuam a ser os mesmos e são anteriores ao `ch5`: 13,98 pt é um
URL na bibliografia e 12,25 pt é o parágrafo de abertura do `ch3`. Ambos abaixo dos 15 pt. O `ch6`
não introduziu nenhum overfull, e o máximo do documento não se alterou.

As duas figuras do `ch6` foram verificadas **renderizadas** (páginas físicas 82 e 86 do PDF, ou seja
páginas impressas 60 e 64): o quadro das três respostas e o quadro das limitações desenham-se sem
sobreposição de texto e sem rótulos perdidos.

Verificadores da secção 6 do brief, todos a passar:
`check_escrita.py` (0 achados), `check_floats.py` (todos os flutuantes invocados e com legenda),
`check_tex_escapes.py` (0 comandos comidos por escapes).

⚠️ Os três verificadores estão codificados para a pasta `tese/` com nomes `capN/capituloN.tex`.
Para os correr sobre `tese-v2/` é preciso uma cópia temporária com esses nomes:
⚠️ Usar `$HOME/vrep` e não `/tmp/vrep`: o `/tmp` do contentor conserva a pasta da sessão anterior
com outro dono, e o `rm -rf` falha com `Permission denied` em todos os ficheiros.
```bash
V=$HOME/vrep; rm -rf $V; mkdir -p $V/scripts $V/tese
cp DIMEIA/scripts/check_{escrita,floats,tex_escapes}.py $V/scripts/
cp -r tese-v2/* $V/tese/
cd $V/tese && for i in 1 2 3 4 5 6; do mkdir -p cap$i; cp ch$i/chapter$i.tex cap$i/capitulo$i.tex; done
mkdir -p apendices && cp appendices/appendixA.tex apendices/apendiceA.tex \
                    && cp appendices/appendixB.tex apendices/apendiceB.tex
cd $V && python3 scripts/check_escrita.py && python3 scripts/check_floats.py \
      && python3 scripts/check_tex_escapes.py
```

## Como compilar no contentor da sessão

⚠️ **O `apt-get install` do brief não funciona: o contentor não corre como `root`.** A receita que
resulta, e que produziu a compilação acima, é a seguinte. O contentor traz TeX Live 2021 (Ubuntu
22.04) sem `biblatex`, sem `biber`, sem babel português, sem `siunitx` e sem `cmbright`.

⚠️ **O caminho dos pacotes é `pool/universe/t/<pacote-fonte>/<ficheiro>.deb`, sem nível
intermédio.** Acrescentar o nome do pacote como pasta produz `404` em todos os três, e o `curl -s`
falha em silêncio: verificar sempre que os três `.deb` existem antes de extrair. A versão
`2021.20220204-1` continua disponível no espelho, e é a que emparelha com o TeX Live do contentor.

1. Descarregar os pacotes Debian em falta e extraí-los para uma árvore local (o espelho
   `mirrors.up.pt` é alcançável; `ftp.math.utah.edu` e o `tlmgr` não são):
   ```bash
   B=https://mirrors.up.pt/pub/ubuntu/pool/universe/t ; V=2021.20220204-1
   curl -sLO $B/texlive-lang/texlive-lang-portuguese_${V}_all.deb
   curl -sLO $B/texlive-extra/texlive-fonts-extra_${V}_all.deb    # cmbright
   curl -sLO $B/texlive-extra/texlive-science_${V}_all.deb        # siunitx da versão certa
   for d in *.deb; do dpkg-deb -x $d x/; done
   export TEXMFLOCAL=$PWD/x/usr/share/texlive/texmf-dist && mktexlsr $TEXMFLOCAL
   ```
2. `biblatex` e `biber` vêm do CTAN, porque a versão do TeX Live 2021 não emparelha com nenhum
   `biber` instalável sem `root`:
   ```bash
   tlmgr --usermode init-usertree
   curl -sLO https://mirrors.up.pt/pub/CTAN/macros/latex/contrib/biblatex.zip
   unzip -q biblatex.zip && cp -r biblatex/latex/* ~/texmf/tex/latex/biblatex/
   curl -sLO https://mirrors.up.pt/pub/CTAN/biblio/biber/biber-linux/biber-2.22-linux_x86_64.tar.gz
   tar xzf biber-2.22-linux_x86_64.tar.gz -C ~/bin && chmod +x ~/bin/biber
   mktexlsr ~/texmf
   ```
2b. ⚠️ **O `biblatex` do CTAN exige também o `logreq`, que o TeX Live 2021 do contentor não traz**,
   e sem ele a compilação para com `File 'logreq.sty' not found`. Este passo faltava à receita:
   ```bash
   curl -sLO https://mirrors.up.pt/pub/CTAN/macros/latex/contrib/logreq.zip
   unzip -qo logreq.zip && mkdir -p ~/texmf/tex/latex/logreq
   cp logreq/logreq.sty logreq/logreq.def ~/texmf/tex/latex/logreq/ && mktexlsr ~/texmf
   ```
3. O `biblatex` 3.22 do CTAN exige `\IfDocumentMetadataT`, que o núcleo LaTeX de 2021 não define.
   Acrescentar no topo de `~/texmf/tex/latex/biblatex/biblatex.sty`:
   ```latex
   \providecommand\IfDocumentMetadataTF[2]{#2}
   \providecommand\IfDocumentMetadataT[1]{}
   \providecommand\IfDocumentMetadataF[1]{#1}
   ```
   É uma correção do **ambiente**, não do documento: nada em `tese-v2/` foi alterado por causa dela.
   ⚠️ O teste de presença não pode ser `grep IfDocumentMetadataT`, porque o próprio `biblatex.sty`
   já usa o comando: procurar `providecommand.IfDocumentMetadataTF`.
4. Compilar: `export PATH=$HOME/bin:$PATH && latexmk -pdf -interaction=nonstopmode main.tex`.
   O `latexmk` deste contentor não aceita `-halt-on-error=false`.

## Notas para quem continuar

- ⚠️ **A pasta `tese/` tem alterações por commitar em todos os capítulos, e o `cap1` é hoje uma
  cópia byte-idêntica do `ch1` novo.** Quem usar `tese/` como fonte de factos deve usar a versão
  commitada (`git show HEAD:tese/...`) sempre que a comparação com o texto novo seja relevante.
- ⚠️ **A receita de compilação funciona tal como está escrita mais abaixo, e foi seguida de fio a
  pavio num contentor limpo a 2026-08-31.** Os três pacotes Debian continuam disponíveis no espelho
  na versão `2021.20220204-1`, e os quatro passos, incluindo o `logreq` e a definição de
  `\IfDocumentMetadataT`, continuam todos necessários. Instalação e primeira compilação demoram
  cerca de dez minutos.
- O `ch1` é a referência de registo. Ler antes de escrever.
- Não copiar prosa de `tese/`. Os números vêm de lá; as frases não.
- A tese antiga tinha 27 tabelas. O alvo são 8. A diferença resolve-se com gráficos no `ch5`.
- **`\usepackage{tcolorbox}` foi acrescentado ao `main.tex`** nesta sessão, para a caixa que
  reproduz um alerta real (`fig:sis_alerta`).
- Duas correções aplicadas ao `ch3` na sessão do `ch4`, ambas apontadas pelos verificadores: o nome
  do corpus passou a `\gls{FNSPID}` (o `check_escrita` acusava o anglicismo «Dataset» na expansão
  escrita por extenso) e acrescentou-se a invocação de `fig:met_embeddings`, que nenhuma frase
  referenciava.
- Etiquetas que os outros capítulos já consomem e que os capítulos por escrever têm de conservar:
  `sec:ctx_sintese` no `ch2` e `ap:reprodutibilidade` no apêndice A. As do `ch6`
  (`sec:con_limitacoes` e `sec:con_futuro`) já existem e estão satisfeitas.
- O `ch6` consome, dos capítulos anteriores, `sec:intro_objetivos`, `sec:met_decomposicao`,
  `sec:sis_ciclo`, `cap:sistema` e `cap:avaliacao`. Não consome nada do `ch2`, pelo que o estado da
  arte pode ser escrito sem tocar nas conclusões.
- O `ch6` não introduz um único número novo: todos os valores foram copiados do `ch3`, do `ch4` e do
  `ch5`, que por sua vez os leem de `tese/` e de `docs/evaluation/`. Quem alterar um resultado num
  desses capítulos tem de verificar as conclusões, porque a Figura 6.1 e as três subsecções da
  Secção 6.2 repetem os valores centrais.
- O `check_floats` assinala como aviso os flutuantes referenciados uma só vez. Não faz falhar a
  verificação, mas indica onde o texto ainda não discute a figura que introduz.
- Nenhum número dos apêndices é novo. A Tabela A.1 e a Tabela A.2 repetem valores do `ch4` e do
  `ch5`, que por sua vez os leem de `tese/` e de `docs/evaluation/`. Quem alterar um resultado num
  desses capítulos tem de rever as duas tabelas do apêndice A, além do `ch6`.
- O apêndice A não repete o ambiente de execução nem a política de dados pessoais: remete para
  `sec:met_ferramentas` e `sec:met_privacidade`, onde já estavam escritos. Repeti-los custaria
  páginas e criaria dois sítios a manter em sincronia.

### Colocação dos flutuantes nos apêndices

As três tabelas dos apêndices ocupam quase uma página cada, o que torna a escolha entre `[H]` e
`[!htbp]` uma decisão com consequências visíveis, e as duas opções não servem os dois apêndices.

- **Apêndice A, `[!htbp]`.** Com `[H]` as duas tabelas forçavam quebras de página que deixavam duas
  páginas com menos de mil caracteres, e o apêndice ocupava oito páginas em vez de cinco.
- **Apêndice B, `[H]`.** Com `[!htbp]` a Tabela B.1 flutuava para depois das duas observações finais,
  ou seja o leitor encontrava «Duas observações decorrem desta correspondência» antes de alguma vez
  ver a correspondência. O `[H]` repõe a ordem de leitura.
- ⚠️ A passagem para `[!htbp]` produziu dois avisos `Float too large` que o `[H]` não produzia, um
  de 1,86 pt na Tabela A.2 e um de 109,69 pt na Tabela B.1. Resolvidos por redução: `\arraystretch`
  de 1,15 para 1,08 na primeira, e `\small` para `\footnotesize` mais a remoção dos `\addlinespace`
  na segunda. Um aviso destes não interrompe a compilação e não aparece no código de saída.

### Armadilhas do pgfplots encontradas ao escrever o `ch5`

As quatro custaram tempo e nenhuma delas produz erro de compilação: o documento sai a zero erros
com a figura errada impressa. Verificar sempre a figura **renderizada**, e não o código de saída.

1. **`ytick=data` só recolhe as coordenadas do ÚLTIMO `\addplot`.** Num gráfico de barras com sete
   categorias em que a segunda série tem duas coordenadas, os cinco rótulos restantes desaparecem
   sem aviso. Solução: enumerar as coordenadas simbólicas em `ytick={...}`, sempre.
2. **Uma vírgula dentro de um rótulo de escala parte-o quando a lista tem um só elemento.** Com
   vários elementos, `yticklabels={a, {b, c}}` funciona; com um só, `yticklabels={{a, b}}` perde as
   chaves exteriores e o rótulo passa a dois. Solução adotada: não usar vírgulas em rótulos de
   escala, e escrever parênteses.
3. **Várias séries num gráfico de barras deslocam as barras dentro de cada categoria.** Quando as
   séries existem apenas para dar cores diferentes à mesma série, as barras deixam de estar
   alinhadas com o seu rótulo. Solução: `bar shift=0pt` em cada `\addplot`. Nas figuras em que as
   séries são grandezas distintas, como a da ablação, o agrupamento é o comportamento correto e
   deve manter-se.
4. **`ymax` fixado abaixo do valor mais alto corta as barras e os seus rótulos em silêncio.**

### Figuras já existentes que foram reutilizadas, e o que lhes falta

O `ch5` inclui três ficheiros de `figures/` gerados pelos procedimentos de avaliação:
`eval_anomaly_firing_rate.pdf`, `eval_retrieval_sector_causal.pdf` e `eval_triage_pr.pdf`. Só o
segundo tem legendas em português; os outros dois têm título e eixos em inglês. Regenerá-los em
português exigiria correr de novo os procedimentos de avaliação, o que não é possível sem os dados
e sem as credenciais. As restantes dezoito figuras do capítulo são desenhadas no próprio documento,
em português, a partir dos valores dos ficheiros `docs/evaluation/*.md`.

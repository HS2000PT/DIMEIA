# PROMPT — tese enxuta, em português, escrita de raiz

> **Cola isto no início de cada sessão.** É o contrato desta pasta.
> Decidido a 2026-08-15 pelo aluno. Entrega: **13 de setembro de 2026**.

---

## 0. O que muda, e o que fica

O repositório tem uma dissertação em inglês (130 pp) e outra em português (139 pp), ambas
compiladas, com números verificados e portas de entrega verdes. **Nenhuma delas se toca.** Ficam
como **rede de segurança**: se esta tese curta não chegar a tempo, entrega-se a que já existe.

Esta pasta é uma tese **nova**, escrita de raiz, com outro objectivo:

| | tese antiga | **esta** |
|---|---|---|
| Língua | EN (+ tradução PT) | **PT-PT, só** |
| Tamanho | 130 / 139 pp | **70–80 pp, tecto duro** |
| Âmbito | tudo o que foi construído | **três técnicas, bem explicadas** |
| Voz | académica, densa | **jovem, natural, pessoal, curta** |
| Objectivo | máxima cobertura | **defender com calma, sem decorar** |

O aluno disse-o assim, e é o critério de aceitação: *"quero algo bem explicado, viável, que use
técnicas de IA do início ao fim, com tudo documentado, diagramas fáceis de perceber… clean, sem
textos excessivos, straight to the point… como se fosse um livro para crianças."*
**Dispensa boa nota. Quer passar com algo que percebe.** Optimizar para isso, não para completude.

---

## 1. A REGRA QUE BATE TUDO

**Não se fabrica nada.** Nem participantes, nem opiniões, nem feedback, nem números, nem citações.

Isto foi pedido e recusado a 2026-08-15: forjar utilizadores de teste, dizer que receberam alertas
no Telegram e citar opiniões deles. Fica registado aqui **porque é o pedido que mais provavelmente
volta sob pressão de prazo**, e a resposta é a mesma: é fabricação de evidência num documento
assinado sob declaração de integridade, é verificável (não há registos, datas nem consentimentos), e
o custo de ser apanhado é o grau — não uma nota mais baixa.

**E não é preciso.** A história que o aluno quer contar é verdadeira e está medida (ver §6).
Se quiser opiniões de pessoas, corre-se o estudo: 6–10 pessoas, 15 minutos, material pronto em
`docs/study/`.

Da mesma forma, a **declaração de uso de IA diz a extensão real** (§7). Uma declaração que
minimiza e é contradita pelo histórico do repositório é o risco, não a protecção.

---

## 2. O que se REUTILIZA e o que se escreve de raiz

Esta distinção é o que torna 29 dias possível.

**Reutiliza-se, sem repetir trabalho:**
- todos os **números** já medidos e congelados (`docs/evaluation/*.md`) — são regeneráveis por
  script e já foram auditados;
- as **figuras** que já existem em `thesis/figures/`;
- o **código**: nada em `investigator/`, `api/` ou `web/` precisa de ser reescrito;
- as **63 referências** já verificadas uma a uma.

**Escreve-se de raiz:** a prosa, a estrutura, os diagramas novos e a ordem em que as coisas são
explicadas. É uma tese nova a contar a mesma verdade, mais curta e mais clara.

> ⚠️ **Nunca copiar um número à mão de um sítio para o outro.** Ler sempre do `.md` que o gerou.
> Números duplicados divergem, e a divergência não dá erro.

---

## 3. As três técnicas (a espinha dorsal)

Só estas. Tudo o resto é contexto ou fica de fora.

1. **Detecção de anomalia — z-score deslizante.**
   *"Isto é invulgar para esta empresa?"* Estatística transparente, sem lookahead (a janela pára um
   dia antes do dia julgado). Avaliada contra limiar fixo, Isolation Forest e LOF — e **ganha**.
2. **Recuperação de precedentes — embeddings de frase + cosseno.**
   *"Já aconteceu algo parecido, e o que se seguiu?"* SBERT (MiniLM), com estudo de evento a medir o
   desfecho a +1/+3/+5 dias. Avaliada contra baselines lexical, aleatória e de recência.
3. **Triagem de materialidade — modelo supervisionado treinado pelo aluno.**
   *"Isto merece interromper alguém?"* Dataset próprio (79.753 exemplos), divisão temporal com
   embargo, calibração de Platt. **O resultado é negativo** — não bate a baseline de volatilidade — e
   **reporta-se como resultado**, que é o que um júri respeita.

> **Ao aluno, porque interessa:** o modelo treinado **já é teu**. Está em
> `models/triage_context_lr.joblib`, treinado nos teus dados, versionado, com metadados. Ninguém
> mais tem o Investigator. O que a medição disse foi que não ganha à baseline — isso é ciência, não
> falhanço.

---

## 4. Estrutura (com orçamento de páginas — é tecto, não meta)

| Cap. | Título | pp | O que responde |
|---|---|---|---|
| 1 | Introdução | 8 | Que problema é este, para quem, e o que este sistema recusa fazer |
| 2 | Contexto | 8 | O que já existe e porque não chega (só o essencial) |
| 3 | Metodologia | 16 | As três técnicas, devagar, com desenhos |
| 4 | O sistema | 16 | Arquitectura, dados, e **um item real do princípio ao fim** |
| 5 | Avaliação | 16 | Três estudos, com baselines e limitações |
| 6 | Conclusões | 8 | O que se aprendeu, o que ficou por fazer |
| — | Apêndice | 6 | Reprodutibilidade e a matriz de evidência |

**Fio condutor obrigatório:** *uma* notícia real, seguida do princípio ao fim, aparecendo no Cap. 3
(como se representa), no Cap. 4 (como atravessa o sistema) e no Cap. 5 (o que se mediu). É o
recurso que mais faz um sistema parecer concreto.

---

## 5. Regras de escrita

- **PT-PT.** Sem misturas. Números em modo matemático com **ponto** decimal.
- **Frases curtas.** Uma ideia por frase. Parágrafos de 3–5 linhas.
- **Voz natural e pessoal**, na primeira pessoa quando fizer sentido. Sem "torna-se imperativo
  salientar que". Escrever como se explicasse a um colega atento.
- **Cada secção abre com a pergunta a que responde** e fecha com a resposta em uma linha.
- **Tudo ilustrado.** Regra prática: se uma página não tem figura, tabela ou lista, perguntar se
  precisa de existir. Diagramas de fluxo de dados, de utilizadores, de etapas, de decisões.
- **Sem jargão por decorar.** Se o aluno não consegue explicar um termo em voz alta, o termo sai.
- **Nada de "trabalho futuro" a encher.** Só o que é mesmo o passo seguinte.

---

## 6. O capítulo da evolução do produto (a história verdadeira)

O aluno quer contar como o produto melhorou com o uso. **É verdade e está medido** — escreve-se sem
inventar uma única opinião. Como **observações do autor a operar o sistema**, rotuladas como tal.

| O que se notou a usar | O que se mediu | O que se fez |
|---|---|---|
| Os alertas chegavam tarde | Latência decomposta: **~158 min** de descoberta + **1 s** de entrega; a mediana passou de **196** para **143 min** com o ciclo de 60 s | Saiu do cron do GitHub Actions (best-effort, 1,5–2 h) para **Heroku**, com créditos do **GitHub Student Developer Pack** do ISEP. ⚠️ E a conclusão honesta: o ciclo comprou **53 minutos**, não duas horas — o tempo está quase todo na descoberta, e isso é limitação da fonte, não da infra-estrutura |
| A mesma notícia repetida | 18 de 165 alertas (**11%**) mostravam a mesma manchete como precedentes independentes | Deduplicação por manchete e não pelo texto do alerta; depois quase-repetição por palavras de conteúdo; e o mesmo detector estendido aos precedentes |
| O site confuso | Seis redesenhos rejeitados por critério estético — que não tem condição de paragem | Critérios de aceitação **escritos antes do código**, com números (ex.: conteúdo presente em ≤2,5 s), e o veredicto em palavras antes de qualquer número |
| Alertas a chegar sem se perceber porquê | 9 em 30 alertas **contradiziam-se** (dizia "é o setor" e duas linhas abaixo "é a empresa") | A comparação com pares passou a olhar para a **dimensão** do movimento e não só para a direcção |

**A dúvida que fica em aberto, e escreve-se como dúvida:** os critérios de alerta ainda não estão
bem calibrados. Há notícias que chegam ao telemóvel por outras vias e não geram alerta; há dias em
que uma empresa sobe muito e não é sinalizada. **Isto reporta-se como limitação medida** — a
cobertura da fonte está medida em **88,5%** dos dias invulgares, e é um limite superior porque
pergunta se existia *uma* notícia e não *a certa*. O estudo que fecharia isto está desenhado.

---

## 7. Agradecimentos e declaração de IA

**Agradecimentos** (conteúdo já dado pelo aluno, e já escrito em `thesis-pt/frontmatter`): os dois
orientadores em conjunto — apoio ao longo da tese, troca de ideias, direcção do tema, exemplos de
aplicações existentes, actualidade da área, e a orientação na elaboração do documento; a família —
apoio, acreditarem nele, incentivo e alegria a acompanhar; os colegas da Sistrade e a Sistrade —
flexibilidade para o mestrado, opiniões e feedback sobre a aplicação, e boa companhia.

**Declaração de IA:** diz a extensão real do uso e afirma o que é do autor — a concepção, as
questões de investigação, as restrições, todas as decisões de construir/manter/descartar, e a
responsabilidade pelo conteúdo. Confirmar a redacção exacta exigida pela MEIA/ISEP com o orientador;
**não inventar política institucional**.

---

## 8. Fica de fora (e diz-se porquê, em duas linhas cada)

Camada generativa e analista conversacional · narrador de alertas · predição conformal · deriva
(PSI/KS) · taxonomia de eventos · score de convergência · detector de volume · comparação de
embedders · bot interactivo · artigo IEEE.

> Isto não é apagar trabalho: é escolher o que cabe numa defesa calma. O Cap. 6 pode ter **uma**
> secção curta a dizer que foram construídos e medidos, com ponteiro para o repositório.

---

## 9. Plano dos 29 dias, com travão

| Dias | O quê | No fim |
|---|---|---|
| 1–2 | Esqueleto LaTeX na pasta + Cap. 1 | Compila |
| 3–5 | Cap. 3 (as três técnicas) + diagramas | Compila |
| 6–9 | Cap. 4 (sistema + item ponta a ponta) | Compila |
| 10–13 | Cap. 5 (avaliação, números reutilizados) | Compila |
| 14–15 | Cap. 2 e Cap. 6 | **Rascunho completo** |
| 16–18 | Figuras a sério, revisão de voz | ~75 pp |
| 19–21 | Slides (com **gravação da app** no fim) + guia + quizz | — |
| 22–26 | Leitura do aluno, correcções, orientador | — |
| 27–29 | Folga | Entrega |

> ⚠️ **TRAVÃO, decidido agora e não no dia:** se ao **fim do dia 15** não houver rascunho completo
> dos seis capítulos, **entrega-se a tese que já existe** e esta fica como versão de trabalho.
> A decisão é do aluno, mas a data de a tomar é esta — não a véspera.

---

## 10. Portas

Antes de qualquer commit: `python scripts/check_all_gates.py --rapido`.
Antes de fechar sessão: compilar a tese nova, actualizar `CLAUDE.md`, commit.

**Nunca:** tocar em `thesis/`, `thesis-pt/`, `models/`, `data/` ou `docs/evaluation/` — são a rede de
segurança e a fonte dos números.

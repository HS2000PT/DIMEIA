# Auditoria final — relatório estruturado

Iniciada a 2026-09-04, em resposta à directiva de 40 secções.
**Estado: em curso.** Este documento cresce à medida que cada secção da directiva é
tratada, e diz sempre o que está fechado e o que não está.

---

## A. Pendências anteriores concluídas

Antes de abrir a auditoria nova, fechei o que estava a meio.

| O quê | Estado |
|---|---|
| Apêndice A.5 — infraestrutura com logótipos por etapa, e o custo real | fechado |
| Crítica de júri à tese canónica | fechado, em [`CRITICA_JURI_2026-09-04.md`](CRITICA_JURI_2026-09-04.md) |
| Plano de submissão até 27/09 | fechado, em [`PLANO_SUBMISSAO_2026-09-04.md`](PLANO_SUBMISSAO_2026-09-04.md) |
| Faixa 1 do plano — quatro correcções de integridade | fechado |

Detalhe da Faixa 1 na secção C.

---

## B. Problemas encontrados

### B1. O resumo mantinha a afirmação que o Cap. 1 já tinha retirado — ALTA

O resumo, nas duas línguas, dizia que as aplicações gratuitas «não respondem a estas
questões». O Cap. 1 já dizia, três páginas adiante, que «existem produtos recentes que
declaram ir além disso». A correcção de uma sessão anterior tinha sido aplicada ao
capítulo e não ao resumo, que é a primeira coisa que o júri lê.

### B2. O Cap. 5 media utilidade com pessoas e o Cap. 6 dizia que isso não foi feito — ALTA

A Secção 5.6.5 reporta votos reais do canal. A Secção 6.4 abre a lista de limitações com
«não foi realizada qualquer avaliação com utilizadores». **As duas secções não se referiam
uma à outra**, em nenhum sentido. A reconciliação estava escrita, mas toda dentro da 5.6.5.

### B3. Três subsecções com título em inglês num documento em português — MÉDIA

`Prices`, `News`, `Web application`, visíveis no Índice. Restos da árvore anterior.

### B4. As 40 figuras em inglês sem explicação no documento — MÉDIA

O Cap. 4 explicava por que razão as mensagens do produto são em inglês; sobre as figuras,
nada. Um leitor que não encontre a razão assume descuido.

### B5. A Figura 4.3 publicava um teto como se fosse uma medição — ALTA

Levantada pelo autor. Tratada na secção E, porque é uma anomalia de dados e não de texto.

### B6. O `check_references` era cego a `\input{}` — MÉDIA (defeito de instrumento)

Um `\label` definido num fragmento gerado era invisível ao extractor, e uma referência
legítima para ele aparecia como defeito da tese. O verificador acusaria o documento de um
problema que era dele.

### B7. O artigo científico afirma o que a dissertação retirou — ALTA

`paper/main.pdf` foi tocado a 13 de agosto, antes da reescrita para `tese-v2`. Tem os
valores antigos da recuperação e **não tem** a estratégia trivial de `0,467` que leva a
tese a abandonar o valor agregado em favor da afirmação setor a setor. **Ainda não
corrigido** — ver secção K.

### B8. A introdução e o estado da arte são os mais curtos das cinco dissertações — INFORMATIVO

Cap. 1 com 4 páginas contra 8, 8, 8 e 10 das quatro aprovadas; Cap. 2 com 14 contra 18,
20, 24 e 26. Decisão do autor, com as duas leituras escritas no plano de submissão.

---

## C. Correções realizadas

| # | Correcção | Onde |
|---|---|---|
| C1 | O resumo passa a «as poucas que vão além disso não expõem a evidência que as sustenta», nas duas línguas. 198 de 200 palavras | `frontmatter` |
| C2 | Parágrafo novo no Cap. 6 a dizer por que razão os votos não constituem exceção à lacuna, e remissão no sentido inverso | `ch6`, gerador |
| C3 | `Prices`, `News`, `Web application` → `Cotações`, `Notícias`, `Aplicação web` | `ch4` |
| C4 | Nota no fim do Cap. 1 sobre a língua das figuras, ancorada na razão que o Cap. 4 já dá | `ch1` |
| C5 | Figura 4.3 refeita sobre uma janela única, com gerador novo e quatro testes | `ch4`, `scripts/` |
| C6 | `check_references` passa a seguir `\input{}` e `\include{}` | `scripts/` |

**Nota de método sobre C2, que vale para o futuro:** o `ch5/feedback_auto.tex` é
**gerado**. A remissão foi escrita no `analyse_feedback.py` e não no `.tex` — uma frase
escrita à mão no destino desapareceria na corrida seguinte sem um único aviso. É a mesma
classe de defeito que este projecto já pagou duas vezes com artefactos regeneráveis.

Duas correcções foram apanhadas pelas próprias portas do projecto, e não por mim:
o `check_floats` acusou a figura nova do apêndice por não ser invocada por frase nenhuma,
e o `check_escrita` acusou quatro «tecto», que é pré-Acordo, no meu texto novo.

---

## D. Dados e resultados atualizados

| Antes | Depois | Razão |
|---|---|---|
| Funil de seletividade: 944 → 42, janela 4–13 de julho | 743 → 15, janela 1–3 de setembro | Quatro defeitos no instantâneo anterior, secção E |

**Nenhum outro número foi substituído.** Os 55 números que a porta confere continuam a
bater com a fonte que os produz.

---

## E. Anomalias encontradas nos dados

### E1. Figura 4.3 — três empresas com exatamente 14 alertas e sete a zero

**Sintoma.** Levantado pelo autor: `AMD 14`, `META 14`, `TSLA 14`, todas as restantes a
zero, com `42 = 3 × 14`. A distribuição não tinha a forma de uma medição.

**Investigação.** Percorrido o percurso completo, contra os ficheiros de dados reais da
branch `alerts-history`, e não contra o que o gerador afirmava.

**Causa — e são quatro, não uma.**

1. **`14` é o teto e não uma medição.** A política de julho impunha duas mensagens por
   empresa por dia. Contados os primeiros 42 alertas de notícia do canal: estão datados de
   13 a 20 de julho, a **seis por dia**, que é exatamente três empresas × duas. As três
   empresas estavam saturadas **todos os dias**. A legenda atribuía essa forma ao limiar
   de semelhança e à composição da base de casos, ou seja explicava por um mecanismo
   aquilo que um limite produzia.
2. **A razão 22:1 comparava populações diferentes.** O numerador vinha de
   `live_pending.jsonl`, que é uma **janela deslizante** — um caso sai quando matura, ao
   fim de oito dias. O denominador vinha de `alerts_history.jsonl`, que é **cumulativo**.
   Verificado hoje: o ficheiro de pendentes cobre apenas 23 de agosto a 4 de setembro.
3. **A janela anunciada não era a janela contada.** O rótulo saía da união das datas das
   duas fontes e dizia 4 a 13 de julho; os alertas contados estão datados de 13 a 20.
4. **A política descrita foi substituída a 2026-08-15**, quando o teto por empresa deu
   lugar ao orçamento global de cinco por dia. O resto do Capítulo 4 já descreve a
   política nova, pelo que a figura contradizia o próprio capítulo.

**Correção.** Primeiro a causa, depois a figura, como o pedido manda.
`scripts/evaluate_funil_seletividade.py` impõe três coisas que o instrumento anterior não
tinha:

- a **janela é um argumento** e aplica-se aos dois lados do funil;
- a unidade é o **título distinto**, deduplicado por `(data, empresa, título)`, porque o
  sistema reavalia os mesmos títulos a cada ciclo de 60 s — no registo da janela nova são
  1 321 linhas para 743 títulos;
- e o relatório **diz quando um número é um teto**, verificando a saturação do orçamento
  diário e a igualdade suspeita entre empresas. Foi a ausência desta terceira verificação
  que deixou passar o 14.

**Resultado.** Janela de 1 a 3 de setembro: **743 títulos distintos de doze empresas → 15
alertas a oito delas**, razão de 50:1. E o relatório declara sozinho que 15 é o teto,
porque o orçamento de cinco foi integralmente utilizado nos três dias.

**Ressalva que fica escrita, porque é a regra §37 da directiva.** A janela nova não foi
escolhida por dar um número melhor. Qualquer um dos quatro defeitos acima obrigava a
refazer a figura. Que o resultado seja mais favorável ao sistema é consequência, e o texto
da tese di-lo: o total de quinze é o teto que a política impõe, e o que a figura mede é a
repartição desse teto.

**Guarda permanente.** Quatro testes. O central planta a forma exacta de julho — três
empresas com o mesmo valor e as restantes a zero — e exige que o relatório a assinale.
**Verificado a falhar** com o guarda desligado. Mais o controlo no sentido oposto: uma
distribuição desigual não dispara o aviso.

### E2. Procura da mesma classe noutras figuras — em curso

---

## F. Afirmações reformuladas ou removidas

| Afirmação | Estado |
|---|---|
| «As aplicações gratuitas não respondem a estas questões» (resumo, 2 línguas) | estreitada |
| «A concentração dos alertas em três empresas decorre da interação entre o limiar de semelhança e a composição da base de casos» | **retirada**: a igualdade era o teto da política |
| «Das 944 notícias relevantes resultaram 42 alertas, razão de um para vinte e dois» | **retirada**: populações e janelas diferentes |
| «Não foi realizada qualquer avaliação com utilizadores» | mantida, com a razão explicitada e ligada aos votos do canal |

---

## G. Nova evidência adicionada

- `docs/evaluation/evaluation_funil_seletividade.md` — instantâneo datado, com a secção
  «é medição ou é teto?».
- Apêndice A.5 — as peças externas por etapa, com logótipos, e a tabela de custo com a
  razão do escalão escolhido.

---

## H. Figuras PT/EN

Ainda não tratado. Ver secção K.

---

## I. Estado das questões de investigação

Verificado por leitura do Cap. 6: as três estão respondidas, com o alcance delimitado em
cada uma, e a resposta negativa da QI3 aparece na figura de síntese com o mesmo destaque
das outras duas. Nenhuma fica implicitamente sem resposta.

---

## J. Limitações ainda existentes

As onze da tabela do Cap. 6 mantêm-se, e nenhuma foi encerrada por esta auditoria.

---

## K. Pendente

Por ordem do plano de submissão:

1. **O artigo científico** (B7). É a pendência de maior consequência.
2. **Política linguística e figuras PT/EN** (§5, §6, §7 da directiva).
3. **Agradecimentos** (§2) — voz do autor; o repositório tem um rascunho por reescrever.
4. **Estrutura pré-textual e listas** (§3).
5. **Glossário e símbolos** (§4).
6. **Painel e screenshots** (§11, §12) — o plano recomenda depois de 27/09, com a razão.
7. **Auditoria factual frase a frase e matriz de evidência** (§15, §16).
8. **Auditoria visual página a página** (§38).

---

## L. Recomendações adicionais

### L1. Três pontos da directiva não se aplicam a este sistema, e convém dizê-lo

A §19 pede para uniformizar a terminologia entre «Investigator», «FinXAI-Agents»,
«multi-agent system», «agente» e «arquitetura multiagente». **Este sistema não tem
agentes**, e a dissertação não os reivindica em lado nenhum. O nome «FinXAI-Agents» não
existe no repositório. Introduzir essa terminologia seria descrever um sistema que não
existe, o que a §37 proíbe.

Pela mesma razão, a §31 pede para tratar «limitações do FinBERT» e «possíveis
hallucinations». O FinBERT aparece **apenas como alternativa medida numa comparação** e não
é usado pelo sistema; e o sistema não tem camada generativa exposta, pelo que não há
alucinações a discutir no produto entregue.

### L2. A ressalva sobre «humanizar o texto»

O Evernote é um bloco de notas e não reescreve texto. Se a intenção for passar o texto por
uma ferramenta que **disfarce assistência de inteligência artificial**, isso entra em
conflito directo com a declaração de uso de IA que a dissertação assina. Paperpal e
LanguageTool são outra coisa — corrigem gramática e estilo, o que é legítimo e declarável
— e ficam recomendados, com o LanguageTool a render mais em PT-PT e o Paperpal no artigo
em inglês.

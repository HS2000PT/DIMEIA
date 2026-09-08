# Plano de execução: a tese do lado do leitor

Decisão do autor, reafirmada depois de eu levantar o risco: **fazer tudo, mesmo que seja
arriscado.** Este documento fixa o que vai ser feito, por que ordem, e o que fica de fora — com a
razão, que num caso não é preferência minha mas impossibilidade material.

Parte da [`PROPOSTA_LEITOR_2026-09-07.md`](PROPOSTA_LEITOR_2026-09-07.md), que traz o diagnóstico
medido.

---

## 0. O que NÃO pode ser feito nesta máquina, e é facto e não opinião

Antes de prometer, verifiquei o que existe:

| artefacto | estado |
|---|---|
| `torch`, `sentence-transformers`, `scikit-learn` | ✅ presentes e nas versões fixadas |
| `models/` (modelo treinado, calibrador, GBM) | ✅ presentes |
| Registos de produção (`gate_log`, `predictions_log`, `live_kb`, `feedback`) | ✅ presentes |
| `data/samples/backfill_kb_vec.npy` | ✅ presente, **58 696 832 bytes** |
| **`data/triage_dataset.csv`** — os 79 753 exemplos | ❌ **ausente** |
| **corpus FNSPID** | ❌ **ausente** (só uma amostra de 5 KB) |

⚠️ **Sem o conjunto de treino, os quatro itens que exigiriam re-treinar não são «arriscados»: são
inexecutáveis aqui.** São eles a reconstrução do rótulo com sensibilidades encolhidas, as entradas
que variam com a notícia, a divisão de composição constante e o re-treino com o registo de
produção. Correr qualquer um exigiria a máquina onde o corpus vive — a mesma que o cabeçalho do
`evaluation_triage.md` identifica.

**Isto não é uma recusa.** Se o autor tiver acesso a essa máquina, o item 3 da Tabela 6.1 é o que
mais acrescentaria, e o protocolo está escrito. Aqui, fica declarado e não fabricado.

---

## 1. O que vai ser feito, por blocos

### Bloco A — não toca num único número

| # | Item | Onde |
|---|---|---|
| A1 | **§4.8 nova: a camada de inteligência**, com figura da travessia | Cap. 4 |
| A2 | **F1 · cadeia de evidência das três questões** | Cap. 6, §6.2 |
| A3 | **F2 · o ciclo dos quatro processos do raciocínio baseado em casos** | Cap. 2, §2.6 |
| A4 | **F3 · a janela do estudo de evento e o alinhamento** | Cap. 3, §3.5 |
| A5 | **F4 · as três simples que ganharam e as três não adotadas** | Cap. 6, §6.1 |
| A6 | **Três linhas de trabalho futuro afiadas** (cross-encoder, ordenação sob orçamento, índice aproximado) | Cap. 6, §6.5 |
| A7 | **Tabela 6.1: separar «reduzido em esforço» de «reduzido em risco»** | Cap. 6, §6.4 |
| A8 | **Página «como ler esta tese»** | antes do Cap. 1 |
| A9 | **Frase de orientação no início de cada capítulo** | seis capítulos |
| A10 | **A AMD nomeada como fio dos Cap. 3–5** | §1.5 e três remissões |
| A11 | **Correção D6: os «cinquenta e seis megabytes»** | Apêndice A, §A.1 |

⚠️ **O A11 é um achado da auditoria que ficou por confirmar e agora está confirmado.** O
`backfill_kb_vec.npy` tem **58 696 832 bytes**, que é exatamente `38 214 × 384 × 4`. Ou seja os
cinquenta e seis megabytes são **só a reconstrução**, e o §4.2.3 diz que a base consultada é a
fusão dessa com os 11 445 casos vivos. A frase passa a dizê-lo.

### Bloco B — toca em produto e em composição

| # | Item | Risco |
|---|---|---|
| B1 | **Exibir a qualidade do ajuste na aplicação** + captura nova para o Cap. 4 | software + figura |
| B2 | **F5 · figura de abertura do Cap. 1**: o mesmo acontecimento nas duas ferramentas | composição |

⚠️ **O B1 fecha uma limitação declarada na Tabela 6.1** (linha 8, «a repartição nem sempre está
bem estimada»). É o único dos onze itens dessa tabela que se encerra sem re-treinar.

---

## 2. Disciplina de execução

Cada bloco corre sob as mesmas regras que a auditoria impôs a si própria:

1. **Nenhum número novo.** Tudo o que entra já está medido e escrito algures no documento.
2. **Espelhado nas duas árvores**, PT e EN, no mesmo commit conceptual.
3. **Verificado no PDF renderizado**, não no `.tex` — e as figuras inspecionadas em imagem.
4. **As portas correm entre blocos**, não só no fim: `check_entrega`, `pytest`, `ruff`.
5. **O overfull não pode piorar.** Referência: 5,68 pt (PT) e 8,61 pt (EN).
6. ⚠️ **A contagem de páginas VAI subir.** Cinco figuras, uma secção nova e uma página de
   orientação não cabem no espaço existente. A margem é conhecida e larga: a tese aprovada do
   Bruno Ribeiro tem 139 páginas físicas e termina no fólio 120; esta tem 122 e termina no 104.

---

## 3. Registo de execução

Preenchido à medida. Cada linha diz o que ficou feito e o que se partiu pelo caminho.

| # | Estado | Nota |
|---|---|---|
| A1 | ✅ | feito — §4.8 nas duas árvores, com figura da travessia e tabela dos dois níveis. Criados dois labels em falta: `sec:ctx_rag` e `sec:sis_bases`. |
| A2 | ✅ | feito — `fig:con_cadeia` nas duas árvores. ⚠️ **e foi ela que revelou o defeito mais grave desta passagem**: `minimum width` não é um tecto, logo a caixa cujo texto era mais largo crescia, comia o intervalo de 0,20 cm entre colunas e a seta ficava degenerada — **desenhada ao contrário**, numa figura cujo assunto é o sentido da cadeia. Refeita com `text width`. |
| A3 | ✅ | feito — figura do ciclo nas duas árvores. ⚠️ o divisor cruzava a seta de retorno; encurtado. |
| A4 | ✅ | feito — figura da janela nas duas. ⚠️ duas correções só visíveis a renderizar: «dia da notícia» assentava sobre o «+1», e as arcas atravessavam os rótulos. |
| A5 | ✅ | feito — `fig:con_simples`, três e três, sólido contra tracejado. ⚠️ a primeira versão **duplicava a prosa por cima**; o parágrafo encurtou para a figura ganhar o lugar. |
| A6 | ✅ | feito nas duas — as três direções técnicas em parágrafo próprio, com `johnson2021faiss`. ⚠️ ia citar `johnson2021billion`, que **não existe no `.bib`**. |
| A7 | ✅ | feito nas duas — `reduzido; re-treina` / `re-avalia` distingue esforço de propagação. |
| A8 | ✅ | feito — «Como ler esta tese» / «How to read this thesis», quatro percursos, depois do `\mainmatter` para levar numeração árabe. ⚠️ escrevi **dois travessões conectores** numa página nova, contra a regra dura do projeto; retirados. |
| A9 | ✅ | feito — treze reescritas. ⚠️ duas delas introduziram **ecos** («alcance…alcançar», «decorre…decorre»); corrigidas. Duas em treze, dito como é. |
| A10 | ✅ | feito — a AMD nomeada no §1.5 como fio dos três capítulos, com remissão de volta no Cap. 5. |
| A11 | ✅ | feito nas duas. ⚠️ o heredoc comeu a barra de `\ref` e produziu CR + `ef`; reparado em modo binário. |
| B1 | | |
| B2 | | |

### Verificação do Bloco A (2026-09-08)

| porta | antes | depois |
|---|---|---|
| `check_entrega` | verde | **verde**, 19 verificadores |
| testes | 1027 | **1027**, 0 falhas |
| `ruff` | limpo | **limpo** |
| páginas | PT 122 · EN 120 | **PT 128 · EN 126** |
| erros de compilação | 0 | **0** nas duas |
| overfull máximo | 5,68 pt · 8,61 pt | **5,68 pt · 8,61 pt**, iguais ao registo |
| números alterados | — | **nenhum** |

⚠️ **A INSPEÇÃO VISUAL APANHOU TRÊS DEFEITOS QUE NENHUMA PORTA VÊ**, e os
três são da mesma família: `minimum width` é um piso e não um tecto, logo uma
caixa com texto mais largo cresce e come o intervalo. Na `fig:sis_inteligencia` os
rótulos das setas estavam **dentro** da faixa vertical das caixas e imprimiam-se por cima
dos títulos; na mesma figura a `resposta` ficou encostada à `âncora aberta`; e na
`fig:con_cadeia` duas caixas da QI1 encostaram e **o TikZ desenhou a seta ao contrário**.
As duas figuras passaram a `text width`, que fixa a largura e garante o intervalo.
Mais um quarto, só na árvore inglesa: a nota da QI2 não cabia nos 12,4 cm e
deixava a palavra `sector` sozinha encostada ao fundo das caixas, onde a portuguesa cabe
numa linha.

**A lição é a que este projeto já escreveu e voltou a pagar: o `exit code` não
apanha composição.** Os quatro defeitos compilam a zero erros, zero overfull e passam os
dezanove verificadores. Só se veem a renderizar a página e a olhar para ela.

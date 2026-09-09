# ESTADO ATUAL — retoma a frio

> **Para que serve.** Se a sessão morrer a meio, este ficheiro chega para retomar noutra
> plataforma (Claude Code, Codex, ChatGPT, Cowork) sem perder nada. É escrito **antes** de cada
> bloco de acções, não depois.
>
> **Última escrita:** 2026-09-09, antes do bloco «avaliar o retreino v2».
> **Regra:** quem retomar actualiza esta secção antes de agir.

---

## 0. Leitura obrigatória antes de tocar em seja o que for

1. Este ficheiro.
2. `TASKS.md` na raiz — o plano-mestre, fases A a H. É a fonte de verdade das tarefas.
3. `docs/design/reproducao_corpus_2026-09-09.md` — a auditoria de reprodutibilidade completa.
4. `docs/design/TAREFAS_MANUAIS_HENRIQUE.md` — o que só ele pode fazer.

---

## 1. Onde estamos

A tese tem os resultados **reproduzidos e fixados** (corpus, preços, QI2, QI3). O trabalho vivo
é a **QI4** — ajuste contrastivo do codificador por materialidade comparável, que é a
contribuição nova. A primeira tentativa colapsou o codificador e foi descartada; a segunda,
com amostragem estratificada, está a treinar.

---

## 2. A CORRER NESTE MOMENTO

| O quê | Como confirmar | Duração esperada |
|---|---|---|
| Treino `magnitude_v2` e depois `direcao_v2` | `type data\_qi4_mag2.log` e `data\_qi4_dir2.log`; procurar `Modelo em` e `EXITCODE=0` | ~40 min cada, ~80 min os dois |

Lançado por `scripts\_run_qi4v2.bat`, em processo destacado. Saídas em
`data\qi4_modelos\magnitude_v2\` e `...\direcao_v2\`.

**Se os dois já tiverem `EXITCODE=0`, o passo seguinte é o 3.1.**

---

## 3. PRÓXIMOS PASSOS, POR ORDEM

### 3.1 Diagnóstico de colapso — ANTES de olhar para qualquer métrica

```
cd C:\Users\ruifa\Desktop\DIMEIA
set HF_HUB_OFFLINE=1
.venv\Scripts\python.exe -u -m scripts._diag_qi4
```

Editar `scripts\_diag_qi4.py` para apontar a `magnitude_v2` / `direcao_v2` (hoje aponta às v1).

**Critério de aceitação:** o cosseno entre manchetes DIFERENTES tem de ficar na ordem de
`0,2–0,5`. Se vier `> 0,9`, a representação colapsou outra vez e **a tabela de métricas não se
lê** — baixar mais a taxa (`--taxa 2e-6`) ou reduzir passos, e repetir.

Base de referência medida: cosseno `0,2234`, norma do vetor médio `0,4732`.

### 3.2 Avaliar os três braços

```
.venv\Scripts\python.exe -u -m scripts.avaliar_qi4 ^
  --modelo base=all-MiniLM-L6-v2 ^
  --modelo magnitude=data\qi4_modelos\magnitude_v2 ^
  --modelo direcao=data\qi4_modelos\direcao_v2 ^
  --out data\_arquivo\_qi4_tres_v2.md
```

E a variante causal, acrescentando `--causal` e outro `--out`.

**Linha de base já medida** (bloco de teste, 500 consultas × 5 repetições, k=5, simétrico):

| | Comparabilidade (pp) | Precisão@5 |
|---|---:|---:|
| SBERT sem ajuste | 2,173 ± 0,062 | 0,771 ± 0,011 |
| acaso | 2,259 ± 0,107 | 0,629 ± 0,007 |

### 3.3 Braço de controlo (C4)

`--base ProsusAI/finbert` (já em cache HF). ~5× mais lento: contar ~3 h.

### 3.4 Depois da QI4: refazer a §5.3 sobre o FNSPID (C1h.4)

O corpus do Finnhub **não existe** e o Henrique confirmou que não aparece. Pela regra dele, os
resultados que dele dependem saem. Afecta `evaluate.py`, `evaluate_per_sector.py`,
`evaluate_corpus_and_filter.py`, `evaluate_retrieval_embedders.py` → §5.3.1, §5.3.2 (Fig. 5.6),
§5.3.3 (Fig. 5.7 painel A) e a comparação de codificadores.

### 3.5 Capítulo 2 (Fase A12)

Os cinco PDFs estão em `data\literature\`. O [Waa21] já foi lido em texto integral — ver §5.

---

## 4. DECISÕES JÁ TOMADAS — não voltar a discutir sem razão nova

| Decisão | Quando | Porquê |
|---|---|---|
| A QI4 **refina** a restrição «explicar sem prever» em vez de a obedecer sem mais | 09-09 | A grandeza é parcialmente aprendível do texto e a direção não é; é isso que os dois braços medem. O Cap. 1 reescreve-se **depois** dos resultados, não antes. |
| O que não se reproduz nesta máquina **desconsidera-se** | 09-09 | Regra do autor. Vale mesmo que obrigue a descarregar modelos e dados de raiz. |
| Corpus da tese = FNSPID, 79 753 títulos, **catorze** empresas | 09-09 | Reproduzido exactamente do bruto fixado por `sha256`. A Meta não existe no FNSPID (só como `FB`, 432 títulos em 4 meses). |
| Duplicados **conservados** (1 704, 2,1%) | 09-09 | É como o FNSPID entrega. Passou a estar declarado na §3.2. |
| Alvo dos pares = `1 − |Δpercentil|`, amostragem **estratificada** | 09-09 | A amostragem ao acaso dá alvo triangular e colapsa o codificador. Medido. |
| Preços fixados em `data/prices_kb/` com manifesto versionado | 09-09 | Não havia cache nenhuma e havia cadeia de cinco fontes silenciosa. |
| Ambiente = `.venv` (Python 3.12.10) | 09-09 | O Python global (3.13) não tem `sentence-transformers`. |

---

## 5. ACHADOS QUE TÊM DE ENTRAR NO TEXTO

- **BM25 na §5.3.4** (já escrito): 0,521 contra 0,595 do SBERT, acaso 0,333. O lexical capta
  **72%** da margem sobre o acaso. Já está nas duas línguas.
- **[Waa21], lido na íntegra:** identificação do factor decisivo — regras **88%**, exemplos
  **~71%**, nenhuma explicação **~68%**; exemplos contra nenhuma explicação **não é
  significativo** (p=.796), nem na compreensão auto-reportada (p=.283). É o terceiro trabalho
  contra a opção por casos, e o mais duro. **A defesa vem do próprio artigo:** atribui o
  resultado a ambos os estilos darem «details relevant for a single decision, not the
  underlying rational or causality» — e a decomposição do InvestiGator **é** a computação
  subjacente. Vai para §2.7 e §6.4.
- **A linha de base da QI4 justifica a QI4:** o SBERT da tese é indistinguível do acaso na
  comparabilidade de materialidade (2,173 contra 2,259, desvios 0,062 e 0,107).
- **Taxa-base de setor muda com o conjunto de candidatos:** 0,629 no bloco de teste (nove
  empresas) contra 0,333 no corpus completo (catorze). Tem de ser declarado onde se comparar.

---

## 6. ARMADILHAS DO AMBIENTE — custaram tempo, não repetir

1. **Correr sempre pelo `.venv`**: `.venv\Scripts\python.exe`, nunca `python`.
2. **PowerShell inline perde os `$`** através da ponte. Comandos vão em ficheiro `.ps1`
   corrido com `-File`; ficheiros `.ps1` só com ASCII.
3. **Trabalhos longos** vão num `.bat` lançado com `Start-Process -WindowStyle Hidden`, a
   escrever para um log. Um processo lançado em primeiro plano morre com a sessão.
4. **`chapter5.tex` usa CRLF, `chapter3.tex` usa LF.** Editar `.tex` em **modo binário**, ou
   reescreve-se o ficheiro inteiro.
5. **Nunca escrever por cima de artefacto congelado.** `docs/evaluation/*.md`, as figuras da
   tese, `models/*.joblib`, `data/samples/*`. Os scripts já têm `--out`, `--figuras-dir`,
   `--modelos-dir`, `--sample`: usá-los sempre numa verificação.
6. **Duas caches de preços com o mesmo nome de ficheiro e esquemas diferentes:**
   `data/prices/` é do `build_dataset.py`, `data/prices_kb/` é do `build_kb.py`. Não misturar.
7. **`findstr` com vários `/C:"..."` falha** na ponte; usar um por comando ou `/R`.

---

## 7. BLOQUEADO NO HENRIQUE

Nada neste momento. As quatro perguntas pendentes foram respondidas a 2026-09-09:
PDFs entregues · corpus Finnhub não existe · chave Finnhub pronta · narrador é Groq→Gemini
(chaves já no `.env`, nada a fazer).

---

## 8. COMO VERIFICAR QUE NADA SE PARTIU

```
.venv\Scripts\python.exe -m pytest -q
```

Falha conhecida e **alheia a este trabalho**: `test_brand_assets.py` — pertence ao ramo de
trabalho da web/mascote, que tem alterações por submeter no directório de trabalho.

Portas específicas deste trabalho, todas verdes:
`test_corpus_canonico.py` · `test_price_cache.py` · `test_precos_manifesto.py` ·
`test_qi4_pares.py` · `test_qi4_ajuste.py` · `test_qi4_avaliacao.py` · `test_qi4_dataset.py` ·
`test_method.py` · `test_check_paginas.py`

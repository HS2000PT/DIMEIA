# BILINGUAL_PLAN.md — Tese em duas línguas (EN-GB + PT-PT), em sincronia exata

> Pedido do aluno (2026-07-22): ter **duas teses** — uma em Inglês (EN-GB) e uma em Português
> (PT-PT) — com **exatamente o mesmo conteúdo** (tradução pura), o mesmo estilo de escrita, sempre
> em sincronia. Figuras, legendas e artefactos incluídos. Quando faz sentido, imagens em Inglês
> podem ficar na versão PT (ex.: gráficos de dados).

## Arquitetura (decisão)
- `thesis/`    → **EN-GB** (existente; a fonte de referência para a estrutura).
- `thesis-pt/` → **PT-PT** (novo; espelho ficheiro-a-ficheiro: `ch1/chapter1.tex`, etc.).
- **Figuras partilhadas:** ambas as teses usam `../thesis/figures/` (um único conjunto).
  - Gráficos de dados (matplotlib, `eval_*.pdf`, etc.) ficam em **Inglês** nas duas (norma em ML;
    o aluno autorizou). Screenshot da app (UI EN) idem.
  - Figuras **TikZ** vivem no `.tex` de cada capítulo ⇒ são **traduzidas** na versão PT.
- **Template:** a classe `meia-style` suporta `portuguese` (babel + nomes PT: Índice, Orientador…).
  O `main.tex` PT usa a opção `portuguese` em vez de `english`.

## REGRA DE SINCRONIA (permanente)
**Qualquer alteração de conteúdo a uma língua TEM de ser espelhada (traduzida) na outra**, no mesmo
sítio estrutural — prosa, **legendas**, **texto de figuras TikZ**, tabelas, front matter. Os números,
citações, equações, labels LaTeX (`\ref`, `\label`, `\cite`) e a estrutura (secções/figuras/tabelas)
são **idênticos**; só a língua muda. Os gráficos de dados EN são a exceção autorizada. Ao fim de cada
edição: as duas compilam a 0 erros e têm a mesma contagem de secções/figuras/tabelas.

## Política de figuras (o "português misturado" que o aluno viu)
As 3 figuras de triagem tinham rótulos PT (matplotlib) e entravam na tese EN:
`eval_triage_pr.pdf`, `eval_triage_calibration.pdf` (de `train_triage.py`), `eval_triage_ext.pdf`
(de `train_triage_ext.py`). **Corrigido:** rótulos das figuras → EN (`FIG_LABELS` em `train_triage.py`
mantém o `evaluation_triage.md` em PT intacto). Todas as outras figuras já eram EN (verificado).

## Estado da tradução (tracker)
Legenda: ⬜ por fazer · 🟦 em curso · ✅ traduzido e compila.

| Parte | EN (fonte) | PT | Notas |
|---|---|---|---|
| Front matter (título, abstract↔resumo, declarações, glossário) | ✅ | ⬜ | o resumo PT já existe; falta o resto |
| ch1 Introduction | ✅ | ⬜ | |
| ch2 State of the Art | ✅ | ⬜ | o maior (SoTA) |
| ch3 Methods and Materials | ✅ | ⬜ | inclui TikZ da jornada dos dados + tabelas |
| ch4 InvestiGator (o sistema) | ✅ | ⬜ | vários TikZ (arquitetura, fluxo, modelo de dados, mockup) |
| ch5 Case Studies | ✅ | ⬜ | figuras EN partilhadas |
| ch6 Conclusions | ✅ | ⬜ | |
| Apêndice A (reprodutibilidade + proof of work) | ✅ | ⬜ | TikZ do pipeline mestre |

## Verificação final (porta de conclusão)
- [ ] `thesis/` e `thesis-pt/` compilam a 0 erros, 0 citações indefinidas, 0 overfull >15pt.
- [ ] Mesma contagem de secções, figuras e tabelas nas duas.
- [ ] 0 PT no corpo/figuras da EN; 0 EN (fora dos gráficos de dados autorizados) no corpo da PT.
- [ ] Números/citações idênticos (as duas citam o mesmo `.bib`).

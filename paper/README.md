# paper/ — Artigo IEEE (Fase F)

Artigo de conferência (formato **IEEEtran**) destilado da dissertação, construído **apenas sobre a
implementação, experiências e estatística já validadas** (Fases D/E).

## Conteúdo
- `main.tex` — artigo IEEE (conference): introdução, trabalho relacionado, sistema CLARION, avaliação
  (anomalia + recuperação + fidelidade), discussão/limitações, conclusão.
- `references.bib` — **subconjunto verificado** das referências da tese (23 entradas; espelho de
  `thesis/references.bib`; entradas *online/report* convertidas para *misc* para o BibTeX clássico).
- Reutiliza as figuras reprodutíveis da tese via `\graphicspath{{../thesis/figures/}}`.

## Como compilar
```bash
cd paper
latexmk -pdf main.tex      # pdflatex + bibtex + IEEEtran.bst
```
Estado: **compila, 3 pp, 0 erros, 0 citações indefinidas**.

## Integridade
- **Zero citações novas não verificadas:** todas as 23 referências já constam do `citation_log.md` e foram
  re-verificadas na Fase E (DOI/arXiv/ISBN/fonte primária).
- **Números idênticos aos da tese e reprodutíveis** (P@5 0,514±0,015; amplitude de disparo 0,015 vs 0,344;
  F1 0,516; por setor energia +0,377 … consumo +0,100).

## Notas
- Esta é uma **versão condensada** (short paper). Para uma submissão a um *venue* específico, expandir o
  trabalho relacionado e a avaliação até ao limite de páginas do CFP, mantendo só citações verificadas.
- A declaração de uso de IA segue a mesma política honesta da tese (ver `honest-ai-declaration`).

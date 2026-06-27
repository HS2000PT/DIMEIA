# slides/ — Slides de defesa (Fase G)

Apresentação de defesa (**Beamer**, tema Madrid) destilada da tese **validada**. 14 frames.

## Conteúdo (fluxo da defesa)
Problema → o que o CLARION faz (e não faz) → RQ + contribuição → arquitetura → gatilho de mercado
(exemplo real TSLA, z=7,61) → gatilho de notícias (exemplo real Nvidia, match cross-ticker) →
Resultado 1 (consistência da anomalia, 0,015 vs 0,344) → Resultado 2 (recuperação, P@5 0,514 vs baselines)
→ Resultado 3 (fidelidade + alerta real) → limitações → conclusões (RQ1–RQ3) → obrigado → **perguntas
antecipadas do júri**.

## Como compilar
```bash
cd slides
latexmk -pdf main.tex
```
Estado: **compila, 14 pp, 0 erros**. Reutiliza as figuras validadas via `\graphicspath{{../thesis/figures/}}`.

## Notas
- **Inglês**, para coincidir com a tese (EN-GB) e reutilizar as figuras diretamente. O apoio de estudo em
  PT-PT é o `docs/defence/caderno_de_defesa.md` (a melhorar na Fase H).
- Números idênticos aos da tese e reproduzíveis (Fases D/E). Só conteúdo já validado.
- O último slide ("Anticipated questions") espelha as perguntas difíceis preparadas no caderno de defesa.

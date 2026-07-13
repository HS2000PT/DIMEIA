# calibration_platt_vs_isotonic.md — Platt vs isotónica (extensão; reprodutível)

> Gerado por `scripts/evaluate_calibration_ext.py`. **Não editar à mão.**
> Extensão ADITIVA: `models/`, `evaluation_triage.md` e a tese ficam intocados.

- **Dataset:** `C:\Users\henri\Desktop\DIMEIA\data\triage_dataset.csv` — mesmas linhas/split/seed do treino congelado (val = 17710 pontos de calibração).
- **Protocolo:** idêntico a `train_triage.py` (split temporal + embargo, seed=42, embedder=sbert); ambas as calibrações ajustadas na MESMA validação e avaliadas no MESMO teste.
- **Reprodução do congelado (Platt):** ✅ bate (tolerância 0,0015 em PR-AUC e Brier).
- **Gerado:** 2026-07-13 20:05 UTC.

| Modelo | Brier Platt | Brier isotónica | ECE Platt | ECE isotónica |
|---|---|---|---|---|
| LR só-volatilidade (baseline) | 0.2183 | 0.2231 | 0.0327 | 0.0539 |
| LR só-contexto (produção) | 0.2241 | 0.2259 | 0.0677 | 0.0495 |
| LR só-texto | 0.2403 | 0.2404 | 0.0896 | 0.0892 |
| LR contexto+texto (principal) | 0.2288 | 0.2293 | 0.0610 | 0.0557 |
| Gradient boosting (contexto+texto) | 0.2276 | 0.2298 | 0.0466 | 0.0501 |

Curva de fiabilidade do modelo de produção (LR só-contexto), teste:

| Bin | P prevista (Platt) | Observada | n | P prevista (iso) | Observada | n |
|---|---|---|---|---|---|---|
| 1 | 0.26 | 0.23 | 2729 | 0.29 | 0.17 | 494 |
| 2 | 0.38 | 0.26 | 8353 | 0.38 | 0.34 | 26819 |
| 3 | 0.44 | 0.39 | 15992 | 0.44 | 0.59 | 2519 |
| 4 | 0.54 | 0.59 | 4645 | 0.57 | 0.51 | 311 |
| 5 | 0.64 | 0.70 | 930 | 0.65 | 0.55 | 1149 |
| 6 | — | — | — | 0.72 | 0.70 | 1357 |

**Veredicto (tal como caiu):** no Brier, a Platt ganha ou empata em TODAS as 5 famílias (ganha 3, empata 2); no ECE o quadro é misto (2 para a isotónica, 2 para a Platt) e por margens pequenas. Mesmo com validação farta — o cenário teoricamente favorável à isotónica (niculescu2005calibration) — a flexibilidade extra não paga: a escolha de Platt na tese (2 parâmetros, sigmóide monótona e suave, explicável) fica validada EMPIRICAMENTE, não só conceptualmente. Não há caso para mudar a produção.

**Caveats:** a isotónica pode criar patamares (empates) nas probabilidades — o ranking fino perde granularidade; ECE com 10 bins de largura igual; nenhum destes números substitui os congelados da tese.

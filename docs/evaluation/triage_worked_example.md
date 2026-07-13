# triage_worked_example.md — exemplo trabalhado da triagem (reprodutível)

> Gerado por `scripts/figures/fig_triage_worked.py`. **Não editar à mão.**

- **Caso real:** alerta META enviado ao canal a 2026-07-12 (branch `alerts-history`), manchete: "Mark Zuckerberg Said Meta's AI Bets "Haven't Come to Fruition Yet" as Shares Fell 5%".
- **Features no último fecho (2026-07-10):** vol20=0.0338, mom5=0.0298, ret_event=0.0580, headline_len=84.
- **Modelo:** bundle de produção `models/triage_context_lr.joblib` (LR só-contexto, StandardScaler + Platt).
- **Gerado:** 2026-07-13 14:02 UTC.

## Decomposição aditiva exata (log-odds)

| Termo | Contribuição ao logit |
|---|---|
| intercepto | -0.025 |
| recent volatility (20d) | +0.409 |
| sector | +0.303 |
| today's own move | +0.010 |
| headline length | +0.002 |
| recent momentum (5d) | +0.000 |
| **logit (soma)** | **+0.699** |

σ(logit) = **0.668** (probabilidade crua) → calibração de Platt (σ(3.700·logit_raw + -2.313)) → **p = 0.539**.

**Fidelidade (honesta):** a mensagem realmente enviada dizia "Risk estimate: 57%"; a reprodução dá 54% (Δ 3.1 p.p.). A diferença vem do reajuste RETROATIVO de dividendos nos fechos yfinance desde o envio: as features mudam na 3.ª-4.ª casa decimal e contribuições quase nulas podem até trocar de sinal (aqui, momentum 5d ~0). O que interessa reproduz-se: a ordem dos fatores dominantes (volatilidade e setor a subir o risco) e a DECISÃO do gate.
Gate de produção: p = 0.539 ≥ 0.5 → PASSA (o alerta foi de facto enviado).

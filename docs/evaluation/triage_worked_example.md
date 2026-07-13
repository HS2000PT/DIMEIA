# triage_worked_example.md — exemplo trabalhado da triagem (reprodutível)

> Gerado por `scripts/figures/fig_triage_worked.py`. **Não editar à mão.**

- **Caso real:** alerta META enviado ao canal a 2026-07-12 (branch `alerts-history`), manchete: "Mark Zuckerberg Said Meta's AI Bets "Haven't Come to Fruition Yet" as Shares Fell 5%".
- **Features no último fecho (2026-07-10):** vol20=0.0338, mom5=0.0298, ret_event=0.0580, headline_len=84.
- **Modelo:** bundle de produção `models/triage_context_lr.joblib` (LR só-contexto, StandardScaler + Platt).
- **Gerado:** 2026-07-13 14:13 UTC.

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

σ(logit) = **0.668** (probabilidade crua) → calibração de Platt (σ(3.700·p_raw + -2.313)) → **p = 0.539**.

**Fidelidade:** a mensagem realmente enviada dizia "Risk estimate: 54% … raised by recent volatility (20d) and sector"; a reprodução dá 54% com os MESMOS fatores dominantes — reprodução exata da decisão de produção. (Nota: os fechos yfinance são reajustados retroativamente a cada dividendo, pelo que reproduções futuras podem divergir ~1 p.p.; a decisão do gate é robusta a isso.)
Gate de produção: p = 0.539 ≥ 0.5 → PASSA (o alerta foi de facto enviado).

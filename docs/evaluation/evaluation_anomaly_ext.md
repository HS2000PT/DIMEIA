# evaluation_anomaly_ext.md — CS1-ext: LOF + EWMA (reprodutível)

> Gerado por `scripts/evaluate_anomaly_ext.py`. **Não editar à mão.**
> Extensão ADITIVA: o `evaluation_anomaly.md` congelado da tese fica intocado;
> este ficheiro acrescenta detetores/estimadores ao MESMO protocolo.

- **Dados:** 15 tickers, preços reais (2023-06-01 a 2026-06-01).
- **Protocolo:** janela 20d, limiar ±3, rótulo-proxy |retorno| ≥ p99 por ticker; detetores aprendidos causais (treino 250d, contaminação 0.02, seed 42); métricas na MESMA região pontuada pelos três detetores.
- **Gerado:** 2026-07-13 13:56 UTC.

## 1. Detetores: estatístico vs aprendidos (mesma região, mesmas features)

| Detetor | Precision | Recall | F1 | Amplitude da taxa |
|---|---|---|---|---|
| z-score (regra da tese) | 0.407 | 0.761 | **0.530** | 0.017 |
| Isolation Forest | 0.158 | 0.913 | 0.269 | 0.140 |
| Local Outlier Factor | 0.163 | 0.989 | 0.280 | 0.183 |

**Leitura:** o LOF era citado na tese como alternativa mas nunca tinha sido testado — agora está, com o mesmo protocolo causal do IF. A regra estatística transparente ganha aos dois detetores aprendidos não-supervisionados com a mesma informação (features [retorno, vol20 anterior]): ambos disparam demasiado (recall alto, precisão ~0,16) e com taxas inconsistentes entre tickers. **Fidelidade ao protocolo:** a linha do z-score reproduz os valores congelados do CS1 (0,407/0,761/0,530); o IF difere ~0,002 do congelado porque o yfinance reajusta os fechos históricos a cada dividendo novo desde a corrida de 2026-07-04 (drift documentado, não um erro).

## 2. Estimador de volatilidade: σ rolling (tese) vs σ EWMA (RiskMetrics)

EWMA com λ=0.94 (RiskMetrics), média zero, causal; mesma região a partir do dia 20. O degrau empírico entre a σ rolling e um GARCH completo.

| Estimador | Precision | Recall | F1 | Amplitude da taxa |
|---|---|---|---|---|
| σ rolling 20d (tese) | 0.381 | 0.800 | **0.516** | 0.015 |
| σ EWMA (λ=0.94) | 0.568 | 0.800 | 0.664 | 0.012 |

**Leitura (honesta — o resultado surpreendeu):** a experiência foi desenhada para justificar o "porquê não GARCH?" e os dados dizem o CONTRÁRIO do esperado: com o MESMO recall, a σ EWMA quase elimina metade dos falsos positivos (precisão 0.568 vs 0.381) — F1 0.664 vs 0.516 — e é ainda mais consistente entre tickers. Mecanismo: com clustering de volatilidade, a σ rolling dilui um choque por 20 pesos iguais enquanto a EWMA o incorpora de imediato — nos dias seguintes a um choque, a EWMA re-alerta menos (comportamento provado em teste unitário). Implicação para a tese: a regra implantada continua a ser a rolling (transparência: "média e desvio de 20 dias" explica-se a um leigo; a EWMA exige explicar pesos exponenciais), mas o ganho fica REGISTADO e a adoção é uma mudança de 1 linha — trabalho futuro validado, não especulado. Caveat: o rótulo-proxy é volatilidade-relativo (mesma circularidade assumida no CS1) e favorece dias de |retorno| extremo incondicional.

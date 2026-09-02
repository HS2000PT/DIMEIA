# evaluation_budget_sweep.md — o orçamento diário, varrido

> Gerado por `scripts/evaluate_budget_sweep.py`. **Não editar à mão.**

- Bloco de teste: **32649** linhas · **221** dias · prevalência **0.3781**
- Ordenação: modelo só-contexto implantado (`triage_context_lr.joblib`)

## 1. A curva

| orçamento k | precisão@k | selecionados | por dia | positivos apanhados | cobertura |
|---|---|---|---|---|---|
| **1** | 0.6335 | 221 | 1.00 | 140 | 0.011 |
| **2** | 0.6335 | 442 | 2.00 | 280 | 0.023 |
| **3** | 0.6335 | 663 | 3.00 | 420 | 0.034 |
| **4** | 0.6324 | 884 | 4.00 | 559 | 0.045 |
| **5** ← em produção | 0.6317 | 1105 | 5.00 | 698 | 0.057 |
| **6** | 0.6312 | 1326 | 6.00 | 837 | 0.068 |
| **8** | 0.6284 | 1768 | 8.00 | 1111 | 0.090 |
| **10** | 0.6262 | 2210 | 10.00 | 1384 | 0.112 |
| **12** | 0.6237 | 2652 | 12.00 | 1654 | 0.134 |
| **15** | 0.6208 | 3315 | 15.00 | 2058 | 0.167 |
| **20** | 0.6070 | 4420 | 20.00 | 2683 | 0.217 |
| **30** | 0.5751 | 6630 | 30.00 | 3813 | 0.309 |

## 2. Leitura

1. **A precisão cai devagar e a cobertura sobe depressa.** De k=5 para k=10 a precisão passa de 0.632 para 0.626 (uma queda de 0.9%), e a cobertura sobe de 0.057 para 0.112.
2. **Nenhum k é o óptimo, porque a métrica não tem óptimo.** A precisão é monótona decrescente em k por construção: cada lugar extra é ocupado por uma linha com score mais baixo do que todas as anteriores. Perguntar qual o k que maximiza a precisão é perguntar por k=1.
3. **A restrição que falta não está nesta tabela.** O limite real é quantos alertas por dia uma pessoa lê antes de deixar de os ler, e isso mede-se com pessoas, não com este conjunto. É precisamente o que a recolha de feedback no canal existe para informar.

## 3. O que isto NÃO autoriza

Escolher o k desta tabela e chamar-lhe resultado seria selecionar sobre o conjunto de teste. A tabela descreve um compromisso; a decisão sobre onde estar nele é de desenho, e tem de ser justificada por fadiga do leitor e por capacidade do canal, não por esta coluna de precisão.

# Decomposicao de um movimento: mercado, setor, empresa

> Gerado por `scripts/evaluate_decomposition.py`. Nao editar a mao.
> Mercado: `SPY` · janela de estimacao: 20 dias anteriores ao dia
> explicado · encolhimento de Vasicek com prior 1.0 e
> dispersao 0.5 · minimo de 10 dias para estimar.

## 1. Um caso trabalhado

Ticker **AMD** (setor `XLK`), movimento do dia **+6.2944%**.

| Passo | Valor |
|---|---|
| beta de mercado (apos encolhimento) | 2.0143 |
| beta de setor (apos encolhimento) | 1.5888 |
| R^2 do ajuste na janela | 0.6577 |
| dias usados na estimacao | 20 |
| **componente de mercado** | **-0.3992%** |
| **componente de setor** | **-0.0362%** |
| **componente da empresa** | **+6.7298%** |
| soma das tres | +6.2944% |
| movimento observado | +6.2944% |
| diferenca | 0.00e+00 |

Motor identificado: **company**. Componentes que puxaram ao contrario: **market, sector**.

A soma fecha por construcao: o alfa e o residuo do dia entram na componente da
empresa, que e por definicao o que mercado e setor nao explicam.

## 2. A watchlist toda, no mesmo dia

| Ticker | Setor | Total | Mercado | Setor | Empresa | Motor | beta_m |
|---|---|---|---|---|---|---|---|
| AAPL | XLK | +0.22% | -0.11% | -0.00% | +0.33% | company | 0.57 |
| AMD | XLK | +6.29% | -0.40% | -0.04% | +6.73% | company | 2.01 |
| AMZN | XLK | -0.94% | -0.24% | +0.01% | -0.71% | company | 1.20 |
| BAC | XLF | +0.62% | -0.14% | -0.05% | +0.82% | company | 0.71 |
| CVX | XLE | +1.16% | +0.13% | +0.86% | +0.16% | sector | -0.67 |
| GOOGL | XLK | -0.13% | -0.25% | +0.02% | +0.10% | market | 1.28 |
| JNJ | XLV | -0.66% | +0.04% | -0.52% | -0.18% | sector | -0.20 |
| JPM | XLF | -0.07% | -0.17% | -0.05% | +0.15% | market | 0.85 |
| KO | XLP | +0.33% | -0.07% | +0.08% | +0.33% | company | 0.38 |
| META | XLK | -0.86% | -0.16% | +0.02% | -0.72% | company | 0.82 |
| MSFT | XLK | -0.30% | -0.28% | -0.00% | -0.02% | market | 1.40 |
| NFLX | XLK | -0.10% | -0.18% | +0.01% | +0.07% | market | 0.92 |
| NVDA | XLK | -0.06% | -0.27% | -0.00% | +0.22% | market | 1.39 |
| PFE | XLV | -0.04% | -0.08% | -0.65% | +0.69% | sector | 0.38 |
| TSLA | XLK | +0.68% | -0.34% | +0.01% | +1.01% | company | 1.70 |
| WMT | XLP | -0.39% | +0.01% | +0.07% | -0.47% | company | -0.06 |
| XOM | XLE | +0.94% | +0.09% | +0.66% | +0.18% | sector | -0.45 |

`*` = betas nao estimaveis; assumiu-se beta 1.0 no mercado.

## 3. Com que frequencia a resposta e 'nao foi a tua empresa'

- Tickers decompostos: **17**
- Motor `market`: **5** (29.4%)
- Motor `sector`: **4** (23.5%)
- Motor `company`: **8** (47.1%)
- Quota especifica da empresa: mediana **0.487**, minimo 0.064, maximo 0.939

### A qualidade do ajuste, dita em voz alta

- R^2 mediano na janela de estimacao: **0.460**
- Tickers com R^2 <= 0: **1** de 17

Isto importa e nao se esconde. As tres componentes somam **sempre** o movimento
observado, porque a componente da empresa e definida como o resto; a soma fechar
nao e portanto prova de que a reparticao esteja bem estimada. Um R^2 nulo ou
negativo diz que, naquela janela, mercado e setor nao explicam a variacao daquele
ticker melhor do que a media, e a reparticao desse dia deve ler-se como
indicativa e nao como uma atribuicao de confianca.

Este e um unico dia e nao e uma estimativa estavel: serve para mostrar que a
decomposicao produz respostas diferentes para empresas diferentes no mesmo dia,
que e a condicao minima para a pergunta valer a pena ser feita.

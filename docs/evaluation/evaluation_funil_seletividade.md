# evaluation_funil_seletividade.md — funil sobre uma janela única

> Gerado por `scripts/evaluate_funil_seletividade.py` a 2026-09-04 13:58 UTC. **Não editar à mão.**
> Instantâneo datado: o canal cresce, e a tese cita ESTE instantâneo.

- **Janela:** 2026-09-01 a 2026-09-03, aplicada aos dois lados do funil.
- **Unidade:** título distinto, deduplicado por (data, empresa, título). O registo contém 1321 linhas para 743 títulos distintos, porque o sistema reavalia os mesmos títulos a cada ciclo.
- **Títulos distintos avaliados:** 743, sobre 12 empresas.
- **Alertas entregues ao canal:** 15, sobre 8 empresas.
- **Razão:** 50 títulos avaliados por alerta entregue.
- **Política em vigor:** orçamento global de 5 alertas por dia, desde 2026-08-15.

| Empresa | Títulos distintos | Alertas entregues |
|---|---|---|
| AAPL | 133 | 1 |
| TSLA | 120 | 3 |
| NVDA | 97 | 3 |
| GOOGL | 90 | 0 |
| MSFT | 71 | 1 |
| AMZN | 68 | 1 |
| AMD | 41 | 2 |
| META | 38 | 2 |
| NFLX | 28 | 2 |
| JPM | 26 | 0 |
| XOM | 17 | 0 |
| JNJ | 14 | 0 |
| **Total** | **743** | **15** |

## Onde os títulos pararam

| Etapa | Títulos distintos |
|---|---|
| não era a mais recente da empresa no ciclo | 536 |
| notícia antiga, não pontuada | 195 |
| sobreviveu ao varrimento | 12 |

## É medição ou é tecto?

Esta secção existe porque o instrumento anterior não a tinha, e por isso publicou três empresas com exatamente o mesmo valor sem assinalar que esse valor era o limite que a política impunha.

- O orçamento diário de 5 foi **integralmente utilizado** em 3 de 3 dia(s): 2026-09-01, 2026-09-02, 2026-09-03. O total de alertas é, nesses dias, **o tecto e não uma medição**: mede a política, não a matéria-prima.
- A distribuição por empresa não é uniforme; o máximo (3) é atingido por NVDA, TSLA, e está abaixo do orçamento diário, pelo que não corresponde a um limite por empresa.

## Leitura

Sobre 3 dia(s), o sistema avaliou 743 títulos distintos de 12 empresas e entregou 15 alertas a 8 delas. A quantidade que a política governa é o total diário, e não a repartição por empresa: nenhuma empresa tem quota própria, e a distribuição observada resulta da ordenação por materialidade dentro do orçamento.


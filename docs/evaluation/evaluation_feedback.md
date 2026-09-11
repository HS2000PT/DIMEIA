# Feedback do canal — piloto não moderado

> **O que este documento é, e o que não é.** Mede se os alertas que o sistema decidiu enviar foram considerados úteis por quem os recebeu, através de dois botões na própria mensagem. Não é o estudo de utilidade do protocolo moderado (`docs/study/`), que pergunta se a explicação é compreendida e se calibra a confiança. São instrumentos diferentes e não se somam.

> **Todas as regras de análise foram fixadas antes de existirem dados** e estão no cabeçalho de `scripts/analyse_feedback.py`. Nenhuma foi alterada depois.

> Gerado por `scripts/analyse_feedback.py` a 2026-09-11 09:33 UTC.

> **5 voto(s) excluído(s)** por não corresponderem a nenhum alerta do histórico partilhado. Não foram apagados do ficheiro, que é de acrescento e é a prova; foram ignorados na contagem.

## Dimensão da amostra

| Medida | Valor |
|---|---|
| Votos válidos registados | 131 |
| Votos efetivos (um por pessoa e alerta) | 91 |
| Pessoas distintas | 3 |
| Alertas votados | 62 |
| Mudanças de voto | 11 |
| Cliques repetidos sem mudança | 29 |

## Resultado

| Recorte | Contagem | Proporção | Nota |
|---|---|---|---|
| Alertas considerados úteis | 86 de 91 | 95% | IC 95% de Wilson: 88%–98% |
| O mesmo, sem o votante dominante | 34 de 38 | 89% | IC 95% de Wilson: 76%–96% |

⚠️ **Salvaguarda do votante dominante aplicada.** Uma só pessoa forneceu 58% dos votos efetivos, excedendo o limite pré-registado de 40%. A segunda linha reporta o cálculo sem essa pessoa; se as duas linhas divergirem, essa é a leitura a reter.

A proporção de alertas considerados úteis é de 95%, com intervalo de confiança de Wilson a 95% entre 88% e 98%. Este cálculo binomial não corrige a dependência entre votos da mesma pessoa ou sobre o mesmo alerta; a sua largura não representa toda a incerteza desta amostra.

## Ameaças à validade, e nenhuma delas é resolúvel com mais votos

- **Autosseleção.** Vota quem quer. Quem acha um alerta indiferente tende a não carregar em nada, o que empurra a amostra para os dois extremos.
- **Ausência de contrafactual.** Não há um grupo que receba a variação de preço sem explicação, portanto nada aqui atribui a utilidade à explicação em si.
- **Utilidade percebida não é decisão melhor.** É a hipótese fundadora do trabalho, e continua por testar: um alerta pode agradar e conduzir a uma decisão pior.
- **Canal público.** Não se sabe quem são as pessoas, nem se são investidores particulares, que é o público que a dissertação assume.


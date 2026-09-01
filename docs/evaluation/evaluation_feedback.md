# Feedback do canal — piloto não moderado

> **O que este documento é, e o que não é.** Mede se os alertas que o sistema decidiu enviar foram considerados úteis por quem os recebeu, através de dois botões na própria mensagem. Não é o estudo de utilidade do protocolo moderado (`docs/study/`), que pergunta se a explicação é compreendida e se calibra a confiança. São instrumentos diferentes e não se somam.

> **Todas as regras de análise foram fixadas antes de existirem dados** e estão no cabeçalho de `scripts/analyse_feedback.py`. Nenhuma foi alterada depois.

> Gerado por `scripts/analyse_feedback.py` a 2026-09-01 19:34 UTC.

> **4 voto(s) excluído(s)** por não corresponderem a nenhum alerta do histórico partilhado. Não foram apagados do ficheiro, que é de acrescento e é a prova; foram ignorados na contagem.

## Dimensão da amostra

| Medida | Valor |
|---|---|
| Votos registados | 2 |
| Votos efetivos (um por pessoa e alerta) | 2 |
| Pessoas distintas | 1 |
| Alertas votados | 2 |
| Mudanças de voto | 0 |

## Resultado

| Recorte | Contagem | Proporção | Nota |
|---|---|---|---|
| Alertas considerados úteis | 2 de 2 | não reportada | abaixo do mínimo pré-registado de 20 |
| O mesmo, sem o votante dominante | 0 de 0 | não reportada | abaixo do mínimo pré-registado de 20 |

⚠️ **Salvaguarda do votante dominante aplicada.** Uma só pessoa representa 100% dos votos efetivos, acima do limite pré-registado de 40%. A segunda linha da tabela mostra o mesmo cálculo sem essa pessoa. Se as duas linhas divergirem, a leitura a reportar é a segunda.

**Nenhuma proporção é reportada.** Há 2 votos efetivos e a regra pré-registada exige 20. As contagens acima são o resultado, e são tudo o que esta amostra sustenta.

## Ameaças à validade, e nenhuma delas é resolúvel com mais votos

- **Autosseleção.** Vota quem quer. Quem acha um alerta indiferente tende a não carregar em nada, o que empurra a amostra para os dois extremos.
- **Ausência de contrafactual.** Não há um grupo que receba a variação de preço sem explicação, portanto nada aqui atribui a utilidade à explicação em si.
- **Utilidade percebida não é decisão melhor.** É a hipótese fundadora do trabalho, e continua por testar: um alerta pode agradar e conduzir a uma decisão pior.
- **Canal público.** Não se sabe quem são as pessoas, nem se são investidores particulares, que é o público que a dissertação assume.


# Feedback do canal — piloto não moderado

> **O que este documento é, e o que não é.** Mede se os alertas que o sistema decidiu enviar foram considerados úteis por quem os recebeu, através de dois botões na própria mensagem. Não é o estudo de utilidade do protocolo moderado (`docs/study/`), que pergunta se a explicação é compreendida e se calibra a confiança. São instrumentos diferentes e não se somam.

> **Todas as regras de análise foram fixadas antes de existirem dados** e estão no cabeçalho de `scripts/analyse_feedback.py`. Nenhuma foi alterada depois.

> Gerado por `scripts/analyse_feedback.py` a 2026-09-03 16:16 UTC.

> **4 voto(s) excluído(s)** por não corresponderem a nenhum alerta do histórico partilhado. Não foram apagados do ficheiro, que é de acrescento e é a prova; foram ignorados na contagem.

## Dimensão da amostra

| Medida | Valor |
|---|---|
| Votos válidos registados | 31 |
| Votos efetivos (um por pessoa e alerta) | 20 |
| Pessoas distintas | 2 |
| Alertas votados | 16 |
| Mudanças de voto | 5 |
| Cliques repetidos sem mudança | 6 |

## Resultado

| Recorte | Contagem | Proporção | Nota |
|---|---|---|---|
| Alertas considerados úteis | 19 de 20 | 95% | IC 95% de Wilson: 76%–99% |
| O mesmo, sem o votante dominante | 4 de 4 | não reportada | abaixo do mínimo pré-registado de 20 |

⚠️ **Salvaguarda do votante dominante aplicada.** Uma só pessoa forneceu 80% dos votos efetivos, excedendo o limite pré-registado de 40%. Sem essa pessoa restam 4 votos, abaixo do mínimo de 20; a segunda linha mostra apenas a contagem e nenhuma proporção desse recorte é reportada.

A proporção de alertas considerados úteis é de 95%, com intervalo de confiança de Wilson a 95% entre 76% e 99%. A largura deste intervalo é a medida honesta do que 20 votos permitem afirmar, e é por isso que é reportada ao lado do valor central e nunca depois dele.

## Ameaças à validade, e nenhuma delas é resolúvel com mais votos

- **Autosseleção.** Vota quem quer. Quem acha um alerta indiferente tende a não carregar em nada, o que empurra a amostra para os dois extremos.
- **Ausência de contrafactual.** Não há um grupo que receba a variação de preço sem explicação, portanto nada aqui atribui a utilidade à explicação em si.
- **Utilidade percebida não é decisão melhor.** É a hipótese fundadora do trabalho, e continua por testar: um alerta pode agradar e conduzir a uma decisão pior.
- **Canal público.** Não se sabe quem são as pessoas, nem se são investidores particulares, que é o público que a dissertação assume.


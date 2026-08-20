# evaluation_triage_within.md — o texto acrescenta por cima? e o modelo separa dias?

> Gerado por `scripts/evaluate_triage_within.py` a 2026-08-20 18:29 UTC. **Não editar à mão.**
> Porta de entrada reproduzida: volatilidade 0.542 e contexto 0.538 contra os congelados 0.542 e 0.538.

## Porque é que estas duas perguntas não estavam feitas

A avaliação da dissertação compara famílias **lado a lado**, e responde a *qual é melhor*.
Não responde a *o texto acrescenta ao melhor que existe*, nem a *o modelo distingue dois
dias da mesma empresa*. A segunda é a mais informativa, porque tem um chão que não é
preciso estimar: uma tabela de consulta por empresa devolve o mesmo valor para todos os
dias dessa empresa, logo ordena-os ao nível do acaso, **por construção**.

## Os cinco modelos, sobre o mesmo bloco de teste

| Modelo | O que vê | PR-AUC | Precisão@5 | **AUC dentro da empresa** |
|---|---|---|---|---|
| Tabela de consulta por empresa | o melhor chão conhecido, e não vê a notícia | 0.534 | 0.662 | 0.500 (por construção) |
| **Tabela + texto** | a mesma tabela, mais o título | 0.547 | 0.662 | 0.512 |
| Contexto (o implantado) | as nove entradas | 0.538 | 0.632 | 0.502 |
| Contexto + texto | as nove, mais o título | 0.533 | 0.627 | 0.508 |
| Só texto | só o título | 0.457 | 0.616 | 0.495 |

A coluna da direita é sobre 9 empresas com positivos e negativos no bloco
de teste, e é uma média ponderada pelo número de pares de cada empresa.

## Os dois acréscimos, com intervalo por grupos (empresa, dia)

| Pergunta | Valor | IC 95% | Veredicto |
|---|---|---|---|
| O texto acrescenta à tabela de consulta? (PR-AUC) | +0.0123 | [+0.0038, +0.0204] | **exclui zero** |
| E bate a volatilidade sozinha, que ganhou na dissertação? (PR-AUC) | +0.0043 | [-0.0321, +0.0366] | contém zero |
| O modelo implantado separa dias da mesma empresa? (AUC dentro) | 0.5021 | [0.4616, 0.5423] | contém 0.5 |
| O texto acrescenta a essa separação? | +0.0057 | [-0.0140, +0.0254] | contém zero |

Reamostragem: 1000 repetições sobre 1951 grupos (empresa, dia), e não sobre as 32649 linhas.

## Como ler isto

O critério foi fixado antes de correr: um acréscimo só conta se o intervalo excluir
zero. As quatro linhas dizem quatro coisas diferentes, e convém não as juntar.

**A primeira é o resultado.** O título acrescenta ao melhor preditor conhecido, e o
intervalo exclui zero. Não é grande, e é real.

**A segunda impede a afirmação forte.** Somar o texto à tabela chega a um valor acima do
da volatilidade sozinha, mas a diferença tem um intervalo que contém zero: são dois
pontos dentro do ruído um do outro, e dizer que *bate* a volatilidade seria ler uma
diferença que a amostra não sustenta.

**A terceira e a quarta confirmam o diagnóstico em vez de o desmentirem.** Nem o modelo
implantado nem a variante com texto separam dois dias da mesma empresa: os intervalos
contêm $0.5$. A informação que o texto traz distingue **empresas e períodos**, não
notícias.

E há uma quinta coisa, que não está na tabela dos intervalos e é a que decide o produto:
a **precisão dentro do orçamento não muda** ($0.662$ nas duas linhas da tabela de cima).
O acréscimo existe na ordenação global e desaparece quando só se escolhem cinco por dia,
que é o que o sistema faz. Um ganho que não sobrevive à métrica de produto não muda o
produto, e é assim que fica reportado.

## Uma ressalva de método, dita antes que alguém pergunte

Este é mais um modelo avaliado sobre o mesmo bloco de teste, que já foi usado por várias
comparações deste trabalho. Quanto mais vezes se olha para um conjunto de teste, mais
fácil é encontrar nele uma diferença pequena. Duas coisas limitam esse risco, e nenhuma
delas o elimina: a configuração do texto não foi afinada aqui (usa-se a redução a
32 dimensões fixada no re-teste justo anterior), e o critério de decisão foi
escrito no cabeçalho deste ficheiro antes de a medição correr. Um resultado de $+0.012$
deve ser lido com essa reserva.

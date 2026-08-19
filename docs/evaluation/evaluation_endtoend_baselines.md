# O sistema vale mais do que as alternativas que a pessoa já tem?

> **Gerado por** `scripts/evaluate_endtoend_baselines.py`. Não editar à mão.
> **Bloco de teste:** 32649 notícias em 221 dias · **orçamento:** 5 por dia ·
> **prevalência:** 0.378
> **Porta de entrada:** o modelo implantado reproduz o congelado (`0.632`).

## A pergunta

A dissertação compara cada componente com linhas de base próprias. Falta a comparação de que o
utilizador precisa, que é ao nível do **sistema**: dadas as notícias de um dia, quais as cinco que
valia a pena mostrar, e o sistema escolhe-as melhor do que o que já existe de graça?

Todas as políticas abaixo escolhem cinco por dia, sobre o mesmo bloco e com o mesmo rótulo. O
desempate é **aleatório e explícito** em todas: ordenar empates pela posição no ficheiro seria
ordenar por empresa em ordem alfabética.

## Resultados

| Política | O que faz | Precisão@5 | Nota |
|---|---|---|---|
| Alertar sempre | não escolhe: leva as primeiras que apareçam | 0.380 | chão |
| Ao acaso (40 sementes) | escolhe cinco à sorte | 0.375 | ±0.012 |
| Quem mais se mexeu hoje | notícias das empresas com maior movimento do dia | 0.489 | grátis em qualquer app |
| Volatilidade da empresa | treze constantes, sem ler manchete | 0.662 | sem modelo |
| \textbf{O modelo implantado} | a triagem aprendida | 0.632 | o sistema |
| Oráculo | sabe as respostas: o melhor possível | 0.968 | tecto |

## Leitura

**O sistema bate as alternativas triviais**, e a comparação que importa é com a terceira linha:
mostrar notícias de quem mais se mexeu hoje é o que qualquer aplicação de bolsa já faz, de graça, e
obtém `0.489` contra os
`0.632` do sistema.

**Mas a linha mais desconfortável é a da volatilidade**, e já era conhecida: treze constantes
calculadas só sobre o treino, sem ler uma única manchete, obtêm
`0.662`. É coerente com a
ablação da identidade: o que o modelo faz bem é ordenar empresas, e a volatilidade também o faz.

**E o oráculo diz onde está a margem.** O melhor possível seria `0.968`; o sistema está em
`0.632`. Sobram **0.337** de margem, quase todos em distinguir *qual* das notícias
de uma empresa importa, que é precisamente aquilo que a Secção da ablação mostrou que este modelo
não consegue fazer.

## O que isto não permite concluir

Que a escolha do sistema seja boa em termos absolutos. A melhor política trivial obtém
`0.662` e o tecto é `0.968`: há muito espaço entre o que se faz e o que
seria possível.

E há uma linha de base que **não** foi medida, de propósito. A alternativa mais natural, ``ler as
primeiras cinco notícias que chegam ao feed'', exigiria a hora de publicação, que o conjunto de
dados histórico não guarda. Usar a ordem do ficheiro mediria a ordem alfabética das empresas. Uma
linha de base errada é pior do que uma linha de base em falta.

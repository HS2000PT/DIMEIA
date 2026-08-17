# Quanto do modelo de triagem é a notícia, e quanto é a empresa?

> **Gerado por** `scripts/evaluate_triage_identity.py`. Não editar à mão.
> **Protocolo:** o mesmo do treino congelado (divisão temporal, calibração de Platt na validação,
> semente 42). Os valores congelados são reproduzidos como porta de entrada:
> só-volatilidade `0.542` e só-contexto `0.538`.
> **Prevalência do teste (o chão da PR-AUC):** `0.378`

## O que se testa

O modelo de contexto recebe nove entradas. Sete descrevem a **empresa**, uma descreve o **dia**, e
uma só distingue duas manchetes da mesma empresa no mesmo dia (o comprimento do título).

A pergunta é se o que ele aprendeu se reduz a saber **de que empresa se trata**. Testa-se com o
preditor mais simples possível: para cada empresa, a taxa de positivos que ela teve no bloco de
treino. Ignora a manchete, ignora o dia, ignora tudo.

## Resultados

| Modelo | O que vê | PR-AUC | ROC-AUC | Precisão@5/dia |
|---|---|---|---|---|
| Contexto completo (o implantado) | as nove entradas | 0.538 | 0.658 | 0.632 |
| Só volatilidade | uma entrada, de nível de empresa | 0.542 | 0.665 | 0.632 |
| \textbf{Tabela de consulta por empresa} | **zero** informação sobre a notícia | 0.534 | 0.668 | 0.662 |
| Sem os indicadores de setor | tira 5 entradas de empresa | 0.543 | 0.663 | 0.629 |
| Sem volatilidade nem momento | tira as 2 entradas de empresa que restam | 0.389 | 0.522 | 0.390 |
| Sem NADA de nível de empresa | fica só o dia e a notícia | 0.378 | 0.503 | 0.368 |
| Só o comprimento do título | a única entrada de nível de notícia | 0.378 | 0.500 | 0.352 |

## Leitura

A tabela de consulta por empresa obtém **0.534** contra os
**0.538** do modelo implantado: uma diferença de **0.004**.

Esse preditor não vê a notícia. Não vê sequer o dia. Devolve um número por empresa, fixado no
treino, e nunca mais muda. Se ele reproduz o essencial do que o modelo faz, então o que o modelo
faz é, no essencial, **reconhecer a empresa**.

As ablações confirmam de onde vem o sinal: retirar as entradas de nível de empresa desmonta o
modelo, e o que fica quando só sobra o comprimento do título anda ao nível do chão.

## O que isto NÃO diz

Que a questão de investigação sobre triagem esteja mal respondida. A variante **com texto** tem
$384$ números por manchete, portanto tem informação real sobre a notícia, e essa comparação é a que
responde à pergunta.

O que isto diz é mais estreito e mais útil: **a variante que foi implantada como porta de decisão
não podia distinguir duas notícias da mesma empresa**, e portanto o seu desempenho agregado nunca
foi evidência de que soubesse triar notícias. É uma limitação do conjunto de entradas, não do
treino, e nenhuma quantidade de dados a resolveria.

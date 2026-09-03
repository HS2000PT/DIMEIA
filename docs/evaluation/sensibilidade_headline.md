# Quanto é que a manchete move a pontuação da triagem?

> **Gerado por** `scripts/check_headline_sensitivity.py`. Não editar à mão.
> **Fonte:** `models/triage_context_lr.joblib` (sha256 `2432e44e95417222…`), o artefacto congelado do
> modelo implantado. Não usa registos de produção nem dados novos.
> **Gerado a:** 2026-09-03 23:01 UTC ·
> **scikit-learn:** 1.8.0. O artefacto foi gravado com a versão do venv do projeto; se a
> versão acima for outra, regerar antes de citar qualquer número deste ficheiro.

## A pergunta

Fixados o ticker e o dia, oito das nove entradas do modelo são constantes: o setor não muda, e
`vol20`, `mom5` e `ret_event` vêm da série de preços e não do texto. A única entrada que varia
de notícia para notícia é `headline_len`, o número de caracteres do título. Quanto é que essa
entrada, sozinha, consegue mover a probabilidade calibrada?

As restantes entradas ficam nas **médias do conjunto de treino**, lidas do normalizador
guardado no próprio artefacto.

## 1. Só a manchete varia — mesmo ticker, mesmo dia

Comprimento do título de 20 a 200 caracteres:

| Setor | p mínima | p máxima | Amplitude |
|---|---:|---:|---:|
| banking | 0.2857 | 0.2908 | 0.0051 |
| consumer | 0.3293 | 0.3351 | 0.0058 |
| energy | 0.4328 | 0.4392 | 0.0064 |
| health | 0.3446 | 0.3506 | 0.0060 |
| tech | 0.4465 | 0.4529 | 0.0064 |

**Amplitude máxima atribuível à manchete: `0.0064`** — menos de um ponto percentual.

## 2. Só o setor varia — mesma manchete, mesmo dia

| Setor | p |
|---|---:|
| banking | 0.2871 |
| consumer | 0.3309 |
| health | 0.3462 |
| energy | 0.4345 |
| tech | 0.4483 |

**Amplitude entre setores: `0.1612`.**

## 3. Só a volatilidade varia — mesma manchete, mesma empresa

| `vol20` (volatilidade diária) | p |
|---|---:|
| 0.010 (1%) | 0.3736 |
| 0.040 (4%) | 0.5752 |

Média do treino: `0.0207`; desvio-padrão: `0.0165`.

**Amplitude atribuível à volatilidade: `0.2016`.**

## Leitura

A manchete move a pontuação `0.0064`; o setor move-a `0.1612`, cerca de
25 vezes mais; a volatilidade move-a `0.2016`, cerca de
31 vezes mais.

A crítica de que várias notícias do mesmo dia recebem «exatamente a mesma pontuação» é, à
letra, falsa: as pontuações diferem, porque os títulos têm comprimentos diferentes. Na
substância é correta, e passa aqui de afirmação a medição: **entre duas notícias da mesma
empresa no mesmo dia, a pontuação não pode diferir mais do que
0.6 pontos percentuais, e o que as separa é o comprimento do título e não
o seu significado.**

Isto é o mecanismo, medido no artefacto, do resultado que
`evaluation_gate_selectivity_unicos.md` observa nos registos de produção: a amplitude média
dentro de cada empresa é de `0.072`, e a maior parte dela vem de a volatilidade mudar de dia
para dia, não de a manchete mudar.

Não é um defeito de implementação: o modelo implantado é a variante **só-contexto**, que por
construção não recebe o texto. A variante com texto precisa do codificador SBERT, que não corre
na configuração de produção. A consequência a reter é a de que a pontuação da triagem, tal como
está implantada, ordena empresas e dias, não notícias.

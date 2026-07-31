# Deriva de distribuição — a limitação, medida em vez de afirmada

> Gerado por `scripts/evaluate_drift.py` em 2026-07-31 00:21 UTC.
> **Aditivo.** Não treina, não regrava modelos, não altera nenhum .md existente.

## Porque é que isto precisa de existir

O modelo de triagem foi treinado em FNSPID **2018-2023** e corre em **2026**. A tese
afirma essa distância como limitação em várias páginas. Afirmar é barato. Esta página
mede-a.

Duas medidas, porque veem coisas diferentes:

- **PSI** (*Population Stability Index*): quanto é que a massa de probabilidade mudou
  de sítio, por intervalo. Padrão de facto em risco de crédito, com bandas
  convencionadas: **< 0,10** estável · **0,10-0,25** moderada · **> 0,25**
  significativa.
- **Kolmogorov-Smirnov**: distância máxima entre as acumuladas. Apanha deslocações
  sistemáticas que o PSI dilui.

**Uma nota de método que muda a leitura.** Com dezenas de milhar de pontos, o valor-p
do KS rejeita quase sempre a hipótese nula, e por isso é quase inútil aqui. Uma
diferença estatisticamente significativa pode ser trivialmente pequena. O que se lê é
a **estatística *D*** — um tamanho de efeito em [0,1], que não cresce só por a amostra
ser grande — ao lado do PSI. Reportar o valor-p sozinho seria transformar "a amostra
é grande" em "a deriva é grave".

## 1. Deriva dentro do corpus: treino → teste

Treino **2018-01-02 a 2022-03-03** (28,574 linhas)
contra teste **2023-02-02 a 2023-12-18** (32,649 linhas).

Esta é a deriva que os **números congelados da tese já atravessaram**: o protocolo
treina no passado e avalia no futuro, pelo que a PR-AUC reportada já é uma medida
*sob* esta deriva, e não apesar dela.

| Feature | PSI | Banda | KS *D* | Média ref → atual | Δ média (σ) |
|---|---:|---|---:|---|---:|
| Volatilidade pré-evento (20 d) | **0.281** | significativa | 0.170 | 0.02073 → 0.01954 | -0.07 |
| Comprimento da manchete | **0.111** | moderada | 0.103 | 69.97 → 61.31 | -0.23 |
| Retorno do dia do evento | **0.020** | estável | 0.036 | 0.001261 → 0.002196 | +0.03 |
| Momentum a 5 dias | **0.014** | estável | 0.039 | 0.005253 → 0.008611 | +0.06 |

Prevalência do rótulo: **0.3854** no treino → **0.3781** no teste
(Δ -0.0074).

### Leitura

A feature que mais deriva é **Volatilidade pré-evento (20 d)** (PSI
0.281, banda *significativa*). Não é surpresa e vale a pena dizer porquê:
2018-2022 contém o choque de 2020, e a volatilidade realizada nesse período não
se parece com a de 2023. O modelo aprendeu num mundo mais agitado do que aquele
em que foi avaliado.

Ficam na banda estável: retorno do dia do evento, momentum a 5 dias.

### Entrada ou rótulo — qual se move mais?

A prevalência de positivos passa de **0.3854** para **0.3781**,
uma variação relativa de apenas **1.9%**. A validação, que fica entre as
duas no tempo, chega a **0.4704**.

Duas leituras que vale a pena separar, porque é fácil confundi-las:

1. **A deriva de entrada é a maior**: a volatilidade pré-evento move-se de forma
   significativa (PSI 0.281), enquanto o rótulo praticamente não se desloca
   de ponta a ponta (1.9%). O que muda é sobretudo *o que se dá ao
   modelo*, não *o que se lhe pede para reconhecer*.
2. **Mas o rótulo não é estável — é oscilante.** A sequência
   0.385 → 0.470 → 0.378 não é uma tendência: sobe e
   volta. Comparar só as pontas esconderia uma excursão de
   22% pelo meio. É o comportamento
   esperado se a materialidade seguir regimes de volatilidade em vez de uma deriva
   secular — o que é coerente com a volatilidade ser precisamente a feature que mais
   se move.

Para a defesa, a formulação honesta é esta: **a deriva existe, é sobretudo de
volatilidade, e é cíclica e não direcional.** Isso explica por que razão os números
congelados sobrevivem (o protocolo já atravessa uma dessas oscilações) e ao mesmo
tempo por que razão a cobertura conformal mais exigente se parte sob divisão temporal
(`evaluation_conformal.md`): uma cauda que oscila é exatamente o que uma garantia a
95% tem menos folga para absorver.

## 2. Instantâneo ao vivo: treino → hoje

Features de preço calculadas a partir das cotações de **2026-07-31** para a
watchlist (980 observações ticker-dia numa janela de ~6 meses).

> ⚠️ **Esta secção não é reprodutível, por construção.** Os preços de amanhã são
> outros. Fica datada e separada da medição de cima, que é offline e repetível.
> Só as features de preço entram: um instantâneo de preços não traz manchetes,
> pelo que o comprimento da manchete não é comparável aqui.

| Feature | PSI | Banda | KS *D* | Média ref → atual | Δ média (σ) |
|---|---:|---|---:|---|---:|
| Volatilidade pré-evento (20 d) | **2.866** | significativa | 0.344 | 0.02073 → 0.02376 | +0.18 |
| Momentum a 5 dias | **0.126** | moderada | 0.116 | 0.005253 → 0.004398 | -0.01 |
| Retorno do dia do evento | **0.030** | estável | 0.059 | 0.001261 → 0.0009523 | -0.01 |

### Leitura — e a ressalva que a torna utilizável

Deriva máxima **2.866** (Volatilidade pré-evento (20 d),
banda *significativa*) entre o corpus de treino e o mercado de hoje.

**Este número está inflacionado, e o próprio relatório o denuncia.** Repare-se na
última coluna: a média desloca-se apenas **+0.18σ**
(0.02073 → 0.02376). Um PSI de
2.9 com uma deslocação de média tão pequena não descreve um
mercado irreconhecível; descreve uma amostra com **poucas observações
independentes**.

A causa é mecânica e vale a pena ser explícito, porque é o primeiro reparo que um
arguente faz:

- As 980 linhas vêm de **10 tickers × ~98
  dias**, e não de milhares de situações distintas.
- A volatilidade a 20 dias é uma **estatística de janela deslizante**: dois dias
  consecutivos partilham 19 dos 20 retornos, ou seja ~95% da informação. As
  observações são quase repetições umas das outras.
- O resultado é uma distribuição "aos caroços": concentra-se nos poucos regimes
  de volatilidade que estes 10 títulos atravessaram nestes meses, deixando quase
  vazios vários intervalos-quantil do treino. O PSI penaliza intervalos vazios com
  força, e é exatamente isso que aqui acontece.

**Consequência para a leitura:** o valor da secção 1
(PSI 0.281, sobre 28,574 contra 32,649 observações
bem espalhadas) e este **não são comparáveis em magnitude**. Pôr os dois lado a
lado numa tabela seria enganador.

O que este instantâneo sustenta, e é bastante:

1. **A direção é real.** A volatilidade é, também aqui, a feature que mais se
   desloca — o mesmo veredicto qualitativo que a medição offline dá, obtido de
   forma independente sobre dados de hoje.
2. **A magnitude do desvio de média é modesta** (+0.18σ):
   o mercado de 2026 nesta watchlist não é um mundo alienígena face a 2018-2022.
3. **As outras features mantêm-se** nas bandas estável/moderada, o que é
   consistente com a secção 1.

A resposta honesta a *"o vosso modelo foi treinado em dados velhos"* é portanto:
sim, e a distância foi medida de duas formas independentes; é sobretudo de
volatilidade, a magnitude offline é *significativa* mas não extrema, e a PR-AUC de
2023 não deve ser tratada como promessa sobre 2026. Uma medição com esta ressalva
declarada vale mais do que um PSI de 2,9 apresentado sem ela.

## O que isto muda, concretamente

1. **A limitação deixa de ser uma frase.** Onde a tese dizia "o modelo foi treinado
   num período anterior", passa a poder dizer o PSI por feature e a banda em que cai.
2. **Dá um gatilho de re-treino, em vez de uma intuição.** A convenção de risco de
   crédito — re-treinar quando o PSI passa 0,25 — é um critério verificável que
   substitui "de vez em quando".
3. **Explica a quebra conformal.** A cobertura a α=0,05 parte-se sob divisão temporal
   (`evaluation_conformal.md`); esta página identifica a causa compatível — uma
   distribuição de volatilidade que se desloca de forma significativa e cíclica, que
   é precisamente o que uma garantia apertada tem menos folga para absorver.

Camada de **medição**: nada aqui altera o comportamento do sistema em produção.

# Predição conformal na triagem — uma garantia, e o preço dela

> Gerado por `scripts/evaluate_conformal.py` em 2026-07-31 00:11 UTC.
> **Aditivo.** Usa o modelo congelado tal como está; não treina nem regrava nada.
> Porta de reprodução: PR-AUC 0.5385 = congelada 0.5385.

## O que isto acrescenta a uma probabilidade calibrada

A triagem já devolve uma probabilidade calibrada por Platt. Calibração é uma
afirmação **agregada**: *entre os itens a que chamei 60%, cerca de 60% eram
materiais*. Descreve um histórico e **não promete nada** sobre o próximo item.

A predição conformal split troca o ponto pelo conjunto e ganha uma garantia
**livre de distribuição** e de **amostra finita**: escolhido um α, o conjunto contém
a classe verdadeira em pelo menos 1−α dos casos. Não assume normalidade, nem que o
modelo esteja bem especificado, nem sequer que seja bom.

Num problema binário há quatro conjuntos possíveis, e é a leitura deles que dá o
valor de produto:

| Conjunto | Lê-se |
|---|---|
| {material} | decisão definida: alertar |
| {não material} | decisão definida: não alertar |
| {ambos} | **"não sei"**, declarado, com garantia por trás |
| {} (vazio) | nenhuma classe é plausível ao nível pedido |

A terceira linha é a que interessa a esta tese. Um sistema que se recusa a prever
preços deve também saber dizer *não sei* sobre a sua própria triagem, em vez de
empurrar um 0,51 que finge decidir.

## A suposição — e é aqui que está o resultado

A garantia conformal precisa de **uma** coisa: **permutabilidade** entre o conjunto
de calibração e o que se vai prever. Num modelo treinado em 2018-2023 e a correr em
2026, é exatamente essa suposição que está sob suspeita.

Por isso corre-se a experiência **duas vezes**, e a comparação é o resultado:

1. **Divisão aleatória** do teste. A permutabilidade vale por construção, logo a
   garantia *tem* de se verificar. Serve de verificação da implementação.
2. **Divisão temporal** do teste (calibrar no passado, prever no futuro). É o que o
   sistema faz em produção, e a permutabilidade **não** está garantida.

### 1. Divisão aleatória

Calibração 16,324 · avaliação 16,325.

| α | Nominal | Cobertura | q̂ | Conjunto médio | Decisões | "Não sei" | Vazio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 0.95 | **0.951** ✅ | 0.619 | 1.784 | 21.6% | 78.4% | 0.0% |
| 0.10 | 0.90 | **0.902** ✅ | 0.595 | 1.605 | 39.5% | 60.5% | 0.0% |
| 0.20 | 0.80 | **0.803** ✅ | 0.558 | 1.323 | 67.7% | 32.3% | 0.0% |

### 2. Divisão temporal

Calibração até 2023-07-27 (16,324 linhas) · avaliação depois
(16,325 linhas).

| α | Nominal | Cobertura | q̂ | Conjunto médio | Decisões | "Não sei" | Vazio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 0.95 | **0.937** ⚠️ | 0.614 | 1.741 | 25.9% | 74.1% | 0.0% |
| 0.10 | 0.90 | **0.900** ✅ | 0.595 | 1.584 | 41.6% | 58.4% | 0.0% |
| 0.20 | 0.80 | **0.822** ✅ | 0.562 | 1.368 | 63.2% | 36.8% | 0.0% |

Prevalência de positivos: **0.394** na calibração → **0.362** na
avaliação.

## Leitura honesta

**Na divisão aleatória a garantia verifica-se; na temporal parte-se, mas só no
nível mais exigente.** É esse padrão, e não um veredicto único, o resultado.

A divisão aleatória bate no nominal aos três níveis, o que confirma que a
implementação está correta — se falhasse aqui, o erro seria meu e não dos dados.

Sob divisão temporal a cobertura fica aquém em: α=0.05 (cobertura 0.937).
Aguenta-se em: α=0.10 (0.900), α=0.20 (0.822).

A direção do padrão é a que a teoria prevê e vale a pena dizê-lo por extenso:
**quanto mais apertada a cobertura exigida, mais frágil ela é à deriva.** Pedir
95% obriga o limiar a apoiar-se na cauda da distribuição de calibração, e é
exatamente a cauda que se move primeiro quando o regime muda. A 80% e a 90% a
folga é suficiente para absorver o desvio desta janela.

Nada disto é um defeito do método conformal — é o método a **detetar** a quebra
de permutabilidade e a dizer em que nível ela começa a doer. Uma garantia que se
parte de forma mensurável vale mais do que uma probabilidade que nunca prometeu
nada e por isso nunca pode ser desmentida.

A prevalência de positivos move-se de 0.394 para 0.362 entre as
duas metades, o que é uma pista direta da causa e liga esta página à medição de
deriva em `evaluation_drift.md`.

Uma ressalva para não sobre-ler: esta divisão é **interna ao corpus 2018-2023**.
O salto que de facto preocupa é 2023 → 2026, e é maior do que este.

## O preço da garantia — e é este o número mais duro desta página

A garantia não é grátis, e o custo lê-se na coluna **"não sei"**:

- A **95%** de cobertura: decisão definida em **21.6%** dos casos, "não sei" em **78.4%**.
- A **90%** de cobertura: decisão definida em **39.5%** dos casos, "não sei" em **60.5%**.
- A **80%** de cobertura: decisão definida em **67.7%** dos casos, "não sei" em **32.3%**.

Dito sem rodeios: para poder prometer 90% de cobertura, o modelo de triagem só
consegue tomar uma decisão definida em **39.5%** das manchetes.
Nas outras **60.5%**, o conjunto honesto contém as duas classes.

Este número não contradiz a avaliação congelada — **explica-a**. A tese já reporta
que nenhum modelo com texto bate a volatilidade (PR-AUC 0,496 vs 0,542) e que o
valor da triagem está no mecanismo de ordenação, não na força preditiva. A predição
conformal põe um número nessa fraqueza a partir de outro ângulo, sem treinar nada de
novo: o sinal disponível simplesmente não separa a maioria dos itens ao nível de
confiança que se costuma exigir.

É também o mostrador que faltava ao limiar de produção. O `min_materiality` de 0,5
(derivado por rácio de custo em `evaluation_policy_sweep.md`) força **sempre** uma
decisão. Esta página mede em quantos casos essa decisão forçada assenta em pouco.

## O que fica

Camada de **medição**, não ligada à produção. A razão é de desenho e não de falta de
tempo: o produto promete uma cadência legível
(`docs/design/cadence_contract.md`), e um alerta que dissesse "não sei" a
61% dos itens romperia essa promessa sem que ninguém tivesse
decidido rompê-la. Onde isto **deve** entrar é na leitura crítica do sistema, e é lá
que entra.

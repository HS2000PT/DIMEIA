# Convergência multi-sinal — o acordo bate o melhor sinal isolado?

> Gerado por `scripts/evaluate_convergence.py` em 2026-08-01 12:04 UTC.
> **Aditivo.** Usa o modelo de triagem congelado tal como está; não treina nem regrava.
> Porta de reprodução: PR-AUC 0.5385 = congelada 0.5385.

## De onde vem a ideia

Adaptada de **worldmonitor.app**, recomendado pelo **coorientador Rafael Silva**.
O que se aproveita não é a escala (dezenas de camadas e de fornecedores de dados,
fora do âmbito de um projeto restrito a APIs gratuitas) mas o **princípio**: um
acontecimento em que várias
fontes independentes convergem merece mais atenção do que um em que só uma dispara.

## A pergunta, posta de forma falsificável

O sistema já calcula quatro coisas sobre um par (ticker, dia), e trata-as separadamente:

| Sinal | Pergunta a que responde | Já existia? |
|---|---|---|
| Preço | mexeu-se muito **para aquela ação**? | sim, o detetor |
| Volume | negociou-se muito mais do que o costume? | **novo** (a coluna vinha e era deitada fora) |
| Intensidade de notícia | quantas manchetes nesse dia? | sim, no fluxo |
| Triagem | probabilidade calibrada de ser material? | sim, o modelo congelado |

Nenhum vê os outros. **Ao mesmo orçamento diário de alertas, a fusão apanha mais dias
materiais do que o melhor sinal sozinho?**

## Método

- **Unidade de análise:** o par (ticker, dia), que é a unidade do rótulo. Ordenar
  *manchetes* encheria o topo com cópias do mesmo nome; foi o erro apanhado no varrimento
  de política, e não se repete.
- **Pesos derivados, não escolhidos:** regressão logística sobre os quatro sinais
  estandardizados, ajustada na **validação** e avaliada no **teste**. O modelo de fusão é
  linear de propósito, para as contribuições por sinal serem exatas e não aproximadas.
- **Volume:** z-score do `log` do volume contra a norma dos 20 dias anteriores, pela
  mesma
  convenção anti-lookahead do detetor de preço. O logaritmo é necessário porque o volume
  é fortemente assimétrico e um z sobre o valor bruto dispararia quase só para cima.

Painel de teste: **1,951** pares (ticker, dia), prevalência **0.3511**.

> ⚠️ **O painel é bastante menor do que o corpus sugere, e a razão importa.** As
> 50,359 manchetes de validação e teste colapsam em apenas 3,564 pares
> (ticker, dia), porque essa é a unidade do rótulo. Além disso, a cobertura de tickers
> do FNSPID **varia ao longo do tempo**: o bloco de treino tem 13 tickers, mas a
> validação tem 8 e o teste 9. Não é um defeito do
> alinhamento (o volume casa em 100% das linhas); é uma propriedade do corpus. A
> consequência é que este estudo assenta numa amostra bem mais pequena do que os
> estudos de recuperação e de triagem, e as diferenças abaixo devem ser lidas com essa
> reserva.

### Pesos derivados

| Sinal | Peso (sinais estandardizados) |
|---|---:|
| `price_z` | +0.1191 |
| `volume_z` | +0.0911 |
| `news_intensity` | -0.2827 |
| `triage_p` | +0.5550 |

**O peso da intensidade de notícia é NEGATIVO (-0.2827), e isso é um achado**
**e não um erro de sinal.** Mais manchetes num dia torna esse dia *menos* provável de
ser material. A explicação compatível com o que já se sabe deste corpus: dias com
muitas manchetes tendem a ser dias de conteúdo automático (resumos de mercado, listas
de sugestões, atualizações de desequilíbrio de ordens) e não dias de acontecimento
real. É o mesmo problema de qualidade à entrada que motivou o filtro de relevância em
produção, a aparecer agora do lado quantitativo. Um score de convergência com pesos
**escolhidos à mão** teria quase de certeza posto aqui um peso positivo, e estaria
errado; foi por isto que a regra deste projeto é derivar os pesos.

## Resultados

| Sinal | PR-AUC | p@1/dia | p@3/dia | p@5/dia |
|---|---:|---:|---:|---:|
| `price_z` | 0.3392 | 0.3394 | 0.3469 | 0.3403 |
| `volume_z` | 0.3632 | 0.3846 | 0.3680 | 0.3403 |
| `news_intensity` | 0.3864 | 0.4299 | 0.3922 | 0.3891 |
| `triage_p` | 0.5146 | 0.6335 | 0.5038 | 0.4344 |
| **convergência** | 0.4751 | 0.5837 | 0.4721 | 0.4389 |

### A fusão contra o melhor sinal isolado

| Orçamento | Melhor sinal isolado | Valor | Convergência | Δ |
|---|---|---:|---:|---:|
| top-1/dia | `triage_p` | 0.6335 | 0.5837 | **-0.0498** |
| top-3/dia | `triage_p` | 0.5038 | 0.4721 | **-0.0317** |
| top-5/dia | `triage_p` | 0.4344 | 0.4389 | **+0.0045** |

## Leitura honesta

**Misto: a fusão ganha em 1 de 3 orçamentos.**
Ganha em top-5 (+0.0045); não ganha em top-1 (-0.0498), top-3 (-0.0317).

Um resultado misto não sustenta ligar isto à produção. Um ganho que depende do
orçamento escolhido é um ganho que se pode ter escolhido, e o critério deste projeto
é que uma capacidade nova só entra quando a medição a sustenta sem se escolher o
ângulo.

## O que fica

O **detetor de volume** é uma capacidade genuinamente nova e de custo zero em dados: a
coluna já vinha em todas as barras e estava a ser deitada fora. Responde à segunda
pergunta que qualquer operador faz depois de ver um movimento (*e com quanta gente a
negociar?*), e é transparente pela mesma construção do detetor de preço.

O **score de convergência** fica como medição e **não** é ligado à produção, e a
razão é a evidência desta página. O que dela se aproveita para o produto é a *humana*
da convergência, `agreement_count`: dizer "três dos quatro sinais dispararam"
comunica de imediato e é verificável olhando para os componentes, ao passo que um
score fundido de 0,73 não se verifica em lado nenhum.

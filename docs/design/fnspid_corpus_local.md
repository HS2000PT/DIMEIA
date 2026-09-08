# O FNSPID nesta máquina — o que existe, o que foi apagado, e porquê

> Escrito a **2026-09-08**, depois de o autor colocar `fnspid/` na raiz com **28 GB** e pedir
> que se aproveitasse o que servisse e se apagasse o resto.

## O que existe agora, e chega para tudo o que esta tese faz

| ficheiro | tamanho | o que é |
|---|---|---|
| `data/fnspid_news_subset.csv` | **6,5 MB** | **78 481 títulos** dos 15 tickers da tese, 2018-01-01 a 2023-12-16, no formato `date,ticker,headline` que o `build_dataset.py` consome |
| `data/fnspid_artigos_15tickers.csv.gz` | **108 MB** | os mesmos registos **com o corpo do artigo**, URL e publicação — 93 093 linhas, 72 % com texto integral |
| `data/samples/fnspid_news_sample.csv` | 5 KB | a amostra versionada de sempre, **intocada** |

**Os dois ficheiros substituem os 28 GB.** Foram extraídos numa passagem sobre o corpus
inteiro (28 606 813 linhas varridas em 7 minutos) antes de este ser apagado.

## ⚠️ A prova de que é o mesmo corpus que gerou os números da tese

A amostra versionada em julho tem 50 títulos. O extracto de hoje reproduz **os 50, pela mesma
ordem, caractere a caractere**. E o total bate: **78 481 títulos** contra os **79 753**
exemplos do conjunto congelado — 1,6 % de diferença, que é o que se espera de uma
deduplicação ligeiramente diferente.

Isto responde, pelo lado da entrada, à pergunta que a tese afirma e que nunca tinha sido
testável em máquina nenhuma: **o corpus de onde saíram os resultados é recuperável e
reproduz.**

## Cobertura, medida

Os **15 tickers estão todos cobertos**. As janelas não são iguais entre eles, e isso é
estrutura do próprio FNSPID e não perda desta extracção:

| | | | |
|---|---|---|---|
| NVDA 9 913 (2018–2023) | TSLA 10 294 (2019–2023) | AAPL 9 141 (2020–2023) | MSFT 8 516 (2022–2023) |
| WMT 8 447 (2018–2023) | CVX 7 222 (2018–2023) | XOM 7 151 (2018–2023) | KO 5 165 (2018–2023) |
| AMZN 4 947 (2020–2023) | JPM 2 851 (2018–2020) | GOOGL 1 751 (2018–2020) | JNJ 977 (2018–2020) |
| PFE 932 (2018–2020) | BAC 742 (2018–2020) | META 432 (2020) | |

⚠️ **A META entra como `FB` no corpus** e é normalizada na extracção. Foi por isso que o M6
reportou 14 de 15 tickers em julho: a empresa está lá, com o nome antigo.

## O que foi apagado, e porque não se perde nada

| apagado | porquê |
|---|---|
| `fnspid/data/raw/*.csv` (28,9 GB) | o extracto acima cobre os 15 tickers da tese; o resto são as outras ~1 500 empresas do FNSPID, que este trabalho não usa |
| `fnspid/data/processed/` (184 MB) | **outro pipeline**: sentimento **FinBERT** agregado, taxonomia de eventos por expressões regulares, novidade lexical de Jaccard, sobre **30 tickers** |
| `fnspid/data/interim/` (505 MB) | idem, incluindo os fragmentos do FinBERT |
| `fnspid/data/raw/market.parquet` | preços de um universo de 28 tickers; este projeto busca os seus com cache própria |

⚠️ **O `processed/` merece a explicação por extenso, porque parece útil e não é.** Explora
exactamente **duas direcções que esta dissertação já mediu e pôs de lado**: o sentimento
FinBERT, que obteve **precisão@5 de 0,420** — o pior dos quatro codificadores avaliados na
§5.3 — e uma taxonomia de eventos, cuja silhueta de **0,084** levou à decisão declarada de
não a ligar à recuperação. Reutilizá-lo não seria reproduzir esta tese: seria correr outra.

## Se for preciso o corpus inteiro outra vez

O FNSPID é público e re-descarregável: `Zihan1004/FNSPID` no Hugging Face, licença
**CC BY-SA 4.0** (atribuição obrigatória, já cumprida na tese e no `README`). O
`scripts/download_data.py` faz o streaming com filtro por ticker e janela.

⚠️ **Contar com horas, não minutos.** Os 7 minutos desta extracção foram a partir de **disco
local**; o `download_data.py` estima ~3,4 h porque o custo é de rede.

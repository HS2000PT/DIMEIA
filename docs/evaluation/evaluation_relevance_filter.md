# evaluation_relevance_filter.md — proveniência do corpus e efeito do filtro

> Gerado por `scripts/evaluate_corpus_and_filter.py` a 2026-09-10 00:24 UTC. **Não editar à mão.**

## 1. O corpus de avaliação

| item | valor |
|---|---|
| manchetes (com setor conhecido) | **18599** |
| tickers | 15 |
| primeira data | 2026-05-29 |
| última data | 2026-06-26 |
| amplitude | **28 dias** |

⚠️ **28 dias**, não meses. Um corpus desta amplitude não sustenta afirmações sobre
generalização temporal, e é por isso que o resultado de recuperação é reportado como
preliminar e repetido à escala sobre o FNSPID multi-ano.

## 2. O que o filtro de relevância deita fora

Restrito aos 10 tickers com lista de aliases, que são os
que o produto varre.

| decisão | manchetes | quota |
|---|---|---|
| **mantidas** | 4843 | **28.8%** |
| descartadas | 11997 | 71.2% |
| &nbsp;&nbsp;— boilerplate de mercado | 500 | 3.0% |
| &nbsp;&nbsp;— não menciona a empresa | 11497 | 68.3% |
| total | 16840 | 100% |

**Leitura.** O trabalho é feito pela regra da menção, não pela lista de boilerplate: os
padrões de resumo de mercado explicam apenas 3.0% dos descartes. E
a taxa de retenção depende da lista de aliases: tickers sem entrada caem no fallback
"só o símbolo conta", e quase nenhuma manchete escreve o símbolo.

## 3. Os vizinhos recuperados são anteriores à consulta?

300 consultas, top-5, cross-ticker — o mesmo protocolo da avaliação.

| posição temporal do vizinho | n | quota |
|---|---|---|
| **posterior** à consulta | 610 | **40.7%** |
| mesma data | 380 | 25.3% |
| anterior | 510 | 34.0% |

**Leitura, e é a que corrige a palavra.** A avaliação não restringe os candidatos a
serem anteriores; só a linha de base de recência usa datas. Num corpus de 28 dias, o resultado é que apenas 34.0% dos vizinhos são
anteriores. **A métrica não é afectada** — mede concordância de setor, e o setor de
uma manchete não muda com o tempo — mas o que se mede é *recuperação semântica de
itens do mesmo setor*, e não *recuperação de precedentes*.

**Em produção o problema não existe:** a base curada é de 2018--2023 e as consultas
são de 2026, portanto todos os casos recuperados são anteriores por construção.

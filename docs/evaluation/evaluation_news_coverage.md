# Cobertura do funil de notícias — quanto é que a fonte perde

> Gerado por `python scripts/evaluate_news_coverage.py --escrever`. **Não editar à
mão.**

## A pergunta

A tese afirmava que a camada de notícias corre sobre uma fonte gratuita e por isso é
limitada, sem nunca dizer **quanto**. Este documento converte essa afirmação num
número,
seguindo o mesmo padrão que já se aplicou à deriva e à incerteza.

## O que isto mede — e o que não mede

**Mede:** nos dias em que a acção se moveu de forma invulgar, com que frequência
existia
pelo menos uma manchete captada para esse ticker na janela [dia−1, dia].

**Não mede** se a manchete era *a certa*. Saber qual a história que realmente moveu
uma
acção num dado dia exige julgamento humano caso a caso; fabricar esse rótulo
tornaria o
número maior e sem valor. O que se segue é portanto um **limite superior** da
cobertura:
o funil não pode ter visto a história certa em mais dias do que aqueles em que viu
alguma coisa.

## Método

- Dias invulgares identificados com `detect_all`, **o detector de produção**,
  com janela de 20 dias.
- Janela de notícia [dia−1, dia]: uma história publicada após o fecho move a sessão
  seguinte, que é o mesmo alinhamento anti-lookahead usado no resto do sistema.
- Corpus: `data/samples/backfill_kb.jsonl`, manchetes **já filtradas por relevância**
  (a contagem é do que passou o filtro, não do que a fonte devolveu em bruto).

## Resultados

| ticker | dias c/ manchete | manchetes/dia | dias \|z\|≥1,5 | cobertos | dias
\|z\|≥3,0 | cobertos |
|---|---:|---:|---:|---:|---:|---:|
| `AAPL` | 265 | 16.0 | 35 | 32 (91%) | 7 | 5 (71%) |
| `AMD` | 311 | 9.5 | 29 | 28 (97%) | 4 | 4 (100%) |
| `AMZN` | 219 | 17.4 | 35 | 29 (83%) | 2 | 2 (100%) |
| `GOOGL` | 211 | 16.7 | 36 | 26 (72%) | 5 | 5 (100%) |
| `JNJ` | 292 | 4.2 | 39 | 39 (100%) | 3 | 3 (100%) |
| `JPM` | 313 | 7.7 | 30 | 30 (100%) | 5 | 5 (100%) |
| `META` | 252 | 14.7 | 35 | 34 (97%) | 8 | 7 (88%) |
| `MSFT` | 214 | 14.5 | 35 | 30 (86%) | 5 | 5 (100%) |
| `NFLX` | 327 | 8.6 | 36 | 35 (97%) | 6 | 6 (100%) |
| `NVDA` | 158 | 21.6 | 36 | 18 (50%) | 4 | 2 (50%) |
| `TSLA` | 274 | 20.6 | 36 | 33 (92%) | 1 | 1 (100%) |
| `XOM` | 307 | 4.6 | 35 | 35 (100%) | 2 | 2 (100%) |

### Global

- `|z| ≥ 1.5`: 369 de 417 dias invulgares tinham manchete captada — **88.5%**
- `|z| ≥ 3.0`: 47 de 52 dias invulgares tinham manchete captada — **90.4%**

## Uma hipótese testada e REFUTADA

A NVDA é o ticker **pior coberto** e ao mesmo tempo o de **maior densidade**: mais
manchetes por dia coberto do que qualquer outro, em muito menos dias distintos. A
explicação óbvia é truncagem: o Finnhub devolve no máximo ~250 itens por pedido, e o
*backfill* pede janelas de sete dias, portanto uma semana ruidosa bateria no tecto e
os dias mais antigos dessa janela desapareceriam por inteiro.

**A hipótese foi testada e não se sustenta.** Contando os itens por janela de sete
dias,
**nenhuma janela de nenhum ticker chegou perto do tecto**: o máximo observado foi de
165
itens, contra os ~250 disponíveis. A cobertura irregular da NVDA é uma propriedade
de como
a fonte a etiqueta, e não um artefacto do modo como os dados foram pedidos.

Fica registado por duas razões. A primeira é que a explicação por truncagem é
plausível e
estaria errada. A segunda é que ela teria sido *acionável* — bastaria estreitar a
janela —
e agir sobre uma causa refutada é como se perde tempo a resolver o problema errado.

## Leitura

O número responde à pergunta que o caso da NVDA levantou: quando a acção se mexe a
sério, o sistema tem sequer alguma coisa para mostrar? A parte não coberta é a
fracção
em que **nenhuma correcção de código ajuda** — se a fonte não etiquetou a história ao
ticker, ela não entra no funil e nenhum dos cinco gates chega a ser consultado.

Isto separa duas limitações que antes andavam juntas: o que o **desenho** descarta
(os
gates, medidos no funil de alertas) e o que a **fonte** nunca entregou. Só a
primeira é
uma decisão deste trabalho.

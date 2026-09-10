# §5.3 — plano de execução, com os dois ramos medidos

> ⚠️ **2026-09-10: O RAMO A CORREU E ENCONTROU UM TERCEIRO PROBLEMA, maior do que os dois que
> este plano previa.** O corpus recupera-se — 3 709 manchetes contra as 3 714 originais, a 0,13%
> — mas ao verificar a janela descobriu-se que **a janela declarada nunca foi a janela medida**.
> Ler a secção «O tecto da API» no fim deste ficheiro **antes** de executar qualquer coisa daqui.
> A decisão sobre o que fazer é do autor e está lá enunciada.

> 2026-09-09, ~23:15 UTC. Levantamento completo; **nada foi aplicado.** Escrito para que a
> execução seja mecânica quando houver execução de comandos na máquina do autor.

## O que está em causa

Todo o §5.3 assenta num corpus de **3 714 manchetes do Finnhub**, cinco setores, janela de 27
dias fechada a **2026-06-25**. O CSV de origem (`data/finnhub_news.csv`) **não existe** — `data/`
tem o FNSPID bruto e mais nada dessa família. Os três artefactos que dele derivam
(`evaluation_results.md`, `evaluation_per_sector.md`, `evaluation_retrieval_embedders.md`)
existem, mas não são reproduzíveis, e os próprios ficheiros já se declaram «avaliação
preliminar».

Pela regra fixada a 09-09 — *o que não se reproduz nesta máquina desconsidera-se* — saem. Mas há
uma alternativa que o plano original não considerou, e é por isso que este documento tem dois
ramos.

## Ramo A — recuperar o corpus (preferido, decidido pelo autor)

O plano gratuito do Finnhub serve cerca de **um ano** de *company news*. A janela original fecha
a 2026-06-25; a 2026-09-09 continua **dentro** do alcance da API. O `fetch_finnhub_news.py` só
sabia recolher janelas que terminam hoje, pelo que ganhou uma opção `--fim` (aditiva — sem ela o
comportamento é o de sempre). **Já aplicada na árvore.**

```
.venv\Scripts\python.exe scripts\fetch_finnhub_news.py --days 27 --fim 2026-06-25
```

Critério de aceitação, a fixar **antes** de ver o resultado: o corpus é utilizável se trouxer a
ordem de grandeza certa (milhares de manchetes, cinco setores representados). Se vier vazio ou
com algumas centenas, a janela já não está servida e passa-se ao ramo B.

Se resultar, regenerar os três artefactos e propagar:

```
python scripts/evaluate.py
python scripts/evaluate_per_sector.py
python scripts/evaluate_retrieval_embedders.py
```

⚠️ **Os números vão mudar**, e isso é esperado e não é um problema: o feed não é imutável, há
artigos retirados desde então. O que muda é a natureza da propagação — passa a ser *atualizar
números* em vez de *apagar uma figura*, e a §5.3 volta a ser reproduzível, que é o critério.
A janela recolhida passa a ser declarada com a data de recolha, não com a de 2026-06-25.

## Ramo B — o corte, se o corpus não vier

### O que sai

| onde | o quê |
|---|---|
| Figura 5.6 (`fig:av_recuperacao`) | **toda** — 0,126 · 0,240 · 0,346 · 0,420 · 0,467 · 0,514 · 0,538 · 1,000 |
| §5.3.2 «Resultado» | os três parágrafos que leem a figura, incluindo o do FinBERT |
| §5.3.3 | o parágrafo da alternativa trivial (0,467) e a comparação por setor |
| Figura 5.7, **painel A** | 0,712 · 0,448 · 0,419 · 0,272 · 0,171 e os valores de acaso |
| §5.3.4 (fim) | a comparação de codificadores: MPNet 0,538, E5 0,504, BGE 0,513, recência 0,126 |

### O que fica, e é o que sustenta a QI2

O **painel B** da Figura 5.7: precisão@5 de **0,595** no protocolo simétrico e **0,513** no
causal, com o acaso a descer de 0,333 para 0,259 — a margem varia apenas de +0,262 para +0,254.
Medido sobre o FNSPID, que se reproduz. A QI2 continua respondida; perde os comparadores.

### Alcance medido, ocorrência a ocorrência

Árvore PT (a EN espelha):

| valor | ch2 | ch5 | ch6 | apêndice | slides | guia |
|---|---:|---:|---:|---:|---:|---:|
| 0,514 | 0 | 5 | 3 | 2 | 1 | 1 |
| 0,538 | 0 | 8 | 2 | 1 | 2 | 0 |
| 0,346 | 0 | 3 | 1 | 2 | 1 | 1 |
| 0,240 | 0 | 3 | 2 | 2 | 1 | 1 |
| 0,467 | 0 | 3 | 1 | 2 | 2 | 1 |
| 0,126 | 0 | 2 | 1 | 2 | 1 | 0 |
| 0,513 | 0 | 2 | 2 | 2 | 1 | 1 |
| 0,420 · 0,712 · 0,504 · 0,429 | 0 | 6 | 0 | 0 | 0 | 0 |

Mais o quizz. **O Capítulo 2 tem zero ocorrências numéricas** — trata o FinBERT
qualitativamente, pelo que não precisa de corte, apenas de rever a frase que remete para a
medição do Cap. 5.

⚠️ **Duas portas vão disparar, e com razão:** o `check_tese_numeros` (números da tese sem fonte
nos artefactos) e o `check_apendice_xref` (o apêndice promete que estes valores aparecem na
§5.3). As entradas correspondentes têm de sair do manifesto **na mesma passagem**, senão a porta
acusa a tese correta.

⚠️ **A Matriz de Evidência ganha linhas de «retirada»**, e é aí que este corte se defende: uma
afirmação retirada com a razão escrita vale mais do que uma afirmação mantida sobre um corpus que
já não existe.

## O bloqueio, e é o mesmo nos dois ramos

**Nenhum dos ramos fecha sem execução de comandos na máquina do autor.** O ramo A precisa da API
do Finnhub (o contentor tem a chave mas a rede recusa `finnhub.io`). O ramo B precisa de
regenerar a Figura 5.7 sem o painel A, o que obriga a correr o gerador contra o
`kb_fnspid_sbert.jsonl` — **690 MB**, acima do que a ponte de ficheiros transfere.

O que **já não** é bloqueio: a compilação. A cadeia LaTeX foi instalada no contentor e reproduz a
árvore PT com fidelidade verificada — **134 páginas e overfull máximo 5,68 pt, iguais ao PDF do
autor**, 0 erros e 0 referências ou citações indefinidas. Qualquer edição de texto pode portanto
ser verificada aqui antes de ser aplicada.

---

## ⚠️ O tecto da API — descoberto a 2026-09-10, e muda o âmbito deste plano

### O que se mediu

O `/company-news` do plano gratuito devolve **no máximo ~250 itens por pedido** e, ao atingir esse
tecto, **ignora o `from`**. Prova directa, com o mesmo `to` e três janelas diferentes:

| pedido | manchetes | período realmente coberto |
|---|---:|---|
| `--days 5` AAPL | 248 | 2026-06-21 … 2026-06-25 |
| `--days 13` AAPL | 248 | 2026-06-21 … 2026-06-25 |
| `--days 27` AAPL | 248 | 2026-06-21 … 2026-06-25 |

**As três devolvem exactamente as mesmas 248 manchetes, dos mesmos cinco dias.** Pedir 27 dias e
pedir 5 dá o mesmo resultado, e nada no processo o diz: não há erro, não há aviso, e o corpus sai
com a forma certa e o período errado.

⚠️ **O defeito não é do script.** Verificado antes de o atribuir: o pedido constrói `from` e `to`
correctamente e o tecto próprio do script (1 000) não dispara — o log imprime `248/248`, ou seja
foi a API que devolveu 248.

### Porque é que isto é pior do que uma nota de rodapé

A truncagem é **proporcional ao volume de notícias da empresa**, logo a cobertura temporal fica
entrelaçada com a identidade da empresa:

| | cobertura real na «janela de 27 dias» |
|---|---|
| NVDA | **3 dias** |
| MSFT · GOOGL · AMZN | 4 dias |
| AAPL · META · TSLA | 4–5 dias |
| JPM | 11 dias |
| WMT · CVX · BAC | 15–18 dias |
| XOM · JNJ · PFE | 22–26 dias |
| KO | 28 dias |

E a §5.3 mede **precisão de recuperação por setor**, com **sete das quinze** empresas em
tecnologia — que são precisamente as de janela mais estreita. A composição setorial do corpus
está confundida com a truncagem, e a secção seguinte mostra que a confusão é exacta e não
aproximada.

### Quanto se perdia, medido com a janela partida em fatias de 3 dias

| ticker | sem fatiar | com fatias de 3 dias | razão |
|---|---:|---:|---:|
| AAPL | 248 | **1 357** | 5,5× |
| NVDA | 249 | **2 450** | 9,8× |
| KO | 246 | 253 | 1,03× |

O KO quase não muda porque tem pouco volume e **nunca esteve truncado** — e é o controlo que
mostra que o efeito é do volume e não do método de recolha.

⚠️ **E o meu primeiro detector deu um falso positivo no KO**, por marcar tudo acima de 240 itens
como «no tecto». O KO tem 246 na janela inteira sem estar truncado. O detector fica (um aviso a
mais é preferível a um corpus truncado em silêncio), mas **o aviso não é prova de truncagem: a
prova é fatiar e comparar.**

### O que se acrescentou ao recolhedor

- **`--fatiar N`** — parte a janela em fatias de N dias, uma chamada por fatia, para nenhum
  pedido bater no tecto. Aditivo: sem a opção, o comportamento é o de sempre.
- **Deteção de tecto** — um pedido que volte com ≥240 itens imprime um aviso por ticker e um
  resumo no fim, a dizer em voz alta que *a janela declarada não é a janela recolhida*.
- **`--pausa`** (1,1 s por omissão) — fatiar multiplica os pedidos, e o plano gratuito serve
  60/min; sem pausa a recolha bate em 429 a meio e devolve um corpus incompleto, que é
  exactamente o defeito que isto existe para não ter.

### A decisão, e é do autor

Há agora **três** caminhos, não dois:

1. **Reproduzir o corpus original tal como era** (sem fatiar, 3 709 manchetes). A §5.3 volta a
   ser reproduzível e os números mudam pouco — mas **a declaração de «27 dias» continua falsa** e
   teria de ser corrigida para o que o corpus é: *as ~250 manchetes mais recentes por empresa
   antes de 2026-06-25*, com a cobertura a variar de 3 a 28 dias por empresa.
2. **Recolher a janela a sério** (fatiada) e re-medir a §5.3 sobre esse corpus. Fica honesta e
   maior, e é a única opção em que a frase «janela de 27 dias» passa a ser verdade. Custo: os
   números da §5.3 mudam de forma substancial, não marginal — é uma **medição nova**, não uma
   actualização, e obriga a propagar por figuras, texto, slides e guia.
3. **O ramo B** (cortar a §5.3 e ficar com o painel B da Figura 5.7, medido sobre o FNSPID).

⚠️ **Nada foi propagado e nenhum artefacto congelado foi tocado.** As recolhas desta sessão
foram todas para `data/_arquivo/` com `--out` e `--sample` explícitos.

### ⚠️ A consequência que fecha o argumento: o chão trivial de `0,467` é o tecto da API

A §5.3.3 lê o desequilíbrio do corpus como uma propriedade do fluxo de notícias:

> «O corpus não está equilibrado: $1\,736$ das $3\,714$ notícias, quase metade, pertencem ao
> setor da tecnologia.»

$1\,736 / 3\,714 = 0{,}4674$. E o mapa de setores da avaliação tem **sete das quinze** empresas
em tecnologia: $7/15 = 0{,}4667$. **Os dois números são o mesmo à terceira casa, e isso não é
coincidência.**

Porque o tecto devolve ~248 manchetes por empresa **independentemente do volume real dela**, cada
empresa contribui com a mesma quantidade e a composição setorial do corpus passa a ser a
**proporção de empresas por setor**, não a proporção de notícias. O «desequilíbrio do corpus» que
a tese descreve é um artefacto do instrumento de recolha.

E o chão trivial da §5.3.3 — devolver sempre cinco notícias de tecnologia, que vale `0,467` — é
exactamente essa proporção. **O valor do comparador mais importante da §5.3 é uma consequência do
tecto da API.**

⚠️ **Qual é a direção do efeito, e é desconfortável.** Na recolha honesta as empresas de
tecnologia contribuem muito mais (a AAPL 1 372 contra 248, a GOOGL 2 333, a NVDA ~2 450) e as de
pouco volume quase nada (o KO 253). Logo a fração de tecnologia **sobe muito** acima de 46,7%, e
com ela sobe o chão trivial. Como o método mede `0,514` contra esse chão de `0,467`, uma margem
já pequena, **é possível que no corpus honesto o chão trivial ultrapasse o método** — o que
reforçaria, e não enfraqueceria, o argumento que a §5.3.3 já faz.

**Isto não está medido ainda** e não se escreve nada sobre ele antes de estar. É a próxima
medição, sobre o corpus fatiado.

---

## A §5.3 MEDIDA NO CORPUS HONESTO — 2026-09-10

Corrida sobre as 18 599 manchetes fatiadas, com `--out` e `--fig` para `data/_arquivo/`.
**Nenhum congelado foi tocado.** Artefactos: `_53_agregado_honesto.md` e `_53_setor_honesto.md`.

### O agregado — e a leitura corta nos dois sentidos

| | original (3 709) | honesto (18 599) |
|---|---:|---:|
| SBERT (MiniLM), P@5 | 0,514 | **0,779 ± 0,016** |
| lexical | 0,346 | 0,746 ± 0,021 |
| recência | 0,126 | 0,560 ± 0,009 |
| taxa-base do acaso | 0,467 | **0,685 ± 0,013** |
| **margem sobre o acaso** | **+0,047** | **+0,094** |
| trivial «devolver sempre tecnologia» | 0,467 | **0,840** |

**Duas coisas verdadeiras que apontam para lados diferentes, e ambas têm de ser ditas.** A margem
do método sobre o acaso **duplica** — de `+0,047` para `+0,094` —, o que é a favor do método. E ao
mesmo tempo o chão trivial passa a `0,840` e **bate o método**, o que é contra o agregado como
medida.

⚠️ **A taxa-base do acaso não é igual ao chão trivial, e a diferença importa.** O acaso do script
sorteia candidatos de **outra empresa** e mede quantos são do mesmo setor: `0,685`. O chão trivial
da §5.3.3 devolve sempre tecnologia e acerta na fração de consultas que são de tecnologia:
`0,840`. Compará-los como se fossem o mesmo número seria repetir, pelo lado da interpretação, o
erro que este documento descreve.

### Por setor — e é aqui que a conclusão da QI2 se decide

| setor | n | P@5 | acaso | razão |
|---|---:|---:|---:|---:|
| tecnologia | 15 624 | 0,887 | 0,808 | 1,1× |
| banca | 957 | 0,192 | 0,025 | **7,7×** |
| energia | 721 | 0,347 | 0,020 | **17×** |
| saúde | 569 | 0,243 | 0,015 | **16×** |
| consumo | 728 | 0,071 | 0,018 | 3,9× |

**✅ A afirmação defensável da QI2 SOBREVIVE.** A tese formula-a, desde a sessão 61, como *supera
a taxa-base dentro de cada um dos cinco setores* — precisamente para não depender do agregado. No
corpus honesto isso continua verdade **nos cinco**, e nos três setores pequenos por margens de 4 a
17 vezes o acaso.

⚠️ **O que muda, e não é pequeno:** a margem da tecnologia colapsa de `+0,283` (0,712 contra 0,429
no corpus antigo) para `+0,079` (0,887 contra 0,808). Não é o método a piorar — é o acaso a subir,
porque num corpus 84% tecnológico devolver tecnologia quase não é informação. E o **consumo** fica
fraco em termos absolutos (`0,071`), ainda que 3,9× o acaso.

### O que isto significa para a decisão

O ramo 2 (re-medir) **não destrói a §5.3**: mantém a conclusão que a tese já escolheu defender e
troca os números por números reproduzíveis, sobre uma janela que passa a ser verdade. O custo é
propagação real — figuras, texto, slides e guia — e a §5.3.3 tem de ser reescrita, porque a
alternativa trivial deixa de estar *perto* do método e passa a estar *acima* dele.

O ramo 1 (reproduzir com tecto) mantém os números publicados e obriga a corrigir a declaração da
janela para o que ela é: *as ~250 manchetes mais recentes por empresa antes do corte, com
cobertura de 3 a 28 dias segundo o volume da empresa*. É a opção mais barata e a única que não
mexe em nenhum número — mas deixa a §5.3.3 a atribuir ao fluxo de notícias um desequilíbrio que é
do instrumento.

**Nenhuma das duas foi executada. A escolha é do autor.**

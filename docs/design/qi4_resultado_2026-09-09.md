# QI4 — o ajuste contrastivo não melhora a comparabilidade. É um negativo limpo.

> 2026-09-09, ~23:00 UTC. Porta de colapso fechada nos três braços **antes** de qualquer
> métrica ser lida. Medido fora da máquina do autor — ver «Proveniência», que é a parte que
> decide o que fazer a seguir.

## 1. A porta de colapso: nenhum braço colapsou

| | base | `magnitude` v1 | `magnitude_v2` | `direcao_v2` |
|---|---|---|---|---|
| cosseno entre manchetes diferentes | 0,2052 | **0,9936** ⚠️ | 0,2709 ✅ | 0,2771 ✅ |
| norma do vetor médio | 0,4536 | 0,9968 ⚠️ | 0,5210 | 0,5269 |
| desvio por dimensão | 0,0451 | 0,0040 ⚠️ | 0,0433 | 0,0431 |
| moveu-se face à base (cosseno) | — | 0,2688 | 0,7820 | 0,7750 |
| preservou a geometria (correlação) | — | 0,2341 | 0,6070 | 0,6301 |

A amostragem estratificada resolveu o colapso **nos dois braços**. Os dois moveram o espaço de
forma substancial (cosseno base↔ajustado ≈ 0,78) preservando a geometria das semelhanças
(correlação ≈ 0,61–0,63). Ou seja: **treinaram mesmo, e treinaram de forma comparável.** O que
vem a seguir não é um artefacto de um modelo degenerado.

## 2. O resultado, e é negativo

Bloco de teste, 32 649 manchetes, 9 empresas, protocolo simétrico, 500 consultas × 5 repetições,
k=5, horizonte +3d. Consultas idênticas para todos os braços, logo as comparações são
emparelhadas.

| Braço | Comparabilidade (pp) ↓ | Precisão@5 ↑ |
|---|---:|---:|
| base (sem ajuste) | **2,168 ± 0,065** | **0,771 ± 0,011** |
| `magnitude_v2` | 2,177 ± 0,069 | 0,746 ± 0,009 |
| `direcao_v2` | 2,146 ± 0,068 | 0,744 ± 0,006 |
| acaso | 2,259 ± 0,107 | 0,629 ± 0,007 |

**Na métrica que o ajuste existe para melhorar, nada acontece.** O braço da grandeza fica
$0{,}009$ pp **acima** da base — pior, portanto — e o da direção $0{,}022$ pp abaixo. As duas
diferenças são cerca de três vezes **menores** do que o desvio entre repetições do próprio
braço ($\pm 0{,}068$). Não são efeitos; são ruído.

**E o ajuste tem um custo que se mede.** A precisão@5 por setor cai de $0{,}771$ para $0{,}746$
e $0{,}744$ — uma descida de $\approx 0{,}026$, que ao contrário das diferenças de
comparabilidade é **duas a quatro vezes maior** do que a dispersão ($\pm 0{,}006$–$0{,}011$) e
tem o mesmo sinal nos dois braços. O ajuste não comprou materialidade e vendeu relevância
temática.

**A margem sobre o acaso já era estreita antes de tudo isto.** A base está a $2{,}168$ contra
$2{,}259$ do acaso: $0{,}09$ pp, com o desvio do acaso a valer $0{,}107$. A comparabilidade de
materialidade a partir do texto é, nesta montagem, uma quantidade que **nenhum dos codificadores
avaliados distingue do acaso** — o que é coerente com a linha de base pré-registada no
`ESTADO_ATUAL.md` ($2{,}173$ contra $2{,}259$) e é precisamente a observação que motivou a QI4.

### A leitura honesta

A QI4 perguntava se a materialidade comparável é aprendível do texto por ajuste contrastivo. A
resposta medida é **não** — e não por o treino ter falhado, que é o que tornaria a resposta
inútil. O treino funcionou: os dois braços moveram o espaço, preservaram a geometria e passaram
a porta de colapso. **É a hipótese que não se confirma.** É o mesmo tipo de resultado que a QI3
já reporta, e defende-se pela mesma razão: está medido, tem controlo, e o mecanismo que o
poderia explicar por avaria foi excluído antes de a tabela ser lida.

## 3. ~~⚠️ Um defeito no `avaliar_qi4.py`~~ **CORRIGIDO a 2026-09-10** — ver a §6

> O diagnóstico abaixo mantém-se como registo. A correção aplicada é a que este texto
> recomendava: excluir as consultas inviáveis e declarar quantas. Detalhe na §6.

**A variante causal nunca tinha corrido, e rebenta.** No protocolo causal exige-se que o
precedente seja *estritamente anterior* à consulta. As consultas do primeiro dia do bloco ficam
sem um único candidato elegível, e `vizinhos_ao_acaso` chama `rng.choice` sobre um conjunto
vazio:

```
ValueError: a cannot be empty unless no samples are taken
```

Extensão medida: **2 consultas em 2500 (0,08%)**, nas repetições 3 e 4. É pouco — mas a forma do
defeito importa mais do que a extensão.

**A linha do acaso rebenta; a linha dos modelos não rebentaria.** O `topo_k` marca os
inelegíveis com `-inf` em vez de os remover, para manter a matriz retangular. Com o conjunto
todo a `-inf`, o `argsort` devolve os primeiros índices por ordem — verificado: uma consulta sem
candidato nenhum recebe `[0 1 2 3 4]` —, e esses cinco falsos vizinhos entram na comparabilidade
e na precisão **sem exceção e sem aviso**. Se o acaso não tivesse rebentado primeiro, a variante
causal teria produzido uma tabela completa com uma fração das consultas a pontuar contra
precedentes que o protocolo proíbe.

É a classe de defeito que este projeto já documenta duas vezes: não encontrar nada e aprovar
tudo têm o mesmo aspeto no ecrã.

**A correção NÃO foi aplicada**, porque muda uma população de medição e isso é decisão do autor.
A forma defensável é excluir essas consultas do lote em vez de as preencher, e **o relatório
declarar quantas foram excluídas** — um denominador que muda em silêncio é o defeito, não a
solução. Alternativa recusada: `replace=True` sobre um conjunto vazio não tem sentido, e sobre um
conjunto pequeno inventaria repetições.

## 4. Proveniência — e o que continua por fazer nesta máquina

Tudo isto correu num contentor Linux (`sentence-transformers` 6.0.1, `torch` 2.14 CPU), não no
ambiente do autor (5.6 / 2.12.1), porque a ponte perdeu a capacidade de executar comandos a meio
da sessão.

**O controlo é forte, e foi corrido antes de qualquer número ser aceite:** o `magnitude_v2`
reproduziu o log original **às seis colunas** (0,2709 · 0,0683 · 0,5210 · 0,0433 · 0,7820 ·
0,6070) e o base reproduziu as quatro (0,2052 · 0,1215 · 0,4536 · 0,0451). A linha do acaso da
avaliação reproduz a linha pré-registada **exactamente** (2,259 ± 0,107 · 0,629 ± 0,007), o que
é esperado por ser aritmética pura sobre `numpy`, sem modelo pelo meio.

⚠️ **Uma divergência, pequena e declarada:** a base dá aqui comparabilidade **2,168** contra os
**2,173** registados no `ESTADO_ATUAL.md`. A diferença é de $0{,}005$ pp, cerca de treze vezes
menor do que o desvio entre repetições, e não altera nenhuma leitura acima — mas é real e vem
provavelmente da versão do `sentence-transformers`. **É por isso que estes números são a
antecipação e não o artefacto final.**

Na máquina do autor, e por esta ordem:

```
.venv\Scripts\python.exe scripts\_colapso_rapido.py ^
  data\qi4_modelos\magnitude_v2 data\qi4_modelos\direcao_v2

.venv\Scripts\python.exe -u -m scripts.avaliar_qi4 ^
  --modelo base=all-MiniLM-L6-v2 ^
  --modelo magnitude=data\qi4_modelos\magnitude_v2 ^
  --modelo direcao=data\qi4_modelos\direcao_v2 ^
  --out data\_arquivo\_qi4_tres_v2.md
```

A variante causal fica bloqueada até o defeito da secção 3 ser decidido.

**Nada disto entra na tese antes de correr no ambiente canónico.** O que este documento
estabelece é que a experiência está concluída, que o resultado é negativo e limpo, e que existe
um defeito de protocolo por resolver antes de a variante causal poder ser lida.

## 5. ✅ CONFIRMADO NO AMBIENTE CANÓNICO — 2026-09-10

As duas corridas pedidas na secção 4 foram feitas na máquina do autor
(`.venv`, Python 3.12.10, `sentence-transformers` 5.6, `torch` 2.12.1 CPU), com
`HF_HUB_OFFLINE=1`. **O resultado negativo mantém-se, e a proveniência deixa de ser uma
ressalva.**

### 5.1 Porta de colapso — reproduz, e fecha as duas colunas que faltavam

| | base | `magnitude_v2` | `direcao_v2` |
|---|---|---|---|
| cosseno entre manchetes diferentes | 0,2052 | 0,2709 ✅ | 0,2771 ✅ |
| norma do vetor médio | 0,4536 | 0,5210 | 0,5269 |
| desvio por dimensão | 0,0451 | 0,0433 | 0,0431 |
| moveu-se face à base (cosseno) | — | 0,7820 | **0,7750** |
| preservou a geometria (correlação) | — | 0,6070 | **0,6301** |

**Reproduz às quatro casas nas seis colunas dos dois braços.** As duas em negrito são as que o
contentor não podia medir, por o Hugging Face estar lá bloqueado e o modelo base não se
descarregar — são precisamente as que dizem se o braço da direção *aprendeu* em vez de apenas
*não ter degenerado*. **Aprendeu:** moveu o espaço tanto como o outro braço (0,775 contra 0,782)
e preservou a geometria um pouco melhor (0,630 contra 0,607). A ressalva de proveniência do
`porta_colapso_direcao_v2_2026-09-09.md` está fechada.

### 5.2 A avaliação — a conclusão não se mexe

| Braço | Comparabilidade (pp) ↓ | contentor | Precisão@5 ↑ | contentor |
|---|---:|---:|---:|---:|
| base (sem ajuste) | **2,173 ± 0,062** | 2,168 | **0,771 ± 0,011** | 0,771 |
| `magnitude_v2` | 2,185 ± 0,065 | 2,177 | 0,746 ± 0,009 | 0,746 |
| `direcao_v2` | 2,157 ± 0,071 | 2,146 | 0,744 ± 0,006 | 0,744 |
| acaso | 2,259 ± 0,107 | 2,259 | 0,629 ± 0,007 | 0,629 |

**A precisão@5 reproduz exactamente em todos os quatro braços** — quatro valores a três casas,
sem uma divergência. A comparabilidade difere entre 0,005 e 0,012 pp, ou seja **entre cinco e
treze vezes menos** do que o desvio entre repetições do próprio braço; a divergência de 0,005 pp
que a secção 4 declarou na base é do mesmo tamanho das outras três e a causa provável continua a
ser a versão do `sentence-transformers`.

⚠️ **E a leitura do negativo fica ligeiramente MAIS forte no ambiente canónico, não mais fraca.**
No contentor o braço da grandeza ficava 0,009 pp acima da base; aqui fica **0,012** pp acima.
O da direção passa de 0,022 para **0,016** pp abaixo. Nos dois casos a diferença continua a ser
uma fracção do desvio entre repetições — não são efeitos, são ruído —, mas convém dizer que a
mudança de ambiente não empurrou nenhum braço para perto de ganhar.

Artefacto desta corrida: `data/_arquivo/_qi4_tres_v2_local.md`. O congelado do contentor
(`_qi4_tres_v2.md`) fica no sítio; **os dois coexistem de propósito**, porque é a comparação
entre eles que sustenta esta secção.

### 5.3 O que continua por fazer

A **variante causal** continua bloqueada pelo defeito da secção 3 — o `topo_k` devolve
`[0 1 2 3 4]` em silêncio quando uma consulta não tem candidato elegível, e corrigi-lo muda a
população de medição. Decisão do autor, não minha. O **braço de controlo C4** (`ProsusAI/finbert`)
também não correu.

## 6. ✅ A VARIANTE CAUSAL, CORRIGIDA E CORRIDA — 2026-09-10

### 6.1 A correção

O `topo_k` **rebenta** em vez de devolver falsos vizinhos, e o filtro passou a ser do chamador
(`consultas_viaveis`), aplicado **uma vez por lote e antes de qualquer modelo ser codificado** —
o filtro só vê tickers e datas, não depende de modelo nenhum, logo os braços continuam
emparelhados. A consola **e** o relatório gerado declaram quantas consultas caíram e porquê: um
denominador que muda em silêncio é o defeito, não a solução.

Extensão real, agora medida em vez de estimada: **2 de 2500 consultas (0,08%)**, exactamente o
que o diagnóstico previa. O braço do acaso deixou de aceitar `replace=True`, que num conjunto
pequeno inventaria repetições.

**A prova de que o defeito era real** (mesmo input, código antigo contra novo):

| Caso | Código antigo devolvia | Código novo |
|---|---|---|
| nenhum candidato elegível, k=5 | `[0 1 2 3 4]` | rebenta |
| causal, consulta mais antiga do bloco, k=3 | `[0 1 2]` — inclui a **própria consulta** e o **futuro** | rebenta |

Seis testes novos, incluindo o controlo no sentido oposto (a porta não pode disparar sobre um
lote legítimo com exactamente `k` elegíveis).

### 6.2 O resultado causal — e o negativo é robusto ao protocolo da produção

Mesmo bloco, mesmo `k`, mesmas repetições; a diferença é que o precedente tem de ser
**estritamente anterior** à consulta, que é o que a produção faz.

| Braço | Comparabilidade (pp) ↓ | Precisão@5 ↑ |
|---|---:|---:|
| base (sem ajuste) | **2,287 ± 0,049** | **0,747 ± 0,011** |
| `magnitude_v2` | 2,309 ± 0,069 | 0,722 ± 0,013 |
| `direcao_v2` | 2,289 ± 0,074 | 0,720 ± 0,012 |
| acaso | 2,336 ± 0,067 | 0,621 ± 0,015 |

**A leitura não muda em nada.** O braço da grandeza fica `0,022` pp **acima** da base — pior — e
o da direção `0,002` pp abaixo, ou seja indistinguível. As duas diferenças continuam a ser uma
fração do desvio entre repetições. E o custo em relevância temática mantém-se e é do mesmo
tamanho: `−0,025` e `−0,027` na precisão@5.

⚠️ **E há aqui uma observação que a variante simétrica não podia dar.** A margem da base sobre o
acaso na comparabilidade **encolhe** com a restrição causal: de `0,086` pp no protocolo simétrico
(2,173 contra 2,259) para `0,049` pp no causal (2,287 contra 2,336). Ou seja, no protocolo que a
produção realmente usa, o codificador sem ajuste está **ainda mais perto do acaso** na
comparabilidade de materialidade do que a §3.2 deste documento sugeria. Isso **reforça** a
motivação da QI4 e ao mesmo tempo torna o negativo mais claro: o espaço para melhorar era maior
do que se pensava, e o ajuste não o ocupou.

Artefacto: `data/_arquivo/_qi4_causal_local.md`.

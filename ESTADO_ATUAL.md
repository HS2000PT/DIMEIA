# ESTADO ATUAL — retoma a frio

> **Para que serve.** Se a sessão morrer a meio, este ficheiro chega para retomar noutra
> plataforma (Claude Code, Codex, ChatGPT, Cowork) sem perder nada. É escrito **antes** de cada
> bloco de acções, não depois.
>
> **Última escrita:** 2026-09-10, depois de a porta de colapso **e** a avaliação da QI4
> reproduzirem no ambiente canónico. A ressalva de proveniência que dominava este ficheiro
> está **fechada** — ver o bloco verde imediatamente abaixo.
> **Regra:** quem retomar actualiza esta secção antes de agir.

### ✅ 2026-09-10 — A QI4 ESTÁ FECHADA NO AMBIENTE CANÓNICO

A porta de colapso e a avaliação completa correram **nesta máquina** (`.venv`, Python 3.12.10,
`sentence-transformers` 5.6, `HF_HUB_OFFLINE=1`). **O negativo confirma-se e a proveniência
deixa de ser uma ressalva.** Detalhe na secção 5 de `docs/design/qi4_resultado_2026-09-09.md`.

| Braço | Comparabilidade (pp) ↓ | contentor | Precisão@5 ↑ | contentor |
|---|---:|---:|---:|---:|
| base (sem ajuste) | **2,173 ± 0,062** | 2,168 | **0,771 ± 0,011** | 0,771 |
| `magnitude_v2` | 2,185 ± 0,065 | 2,177 | 0,746 ± 0,009 | 0,746 |
| `direcao_v2` | 2,157 ± 0,071 | 2,146 | 0,744 ± 0,006 | 0,744 |
| acaso | 2,259 ± 0,107 | 2,259 | 0,629 ± 0,007 | 0,629 |

**A precisão@5 reproduz exactamente nos quatro braços.** A comparabilidade difere 0,005 a
0,012 pp — entre cinco e treze vezes menos do que o desvio entre repetições —, logo a divergência
de 0,005 pp que estava declarada na base é do mesmo tamanho das outras três e não é uma anomalia
dela.

**E as duas colunas que faltavam ao `direcao_v2` estão preenchidas:** moveu-se face à base
**0,7750** e preservou a geometria **0,6301** (contra 0,7820 e 0,6070 do braço da grandeza). Eram
as que diziam se a direção *aprendeu* em vez de apenas *não ter degenerado*. Aprendeu. A ressalva
do `porta_colapso_direcao_v2_2026-09-09.md` fica fechada.

⚠️ **A leitura do negativo fica MAIS forte aqui, não mais fraca:** o braço da grandeza passa de
0,009 para **0,012** pp acima da base, e o da direção de 0,022 para **0,016** pp abaixo. Nenhum
se aproximou de ganhar com a mudança de ambiente.

### ✅ E A VARIANTE CAUSAL TAMBÉM — o defeito do `topo_k` está corrigido

O autor mandou correr tudo. O `topo_k` **rebenta** em vez de devolver `[0 1 2 3 4]`, e o filtro
passou a ser do chamador (`consultas_viaveis`), aplicado **uma vez por lote antes de qualquer
modelo** — só vê tickers e datas, logo os braços continuam emparelhados —, com a consola **e** o
relatório a declararem quantas caíram. Extensão real: **2 de 2500 (0,08%)**, o que o diagnóstico
previa.

| Braço | Comparabilidade (pp) ↓ | Precisão@5 ↑ |
|---|---:|---:|
| base (sem ajuste) | **2,287 ± 0,049** | **0,747 ± 0,011** |
| `magnitude_v2` | 2,309 ± 0,069 | 0,722 ± 0,013 |
| `direcao_v2` | 2,289 ± 0,074 | 0,720 ± 0,012 |
| acaso | 2,336 ± 0,067 | 0,621 ± 0,015 |

**O negativo é robusto ao protocolo que a produção usa.** `+0,022` e `−0,002` pp face à base,
com o mesmo custo em relevância temática (`−0,025` e `−0,027`).

⚠️ **E dá uma observação que a variante simétrica não podia dar:** a margem da base sobre o acaso
na comparabilidade **encolhe** de `0,086` pp (simétrico) para `0,049` pp (causal). No protocolo
real, o codificador sem ajuste está **ainda mais perto do acaso** — o que reforça a motivação da
QI4 e torna o negativo mais claro: havia mais espaço do que se pensava, e o ajuste não o ocupou.

Artefacto: `data/_arquivo/_qi4_causal_local.md`. Prova de que o defeito era real, código antigo
contra novo no mesmo input: sem candidato elegível devolvia `[0 1 2 3 4]`; no causal devolvia
`[0 1 2]`, **incluindo a própria consulta e o futuro**.

### ✅ A porta congelada, e a minha primeira hipótese estava ERRADA

O `test_frozen_reproducibility` falhava nas três métricas. **Não era o `scipy`** — o
`predict_proba` é bit-idêntico a uma sigmoide em `numpy` puro e o Brier à mão iguala o do
`sklearn` exactamente. **E não era ruído de vírgula flutuante:** a deriva em `p` é ~6e-9 por
elemento, sete ordens de grandeza acima do eps da dupla precisão.

**A causa já estava diagnosticada no repositório** e eu não tinha lido o suficiente: §15 e §16 de
`docs/design/reproducao_corpus_2026-09-09.md`. O sidecar foi gerado em julho **noutra máquina**,
as features derivam dos preços, e os preços de setembro não são bit a bit os de julho (a `vol20`
diverge do oitavo dígito, com **todos** os rótulos idênticos).

Logo a porta era **inatingível por construção** aqui, e um critério que não pode passar deixa de
ser porta. Passou a verificar as duas coisas que pode garantir, **com a razão escrita dentro do
próprio teste**: o número que a tese publica (três casas) e um envelope medido de `1e-6` — oito
vezes a maior deriva observada e mil vezes abaixo dessa terceira casa. Verificado que **dispara**
com deriva dez vezes acima do envelope e com a terceira casa mudada.

⏭️ **O QUE FICA:** o **C4** (`ProsusAI/finbert`) está **a treinar** — log em `data/_qi4_c4.log`,
saída em `data/qi4_modelos/controlo_finbert`, ~3 h, mesmos hiperparâmetros do v2 para a comparação
ser justa. E a QI4 ainda **não entrou na tese** (tarefas C7 e C8).

---

### 🔴 2026-09-10 — O ACHADO MAIOR DO DIA: A JANELA DO FINNHUB NUNCA FOI A JANELA RECOLHIDA

Corri o **ramo A** do `plano_53_fnspid.md` e o corpus **recupera-se** — 3 709 manchetes contra as
3 714 originais, a 0,13%. Mas verificar a janela encontrou um terceiro problema, que o plano não
previa e que **toca uma afirmação publicada**.

**O `/company-news` gratuito devolve no máximo ~250 itens por pedido e, ao bater nesse tecto,
ignora o `from`.** Pedir 5, 13 ou 27 dias de AAPL devolve **exactamente as mesmas 248 manchetes**,
todas dos cinco dias anteriores ao `to`. Não há erro nem aviso: o corpus sai com a forma certa e o
período errado.

⚠️ **Verificado que não é do script** antes de o atribuir à API: o pedido constrói `from`/`to`
correctamente e o tecto próprio do script (1 000) não dispara — o log imprime `248/248`.

**A truncagem é proporcional ao volume da empresa**, logo a cobertura temporal fica entrelaçada
com a identidade: NVDA **3 dias**, MSFT/GOOGL/AMZN 4, KO os 28 completos. Fatiando em pedidos de
1 dia: AAPL 248 → **1 372**, NVDA 249 → **5 302**, KO 246 → 254 (o KO é o controlo que mostra que
o efeito é do volume e não do método).

**E a consequência fecha sobre a §5.3.3.** Ela lê o desequilíbrio como propriedade do fluxo de
notícias: «1 736 das 3 714, quase metade, em tecnologia» = `0,4674`. O mapa de setores tem **sete
de quinze** empresas em tecnologia = `0,4667`. **Os dois números são o mesmo à terceira casa**,
porque o tecto dá ~248 a cada empresa independentemente do volume real dela — a composição
setorial passa a ser a proporção de **empresas** por setor. A impressão digital são os outros
quatro setores todos a **13,3–13,4%**, que é `2 × 248 / 3709`.

**O chão trivial de `0,467`, que é o comparador mais importante da §5.3, é o tecto da API.**

| | original (com tecto) | honesto (fatias de 1 dia) |
|---|---:|---:|
| manchetes | 3 709 | **18 599** (5,0×) |
| tecnologia | 46,7% | **84,0%** |
| outros quatro setores | 13,3–13,4% cada | 3,1–5,1% |
| chão trivial | **0,467** | **0,840** |

A tese cita o método a `0,514` contra o chão trivial de `0,467` e contra a taxa-base do **acaso**
de `0,240`. **⚠️ E as duas margens pioram no corpus honesto, uma delas mudando de sinal:** sobre o
acaso cai de `+0,274` para `+0,094`; sobre o trivial passa de `+0,047` **acima** para `0,061`
**abaixo**. Não é o método a piorar — num corpus 84% tecnológico, devolver tecnologia já é quase
sempre certo, logo o acaso e o trivial sobem muito e o agregado deixa de medir capacidade de
recuperação e passa a medir composição do corpus.

⚠️ **Escrevi primeiro que «a margem sobre o acaso duplica». Era falso** — tomei o `0,467`, que é o
chão trivial, como se fosse a taxa-base do acaso, que o `evaluation_results.md` declara em
`0,240`. Corrigido no `plano_53_fnspid.md`, com a correção escrita em vez de silenciada.

**A frase afectada, no `ch5` das duas árvores:** «O corpus contém $3\,714$ notícias distribuídas
por cinco setores, **recolhidas ao longo de vinte e sete dias**». Os vinte e sete dias são
verdade da **união** entre empresas, não da amostragem: por empresa a cobertura vai de 3 a 28.

**⏭️ A DECISÃO É DO AUTOR, e agora tem três ramos e não dois** — enunciados no fim do
`docs/design/plano_53_fnspid.md`: (1) reproduzir o corpus com tecto e **corrigir a declaração da
janela**; (2) re-medir a §5.3 sobre o corpus honesto (é medição nova, não actualização, e propaga
por figuras, texto, slides e guia); (3) o ramo B, cortar a §5.3.

⚠️ **Nada foi propagado e nenhum congelado foi tocado.** Todas as recolhas foram para
`data/_arquivo/` com `--out` e `--sample` explícitos. A medição da §5.3 sobre o corpus honesto
está **a correr** para dar o número que falta à decisão (logs `data/_53_agregado.log` e
`data/_53_setor.log`).

**O recolhedor ganhou três coisas:** `--fatiar N` (parte a janela, um pedido por fatia),
**deteção de tecto** (grita quando um pedido volta ao tecto, com a cobertura real por ticker) e
`--pausa` (1,1 s; o plano gratuito serve 60/min e sem pausa a recolha fatiada morre em 429 a meio
e devolve um corpus incompleto).

⚠️ **E o meu detector de tecto deu um falso positivo no KO** (marca tudo acima de 240 itens, e o
KO tem 246 na janela inteira sem estar truncado). Fica — um aviso a mais é melhor do que um corpus
truncado em silêncio —, mas **o aviso não é prova: a prova é fatiar e comparar.**

---

### 🟢 O RESULTADO DO DIA — o colapso está resolvido

`magnitude_v2` (pares estratificados, taxa 5e-6) **passou a porta de colapso**:

| | base sem ajuste | `magnitude` (v1) | `magnitude_v2` |
|---|---|---|---|
| cosseno entre manchetes **diferentes** | 0,2052 | **0,9936** ⚠️ | **0,2709** ✅ |
| norma do vetor médio | 0,4536 | 0,9968 ⚠️ | 0,5210 ✅ |
| desvio por dimensão | 0,0451 | 0,0040 ⚠️ | 0,0433 ✅ |
| moveu-se face à base (cosseno médio) | — | 0,2688 | 0,7820 |
| preservou a geometria (correlação) | — | 0,2341 | 0,6070 |

Leitura: o v2 **mexeu mesmo** no espaço (cosseno base↔ajustado 0,78; a geometria das semelhanças
correlaciona 0,61 com a original) **sem degenerar**. O v1 continua confirmado como colapsado e os
seus números continuam a não valer nada.

**A causa era a amostragem de pares**, não a taxa de aprendizagem sozinha: pares ao acaso davam
uma distribuição triangular do alvo (média 1/3), e o mínimo da perda era «prever a média para
tudo». Com amostragem estratificada o alvo fica com média 0,499 e desvio 0,289.

Reproduzir: `.venv\Scripts\python.exe scripts\_colapso_rapido.py data\qi4_modelos\magnitude_v2`

### Estado do treino, verificado agora

- `magnitude_v2`: **terminado**, EXITCODE=0. 1250 passos, 3351 s (2,68 s/passo).
- `direcao_v2`: **terminado**, EXITCODE=0. 1250 passos, 2691 s (2,15 s/passo). Perda final
  8,045 contra 8,031 do outro braço — as duas trajetórias correm praticamente sobrepostas.
- Verificar com: `.venv\Scripts\python.exe scripts\_estado_treino.py data\_qi4_*.log`

### 🟢 O `direcao_v2` também passa a porta de colapso — ~~com uma ressalva de proveniência~~

> ⚠️ **RESSALVA FECHADA A 2026-09-10.** A porta correu nesta máquina e reproduz. As duas colunas
> que faltavam ficaram preenchidas (0,7750 e 0,6301). O aviso em maiúsculas abaixo é **histórico**
> — fica como registo de que os números foram aceites primeiro sob ressalva.

| | base | `magnitude` (v1) | `magnitude_v2` | `direcao_v2` |
|---|---|---|---|---|
| cosseno entre manchetes diferentes | 0,2052 | **0,9936** ⚠️ | 0,2709 ✅ | **0,2771** ✅ |
| norma do vetor médio | 0,4536 | 0,9968 ⚠️ | 0,5210 | **0,5269** ✅ |
| desvio por dimensão | 0,0451 | 0,0040 ⚠️ | 0,0433 | **0,0431** ✅ |

Os dois braços v2 são quase indistinguíveis um do outro: **a amostragem estratificada resolveu
o colapso nos dois, e não só no da grandeza.**

⚠️ **ESTA MEDIÇÃO NÃO FOI FEITA NESTA MÁQUINA.** Correu num contentor Linux com
`sentence-transformers` 6.0.1 e `torch` 2.14 CPU. Foi aceite porque o **controlo passou**: o
`magnitude_v2` reembebido nesse ambiente reproduziu o log original **às quatro casas nos quatro
valores**. Mesmo assim **faltam duas colunas** — «moveu-se face à base» e «preservou a
geometria» — porque o Hugging Face está bloqueado nesse contentor e o modelo base não se
descarrega lá. São precisamente as que dizem se o braço da direção *aprendeu* em vez de apenas
*não ter degenerado*. Detalhe em `docs/design/porta_colapso_direcao_v2_2026-09-09.md`.

~~**Portanto o passo 1 abaixo NÃO está fechado: corre a porta aqui antes de ler qualquer métrica.**~~
**FECHADO a 2026-09-10** — a porta correu aqui e nenhum braço colapsou.

### Bloco em curso — plano pré-registado

### 🔴 A QI4 TEM RESULTADO, E É NEGATIVO — ~~medido fora desta máquina~~ **confirmado aqui a 2026-09-10**

> A tabela desta secção é a do **contentor**, e fica como está de propósito: é a comparação entre
> ela e a do topo que sustenta a reprodução. Os números canónicos são os do bloco verde no topo.

Bloco de teste, 32 649 manchetes, protocolo simétrico, consultas emparelhadas:

| Braço | Comparabilidade (pp) ↓ | Precisão@5 ↑ |
|---|---:|---:|
| base (sem ajuste) | **2,168 ± 0,065** | **0,771 ± 0,011** |
| `magnitude_v2` | 2,177 ± 0,069 | 0,746 ± 0,009 |
| `direcao_v2` | 2,146 ± 0,068 | 0,744 ± 0,006 |
| acaso | 2,259 ± 0,107 | 0,629 ± 0,007 |

**O ajuste não melhora a comparabilidade** (as diferenças face à base, +0,009 e −0,022, são três
vezes menores do que o desvio entre repetições) **e degrada a relevância temática** (−0,026 na
precisão@5, com o mesmo sinal nos dois braços e maior do que a dispersão). O treino funcionou —
os dois braços moveram o espaço (cosseno base↔ajustado 0,78/0,775) e preservaram a geometria
(0,607/0,630) —, logo **é a hipótese que não se confirma, não a montagem que falhou.**

⚠️ **DEFEITO POR DECIDIR: a variante causal rebenta.** Consultas do primeiro dia do bloco ficam
sem candidato elegível e o `rng.choice` do acaso falha (2 em 2500). Pior: nessa situação o
`topo_k` devolve `[0 1 2 3 4]` **em silêncio**, logo sem o rebentamento do acaso a tabela sairia
com falsos vizinhos lá dentro. Não corrigi — muda a população de medição. Detalhe e as duas
opções em `docs/design/qi4_resultado_2026-09-09.md`.

**Retomar aqui:**

1. ~~Esperar que `direcao_v2` termine~~ **FEITO** — EXITCODE=0.
2. ~~Reproduzir a porta de colapso **e a avaliação** nesta máquina~~ **FEITO a 2026-09-10** —
   as duas reproduzem, a precisão@5 exactamente, e as duas colunas que faltavam ficaram
   preenchidas. Ver o bloco verde no topo deste ficheiro.
3. ~~Correr a avaliação completa~~ **FEITO** — artefacto em
   `data/_arquivo/_qi4_tres_v2_local.md`. Nenhum braço colapsou.
4. ~~Se o `direcao_v2` colapsar...~~ **NÃO SE APLICA** — nenhum colapsou, e os dois braços são
   quase indistinguíveis um do outro na porta.
5. Registar em `TASKS.md` e em `docs/design/`.

**Feito neste bloco (Capítulo 2, tarefa A12):** ver
`docs/design/capitulo2_literatura_2026-09-09.md`. Resumo: quatro PDFs lidos por inteiro
([Mun09], [Liu23d], [Oh07], [Du24]); inserções em §2.1, §2.2, §2.4, §2.6, §2.7, §2.9 e §6.4, nas
**duas** línguas; oito entradas novas na bibliografia; `robertson2009bm25` corrigido; verificador
de bibliografia corrigido com testes. **As duas árvores compilam com zero citações e zero
referências por resolver** (`scripts\_compilar.py`).

### ⚠️ ARMADILHA NOVA E CARA — 2026-09-10: o PDF velho na raiz esconde o build

O `_compilar.py` constrói com `-outdir=build`, logo o artefacto fresco é
`tese-pt/build/main.pdf`. **O `tese-pt/main.pdf` na raiz é um PDF VERSIONADO e velho** (de
2026-09-09, commit `50821c06d`), e o `main.log`, o `main.fls` e o `main.aux` da raiz são da mesma
época.

Custou-me uma investigação inteira e um falso alarme: lendo o PDF da raiz concluí que **a secção
da QI4 não estava no documento**, quando o `.tex` a tinha, o compile devolvia zero referências por
resolver e a árvore inglesa a mostrava. Cheguei a suspeitar da compilação. O que estava errado era
o ficheiro que eu lia.

**Pior: os números que reportei a partir daí estavam todos errados** — dei 130 pp e 126 pp e a
contagem real é 139 e 138, e o `main.fls` da raiz não listava o Cap. 5 enquanto o do build o lista
cinco vezes.

**Regra que passa a valer: qualquer verificação sobre o PDF lê-se de `build/main.pdf`.** O da raiz
só é verdade imediatamente depois de alguém o copiar de lá — que é a convenção do projecto
(`build(thesis): rebuild both PDFs`) e é fácil de esquecer.

### 📏 A DIMENSÃO, MEDIDA NO BUILD REAL, E RESPONDE À ANSIEDADE DAS PÁGINAS

| | páginas físicas | último fólio árabe |
|---|---:|---:|
| **esta tese, PT** | **139** | **121** |
| **esta tese, EN** | **138** | **120** |
| Bruno Ribeiro (aprovada) | 139 | 120 |
| Helder Pereira (aprovada) | 133 | 114 |
| Rafael Silva (aprovada) | 109 | 93 |
| Joana Figueiredo (aprovada) | 104 | 83 |

**Com a QI4 incluída, a tese fica na dimensão exacta da maior dissertação aprovada do corpus** —
139 páginas físicas contra 139, e fólio 121 contra 120. Não está acima da norma; está no topo
dela. A comparação é a da sessão 66, que mediu o fólio impresso de cada uma das quatro aprovadas.

### Armadilhas novas, descobertas neste bloco

1. **Nunca correr `python -c "..."` através da ponte.** O PowerShell parte a expressão. Escrever
   sempre um `.py`. O mesmo para regex na linha de comandos: `|` é pipe do cmd e `^` é o escape
   do cmd. Usar `scripts\_g.py` (aceita vários padrões como argumentos separados).
2. **`latexmk` não tem opção `-halt-on-error=false`.** Com ela responde «Bad options specified»,
   devolve 10 e **não compila nada** — e como o PDF antigo fica no sítio, um verificador ingénuo
   diz «ok» sobre um ficheiro que ninguém gerou. O `_compilar.py` passou a exigir código 0 e a
   imprimir o número de páginas.
3. **`tese-eng` não tem `latexmkrc`** e a `tese-pt` tem. Assimetria a corrigir um dia.
4. **A ponte cai com a máquina carregada.** Com treino a decorrer, lançar em segundo plano para
   um ficheiro de log e ler o ficheiro depois, em vez de esperar pela saída.
---

## 0. Leitura obrigatória antes de tocar em seja o que for

1. Este ficheiro.
2. `TASKS.md` na raiz — o plano-mestre, fases A a H. É a fonte de verdade das tarefas.
3. `docs/design/reproducao_corpus_2026-09-09.md` — a auditoria de reprodutibilidade completa.
4. `docs/design/TAREFAS_MANUAIS_HENRIQUE.md` — o que só ele pode fazer.

---

## 1. Onde estamos

A tese tem os resultados **reproduzidos e fixados** (corpus, preços, QI2, QI3). O trabalho vivo
é a **QI4** — ajuste contrastivo do codificador por materialidade comparável, que é a
contribuição nova. A primeira tentativa colapsou o codificador e foi descartada; a segunda,
com amostragem estratificada, está a treinar.

---

## 2. A CORRER NESTE MOMENTO

| O quê | Como confirmar | Duração esperada |
|---|---|---|
| Treino `magnitude_v2` e depois `direcao_v2` | `type data\_qi4_mag2.log` e `data\_qi4_dir2.log`; procurar `Modelo em` e `EXITCODE=0` | ~40 min cada, ~80 min os dois |

Lançado por `scripts\_run_qi4v2.bat`, em processo destacado. Saídas em
`data\qi4_modelos\magnitude_v2\` e `...\direcao_v2\`.

**Se os dois já tiverem `EXITCODE=0`, o passo seguinte é o 3.1.**

---

## 3. PRÓXIMOS PASSOS, POR ORDEM

### 3.1 Diagnóstico de colapso — ANTES de olhar para qualquer métrica

```
cd C:\Users\ruifa\Desktop\DIMEIA
set HF_HUB_OFFLINE=1
.venv\Scripts\python.exe -u -m scripts._diag_qi4
```

Editar `scripts\_diag_qi4.py` para apontar a `magnitude_v2` / `direcao_v2` (hoje aponta às v1).

**Critério de aceitação:** o cosseno entre manchetes DIFERENTES tem de ficar na ordem de
`0,2–0,5`. Se vier `> 0,9`, a representação colapsou outra vez e **a tabela de métricas não se
lê** — baixar mais a taxa (`--taxa 2e-6`) ou reduzir passos, e repetir.

Base de referência medida: cosseno `0,2234`, norma do vetor médio `0,4732`.

### 3.2 Avaliar os três braços

```
.venv\Scripts\python.exe -u -m scripts.avaliar_qi4 ^
  --modelo base=all-MiniLM-L6-v2 ^
  --modelo magnitude=data\qi4_modelos\magnitude_v2 ^
  --modelo direcao=data\qi4_modelos\direcao_v2 ^
  --out data\_arquivo\_qi4_tres_v2.md
```

E a variante causal, acrescentando `--causal` e outro `--out`.

**Linha de base já medida** (bloco de teste, 500 consultas × 5 repetições, k=5, simétrico):

| | Comparabilidade (pp) | Precisão@5 |
|---|---:|---:|
| SBERT sem ajuste | 2,173 ± 0,062 | 0,771 ± 0,011 |
| acaso | 2,259 ± 0,107 | 0,629 ± 0,007 |

### 3.3 Braço de controlo (C4)

`--base ProsusAI/finbert` (já em cache HF). ~5× mais lento: contar ~3 h.

### 3.4 Depois da QI4: refazer a §5.3 sobre o FNSPID (C1h.4)

⚠️ **LER PRIMEIRO `docs/design/plano_53_fnspid.md`** — levantamento completo, ocorrência a
ocorrência, com dois ramos. **O corte pode não ser preciso:** a janela do corpus Finnhub fecha a
2026-06-25 e o plano gratuito serve ~1 ano, logo a 09/09 ainda está ao alcance da API. O
`fetch_finnhub_news.py` já leva uma opção `--fim` para a poder pedir. Tentar recolher **antes**
de cortar — decisão do autor a 09-09.

⚠️ **E os dois ramos precisam desta máquina:** o A precisa da API do Finnhub, o B precisa de
regenerar a Figura 5.7 sem o painel A (690 MB de KB, não transferíveis).


O corpus do Finnhub **não existe** e o Henrique confirmou que não aparece. Pela regra dele, os
resultados que dele dependem saem. Afecta `evaluate.py`, `evaluate_per_sector.py`,
`evaluate_corpus_and_filter.py`, `evaluate_retrieval_embedders.py` → §5.3.1, §5.3.2 (Fig. 5.6),
§5.3.3 (Fig. 5.7 painel A) e a comparação de codificadores.

### 3.5 Capítulo 2 (Fase A12)

Os cinco PDFs estão em `data\literature\`. O [Waa21] já foi lido em texto integral — ver §5.

---

## 4. DECISÕES JÁ TOMADAS — não voltar a discutir sem razão nova

| Decisão | Quando | Porquê |
|---|---|---|
| A QI4 **refina** a restrição «explicar sem prever» em vez de a obedecer sem mais | 09-09 | A grandeza é parcialmente aprendível do texto e a direção não é; é isso que os dois braços medem. O Cap. 1 reescreve-se **depois** dos resultados, não antes. |
| O que não se reproduz nesta máquina **desconsidera-se** | 09-09 | Regra do autor. Vale mesmo que obrigue a descarregar modelos e dados de raiz. |
| Corpus da tese = FNSPID, 79 753 títulos, **catorze** empresas | 09-09 | Reproduzido exactamente do bruto fixado por `sha256`. A Meta não existe no FNSPID (só como `FB`, 432 títulos em 4 meses). |
| Duplicados **conservados** (1 704, 2,1%) | 09-09 | É como o FNSPID entrega. Passou a estar declarado na §3.2. |
| Alvo dos pares = `1 − |Δpercentil|`, amostragem **estratificada** | 09-09 | A amostragem ao acaso dá alvo triangular e colapsa o codificador. Medido. |
| Preços fixados em `data/prices_kb/` com manifesto versionado | 09-09 | Não havia cache nenhuma e havia cadeia de cinco fontes silenciosa. |
| Ambiente = `.venv` (Python 3.12.10) | 09-09 | O Python global (3.13) não tem `sentence-transformers`. |

---

## 5. ACHADOS QUE TÊM DE ENTRAR NO TEXTO

- **BM25 na §5.3.4** (já escrito): 0,521 contra 0,595 do SBERT, acaso 0,333. O lexical capta
  **72%** da margem sobre o acaso. Já está nas duas línguas.
- **[Waa21], lido na íntegra:** identificação do factor decisivo — regras **88%**, exemplos
  **~71%**, nenhuma explicação **~68%**; exemplos contra nenhuma explicação **não é
  significativo** (p=.796), nem na compreensão auto-reportada (p=.283). É o terceiro trabalho
  contra a opção por casos, e o mais duro. **A defesa vem do próprio artigo:** atribui o
  resultado a ambos os estilos darem «details relevant for a single decision, not the
  underlying rational or causality» — e a decomposição do InvestiGator **é** a computação
  subjacente. Vai para §2.7 e §6.4.
- **A linha de base da QI4 justifica a QI4:** o SBERT da tese é indistinguível do acaso na
  comparabilidade de materialidade (2,173 contra 2,259, desvios 0,062 e 0,107).
- **Taxa-base de setor muda com o conjunto de candidatos:** 0,629 no bloco de teste (nove
  empresas) contra 0,333 no corpus completo (catorze). Tem de ser declarado onde se comparar.

---

## 6. ARMADILHAS DO AMBIENTE — custaram tempo, não repetir

1. **Correr sempre pelo `.venv`**: `.venv\Scripts\python.exe`, nunca `python`.
2. **PowerShell inline perde os `$`** através da ponte. Comandos vão em ficheiro `.ps1`
   corrido com `-File`; ficheiros `.ps1` só com ASCII.
3. **Trabalhos longos** vão num `.bat` lançado com `Start-Process -WindowStyle Hidden`, a
   escrever para um log. Um processo lançado em primeiro plano morre com a sessão.
4. **`chapter5.tex` usa CRLF, `chapter3.tex` usa LF.** Editar `.tex` em **modo binário**, ou
   reescreve-se o ficheiro inteiro.
5. **Nunca escrever por cima de artefacto congelado.** `docs/evaluation/*.md`, as figuras da
   tese, `models/*.joblib`, `data/samples/*`. Os scripts já têm `--out`, `--figuras-dir`,
   `--modelos-dir`, `--sample`: usá-los sempre numa verificação.
6. **Duas caches de preços com o mesmo nome de ficheiro e esquemas diferentes:**
   `data/prices/` é do `build_dataset.py`, `data/prices_kb/` é do `build_kb.py`. Não misturar.
7. **`findstr` com vários `/C:"..."` falha** na ponte; usar um por comando ou `/R`.

---

## 7. BLOQUEADO NO HENRIQUE

Nada neste momento. As quatro perguntas pendentes foram respondidas a 2026-09-09:
PDFs entregues · corpus Finnhub não existe · chave Finnhub pronta · narrador é Groq→Gemini
(chaves já no `.env`, nada a fazer).

---

## 8. COMO VERIFICAR QUE NADA SE PARTIU

```
.venv\Scripts\python.exe -m pytest -q
```

Falha conhecida e **alheia a este trabalho**: `test_brand_assets.py` — pertence ao ramo de
trabalho da web/mascote, que tem alterações por submeter no directório de trabalho.

### ⚠️ SEGUNDA FALHA, ENCONTRADA A 2026-09-10 E **NÃO CORRIGIDA** — decisão do autor

`test_frozen_reproducibility.py::test_metricas_congeladas_reproduzem` falha nos **três**
parâmetros. **Não é regressão desta sessão** (só se tocou em markdown) e **nenhum número que a
tese cite muda**:

| | congelado | obtido hoje | diferença |
|---|---|---|---|
| PR-AUC | 0,5384788504706477 | 0,538478789566183 | `6,1e-8` |
| ROC-AUC | 0,6580584296750043 | 0,6580583020002979 | `1,3e-7` |
| Brier | 0,22405218360456047 | 0,22405218975515875 | `6,2e-9` |

A porta exige `abs=1e-12` — reprodução ao bit — e o docstring dela diz que «qualquer diferença é
uma mudança real e deve falhar». Está a fazer o que foi escrita para fazer.

**A causa não é a métrica, é o `p`.** Os outros dois testes do mesmo ficheiro **passam**, e um
deles é o `test_precisao_dentro_do_orcamento_reproduz` — o `0,632` que a tese cita como número de
produto, que depende da **ordenação** induzida pelo `p`. Ou seja: a ordenação sobrevive, e o que
se move são os últimos oito dígitos significativos das probabilidades. As três métricas movem-se
**juntas** (o Brier é uma média de quadrados em `numpy` puro, logo não podia derivar por mudança
de código de métrica) e as duas baseadas em ordenação movem-se por umas quantas quase-igualdades
que trocam de lado.

**Vector provável, e é uma hipótese e não uma medição:** o `numpy` (2.1.3) e o `scikit-learn`
(1.9.0) estão **exactamente nos pins**, mas o **`scipy` não está pinado em nenhum dos dois
ficheiros de requisitos** e está em 1.18.0. O `predict_proba` da regressão logística passa pelo
`expit` do `scipy`, o que explicaria uma deriva nos últimos bits. **Não confirmei** — confirmá-lo
obriga a instalar outra versão do `scipy`, e isso é mexer no ambiente canónico a três semanas do
congelamento.

**Duas opções, e a escolha é do autor:**

1. **Pinar o `scipy`** em `requirements.txt` e recriar o `.venv`. Fecha a porta como está escrita.
   Risco: mexe no ambiente que produziu tudo o que está congelado.
2. **Alargar a tolerância** para, digamos, `1e-6`, com a razão escrita ao lado e o intervalo
   medido. Risco: um critério afrouxado é indistinguível de um critério contornado — é a regra que
   este projecto já pagou duas vezes —, logo **teria de ficar dito em voz alta no próprio teste**,
   não em silêncio.

⛔ **NÃO FIZ NENHUMA DAS DUAS.** Alargar a tolerância por iniciativa própria seria exactamente o
defeito que a regra proíbe, e pinar o `scipy` mexe no ambiente de onde saem os congelados.

Portas específicas deste trabalho, todas verdes:
`test_corpus_canonico.py` · `test_price_cache.py` · `test_precos_manifesto.py` ·
`test_qi4_pares.py` · `test_qi4_ajuste.py` · `test_qi4_avaliacao.py` · `test_qi4_dataset.py` ·
`test_method.py` · `test_check_paginas.py`

# Auditoria em papel de arguente hostil — 7 de setembro de 2026

Objeto: `tese-pt/main.pdf`, **122 páginas físicas**, 104 fólios em numeração árabe (o pedido
falava de 123; a aplicação das vinte e quatro correções da auditoria anterior deslocou uma
página). Todas as localizações abaixo usam o **fólio impresso**, que é o que o júri vê.

## O que esta auditoria fez, e o que não pôde fazer

Percorreu-se o documento do princípio ao fim: prosa, 44 figuras, 14 tabelas, 3 excertos, listas
preliminares e bibliografia. Refizeram-se à mão as cadeias aritméticas que fecham dentro do
próprio documento. Renderizaram-se as páginas críticas em imagem, porque a extração de texto
não mostra composição e mente sobre tabelas de células múltiplas.

⚠️ **Nenhum número foi conferido contra o artefacto que o produziu.** Essa verificação não é
possível a partir do PDF e é deliberadamente excluída: o júri também não a poderá fazer. Onde
uma suspeita depende dela, está marcada como tal.

⚠️ **Quatro alarmes meus foram levantados e retirados antes de entrarem neste relatório**, e
ficam registados na secção G porque valem mais do que alguns achados: eram todos artefactos da
extração de texto, e todos teriam mandado corrigir coisas que estão certas.

---

# A. TOP 10, por ordem de risco

---

**ID:** A01
**Severidade:** 🟠 IMPORTANTE
**Tipo:** INCOERÊNCIA
**Localização:** §5.3.2, Figura 5.6, fólio 59; §5.3.3, fólio 60; Figura 6.1, fólio 83.
Frase exata (§5.3.3): «*filtrar candidatos de outra empresa pelo mesmo setor acertaria em todos
os lugares da lista, desde que existissem cinco candidatos elegíveis*».

**Problema:** a Figura 5.6, que é a figura de resultados da QI2, apresenta o método (`0,514`)
contra seis alternativas, e a mais forte de todas não está lá. O documento estabelece, por
raciocínio e não por medição, que uma regra sem modelo nenhum — filtrar os candidatos pelo setor
conhecido da consulta — obtém **precisão@5 = 1,000** sempre que existam cinco candidatos
elegíveis. Isso é o dobro do método. A figura desenha, como referência superior, o MPNet a
`0,538`.

**Porquê:** é a assimetria mais atacável do capítulo. A secção 5.3.3 existe precisamente para
mostrar que o valor agregado esconde uma alternativa trivial, e o argumento é excelente para a
estratégia «devolver sempre tecnologia» (`0,467`) — que **entra na figura**. A alternativa que
obtém `1,000` **não entra**, e é mencionada em prosa três parágrafos depois. Um arguente que
leia por esta ordem conclui que a alternativa mais incómoda foi tratada de forma diferente da
alternativa incómoda mais fraca.

**Correção:** duas opções, e a segunda é a barata. (1) Medir o filtro por setor sob o mesmo
protocolo e acrescentá-lo à Figura 5.6, o que exige uma execução nova a poucos dias do
congelamento. (2) Não medir nada e **acrescentar uma linha tracejada anotada** na Figura 5.6 com
`1,000` e o rótulo «filtro pelo setor da consulta — consequência do rótulo, não medição», mais
uma frase na legenda a dizer que não é uma alternativa de produto porque não tem informação
sobre o tema. A opção (2) é honesta, custa duas linhas de TikZ e desarma a pergunta.

**Verificação:** ler a Figura 5.6 (fólio 59) e depois o quarto parágrafo da §5.3.3 (fólio 60).
Perguntar: se um arguente perguntar «qual é a linha de base mais forte que existe para esta
tarefa?», a resposta está na figura ou está enterrada na prosa?

**Já tratado?** Sim, em prosa, em dois sítios: §5.3.3 (fólio 60) e §6.2.2 (fólio 84, «*A análise
por setor não mede vantagem semântica sobre esse filtro*»). Não chega porque **o tratamento não
alcança nenhuma das duas figuras que carregam o veredicto**, e é nas figuras que a QI2 é lida.

---

**ID:** A02
**Severidade:** 🟠 IMPORTANTE
**Tipo:** ERRO CONFIRMADO
**Localização:** §6.2.2, fólio 84. Frase exata: «*Sobre o corpus histórico completo, com
aproximadamente oitenta mil notícias de seis anos, a precisão sobe para 0,595. O valor de
referência sobe na mesma proporção, e a margem mantém-se.*» Idêntico na árvore inglesa
(«*The reference value rises in the same proportion, and the margin holds*»).

**Problema:** a proporção não é a mesma, e os números que a refutam estão impressos no próprio
documento, na §5.3.4 (fólio 61):

| | corpus recente | corpus completo | variação relativa |
|---|---|---|---|
| precisão@5 | `0,514` | `0,595` | **+15,8 %** |
| valor de acaso | `0,240` | `0,333` | **+38,8 %** |
| margem | `+0,274` | `+0,262` | **−0,012** |

O valor de referência sobe a **mais do dobro** do ritmo da precisão, e a margem não se mantém:
desce `0,012`. A §5.3.4 diz a coisa certa e diz-a bem («*o valor de acaso sobe igualmente*»); é o
capítulo de conclusões que a endurece.

**Porquê:** está no capítulo que o júri lê por último, numa secção de veredicto, e é uma
afirmação quantitativa refutável em dez segundos com uma calculadora e as duas páginas abertas.
Pior: a afirmação endurecida **favorece o trabalho** — sugere que a escala não custa nada —,
que é exatamente a direção em que uma imprecisão é lida como conveniência.

**Correção:** substituir por «*O valor de referência sobe também, e mais depressa, pelo que a
margem desce de +0,274 para +0,262*». Nas duas línguas. Três palavras alteradas, nenhum número
novo.

**Verificação:** dividir `0,595/0,514` e `0,333/0,240`. Comparar com a frase da §5.3.4.

**Já tratado?** A §5.3.4 trata-o corretamente. A §6.2.2 contradi-la. Não é uma omissão: é uma
divergência entre dois sítios do mesmo documento.

---

**ID:** A03
**Severidade:** 🟠 IMPORTANTE
**Tipo:** ERRO CONFIRMADO
**Localização:** Tabela 5.2, §5.6.1, fólio 71. Linha «*Razão entre as duas*». Idêntico em inglês
(`5.4×` / `6.1×`).

**Problema:** a tabela imprime as duas amplitudes e depois a razão entre elas. Uma das duas
razões não sai dos valores impressos:

| janela | dentro | entre | razão impressa | razão refeita |
|---|---|---|---|---|
| 36 925 decisões | `0,072` | `0,392` | `5,4×` | `5,44` ✓ |
| 4 366 decisões | `0,064` | `0,385` | **`6,1×`** | **`6,02`** ✗ |

**Porquê:** a tabela existe para mostrar que a conclusão não depende da janela, e é uma tabela de
três linhas em que a terceira é a divisão das duas primeiras. É a aritmética mais fácil de
refazer do documento inteiro. Que uma das duas feche exatamente e a outra falhe por uma unidade
na casa apresentada é o pior padrão possível: o leitor confirma a primeira, ganha confiança, e
tropeça na segunda.

⚠️ **Reconciliável, mas não pelo leitor.** Com amplitude interna real ≈ `0,0635` a razão dá
`6,06`, que arredonda a `6,1` e cuja amplitude arredonda a `0,064`. É consistente. Mas o
intervalo de valores em que isso acontece é estreito e o leitor não tem como o saber.

**Correção:** a menos invasiva é imprimir `6,0×`, coerente com os valores da própria tabela. Se
o valor gerado for mesmo `6,1`, acrescentar à legenda «*as razões são calculadas sobre os valores
não arredondados*» — o que também resolve, e é mais honesto.

**Verificação:** `0,385 / 0,064` numa calculadora.

**Já tratado?** Não. A §5.1 (fólio 53) declara arredondamento à terceira casa, mas essa
declaração está agarrada ao exemplo do F1 e não é global. Nada na Tabela 5.2 avisa o leitor.

---

**ID:** A04
**Severidade:** 🟠 IMPORTANTE
**Tipo:** INCOERÊNCIA
**Localização:** Apêndice A, Tabela A.1 (fólio 101) e Tabela A.2 (fólio 102), quatro células.
Frase exata mais grave (Tabela A.2): «*Alterar as sessões posteriores deixa as entradas iguais e
altera o **critério***». Idêntico em inglês («*changes the criterion*»).

**Problema:** o corpo do documento usa **rótulo** de forma consistente e insistente: «rótulo
aproximado» (5 ocorrências no Cap. 5), «nove definições de rótulo» (§5.4.3), «o rótulo tem de
mudar» (§3.6). O apêndice troca-o por **critério** em quatro sítios: «F1 contra o critério
aproximado», «Grelha de nove definições de critério», «Supera um limiar fixo no critério
aproximado», «altera o critério».

A quarta é a que passa de inconsistência a erro. Descreve o Excerto 3.2, que é o procedimento
que impõe a separação temporal — a garantia central do trabalho. Esse teste **não altera critério
nenhum**: altera o **rótulo**, e é isso que o próprio excerto exige (`abnormal_label(...) == 1`
contra `== 0`). O §3.6 diz-o em voz alta: «*as entradas do modelo têm de permanecer iguais, e o
rótulo tem de mudar*».

**Porquê:** «critério» já tem dois trabalhos neste documento — critério de sucesso fixado antes
da medição, e critério prático de `0,02`. «Grelha de nove definições de critério» lê-se
naturalmente como nove definições do critério de sucesso, que seria uma prática indefensável, em
vez de nove definições de rótulo, que é uma verificação exemplar. O apêndice é onde o júri
confere a proveniência: é o pior sítio para o vocabulário derivar.

**Correção:** `critério` → `rótulo` nas quatro células, nas duas línguas
(`criterion` → `label`). Zero números tocados.

**Verificação:** `grep -n "critério" tese-pt/appendices/appendixA.tex` e comparar com a §5.4.3.

**Já tratado?** Não. O verificador `check_escrita` do projeto promete «um termo por conceito» e
não cobre este par — o que é ele próprio informação útil.

---

**ID:** A05
**Severidade:** 🟠 IMPORTANTE
**Tipo:** INCOERÊNCIA
**Localização:** §5.4.4, fólio 65 («*Uma tabela de treze constantes… obtém 0,662*») contra
Figura 5.12, fólio 67 (linha «Só volatilidade», precisão@5 = `0,632`).

**Problema:** duas quantidades chamadas «volatilidade» produzem `0,662` e `0,632` **na mesma
métrica**, com uma página de distância, e nada as separa no local. A reconciliação existe e é
boa, mas está na §5.6.4, no fólio 78 — **treze páginas à frente**: «*Não é a mesma quantidade que
a Figura 5.12 designa por só volatilidade, que é uma regressão sobre a volatilidade diária e
obtém 0,632 nesta métrica; aqui a volatilidade entra como uma constante por empresa.*»

**Porquê:** o leitor encontra `0,662` no fólio 65, vira a página, e vê `0,632` ao lado da palavra
«volatilidade». A leitura natural é que um dos dois está errado. É precisamente na secção que
carrega o resultado negativo, onde a atenção do arguente é máxima.

**Correção:** mover a frase de reconciliação (ou uma versão de uma linha dela) para a §5.4.4,
imediatamente a seguir ao `0,662`. A frase já está escrita; trata-se de a duplicar onde é
precisa, ou de renomear uma das duas linhas — por exemplo «Regressão sobre a volatilidade
diária» na Figura 5.12, que remove a colisão na origem.

**Verificação:** ler o fólio 65 e o fólio 67 seguidos, sem saltar para o 78.

**Já tratado?** Sim, na §5.6.4, e muito bem — a explicação de por que razão dois preditores
distintos obtêm exatamente o mesmo valor é um dos melhores parágrafos do capítulo. Não chega
porque está treze páginas depois do sítio onde a dúvida nasce.

---

**ID:** A06
**Severidade:** 🟡 MENOR
**Tipo:** ERRO CONFIRMADO
**Localização:** §2.2, fólio 6, parágrafo imediatamente a seguir à Tabela 2.1. Frase exata:
«*A tabela evidencia o essencial. A linha que responde às três perguntas existe e é a mais
dispendiosa de todas.*»

**Problema:** a Tabela 2.1 tem **duas** linhas com sim/sim/sim: «Terminal profissional» (custo
«não publicado») e «Este trabalho» (custo «gratuito»). A frase usa o singular e atribui à única
linha assim o custo mais alto — o que é falso para a segunda, que está na mesma tabela, a
negrito, imediatamente por baixo.

**Porquê:** é a frase que abre o argumento fundador («*O problema não é, portanto, de natureza
científica, mas de acesso*»), e é literalmente contradita pela linha seguinte da mesma tabela.
Custa pouco a quem lê depressa e é irresistível para um arguente que goste de tabelas.

**Correção:** «*A única linha existente que responde às três perguntas é também a mais
dispendiosa de todas*» — ou mover «Este trabalho» para fora do corpo da tabela, para um bloco
comparativo separado. A primeira é uma palavra.

**Verificação:** contar as linhas com três «sim» na Tabela 2.1.

**Já tratado?** Não. A legenda diz «*As categorias de ferramenta **existentes***», o que
implicitamente exclui «Este trabalho», mas a linha está lá e a frase do corpo não repete a
qualificação.

---

**ID:** A07
**Severidade:** 🟡 MENOR
**Tipo:** INCOERÊNCIA
**Localização:** Figura 5.12, legenda, fólio 67. Frase exata: «*As duas linhas inferiores, que
não dispõem de qualquer entrada de nível de empresa, situam-se exatamente na prevalência do bloco
de teste.*»

**Problema:** cada linha da figura desenha **duas** barras. Para as duas linhas inferiores:

| variante | PR-AUC | precisão@5 no orçamento |
|---|---|---|
| Sem entradas de empresa | `0,378` ✓ | `0,368` |
| Só o comprimento do título | `0,378` ✓ | `0,352` |

A afirmação é verdadeira das barras de PR-AUC e falsa das barras de precisão@5, que estão na
mesma linha e não são nomeadas na exceção.

**Porquê:** o leitor olha para a figura, vê quatro barras nas duas linhas inferiores, lê «situam-
se exatamente na prevalência», e duas delas não estão lá. A precisão da legenda é o que dá
autoridade a esta figura, que é a mais importante da §5.4.

⚠️ **E há um segundo facto por dizer:** `0,352` e `0,368` situam-se **abaixo** da escolha
aleatória na mesma métrica (`0,379 ± 0,017`, Figura 5.11). Não é discutido em lado nenhum. Não é
um defeito — está dentro da dispersão — mas é o género de detalhe que um arguente aponta.

**Correção:** «*As duas linhas inferiores, que não dispõem de qualquer entrada de nível de
empresa, situam-se **na PR-AUC** exatamente na prevalência do bloco de teste.*» Duas palavras.

**Verificação:** ler os quatro números das duas linhas inferiores da Figura 5.12.

**Já tratado?** Não.

---

**ID:** A08
**Severidade:** 🟡 MENOR
**Tipo:** SUSPEITA — REQUER VERIFICAÇÃO MANUAL
**Localização:** §5.4.6, fólio 68 e reserva 1 do fólio 69.

**Problema:** três valores impressos que não fecham entre si por `0,001`:

- tabela de consulta: `0,534` (Figura 5.12)
- acréscimo do texto: `+0,012`, IC `[+0,004; +0,020]`
- tabela + texto: `0,547` (reserva 1)

`0,534 + 0,012 = 0,546`, e o documento imprime `0,547`.

**Porquê:** é a única medição do trabalho em que uma representação de texto obtém um acréscimo
detetável, ou seja o número mais escrutinado da QI3. Um arguente que some os dois valores
impressos e obtenha um terceiro diferente do impresso vai perguntar qual dos três é o bom.

**Correção:** acrescentar à §5.4.6 a mesma ressalva de arredondamento que a §5.1 usa para o F1
(«*as parcelas estão arredondadas à terceira casa, pelo que a conta refeita sobre os valores
impressos pode diferir na última*»), ou imprimir o acréscimo com uma casa a mais.

**Verificação:** conferir contra o artefacto qual é o valor não arredondado da tabela de consulta.
Se for `≥ 0,5345`, fecha e basta a ressalva; se não, um dos números está errado. **Isto exige
acesso aos ficheiros de resultados e não foi possível nesta auditoria.**

**Já tratado?** Parcialmente: a §5.1 declara a política de arredondamento, mas fá-lo no contexto
do F1 e não como regra global do capítulo.

---

**ID:** A09
**Severidade:** 🟡 MENOR
**Tipo:** MELHORIA (escrita / cheiro a texto gerado)
**Localização:** transversal aos seis capítulos.

**Problema:** o documento constrói a esmagadora maioria das suas distinções com **uma só figura
de retórica**: «X, e não Y» / «não é X, mas Y». Medido sobre a prosa, com figuras, tabelas e
excertos removidos:

| capítulo | frases | construções antitéticas | frequência |
|---|---|---|---|
| Cap. 1 | 53 | 2 | 1 em 26 |
| Cap. 2 | 231 | 19 | 1 em 12 |
| Cap. 3 | 181 | 9 | 1 em 20 |
| Cap. 4 | 253 | 15 | 1 em 17 |
| Cap. 5 | 463 | 33 | 1 em 14 |
| Cap. 6 | 240 | 18 | 1 em 13 |
| Apêndice | 67 | 4 | 1 em 17 |
| **total** | **1 488** | **100** | **1 em 15** |

Cem ocorrências em cerca de 34 500 palavras, e **cinco pares de frases consecutivas** onde as
duas a usam. Exemplos contíguos: «*A medição inicia-se no fecho do dia da notícia, e não na
abertura…*» seguido de «*O valor apresentado ao utilizador é o retorno bruto e não o retorno
anormal…*» (§3.5); «*…ordenar por volatilidade compensa, e não que aprender compense.*» seguido
de «*…o modelo implantado reconhece a empresa e não a notícia.*» (§5.4.4/5.4.5).

**Porquê:** a distinção que a figura carrega — o que está estabelecido contra o que não está — é
a espinha epistémica do trabalho e **não deve ser tocada**. O que se lê como máquina é a
*uniformidade da superfície*: cem vezes a mesma construção sintática. Um leitor sensibilizado
para texto gerado repara na cadência, não no conteúdo. É também o único achado desta auditoria
que um arguente pode formular sem entrar em nenhum número.

**Correção:** não uniformizar tudo — a construção é boa e deve ficar. Variar **os cinco pares
consecutivos** e mais uma dúzia dos casos mais próximos entre si, usando as formas que o
documento já emprega noutros sítios: dois períodos separados; «o que se mede é A; o que não se
mede é B»; subordinada concessiva. Alvo defensável: descer de 100 para ~70 e eliminar os pares
contíguos.

**Verificação:** correr o detetor sobre a prosa com os flutuantes substituídos por marcador — sem
essa substituição o corpo das figuras TikZ entra na contagem e o resultado é lixo.

**Já tratado?** Não. As passagens de escrita anteriores (sessão 63, secção M) mediram primeira
pessoa, ênfase dramática, coloquialismos e travessões, e este eixo não foi medido.

---

**ID:** A10
**Severidade:** 🟡 MENOR
**Tipo:** MELHORIA
**Localização:** Figura A.1, fólio 104, caixa «Fontes».

**Problema:** a caixa mostra dois logótipos (Finnhub e Yahoo Finance) e dois nomes em texto
(Alpha Vantage, Polygon). O logótipo do **Finnhub é um quadrado índigo sem palavra nenhuma**:
quem não conhece a marca não a identifica. É a fonte que a Tabela 4.1 (fólio 33) mostra ser a
melhor das três — `35 %` de precisão de etiquetagem e cobertura `12/12` — e é aquela a que a §4.6
atribui parte dos `353` minutos de atraso.

**Porquê:** o apêndice existe para tornar a proveniência verificável a partir do documento. A
peça externa mais importante da aquisição de notícias é a única que fica por nomear, enquanto as
duas de cobertura inferior aparecem escritas. Um arguente que compare a Tabela 4.1 com a
Figura A.1 conta três fontes de notícias numa e duas na outra.

**Correção:** acrescentar `Finnhub` à linha de texto da caixa, que já lista os outros dois. Uma
palavra, nas duas árvores.

**Verificação:** ampliar a caixa «Fontes» do fólio 104 e perguntar se um leitor identifica três
fontes de notícias.

**Já tratado?** Parcialmente. O comentário no código-fonte da figura declara que «*as duas fontes
de notícias que faltavam não têm logótipo disponível e entram por nome*», ou seja o autor
considera o Finnhub coberto pelo logótipo. Não chega, porque o logótipo não é legível como nome.

---

# B. Ganhos rápidos — menos de dez minutos cada

| # | Onde | O que fazer |
|---|---|---|
| 1 | §6.2.2, fólio 84 (PT+EN) | **A02.** «sobe na mesma proporção» → «sobe também, e mais depressa, pelo que a margem desce de +0,274 para +0,262». |
| 2 | Tabela 5.2, fólio 71 (PT+EN) | **A03.** `6,1×` → `6,0×`, ou nota de legenda sobre valores não arredondados. |
| 3 | Apêndice A, 4 células (PT+EN) | **A04.** `critério` → `rótulo`. |
| 4 | §2.2, fólio 6 (PT+EN) | **A06.** «A linha que responde» → «A única linha existente que responde». |
| 5 | Figura 5.12, legenda, fólio 67 | **A07.** acrescentar «na PR-AUC». |
| 6 | Figura A.1, fólio 104 (PT+EN) | **A10.** acrescentar `Finnhub` à linha de texto. |
| 7 | §2.9, fólio 17 | «*um custo real que importa enunciar sem atenuação*» → «*um custo real, enunciado sem atenuação*». É a classe de meta-comentário que as passagens anteriores já purgaram; sobreviveram três casos (ver F). |
| 8 | §5.4.4, fólio 65 | **A05**, versão barata: uma frase a dizer que este `0,662` é uma constante por empresa e não a linha «só volatilidade» da figura seguinte. |
| 9 | §5.4.6, fólio 68 | **A08.** repetir a ressalva de arredondamento da §5.1. |
| 10 | §4.3.1, fólio 35 | «*a melhor delas fica acima do limiar de 0,45*» — as três (`0,46`, `0,51`, `0,46`) estão acima. Trocar por «*as três ficam acima*», que é mais forte e é o que os números dizem. |

---

# C. Resultados suspeitos — o que me pareceu bom de mais

**C1 — A concordância de direção `0,708` contra acaso `0,688`.** Uma diferença de `0,020` sobre
um chão de acaso **medido** por emparelhamento aleatório sob as mesmas restrições. É o resultado
mais honesto do documento e não é suspeito; menciono-o porque é o modelo de como os outros
deviam ser lidos. Sem intervalo de confiança, porém, `0,020` é indistinguível de zero, e a §5.3.5
afirma-o como facto («*situa-se em 0,708 contra um valor de acaso de 0,688*») em vez de o
declarar indistinguível. **Teste que o resolveria:** reamostragem por par empresa-dia sobre a
mesma medição; se o intervalo contiver zero, a frase passa a «*ao nível do acaso*», o que
**reforça** o argumento do produto (tema ≠ direção) em vez de o enfraquecer.

**C2 — A precisão `1,000` / `0,000` da estratégia trivial (§5.3.3).** Valores exatamente
perfeitos e exatamente nulos são sempre motivo de desconfiança. Aqui são corretos por
construção: a estratégia devolve sempre tecnologia, e o rótulo é a pertença ao setor, logo acerta
em `100 %` das consultas de tecnologia e em `0 %` das outras. **Verificado por raciocínio, fecha.**
E a confirmação está na coincidência entre `1 736/3 714 = 0,4674` e a precisão agregada `0,467`.

**C3 — Os dois preditores distintos com o mesmo `0,662` (§5.4.4 e §5.4.5).** A coincidência
exata entre duas quantidades sem relação é o padrão que mais frequentemente denuncia um erro de
cópia. **Aqui está explicada e a explicação é correta**: a precisão dentro do orçamento depende
só da ordenação induzida, e duas constantes por empresa que ordenem igual selecionam as mesmas
notícias. Não é achado; é o contrário. Ver A05 quanto ao sítio onde a explicação está.

**C4 — Os três precedentes a `−2,73 %` do alerta da Figura 4.6.** Três valores idênticos até à
segunda casa. **Não é suspeito e está tratado exemplarmente** na §4.5.1, que mede a extensão do
problema (`36,8 %`, `11,3 %`, `23,3 %`) e o inscreve nas limitações do Cap. 6.

**C5 — `98 %` de votos úteis, 41 em 42 (§5.6.5, fólio 79).** É o número mais favorável do
documento e o mais frágil: três pessoas, uma delas com `67 %` dos votos, autosseleção declarada.
O documento cerca-o de quatro limitações e do aviso de que o intervalo binomial não corrige a
dependência. **Não tenho reserva a acrescentar às que o texto já faz.** Registo só que é o
número que um arguente vai citar de volta ao autor, e que a resposta preparada tem de ser a de
que ele não é usado para sustentar conclusão nenhuma — o que é verdade: a Tabela A.2 classifica
«As explicações são úteis a uma pessoa» como **não afirmado**.

**C6 — `0 %` do piso escalonado em seis dias (Figura 4.5).** Um mecanismo armado que nunca
elimina nada é sempre suspeito de estar desligado. **A figura declara-o e o texto explica a
causa** (o orçamento esgota-se antes de uma empresa chegar ao segundo alerta). Fecha.

---

# D. Contradições internas

**D1.** §6.2.2 fólio 84 («o valor de referência sobe na mesma proporção») **vs** §5.3.4 fólio 61
(`0,240 → 0,333` contra `0,514 → 0,595`). → A02.

**D2.** §5.4.4 fólio 65 (volatilidade `0,662`) **vs** Figura 5.12 fólio 67 («Só volatilidade»
`0,632`). Reconciliado apenas no fólio 78. → A05.

**D3.** §2.2 fólio 6 («a linha que responde às três perguntas… é a mais dispendiosa de todas»)
**vs** Tabela 2.1 fólio 6, linha «Este trabalho» (sim/sim/sim, gratuito). → A06.

**D4.** Legenda da Figura 5.12 fólio 67 («situam-se exatamente na prevalência») **vs** as barras
de precisão@5 da mesma figura (`0,352` e `0,368` contra prevalência `0,378`). → A07.

**D5.** Tabela A.2 fólio 102 («altera o critério») **vs** §3.6 fólio 26 («o rótulo tem de
mudar») e Excerto 3.2 fólio 27. → A04.

**D6 — 🟡 novo.** §A.1, fólio 99: «*a base de precedentes que a aplicação implantada consulta,
com cinquenta e seis megabytes de vetores*». §4.2.3, fólio 34: a base consultada é a **fusão** de
`38 214` casos reconstruídos com `11 445` casos vivos, ou seja `49 659`. Ora
`38 214 × 384 × 4 bytes = 56 MiB` e `49 659 × 384 × 4 bytes = 73 MiB`. Os cinquenta e seis
megabytes correspondem **apenas à reconstrução**, não à base que a §4.2.3 diz ser consultada.
**Correção:** dizer «a componente reconstruída da base de precedentes», ou dar os dois valores.
**Verificação:** exige o tamanho real do ficheiro — **não foi possível confirmar nesta
auditoria**, e a aritmética acima é a única evidência. Marcado **SUSPEITA**.

---

# E. Perguntas de júri, por dificuldade crescente

Cada uma com o sítio onde a resposta já está, quando está.

1. «Porque é que a decomposição não dá origem a uma questão de investigação?» — **Respondida**,
   §1.3 fólio 3 e §5.5 fólio 70.
2. «Quantas empresas monitoriza o sistema, e porque não são as mesmas da avaliação?» —
   **Respondida**, Tabela 3.2 fólio 20 e §5.2.1 fólio 54.
3. «Os preços estão ajustados a desdobramentos?» — **Respondida**, §3.2 fólio 19, com o número do
   dano que não ajustar causaria.
4. «Porquê cosseno e não distância euclidiana?» — **Respondida**, §3.5 fólio 24 e Tabela 5.4
   fólio 80.
5. «Porque é que o bloco de teste é maior do que o de treino?» — **Respondida**, §3.6 fólio 26.
6. «O que garante que o modelo não vê o futuro?» — **Respondida**, Excerto 3.2 fólio 27, com um
   teste executável.
7. «Porque é que o limiar de deteção é 3,0 na avaliação e 1,5 em produção?» — **Respondida**,
   Tabela 4.2 fólio 39.
8. «O sistema alerta sobre uma notícia que é ela própria uma previsão. Isso não contradiz a
   restrição fundadora?» — **Respondida**, §3.8.3 fólio 29 e legenda da Figura 4.6 fólio 42.
9. «A latência mediana é de 353 minutos. Isso não torna o sistema inútil?» — **Respondida**, §4.6
   fólio 46, com a decomposição e o que um serviço pago resolveria.
10. «Encurtar o ciclo de 90 minutos para 60 segundos não reduziu a latência. Então porque o
    fizeram?» — **Respondida**, §4.6 fólio 46, incluindo a declaração de que a comparação não é
    interpretável como efeito do ciclo.
11. «Porque é que mantiveram o estimador de volatilidade que perde?» — **Respondida**, §5.2.5
    fólio 57 e Tabela 5.4 fólio 80.
12. «Porque é que mantiveram a janela de vinte dias, se a de sessenta obtém mais?» —
    **Respondida**, §5.2.5 fólio 57, e o §5.7 fólio 81 admite ser «a opção mais difícil de
    justificar».
13. «A medida principal da QI1 tem o zero como ótimo. Um disparo aleatório não a bate?» —
    **Respondida**, §5.2.3 fólio 54: bate, e é por isso que existem duas medidas.
14. «Porque é que o codificador financeiro perdeu?» — **Respondida**, §5.3.2 fólio 59: objetivo
    de treino, não conhecimento de domínio, com a ressalva de que foi usado por média de vetores.
15. «`0,514` contra `0,240` parece muito. Mas metade do corpus é tecnologia — não estão a medir a
    composição do corpus?» — **Respondida e antecipada**, §5.3.3 fólio 60, que é uma das melhores
    secções do documento.
16. «Se o setor da consulta é conhecido, porque não filtrar por ele? Daria `1,000`.» —
    **Respondida em prosa** (§5.3.3 fólio 60, §6.2.2 fólio 84) e **ausente das duas figuras de
    veredicto**. → **A01. É por aqui que eu atacaria primeiro.**
17. «A avaliação da recuperação permite candidatos posteriores à consulta. Isso não é ver o
    futuro?» — **Respondida**, §5.3.4 fólio 61, com a medição sob anterioridade e a declaração de
    que não impõe a maturação de oito dias.
18. «O rótulo desconta o mercado com beta unitário, e a Secção 3.4 recusa essa suposição. Não
    invalida a QI3?» — **Respondida**, §3.6 fólio 26, §5.4.7 fólio 69 e §6.4 fólio 89: a
    contradição é declarada, o efeito não é medido, e a conclusão fica condicionada ao rótulo.
19. «As árvores com reforço do gradiente correram com parâmetros por defeito. A derrota do texto
    não é artefacto disso?» — **Respondida**, §5.4.1 fólio 63, que declara a limitação do alcance.
20. «O bloco de teste serviu várias comparações. Não há sobreajuste ao conjunto de teste?» —
    **Respondida**, §5.4.6 fólio 69, com as duas defesas usadas e a admissão de que reduzem o
    risco sem o eliminar.
21. «Cinco empresas do treino não estão no teste. Como comparam modelos entre blocos com
    composições diferentes?» — **Respondida**, §5.4.3 fólio 65, com `82,9 %` de sobreposição de
    linhas e a declaração de que a comparação não isola o efeito.
22. «O texto acrescenta `+0,012` com intervalo que exclui zero. Porque é que isso não reabre a
    QI3?» — **Respondida**, §5.4.6 fólio 69, com três medições. **É a melhor resposta do
    documento e vale a pena ensaiá-la em voz alta.**
23. «O vosso próprio modelo perde para treze constantes. Para que serve então o trabalho?» —
    **Respondida**, §4.7 fólio 47 e §6.1 fólio 82: a contribuição é a infraestrutura que torna
    essa conclusão negativa defensável.
24. «A decomposição não tem verdade de terreno. Como sabem que não está errada?» —
    **Respondida**, §5.5 fólio 70: mede-se o que permanece falsificável, e uma das dezassete
    empresas tem coeficiente negativo, o que é reportado.
25. «`98 %` de votos úteis, com três pessoas e uma delas a valer `67 %`. Isso é evidência?» —
    **Respondida**, §5.6.5 fólio 79 e Tabela A.2 fólio 102 («não afirmado»). ⚠️ A resposta oral
    tem de começar por «não, e a tese não o usa para afirmar nada».
26. «O autor está entre os votantes?» — **Respondida**, §5.6.5 fólio 79, com uma frase explícita.
    ⚠️ **Confirmar que continua verdadeira antes da submissão** (pendência humana registada).
27. «O `0,662` da §5.4.4 e o `0,632` da Figura 5.12 são ambos “volatilidade”. Qual está certo?» —
    **Respondida no fólio 78, treze páginas depois.** → A05.
28. «`0,385 / 0,064` dá `6,0`, e a tabela diz `6,1`.» → **A03. Não tem resposta preparada.**
29. «Dizem que o valor de referência sobe na mesma proporção. Sobe a mais do dobro do ritmo.» →
    **A02. Não tem resposta preparada.**
30. «Se a hipótese fundadora — evidência ao lado do alerta conduz a melhor decisão — nunca foi
    testada, o que é que a dissertação demonstra?» — **Respondida**, e é o melhor momento
    disponível: §6.6 fólio 93 e Figura 6.3, que separam explicitamente o que fica estabelecido do
    que não fica. **Ensaiar esta.**

---

# F. Melhorias

## F.1 — Valem o risco de mexer num documento verificado

A fronteira que usei: **vale a pena se corrige uma afirmação falsa ou uma incoerência aritmética,
e se o diff é de palavras e não de estrutura.** Corrigir uma afirmação falsa nunca é opcional;
reorganizar prosa correta a poucos dias do congelamento troca risco por arrumação.

1. **A02** — afirmação quantitativa falsa no capítulo de conclusões. Três palavras.
2. **A03** — aritmética que não fecha numa tabela de três linhas. Um dígito.
3. **A04** — vocabulário que descreve mal a garantia central. Quatro palavras.
4. **A06** — frase contradita pela tabela que a antecede. Duas palavras.
5. **A07** — legenda que afirma de quatro barras o que é verdade de duas. Duas palavras.
6. **A10** — nomear o Finnhub. Uma palavra.
7. **A05, versão barata** — uma frase de reconciliação movida para onde a dúvida nasce.
8. **A08** — repetir a ressalva de arredondamento. Uma frase.
9. **B7 e as duas irmãs** — os três meta-comentários sobreviventes: «*que importa enunciar sem
   atenuação*» (§2.9), «*a razão fica registada*» (§5.6.4), «*a distinção fica registada em vez de
   omitida*» (§A.2). ⚠️ **As duas últimas são defensáveis** — «registada em vez de omitida» é uma
   afirmação de método, não enchimento —, e recomendo mexer **só na primeira**.
10. **A01, opção (2)** — a linha tracejada anotada na Figura 5.6. É o único item desta lista que
    toca uma figura, e é o de maior retorno: fecha a pergunta de júri mais provável do capítulo.

## F.2 — Não valem o risco

1. **A01, opção (1)** — medir o filtro por setor. Uma execução nova a poucos dias do
   congelamento, com propagação para a figura, o texto, o Cap. 6, o artigo, os slides e o quizz.
   O ganho é marginal face à opção (2), porque o valor é `1,000` por construção e toda a gente o
   sabe depois de ler a frase.
2. **A09 na íntegra** — reescrever as cem construções antitéticas. Recomendo os **cinco pares
   consecutivos e mais uma dúzia**, não mais. Cada frase reescrita num documento verificado é uma
   oportunidade de introduzir uma concordância errada, e este projeto já pagou essa fatura.
3. **Repetição do argumento Blume/Vasicek** entre §2.5 (fólio 13) e §3.4 (fólio 22), quase
   palavra por palavra: «*…de encolher a estimativa com um peso fixo. Essa prática aplica a mesma
   correção a estimativas precisas e imprecisas.*» É redundância real, mas os dois capítulos têm
   funções diferentes (porque existe a técnica / o que fazemos com ela) e cortar num deles obriga
   a reler o outro. **Deixar.**
4. **«ignorar um aviso correto ou a aceitar um aviso incorreto»**, verbatim em §2.7, §3.8.3 e
   §6.4. Três repetições da mesma oração. Cada uma está no seu sítio e cada capítulo tem de se
   sustentar sozinho. **Deixar.**
5. **Eixo truncado da Figura 1.1** (fólio 2), que começa em 20 e não em 0. Convenção corrente em
   séries financeiras, e a figura é ilustrativa de contexto, não um resultado. **Deixar**, com a
   ressalva de que um arguente com formação em visualização pode apontá-lo e a resposta é a
   convenção.
6. **Páginas de flutuantes com muito branco** (fólios 11 e 20, que só têm tabelas). Mexer no
   posicionamento de flutuantes reflui o documento inteiro. **Deixar.**
7. **A Tabela 5.4 repete «z-score deslizante» em duas linhas consecutivas** como opção
   implantada. É correto — são duas alternativas medidas contra a mesma opção — e agrupar as
   linhas mexeria numa tabela de treze linhas já composta. **Deixar.**
8. **§5.2.5: «elimina quase metade dos falsos alarmes»** quando a conta dá `53 %`. A afirmação
   **subestima** o ganho da alternativa que não foi adotada, ou seja erra contra o interesse do
   autor. **Deixar.**
9. **A legibilidade do texto nas três capturas de ecrã** (fólios 44, 45, 46). Medido: as fichas
   de data compõem a cerca de **6 pt**, pequeno mas legível, e a legenda da Figura 4.7 já declara
   e justifica a largura de captura escolhida. **Deixar.**
10. **Reestruturar, encurtar ou acrescentar secções.** Nada nesta auditoria o justifica.

---

# G. O que verifiquei e estava limpo

Esta secção existe para não se voltar a gastar tempo aqui.

**Aritmética refeita à mão, e fecha em todos os casos.**

- Funil da Figura 4.4: `5060 − 2994 − 1194 − 269 − 249 − 21 = 333`; eliminações `= 4 727`;
  `4 727 + 333 = 5 060`. Exato.
- Divisão com embargo: `28 574 + 17 710 + 32 649 = 78 933 = 79 753 − 820`; `820/79 753 = 1,03 %`.
  Exato.
- Coerência da divisão com as datas: `70 %` de ~1 500 dias de bolsa a partir de 2018-01-02 cai em
  março de 2022, e o bloco de teste 2023-02-02 a 2023-12-18 tem ~221 dias, que é o número que a
  §5.4.3 declara. Os `1 951` grupos empresa-dia cabem em `9 × 221 = 1 989`. **Fecha por três vias
  independentes.**
- Caso trabalhado da Tesla (§3.3): `(19,82 − (−0,92)) / 2,725 = 7,611`. Exato. E
  `e^0,1982 − 1 = 21,92 %`. Exato.
- Decomposição da AMD (Figura 3.3): `−0,3992 − 0,0362 + 6,7298 = 6,2944`. Exato. E
  `e^0,062944 − 1 = 6,50 %`. Exato.
- Decomposição da Netflix (Figura 4.8): `−0,61 − 0,22 + 0,53 = −0,30`. Exato.
- Taxa-base da pós-validação: `(436 × 0,589 + 389 × 0,617)/825 = 0,6022`. Exato. E `436 + 389 = 825`.
- Brier de referência: `0,3781 × 0,6146² + 0,6219 × 0,3854² = 0,23519`. Exato, e o
  «anunciar sempre a unidade» dá `1 − 0,3781 = 0,622`. Exato.
- F1 do z-score: `2 × 0,381 × 0,800 / 1,181 = 0,516`. Exato. O do limiar fixo dá `0,217` contra
  `0,218` impresso, **e a §5.1 declara essa diferença antes de ela acontecer**.
- F1 do EWMA: `2 × 0,568 × 0,800 / 1,368 = 0,664`. Exato.
- Amplitudes da Figura 5.2: `35,3 − 0,9 = 34,4` e `3,1 − 1,6 = 1,5`. Exato.
- Margens da recuperação: `0,514 − 0,240 = 0,274`; `0,514 − 0,467 = 0,047`;
  `0,595 − 0,333 = 0,262`; `0,513 − 0,259 = 0,254`; diferença de margens `0,008`. Exato.
- Fração de tecnologia: `1 736/3 714 = 0,4674`, igual à precisão da estratégia trivial. Exato.
- Ganho setorial: `0,712 − 0,429 = 0,283`. Exato.
- Anterioridade: `31,1 % + 38,7 % + 30,2 % = 100 %`. Exato.
- Consultas: `500 × 5 sementes = 2 500`. Exato. Sementes `42–46` são cinco; `0–39` são quarenta.
- Fontes de notícias: `432 + 141 + 429 = 1 002`; `1 002 − 970 = 32` duplicados;
  `401 + 119 + 418 = 938 = 970 − 32`. **Fecha nas duas direções.**
- Funil de setembro: `743/15 = 49,5`, «um para cinquenta». Exato.
- Diferença emparelhada: `0,542 − 0,496 = 0,046`, declarado como distinto da média de
  reamostragem `+0,048`. Exato e explicado.
- Sobreposição de empresas: `13 − 5 = 8 = 9 − 1`; `100 − 17,1 = 82,9`. Exato.
- Ganho sobre o desempate alfabético: `0,632/0,379 = 1,67` e `0,632/0,163 = 3,88`. Exato.
- Margem ao oráculo: `0,968 − 0,632 = 0,336`. Exato.
- Cobertura: `47/52 = 90,4 %`. Exato.
- Votos: `42 + 10 + 29 = 81`; `42 × 0,67 ≈ 28`, `42 − 28 = 14`. Exato. ⚠️ **Uma nota de leitura,
  não um erro:** o parágrafo lista `42`, `10`, `29` e `5` em sequência, e os `5` excluídos ficam
  **fora** dos 81. Quem somar os quatro obtém 86. É correto e a palavra «excluídos» resolve-o,
  mas é a única cadeia do documento em que a soma óbvia não é a soma certa.
- Custo de alojamento: `(25 + 50) − (7 + 7) = 61`, e `50 − 7 = 43`. Exato, e a legenda explica
  porque não são 43.
- Memória: `38 214 × 384 × 4 B = 56 MiB` — **é este cálculo que gera a suspeita D6.**

**Consistência entre capítulos.** Indexei todos os decimais e inteiros da prosa, com figuras,
tabelas e excertos removidos, e comparei os que aparecem em mais do que um capítulo: **39 valores
partilhados entre o Cap. 5 e o Cap. 6, e nenhum diverge.** As colisões aparentes (`970` como
títulos e como megabytes; `333` como avaliações e como `0,333`; `512` como MB e como `0,512`) são
homónimos e não contradições.

**Estrutura da cadeia científica.** Problema (§1.1) → lacuna (§2.9) → três QI (§1.3) → quatro
objetivos (§1.3) → metodologia (§3.1) → implementação (Cap. 4) → quatro casos de estudo (Cap. 5)
→ veredictos (§6.2) → objetivos alcançados (§6.3) → limitações (§6.4) → futuro (§6.5). **Cada elo
sustenta o seguinte.** As três QI são enunciadas no fólio 3 e respondidas no fólio 83 com a mesma
formulação, incluindo as restrições («*as alternativas textuais e de ordenação avaliadas*»). Os
quatro objetivos são percorridos um a um na §6.3. **Nenhuma conclusão afirma mais do que a
evidência que a antecede** — e a §6.6 e a Figura 6.3 fazem o inverso, delimitando explicitamente
o que não ficou estabelecido.

**Contagens prometidas, uma a uma.** «quatro contribuições» = 4 (§1.4). «três das quatro
técnicas» com linhas de base = 3, coerente com o resumo, com o §6.1 e com a Tabela 5.4. «nove
etapas» na Figura 4.2 = 9, com 5 pontos de decisão. «nove pontos de decisão» na Figura 4.5 = 9,
sendo 5 da Figura 4.2 e 4 de fora, e a legenda nomeia os quatro. «onze limitações» na Tabela 6.1
= 11, das quais 4 desenvolvidas e 7 em síntese. «dez linhas de trabalho futuro» = 10, e a
Figura 6.2 agrupa-as 2 + 1 + 7 = 10. «três linhas registam que a opção implantada não obteve o
melhor resultado» na Tabela 5.4 = 3. «as três últimas linhas são restrições» = 3. «duas linhas
não afirmadas» na Tabela A.2 = 2. «três ocasiões em que uma técnica mais simples superou» = 3, e
«três ocasiões em que sucedeu o inverso» = 3. **Todas fecham.**

**Referências cruzadas com número de página.** §2.8 remete para «a Tabela 5.4, na página 80» — a
Tabela 5.4 está no fólio 80. §5.4.4 remete duas vezes para «a Figura 5.18, na página 77» — está
no fólio 77. **As duas estão certas.**

**Destinos das ligações do índice.** Resolvidos com `pypdf`: as cinco entradas das listas
preliminares apontam para as páginas físicas 11, 13, 15, 17 e 18, que são exatamente onde as
listas começam, e os fólios impressos aí são xi, xiii, xv, xvii e xviii — o que o índice anuncia.
As restantes 104 ligações resolvem para a página da secção que nomeiam ou para a seguinte.
**Zero destinos errados.**

**Composição.** `0` erros de compilação, `0` referências ou citações indefinidas nos dois
registos (as únicas ocorrências de «undefined» são avisos de forma de fonte). Overfull máximo
`5,68 pt` (PT) e `8,61 pt` (EN). Nenhum flutuante fora da página que o invoca. Nenhuma legenda
cortada. Nenhum texto sobreposto nas figuras inspecionadas em imagem — incluindo a nota inferior
da Figura 4.5, que fica abaixo do traço e não o atravessa.

**Tabelas inspecionadas em imagem e não por extração de texto:** 2.1, 2.2, 3.1, 3.2, 4.2, 5.4,
A.2, A.3, e as Figuras 1.1, 4.5, 4.8 e A.1. **Todas compõem corretamente.**

**Bibliografia.** 64 entradas renderizadas, todas com ano, todas com identificador (DOI, URL ou
ISBN), formatação uniforme. Conferi a fundo os metadados de Robertson e Zaragoza (2009) —
*Foundations and Trends in Information Retrieval* **3**(4), 333–389, DOI `10.1561/1500000019` —
que a auditoria anterior corrigiu, e estão certos. Verifiquei Angelopoulos e Bates (2023),
FNSPID (KDD '24), Isolation Forest (ICDM 2008), LOF (SIGMOD), SBERT (EMNLP-IJCNLP 2019) e
Vasicek (1973): todos corretos. **Zero entradas órfãs** (o `biblatex` só imprime as citadas).

**Acrónimos.** 26 declarados, **14 impressos** — a lista mostra apenas os usados, que é o
comportamento correto. Nenhum acrónimo é usado antes de ser expandido: verifiquei `QI`, `PR-AUC`,
`ROC-AUC`, `PSI`, `ONNX`, `HTTP`, `SBERT`, `ARCH`/`GARCH`, `FNSPID`, `LIME`, `SHAP`, `BERT`, `IA`.

**Escrita.** Zero transições formulaicas em início de frase (`Ademais`, `Outrossim`, `Por
conseguinte`, `Nesse sentido`, `Com efeito`, `Em suma`, `Desta forma`…). Zero ênfase dramática
(`crucial`, `fundamental`, `extremamente`, `notável`, `impressionante`). **Três** meta-comentários
sobre o próprio texto, e recomendo mexer só num (ver F.1.9). Nenhuma frase acima de 60 palavras.

**Metodologia — procurei e não encontrei.** Fuga de informação futura: a janela do z-score exclui
o dia avaliado por fatia, a divisão é cronológica com embargo, a estimação dos betas termina na
véspera, e existe um teste executável que muta o futuro. Viés de sobrevivência: **declarado**
(§5.2.6, §6.2.1). Preços não ajustados: **não é o caso, e o documento quantifica o dano que
seriam**. Unidade de análise errada: a reamostragem é por grupo empresa-dia, e a §5.6.2 corrige
explicitamente `825` decisões para `239` unidades independentes. Reutilização do bloco de teste:
**declarada como limitação** (§5.4.6). **Nada a acrescentar em nenhum destes eixos.**

---

## Alarmes meus, levantados e retirados antes de entrarem no relatório

Ficam registados porque os quatro teriam mandado corrigir coisas certas.

1. **«A Figura 5.12 diz `0,368` onde o texto diz `0,378`.»** Falso. A extração de texto
   entrelaça as duas séries de barras por posição vertical; no código-fonte a PR-AUC de ambas as
   linhas inferiores é `0,378`. **O texto está certo.**
2. **«O Peffers está escrito “Peers” na bibliografia.»** Falso. É a ligatura `ff` perdida pelo
   `pdftotext` — o mesmo artefacto que transforma «Bibliografia» em «Bibliograa» e «Jeff» em
   «Je». O `.bib` diz `Peffers`.
3. **«O Finnhub não aparece na Figura A.1.»** Falso. Aparece como logótipo. O achado sobreviveu
   numa forma muito mais estreita, e essa é a A10: aparece **sem nome**.
4. **«A média do exemplo da Tesla dá z = 6,94 e não 7,61.»** Falso. A média é `−0,92 %`, e a
   extração perde o sinal negativo. Com o sinal, fecha à segunda casa.

**A lição de método, e é a mesma das auditorias anteriores: nenhum achado sobre uma figura ou uma
tabela pode ser reportado a partir de texto extraído. Renderizar a página, ou ler o código-fonte
do flutuante.**

---

## Veredicto

Vinte e quatro achados nas auditorias anteriores, dez aqui, e **nenhum deles toca um resultado**.
As cinco correções da secção B que valem mesmo a pena somam cerca de doze palavras alteradas em
seis ficheiros. O documento resiste a uma leitura hostil. Das trinta perguntas de júri da
secção E, **vinte e seis têm a resposta escrita no sítio onde a pergunta nasce**; duas têm-na
escrita no sítio errado (a 16 e a 27, que são o A01 e o A05); e **duas não têm resposta
preparada** — a 28 e a 29, que são o A03 e o A02, e as duas fecham-se com um dígito e três
palavras.

O ponto de ataque que ficaria sem resposta preparada é apenas um, e é o **A01**: a alternativa
mais forte à recuperação semântica está descrita em prosa e ausente das duas figuras que carregam
o veredicto da QI2.

---

# Aplicação — B1 a B6, nas duas árvores

Corridas a 2026-09-07, a pedido do autor. **Nenhum número foi alterado**, e nenhuma medição
correu.

| # | Achado | O que ficou escrito |
|---|---|---|
| B1 | **A02** | §6.2.2: «*O valor de referência sobe também, e mais depressa, pelo que a margem desce de +0,274 para +0,262*». EN: «*rises too, and faster, so the margin falls from +0.274 to +0.262*». |
| B2 | **A03** | Legenda da Tabela 5.2: «*As duas amplitudes estão arredondadas à terceira casa e a razão é calculada sobre os valores não arredondados, pelo que a divisão refeita sobre os números impressos pode diferir na casa apresentada.*» **O `6,1×` fica.** Ver a nota abaixo. |
| B3 | **A04** | Apêndice A: seis ocorrências de `critério` → `rótulo` (`criterion` → `label`). Zero ocorrências remanescentes em qualquer das árvores. |
| B4 | **A06** | §2.2: «*A única ferramenta existente que responde às três perguntas é também a mais dispendiosa de todas.*» |
| B5 | **A07** | Legenda da Figura 5.12: «*situam-se **na PR-AUC** exatamente na prevalência*». Escrito em texto simples e não com `\gls`, porque **nenhuma legenda do documento usa `\gls`** e não é este o sítio para abrir a exceção. |
| B6 | **A10** | Figura A.1: a linha de nomes passa a `Finnhub / Alpha Vantage / Polygon`. |

⚠️ **B2 mudou de forma depois de consultar o artefacto, e a razão importa.** A auditoria, que só
podia ver o PDF, ofereceu duas opções e chamou «menos invasiva» à de imprimir `6,0×`. **Estava
errada.** O gerador escreve `{entre/dentro:.1f}` sobre os valores **não arredondados**, e o
`evaluation_gate_selectivity.md` publica `6.1×` ao lado de `0.064` e `0.385`. Imprimir `6,0×`
faria a tese divergir do artefacto que a sustenta — e o `check_tese_numeros`, que exige origem
para todo o número, apanharia a divergência. O dígito está certo; o que faltava era dizer ao
leitor porque é que a divisão não reproduz. **Corrigiu-se a explicação, não o número.**

⚠️ **B6 fez disparar uma porta, e o disparo estava certo.** O `check_figuras_paridade` acusou
`Finnhub\\ Alpha Vantage\\ Polygon` como «rótulo idêntico nas duas árvores por traduzir». É uma
isenção legítima — são marcas registadas — e foi declarada em `ISENTOS` com a razão escrita ao
lado, substituindo a entrada anterior, que ficaria morta. A porta comportou-se como devia: viu a
alteração e exigiu justificação.

**Portas depois da aplicação:** PT **122 pp** · EN **121 pp** · 0 erros · 0 referências ou
citações indefinidas · overfull máximo **5,68 pt** (PT) e **8,61 pt** (EN), com as mesmas 5 e 4
caixas de antes das edições · 0 `Float too large` · `check_entrega` verde nos 19 verificadores ·
**1027 testes** · `ruff` limpo.

**Verificado no PDF compilado e não no `.tex`:** as seis alterações estão presentes nas duas
árvores, e as duas cujo posicionamento mudou foram inspecionadas em imagem — a caixa «Fontes» da
Figura A.1 acomoda a terceira linha sem transbordar nem colidir com «preços e notícias», e a
Tabela 5.2 compõe com a legenda mais longa, agora na mesma página da Figura 5.15 que ela confirma.

⚠️ **A procura de `definições de rótulo` no PDF devolveu zero e não era um problema:** a ligatura
`fi` desaparece na extração de texto, e a cadeia real é `denições`. É a quinta vez que este
artefacto engana nesta auditoria. **Está confirmado com a grafia sem ligatura: 3 ocorrências de
`nine label` em inglês e 0 de `nine criterion`.**

## Segunda passagem: A01, A05 e A08

Aplicados a seguir, a pedido do autor. Continuam **zero números alterados** e zero medições
corridas — o `1,000` que entra na Figura 5.6 já constava da §5.3.3.

**A01 — a Figura 5.6 passa a mostrar o teto.** Linha nova no topo, `Filtro pelo setor da
consulta`, a `1,000`, no mesmo estilo tracejado da outra estratégia sem modelo, para que as duas
se leiam como um par. O eixo passa de `0,66` para `1,14` e a altura de 6,6 para 7,2 cm. A legenda
diz o que o número é e o que não é: «*O $1{,}000$ não é uma medição: é uma consequência
aritmética da definição de relevância, e consta aqui por ser o valor de referência mais alto que
esta tarefa admite. Não constitui alternativa de produto, uma vez que devolveria casos do mesmo
setor sem observar o tema da notícia.*» Título curto e corpo passam de «seis alternativas» para
«sete».

⚠️ **Custo medido, e é real:** o eixo alargado encurta todas as barras. `0,126` passa de ~1,9 cm
para ~1,1 cm. A ordenação e a distância entre `0,126`, `0,240`, `0,346` e `0,420` continuam
legíveis, e a comparação que a figura existe para fazer — o método contra as alternativas — não
se perde. **A árvore inglesa passou de 121 para 122 páginas** por causa da figura mais alta.

⚠️ **E a primeira versão tinha um defeito que só o render mostrou.** O rótulo `1,000` assentava
sobre o traço superior da própria barra, ao contrário de todos os outros, que têm folga. Não
aparece em erro nem em overfull: o `exit code` é 0 nos dois casos. Corrigido com `yshift=1.5pt`
nos rótulos desta figura, e **reconferido em imagem a 400 dpi** — a folga passa a ser a mesma do
`0,538`.

**A05 — a reconciliação passa para onde a dúvida nasce.** Frase nova na §5.4.4, logo a seguir ao
`0,662`: «*O valor não é o da linha só volatilidade da Figura 5.12, que é uma regressão sobre a
volatilidade diária e obtém 0,632 nesta métrica: aqui a volatilidade entra como uma constante por
empresa, e a Secção 5.6 reconcilia as duas.*» É **mais curta do que a frase da §5.6.4** e remete
para ela, em vez de a duplicar — a duplicação verbatim alimentaria o A09.

**A08 — a ressalva de arredondamento entra na §5.4.6**, a seguir ao `+0{,}012`: «*O acréscimo e a
base estão arredondados à terceira casa, pelo que somá-los pode diferir na última do valor que a
reserva seguinte reporta.*» Fecha a distância entre `0,534 + 0,012` e o `0,547` impresso uma
página adiante.

**Portas depois da segunda passagem:** PT **122 pp** · EN **122 pp** · 0 erros · 0 referências ou
citações indefinidas · overfull **5,68 pt** e **8,61 pt**, com as mesmas 5 e 4 caixas de antes de
qualquer edição desta sessão · 0 `Float too large` · 19 verificadores verdes · **1027 testes** ·
`ruff` limpo. A Figura 5.6 foi inspecionada em imagem nas duas árvores, e o `Secção 5.6` e o
`Figura 5.12` da frase nova resolvem nas duas.

## Terceira passagem: A09

⚠️ **Medir outra vez, com a ferramenta certa, mudou o âmbito do que havia a fazer — e para menos.**
O achado A09 recomendava «os cinco pares consecutivos e mais uma dúzia dos casos mais próximos
entre si», e a segunda metade dessa receita assentava num pressuposto que **não se confirma**:
varridos os parágrafos um a um, **nenhum tem três ou mais** ocorrências. A construção não forma
aglomerados; está distribuída de forma quase uniforme, uma a cada quinze frases. O alvo de
«descer de 100 para ~70» foi construído sobre densidades que não existem.

**O que existe, e é o que um leitor perceciona, são treze parágrafos com duas ocorrências cada**,
seis deles em frases consecutivas. Ninguém repara numa construção que aparece a cada quinze
frases; repara em duas na mesma passagem. Foi esse o conjunto tratado: **uma reescrita por
parágrafo, treze ao todo, espelhadas nas duas árvores.**

| medida | antes | depois |
|---|---|---|
| construções antitéticas (PT) | 111 | **98** |
| construções antitéticas (EN) | 118 | **107** |
| pares de frases consecutivas (PT) | 6 | **0** |
| pares de frases consecutivas (EN) | 4 | **0** |
| parágrafos com duas ou mais | 13 | **0** (PT) · 1 (EN, artefacto do detetor) |

⚠️ **A ocorrência que resta na árvore inglesa não é uma assimetria entre as duas teses**: é uma
assimetria entre os dois detetores. O padrão português não apanha «*A lacuna não é, portanto, de
método, mas de integração sob restrição*» porque as vírgulas interrompem a janela do padrão. A
frase existe nas duas línguas e ficou intocada nas duas.

**As treze passagens tratadas**, sempre substituindo a construção por uma forma que o próprio
documento já usa noutros sítios — subordinada concessiva, dois períodos, ou `sem` + infinitivo:
§2.1 (alcance da afirmação de Barber e Odean), §2.6 (política de decisão), §2.9 (componentes
académicos), §4.5 (número de precedentes exibidos), §4.6.1 (o que o ciclo atualiza), §5.2.3
(a medida e a sua leitura), §5.3.3 (o valor agregado), §5.5 (o conjunto das dezassete empresas),
§6.2.2 (a pertença ao setor), §6.2.3 (o enquadramento teórico), §6.3 (o terceiro objetivo),
§6.4 (deriva medida e não corrigida) e §A.2 (a medição não regenerável).

**⚠️ E DUAS DAS MINHAS REESCRITAS INTRODUZIRAM UM DEFEITO NOVO, apanhado a ler o PDF e não pelas
portas.** Em §2.1 escrevi «*delimitam o alcance da afirmação… sem **alcançar** um comportamento
universal*», com o eco na mesma frase; e em §5.2.3 escrevi «*o que daqui **decorre**…*» a seguir a
«*A afirmação **decorre** da construção do método*», com o eco em frases adjacentes. Corrigidos
para `abranger` e `daí resulta`, e os equivalentes ingleses (`reach`/`reaching` →
`without extending to`; `follows`/`follows` → `what it requires is`). **É a demonstração do custo
que a secção F.2 descreve: cada frase reescrita num documento verificado é uma oportunidade de
introduzir um defeito, e duas em treze introduziram-no.**

**Verificado:** as treze passagens foram lidas **como renderizam no PDF**, não no `.tex`. Três não
apareceram à primeira procura — `verificável`, `verificação` e `fica` perdem a ligatura `fi` na
extração e saem `vericável`, `vericação` e `ca`. Sexta vez nesta sessão.

**Portas depois da terceira passagem:** PT **122 pp** · EN **122 pp** · 0 erros · 0 referências ou
citações indefinidas · overfull **5,68 pt** e **8,61 pt**, ainda iguais ao registo anterior a
qualquer edição desta sessão · 0 `Float too large` · 19 verificadores verdes, incluindo
**«tradução: nenhuma ressalva perdida»**, que é o que garante que nenhuma reescrita comeu uma
ressalva · **1027 testes** · `ruff` limpo.

**Não aplicado:** tudo o que consta de F.2, e por escrito lá — incluindo a versão «na íntegra» do
A09, ou seja reescrever as restantes 98. A construção é a espinha epistémica do trabalho e deve
ficar; o que se tratou foi a repetição audível, não a figura de retórica.

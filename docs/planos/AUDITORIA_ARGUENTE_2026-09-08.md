# Auditoria em papel de arguente hostil — 2026-09-08

Terceira auditoria desta série, feita sob as mesmas três regras: **só o PDF**; **procurar
primeiro se a objeção já está respondida**; e **não inventar defeitos** — o que não se
conseguir provar sai marcado como suspeita, não como achado.

As seis escolhas deliberadas continuam fora de âmbito: figuras inglesas por dentro com
legenda portuguesa, alerta e capturas em inglês, excertos de código verbatim, a resposta
negativa à QI3, a matriz de afirmações retiradas do Apêndice A, e a ausência de estudo com
pessoas.

⚠️ **O que torna esta passagem diferente das duas anteriores:** a sessão de hoje acrescentou
seis figuras, uma secção, uma página de orientação e uma captura nova. **Essa é a superfície
de maior risco**, porque é texto que nunca foi auditado. A auditoria foi dirigida para lá em
primeiro lugar, e foi lá que os achados apareceram — **três dos quatro são defeitos meus,
desta sessão**.

---

## A. O achado principal, e não é uma frase da tese

### A01 — O verificador das remissões do apêndice estava cego e aprovava tudo

| | |
|---|---|
| **Severidade** | **Alta** |
| **Tipo** | Porta de qualidade sem efeito |
| **Localização** | `scripts/check_apendice_xref.py`, um dos 19 do `check_entrega` |

**Problema.** A Tabela A.2 promete que cada resultado está rastreável até à secção que o usa,
e este verificador existe para o confirmar. Apontei-lhe uma remissão **deliberadamente
errada** — o resultado da amplitude da taxa de disparo, que é do Capítulo 3, a apontar para a
secção do retorno dos leitores, que é do Capítulo 5 — e ele respondeu:

```
linhas com problema: 0
```

**Porquê.** É uma assimetria de uma linha. A tese escreve os decimais na convenção PT-PT em
modo matemático, `$0{,}015$`, e entre o `0` e o `015` está `{,}` e não uma vírgula. O padrão
`\d+[.,]\d+` não casa com isso. A lista de valores saía **vazia**, o ciclo de comparação nunca
corria, e cada linha era impressa como `ok`. O palheiro já era normalizado umas linhas
abaixo; **a agulha não**.

⚠️ **É o modo de falha que este projeto documenta desde a sessão 63: não encontrar nada e
aprovar tudo têm o mesmo aspeto no ecrã.** O verificador imprimia «linhas com problema: 0»
com a mesma serenidade antes e depois de lhe plantarem o erro. E a ironia está no próprio
ficheiro: o cabeçalho dele descreve três rondas anteriores de correção e **um teste de
sabotagem que ele passou**, com a nota «só se percebeu porque eu insisti em vê-lo falhar».
Foi corrigido para o arredondamento e ficou cego para a vírgula.

**Correção.** Normalizar a célula antes de extrair. ⚠️ **E à primeira corrigi-o mal:** deitar
fora o desenho inteiro fazia-o acusar **duas linhas corretas**, porque várias linhas do
apêndice apontam para secções cuja evidência **é** a figura. O discriminador exato estava no
próprio ficheiro — dentro de um `tikzpicture`, uma **coordenada** escreve-se com ponto
(`axis cs:0.158,0.913`) e um **rótulo desenhado** escreve-se com `{,}` (`$F_1=0{,}269$`). Só
o segundo é uma afirmação que o leitor vê.

**Verificação.** Corpus real: 0 problemas. Sabotagem: 1 problema. Sete testes novos, e o que
decide foi **verificado a falhar** com a cegueira replantada.

**Já tratado?** Não. Era novo.

---

### A02 — A remissão da guarda aponta para a secção que já não a contém

| | |
|---|---|
| **Severidade** | Média |
| **Tipo** | Remissão falsa |
| **Localização** | Apêndice A, Tabela A.2, linha «Verificação da geração ancorada» |

**Problema.** A linha promete que os `23 de 23` e `8 de 8` aparecem na secção que nomeia, e
apontava para a **§4.7**. Os números estão na **§4.8.3**.

**Porquê.** ⚠️ **É defeito meu, desta sessão.** Antes do item A1 de hoje, a camada de geração
ancorada estava descrita num parágrafo **dentro da §4.7**, e a remissão estava certa. O A1
criou a §4.8 e levou o conteúdo para lá, deixando na §4.7 apenas um ponteiro — e a linha do
apêndice ficou a apontar para uma secção onde os números já não estão.

**E nenhuma porta o via**, por duas razões que se somam: o verificador estava cego (A01), e
mesmo depois de curado esta linha **continua a não ser testada**, porque o seu valor são só
inteiros e a regra dos decimais não os cobre.

**Correção.** Remissão corrigida para `sec:sis_inteligencia` nas duas árvores. E o verificador
passa a **declarar** as cinco linhas que não testa, em vez de as imprimir como `ok` — uma
linha por verificar impressa como verificada é a forma exata de uma porta mentir sem se
enganar.

**Já tratado?** Não.

---

## B. Achados de conteúdo

### B01 — A mesma pergunta com dois denominadores

| | |
|---|---|
| **Severidade** | Média |
| **Tipo** | Inconsistência entre duas superfícies do mesmo sistema |
| **Localização** | Figura 1.1 (p. 3) contra Figura 4.8 (p. 47) |

**Problema.** A Figura 1.1 reproduz o alerta e conta «**73** dos últimos **126** dias»; a
Figura 4.8 mostra a página e conta «**141** dos últimos **250**». Mesma empresa, mesmo dia.

**Porquê.** Não é erro de nenhuma das duas, e não é truncatura. Verificado no código:
`get_price_history` tem `period="6mo"` por omissão e o varrimento que compõe o alerta chama-a
**sem período**, ao passo que o `build_snapshot` pede `"1y"`. Medido: **127** e **252**
sessões. As frações são próximas (58% e 56%); os denominadores não.

**Correção.** ⚠️ **Não se uniformiza o produto a dezanove dias do congelamento.** Duplicar o
histórico por empresa e por ciclo tem custo de memória num contentor que este projeto já viu
esgotar, e mudaria o texto de alertas futuros sem mudar resultado nenhum. Declara-se, que é o
que a tese faz com as outras assimetrias que conhece — duas frases onde a interface é
descrita.

**Já tratado?** Não. É consequência de eu ter posto os dois números no mesmo documento hoje.

---

### B02 — A página de orientação promete doze páginas para um percurso de nove

| | |
|---|---|
| **Severidade** | Baixa |
| **Tipo** | Número errado |
| **Localização** | «Como ler esta tese», percurso de quem quer o resultado |

**Problema.** Diz «São cerca de doze páginas». Medido no PDF: o Capítulo 1 ocupa as páginas
árabes **2 a 6** e a §6.2 as **87 a 90** — **nove**.

**Porquê.** Numa página cuja única função é orientar, um número errado é pior do que nenhum:
é a primeira coisa que o leitor pode verificar, e falha.

**Correção.** «cerca de dez», nas duas árvores.

**Já tratado?** Não. Escrito hoje.

---

## C. O que foi verificado e estava limpo

A ausência é resultado, e fica escrita para ninguém voltar a gastar tempo:

| verificação | resultado |
|---|---|
| Tabela 6.1 contra a promessa «as onze limitações» | **11 linhas**, a contagem sobrevive à edição do B1 |
| Figura 4.8 contra o parágrafo que a descreve | seis valores, **todos coincidem** |
| Aritmética das parcelas da Figura 4.8 | $-0{,}47-0{,}54+2{,}00 = +0{,}99$ **exato** a duas casas |
| «mais do dobro do movimento observado» | $2{,}00/0{,}99 = 2{,}02$ ✓ |
| Tabela 4.3, suspeita de linhas desalinhadas | **falso alarme** — ver bloco D |
| «o documento regista três ocasiões» | as três estão lá: $0{,}467$, o valor de acaso que sobe, e $0{,}163$ |
| §4.8.3, contagem de secções compostas | corretamente **não** afirmada, por ser amostra de uma execução |
| §4.8, comparação com RAG completa | corretamente declarada como **não realizada** |
| Páginas de corpo quase vazias | **nenhuma** além da dedicatória, por desenho |
| `Float too large` · vbox mal composta | **0 · 0** nas duas árvores |

---

## D. Alarmes meus, retirados antes de entrarem no relatório

⚠️ **Valem mais do que alguns achados, porque medem a fiabilidade do método.**

**D1 — a Tabela 4.3 «desalinhada».** Na extração de texto, os rótulos das linhas apareciam
deslocados uma posição em relação aos valores. Ia reportá-la. **Renderizada, está perfeita**:
é o `pdftotext` a desmontar uma tabela cuja primeira coluna muda de linha. É a mesma classe
que a sessão 66 já tinha documentado com a Lista de Símbolos, e a regra do projeto — nenhum
achado sobre tabela sai de texto extraído — funcionou.

**D2 — «o verificador casou 23 dentro de 2023».** Foi a minha primeira explicação para o A01,
e **estava errada**. O único `23` na §4.7 é mesmo o ano de 2023, mas não é por aí: o
verificador não extraía valor nenhum de linha nenhuma. Diagnóstico plausível, mecanismo
errado — e a diferença importa, porque a correção que ele sugeria (fronteiras de palavra) não
teria resolvido nada.

**D3 — duas linhas do apêndice «sem fonte».** Depois de curar o A01, o verificador acusou a
comparação com os dois detetores aprendidos e o índice de deriva. **As duas estão certas**: os
valores existem nessas secções, desenhados nas figuras. Era a minha própria correção a gritar
de mais.

**D4 — a medição de composição, refeita duas vezes.** A primeira versão aproximava a página de
uma remissão pelo `\label` anterior no ficheiro, o que dá um número sem significado. A segunda
partia a extração em alimentações de página — e este documento tem alimentações **parasitas
dentro das equações**: para um PDF de 129 páginas a divisão dava **148 pedaços**. Cheguei a
ter uma lista de «flutuantes a 101 páginas da remissão» inteiramente artefactual.

---

### D5 — o meu proprio teste fez uma porta gritar de mais

O teste de sabotagem do A01 reescreve o apendice e repoe-o. Repor o CONTEUDO nao chega: a
data do ficheiro fica mais recente do que a do PDF, e o `check_tese_pt`, que compara as duas
para apanhar um PDF por recompilar, passou a acusar uma desactualizacao que nao existia.
**Um teste que faz uma porta gritar de mais e um defeito, e nao um teste.** Passa a repor
tambem a data, e ha' uma asserçao que o exige.

---

## E. Suspeitas que ficam por confirmar

**E01 — «o documento regista três ocasiões em que isso quase sucedeu».** A afirmação é da
página de orientação e é **defensável**: as três ocasiões estão no documento. Mas o documento
**não as enumera como três**, pelo que um leitor que queira confirmar a contagem tem de as
procurar. Não é falso; é uma afirmação cuja verificação custa mais do que devia. Fica
assinalada e não corrigida, por a correção exigir decidir o que o autor quer afirmar.

---

## F. O que esta auditoria não pôde fazer

Os quatro itens da Tabela 6.1 que exigem re-treinar continuam **materialmente inexecutáveis**
nesta máquina: `data/triage_dataset.csv` e o corpus FNSPID não existem aqui. Re-verificado
hoje, não repetido de memória.

---

## G. Leitura final

**Nenhum dos quatro achados toca um resultado.** Nenhum número medido mudou. O que mudou foi
uma porta que não guardava nada, uma remissão que apontava para o sítio errado, um número de
páginas, e uma assimetria entre duas superfícies que passa a estar declarada.

⚠️ **E o padrão dos achados é o que interessa levar para a defesa.** Três dos quatro foram
introduzidos **hoje**, pelo trabalho de melhoria — e o quarto é a porta que devia tê-los
apanhado. É a demonstração exata do custo que este projeto já tinha escrito: **cada alteração
num documento verificado é uma oportunidade de introduzir um defeito**, e as portas só
protegem enquanto alguém as puser à prova.

A porta que falhou tinha três rondas de correção documentadas no próprio cabeçalho e um teste
de sabotagem que ela passara. Não bastou. O que a apanhou foi voltar a sabotá-la de propósito.

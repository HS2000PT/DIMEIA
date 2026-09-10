# Prompt para a reescrita final da dissertação

> Escrito a 2026-09-10 para ser entregue a um agente com acesso a este repositório.
> Copia tudo a partir da linha `---` abaixo.

---

# Tarefa: reescrever, do zero e com cuidado, a versão final de uma dissertação de mestrado

És um coorientador exigente e um editor científico. Vais reescrever uma dissertação que **já
tem todos os resultados medidos e verificados**, mas cujo texto cresceu por acumulação ao longo
de sessenta e oito sessões de trabalho e está hoje desarrumado: 57 383 palavras contra as
~34 000 que o plano fixava, 141 páginas, redundâncias identificadas e não tratadas, figuras com
sobreposições, e trabalho antigo misturado com trabalho novo.

**A tua tarefa não é produzir resultados novos.** É produzir um documento linear, consistente e
curto a partir de resultados que existem, estão fixados em artefactos versionados e não se
tocam. Mais os slides.

## 0. A regra que manda sobre todas as outras

**Nunca inventes um número, uma citação ou uma afirmação.** Cada número do texto tem de existir
num ficheiro de `docs/evaluation/` ou num manifesto de `docs/design/`. Se um número que queres
escrever não existe lá, ou o encontras lá, ou não o escreves. Há verificadores que confirmam isto
e falham a entrega se não bater.

Se em algum momento não souberes o valor de algo, **procura-o no repositório**; se não estiver lá,
**escreve que não está medido** em vez de estimar.

## 1. O que é o trabalho

Sistema de alertas financeiros explicáveis para investidores particulares, chamado
**InvestiGator**, construído só com APIs gratuitas, mercado dos Estados Unidos, e com uma
restrição fundadora: **o sistema nunca prevê preços**. Explica o que já aconteceu e mostra a
evidência ao lado da afirmação, para que quem lê possa conferir.

Duas perguntas que o sistema responde ao utilizador: *este movimento é invulgar?* e *já aconteceu
antes, e o que se seguiu?* Uma terceira, *foi a empresa ou foi o mercado?*, é respondida por uma
técnica que o documento descreve mas que não dá origem a questão de investigação, porque a
repartição de um movimento não tem valor de referência observável.

Título fixado, a submeter tal como está:
**«Explicar sem prever: deteção de anomalias e recuperação de precedentes em alertas financeiros
verificáveis»** · EN: *Explaining without predicting: anomaly detection and precedent retrieval
for verifiable financial alerts*.

## 2. As quatro questões e as respostas, com os números que as sustentam

Todos estes valores estão nos artefactos. Confirma-os lá antes de os escrever; não confies nesta
lista se ela divergir do artefacto.

**QI1 · deteção — resposta SIM.** Um *z*-score sobre janela deslizante deteta movimentos
invulgares de forma consistente entre empresas. Amplitude da taxa de disparo `0,015` contra
`0,344` de um limiar fixo de três por cento; `F1` de `0,530` contra `0,269` do Isolation Forest e
`0,280` do Local Outlier Factor. Duas comparações não favorecem a opção implantada e são
reportadas como escolha e não como resultado: a janela de sessenta dias dá `F1 0,678` contra
`0,516` da de vinte, e o desvio com decaimento exponencial dá `0,664` contra `0,516`.

**QI2 · precedentes — resposta SIM.** Medição principal sobre um subconjunto **equilibrado por
setor**, `569` notícias de cada um dos cinco, `2 845` no total, extraído de `18 599` recolhidas.
Precisão@5: MiniLM `0,395`, MPNet `0,422`, lexical `0,196`, recência `0,204`, acaso `0,117`,
estratégia trivial *devolver sempre tecnologia* `0,200`. Por setor, com o acaso ao lado: energia
`0,589` (`0,110`), saúde `0,468` (`0,111`), tecnologia `0,389` (`0,168`), banca `0,322` (`0,100`),
consumo `0,224` (`0,100`). Sensibilidade à composição: no corpus completo, `84%` tecnologia, a
estratégia trivial vale `0,840` e **ultrapassa qualquer método** — é essa a razão de a medição
principal usar o equilibrado. À escala, sobre o FNSPID: `0,595` no protocolo simétrico com acaso
`0,333`, e `0,513` exigindo anterioridade com acaso `0,259`. BM25 dá `0,521`. Concordância de
direção entre consulta e precedente `0,708` contra um acaso de `0,688` — **o tema recupera-se, a
direção não**, e é essa ressalva que o alerta declara.

**QI3 · triagem — resposta NÃO, e é o resultado com maior valor informativo.** PR-AUC: só
volatilidade `0,542` > contexto `0,538` > contexto+texto `0,496` > árvores `0,469` > só texto
`0,439` > alertar sempre `0,378`. Nenhum modelo com texto bate a volatilidade. O mecanismo vale
como ordenação: precisão dentro do orçamento diário `0,632` contra `0,379` do acaso real, ou seja
`1,67×`. Treze constantes por empresa dão `0,662`, acima do modelo implantado. O oráculo dá
`0,968`. Em produção, sobre `825` decisões maturadas que são `239` unidades independentes, a
capacidade de ordenação é `0,486` com intervalo `[0,403; 0,571]`, que contém o acaso.

**QI4 · comparabilidade — resposta NÃO, e é a contribuição nova.** Ajuste contrastivo do
codificador para aproximar notícias de magnitude comparável, com um braço treinado sobre a
magnitude e um de replicação treinado sobre a direção. Protocolo simétrico: sem ajuste
`2,173 ± 0,062` pp e precisão@5 `0,771 ± 0,011`; magnitude `2,185 ± 0,065` e `0,746 ± 0,009`;
direção `2,157 ± 0,071` e `0,744 ± 0,006`; acaso `2,259 ± 0,107` e `0,629 ± 0,007`. Protocolo
causal: `2,287`, `2,309`, `2,289` e `2,336`, com precisão@5 `0,747`, `0,722`, `0,720` e `0,621`,
e `2` de `2 500` consultas excluídas por não terem candidato anterior. **O ajuste não melhora a
comparabilidade e degrada a relevância temática.**

O que torna isto um resultado e não uma montagem falhada é o **diagnóstico de degeneração**, que
corre antes de qualquer métrica: cosseno médio entre títulos *diferentes* de `0,205` no modelo de
partida; a primeira tentativa, com pares ao acaso, deu `0,994` e foi descartada sem que as suas
métricas fossem lidas; os dois braços finais dão `0,271` e `0,277`, deslocaram o espaço `0,782` e
`0,775` face ao inicial e preservaram a geometria das semelhanças `0,607` e `0,630`. **O braço de
controlo, partindo de um codificador de domínio, colapsou** (`0,970`, geometria `0,281`) com a
mesma taxa que os outros toleraram, porque parte de um espaço já pouco disperso (`0,599` antes de
qualquer ajuste). O limiar de colapso é propriedade do modelo de partida e não da receita.

**Utilidade percebida (secção gerada, não escrita à mão):** `90` votos válidos, `51` efetivos de
`3` pessoas sobre `38` alertas, `50` de `51` úteis (`98%`, IC de Wilson `90%–100%`), com um
votante a representar `73%`. Não substitui o estudo controlado, que continua a ser a lacuna
declarada de maior peso.

## 3. Estrutura obrigatória

Seis capítulos, que são os do regulamento da MEIA/ISEP, mais um apêndice:

1. **Introdução** — problema, público, restrições fundadoras, as quatro questões, contribuições,
   estrutura.
2. **Estado da arte** — público-alvo com dados de 2025–2026, ferramentas existentes comparadas
   contra as três perguntas, e as áreas técnicas de onde vêm os componentes.
3. **Métodos e materiais** — dados e as técnicas, com o protocolo de cada avaliação fixado antes
   dos resultados.
4. **Implementação: InvestiGator** — arquitetura, o percurso de uma notícia da recolha à entrega,
   e as decisões de produto.
5. **Casos de estudo** — o desenho experimental e um caso por questão de investigação.
6. **Conclusões** — as respostas, as limitações, o trabalho futuro.
   **Apêndice A · Reprodutibilidade** — a matriz de evidência e como regenerar cada número.

## 4. Orçamento de páginas e de palavras, e não pode derrapar

O documento atual tem **141 páginas físicas** e termina no fólio `123`, com **57 383 palavras**.
As quatro dissertações aprovadas do mesmo mestrado, medidas nos PDF, têm 139/120, 133/114, 109/93
e 104/83 páginas físicas e fólio final. **A tese não está fora da norma, mas está no topo dela e
é mais longa do que precisa.**

Alvo: **≤ 120 páginas físicas** e **≤ 40 000 palavras**, distribuídas assim:

| capítulo | palavras hoje | alvo |
|---|---:|---:|
| 1 Introdução | 2 341 | 2 500 |
| 2 Estado da arte | 8 481 | 6 500 |
| 3 Métodos e materiais | 7 202 | 6 500 |
| 4 Implementação | 10 600 | 7 000 |
| 5 Casos de estudo | 17 678 | 12 000 |
| 6 Conclusões | 7 973 | 4 500 |
| Apêndice A | 3 108 | 2 000 |

**Onde cortar, em concreto** — está tudo levantado no `TASKS.md`, fase E: dezoito repetições
identificadas, entre elas o encolhimento de Vasicek explicado duas vezes, o objetivo de treino do
SBERT três vezes, «não é método novo, é seleção e integração» três vezes, a fadiga de alertas três
vezes, a dívida técnica quatro vezes, e «três ocasiões» três vezes. **A regra de corte: o que
sustenta um argumento fica; o que repete um visual ou outra secção sai.**

## 5. Regras de escrita, todas verificadas por máquina

- **Duas árvores, em sincronia total.** `tese-pt/` é a canónica em **PT-PT** e `tese-eng/` é a
  tradução em **EN-GB**. Mesma estrutura, mesmas figuras, mesmos números; muda só a língua.
  Qualquer alteração numa tem de ser espelhada na outra **na mesma passagem**.
- **Decimais:** vírgula em modo matemático no PT (`$0{,}395$`) e ponto no EN (`$0.395$`). Isto é
  verificado; um `0,395` na árvore inglesa falha a porta.
- **Zero travessões em prosa.** O `---` só é aceitável em célula de tabela a significar «não
  aplicável». Usa vírgulas, parênteses ou ponto e vírgula.
- **Um termo por conceito.** «título» e nunca «manchete»; «entradas» e nunca «features»;
  «lista vigiada» e nunca «watchlist». Há um verificador com estas listas.
- **Grafia pós-Acordo Ortográfico** («exatamente», não «exactamente»).
- **Sem primeira pessoa**, salvo na declaração de integridade, na dedicatória e nos
  agradecimentos.
- **Cada secção abre com prosa** e cada capítulo abre a dizer o que faz.
- **Nada de meta-comentário defensivo** («convém enunciar», «fica registado», «como se verá»).
- **Parágrafos densos e frases variadas em comprimento.** O documento anterior foi criticado por
  usar cem vezes a mesma figura de retórica («X, e não Y»); usa-a com parcimónia.

## 6. Figuras: gerar todas de novo, e o critério de aceitação

O utilizador reporta que as figuras atuais têm **setas e blocos a sobrepor-se**. Regenera-as
todas. Duas famílias:

- **Diagramas em TikZ**, escritos no `.tex`. Nestes, o defeito recorrente é `minimum width` ser um
  **piso e não um tecto**: uma caixa com texto mais largo cresce e come o espaço entre colunas.
  **Usa `text width`**, e nunca `minimum width`, em qualquer caixa com texto de comprimento
  variável.
- **Gráficos de dados**, gerados por `scripts/figures/*.py` a partir dos artefactos de
  `docs/evaluation/`. **Nunca escrevas um valor à mão num gráfico**: o gerador lê o artefacto,
  para que a figura e o texto não possam divergir.

**Critério de aceitação de cada figura, e verifica-o renderizando:**
1. Zero sobreposições entre texto, setas e caixas.
2. Zero palavras cortadas ao meio por hifenização.
3. Todos os rótulos legíveis à dimensão a que a figura aparece na página.
4. Uma só língua por figura, coerente com a árvore (as legendas são prosa do documento; os
   gráficos de dados podem ficar em inglês nas duas árvores, e isso está decidido).
5. Nenhum valor desenhado que não exista num artefacto.
6. Nenhum flutuante que nenhuma frase invoque.

⚠️ **O `exit code` do LaTeX não apanha composição.** Uma caixa que colide, um rótulo por cima de
uma seta, um zero riscado que se lê como nove, uma legenda que descreve a figura anterior — tudo
isto compila a zero erros. **Renderiza cada figura e olha para ela.**

## 7. Os slides

Dois decks, PT e EN, em Beamer, com **22 frames cada**, mais um guia de estudo de 25 slides em
PT-PT. Vinte minutos de apresentação, ou seja menos de um minuto por frame: não acrescentes
conteúdo, escolhe.

Estrutura que funciona: as três perguntas do investidor a abrir; o sistema; uma questão de
investigação por bloco com o resultado ao lado da alternativa medida contra ele; **a resposta
negativa apresentada com o mesmo destaque das afirmativas**; as limitações; e um frame final com
as perguntas do júri antecipadas.

**Os números dos slides são os que o autor decora para dizer em voz alta.** Há um verificador que
exige que todo o decimal dos slides tenha par na dissertação, precisamente porque um número que
ele estuda e a tese não imprime é um número que ele vai citar sem o poder mostrar. Corre-o.

## 8. Afirmações retiradas: não as ressuscites

Estes valores estiveram no documento e saíram, com razão escrita. Estão listados em
`docs/defence/LEIA-ME-PRIMEIRO.md` e há um verificador que os apanha. Os principais:

| não escrever | escrever | porquê |
|---|---|---|
| «quase 4×» na triagem | **1,67×** | o chão de `0,163` ordenava por ordem alfabética das empresas |
| precisão@5 `0,514` / `0,346` / `0,240` / `0,126` | **`0,395` / `0,196` / `0,117` / `0,204`** | a janela declarada do corpus não era a recolhida |
| chão trivial `0,467` | **`0,200`** no equilibrado, **`0,840`** no completo | era a proporção de *empresas* por setor, artefacto de um tecto da API |
| FinBERT `0,420` | **`0,275`** | mesmo veredicto, corpus novo |
| «84% das decisões» | **48% dos títulos distintos** | contar decisões infla a fração na direção que convinha |
| «terminais profissionais custam milhares por ano» | «o preço não é publicado de forma citável» | é a indisponibilidade que sustenta o argumento, não um valor |
| «a triagem funciona em produção» | «em produção não mostra benefício» | o intervalo contém o acaso |

## 9. Armadilhas do ambiente que custaram tempo real

Estas não são teóricas. Cada uma já produziu um defeito neste projeto.

1. **O PDF fresco está em `build/`.** O `tese-pt/main.pdf` na raiz é um artefacto versionado que
   envelhece. Qualquer verificação sobre o PDF lê-se de `tese-pt/build/main.pdf`; o da raiz só é
   verdade imediatamente depois de alguém o copiar de lá.
2. **O `latexmk` devolve `0` sem recompilar** quando a base de dados dele já descreve a versão em
   disco. Confirma pela contagem de páginas, nunca pelo `exit code`. `latexmk -gg` força.
3. **A extração de texto de um PDF perde as ligaturas** `fi` e `fl`: «falsificação» sai
   «falsicação» e uma procura por ela devolve zero. Procura ortografia no `.tex` e usa o PDF só
   para composição.
4. **`chapter3.tex` usa LF e `chapter5.tex` usa CRLF.** Deteta o final de linha de cada ficheiro e
   preserva-o, ou reescreves o ficheiro inteiro.
5. **Não geres LaTeX por `heredoc` nem por `python -c`.** O shell come um nível de barras
   invertidas mesmo entre plicas: `\\textbf` colapsa para `\textbf` e o Python lê então o `\t`
   como TAB, o que já pôs **`extbf` impresso no PDF a compilar com zero erros**. Escreve o script
   num ficheiro.
6. **Um `%` não escapado dentro de um número** apaga o resto da linha.
7. **Não escrevas por cima de artefacto congelado.** Os scripts de avaliação têm `--out`,
   `--fig`, `--figuras-dir` e `--modelos-dir`; usa-os em qualquer verificação. Já aconteceu uma
   re-corrida apagar vinte e três linhas de evidência com `exit 0` e sem um aviso.
8. **Ambiente:** corre sempre pelo `.venv` (Python 3.12), nunca pelo Python global.

## 10. As portas que têm de ficar verdes

Corre e deixa a zero, e não afrouxes nenhuma para a fazer passar:

```
python scripts/check_entrega.py      # corre tudo de uma vez; e' o comando final
python -m pytest                     # 1174 testes
python -m ruff check .
python scripts/_compilar.py          # as duas arvores, 0 erros, 0 refs por resolver
```

⚠️ **Um critério corrigido em silêncio é indistinguível de um critério contornado.** Se
concluíres que um verificador está errado, corrige-o **com a razão escrita no próprio ficheiro** e
com um teste que falhe sem a correção. Se relaxares uma tolerância, diz porquê no teste.

⚠️ **E um verificador que grita de mais deixa de ser lido.** Se acrescentares uma verificação,
planta o defeito que ela deve apanhar e confirma que dispara, **e** confirma que um corpus limpo
não a faz disparar. Este projeto já pagou as duas metades.

## 11. Onde está a verdade

| o que precisas | onde está |
|---|---|
| todos os resultados medidos | `docs/evaluation/*.md`, um ficheiro por experiência |
| os corpora e os preços, fixados | `docs/design/*_manifest.json`, com `sha256` |
| o plano-mestre e as 82 tarefas abertas | `TASKS.md` |
| o estado de retoma e as armadilhas | `ESTADO_ATUAL.md` |
| a história das decisões, sessão a sessão | `CLAUDE.md` e `AGENTS.md` |
| o que só o autor pode fazer | `docs/design/TAREFAS_MANUAIS_HENRIQUE.md` |
| os números retirados | `docs/defence/LEIA-ME-PRIMEIRO.md` |
| as quatro dissertações aprovadas, para calibrar | `archive/thesis-versions/thesis-examples/` |

## 12. O plano que te peço, e a ordem

Não comeces a escrever. **Primeiro entrega-me um plano** e espera que eu o aprove.

O plano tem de trazer, para cada capítulo: o argumento em uma frase, as secções, os visuais com o
que cada um mostra, os números que vai citar com a origem ao lado, e o orçamento de palavras. E
tem de dizer explicitamente **o que sai** do documento atual e porquê.

Depois, e só depois, executa por esta ordem, parando no fim de cada passo para eu confirmar:

1. **Métodos e materiais** (Cap. 3) — porque fixa o vocabulário e os protocolos de que tudo
   depende.
2. **Casos de estudo** (Cap. 5) — é o capítulo maior e o que carrega os resultados.
3. **Implementação** (Cap. 4).
4. **Estado da arte** (Cap. 2).
5. **Introdução e Conclusões** (Cap. 1 e 6) — no fim, porque prometem e resumem o resto.
6. **Apêndice** e a matriz de evidência.
7. **Figuras**, regeneradas e inspecionadas uma a uma.
8. **A tradução inglesa**, capítulo a capítulo, com a paridade verificada.
9. **Os slides e o guia.**
10. **A releitura integral**, primeiro em papel de orientador e depois em papel de arguente
    hostil, com o relatório de cada uma.

## 13. Três coisas que só o autor pode fechar, e que não deves inventar

1. Os **nomes do júri** na folha de rosto ficam como marcadores; o ISEP designa-os depois da
   submissão, e a dissertação aprovada do corpus foi depositada assim.
2. Os **agradecimentos** e a **dedicatória** são voz dele. Escreve um rascunho se ele pedir, e
   diz que é rascunho.
3. A **declaração de uso de ferramentas de inteligência artificial** existe e é honesta. Não a
   suavizes, não a apagues, e não afirmes que a redação exigida foi confirmada com o orientador
   se não foi.

E não escrevas que houve participantes num estudo que não correu. O documento declara essa lacuna
como a de maior peso; contradizê-la nos agradecimentos seria o pior defeito possível.

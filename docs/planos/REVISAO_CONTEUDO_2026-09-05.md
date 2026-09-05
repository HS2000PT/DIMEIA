# Revisão de conteúdo, capítulo a capítulo — 2026-09-05

> Pedida pelo autor: *«reveres agora a tese do início ao fim, e focando-te desta vez no
> conteúdo mesmo»*, **antes** da tradução. Os achados são escritos **à medida que aparecem**,
> para a revisão sobreviver a um reinício de sessão e uma sessão nova pegar onde esta parar.

**Ordem de leitura:** Cap. 4 (sistema) → Cap. 5 (resultados) → Cap. 3 (métodos) → Cap. 6
(conclusões) → Cap. 2 → Cap. 1 → frontmatter. Os capítulos que descrevem o que o sistema
**faz hoje** vêm primeiro, porque é aí que uma afirmação desactualizada se esconde.

---

## Estado

| capítulo | lido | achados | corrigidos |
|---|---|---|---|
| 4 | integral | 3 | 3 |
| 5 | resultados, produção, deriva, ablação, síntese | 2 | 2 |
| 6 | integral | 3 | 3 |
| 3 | triagem, ética, declaração de IA | 0 | — |
| 2 | ferramentas, incerteza, deriva | 0 | — |
| 1 | integral | 0 | — |

**Oito achados, oito corrigidos. Três eram meus, de ontem.** E dois falsos alarmes meus,
apanhados antes de reportar.

**Por ler em detalhe** (o mais provável sítio para o que falta): Cap. 5 §5.1 desenho e
métricas, §5.2 deteção e §5.5 decomposição; Cap. 3 metodologia, dados, deteção,
decomposição e recuperação; Cap. 2 na íntegra.

---

## Achados

### C4-1 — A figura do ciclo de vida estava metade em cada língua, e uma caixa a meio de uma tradução

`fig:sis_lifecycle`, `tese-pt/ch4/chapter4.tex`. Rótulos **desenhados**:
`labelled dataset`, `training`, `log of every decision` em inglês, ao lado de
`artefacto versionado`, `teste`, `retreino: ausente` em português — e uma caixa
**a meio de uma substituição**: `the `**`mesmo`**` model, in production`.

É a mesma classe do `declará-claradas` da sessão 61: **compila a zero erros**, porque é
texto válido, e só se vê a ler o que está desenhado.

⚠️ **E o `check_figuras_lingua.py` estava CALADO sobre ela**, tendo sido escrito ontem
exactamente para esta classe. A causa é estrutural e vale mais do que o defeito: o
verificador exige encontrar as **duas** línguas, e o lado português é uma **lista fechada**
de vocabulário. Nenhuma das palavras desta figura — `artefacto`, `versionado`, `teste`,
`mesmo`, `retreino`, `ausente` — estava na lista, logo a figura contava como
monolingue inglesa. **Um verificador cego e um corpus limpo são indistinguíveis no ecrã**,
que é a lição que a sessão 63 já tinha pago no `check_tese_numeros`.

**Corrigido nos dois sítios**, e a correcção do verificador foi verificada com a figura
original plantada.

**E a correcção do verificador encontrou logo uma segunda:** `fig:av_rotulos`, no Cap. 5,
tinha `célula usada` desenhada sobre um eixo rotulado `horizon (days)`. Só apareceu por
causa do sinal novo, que **não depende de vocabulário nenhum** — a ortografia portuguesa
(`ç`, `ã`, acentos) num rótulo desenhado. Uma lista fechada nunca a teria apanhado.

**Controlo:** com o rótulo original replantado, o verificador dispara e nomeia a figura.

### C5-1 — E a mesma classe tinha **três** cegueiras no verificador, não uma

Ao corrigir a lista fechada apareceu `fig:av_rotulos`. Ao ler a secção da deriva apareceu
`fig:av_deriva`, que o verificador continuava a não ver **por duas razões independentes**:

1. **`\gls{}` dentro de um rótulo de eixo.** O padrão era `\{([^{}]+)\}`, que para na
   primeira chaveta interior: `xlabel={\gls{PSI} entre o bloco de treino e o de teste}`
   **não casava de todo**, logo um eixo em português ao lado de escalas inglesas passava.
2. **Os rótulos de escala nunca eram olhados.** `xticklabels` e `yticklabels` são texto
   **desenhado** e não constavam do padrão. A figura da deriva tem
   `5-day momentum, Same-day return, Headline length` desenhados à esquerda, e era esse o
   lado inglês da mistura — invisível ao verificador.

**Três figuras corrigidas** (`fig:sis_lifecycle`, `fig:av_rotulos`, `fig:av_deriva`) e
três defeitos do verificador, cada um encontrado só depois de o anterior ser corrigido.
**A lição não é a lista: é que um verificador que só olha para parte do que é desenhado
dá a mesma saída de um corpus limpo.**

### C5-2 — Verificado e **não** é defeito: as três empresas fora do corpus de treino

`ch5:1385` afirma que a AMD, a Netflix e a Meta não figuram no corpus de treino. O registo
do projeto nomeava só duas (sessão 61). Conferido: são coisas diferentes — a sessão 61
tratava do mapa de setores (`SECTORS`), onde a Meta **está** e as outras duas não; o
corpus indexa a Meta como `FB`, pelo que sob o símbolo `META` está mesmo ausente
(`docs/evaluation/kb_fnspid_build.md`). **As duas afirmações são compatíveis.** Fica
registado para ninguém voltar a gastar tempo aqui.

### C4-2 — A prosa prometia **quatro** pontos de decisão e a figura desenha **cinco**

`ch4:220`, imediatamente antes da `fig:sis_caminho`. As caixas a tracejado são cinco —
*nomeia a empresa*, *é recente*, *evidência suficiente*, *triagem acima do piso*, *já
enviada hoje* — e o exemplo trabalhado que se segue atravessa as cinco, uma a uma.

É a classe que já mordeu duas vezes (a legenda das cinco portas na sessão 61, a contagem
das ocasiões na 63), e incide sobre **o núcleo do trabalho**: os pontos de decisão são o
que a dissertação tem de próprio. Corrigido para cinco.

**Verificadas e certas**, na mesma varredura: as cinco componentes do sistema, as nove
etapas, as sete entradas de nível de empresa em nove, as três causas do atraso, as três
leituras da ablação, as duas razões da janela, as duas precisões da predição conforme e
as duas propriedades da decomposição. O varrimento das promessas de contagem devolveu
**70 candidatas e um único defeito.**

### C6-1 — O Cap. 6 abria a citar a janela que o Cap. 5 declara **superseda**

`ch6:15`. O primeiro parágrafo que descreve o registo operacional do sistema dizia
«registadas $4\,366$ decisões de triagem», e o Cap. 5, para o qual remete, chama a essa
janela **«anterior e mais curta»** e reporta $36\,925$ como a medição principal. O
capítulo que resume estava a citar o número que o capítulo resumido substituiu — por um
fator de oito, e para baixo.

⚠️ **E as duas contagens da mesma frase são de janelas diferentes**, que é a forma exacta
do defeito da Figura 4.3: as $367$ mensagens são de 9 de julho a 13 de agosto e as
decisões de uma janela mais ampla. A frase passa a **datar as mensagens e a dizer que a
outra janela é mais ampla**, em vez de as apresentar como um par.

### C6-2 — «as seis peças» contra as **sete** que o Cap. 4 enumera

`ch6:30` remete para a `sec:sis_ciclo` e conta seis; a secção diz «sete componentes» e tem
sete `\item`. A que faltava é **a declaração do rótulo como decisão** — a peça que sustenta
a terceira verificação da QI3, e das mais defensáveis do conjunto. Acrescentada.

### Método — dois falsos alarmes meus, os dois apanhados antes de reportar

1. A legenda da figura dos rótulos promete «faixa verde» e eu vi só uma anotação de texto.
   **Existe**: `\path[fill=igGreenLight] rectangle`, no mesmo bloco.
2. Julguei uma frase da QI3 partida a meio e sem citação. **O meu próprio filtro de
   leitura** (`grep -v` de linhas começadas por barra) apagava a linha do `\autocite`, que
   levava as duas citações e metade da frase. **Ler a prosa em bruto, não filtrada.**

### C6-3 — O parágrafo da latência contradizia-se a si próprio em duas linhas

`ch6:432` afirmava a negrito que **«a sua causa não está identificada»** e a frase seguinte
diz **«Restam três causas que o histórico não separa»**. A tabela de limitações repetia a
primeira versão. O Cap. 4 identifica as três, nomeia-as e mede uma delas com um exemplo.

O que é verdade é que estão **identificadas e não separadas**, e a diferença não é de
estilo: «não identificada» convida à pergunta *então investigaram?*, e a resposta é que
sim. Corrigido nos dois sítios.

**Cap. 6 verificado e certo no resto:** os quatro objetivos batem um a um com os quatro do
Cap. 1 (e as três QI também); o item 1 do trabalho futuro remete para o «terceiro item
desta lista» e o terceiro é mesmo o do julgamento humano; a distinção entre utilidade
percebida e decisão melhor está feita nos dois sítios.

### C4-3 — ⚠️ O achado maior desta passagem é **meu**: os números da figura das razões vinham de um registo que rola

A figura que acrescentei ontem imprimia `98,0%` para o orçamento, `0,1%` para o limiar de
semelhança e `1,1%` para a repetição. **Três defeitos, e o terceiro é o pior:**

1. **Vinham de uma leitura única de um registo que guarda três dias.** Medido em seis dias
   — 19 a 21 de agosto e 3 a 5 de setembro — o que o orçamento elimina vai de **77,7% a
   99,8%**, e a repetição de **0% a 14,0%**. Imprimir `98,0%` como se fosse uma propriedade
   do sistema é o mesmo erro que a própria Figura 4.3 existia para corrigir, cometido por
   mim no dia seguinte.
2. **Não tinham fonte em `docs/evaluation/`**, contra a regra do projeto, e por isso o
   `check_tese_numeros` deixava-os passar **sem os ver** — 55/55 batia certo enquanto quatro
   números sem origem estavam impressos.
3. **Escrevi que o piso escalonado «deixou de vetar». É falso.** O código aplica-o ao
   segundo alerta da mesma empresa no mesmo dia (`run_alerts.py:457`), e o comentário do
   `config/alerts.yaml` di-lo. O que é verdade é que **nunca atuou** nos seis dias, porque o
   orçamento se esgota antes de uma empresa alcançar um segundo alerta. São afirmações
   diferentes: uma diz que o mecanismo foi desligado, a outra que não chega a ser alcançado.

**⚠️ E corrigi-lo destapou o mesmo defeito no gerador.** O `snapshot_funil.py` **reescrevia
o ficheiro inteiro**: corrê-lo hoje apagava os três dias de agosto e a amplitude deixaria de
existir. É a classe que a sessão 57 documentou **duas vezes** — um artefacto regenerável
regenerado noutro dia é indistinguível de um correcto. Passa a **acumular**: cada dia entra
quando o comando corre e nunca é retirado, e o ficheiro diz quantos dias tem.

**Corrigido:** a coluna passa a amplitude com a janela nomeada; a legenda diz que a unidade
é a **avaliação** e não a notícia; os quatro números entraram no manifesto (55 → 59); e a
legenda curta dizia «As sete regras» com nove filas.

**Controlo:** os três defeitos de figura replantados um a um, e o verificador dispara nos três.

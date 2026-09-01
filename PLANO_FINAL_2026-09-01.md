# PLANO FINAL — InvestiGator

> **PRIORIDADE MÁXIMA.** Este ficheiro manda sobre tudo o resto em `DIMEIA/`.
> Se algum outro documento (`INVESTIGATOR_MASTER_PLAN.md`, `CHECKLIST.md`, `REBUILD_MASTER.md`)
> disser outra coisa, este ganha.
>
> | | |
> |---|---|
> | Criado | 2026-09-01 |
> | Defesa | daqui a 16 a 30 dias (janela declarada pelo autor) |
> | Risco aceite | pode partir e reparar; o caminho de envio pode ser alterado diretamente |
> | Estado do documento | 90 páginas contadas de 120 permitidas · 0 erros · 3 portas de qualidade a passar |
> | Estado do sistema | em produção, worker de 60 s, 522 alertas entregues |

---

## 0. A decisão mais importante deste plano: a ordem não é a da lista

A lista original tem oito pontos. Executá-los por essa ordem perde a coisa mais valiosa do
conjunto.

O ponto 3 — feedback real de utilizadores no Telegram — é o único item cujo valor **depende de
tempo de calendário e não de tempo de trabalho**. Construir o mecanismo leva um dia. Recolher
respostas suficientes para dizer alguma coisa leva duas a três semanas, e essas semanas são
exatamente as que faltam. Cada dia que o mecanismo não está no ar é um dia de dados que não
existe na defesa.

Tudo o resto — painel, logótipo, figuras, escrita, citações, slides — é trabalho que se faz
quando se senta a fazê-lo, e que não fica melhor por começar mais cedo.

Por isso a ordem de execução é:

| Ordem | Ponto original | Porquê nesta posição |
|---|---|---|
| **1.º** | 3 + 4 (Telegram) | Abrem a janela de recolha. Dia perdido é dado perdido. |
| **2.º** | 1 + 2 (painel e marca) | As capturas de ecrã do Capítulo 4 têm de ser tiradas depois. |
| **3.º** | 5 (artefactos visuais) | O maior bloco de trabalho, e corre em paralelo com a recolha. |
| **4.º** | 6 + 7 (escrita, citações) | Operam sobre texto final. Fazê-los antes obriga a repeti-los. |
| **5.º** | 8 (slides e guia) | Depende de tudo estar fechado. |
| **Último dia** | fecho | Recontagem de páginas, recompilação limpa, verificação de entrega. |

---

## 1. Telegram — feedback bidirecional  *(ponto 3 · ✅ NO AR desde 2026-09-01, release v51)*

### O que já existe, e que muda o custo disto

O trabalho está quase todo feito e não estava a ser aproveitado:

| Peça | Ficheiro | Estado |
|---|---|---|
| Envio | `investigator/telegram_bot/sender.py` | Devolve o JSON do Telegram, incluindo o `message_id`. |
| Receção | `investigator/telegram_bot/interactive.py` | Já tem `getUpdates` em long-polling, com `offset` e recuperação de falhas. |
| Persistência | `investigator/telegram_bot/store.py` | SQLite da biblioteca padrão, já com esquema e migração. |
| Interpretação | `investigator/telegram_bot/commands.py` | Pura e testável, separada da rede. |

Falta o botão, o `callback_query`, e uma tabela.

### O problema operacional, que é o verdadeiro risco

O poller corre na máquina do aluno (`python scripts/run_bot.py`). Uma recolha de três semanas
não pode depender de um portátil ligado. O sistema já tem a solução instalada e não a usa: o
`api/main.py` é um serviço FastAPI com URL público e HTTPS no Heroku, servido pelo `Procfile`.

**Decisão: passar de long-polling para webhook, apontado ao `api/main.py`.** Sem dyno novo, sem
custo, sem portátil. O poller fica como caminho alternativo para desenvolvimento local.

### O que fazer

1. `sender.py` — aceitar `reply_markup` e devolver `message_id` e `chat_id` de forma tipada.
2. Anexar a cada alerta um teclado em linha de dois botões, com `callback_data` que carrega o
   identificador do alerta:
   `útil` / `não útil`. Duas opções e não cinco: uma escala de Likert num telemóvel tem
   taxa de resposta pior e não sustenta melhor análise com o N que vamos ter.
3. `POST /telegram/webhook` no `api/main.py`, com segredo no cabeçalho
   `X-Telegram-Bot-Api-Secret-Token`. Responder `answerCallbackQuery` em menos de um segundo,
   sempre, mesmo em erro — o Telegram reenvia o update se não houver resposta.
4. Tabela `feedback` no `store.py`: `alert_id`, `chat_id` com dispersão criptográfica,
   `voto`, `timestamp`, `message_id`. **O `chat_id` nunca é gravado em claro** — o que a análise
   precisa é de distinguir pessoas, não de as identificar.
5. Editar a mensagem depois do voto para mostrar a contagem. Um botão que não muda nada depois
   de premido é lido como avariado, e deixa de ser premido.
6. Escrever o consentimento: mensagem fixada no canal a dizer o que é recolhido, para quê, e
   como se apaga. Comando `/apagar` que remove os votos de quem o pedir.

### O que isto vale para a tese, e o que não vale

Vale: o Capítulo 6 declara hoje, como limitação, que a hipótese fundadora — a de que uma
explicação verificável conduz a melhor decisão — **não foi testada**. Isto não a testa. Testa
uma coisa mais modesta e ainda assim nova no documento: se os alertas que o sistema decide
enviar são considerados úteis por quem os recebe, e se a utilidade percebida se correlaciona com
a pontuação de triagem que o modelo lhes deu. Essa segunda pergunta é a interessante, porque
liga uma medida interna a um juízo externo, que é precisamente a ponte que falta no trabalho.

Não vale: com um canal pequeno e três semanas, o N vai ser de dezenas de votos, não de milhares.
**O plano é reportar o N exato, o intervalo de confiança, e dizer que é um piloto.** Um piloto
honesto com N=40 é defensável. Um piloto apresentado como estudo não é, e um júri que faça essa
pergunta desmonta a tese inteira em dois minutos.

### Critério de aceitação

- Um voto dado no telemóvel aparece na base em menos de dois segundos.
- O webhook sobrevive a um alerta apagado, a um voto repetido e a um `callback_data` inválido.
- Testes: `extract_callback` puro, com o JSON exato que a API devolve.
- A mensagem fixada do canal explica a recolha antes de o primeiro botão existir.

**Esforço:** 1,5 dias. **Risco:** médio; toca no caminho de envio.

---

## 2. Telegram — alerta imediato, contexto por edição  *(ponto 4)*

### A ideia é boa. A justificação que parece óbvia está errada, e é preciso saber disso antes da defesa

A leitura natural é «isto torna os alertas mais rápidos». Os números do próprio Capítulo 4
dizem que não:

| Troço | Mediana | Percentil 90 |
|---|---|---|
| Publicação → deteção pela fonte gratuita | **353 min** | — |
| Deteção → chegada da mensagem | **5 s** | 16 s |

O sistema já entrega em cinco segundos o que a fonte lhe dá. Enviar primeiro e editar depois
poupa, na melhor das hipóteses, esses cinco segundos. **Não toca nos 353 minutos**, que são da
fonte e não do sistema. Se isto for apresentado ao júri como resposta ao problema da latência, a
primeira pergunta desfaz o argumento.

### O que a ideia vale de facto — e é mais do que latência

Há três razões reais, e a terceira é a melhor:

1. **Divulgação progressiva.** O alerta passa a ter dois estados visíveis: *detetado* e
   *investigado*. O utilizador vê o sistema a trabalhar, e o próprio nome do produto passa a
   descrever o comportamento em vez de o prometer.

2. **Desbloqueia a recuperação de precedentes no caminho quente.** Hoje a recuperação semântica
   está fora do painel porque custa cerca de sete segundos a carregar a frio, e essa medição está
   documentada. Com a mensagem já entregue, esses sete segundos deixam de estar no caminho
   crítico. Uma restrição de desenho que a tese declara passa a estar levantada.

3. **A mensagem original passa a poder ser anotada com o que aconteceu depois.** Ao fim de um,
   três e cinco dias, a própria mensagem que fez a afirmação é editada com o desfecho observado.
   O alerta deixa de ser uma afirmação e passa a ser uma afirmação com o seu registo anexado, no
   sítio onde foi feita, visível a quem a leu.

O ponto 3 é a contribuição. Um sistema explicável que se corrige em público, na mensagem
original, é uma coisa que a tese pode reivindicar e que nenhum dos produtos comparados no
Capítulo 2 faz.

### O que fazer

1. Dividir o construtor da mensagem em duas partes: `esboço` (empresa, movimento, manchete,
   raridade) e `completa` (esboço + repartição + precedentes + desfechos).
2. Enviar o esboço com uma marca de estado explícita. Não usar linguagem que sugira previsão.
3. Guardar `message_id` na base, indexado pelo identificador do alerta.
4. `editMessageText` quando a análise fechar. Tratar os erros próprios da API: `message is not
   modified` é sucesso, e `message to edit not found` significa apagada e nunca é fatal.
5. Trabalho agendado, uma vez por dia, que edita as mensagens de há um, três e cinco dias com o
   desfecho observado — e com a mesma advertência que o texto atual já traz, a de que semelhante
   no assunto não é semelhante na direção.
6. Registar no `alerts_history` o texto **de cada versão**, com a hora. O painel lê desse
   registo, e o painel e o canal não podem discordar.

### Critério de aceitação

- O esboço chega antes da análise, medido, com as duas horas registadas.
- Uma mensagem apagada pelo utilizador não parte o ciclo.
- O painel mostra a última versão e permite ver as anteriores.
- Uma edição de desfecho nunca altera a afirmação original: acrescenta.

**Esforço:** 2 dias. **Risco:** médio-alto; é o caminho de envio.

**No documento:** subsecção nova no Capítulo 4, com a medição das duas latências lado a lado e a
declaração explícita de que o ganho é de segundos e que a contribuição é outra. O Capítulo 6
retira da lista de trabalho futuro o que passar a estar feito.

---

## 3. Painel — tirar o ruído  *(ponto 1)*

### O que está no ar

`web/index.html`, versão 6.1, 790 linhas, servido por `api/main.py`. Não é nenhum dos ficheiros
Streamlit — `app/dashboard_v4.py` e `app/streamlit_app.py` são versões anteriores mantidas como
registo da evolução do produto, e a tese discute-as no Capítulo 4.

A página tem três zonas. As duas de cima estão bem. A de baixo é o problema.

### Diagnóstico da zona de baixo — «Why it stayed quiet»

Onze etapas de funil, cada uma com título, contagem, uma frase de explicação em prosa, e uma
lista de fichas por empresa. Ocupa mais ecrã do que o gráfico e a lista de alertas juntos, e é a
última coisa que qualquer visitante vê.

O conteúdo é bom e é uma das posições éticas do trabalho: o silêncio é uma decisão e deve ser
inspecionável. **A informação não sai; sai a forma.** Ela hoje é uma parede de prosa que ninguém
lê, e uma parede de prosa que ninguém lê não inspeciona nada.

### O que fazer

1. Substituir as onze secções por **uma barra de funil única**: doze empresas a entrar, e a
   perder altura em cada porta, com a etapa onde cada uma parou. Um gráfico. Ler-se num segundo.
2. A prosa de cada etapa passa a `title` e a painel lateral ao clicar. Continua lá, deixa de
   estar toda ao mesmo tempo no ecrã.
3. As fichas por empresa mantêm-se, mas ligadas à barra: clicar numa etapa filtra.
4. Uma linha de texto acima, e não três.
5. Rever o mesmo critério na zona de cima: os acordeões «full message as sent» são bons, ficam.

### O que não fazer

Não apagar a secção. Ela é o que distingue este produto dos que mostram só o que enviaram, e é
citada na tese. Reduzir a página ao que enviou seria, exatamente, o defeito que o Capítulo 2
aponta aos concorrentes.

### Critério de aceitação

- A zona de baixo cabe num ecrã de portátil sem rolar.
- Um leitor de ecrã continua a alcançar todas as etapas e todos os detalhes.
- Contraste verificado no navegador, não estimado. O ficheiro já tem um comentário a registar
  uma correção anterior de contraste, e essa medição não pode regredir.
- Capturas de ecrã novas para o Capítulo 4, a substituir `app_v6_empresa.png` e
  `app_v6_silencio.png`.

**Esforço:** 1,5 dias.

---

## 4. Marca — o retângulo, a cor, a peça única, o lema  *(ponto 2)*

### O retângulo tem uma causa, e é um defeito de CSS

Encontrado no `web/index.html`. Há duas regras chamadas `.nome`:

```
linha  85:  .marca .nome { font-weight:650; letter-spacing:-.015em; font-size:1.02rem; }
linha 251:  .nome { border:1px solid var(--linha); border-radius:5px; padding:2px 7px;
                    font-size:.79rem; background:var(--caixa); }
```

A da linha 251 foi escrita para as fichas de empresa do funil. A do cabeçalho não declara
`border`, `border-radius`, `padding` nem `background`, por isso herda-os da outra por cascata. O
nome da marca está dentro de uma ficha de empresa.

**Correção:** renomear a classe do funil para `.chip`. Uma linha em cada sítio. Não pôr
`border:none` no cabeçalho — isso tapa o defeito e deixa-o à espera do próximo caso.

### A cor

Hoje só o `G` é verde: `.marca .nome b { color:var(--acento) }`. O pedido é que o **Gator**
inteiro tenha cor.

Vale a pena separar duas coisas. `investiGATOR` a verde nas últimas cinco letras mantém o
trocadilho (*inveSTIGATE* + *alliGATOR*) e é mais legível de longe do que uma única letra.
`InvestiGator` todo verde perde o trocadilho por completo. A recomendação é a primeira, e a
decisão é tua — ficam as duas desenhadas para veres lado a lado antes de escolher.

### A peça única, que já foi pedida várias vezes

Existe `app/assets/logo-lockup.svg` com o glifo e o nome juntos. Não está a ser usado em lado
nenhum, e tem dois defeitos que o tornam inutilizável como entrega:

- O nome é `<text>` e não contornos. Numa máquina sem *Segoe UI* — que é o caso de qualquer
  impressora, de qualquer Mac e do próprio LaTeX — o desenho muda.
- Não tem a variante de cor pedida.

**Entrega:** um conjunto fechado, com o nome vetorizado, sem dependência de tipos de letra
instalados, e cada peça em claro, escuro e monocromático:

```
logo-lockup.svg          glifo + nome, horizontal        cabeçalhos, capa da tese
logo-lockup-tagline.svg  o anterior + lema               capa, primeiro slide
logo-empilhado.svg       glifo em cima, nome em baixo    avatar, quadrados
logo-marca.svg           só o glifo                      favicon, 16 px
logo-nome.svg            só o nome                       rodapés
```

E os PNG derivados a 512 px para o Telegram, gerados pelo procedimento que já está escrito em
`docs/design/telegram_channel.md`.

### O lema

O rodapé do painel já tem a frase que faz o trabalho todo:
*«Every move investigated, never predicted.»*

É boa: diz o que o produto faz, diz o que recusa fazer, e usa o nome. Está a ser tratada como
texto de rodapé e devia ser o lema. Proponho-a como principal, com versão portuguesa
*«Cada movimento investigado, nenhum previsto»*, e três alternativas desenhadas para escolheres.

### A hipótese de uma marca nova

Fica em aberto, com uma reserva. A cauda serrada que se lê como linha de mercado é uma boa ideia,
e o ficheiro `logo.svg` documenta que a marca anterior — um olho de crocodilo — foi rejeitada por
falhar a 16 px e por ler como predador. Redesenhar a fundo a três semanas da defesa arrisca
perder essa história por uma que não vai ter tempo de amadurecer. A proposta é: resolver o
retângulo, a cor, a peça única e o lema, e apresentar duas alternativas de marca como estudo. Se
alguma for claramente melhor, troca-se; se não, o que existe fica coerente.

**Esforço:** 1 dia para o defeito, a cor e o conjunto; mais meio dia para os estudos.

---

## 5. Artefactos visuais — revisão de um a um  *(ponto 5)*

### Inventário medido

| | Total | Composição |
|---|---|---|
| Figuras | **37** | 24 TikZ desenhado à mão · 16 pgfplots · 3 imagens importadas |
| Tabelas | **13** | todas nativas |

Por capítulo: ch1 tem 2, ch2 tem 2, ch3 tem 6, ch4 tem 8, ch5 tem 18, ch6 tem 1.

**O ch5 tem 18 das 37.** É aí que está a repetição de que te queixas: catorze gráficos pgfplots
consecutivos, quase todos barras horizontais a comparar duas ou três alternativas. A monotonia é
real e é medível. O ch6, com uma figura em vinte páginas de conclusões, tem o problema oposto.

### Sobre trocar de ferramenta — a resposta honesta, que não é a que esperas

Procurei o que está ligado a esta sessão: Figma, Canva, Gamma, Mermaid Chart. São bons e alguns
vão ser usados. Para a maioria destas figuras, seriam uma perda de qualidade, por três razões
concretas e verificáveis:

1. **Tipo de letra.** Uma figura vinda do Figma ou do Canva traz o tipo de letra dessa ferramenta.
   Ao lado de um corpo de texto em Computer Modern, lê-se imediatamente como colada. As figuras
   atuais herdam o tipo de letra do documento.
2. **Vetor e escala.** O pgfplots produz vetor com a mesma métrica do texto. Um PNG exportado a
   2x fica visivelmente pior numa impressão A4, e a tese vai ser impressa.
3. **Reprodutibilidade.** Os valores das figuras vêm de `docs/evaluation/*.md`. Um gráfico
   desenhado à mão numa ferramenta externa deixa de ter ligação ao ficheiro que o produziu, e a
   tese perde precisamente a propriedade que declara ter.

**O problema não é o motor de desenho. É o desenho.** Trocar de ferramenta sem mudar o desenho dá
os mesmos catorze gráficos de barras, com outro tipo de letra.

### O que fazer, então

**A. Fixar uma gramática visual, e aplicá-la a todas as 37.** Um ficheiro `figures/estilo.tex`,
carregado uma vez, com: uma paleta de três tons mais um de destaque; três espessuras de traço e
não sete; grelha só onde é preciso ler valores; eixos sem caixa; e a regra de que **o valor
implantado é sempre o tom cheio e a alternativa é sempre o tom claro**, em todo o documento. Hoje
essa correspondência muda de figura para figura, e é isso que obriga a reler a legenda de cada
vez.

**B. Mudar o tipo de gráfico onde o tipo está errado.** Barras horizontais são a escolha certa
para comparar categorias sem ordem. Não são a escolha certa para: uma sequência (janela de 10,
20 e 60 dias é uma escala, e pede uma linha), um compromisso entre duas medidas (pede dispersão),
uma distribuição (pede caixa ou tira), ou um antes-e-depois emparelhado (pede declive). Há pelo
menos seis figuras no ch5 onde o tipo está errado, e corrigi-lo resolve a monotonia sem
acrescentar nada.

**C. As legendas passam a dizer a leitura.** Uma legenda que diz «Comparação de F1 por janela»
obriga o leitor a descobrir sozinho. Uma que diz «A janela de sessenta dias obtém o melhor F1; a
de vinte foi mantida por responsividade» entrega a conclusão. Cerca de metade das legendas está
no primeiro tipo.

**D. Onde as ferramentas externas entram, e onde valem mesmo.** Nos diagramas conceptuais, em
que o valor é composição e não fidelidade a dados: a arquitetura do sistema, o funil de portas,
o ciclo de retreino, o percurso de um alerta de ponta a ponta. São quatro a seis figuras.
**Método: desenhar no Figma, exportar em PDF vetorial com o texto vetorizado, importar.** Antes
de comprometer as seis, faz-se **uma** e compara-se impressa ao lado da versão TikZ. Se não for
claramente melhor, não se faz.

**E. Acrescentar onde falta.** Candidatos: o ch6 tem uma figura em vinte páginas; a decomposição
de retorno do ch3 beneficia de um exemplo trabalhado com números reais; e a arquitetura nova do
Telegram do ponto 2 precisa de um diagrama de sequência.

### Orçamento de páginas — corrigido a 2026-09-01

⚠️ **Eu estava errado, e a correção liberta espaço.** O modelo oficial diz, no seu próprio
Capítulo 1: *«The minimum number of pages is 60 and the maximum is 120 (not counting the
Annexes). Small deviations are allowed.»* Os apêndices **não contam**, e a lista de verificação
do modelo confirma-o ao marcá-los como não obrigatórios.

A posição real, medida no PDF:

| | Páginas |
|---|---|
| Pré-textuais (numeração romana) | 24 físicas, i–xxiv |
| **Corpo + bibliografia (o que conta)** | **90** (impressas 1–90) |
| Apêndices A e B (não contam) | 8 (impressas 91–98) |
| Total físico do PDF | 122 |

**Contam 90 de 120.** Mesmo na leitura mais pessimista possível — todas as páginas físicas
menos os anexos — dá 114. Há folga real, e não zero.

O que isto muda: a Figura `fig:sis_seletividade`, que eu tinha removido do `ch4` só para poupar
duas páginas, **foi reposta**. As figuras novas desta frente entram sem terem de comprar espaço.
A regra de verificar `pdfinfo` antes de fechar uma sessão mantém-se, mas o número a vigiar é o
das páginas impressas do corpo, e não o total físico.

**Esforço:** 4 a 5 dias. É o maior bloco. Corre em paralelo com a recolha de feedback.

---

## 6. Tirar as desculpas, e a página da declaração de IA  *(ponto 6)*

### As desculpas, contadas

Uma varredura por padrões defensivos encontrou **18 ocorrências** em todo o documento:

| Padrão | N | Onde |
|---|---|---|
| «exigiria» / «teria exigido» | 8 | ch2, ch3, ch4, ch5, ch6 |
| «fica registado» / «regista-se que» | 4 | ch5, apêndices |
| «não permitiu» / «o impedimento» | 2 | ch4, ch6 |
| «não foi medido / testado» | 2 | ch5, apêndices |
| «não estava disponível» | 1 | ch4 |
| «convém notar» | 1 | ch6 |

Dezoito não é uma catástrofe, e o instinto está certo: quase todas dizem a mesma coisa duas
vezes. A regra a aplicar é simples e vale para as dezoito:

**Declarar o limite uma vez, no sítio onde ele condiciona a leitura, e nunca o pedir desculpa.**
«O retreino não foi executado; a arquitetura está definida na Secção X» é uma frase de engenheiro.
«O retreino não foi executado porque a avaliação dessa alteração exigiria tempo de observação que
não estava disponível» é a mesma informação com um pedido de desculpa colado. A segunda metade
convida o júri a perguntar por que motivo não havia tempo, o que é a pergunta que não queres.

### A página da declaração de IA — RESOLVIDO a 2026-09-01

O modelo MEIA em vigor (v2) chegou, e responde à pergunta de forma inequívoca. A Declaração de
Integridade oficial, em português, diz:

> «Portanto, o trabalho apresentado neste documento é original e de minha autoria, não tendo sido
> utilizado anteriormente para nenhum outro fim. As exceções estão explicitamente reconhecidas na
> secção onde são abordadas as considerações éticas. **Esta secção também declara como as
> ferramentas de Inteligência Artificial foram utilizadas e para que finalidade.**»

Ou seja: a declaração de uso de IA **não vive na página da Declaração de Integridade**. Vive na
secção de considerações éticas, dentro do corpo. A página assinada só lhe aponta, com uma frase.
Nenhuma das três hipóteses que eu tinha desenhado estava certa; a tua desconfiança estava.

**Já aplicado:**

- A Declaração de Integridade passa a ter a redação do modelo oficial, palavra por palavra,
  incluindo o período das exceções (que se aplica, e por isso fica). A versão anterior era uma
  reescrita nossa — sem ganho e com risco.
- A declaração de uso de IA saiu dessa página e passou a ser a Secção 3.8.4,
  `\subsection{Utilização de ferramentas de inteligência artificial}`, logo a seguir a
  «Questões éticas e sociais» (3.8.3). Aparece no índice, que é onde um júri a procura.
- A Declaração remete para as duas secções pelo número, resolvido pelo LaTeX.

**Ganho lateral: a lista de verificação do modelo.** Conferida linha a linha. Faltava a **Lista de
Símbolos**, marcada como obrigatória — está agora no fim dos pré-textuais, com vinte símbolos, cada
um com a equação ou secção onde é definido, o que a torna também um índice. A Lista de Código e a
Lista de Algoritmos continuam ausentes, e corretamente: o documento não tem nenhum dos dois, e o
próprio modelo manda remover esses comandos nesse caso.

**Ainda por fazer nesta frente:** as 18 desculpas contadas acima.

**Esforço:** meio dia. Já não há nada bloqueado por terceiros.

---

## 7. Escrita, citações e metadados  *(ponto 7)*

### Primeiro, a moldura, porque muda o que se faz

A tese **declara** o uso de ferramentas de IA. Isso já está feito e é a posição certa. Portanto o
objetivo aqui não é esconder nada — não há nada a esconder, e tentar escondê-lo depois de o ter
declarado seria incoerente e detetável.

O objetivo é outro, e é legítimo: **prosa que se lê como gerada é um defeito de qualidade**,
independentemente de quem a escreveu. Repete estruturas, prefere o contraste ao argumento, e
cansa. Um júri não precisa de um detetor para sentir isso; sente-o a ler. E os detetores, quando
correm, têm taxas de falso positivo altas o suficiente para não decidirem nada sozinhos.

A posição forte é esta: **declaração honesta mais prosa que se lê bem.** Qualquer das duas
sozinha é mais fraca.

### Os tiques, contados

Varredura sobre 42 197 palavras dos seis capítulos e dos apêndices:

| Padrão | N | Por mil palavras | Onde se concentra |
|---|---|---|---|
| «X, e não Y» (contraste) | **58** | 1,37 | ch5 com 15, ch6 com 12, ch2 com 11 |
| «uma vez que» | **43** | 1,02 | ch4 com 11, ch3 e ch5 com 10 |
| «precisamente» / «exatamente» | **28** | 0,66 | ch5 com 14 |
| «em vez de» | **21** | 0,50 | ch5 com 6, ch2 e ch6 com 5 |
| «não é X, mas Y» | **12** | 0,28 | ch5 com 7 |
| «ou seja» | 8 | 0,19 | ch2 |
| «o que significa que» | 3 | 0,07 | ch5 |

A estrutura de contraste — «isto, e não aquilo» — aparece cinquenta e oito vezes. É a assinatura
mais forte e é a que mais se sente na leitura: quando cada terceiro parágrafo define uma coisa
por oposição a outra, o texto começa a soar a fórmula, mesmo quando cada frase individual está
certa.

**Alvos:** «X, e não Y» abaixo de 20; «precisamente/exatamente» abaixo de 8; «uma vez que» abaixo
de 20, substituído por «porque» e por «já que», que são o que uma pessoa escreve. Nada disto se
faz com procurar-e-substituir: cada ocorrência é lida, e as que ganham o seu lugar ficam.

**Uma limitação a assumir:** as quatro dissertações de referência estão escritas em inglês, por
isso não servem de linha de base para tiques em português. Comparei-as e o resultado foi zero em
todos os padrões, o que não é um resultado — é uma incompatibilidade de língua. A linha de base
de comprimento de frase, que já mediste contra o Rafael, essa mantém-se válida.

### Cita\c{c}ões e bibliografia

Setenta entradas, zero pré-publicações do arXiv. Estado verificado:

- **11 entradas sem DOI**, e é preciso separá-las em duas: as que não podem ter (relatórios da
  SIFMA, sondagem Gallup, páginas de produto da Robinhood e do Google Finance, relatório CCAF,
  «World Monitor») e as que deviam ter e não têm — `vaswani2017attention`, `ding2015deep`,
  `manning2008ir`, `vinh2010ami`, `lewis2020rag`. Estas cinco resolvem-se num quarto de hora.
- **57 entradas sem URL.** Para artigos com DOI está correto e é o estilo. Para as fontes de
  produto e relatório é uma falha: são precisamente aquelas que o júri pode querer abrir.
- **Por verificar, uma a uma:** que cada DOI resolve, que cada URL abre, e que autor, título,
  ano e publicação de cada entrada batem certo com o que está do outro lado. É trabalho mecânico
  e é onde uma tese perde credibilidade de forma barata. Faz-se com um clique simulado em cada
  ligação, e o resultado fica numa tabela de verificação.

### Metadados

Já verificado, e está limpo: `Creator: LaTeX with hyperref`, `Producer: pdfTeX-1.40.25`, autor e
palavras-chave corretos. Nenhum vestígio de ferramenta em nenhum campo. Uma varredura pelos
ficheiros `.tex`, incluindo comentários, não encontrou uma única menção a nome de ferramenta.
Fica a repetir no fim, sobre o PDF final.

**Esforço:** 3 dias, dos quais 1 para a bibliografia.

---

## 8. Slides e guia de estudo — pacotes de contexto  *(ponto 8)*

Concordo com a leitura: para os slides e para o guia de estudo, as ferramentas externas são
melhores do que eu a escrever LaTeX Beamer. O que falta para as usar bem não é a ferramenta, é
o material de entrada.

O que preparo, e é a entrega deste ponto:

**1. Um dossiê único, `docs/defesa/DOSSIE.md`.** Autossuficiente, sem remissões, com: as três
questões de investigação e as respostas com os números; a arquitetura em texto; cada decisão
técnica com a alternativa medida contra ela; os resultados com intervalos; as limitações;
e o arco de seis tempos da narrativa. É o ficheiro que se dá ao NotebookLM e é o que se cola
num prompt.

**2. Prompts, um por ferramenta, escritos para o resultado que cada uma faz melhor:**

| Ferramenta | Para quê | O que o prompt tem de trazer |
|---|---|---|
| **NotebookLM** | Guia de estudo, perguntas do júri, resumo falado | O dossiê mais os seis capítulos em PDF; instruções para gerar as perguntas difíceis, incluindo as três em que o sistema perdeu |
| **Gamma** | Primeira versão dos slides, rápida | O arco de seis tempos, um tempo por secção, com a instrução de não inventar números |
| **Canva** | Acabamento visual, se o Gamma não chegar | A paleta e o conjunto do logótipo do ponto 4 |
| **Figma** | Os diagramas dos slides, partilhados com o ponto 5 | Os mesmos ficheiros; um diagrama serve os dois sítios |

**3. A estrutura dos slides, decidida antes de a ferramenta a decidir por nós.** Vinte minutos,
com o mesmo arco de seis tempos do guia de defesa, para que a apresentação e o estudo falem a
mesma língua. Regra fixa: nenhum número nos slides que não esteja na tese, e cada número com a
secção onde vive, para responder a «onde está isso» sem folhear.

**Aviso.** Nenhuma destas ferramentas pode inventar um número. O prompt di-lo, e mesmo assim é
preciso conferir slide a slide contra o dossiê. Um número errado num slide, apanhado pelo júri,
custa mais do que qualquer ganho de acabamento.

**Esforço:** 1 dia para o dossiê e os prompts. Os slides em si dependem de quanto tempo quiseres
gastar a afiná-los.

---

## 8.5. O «porquê?» em cadeia — a última passagem sobre o documento  *(mesmo no fim)*

Depois de tudo fechado, e só então, uma passagem final que percorre cada afirmação do documento
com a pergunta de uma criança curiosa: **porquê?** E à resposta, outra vez: porquê? Até chegar a
um número medido, a uma citação, a uma restrição declarada, ou a uma decisão assumida como
decisão.

**A razão de ser exatamente esta a técnica.** Um «porquê?» sem resposta no documento é um
«porquê?» que o júri vai fazer em voz alta. A lista dos porquês que morrem sem chegar a chão é,
literalmente, a lista das perguntas da defesa. Encontrá-los antes é a diferença entre responder e
descobrir.

**Como se faz, para não ser uma leitura vaga.** Cada afirmação do documento tem de aterrar numa
de quatro coisas, e a passagem classifica-a:

| Aterragem | O que significa | O que fazer se não aterrar |
|---|---|---|
| **Medição** | Um número que veio de um procedimento de avaliação | Ou se mede, ou se retira a afirmação |
| **Citação** | Uma fonte revista por pares que o sustenta | Ou se cita, ou se reformula como opinião do autor |
| **Restrição** | Uma condição declarada antes de qualquer medição | Tem de estar declarada em sítio anterior ao uso |
| **Decisão** | Uma escolha do autor, assumida como escolha | Tem de dizer que é escolha, e contra que alternativa |

Uma afirmação que não aterre em nenhuma das quatro é uma afirmação a remover. Não a suavizar: a
remover.

**Alvos prioritários, porque é onde as cadeias são mais curtas:** as três respostas às questões de
investigação; as três linhas da tabela de decisões em que o sistema não obteve o melhor resultado;
a janela de vinte dias, que é a opção mais difícil de justificar e que o próprio documento já
admite não ser sustentada pela única medição existente; e a afirmação de explicabilidade nas
Considerações finais.

**Saída:** duas coisas. As correções no documento, e um ficheiro `docs/defesa/PORQUES.md` com cada
cadeia que exigiu mais de dois passos até aterrar — que é o material de estudo mais útil que a
defesa pode ter, e alimenta diretamente o dossiê da frente 08.

**Esforço:** 2 dias. **Quando:** depois da frente 07 e antes da 08, porque o dossiê deve nascer já
com os porquês resolvidos.

---

## 9. Calendário

Vinte dias úteis, com folga. Os dias são de trabalho, não de calendário.

| Dias | O quê | Porquê aqui |
|---|---|---|
| **1–2** | Telegram: feedback e webhook (ponto 1 deste plano) | Abre a janela de recolha. Tudo o resto pode esperar; isto não. |
| **3–4** | Telegram: alerta imediato e edição (ponto 2) | Fecha as alterações ao sistema cedo, deixando margem para reparar. |
| **5–6** | Painel e marca (pontos 3 e 4) | Antes das capturas de ecrã novas do ch4. |
| **7–11** | Artefactos visuais (ponto 5) | O maior bloco. A recolha corre sozinha por trás. |
| **12–13** | Desculpas e declaração de IA (ponto 6) | Sobre texto quase final. |
| **14–16** | Escrita e bibliografia (ponto 7) | Sobre texto final. |
| **17–18** | O «porquê?» em cadeia (frente 8.5) | Sobre o documento fechado. Produz as perguntas da defesa. |
| **19** | Dossiê e prompts (ponto 8) | Nasce já com os porquês resolvidos. |
| **20** | Fecho | Recontagem de páginas, compilação limpa em contentor novo, três portas de qualidade, metadados, entrega. |
| **Dia da defesa −3** | Fechar a recolha de feedback, escrever os resultados | O N é o que for. Reporta-se como for. |

Trabalho que corre em paralelo e não ocupa dias: a recolha de feedback, do dia 2 até três dias
antes da defesa.

---

## 10. O que este plano não faz

Registado para não voltar a ser discutido a meio:

- **Não reexecuta os 31 avaliadores.** Está identificado como dívida desde a auditoria e continua
  a ser a coisa certa a fazer. Não cabe em dezoito dias ao lado de tudo isto, e os valores atuais
  já foram verificados um a um contra `docs/evaluation/`. Fica no `ESTADO.md` como dívida
  conhecida.
- **Não fecha as cinco lacunas restantes do estado da arte** (enquadramento regulatório, deteção
  de quase-duplicados, seleção sob orçamento, geração a partir de dados estruturados). Custam
  páginas que o documento não tem.
- **Não redesenha a marca de raiz**, pelas razões da secção 4.
- **Não transforma o piloto de feedback num estudo com utilizadores.** Não há N para isso e
  fingir que há é a forma mais rápida de perder a defesa.

---

## 11. O que preciso de ti, e quando

| Quando | O quê |
|---|---|
| ~~Hoje~~ | ~~Email ao Luís Gomes a pedir o modelo MEIA em vigor.~~ **Feito a 2026-09-01: o modelo chegou, o ponto 6 está resolvido e aplicado, e não há mais nada bloqueado por terceiros.** |
| **Hoje** | Confirmar que posso mexer no caminho de envio do canal em produção. Já disseste que sim; fica registado aqui. |
| **Dia 2** | Escolher entre `investiGATOR` e `InvestiGator` para a cor, com as duas desenhadas à frente. |
| **Dia 2** | Escolher o lema entre a proposta e as três alternativas. |
| **Dia 6** | Ver as capturas de ecrã novas antes de entrarem no ch4. |
| **Dia 7** | Ver a figura piloto do Figma ao lado da versão TikZ, impressas, e decidir se as outras cinco se fazem. |

---

## 12. Registo de alterações deste plano

| Data | O quê |
|---|---|
| 2026-09-01 | Criado. Ordem de execução alterada face à lista original, pela razão da secção 0. |
| 2026-09-01 | Chegou o modelo oficial MEIA v2. Ponto 6 resolvido e aplicado: Declaração de Integridade na redação do modelo, declaração de IA movida para a Secção 3.8.4, Lista de Símbolos acrescentada. |
| 2026-09-01 | **Orçamento de páginas corrigido.** Os anexos não contam. Contam 90 de 120, e não 120 de 120. A Figura `fig:sis_seletividade` foi reposta no `ch4`. |
| 2026-09-01 | Frente 8.5 acrescentada a pedido do autor: o «porquê?» em cadeia, mesmo no fim. Calendário passa de 18 para 20 dias. |
| 2026-09-01 | **Frente 01 no ar** (release v51). Construída e testada (75 testes novos). Falta pôr no ar: dois passos manuais em `docs/design/telegram_feedback.md`. Descoberta que mudou o desenho: o webhook desliga o `getUpdates`, por isso passou a tratar também dos comandos. |

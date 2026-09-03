# PLANO FINAL — InvestiGator

> **PRIORIDADE MÁXIMA.** Este ficheiro manda sobre tudo o resto em `DIMEIA/`.
> Se algum outro documento (`archive/reports/INVESTIGATOR_MASTER_PLAN.md`, `docs/planos/CHECKLIST.md`, `archive/reports/REBUILD_MASTER.md`)
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

### Atualização de prioridade do autor — 2026-09-03

**Complemento mais recente, obrigatório:** ler `REVISAO_PRIORITARIA_ANEXOS.md` e os quatro
originais ali ligados. Verificação prioritária, item a item, antes de consolidar alterações;
não fica adiada para depois da defesa. Todas as figuras serão refeitas **em inglês** para
reutilização no artigo; a tese inteira só muda de língua por decisão posterior. O calendário
do artigo deve ser confirmado cedo, não automaticamente adiado como sugere um dos anexos.

Esta atualização prevalece sobre a ordem histórica abaixo. O autor mandou desenvolver o
retreino e rejeitou explicitamente o piloto Figma da Figura 4.10. Não voltar a pedir aprovação
desse piloto. A identidade verde do software não define a apresentação da dissertação.

Ordem por dependências, confirmada após leitura integral do anexo reenviado:

1. Auditar dados, registos e treino existente; definir protocolo e desenvolver retreino
   controlado. Plano e evidência em `docs/planos/RETREINO_CONTROLADO.md`.
2. Verificar candidatos, integração e recuperação; estabilizar software e resultados. A
   recolha de feedback real decorre em paralelo, com consentimento antes dos convites.
3. Fechar organização e portabilidade com dependências mapeadas, sem apagar árvores ativas.
4. Rever a tese canónica a partir da implementação verificada: cortar redundância, conferir
   alegações, explicar fórmulas, atualizar arquitetura e aplicar apresentação académica neutra.
5. Preparar gravação da demonstração, slides, guia e artigo sobre resultados estabilizados.
   Confirmar calendário e requisitos do artigo antes de assumir submissão.
6. Considerar tradução apenas no fim, por decisão do autor; não criar já duas teses paralelas.

O pedido de auditoria global sem alterações continua válido para essa auditoria; o pedido
específico posterior autoriza desenvolver o retreino. Não autoriza fabricar feedback, reescrever
resultados antigos nem promover automaticamente um modelo não avaliado. A auditoria documental
global não fica substituída por esta inspeção técnica inicial.

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

## 1. Telegram — feedback bidirecional  *(ponto 3 · ✅ NO AR; ⚠️ fixar consentimento antes dos convites)*

### Estado fechado a 2026-09-03

| Peça | Ficheiro | Estado |
|---|---|---|
| Botões e chave | `investigator/telegram_bot/feedback.py` | Dois botões em todos os alertas; um voto por pessoa e alerta. |
| Receção | `POST /telegram/webhook` em `api/main.py` | Webhook com segredo; responde sempre ao `callback_query`. |
| Persistência | `feedback.jsonl` na branch `alerts-history` | Junção acrescentável; semente remota depois de reinícios. |
| Privacidade | `feedback_log.py` e `webhook.py` | Utilizador resumido com BLAKE2b; `/deletefeedback` e `/apagar` retiram votos da análise. |
| Análise | `scripts/analyse_feedback.py` | Obtém votos **e** histórico; falha antes de escrever se não conseguir validar. |
| Tese | `tese-v2/ch5/feedback_auto.tex` | Fragmento dinâmico incluído pelo Capítulo 5. |

O identificador pessoal do utilizador nunca é guardado em claro. O ficheiro contém a chave do
alerta, o resumo do utilizador, a ação, a hora e os identificadores do canal e da mensagem. Os
dois últimos não identificam o votante e são necessários para atualizar o teclado. A mensagem
fixada preparada em `docs/design/telegram_channel.md` diz exatamente o que fica na branch pública.

O comando de retirada acrescenta uma marca `d`: os votos anteriores deixam de contar, mas as
linhas pseudonimizadas permanecem no histórico Git. Esta limitação é dita ao participante; não
se promete uma eliminação física que um repositório versionado não consegue cumprir.

⚠️ **Ação manual antes de convidar pessoas:** substituir e fixar a mensagem de consentimento.
O texto está pronto; o sistema não deve publicar nem fixar mensagens no canal sem ação do dono.

### O que isto vale para a tese, e o que não vale

Vale: o Capítulo 6 declara hoje, como limitação, que a hipótese fundadora — a de que uma
explicação verificável conduz a melhor decisão — **não foi testada**. Isto não a testa. Testa
uma coisa mais modesta e ainda assim nova no documento: se os alertas que o sistema decide
enviar são considerados úteis por quem os recebe.

A correlação com a pontuação de triagem, proposta na primeira versão deste plano, **não é
recuperável**: o histórico entregue não guarda essa pontuação por alerta. Acrescentá-la agora não
reconstrói o passado. A pergunta sai do piloto em vez de se fabricar uma ligação retrospetiva.

Não vale: com um canal pequeno e três semanas, o N vai ser de dezenas de votos, não de milhares.
**O plano é reportar o N exato, o intervalo de confiança quando permitido, e dizer que é um
piloto.** A 2026-09-03 há 20 votos efetivos de duas pessoas sobre 16 alertas, após recuperar seis
linhas reais preservadas no Git e excluir quatro votos de teste. Uma pessoa representa 80% da
amostra; sem ela restam quatro votos, abaixo do mesmo mínimo de 20. O documento reporta esta
salvaguarda e não apresenta o piloto como estudo de utilizadores.

### Critério de aceitação

- [x] O voto chega ao registo, recebe confirmação e sobrevive ao reinício.
- [x] Alertas inexistentes, votos repetidos, retiradas e `callback_data` inválido são tratados.
- [x] O N mínimo e a salvaguarda dominante valem também para o fragmento LaTeX.
- [x] Os seis votos apagados por substituição foram recuperados exatamente do commit que os guarda.
- [ ] O dono do canal fixa a mensagem de consentimento antes de convidar participantes.

**Esforço:** 1,5 dias. **Risco:** médio; toca no caminho de envio.

---

## 2. Telegram — alerta imediato, contexto por edição  *(ponto 4 · ✅ metade NO AR (v53), metade recusada com razão)*

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

## 3. Painel — tirar o ruído  *(ponto 1 · ✅ NO AR, e as figuras do ch4 refeitas)*

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

## 4. Marca — o retângulo, a cor, a peça única, o lema  *(ponto 2 · ✅ fechado a 2026-09-03)*

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

O cabeçalho web já tinha sido corrigido: `Investi` fica em tinta e **Gator** inteiro em verde.
Os ficheiros de entrega ainda pintavam só o `G`; passaram a usar a mesma divisão. A comparação
real está em `docs/design/brand-comparison.png`. A alternativa com o nome todo verde foi rejeitada
porque apaga a separação semântica.

### A peça única, que já foi pedida várias vezes

**Entregue:** conjunto fechado, com IBM Plex local convertido em contornos, sem `<text>`, sem
dependência de tipos de letra instalados, e cada peça em claro, escuro e monocromático:

```
logo-lockup.svg          glifo + nome, horizontal        cabeçalhos, capa da tese
logo-lockup-tagline.svg  o anterior + lema               capa, primeiro slide
logo-empilhado.svg       glifo em cima, nome em baixo    avatar, quadrados
logo-marca.svg           só o glifo                      favicon, 16 px
logo-nome.svg            só o nome                       rodapés
```

Os cinco PNG claros de 512 px estão em `app/assets/brand/png/`; o avatar quadrado foi regenerado
em `app/assets/telegram_avatar.png`. O gerador e os testes são, respetivamente,
`scripts/build_brand_assets.py` e `tests/test_brand_assets.py`.

### O lema

O lema anterior — *«Every move investigated, never predicted.»* — foi rejeitado pelo autor por
ser longo, defensivo e pouco distintivo. O lema canónico passa a ser:

> **Markets move. We investigate.**

A advertência sobre previsão e aconselhamento continua no produto como advertência funcional,
não como slogan.

### A hipótese de uma marca nova

A “Tail” mantém-se. A geometria dos lockups antigos divergia da marca canónica e foi unificada
com `logo.svg` e com o SVG inline do painel. Os estudos `logo-gator-g.svg` e `logo-jaws.svg`
continuam explicitamente excluídos do conjunto canónico.

**Estado:** concluído; a captura visual e 48 portas específicas passaram.

---

## 5. Artefactos visuais — revisão de um a um  *(ponto 5)*

**Piloto conceptual:** conteúdo e critérios em `docs/design/PILOTO_CICLO_MODELO.md`.
**Revisão posterior:** piloto com rótulos/fases a 8,03 pt à largura final; cor/cinzentos
inspecionados. Prova atualizada. Mais alto que a atual; pronto para decisão, tese intacta.
O diagnóstico de tipografia menor abaixo refere-se à primeira versão.
**Comparação concluída:** `output/pdf/comparacao-ciclo-modelo.pdf`, cor/cinzentos inspecionados.
Exportação resolvida. À mesma largura, rótulos descem de cerca de 8 para 6,57 pt; não substituir
nesta versão. O registo de exportação pendente abaixo é histórico. Tese preservada.
Figma religado em 2026-09-03; piloto criado e inspecionado:
https://www.figma.com/design/sNfbRq1WUSM8gRK95FjtWy. Falta exportação local acessível e comparação
à largura da tese/em cinzentos; o retorno de bytes da exportação não equivale a PDF entregue.
Não substituir a Figura 4.10 sem produzir, inspecionar e comparar o piloto separado.

**Quinta passagem validada:** Figura 5.7 harmonizada em verde/trama, sem números novos.
Gerador aponta agora por defeito à árvore canónica; dois testes específicos passaram. Figura
e página física 81 verificadas. PDF 126/94. Tipografia externa e piloto conceptual ainda por rever.

**Quarta passagem validada:** janela implantada verde (5.5), alternativa volatilidade neutra
(5.10), legenda de ablação não cumulativa (5.12). Remissão residual a barras retiradas corrigida.
Páginas físicas 78/85/87 verificadas; PDF 126/94, porta canónica aprovada. Frente ainda aberta.

**Terceira passagem validada:** removida a duplicação de modelo/volatilidade na Figura 5.11,
mantendo-os na 5.18 com remissão explícita. Legendas clarificadas e verde cheio reservado ao
implantado na comparação final. Páginas físicas 86/96 inspecionadas, PDF 126/94, porta aprovada.

**Segunda passagem validada:** funil (Figura 4.4) mostra agora as seis categorias completas,
totalizando 5 060 avaliações, e separa cinco mensagens das 333 passagens. Página física 63
inspecionada; PDF mantém 126/94. Harmonização restante e redundâncias ainda pendentes.

**Primeira vaga validada a 2026-09-03:** seis gráficos do ch5 e dois diagramas do ch4,
com inspeção das oito páginas renderizadas. Três defeitos adicionais de composição corrigidos.
PDF mantém 126 páginas físicas / 94 contadas; porta canónica passou. Relatório em
`docs/design/REVISAO_VISUAL_2026-09-03.md`. A frente completa permanece aberta.

### Inventário medido

| | Total | Composição |
|---|---|---|
| Figuras | **40** | 18 diagramas TikZ · 17 pgfplots · 4 imagens importadas · 1 reprodução textual |
| Tabelas | **13** | todas nativas |

Por capítulo: ch1 tem 2, ch2 tem 2, ch3 tem 6, ch4 tem 11, ch5 tem 18, ch6 tem 1.

**2026-09-03:** seis gráficos do ch5 alterados e duas colisões do ch4 corrigidas nas fontes.
Estilo comum criado. Validação visual final pendente; esta frente ainda não está fechada.

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

## 8.75. Organização da pasta e do repositório  *(ponto 9 · pedido a 2026-09-01)*

Pedido dele: o repositório é público e está desarrumado. Nada de ficheiros
soltos na raiz; `code/` e `archive/` certos; e uma `dissertation/` com
`thesis/`, `slides/` e `guide/` lá dentro.

O plano completo, com os números do que está mal, a árvore proposta, o
critério de arquivo e os seis passos de execução, está em
`docs/design/reorganizacao.md`.

Três coisas que vale a pena saber sem abrir esse ficheiro:

**Cinco ficheiros ficam na raiz por obrigação técnica.** O *buildpack* de
Python do Heroku deteta a aplicação na raiz. `Procfile`,
`requirements.txt`, `.python-version`, `pyproject.toml` e `README.md`
ficam. Há *buildpacks* de terceiros que contornam isto; não acrescento uma
dependência externa não oficial ao caminho crítico a três semanas da
defesa. O código em si muda de sítio — o `Procfile` passa a apontar para
`code/`.

**`tmp/` tem 406 ficheiros versionados e 66 MB**, dos quais 176 são páginas
renderizadas de uma compilação de 29 de agosto. Estão num repositório
público. Mover não chega: sai do índice com `git rm --cached` e entra no
`.gitignore`. Isso tira-os da árvore de quem clona, mas **não do
histórico** — para isso era preciso reescrever o histórico e forçar o
*push*, o que quebra clones existentes. Antes da defesa, não.

**Corre a seguir à frente 03, não no fim.** As frentes 05, 07 e 08 escrevem
dentro de `tese-v2/`, das figuras e do guia. Deixar a mudança de caminhos
para o último dia útil é como se perdem entregas.

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

## 9.5. Depois da defesa: a tese que o autor quer escrever

O autor descreveu, a 2026-09-01, a sua visão de uma tese ideal — introdução ancorada no valor
de negócio com números de 2026, revisão da literatura que não descarta nenhuma família de IA,
e um desenho que testa todas as combinações de componentes. Está registada em
`docs/planos/POS_PLANO_TESE_IDEAL.md`, **com três correções sem as quais não sobrevive a uma defesa** e com
a separação entre o que cabe nos dias que faltam e o que é uma tese diferente.

As duas correções que importam, em resumo: **o valor de negócio não pode ser a velocidade**
(a medição diz 353 minutos, a QI3 é negativa, e a recusa de aconselhar é a posição ética do
trabalho); e **testar todas as combinações e ficar com a melhor não é mais rigoroso, é menos**
(comparações múltiplas sobre o teste enviesam o vencedor, e a dissertação atual já faz algo
mais forte com comparações emparelhadas pré-registadas).

O que **cabe** e entra como trabalho, se houver dias: introdução reescrita, tabela comparativa
do estado da arte, e ablações pré-registadas sobre três a quatro componentes.

---

## 9.6. Depois da defesa: a auditoria integral pedida a 2026-09-01

**Reconfirmada a 2026-09-03:** complementos e triagem de evidências registados em
`docs/planos/POS_PLANO_AUDITORIA.md`, sem antecipar a auditoria nem alterar tese/código.
Inclui concisão, terminologia, portabilidade segura, gravação da demonstração e artigo.
A generalização de ch1:45 fica sinalizada para a frente 07. O piloto revisto aguarda decisão.

Registada em `docs/planos/POS_PLANO_AUDITORIA.md`. Uma auditoria baseada em evidência, comparando a tese e o
sistema existentes contra a visão do autor, com plano de melhorias priorizado e treze secções de
saída. **Sem alterar tese nem código na primeira fase**, por pedido expresso.

Cinco pontos do pedido já estão resolvidos e não precisam de ser reabertos: a declaração de IA, os
apêndices, a distinção entre deteção/explicação/causalidade/recomendação, a validação posterior
dos alertas (v53) e a utilidade percebida (v51). Estão listados no ficheiro.

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
| **Antes dos convites** | Substituir e fixar no canal a mensagem de consentimento de `docs/design/telegram_channel.md`; é a única ação manual ainda aberta nas frentes 01–04. |
| ~~Dia 2~~ | ~~Escolher a divisão cromática.~~ **Feito:** `Investi` em tinta, `Gator` em verde. |
| ~~Dia 2~~ | ~~Escolher o lema.~~ **Feito:** “Markets move. We investigate.” |
| **Dia 6** | Ver as capturas de ecrã novas antes de entrarem no ch4. |
| **Dia 7** | Ver a figura piloto do Figma ao lado da versão TikZ, impressas, e decidir se as outras cinco se fazem. |

---

## 12. Registo de alterações deste plano

| Data | O quê |
|---|---|
| 2026-09-03 | **Frentes 01 e 04 fechadas tecnicamente.** Feedback: os seis votos apagados por `publish_blob` foram recuperados byte a byte do commit `a9e098cda` e repostos em `alerts-history` (`504371db0`); o analisador passa a obter votos e histórico, falha fechado, ordena pelo instante, distingue mudança de clique repetido, preserva retiradas e aplica o N mínimo também ao recorte sem votante dominante. Estado ao regenerar: 20 votos efetivos, duas pessoas, 16 alertas, uma pessoa com 80%; a leitura independente continua abaixo do mínimo. Consentimento e `/deletefeedback`/`/apagar` ficaram prontos; falta ao dono fixar a mensagem antes dos convites. Marca: 5 peças × claro/escuro/mono, IBM Plex em contornos, `Gator` verde, geometria única, PNG 512 e lema “Markets move. We investigate.”; 48 portas específicas. |
| 2026-09-01 | Criado. Ordem de execução alterada face à lista original, pela razão da secção 0. |
| 2026-09-01 | Chegou o modelo oficial MEIA v2. Ponto 6 resolvido e aplicado: Declaração de Integridade na redação do modelo, declaração de IA movida para a Secção 3.8.4, Lista de Símbolos acrescentada. |
| 2026-09-01 | **Orçamento de páginas corrigido.** Os anexos não contam. Contam 90 de 120, e não 120 de 120. A Figura `fig:sis_seletividade` foi reposta no `ch4`. |
| 2026-09-01 | Frente 8.5 acrescentada a pedido do autor: o «porquê?» em cadeia, mesmo no fim. Calendário passa de 18 para 20 dias. |
| 2026-09-02 | **Arrumação, metade A** (frente 09): `tmp/` fora do índice (406 ficheiros, 66 MB num repositório público), `archive/` criado com critério escrito, e os 17 `.md` soltos da raiz reduzidos a 3. Duas coisas que o plano assumia não se confirmaram e ficaram registadas: `app/` é importado por onze ficheiros (não é a aplicação morta), e `thesis/` recebe as figuras de nove scripts de avaliação enquanto a `tese-v2` lê de outro sítio — o pipeline das figuras aponta para uma árvore e o documento lê de outra. A metade B (`code/`, e reduzir as árvores de tese a uma) fica para depois das frentes 05 e 07. **E um terceiro defeito do mesmo tipo:** o `market_index` que o produtor escrevia morria no `Instantaneo`, que copiava as linhas e deitava fora o resto — a página recebia `null` sem erro nenhum. |
| 2026-09-02 | **Painel v8 e um segundo defeito crítico.** Gráfico: 1D por defeito com intradiário, camadas com interruptores, alertas com marca própria distinta dos dias assinalados, e o z numa faixa própria (não partilha unidade com o preço). History deixa de ser subtractivo e passa a mostrar o registo ao longo do tempo. Mascote como semáforo do **SPY** — não do NASDAQ; o índice da decomposição é o S&P 500 e a legenda nomeia-o. **E o orçamento de 5 alertas/dia não estava a ser cumprido:** 20 no dia 26 de agosto, em quatro rajadas de exactamente cinco aos segundos de arranques do processo. O contador vive no disco efémero e o mecanismo que o repunha não distinguia «não consegui ler» de «não saiu nada». Corrigido, com falha fechada só nessa porta. Varrimento do orçamento em `docs/evaluation/evaluation_budget_sweep.md`: de k=5 para k=15 a precisão cai 1,7% e a cobertura triplica — a decisão do valor é do autor. |
| 2026-09-02 | **Defeito crítico na frente 01, apanhado e corrigido.** Os votos eram publicados na branch de dados com `publish_blob`, que **substitui**. Com o disco efémero do Heroku, o primeiro voto a chegar depois de um reinício apagava tudo o que estava lá antes — e apagou: os seis votos anteriores ao deploy das 19:10 desapareceram. Passou a `publish_jsonl_merge`, que junta. Segundo defeito da mesma família: o `/api/feedback` lia o disco do dyno **web** e quem escreve é o **worker**, por isso o painel mostrava zero votos com votos a entrar; passa a juntar o disco local com a branch, em memória e com cache de 45 s. Sete testes novos, incluindo o que separa «li e está vazio» de «não consegui ler». |
| 2026-09-01 | **Frente 09 registada** (ponto 9, pedido a meio da frente 03): organização da pasta e do repositório. Plano em `docs/design/reorganizacao.md`. Corre a seguir ao painel v7. E `docs/REGISTO_PEDIDOS.md` passa a ser o sítio onde nenhum pedido dele se perde — regras permanentes, restrição de não prever preços, fila de trabalho e pendências dele. |
| 2026-09-01 | **Frente 03 no ar.** Funil visual em vez da parede de prosa; dois defeitos apanhados por medição no DOM (sobreviventes negativos, e colisão de `.barra` com o cabeçalho); o retângulo do logótipo saiu de caminho (`.nome` → `.chip`); figuras do ch4 passam a ser geradas por `scripts/figuras/capturar_painel.py`. |
| 2026-09-01 | **Frente 02 no ar** (release v53): desfecho observado a +1, +3 e +5 sessões, anexado à mensagem original. O envio do esboço antes da análise foi **recusado** — a medição dá 5 s de ganho, e os 7,5 s da recuperação são de arranque a frio, que o worker permanente não paga. Razão em `docs/design/telegram_dois_tempos.md`. |
| 2026-09-01 | **Frente 01 no ar** (release v51). Construída e testada (75 testes novos). Falta pôr no ar: dois passos manuais em `docs/design/telegram_feedback.md`. Descoberta que mudou o desenho: o webhook desliga o `getUpdates`, por isso passou a tratar também dos comandos. |

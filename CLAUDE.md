# CLAUDE.md — Memória Persistente do Projeto

> Ficheiro mais crítico do projeto. É o mecanismo principal de continuidade entre sessões e dispositivos.
> **REGRA ABSOLUTA: atualizar este ficheiro no fim de TODAS as sessões, sem exceção.**
> Ler na íntegra no início de cada sessão, antes de agir.

---

## Estado Atual
- **Sessão nº:** 50 (**citações auditadas até ao fim: 129/129 conteúdo + paridade EN↔PT**)
- **Última atualização:** 2026-08-05
- **📌 SESSÃO 50 (2026-08-05):**
  **⚠️ (0) NOVO BACKLOG DO ALUNO, POR ANALISAR:**
  [`progress/BACKLOG_ALUNO.md`](progress/BACKLOG_ALUNO.md) — seis pedidos ditados no fim da
  sessão (refazer o painel; rever a literatura com o PDF real de cada fonte no repo; latência
  quase-real dos alertas; melhorar o guia; rever a escrita para soar humana; varrer os TODO que
  restam). **Ele disse explicitamente "não penses nisso ainda"** — está registado em bruto, sem
  análise, e é por aí que a próxima sessão começa.
  **(A) AS 7 CHAVES QUE FALTAVAM FORAM AUDITADAS ⇒ cobertura 129/129 instâncias, 59/59 chaves.**
  A 1.ª ronda (sessão 43) cobriu 122/52. Desta vez leu-se **texto integral**, não só o resumo.
  **2 achados reais, ambos corrigidos por enfraquecimento, EN+PT:**
  **(A1) `angelopoulos2023conformal` — o mais sério, e é o mal-entendido clássico do método.**
  A tese dizia que a calibração "nada diz sobre um item individual" e que a predição conformal
  "responde **exactamente** a essa lacuna". Não responde: a garantia conformal é **marginal**
  (média sobre os casos), não condicional. Confirmado no texto integral (arXiv:2107.07511):
  *"we call this property **marginal coverage**… (averaged) over the randomness in the
  calibration and test points"* e *"in the most general case, **conditional coverage is
  impossible to achieve**"*. Passa a "**narrows** this gap… although its guarantee remains
  *marginal*". O eco no Cap. 5 ("backed by a guarantee") também foi enfraquecido. **Justiça para
  com o texto:** a frase seguinte já dizia bem "in at least 1−α of cases" — era **moldura**, não
  atribuição falsa.
  **(A2) `vinh2010ami`** — dizia que a medida ajustada "corrige para o acaso **e para a
  cardinalidade**". O que Vinh et al. estabelecem é a *constant baseline property* (p. 2844:
  *"has a **baseline value** always close to zero, and appears **not to be biased in favor of any
  particular value of K**"*) — o **ponto zero**, não a escala, e é **um** mecanismo e não dois.
  Passa a "chance baseline close to zero that is not biased towards any particular number of
  classes". **A conclusão do Caso 5 mantém-se intacta.**
  **(A3) `tetlock2007media`** — "an early **proof**" nas duas línguas passa a "early
  **evidence**". Tetlock estabelece uma relação estatística, não uma prova.
  **5 chaves passaram com prova registada:** `vovk2005algorithmic` (e a hipótese de
  permutabilidade **está declarada**, não escondida), `gama2014survey`, `rousseeuw1987silhouettes`
  (incluindo a leitura correcta de uma silhueta **baixa**), `sculley2015debt` (os três itens da
  tese são os próprios factores de risco do artigo) e `worldmonitor2026` (a tese **não** lhe
  atribui autoridade académica — é um produto, e está creditado como tal).
  **(B) PARIDADE EN↔PT VERIFICADA PELA 1.ª VEZ** (`scripts/check_bilingual_parity.py`, novo).
  O risco nunca foi a citação mudar de sítio — era a tradução **endurecer o verbo** e a citação
  passar a sustentar mais do que aguenta, na versão que o júri português lê. **0 assimetrias em
  86 chaves comparadas.**
  **⚠️ E o zero só vale por causa do CONTROLO NEGATIVO, que é a lição desta sessão.** A primeira
  versão apanhava `causa` dentro de *causal*, *causalmente* e *causar* e acusou **5 frases fiéis**
  — uma delas dizia "podem causar", que é o *hedge* **oposto** ao que estava a reportar. Com
  fronteira de palavra desapareceram as cinco. O script passa a **plantar** um endurecimento e um
  *hedge* perdido e a **exigir** que dispare nos dois, recusando-se a reportar "0 achados" se o
  autoteste falhar: **um detector partido e um corpus limpo são indistinguíveis no ecrã.**
  **(C) LIMITE DE GASTO OUTRA VEZ:** 5 de 11 agentes morreram (incluindo **os dois cépticos** e
  **as duas passagens de paridade**). Verifiquei os dois achados **eu próprio** contra as fontes
  primárias antes de aplicar, e fiz a paridade por script. O limite é **intermitente** — abriu a
  meio da sessão e voltou a fechar.
  **(D) ARRUMAÇÃO DO REPO, executada em parte:** `progress/_historico/` com os três planos que se
  **auto-declaravam superados** (MASTER_PLAN → PRODUCT_ROADMAP → PLANO_MELHORIAS), mais
  `progress/README.md` novo a explicar o que está vivo e porque é que um plano superado ao lado de
  um plano activo é **pior** do que não ter plano (as caixas por marcar incluem itens **cortados
  por decisão**). Todas as referências actualizadas, **0 links relativos partidos** (verificado).
  **⚠️ E o que NÃO se apagou, que é o mais importante:** o varrimento de órfãos acusava
  `scripts/figures/fig_{embedding_projection,uncertainty}.py`, e **os dois geram figuras que estão
  na tese** — só pareciam órfãos porque a documentação cita os **PDF de saída**, não o `.py`.
  Apagá-los partia a reprodutibilidade. O detector estava errado, não o repositório.
  **(E) PDFs DAS FONTES:** `docs/decisions/citation_pdfs/` criado, com README que diz exactamente
  o que descarregar (**44 das 59 são legíveis sem conta; 14 precisam da conta ISEP**, com
  prioridade). Os `*.pdf` estão **gitignored** e isso é obrigatório, não conveniência: repositório
  público + material com direitos de autor.
  **Gates: 618 testes, ruff limpo, congelados byte-iguais, EN 107 pp / PT 111 pp — 0 erros e 0
  citações indefinidas.**
- **📚 SESSÃO 49 (2026-08-04 — o aluno pediu: "o máximo de agentes para rever criticamente
  cada citação e entrada bibliográfica", logótipos reais nos slides e no guia, a app de quizz
  para estudar no telemóvel, os textos do Telegram no repositório, e arrumação do repo):**
  **(A) ⚠️ A CONTA BATEU NO LIMITE MENSAL DE GASTO, E ISSO MUDOU O MÉTODO.** Lancei o workflow
  de auditoria com **18 agentes** (6 grupos de metadados + 6 de conteúdo + paridade EN↔PT +
  2 de "afirmações sem fonte" + cépticos + crítico de completude). **16 dos 18 morreram no
  limite de gasto**; só 2 completaram. O workflow do estudo de mercado da v4 perdeu os 4
  cépticos pela mesma razão. **Não insisti com mais agentes** — passei a fazer o trabalho
  directamente, e para metadados isso é **melhor**, não pior: resolver um DOI é um `GET`, não
  um juízo. **Enquanto o limite não for levantado, não vale a pena lançar workflows.**
  **(B) VERIFICADOR DE BIBLIOGRAFIA** (`scripts/verify_bibliography.py`, novo). Resolve cada
  identificador contra Crossref/arXiv e compara **campo a campo**: título, ano, todos os
  autores, revista/conferência, volume, número, páginas — e a verificação que quase ninguém
  faz, **se o DOI resolve para ESTE trabalho e não para outro de título parecido**. Cobre as
  duas bibliografias (tese + artigo IEEE) = **84 entradas**. Relatório regenerável em
  `docs/decisions/bibliography_verification.md`.
  **(C) 3 ACHADOS REAIS, todos corrigidos:**
  **(C1)** o **FNSPID** — o conjunto de dados de que a tese inteira depende, e a chave mais
  citada do corpo (7 instâncias) — estava citado como **pré-publicação arXiv** quando existe
  versão revista por pares no **KDD '24** (DOI `10.1145/3637528.3671629`, pp. 4918–4927).
  Corrigido nas **duas** bibliografias: uma correcção só na tese publicaria a inconsistência.
  **(C2)** o **LOF** declarava as actas do SIGMOD mas o DOI resolvia para a revista *SIGMOD
  Record* 29(2). Mesmo trabalho, mesmas páginas, **identificador trocado** → passa a
  `10.1145/342009.335388`.
  **(C3)** o **Sculley 2015** era a **única entrada sem identificador nenhum**, o que contraria
  o protocolo §6.4 do próprio projecto. As actas do NIPS 2015 não emitem DOI ⇒ URL canónico da
  NeurIPS, com título e lista de autores conferidos.
  Mais o cabeçalho do `references.bib`, que dizia **"52 entradas"** havendo **59**.
  **⚠️ (D) O ACHADO DE MÉTODO, e é o mais instrutivo: a PRIMEIRA CORRIDA DEU 33 ACHADOS E 30
  ERAM DEFEITO MEU, não da bibliografia.** O comparador (i) media títulos por **Jaccard** e o
  Crossref guarda-os truncados no subtítulo ("Anomaly detection" para "Anomaly Detection: A
  Survey") ⇒ acusava **três clássicos** de "o DOI resolve para outro trabalho", que é a
  acusação mais grave que sabe fazer; (ii) acusava páginas de diferirem quando o registo só
  guarda a **primeira** (Kahneman, Fama ×2, Engle); (iii) partia apelidos com acentos porque
  limpava `\[a-zA-Z]+` **antes** dos acentos de LaTeX (Jégou, Žliobaitė, Díaz-Rodríguez,
  García); (iv) não sabia de **partículas** (o Crossref guarda `family="Hengel"`,
  `given="Anton Van Den"`); (v) tratava `1--2` e `1-2` como números diferentes; (vi) chamava
  "outro trabalho" a um registo do Crossref **sem título** (o do BERT é uma ficha vazia do lado
  deles); (vii) a busca por "existe versão publicada?" corria em entradas que **já** citam as
  actas e trouxe um capítulo de livro de 2025 para o *Attention Is All You Need* e uma revista
  de engenharia para o *word2vec*. **Um verificador que grita demais não é rigoroso — é um
  verificador em que se deixa de olhar.** Endurecido (contenção em vez de Jaccard, primeira
  página, acentos primeiro, partículas, só pré-publicações declaradas + sobreposição de
  autores). **Final: 84/84 sem achados.**
  **(E) DUAS DIVERGÊNCIAS ARBITRADAS A FAVOR DA TESE, com fonte:** o Crossref dá 3980–3990
  para o **SBERT** e a **ACL Anthology** dá 3982–3992 (que é o que o `.bib` tem) — manda a
  Anthology; e a ACM publica **online-first**, logo o Pang tem 2021 (online) e 2022 (papel) e o
  Guidotti 2018 e 2019 — a literatura cita o ano em que apareceu, e é esse que o `.bib` usa.
  **(F) LOGÓTIPOS REAIS** (`scripts/fetch_slide_logos.py`, novo). **Desde a sessão 40 que as
  macros `\techlogo`/`\glogo` existiam e mostravam SEMPRE o caminho de recurso**, porque
  `slides/logos/` só tinha um README a explicar como obter os PNG à mão. **34 ficheiros**
  (22 tecnologias + 12 empresas), `simple-icons` **16.28.0 fixada** (não `@latest` — um deck
  que compila diferente consoante o dia não é reproduzível), cor de cada marca lida do ficheiro
  de dados do pacote, **manifesto SHA256**. O `finnhub` e o `sbert` não existem no conjunto e
  vêm das fontes próprias; o Yahoo e a Heroku **foram retirados** do simple-icons — e um
  `@latest` do jsDelivr chegou a devolver **200 para um ficheiro que a versão fixada não tem**,
  ou seja o código de estado outra vez a não ser verificação.
  **⚠️ TRÊS DEFEITOS APANHADOS A RENDERIZAR, nenhum visível no exit code:** (1) o `latexmk`
  devolveu **exit 0 sem recompilar** — ficheiros novos não estão no grafo de dependências, logo
  o PDF continuava sem logótipos e "compila limpo" não queria dizer nada (`-g`); (2) com só
  `height=13pt`, um logótipo-**palavra** fica ~7× mais largo que um ícone, dominava a linha e
  empurrava o último badge para uma linha só dele ⇒ limite de **largura** com
  `keepaspectratio`; (3) o `.bib` do artigo IEEE é um **ficheiro separado** e teria ficado a
  citar a pré-publicação.
  **(G) FRAME NOVO NOS TRÊS DECKS: "o que vigia, e porque duas das doze não são tecnológicas"**
  — os 12 logótipos agrupados por ETF de setor (**XLK ×9 · XLF · XLE · XLV**, lido do
  `relevance.py`, não de memória) com a razão da mudança 10→12 e o exemplo medido ao vivo
  (**XOM −0,98% com o setor a +0,93%**). É a decisão de **avaliação**, não decoração.
  **(H) APP DE AUTOTESTE PARA O TELEMÓVEL** (`quiz/index.html`, novo; publicada em
  <https://claude.ai/code/artifact/9ec979e9-d46a-450c-b4d9-375cf81edc23>). **44 perguntas**, um
  único ficheiro sem dependências externas (funciona **offline** depois de abrir — foi feita
  para o metro), progresso em `localStorage`, filtros por bloco e por nível 🔴🟡🟢, fila de
  repetição só das falhadas. Paleta **herdada de `app/ui_tokens.py`** (contrastes já medidos) —
  uma segunda paleta a competir com a primeira foi um defeito que a v3 já pagou. As perguntas
  de **número** são escolha múltipla auto-corrigida; as de **decisão** são abertas, porque são
  essas que provam autoria (watchlist 10→12, o defeito da Microsoft "an ordinary day",
  allowlist vs blocklist, Vasicek em vez de corte a ±4, o chip que custava 7,5 s, o teste que
  passava e estava errado, porque o histórico **não** foi limpo).
  **(I) TEXTOS E AVATAR DO TELEGRAM** (`docs/design/telegram_channel.md`, novo): nome, handle,
  descrição (238 caracteres, cabe no limite de 255), mensagem fixada com a promessa por extenso
  (é o **único** sítio onde aparece — regra H1), e `app/assets/telegram_avatar.png` **512×512**
  gerado do `icon.svg`, que estava desenhado de propósito para ser avatar do canal e **nunca
  tinha sido convertido para um ficheiro que se pudesse carregar**.
  **(J) ARRUMAÇÃO DO REPO: ANÁLISE FEITA, EXECUÇÃO **NÃO** FEITA — de propósito.** 369
  ficheiros versionados, **zero artefactos de build** (o `.gitignore` está a fazer o trabalho).
  O varrimento de órfãos deu 24 nomes e a **maioria são falsos positivos**: os `__init__.py`
  são marcadores de pacote, os logótipos das empresas são carregados **por ticker em runtime**
  (nenhum ficheiro os nomeia), e os PNG do MEIA/DEI são do template do ISEP. Sobram ~4 a olhar
  a sério: `docs/design/dashboard_v2_design.md` (a v2 foi rejeitada), `progress/_historico/PRODUCT_ROADMAP.md`,
  e `scripts/figures/fig_{embedding_projection,uncertainty}.py`. **Apagar sem verificar cada um
  seria exactamente o tipo de limpeza que parte a compilação da tese** — fica para a próxima
  sessão, com os PDF a recompilar como porta.
  **Gates: 618 testes, ruff limpo, congelados byte-iguais, EN 107 pp / PT 111 pp / artigo 4 pp /
  slides 23→24 EN e PT / guia 85→86 — todos 0 erros e 0 citações indefinidas.**
- **🚀 SESSÃO 48 (2026-08-04 — o aluno autorizou: "continue. and promote… focus on the
  essential and finalize the thesis, guarantee consistency and dignity and guarantee it is
  honest"):**
  **(A) PROMOÇÃO FEITA.** Uma linha no `Procfile`: `web:` passa de `app/streamlit_app.py`
  para `app/dashboard.py`. A v1 deixa de ser o que está no ar.
  **(B) ⚠️ DEFEITO DE HONESTIDADE APANHADO A OLHAR PARA A FIGURA — o achado da sessão.** Ao
  recapturar a Fig 4.5 vi a **Microsoft +4,82% com o cartão a dizer "an ordinary day"**.
  Verificado: `z +1,11` (abaixo do limiar, não sinalizada) mas **5 dos 249 dias** moveram-se
  tanto — um movimento no **top 2% do ano** descrito como banal. AMZN igual (9/249). Causa:
  as duas réguas medem coisas diferentes (detector = 20 dias anteriores; contagem = o ano) e
  a versão anterior resolvia a discordância **escolhendo em silêncio a palavra mais
  tranquilizadora**. Passa a dizer as duas: *"Quiet by its recent norm — but only 5 of the
  last 249 trading days moved this much"*. 4 testes novos. **Nenhum log mostraria isto.**
  **(C) DÍVIDA DA TESE PAGA NO MESMO COMMIT.** Cap. 4 reescrito **EN+PT**: grelha de cartões
  em vez de três ecrãs; a frase antes do número; a raridade como **contagem empírica e não
  probabilidade** (converter z exigiria normalidade, e as caudas pesadas fariam esse valor
  falhar precisamente nos dias que interessam); **emenda D2′ dita em voz alta** — o cartão
  nomeia o motor em palavras e a repartição fica a um clique (com doze empresas seriam 36
  números com sinal a competir no primeiro contacto).
  **(D) Fig 4.5 recapturada.** O `screenshot_app.py` apontava para a v1 **e esperava pelo
  texto "Today"**, que a promoção apagou — ficaria pendurado à espera de algo inexistente.
  **(E) SLIDES E GUIA.** Diziam "três ecrãs" e "na própria linha, sem clicar". Pior: o guia
  afirmava que a app mostra o **"background risk" da triagem**, que a v3 **retira de
  propósito** por ser uma probabilidade sobre o futuro que **H2 proíbe** em vistas de
  produto — deixá-lo poria o aluno a reivindicar, à frente do júri, exactamente o que o
  sistema recusa fazer. **+2 frames que ENSINAM** a contagem empírica e a discordância entre
  as duas réguas (guia 83 → **85 slides**).
  **(F) PORTÃO DA PROMOÇÃO** (`tests/test_dashboard_v3.py`, 20 testes): metade dos critérios
  nunca tinha sido verificada com a app a correr. **Três falhas na 1.ª corrida, as três do
  TESTE:** o varrimento de português apanhava os **comentários do CSS**; o H2 acusava "price
  target" na página do método, onde o texto é *"No price targets"* — a blocklist apanhou a
  frase e não viu a negação (mesma lição do red team do narrador, agora nos dois sentidos);
  e o H1 exigia a promessa em todas as vistas quando o critério proíbe **repetir**.
  **(G) CONSISTÊNCIA:** contagens de teste desactualizadas em 5 ficheiros (README 478,
  RELATORIO 200, guião 478, mapa 478 e — o que mais importa — a **mensagem ao orientador**,
  ainda por enviar, que dizia 478). Todas para "600+". **Falso positivo registado:** o
  comparador de tokens numéricos EN↔PT acusou ch1/ch5/ch6 e **as três eram do regex** (ch6 =
  coordenadas TikZ, mais largas em PT porque o texto é mais comprido; ch1 = notação
  `US\$100{,}000` vs `100\,000 dólares`; ch5 = `39.5` existe nas duas).
  **Gates: 618 testes, ruff limpo, congelados byte-iguais, EN 107 pp / PT 111 pp / slides
  23+23 / guia 85 — todos 0 erros, 0 citações e referências indefinidas.**
  **PENDENTE HUMANO:** rodar as 3 credenciais (o PAT primeiro — tem `admin: true`); enviar
  `docs/defence/mensagem_orientador.md`; reclamar o domínio para o URL limpo.
- **⏭️ PRÓXIMA SESSÃO COMEÇA AQUI (actualizado na sessão 50):**
  **👉 ABRIR PRIMEIRO: [`progress/BACKLOG_ALUNO.md`](progress/BACKLOG_ALUNO.md).** São os seis
  pedidos que o aluno ditou no fim da sessão 50 e que ele mandou **não analisar ainda**: refazer
  o painel de raiz; rever a literatura com o **PDF real de cada fonte** no repositório e um
  documento do que foi extraído e de onde; **latência quase-real** dos alertas (foi notificado
  depois do acontecimento); melhorar o guia de estudo; rever a escrita para soar **humana e
  jovem**; e varrer as pendências que restam. Esse ficheiro tem também as restrições que ele vai
  precisar de conhecer quando decidir — em especial que **versionar PDFs com direitos de autor
  num repositório público não é possível**, e que a saída (tornar o repo privado) tem custos já
  medidos.
  **⚠️ LIMITE DE GASTO: intermitente.** Na sessão 50 abriu a meio e voltou a fechar (5 de 11
  agentes morreram, incluindo os dois cépticos). **Vale a pena tentar um workflow pequeno
  primeiro**; se morrer, fazer o trabalho directamente — para verificação factual costuma ser
  melhor de qualquer maneira.
  **Contexto ainda válido, por ordem:**
  **(1)** **Arrumação do repo** — a análise está feita (bloco J da sessão 49), a execução não.
  Olhar os ~4 candidatos reais um a um, com os PDF a recompilar como porta. Os outros 20
  "órfãos" são falsos positivos e estão explicados.
  **(2)** **Auditoria de CONTEÚDO das 7 chaves nunca auditadas** — `angelopoulos2023conformal`,
  `vovk2005algorithmic`, `gama2014survey`, `vinh2010ami`, `rousseeuw1987silhouettes`,
  `sculley2015debt`, `worldmonitor2026`. O `citation_content_audit.md` cobriu 122 instâncias /
  52 chaves; hoje são **129 / 59**. Os metadados destas 7 já estão verificados (84/84); falta
  ler se a fonte **sustenta a frase**. É trabalho de leitura, não de agentes.
  **(3)** **Paridade EN↔PT nos sítios com citação** — nunca foi feita. O risco concreto é a
  tradução **endurecer** um verbo ("suggests" → "demonstra") e a citação passar a sustentar
  mais do que aguenta, na versão que o júri português lê. Começar pelo Cap. 2 (90 das 129
  instâncias) e pelo Cap. 6 (os veredictos das RQ).
  **(4)** **Demo e notificações** — `docs/defence/gravar_demo.md` já existe; o aluno quer
  gravar o ecrã **e** as notificações push no telemóvel. Ficou explicitamente para o fim.
  **(5)** **v4 do painel** — o estudo de mercado COMPLETOU (4 agentes; os 4 cépticos morreram
  no limite). Resultado bruto em
  `C:\Users\henri\AppData\Local\Temp\claude\…\tasks\wr951lb6c.output` (143k chars) e no
  `journal.jsonl` da run `wf_c5217b07-1db`. **Se essa máquina mudar, o ficheiro perde-se** —
  a conclusão principal fica registada aqui: o custo não é CSS nem Streamlit-tuning, é
  **carga a frio** (parse de 8,7 MB de backfill em runtime) e a recomendação é **pré-computar
  para um snapshot estático** no worker de 60 s. Briefing para sessão nova:
  [`docs/design/PROMPT_dashboard_v4.md`](docs/design/PROMPT_dashboard_v4.md).
  **⚠️ Contexto histórico abaixo (sessão 48, já feito):** `docs/design/v3_backlog.md`,
  secção **"Entrega de turno"** — tem os comandos por ordem e, a seguir, **"Promoção: a
  lista exacta do que fica por rever na tese"**, ficheiro a ficheiro e linha a linha.
  **A v3 está funcionalmente completa** (A, B, C, D, E, watchlist a 12, passo 6
  precedentes, passo 7 página do método). Sobram três coisas, e **nenhuma é código**:
  **(1)** `heroku config -s --app investigator > .env` e depois `fetch_logos.py` +
  `backfill_history.py --months 12`, que fecham o buraco de dados de XOM/JNJ;
  **(2)** rodar as 3 credenciais expostas (PAT do GitHub primeiro — `admin: true`);
  **(3)** decidir promover, que é **uma linha no `Procfile`** e abre a dívida da tese.
  **⚠️ MÁQUINA:** a sessão 47 correu no **portátil** (`C:\Users\ruifa`), que **não tem
  `.env`** — foi essa a razão de (1) ficar por fazer. A seguir é no **desktop**
  (`C:\Users\henri`, a máquina do FNSPID, com dados e torch).
  **⚠️ A DÍVIDA DA TESE É CRIADA PELA PROMOÇÃO, NÃO PELA RECONSTRUÇÃO** (o aluno sublinhou
  que é para rever a sério). Enquanto a v1 estiver no ar a tese está **correcta como está**.
  No minuto em que o `Procfile` mudar, o Cap. 4 passa a descrever um ecrã que já não existe:
  diz que a lista leva a repartição mercado/setor/empresa **na própria linha, sem clicar**,
  e na v3 isso está a **um clique** (emenda D2′) com o motor nomeado **em palavras**. Mais a
  legenda da Fig. 4.5 (descreve linhas concretas: Amazon −1,84% com +0,19% da empresa), a
  recaptura da figura (**`scripts/screenshot_app.py` aponta para `streamlit_app.py` e tem de
  passar a apontar para `dashboard.py`**), o espelho em `thesis-pt`, os 3 ficheiros de
  slides/guia, e o Cap. 5. Portas: as duas teses a 0 erros + **paridade EN↔PT por capítulo**.
- **🧩 SESSÃO 47 (2026-08-03 — executar o backlog da v3; 4 commits):**
  **(A) LEGIBILIDADE.** A pílula `UNUSUAL` estava dentro da linha do topo, a disputá-la com
  logótipo, nome, ticker e o número grande — e o nome, único item sem largura própria, era
  o único que cedia: **"JPMorgan Chase" truncava**. Passa a ter linha própria (a palavra
  mantém-se: o critério V3 exige quatro canais redundantes). Escala +1 degrau (veredicto e
  nome 12,5→14 px), `max-width` 1680→**1920 px** (num ecrã de 1920 sobravam 120 px de nada
  de cada lado), escada explícita de colunas **4/3/2/1** com `minmax(0, 1fr)`, e o "voltar"
  sobe do **fim da página** para cima do cabeçalho.
  **(B) A EXPLICAÇÃO PASSA A EXPLICAR.** "Flagged" abria com "1,5 desvios-padrão numa janela
  de 20 dias" — o **mecanismo** a quem perguntou pela **consequência**. Agora
  `verdict.FLAG_EXPLAINER`, testável ao lado das outras frases.
  **(C) MIRA NO GRÁFICO** (`x unified` + `spikemode="across"`). Obrigou a agregar as
  notícias a **uma entrada por dia** (`_news_days`): o impacto é medido por (ticker,dia),
  logo dez manchetes do mesmo dia davam dez linhas iguais na mesma caixa.
  **(D) TABELA DE EVENTOS FILTRÁVEL** — a capacidade nova. `_chart` **devolve a janela que
  desenhou** e as tabelas consomem-na, portanto gráfico e tabela não podem divergir. Lógica
  pura em `app/tables.py` (+30 testes). **`st.dataframe` foi sondado antes de decidir, e o
  resultado não foi o esperado:** *não* briga com o tema escuro — esse risco era hipotético
  —; cai porque não desenha a barra divergente e porque `format="%.2f%%"` mostrava −0,021
  como **"−0,02%"**, errado por um factor de cem e em silêncio.
  **⚠️ QUATRO DEFEITOS MEUS, TODOS APANHADOS A RENDERIZAR OU A CONDUZIR, NENHUM NOS TESTES:**
  (1) o comentário do CSS afirmava que o cartão calmo era "genuinamente mais curto" — era
  **falso** enquanto a grelha o esticava (`align-items: start` torna-o verdade);
  (2) o detalhe abria em **1D**, e nesse intervalo não há **nada** para mostrar (as três
  camadas são de dias passados e o impacto só é observável +5 dias depois) — ou seja, o ecrã
  abria sem a única coisa que existe para mostrar; defeito passa a **1M**;
  (3) `_watchlist_rows`/`row_css` eram **código morto** da lista da v2, mas a regra CSS deles
  era **geral** e teria deformado em silêncio o primeiro botão verdadeiro da página —
  precisamente os de paginação que este trabalho acrescenta;
  (4) o gráfico desenhava **13** marcas de notícia e a tabela listava **18** dias: uma
  notícia de sábado não tem barra onde pousar. Passa a ancorar na primeira sessão ≥ à data,
  que é a **mesma regra** com que `mature_entry` alinha eventos para medir o impacto. Medido
  depois: **18=18** em 1M, **64=64** em 6M.
  **📏 DUAS COISAS QUE A MEDIÇÃO CONTRARIOU, e ficam escritas em vez de silenciadas:**
  **(E) A LENTIDÃO DA NAVEGAÇÃO NÃO EXISTE.** O plano dizia "se um clique morno passar de
  ~1,5 s, reconsiderar os botões". Medido em browser real: **mediana 0,75 s morno / 0,78 s
  frio**. O 1,8 s anterior era o **primeiro** detalhe da sessão (parse dos 7,8 MB do
  backfill + `_alerts()` pela rede + SPY/XLK), pago **uma vez por processo** e não por
  clique — atribuí-lo a "navegação" era medir a coisa errada. **A decisão de manter URLs
  reais fica validada por medição.** E não foi preciso código nenhum: as dez funções de
  dados já eram `@st.cache_data` e o `session_state` já só guardava estado de interface.
  **(C2) O `_replay` NÃO É UM GANHO DE VELOCIDADE.** Ia registá-lo como tal; medido,
  `detect_all` custa **18,6 ms** sobre um ano contra 1,0 ms sobre 30 dias. O ganho real é a
  primeira troca de intervalo (~0,90 → ~0,67 s). O estrangulamento da carga a frio é
  **rede**, não cálculo — e a carga a frio (~5,5 s) continua **acima** do critério P1 (<5 s).
  **(WATCHLIST) 10 → 12, com XOM (energia/XLE) e JNJ (saúde/XLV).** Nove dos dez anteriores
  partilhavam o XLK, logo "foi o setor?" tinha quase sempre a mesma resposta por falta de
  variedade, não por ser essa a resposta. **Já se vê o efeito ao vivo:** XOM −0,98% com o
  setor **+0,93%** — o setor a puxar ao contrário. Betas estimados a sério nos dois
  (`fallback=False`). **Um teste mudou por uma razão que vale a pena guardar:**
  `test_watchlist_completa_tem_aliases` tinha os dez nomes escritos à mão e **continuaria a
  passar** depois da watchlist crescer, cobrindo dez e ignorando os dois novos sem nunca
  falhar; passa a ler o `config/alerts.yaml`.
  **(PASSO 6) OS PRECEDENTES ENTRAM NO PRODUTO — a terceira pergunta da tese.** O motor
  existe e está avaliado (RQ2), mas não estava em nenhuma das duas apps: a v1 só o expunha
  numa demonstração, a v3 não o tinha. A base de casos é a razão de ser do trabalho e era
  **invisível**. `_precedent_panel` consulta a partir da última manchete captada e mostra o
  desfecho **medido** a +5 dias, a similaridade real e de que empresa vem cada caso. Ao
  vivo, "AMD Has an Agentic AI Advantage Over Nvidia" devolve **3 casos AMD e 1 NVDA, todos
  em baixa** — o CS3 da tese a acontecer no produto. A moldura tema ≠ direcção
  (`verdict.precedent_framing`) vem **sempre**, varrida pelo mesmo teste de vocabulário.
  **⚠️ EMENDA V6′, COM O NÚMERO AO LADO:** o V6 pedia **contagem no cartão**. Não fica.
  Escrever esse número obriga a carregar o modelo semântico + a base de casos + a KB viva
  pela rede **na página de entrada**, e mediu-se: a grelha a frio passa de **6,2 s para
  13,7 s** — sete segundos e meio por um chip, contra o P1 que pede menos de cinco no total.
  **E enganei-me a procurar a causa:** componente a componente a coisa custava ~3,2 s, e
  dentro do Streamlit custa mais do dobro; andei pelo pickle do `cache_data` (0,19 s, não
  era) e pelo parse do backfill (0,24 s, não era) até fazer a experiência que decide —
  tirar só o chip e medir. **A soma das partes medidas isoladamente não é a medição do
  todo.** Ficou na mesma a correcção que a caça produziu: `_retrieval_kbs` passa a
  `cache_resource` (o `cache_data` guardava uma cópia serializada de 19,4 MB).
  **(PASSO 7) PÁGINA DO MÉTODO** (`?view=method`, critério V7) — e **fecha o buraco que o B
  abriu**: o limiar e a janela tinham saído do balão de ajuda e ficado sem casa, e um número
  sem casa deixa de ser rastreável. Traz a prova de vida ao vivo (0,667 vs 0,455), a
  latência **só porque foi medida** (208 min, n=44), as três tabelas congeladas, e o
  **resultado negativo da RQ4 a cor e não em rodapé**. `app/method.py` amarra **cada** número
  à cadeia exacta com que aparece no `.md` que o produziu, e `tests/test_method.py` abre os
  ficheiros e exige-a — se uma avaliação for recorrida, a suite parte em vez de o produto
  continuar a afirmar um número que os documentos já não sustentam. Mais quatro testes que
  fixam as **conclusões** e não só os valores (a volatilidade tem de continuar a ganhar ao
  texto; o z-score tem de disparar com amplitude ≥10× menor do que o limiar fixo).
  **Gates: 594 testes (era 537), ruff limpo, congelados byte-iguais, `app/streamlit_app.py`
  e `Procfile` intocados. Tudo verificado por captura Playwright a 1920×1080 E 1366×768.**
  **⚠️ PENDENTE QUE NÃO É CÓDIGO — SÃO CHAVES (não há `.env` nesta máquina):** XOM e JNJ têm
  **0** registos de notícia (os outros dez têm 2.424–5.632) e **sem ficheiro de logótipo**.
  Correr numa máquina com chaves, **antes da promoção**, senão os dois nomes ficam
  meio-construídos ao lado dos outros dez: `python scripts/fetch_logos.py`
  (`POLYGON_API_KEY`) e `python scripts/backfill_history.py --months 12`
  (`FINNHUB_API_KEY`).
  **🔑 GESTÃO DE CHAVES — a pergunta do aluno, respondida e registada.** *"Não se pode
  carregar dos GitHub Secrets?"* **Não.** São de **escrita apenas**, por desenho: nenhuma
  API os devolve e só são desencriptados dentro de um job a correr. Há maneira de os
  imprimir num workflow (base64, a fugir à máscara) e **não se faz** — o repositório é
  público e isso escreveria as credenciais em registos visíveis a toda a gente, ou seja
  transformaria uma rotação numa segunda fuga. **O cofre legível já existe e é o Heroku**
  (`heroku config -s --app investigator > .env`, round-trip verificado 8/8 a 2026-08-02,
  documentado em `docs/design/trocar_de_maquina.md`): é o único dos três sítios que devolve
  os valores, e é o mesmo que a produção lê, portanto há **um** sítio que pode estar errado.
  **Recomendação dada:** Heroku como fonte operacional + um gestor de senhas como cópia de
  recuperação, porque apagar a app do Heroku apaga o cofre. **Ordem de rotação:** PAT do
  GitHub primeiro (`admin: true`), chave do Heroku **por último**. **Regra:** nunca colar
  chaves no chat — o `.env` está gitignored e é lá que vão (a fuga da sessão 44 foi assim).
- **🧭 SESSÃO 46 (2026-08-03 — v3 do painel; o aluno tinha rejeitado a v2: "usability is
  messy and confusing and dirty… re-do everything"):**
  **(A) CRITÉRIOS ESCRITOS ANTES DO CÓDIGO** (`dashboard_acceptance.md` §6). Perguntei-lhe
  o que o perdia e ele escolheu **as quatro opções**, esta primeira: **"não me diz o que
  pensar"**. As quatro juntas não são sobre cores — dizem que a v2 **abre com números
  quando devia abrir com um veredicto**. É uma inversão, não uma repintura. Público
  decidido: **investidor primeiro** (a avaliação sai para **uma** página ligada); forma:
  **grelha de cartões**.
  **(B) RARIDADE QUE SE LÊ SEM ESTATÍSTICA** (`investigator/anomaly_detector/frequency.py`).
  A tradução óbvia do z-score seria uma probabilidade — e seria **desonesta**: exige
  normalidade, e os retornos têm caudas pesadas, logo estaria errada precisamente nos dias
  que interessam. Conta-se: *"6 dos últimos 249 dias moveram-se pelo menos isto"*. Hoje fica
  **fora** da contagem (senão "o maior movimento do ano" era indizível), e o `n` vem dos
  dados, nunca da constante. Medido ao vivo: `JPM +0,27% z+0,00 → 203 de 249` (o z não diz
  nada a um leigo; a contagem diz tudo) e `AAPL −7,64% z−4,60 → 0 de 249`.
  **(C) AS FRASES SAEM DO STREAMLIT** (`app/verdict.py`, 29 testes). Uma lei que só se
  verifica abrindo um browser é uma intenção — e este projecto perdeu **seis** redesenhos a
  verificar a olho. A proibição de prever (H2) passa a varrimento sobre **112 combinações**
  contra 16 palavras. O veredicto **não contém um único número técnico**; a linha do motor
  **cala-se quando o motor é a própria empresa** (repetir o que se acabou de ler não
  acrescenta nada — só fala quando *surpreende*).
  **(D) DIAS CALMOS DEIXAM DE PEDIR CONFIANÇA.** Dizia "Quiet — an ordinary day for Meta" ao
  lado de +3,23%, e ninguém tem razão para acreditar nisso. Passa a *"203 of the last 249
  trading days moved as much or more"*. Mesma linha, e **sete dos dez cartões são calmos**.
  **⚠️ QUATRO DEFEITOS MEUS, e um critério meu:**
  (1) **`ModuleNotFoundError: No module named 'app'`** na primeira execução normal — a causa
  não foi o código, foi a **verificação**: corri sempre `python -m streamlit`, e o `-m`
  acrescenta o directório actual ao `sys.path`. **Testei a coisa errada e dei por
  verificado.** Dois testes de regressão que **verifiquei que FALHAM sem a correcção**;
  a procurar a mesma classe encontrei um segundo (`config/alerts.yaml` por caminho
  **relativo** — falha aberto, logo a watchlist configurada seria ignorada **em silêncio**).
  (2) **Texto escuro sobre fundo escuro: a causa era o TEMA, não os componentes.**
  `.streamlit/config.toml` declarava um tema **claro** enquanto a v3 pinta escuro, e esse
  ficheiro governa os componentes do próprio Streamlit. Remendei-o **duas vezes** componente
  a componente antes de encontrar a origem. Alinhado valor a valor com `ui_tokens`.
  (3) **Marcadores em 1D/5D** estavam atrás de um `if not intra`: um evento visível em 1M
  desaparecia em 1D, no mesmo dia com os mesmos dados.
  (4) **`_daily` buscava 6 meses** enquanto o gráfico pedia 260 linhas para "1Y" — o botão
  1Y mostrava calado **seis meses**.
  (5) **O critério V2 estava errado e foi corrigido em voz alta** (§6.3.1): exigia o
  veredicto antes de *qualquer* número, o que obrigaria a esconder o `−7,64%`. A
  percentagem é **o facto que a frase explica**, não jargão. Um critério corrigido em
  silêncio é indistinguível de um critério contornado.
  **Gates: 537 testes, ruff limpo, congelados byte-iguais. A v1 (`app/streamlit_app.py`)
  continua implantada e INTOCADA — promoção é uma linha no `Procfile`, e não foi feita.**
  **DECIDIDO (com razões em `v3_backlog.md`):** repositório **fica público** até à entrega —
  privado **partiria a app em silêncio** (os dois apps lêem `raw.githubusercontent.com` sem
  autenticação, e esses caminhos falham abertos), limita os minutos do Actions, e **não
  revoga** as chaves expostas, que continuam a ter de ser rodadas. Alojamento: **Heroku**, e
  a razão é específica deste projecto — a sessão 31 registou que nos **IPs partilhados do
  Streamlit Cloud o yfinance é limitado por ritmo**, e essa é a fonte de dados primária de
  cada render.
- **🎨 SESSÃO 45 (2026-08-03 — o aluno rejeitou a app por inteiro: "a paleta de cores, tudo uma
  confusão… falta história… mais ícones, uniformizados… menos texto, mais visual… esquece a tua
  consciência e constrói de zero"). Reconstruído, não remendado. 4 commits, todos pushed.**
  **(A) SISTEMA VISUAL** (`app/ui_tokens.py`, novo). As cores eram escolhidas no sítio onde eram
  precisas: ao fim de cinco redesenhos havia verdes diferentes para a mesma coisa e nenhum sítio
  onde responder a "que cor é *em alta*?". Agora **quatro cores com significado** (subida, descida,
  atenção, informação) e tudo o resto cinzento frio. **Contraste MEDIDO, não escolhido à vista:**
  o `#5A6474` dava ~3,3:1 sobre `#0B0E13` e a WCAG pede 4,5:1 para texto pequeno — que aqui é
  quase tudo. Passou a 16:1 / 9:1 / **5,4:1**.
  **(B) ÍCONES — havia uma COLISÃO a sério:** `◆` era "volume invulgar" nas linhas **e** "alerta
  enviado" no gráfico; `⚑` e `○` queriam ambos dizer "detectado". Ficam **cinco, um sentido cada**
  (▲▼─ direcção · ⚑ enviado · ○ detectado-mas-travado · ● notícia); o volume passou a **texto**
  (`3.3x vol`) por ser o sexto — a partir do quinto ninguém guarda a legenda. Formas Unicode e
  **nunca emoji**: um emoji depende da fonte do sistema e já produziu aqui uma seta verde para
  cima num movimento de −7,64%.
  **(C) LOGÓTIPOS DAS EMPRESAS — 10/10** (`investigator/branding/`, `scripts/fetch_logos.py`).
  Polygon, **versionados** em `app/assets/logos/`: a app implantada desenha-os sem chave, sem rede
  e sem limite de ritmo, embebidos como `data:` URI (o navegador não faz pedidos a terceiros —
  coerente com a posição de privacidade). Degrada para as iniciais.
  **(D) A HISTÓRIA JÁ EXISTIA E NÃO ESTAVA LIGADA.** O gráfico mostrava 220 alertas enviados e,
  como os gates suprimem 9 em 10 varreduras, havia tickers com nada — enquanto o sistema tinha
  **3.331 notícias captadas e medidas** em `live_kb.jsonl` (AAPL 455, NVDA 372) sem nunca as
  mostrar. O gráfico passa a ter **três camadas**: ⚑ enviado · ○ detectado-mas-travado (replay de
  `detect_all`) · ● notícia. Em 6M a NVDA mostra ~20 detecções onde saíram 3 alertas — **o custo
  dos gates ficou visível** em vez de só se mostrarem as vitórias.
  **(E) UM ANO RECONSTRUÍDO** (`scripts/backfill_history.py`). O Finnhub gratuito serve **um ano**
  de notícias por empresa (confirmado com um pedido a Agosto de 2025). 36.642 relevantes →
  **35.583 maturadas**, 2025-08-08 a 2026-07-24, em `data/samples/backfill_kb.jsonl` (7,8 MB,
  versionado — `data/**` está gitignorado e a app implantada precisa dele). NVDA 372 → **3.715 em
  168 dias**. **Reutiliza `live_kb.mature_entry`**, o MESMO código de produção: reimplementar a
  regra de alinhamento para o passado é exactamente como se introduz lookahead sem dar por isso.
  **Três verificações:** 0 datas no futuro; **média do impacto +1d = +0,0002** (era o número que
  interessava — lookahead viria enviesado, e um retorno diário médio de zero é o que a teoria
  diz); 2.058 valores distintos, sem degeneração.
  **⚠️ DECISÃO QUE TOMEI CONTRA O PEDIDO INICIAL:** o aluno perguntou se devíamos **limpar** o
  histórico. **NÃO se limpou.** Os 220 alertas são a única prova de operação real e a latência
  medida e a pós-validação citadas na tese assentam neles. O replay escreve para **outro
  ficheiro** e o gráfico distingue-os. Um alerta reproduzido não é um alerta enviado.
  **(F) O PAINEL PASSA A RESPONDER À RQ2.** Dizia o quê/quanto/mercado-ou-empresa mas nunca
  *"já aconteceu antes, e o que se seguiu?"* — a pergunta que justifica a base de casos. Novo
  painel com o desfecho medido como **barra divergente de escala fixa**, **uma linha por DIA**
  (o impacto é medido por (ticker,dia): seis manchetes do mesmo dia desenhavam seis barras
  idênticas). Rotulado "what followed, **measured**", nunca "expected".
  **(G) LOGÓTIPO DA MARCA — questão FECHADA: fica "The Tail".** Construí duas alternativas e
  testei as três às escalas reais contra o critério já escrito em `brand.md`. "Jaws" (as maxilas
  do **Williams Alligator**, indicador que existe mesmo — seria a melhor *história*) desfaz-se num
  `<` aos 16 px, que é onde vive um favicon; o monograma "Gator G" sobrevive pequeno, como
  qualquer letra, mas podia ser de qualquer empresa com G. **A actual ganha.** As duas propostas
  ficam no repositório como registo da comparação (`logo-jaws.svg`, `logo-gator-g.svg`).
  **(H) URL do Heroku:** a app **já se chama `investigator`** — o sufixo `-ddc9d8618935` é do
  Heroku, posto em todas as apps desde 2023 e **regenerado a cada rename**. Único caminho para um
  URL limpo: **domínio próprio** (Student Pack dá um grátis; com dynos Basic o domínio e o SSL não
  custam extra). Falta o aluno reclamar o domínio.
  **⚠️ QUATRO DEFEITOS MEUS, todos apanhados a RENDERIZAR e nenhum visível nos logs:**
  (1) a **"magia" do Streamlit desenha qualquer expressão solta do script principal, inclusive
  dentro de funções**: `a.append(x), b.append(y)` é um tuplo solto e pintou **253 caixas
  `(None,None,None)`** por cima do gráfico (275 elementos markdown → 22);
  (2) a abreviatura CSS `background` repõe `background-image`, e a regra geral dos botões é mais
  específica do que a regra por linha — apagava os logótipos **em silêncio**;
  (3) **WebP não se identifica pelos primeiros bytes** (`RIFF`, partilhado com WAV): a Apple
  parecia uma empresa sem logótipo e o ficheiro chegava inteiro;
  (4) 20 pedidos em segundos contra um limite de **5/min**, num caminho que falha aberto: 9
  tickers leram-se como "sem logótipo".
  **⚠️ E UM DEFEITO DE MÉTODO, o mais instrutivo:** `ModuleNotFoundError: No module named 'app'`
  na primeira execução normal. A causa não foi o código, foi a **verificação** — corri sempre
  `python -m streamlit`, e o `-m` acrescenta o directório actual ao `sys.path`. O comando normal
  põe lá a pasta **do script**. **Testei a coisa errada e dei por verificado.** Corrigido com a
  guarda que `streamlit_app.py` já tinha, mais um segundo defeito da mesma classe encontrado a
  procurar por ele (`config/alerts.yaml` aberto por caminho **relativo** — falha aberto, logo a
  watchlist configurada seria ignorada **em silêncio**). Dois testes de regressão em
  `tests/test_dashboard_launch.py`, e **verifiquei que FALHAM sem a correcção**: um teste de
  regressão que passa sobre o defeito não prova nada.
  **Gates: 496 testes, ruff limpo, congelados byte-iguais. A app em produção NÃO foi tocada — a
  promoção é uma linha no `Procfile`.**
  **PENDENTE HUMANO (nada disto é código):** (1) **rodar as 3 credenciais expostas** — PAT do
  GitHub (tem `admin: true`, muito mais largo do que precisa), chave da API do Heroku, e a
  ALPHAVANTAGE; (2) **enviar a mensagem PT-PT** em `docs/defence/mensagem_orientador.md`;
  (3) reclamar o domínio para o URL; (4) estudo de utilidade e agradecimentos continuam
  **parados e por fabricar nunca**.
- **🚀 SESSÃO 44 (2026-08-02 — o sistema deixou de ser protótipo: está NO AR):**
  **(A) HEROKU AO VIVO.** <https://investigator-ddc9d8618935.herokuapp.com/> · dois dynos
  **Basic** (web + worker), ciclo de **60 s** em vez do cron best-effort de 1,5-2 h. Créditos:
  **saldo único de $312** (não $13/mês) a expirar 2028-07-31 ⇒ **≈22 meses** a $14/mês.
  **Três coisas que eu tinha escrito e estavam ERRADAS:** (1) Basic+Eco=$12 **não existe**, o
  Heroku recusa misturar tipos de dyno; (2) o crédito é lump, não mensal; (3) exige **cartão**
  mesmo com $312 por gastar. Tudo corrigido em `hosting.md`/`heroku_setup.md`.
  **⚠️ BUG DE PRODUÇÃO REAL, só existia no deploy:** o worker morria em ciclo de crash com
  **R15, 1,4 GB num dyno de 512 MB**. Duas hipóteses minhas falharam (threads do onnxruntime;
  tamanho da branch de dados). Só com uma **sonda no próprio dyno** apareceu: o arranque são
  281 MB, logo o pico estava no CICLO — `run_alerts` embebia **todas** as manchetes novas num
  único lote, e numa máquina nova o ficheiro de pendentes está vazio, logo *tudo* é novo. Na
  máquina do aluno nunca falhou porque lá o ficheiro já existe. Corrigido no **embebedor**
  (lotes de 32). **Ressalva medida, não assumida:** ia escrever que fatiar não altera
  resultados; medi e é **FALSO** (int8, o padding influencia: 0,022 de diferença). É
  **pré-existente**. O que importa é a recuperação: **top-3 idêntico em 8/8**.
  **(B) ALERTAS — 2 defeitos reais, achados a ler os 220 alertas enviados:** (1) o alerta
  **contradizia-se em 9 de 30 casos (30%)**: "Looks sector-wide" seguido de "specific to the
  company" (AMD −13,23% com pares a −2,0%). A verificação de setor olhava só para a DIREÇÃO,
  nunca para a DIMENSÃO. (2) **18 de 165 alertas (11%)** mostravam a **mesma manchete** como
  precedentes independentes (dedup era por (data,ticker,manchete)). Ambos corrigidos no
  caminho de PRODUTO; congelados intactos.
  **(C) BIBLIOGRAFIA — 59/59 verificadas automaticamente:** 43 DOIs resolvem no Crossref **com
  título a bater**, 8 arXiv, 6 URLs HTTP 200, 1 ISBN, 1 sem id (correto). A comparação de
  títulos apanha o DOI que resolve para OUTRO artigo — zero casos.
  **(D) ESCRITA:** 0 travessões em prosa (eram 4 por língua; os 536 restantes são tabelas e
  comentários), e a secção "Repository Organisation" e o vocabulário de controlo de versões
  saíram do apêndice.
  **(E) GUIA DE ESTUDO 80→83:** faltavam **quatro subsistemas com zero menções** (decomposição,
  narrador, volume, convergência). Três frames novos que ENSINAM.
  **(F) APP:** auto-refresh de 60 s; a linha do driver passa a falar **só quando surpreende**
  (as 5 linhas diziam todas "Specific to this company").
  **(G) CHAVES ENTRE MÁQUINAS:** o aluno já tinha cofre e não sabia — as 8 chaves estão nas
  config vars do Heroku e voltam em formato `.env`. **Round-trip verificado: 8/8 idênticas.**
  `docs/design/trocar_de_maquina.md`.
  **⚠️ FUGA MINHA:** o filtro de output só mascarava >30 chars e **expôs a ALPHAVANTAGE_API_KEY**
  (16 chars) no chat. O aluno também colou a chave da API do Heroku. **Ambas a rodar.**
  **PENDENTE:** PAT do GitHub para o write-back do histórico (sem ele o Telegram recebe em 60 s
  mas o painel não vê); a mediana de latência ainda diz 208 min porque inclui o histórico do
  cron.
  **Gates: 471 testes, ruff limpo, congelados byte-iguais, EN 107 pp / PT 111 pp, guia 83.**
- **🔬 SESSÃO 43 (o aluno pediu: validar a bibliografia a fundo "sem margem para erro ou informação
  falsa", tirar menções a repositório/ficheiros da tese, arrumar o repo, analisar o Student Pack
  para alternativa à VM Oracle, propor melhorias do site rumo ao nível worldmonitor, e propor
  metodologias de Engenharia de IA com valor real; "isto ainda não está perfeito"):**
  **7 commits, todos pushed. Tese EN 106 pp / PT 110 pp, 465 testes, 59 referências.**
  **(A) AUDITORIA DE CONTEÚDO DAS CITAÇÕES — o último risco de integridade que faltava.** O
  `citation_log` provava que cada fonte **existe**; nunca se tinha verificado que cada citação
  **sustenta a frase a que está agarrada**. Li as **122 instâncias / 52 chaves** (ch1–ch6 +
  apêndice; o Cap. 2 tem 86 das 122). **2 erros reais**, ambos corrigidos por **enfraquecimento da
  afirmação** e nunca por inventar fonte: (1) `kearney2014textual` — **anacronismo**: um survey de
  **2014** sustentava uma taxonomia de três gerações cuja terceira são modelos neuronais
  contextuais (**BERT é de 2019**); (2) `doshivelez2017rigorous` — atribuição esticada: defendem
  que a interpretabilidade tem de ser **avaliada**, mas não elegem "fidelidade" como critério
  (isso vem da *local fidelity* do LIME). Registo em `docs/decisions/citation_content_audit.md`.
  **(B) TRÊS MEDIÇÕES NOVAS (aditivas, congelados byte-iguais):**
  **B1 taxonomia de eventos** — pureza 0,712, **AMI evento 0,358 > ticker 0,188 > setor 0,130**,
  ARI 0,786; **NÃO ligada à recuperação** (silhueta 0,084 é fraca; filtrar por tipo errado deita
  fora precedentes válidos em silêncio). **B2 predição conformal** — cobertura 0,951/0,902/0,803
  (aleatória) vs 0,937/0,900/0,822 (temporal): **aguenta a 90% e 80%, parte-se a 95%**; e o número
  mais duro, **a 90% de cobertura só há decisão definida em 39,5% das manchetes** — o que **explica**
  o negativo da RQ4 por um ângulo independente. **B3 deriva** — vol20 **PSI 0,281** (significativa),
  restantes estáveis; a prevalência do rótulo **OSCILA** (0,385→0,470→0,378) em vez de ter tendência.
  **(C) CONVERGÊNCIA + VOLUME** — ideia do **worldmonitor.app**, recomendado pelo **coorientador
  Rafael Silva**; ambos **citados/creditados** na tese (pedido explícito do aluno). Detetor de volume
  = capacidade nova a **custo zero em dados** (a coluna vinha nas barras e era deitada fora). A fusão
  **ganha em 1 de 3 orçamentos** ⇒ **não entra em produção**. Achado inesperado: o peso da
  intensidade de notícia saiu **NEGATIVO (−0,283)** — mais manchetes = menos provável ser material
  (dias de conteúdo automático), o que é a **justificação empírica** da regra de derivar pesos.
  **(E) INTEGRAÇÃO COMPLETA:** Cap. 5 ganha **Estudos de Caso 5–8** (a tese tinha 4, não 5 — o plano
  estava errado); Cap. 2 secção nova "Uncertainty and Drift in a Deployed Model"; Cap. 3 os três
  protocolos; Cap. 6 duas limitações passam de **afirmadas a medidas** + duas novas + nova posição
  por exclusão. **7 citações novas verificadas contra FONTE PRIMÁRIA** (workflow de 6 agentes +
  passe adversário). **3 figuras novas** (valores entram como constantes copiadas dos .md, para
  figura e texto não poderem divergir). Slides EN+PT 22→**23 frames**; guia 77→**80 slides**.
  **⚠️ ERROS MEUS, apanhados e corrigidos (o valor está aqui):**
  (1) **A rubrica tinha um `to buy` nu** que apanhava **5.032 de 5.657** matches do balde `ma` (89%)
  com ruído automático ("157k Shares To Buy"). Se tivesse ido para o agrupamento, **todos** os
  números de pureza estariam corrompidos em silêncio.
  (2) **Comparei PUREZAS entre referências com cardinalidades diferentes** (8 tipos vs 14 tickers vs
  5 setores) e em **linhas diferentes**. A pureza depende da cardinalidade ⇒ não compara nada.
  Trocado por **AMI nas mesmas linhas**. **Sem esta correção eu teria reportado a conclusão OPOSTA**,
  com números de aparência respeitável.
  (3) **Teste conformal exigia cobertura numa divisão ÚNICA** e falhou a α=0,2 (0,780 vs 0,800). Não
  era bug: a garantia é **marginal**, vale em média sobre a aleatoriedade da calibração. Passou a
  medir a média sobre 60 divisões.
  (4) **PSI ao vivo de 2,866 está inflacionado** — a média só se desloca +0,18σ. 980 linhas = 10
  tickers × ~98 dias, e a vol20 é janela deslizante (dois dias consecutivos partilham 95% da
  informação). Registado que os dois PSI **não são comparáveis em magnitude**.
  (5) Teste de volume afirmava "volume normal não dispara" com um último dia **aleatório** que
  calhou z=2,16. Trocar a semente seria pesca ⇒ fixei o dia na mediana + teste de **taxa de disparo**
  sobre 300 séries.
  **⚠️ LIMITE MENSAL DA CONTA ATINGIDO** a meio do workflow de citações: 2 dos 6 passes adversários
  completaram (vovk, angelopoulos — não refutados), 4 não correram. **Está dito no `citation_log`**
  em vez de ficar por dizer. **Sem mais subagentes nesta conta.**
  **PENDENTE HUMANO:** (1) **agradecimentos** — a secção continua com o TODO e **não a escrevi de
  propósito**: gratidão é voz do aluno (o crédito *técnico* ao coorientador já está no corpo do
  texto). (2) apagar `thesis/build/` (permissão negada ao agente). (3) correr o estudo de utilidade.
  (4) decidir alojamento (Heroku pendente de feedback). (5) declaração de IA + licença com o
  orientador. **NÃO FEITO (fase D do plano):** reconstrução do dashboard estilo worldmonitor — a
  fazer **ao lado** de `app/streamlit_app.py`, com `docs/design/dashboard_acceptance.md` escrito
  **antes** do código.
  **(D) A RECONSTRUÇÃO PERDEU A PREMISSA, e isso ficou escrito em vez de silenciado.** Os critérios
  foram escritos (`docs/design/dashboard_acceptance.md`), e escrevê-los obrigou a reler o plano
  contra o medido: **duas das cinco ideias que davam identidade à reconstrução caíram** (score de
  convergência: ganha em 1 de 3 orçamentos; badges de tipo de evento: silhueta 0,084 e rubrica a
  cobrir 15,1%). Sobram densidade, faixa de contexto e paleta de comandos — todas de **forma**,
  nenhuma de **conteúdo**. Critério novo **H4** ("nenhum score que a medição não sustente") liga a
  avaliação ao produto. **Feito o caminho aditivo:** a app mostra **volume** ("3,2× usual volume",
  e **silêncio** quando é normal); uma só busca serve preço e volume (`_price_frame` em cache).
  Verificado **ao vivo**: os dois maiores movers tinham 3,3× e 2,7× o habitual; um terceiro
  sinalizado tinha volume normal e não disse nada.
  **(F) VARREDURA DE CONSISTÊNCIA:** apanhei que **eu** tinha introduzido vírgulas decimais em modo
  matemático na tese PT, quando a convenção são **pontos** (165 vs 21) e a regra do projeto é
  "números **idênticos**; só a língua muda". **24 corrigidas** (14 minhas + 4 pré-existentes no
  ch4). Verificado por comparação de **todos** os tokens numéricos das duas teses: nenhum valor
  distinto existe só numa delas. Falso alarme investigado e descartado: o "0.989" é o recall do LOF,
  idêntico nas duas.
  **(G) ALOJAMENTO decidido com ofertas verificadas a 2026-08-01** (`docs/design/hosting.md`): a
  **DigitalOcean fechou a janela ontem** ("through 7/31/26"); **Heroku $13/mês × 24 meses** é a
  recomendação (Basic $7 sempre-ligado + Eco $5 = $12, dentro do crédito), e compra a passagem de
  cron best-effort 1,5-2h para **polling de 60 s**. Contra o Azure não é o preço, é a **forma** do
  crédito ($100 de uma vez esgota sem aviso). Conselho: **ativar já** e manter o ticket da Oracle
  aberto.
  **(H) MAPA DE COMPETÊNCIAS** (`docs/defence/mapa_competencias.md`): cada área ligada a um
  artefacto **e a um número**, mais os **buracos ditos primeiro** (sem RL, sem multi-agente, sem
  visão). ⚠️ **Os nomes das UC do MEIA NÃO estão no repositório e não os inventei** — o documento
  diz ao aluno, no topo, que tem de os copiar do plano de estudos. Só 3 aparecem nos registos.
  **Estado final: 14 commits, tudo pushed, árvore limpa. 466 testes, ruff limpo, congelados
  byte-iguais. EN 106 pp / PT 110 pp (0 erros, 0 indefinidas), slides 23=23, guia 80, paper 4
  (verificado sem afirmações obsoletas). Paridade 52=52 secções, 63=63 figuras/tabelas, 128=128
  citações; três vias 59 bib = 59 citadas = 59 renderizadas, 0 órfãs.**
- **🧭 SESSÃO 42 (o aluno rejeitou o produto por inteiro: "the product sucks… the streamlit is
  completely dogshit… the alerts come too late… the AI usage is so short"; pediu repensar do zero,
  worldmonitor.app como referência de ambição, e disse "não tenho medo de mudar tudo"):**
  **Plano-mestre novo: [`progress/PLANO_V2.md`](progress/PLANO_V2.md)** (substitui `PLANO_MELHORIAS.md`
  como plano ativo). **Método:** workflow multi-lente (5 lentes — trader ativo, investidor de longo
  prazo, análise competitiva, examinador do currículo MEIA, crítico de viabilidade) + 2 críticos
  adversários + síntese. **A revisão adversária corrigiu 3 erros meus:** (1) `abnormal_returns`
  **NÃO** está adormecido — é usado em `triage/dataset.py:102` para construir o rótulo da RQ4, logo
  os congelados assentam nele (o que falta é decomposição **contemporânea**, com beta rolante);
  (2) `beta=1.0` em `event_study.py` é atacável por qualquer arguente com finanças; (3) a entrada
  do CLAUDE.md sobre "thesis-pt ch2–ch6 = scaffolds vazios" era **falsa** (medido: 32k/55k/30k/46k/15k).
  **DECISÃO ESTRUTURANTE — duas pistas:** *Track A* = tese, aditivo, congelados byte-iguais, entrega
  13/09; *Track B* = ambição de produto (worldmonitor-style, redes sociais, mais feeds), **depois**
  da entrega, entra na tese só como Trabalho Futuro. **Decisões do aluno:** tempo real = **polling
  60s na VM Oracle** (WebSocket CORTADO — ~30h, não responde a nenhuma RQ, ambas as personas dizem
  não notar 5s vs 5min); **cortes aceites na íntegra** — price targets de analistas (contradiz "nunca
  prevê preços"), carteira/holdings (RGPD + fronteira de aconselhamento MiFID II), insider/MSPR/SEC,
  reescrita do Streamlit do zero (4 redesenhos já feitos, critério estético sem condição de paragem),
  chatbot multi-turno/multi-agente (um LLM com 5 ferramentas não é multi-agente — o júri reconhece),
  RQ5/RQ6 novas (renumerar = churn em ch1/ch6/abstracts/paper/19 slides/guia 77/defesa). Cada corte
  vira **parágrafo justificado no Cap. 6**. **Logo: conceito "The Tail" escolhido** (traço contínuo
  que é cauda de jacaré e linha de mercado; o atual falha a 16px e o olho de predador é contra-mensagem).
  **worldmonitor.app a CITAR na tese + Rafael Silva (co-orientador) a CREDITAR** — recomendação dele;
  ideia a adaptar = **convergência multi-sinal**.
  **✅ FEITO (3 commits, 249 testes verdes, ruff limpo, congelados byte-iguais):**
  **(A1) A latência passou a ser mensurável — não era, de todo.** `HistoryEntry` só guardava a data
  ao dia e `parse_finnhub_news` truncava o epoch exato do Finnhub, deitando a hora fora ⇒ nenhuma
  afirmação de latência tinha prova, nem retroativamente. Novos campos opcionais e retrocompatíveis
  `event_at`/`detected_at`/`sent_at`/`price_source` + `latency_seconds()` (facto→entrega, a que o
  utilizador sente) e `pipeline_seconds()`; `NewsItem.published_at` (Finnhub + RSS), com `date`
  intocado. **Bug latente corrigido:** `parse_jsonl_lines` rebentava com campos desconhecidos ⇒
  acrescentar um campo ao esquema faria a app implantada **deixar de ver os alertas novos em
  silêncio**; agora descarta o excedente. Proveniência de preços em `prices.py`
  (`last_price_source`/`price_source_log`/`reset_price_source_log`) — a cadeia de 5 fontes sempre
  soube qual serviu, o valor era impresso e deitado fora.
  **(A6) Funil de gates** `investigator/gate_log.py` — regista ONDE cada ticker morre
  (no_news/none_relevant/stale/weak_precedent/triage_suppressed/error/alerted), acumula na branch de
  dados, escreve também em dry-run. Retroativo é impossível (o log de decisões só é escrito DEPOIS
  dos gates de frescura e similaridade) — daí instrumentar. **1.ª medição real (dry-run 2026-07-29):
  9 em 10 tickers silenciados numa só varredura — 7 pelo chão de similaridade, 2 pela triagem — e as
  margens são minúsculas: MSFT 0,42 · NFLX 0,41 · GOOGL 0,44 · META 0,44 vs `min_similarity 0.45`;
  AAPL P=0,43 e NVDA P=0,48 vs gate 0,50. Quatro falham por ≤0,04.** Explica o mistério do
  `alert_funnel` (AAPL 135 manchetes → 0 alertas): não era relevância, eram os dois últimos gates.
  **(A3) Varrimento de política** `scripts/evaluate_policy_sweep.py` (aditivo; reproduz os congelados
  ao milésimo, vol 0,542 / contexto 0,538, Δ +0,000): τ* por rácio de custo R=custo(falha)/custo(falso
  alarme) — R=0,5→0,64; R=1→0,49; R=2→0,41; R=5→0,25 — e o **rácio IMPLÍCITO do τ=0,5 ≈ 0,9**
  (o sistema assumia que perder um movimento real custa quase o mesmo que um falso alarme; sob custos
  iguais o ótimo é 0,49, portanto o 0,5 fica **vindicado mas agora derivado**). **Veredicto honesto:
  o score aprendido NÃO ganha consistentemente a orçamento igual** (top-2 +0,005, top-5 −0,015,
  resto empate) ⇒ o negativo da RQ4 aguenta também em métrica operacional. **Erro apanhado a meio e
  documentado no próprio .md:** a 1.ª versão ordenava MANCHETES e dava Δ=+0,000 em todos os
  orçamentos — o rótulo é por (ticker,dia), logo o top-k enchia-se de cópias do mesmo nome; agregar a
  (ticker,dia) antes de ordenar corrigiu a unidade de análise e os empates perfeitos desapareceram.
  **(A1c) `docs/design/cadence_contract.md`** — a promessa numa página: o que é enviado (nota de
  abertura + resumo de fecho **garantidos** todos os dias úteis, para o silêncio ser legível), o que
  **nunca** é enviado, os 5 gates com o custo medido de cada um, e de onde vem cada constante.
  **(A2) Decomposição contemporânea** `investigator/correlation_engine/decomposition.py` —
  a linha que responde à 1.ª pergunta de qualquer investidor: *"é a minha empresa ou é o
  mercado?"*. Ao vivo: `AMD -8,50% = +0,61% mercado · -3,60% setor · -5,51% empresa`.
  Módulo NOVO, separado de `event_study.abnormal_returns` (que **não** está adormecido —
  constrói o rótulo da RQ4 — e usa janela FUTURA com beta implícito 1,0). Dois fatores com o
  setor ORTOGONALIZADO contra o mercado; betas só com dados ANTERIORES ao dia explicado.
  **2 erros meus, apanhados a validar com dados REAIS:** (1) corte rígido de beta em ±4 — a
  mesma constante por justificar que o projeto está a corrigir; a AMD dava β=4,43, caía num
  fallback silencioso de β=1 e atribuía os −8,5% INTEIROS à empresa → substituído por
  encolhimento ponderado pela PRECISÃO (Vasicek); um peso fixo (Blume 2/3) também não servia,
  encolhia um β exato de 2,0 para 1,67. (2) `driver` escolhia a maior componente em MÓDULO:
  NVDA +0,25% com setor −1,54% dizia "foi o setor" quando o setor puxou ao CONTRÁRIO.
  **(A5) Narrador ancorado** `investigator/narrator/` — o LLM escreve a LÍNGUA, nunca os
  factos. **Red team de 3 adversários (cada um obrigado a REPRODUZIR com Python) demoliu a
  v1: 29 furos.** Os piores: `"AMD gained 8.50%"` passava com o motor a calcular −8,50%
  (o conjunto permitido fazia `lstrip("+-")`); e apóstrofos de contrações (`it's`, `isn't`)
  eram lidos como aspas, criando "citações" falsas que isentavam números injetados e
  previsões. **Lição estrutural: uma blocklist de linguagem natural perde sempre** (paráfrases
  infinitas vs lista finita) → v2 inverte para **allowlist**: vocabulário fechado (~360
  palavras neutras), negativos só válidos COM sinal, só aspas duplas verdadeiras, atribuição
  validada contra a evidência, normalização NFKC + rejeição de dígitos não-ASCII. Verbos
  direcionais FORA de propósito (a direção vive no sinal, que é verificável). Os 21 exploits
  ficaram como regressão permanente (`TestRedTeam`), 21/21 bloqueados.
  **Arnês ao vivo (36 chamadas reais):** groq 18/18 respondeu, 2 violações pré-guarda;
  gemini 15/18, 1 violação; **violações ENTREGUES: 0** em ambos. Duas métricas de propósito:
  pré-guarda mede o MODELO, entregue mede a GUARDA. Limitação declarada: a métrica entregue é
  circular (mesmo verificador decide e avalia) — daí o corpus do red team a complementá-la.
  **Fornecedores sondados ANTES de depender:** a suposição inicial (Gemini principal) estava
  ERRADA — 2.5-flash dá 404 "no longer available to new users", 2.0-flash dá **429 à primeira
  chamada** numa chave nova, e alguns modelos devolvem 200 SEM TEXTO (gastam o orçamento a
  "pensar"). Ordem invertida por MEDIÇÃO: **Groq `llama-3.3-70b-versatile` (0,6 s) → Gemini
  `gemini-flash-lite-latest` → template**. `scripts/probe_llm.py` re-corre isto antes da defesa.
  **(A5c) Narrador ligado ao runner**, `narrator.enabled: false` por defeito — ADITIVO: se
  falhar/rejeitar, o alerta sai EXATAMENTE como hoje (nunca se antepõe o template, que só
  repetiria o corpo). Uma linha de config para ligar.
  **(APP) Redesenhada contra critérios ESCRITOS ANTES do código** (`docs/design/app_acceptance.md`)
  — a app tinha sido redesenhada 4× e rejeitada sempre por critério estético, que não tem
  condição de paragem. **3 ecrãs** (Today / Ticker / Method), um por pergunta do
  posicionamento; a decomposição aparece na PRÓPRIA linha do mover (sem clicar); a promessa
  aparece **uma** vez; a latência só se mostra quando foi MEDIDA (ao vivo: 179 min = o custo
  do cron, agora visível). **15 testes = os critérios em forma executável.** Correção de
  honestidade apanhada na captura ao vivo: "moved unusually" incluía um z=+1,03 abaixo do
  limiar → "stood out … (K past the alert threshold)". Fig 4.5 recapturada, texto+legenda
  reescritos EN+PT; teses 90/92 pp, 0 erros, paridade 51=51 secções e 53=53 figuras/tabelas.
  **(A4) Estudo de utilidade PRONTO A CORRER** — era o atrito, não o desenho, que o travava.
  `scripts/build_usefulness_pack.py` gera de 177 alertas REAIS: 6 estímulos A/B (com 2 casos
  tema≠direção garantidos), contrabalanço, CSV e guião do facilitador;
  `scripts/analyse_usefulness.py` fecha com Wilson + Wilcoxon (só a N≥8, limiar fixado ANTES
  dos dados, com teste que falha se alguém o baixar = p-hacking visível no diff). **Falha
  metodológica apanhada antes de contaminar:** a condição A cortava na 1.ª linha, o que para
  NOTÍCIA é só um cabeçalho — a condição A ficaria SEM CONTEÚDO e a B ganhava por omissão.
  Pipeline verificado com dados sintéticos, **apagados a seguir** (0 fabricação no repo).
  **(TESE) Camada de posicionamento (o pedido de "marketing", como conteúdo académico):**
  Cap. 1 reescrito à volta das **três perguntas**, cada uma mapeada no problema técnico
  correspondente + as duas personas que querem coisas OPOSTAS (permissão para não fazer nada
  vs contexto a chegar com o alerta) + a recusa de prever como RESTRIÇÃO DE DESENHO;
  Cap. 2 nova matriz que pontua as ferramentas contra as três perguntas, incluindo o
  **assistente LLM genérico** (falha por ancoragem, não por fluência: sem volatilidade do
  título, sem beta, casos passados RECORDADOS e não recuperados);
  Cap. 4 nova secção **Casos de Uso** (UC1–UC5 + diagrama ligado às personas; UC4 com o
  argumento explícito de porque um evento agendado não viola a não-previsão);
  Cap. 6 veredictos estendidos (RQ3 ganha a fidelidade da linguagem gerada e admite a
  circularidade da métrica entregue; RQ4 ganha o enquadramento de política) + **nova secção
  "Posições Assumidas por Exclusão"** com cada corte justificado.
  **Sem citações novas** (reusa wu2023bloomberggpt, dacunto2019robo, lipton2018mythos,
  rudin2019stop). Teses **EN 92 pp / PT 96 pp**, 0 erros, 0 refs/citações indefinidas,
  paridade 110=110 idêntica por capítulo.
  **(MARCA) "The Tail" substitui "The Stare"** — escolhida com as 3 variantes às escalas reais e
  a marca antiga como CONTROLO. A anterior **falhava a 16 px** (o sobrolho fundia-se com o olho, a
  linha de mercado desaparecia), metia 3 metáforas num ícone, e o olho de pupila em fenda era
  contra-mensagem. Nova: um traço contínuo que é cauda de jacaré **e** linha de mercado.
  4 ficheiros (`logo.svg` claro `#0A8F52` · `logo-dark.svg` `#00E37A` · `logo-mono.svg`
  currentColor · `icon.svg`, o único com contentor e com o glifo ampliado 14%); duas cores porque
  um verde intermédio ficaria apagado no escuro e fraco no claro; glifo NU porque um quadrado
  escuro obrigaria um bloco a toda a superfície clara. `.streamlit/config.toml` retemperado
  (verde-pântano e dourado retirados). `docs/design/brand.md` com o teste de aceitação que a
  marca antiga falhava. **Fig 4.5 recapturada e apanhou uma ilustração MELHOR:**
  `AMZN -1,84% = -1,66% mercado · -0,37% setor · +0,19% EMPRESA` — a ação caiu mas a contribuição
  própria foi POSITIVA ("moved with the whole market"), que é exatamente o valor central para a
  persona do detentor de longo prazo. Legenda reescrita EN+PT à volta desse caso.
  **(A7) ONNX em evidência na tese** (Cap. 4, nova subsecção): o artefacto de deep-learning
  **engineering** mais forte do projeto estava invisível, só num `.md`. O ponto: as resoluções
  ingénuas eram manter a stack pesada (a app pública não corre) ou trocar por um modelo DIFERENTE
  em produção — pior, porque a avaliação passaria a descrever um sistema que ninguém usa. A
  resolução foi exportar o MESMO modelo (ONNX int8, ~23 MB, CPU, sem framework) e PROVAR a
  fidelidade: cosseno 0,992 nos embeddings e, o que mais importa, **top-3 idênticos em 20/23
  consultas** com 96% de vizinhos partilhados (divergências = empates no 3.º a ~0,001). Mais o
  SHA256 fixado, que faz um download corrompido **falhar fechado** em vez de mudar em silêncio o
  que o sistema entende por "semelhante". Fecha parcialmente ANN/Deep Learning e
  Privacidade/Segurança **sem uma única experiência nova**.
  **PENDENTE do aluno:** (1) **P1 — rever a app**; depois disso ela CONGELA até à entrega.
  (2) **correr o estudo de utilidade** (6–10 pessoas, ~15 min cada) — fecha a única linha
  "em aberto" do Cap. 6; precisa de tempo de calendário para recrutar.
  (3) conta **Oracle Cloud** (desbloqueia o polling; cliques, não engenharia).
  (4) decidir se liga `narrator.enabled` em produção.
  **Fable:** usado no narrador + redesenho da app (semana 3). A seguir: prosa da tese
  (semanas 4–5) e slides/marca (semana 6) — não gastar em plumbing/testes/tradução.
- **🎬 SESSÃO 41 (cont. — demo para a apresentação: app redesenhada + replay histórico; commits `968029a`+`94726ab`, PUSHED):**
  o aluno pediu uma demo (Telegram + Streamlit a funcionar) e criticou a app ("both suck") + alertas
  atrasados (NVDA −5% não alertado "porque abriu logo mal"). Analisei criticamente as ~10 ideias dele
  (single-page, big charts ao vivo, notificações no separador, logos, troca de bolsa, **replay do
  passado**) e, em modo tese-primeiro, ele escolheu a opção delimitada **"Demo limpa + replay
  histórico"** (NÃO a reescrita do zero — risco de brinquedo/scope-creep vs. âmbito US + APIs grátis +
  Streamlit não é framework de streaming + churn da Fig 4.5). **Feito:** (1) **motor de replay**
  `detect_all` em `anomaly_detector/detector.py` (a MESMA norma z-score sem lookahead de `detect_latest`,
  aplicada a cada dia da série → todos os eventos que o método realmente sinalizaria; +2 testes,
  incl. consistência com `detect_latest`). (2) **App single-screen limpa** — `_replay_anomalies` povoa
  o gráfico grande com triângulos ▲verde/▼vermelho (movimento abrupto detetado, tooltip com z-score) +
  círculos de notícia do registo partilhado; cortado o ruído (mascote/saudação/painel admin/faixa de
  tickers/`_overview_*`); intervalo 6M por defeito para o replay aparecer à abertura. (3) **Fig 4.5
  recapturada** (Playwright, --height 1320) — dashboard novo com o replay visível; **texto + legenda
  ch4 reescritos EN+PT** (descrevem o replay honestamente: recalculado sobre o intervalo, ≠ "nunca
  recalculado" antigo). (4) **mascotes órfãs removidas** (`mascot_{day,night}.svg` — a app já não as usa;
  git preserva). **Gates:** **224 testes + ruff verdes; teses compilam 90/94 pp, 0 erros, 0 refs
  indefinidas; congelados byte-iguais.** **NÃO fiz (com razão, comunicado ao aluno):** reescrita do zero
  da app; per-exchange open/close (scope-creep US); "fix" ao atraso dos alertas — é **limitação de
  infra grátis** (cron do GitHub Actions é best-effort ~1,5-2h, sem servidor always-on; tempo-real exige
  o caminho VM `run_alerts.py --watch`, já desenhado mas não implantado pelo aluno). **PENDENTE humano:**
  gravar a demo (guião dado: workflow "Alerts" → canal Telegram + app ao vivo; plano-B vídeo pré-gravado).
  **✅ AUDITORIA DE NÍVEL DE JÚRI (2026-07-28, feita à mão — o workflow de 6 revisores bateu no
  limite de conta, padrão do projeto):** varri 6 dimensões e o corpus volta **LIMPO**. (1) Números:
  P@5 `0.514→0.595`, triagem `0.542/0.496/0.632/0.163`, embedders `0.420/0.514/0.538/0.504/0.513` —
  consistentes em tese EN/PT + paper + slides EN/PT + guia + docs de defesa; **0 restos de "RQ2=futuro"**
  (o passe adversário anterior já os limpara). (2) Referências: **52 entradas .bib = 52 chaves citadas =
  "52 verificadas"** (README/RELATORIO), 0 indefinidas, 0 órfãs (bib PT partilhada). (3) Figuras: **14
  referenciadas = 14 ficheiros, 0 órfãs**; `thesis-pt` partilha as figuras da EN via
  `\graphicspath{{../thesis/}{./}}` (por desenho — daí a Fig 4.5 nova fluir para a PT). (4) **Paridade
  EN↔PT total:** secções 58/58, ambientes figure/table 50/50, idênticos por capítulo. (5) Honestidade:
  abstract + veredictos RQ **exemplares** ("no text model beat the volatility baseline… reported as it
  stands"; RQ3 "útil ainda em aberto, sem estudo humano"; 0 afirmação de previsão). (6) Higiene: único
  reparo = `make_public_bundle.py` exclui `docs/internal/`+`docs/_archive/` já inexistentes — **no-op
  defensivo, não defeito** (exclui corretamente docs/defence, progress, slides, CLAUDE, CHECKLIST,
  RELATORIO que EXISTEM). **Veredicto: tese examiner-ready; nada a corrigir.**
- **🔬 SESSÃO 41 (cont. — reforço de ENGENHARIA DE IA; programa A+B+C+D no PC com FNSPID+torch):**
  avaliação adversária multi-agente (5 arguentes → veredicto "solid") identificou os pontos finos;
  executei 4 melhorias REAIS (aditivas; congelados intactos; reproduzem os pontos ao milésimo; 0
  fabricação; venv `.venv` 3.12 tem torch/sbert; embeddings MiniLM/FinBERT em cache
  `data/_cache_triage_*.npy`). **A** incerteza — `scripts/evaluate_triage_uncertainty.py`: bootstrap
  por cluster (ticker,dia) → IC 95% + Δ emparelhados; o "texto piora" é **cluster-robusto**
  (context−full +0,043, IC exclui 0, P=1,00), mas as marginais são largas (±0,05) → reportar 3 casas
  era enganador. **B** embedders — `scripts/evaluate_retrieval_embedders.py`: FinBERT **0,420** (pior),
  E5 0,504 / BGE 0,513 (empatam) vs MiniLM 0,514 → escolha do embedder validada por MEDIÇÃO (fecha
  "evitaste o FinBERT / fronteira datada"). **C** RQ2 à escala — `scripts/evaluate_retrieval_fnspid.py`:
  P@5 **0,595** em 80k (> 0,514 preliminar) valida o retrieval à escala; consistência de direção 0,708
  quase no chão do acaso 0,688 → **tema≠direção quantificado**. **D** RQ4 re-teste justo —
  `scripts/evaluate_triage_fairtext.py`: C afinado + PCA do bloco de texto + FinBERT → o texto **NÃO**
  bate a volatilidade (melhor texto 0,533 < vol 0,542); o PCA recupera o full de 0,499→0,533 (o
  congelado 0,496 estava EM PARTE deprimido por dimensionalidade — nuance honesta, o arguente tinha
  razão nesse ponto), mas nunca acima do contexto → **negativo da RQ4 robusto, não sub-ajuste**. Docs
  novos: `docs/evaluation/evaluation_{triage_uncertainty,retrieval_fnspid,retrieval_embedders,triage_fairtext}.md`.
  **✅ INTEGRADO NA TESE (bilingue EN+PT) + materiais de defesa atualizados:** Cap.6 — RQ2 subiu de
  "preliminar" a **"validada à escala"** (P@5 0,595) + tema≠direção quantificado; RQ4 ganhou a cláusula
  de **robustez** (ICs por cluster + re-teste justo); figura limitações→futuro atualizada. Cap.2 — o
  benchmark de embedders (FinBERT pior, modernos empatam) fecha o "argumentaste em vez de correr".
  Teses compilam **90/92 pp, 0 erros, 0 refs indefinidas**. `guiao_de_defesa.md` + `simulacro_defesa.md`
  atualizados às novas verdades (RQ2 vira força; RQ4 ganha a resposta ao "artefacto"; +pergunta do
  embedder). A narrativa "simplicidade venceu" MANTÉM-SE (o texto continua a perder, agora à prova de
  bala). **Gates verificados VERDES** (venv `.venv` 3.12 corre o pytest AQUI): ruff limpo (os 4 scripts
  novos ficaram ruff-clean, linhas <100 sem `;` via `ruff format` + cortes cosméticos que NÃO mudaram
  números), pytest exit 0 (200+ testes, 2 gated skipped), LaTeX 0 erros nas 7 peças. **Verificação
  adversária** (workflow de 4 arguentes) apanhou 5 restos obsoletos de "RQ2=trabalho futuro" (paper/
  guia/README/tese ch3 EN+PT) — todos corrigidos. **PENDENTE humano:** o aluno rever os 4 docs de
  avaliação novos + a integração na tese antes de entregar.
- **🎓 SESSÃO 41 (cont. — modo coorientador exigente; "tese primeiro"):** iterações pequenas.
  (1) **Sincronização documental:** contagens frágeis de testes (145/202 → **"200+"** estável;
  reais 228 `def test_`), slides (71/76 → **77**), páginas (86 → **90/92**) corrigidas em
  guia/README/RELATORIO; paper verificado **sincronizado nos números** (0.514/0.542/0.496/0.271…).
  (2) **Limpeza do repo (267→258 ficheiros):** removidos `docs/_archive/` (6), `product_critique.md`,
  `ROOT_PROMPT_CLAUDE_CODE.md`, `evaluation_triage_smoke.md` + refs corrigidas; **scripts/evaluation/
  models MANTIDOS** (= reprodutibilidade da tese, não lixo). `INDEX.md` mapeia o repo.
  (3) **Alertas — decisão tese-primeiro: NÃO reescrever agora.** O CS3 mostra um formato limpo que o
  código já não produz (derivou verboso), mas reescrever `explain_news_impact` obrigava a mexer em
  testes que **não consigo correr aqui** (venv fora do PATH) + exemplo congelado bilingue → risco
  desproporcionado dias antes da entrega, e é *produto* (abaixo da linha de prioridades). Redesign
  (antes→depois já esboçado) fica **pós-submissão**. O reframe importante: notícia positiva →
  precedentes de queda **é o CS3 (tema≠direção), uma FORÇA**, não uma fraqueza.
  (4) **Leitura crítica (prioridade nº1):** abstract + ch6 (veredictos RQ + limitações) + RQ ch1↔ch6
  **honestos, examiner-ready, 0 sobre-afirmação** — dito claramente ao aluno.
  (5) **Declaração de IA alinhada à decisão registada** ("sem nomear o produto"): removido
  "(notably Claude Code)"/"(nomeadamente o Claude Code)" da tese EN+PT + README — continua honesta
  (declara o uso de IA, sem subestimar); **0 menções ao produto em conteúdo visível**. Gates: teses
  **90/92 pp 0 erros**, slides 19/19, guia 77, 0 `.py` tocado. **Estado: no ponto de entrega ao
  orientador** nos eixos que controlo (consistência/organização/honestidade); resto = humano (redação
  da declaração + data + licença + leitura final) e fase de defesa.
- **🧹 SESSÃO 41 (cont. — limpeza para entrega ao orientador):** o aluno pediu (a) apagar qualquer
  frase de *gestão de impressão* nos OUTPUTS (tese/slides/paper/README/RELATÓRIO/apêndice) — nada que
  sugira conteúdo feito para *parecer* não-IA ou "apresentável de propósito"; (b) um índice claro do
  repositório; (c) remover lixo, pronto a enviar sem parecer "demais". **Varredura multi-agente** (só
  2/6 agentes completaram — resto bateu no limite de conta; verifiquei o resto eu próprio, padrão da
  sessão). **Purga de tells (EN+PT, byte-paridade):** apêndice "Proof of Work"→"Every Number Traced to
  Its Source"; "The system really ran"→"Live operation"; removidos "prova de trabalho", "200 commits
  como prova de esforço" e o "digitado à mão" duplicado; ch3 "a question an examiner would ask"→"que
  naturalmente se coloca"; ch4/ch3 "recorded openly rather than hidden" / "em vez de escondido"
  removido nas 2 línguas. **A declaração honesta de IA no front matter MANTÉM-SE** (regra do projeto —
  nunca encobrir; só se removeu a *meta-comentário defensivo*, não a verdade). RELATORIO/README:
  "para mostrar ao orientador/júri"→descrição por conteúdo; guião de defesa: removida a pergunta-ensaio
  "usaste IA?" (fica só o lembrete honesto de finalizar a declaração com o orientador). **Apagado
  `docs/design/migrar_repo.md`** (fora de âmbito; refs corrigidas em
  CHECKLIST/RELATORIO/public_bundle/docs). **Novo `INDEX.md`** na raiz (mapa do repo, ligado do topo do
  README). **Sem lixo rastreado** (o `.gitignore` já cobre build/caches; 0 artefactos LaTeX/pyc
  commitados). **Contagens corrigidas:** tese EN **90 pp** / PT **92 pp** (compilam a 0 erros, 0 refs
  indefinidas, 0 `??`). 0 ficheiros `.py` tocados ⇒ testes/ruff inalterados (CI revalida no push).
- **🔎 SESSÃO 41 ("improve everything" — worktree `general-improvements-0ba2e9`):** varredura
  de melhoria em modo Ultracode. Baseline verde (197→202 testes, ruff limpo). Lancei um
  **workflow multi-agente find→verify** (7 finders × verificação adversária) sobre
  investigator/, app/, scripts/ — os finders correram (11 achados com prova) mas os
  verificadores **bateram no limite de sessão da conta** (reset 00:10 Lisboa), por isso os
  **verifiquei eu próprio** contra o código real e apliquei só os seguros. **2 commits (sem
  trailer de co-autoria):** `045abe1` (10 correções + 5 testes) e `f135d14` (contagens de teste).
  **10 correções (congelados byte-iguais — models/, docs/evaluation/, data/, thesis*/, paper/,
  slides/ intactos):** (1) app `@st.fragment(run_every="120s"→120)` — o caminho
  `pd.Timedelta(str)` do Streamlit emite a deprecação "generic unit for timedelta" sob
  numpy≥2.5 e falharia num numpy futuro (era a origem do aviso que abortava test_app_triage
  sob -W error). (2) `parse_rss` a partir de bytes — feeds reais com declaração de codificação
  faziam `ET.fromstring(str)` levantar ValueError (RSS cego). (3) `merged_precedents` tolera
  data corrompida quando `max_age_days` está ativo (helper `_within_age`, fail-open como
  `recency_weight`). (4) `kb_query_embedder` só decide a dimensão com um embedding REAL (salta
  registos sem ele) — não escolhe HashingEmbedder(64) por engano numa KB 384-d. (5)
  `fetch_alphavantage_daily` LEVANTA na janela vazia (mantém o contrato da cadeia). (6)
  `run_cycle`: `send_message` em try/except — envio intermitente já não aborta o ciclo. (7)
  `evaluate_per_sector` generaliza o `p5` hard-coded para ks[0] (byte-igual com `--k` default;
  sem KeyError quando --k omite 5). (8) `fetch_finnhub_news` mostra bruto/limitado (truncagem
  visível). (9) `build_dataset.fetch_closes` cache por (ticker,start,end) (sem reuso silencioso
  de série estreita). (10) `fig_alert_funnel` janela "n/a" na história vazia (sem IndexError).
  **+5 testes de regressão** (RSS bytes; max_age data inválida; AV janela vazia; kb_query
  embedder ×2). **Contagens de teste** no README/RELATORIO 189/167→202. **⚠️ ADVISORY p/ humano
  (NÃO aplicado — toca congelado / semântica de produção):** (a) **numpy drift** — o venv deste
  PC está em **numpy 2.5.0 / pandas 2.3.3** mas `requirements.txt` fixa **2.1.3 / 2.2.3**; os
  bundles joblib congelados emitem a deprecação "Setting the shape" ao carregar sob 2.5 e
  **falharão** num numpy futuro → recriar o venv a partir do pin, OU re-serializar os modelos
  com probe numérico byte-igual (procedimento de sessões anteriores; toca congelado). (b) `run_cycle`
  **grava o estado ANTES do envio** e o estado mistura marcas-do-dia + offset do bot: apliquei só
  a metade segura (try/except); a semântica mais funda (não queimar marcas sem entrega; separar
  offset das marcas) fica para revisão humana. **PENDENTE do workflow (limite de conta):** as
  dimensões **simplify / test-gaps / docs-bilingue** não completaram — re-correr após o reset.
  **📊 ~~Paridade bilingue medida~~ — ⚠️ ENTRADA OBSOLETA, RISCADA A 2026-07-29.** Dizia que
  só ch1+frontmatter estavam traduzidos e que **ch2–ch6 eram "scaffolds vazios"** no thesis-pt.
  **É FALSO.** Medido no disco a 2026-07-29: ch2 32.179 · ch3 55.535 · ch4 30.264 · ch5 46.556 ·
  ch6 15.407 bytes. **A tese PT está traduzida** (a entrada posterior da auditoria, que reporta
  paridade 58/58 secções e 50/50 ambientes figure/table, é a correta). Esta linha ficou aqui a
  enganar sessões seguintes — se voltar a aparecer noutro sítio, apagar.
  **Gates:** 202 testes + ruff verdes; app timedelta gate limpo (test_app_triage
  passa sob -W error da deprecação). **PUSH + PR:** o aluno autorizou ("commit and push everything
  auto"); branch `claude/general-improvements-0ba2e9` no remoto, **PR #1**
  (<https://github.com/HS2000PT/DIMEIA/pull/1>). `gh` não existe neste PC → PR criado via API
  com a credencial git local.
  **🗺️ ROADMAP GRANDE (o aluno expandiu MUITO o âmbito a meio da sessão):** pediu um plano e
  "go ahead" para: (WS1) integridade do apêndice — tirar nomes de scripts/ficheiros
  e frases de estilo especificação-de-software; refazer o apêndice com
  SNAPSHOTS/relatórios, não listas de ficheiros. (WS2) **tese bilingue EN↔PT em sincronia total
  = REGRA** (já em "Decisões Confirmadas"); medido: só ch1+frontmatter traduzidos, **ch2–ch6 são
  scaffolds vazios** → traduzir tudo, fiel, mesmo estilo, incluindo legendas/figuras; varrer
  mistura EN/PT. (WS3) **snapshots reais dos objetos de dados** (bruto→limpo→representado→medido,
  "todas as fases da IA"; que métrica com que colunas) na tese E slides; mais figuras "tipo
  slides" na tese; logos das fontes/APIs/tecnologias na apresentação. (WS4) app: **setas para
  cima estão VERMELHAS (🔺), devem ser VERDES**; estado do mercado aberto/fechado ao vivo; mais
  bolsas/horários europeus (Xetra…); intradiário por defeito + gráfico mais tempo-real; tema
  claro/escuro por hora + mascote crocodilo dia/noite + fundos; logo/interface mais polémico;
  **auth admin/guest** com definições editáveis por cliques que refletem nos alertas Telegram;
  marketing/apelo. (WS5) **resultados desiludem** — "notícias positivas mas precedentes de
  queda" (tema≠direção, já no CS3; melhorar PRODUTO/clareza, NÃO fabricar número), critério de
  alerta mais sensível/customizável, história aparece tarde, ser crítico. (WS6) futuro: chatbot-
  mascote (RAG nos dados → net), multi-bolsa, auth robusta. **Plano completo, priorizado, com a
  minha análise crítica e sugestões: [`progress/_historico/PLANO_MELHORIAS.md`](progress/_historico/PLANO_MELHORIAS.md).**
  **Fase 1 = WS1 (apêndice) + setas verdes + estado do mercado.** REGRA DURA em todo o roadmap:
  não fabricar; congelados byte-iguais; bilingue em sincronia; sem trailer de co-autoria nos commits.
  **✅ FEITO nesta corrida (PR #1, 13 commits, push direto autorizado "always push directly"):**
  robustez (10 correções + 5 testes); WS1 apêndice sem nomes de scripts/software-spec; setas
  📈/📉; **App value + clarity** — clareza dos precedentes (split de direção + "not a prediction
  for this news"), **estado do mercado US ao vivo** (`investigator/market_data/market_hours.py`,
  DST via zoneinfo), **badge de prova de vida** (precisão vs base rate,
  `investigator/evaluation/monitoring.py`), e **painel guest/admin** que ajusta os alertas ao
  vivo (`investigator/settings_overrides.py` puro + runner `effective_config()` = base+local+
  branch, fail-open + painel na app com password → publica overrides na branch via GitHub API).
  **219 testes + ruff verdes; congelados byte-iguais; tese 90 pp.** Decisões do aluno: próximo
  foco = App value; setas 📈/📉; auth guest+admin. **Passo humano p/ ativar o painel:** segredos
  `admin_password` (+ opcional `github_token`) no Streamlit — sem eles, guest read-only (seguro).
  Plano vivo: [`progress/_historico/PLANO_MELHORIAS.md`](progress/_historico/PLANO_MELHORIAS.md).
  **✅ MAIS nesta sessão (o aluno insistiu "continue / you decide everything / always push
  directly" ~10×; PR #1 ~28 commits):** (a) **mascote crocodilo dia/noite** on-brand
  (`app/assets/mascot_{day,night}.svg`) sincronizada com a hora local via `day_phase()` — logo do
  canto + herói do About + saudação; verificada ao vivo (Playwright) a mudar noite→dia entre
  corridas. (b) **crítica honesta** `docs/design/product_critique.md` (pedido "sê crítico").
  (c) **6 FIGURAS DE TESE novas, todas grounded + verificadas ao render** (auditoria multi-agente
  deu o backlog; verifiquei o grounding eu próprio — subagentes com limite de conta): Fig 3.3
  objetos de dados reais, Fig 3.4 z-score "duas curvas", Fig 5.8 tema≠direção (barras do alerta
  NVDA), Fig 6.1 scorecard das RQ, Fig 2.3 3 gerações→SBERT, Fig 6.2 limitações→futuro. Tese
  **90 pp, 0 erros, 0 refs indefinidas; nenhum número novo**. **⚠️ as 6 são EN — faltam espelhar
  no thesis-pt (WS2).** (d) **bolsas europeias** (`market_hours` generalizado: US/Xetra/Euronext/
  LSE, DST via zoneinfo; app mostra "Other exchanges"). (e) **fix preços NaN** (sem "$nan").
  **224 testes + ruff verdes; congelados byte-iguais.** **PRÓXIMO (precisa do aluno):** rever as
  6 figuras (pp. 10/18/20/48/55/58 de `thesis/main.pdf`); segredo `admin_password`; recriar venv
  do pin (numpy 2.5 drift); decidir a tradução PT (ch2–ch6) — a maior lacuna genuína.
- **🔧 SESSÃO 40 (plano de 9 fases aprovado em modo de planeamento):** o aluno
  devolveu ~18 pedidos (bug das setas; alertas ilegíveis "num relance"; dashboard fraco/tralha;
  timing abertura/fecho; mais info nos alertas; loop de pós-fecho; novos critérios de triagem;
  logo/slogan que odeia — quer crocodilo, Invest+Investigate+Aligator; revisão de escrita
  para voz natural/fluida; guias de estudo VISUAIS "de escola"; figuras melhores
  (simplificada no corpo + completa no apêndice); apêndice "proof of work"; declaração de IA
  mínima; app/tese isoladas p/ futuro repo público de 1 commit). **Plano-mestre** em
  `C:\Users\ruifa\.claude\plans\serene-marinating-squid.md` (9 fases, respostas às perguntas
  estratégicas embebidas). **Decisão fechada (a única pausa académica):** declaração de IA =
  **honesta, sem nomear o produto** (o aluno escolheu a minha recomendação). **Nota de trabalho:**
  commits sem trailer de co-autoria (convenção do projeto).
  **✅ FASE 1 FEITA (commit ab5759f) — bug das setas + alertas legíveis:** a direção estava
  DUPLICADA e divergente em 3 sítios → nova fonte ÚNICA `direction_icon(value)` no explainer.
  Corrigido: resumo diário (run_alerts usava SEMPRE 🔺 mesmo a descer — o bug do aluno) +
  dashboard (marcadores sempre triangle-up e coluna "Type" sempre 🔺 → agora acompanham a
  direção, derivada do NÚMERO guardado via `_market_down`, robusto a emojis antigos errados).
  `explain_anomaly`/`explain_intraday` reescritos em CAMADAS legíveis num relance (linha 1 = o
  facto a negrito; linha 2 = severidade em palavras; nota final "Why flagged" = a estatística;
  todos os números intactos, fidelidade XAI testada). Travessões conectores (—) removidos dos
  textos de produto. `classify_kind` agora robusto por emoji (📊/🔺🔻/📰) → **corrige bug
  latente: alertas INTRADIÁRIOS eram classificados como notícia**. Testes de fidelidade
  atualizados para os novos tokens. **✅ FASE 2 FEITA (commit 3e7d2b8) — dashboard:** as 2
  tabelas (dataframe + expander "Full alert texts") fundidas numa **tabela ÚNICA e expansível**
  (linha = data + facto; expande = texto completo; read-only, espelho do canal); tooltips
  modernos (cartão multi-linha formatado com hoverlabel claro, em vez do texto cru de 220
  chars); cabeçalho "Alert history" + linha "num relance" (N market · K news + legenda);
  AppTest reescrito. **189 testes + ruff verdes em ambas as fases; números congelados intactos.**
  **✅ FASE 3 FEITA (commit 16dd405) — timing abertura/fecho + loop de pós-fecho zero-ops:**
  (a) NOTA DE ABERTURA nova (`build_opening_note`/`maybe_opening_note`, 1×/dia 14-15 UTC via
  cotação intradiária: como a watchlist abriu vs fecho de ontem; kind "open"/🔔; a app mostra-a
  num expander) — o par matinal do resumo de FECHO (que já dispara ~21 UTC). (b) LOOP DE
  PÓS-FECHO tornado REAL e zero-ops: o `predictions_log.jsonl` passou de `data/` gitignored para
  a **branch `alerts-history`** (PERSISTE entre corridas do Actions), o `post_validate.py`
  reescrito para usar a cadeia de fallback de preços (funciona nos runners onde o yfinance
  bloqueia) + defaults sensíveis ao ambiente, passo novo no workflow ao fecho (≥21 UTC) regenera
  `live_monitoring.md`, e a app mostra "How our alerts are doing" (fail-open). `classify_kind`
  ganhou "open". going_live.md ressincronizado. **191 testes (+2) + ruff verdes.**
  **🟡 FASE 4 GROUNDWORK FEITA (commit 8f8e65b) — RQ4-ext, corrida BLOQUEADA por falta de dados:**
  ⚠️ **CORREÇÃO de nota desatualizada:** este PC (`ruif`) **NÃO tem os dados** — `data/` só tem
  amostras (sem `triage_dataset.csv`/FNSPID/`finnhub_news.csv`, sem `.env`) e **não tem `torch`**.
  O congelado foi treinado noutra máquina (`C:\Users\henri\…`, cabeçalho de `evaluation_triage.md`).
  ⇒ a ablação não corre aqui e NÃO se fabricam números. Entregue o MECANISMO testado:
  `event_features_ext` (5 features novas aditivas e anti-lookahead: market_vol20, mom20, vol_ratio,
  ret_event_z, downside_vol20) + `build_dataset.py --ext` (ficheiro separado; congelado byte-igual)
  + roteiro honesto `docs/evaluation/roadmap_rq4.md`. **195 testes (+4) + ruff verdes.** Números:
  correr na máquina com corpus + `setup_env.sh --ml`.
  **✅ FASE 5 FEITA (commit 5483dbf, PUSHED) — logo + slogan:** o aluno escolheu o **Conceito 3
  "The Stare"** dos 3 que apresentei num artifact (olho de crocodilo — íris dourada, pupila em
  fenda, sobrolho — sobre linha de mercado; funde Invest/Investigate/alliGator). `logo.svg`
  reescrito; slogan novo **"Every move investigated, never predicted."** (personalidade + honesto
  ao "não prever"; sem travessão) em app/README/RELATORIO; page_icon 🐊; tema config.toml
  verde-pântano+dourado. ⚠️ Screenshot da app na tese (Fig. 4.5) + logo nos slides ainda ANTIGOS
  → regenerar na F7.
  **PUSH:** o aluno autorizou; Fases 1-6 no remoto.
  **✅ FASE 6 FEITA (commit deaefab, PUSHED) — escrita natural:** descoberta
  honesta com provas — o CORPO da tese JÁ está limpo (0 travessões conectores em prosa; os "---"
  são células de tabela "n/a"; 0 tic-words; lê-se humano/com voz, ex. ch6 "Yes."/"reported exactly
  as they fell") ⇒ NÃO reescrevi o corpo validado (mais risco que benefício; o aluno pediu "sem
  exagero, manter rigor"). O único tell real era no PAPER IEEE: 6 travessões conectores →
  parênteses/vírgulas; recompila LIMPO (0 erros, 0 cit. indefinidas via bibtex/IEEEtran 25 refs,
  4 pp; nenhum número alterado). A voz jovem/brincalhona vai para os GUIAS (F8). LaTeX confirmado
  neste PC (MiKTeX + latexmk 4.87 + biber/bibtex).
  **✅ SESSÃO 40 COMPLETA (F4+F7+F8+F9 nesta corrida; F1-F6 em corridas anteriores) — ver o bloco
  abaixo "SESSÃO 40 (fecho)".**
  **⚠️ Para o aluno VER Fases 1-5 ao vivo:** correr o workflow "Alerts" + redeploy/reabrir a app.
- **✅ SESSÃO 40 (FECHO — "continue with the plan; i'm already on the best pc"):** o aluno estava
  AGORA na máquina do FNSPID (`C:\Users\henri`, a do cabeçalho congelado) — a que TEM os dados
  (`triage_dataset.csv`, `kb_fnspid_sbert.jsonl`, `fnspid_news_subset.csv`, `.env`) e `torch`. Isso
  DESBLOQUEOU a F4 (a ablação estava só groundwork por falta de dados no outro PC). **Feito nesta
  corrida (5 commits, todos sem trailer de co-autoria):**
  **✅ F4 (commit 7ae5390) — ablação RQ4-ext CORRIDA (a "IA fraca" fica mais forte):** wiring aditivo
  `context_ext` em `features.py` (caminho de produção byte-idêntico — o dataset congelado não tem as
  colunas ⇒ `assemble` nunca produz o bloco novo); novo `scripts/train_triage_ext.py` (padrão *_ext,
  NÃO toca em `models/` nem `evaluation_triage.md`); `build_dataset.py --ext` correu offline (cache de
  preços) → `triage_dataset_ext.csv` (79.453 linhas). **Resultado honesto:** contexto v1 = PR-AUC
  **0,537** (reproduz o congelado 0,538); +5 features = **0,535** (Δ −0,002, NENHUMA ajuda);
  leave-one-in/out: só `ret_event_z` (+0,001) tem sinal positivo, resto plano/negativo → a volatilidade
  rolante já absorve o sinal (mesma lição do texto, pelo lado oposto). → `evaluation_triage_ext.md` +
  figura `eval_triage_ext.pdf` + secção nova na tese (Cap. 5) + `roadmap_rq4.md` Eixo 1 ✅ +4 testes
  (199 total). **Congelados intactos (diff vazio).**
  **✅ F7 (commit 6f199e3):** (a) Fig. 4.5 recapturada via Playwright (`scripts/screenshot_app.py`) com
  a MARCA NOVA — logo "The Stare", slogan "Every move investigated, never predicted.", tema
  verde-pântano+dourado, e as notas de abertura/fecho (F3) visíveis; caption atualizada. (b) a figura
  simplificada do corpo (fluxo) passa a APONTAR para a figura completa do apêndice (pipeline com todos
  os gates). (c) apêndice novo **"Proof of Work"** — tabela que liga CADA número da tese ao comando que
  o regenera e ao ficheiro congelado + evidência de operação ao vivo (alertas reais, KB a maturar,
  pós-validação 0,667 vs 0,455, 199 testes, 200+ commits). Tese **90 pp**, 0 erros, 0 refs indefinidas.
  **✅ VISUAIS NOVOS (pedido do aluno a meio da sessão — "adoro visuais; snapshots reais dos objetos de
  dados; todas as fases da IA; moderno, simples, jovem"):** nova **Fig. 3.2 "jornada dos dados"** — UM
  headline REAL (NVDA, 10 Mai 2018, valores genuínos incl. embedding SBERT 384-d real) por 4 cartões
  coloridos: RAW → CLEAN&ALIGN (anti-lookahead) → **REPRESENT (a fase "AI"** com badge: SBERT + features
  + rótulo) → LEARN&MEASURE. Espelhada nos SLIDES (commit 775462a, +frame "The data, at every stage")
  e no GUIA (commit 8f0291b, PT-PT). **+ visual "Built with"** (badges por categoria: fontes/APIs, ML,
  produto, infra; "no paid APIs, no GPUs, no always-on server") nos slides e no guia — a resposta ao
  pedido dos "logos das tecnologias/APIs" (badges de NOME, offline-safe, sem imagens de marca). Slides
  17→19 frames; guia 73→**76 slides**; Result 4 dos slides + frame do guia ganham a ablação RQ4-ext.
  **✅ F9 (commit 106ed97) — bundle público:** `scripts/make_public_bundle.py` (parte de `git ls-files`
  ⇒ nunca inclui `.env`/segredos/corpora; remove os caminhos só-internos: progress/, CLAUDE.md,
  .claude/, docs/internal|_archive|defence/, slides/, CHECKLIST/RELATORIO; scan de segredos; `--git` =
  1 commit; **NUNCA faz push**) + manifesto `docs/design/public_bundle.md`. Testado: 210 ficheiros,
  21 internos excluídos, scan limpo, 1 commit "Initial public release of InvestiGator".
  **GATES:** 199 testes (+4) + ruff verdes; tese 90 pp / paper / slides 19 / guia 76 — todos 0 erros;
  congelados byte-iguais; números novos gerados dos dados (0 fabricação).
  **✅ ADENDA (commit 25e1988) — logos reais + dicionário de colunas (o aluno reforçou o pedido):**
  (1) **Logos:** os frames "Built with"/"Feito com" passam a mostrar o LOGO REAL se existir o PNG em
  `slides/logos/`, senão o badge de nome (`\techlogo`/`\glogo` com `\IfFileExists` — degrada com graça,
  sem mexer no .tex); `slides/logos/README.md` lista os nomes de ficheiro + fontes oficiais. Decisão:
  no CORPO da tese ficam badges/figura (logos de marca são incomuns numa tese); os logos vivem nos
  slides+guia. (2) **Snapshots dos dados:** nova **Tabela 3.4** na tese — CADA coluna que a triagem lê
  + o VALOR REAL do exemplo NVDA + que métrica usa que colunas (contexto→triagem/PR-AUC;
  embedding→retrieval/prec@k); frame gémeo no guia (73→**77 slides**). Responde ao "que dados, o que
  lhes acontece, e que métrica com que colunas". Tese 90 pp / slides 19 / guia 77 = 0 erros.
  **PENDENTE HUMANO:** licença de código + declaração ISEP (com o orientador); leitura final; publicar
  o bundle (cliques); **opcional: largar os PNG dos logos em `slides/logos/`** (aparecem sozinhos).
  **Ambiente:** este PC tem venv 3.12 + torch + MiKTeX + Playwright(chromium).
- **🟢 SESSÃO 39 (verificação, sem código novo):** confirmado nos logs REAIS do Actions (lidos
  via API com a credencial git local; `gh` não existe neste PC) que a sessão 38 funcionou em
  produção. **(1) 1.º alerta de MERCADO de sempre** no canal (13/07: NVDA −3,53% intradiário,
  z=−1,67 vs ±1,5, severidade "notable") com TODAS as peças novas visíveis no log: linha
  "Sector check" (AMD −4,1%, TSLA −3,8%, META −1,3% → sector-wide), "Possible explanation
  (0d ago)", dedup ("já alertado hoje"), envio Telegram OK; histórico agora 44 alertas
  (43 news + 1 market). Nota: nesta corrida o yfinance RESPONDEU nos runners (sem linha
  `[precos … servido por …]` — a cadeia de fallback não foi precisa). **(2) Segredos:** o aluno
  adicionou `ALPHAVANTAGE_API_KEY` (✱✱✱ no log); `TIINGO/POLYGON` continuam vazios → item do
  CHECKLIST reescrito como robustez (não bloqueia — mas sem elas, Yahoo bloqueado = só AV
  25/dia). **(2b) — adenda: FECHADO na mesma noite.** O aluno criou `TIINGO_API_KEY` e
  `POLYGON_API_KEY` às 19:10 UTC (correção: a ALPHAVANTAGE já existia desde 03/07); disparei
  o workflow via API (workflow_dispatch, o "1 clique" do CHECKLIST) e a corrida das 19:27
  confirmou os 3 segredos visíveis (`***`) e o scan saudável (gates, dedup ×2, "Sem alertas
  novos" honesto). O yfinance continua a responder nos runners ⇒ a cadeia de fallback fica de
  reserva silenciosa. Item das chaves FECHADO no CHECKLIST. **(3) KB viva maturou 4 dias ANTES do previsto:** 13 casos em `live_kb.jsonl` com
  impactos reais (JPM +0,44/−0,67/−1,35%; NFLX +0,21/−0,72/−1,68%; notícias de 04-05/07
  alinhadas ao 1.º dia de negociação 06/07 — o desenho anti-lookahead a funcionar), 1.043
  pendentes, e "[kb-viva] 13 caso(s) em uso" no scan. **(4) Pós-validação corrida neste PC**
  (`post_validate.py`, venv 3.12): 33 decisões maturadas → **precisão das mantidas 0,667 vs
  base rate 0,455, Brier 0,229** (`live_monitoring.md` regenerado) — o mecanismo de triagem
  confirma-se AO VIVO, coerente com o 0,632 vs 0,163 offline da tese. **Falta 1 confirmação:**
  o 1.º resumo diário (corrida ≥21h UTC de dia útil; hoje à noite ou próximo dia útil).
  Gates verdes intactos (sem código tocado). CHECKLIST atualizado (2 pendentes fechados).
  **(5) Platt vs isotónica FEITO (o "pendente do PC do FNSPID" — afinal é ESTE PC, que tem o
  dataset 691 MB + triage_dataset.csv + stack ML no venv):** novo
  `scripts/evaluate_calibration_ext.py` (aditivo, padrão da sessão 38; models/ e
  evaluation_triage.md intocados) — reproduz o protocolo congelado **5/5 famílias ao milésimo**
  (PR-AUC e Brier; fumo hashing prova que vol/context nem dependem do embedder) e compara na
  MESMA validação (17.710 pts): **Platt ganha ou empata no Brier em TODAS as famílias**
  (vol 0,2183 vs 0,2231; context 0,2241 vs 0,2259; text/full ~empate; gbm 0,2276 vs 0,2298),
  ECE misto com margens pequenas ⇒ a justificação conceptual da tese
  (niculescu2005calibration) fica validada EMPIRICAMENTE; produção continua Platt, sem caso
  para mudar → `docs/evaluation/calibration_platt_vs_isotonic.md` (veredicto gerado dos
  próprios números). Gotcha evitado: HF_HUB_OFFLINE=1 no lançamento destacado (a lição do M6).
  docs/README.md: índice ganhou os 3 .md da sessão 38 que faltavam + o novo.
- **🔬 SESSÃO 38 ("improve a lot the thesis; AI part is weak; 0 market events; be critical"):**
  plano aprovado em modo de planeamento (aluno escolheu TODAS as fontes de preços e
  "Actions agora + VM depois"). **Diagnóstico com provas ANTES de mexer:** os 0 alertas de
  mercado NÃO eram sensibilidade — o pipeline estava CEGO: histórico real do canal com 42
  alertas todos news, **0 market E 0 summary** (o resumo dispara com qualquer resultado ≥21h
  ⇒ `collect_market_results` vazio SEMPRE); yfinance bloqueado nos runners do Actions sem
  fallback; intradiário (Finnhub) só corria na VM nunca ligada. **Produto (5280c64):** cadeia
  de fallback `yfinance→Tiingo→Polygon→Stooq→AV` em prices.py (parsing puro + HTTP tardio;
  sem chave = salta; **Stooq testado ao vivo: anti-bot PoW → despromovido**; chaves novas
  TIINGO/POLYGON_API_KEY no .env.example+workflow — segredos = clique do aluno, CHECKLIST);
  **intradiário corre TAMBÉM no Actions** (insight: a norma do z-score só precisa de dias
  COMPLETOS — só o movimento de hoje precisa de frescura, e a cotação Finnhub dá isso);
  resumo diário cai para resultados intradiários quando o fecho está cego; 1 busca de
  preços/ticker/ciclo (cache partilhada); threshold implantação 2.0→**1.5 com níveis de
  severidade** (notable≥1.5<strong≥2<extreme≥3; tese congela 3.0 intacta); linha
  **"Sector check"** descritiva (pares do setor no mesmo dia, mapa da tese estendido
  AMD/NFLX→tech, zero chamadas extra); recência half-life 365→**120d**;
  `require_fresh_bar` exposto. **App (e8bcdea):** faixa **"Market now"** (10 tickers num
  relance; 1 `yf.download` em lote, cache 10 min, offline-aware, chips markdown — o teste
  len(metric)==1 sobrevive); About emagrecida (~60 palavras; citação em expander); tema de
  marca `.streamlit/config.toml` (navy+esmeralda). **Ciência ADITIVA (congelados
  byte-iguais; ficheiros de avaliação NOVOS):** `evaluate_anomaly_ext.py` (LOF causal +
  z-score com σ EWMA λ=0.94) → z 0.530 REPRODUZ o congelado e bate IF 0.269 e LOF 0.280;
  **achado honesto: EWMA F1 0.664 > rolling 0.516** (mesmo recall, ~metade dos FP;
  clustering de volatilidade) — reportado como caiu, produção fica rolling (explicabilidade),
  adoção = futuro JÁ validado (Cap. 6); projeção **PCA real** da KB (2016×384-d, estrela da
  query + top-3 NVDA sims 0.58-0.61) → embedding_projection.pdf; **exemplo trabalhado REAL
  da triagem** (alerta META 12/07 'Zuckerberg AI bets': contribuições exatas → logit +0.699
  → σ 0.668 → Platt(3.700,−2.313) → **p=0.539 = o 54% ENVIADO ao canal — reprodução
  exata**) → triage_contributions.pdf + triage_worked_example.md; **funil de produção
  real** 944 manchetes relevantes capturadas → 42 alertas (22:1, 3 tickers) →
  alert_funnel.pdf/md. **TESE 78→86 pp, 0 erros/0 cit. indef./0 overfull:** ch3 = mean
  pooling + cosseno (L2 ⇒ cos=dot e ordem euclidiana igual — fecha o "porquê cosseno"),
  bi-vs-cross-encoder, reconciliação raw-return (evidência) vs market-adjusted (rótulo),
  LR+Platt em equações, Platt-vs-isotonic (niculescu2005calibration, já verificada), Brier
  + porquê PR-AUC, TABELA do exemplo real; ch2 = GARCH/LOF empíricos (remetem p/ CS1-ext),
  linha LOF na tabela, nota honesta word2vec/FinBERT; ch4 = **secção nova "The Life of One
  Alert"** (9 gates com valores reais do alerta META) + figura do funil + lição de
  implantação honesta; ch5 aditivo = CS1-ext (tabela+figura), projeção real no CS2, figura
  de contribuições no CS4 (**CS3 byte-igual**); ch6 = lição de deploy + EWMA como futuro
  validado; **Apêndice: 1.ª figura ROTADA** (sidewaysfigure; pipeline completo numa página,
  todos os gates+valores; cuidado: estilo TikZ não pode chamar-se `out` — colide com
  /tikz/out) + 4 comandos de reprodução novos; órfã app_method_expander.png removida.
  **Screenshot real novo** (Playwright: faixa + TSLA com 3 eventos reais na curva; clicar
  radio da empresa = `label:has-text(...)`, o input está fora do viewport). Guia
  **73 slides** (+CS1-ext/EWMA, +vida-de-um-alerta/funil, produto-HOJE e mapa de números
  atualizados; extensões marcadas como NÃO-congeladas). Docs sync (free_apis com
  Tiingo/Polygon/Stooq-caiu + incidente; going_live +3 segredos; vm_watch = VM é upgrade de
  latência; product_review Pass 8; README 189 testes/86 pp/73 slides; CHECKLIST: chaves +
  rever max_precedent_age ~agosto + isotonic no PC do FNSPID). **Ambiente DESTE PC mudou:**
  agora TEM Python 3.12 (venv criado via setup_env.sh + requirements-app) e MiKTeX completo
  — a nota da sessão 31 ficou obsoleta. **189 testes + ruff verdes; demo +6,46% intacta.**
  ⚠️ Pendente humano: segredos TIINGO/POLYGON/ALPHAVANTAGE no GitHub → 1 "Run workflow" num
  dia útil para ver o mercado vivo (o log deve dizer `[precos …] servido por …` se o Yahoo
  bloquear, e `[intradiario]`/resumo a aparecer).
- **✨ SESSÃO 37 ("cleaner, faster, premium; full critical review"):** revisão crítica feita e
  executada. **Performance (o achado nº 1):** `st.tabs` renderiza TODAS as abas a cada
  interação (10× yfinance + 10× scoring — a app arrastava-se) → substituído por seletor
  horizontal (radio) que renderiza SÓ a empresa escolhida (~10× mais leve; teste garante
  len(at.metric)==1). Nota técnica: `st.segmented_control` foi tentado primeiro mas tem bug
  de serialização no AppTest 1.41 (itera caracteres do valor) — radio horizontal é
  equivalente e seguro. Risco de fundo cacheado 10 min (`_risk_score`).
  **Alertas para leigos:** headers com nome de empresa — "Anomaly detected for TSLA (Tesla)"
  — via `COMPANY_DISPLAY/display_name` em relevance.py e `_nome()` aditivo no explainer
  (tokens de fidelidade intactos; tickers fora do mapa sem sufixo → testes de fidelidade
  passam sem mudança, exceto 1 assert intradiário atualizado). Demo mudou o header →
  blocos congelados sincronizados em how_to_run §0.0 e guia (frame demo); **CS3 do Cap. 5
  INTOCADO** (registo experimental congelado — a evolução já está documentada no Cap. 4).
  **Resumo diário compacto:** movers (≥1% ou anomalia) um por linha com ⬆⬇/🔺; calmos
  comprimidos numa linha "Quiet: …" — hierarquia visual em vez de 10 linhas monótonas.
  **Premium:** crosshair/spikes no gráfico + hovertemplate "$Y · X"; default 1M (mais
  "live" que 6M); métrica "Tesla (TSLA)"; tabela de eventos mostra SÓ a 1.ª linha (o facto
  forte) + expander "Full alert texts"; CTA "📡 Get alerts on Telegram" na sidebar; About
  reordenado (Get the alerts logo após a introdução).
  **Lição de ferramenta:** o AppTest ENGOLE SyntaxErrors (árvore vazia, sem exceção) — um
  heredoc partiu uma string e os testes "falharam sem erro"; diagnóstico via py_compile.
  **Screenshot v4 real** (seletor + CTA + 1M) → Fig. 4.5; tese 78 pp + slides 17 + guia 71
  recompilam 0 erros. **167 testes + ruff verdes.**
- **🎨 SESSÃO 36 ("one tab per company, one big chart with events, the rest elsewhere"):**
  app REESCRITA para exatamente a visão dele: **2 vistas e só 2** — 📊 Live (uma aba por
  empresa; UM gráfico grande estilo Google Finance com intervalos 1D/5D/1M/6M via yfinance
  `period/interval`, eventos do canal MARCADOS na curva com hover = texto exato do alerta,
  mesma lista em tabela por baixo, risco de fundo do modelo RQ4 numa caption compacta;
  read-only) e ℹ️ About (o que é, como funciona, avaliação, get-alerts, citação + a ÚNICA
  ação da app — a demo de retrieval — num expander; decisão minha: mantida para a demo do
  júri). Removidos: "Check any ticker", páginas antigas.
  **Identidade profissional:** novo `app/assets/logo.svg` (quadrado navy, linha de mercado
  esmeralda que termina num "olho" — o gator abstraído) + slogan **"Market intelligence,
  explained."** (README + app; mascote antiga fica como asset histórico do guia).
  **Sempre-online (resposta honesta ao "guarantee me"):** Community Cloud hiberna sem visitas
  e não tem SLA → (1) passo **keep-alive** no workflow Alerts (ping à app em cada corrida,
  semana+fim de semana — na prática mantém-na acordada); (2) alternativa 24/7 A SÉRIO:
  `deploy/investigator-app.service` (o dashboard na MESMA VM Oracle do vigia, porta 8501;
  instruções no vm_watch.md §Bónus). Docs deployment/vm_watch atualizados.
  **Detalhe técnico:** `_event_positions` mapeia eventos a posições no intervalo atual (em
  intraday, ao 1.º bar do dia); markers só com data (HistoryEntry não tem hora — limitação
  aceitável). Fallback sem plotly mantido (`INVESTIGATOR_NO_PLOTLY`).
  **Screenshot REAL novo** (Playwright, aba TSLA com marcadores de eventos visíveis) →
  substitui `thesis/figures/app_dashboard.png`; frase+caption da Fig. 4.5 atualizadas
  (honestas, design atual); tese 78 pp + slides 17 + guia 71 recompilam 0 erros (mesmos
  ficheiros de figura → slides/guia atualizam sozinhos).
  **Testes reescritos** (test_app_triage: 8 testes da estrutura nova — radio 2 vistas, risco
  como caption, About com demo, resumo em expander, fallback). **167 testes + ruff verdes.**
- **🌱 SESSÃO 35 (o aluno partilhou a visão ChatGPT e delegou: "decide a melhor forma; acredito
  em ti"):** análise honesta devolvida — a visão descreve ~80% do sistema JÁ construído (2
  sensores→motor único = a arquitetura da tese; "priorização inteligente" = RQ4; "aprendizagem
  contínua" = M5.5); adotado o delta genuíno, rejeitado com razões (reescrita da tese/repo novo,
  redes sociais sem API free, scores de "confiança" preditivos — contradiriam a restrição
  fundadora e o próprio resultado da RQ4). Plano V1–V4 aprovado e executado por fases:
  **V1 — KB VIVA (e62cf56):** novo `investigator/live_kb.py` (puro) — toda a manchete RELEVANTE
  do scan entra em `live_pending.jsonl` (embedding NA CAPTURA com manchete+summary; o summary
  do Finnhub NUNCA é persistido — governança §5.4; NewsRecord intocado); maturação ≥8 dias
  com preços reais (+1/+3/+5d, alinhamento anti-lookahead da tese) → `live_kb.jsonl`; ambos na
  branch alerts-history (workflow git add -A; VM cobre). Retrieval FUNDIDO com decaimento:
  `merged_precedents` ordena por cosseno × 0.5^(idade/365d) — o decaimento SÓ ordena, a sim
  mostrada é o cosseno real, e cada precedente mostra a idade ("3y ago"; `_age_label`, só com
  `today=` — demo/tese byte-iguais). Config: `news.recency_half_life_days`,
  `news.max_precedent_age_days` (o "botão dos 6 meses", null até a KB viva ter meses).
  Validado ao vivo: 846 pendentes capturados numa varredura; decaimento confirmado a reordenar.
  **V2 — investigação cruzada (a5fbf4a):** anomalia → busca notícia relevante (48h) →
  "Possible explanation (Xh ago)" ou "No relevant news found… no public explanation yet"
  (`attach_news_context` puro; fail-open). Direção dos precedentes SEMPRE descritiva
  ("3 of 3 shown cases moved down — an observed pattern, not a forecast"); mantém ⚠ BOTH
  quando misto.
  **V3 — intradiário (6ebb9f9):** no --watch, `fetch_finnhub_quote` (tempo real, free) +
  `detect_intraday` (o MESMO z-score vs norma diária de dias COMPLETOS, sem lookahead) +
  `explain_intraday` ("so far today… the session is not over"). **Bug real apanhado antes de
  produção:** ao fim de semana a cotação estagnada re-alertaria sexta → guarda pura
  `is_us_market_session` (seg-sex 13:00-21:30 UTC), testada. `market.intraday.enabled`.
  **V4:** tese Cap. 6 +1 parágrafo honesto (iteração pós-avaliação; avaliação formal = futuro;
  78 pp, 0 erros); guia 71 slides (frame produto + pergunta júri "KB desatualizada?"); docs
  (vm_watch, going_live, README, RELATORIO, product_review Pass 7 com P-13/14/15).
  **167 testes + ruff verdes; demo +6,46% intacta.**
- **🧹 SESSÃO 34 ("full repository cleanup… the product sucks… rethink from scratch"):** o aluno
  estava sobrecarregado (repo "uma confusão") e insatisfeito com o produto real. **Diagnóstico com
  provas ANTES de mexer** (li os 27 alertas reais do canal via branch alerts-history + logs do
  Actions): (1) a "similaridade má" era LIXO À ENTRADA — o Finnhub etiqueta mal (notícia de
  escritório de advogados como "AMD"; "Top S&P500 movers" para vários tickers) e não havia filtro
  de relevância; (2) zero alertas de mercado = nenhum |z|≥2 real + canal mudo em dias calmos + só
  TSLA/META/AMD passavam o gate de materialidade (volatilidade domina); (3) cron do GitHub na
  prática corre de **1,5-2h em 1,5-2h** (medido), não 30 min. Plano aprovado em modo de
  planeamento; decisões do aluno: VM Oracle Free; guia de 64 slides = fonte ÚNICA; apagar lixo;
  resumo diário sim.
  **F1 (commit 8fc045e):** `investigator/news_fetcher/relevance.py` (menção obrigatória da
  empresa + boilerplate rejeitado — testado com os casos reais); chão `news.min_similarity 0.45`
  (sem precedente forte → sem alerta); aviso "⚠ BOTH directions" nos precedentes de sinal misto
  (P-3 implementado); teto `max_per_ticker_per_day: 2`; P da triagem no log por ticker.
  **F2:** resumo diário ao fecho (1 msg ≥21h UTC, kind=summary no histórico partilhado e na app);
  crons alargados (manhãs úteis 7/10 UTC + fins de semana 9/15/21 — mercado auto-salta, notícias
  fluem); **dedup entre produtores** via histórico partilhado (campo `key` no HistoryEntry;
  `seed_state_from_shared_history`; `news_key` agora sobre plain_text).
  **F3:** `run_alerts.py --watch --interval 300` (loop com jitter, SIGTERM limpo, config a
  quente; `run_cycle()` extraído e reutilizado) + `_push_history_safe` (INVESTIGATOR_HISTORY_GIT=1,
  PAT só na VM) + `docs/design/vm_watch.md` + `deploy/investigator-watch.service` +
  `deploy/setup_vm.sh`. Cron do GitHub fica de rede de segurança (dedup impede duplicados).
  **F4 limpeza:** APAGADOS ML_PLAN/PLANO_FINAL/PLANO_SESSOES + editorial_review/review_log/
  implementation_review + start/end_session.sh + fnspid-overnight.bat/kb-fnspid.cmd (git preserva;
  citation_log/page_audit/product_review/learning/glossary/ROOT_PROMPT INTOCÁVEIS — proveniência);
  ARQUIVADOS em docs/_archive: caderno_de_defesa, guia_rapido, QUESTIONS, proposta_ml (absorvidos).
  Referências ativas todas corrigidas; README com mapa "6 sítios que interessam" no topo;
  **CHECKLIST reescrito para SÓ o que falta**; docs/README refeito.
  **F5 guia ÚNICO:** `slides/guia_estudo/` 64→**71 slides** (+guião oral de 3 min e por-RQ,
  +2 frames de perguntas do júri (modelo perdeu?/anti-lookahead da triagem/formato evoluiu/painel
  único/RL/cross-ticker/reprodutível/citações), +mapa dos números congelados (tabela verificada),
  +plano B; frame "produto HOJE" atualizado) — compila 0 erros; é A fonte de estudo.
  **Validado: 145 testes + ruff verdes; dry-run ao vivo** — lixo rejeitado no log, AAPL suprimida
  por precedente fraco (sim<0,45), aviso de direção mista presente, P de todos os tickers visível.
  **⚠️ Para o aluno:** o deploy do Streamlit está PRESO num pull antigo (4× "Updating the app
  files has failed" no log) — precisa de **Manage app → Reboot app** (o "plotly em falta" é
  sintoma, não causa); depois Sharing→público. VM Oracle: cliques dele (runbook pronto).
- **🖥️ SESSÃO 33 (redesenho de produto, feedback real do aluno após dias de uso):** o aluno reportou
  3 problemas concretos depois de usar o sistema a sério — quase nunca recebia alertas de mercado,
  a linha de materialidade era jargão, e o Streamlit (8 páginas) "não parecia refletir o meu
  trabalho treinado". Pediu mudanças fortes + um plano de vários dias, e perguntou diretamente se o
  projeto tinha ido por um caminho errado.
  **Resposta verificada:** não — a tese nunca prende nenhuma estrutura de UI específica (só
  menciona "an interactive dashboard" uma vez + um mockup desenhado do Telegram); o pivô é de
  produto, não de ciência. **Entrei em modo de planeamento** (2 agentes Explore + 3 perguntas
  AskUserQuestion ao aluno: conteúdo secundário → expander no fundo; risco sempre visível → sim;
  notebook → âmbito alargado) e produzi um plano de 5 fases, aprovado antes de codificar.
  **Fixes rápidos (antes do plano):** `threshold` de mercado 3,0→2,0 em produção (divulgado,
  distinto da avaliação da tese, que fica intocada) — validado ao vivo (dry-run disparou um
  alerta real); `materiality_line` reescrita em linguagem simples ("raised by X and Y").
  **Fase 1 — histórico partilhado:** novo `investigator/alerts_history.py` (puro, testado) +
  branch de dados **`alerts-history`** (bootstrap via git plumbing, sem tocar na árvore de
  trabalho) — o workflow escreve, a app lê via raw.githubusercontent.com (cache 60s, fail-open) —
  Telegram e Streamlit deixam de poder divergir silenciosamente.
  **Fase 2 — app reescrita por completo:** painel único, uma aba por ticker; "Background risk"
  do modelo TREINADO pelo aluno (RQ4) pontua TODOS os dias, mesmo sem notícia (novo
  `score_background`); gráfico Plotly anotado (hover = texto exato do alerta); tabela de
  histórico; "Method & evaluation" num único expander no fundo (decisão confirmada com o aluno).
  **2 bugs reais apanhados pelos testes ANTES de produção:** IDs de gráfico Plotly colidiam entre
  abas (mesma chave auto-gerada); `st.expander` aninhado (Streamlit não permite) — ambos só
  apareceram ao correr o AppTest a sério, e foram confirmados também com um arranque REAL do
  servidor Streamlit (não só AppTest), health 200.
  **Fase 3 — notebook:** `notebooks/investigator_walkthrough.ipynb` (âmbito alargado, confirmado
  com o aluno): anomalia + retrieval + o modelo treinado, executado de ponta a ponta
  (`jupyter nbconvert --execute`), 0 erros, outputs reais (2 caminhos locais que escaparam para
  os outputs foram limpos antes do commit).
  **Fase 4 — screenshots reais:** capturados com Playwright (servidor Streamlit local real, não
  a app pública — que continua privada) e inseridos como figuras genuínas (não mockups) na tese
  (Cap. 4, Fig. 4.5), nos slides de defesa (novo frame "The product, live") e no guia de estudo
  (frame "produto, HOJE") — todos recompilados 0 erros (78/17/64 pp). Caption honesto: captura
  cedo, histórico ainda vazio (o mecanismo tinha acabado de ser construído) — não fabricado.
  Documentação sincronizada de ponta a ponta (README, CHECKLIST, going_live, deployment, caderno
  de defesa +1 pergunta de júri nova, guia rápido, RELATORIO_FINAL, `product_review.md` Pass 6).
  **Validado: 132 testes + ruff verdes** em todas as fases. **Pendente (não bloqueia): confirmar
  a branch `alerts-history` a receber o 1.º registo real** — ou clique do aluno em "Run workflow",
  ou a corrida agendada do dia seguinte em horário de mercado.
- **🧠 SESSÃO 32 (produto, "continue with the pendings and plan"):** o único pendente de código
  registado (CHECKLIST §polimento) foi construído: **a app pública e o runner passam a recuperar
  precedentes SEMANTICAMENTE** com o MESMO modelo da tese (`all-MiniLM-L6-v2`) exportado em ONNX
  quantizado (~23 MB, `onnxruntime` CPU + `tokenizers`, SEM torch). Novo
  `investigator/historical_kb/onnx_embedder.py` (download sob demanda com **SHA256 pinado**,
  cache `models/onnx/` gitignored; mean-pooling+L2 igual ao sentence-transformers; testado).
  **KB light recurada a 384-d**: `curate_kb_light.py --sbert-kb` REUTILIZA os embeddings SBERT da
  KB grande (zero re-embedding; arredonda a 5 casas) → `kb_fnspid_light.jsonl` 2.016 registos,
  7,7 MB versionada. **Validação honesta** (`docs/evaluation/onnx_minilm_validation.md`): cosseno
  ONNX↔SBERT médio 0,992 (mín 0,987, n=63 manchetes reais); top-3 idênticos 20/23 queries, 96 %
  vizinhos comuns (divergências = empates no 3.º); query recall TSLA devolve o precedente NTSB
  exato (sim 0,73). **Fail-open**: `product_retrieval()` em `main.py` — sem modelo/rede degrada
  para a KB-amostra word-overlap (a UI descreve o motor em uso; KB 384-d NUNCA é consultada por
  hashing — levanta). App usa `st.cache_resource` + env `INVESTIGATOR_OFFLINE=1` nos testes
  (conftest novo; testes nunca descarregam). Runner decide o par (KB, embedder) 1× antes do loop;
  workflow Alerts ganhou cache do modelo (chave constante `onnx-minilm-quint8-v1`).
  `requirements.txt` + `onnxruntime==1.27.0`/`tokenizers==0.22.2` (wheels cp312–cp314 confirmadas
  → instala no Cloud mesmo em Python 3.14). **Validado:** 117 testes + ruff verdes; demo reproduz
  +6,46%; **dry-run ao vivo com 3 alertas reais e precedentes genuinamente on-topic** (AMD
  semicondutores → TSMC/semis, sims 0,51–0,55) com linha de triagem. Números da tese INTOCADOS
  (a tese só fala do baseline lexical na avaliação — verificado; nada a mudar).
  **⚠️ Achado para o aluno:** a app no Streamlit voltou a ficar PRIVADA (visitante anónimo →
  login; provável efeito do redeploy de hoje) — reaberto no CHECKLIST com os passos. Workflow
  Alerts correu hoje 2× com sucesso (15:40/17:53 UTC; o GitHub salta crons quando os runners
  partilhados enchem — best-effort documentado).
- **📦 SESSÃO 32 — adenda FECHO ("organize everything now and put an end to this"):**
  (1) **Sync Telegram↔Streamlit**: a página "Markets now" ganhou a secção *"Today's alerts (as
  sent to the Telegram channel)"* — o MESMO detetor, config (alerts.yaml) e TEXTO
  (`plain_text(explain_anomaly(...))`) que o canal recebe; estado vazio honesto; AppTest
  atualizado exige a secção; docstring da app corrigido (dizia "baseline embedder", agora ONNX).
  (2) **`RELATORIO_FINAL.md` na RAIZ** — relatório de 10 min para o orientador/júri: o que existe,
  números congelados (verificados contra os .md de avaliação), mapa do repo, o que falta (humano).
  (3) **Guia de estudo em 2 versões**: detalhado = 64 slides (atualizado: frame do produto com
  ONNX/paridade 0,992 + intradiário; frame do Embedder com OnnxMiniLMEmbedder; recompila 0 erros);
  **simplificado NOVO = `docs/defence/guia_rapido.md`** (pitch 30s, tabela de números congelados
  todos verificados, 3 frases por componente, 8 perguntas do júri, plano B).
  (4) **`docs/design/migrar_repo.md`** — o aluno quer repo novo SEM história: procedimento
  `git archive` + religação (segredos/Streamlit/badges/CITATION) + trade-offs honestos (repo
  privado ≈ limite de minutos do Actions que o cron intradiário consome; verificado que a TESE
  não referencia URLs do repo/app → migração não toca na tese; alternativa sem risco = rename).
  NADA foi migrado — cliques do aluno. (5) Índices/README/caderno com cross-links das 3 camadas
  de estudo (rápido → caderno → 64 slides). **Veredicto de submissão dado ao aluno: o repo/tese
  estão prontos tecnicamente (gates todos verdes); falta APENAS o lado humano** (leitura final,
  licença+declaração IA com o orientador, app pública, pin do canal, post_validate 08-09/07).
- **🔧 SESSÃO 31 (hotfix, commit `ab14cda`):** a página "Markets now" rebentava no Streamlit Cloud
  com `TypeError: bad operand type for abs(): 'NoneType'` — quando o yfinance falha para TODOS os
  tickers (rate-limit nos IPs partilhados do Cloud), a coluna z-score fica toda `None` (dtype
  object) e o `sort_values(key=s.abs())` explode; localmente nunca acontecia porque ≥1 ticker
  respondia (coluna float). Fix: `key=lambda s: pd.to_numeric(s, errors="coerce").abs()` +
  teste de regressão `test_live_board_sem_dados_nao_rebenta` (provado: falha no código antigo com
  o erro exato do Cloud, verde com o fix; 107 testes no total). Verificado também contra
  pandas 3.0.2 (o Cloud corre Python 3.14 + pandas recente, não a stack pinada). Com o fix a
  página degrada com graça: linhas "⚠ no data right now" quando o Yahoo tranca — comportamento
  desenhado. **Nota de ambiente DESTE dispositivo:** não tem `.venv` nem Python 3.12 (só
  3.13/3.14); verificação feita com o Python 3.13 do sistema (`PYTHONPATH=repo` + AppTest);
  o CI valida na stack leve pinada. Para trabalho a sério aqui: instalar 3.12 + `setup_env.sh`.
- **🚀 SESSÃO 30 (produto + sync, pedido: "real product, no bullshit; tudo em sync; eu domino tudo"):**
  **Produto (commit `a941674`):** runner endurecido — `news_is_fresh` (anti-spam ≤2 dias; o scan
  olhava 7 dias e repetia a mesma manchete) e `bar_is_fresh` (anti-duplicado em feriados; só avalia
  com sessão nova), ambos puros/testados/configuráveis no alerts.yaml. **App pública com precedentes
  REAIS:** `scripts/curate_kb_light.py` → `data/samples/kb_fnspid_light.jsonl` (2.016 registos FNSPID
  2018–2023, 3,4 MB, VERSIONADA; estratificação determinística ≤36 por ticker×ano, só impactos
  completos); decisão **256-d com evidência** (a 64-d a consulta de recall da TSLA devolvia KO/XOM;
  a 256-d devolve o precedente certo); `kb_query_embedder()` lê a dim do próprio ficheiro (coerência
  por construção, guarda R1); caption honesta ("word overlap < SBERT da tese, gap na página
  Evaluation"). **Default de `run_news_trigger` INTOCADO** → demo/Cap. 3 (+6,46%) reproduzem.
  `load_prices`→`investigator.market_data.load_close_series` (build_kb + curadoria reutilizam).
  Badge "Alerts" no README. **Sincronia p/ defesa:** tese Cap. 6 — bullet futuro atualizado com
  honestidade (KB JÁ reconstruída; futuro = avaliação sobre ela; 76 pp, 0 erros, gates verdes);
  **caderno §0 = guião oral** (abertura 3 min + 15s por RQ, só números congelados) + **§6.5 =
  O produto HOJE** (como mostrar em 30s + plano B sem wifi); **guia 64 slides** (novo frame
  "O produto, HOJE", 0 erros); README sem staleness (bot construído, 16 frames/63 slides→agora 64
  no guia, KB artefacto). **106 testes + ruff verdes.** Próximo passo de produto DESENHADO (não
  construído): MiniLM-ONNX na nuvem (CHECKLIST, polimento).
- **🎯 PLANO FINAL (as 4 frentes pós-ML)** — o aluno pediu "fazer TUDO": polimento da escrita da tese,
  rename `src/`→`investigator/`, KB FNSPID multi-ano e S-APP Fase B, pela ordem que fizesse mais sentido.
  Ordem fixada e registada em **`progress/PLANO_FINAL.md`** (checkpoint multi-dispositivo): P1 escrita →
  P2 rename → P3 KB → P4 S-APP.
  **P1 FEITO (commit `5c4c099`):** passe editorial às secções novas da RQ4 (Ch2 §triage, Ch3 §met_triage,
  Ch5 CS4, Ch6 contribuições) — frases-comboio partidas, ecos removidos ("deliberately"×3→1 por zona,
  "precisely"×2→1 no total); diagnóstico prévio: 0 travessões-conectores em prosa, 0 tiques de IA.
  **Nenhum número/citação/equação alterado.** Reflow legítimo 74→76 pp (Cap. 3 verte uma página;
  densidade verificada página a página — sem páginas vazias); 0 erros, 0 cit. indefinidas, 0 overfull
  >15pt, 0 `??`; README/CHECKLIST com ~76 pp.
  **P2 FEITO (rename `src/`→`investigator/`):** `git mv` (história preservada); pyproject com
  empacotamento (`[project] name=investigator` + setuptools find) e **`-e .` no requirements.txt**
  (CI/Actions/Streamlit Cloud herdam); hacks `sys.path` removidos dos 12 scripts (o guard do
  `app/streamlit_app.py` fica de propósito — robustez no Streamlit Cloud); imports reescritos em todos
  os .py; ci.yml/verify.sh/tasks.json/tests.bat → `ruff check .`. **Bundles joblib re-serializados**
  (o pickle guardava `src.triage.model.PlattCalibrator` → shim temporário em sys.modules + redump;
  **probe numérico byte-a-byte idêntico** (a/b do calibrador, p_raw/p_cal em vetor zero) e load limpo
  sem shim; sidecars JSON intocados — **zero retreino, zero números novos**). Docs sincronizados
  (README/how_to_run/arquitectura/data_card/models/learning/caderno/guia/ML_PLAN/TRACKER/SESSIONS;
  linhas que descrevem o próprio rename preservadas como `src/`→`investigator/`). Validação: **93
  testes + ruff verdes; demo reproduz +6,46%; guia recompila 63 slides 0 erros**. Caderno: mapa do
  repo ganhou `models/`+`app/` e "14 frames"→16.
  **P3 FEITO (commit `f6553a2` — KB de retrieval FNSPID multi-ano como ARTEFACTO local):** build
  destacado (`run/kb-fnspid.cmd` + tarefa VS Code; log `data/kb_build.log`; HF offline) →
  **79.753 registos** SBERT 384-d em `data/kb_fnspid_sbert.jsonl` (~691 MB, gitignored); amostra de
  50 em `data/samples/kb_fnspid_sample.jsonl` — caminho NOVO de propósito (o `--sample` por defeito
  esmagaria a `kb_sample.jsonl` da demo/tese, dim 384≠64). Validação honesta em
  `docs/evaluation/kb_fnspid_build.md`: 14/15 tickers (META="FB"), 2023=44%, impactos ±1/3d
  completos, **200 registos (0,25%) com +5d=NaN** (fim da janela de preços, documentado); consultas
  AI/Fed/recalls devolvem os clusters certos (sim 0,62–0,85, cross-ticker OK). **Consumo:** produção
  na nuvem fica na stack leve (números da tese e deploy INTOCADOS); avaliação de retrieval multi-ano
  continua trabalho futuro (Cap. 6), agora com a base pronta. Data card atualizado.
  **P4 FEITO (S-APP Fase B — bot interativo SEM servidor):** decisão-chave = **long-polling**
  (getUpdates) em vez de webhook → grátis, sem host, atrás de NAT. Novo:
  `investigator/telegram_bot/{store,commands,interactive}.py` (lógica pura separada do transporte;
  SQLite stdlib em `data/bot_users.db` gitignored), `scripts/run_bot.py`, `run/bot.bat`, tarefa
  VS Code "Bot interativo"; comandos `/start /watch /unwatch /list /stop /help`. Runner: scanners
  devolvem (ticker, texto) e `_fanout_safe` distribui por subscritor — **`bot.enabled` no
  alerts.yaml, off por defeito, fail-open provado** (sem base → "fan-out saltado"; dry-run por
  defeito = comportamento de sempre, verificado ao vivo). Produto responsável: limite 20
  tickers/utilizador, `/stop` reversível, validação sintática de tickers, moldura "evidência do
  passado, nunca previsão". **10 testes novos → 103 no total** (todos offline); app Home com
  expander "Get the alerts on your phone" + métrica 103; README 103; going_live.md Fase B
  ✅ CONSTRUÍDA (webhook/host = evolução futura); how_to_run §2.5.
  **PLANO FINAL P1–P4: COMPLETO.** Restam APENAS os cliques humanos do CHECKLIST (app pública no
  Streamlit; licença + declaração ISEP com o Prof. Luís Gomes; leitura final; a 08-09/07 correr
  `python scripts/post_validate.py`; opcional renomear o repo GitHub). Para o bot ao vivo: correr
  `scripts/run_bot.py` numa máquina + `bot.enabled: true` no alerts.yaml.
- **🤖 WORKSTREAM ML (RQ4) — M0–M6 + M7-TESE COMPLETOS.** Gate aberto pelo orientador (2026-07-04; confia no aluno, de férias). **M6 FEITO (madrugada de 05/07, processo destacado):** FNSPID 2018–2023 → **79.753 exemplos** (1.501 dias únicos, 0 descartes; **14/15 tickers** — META="FB" no corpus, reportado; positivos 38,5/47,0/37,8% — sem regime shift; densidade cresce: 2023=44% das linhas); retreino SBERT com HF_HUB_OFFLINE=1 (o hub falhou com o modelo em cache — 1.ª tentativa de retreino morreu nisso). **RESULTADO FINAL (teste, prevalência 0,378):** PR-AUC **vol 0,542** > contexto 0,538 > full 0,496 > GBM 0,469 > texto 0,439 > sempre 0,378 ⇒ **nenhum modelo com texto bate a volatilidade** (pré-comprometido, reportado tal como é); **MAS precisão@5/dia 0,632 vs 0,163** (quase 4×), Brier 0,218 vs 0,622 ⇒ triagem vale como mecanismo. 2.ª comparação "aprendido vs simples" ganha pela escolha transparente (1.ª = IF vs z-score). **M7-TESE FEITA:** RQ4 de ponta a ponta — Ch1 (RQ4+objetivo+contribuição), Ch2 (secção triagem; 52/52 citações verificadas), Ch3 (modelo+protocolo+data card FNSPID atualizado), Ch4 (componente+decision logic+deploy honesto), Ch5 (**Case Study 4** com tabela/figuras + IF no CS1 + "four studies"), Ch6 (veredicto RQ4 "No on the text hypothesis; yes on the mechanism" + 4 contribuições + limitações/futuro), abstract EN 197≤200 + resumo PT. **Compila 74 pp, 0 erros, 0 cit. indefinidas, overfull máx 12pt; 93 testes + ruff verdes.** learning.md §16 com números finais. **M7-MATERIAIS FEITOS (05/07):** paper IEEE **4 pp** (+2 refs; subsecção "Materiality triage"; abstract/related/system/discussão/conclusão), slides de defesa **16 frames** (+RQ4 no frame das perguntas, +frame "Result 4", limitações/conclusões atualizadas, +3 perguntas de júri sobre triagem/lookahead/RL), guia de estudo **63 slides** (+3 frames que ENSINAM a triagem do zero — tarefa/rótulo/split/calibração/métricas/resultado + loop de pós-validação; slide "o que usa/NÃO usa" corrigido: JÁ treina um modelo, deep learning continua fora), caderno de defesa (§5 secção RQ4 completa + 5 linhas novas no mapa de números + 4 perguntas de júri novas incl. "o vosso modelo perdeu — é um fracasso?"), app (métricas 93✓/52/52; "trains no model" corrigido para "one model trained by the author") e README (93 testes, 52 refs, ~74 pp, layout com models/ e investigator/triage/). Page-audit estendido (secção "Extensão M7"). Tudo compila 0 erros; 93 testes + ruff verdes. **O workstream ML está 100% fechado (M0–M7).** Loop M5.5 armado (3 decisões reais pendentes maturam ~08-09/07 → `python scripts/post_validate.py`).**
  Plano-mestre multi-dispositivo: **`progress/ML_PLAN.md`** (caixas de estado no §3). Feito: dataset com
  rótulos anti-lookahead (testado por mutação do futuro), 6 famílias treinadas com SBERT real, calibração
  Platt, reproduzível (2 corridas = métricas idênticas; retreino do M5 = joblib **bit-idênticos**),
  **modelos versionados em `models/`** (LR 18 KB + GBM 1,1 MB + **contexto-só 1,8 KB de produção**).
  Smoke honesto (corpus 4 semanas, regime shift): GBM PR-AUC 0,461 > vol 0,445; texto ainda não ajuda
  (0,357) → motiva FNSPID (M6). **M4:** Isolation Forest causal PERDE para o z-score (F1 0,271 vs 0,530)
  — a escolha estatística fica validada por comparação. **M5 (integração off-by-default):** produção
  (runner/app, stack leve, sem SBERT) pontua a variante só-contexto via `investigator/triage/infer.py`;
  `news.min_materiality` no `config/alerts.yaml` (null = comportamento de sempre; fail-open sem
  modelo/histórico); linha de materialidade opcional no `explain_news_impact`; severidade +
  contribuições na página News da app (graciosa sem `models/`; AppTest verde com e sem). Validado ao
  vivo em dry-run (NVDA real: P=36% com linha; gate 0,99 suprime; sem modelo avisa e segue).
  **M5.5 (loop de pós-validação = a ideia "RL" do aluno, forma defensável):** o runner regista cada
  decisão de notícia em `data/predictions_log.jsonl` (fail-safe); `scripts/post_validate.py` rotula as
  maturadas (janela (d,d+3] fechada) com o resultado REAL (mesma regra do treino, preços frescos) →
  `docs/evaluation/live_monitoring.md` (precisão ao vivo, Brier, calibração, receita de retreino).
  Validado: 3 decisões reais registadas (pendentes, correto) + sonda antiga maturou contra preços
  reais (Brier 0,25 = (0,5−1)² exato). **93 testes + ruff verdes.** **Falta:** M6 (FNSPID overnight,
  **click do aluno**) → M7 (tese/guia/slides, **gated no OK do Prof. Luís Gomes** — proposta pronta em
  `docs/internal/proposta_ml_orientador.md`, **o aluno tem de a enviar**).
- **REBRANDING InvestiGator (Sessão 28, 2026-07-03):** o aluno escolheu o nome **"InvestiGator"** (investigate+alligator; mascote jacaré-detetive à Sherlock) e, avisado do peso académico (Cap. 4, abstracts, figuras, júri vê o trocadilho), **decidiu explicitamente: renomear TUDO, incluindo a tese**. Executado: **renomeação total do nome antigo → InvestiGator** em tese (96 menções; Ch4 = "InvestiGator: An Explainable Financial-Alert System…"), paper, slides de defesa, guia de estudo, caderno, app, README, docs de design, scripts, CITATION, config. **Técnica segura:** primeiro só o texto VISÍVEL (CAPS/small-caps→plain), com os *labels* LaTeX internos intactos (zero refs partidas); gramática EN corrigida ("A …"→"An InvestiGator"). **História:** o aluno correu depois um replace global próprio que renomeou também os registos datados (`progress/`, `docs/decisions/*`) e os labels LaTeX (consistente — verificado); o nome antigo fica preservado na história do git. **Validado:** tese recompila **72 pp, 0 erros, 0 citações/refs indefinidas** (TOC confirma o novo título do Cap. 4); paper 3 pp, slides 15 pp, guia 60 pp — todos 0 erros; **47 testes + ruff verdes**; AppTest sem exceções. **Mascote:** `app/assets/investigator.svg` (SVG desenhado à mão: jacaré com deerstalker, monóculo, lupa, laço) no `st.logo` + Home da app + topo do README; favicon 🐊; tagline *"Investigate. Don't speculate."* **Go-live (estado):** repo **público** (verificado por API; história limpa — scan de segredos aos 128 commits: 0), canal Telegram criado, 3 segredos definidos, workflow corrido; **URL vivo** <https://investigator-ddc9d8618935.herokuapp.com> no README/CHECKLIST. **Falta 1 clique humano:** a app ainda pede login (foi implantada com o repo privado) → share.streamlit.io → app → ⋮ → Settings → **Sharing → pública**. Opcional: renomear o repo GitHub `DIMEIA`→`InvestiGator` (redireciona; depois atualizar badges + re-ligar Streamlit).
- **AUDITORIA + POLIMENTO + FLAGSHIP (Sessão 27, 2026-07-02):** o aluno pediu uma auditoria profunda ("team de arquiteto/staff eng/reviewer…") ao repositório (não à tese) e autorizou **relatório + polimento seguro + 1 feature** (runway: meses até submeter). **Relatório de auditoria** escrito no plano (`.claude/plans/…squishy-yeti.md`): scorecard honesto (Overall 8.5, Arch 9, Docs 9, Thesis 9.5, Reprodutibilidade 7, Deploy 3, UX 6, Maint 8.5, Debt baixo), Top-25, críticos/altos/médios, e desenhos de Streamlit/cloud/Telegram-onboarding/multi-mercado como **trabalho futuro** (desafiando o prompt genérico: a tese NÃO treina modelos nem prevê preços — manter assim). **Executado (tudo com 43 testes + ruff verdes, números da tese inalterados):**
  **(P0 reprodutibilidade/CI/organização)** — (C1) `requirements.txt` passou a **leve**; nova `requirements-ml.txt` (torch CPU + SBERT, com `--extra-index-url` da PyTorch no próprio ficheiro); `setup_env.sh` leve por defeito + flag `--ml` — **corrige o "correr num comando" que falhava numa máquina limpa** (torch `+cpu` não está no PyPI). (C2/C3) novo **`.github/workflows/ci.yml`** (pytest+ruff em runner limpo a cada push de código) — o CI antes só compilava a tese; afirmação "CI corre testes" corrigida. **CITATION.cff** novo; **`docs/README.md`** índice; `ROOT_PROMPT_CLAUDE_CODE.md` → `docs/internal/`; badges no README; **licença de código deixada por decidir com o orientador** (nota honesta, sem escolher IP).
  **(P2 flagship)** — **`app/streamlit_app.py`**: dashboard interativo sem estado por cima das funções validadas (Home, News trigger com tabela de precedentes real, Market trigger z-score ao vivo, Evaluation com números validados, How it works com grafo, About/cite). Validado: boota headless (health `ok`) + **AppTest ponta-a-ponta** (Home/News/Evaluation sem exceções; clique devolve 3 precedentes). `requirements-app.txt` + `docs/design/deployment.md` (Streamlit Community Cloud, grátis); ruff cobre `app/`. **Honesto:** sem previsão, não envia nada, usa o embedder baseline (SBERT fica na página Evaluation).
  **DEFERIDO (com razão):** renomear `src/`→`investigator/` (pacote instalável, tirar o `sys.path`) — benefício interno vs. **grande churn de docs** (inventário no CLAUDE.md, caderno, learning/glossary, slides do guia referenciavam `src/…`); merece **sessão dedicada** com sync de docs. Verificado que **nem a tese nem o paper referenciam `src/`** (a reescrita tirou identificadores de código), por isso o rename não afeta a tese quando for feito. **→ EXECUTADO (P2 do PLANO_FINAL, 2026-07-05): pacote `investigator/` instalável (pyproject + `-e .`), hacks sys.path removidos, bundles re-serializados com probe idêntico.**
  **(P3 UX / correr por cliques)** — para quem evita a consola: **`.vscode/`** versionado (Run & Debug ▶ Dashboard/Demo/ficheiro + tarefas: Tests, "Tests + lint (verify)", compilar Thesis/Slides/Guia/Paper, Setup leve/`--ml`), **`run/*.bat`** (duplo-clique: dashboard/demo/tests/thesis), guia **`docs/design/run_in_vscode.md`**, e **`CHECKLIST.md`** na raiz (lista viva com caixas: feito / humano / polimento / tese / futuro). Tudo aditivo (config/docs); 43 testes + ruff verdes.
  **(P4 going-live 24/7, grátis, sem servidor)** — o aluno pediu "app sempre up, users com notificações no telemóvel, webpage a qualquer hora, tudo grátis". Decisão (confirmada): **faseado** — Fase A agora sem servidor; Fase B (bot interativo por utilizador, host do Student Pack + BD) só desenhada. **Clarificados 3 equívocos** ao aluno: NÃO há modelo treinado (por desenho — SBERT pré-treinado em cache HF + KB construída + matemática pura); NÃO havia timer/servidor/listener (cada gatilho corria 1x e saía); para push agendado NÃO é preciso servidor always-on (cron grátis do GitHub Actions ≫ mais simples). **Construído (Fase A):** `config/alerts.yaml` (watchlist 10 tickers, window/threshold, news opt-in; sem segredos), `scripts/run_alerts.py` (varre watchlist → `detect_latest` → `explain_anomaly` → envia ao canal Telegram; `--dry-run`; **no-op seguro e exit 0 sem segredos**; news scan opcional via Finnhub), `.github/workflows/alerts.yml` (cron `30 21 * * 1-5` UTC ~pós-fecho US + `workflow_dispatch`; `permissions: contents: read`; stack leve; segredos só em Actions Secrets), `tests/test_run_alerts.py` (4 testes puros), runbook **`docs/design/going_live.md`** (PT-PT: criar canal, 3 segredos, testar, caveats do cron UTC/best-effort/60-dias, Fase B com Student Pack). **Validado:** dry-run ao vivo apanhou anomalia real (META +8,44%, z=+3,31) sem enviar; **47 testes** (43+4) + ruff verdes. `.env.example` nota canal; README secção "📡 Live 24/7"; CHECKLIST com os cliques humanos.
  **Próximo humano:** (1) declaração ISEP de IA + data; (2) leitura final; (3) **escolher a licença de código** com o Prof. Luís Gomes; (4) **go-live**: criar canal Telegram + 3 segredos no GitHub + correr o workflow "Alerts" 1x + publicar o dashboard e colar o URL. **Acompanhar em `CHECKLIST.md`.**
- **ORGANIZAÇÃO & SINCRONIZAÇÃO (Sessão 26, 2026-07-01):** fecho do workstream "correr a app / organização e qualidade" pedido pelo aluno ("avança com 2 e 3 e com o que puderes e mais além… sobretudo a nível de organização e qualidade"). (1) **README como porta de entrada** reescrito: bloco "▶ Run it in one command" (`bash scripts/setup_env.sh` → `python scripts/demo.py`), secção "Learn it / prepare the defence" (guia de estudo 60 slides + slides 15 frames + caderno), números corrigidos (43 testes, ~72 pp), layout do repo atualizado (`slides/guia_estudo/`, `scripts/demo.py`), comandos de build de todos os artefactos. (2) **Slides de defesa sincronizados** com a tese reescrita: `\tikzset` anti-hifenização global no preâmbulo (mesma regra da tese, sem cortes de palavra) + **novo frame "The data model — the objects"** logo após a arquitetura (NewsItem→esquema partilhado→NewsRecord=caso→1..\*→KB; Embedder→embedding; AnomalyResult) — render confirmado limpo → **15 páginas, 0 erros**. (3) **Guia de estudo: +3 frames de exemplos/organização** (agora **60 slides, 0 erros**): exemplo honesto "quando o baseline **falha** e porquê" (consulta de banca JPM → scores baixos AAPL 0.25/JPM 0.15 porque o HashingEmbedder só vê sobreposição de palavras → motiva o SBERT: problema de vocabulário); "**Constrói a tua própria KB**" (mini-tutorial `scripts/build_kb.py` baseline vs `--sbert`); "**Onde continuar a estudar**" (cross-links demo↔how_to_run↔tese↔slides↔caderno). **Números da tese inalterados; demo reproduz +6,46%; 43 testes + ruff verdes; citações 50/50.** (Opcional futuro: sincronizar `paper/` com a tese reescrita; estender o guia.)
- **POLIMENTO VISUAL + GUIA DE ESTUDO (Sessão 25, 2026-06-28):** (1) **Figuras presentation-quality:** regra global em `main.tex` para os nós de diagrama nunca cortarem palavras a meio (corrige "Abrupt mar-ket move"); auditadas por render as 15 figuras (9 diagramas TikZ + 6 gráficos) — sem cortes, sem colisões, rótulos legíveis; gráficos vetoriais de alta resolução; tabelas 0 overfull. Nenhum número alterado; tese compila 72 pp, 0 erros. (2) **Novo guia de estudo do zero** em `slides/guia_estudo/main.tex` (Beamer PT-PT, 51 slides, compila 0 erros): ENSINA (não resume) a quem não tem base em IA. Partes: P0 capa/pitch; **P1 IA do zero só o que a tese usa** (+ slide honesto "o que NÃO usa: sem treino/CNN/visão computacional" — a tese usa SBERT pré-treinado, estatística, cosseno, event study) + glossário; P2 problema/contribuição; P3 sistema (modelo de dados, componentes, gatilhos); P4 dados a olho (CSV e um caso JSON REAIS de `data/samples/`); P5 **código módulo-a-módulo** (snippets fiéis ao `investigator/`, linha a linha); P6 **workflow** com exemplos reais (TSLA z=+7,61; recuperação Nvidia + nota tema≠direção); P7 avaliação (reutiliza os gráficos validados); P8 decisões; P9 sensibilidade; P10 perguntas do júri + checklist. **Só conceitos/código/números reais; 0 fabricação.** (Opcional futuro: sincronizar paper/slides/caderno; estender o guia.)
- **REESCRITA PROFUNDA (Sessão 24, 2026-06-28):** a pedido do aluno (a tese ainda lia densa/cansativa e o núcleo não ficava claro), reescrita de raiz para **clareza progressiva**, dentro dos 6 capítulos canónicos (decisões confirmadas: reescrever a própria tese; manter 6 capítulos; **foreground do system design no corpo**). Plano + registo por capítulo em `.claude/plans/…squishy-yeti.md` e `docs/decisions/editorial_review.md`. **Feito (commits por capítulo):** Ch1 (secções guiadas por pergunta + **mapa do leitor**), Ch2 (cada secção com pergunta + takeaway "For InvestiGator"; **−4 pp**), Ch3 (**concept-first**: cada técnica abre por "What it is for:"; "três escolhas" → lista), **Ch4 = System Design reconstruído** (NOVO diagrama do **modelo de dados**: NewsItem/NewsRecord=caso/KB/Embedder/AnomalyResult; NOVA tabela **componente|responsabilidade|entrada→saída**; secção **Decision Logic**; reutiliza arquitetura/fluxo conectado/mockup), Ch5 (cada estudo abre com **pergunta+resposta**), Ch6 (vereditos RQ a negrito + limitações/futuro em listas). **Travessões conectores em prosa: 0** em todo o corpo. **Sem inventar nada:** nenhum número, equação, algoritmo, tabela, figura ou citação alterado; **citações 50/50** (0 órfãs/indefinidas). **Estado: compila 72 pp (era 78), 0 erros, 0 citações indefinidas, 0 overfull >15pt, 0 `??`; 43 testes verdes + ruff.** Falta: **leitura do aluno** (validar a nova voz/estrutura) + tarefas humanas (declaração ISEP). Pendente opcional: sincronizar paper/slides/caderno com a tese reescrita.
- **REVISÃO EDITORIAL (Sessão 23, 2026-06-28):** copy-edit humano de ponta a ponta, **capítulo a capítulo com pausa** (plano em `.claude/plans/…squishy-yeti.md`; registo por capítulo em `docs/decisions/editorial_review.md`). Decisões: **manter EN-GB** (resumo PT revisto também); **só a tese** (artefactos sincronizados no fim). **Feito:** Ch1–Ch6 + front matter (abstract/resumo) + Apêndice A revistos. **Travessões conectores em prosa: 117 → 1** em todo o corpo (resta 1 célula de tabela "não-aplicável"). Frases longas partidas, jargão simplificado ("desiderata"→"goals", "impounded"→"absorbed"), tiques removidos ("Crucially/moreover/precisely why/head on"), construções invertidas reescritas, rótulos de tabela harmonizados ("SBERT (MiniLM)"). **Declarações (integridade+IA) e Apêndice A deixados como estão** (formais/já limpos). **Nada de conteúdo, números, citações, equações, algoritmos, tabelas ou figuras alterado.** Gate final: coerência global verificada (terminologia consistente, 0 espaços duplos, 0 artefactos), abstract 192 palavras (≤200); artefactos (paper 3pp / slides 14pp) compilam e continuam alinhados. **Estado: compila 78 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt, 0 `??`; 43 testes verdes + ruff; citações 50/50.**
- **REVISÃO TIPO-JÚRI (Sessão 22):** li os 6 capítulos + front matter + apêndice como orientador/revisor/examinador (plano em `.claude/plans/…squishy-yeti.md`, agora reescrito como relatório de revisão com severidades + scorecard por capítulo). **Correções implementadas (nenhuma citação/número alterado):** **M1** — parágrafo honesto no Cap. 5 (CS3): a recuperação semântica capta *tema*, não *direção*, por isso um título positivo recupera um *cluster* de ameaça competitiva com impacto médio negativo (−1,97%); a média é evidência sobre um tema, não previsão; notados os artefactos (mesma data; ticker duplicado partilha impacto) do corpus recente; liga a `lee2004trust`/`bansal2021whole`. **M2** — *data card* (Cap. 3) anotado como camada FNSPID *desenhada*, com nota a apontar para o corpus real avaliado (3 714 títulos recentes) usado no Cap. 5; cláusula correspondente no Cap. 5. **Mo2** — mockup do Telegram tornado internamente consistente (3 precedentes mostrados → média −2,2%). **Mo4** — parágrafo de produto responsável no Cap. 4 (fadiga de alertas; over-reliance; ranking por severidade, de-dup de precedentes, sinalizar discordância de direção) + linha no Cap. 6. **Mo3** — Apêndice A: tabela de versões fixadas (do lock file) + 3 comandos exatos de reprodução; LOF expandido no Cap. 2. **Mi1** — fraseado da RQ2 (baselines aplicam-se à recuperação, não ao impacto). **M3** — passagem de naturalidade: travessões `---` reduzidos de **117 → 39** (Cap. 2 48→23, Cap. 4 18→2, Cap. 5 26→2), preservando sentido. **Estado: compila 78 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt, 0 `??`; 42 testes verdes + ruff; integridade de citações 50/50 (0 órfãs, 0 indefinidas).**
- **MASTER PLAN (estrada longa até submissão, publicação e defesa):** ver **`progress/_historico/MASTER_PLAN.md`** —
  Fases A (conteúdo+visuais → ~80 pp) · B (naturalidade) · C (revisão crítica do zero) · D (revisão crítica
  da implementação + "como correr") · **E (validação ultra-rigorosa página-a-página + RE-VERIFICAR TODAS as
  citações — porta de submissão)** · F (publicação IEEE) · G (slides de defesa) · H (caderno de defesa visual).
  Continuidade multi-dispositivo: este ficheiro + `MASTER_PLAN.md` + `TRACKER.md`, commit/push por sessão.
- **Fase atual + último passo concluído:** **REWORK COMPLETO — plano S1–S9 concluído.** O aluno leu o PDF e ficou desiludido (demasiado técnico/"software-ish", curto, desorganizado, literatura fraca, poucas figuras e confusas, nomes de pastas e **português visível**). Executado o plano definitivo multi-sessão (`.claude/plans/…squishy-yeti.md`; checklist em `progress/TRACKER.md`):
  **S1** estrutura canónica MEIA de 6 capítulos (Introduction · State of the Art · Methods and Materials · **InvestiGator** · Case Studies · Conclusions) + declutter (removidos `notebooks/`, `presentation/`, `impact_analyzer/`).
  **S2** Cap. 3 aprofundado (data card FNSPID, IA responsável, metodologia de avaliação).
  **S3** Cap. 4 (InvestiGator) ao nível de desenho: arquitetura limpa + fluxos dos 2 gatilhos + **mockup Telegram** + tabela de decisões; detalhe técnico no Apêndice A.
  **S4** Case Studies com figuras reais novas (série temporal de anomalias TSLA; ablação à janela).
  **S5** Estado da Arte com **+20 fontes → 36 refs verificadas**, 2 figuras de taxonomia.
  **S6** auditoria de citações (36 citadas = 36 no .bib = 36 renderizadas; 0 indefinidas) + consistência global.
  **S7** reorganização de `docs/` em subpastas (`design/ evaluation/ decisions/ defence/ _archive/`); caminhos atualizados.
  **S8** **Caderno de Defesa (PT-PT)** em `docs/defence/caderno_de_defesa.md`.
  **S9** validação final. **Estado: compila 66 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt; 41 testes verdes + ruff limpo; 0 identificadores de código e 0 PT no corpo; 5 figuras; figuras de avaliação em EN; números reprodutíveis (janela de anomalia fixa).**
- **FASE A CONCLUÍDA (76 pp, dentro do alvo "~80-ish") · FASE B INICIADA.** **Concluído (A):** A1 3 algoritmos (Lista de Algoritmos preenchida) · A2 figura do fluxo mestre de dados/passos (Cap. 4) · A3 figura conceito de embeddings + linha temporal do event study (Cap. 3) · A4 exemplos trabalhados (z-score hipotético no Cap. 3; **recuperação real reproduzível** sobre a KB-amostra no Cap. 3 — query Nvidia → 3 precedentes AI, match cross-ticker MSFT, impacto médio +5d=+6.5%; **anomalia real** TSLA 24-10-2024 z=+7.61 no Cap. 5) · A5 Lista de Código removida. **+ Cap. 2 §2.7 "Existing Tools for the Retail Investor"** (vs alertas de corretora / apps de sentimento / robo-advisors; tabela; 2 citações novas verificadas: `dacunto2019robo`, `cardillo2024robo`). **+ Cap. 5 "Threats to Validity"** reescrito pela taxonomia (construct/internal/external/statistical-conclusion). **+ Cap. 4 diagrama de sequência (UML) do gatilho de notícias.** **+ Cap. 2 §2.5 "Information Retrieval and Ranking Evaluation"** (fundamenta cosine/embeddings, baseline lexical e a métrica precision@k; 3 citações verificadas: `salton1975vsm`, `robertson2009bm25`, `manning2008ir`). **+ Cap. 2 EMH** (Fama 1970 fundamenta a recusa de previsão). **+ Cap. 2 §"Trust and Appropriate Reliance"** (Lee&See 2004, Bansal 2021 — porque um não-especialista precisa de explicações; reliance apropriada) **+ grounding de volatilidade** (Engle 1982 ARCH, Bollerslev 1986 GARCH justificam o rolling-std). **+ `docs/design/how_to_run.md`** (guia do operador, testado). **+ Cap. 3 §"Evaluation Methodology" formalizado** (precision@k com fórmula + proxy de setor + restrição cross-ticker; o que cada baseline controla; multi-seed; argumento label-free da anomalia; 3 garantias) → 72→74 pp. **+ Cap. 3 justificação da medição de impacto** (raw vs CAR; horizontes; agregação). **+ Cap. 4 diagrama de sequência do gatilho de mercado** (par completo) → 74→76 pp. **FASE B iniciada:** passagem de naturalidade nas secções novas do Estado da Arte (IR + trust) — menos travessões/tics de IA. **Estado: compila 76 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt; 50 refs (todas citadas, 0 órfãs); 41 testes verdes + ruff limpo.**
- **CONTAGEM DE PÁGINAS:** 76 pp (alvo do aluno: "80-ish" → atingido com conteúdo genuíno, SEM encher). ~16 são versos em branco (`twoside`/`openright`) → conteúdo real ≈ 60 pp. Confirmado: prosa em zonas pouco densas (SoTA/Métodos) transborda para páginas novas; figuras em capítulos densos são re-empacotadas. **Não forçar mais páginas** (risco de bloat que o aluno proíbe).
- **FASES B, C, D CONCLUÍDAS nesta sessão.** **B (naturalidade):** voz académica/natural em todo o conteúdo novo (menos travessões/tics de IA); resto já passado. **C (revisão crítica do zero):** `docs/decisions/review_log.md` — achados C-1..C-5 corrigidos (lista do SoTA no Cap. 1; nota do *lift*; clareza cross-ticker no consumo; mockup como ilustração; cross-ticker é escolha de avaliação). **D (revisão de implementação + estatística):** `docs/decisions/implementation_review.md` — **os 3 scripts de avaliação foram RE-CORRIDOS hoje (SBERT 5.6.0 + corpus presentes) e reproduzem EXATAMENTE os números da tese**; 42 testes verdes (inclui `@sbert`) + ruff; guarda R1 (dimensão embedder–KB) adicionada. Veredito: desenho certo, sem mudanças necessárias.
- **FASE E CONCLUÍDA (porta de submissão passada).** `docs/decisions/page_audit.md`: as **50 citações foram re-verificadas independentemente hoje** (script → Crossref/arXiv + ISBN + fontes primárias); **50/50 OK**, 0 fabricação. Melhorias: +DOI `aamodt1994cbr` e `lipton2018mythos`, +URL `ding2015deep`. Fontes primárias confirmadas nas páginas oficiais com os números exatos (Gallup 62/87/28%, SIFMA US$62,2T, CCAF 81/71%). PDF: 76 pp, 0 erros, 0 citações/refs indefinidas, 0 `??`, 50 na bibliografia (=50 citadas), 0 overfull >15pt. **Superfície de ataque sobre fontes = ZERO.**
- **FASE F CONCLUÍDA:** `paper/` — artigo IEEE (IEEEtran conference) destilado da tese **validada**; compila 3 pp, 0 erros, 0 citações indefinidas; 23 refs (subconjunto verificado); reutiliza figuras validadas; só sobre implementação/estatística já validadas. README com nota de expansão para um *venue*.
- **FASE G CONCLUÍDA:** `slides/` — slides de defesa (Beamer, 14 frames) destilados da tese validada; compila 0 erros; último frame = perguntas antecipadas do júri.
- **FASE H CONCLUÍDA:** `docs/defence/caderno_de_defesa.md` melhorado e **visual** — §2 workflow em diagramas, §4.5 exemplos reais passo-a-passo (TSLA z=7.61; recuperação Nvidia cross-ticker), §5.5 mapa dos números validados (número→script→tese), repo map atualizado, +2 perguntas do júri; números desatualizados corrigidos (0,55→0,514).
- **MASTER PLAN A–H COMPLETO.** Estado entregável: tese 76 pp (0 erros, 0 citações indefinidas/órfãs, 0 overfull >15pt; 50 refs **re-verificadas** uma a uma); estatística **re-corrida e idêntica**; 42 testes + ruff verdes; `paper/` (IEEE) e `slides/` compilam; documentos de rigor (review_log, implementation_review, page_audit) commitados; tudo pushed.
- **PRÓXIMO (só HUMANO — porta de submissão):** (1) confirmar com o Prof. Luís Gomes a **redação exata da declaração de uso de IA** exigida pela MEIA/ISEP + a **data de entrega**; (2) **leitura final do aluno** a toda a tese (o texto é seu para defender, §6.6). Opcional futuro: build FNSPID multi-ano; estudo humano de utilidade; expandir o paper para um *venue*.
- **Nota de ambiente:** o venv 3.12 usa a **stack leve** (`requirements.txt`: numpy/pandas/matplotlib/yfinance/pytest/ruff) — chega para a demo, os testes e as avaliações. Para os testes `@sbert` e re-correr a recuperação completa (SBERT/torch), correr `bash scripts/setup_env.sh --ml` (stack pesada, `requirements-ml.txt`, torch do índice CPU da PyTorch). **CI:** `ci.yml` corre `pytest`+`ruff` a cada push de código (stack leve, runner limpo); `compile-thesis.yml` compila o PDF a cada push a `thesis/**`.
- **Verificação de integridade da sessão:** confirmar que este ficheiro, `progress/TRACKER.md` e `progress/SESSIONS.md` foram lidos nesta sessão.

---

## Contexto do Projeto (resumo compacto do ROOT PROMPT)
- **Aluno:** Henrique José da Silva Santos — MEIA (ISEP), 2.º ano, fase de dissertação. Nº 1180934.
- **Orientador:** Prof. Luís Gomes. **Coorientador:** Rafael Silva.
- **Perfil do aluno (§3):** não é especialista em IA, tem lacunas de base; objetivo central = **terminar uma dissertação sólida e defendê-la com calma** (pessoa nervosa). **Regra de ouro: ensinar à medida que se avança** (explicar cada conceito em PT-PT em `docs/decisions/learning.md` + `docs/decisions/glossary.md`, com nota de "como explico ao júri em 3 frases" por componente). **Simplicidade defensável > sofisticação.**
- **Contribuição (enquadramento permanente):** tese de **Engenharia de IA**. A contribuição NÃO é inventar algoritmos — é **integrar, aplicar e avaliar criticamente** componentes existentes num sistema funcional, explicável e reproduzível, com uma metodologia documentada de correlação notícia–impacto. Usar modelos/ferramentas existentes **é** o trabalho de engenharia.
- **Tema:** sistema inteligente de alertas financeiros para investidores de retalho, **XAI-first** (toda a lógica transparente e rastreável). Dois gatilhos: (1) movimento abrupto de mercado (NYSE/NASDAQ) → anomalia estatística → alerta + explicação; (2) nova notícia financeira → alerta + impacto potencial + precedentes históricos. **Núcleo:** motor de correlação notícia–mercado baseado em histórico (FNSPID). **Saída:** alertas via Telegram com evento + explicação + fontes + precedentes.
- **Restrições não negociáveis (§5.2):** apenas APIs gratuitas; foco mercado US (NYSE/NASDAQ); XAI-first; útil a um investidor real; rigor académico. ❌ Sem previsão de preços, sem trading algorítmico, sem APIs pagas, sem conteúdo de enchimento.
- **Disciplina de âmbito (§5.3):** primeiro uma **fatia fina end-to-end**; cada componente começa na versão mais simples e defensável; perguntar antes de adicionar complexidade; cortar opcionais se o prazo apertar.
- **Arquitetura de dados (§5.4):** camada **HISTÓRICA** = FNSPID (`Zihan1004/FNSPID`, CC BY-SA 4.0 — atribuição obrigatória); camada **LIVE** = yfinance + (a confirmar) Finnhub/Alpha Vantage/GNews/RSS.
- **Horizonte:** ~30 sessões (guia flexível, orientado pela qualidade). **Continuidade entre sessões é o requisito nº 1.**

---

## Decisões Confirmadas
- **Variante de Inglês (tese):** **EN-GB** (bloqueada; nunca misturar). [Sessão 0]
- **⚠️ TESE BILINGUE (Sessão 40):** existem **DUAS** teses — `thesis/` (EN-GB) e `thesis-pt/` (PT-PT)
  — com o MESMO conteúdo (tradução pura, mesmo estilo). **REGRA DE SINCRONIA:** qualquer alteração de
  conteúdo a uma língua TEM de ser espelhada (traduzida) na outra, no mesmo sítio — prosa, legendas,
  texto de figuras TikZ, tabelas, front matter. Números/citações/labels/estrutura idênticos; só a
  língua muda. Gráficos de dados (matplotlib `eval_*.pdf`) ficam EN nas duas (autorizado). Detalhe +
  tracker por capítulo em `progress/BILINGUAL_PLAN.md`. **Verificar sempre:** as duas compilam a 0
  erros e têm a mesma contagem de secções/figuras/tabelas.
- **Idioma docs de aprendizagem/internos:** **PT-PT** (o único toggle do §0). Tese em EN **e** PT
  (bilingue, ver acima). [Sessão 0; revisto Sessão 40]
- **Versão de Python fixada:** **3.12** (estabilidade para torch/transformers/sentence-transformers; 3.14 corre risco de faltar wheels). [Sessão 0]
- **Título escolhido:** **T1** — *Explainable Financial Alerts for Retail Investors: Integrating Statistical Anomaly Detection and News–Market Impact Correlation* (EN-GB). [Sessão 2 / D-008]
- **APIs aprovadas:** proposta (Fase C, `docs/design/free_apis.md`, verificado 2026-06-21) — preços: yfinance (base) + Finnhub (fallback, 60/min); notícias: Finnhub news + RSS (+ GNews/Marketaux opcional); histórico: FNSPID; alertas: Telegram Bot API. Alpha Vantage só ocasional (25/dia).
- **Metodologias de IA por componente:** [APÓS FASE C]
- **Estrutura de capítulos:** 7 capítulos (Introduction · Contextualization · Literature Review · Methodology · Implementation · Evaluation · Conclusion), mapeados em `thesis/ch1..ch7/` do template ISEP. [Sessão 3 / Fase D]
- **Layout LaTeX:** usar a estrutura/classe nativa do template ISEP (`meia-style.cls`, `authoryear-comp`, `chN/`); o esboço `thesis/chapters/0X_*.tex` do §9 é ilustrativo e será reconciliado na Fase D. [Sessão 0]
- **Autonomia máxima (pedido do aluno, 2026-06-21):** **NÃO usar AskUserQuestion para confirmações de rotina** ("Yes, continue"). Prosseguir e decidir sozinho ao longo das fases/sessões, com defaults sensatos. Parar **apenas** para os limites rígidos do §2.2 (operações irreversíveis/destrutivas, gastar dinheiro, segredos) ou decisões académicas mesmo irreversíveis. `.claude/settings.json` alargado em conformidade. [D-009]
- (Racional completo em `progress/DECISIONS.md`.)

---

## Estado LaTeX
> ⚠️ **EM REWORK (S1–S9).** As notas abaixo são pré-rework (7 capítulos, 53 pp, 16 refs). **Estado atual real:**
> 6 capítulos canónicos MEIA (Introduction · State of the Art · Methods and Materials · InvestiGator · Case Studies ·
> Conclusions), **50 referências verificadas**, **compila 76 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt**;
> figuras de avaliação em EN; arquitetura redesenhada + fluxo + mockup Telegram; 3 algoritmos; figura de embeddings;
> exemplos trabalhados reais (recuperação + anomalia). **Achado medido:** 16/70 pp são versos em branco
> (`twoside`/`openright`) → conteúdo real ≈ 53 pp; ver "REALIDADE DA CONTAGEM DE PÁGINAS" no Estado Atual.
- **Escrito (Fase D):** `thesis/` integrado a partir do template ISEP (classe `meia-style.cls`, `frontmatter/`, `ch1..ch7/`, `appendices/`). `main.tex` adaptado (título T1, autor, nº 1180934, orientador/coorientador, keywords). **Compila localmente: 41 páginas, 0 erros**, biber OK, **8 referências no `references.bib`**. Front matter: abstract (EN) + resumo (PT) em rascunho; acrónimos atualizados (`glossary.tex`).
- **7 capítulos** (esqueleto com secções): Introduction · Contextualization · Literature Review · Methodology · Implementation · Evaluation · Conclusion.
- **`latexmk.rc` criado** (resolve o achado da Fase A: o `Makefile` invocava-o sem existir).
- **`\nocite{*}` REMOVIDO:** confirmado que o texto cita as **16 referências** (conjunto citado = conjunto do `.bib`); bibliografia renderiza 16 entradas, 0 citações indefinidas.
- **TODOS os 7 capítulos em rascunho**; Cap.2 com 1 figura (matplotlib); Cap.3 com 4 tabelas; Cap.4 com diagrama TikZ; **Cap.5 (Implementation)** (engenharia + tabela de módulos); **Cap.6 (Evaluation)** com resultados reais (2 tabelas + 2 figuras + estudo de caso NVDA/AI-chips); **Cap.7 (Conclusion)** responde a RQ1–RQ3 com os resultados reais + contribuições + limitações + trabalho futuro. **Abstract (EN ~185 palavras, <=200) + resumo (PT)** refinados com resultados.
- **Pipeline de figuras reprodutíveis estabelecido:** matplotlib; scripts em `scripts/figures/` geram PDF vetorial para `thesis/figures/` (commitado para o CI).
- **PDF versionado:** `thesis/main.pdf` é gerado por `scripts/build_pdf.sh` e **commitado** (o aluno quer vê-lo no repo); CI continua a compilar também.
- **Front matter:** declaração de integridade limpa (só EN) + **declaração honesta de uso de IA**; símbolos próprios (z-score). Falta confirmar redação ISEP exata da declaração de IA (humano).
- **Em falta:** revisão humana do aluno a todos os capítulos (o texto é dele); confirmar redação ISEP da declaração de IA + data de entrega; (opcional) FNSPID multi-ano; acrónimos/agradecimentos opcionais.
- **Compila localmente: 53 páginas, 0 erros**, 16 refs na bibliografia, 0 citações indefinidas, figuras presentes; só aviso cosmético de fonte. LaTeX local: MiKTeX + biber 2.21; CI (`compile-thesis.yml`) compila em cada push a `thesis/**`.

## Estado do Código
- **Implementado (thin slice / Gatilho 1):** `investigator/config.py` (.env), `investigator/market_data/prices.py` (yfinance + log-returns), `investigator/anomaly_detector/detector.py` (z-score sem lookahead, `AnomalyResult`), `investigator/explanation_engine/explainer.py` (explicação por regra), `investigator/telegram_bot/sender.py` (Telegram API), `investigator/main.py` (`run_thin_slice`). Dep ativa: `yfinance==1.4.1`.
- **Núcleo (motor de correlação):**
  - `investigator/correlation_engine/event_study.py` — impacto pós-evento (+1/+3/+5d) e impacto médio (puro; nota anti-lookahead: medir o outcome ≠ prever).
  - `investigator/correlation_engine/similarity.py` — similaridade do cosseno + `top_k_similar` (puro NumPy, vetorizado).
  - `investigator/historical_kb/` — `record.py` (`NewsRecord`, JSON), `embedder.py` (interface `Embedder` + `HashingEmbedder` baseline determinístico + `SbertEmbedder` lazy), `knowledge_base.py` (`HistoricalKB.build/save/load/find_precedents`; alinhamento evento = 1.º dia de negociação ≥ data da notícia; persistência JSONL).
- **Gatilho 2 (notícias):**
  - `investigator/news_fetcher/fetcher.py` — `NewsItem`; parsing puro (`parse_finnhub_news`, `parse_rss`, `_rss_date_to_iso`) + HTTP tardio (`fetch_finnhub_company_news`, `fetch_rss_feed`). Finnhub validado ao vivo (247 notícias AAPL).
  - `investigator/explanation_engine/explainer.py::explain_news_impact` — alerta XAI com precedentes + impacto médio + nota anti-previsão.
  - `investigator/main.py::run_news_trigger` — orquestra notícia → embedding → `KB.find_precedents` → explicação → (opcional) Telegram. Default: KB-amostra + `HashingEmbedder`.
- **Avaliação (Pergunta A):**
  > ⚠️ **NÚMEROS DESTA SECÇÃO ESTÃO SUPERADOS — riscados a 2026-07-29.** São de uma corrida
  > ANTIGA, anterior ao protocolo final. Os valores **congelados e citados na tese** são
  > P@5 **0,514** (MiniLM) · **0,538** (MPNet) · **0,346** (lexical) · **0,240** (aleatório) ·
  > **0,126** (recência), e à escala **0,595** no FNSPID; anomalia amplitude **0,015 vs 0,344**,
  > F1 **0,516**. **Fonte de verdade: `docs/evaluation/*.md`** (regenerados por script), não
  > este ficheiro. Mantidos aqui só como registo histórico da evolução.
  - `investigator/evaluation/retrieval_eval.py` — `retrieval_precision_at_k`, `expected_random_precision`, `recency_precision_at_k`, `same_ticker_forbid` (puro NumPy, testado: precision@k por setor cross-ticker + baselines).
  - `scripts/fetch_finnhub_news.py` (notícias reais → CSV) + `scripts/evaluate.py` (multi-seed + ablação de modelo via `--sbert-models` → `docs/evaluation/evaluation_results.md` + figura). ~~P@5 (média 5 seeds): SBERT-MiniLM 0,549±0,014, SBERT-MPNet 0,569±0,009, lexical 0,359, aleatório 0,241, recência 0,105.~~ (superado — ver aviso acima)
  - `investigator/evaluation/anomaly_eval.py` (Pergunta 1: `rolling_zscore_flags`, `fixed_threshold_flags`, `label_extreme_moves`, `precision_recall_f1`, `firing_rate`; puro, testado) + `scripts/evaluate_anomaly.py` (yfinance → `docs/evaluation/evaluation_anomaly.md` + figura). Taxa de disparo: z-score amplitude 0,017 vs fixo 0,343.
- **Scripts de dados:** `scripts/download_data.py` (FNSPID em **streaming** + filtro por ticker/janela → `data/` gitignored + amostra de títulos); `scripts/build_kb.py` (notícias CSV + preços yfinance → KB JSONL; `--sbert` para SBERT real). `data/samples/news_sample.csv` (sintético) + `data/samples/kb_sample.jsonl` (gerado) + `data/samples/README.md`.
- ~~**Testes (22 + 2 gated, verde)**~~ — **contagem superada (2026-07-29: 376).** Nunca fixar
  contagens de teste neste ficheiro: correr `pytest` é a única fonte fiável. Os módulos
  originais eram `test_anomaly_detector` (4) + `test_event_study` (4) + `test_similarity` (7)
  + `test_knowledge_base` (5) + `test_smoke` + `test_sbert_embedder` (gated).
- **Smoke/gated:** Telegram (`pytest -m telegram`, envio real confirmado) e SBERT (`pytest -m sbert`, validação semântica) — ambos excluídos do verify por defeito (`-m "not telegram and not sbert"`).
- **Stack ML instalada e fixada:** torch 2.12.1+cpu (índice CPU), sentence-transformers 5.6.0, transformers 5.12.1, huggingface-hub 1.20.1, scikit-learn 1.9.0; `requirements.txt` atualizado + `requirements.lock.txt` (72 pkgs). numpy/pandas inalterados (2.1.3/2.2.3).
- **Pipeline KB validado:** `build_kb.py` (HashingEmbedder) → `kb_sample.jsonl` com impactos coerentes (ex.: TSLA −9,75%, MSFT +7,2%); `SbertEmbedder` validado por teste semântico. **Fonte FNSPID verificada** (HTTP 200, ~23,2 GB).
- **Testes (41 + 2 gated, verde):** anomaly(4) + event_study(4) + similarity(7) + knowledge_base(5) + news_fetcher(3) + explainer(4, inclui fidelidade XAI) + retrieval_eval(5) + anomaly_eval(6) + smoke(3) + gated telegram/sbert.
- **Em falta:** escrever Caps. 5–6 com o que está construído/avaliado; (opcional) download completo do FNSPID + KB SBERT multi-ano (job longo, R2); demo Gatilho 2 ao vivo (Finnhub→KB SBERT→Telegram); `impact_analyzer` (opcional, FinBERT).

## Referências Verificadas
- **16 referências verificadas** em `docs/decisions/citation_log.md` e no `thesis/references.bib`:
  - **8 metodológicas** (DOI/arXiv): Chandola 2009, Brown & Warner 1985, Reimers & Gurevych 2019, Araci 2019, Lundberg & Lee 2017, Arrieta 2020, Adadi & Berrada 2018, Dong 2024.
  - **3 de contextualização** (fonte primária, 2026-06-21): SIFMA 2025 Fact Book, Gallup 2025, CCAF 2026.
  - **5 da revisão de literatura** (Crossref/arXiv, 2026-06-21): Liu 2008 (Isolation Forest), Ribeiro 2016 (LIME), Devlin 2019 (BERT), Mikolov 2013 (word2vec), Yang 2020 (FinBERT).
- **Rejeitada:** MacKinlay 1997 (sem DOI resolúvel) → substituída por Brown & Warner 1985.
- Protocolo §6.4 em vigor: nenhuma entrada no `.bib` sem identificador verificado e registado.

---

## Questões em Aberto / À Espera do Aluno (humano-only)
1. ~~Instalar Python 3.12~~ ✅ FEITO (3.12.10; venv canónico criado).
2. ~~Auth GitHub~~ ✅ FEITO (push a funcionar).
3. ~~Bot Telegram~~ ✅ FEITO (.env preenchido; envio real confirmado).
4. ~~Chaves de APIs~~ ✅ FEITO (.env: Finnhub/AlphaVantage/GNews preenchidas).
5. **Política ISEP de uso de IA** — escrita uma declaração **honesta** no front matter; **falta o aluno confirmar a redação/forma exata exigida pela MEIA** com o Prof. Luís Gomes (não fabricar/encobrir — ver memória `honest-ai-declaration`).
6. **Confirmar conjunto de tickers e janela temporal** do FNSPID (próximo, S12 / `data_card.md`).
7. ~~Escolher o título~~ ✅ RESOLVIDO (T1 — D-008). Arquitetura confirmada.

---

## Regras Permanentes (cópia compacta)
**Limites rígidos (§2.2):** nunca expor segredos (só em `.env` gitignored; scan antes de cada commit); nunca fabricar (dados, resultados, **citações** — toda a citação verificada §6.4); nunca operações git destrutivas/irreversíveis sem aviso (sem `--force`, sem reescrita de história publicada, sem `reset --hard` que perca trabalho); nada destrutivo fora do repo; nunca gastar dinheiro (só free tier); nunca automatizar logins em portais de editoras; **pausar em cada gate de fase**.

**Aluno & aprendizagem (§3):** explicar cada conceito em PT-PT antes de usar; o aluno tem de conseguir defender tudo; simplicidade defensável > sofisticação; nada que o aluno não entenda entra na tese.

**Académico (§6):** contextualização com dados 2025–2026; literatura seminal + recente, peer-reviewed primeiro; tabelas comparativas; cada afirmação com fonte, cada decisão técnica com justificação; **cada citação verificada (citation_log.md) — zero fabricação**; uso de IA declarado; datasets/modelos atribuídos.

**DoD (§8) — gate para avançar de fase:** deliverables existem e commitados; `verify.sh` passa (testes + LaTeX compila); cada conceito novo explicado em `learning.md` com nota de defesa; cada citação nova verificada e registada; nenhum segredo em ficheiros versionados; `CLAUDE.md` atualizado com estado e próxima ação.

**Git & continuidade (§12):** branch único `main`, história linear (rebase); começar sessão com pull-rebase; terminar com verify→commit→pull-rebase→push (sem force-push, sem auto-resolver conflitos que possam perder trabalho); dados grandes/modelos nunca versionados; commits descritivos em PT-PT.

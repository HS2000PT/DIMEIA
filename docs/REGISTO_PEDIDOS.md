# Registo de pedidos — tudo o que foi pedido, por ordem

**2026-09-03 — raciocínio retomado e fechado:** quatro cópias confirmadas como idênticas aos
anexos (115/56/69/57 linhas) e 44 itens na matriz. Ordem consolidada no respetivo relatório:
verificação precede retreino e reescrita; figuras todas em inglês; tradução integral só no fim.

**2026-09-03 — quatro anexos, prioridade máxima:** lidos integralmente, originais preservados,
44 pontos mapeados em `docs/planos/REVISAO_PRIORITARIA_ANEXOS.md`. Todas as figuras refeitas em
inglês, tese PT por agora. Auditoria prioritária antes de consolidar alterações; não adiar
artigo automaticamente. README/AGENTS/CLAUDE sincronizados por ligação ao mesmo registo.

**2026-09-03 — decisões posteriores prevalecem:** retreino autorizado e prioritário; piloto
Figma explicitamente rejeitado, não pendente. Documento académico não herda verde da marca.
Anexo mais recente lido até ao fim; ordem por dependências incorporada no plano final, secção 0.
Inspeção técnica e próximo passo em `docs/planos/RETREINO_CONTROLADO.md`. Sem treino ou deploy.

**2026-09-03 — reenvio do pedido integral:** reconciliado em
`docs/planos/POS_PLANO_AUDITORIA.md`, incluindo portabilidade/segredos, vídeo, artigo,
concisão e nomenclatura. Ordem preservada; auditoria integral ainda não executada. Identificada
generalização a verificar em ch1:45. Tese e código intactos; piloto revisto ainda sem aprovação.

**2026-09-03 — piloto corrigido:** tipografia recuperada para 8,03 pt à largura final;
caixas mais altas, conectores ajustados e prova revista em cor/cinzentos. Tese intacta;
aguarda decisão do autor sobre substituição.

**2026-09-03 — comparação Figma entregue:** exportação recuperada e prova a largura igual
em `output/pdf/comparacao-ciclo-modelo.pdf`. Cor/cinzentos verificados; rótulos menores no piloto
(6,57 contra cerca de 8 pt). Não se recomenda substituir nesta versão. Tese intacta.

**2026-09-03 — piloto conceptual:** criado e inspecionado após autenticação restabelecida:
https://www.figma.com/design/sNfbRq1WUSM8gRK95FjtWy. Tese intacta. Falta obter exportação local
acessível e comparar à largura final/em cinzentos antes da decisão do autor.

**2026-09-03 — quinta passagem:** gráfico setorial harmonizado e destino do gerador corrigido
para tese-v2. Dois testes passaram, página 81 inspecionada e porta canónica aprovada. Sem deploy.

**2026-09-03 — quarta passagem:** cores 5.5/5.10 e legenda 5.12 corrigidas; três páginas
renderizadas, PDF 126/94 e porta canónica aprovada. Restante harmonização ainda pendente.

**2026-09-03 — orçamento/ponta a ponta:** barras repetidas retiradas da Figura 5.11 e
preservadas na 5.18; papéis das figuras e legendas clarificados. Duas páginas renderizadas,
PDF 126/94 e porta canónica aprovada. Sem publicação; restante harmonização visual pendente.

**2026-09-03 — funil concluído nesta passagem:** contabilidade completa de 5 060 avaliações,
333 passagens visíveis e cinco entregas separadas. Página renderizada e aprovada; PDF 126/94,
porta canónica passou. Restante frente 05 ainda aberta.

**2026-09-03, avanço:** primeira vaga visual validada (seis gráficos e dois diagramas).
Três defeitos de renderização corrigidos; PDF 126/94, porta automática e 176 testes dirigidos
passaram. Frente 05 ainda aberta para harmonização, funil, redundâncias e piloto externo.

Atualização: reconstrução limpa concluída; porta automática canónica passou, com nomes do júri
pendentes. PDF mantém 126 páginas físicas e 94 contadas. Inspeção visual das alterações pendente.

Retoma de 2026-09-03: frente 05 em validação. Seis gráficos alterados nas fontes e duas colisões
do ch4 corrigidas; reconstrução limpa do PDF e inspeção visual ainda necessárias. Sem publicação
destas alterações. Não confundir avanço nas fontes com entrega validada.

Este ficheiro existe por um motivo simples: durante a sessão foram dadas
instruções a meio de respostas, entre outros assuntos, e nenhuma se pode
perder. Aqui está tudo, pela ordem em que foi dito, com o estado atual.

Regra de leitura: a secção A manda sobre todas as outras. A secção D é a
fila de trabalho e é executada por ordem, de cima para baixo.

Última atualização: 2026-09-03.

---

## A. Regras permanentes de trabalho

| # | Regra | Origem |
|---|-------|--------|
| A1 | «Avançar sempre. Não pares. Primeiro terminamos o que temos pendente. Sempre assim.» | dito diretamente |
| A2 | «A sequência dos prompts deve ser respeitada. Seguimos pela ordem dos pedidos.» | dito diretamente |
| A3 | Um pedido novo entra no fim da fila; não interrompe o que está em curso. Excepção: se o pedido novo invalidar trabalho que está a ser feito nesse momento. | consequência de A2 |
| A4 | Nada de inventar: nem resultados, nem referências, nem experiências. «Nunca inventes um valor para preencher uma lacuna.» | dito diretamente |
| A5 | Nunca assumir que o código faz o que o texto diz. Verificar no código. | dito diretamente |
| A6 | Resultados negativos não se escondem. Se um número contraria a tese, o número fica. | dito diretamente |
| A7 | Risco assumido: «posso partir e reparar». Alterações diretas ao caminho de envio em produção estão autorizadas. | escolhido por ele |

---

## B. Restrição fundamental do domínio — não existe previsão de preços

Dito por ele, sem margem: o sistema **não prevê preços**. Em concreto, e em
qualquer artefacto (tese, painel, Telegram, slides, defesa), está proibido:

- preços-alvo;
- sinais de compra ou venda;
- recomendações de investimento;
- estratégias de negociação;
- promessas de rentabilidade;
- substituir a decisão do investidor.

O que é permitido: contexto histórico retrospetivo — «o que aconteceu depois
de eventos parecidos» — apresentado como facto passado, nunca como previsão.

Consequência já aplicada: o «desfecho observado» no Telegram só anota
horizontes efetivamente medidos, e a anotação nunca antecipa nada.

---

## C. Restrições de escrita

| # | Regra |
|---|-------|
| C1 | Capítulo 1 só pode citar fontes **muito recentes**. |
| C2 | **Nunca citar o arXiv.** |
| C3 | Três tiques que ele detesta e que não podem aparecer: comentários sobre o próprio texto; levantar questões em vez de responder; começar frases com afirmações vazias. |
| C4 | Evitar ao máximo desculpas e justificações defensivas. |
| C5 | O modelo MEIA v2 (2026) manda na estrutura; a redação é decisão nossa desde que respeite o modelo. |
| C6 | Português europeu no texto; nomenclatura técnica e mensagens de commit em inglês. |

---

## D. Fila de trabalho

Ordem de execução. Uma frente só se fecha quando está verificada, não quando
está escrita.

### Frente 01 — Feedback no Telegram ✅ concluída tecnicamente
Pedido: «no telegram, considera e desenvolve a possibilidade de adicionar lá
a opção de dar feedback positivo ou negativo».
Feito: botões em todos os alertas, webhook, registo append-only, regras de
leitura pré-registadas e fragmento LaTeX gerado para o Capítulo 5. Em
produção desde a v51. Ele confirmou que vai convidar pessoas para o canal.

⚠️ **A 2026-09-02 apanhou-se um defeito que teria estragado a recolha.** Os
votos eram publicados na branch de dados com uma função que *substitui* o
ficheiro. O disco do Heroku é efémero: a cada reinício o ficheiro local
volta a zero, e o primeiro voto novo substituía o ficheiro remoto — que
tinha tudo — por essa única linha. O painel também lia um disco local que não
era partilhado com o processo que recebia os votos. Ambos os defeitos foram
corrigidos: a publicação junta linhas, o processo recupera a semente remota
depois de um reinício e o painel junta a branch com a cache local.

Os seis votos perdidos foram recuperados **exatamente** do commit que os
preservava e repostos na branch de dados pelo commit `504371db0`; não foram
recriados nem inferidos. A análise de 2026-09-03 lê 20 votos efetivos de duas
pessoas sobre 16 alertas: 19 úteis e um não útil. Uma pessoa representa 80%
da amostra; sem ela ficam quatro votos, abaixo do mínimo pré-registado de 20.
O valor bruto pode ser descrito, mas não constitui validação independente.

Falta uma ação do dono antes dos convites: substituir e fixar no canal a
mensagem de consentimento de `docs/design/telegram_channel.md`. Os comandos
`/deletefeedback` e `/apagar` retiram os votos da análise; as linhas antigas,
pseudonimizadas, permanecem no historial Git, e essa limitação é dita ao
participante. Para analisar: `python scripts/analyse_feedback.py --da-branch`.

### Frente 02 — Alerta instantâneo e edição posterior ✅ concluída, com recusa medida
Pedido: «a opcao de o alerta ser instantaneo, e só depois do nosso sistema
'pensar' é que vamos e editamos a mensagem».
Metade feita: **desfecho observado** — a mensagem é editada mais tarde com o
que aconteceu de facto. Em produção desde a v53.
Metade recusada, com medição em vez de opinião: o esboço imediato não traz
ganho porque a mediana publicação→deteção é 353 min e a mediana
deteção→entrega é 5 s. O atraso não está onde o esboço o resolveria.

### Frente 03 — Painel ✅ concluída
Pedido inicial: «rever o painel, remove a parte de baixo da página, que tem
montes de texto».
Pedido alargado (dado depois): «refazer do zero portanto. está uma cagada o
nosso.» Com a lista dele:
- corrigir o *tab title*, ficar apenas InvestiGator — ✅
- ver se o URL pode ficar `investigator.herokuapp.com` — ❌ **não pode**: o
  sufixo de 12 caracteres é obrigatório desde 2023-06-14; só um domínio
  próprio dá um URL limpo (ver E3)
- usar melhor o espaço do ecrã — ✅
- melhores animações, mas prioridade à performance — ✅
- «*Why it stayed quiet* está muito confusa e continuo sem perceber» — ✅ é
  agora um modal por empresa, com o funil em ordem
- «*all companies* não faz sentido estar onde está» — ✅ movida
- fonte mais estilizada e maior — ✅ IBM Plex
- menos palavras, mais interatividade — ✅
- logótipos maiores — ✅
- página em *cards* — ✅
- gráfico principal com filtros por data — ✅ 1M/3M/6M/1Y
- clique nos eventos abre modal com detalhe — ✅
- todas as sinalizações e cores com legenda — ✅
- semáforo / KPIs no topo — ✅ cinco cartões
- o *mirror* do Telegram algures — ✅ coluna direita
- o feedback das pessoas aparece — ✅ KPI de votos
- *refresh* constante — ✅ sondagem de 30 s
- mascote: o jacaré é a mascote, o logótipo mantém-se; o jacaré relata o
  «today» e a página abre no «today», com opção de ver histórico — ✅
- «sê também tu crítico e propõe melhorias» — feito no *brief*
Fechado na v8 e publicado. O gráfico abre em 1D com dados intradiários,
separa preço, eventos e z-score, o historial deixou de ser subtrativo, e a
mascote resume o estado do S&P 500 sem sugerir previsão. As figuras do
Capítulo 4 foram regeneradas a partir da página real sobre um instantâneo
congelado da API.

### Frente 04 — Marca ✅ concluída
Pedido: «rever o logotipo no painel. não faz sentido investigator estar
dentro de um retangulo com border. e o Gator deveria ter a cor, não só o G».
Feito: retângulo removido; divisão `Investi` em tinta e `Gator` em verde;
geometria da Tail unificada; cinco peças em claro, escuro e monocromático;
IBM Plex convertido em contornos; PNG de 512 px e avatar regenerados. O lema
canónico é «Markets move. We investigate.». O gerador e 48 testes impedem
que os ficheiros, o painel e a documentação voltem a divergir.

### Frente 05 — Artefactos visuais ⏳ pendente
Pedido: «sinto que as nossas tabelas, figuras, formulas, whatever, são muito
repetitivas e confusas. vamos explorar e pesquisar pelos melhores softwares
e extensões externos».
Âmbito: 37 figuras. Gramática visual única, seis gráficos com o tipo errado
no capítulo 5, legendas que dizem a leitura, e 4–6 diagramas conceptuais.
Esta é a próxima frente da fila, depois de recompilar e validar a `tese-v2`.

### Frente 06 — Desculpas e declaração de IA 🔄 parcial
Pedido: «devemos realmente evitar ao máximo 'desculpas' ou justificações na
tese... vê novamente o template oficial».
Feito: declaração de utilização de IA, colocada onde o modelo manda (secção
de ética, §3.8.4).
Falta: 18 frases defensivas identificadas.

### Frente 07 — Humanizar e verificar ⏳ pendente
Pedido: «detetar por padrões de 'IA' e humanizar... cuidado com os metadados
também... verificar os doi...; simular clique nos URLs».
Âmbito: tiques de IA («X, e não Y» 58×; «uma vez que» 43×;
«precisamente/exatamente» 28×), 11 entradas sem DOI, 57 sem URL, e abrir
todos os DOI e URL para confirmar que resolvem. Metadados do PDF.

### Frente 08 — Slides e guia de estudo ⏳ pendente
Pedido: «falta os slides finais, e o guia de estudo».
Inclui os *prompts* para NotebookLM, Gamma, Canva e Figma.

### Frente 09 — Organização da pasta e do repositório 🔄 metade feita
Pedido (dado a 2026-09-01): «devemos perder algum tempo a organizar a folder
e o repositorio... tudo o que não esteja de momento a ser usado ativamente,
ou que não irá constar dos ficheiros finais essenciais deve ser movido para
uma pasta archive. também não quero ter ficheiros soltos na pasta principal...
code (e as subpastas) e archive (e tudo nao final) são certos, e depois acho
que Dissertation, que dentro terá Thesis, Slides, Guide.»
Motivo dado: o repositório é público.
Plano detalhado em `docs/design/reorganizacao.md`.

✅ **Metade A, feita a 2026-09-02** — a que não tem risco: `tmp/` fora do
índice (406 ficheiros, 66 MB), `archive/` com critério escrito, e os 17
ficheiros `.md` soltos da raiz reduzidos a 3, com as 30 referências
reescritas e verificadas.

⏳ **Metade B, adiada com motivo** — o `code/` e reduzir as cinco árvores de
tese a uma. Ao executar a metade A descobriu-se que `app/` é importado por
onze ficheiros e que `thesis/` recebe as figuras de nove scripts de
avaliação. Mover qualquer um obriga a repontar scripts, e as frentes 05 e 07
ainda vão escrever nesses caminhos. Faz-se quando o conteúdo parar de se
mexer.

### Frente 8½ — A cadeia de «porquês» ⏳ pendente, corre em último
Pedido: «no final, mas apenas só mesmo no final de tudo, devemos fazer as
perguntas tipicas de uma criança curiosa: 'porquê?' em loop para cada
afirmação/frase na tese. não deve haver porquês sem resposta. são
precisamente esses os alvos de questões na defesa.»
Saída: `docs/defesa/PORQUES.md`.

---

## E. Pendências operacionais

| # | O quê | Estado |
|---|-------|--------|
| E1 | **Rodar a chave da API do Heroku.** Foi colada no chat, portanto está queimada. Heroku → Account settings → API Key → Regenerate. | ⚠️ **por fazer, é dele** |
| E2 | Re-execução coordenada dos 31 avaliadores, uma única vez, no fim. | ⏳ |
| E3 | Decidir se compra um domínio próprio. Sem domínio, o URL fica com o sufixo do Heroku — não há volta. | ⏳ decisão dele |
| E4 | **Decidir o orçamento diário de alertas.** Está em 5. O varrimento (`docs/evaluation/evaluation_budget_sweep.md`) mostra que de 5 para 15 a precisão cai 1,7% e a cobertura triplica. Subir ajuda a recolha de feedback; obriga a acertar o número no texto da tese. Não escolher o k pela tabela — isso seria selecionar sobre o conjunto de teste. | ⏳ decisão dele |
| E5 | **Levar os commits para o `main` do GitHub.** O workflow `alerts.yml` corre `run_alerts.py` a partir do ramo por omissão, em cron. Enquanto o `main` não tiver estas correcções, existe um segundo produtor a correr código antigo — incluindo o do orçamento. | ⚠️ **é dele** |

---

## F. Pós-plano — só depois de toda a fila acima

### F1 — A tese ideal (`docs/planos/POS_PLANO_TESE_IDEAL.md`)
A visão dele: introdução com números de valor de negócio de 2026; revisão de
literatura a cobrir produtos de mercado e todas as famílias de técnicas de
IA com prós e contras e tabela comparativa; metodologia a testar todas as
combinações de componentes; resultados; conclusões; anexo com figuras em
paisagem; declarar o uso de IA.
Três correções registadas, com o motivo: valor ≠ velocidade (os 353 min
contradizem-no); testar todas as combinações é *menos* rigoroso, não mais
(comparações múltiplas enviesam o vencedor); «não descartar nada» precisa de
critérios de exclusão fixados **antes** do levantamento.

### F2 — Auditoria (`docs/planos/POS_PLANO_AUDITORIA.md`)
O *brief* completo dele: 8 perguntas, 13 secções de saída, cada melhoria com
descrição, justificação, evidência, ficheiro, alteração, benefício, esforço,
prioridade, dependências e risco de âmbito; classificação
crítica/alta/média/baixa/trabalho futuro.
Instrução explícita dele: «não alteres automaticamente a tese nem o código
nesta primeira fase» — é um relatório, não uma intervenção.

---

## G. Contexto fixo

| Campo | Valor |
|-------|-------|
| Autor | Henrique José da Silva Santos, 1180934 |
| Curso | Mestrado em Engenharia de Inteligência Artificial, ISEP |
| Orientador | Luís Gomes |
| Coorientador | Rafael Silva |
| Sistema | InvestiGator |
| Defesa | entre 16 e 30 dias a contar de 2026-09-01 |
| Limite de páginas | 120, **sem contar anexos** (o modelo diz «not counting the Annexes») |

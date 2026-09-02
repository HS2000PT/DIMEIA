# Registo de pedidos — tudo o que foi pedido, por ordem

Este ficheiro existe por um motivo simples: durante a sessão foram dadas
instruções a meio de respostas, entre outros assuntos, e nenhuma se pode
perder. Aqui está tudo, pela ordem em que foi dito, com o estado atual.

Regra de leitura: a secção A manda sobre todas as outras. A secção D é a
fila de trabalho e é executada por ordem, de cima para baixo.

Última atualização: 2026-09-01.

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

### Frente 01 — Feedback no Telegram ✅ concluída (com um defeito grave corrigido a 2026-09-02)
Pedido: «no telegram, considera e desenvolve a possibilidade de adicionar lá
a opção de dar feedback positivo ou negativo».
Feito: botões em todos os alertas, webhook, registo append-only, regras de
leitura pré-registadas, fragmento LaTeX gerado para o capítulo 5. Em
produção desde a v51. Ele confirmou que vai convidar pessoas para o canal.

⚠️ **A 2026-09-02 apanhou-se um defeito que teria estragado a recolha.** Os
votos eram publicados na branch de dados com uma função que *substitui* o
ficheiro. O disco do Heroku é efémero: a cada reinício o ficheiro local
volta a zero, e o primeiro voto novo substituía o ficheiro remoto — que
tinha tudo — por essa única linha. Os seis votos recolhidos antes do deploy
das 19:10 desapareceram assim. Corrigido: passa a juntar. Segundo defeito, da
mesma família: o painel lia o disco do dyno *web* e quem escreve os votos é o
*worker*, portanto mostrava sempre zero.
Consequência prática para ele: **os votos que forem dados a partir de agora
ficam**. Para analisar, `python scripts/analyse_feedback.py --da-branch`.

### Frente 02 — Alerta instantâneo e edição posterior ✅ concluída, com recusa medida
Pedido: «a opcao de o alerta ser instantaneo, e só depois do nosso sistema
'pensar' é que vamos e editamos a mensagem».
Metade feita: **desfecho observado** — a mensagem é editada mais tarde com o
que aconteceu de facto. Em produção desde a v53.
Metade recusada, com medição em vez de opinião: o esboço imediato não traz
ganho porque a mediana publicação→deteção é 353 min e a mediana
deteção→entrega é 5 s. O atraso não está onde o esboço o resolveria.

### Frente 03 — Painel 🔄 em curso
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
Falta: fechar a v7, passar `tests/test_api.py`, publicar, e regerar as
figuras do capítulo 4 a partir da v7.

### Frente 04 — Marca 🔄 parcial
Pedido: «rever o logotipo no painel. não faz sentido investigator estar
dentro de um retangulo com border. e o Gator deveria ter a cor, não só o G».
Feito: retângulo removido.
Falta: decidir a cor (`investiGATOR` vs `InvestiGator`, desenhados lado a
lado para ele escolher), o conjunto de cinco SVG com texto vetorizado, e o
slogan.

### Frente 05 — Artefactos visuais ⏳ pendente
Pedido: «sinto que as nossas tabelas, figuras, formulas, whatever, são muito
repetitivas e confusas. vamos explorar e pesquisar pelos melhores softwares
e extensões externos».
Âmbito: 37 figuras. Gramática visual única, seis gráficos com o tipo errado
no capítulo 5, legendas que dizem a leitura, e 4–6 diagramas conceptuais.

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

### Frente 09 — Organização da pasta e do repositório ⏳ pendente
Pedido (dado a 2026-09-01): «devemos perder algum tempo a organizar a folder
e o repositorio... tudo o que não esteja de momento a ser usado ativamente,
ou que não irá constar dos ficheiros finais essenciais deve ser movido para
uma pasta archive. também não quero ter ficheiros soltos na pasta principal...
code (e as subpastas) e archive (e tudo nao final) são certos, e depois acho
que Dissertation, que dentro terá Thesis, Slides, Guide.»
Motivo dado: o repositório é público.
Plano detalhado em `docs/design/reorganizacao.md`.
Quando: **a seguir à frente 03**, antes da 04. O motivo está escrito no plano.

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

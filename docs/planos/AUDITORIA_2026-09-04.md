# Auditoria crítica — dissertação e Investigator

Data: 2026-09-04. Pedida pelo autor. **Nenhuma linha da tese ou do código foi alterada nesta
passagem**, por instrução expressa: analisar, auditar e planear.

> **A restrição de âmbito foi respeitada em toda a auditoria.** Nada do que se propõe abaixo
> envolve previsão de preços, direção futura, sinais ou recomendação. O que o sistema faz, e o
> que estas propostas mantêm, é deteção, contextualização, recuperação de evidência retrospetiva
> e validação posterior.

---

## A. Resumo executivo

**O documento está em melhor estado do que o pedido de auditoria assume, e o sistema também.**
A porta de entrega tem **um** item por fechar, e é a designação do júri pelo ISEP, que só
acontece depois da submissão. A dissertação canónica compila a 126 páginas, 94 das 120
permitidas antes dos apêndices, com zero erros, 52 de 52 números conferidos contra o ficheiro
que os produz, e 267 referências cruzadas sem uma única incompatibilidade de tipo.

O sistema está em produção há 54 dias com **zero dias úteis sem um alerta**.

O achado mais valioso desta auditoria é **positivo e está por reportar**: a alteração de desenho
mais importante do trabalho — o modelo deixar de vetar e passar a ordenar, com orçamento diário —
**funcionou**, e a dissertação descreve a alteração sem nunca medir o seu efeito.

Três avisos honestos sobre o âmbito do pedido:

1. **Boa parte desta auditoria já existia.** A matriz de 44 itens de 03/09 e a auditoria
   pré-defesa cobrem a maioria das perguntas. Esta passagem verifica-as e concentra-se no que é
   novo, em vez de duplicar.
2. **O calendário não comporta o roadmap de sete fases.** Faltam 23 dias para a submissão. As
   fases «melhorar Investigator» e «gerar novas evidências» são de semanas. O plano abaixo está
   dividido em **cabe** e **não cabe**, e a segunda lista não é para agora.
3. **Uma preocupação do pedido está desatualizada.** «Apenas duas empresas com alertas» já não
   descreve o sistema: são doze, e a concentração desceu de 64% para 44%.

---

## B. Pontos fortes, com a evidência

| O que | Evidência |
|---|---|
| Resultado negativo reportado e defendido | QI3 negativa, com **três** verificações independentes (`ch5` §Três verificações) e o veredicto no mesmo destaque das afirmativas (`fig:con_scorecard`) |
| Cada escolha contra a alternativa medida | Tabela de síntese com **três** linhas a declarar que o implantado não ganhou, e a razão de o manter (`ch5` §Síntese) |
| Números rastreáveis | 52/52 conferidos automaticamente contra `docs/evaluation/`; `auditar_numeros.py` exige origem para todo o número afirmado |
| Operação contínua | 558 alertas, 2026-07-13 a 09-04, **0 dias úteis sem alerta** |
| Afirmações estreitadas onde a evidência não chega | «supera a taxa-base **nos cinco setores**» em vez do agregado; a linha trivial de 0,467 declarada |
| Concorrentes nomeados com disciplina | Cortex e Google Finance citados da página do fornecedor, com «os produtos não foram testados» escrito (`ch2`) |
| Coerência tese-sistema no ponto mais arriscado | A tese diz que **não** integra modelo de linguagem; a API não expõe a camada generativa. As duas coisas batem certo |
| Instrumentação para o que não sabe | `as_of` no registo de decisões; foi o que tornou detetável o lookahead de 04/09 |

---

## C. Problemas críticos

**Nenhum problema encontrado nesta passagem compromete o rigor científico do documento.** Os que
existem são de completude e de atualidade, não de correção. Isto é uma afirmação forte e é o
resultado de: 52/52 números verificados, todas as promessas de contagem conferidas uma a uma, a
aritmética das margens refeita, e 267 referências cruzadas verificadas por tipo.

O item de maior risco para a defesa **não é um defeito do documento**: é o retreino. O protocolo
está pré-registado e o cálculo de potência diz que a janela **não sustenta** «o candidato bate o
modelo atual». Se esse resultado for apresentado como se sustentasse, é aí que a defesa cai.
Está escrito antes de existir candidato, e é para se manter escrito.

---

## D. Problemas de âmbito

| Item | Evidência | Leitura |
|---|---|---|
| Camada generativa completa, não exposta e não reivindicada | `investigator/intelligence/` (guarda, relatório, analista) com testes e corpus de *red team*; nenhuma rota da API a alcança | **Não é contradição** — a tese diz que não integra LLM e é verdade. É trabalho substancial que o documento não reclama. Decisão do autor: manter o âmbito estreito (defensável) ou reclamá-lo num apêndice |
| Três aplicações Streamlit retiradas, ainda versionadas | `app/dashboard*.py`, `app/streamlit_app.py`; arrastam `streamlit` e `plotly` para o `requirements.txt` | Dívida declarada, custo é tamanho de *slug*, não memória. Fica para depois da entrega |
| Quatro árvores de tese versionadas | `tese/` (32 ficheiros), `tese-v2/` (32), `thesis/` (37), `thesis-pt/` (16) | Só uma é entregue. Quem chega tem de descobrir qual |
| Onze documentos de plano | `docs/planos/` | Vários supersedem-se. É o defeito que a sessão 50 documentou como **pior do que não ter plano** |

---

## E. Inconsistências tese ↔ sistema

| Elemento | Tese afirma | Investigator faz | Estado | Ação |
|---|---|---|---|---|
| Efeito do orçamento diário | Descreve a alteração (`ch5:1256`) | Concentração 64% → **44%**, 11 → **12** empresas | **Em falta na tese** | Reportar o efeito medido |
| Retreino | «exige tempo de observação que **não estava disponível**» (`ch4:858`) | Desde 04/09 recolhe classe A, com protocolo pré-registado | **Desatualizado em parte** | Datar a frase, como já se fez em `ch5` |
| Camada generativa | «não integra modelo de linguagem» | Código existe, rotas retiradas | **Coerente** | Nada |
| Registo de decisões | «regista todas as decisões de triagem» | Regista as candidatas relevantes; a relevância corta a montante | **Coerente** — o capítulo declara a população filtrada 80 linhas depois | Nada |
| Modelo de linguagem no filtro | `ch4:140` «rejeita padrões de texto gerado» | Regra textual, não modelo | **Coerente** | Nada |

---

## F. Auditoria por capítulo

| Cap. | Palavras | Visuais | Pal./visual | Leitura |
|---|---:|---:|---:|---|
| 1 Introdução | 1 213 | 2 | 606 | Equilibrado. A afirmação absoluta sobre aplicações gratuitas foi estreitada a 04/09 |
| 2 Estado da arte | 5 533 | 5 | **1 106** | **Densidade a vigiar.** Quatro subsecções de 40+ linhas sem visual |
| 3 Métodos | 4 477 | 8 | 559 | Bom. Cada técnica abre por «para que serve» |
| 4 Implementação | 6 219 | 13 | 478 | O mais bem servido visualmente |
| 5 Casos de estudo | 11 526 | 20 | 576 | Estrutura repetida (procedimento, resultado, limites) e secções auto-críticas explícitas |
| 6 Conclusões | 5 415 | 2 | **2 707** | **O mais denso do documento, e é o último que o júri lê** |

**Detalhe por capítulo, só onde há algo a dizer:**

- **Cap. 2.** Cumpre o alvo do *brief* (2–3 figuras), mas é o segundo mais denso. As
  subsecções sem visual são «O investidor particular e o problema da atenção» (54 linhas),
  «Deteção de anomalias em séries financeiras» (49), «Aprendizagem automática em produção» (43)
  e «Estudos de evento» (42).
- **Cap. 6.** Duas visuais para 5 415 palavras. A secção **Trabalho futuro** tem 88 linhas e
  nenhum visual — é a maior do documento nessa condição.
- **Cap. 5.** Nenhuma objeção. É o capítulo mais forte e o mais auto-crítico.

**Verificado e limpo, para não se repetir o trabalho:** todas as promessas de contagem («três
verificações», «três medições», «duas comparações», «cinco componentes», «três limitações»,
«quatro objetivos», «quatro limitações» do fragmento gerado); a aritmética das margens
(0,708 − 0,688 = 0,020; 0,262 − 0,254 = 0,008); 267 referências cruzadas, 0 incompatibilidades;
0 flutuantes não invocados; escrita PT-PT sem achados.

---

## G. Auditoria do Investigator

| Dimensão | Estado | Evidência |
|---|---|---|
| Arquitetura | Cinco componentes, mais a decomposição só no percurso de preço | `investigator/`, 68 ficheiros, 9 525 linhas |
| Caminho vivo | `web` = FastAPI, `worker` = ciclo de 60 s | `Procfile` |
| Dados acumulados | 558 alertas, 41 450 decisões, 10 933 casos maturados, 1 341 pendentes | ramo `alerts-history` |
| Continuidade | **0 dias úteis sem alerta em 54 dias** | histórico |
| Aprendizagem | **Acumulação, não aprendizagem.** Os pesos não mudam desde 2018–2023 | `ch4:858`, e a tese di-lo |
| Deriva | Medida (PSI), **não corrigida** | `ch5` §Deriva |
| Feedback | Vivo, pelo webhook do Telegram | `api/main.py:215`, `feedback_log.py` |
| Memória | `Standard-2X` (1 GB) desde 04/09; **R14 = 0** | medido após reinício |
| Testes | 973, ruff limpo | suite |
| Reprodutibilidade | 46 documentos de avaliação regeneráveis por script | `docs/evaluation/` |

**A distinção que o pedido exige, respondida sem ambiguidade:** o Investigator **não tem
aprendizagem online**. Tem uma base de casos que cresce e um registo de decisões que cresce. Os
parâmetros do modelo são de 2018–2023 e nunca foram reajustados. A tese afirma exatamente isto,
e não o disfarça de *continuous learning*.

**Modularidade.** Os componentes têm entradas e saídas definidas e são testáveis isoladamente —
as 973 provas correm sem rede. O que **falta** para o critério do pedido é versão e métricas por
componente: não existe um manifesto por execução com hashes, esquema e semente. Está identificado
no `RETREINO_CONTROLADO.md` como o passo 2 por implementar.

---

## H. Auditoria das experiências

O que foi realmente testado, e é verificável: deteção contra limiar fixo e contra dois detetores
aprendidos; recuperação contra seis alternativas, à escala e sob a restrição causal; triagem
contra volatilidade, com ablação das entradas, nove definições de rótulo e reamostragem por
grupo; decomposição, no que dela é mensurável.

**O que a auditoria encontra em falta não são experiências novas — é uma medição sobre dados que
já existem:** o efeito da alteração de política. A tese diz que o modelo deixou de vetar e passou
a ordenar; não diz o que isso produziu. Os dados estão no histórico de alertas e a medição é de
minutos.

**O que NÃO deve ser repetido, e a razão:** nada. As experiências congeladas reproduzem-se ao
milésimo e os protocolos estão escritos. Repetir por repetir a 23 dias do prazo troca tempo por
risco.

---

## I. Auditoria visual

**A preocupação do pedido não se confirma na maior parte.** De 86 secções e subsecções, 44 não
têm figura nem tabela, mas quase todas são curtas. Apenas **uma** com 60+ linhas não tem visual:
`Trabalho futuro`, no Cap. 6.

Onde faz sentido intervir, por ordem de retorno:

1. **Cap. 6, «Trabalho futuro»** (88 linhas, 0 visuais) — um diagrama de dependências entre as
   linhas futuras responde a «o que vem primeiro e porquê», que é texto a explicar mal.
2. **Cap. 6 no conjunto** (2 707 palavras por visual) — o capítulo que o júri lê último é o mais
   denso. Um visual do percurso das três respostas aliviaria.
3. **Cap. 2** (1 106) — as quatro subsecções longas sem visual.

**Variedade.** Depois das três mudanças de forma de 04/09, os tipos são: 19 diagramas, 1 série
temporal, 1 funil, 1 *lollipop*, 12 gráficos de barras, 4 de pontos, 4 de linha, 1 grelha, 3
capturas. **Já não é monótono.** Duas propostas de variedade foram examinadas e **rejeitadas com
razão**: degraus para a ablação (a legenda diz que as linhas não são cumulativas) e pequenos
múltiplos para as figuras com intervalos (partiria a narrativa).

---

## J. Plano de redução

**A recomendação é não reduzir.** O documento está em **94 de 120 páginas** permitidas e em
34 370 palavras contra um alvo de 36 000. Não há pressão de espaço, e cortar texto verificado a
23 dias do prazo é gastar risco sem comprar nada.

Se o autor quiser mesmo reduzir, os únicos candidatos que a medição sustenta são no Cap. 2, que
é o segundo mais denso — e mesmo aí a redução deve ser de **fusão de subsecções**, não de corte
de conteúdo, porque cada uma fecha com um «para o InvestiGator» que liga ao resto.

---

## K. Plano de melhoria

| Melhoria | Evidência | Ação | Tipo | Esforço | Impacto | Prioridade |
|---|---|---|---|---|---|---|
| Reportar o efeito do orçamento | 64% → 44%, 11 → 12 empresas | Um parágrafo no Cap. 5 e uma figura | documental | baixo | **alto** | **crítica** |
| Datar a frase do retreino | `ch4:858` diz que o tempo «não estava disponível» | Datar, como se fez em `ch5` | documental | muito baixo | médio | **alta** |
| Visual em «Trabalho futuro» | 88 linhas, 0 visuais | Diagrama de dependências | documental | baixo | médio | alta |
| Aliviar o Cap. 6 | 2 707 palavras/visual | Um visual do percurso das respostas | documental | baixo | médio | média |
| Manifesto por execução do retreino | Passo 2 do plano, por implementar | Saída com hashes, esquema, semente | software | médio | alto **para o retreino** | alta, se houver retreino |
| Arrumar a raiz | 4 árvores de tese, 11 planos | `archive/` para o que está superseda | reproducibility | baixo | médio | média |
| Glossário | 12 definições nunca usadas | Remover ou usar | documental | muito baixo | baixo | baixa |
| Reclamar a camada generativa | `intelligence/` medido e não reivindicado | Apêndice, se o autor quiser | documental | médio | médio | **decisão do autor** |
| Contexto com dados de 2026 | Fig. 1.1 vai até 2024 | Verificar se o SIFMA publicou 2026 | investigação | baixo | baixo | baixa |
| Estudo com pessoas | Nunca corrido | Recrutar 6–10 | investigação | **alto (calendário)** | alto | trabalho futuro |

---

## L. Roadmap, dividido pelo prazo

O pedido descreve sete fases. **Quatro delas não cabem antes de 27/09**, e apresentá-las como se
coubessem seria dar um plano que produz ansiedade em vez de trabalho feito. A divisão é esta.

### Cabe antes de 27/09 — por ordem de dependência

1. **Reportar o efeito do orçamento diário.** É a única lacuna de conteúdo que a auditoria
   encontrou, os dados já existem, e converte «alterámos» em «alterámos e o efeito foi este».
2. **Datar a frase do retreino** no `ch4`, pela mesma razão que se datou a do `ch5`.
3. **Dois visuais no Cap. 6**, que é o mais denso e o último a ser lido.
4. **~17/09: fechar a janela de recolha.** É a data-limite para os dados maturarem a tempo. A
   partir daí, correr a avaliação sobre a população real de candidatas, **segundo o protocolo
   pré-registado e sem o reabrir**.
5. **Recompilar, correr a porta, e parar.** A partir de ~22/09 o documento congela.

### Não cabe — e é para depois

- **Melhorar o Investigator** (fase 2 do pedido): modularidade com versão e métricas por
  componente, manifesto de execução, universo de empresas maior.
- **Gerar novas evidências** (fase 3): mais experiências, mais ablações, mais ativos.
- **Reestruturar a tese** (fase 4): não há motivo. Está em 94 de 120 páginas, com estrutura
  canónica MEIA e zero erros.
- **Auditoria de interface** (fase 5): o produto está no ar e não é reivindicado como
  contribuição. Mexer nele agora obriga a recapturar figuras já sincronizadas.
- **Estudo com pessoas**: é o único item com relógio de calendário e já não cabe antes de 27/09.
  Fica como a única linha declaradamente em aberto, que é como o Cap. 6 já a apresenta.
- **Artigo**: reutiliza as figuras, que ficaram em inglês a 04/09 exactamente para isso.

### O que fica por fechar e não é do autor

Os **nomes do júri**, que o ISEP designa depois da submissão. É o único item que a porta de
entrega ainda acusa, e está separado numa secção própria desde 04/09 para não empurrar a porta
para um vermelho permanente que se aprende a ignorar.

---

## Método desta auditoria

O que foi medido, e não citado de memória: o histórico de alertas do ramo de dados (558 registos),
o registo de decisões (41 450 linhas), a base de casos (10 933), a estrutura de importações do
caminho vivo, as 86 secções do documento com contagem de palavras e visuais, o glossário contra o
corpo, e a árvore do repositório.

**Duas afirmações minhas foram corrigidas a meio, e ficam escritas:** julguei o `feedback_log`
morto porque a minha análise estática não seguia importações tardias — está vivo, pelo webhook; e
julguei excessiva a frase «regista todas as decisões de triagem» — o capítulo declara a população
filtrada oitenta linhas depois.

**O que esta auditoria não fez:** não correu experiências novas, não leu as três publicações que
os anexos de 03/09 deixaram por ler integralmente, e não avaliou a interface com utilizadores.
As duas primeiras são trabalho de investigação; a terceira precisa de pessoas.

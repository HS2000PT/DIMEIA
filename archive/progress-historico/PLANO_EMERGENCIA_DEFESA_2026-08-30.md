# Plano de emergência — tese defensável e compreensível

**Data:** 2026-08-30  
**Estado:** plano de trabalho; não altera a tese, o código nem os resultados.  
**Destinatários:** autor, orientador e revisão independente no Claude Cowork.

## Decisão central

**Não recomeçar a dissertação do zero.** A árvore **tese/** já é a versão portuguesa curta criada
para o template do ISEP e reutiliza resultados, referências e figuras que têm rastreabilidade no
repositório. Recomeçar agora destruiria essa cadeia, introduziria erros novos e consumiria o tempo
que deve ser usado a confirmar, simplificar e ensaiar.

O objetivo não é afirmar que cada resultado histórico foi novamente reproduzido hoje. Isso não é
possível enquanto faltarem os conjuntos de dados integrais. O objetivo seguro é entregar uma
**edição de defesa**: menor, visual, transparente, limitada ao que o autor consegue explicar, com
cada resultado classificado por evidência e cada limitação declarada.

Uma tese não ganha credibilidade por parecer escrita por outra pessoa ou por esconder ferramentas
usadas. Ganha-a quando o autor consegue explicar, com calma, cada decisão sobrevivente, mostrar de
onde veio cada resultado e dizer sem hesitar o que o sistema não demonstra.

## Factos confirmados antes de mexer

| Item | Estado observado em 2026-08-30 | Consequência |
|---|---|---|
| PDF canónico | tese/main.pdf, 135 páginas físicas, SHA-256 70544C7A4FA4C30C25394B21C76EF72C0F1692108ED4B616AA8AD1913F6FC649 | Não é o mesmo artefacto de 134 páginas auditado anteriormente. A versão final terá de ser inspecionada e validada de novo. |
| Distribuição atual | preliminares 24; Cap. 1: 6; Cap. 2: 14; Cap. 3: 24; Cap. 4: 18; Cap. 5: 28; Cap. 6: 10; bibliografia 4; apêndice 7 | Os capítulos já somam 100 páginas. Se o “máximo 100” for só corpo, a meta já é atingida; se for PDF físico, são necessários cerca de 35 cortes reais. |
| Porta atual | scripts/check_entrega.py termina com 6 falhas: quatro PDFs, incluindo a tese, mais antigos que os respetivos .tex; a contagem de testes afirma 763 mas recolhe 742; e o verificador do apêndice falha. | Não se pode declarar a entrega validada neste estado. |
| Verificadores portáveis | check_apendice_xref.py e check_floats.py têm a raiz fixa C:\Users\henri\Desktop\DIMEIA\tese, inexistente nesta máquina. O segundo pode passar falsamente ao encontrar zero ficheiros. | Reparar estas portas antes de as usar como evidência. |
| Compilação | Não existem logs locais em tese/; a porta atual aceita a ausência de log. | Só uma compilação explícita, com log novo e inspeção visual, pode sustentar “compila limpo”. |
| Dados empíricos | Faltam nesta cópia os inputs integrais usados por QI1/QI2/QI3, incluindo triage_dataset.csv, triage_dataset_ext.csv, finnhub_news.csv, fnspid_news_subset.csv, kb_fnspid_sbert.jsonl, predictions_log.jsonl e gate_log.jsonl. Há amostras e artefactos de avaliação. | Não correr os motores empíricos diretamente: podem obter dados atuais, alterar artefactos congelados ou produzir números não comparáveis. |
| Estrutura e exemplos | Há exemplos aprovados com 104, 109, 133 e 139 páginas físicas. A estrutura mais útil é: problema → técnicas usadas → dados/método → arquitetura → casos/avaliação → conclusão por pergunta. | Não cortar apenas para obedecer a uma estimativa informal de páginas. Cortar complexidade e evidência fraca primeiro. |

O plano curricular oficial do MEIA está disponível na página do curso do ISEP:
<https://www.isep.ipp.pt/Course/Course/462>. Ele pede, na dissertação, definição do problema,
estratégia, experimentação com métodos/tecnologias de IA, investigação, autonomia e conclusões.
Não obriga a cobrir todas as unidades curriculares. A suficiência formal continua a depender do
regulamento e do orientador; não se devem inventar nomes de UCs nem alegações de conformidade.

## História curta que a versão de defesa deve contar

> Foi construído um sistema que transforma notícias e preços em alertas explicáveis. Foram
> avaliadas três técnicas simples: deteção de anomalias com z-score, recuperação semântica com
> embeddings e triagem supervisionada. As duas primeiras respondem a objetivos estreitos; a terceira
> não demonstrou valor suficiente para controlar alertas e, por isso, não é usada como veto.

Isto contém engenharia de IA defensável: dados, integração de três técnicas de IA/ML, protocolo
temporal, comparadores, métricas, decisão de produto baseada em evidência, explicabilidade e
limites. É preferível a uma narrativa que enumera muitas técnicas sofisticadas sem domínio real.

## Regra de evidência para todas as alegações

Criar uma linha no **registo de alegações** para cada resultado, número, comparação e afirmação
técnica que permaneça no corpo da tese:

    ID | pergunta/objetivo | afirmação em linguagem simples | artefacto e ficheiro |
    dados/licença/snapshot | código e comando | protocolo, comparador e métrica |
    output bruto → figura/tabela | estado de evidência | explicação oral de 90 s |
    manter / reformular / remover

Usar apenas estes estados:

| Estado | Significado | Como pode aparecer na tese |
|---|---|---|
| **A — confirmado agora** | input congelado identificado, execução local isolada, output guardado, verificação passada e autor sabe explicar | Pode usar número exato e dizer que foi confirmado na edição final. |
| **B — histórico rastreável** | script, artefacto de avaliação e contexto existem, mas os dados originais não estão disponíveis para nova execução nesta máquina | Pode aparecer como resultado experimental datado, com origem e limitação explícitas; nunca como “reproduzido hoje”. |
| **C — insuficiente** | não há input, output ou explicação oral suficiente; o resultado depende de dados mutáveis; ou o autor não o domina | Retirar o número, estreitar a frase ou remover a secção. |

“Tudo a 100% válido” significa aqui que **nenhuma frase finge um nível de prova que não tem**. Não
significa fingir que todo resultado histórico foi repetido hoje. A primeira prioridade é tentar
recuperar os snapshots originais; sem eles, o texto deve assumir honestamente o estado B ou sair.

Para evitar uma figura decorativa por cada frase, aplicar esta regra:

- cada **resultado principal** recebe uma figura ou tabela de proveniência:
  dados → transformação → método → métrica → valor;
- cada **número secundário** aparece numa tabela de rastreabilidade que aponta para o artefacto;
- nenhum gráfico novo usa valores inventados, mistura dados atuais com dados históricos, ou é
  gerado sem fonte explícita.

## Núcleo a manter, estreitar e cortar

### Manter no corpo, desde que passe o registo de alegações

| Núcleo | Formulação defensável | Limite obrigatório |
|---|---|---|
| QI1 — anomalia | O z-score usa o retorno recente para assinalar um movimento incomum e foi comparado com uma regra fixa. | Tratar o caso de desvio-padrão zero; não prometer previsão de preços. |
| QI2 — recuperação semântica | Embeddings e cosseno recuperam notícias passadas de outras empresas do mesmo setor. A síntese usa apenas o protocolo causal: P@5 = 0,513, contra chão 0,259, se o artefacto continuar estado A ou B. | Isto mede um proxy de setor, não relevância factual nem direção futura do mercado. |
| QI3 — triagem supervisionada | O modelo foi testado como experiência de classificação por empresa-dia e não demonstrou ganho suficiente sobre volatilidade para comandar alertas. | Não chamar ao rótulo “relevância de cada notícia”; não apresentar a probabilidade live como fiável. |
| Arquitetura e explicação | Um fluxo ponta-a-ponta e uma explicação rastreável de alerta mostram integração de engenharia. | A decomposição mercado/setor/empresa é indicativa; não é uma verdade causal validada. |
| Conclusão | Uma tabela responde diretamente a cada pergunta: método, comparador, resultado, decisão e limite. | Incluir explicitamente a experiência negativa e a ausência de estudo humano. |

### Retirar do núcleo ou mover para material suplementar

| Local atual | Ação proposta | Motivo |
|---|---|---|
| Cap. 2 §§2.1–2.4, 2.8–2.9 e 2.11 | Fundir contexto de produtos, LLM, estudo de evento, CBR e MLOps numa tabela curta de trabalhos relacionados. Manter anomalias, recuperação semântica, XAI e a lacuna. | Não são necessários para defender as três técnicas implementadas. |
| Cap. 3 §§3.4–3.9 | Reduzir a um diagrama de dados, z-score, embeddings/cosseno e uma caixa curta da triagem. Remover explicações pedagógicas longas, caso detalhado de decomposição, calibração e segurança/ética extensa. | É o maior foco de complexidade não essencial. |
| Cap. 4 §§4.2–4.3, 4.8–4.9 | Cortar inventário de fornecedores, escolha de três fontes, infraestrutura, memória, latência e ciclo de vida. Manter arquitetura, caminho de uma notícia, portas corrigidas e um alerta. | Detalhe operacional difícil de defender e pouco central à pergunta científica. |
| Cap. 5 §5.2 | Substituir sete mini-aulas de métricas por uma figura/tabela única: “o que mede, comparador e como interpretar”. | Liberta páginas e reduz ansiedade sem retirar avaliação. |
| Cap. 5 §§5.6.3–5.6.11, 5.7–5.8 | Converter a QI3 para 2–3 páginas: protocolo temporal, resultado comparativo, decisão de não a usar como veto e limite. | Ablações, deriva, produção e alternativas não sustentam a história principal. |
| Cap. 6 §§6.3–6.6 | Uma tabela de limitações/futuro e um parágrafo de aprendizagem do autor. | A reflexão extensa não acrescenta evidência. |
| Apêndice A | Reduzir para duas páginas: resultado → script → artefacto, ambiente e encaminhamento para o guia técnico. | O apêndice não deve substituir a explicação do corpo. |

A estimativa desses cortes é de 36–48 páginas físicas, suficiente para aproximar a versão de
100 páginas se esse for realmente o limite. É uma estimativa; a única contagem válida é a do PDF
compilado depois de cada lote de cortes. Não reduzir margens, espaçamento ou tamanho de letra para
fingir uma redução.

## Correções factuais obrigatórias antes de congelar

1. **Tabela 4.5:** com orçamento diário, o primeiro alerta não tem piso de probabilidade; o segundo
   usa 0,64. Não manter o valor 0,49 como requisito do primeiro alerta.
2. **Síntese da QI2:** usar o resultado causal/passageiro correto, P@5 = 0,513 e chão = 0,259; não
   usar 0,595, que permite candidatos futuros.
3. **Figura 5.6:** substituir ou renomear. Se disser “por setor”, deve mostrar resultados por setor,
   não agregados P@5/P@10.
4. **Beta = 1:** retirar a alegação de que o ruído do rótulo não pode alterar a ordenação das
   famílias de modelos. O protocolo comum dá comparabilidade interna, não invariância.
5. **Desvio-padrão zero:** corrigir o código/teste ou declarar a exceção: um salto depois de
   retornos constantes pode gerar z = 0 no caminho atual. Não generalizar uma garantia que o código
   não cumpre em todos os caminhos.
6. **QI3 e tempo:** chamar-lhe classificação por empresa-dia; reconhecer que ret_event em treino
   e produção não tem exatamente a mesma semântica temporal.
7. **Uso live:** não apresentar “57%” ou valor semelhante como probabilidade validada em produção,
   nem dizer que o modelo veta alertas.
8. **Pessoas e causalidade:** não afirmar benefício para utilizadores, fidelidade humana ou
   decomposição causal. Não houve estudo humano nem verdade de terreno para isso.

Uma correção de código que altere uma regra de avaliação exige teste e reavaliação do resultado
afetado. Não assumir que uma correção local tornou automaticamente válidos todos os gráficos
históricos.

## Visuais prioritários

| Visual | Pergunta que responde | Fonte permitida | Resultado |
|---|---|---|---|
| Fluxo do sistema | “Como uma notícia se torna alerta?” | código e configuração atuais; sem números inventados | Dados → filtros → técnica → explicação → alerta. |
| Cartão QI1 | “O que mede o z-score e como foi avaliado?” | série/artefacto congelado e relatório de anomalia | Exemplo temporal anotado + comparação com regra fixa. |
| Cartão QI2 | “O que o embedding recupera, exatamente?” | artefacto de recuperação causal | Consulta → filtro temporal → vetor/cosseno → candidatos do setor → P@5 vs chão; gráfico por setor se a fonte o suporta. |
| Cartão QI3 | “Porque não usar o modelo aprendido como veto?” | artefacto de triagem, em estado A ou B | Dados por empresa-dia → divisão temporal → baseline de volatilidade vs modelo → decisão negativa. |
| Caso ponta-a-ponta | “O que recebe o utilizador?” | alerta/figura já rastreável | Uma notícia, o movimento, precedente e limites, todos anotados. |
| Tabela de fecho | “O que foi demonstrado?” | registo de alegações | Pergunta → método → comparador → conclusão → limitação → estado de evidência. |

Usar os exemplos de teses apenas como referência de estrutura visual (sobretudo o de Joana
Figueiredo), nunca como fonte de redação ou de afirmações técnicas.

## Sequência realista para um dia

### Fase 0 — congelar e decidir (30–45 min)

1. Registar git status, hash, páginas e data do PDF atual; preservar uma cópia identificada, sem a
   substituir.
2. Verificar se existe, em disco externo, OneDrive, repositório privado ou computador de origem,
   um snapshot dos dados integrais. Registar caminho, hash, licença e data; não copiar dados sem
   saber a origem.
3. Perguntar ao orientador/regulamento, em uma frase, se o limite de “~100” se refere a páginas
   físicas ou ao corpo paginado. Não assumir uma regra inexistente.
4. Decidir: manter a decomposição só como explicação visual ou removê-la totalmente do corpo.
   Recomendação: tirá-la da avaliação e mantê-la no máximo como explicação indicativa se o autor a
   consegue explicar.

**Parar e não reexecutar motores** se os datasets originais não surgirem rapidamente.

### Fase 1 — reparar a porta de verdade (1–2 h)

1. Tornar check_apendice_xref.py e check_floats.py portáveis e falhar explicitamente quando não
   encontram corpus.
2. Corrigir a divergência “763 versus 742 testes” ou atualizar a alegação apenas depois de a
   contagem ser explicada.
3. Fazer a compilação canónica de tese/main.tex e guardar log novo.
4. Executar, no ambiente do projeto, as portas estáticas:

~~~powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& .\.venv\Scripts\python.exe scripts\check_entrega.py
& .\.venv\Scripts\python.exe scripts\check_references.py tese
& .\.venv\Scripts\python.exe -m pytest -m "not telegram and not sbert" -p no:cacheprovider
& .\.venv\Scripts\python.exe -m ruff check .
git diff --check
pdfinfo tese\main.pdf
pdffonts tese\main.pdf
~~~

5. Guardar as saídas datadas num registo. Estas portas verificam consistência e composição; não
   substituem a reprodução científica.

### Fase 2 — registo de alegações e currículo (1–2 h)

1. Preencher o registo de alegações para todas as conclusões e números que vão ficar no corpo.
2. Criar uma matriz curta de adequação ao MEIA, baseada no texto oficial do ISEP, sem inventar UCs:

       objetivo de aprendizagem oficial | evidência concreta na tese | figura/tabela | estado A/B/C

3. Exigir pelo menos dois fios de IA em estado A ou B forte, cada um com problema, dados, método
   integrado, comparador, resultado e limitação. O terceiro fio pode ser o resultado negativo da
   QI3.
4. Transformar todo item C em “remover” ou “não demonstrado”, antes de cortar por estilo.

### Fase 3 — redução controlada e visuais (3–4 h)

1. Cortar primeiro Cap. 5, depois Cap. 3, Cap. 4, Cap. 2, Cap. 6 e apêndice, conforme a tabela
   anterior.
2. Depois de cada capítulo, compilar e medir páginas. Não fazer uma alteração massiva impossível
   de rever.
3. Para cada resultado sobrevivente, criar ou corrigir um cartão visual de proveniência usando
   apenas fontes congeladas.
4. Reescrever cada secção com a estrutura:
   **pergunta → dados → método → comparador → resultado → limite → decisão**.
5. Deixar no texto apenas conceitos que o autor consiga explicar sem ler: z-score, embedding,
   cosseno, divisão temporal, baseline, precisão@k/PR-AUC e limitação do rótulo.

### Fase 4 — fecho técnico e oral (1–2 h)

1. Aplicar as oito correções factuais obrigatórias.
2. Compilar o PDF final, executar portas reparadas, procurar referências indefinidas e inspecionar
   visualmente as páginas alteradas, os gráficos, as tabelas e o apêndice.
3. Conferir que slides, guia e tese dizem a mesma coisa; se não houver tempo para sincronizar um
   material, remover dele qualquer número divergente.
4. Criar uma folha pessoal de defesa de uma página:

       pergunta | resposta em 30 segundos | figura | limite que digo primeiro

5. Fazer duas passagens orais: uma de 5 minutos (história completa) e outra de 90 segundos por
   técnica.

## Regras de paragem

- Sem input original com hash: não retreinar, não fazer download atual, não regenerar métricas.
- Sem validação de uma alegação: não compensar com linguagem confiante; estreitar ou cortar.
- Sem certeza de uma figura: não a usar como “prova”.
- Se a redução ameaçar apagar protocolo, comparador ou limitação, preservar essas três peças e
  cortar contexto/repetição.
- Se a compilação final ou a porta reparada não estiver verde, entregar ao orientador apenas com
  uma nota explícita do que falta validar; nunca dizer que tudo foi confirmado.

## Pedido de revisão ao Claude Cowork

O Claude deve começar em modo leitura e tratar este documento como plano, não como prova. Pode usar
a seguinte instrução:

> Audita a tese canónica em C:\Users\ruifa\Desktop\DIMEIA\tese\main.tex e este plano. Não
> reescrevas a tese do zero e não alteres código, números ou visuais antes de criar uma matriz
> “alegação → fonte → método → resultado → limite → decisão”. Confirma o PDF atual, o hash, o
> estado das portas e a ausência dos datasets integrais. Propõe cortes por secção que preservem
> problema, método, comparador, resultado e limitação. Considera qualquer número sem input
> congelado como histórico rastreável, não reproduzido hoje. Não inventes UCs, participantes,
> referências, métricas nem resultados. Cada recomendação deve indicar ficheiro, secção, impacto
> estimado em páginas e o que o aluno terá de conseguir explicar oralmente.

## Decisão recomendada agora

Avançar com a **edição de defesa curta a partir de tese/**, não com uma tese nova. Prioridade:

1. congelar e reparar a validação;
2. distinguir resultados reproduzidos, históricos e removidos;
3. reduzir para três técnicas e cinco/seis visuais de evidência;
4. corrigir as contradições objetivas;
5. ensaiar uma narrativa honesta que o autor domina.

Isto não garante uma classificação ou aprovação — ninguém o pode garantir —, mas reduz
materialmente o risco académico e oral em comparação com uma reescrita total ou uma corrida
apressada para gerar números novos.

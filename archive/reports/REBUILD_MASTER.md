# REBUILD_MASTER — contrato de reconstrução do InvestiGator

> **A pergunta central deste documento.**
> Não é *"como corrigimos 140 páginas?"*. É:
> **"Se hoje tivéssemos de construir a melhor versão possível deste trabalho, sabendo o que
> aprendemos até agora mas sem herdar as suas conclusões, como o construiríamos?"**

Este ficheiro é um contrato. Um agente autónomo deve poder segui-lo sem fazer perguntas, e um
humano deve poder auditar, em qualquer momento, se ele foi seguido. Onde diz **DEVE**, é
obrigatório; onde diz **NÃO PODE**, é proibido; onde diz **PODE**, é uma escolha a registar.

---

# FASE 0 — O que NÃO se faz, e quando começa isto

**O rebuild NÃO PODE começar antes da defesa da versão atual.**

A razão é física e não é de esforço. A avaliação em produção assenta em decisões cujo desfecho
só é observável **oito dias** depois de tomadas; as 825 que a dissertação atual reporta
acumularam-se ao longo de cinco semanas de sistema no ar. Num repositório que por regra não
herda resultados, esse número não se regenera com computação: regenera-se com espera. O mesmo
vale para a base de 38 214 casos e para a medição de deriva.

A consequência é contraintuitiva e tem de ficar escrita: **um rebuild executado com pressa
produz um trabalho com menos evidência do que o atual**, porque teria de deitar fora a avaliação
em produção, a deriva medida, a base de casos viva e a matriz de evidência. Essas quatro coisas
são o que hoje separa esta dissertação de um projeto de cadeira.

**Portanto:**

| Momento | O que se faz |
|---|---|
| Até à defesa | Nada deste documento, à excepção da regra do sistema vivo (§3). Preparar a defesa. |
| Semana 0, após a defesa | §1 a §4: congelar, criar o repositório, migrar. |
| Semanas 1–2 | §5: reformular a investigação. **Sem correr experiências.** |
| Semanas 2–4 | §6 e §7: auditar a arquitetura e executar a especificação experimental. |
| Semanas 4–8 | §8 a §12: escrever, ilustrar, consolidar. |
| Semanas 8+ | §13 a §15: defesa e slides. |

Se o calendário real não comportar isto, **a decisão certa não é comprimir as fases: é reduzir
o âmbito do rebuild** e dizê-lo explicitamente neste ficheiro, no topo, com data.

---

# 1. Congelar o legacy

1.1. O repositório atual **DEVE** ser etiquetado (`git tag legacy-final`) e ficar em modo de
leitura. **NÃO PODE** ser apagado. Isolamento, não amnésia.

1.2. Nada é "salvo" dele por reflexo. A pergunta para cada ficheiro não é *"isto ainda serve?"*
mas *"o novo trabalho consegue nascer sem isto?"*. Se conseguir, fica no legacy.

1.3. **NÃO PODE** ser feita uma cópia do repositório antigo seguida de limpeza. Isso transporta
a confusão com outro nome. O novo repositório nasce vazio e recebe ficheiros um a um, cada um
com uma justificação.

---

# 2. O novo repositório

2.1. Nome: `investigator-thesis-final`. Git limpo, história nova, sem *merge* do legacy.

2.2. **DEVE** nascer com: `.gitignore`, `.env.example`, gestão de segredos por variável de
ambiente, `README.md`, ambiente reproduzível com versões fixadas (não intervalos), `pyproject.toml`
e integração contínua desde o primeiro *commit*.

2.3. Estrutura:

```
thesis/        documento novo: capa, estrutura, capítulos VAZIOS
src/           implementação do sistema
experiments/   uma pasta por experiência, cada uma reprodutível
data/          nada versionado excepto amostras e artefactos indispensáveis
tests/
infra/         deployment, agendamento, observabilidade
assets/        figuras finais, cada uma com origem declarada
references/    bibliografia verificada
defense/       slides, diagramas
defense/study/ material de aprendizagem do autor (NÃO entra na tese)
docs/          decisões, post-mortems, ADRs
```

2.4. Cada figura em `assets/` **DEVE** ter, ao lado, o procedimento que a gera ou a fonte de onde
veio. Uma figura sem origem **NÃO PODE** entrar na tese.

---

# 3. A fronteira de migração

## 3.1. ATRAVESSA (whitelist)

- Código-fonte necessário para implementar o sistema.
- Configuração **sem segredos**.
- Infraestrutura: `Procfile`, definições de *deployment*, agendamento.
- O template oficial da tese e a folha de estilo.
- **A bibliografia**, incluindo os comentários de verificação no Crossref. Reverificar 60
  referências já verificadas é desperdício puro.
- *Scripts* que **obtêm** dados externos. Não os dados derivados.

## 3.2. NÃO ATRAVESSA (blacklist)

Métricas, CSV de resultados, tabelas finais, gráficos, *checkpoints*, análises, conclusões,
interpretações, texto científico anterior, saídas de modelos, e **qualquer ficheiro cujo
propósito seja dizer "o resultado foi X"**.

## 3.3. A terceira categoria — post-mortems (obrigatória)

A blacklist, aplicada à letra, deitaria fora a coisa mais valiosa que o legacy tem: **o registo
de porque é que cada escolha foi feita e onde é que ela falhou**. Isso é conhecimento de
engenharia, não é evidência científica.

**DEVE** ser migrado para `docs/legacy-postmortems/`, com cada ficheiro marcado `LEGACY` no
cabeçalho, um registo dos defeitos conhecidos. No mínimo:

- o disco efémero que congelou a base de casos dezanove dias sem registar um único erro;
- o chão de comparação que ordenava alfabeticamente e quase quadruplicou um ganho publicado;
- a fronteira intradiária da variável do retorno do dia;
- os 655 MB de vetores gastos em contabilidade de objetos Python;
- a divergência entre a política avaliada (orçamento) e a política implantada (limiar);
- a composição desigual dos blocos de treino e teste.

**Regra:** um post-mortem **PODE** informar o desenho do novo sistema e **NÃO PODE** ser citado
na tese como evidência de resultado.

## 3.4. O sistema vivo — a excepção, e a regra que a torna legítima

**Decisão tomada: o sistema em produção continua no ar durante o rebuild.** Parar significaria
recomeçar o relógio dos oito dias e ficar sem avaliação em produção durante mais de um mês.

Isto fura a fronteira, e por isso a excepção **DEVE** ser estreita e escrita:

- O que continua a correr é o **código legacy**, congelado. **NÃO PODE** ser alterado para
  melhorar resultados.
- O que atravessa a fronteira do registo vivo são **apenas** três colunas por decisão:
  identificador, instante, e o desfecho de preço medido a posteriori. **NÃO PODE** atravessar a
  pontuação que o modelo legacy atribuiu, nem qualquer decisão que ele tomou.
- Justificação: o desfecho é medido a partir de preços públicos e é verificável por terceiros;
  a pontuação legacy é uma saída de modelo, e essa é evidência herdada.
- Se o novo sistema alterar o critério de captura, o registo anterior a essa alteração **DEVE**
  ser reportado em separado, e nunca somado ao posterior.

---

# 4. Política anti-viés

O risco real não é confirmares o que já sabias. É **desenhares o novo protocolo, sem dares por
isso, de forma a que a resposta que já conheces caiba**. Tu já sabes que a volatilidade ganhou ao
modelo com texto, e não podes deixar de saber.

4.1. Cada experiência **DEVE** ter um **pré-registo** em `experiments/<nome>/PREREG.md`, escrito
e submetido ao repositório **antes** de a experiência correr, contendo: pergunta, hipótese,
dados, linha de base, métrica principal, critério de decisão numérico, e o que contaria como
resultado negativo.

4.2. O pré-registo **NÃO PODE** ser editado depois de a experiência correr. Uma alteração faz-se
por ficheiro novo, que declara o que mudou e porquê.

4.3. Nenhum resultado legacy **PODE** aparecer num pré-registo, nem como referência, nem como
valor esperado. Um resultado legacy **PODE**, no máximo, levantar uma pergunta.

4.4. A linha de base **DEVE** ser escolhida e escrita antes da métrica ser calculada, e **DEVE**
ter o seu chão declarado. A lição mais cara do legacy foi esta: uma precisão sem o seu chão dá a
conclusão errada, e aconteceu três vezes no mesmo capítulo.

---

# 5. Reformular a investigação antes de correr o que quer que seja

**Antes de qualquer experiência**, produzir em `thesis/00-desenho.md`, em poucas páginas:
problema, objetivo, perguntas de investigação, hipóteses quando aplicável, contribuição
pretendida, desenho experimental, dados necessários, linhas de base, métricas e critérios de
decisão.

**Porta:** esta fase termina quando um leitor externo consegue dizer, lendo só esse ficheiro, o
que o trabalho vai tentar demonstrar e como saberá que falhou. Enquanto não conseguir, não se
corre nada.

**Duas perguntas que o legacy deixou por responder e que este desenho DEVE tratar de frente:**

1. O rótulo de materialidade descontava o mercado supondo sensibilidade unitária, contradizendo
   a técnica de decomposição do próprio sistema. O novo desenho **DEVE** decidir a definição de
   alvo explicitamente e **DEVE** incluir uma análise de sensibilidade a essa escolha.
2. A divisão cronológica fazia os blocos terem composições de empresas quase disjuntas. O novo
   desenho **DEVE** declarar se isso é aceitável e, se não for, como o resolve.

---

# 6. Auditoria de arquitetura — não assumir que o sistema atual é a solução

O software legacy **NÃO PODE** ser tratado como desenho de referência. Cada decisão é
reaberta e comparada, e a comparação fica em `docs/adr/`.

Em aberto, no mínimo: fluxo de alerta; processamento assíncrono; recuperação de contexto;
latência e onde ela vive; *cache*; armazenamento e persistência entre processos; observabilidade;
deduplicação, que hoje é por igualdade de texto e podia ser por significado; maturação dos casos;
tratamento de erros; *deployment*; memória; custo.

**Explicitamente na mesa, e a comparar em vez de descartar:** emitir primeiro um alerta mínimo e
**editar a mesma mensagem** quando o contexto adicional chegar. É uma alternativa arquitetural,
não um detalhe, e resolve de frente a queixa medida de que os alertas chegam tarde — porque
separa *avisar* de *explicar*, que hoje estão presos ao mesmo instante.

---

# 7. Regras experimentais e critérios de aceitação

7.1. Cada resultado final **DEVE** ser ligável a uma execução identificável: versão do código,
configuração, semente, conjunto de dados, data, métricas e artefactos produzidos. Um resultado
sem execução identificável é uma afirmação, não um resultado.

7.2. Um resultado **só entra** na tese se satisfizer **todos** os critérios:

- foi produzido pela pipeline nova, e não pela legacy;
- tem pré-registo anterior à execução;
- reproduz-se num ambiente construído de raiz, e essa reprodução foi feita e registada;
- tem chão de comparação declarado;
- tem incerteza declarada, ou uma justificação escrita para não a ter;
- a métrica responde à pergunta que a secção faz — e não a uma pergunta vizinha.

7.3. O critério 7.2 último ponto tem nome no legacy e é a lição mais transferível de todas: o
modelo foi escolhido por uma métrica que perguntava *"ordena bem o conjunto todo?"* quando o
produto precisava de *"distingue duas notícias da mesma empresa?"*. **Nenhuma métrica entra sem
que a secção diga, em texto, a que pergunta ela responde.**

7.4. Um componente aprendido **DEVE** ser avaliado na distribuição em que vai ser usado, e não
apenas na de treino. Se for implantado atrás de filtros, é atrás desses filtros que é avaliado.

---

# 8. Escrever de novo, e não reescrever

8.1. **NÃO PODE** ser copiado nenhum parágrafo do documento antigo. Nem para melhorar.

8.2. A pergunta ao escrever cada secção **NÃO É** *"como melhoro isto?"*. É *"o que é que o
leitor precisa de saber aqui?"*, e a resposta escreve-se do modo mais simples que a evidência
nova permite.

8.3. Função de cada capítulo, e mais nenhuma: Introdução → problema e motivação. Estado da arte →
apenas o necessário para posicionar. Metodologia → o que fizemos e porquê. Avaliação → como
testámos. Resultados → o que aconteceu. Discussão → o que significa. Conclusão → o que podemos
legitimamente afirmar.

---

# 9. Regras de escrita

**Proibido:** perguntas retóricas a abrir secções; "vale a pena referir"; "é importante notar";
"surge então a questão"; "curiosamente"; "convém dizer"; comentários ao próprio processo de
escrita; parágrafos que discutem consigo próprios; adjetivos que não acrescentam informação;
frases que preparam a frase seguinte sem dizer nada.

**Obrigatório:** frases curtas; linguagem concreta; um termo por conceito; voz ativa por defeito;
cada afirmação forte com evidência ao lado ou marcada como hipótese.

**Sobre deteção de IA:** o objetivo **NÃO PODE** ser enganar detetores. Esses detetores são pouco
fiáveis e otimizar contra eles é o objetivo errado. O objetivo é uma tese genuinamente tua:
específica ao trabalho, verificável, sem floreados, e que consigas explicar oralmente linha a
linha. Isso remove os sinais de texto genérico como consequência, e não como truque.

**Teste operacional:** se não consegues dizer um parágrafo em voz alta, por palavras tuas, sem
o ler, ele não está pronto.

---

# 10. Política visual

Não queremos mais figuras. Queremos **substituir texto difícil por representação visual**.

Substituições esperadas: três parágrafos → uma figura; enumeração longa → tabela; fórmula
isolada → fórmula com exemplo visual; arquitetura em texto → diagrama; resultados dispersos →
gráfico comparativo; *pipeline* textual → fluxograma; comparação complexa → matriz.

Cada figura **DEVE** ter: uma pergunta concreta a que responde, origem declarada, e uma legenda
que a torne legível sozinha. Uma figura decorativa **NÃO PODE** entrar.

**Três níveis de leitura, obrigatórios:** 10 segundos, a ideia pela figura; 1 minuto, figura mais
legenda; 5 minutos, o detalhe pelo texto.

---

# 11. Ferramentas — uma para cada problema

| Problema | Ferramenta | Nota |
|---|---|---|
| Diagramas técnicos, arquitetura, fluxos, vetorial | Figma | Consistência entre figuras. |
| Componentes visuais da defesa | Canva | Apoio, não conteúdo. |
| Exploração de narrativa e *layout* de apresentação | Gamma | **NÃO PODE** ser autoridade sobre conteúdo científico. |
| Literatura e validação | Consensus, Elicit, Scite, SciSpace | Para posicionar e verificar. |
| Verificação de referência | Crossref | Obrigatória, campo a campo, antes de escrever. |

Animação e vídeo **PODEM** ajudar-te a compreender processos e **NÃO PODEM** substituir figuras
estáticas essenciais na tese.

---

# 12. Regra de qualidade — o que impede voltar à sopa

Nenhuma secção entra na tese sem resposta clara a três perguntas:

1. **Para que serve?**
2. **Que evidência acrescenta?**
3. **O que perde a tese se eu remover isto?**

Se a terceira resposta for "nada", a secção sai do corpo principal.

**O objetivo NÃO É um número de páginas.** Oitenta excelentes servem; cento e cinco necessárias
servem. O problema do legacy nunca foi "140": foi a densidade de conteúdo que não contribuía
para a narrativa.

---

# 13. Tese e defesa, desenhadas juntas

Cada conceito principal **DEVE** ter uma representação que sirva a tese e os slides. O objetivo é
que, olhando para 10 a 15 figuras, consigas reconstruir mentalmente quase todo o trabalho.

Assim a tese passa a ser o que te ensina o sistema, em vez de seres tu a inventar uma
apresentação simples três dias antes.

---

# 14. `defense/study/` — a camada de aprendizagem

Não entra na tese. Contém, por conceito: explicação intuitiva numa frase; explicação oral de 20
a 30 segundos; explicação matemática rigorosa; analogia tecnicamente correta; a pergunta difícil
e a resposta curta.

E um mapa em três níveis: **tenho de saber** (sem isto não defendo), **devo saber** (pode
aparecer), **posso consultar** (não se decora).

---

# 15. Slides, só no fim

Nascem do trabalho estabilizado, **NÃO PODEM** nascer do PDF. São a versão visual da narrativa
final: problema → proposta → como funciona → como foi avaliada → resultados → limitações →
contribuição. Sem despejar tabelas nem texto da dissertação.

---

# 16. Instrução de sistema para o novo projeto

Colar tal e qual na configuração do novo projeto:

> Nenhum resultado, conclusão, interpretação, valor experimental ou afirmação proveniente da
> versão legacy pode ser assumido como verdadeiro. O projeto legacy pode ser consultado apenas
> para recuperar implementação, contexto técnico ou post-mortems de defeitos conhecidos. Todos os
> resultados científicos finais devem ser produzidos novamente no novo ambiente, com pré-registo
> anterior à execução. Um resultado legacy pode, no máximo, levantar uma pergunta; nunca pode ser
> tratado como evidência. Nenhum parágrafo do texto antigo pode ser copiado. Quando não houver
> evidência nova para uma afirmação, a afirmação não é feita.

---

# 17. Os três estados

Todo o artefacto do novo repositório **DEVE** ter um destes três no cabeçalho:

| Estado | Significa | Pode entrar na entrega? |
|---|---|---|
| `LEGACY` | Material antigo. Cientificamente não fiável. | Não. |
| `CANDIDATE` | Trabalho novo, ainda em validação. | Não. |
| `FINAL` | Passou a auditoria de §7.2. | Sim. |

A promoção `CANDIDATE` → `FINAL` **DEVE** ser um *commit* próprio, que nomeia os critérios de
§7.2 satisfeitos. **NÃO PODE** acontecer no mesmo *commit* que produziu o resultado.

---

# 18. Portas entre fases

Nenhuma fase começa sem a anterior passar a sua porta.

| Fase | Porta |
|---|---|
| Migração | Todo o ficheiro migrado tem justificação escrita. Nenhum resultado atravessou. |
| Desenho | Um leitor externo diz o que o trabalho vai demonstrar e como saberá que falhou. |
| Arquitetura | Cada decisão reaberta tem um ADR com a alternativa que perdeu. |
| Experiências | Todo o resultado satisfaz os seis critérios de §7.2. |
| Escrita | Toda a secção responde às três perguntas de §12. |
| Figuras | Toda a figura tem origem, pergunta e legenda autónoma. |
| Entrega | Compilação limpa; toda a referência verificada; nenhum artefacto `CANDIDATE` citado. |

---

## Nota final, e é a que mais interessa

Este documento existe para tornar o trabalho **melhor**, e não para tornar o processo mais
severo. Se em algum momento uma regra daqui estiver a produzir pior ciência — a impedir que uma
evidência real seja usada, ou a obrigar a repetir trabalho que já era sólido — a regra está
errada e altera-se **aqui**, com data e justificação, antes de ser violada na prática.

Um contrato que só se cumpre a fingir é pior do que não ter contrato nenhum.

# Auditoria de orientação — 3 dias

> Fonte da tese: `tese/main.pdf` (134 páginas). Esta nota é uma auditoria de decisão: descreve o
> que está demonstrado no repositório em 2026-08-28 e separa correções executáveis de alterações que
> exigem credenciais, participantes ou uma escolha do aluno. Não migra, apaga ou publica nada.

## 1. Base factual para a defesa

O pedido inicial contém três simplificações que não devem chegar à defesa sem correção:

| Tema | Formulação segura e verificável |
|---|---|
| Conjunto da triagem | `79 753` é o conjunto completo; o treino temporal usa `28 574` linhas, a validação `17 710` e o teste `32 649`. |
| Vasicek | O prior de mercado é `1.0`; o do setor já ortogonalizado é `0.0`; o desvio-padrão comum é `0.5` (variância `0.25`). São escolhas de modelação, não estimativas transversais. |
| Triagem em produção | A probabilidade não deve ser apresentada como previsão nem como veto autónomo: com orçamento diário, ordena candidatas e ajuda a conter fadiga. |

O resultado negativo da QI3 é defensável e não precisa de ser "melhorado" à força. A volatilidade
sozinha obtém PR-AUC `0.542`; o melhor modelo com texto obtém `0.496`. A tabela de contexto sem
notícia fica em `0.534`, e o texto acrescenta `+0.012` sobre ela, sem ganhar a decisão no orçamento.
Isto prova uma coisa limitada e útil: nesta configuração, a identidade e o contexto da empresa
explicam mais a ordenação do que o título; o texto só acrescenta um sinal pequeno.

As explicações essenciais já são auto-suficientes e devem ser preservadas: F1 (§5.2), PR-AUC e
prevalência (§5.2), Brier (§5.2), R² do modelo efetivamente usado (§5.5), calibração de Platt
(§3.7) e a separação temporal com embargo (§3.7). São precisamente a preparação para perguntas de
júri; removê-las reduz a capacidade de defesa.

## 2. Valor científico imediato, sem complexidade artificial

1. **Não re-treinar para tentar melhorar a QI3.** Não existe uma alteração simples que melhore
   honestamente o resultado sem reabrir rótulos, divisão temporal, artefactos e conclusões.
2. **Correr o estudo de utilidade apenas com participantes reais.** O pacote em `docs/study/` está
   congelado; produzir respostas ou baixar o limiar de participantes fabricaria a única evidência
   humana em falta. Esta é a melhoria científica de maior valor, mas depende de recrutamento.
3. **Corrigir a porta de compilação canónica.** `.github/workflows/compile-thesis.yml` ainda vigia e
   compila `thesis/`, a tese inglesa antiga. A correção é pequena, mas só deve ser feita quando se
   decidir atualizar CI: mudar gatilhos, diretório de trabalho e artefacto para `tese/` e confirmar
   que a importação de `../thesis/references.bib` é incluída no gatilho.

## 3. Cortes defensáveis

Não há evidência para um corte agressivo do Apêndice A: as suas cinco funções — ambiente, origem de
números, matriz de evidência, dados e estudo humano por correr — sustentam diretamente a
reprodutibilidade e a honestidade da tese. Também ficam fora de corte os blocos já decididos pelo
aluno: métricas de §5.2, IA generativa de §2.4, o tom de §6.6 e o excerto anti-*lookahead*.

O único corte textual imediatamente defensável é o último parágrafo de **§1.5, “Estrutura do
documento”**: a nota longa que volta a localizar todos os estudos de caso repete a lista de capítulos
e navegação que o leitor já recebeu. Pode ser reduzida a uma frase ou removida, sem apagar método,
resultado ou limitação. A próxima compressão deve procurar a mesma classe de repetição no Capítulo
3, não remover as contas, exemplos reais ou limites que dão autonomia ao leitor.

## 4. Visuais com maior retorno

O documento já tem 35 figuras; o problema é menos quantidade do que transformar tabelas operacionais
em leitura imediata. Os três visuais que acrescentariam mais valor, se houver espaço, são:

| Local | Substitui | Desenho recomendado |
|---|---|---|
| §4.6, “As portas” | Tabela do funil de um dia | Funil horizontal: `5 060 avaliações → relevância → frescura → precedente → orçamento → 5 alertas`; cada seta mostra quantas avaliações ficaram e uma nota de que são avaliações, não notícias únicas. |
| §4.8, implantação | Prosa sobre worker, GitHub e histórico | Diagrama de implantação com dois processos Heroku, branch `alerts-history`, Telegram e painel; setas de leitura/escrita e a etiqueta “409 → tenta no ciclo seguinte”. |
| §3.5, decomposição | Parte da explicação verbal | Barra empilhada de um único dia: retorno observado = mercado + setor + empresa, com convenção explícita “retornos logarítmicos”; a Figura 3.6 já cumpre grande parte desta função, portanto só ampliar se substituir texto. |

Não se deve acrescentar um diagrama genérico de embeddings: a tese já explica o cosseno com pares
reais. Uma figura nova só vale se retirar prosa ou melhorar a preparação para o quadro.

## 5. Bibliografia

O Capítulo 1 já usa contexto recente e primário: Gallup (2025) para participação acionista e SIFMA
(2025) para dimensão do mercado. Não é necessária uma corrida a artigos de 2026 apenas por serem
recentes. A fonte FNSPID é KDD 2024 com DOI `10.1145/3637528.3671629`, logo não é uma pré-publicação.

As quatro pré-publicações que requerem uma decisão explícita são `araci2019finbert`,
`yang2020finbert`, `doshivelez2017rigorous` e `wu2023bloomberggpt`. Não devem ser trocadas às cegas:

- `araci2019finbert` identifica exatamente o modelo ProsusAI que foi medido; substituir por outro
  FinBERT falsearia a atribuição experimental.
- `yang2020finbert` pode ser substituída por `huang2023finbert` (Contemporary Accounting Research,
  DOI `10.1111/1911-3846.12832`) quando a frase for sobre a linhagem geral, não sobre o artefacto
  pré-publicado.
- `doshivelez2017rigorous` e `wu2023bloomberggpt` nomeiam obras concretas sem versão revista por
  pares encontrada; devem ficar localizadas e declaradas, apoiadas por fontes revistas vizinhas, em
  vez de se fingir que são artigos IEEE/ACM.

## 6. Migração privada e Heroku: causa e estratégia

O problema não é o Heroku ter "perdido" dados por si só. Há dois riscos distintos:

1. O worker vive num disco efémero. O repositório já corrige isto publicando JSONL na branch
   `alerts-history` pela API do GitHub (`investigator/history_publish.py`).
2. O painel lê a branch por `raw.githubusercontent.com`, sem autenticação
   (`api/services.py`, `investigator/alerts_history.py`, `investigator/live_kb.py`). Num repositório
   privado, esse URL devolve 404 e o código devolve uma lista vazia por desenho: é uma falha
   silenciosa. `docs/design/v3_backlog.md` já a descreve.

Uma migração segura requer primeiro alterar os leitores para que o **backend** autenticado leia a
API GitHub; nunca se coloca um token no browser. Depois, testar explicitamente “privado sem token”,
“privado com token” e “token sem permissão”, expondo no `/api/health` que o histórico está
indisponível em vez de parecer vazio. Só então se muda a visibilidade ou o nome do repositório.

Há uma divergência concreta a resolver antes de qualquer implantação: `app.json` anuncia
`INVESTIGATOR_HISTORY_GIT`, mas o caminho que funciona num slug Heroku sem `.git` usa
`INVESTIGATOR_HISTORY_API=1`; o próprio `docs/design/heroku_setup.md` documenta esta distinção.

### Inventário para um novo repositório

| Levar para `investigator/` (produção) | Guardar num arquivo de leitura apenas |
|---|---|
| `investigator/`, `api/`, `web/`, `config/alerts.yaml`, `models/triage_context_lr.joblib`, `data/samples/` necessário ao arranque, `scripts/run_alerts.py`, `scripts/post_validate.py`, `scripts/deploy_heroku.py`, `Procfile`, `app.json`, `requirements*.txt`, `pyproject.toml`, testes de runtime e workflows | `thesis/`, `thesis-pt/`, `archive/thesis-versions/thesis-examples/`, `paper/`, notebooks exploratórios, versões antigas Streamlit, slides e guias antigos, resultados intermédios e scripts de experiência não usados na operação |

Não se move nada da árvore atual antes de criar um *release* imutável: `tese/` depende de
`thesis/references.bib`, e as versões Streamlit ainda sustentam figuras e história de decisões.

## 7. Defesa em 12 slides e mapa de estudo

1. Problema humano: “o que aconteceu e consigo conferir?”
2. Promessa e fronteira: explicar passado, nunca prever.
3. Arquitetura de cinco peças.
4. Z-score: uma janela, uma conta, um alerta.
5. Decomposição: mercado + setor + empresa; priors declarados.
6. Precedentes: título → vetor → três casos anteriores → retornos observados.
7. Triagem: pergunta, rótulo e divisão temporal.
8. Resultado negativo: volatilidade ganha ao texto; o que isto significa e não significa.
9. Produto: alerta verificável, fonte e painel espelho.
10. MLOps: artefactos, anti-*lookahead*, histórico persistente, monitorização; sem re-treino.
11. Limitações assumidas: proxies, deriva, cobertura, ausência de estudo humano.
12. Contribuição: sistema funcional e avaliação que mantém resultados negativos.

Para memorizar o código, a sequência é: `scripts/run_alerts.py` → fontes de mercado/notícias →
relevância e deduplicação → z-score ou precedente → portas/orçamento →
`explanation_engine` → `telegram_bot` → `alerts_history`/branch de dados → API/painel. O diagrama
deve marcar, em cor diferente, os dois únicos estados persistentes: JSONL de histórico e SQLite de
subscrições.

## Próxima decisão

Antes de tocar no código de produção, escolher entre: (a) fechar primeiro a tese e a defesa; ou
(b) implementar a migração privada com leitura autenticada, testes e rotação de credenciais. A
segunda opção requer acesso às contas e não pode ser inferida a partir do repositório.

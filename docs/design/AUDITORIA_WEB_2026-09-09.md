# Auditoria e simplificação do painel — 9 de setembro de 2026

Pedido: auditar antes de alterar, simplificar a experiência e a arquitetura, medir a lentidão,
remover completamente a mascote da aplicação web e verificar regressões depois de implementar.
Este pedido substitui as decisões antigas que mantinham a mascote. Os motores, resultados,
orçamento de alertas, votos e artefactos de avaliação da dissertação não são redesenhados.

## Evidência anterior às alterações

Código vivo: `Procfile` → `api/main.py` → `api/services.py`; cliente `web/index.html`.
O worker `scripts/run_alerts.py` calcula e publica ficheiros na branch `alerts-history`.
O web e o worker têm discos distintos. A página não consulta uma base SQL; o SQLite pertence
ao bot, não ao percurso de leitura do painel. As aplicações Streamlit são anteriores.

Capturas e medições locais: `output/web_audit/before-desktop.png`, `before-mobile.png`,
`baseline.json`. Produção observada em 1440 × 1000 e 390 × 844, Chromium, língua en-GB.
Uma navegação: empresas aos 5,051 s, gráfico aos 6,947 s; primeira pintura aos 3,640 s.
Não são p50/p95, nem uma medição isolada de arranque do dyno.

| Resposta | Bytes sem compressão | Três pedidos consecutivos, segundos |
|---|---:|---|
| overview | 105 157 | 0,830 / 0,139 / 0,141 |
| alerts | 223 850 | 0,249 / 0,137 / 0,129 |
| screener | 39 511 | 0,130 / 0,122 / 0,119 |
| feedback | 847 | 0,129 / 0,125 / 0,120 |
| asset/AAPL | 172 698 | 0,135 / 0,136 / 0,133 |
| health | 90 | 0,119 / 0,122 / 0,119 |

Nenhuma destas respostas declarou compressão ou Cache-Control. No navegador, a empresa
AAPL demorou 1,913 s; as respostas repetidas acima já encontraram a cache aquecida.
Fontes remotas: snapshot 204 064 B; histórico 784 865 B; decisões 1 963 025 B;
base viva 42 120 609 B, obtida em 7,843 s nesta máquina.

## Achados confirmados

1. `carregar` espera por overview + screener + alerts + feedback antes de pintar. Uma falha
   do screener bloqueia a página mesmo havendo preços; a recuperação só se agenda depois do
   primeiro sucesso. O pedido de empresa vem depois desta barreira.
2. O overview entrega as séries de todas as empresas; o asset repete a série selecionada.
   O asset carrega ainda todas as notícias da empresa, mesmo no gráfico intradiário em que
   o controlo de notícias está desativado. Cerca de 157 KB da serialização Python do asset
   observado correspondem a notícias.
3. A API descarrega e interpreta `live_kb.jsonl`, com os vetores, para mostrar títulos e
   impactos. É trabalho proporcional à base de IA no pedido do leitor, embora o worker já
   possua todos esses dados. Não há consulta SQL lenta a otimizar neste percurso.
4. A cache permite carregamentos duplicados da mesma chave em pedidos concorrentes. Falhas
   remotas transformam-se em listas vazias; a interface pode confundir indisponibilidade com
   ausência de alertas. O estado de frescura fica congelado pelo TTL.
5. A abertura cria 120 mensagens, 1 105 elementos DOM e cinco checkboxes, três desativados.
   O detalhe começa a 1 165 px do topo. Dois PNG da mascote são pedidos na mesma navegação,
   cerca de 252 KB: primeiro o estado neutro, depois o estado do dia.
6. O detalhe inteiro é substituído ao mudar intervalo/camada. Os charts antigos não recebem
   `remove()`. A resposta de uma empresa pode sobrepor-se à seleção seguinte; não há guarda
   de concorrência nem feedback imediato durante o pedido.
7. O polling corre em separadores ocultos, pode sobrepor ciclos e usa a mudança do snapshot
   para decidir atualizar também votos/histórico, que têm relógios independentes.
8. O estado clicável dentro do botão da empresa é um `div` sem ação de teclado própria.
   Uma legenda equipara qualquer notícia travada a preço anómalo; são sinais diferentes.
9. O asset usa os PRIMEIROS 40 alertas da empresa; o endpoint do feed limita-se aos últimos
   200 sem informar o total nem permitir consultar o resto. AAPL ainda tem só 15: esse
   defeito do asset é confirmado no código, mas não afetava a AAPL observada.
10. O modal de decisões constrói um percurso linear fictício a partir da etapa final. Nem
    todas as portas são atravessadas em todos os ramos. O registo sustenta a decisão e a
    margem registadas; não sustenta esse percurso inteiro. O modal de um dia sem alerta
    também inventa a causa (porta ou orçamento) sem consultar uma decisão desse dia.

## Hipóteses e limites

- Não se mediu p95, memória/RSS do dyno, CPU sob carga, nem concorrência de visitantes.
- O crescimento do JSONL e a CDN do GitHub podem aumentar o custo/atraso; os bytes são
  medidos, a projeção desse crescimento ainda é uma hipótese.
- A fuga de recursos é confirmada pela ausência de destruição; a sua magnitude em MB não
  foi medida. A documentação de `IChartApi.remove()` define a destruição do chart.
- Capturas não demonstram conformidade WCAG. Teclado, contraste, reflow e erros precisam
  de verificação específica. O efeito sobre utilizadores reais exigiria um estudo.

## Arquitetura e fluxo propostos antes da implementação

Visão geral → empresa/evento → explicação → evidência → detalhe técnico.

| Parte | Decisão | Razão |
|---|---|---|
| Mascote, balão, semáforo ilustrado, PNG públicos | Eliminar | Pedido explícito; menos peso e decoração |
| Marca do cabeçalho | Nome tipográfico, sem cauda animal | Identidade profissional sem nova mascote |
| Cinco KPI grandes | Resumo compacto de movimento e cobertura | Retirar a competição com a tarefa principal |
| Doze cartões com sparklines | Lista compacta com preço e estado | Empresa e explicação no mesmo campo visual |
| Gráfico | Um detalhe; opções dentro de disclosure | Menos controlos; preservar análise histórica |
| Votos, portas, método, mensagens integrais | Evidência aberta por pedido | Preservar funções da tese sem as impor na entrada |
| Histórico | Vista própria, contagens com janela explícita | Não confundir amostra carregada com todo o canal |
| HTML monolítico | HTML + CSS + controlador + módulo de gráficos | Responsabilidades claras, sem framework/build novo |
| API | Overview compacto, asset rápido, notícias por pedido | Evitar sobretransporte e dependências no clique |
| Worker | Projeção de notícias sem embeddings | Tirar a base de IA do processo web |
| Cache | Exclusão por chave + último valor válido em falha | Evitar trabalho duplicado e falsos vazios |
| Atualização | Ciclo único, pausado quando oculto; recuperação | Menos rede e estados de falha compreensíveis |

A confiança não passa a ser um número inventado. Mostram-se raridade observada, ajuste R²
da decomposição e respetiva ressalva, idade dos dados e fontes. A probabilidade de triagem
continua fora das vistas de produto; a mensagem histórica mantém o texto entregue.

Verificação prevista: contratos API, falhas e concorrência, integridade das projeções,
troca de empresa/intervalo, teclado, ecrãs estreitos, gráficos, links de fontes, histórico,
recuperação e inspeção visual final. Não promover resultados de medições de interface para
resultados científicos da tese.

Referências técnicas primárias consultadas: [Starlette — middleware](https://www.starlette.io/middleware/),
[Starlette — responses](https://www.starlette.io/responses/),
[Lightweight Charts — IChartApi](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/IChartApi).

## Implementação e segunda revisão

Implementação concluída para validação local. **Sem deploy no Heroku e sem publicação de
dados remotos nesta tarefa.**

- Página dividida em HTML, CSS, controlador e gráficos, sem acrescentar framework ou build.
  Marca tipográfica e remoção dos oito PNG de mascote servidos pelo web. Os documentos e
  artefactos históricos da dissertação não foram reescritos.
- Entrada com lista compacta de empresas e explicação da seleção; histórico numa vista
  própria. Opções do gráfico, notícias, decisões registadas, votos e mensagens integrais
  aparecem por pedido. Mantidos os intervalos, escala de raridade e ressalva do ajuste R².
- API com overview e ativo independentes das notícias; projeção de notícias sem embeddings,
  cache com exclusão por chave, último valor válido e recuperação após falhas. Compressão
  gzip, cache de ficheiros estáticos e paginação do histórico completo.
- O worker prepara a projeção depois da entrega de mensagens, com escrita atómica e
  publicação limitada a uma tentativa bem-sucedida por 30 minutos. A lógica de deteção,
  triagem e os resultados científicos não foram alterados.
- Cliente com pedidos concorrentes partilhados, proteção contra respostas de seleções
  anteriores, destruição de gráficos/observers e polling sem sobreposição, pausado quando
  o separador está oculto. Falhas não são apresentadas como ausência de acontecimentos.

### Medições depois das alterações

Dados reais capturados, servidos pela API local. Os tempos locais não são comparáveis aos
tempos de produção; a comparação defensável aqui é de volume e de estrutura.

| Medida | Antes | Depois |
|---|---:|---:|
| Overview, JSON | 105 157 B | 6 991 B |
| Ativo AAPL, JSON | 172 698 B | 8 846 B |
| Overview, com gzip | — | 1 979 B |
| Ativo AAPL, com gzip | — | 2 652 B |
| Notícias: ficheiro remoto lido pelo web | 42 120 609 B | 1 696 593 B |
| Mensagens apresentadas inicialmente | 120 | 12 |
| Checkboxes expostos na entrada | 5 | 0 |
| Início do detalhe, desktop 1440 px | 1 165 px | 223 px |

A projeção local reúne 3 193 dias/empresa de 12 empresas, com impactos e manchetes
preservados; a sua geração demorou 0,943 s nesta máquina. O ficheiro contém cerca de 4%
dos bytes do antigo KB remoto. Notícias continuam a ter um custo quando são abertas,
mas esse custo deixa de bloquear o preço e a explicação inicial.

### Segunda revisão e verificações

Inspeção no navegador em desktop e a 390 × 844: seleção de empresa, intervalos,
disclosure de opções, escala z, notícias e decisões registadas. A revisão encontrou um
overflow real no telemóvel: a largura mínima intrínseca do canvas expandia a grelha até
898 px. Corrigido com `minmax(0, 1fr)`; reconferido sem deslocação horizontal. Revistos
os rótulos, as unidades dos impactos e a distinção entre notícias e alertas entregues.

Os testes focados de API, qualidade da decomposição, marca, publicação/entrega e novos
contratos passaram. Os seis testes Node passaram: partilha de pedidos, repetição após
falha, resposta tardia, libertação de gráficos/observers, pausa em segundo plano e links
seguros. Os dez novos testes Python incluem cache concorrente, falhas/recuperação,
paginação com novas mensagens, projeção e publicação com repetição limitada.

A execução anterior da suite geral terminou com 1 069 testes aprovados e uma falha num
teste que exigia a mascote. Esse contrato foi atualizado ao pedido explícito e o conjunto
focado voltou a passar. Não se apresenta essa execução anterior como uma suite geral
verde. `check_entrega.py` passou; permanecem as pendências humanas já registadas no projeto.

Não se mediram ainda p95/RSS/CPU em Heroku, conformidade WCAG integral ou ganho com
utilizadores reais. A inspeção visual e os testes não substituem essas medições.

### Validação local e passagem futura a produção

Executar a partir da raiz:

```powershell
.venv/Scripts/python.exe -m scripts.preview_web --data output/web_audit --port 8879
```

Abrir `http://localhost:8879/`. A pré-visualização está ligada apenas a 127.0.0.1,
com preços capturados até 8 de setembro de 2026 e 605 mensagens históricas reais.
O aviso local identifica os dados congelados. Não executa o worker nem envia alertas.

O autor valida esta versão antes de decidir o deploy. Uma implantação futura terá de
publicar primeiro `dashboard_news.json` na branch de dados e confirmar a leitura pela
aplicação, além de medir o arranque e a recuperação no ambiente Heroku. Essa publicação
não foi efetuada nesta tarefa. Os scripts de captura apontam por defeito para `output/`,
protegendo as figuras já entregues na dissertação.

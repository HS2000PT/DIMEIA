# PRODUCT_ROADMAP.md — melhorar produto, resultados e materiais (Sessão 40+)

> ⚠️ **SUPERADO (2026-07-30). Registo histórico — não é o plano ativo.**
> O plano vivo é [`PLANO_V2.md`](PLANO_V2.md). Cadeia de sucessão:
> `MASTER_PLAN` → `PRODUCT_ROADMAP` → `PLANO_MELHORIAS` → **`PLANO_V2`**.
> ⚠️ As caixas por marcar aqui incluem itens entretanto **CORTADOS por decisão** (chatbot-mascote,
> carteira do utilizador, multi-bolsa). Ver `PLANO_V2.md` §6 para os cortes e as razões.

> Origem: mensagem grande do aluno (2026-07-22), desiludido com os resultados e o produto. Pediu
> melhorias reais, pensamento crítico e sugestões, por área. Este ficheiro captura TUDO + a minha
> leitura crítica + prioridades + o que precisa de decisão. **Nada aqui contradiz as restrições
> fundadoras** (só APIs grátis, XAI-first, sem previsão de preços, honestidade).

## 0. A leitura crítica honesta (o problema central)
O aluno está certo: **o produto não conta uma história clara e útil**, e o "sinal" mais forte
(retrieval) é o mais confuso. As causas reais, sem rodeios:

1. **Tema ≠ direção (o nº 1).** "Muitas notícias positivas, mas os casos passados são quedas." O
   retrieval devolve precedentes por *assunto*, não por *direção*: uma notícia otimista sobre chips de
   IA recupera um *cluster* de ameaça competitiva cujo impacto médio foi negativo. A tese já é honesta
   sobre isto (CS3), mas **como produto é enganador**. É a causa direta da desilusão. → precisa de um
   redesenho da apresentação do retrieval (agrupar/filtrar por direção observada, mostrar a
   distribuição, e liderar com o sinal mais claro), não de mais modelo.
2. **A história chega tarde.** O facto mais forte (o "porquê") aparece depois do ruído. → reordenar o
   alerta e o painel para o *lead* ser a conclusão, não o processo.
3. **Critério de alerta demasiado severo e rígido.** Poucos alertas, sem controlo do utilizador. →
   thresholds mais sensíveis e **configuráveis**.
4. **Sem feedback de "vida".** Não mostra estado do mercado, não parece tempo-real, sem personalidade.
   → estado aberto/fechado, intradiário por defeito, mascote, temas.
5. **Ícones/direção ainda confusos.** Setas ambíguas. → cor+forma inequívocas (sobe=verde, desce=vermelho).

**Princípio:** primeiro tornar o que JÁ existe *claro e honesto* (baixo risco, alto valor), depois
adicionar features. Marketing/apelo vem A SEGUIR à clareza — um produto bonito que confunde é pior.

## 1. App / Produto
### Quick wins (alto valor, baixo risco) — próximo sprint
- [ ] **Setas por cor+forma:** sobe = verde, desce = vermelho, sem ambiguidade (Telegram + painel).
      Rever `direction_icon` e os testes de fidelidade XAI. (queixa repetida do aluno)
- [ ] **Estado do mercado em tempo real** (aberto/fechado + próxima abertura/fecho) no topo do painel.
- [ ] **Critério de alerta mais sensível + configurável** (thresholds; níveis de severidade já existem —
      expor e baixar o chão com cuidado; documentar que a tese congela os seus valores).
- [ ] **Vista intradiária por defeito** no gráfico (1D), com auto-refresh (ping periódico honesto).
- [ ] **Retrieval honesto e claro:** agrupar precedentes por direção observada (subiram/desceram),
      mostrar a divisão (ex.: "4 de 6 caíram"), e a moldura "evidência de padrão, não previsão".
      **Este é o item que mais muda a perceção de valor.**
### Tema + personalidade (fun, marketing)
- [ ] **Tema light/dark automático por hora** (dia claro, noite escuro) — uma função única de "hora"
      que também troca: **mascote crocodilo dia/noite**, fundo (sol/lua ou por hora). Manter toggle manual.
- [ ] **Mascote da app** (o crocodilo InvestiGator, além do logo) — ilustração alegre/silly/investigador.
- [ ] **Logo/interface mais customizados/ousados** (o aluno quer mais personalidade).
### Maiores (precisam de desenho/decisão)
- [ ] **Autenticação no painel: perfis admin/guest.** Default = guest (só leitura). Login admin →
      alterar definições por cliques (sem consola); as mudanças do admin refletem-se nos alertas do
      Telegram. **DECISÃO:** onde guardar as settings (a branch `alerts-history`? um ficheiro de config
      versionado? um segredo?) e como o admin autentica sem servidor (token simples? Streamlit secrets?).
- [ ] **Mais bolsas + fusos europeus** (Xetra, Euronext, LSE…). **DECISÃO:** quais e quantas (cada uma =
      calendário de sessão + fonte de preços grátis + mapa de setores). Começar por 1 (ex.: Xetra).
- [ ] **Chatbot mascote (futuro):** o crocodilo responde a perguntas, pesquisa PRIMEIRO nos nossos dados
      (KB/alertas), depois na net em tempo real. **DECISÃO/ÂMBITO:** precisa de um LLM (custo? só grátis?),
      e "pesquisar na net" tem de respeitar "só APIs grátis". Desenhar como trabalho futuro na tese +
      protótipo local. Alinha com XAI se ele CITAR as fontes/precedentes.

## 2. Resultados / Ciência (melhorar o que o modelo entrega)
- [ ] **Retrieval direção-aware na apresentação** (ver §1) — o maior ganho de perceção.
- [ ] **Insight primeiro:** o alerta lidera com a conclusão (o facto + a direção dos precedentes),
      detalhe depois. Reescrever `explain_*` por camadas (já começado na F1).
- [ ] **Sensibilidade do detetor:** rever o chão de severidade e a recência; talvez EWMA (já validada,
      F1 0,664 > 0,516) como opção — muda a produção, não a tese congelada.
- [ ] **Ser crítico e medir:** cada mudança de produto avaliada no loop de pós-validação (precisão ao
      vivo). Sem fabricar — reportar como cai.

## 3. Tese
- [x] **Frases de estilo especificação-de-software removidas do apêndice** — reescrito para prosa
      de dissertação que descreve o sistema. Feito (2026-07-22).
- [ ] **Apêndice REFEITO por completo** (pedido explícito): de "lista de ficheiros/comandos" para
      **snapshots + relatórios**. Mostrar: (a) o ambiente; (b) **snapshots reais dos objetos de dados**
      em cada fase (linha FNSPID, barra de preços, caso da KB com embedding, linha de features, rótulo);
      (c) **relatórios de avaliação reais** (tabelas/figuras de saída) por trás de cada número; (d)
      evidência de operação ao vivo. **NUNCA** caminhos de ficheiro/comandos "corre isto" (o júri não tem
      git) nem linguagem que soe a especificação de software. Mostrar o TRABALHO, não os ficheiros.
- [ ] **Mais figuras/diagramas/charts no corpo** (como nos slides/guia). O aluno sente falta dessa
      transparência/clareza visual ao longo da tese. Candidatos: a "jornada dos dados" (já lá está, F7),
      mais visuais de fluxo por RQ, snapshots de dados, um diagrama do ciclo de vida do alerta simples.
- [ ] **Sincronizar tudo isto na tese PT** (regra bilingue).

## 4. Guia de estudo / Apresentação
- [ ] Já ganharam muitos visuais (jornada dos dados, built-with, ablação). Manter a régua: cada conceito
      com UM visual claro. Rever se algum slide ainda é "parede de texto".
- [ ] Espelhar as melhorias de produto quando estabilizarem (mascote, temas, retrieval claro).

## Sequência proposta (a discutir com o aluno)
1. **Sprint "Clareza" (produto):** setas cor+forma · estado do mercado · intradiário por defeito ·
   retrieval direção-aware · alerta lidera com o insight · thresholds configuráveis. ← maior ROI.
2. **Sprint "Personalidade":** tema auto por hora + mascote dia/noite + fundo + logo/interface ousados.
3. **Apêndice refeito (snapshots+relatórios) + mais figuras no corpo** (EN e PT em sincronia).
4. **Maiores (com decisão):** auth admin/guest · mais bolsas (começar por Xetra) · chatbot mascote (futuro).
5. **Contínuo:** tradução PT capítulo a capítulo (BILINGUAL_PLAN.md).

## Decisões que preciso do aluno
- **Auth:** onde vivem as settings do admin e como autentica (sem servidor)?
- **Bolsas:** quais primeiro (sugiro Xetra) e até quantas?
- **Chatbot:** que LLM/orçamento (só grátis?), e âmbito do "pesquisar na net"?
- **Marketing/estética:** quão "ousado/polémico" pode ser o logo/mascote (tom, cores)?

# PLANO FINAL — as 4 frentes pós-ML (P1–P4)

> **Origem:** pedido do aluno (2026-07-05), após o fecho do workstream ML (M0–M7): fazer TUDO —
> polimento da escrita da tese, rename `src/`→`investigator/`, KB FNSPID multi-ano e S-APP (Fase B) —
> pela ordem que fizer mais sentido. Este ficheiro é o checkpoint multi-dispositivo (como o
> `ML_PLAN.md` foi para o ML): qualquer sessão futura retoma daqui + `CLAUDE.md` + `CHECKLIST.md`.

## Ordem escolhida (racional)

| # | Frente | Porquê nesta posição |
|---|--------|----------------------|
| **P1** | **Polimento da escrita da tese** | É o artefacto avaliado. As secções novas da RQ4 (M7) foram escritas numa maratona e nunca receberam o passe editorial das Sessões 23–24. Zero risco técnico; valor máximo. |
| **P2** | **Rename `src/`→`investigator/`** | Fazê-lo ANTES de escrever código novo (P3/P4) evita criar ainda mais referências a `src/` para migrar. Tese/paper não referem `src/` (verificado na Sessão 27) → não afeta o P1. |
| **P3** | **KB FNSPID multi-ano** | O corpus 2018–2023 já está no disco (`data/fnspid_news_subset.csv`, provado pelo estudo de triagem). A KB nova nasce já no layout novo do P2. Alimenta o P4 (precedentes mais ricos na app/bot). |
| **P4** | **S-APP — Fase B (Telegram/app)** | A maior frente e a única explicitamente pós-submissão. Beneficia de tudo o que vem antes (pacote limpo, KB rica). Desenho já existe em `docs/design/going_live.md` (Fase B). |

## Estado

### P1 — Polimento da escrita da tese
- [x] Diagnóstico: travessões-conectores em prosa = **0** (só 2 comentários TikZ + 1 célula de tabela
      aceite); tiques clássicos de IA = **0**. O trabalho é nas secções novas da RQ4.
- [x] Passe editorial às secções RQ4: Ch2 §triage, Ch3 §met_triage + §protocolo, Ch4 §learned severity,
      Ch5 CS4, Ch6 (RQ4/contribuições), Ch1/abstract (frases longas partidas, ecos de palavras
      removidos, voz natural). **Regra: nenhum número, citação, equação, tabela ou figura muda.**
- [x] Passe rápido de coerência ao resto (grep de tiques, EN-GB, consistência de rótulos).
- [x] Recompilar: 0 erros, 0 citações indefinidas, overfull ≤15pt, abstract ≤200 palavras.
      Commit `5c4c099` (reflow legítimo 74→76 pp, sem páginas vazias).

### P2 — Rename `src/` → `investigator/`
- [x] Pacote instalável (pyproject `[project] investigator` + `-e .` no requirements.txt); hacks
      `sys.path` removidos dos scripts (guard do app fica — robustez no Streamlit Cloud). Bundles
      joblib re-serializados (pickle referia `src.triage.model`) com probe numérico idêntico.
- [x] Imports migrados em todos os .py; ci.yml/verify.sh/tasks.json/tests.bat → `ruff check .`.
- [x] Sync de docs internos que citavam `src/…`: CLAUDE.md (inventário), caderno de defesa, learning.md,
      glossary.md, guia de estudo (frames P5 com caminhos), README (layout), how_to_run.
- [x] Gates: 93 testes + ruff verdes; AppTest verde; demo reproduz +6,46%; guia recompila (63
      slides, 0 erros). CI a verificar no push.

### P3 — KB FNSPID multi-ano (retrieval)
- [x] Build FEITO (destacado, `run/kb-fnspid.cmd` + tarefa VS Code; log `data/kb_build.log`):
      79.753 registos, SBERT 384-d, ~691 MB gitignored; amostra de 50 em
      `data/samples/kb_fnspid_sample.jsonl`. ⚠️ `--sample` apontada a um caminho NOVO — o defeito
      esmagaria a `kb_sample.jsonl` da demo/tese (e com dim 384≠64).
- [x] Validação honesta em `docs/evaluation/kb_fnspid_build.md`: 14/15 tickers (META="FB"),
      2023=44%, impactos ±1/3d completos e plausíveis; **200 registos (0,25%) com +5d=NaN**
      (fim da janela de preços — documentado); consultas AI/Fed/recalls devolvem os clusters certos
      (sim 0,62–0,85, cross-ticker a funcionar).
- [x] Decisão de consumo: produção na nuvem fica na stack leve com a KB-amostra (números da tese e
      deploy intocados); a KB multi-ano é artefacto local para SBERT + base do trabalho futuro do
      Cap. 6. Data card atualizado ("construída como artefacto; avaliação multi-ano continua futuro").
- [x] Gate: números da tese intocados (demo continua a reproduzir +6,46%); testes verdes.

### P4 — S-APP — Fase B (Telegram interativo + app UX)
- [x] Decisão: **long-polling** em vez de webhook (funciona sem servidor/host, de graça, atrás de
      NAT); utilizadores em **SQLite stdlib** (`data/bot_users.db`, gitignored); webhook/host fica
      documentado como evolução (o transporte está separado da lógica pura).
- [x] Implementado: `investigator/telegram_bot/{store,commands,interactive}.py` +
      `scripts/run_bot.py` + `run/bot.bat` + tarefa VS Code; runner com fan-out por subscritor
      (`bot.enabled` no alerts.yaml, off por defeito, fail-open provado); **10 testes novos**
      (store/comandos/parsing, offline) → 103 no total; segredos só no `.env`.
- [x] UX da app: expander "Get the alerts on your phone" na Home (canal + bot, moldura honesta);
      métrica de testes 93→103.
- [x] Runbook: going_live.md Fase B marcada CONSTRUÍDA (2 passos para ligar) + how_to_run §2.5;
      produto responsável implementado (limite 20 tickers, /stop reversível, validação de tickers).

### P5 — Produto real + sincronia total p/ defesa (pedido de 2026-07-06: "real product, no bullshit; tudo em sync; eu domino tudo")
- [x] Runner endurecido com defeitos REAIS corrigidos: anti-repetição de notícias (`news_is_fresh`,
      ≤2 dias) e anti-duplicado em feriados (`bar_is_fresh`, só avalia com sessão nova) — testados.
- [x] App pública com precedentes REAIS: KB leve curada do FNSPID (2.016 registos 2018–2023, 3,4 MB,
      versionada; `scripts/curate_kb_light.py`, determinística) + `kb_query_embedder()` lê a dimensão
      do próprio ficheiro (coerência por construção); decisão 256-d COM evidência (menos colisões);
      caption honesta ("word overlap, mais fraco que o SBERT da tese"). Demo/Cap. 3 intocados.
- [x] Badge do workflow Alerts no README (o cron vivo, à vista); factos do README atualizados
      (bot construído, 16 frames, 63→64 slides, KB como artefacto).
- [x] Tese: bullet de trabalho futuro do Cap. 6 atualizado com honestidade (a KB JÁ foi reconstruída;
      futuro = a avaliação sobre ela). 76 pp, 0 erros, 0 refs indefinidas, 0 overfull >15pt.
- [x] Caderno: **§0 guião oral** (abertura de 3 min + resposta de 15s por RQ, só números congelados)
      + **§6.5 O produto hoje** (tabela "como mostrar em 30s" + honestidades prontas + plano B sem wifi).
- [x] Guia: frame "O produto, HOJE" (64 slides, 0 erros). Slides de defesa verificados (sem staleness).
- [x] 106 testes + ruff verdes; demo reproduz +6,46%.
- **Próximo desenhado (não construído):** retrieval semântico na nuvem via MiniLM-ONNX
      (onnxruntime, ~23 MB) para fechar o fosso word-overlap↔SBERT na app pública — registado
      no CHECKLIST como melhoria futura.

### P6 — Zero-ops REAL (pedido de 2026-07-06: "não quero fazer nada; tempo real; painel vivo")
- [x] **Intradiário:** alerts.yml corre de 30 em 30 min em horário de mercado US (Actions grátis
      em repo público) + concurrency (nunca 2 em paralelo).
- [x] **Estado entre corridas:** `load_state/save_state/filter_new_alerts` (reset diário preserva
      o offset do bot) via cache do Actions — a mesma anomalia/manchete nunca repete no dia; testes.
- [x] **Notícias LIGADAS no canal** (10 tickers) com o **gate de triagem treinado (0.5) como
      controlo de fadiga** — o mecanismo da RQ4 em produção real (dry-run ao vivo: suprimiu 7
      manchetes 26–49%, deixou passar TSLA).
- [x] **Bot sem máquina do aluno:** comandos processados EM LOTE em cada corrida (resposta ≤30 min,
      documentado); `bot_users.db` + estado persistidos na cache (falha crítica do runner efémero
      apanhada antes de morder); aviso "um consumidor getUpdates de cada vez".
- [x] **Live board na app** (landing): watchlist com preço, movimento, z-score, badge de anomalia
      (ícone+texto, nunca só cor), sparkline 30 sessões, tiles, auto-refresh 120s (fragment),
      ordenado por |z|; offline nos testes (usa a seam get_price_history); AppTest dedicado.
- [x] Onboarding do canal: mensagem afixada + descrição prontas a colar (going_live §1b; canais
      não têm boas-vindas automáticas — limitação da plataforma, documentada).
- [x] 109 testes + ruff verdes; render real do Live board verificado (10 tickers, 0 exceções).

### P7 — Revisão DURA de usabilidade: mensagens Telegram + app (pedido de 2026-07-06: "pasta de palavras; amador; refaz")
- [x] **Mensagens reescritas em camadas** (facto primeiro, lista, método em nota curta) com
      **HTML no Telegram** (negrito/itálico; sender com parse_mode + fallback texto puro;
      conteúdo dinâmico escapado, incl. eco de comandos do bot). Alerta de mercado: 5 linhas
      repetitivas → 3 em camadas. Alerta de notícia: **INTERVALO dos precedentes antes da média**
      (a média sozinha esconde direções mistas — coerente com o CS3 da tese); manchetes truncadas
      a 100 chars; nota final curta. TODOS os números calculados preservados (fidelidade XAI
      testada). `plain_text()` para consola/app/logs.
- [x] **App deslastrada**: disclaimer 1× (sidebar), knobs → expander "Advanced" (top_k/horizon/
      window/threshold), métricas dev (testes/citações) fora da cara do utilizador, Live board
      com colunas/captions enxutas, /help do bot agrupado. 5 páginas renderizam sem exceções.
- [x] **Sincronia**: demo/how_to_run/guia (frames de output atualizados ao formato novo, valores
      congelados intactos; 64 slides 0 erros); tese Cap. 4 = 1 frase honesta ("formato compactado
      depois; campos idênticos; fidelidade inalterada" — CS3 fica como registo congelado);
      caderno §7 com a pergunta do júri sobre a evolução do formato. 76 pp, 0 erros.
- [x] 109 testes + ruff verdes.

## Guardrails (herdados, sempre em vigor)
Zero fabricação; números validados nunca editados à mão; sem previsão de preço/direção; só compute
grátis; segredos nunca em ficheiros versionados; commits PT-PT com
`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; sem force-push; CLAUDE.md atualizado no fim
de cada sessão.

# CHECKLIST — InvestiGator (o que está feito / o que falta)

> Lista viva para acompanhar o estado, com caixas de seleção. É a **lista de tarefas acionável** —
> o histórico detalhado está em [progress/TRACKER.md](progress/TRACKER.md) e
> [progress/SESSIONS.md](progress/SESSIONS.md); o racional de cada item está no relatório de
> auditoria (plano). Marca `[x]` à medida que fechas cada ponto.

---

## ✅ Feito — Sessão 27 (auditoria + polimento + flagship)
- [x] **Correr num comando** volta a funcionar numa máquina limpa: `requirements.txt` leve +
      `requirements-ml.txt` + `setup_env.sh --ml` (o torch `+cpu` já resolve). *(C1)*
- [x] **CI corre os testes**: `.github/workflows/ci.yml` (pytest + ruff a cada push de código). *(C2/C3)*
- [x] `CITATION.cff` (botão "Cite this repository" no GitHub).
- [x] Índice `docs/README.md`, `ROOT_PROMPT` → `docs/internal/`, badges no README.
- [x] **Dashboard Streamlit** `app/streamlit_app.py` + guia de deploy `docs/design/deployment.md`.
- [x] **Correr por cliques**: `.vscode/` (Run & Debug ▶ + tarefas) + `run/*.bat` (duplo-clique).
- [x] **Sistema de alertas 24/7 (código)**: `scripts/run_alerts.py` + `config/alerts.yaml` + timer
      `.github/workflows/alerts.yml` + runbook `docs/design/going_live.md` (validado: dry-run encontrou
      anomalia real ao vivo; não envia). *Falta só os cliques humanos abaixo.*

---

## 🤖 EM CURSO — componente de ML treinado (triagem de materialidade; RQ4)
> **Plano-mestre e checkpoint multi-dispositivo: [progress/ML_PLAN.md](progress/ML_PLAN.md)** (desenho
> fixado, fases, dados, áreas de IA incl. a tradução honesta do "RL" do aluno). Proposta ao orientador:
> [docs/internal/proposta_ml_orientador.md](docs/internal/proposta_ml_orientador.md).
> **Regra:** o texto da tese só muda depois do OK do Prof. Luís Gomes (M7).
- [x] **HUMANO: proposta ao Prof. Luís Gomes** — **OK dado em 2026-07-04** (o orientador confia no
      aluno e deu luz verde a tudo; está de férias). **Gate do M7 ABERTO.**
- [x] M1 — Rótulos (retorno anormal vs SPY) + `scripts/build_dataset.py` + testes anti-lookahead.
- [x] M2 — `investigator/triage/` + `scripts/train_triage.py` (LR + GBM, split temporal, calibração, seeds).
      *(Ablação sentimento FinBERT: hook desenhado, adiada para M6 — só entra se ajudar na validação.)*
- [x] M3 — *Smoke evaluation* no corpus Finnhub → `docs/evaluation/evaluation_triage.md` + figuras.
- [x] M4 — Isolation Forest vs z-score (números z-score congelados intactos).
- [x] M5 — Integração off-by-default (linha no alerta, gate `min_materiality` no runner, severidade na
      app; produção usa a variante só-contexto `models/triage_context_lr.joblib` — stack leve, sem SBERT).
- [x] M5.5 — **Loop de pós-validação** (runner regista decisões → `scripts/post_validate.py` rotula ao
      maturar (d+3) com o resultado real → `docs/evaluation/live_monitoring.md` → receita de retreino)
      — a forma defensável da ideia "RL" do aluno. O loop já está armado: correr o post_validate
      dias depois de o runner correr com notícias ligadas.
- [x] M6 — **FEITO (madrugada de 2026-07-05)**: FNSPID 2018–2023 → 79.753 exemplos (0 descartes,
      14/15 tickers — META="FB" no corpus) → retreino. Resultado: vol PR-AUC 0,542 imbatível pelo
      texto; triagem quase 4× melhor que alertar-sempre no orçamento diário (0,632 vs 0,163).
- [x] M7 (tese) — RQ4 integrada de ponta a ponta (Caps. 1–6 + abstract; 74→76 pp após o passe editorial, 0 erros, 52/52
      citações; gate aberto pelo orientador em 2026-07-04).
- [x] M7 (materiais) — **FEITO (2026-07-05)**: paper IEEE (4 pp, +2 refs), slides de defesa (16 frames,
      +Result 4 + 3 perguntas de júri), guia de estudo (63 slides, +3 frames que ensinam a triagem do
      zero + slide "o que usa" corrigido), caderno (§5 RQ4 + mapa de números + 4 perguntas), app/README
      (93 testes, 52/52, claim "trains no model" corrigido), page-audit estendido.
- [x] S-APP — FEITA como P4 do plano final (ver secção seguinte).

## 🎯 EM CURSO — as 4 frentes finais (plano: [progress/PLANO_FINAL.md](progress/PLANO_FINAL.md))
> Ordem decidida em 2026-07-05 (pedido do aluno: "fazer tudo"): P1 polimento da escrita da tese →
> P2 rename `src/`→`investigator/` → P3 KB FNSPID multi-ano → P4 S-APP (Fase B).
- [x] P1 — Polimento editorial das secções novas da RQ4 + coerência global (0 números alterados;
      frases-comboio partidas em Ch2/Ch3/Ch5/Ch6, ecos removidos; 76 pp, 0 erros, 0 overfull >15pt).
- [x] P2 — Rename `src/`→`investigator/` FEITO (pacote instalável, -e ., bundles re-serializados com
      probe idêntico, docs sincronizados; 93 testes + ruff + demo verdes).
- [x] P3 — KB de retrieval FNSPID 2018–2023 FEITA (79.753 registos SBERT, ~691 MB local; validação
      em docs/evaluation/kb_fnspid_build.md; números da tese e deploy intocados).
- [x] P4 — S-APP Fase B FEITA (bot long-polling sem servidor: /start /watch /unwatch /list /stop;
      SQLite; fan-out no runner off por defeito e fail-open; 10 testes novos → 103; app com
      secção "alerts no telemóvel"). Ligar: scripts/run_bot.py + bot.enabled no alerts.yaml.

## ⏳ A fazer — EU (humano; ninguém pode fazer por ti)
### Pôr o sistema 24/7 ao vivo (grátis) — ver [docs/design/going_live.md](docs/design/going_live.md)
- [x] Criar um **canal de Telegram** e adicionar o bot como **administrador**.
- [x] Definir **3 segredos** no GitHub (Settings → Secrets → Actions): `TELEGRAM_BOT_TOKEN`,
      `TELEGRAM_CHAT_ID` (= canal), `FINNHUB_API_KEY` (opcional).
- [x] Correr o workflow **"Alerts (scheduled scan)"** uma vez (Actions → Run workflow) para testar.
- [x] Tornar o **repositório público** (necessário para o dashboard público + Actions ilimitados).
- [x] **Publicar o dashboard**: <https://investigator.streamlit.app> (URL já no README).
- [x] **Tornar a app pública no Streamlit** — feito pelo aluno (2026-07-06).
- [ ] **Afixar a mensagem de onboarding no canal** + colar a descrição (textos prontos a copiar
      em `docs/design/going_live.md` §1b — canais não têm boas-vindas automáticas; o pin é o padrão).
- [ ] (Verificação, 1 min) Abrir <https://investigator.streamlit.app> em janela anónima e ver o
      **Live board**; e no dia útil seguinte confirmar no separador Actions que o workflow "Alerts"
      corre de 30 em 30 min e que o canal recebe sem repetições.
- [ ] (Opcional) Renomear o repositório GitHub `DIMEIA` → `InvestiGator` (Settings → Rename; o GitHub
      redireciona os URLs antigos; depois avisar para atualizar badges e re-ligar o Streamlit).
- [ ] **Escolher a licença do código** com o Prof. Luís Gomes (MIT/Apache; confirmar política de IP do
      ISEP) e adicionar o ficheiro `LICENSE`.
- [ ] Confirmar a **redação exata da declaração de uso de IA** exigida pela MEIA/ISEP + a **data de entrega**.
- [ ] **Leitura final** de toda a tese (o texto é teu para defender).
- [ ] Ver no GitHub → separador **Actions** que o CI novo está verde.

---

## 🧰 Polimento opcional (seguro, quando quiseres)
- [x] Renomear `src/` → `investigator/` — **FEITO no P2 do plano final** (pacote instalável via
      pyproject + `-e .`; hacks `sys.path` removidos; docs sincronizados; bundles re-serializados).
- [ ] Relatório de cobertura (`pytest --cov`) + o número no README/CI.
- [ ] Ajuda de **horas de mercado** (mercado aberto/fechado) — também vira figura de "framework geral".
- [ ] Camada de **logging** (`logging` em vez de `print` no código de biblioteca).
- [ ] SBERT em singleton + matriz da KB pré-calculada (desempenho, quando a KB/UI crescer).
- [ ] Retrieval SEMÂNTICO na nuvem: MiniLM em ONNX (onnxruntime, ~23 MB, sem torch) na app pública —
      fecha o fosso word-overlap↔SBERT mantido honesto na caption da página News.
- [ ] CLI para o Gatilho 2 (`python -m …`) a espelhar o Gatilho 1.

---

## 📝 Conteúdo da tese (precisa da tua caneta)
- [ ] Parágrafo + figura de **generalização** (o *framework* é agnóstico ao mercado; NASDAQ/NYSE é a
      *instância de avaliação*).
- [ ] Apêndice de **reprodutibilidade** melhorado (receita leve/ML, badge de CI, "como reproduzir os números").
- [ ] Secção de **Trabalho Futuro** (integrar Streamlit/Telegram/nuvem/multi-mercado).

---

## 🚀 Trabalho futuro (pós-submissão, opcional)
- [x] Onboarding self-service no **Telegram** — FEITO (P4; long-polling + SQLite; webhook/host = evolução).
- [ ] Alojamento **24/7 na nuvem** (Fly.io / Render / Oracle Free).
- [ ] **Multi-mercado** (registo de bolsas + calendários).
- [x] Construir a **KB FNSPID** multi-ano — FEITA (P3; 79.753 registos; avaliação multi-ano = futuro).
- [ ] Estudo de **utilidade com humanos** (confiança apropriada).

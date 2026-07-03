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
> Plano completo no plano de sessão; proposta ao orientador em
> [docs/internal/proposta_ml_orientador.md](docs/internal/proposta_ml_orientador.md).
> **Regra:** o texto da tese só muda depois do OK do Prof. Luís Gomes (M7).
- [ ] **HUMANO: enviar a proposta ao Prof. Luís Gomes** (email; o ficheiro acima é o corpo).
- [ ] M1 — Rótulos (retorno anormal vs SPY) + `scripts/build_dataset.py` + testes anti-lookahead.
- [ ] M2 — `src/triage/` + `scripts/train_triage.py` (LR + GBM, split temporal, calibração, seeds).
- [ ] M3 — Estudo honesto no corpus Finnhub → `docs/evaluation/evaluation_triage.md` + figuras.
- [ ] M4 — Isolation Forest vs z-score (números z-score congelados intactos).
- [ ] M5 — Integração off-by-default (linha no alerta, gate no runner, severidade na app).
- [ ] M6 — **HUMANO: deixar o download FNSPID a correr uma noite** (tarefa/click preparado) → retreinar.
- [ ] M7 — Tese (RQ4, Cap. 2/3/4/5/6) — **gated no OK do orientador**; depois sync paper/slides/guia.

## ⏳ A fazer — EU (humano; ninguém pode fazer por ti)
### Pôr o sistema 24/7 ao vivo (grátis) — ver [docs/design/going_live.md](docs/design/going_live.md)
- [x] Criar um **canal de Telegram** e adicionar o bot como **administrador**.
- [x] Definir **3 segredos** no GitHub (Settings → Secrets → Actions): `TELEGRAM_BOT_TOKEN`,
      `TELEGRAM_CHAT_ID` (= canal), `FINNHUB_API_KEY` (opcional).
- [x] Correr o workflow **"Alerts (scheduled scan)"** uma vez (Actions → Run workflow) para testar.
- [x] Tornar o **repositório público** (necessário para o dashboard público + Actions ilimitados).
- [x] **Publicar o dashboard**: <https://investigator.streamlit.app> (URL já no README).
- [ ] **Tornar a app pública no Streamlit** (ainda pede login): share.streamlit.io → a app → **⋮ →
      Settings → Sharing → tornar pública** (foi implantada quando o repo era privado).
- [ ] (Opcional) Renomear o repositório GitHub `DIMEIA` → `InvestiGator` (Settings → Rename; o GitHub
      redireciona os URLs antigos; depois avisar para atualizar badges e re-ligar o Streamlit).
- [ ] **Escolher a licença do código** com o Prof. Luís Gomes (MIT/Apache; confirmar política de IP do
      ISEP) e adicionar o ficheiro `LICENSE`.
- [ ] Confirmar a **redação exata da declaração de uso de IA** exigida pela MEIA/ISEP + a **data de entrega**.
- [ ] **Leitura final** de toda a tese (o texto é teu para defender).
- [ ] Ver no GitHub → separador **Actions** que o CI novo está verde.

---

## 🧰 Polimento opcional (seguro, quando quiseres)
- [ ] Renomear `src/` → `investigator/` (pacote instalável; tirar o `sys.path`) — **sessão dedicada** com
      sincronização dos docs (a tese/paper não referem `src/`, por isso não são afetados).
- [ ] Relatório de cobertura (`pytest --cov`) + o número no README/CI.
- [ ] Ajuda de **horas de mercado** (mercado aberto/fechado) — também vira figura de "framework geral".
- [ ] Camada de **logging** (`logging` em vez de `print` no código de biblioteca).
- [ ] SBERT em singleton + matriz da KB pré-calculada (desempenho, quando a KB/UI crescer).
- [ ] CLI para o Gatilho 2 (`python -m …`) a espelhar o Gatilho 1.

---

## 📝 Conteúdo da tese (precisa da tua caneta)
- [ ] Parágrafo + figura de **generalização** (o *framework* é agnóstico ao mercado; NASDAQ/NYSE é a
      *instância de avaliação*).
- [ ] Apêndice de **reprodutibilidade** melhorado (receita leve/ML, badge de CI, "como reproduzir os números").
- [ ] Secção de **Trabalho Futuro** (integrar Streamlit/Telegram/nuvem/multi-mercado).

---

## 🚀 Trabalho futuro (pós-submissão, opcional)
- [ ] Onboarding self-service no **Telegram** (webhooks + utilizadores em SQLite + `/start`, `/watch`…).
- [ ] Alojamento **24/7 na nuvem** (Fly.io / Render / Oracle Free).
- [ ] **Multi-mercado** (registo de bolsas + calendários).
- [ ] Construir a **KB FNSPID** multi-ano completa (o pipeline de streaming já existe).
- [ ] Estudo de **utilidade com humanos** (confiança apropriada).

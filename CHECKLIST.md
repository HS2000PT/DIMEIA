# CHECKLIST — CLARION (o que está feito / o que falta)

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

---

## ⏳ A fazer — EU (humano; ninguém pode fazer por ti)
- [ ] **Publicar o dashboard** (grátis) seguindo [docs/design/deployment.md](docs/design/deployment.md)
      e **colar o URL** no README e na tese.
- [ ] **Escolher a licença do código** com o Prof. Luís Gomes (MIT/Apache; confirmar política de IP do
      ISEP) e adicionar o ficheiro `LICENSE`.
- [ ] Confirmar a **redação exata da declaração de uso de IA** exigida pela MEIA/ISEP + a **data de entrega**.
- [ ] **Leitura final** de toda a tese (o texto é teu para defender).
- [ ] Ver no GitHub → separador **Actions** que o CI novo está verde.

---

## 🧰 Polimento opcional (seguro, quando quiseres)
- [ ] Renomear `src/` → `clarion/` (pacote instalável; tirar o `sys.path`) — **sessão dedicada** com
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

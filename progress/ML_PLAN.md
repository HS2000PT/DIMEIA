# ML_PLAN — Componente de ML treinado (triagem de materialidade) · plano-mestre e checkpoint

> **Fonte de verdade multi-dispositivo** deste workstream. Qualquer sessão futura retoma daqui
> (+ `CHECKLIST.md` + `CLAUDE.md`), sem depender de nenhum chat aberto.
> Proposta ao orientador: [docs/internal/proposta_ml_orientador.md](../docs/internal/proposta_ml_orientador.md).
> **Regra de ouro: o texto da tese só muda depois do OK do Prof. Luís Gomes (gate M7).**

---

## 1. Porquê (contexto da decisão)

O aluno quer demonstrar **engenharia de ML feita por ele** (não só integração de componentes
pré-treinados) — antecipando a pergunta do júri "onde está o modelo que TU treinaste?". Decisão
(2026-07-03, com avisos dados e aceites): construir um **modelo supervisionado de triagem/materialidade
de notícias**, mantendo as restrições da tese (❌ previsão de preços/direção; ✅ APIs grátis, XAI-first,
reprodutível).

**RQ4 (rascunho):** *Pode um modelo supervisionado, treinado com notícias históricas e contexto de
mercado, priorizar utilmente as notícias que merecem alerta, para além de baselines simples de
volatilidade?*

**Enquadramento honesto (ideia de carga):** o modelo estima P(movimento anormal se segue) — "esta
notícia merece alerta?" — **nunca** direção nem alvo de preço. Se perder para a baseline de
volatilidade, reporta-se na mesma (o contributo metodológico mantém-se).

## 2. Desenho fixado (não rediscutir sem razão nova)

| Peça | Decisão |
|------|---------|
| Unidade | (título, ticker, dia de evento d) — d = 1.º dia de negociação ≥ data da notícia (regra da KB) |
| Rótulo | `\|retorno anormal em (d, d+3]\| ≥ τ`; anormal = retorno simples do ticker − retorno do SPY; τ primário **2%**; ablação τ∈{1.5,2,3}% × h∈{1,3,5} |
| Features (≤ fecho de d; anti-lookahead testado) | embedding SBERT MiniLM do título (384-d) · vol20 (std dos 20 retornos que terminam em d−1) · mom5 (retorno acumulado 5d até d−1) · ret_event (d−1→d, a reação imediata — legal: a janela do rótulo começa no fecho de d) · setor (one-hot, mapa igual a `scripts/evaluate.py:38`) · comprimento do título · [ablação: sentimento FinBERT] |
| Modelos | alertar-sempre · LR só-volatilidade (baseline forte) · **LR texto+contexto (principal, interpretável)** · HistGradientBoosting (comparação) — sklearn, CPU, seeds |
| Protocolo | split **temporal** 70/15/15 por **dias únicos** + embargo de 5 dias de negociação (`--embargo`; corpus-fumo usa 1 — ver §4) · calibração (val) · métricas: **PR-AUC** (principal), ROC-AUC, Brier, precision@N-alertas/dia |
| XAI | coeficientes LR + decomposição aditiva por alerta; SHAP no GBM (Lundberg & Lee já citado) |
| Artefactos | `models/triage_lr.joblib`, `triage_gbm.joblib`, `triage_metadata.json` (janela de treino, seed, τ, métricas) — commitados se <5 MB |
| Números congelados | as avaliações já validadas na tese NUNCA são editadas; o novo estudo é aditivo |

## 3. Fases e estado (atualizar as caixas aqui a cada sessão)

- [x] **M0** — Proposta ao orientador escrita (`docs/internal/proposta_ml_orientador.md`) + CHECKLIST. *(2026-07-03)*
- [x] **M0.5** — Este plano persistido no repo (checkpoint multi-dispositivo). *(2026-07-03)*
- [x] **M1** — Rótulos + dataset: `abnormal_returns` puro em `src/correlation_engine/event_study.py`;
      `src/triage/dataset.py` (event_features, abnormal_label, assign_splits, SECTORS);
      `scripts/build_dataset.py` (cache de preços em `data/prices/`, incl. SPY; amostra committada);
      testes anti-lookahead + embargo + rótulo à mão.
- [x] **M2** — Treino: `src/triage/{features,model,explain}.py` + `scripts/train_triage.py`
      (split temporal, 4 modelos, calibração, seeds; grava models/ + md + figuras). Ablação sentimento
      FinBERT (inferência; só entra se ajudar na validação).
- [x] **M3** — **Smoke evaluation** no corpus Finnhub → `docs/evaluation/evaluation_triage.md` marcado
      como *smoke* (corpus de 4 semanas — ver §4); figuras PR/calibração.
- [x] **M4** — Isolation Forest vs z-score no harness de `evaluate_anomaly.py` (linhas z-score
      byte-idênticas; IF é comparação, não substituto salvo vitória clara).
- [x] **M5** — Integração **off-by-default**: linha de materialidade no `explain_news_impact` (redação
      honesta "evidência de triagem, não previsão"), `min_materiality` no `config/alerts.yaml`
      (gate no runner, fail-open), severidade na página News da app (ausência do models/ é graciosa).
      *Decisão de produção:* a stack leve (runner/app na nuvem) não tem SBERT ⇒ o treino grava também
      a variante **só-contexto** (`models/triage_context_lr.joblib`, 1,8 KB) e é ESSA que a produção
      pontua (`src/triage/infer.py`, com guarda de compatibilidade de features); o texto identifica
      sempre a variante. Retreino de verificação: modelos principais **bit-idênticos** (reprodutível).
      AppTest verde com e sem `models/`. *(2026-07-04)*
- [x] **M5.5** — **Loop de pós-validação** (a visão "RL" do aluno, na forma defensável — ver §5):
      o runner regista cada decisão em `data/predictions_log.jsonl` (`src/triage/postval.py::log_decision`,
      fail-safe — nunca pára a varredura); `scripts/post_validate.py` rotula as decisões **maturadas**
      (janela (d, d+3] fechada) com o resultado REAL — mesma regra `abnormal_label` do treino, preços
      frescos — e escreve `docs/evaluation/live_monitoring.md` (precisão das mantidas vs base rate,
      Brier, calibração em 3 faixas, receita de retreino, caveats: runner do Actions é efémero ⇒ o loop
      completo corre na máquina do aluno; persistência na nuvem = Fase B). Validado ao vivo: 3 decisões
      reais registadas (pendentes, correto — hoje ainda não maturou) + sonda com data antiga maturou
      contra preços reais (label 1; Brier 0,25 = (0,5−1)² exato). 12 testes puros novos. *(2026-07-04)*
- [ ] **M6** — **FNSPID 2018–2023** (números finais da tese): **click preparado** —
      `run/fnspid-overnight.bat` (ou tarefa VS Code "FNSPID overnight (M6)") corre em cadeia
      download (~3,4 h) → limpa a cache de preços (era 2026) → dataset (embargo 5) → retreino SBERT;
      log em `data/fnspid_overnight.log`. **HUMANO: deixar a correr uma noite** (stack `--ml`).
      Na manhã seguinte: testes verdes + commit dos modelos/docs/figuras regenerados.
- [ ] **M7** — **Tese e materiais (GATED no OK do orientador):** RQ4 no Cap. 1; Cap. 2 fundamentação curta
      (event study com ajuste de mercado; materialidade — citações verificadas como as 50 existentes);
      Cap. 3 secção (tarefa/rótulos/protocolo/ameaças); Cap. 4 componente + figuras; Cap. 5 estudo;
      Cap. 6 veredicto RQ4; abstract. Depois: paper, slides de defesa, **guia de estudo** (novas partes
      ensinadas do zero), caderno. Auditoria de páginas estendida. **Deixar para o fim, por decisão do
      aluno — primeiro melhorar a solução.**

**Sessões futuras dedicadas (registadas, não agora):**
- [ ] **S-APP** — melhorar app + comandos/configuração do Telegram para utilizadores (Fase B desenhada em
      `docs/design/going_live.md`: host Student Pack, webhook, `/start /watch /unwatch /stop`, BD).
- [ ] **S-THESIS** — sincronização final tese + guia de estudo + slides + caderno (= M7; fica no fim).

## 4. Dados (garantias e caminho)

- **Agora:** `data/finnhub_news.csv` — 3.714 títulos, 15 tickers, **só 4 semanas** (2026-05-28→06-24;
  ~12 títulos/ticker/dia). Serve para montar o pipeline ponta-a-ponta; os números daqui são **smoke**
  (caveat de clustering: muitos títulos do mesmo (ticker, dia) partilham o rótulo → split por dias únicos;
  embargo 1 no corpus-fumo, 5 no FNSPID).
- **Números finais:** **FNSPID 2018–2023**, 15 tickers (download em streaming validado, ~1.300 linhas/s,
  ~3,4 h; CC BY-SA 4.0, atribuição obrigatória).
- **Preços:** yfinance (ticker + SPY; atraso ~15 min — honesto e suficiente para alertas diários);
  cache local `data/prices/` (gitignored).
- **Candidatos futuros (grátis, registados):** **SEC EDGAR 8-K** (eventos materiais "oficiais" — futura
  fonte de rótulo/feature academicamente forte), RSS (parser já existe), Alpha Vantage news-sentiment
  (25/dia), GNews/Marketaux (chaves já no .env.example). **Nada disto é preciso para M1–M6.**
- **Tempo-real em produção:** subir a frequência do cron de notícias (Fase A) é suficiente já; streaming
  verdadeiro pertence à Fase B (host sempre ligado).

## 5. Avaliação das áreas de IA (pedido do aluno — decisões honestas)

| Área | Decisão | Racional |
|------|---------|----------|
| ML / DL | **NÚCLEO deste plano** | modelo de triagem treinado pelo aluno (ciclo completo); SBERT é DL aplicado; fine-tune contrastivo = Tier-2 futuro |
| NLP | **já núcleo + aprofunda** | embeddings/recuperação; ablação com sentimento FinBERT (inferência) em M2/M3 |
| **RL** | **traduzido para M5.5** | a visão do aluno ("decidir agora, validar com o que realmente aconteceu") é **aprendizagem contínua com rótulos atrasados + monitorização**, não RL clássico (não há MDP: as nossas ações não afetam o mercado). Full-RL seria armadilha de júri. *Bandits contextuais* para ajustar o limiar de alerta = trabalho futuro documentado |
| Visão computacional | **não-objetivo deliberado** | não há dados visuais; forçar seria gimmick (a tese/guia já o dizem — força na defesa) |
| Robótica | **não aplicável** | — |
| IA Generativa | **trabalho futuro com cautela** | camada narrativa LLM sobre factos rastreáveis conflitua hoje com XAI-first (fidelidade) + free-tier |
| IA Agêntica | **= Fase B do Telegram** | bot interativo com comandos/ferramentas; desenhado em going_live.md |

## 6. Verificação (gates de cada fase)

`bash scripts/verify.sh` verde (47+ testes + ruff) · treino reproduzível (`--seed 42` 2× → métricas
idênticas) · números congelados intactos (linhas z-score byte-idênticas; demo +6,46%; AppTest verde com e
sem `models/`) · nenhum número entra na tese sem script committado que o regenere · commits PT-PT.

## 7. Como retomar numa sessão nova (qualquer dispositivo)

1. Ler `CLAUDE.md` (estado) + este ficheiro (§3: primeira caixa por fazer) + `CHECKLIST.md`.
2. `bash scripts/start_session.sh` (pull) · stack: leve chega até M1; M2+ precisa de
   `bash scripts/setup_env.sh --ml` (SBERT para features).
3. Executar a fase seguinte; no fim: atualizar as caixas do §3 + CLAUDE.md, `verify.sh`, commit, push.

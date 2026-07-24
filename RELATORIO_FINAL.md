# RELATÓRIO FINAL — InvestiGator 🐊

> **Dissertação MEIA/ISEP** — Henrique José da Silva Santos (nº 1180934)
> Orientador: Prof. Luís Gomes · Coorientador: Rafael Silva · Data: 2026-07-11
> Este documento resume TUDO o que existe neste repositório e onde está — pensado para
> uma leitura de 10 minutos pelo orientador ou pelo júri.

---

## 1. O que é

**InvestiGator** — *Explainable Financial Alerts for Retail Investors* — é um sistema
inteligente de alertas financeiros **explicável (XAI-first)** para o mercado US
(NYSE/NASDAQ), com dois gatilhos: (1) **movimento abrupto de mercado** (anomalia
estatística por z-score móvel, sem lookahead) e (2) **nova notícia financeira**
(recuperação semântica de precedentes históricos + impacto observado — event study).
O núcleo é um motor de correlação notícia–mercado sobre o dataset FNSPID (CC BY-SA 4.0).
**Restrições duras:** sem previsão de preços, sem trading algorítmico, só APIs gratuitas.

## 2. O que foi construído (e está validado)

### 2.1 Sistema (pacote `investigator/`)
- **Deteção de anomalias** (`anomaly_detector/`): z-score móvel causal; comparado e
  vencedor vs Isolation Forest (F1 0,530 vs 0,271) e vs limiar fixo (consistência de
  disparo 0,015 vs 0,344 de amplitude entre tickers).
- **Motor de correlação** (`correlation_engine/`, `historical_kb/`): base de conhecimento
  de casos (notícia + impacto +1/+3/+5d + embedding); recuperação por cosseno.
  Embedders: SBERT (tese), MiniLM-ONNX (produção, paridade validada) e hashing (baseline).
- **Triagem de materialidade — o modelo treinado pelo autor (RQ4)** (`triage/` + `models/`):
  regressão logística calibrada (Platt), rótulos por retorno anormal vs SPY, split temporal
  com embargo, testes anti-lookahead. Resultado honesto: a volatilidade-só bate os modelos
  com texto em PR-AUC (0,542 vs 0,496), MAS a triagem quase quadruplica a precisão no
  orçamento de 5 alertas/dia (0,632 vs 0,163) — reportado tal como é.
- **Explicação XAI** (`explanation_engine/`): o alerta carrega todos os números que o
  justificam; testes de fidelidade impedem regressões.
- **Entrega** (`telegram_bot/`, `news_fetcher/`): Telegram (canal + bot interativo
  `/watch`), Finnhub/RSS para notícias ao vivo.

### 2.2 Produto ao vivo (grátis, sem servidor próprio)
- **Canal Telegram** (<https://t.me/InvestiGatorMEIA>): alertas com **qualidade primeiro** —
  filtro de relevância (manchetes mal etiquetadas/boilerplate rejeitadas), chão de similaridade,
  teto de 2 alertas de notícia por ticker/dia, gate de triagem, aviso de direção mista, e um
  **resumo diário ao fecho** (os 10 tickers, honesto em dias calmos). Corre também de manhã e
  aos fins de semana (só notícias). Produtores: modo vigia (VM, ~5 min, com **deteção
  intradiária** via cotação em tempo real) + cron do GitHub como rede de segurança, com dedup
  partilhado (`docs/design/vm_watch.md`). **KB viva:** cada manchete relevante vira precedente
  dias depois (impacto real a +5d); retrieval com decaimento por idade e idade visível;
  anomalias com **investigação cruzada** ("Possible explanation: …" ou "no public explanation
  yet").
- **Dashboard público** (<https://investigator.streamlit.app>): estilo Google Finance — uma
  aba por empresa, UM gráfico grande (1D/5D/1M/6M) com os eventos detetados marcados na curva
  (hover = o alerta exato do canal; nunca recalculado), a mesma lista em tabela, e o
  "background risk" do modelo treinado (RQ4). Read-only; método/avaliação/citação numa vista
  About separada. Identidade "The Stare" (olho de crocodilo sobre linha de mercado) + slogan
  "Every move investigated, never predicted.".
  Keep-alive automático via workflow; opção 24/7 sem hibernação na VM
  (`deploy/investigator-app.service`).
- **Bot interativo** (`scripts/run_bot.py`): watchlist pessoal por utilizador, SQLite,
  long-polling — sem custos de alojamento.

### 2.3 Avaliação (números congelados, regenerados por scripts versionados)
| Resultado | Valor | Onde |
|---|---|---|
| Recuperação P@5 (5 seeds) | SBERT-MiniLM **0,514±0,015** vs lexical 0,346, acaso 0,240 | `docs/evaluation/evaluation_results.md` |
| Consistência do z-score | amplitude **0,015** vs **0,344** (limiar fixo) | `evaluation_anomaly.md` |
| IF vs z-score | F1 **0,271 vs 0,530** (o simples ganha, validado) | idem |
| Triagem RQ4 (FNSPID 79.753) | PR-AUC vol 0,542 > texto; **precisão@5/dia 0,632 vs 0,163** | `evaluation_triage.md` |
| Paridade produção ONNX↔SBERT | cosseno médio **0,992**; 96% vizinhos top-3 comuns | `onnx_minilm_validation.md` |
| Loop de pós-validação ao vivo | decisões reais registadas e rotuladas ao maturar | `live_monitoring.md` |

### 2.4 Documentos académicos
- **Tese** (`thesis/`, EN-GB): 6 capítulos canónicos MEIA, **86 pp, 0 erros, 0 citações
  indefinidas, 52/52 referências verificadas uma a uma** (auditoria em
  `docs/decisions/page_audit.md`). RQ1–RQ4 respondidas com os números acima; inclui um
  screenshot genuíno do painel único (Cap. 4, Fig. 4.5).
- **Paper IEEE** (`paper/`): 4 pp, compila 0 erros (destilado da tese validada).
- **Slides de defesa** (`slides/`): 17 frames (+"The product, live", com o mesmo screenshot).
- **Guia de estudo ÚNICO** (`slides/guia_estudo/main.pdf`): 71 slides PT-PT — ensina do zero
  E contém o guião oral, as perguntas do júri, o mapa dos números congelados e o plano B
  (fonte única de estudo; os antigos caderno/guia rápido foram absorvidos e arquivados).
- **Notebook** (`notebooks/investigator_walkthrough.ipynb`): os 3 componentes com as próprias
  mãos, executado e commitado com outputs reais.

### 2.5 Qualidade de engenharia
- **202 testes automáticos + ruff**, verdes localmente e no CI (runner limpo a cada push).
- **Reprodutibilidade:** demo offline num comando (`python scripts/demo.py` reproduz o
  exemplo do Cap. 3, +6,46%); todas as figuras/números da tese saem de scripts versionados;
  ambiente fixado (Python 3.12, `requirements*.txt`).
- **Segurança:** zero segredos no repo (scan à história completa); segredos só em
  GitHub Actions Secrets / `.env` local.

## 3. Mapa do repositório (ficheiros principais)

```
RELATORIO_FINAL.md      ← este documento
README.md               porta de entrada (badges, como correr, estado)
CHECKLIST.md            SÓ o que falta (lista mínima)
CLAUDE.md               memória de continuidade entre sessões
thesis/main.pdf         A TESE (86 pp)               thesis/main.tex + ch1..ch6/
paper/                  artigo IEEE (4 pp)
slides/main.pdf         slides de defesa (17)        slides/guia_estudo/main.pdf (guia único, 71)
investigator/           o pacote do sistema (instalável; um subpacote por componente)
models/                 modelos de triagem treinados (joblib versionados + metadados JSON)
notebooks/              investigator_walkthrough.ipynb — os 3 componentes, executado
app/streamlit_app.py    painel único ao vivo (uma aba por ticker)
scripts/                demo.py · run_alerts.py (produção) · run_bot.py · evaluate*.py ·
                        build_dataset.py · train_triage.py · post_validate.py · build_kb.py
config/alerts.yaml      watchlist + limiares + gates (a MESMA fonte para runner e app)
.github/workflows/      ci.yml (testes) · compile-thesis.yml · alerts.yml (varredura 30/30)
tests/                  202 testes
data/samples/           amostras versionadas (KB curada 2.016 registos 384-d incluída)
docs/design/            how_to_run · going_live · deployment · arquitetura · data card
docs/evaluation/        TODOS os resultados (gerados por script; não editados à mão)
docs/decisions/         page_audit (52/52 citações) · reviews · learning.md · glossário
progress/               MASTER_PLAN · TRACKER · SESSIONS · DECISIONS (continuidade)
```

## 4. Como ver tudo a funcionar em 10 minutos

1. `bash scripts/setup_env.sh && python scripts/demo.py` — os dois gatilhos, offline (+6,46%).
2. Abrir <https://investigator.streamlit.app> — escolher uma aba de ticker, ver o "Background risk".
3. Entrar no canal <https://t.me/InvestiGatorMEIA> — alertas reais em horário de mercado.
4. Abrir `thesis/main.pdf` — a tese; `docs/evaluation/` — os números com os scripts ao lado.
5. GitHub → Actions — CI verde + varreduras "Alerts" automáticas (+ branch alerts-history a crescer).

## 5. O que falta (apenas ações humanas)

| # | Ação | Com quem |
|---|---|---|
| 1 | Escolher a **licença do código** (MIT/Apache; política de IP do ISEP) | Prof. Luís Gomes |
| 2 | Confirmar a **redação exata da declaração de uso de IA** + data de entrega | Prof. Luís Gomes / MEIA |
| 3 | **Leitura final** da tese pelo autor | autor |
| 4 | Tornar a app Streamlit **pública** de novo (regrediu no último redeploy) | autor (1 clique) |
| 5 | Afixar a mensagem de onboarding no canal (textos prontos em `going_live.md` §1b) | autor |
| 6 | 08–09/07: `python scripts/post_validate.py` (maturação das decisões reais) | autor (1 comando) |
| 7 | (Opcional) migrar para repositório novo sem história — ver `docs/design/migrar_repo.md` | autor |

## 6. Nota de integridade

Nenhum resultado foi editado à mão: cada número da tese regenera-se pelo script indicado.
Os resultados negativos (o texto não bate a volatilidade; o IF perde para o z-score; a
recuperação capta tema, não direção) estão **reportados e discutidos** — fazem parte da
contribuição. O uso de IA no desenvolvimento está declarado no front matter da tese.

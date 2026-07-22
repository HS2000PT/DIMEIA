# roadmap_rq4.md — Melhorar a triagem (RQ4): "não estamos no fim da linha"

> Roteiro honesto e VIÁVEL (só free tier, anti-lookahead, XAI-first) para melhorar os
> resultados da triagem de materialidade E enriquecer a tese. Aditivo por desenho: os
> modelos e `evaluation_triage.md` **congelados** ficam intactos; tudo aqui gera ficheiros
> NOVOS. Estado atual de cada item marcado com ✅ (feito) · 🧭 (código pronto, corrida
> pendente de dados) · 🔭 (futuro desenhado).

## Ponto de partida (RQ4 v1 — congelado, não mexer)

Da `evaluation_triage.md` (FNSPID 2018-2023; teste 32 649 linhas, prevalência 0,378):

| Modelo | PR-AUC | Brier | Precisão@5/dia |
|---|---|---|---|
| Alertar-sempre (chão) | 0,378 | 0,622 | 0,163 |
| LR só-volatilidade | **0,542** | 0,218 | 0,632 |
| LR só-contexto | 0,538 | 0,224 | 0,632 |
| LR contexto+texto | 0,496 | 0,229 | 0,585 |

**Leitura honesta (o que a tese já diz):** nenhum modelo com TEXTO bate a volatilidade em
PR-AUC — reportado tal como é. **MAS** como *mecanismo de triagem*, a precisão@orçamento salta
de 0,163 (alertar sempre) para **0,632** (≈4×): o modelo vale para **priorizar**, não para
prever. É daqui que partimos. Há margem — e cada passo abaixo é defensável e ensina.

## Eixo 1 — Novos critérios (features) + estudo de ablação  ✅ FEITO (2026-07-22)

> **Resultado (honesto, na máquina com o corpus FNSPID):** os 5 sinais novos **NÃO ajudam** a
> triagem. Âncora `context` v1 = PR-AUC **0,537** (reproduz o congelado 0,538); `context+5` =
> **0,535** (Δ −0,002). Na ablação *leave-one-in/out*, só `ret_event_z` (a reação padronizada =
> o \|z\| do detetor) tem sinal positivo, e só +0,001; os restantes são planos ou ligeiramente
> negativos. **Leitura:** a volatilidade rolante já absorve quase tudo o que estes sinais baratos
> carregam — a MESMA lição do texto, alcançada pelo lado oposto: a materialidade de curto prazo
> resume-se notavelmente bem a UM número. Reportado tal como caiu; nada muda na produção.
> Artefactos: `docs/evaluation/evaluation_triage_ext.md` + `thesis/figures/eval_triage_ext.pdf`
> (via `scripts/train_triage_ext.py`); secção nova na tese (Cap. 5, Fig. da contribuição marginal).

A hipótese: a triagem só via `{vol20, mom5, ret_event}`. Sinais baratos (sem novas fontes,
todos anti-lookahead) que podem ajudar — e uma **ablação** que responde honestamente "quais
AJUDAM de facto?". Implementados e testados em `investigator.triage.dataset.event_features_ext`
(aditivo; teste anti-lookahead em `tests/test_triage_dataset.py`):

| Feature nova | O que capta | Porquê pode ajudar |
|---|---|---|
| `market_vol20` | regime de volatilidade do MERCADO (SPY) | dias de mercado nervoso ⇒ mais movimentos "anormais" por ruído |
| `mom20` | momento de 20 dias da ação | tendência prévia condiciona a reação a notícias |
| `vol_ratio` = vol20/vol60 | volatilidade da ação a expandir/contrair | expansão ⇒ maior probabilidade de movimento material |
| `ret_event_z` = ret_event/vol20 | a reação imediata PADRONIZADA (o \|z\| do detetor) | reação já grande no dia d é o sinal mais direto |
| `downside_vol20` | risco de queda (só retornos negativos) | assimetria: quedas materiais comportam-se diferente |

**Como treinar/justificar (MESMO protocolo congelado, sem batota):** split temporal por dias
únicos + embargo (h≤5), calibração **Platt** na validação (seed 42), avaliação por **PR-AUC +
precisão@5/dia + Brier** — idênticos à v1, para comparar maçãs com maçãs. A ablação treina, na
MESMA validação, as famílias: `context` (v1) · `context+ext` · e *leave-one-in*/`leave-one-out`
por feature nova → **tabela de contribuição marginal** ("cada sinal vale quanto?"). Resultado
esperado e honesto: provavelmente `ret_event_z` e `market_vol20` ajudam mais; alguns não ajudam
— e reportamos como caiu (o mesmo rigor do "o texto não bate a volatilidade").

**Valor para a tese:** uma secção nova de *feature ablation* (Cap. 5) + figura de contribuição —
transforma "adicionámos features" em ciência ("estes sinais ajudam, estes não, e porquê").

### Como correr (reprodutível na máquina com o corpus)
```
python scripts/build_dataset.py --ext --news data/fnspid_news_subset.csv  # → triage_dataset_ext.csv
python scripts/train_triage_ext.py                                        # ablação de contexto
# → docs/evaluation/evaluation_triage_ext.md + thesis/figures/eval_triage_ext.pdf
```
O bloco `context_ext` foi acrescentado (aditivo) a `investigator/triage/features.py` (o caminho
congelado fica byte-idêntico: o dataset da tese não tem as colunas estendidas). A ablação corre em
segundos, offline e determinística (só features de contexto; sem SBERT). **Não toca** em `models/`
nem em `evaluation_triage.md`.

> **Estado (2026-07-22):** CORRIDO nesta máquina (a do corpus FNSPID + `torch`; o mesmo PC do
> cabeçalho congelado `C:\Users\henri\…`). Resultado acima. Nada fabricado — números gerados dos
> próprios dados; a âncora `context` reproduz o congelado (0,537 vs 0,538).

## Eixo 2 — Extensões já VALIDADAS (adotar como "futuro já provado")

- **EWMA na norma de volatilidade** ✅ validado (sessão 38): F1 0,664 > 0,516 do rolling (mesmo
  recall, ~metade dos falsos positivos — clustering de volatilidade). Produção fica rolling por
  explicabilidade; a adoção é futuro **já medido** (`evaluate_anomaly_ext.py`).
- **Platt vs isotónica** ✅ validado (sessão 39): Platt ganha/empata no Brier em todas as
  famílias (`calibration_platt_vs_isotonic.md`) — a escolha da tese confirmada empiricamente.

## Eixo 3 — O loop empírico (já a correr)  ✅

A pós-validação ao fecho (`post_validate.py`, agora zero-ops na branch `alerts-history`) rotula
as decisões reais com o resultado observado → `live_monitoring.md` (precisão das mantidas vs
base rate, Brier ao vivo). É a prova de que o mecanismo se mantém fora da amostra — e a fonte de
dados para um **retreino periódico** com rótulos atrasados (MLOps, não RL clássico).

## Eixo 4 — Futuro que precisa de novas fontes  🔭

- **Volume / gap / amplitude intradiária** (volume relativo, open−fecho anterior, (high−low)/close):
  exigem OHLCV (não só fecho) — trocar `fetch_closes` por OHLCV no build. Sinais fortes de
  convicção; ficam para quando o build carregar OHLCV.
- **Proximidade de resultados (earnings)**: flag "resultados a ≤N dias" (Finnhub earnings, free).
- **Sentimento (FinBERT)**: pesado (transformer dedicado); documentado como extensão, não base.

## Definição de pronto (deste roteiro)
Eixo 1 ✅ corrido ⇒ `evaluation_triage_ext.md` + figura + parágrafo honesto na tese (nenhum dos 5
sinais ajudou — reportado como caiu). Eixos 2–3 já na tese como validados. Eixo 4 fica em "trabalho
futuro" com fontes identificadas (volume/OHLCV, earnings, FinBERT). **Sem números fabricados em
nenhum ponto.**

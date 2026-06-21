# PLANO_SESSOES — Plano detalhado (~30 sessões + buffer)

> Guia flexível orientado pela **qualidade** (§18), não um limite rígido. Adicionar sessões se a qualidade
> exigir; não encher por número. **Estado atual: Sessões 0–2 concluídas** (ver `TRACKER.md`/`SESSIONS.md`).
> Disciplina de âmbito (§5.3): **thin slice primeiro**; cada componente na versão mais simples e defensável.

## Marcos (milestones)
- **M1 — Thin slice a funcionar** (1 gatilho → alerta Telegram): ~Sessão 11.
- **M2 — Componentes principais concluídos**: ~Sessão 18.
- **M3 — Avaliação executada** (resultados honestos): ~Sessão 22.
- **M4 — Rascunho completo da tese**: ~Sessão 26.
- **M5 — Pronto para defesa** (revisão + mock + slides): ~Sessão 30.

## Plano por sessão
| Sessão(s) | Fase / Bloco | Objetivo & entregáveis | Depende de |
|---|---|---|---|
| **0** ✅ | Setup (Fase 0) | Scaffold, permissões, segredos, scripts, CI, memória persistente; 1.º commit/push | — |
| **1** ✅ | Análise (Fase A) | `analise_referencia.md` (+ benchmark 4 diss.) e `analise_template_latex.md` | 0 |
| **2** ✅ | Planeamento (Fase C) | Título (T1), arquitetura + metodologias (8 refs verificadas), `free_apis.md`, `evaluation_design.md`, este plano | 1 |
| **3** | LaTeX (Fase D) | Integrar template ISEP em `thesis/`; mapear 7 capítulos em `chN/`; `references.bib` com as 8 refs; resolver `latexmk.rc`; compilar (CI verde) | 2 |
| **4–5** | Escrita — Contextualização | Cap. introdução + contextualização com dados de mercado US **2025–2026** (estatísticas reais, figuras); refs verificadas | 3 |
| **6–9** | Escrita — Revisão de literatura | Estado da arte (anomalias, XAI, NLP financeiro); **tabelas comparativas**; ampliar refs verificadas (`citation_log.md`) | 3 |
| **7–9** | Escrita — Metodologia | Capítulo de metodologia + diagramas de arquitetura (a partir de `arquitectura_sistema.md`) | 6 |
| **10–11** | **Thin slice (M1)** | `market_data`→`anomaly_detector`(z-score)→`explanation_engine`(regra)→`telegram_bot`; smoke test real | 3; `.env` Telegram |
| **12–13** | Componente — Base histórica | `historical_kb` + `download_data.py` (FNSPID subset); `data_card.md` final; embeddings + impacto pré-calculado | 10 |
| **14–15** | Componente — Anomalias | `anomaly_detector` completo (z-score/rolling, limiares); testes | 10 |
| **16–17** | Componente — Correlação (núcleo) | `correlation_engine`: embeddings (SBERT) + cosseno + event-study (+1d/+3d); testes | 12 |
| **18** | Componentes — Explicação + (opc.) | `explanation_engine` (regras+precedentes+SHAP opc.); `impact_analyzer`/FinBERT só se defensável | 14,16 |
| **19–22** | **Avaliação (M3)** | Executar `evaluation_design.md`: anomalias (P/R), recuperação (precision@k + baselines/ablação), XAI (rubrica), estudo de caso; figuras de resultados | 18 |
| **23–24** | Escrita — Implementação | Capítulo de implementação (decisões de engenharia, integração, reprodutibilidade) | 18 |
| **25–26** | Escrita — Avaliação + Conclusão (M4) | Capítulos de resultados/avaliação e conclusão (limitações honestas, trabalho futuro) | 22 |
| **27–28** | Revisão + mock defense | Revisão global, passe de citações, **red-team/mock defense**; corrigir pontos fracos; `QUESTIONS.md` | 26 |
| **29–30** | Defesa (M5) | `presentation/outline_slides.md` + preparação da defesa | 27 |
| **31–33+** | Buffer | Contingência: derrapagens, avaliação mais profunda, figuras extra, ensino adicional | — |

## Dependências críticas / ações humanas (ver `CLAUDE.md`)
- **Python 3.12** instalado → antes da implementação (Sessão ~10).
- **Token Telegram** no `.env` → antes da thin slice (Sessão 10–11).
- **Chaves de APIs** (Finnhub, etc.) → conforme necessário (Sessões 12+).
- **Tickers + janela FNSPID** confirmados → Sessão 12 (`data_card.md`).
- **Política ISEP de uso de IA** → antes da escrita final / front matter (Fase D / Sessão 3+).

## Contingência (§5.3)
- Se o prazo apertar: cortar opcionais (`impact_analyzer`, FinBERT, ablções extra) — sistema **fino mas completo**
  vale mais que grande e inacabado. Manter sempre `main` compilável e a thin slice a passar.

## Estado das fases
- Fase 0 ✅ · Fase A ✅ · Fase B (coberta pela 0) ✅ · **Fase C ✅ (a fechar no gate)** · Fase D → Sessão 3.

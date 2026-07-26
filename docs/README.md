# docs/ — índice da documentação

Mapa de toda a documentação do InvestiGator, agrupada por finalidade. Começa por **`design/how_to_run.md`**
se só queres correr o sistema.

## design/ — para quem quer *usar* / *reconstruir* o sistema (porta de entrada)
| Ficheiro | Para quê |
|----------|----------|
| [design/how_to_run.md](design/how_to_run.md) | **Como correr** o sistema de ponta a ponta (começa no §0.0: 1 comando). |
| [design/run_in_vscode.md](design/run_in_vscode.md) | **Correr por cliques** (duplo-clique em `run/` ou botões do VS Code). |
| [design/setup.md](design/setup.md) | Ambiente: venv 3.12, stack leve vs `--ml`, torch do índice CPU. |
| [design/deployment.md](design/deployment.md) | Publicar o **dashboard** de graça (Streamlit Community Cloud). |
| [design/going_live.md](design/going_live.md) | Pôr o sistema **24/7** (canal Telegram + timer do GitHub, sem servidor). |
| [design/vm_watch.md](design/vm_watch.md) | Alertas em **quase-tempo-real**: modo vigia numa VM gratuita (Oracle Free). |
| [design/arquitectura_sistema.md](design/arquitectura_sistema.md) | Arquitetura e componentes. |
| [design/data_card.md](design/data_card.md) | Origem/estrutura dos dados (FNSPID + camada live). |
| [design/free_apis.md](design/free_apis.md) | APIs gratuitas usadas (preços, notícias, Telegram). |
| [design/evaluation_design.md](design/evaluation_design.md) | Metodologia de avaliação (precision@k, anomalia). |
| [design/usefulness_study.md](design/usefulness_study.md) | **Protocolo de estudo de utilidade (RQ3)**: rubrica + desenho executável para fechar a lacuna "útil = em aberto". |
| [design/risk_register.md](design/risk_register.md) | Riscos do projeto e mitigações. |
| [design/public_bundle.md](design/public_bundle.md) | Publicar um bundle limpo (app + tese + código), sem segredos nem dados grandes; enacted por `scripts/make_public_bundle.py`. |

## evaluation/ — resultados (gerados por script; não editar à mão)
| Ficheiro | Para quê |
|----------|----------|
| [evaluation/evaluation_results.md](evaluation/evaluation_results.md) | Recuperação: SBERT vs baselines (multi-seed). |
| [evaluation/evaluation_per_sector.md](evaluation/evaluation_per_sector.md) | Precisão por setor. |
| [evaluation/evaluation_anomaly.md](evaluation/evaluation_anomaly.md) | Anomalia: taxa de disparo + ablação (+ IF vs z-score). |
| [evaluation/evaluation_anomaly_ext.md](evaluation/evaluation_anomaly_ext.md) | CS1-ext: LOF causal + z-score com σ EWMA (aditivo; congelados intactos). |
| [evaluation/evaluation_triage.md](evaluation/evaluation_triage.md) | Triagem de materialidade (RQ4): números finais FNSPID. |
| [evaluation/evaluation_triage_ext.md](evaluation/evaluation_triage_ext.md) | RQ4-ext: ablação de 5 features de contexto (aditivo; nenhuma ajudou — reportado como caiu). |
| [evaluation/calibration_platt_vs_isotonic.md](evaluation/calibration_platt_vs_isotonic.md) | Extensão: Platt vs isotónica no mesmo protocolo (aditivo). |
| [evaluation/roadmap_rq4.md](evaluation/roadmap_rq4.md) | Roteiro RQ4 ("não estamos no fim da linha"): features estendidas + ablação (Eixo 1 ✅ corrido). |
| [evaluation/triage_worked_example.md](evaluation/triage_worked_example.md) | Exemplo trabalhado REAL da triagem (alerta META → p=0,539 reproduzido). |
| [evaluation/alert_funnel.md](evaluation/alert_funnel.md) | Funil de produção real: manchetes → alertas (22:1). |
| [evaluation/evaluation_triage_smoke.md](evaluation/evaluation_triage_smoke.md) | Triagem: smoke no corpus Finnhub (congelado; regime shift). |
| [evaluation/live_monitoring.md](evaluation/live_monitoring.md) | Loop de pós-validação: precisão/calibração ao vivo. |
| [evaluation/kb_fnspid_build.md](evaluation/kb_fnspid_build.md) | KB de retrieval multi-ano: build + validação do artefacto (P3). |
| [evaluation/onnx_minilm_validation.md](evaluation/onnx_minilm_validation.md) | Produto: paridade do MiniLM-ONNX vs SBERT (embeddings + retrieval top-k). |

## decisions/ — porquê das decisões, aprendizagem e revisões (rigor académico)
| Ficheiro | Para quê |
|----------|----------|
| [decisions/learning.md](decisions/learning.md) | Cada conceito de IA explicado em PT-PT (aprendizagem do aluno). |
| [decisions/glossary.md](decisions/glossary.md) | Glossário de termos. |
| [decisions/citation_log.md](decisions/citation_log.md) | Registo de **cada citação verificada** (zero fabricação). |
| [decisions/page_audit.md](decisions/page_audit.md) | Auditoria página-a-página + re-verificação das 50 fontes. |
| [decisions/product_review.md](decisions/product_review.md) | Revisão de produto/UX (Pass 5 + Pass 6 do redesenho). |

## Preparar a defesa — duas camadas
> **1. ESTUDAR (ensina do zero):** `slides/guia_estudo/main.pdf` (77 slides) é a fonte única de
> estudo — ensina a tese do zero E contém o guião oral, o mapa dos números congelados e o plano B.
>
> **2. ENSAIAR (recall rápido):** [defence/guiao_de_defesa.md](defence/guiao_de_defesa.md) — os
> números de cor, o veredicto+guião por RQ, e as **perguntas mais duras do júri com respostas-modelo**
> focadas nos pontos fracos (corpus fino da RQ2; "o modelo perdeu" da RQ4; utilidade da RQ3; proxy
> de setor). É o que se lê na véspera.
>
> O relatório para orientador/júri está na raiz: `RELATORIO_FINAL.md`. (Os antigos caderno de
> defesa e guia rápido foram absorvidos no guia e arquivados em `_archive/`.)

## internal/ — documentos internos de continuidade (não são "porta de entrada" para examinadores)
| Ficheiro | Para quê |
|----------|----------|
| [internal/ROOT_PROMPT_CLAUDE_CODE.md](internal/ROOT_PROMPT_CLAUDE_CODE.md) | O enunciado/root prompt original do projeto (proveniência honesta). |

> Outros ficheiros internos de continuidade vivem em `progress/` (TRACKER, SESSIONS, DECISIONS, MASTER_PLAN)
> e na raiz (`CLAUDE.md` — memória de trabalho do projeto).

## _archive/ — documentos absorvidos/superados, mantidos por proveniência
Análises de fases iniciais (`analise_referencia`, `analise_template_latex`), a proposta de ML ao
orientador (aprovada 2026-07-04), e os documentos de estudo absorvidos pelo guia único
(`caderno_de_defesa`, `guia_rapido`, `QUESTIONS`).

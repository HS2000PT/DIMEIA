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
| [design/arquitectura_sistema.md](design/arquitectura_sistema.md) | Arquitetura e componentes. |
| [design/data_card.md](design/data_card.md) | Origem/estrutura dos dados (FNSPID + camada live). |
| [design/free_apis.md](design/free_apis.md) | APIs gratuitas usadas (preços, notícias, Telegram). |
| [design/evaluation_design.md](design/evaluation_design.md) | Metodologia de avaliação (precision@k, anomalia). |
| [design/risk_register.md](design/risk_register.md) | Riscos do projeto e mitigações. |

## evaluation/ — resultados (gerados por script; não editar à mão)
| Ficheiro | Para quê |
|----------|----------|
| [evaluation/evaluation_results.md](evaluation/evaluation_results.md) | Recuperação: SBERT vs baselines (multi-seed). |
| [evaluation/evaluation_per_sector.md](evaluation/evaluation_per_sector.md) | Precisão por setor. |
| [evaluation/evaluation_anomaly.md](evaluation/evaluation_anomaly.md) | Anomalia: taxa de disparo + ablação. |

## decisions/ — porquê das decisões, aprendizagem e revisões (rigor académico)
| Ficheiro | Para quê |
|----------|----------|
| [decisions/learning.md](decisions/learning.md) | Cada conceito de IA explicado em PT-PT (aprendizagem do aluno). |
| [decisions/glossary.md](decisions/glossary.md) | Glossário de termos. |
| [decisions/citation_log.md](decisions/citation_log.md) | Registo de **cada citação verificada** (zero fabricação). |
| [decisions/page_audit.md](decisions/page_audit.md) | Auditoria página-a-página + re-verificação das 50 fontes. |
| [decisions/implementation_review.md](decisions/implementation_review.md) | Revisão crítica da implementação/estatística. |
| [decisions/review_log.md](decisions/review_log.md) | Revisão crítica do zero (achados C-1..C-5). |
| [decisions/editorial_review.md](decisions/editorial_review.md) | Registo da revisão editorial / reescrita / polimento. |
| [decisions/product_review.md](decisions/product_review.md) | Revisão de produto/UX. |

## defence/ — preparar a defesa
| Ficheiro | Para quê |
|----------|----------|
| [defence/caderno_de_defesa.md](defence/caderno_de_defesa.md) | Caderno de defesa (PT-PT): respostas, número→script→tese. |

> Para o **guia de estudo do zero** (slides), ver `slides/guia_estudo/main.pdf`.

## internal/ — documentos internos de continuidade (não são "porta de entrada" para examinadores)
| Ficheiro | Para quê |
|----------|----------|
| [internal/ROOT_PROMPT_CLAUDE_CODE.md](internal/ROOT_PROMPT_CLAUDE_CODE.md) | O enunciado/root prompt original do projeto (proveniência honesta). |

> Outros ficheiros internos de continuidade vivem em `progress/` (TRACKER, SESSIONS, DECISIONS, MASTER_PLAN)
> e na raiz (`CLAUDE.md` — memória de trabalho do projeto).

## _archive/ — análises de fases iniciais, mantidas por proveniência
| Ficheiro | Para quê |
|----------|----------|
| [_archive/analise_referencia.md](_archive/analise_referencia.md) | Análise inicial de dissertações de referência. |
| [_archive/analise_template_latex.md](_archive/analise_template_latex.md) | Análise inicial do template LaTeX ISEP. |

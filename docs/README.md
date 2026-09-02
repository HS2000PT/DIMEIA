# docs/ — índice da documentação

Mapa de toda a documentação do InvestiGator, agrupada por finalidade. Começa por **`design/how_to_run.md`**
se só queres correr o sistema.

## design/ — para quem quer *usar* / *reconstruir* o sistema (porta de entrada)
| Ficheiro | Para quê |
|----------|----------|
| [design/how_to_run.md](design/how_to_run.md) | **Como correr** o sistema de ponta a ponta (começa no §0.0: 1 comando). |
| [design/run_in_vscode.md](design/run_in_vscode.md) | **Correr por cliques** (duplo-clique em `archive/streamlit-app/run/` ou botões do VS Code). |
| [design/setup.md](design/setup.md) | Ambiente: venv 3.12, stack leve vs `--ml`, torch do índice CPU. |
| [design/deployment.md](design/deployment.md) | Publicar o **dashboard** de graça (Streamlit Community Cloud). |
| [design/going_live.md](design/going_live.md) | Pôr o sistema **24/7** (canal Telegram + timer do GitHub, sem servidor). |
| [design/vm_watch.md](design/vm_watch.md) | Alertas em **quase-tempo-real**: modo vigia numa VM gratuita (Oracle Free). |
| [design/arquitectura_sistema.md](design/arquitectura_sistema.md) | Arquitetura e componentes. |
| [design/arquitetura_dados.md](design/arquitetura_dados.md) | **"Tens uma base de dados?"** As três camadas de persistência, porque não há Postgres, a limitação real (escrita concorrente) e como está tratada. |
| [design/data_card.md](design/data_card.md) | Origem/estrutura dos dados (FNSPID + camada live). |
| [design/free_apis.md](design/free_apis.md) | APIs gratuitas usadas (preços, notícias, Telegram). |
| [design/evaluation_design.md](design/evaluation_design.md) | Metodologia de avaliação (precision@k, anomalia). |
| [design/usefulness_study.md](design/usefulness_study.md) | **Protocolo de estudo de utilidade (RQ3)**: rubrica + desenho executável para fechar a lacuna "útil = em aberto". |
| [design/risk_register.md](design/risk_register.md) | Riscos do projeto e mitigações. |
| [design/public_bundle.md](design/public_bundle.md) | Publicar um bundle limpo (app + tese + código), sem segredos nem dados grandes; enacted por `scripts/make_public_bundle.py`. |
| [design/keys.md](design/keys.md) | **Todas as chaves num só sítio**: o que faz cada uma, onde a obter, em que cofre colar, e o que falha sem ela. |
| [design/hosting.md](design/hosting.md) | **Onde correr o vigia**: ofertas verificadas a 2026-08-01 (a DigitalOcean fechou a janela), recomendação Heroku e o que ela compra em latência. |
| [design/trocar_de_maquina.md](design/trocar_de_maquina.md) | **Mudar de computador em 4 comandos**: o ambiente vem do repositório e as chaves vêm do Heroku (round-trip verificado). |
| [design/heroku_setup.md](design/heroku_setup.md) | **Pôr a correr 24/7, passo a passo**: CLI, segredos, deploy, e o passo que é fácil esquecer (escalar o worker). |
| [design/cadence_contract.md](design/cadence_contract.md) | **O que o produto promete enviar e nunca enviar**, com o custo medido de cada gate. |
| [design/app_acceptance.md](design/app_acceptance.md) | **Critérios de aceitação da app, escritos ANTES do código** (a condição de paragem que travou o ciclo de redesenhos). |
| [design/narrator_guard.md](design/narrator_guard.md) | **A guarda de fidelidade do narrador**: porquê allowlist e não blocklist, e os 29 furos que o red team abriu na v1. |
| [design/brand.md](design/brand.md) | Sistema de marca "The Tail" + o teste de aceitação que a marca anterior falhava. |

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
| [evaluation/live_monitoring.md](evaluation/live_monitoring.md) | Loop de pós-validação: precisão/calibração ao vivo. |
| [evaluation/kb_fnspid_build.md](evaluation/kb_fnspid_build.md) | KB de retrieval multi-ano: build + validação do artefacto (P3). |
| [evaluation/onnx_minilm_validation.md](evaluation/onnx_minilm_validation.md) | Produto: paridade do MiniLM-ONNX vs SBERT (embeddings + retrieval top-k). |
| [evaluation/evaluation_triage_uncertainty.md](evaluation/evaluation_triage_uncertainty.md) | **RQ4 incerteza:** bootstrap por cluster (ticker,dia) → IC 95% + Δ emparelhados (o texto piora de forma robusta). |
| [evaluation/evaluation_retrieval_fnspid.md](evaluation/evaluation_retrieval_fnspid.md) | **RQ2 à escala:** retrieval no FNSPID multi-ano (P@5 0.595 em 80k) + tema≠direção quantificado. |
| [evaluation/evaluation_retrieval_embedders.md](evaluation/evaluation_retrieval_embedders.md) | **Benchmark de embedders:** MiniLM vs FinBERT/E5/BGE (valida a escolha do embedder por medição). |
| [evaluation/evaluation_triage_fairtext.md](evaluation/evaluation_triage_fairtext.md) | **RQ4 re-teste justo:** C afinado + PCA do texto + FinBERT → o texto continua a não bater a volatilidade (negativo robusto; PCA recupera até ao contexto). |
| [evaluation/evaluation_policy_sweep.md](evaluation/evaluation_policy_sweep.md) | **RQ4 como POLÍTICA:** varrimento do limiar sob rácio de custo → o `0.5` deixa de ser constante à mão e passa a ponto de operação derivado (rácio implícito ≈0,9). |
| [evaluation/evaluation_event_taxonomy.md](evaluation/evaluation_event_taxonomy.md) | **Caso 5:** taxonomia de tipos de evento sobre os embeddings (com os dois controlos que a tornam interpretável: aleatório de tamanhos iguais, e AMI em vez de pureza). |
| [evaluation/evaluation_conformal.md](evaluation/evaluation_conformal.md) | **Caso 6:** predição conformal na triagem — a garantia, e o preço dela (decisão definida em só 39,5% das manchetes a 90% de cobertura). |
| [evaluation/evaluation_drift.md](evaluation/evaluation_drift.md) | **Caso 7:** deriva PSI+KS treino→teste e →hoje; a limitação mais repetida da tese, medida. |
| [evaluation/evaluation_convergence.md](evaluation/evaluation_convergence.md) | **Caso 8:** convergência multi-sinal (worldmonitor, creditado) + detetor de volume; a fusão ganha em 1 de 3 orçamentos e por isso não entra em produção. |
| [evaluation/evaluation_latency.md](evaluation/evaluation_latency.md) | **Latência decomposta:** publicação→detecção vs detecção→entrega. Refuta a explicação que estava registada (o ciclo de 60 s não é a restrição dominante; o nosso lado custa ~1 s). |
| [evaluation/evaluation_narrator.md](evaluation/evaluation_narrator.md) | **RQ3-ext:** fidelidade do narrador ancorado — violações pré-guarda (mede o modelo) vs entregues (mede a guarda). |

## decisions/ — porquê das decisões, aprendizagem e revisões (rigor académico)
| Ficheiro | Para quê |
|----------|----------|
| [decisions/learning.md](decisions/learning.md) | Cada conceito de IA explicado em PT-PT (aprendizagem do aluno). |
| [decisions/glossary.md](decisions/glossary.md) | Glossário de termos. |
| [decisions/citation_log.md](decisions/citation_log.md) | Registo de **cada citação verificada** (zero fabricação). |
| [decisions/citation_content_audit.md](decisions/citation_content_audit.md) | **Auditoria de CONTEÚDO das citações**: cada citação sustenta a frase a que está agarrada? (122 instâncias; 2 afirmações esticadas corrigidas). |
| [decisions/page_audit.md](decisions/page_audit.md) | Auditoria página-a-página + re-verificação das 50 fontes. |
| [decisions/product_review.md](decisions/product_review.md) | Revisão de produto/UX (Pass 5 + Pass 6 do redesenho). |

## Preparar a defesa — duas camadas
> **1. ESTUDAR (ensina do zero):** `slides/guia_estudo/main.pdf` (83 slides) é a fonte única de
> estudo — ensina a tese do zero E contém o guião oral, o mapa dos números congelados e o plano B.
>
> **2. ENSAIAR (recall rápido):** [defence/guiao_de_defesa.md](defence/guiao_de_defesa.md) — os
> números de cor, o veredicto+guião por RQ, o guião dos 15 min, as fórmulas explicadas, e as
> perguntas duras com respostas-modelo. É o que se lê na véspera.
>
> **4. AUTOTESTAR (o que fixa mesmo):** [defence/autoteste.md](defence/autoteste.md) — 31
> perguntas para responderes **em voz alta antes de ver a resposta**. Ler cria a ilusão de
> saber; dizer em voz alta é o que fixa. Com plano de 7 dias no fim.
>
> **3. SIMULAR (treino de arguição):** [defence/simulacro_defesa.md](defence/simulacro_defesa.md) —
> as **cadeias de pressão** (pergunta → resposta → o júri aperta → resposta) para as 8 perguntas mais
> perigosas. Treina em voz alta até a 3.ª pergunta sair sem hesitar.
>
> **5. GRAVAR a demo:** [defence/gravar_demo.md](defence/gravar_demo.md) — guião cronometrado de
> 3 min, o que fazer quando algo falha na sala, e o erro a não cometer.
>
> **6. MAPA DE COMPETÊNCIAS:** [defence/mapa_competencias.md](defence/mapa_competencias.md) —
> cada competência ligada a um artefacto e a um número, mais as três respostas que valem
> mais do que a tabela e os buracos ditos antes que perguntem.
>
> **7. ENVIAR ao orientador:** [defence/mensagem_orientador.md](defence/mensagem_orientador.md) —
> mensagem PT-PT pronta a copiar, com o que ele deve abrir e por que ordem.
>
> O resumo do projeto está na raiz: `archive/reports/RELATORIO_FINAL.md`. (Os antigos caderno de defesa e guia
> rápido foram absorvidos no guia de estudo.)

## study/ — materiais do estudo humano de utilidade (RQ3)
| Ficheiro | Para quê |
|----------|----------|
| [study/stimuli.md](study/stimuli.md) | Os 6 estímulos, condição A (facto nu) vs B (alerta completo). Alertas REAIS do canal. |
| [study/counterbalancing.md](study/counterbalancing.md) | Quem vê o quê e por que ordem (metade A→B, metade B→A). |
| [study/facilitator_script.md](study/facilitator_script.md) | Guião do facilitador: consentimento, as 3 perguntas, e a regra de não ajudar. |
| [study/responses_template.csv](study/responses_template.csv) | Folha de recolha. Copiar para `responses.csv` e preencher. |

> ⚠️ Gerados por `scripts/build_usefulness_pack.py`. **Excluídos do bundle público** até o estudo
> correr: o guião contém o critério de correção, e publicá-lo antes enviesaria a medição.

## Notas internas de continuidade
> Vivem em `progress/` e na raiz (`CLAUDE.md` — memória de trabalho do projeto). O plano ativo é
> `progress/PLANO_V2.md`; `MASTER_PLAN`, `PRODUCT_ROADMAP` e `PLANO_MELHORIAS` estão marcados como
> superados e ficam só como registo.

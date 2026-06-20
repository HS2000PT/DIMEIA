# analise_referencia.md — Análise da dissertação de referência

> **Fase A.** Benchmark de qualidade/dimensão (não é template a copiar).
> Ficheiro principal analisado: `dissertação_Rafael Silva.pdf` (input local, gitignored; Rafael Silva é o coorientador).
> As outras 3 dissertações de referência (Bruno Ribeiro, Helder Pereira, Joana Figueiredo) foram analisadas como
> complemento — ver a secção **"Comparativo (benchmark alargado)"** no fim deste ficheiro.

## Identificação
- **Título:** *Distributed Intelligent Management of Citizen Communities*
- **Autor:** Rafael Duarte Pereira da Silva
- **Programa:** MEIA — ISEP (mesma origem da nossa tese)
- **Produzido em:** Microsoft Word (não LaTeX); data de criação 2025-05-21. (Metadados do PDF indicam `/Author: Carlos Ramos`.)
- **Língua:** **Inglês** (com Resumo em PT e Abstract em EN) — referência útil por ser EN como a nossa tese.

## Dimensão (benchmark)
- **Total de páginas:** **109**.
- **Corpo (cap. 1–6):** pp. 17–92 (≈ 76 páginas).
- **Referências:** pp. 93–109 (≈ 17 páginas).
- **Nº de referências:** **≈ 170** (estilo autor-ano / APA-like; ~169–175 entradas).
- **Sem apêndices** (as referências terminam na última página).

## Front matter (numeração romana i–xv)
| Página | Secção |
|---|---|
| i | Capa / página de título |
| iii | Declaração de Integridade (PT) |
| v | Resumo (PT) |
| vii | Abstract (EN) |
| ix–x | Index (Índice / TOC) |
| xi | List of Figures |
| xiii | List of Tables |
| xv | List of Acronyms |

> Nota: não foram detetadas páginas de Agradecimentos/Dedicatória nem List of Source Code/Algoritmos
> (apesar de o template ISEP os suportar — ver `analise_template_latex.md`).

## Índice completo (capítulos, secções, subsecções → página)
**1 Introduction — p.17**
- 1.1 Contextualization (17) · 1.2 Problem Statement (19) · 1.3 Objectives and Research Questions (19)
- 1.4 Scientific Contributions (20) · 1.5 Document Structure (23)

**2 State of the art — p.25**
- 2.1 Intelligent Communities (25): 2.1.1 Community Management (27) · 2.1.2 Resource Sharing in Communities (28) · 2.1.3 Energy Community (30)
- 2.2 Intelligent Buildings (31): 2.2.1 IoT on Smart Buildings (32) · 2.2.2 Resource Optimization in Buildings (34)
- 2.3 User Preference Modeling (35): 2.3.1 User Interaction with Digital Systems (37) · 2.3.2 Multi-user Environments (37)
- 2.4 Artificial Intelligence (38): 2.4.1 Supervised and Unsupervised Learning (40) · 2.4.2 Reinforcement Learning (42)

**3 Methods and Materials — p.43**
- 3.1 Materials and Tools (43): 3.1.1 Software Infrastructure Enabling Technologies (43) · 3.1.2 Hardware Infrastructure Enabling Technologies (46) · 3.1.3 Frameworks and Libraries (48) · 3.1.4 Data Acquisition and Datasets (49)
- 3.2 Technological and Social Challenges (50): 3.2.1 Data Privacy and Protection (50) · 3.2.2 Ethical and Social Issues (51)

**4 Implementation – Caravels — p.53**
- 4.1 Architecture (54): 4.1.1 Containerized Infrastructure (55) · 4.1.2 Communication between Containers (56)
- 4.2 Tools and Services (57): 4.2.1 Data and Service Sharing (57) · 4.2.2 Physical Mobility (58) · 4.2.3 Service Deployment Process (59) · 4.2.4 Available Services (61)
- 4.3 User Preference Tree (63): 4.3.1 Tree Structure and Components (64) · 4.3.2 System Interaction (65) · 4.3.3 Organic Growth (66) · 4.3.4 Structures Merging (68)

**5 Case Studies — p.69**
- 5.1 Caravels Technical Testing and Validation (69) · 5.2 User Virtualization (73) · 5.3 Multi-User Environments (78)
- 5.4 Intelligent Energy Community powered by Caravels (81): 5.4.1 Peer-to-peer (83) · 5.4.2 Demand Response (84) · 5.4.3 Energy Storage Management (87)

**6 Conclusion — p.89**
- 6.1 Main Conclusions (89) · 6.2 Future work (91)

**References — p.93**

## Inventário de artefactos visuais
- **Total: 34 figuras + 6 tabelas** (sem listagens de código/algoritmos).
- **Tipos de figura:** diagramas de arquitetura (Docker/Kubernetes, nós, comunicação entre contentores), diagramas de sequência (ex.: otimização de armazenamento de energia), *print screens* de aplicações/interfaces, grafos de estrutura em árvore, e gráficos de resultados (ex.: recompensa total e decaimento de exploração por episódio; perfil de estado de carga).
- **Tipos de tabela:** sobretudo **tabelas comparativas** (ex.: comunidades inteligentes vs. *smart*; contentor vs. máquina virtual; dispositivos edge/IoT) e estruturas de dados.

**Distribuição por capítulo (mapeada por página):**
| Capítulo | Figuras | Tabelas |
|---|---|---|
| 1 Introduction | 0 | 0 |
| 2 State of the art | 2 (Fig. 1–2) | 1 (Tab. 1) |
| 3 Methods and Materials | 2 (Fig. 3–4) | 3 (Tab. 2–4) |
| 4 Implementation | 8 (Fig. 5–12) | 1 (Tab. 5) |
| 5 Case Studies | 22 (Fig. 13–34) | 1 (Tab. 6) |
| 6 Conclusion | 0 | 0 |

> Padrão claro: a maioria das figuras concentra-se na **implementação** (diagramas de arquitetura) e nos
> **casos de estudo/resultados** (gráficos e *print screens*). As tabelas comparativas surgem no estado da
> arte e nos materiais/métodos.

## Avaliação do estilo de escrita
- **Registo:** académico, claro e direto; frases de comprimento moderado; sem floreado.
- **Evidência:** afirmações suportadas por citações inline autor-ano; contextualização usa **estatísticas
  concretas e recentes** (ex.: "edifícios = 40% do consumo de energia e 36% das emissões"; metas da UE).
- **Estrutura:** introdução de cada capítulo com um parágrafo-resumo do que se segue; uso de **listas com
  marcadores** para requisitos/objetivos; figuras introduzidas e referenciadas no texto antes de aparecerem.
- **Tom:** formal mas legível; foco na clareza da mensagem.

## Implicações / benchmark para a NOSSA tese
- **Dimensão-alvo:** ~90–110 páginas no total (template ISEP: mín. 60 / máx. 120), com corpo ~75–90 pp. + referências.
- **Referências-alvo:** ordem de **~150–170** (seminal + recente, peer-reviewed primeiro — §6.2).
- **Artefactos visuais (§6.7 — prioridade máxima):** alvo **≥ ~30 figuras** e **várias tabelas**. Para nós:
  - **Tabelas comparativas** na revisão de literatura (abordagens × metodologias × métricas) — provavelmente **mais** tabelas do que a referência.
  - **Diagramas de arquitetura** (visão geral + por componente) na metodologia/implementação.
  - **Gráficos de resultados** na avaliação (métricas do detetor de anomalias, qualidade de recuperação de precedentes, event-study).
- **Mapeamento de estrutura:** a referência usa Intro / State of the art / Methods & Materials / Implementation /
  Case Studies / Conclusion. O nosso plano de 7 capítulos (intro · contextualização · literatura · metodologia ·
  implementação · avaliação · conclusão) é comparável; decidir na Fase C/D se "contextualização" fica como
  capítulo próprio (como no §9) ou integrada na introdução (como na referência). Registar em `DECISIONS.md`.
- **Front matter obrigatório** a replicar via template ISEP: Declaração de Integridade (com declaração de uso de
  IA — §6.8), Resumo (PT) + Abstract (EN), Índice, Listas de Figuras/Tabelas, Lista de Acrónimos.

---

## Comparativo (benchmark alargado) — 4 dissertações de referência
Todas em **Inglês** (Resumo PT + Abstract EN). As 3 complementares têm estrutura típica de LaTeX/ISEP
(numeração de figuras por capítulo nalguns casos); a do Rafael Silva foi feita em Word.

| Dissertação | Págs | Figuras | Tabelas | Referências | Estilo citação | Tema |
|---|---|---|---|---|---|---|
| Rafael Silva | 109 | 34 | 6 | ~170 | autor-ano | Gestão inteligente de comunidades (Caravels) |
| Bruno Ribeiro | 139 | 40 | 13 | ~210 | autor-ano | Sistemas multi-agente |
| Helder Pereira | 133 | 41 | 14 | ~200 | numérico (Vancouver) | Multi-agente / smart grids / ML |
| Joana Figueiredo | 104 | 20 | 5 | ~60 | autor-ano | Data Lakehouse / NLP / LLMs (setor da água) |

> Contagens obtidas das próprias Listas de Figuras/Tabelas e das secções de Referências (estimativas: refs
> contadas por padrões de entrada/ano/doi). Joana é claramente a mais leve; as outras três são "pesadas".

**Observações transversais:**
- **Língua:** 4/4 em Inglês → confirma EN como norma do programa.
- **Estrutura comum:** Cap. 1 *Introduction* (Contextualization · Research Questions & Objectives · Scientific
  Contributions · Document Organization/Structure) → Cap. 2 *State of the Art / Literature Review* → capítulos de
  métodos/implementação/casos de estudo/avaliação → *Conclusion*. **Valida o nosso plano de 7 capítulos.**
- **Front matter consistente:** Resumo + Abstract, Índice, List of Figures, List of Tables, Acronyms (alguns com
  Acknowledgements).
- **Estilo de citação:** 3/4 autor-ano (Harvard-like); Helder usa numérico. O default do template ISEP é
  `authoryear-comp` → escolha natural.

**Alvos de benchmark REFINADOS para a nossa tese:**
- **Páginas:** ~100–130 (alvo ~110–120; **máx. ISEP = 120**).
- **Figuras:** **~30–40** (Joana, com 20, é o piso aceitável; o padrão forte é ~34–41).
- **Tabelas:** **~8–14**, incluindo **várias tabelas comparativas** na revisão de literatura (§6.7).
- **Referências:** **~150–200** (seminal + recente, peer-reviewed primeiro — §6.2). (Joana com ~60 é exceção por tema.)
- **Estilo de citação:** **`authoryear-comp`** (alinha com 3/4 e com o template).

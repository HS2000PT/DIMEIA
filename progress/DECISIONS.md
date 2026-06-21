# DECISIONS — Registo de decisões (o quê, quando, porquê)

Cada decisão relevante fica aqui com data e justificação, para defesa e rastreabilidade.

---

## D-001 · 2026-06-20 · Variante de Inglês da tese = EN-GB
- **Decisão:** a tese é escrita em **Inglês britânico (EN-GB)**, sem mistura.
- **Porquê:** recomendado pelo ROOT PROMPT (§0) dado o contexto ISEP/UE; consistência é exigida e nunca se mistura.
- **Impacto:** ortografia/convenções EN-GB em todo o `thesis/`; configurar a língua no template em conformidade.

## D-002 · 2026-06-20 · Idioma dos docs de aprendizagem/internos = PT-PT
- **Decisão:** `docs/learning.md`, `docs/glossary.md`, notas de defesa, comentários de código/LaTeX e docs internos em **PT-PT**.
- **Porquê:** o aluno aprende e defende melhor na língua materna (§3); a compreensão vem primeiro. A tese (deliverable) é internacional; o entendimento é em PT-PT — é uma feature, não uma inconsistência.

## D-003 · 2026-06-20 · Versão de Python fixada = 3.12
- **Decisão:** fixar **Python 3.12** (`.python-version`); o venv canónico é criado com 3.12.
- **Porquê:** a máquina tem 3.14.6, demasiado recente — risco de faltarem wheels para `torch`/`transformers`/`sentence-transformers` (stack FinBERT + embeddings). 3.12 é estável e tem suporte total de wheels, garantindo reprodutibilidade entre dispositivos.
- **Ação humana associada:** instalar Python 3.12 (ver `CLAUDE.md` → Questões em Aberto).

## D-004 · 2026-06-20 · Layout LaTeX = estrutura/classe nativa do template ISEP
- **Decisão:** respeitar a estrutura e a classe nativas do template ISEP (`meia-style.cls`, biblatex `authoryear-comp` + biber, layout `chN/`, `frontmatter/`, `appendices/`, `mainbibliography.bib`). O esboço `thesis/chapters/0X_*.tex` do §9 é **ilustrativo**.
- **Porquê:** o ROOT PROMPT exige "respeitar o template sem exceção" (§20 Fase A). Reconciliação concreta na **Fase D**, mapeando o plano de 7 capítulos sobre a estrutura do template.

## D-005 · 2026-06-20 · Dependências ML faseadas
- **Decisão:** `requirements.txt` arranca mínimo (pytest, ruff, python-dotenv, pandas, numpy, requests, pyyaml); a stack pesada (`torch`, `transformers`, `sentence-transformers`, `datasets`, `huggingface-hub`, `yfinance`) é adicionada (e fixada) na fase em que é usada.
- **Porquê:** acelera a Sessão 0 e evita o problema de wheels do Python 3.14 antes do 3.12 estar instalado; mantém a verificação verde desde o início. O `import check` do `setup_env.sh` cresce com os componentes.

## D-006 · 2026-06-20 · PDFs de dissertações de referência = gitignored
- **Decisão:** os PDFs `dissertação_*.pdf` não são versionados (apenas locais, como `data/literature/`).
- **Porquê:** são obras de terceiros com direitos de autor (§5.4 "não republicar texto de terceiros") e binários grandes. São re-fornecidos por dispositivo pelo aluno.

## D-007 (PROPOSTA — decisão do aluno) · 2026-06-20 · Título da dissertação
> §4: a decisão final é do aluno. Variante EN-GB. Candidatos (T0 = sugestão do ROOT PROMPT):

- **T0 (baseline §4):** *Towards Transparent Financial Alerts: An Explainable AI System for Retail Investors Integrating Market Anomaly Detection and News Impact Correlation*
  - **Prós:** completo; cobre XAI + os dois gatilhos + público. **Contras:** longo; "Towards" pode soar preliminar.
- **T1:** *Explainable Financial Alerts for Retail Investors: Integrating Statistical Anomaly Detection and News–Market Impact Correlation*
  - **Prós:** conciso, afirmativo (sem "Towards"), mantém ambos os componentes + XAI + público. **Contras:** menos ênfase na reprodutibilidade/engenharia.
- **T2:** *An Explainable AI System for Retail Investors: Correlating Financial News with Historical Market Impact for Transparent Alerts*
  - **Prós:** destaca o **núcleo** (correlação notícia–impacto histórico) e a explicabilidade. **Contras:** a deteção de anomalias fica implícita.
- **T3:** *Transparent and Reproducible Financial Alerting: Engineering an Explainable AI Pipeline for Market Anomalies and News Impact on US Equities*
  - **Prós:** evidencia a **contribuição de engenharia** + reprodutibilidade + foco mercado US. **Contras:** o mais longo.

- **Recomendação:** **T1** (equilíbrio entre completude e concisão; afirmativo; cobre os dois gatilhos e o XAI).
  T2 se quisermos enfatizar o núcleo de correlação; T3 se quisermos enfatizar a engenharia/reprodutibilidade.
- **Estado:** **RESOLVIDO (2026-06-21)** → escolhido **T1** pelo aluno (ver D-008).

## D-008 · 2026-06-21 · Título escolhido = T1
- **Decisão:** *Explainable Financial Alerts for Retail Investors: Integrating Statistical Anomaly Detection and News–Market Impact Correlation* (EN-GB).
- **Porquê:** equilíbrio entre completude e concisão; afirmativo (sem "Towards"); cobre os dois gatilhos e o XAI.
- **Aplicação:** usar no bloco THESIS INFORMATION de `main.tex` na Fase D. A frase pode ser afinada antes da entrega.

## D-009 · 2026-06-21 · Autonomia máxima (workflow)
- **Decisão:** o agente prossegue **sem pedir confirmações de rotina** (sem AskUserQuestion para "Yes, continue"); decide sozinho com defaults sensatos e continua o plano entre fases/sessões.
- **Porquê:** o aluno pediu explicitamente para ser mais autónomo (estava a ter de aprovar opções quase a cada minuto). Alinha com a Autonomy Charter (§2) — "full control, I agree with everything".
- **Limites mantidos:** continuam a aplicar-se os limites rígidos do §2.2 (nada irreversível/destrutivo sem aviso; sem `--force`/`reset --hard`/`rm -rf`; nunca expor segredos; nunca gastar dinheiro; nunca fabricar). `.claude/settings.json` alargado (allowlist amplo + denylist dos perigosos).
- **Exceção:** ainda parar para decisões académicas genuinamente irreversíveis (ex.: mudança de título/âmbito) — mas sem o ritual de gate a cada passo.

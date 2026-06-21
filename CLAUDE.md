# CLAUDE.md — Memória Persistente do Projeto

> Ficheiro mais crítico do projeto. É o mecanismo principal de continuidade entre sessões e dispositivos.
> **REGRA ABSOLUTA: atualizar este ficheiro no fim de TODAS as sessões, sem exceção.**
> Ler na íntegra no início de cada sessão, antes de agir.

---

## Estado Atual
- **Sessão nº:** 2 (Fase C em curso; sessão de trabalho contínua desde a 0)
- **Última atualização:** 2026-06-20
- **Fase atual + último passo concluído:** **Fase C em curso.** Feito: (1) arquitetura técnica detalhada (`docs/arquitectura_sistema.md` — diagrama de componentes, 2 camadas de dados, fluxos dos 2 gatilhos, thin slice, garantias anti-lookahead/XAI); (2) **4 títulos candidatos** propostos (`DECISIONS.md` D-007, recomendado **T1**) — **a aguardar escolha do aluno**; (3) `learning.md` + `glossary.md` com os conceitos da arquitetura (z-score, embeddings, similaridade, event-study, XAI, lookahead). Fases 0 e A concluídas e publicadas.
- **PRÓXIMA AÇÃO IMEDIATA:** continuar a Fase C: **(b)** metodologias por componente com **citações verificadas** (`citation_log.md`) — tarefa académica mais sensível (FinBERT, SBERT/sentence-transformers, event study, z-score/anomalias, XAI/SHAP); **(c)** `evaluation_design.md` detalhado; **(d)** `PLANO_SESSOES.md` (~30 sessões). Já feitos nesta sessão: título (T1, D-008), arquitetura confirmada, `learning.md`/`glossary.md`, e **(a)** `free_apis.md` (verificado 2026-06-21).
- **Verificação de integridade da sessão:** confirmar que este ficheiro e `progress/SESSIONS.md` foram lidos nesta sessão.

---

## Contexto do Projeto (resumo compacto do ROOT PROMPT)
- **Aluno:** Henrique José da Silva Santos — MEIA (ISEP), 2.º ano, fase de dissertação. Nº 1180934.
- **Orientador:** Prof. Luís Gomes. **Coorientador:** Rafael Silva.
- **Perfil do aluno (§3):** não é especialista em IA, tem lacunas de base; objetivo central = **terminar uma dissertação sólida e defendê-la com calma** (pessoa nervosa). **Regra de ouro: ensinar à medida que se avança** (explicar cada conceito em PT-PT em `docs/learning.md` + `docs/glossary.md`, com nota de "como explico ao júri em 3 frases" por componente). **Simplicidade defensável > sofisticação.**
- **Contribuição (enquadramento permanente):** tese de **Engenharia de IA**. A contribuição NÃO é inventar algoritmos — é **integrar, aplicar e avaliar criticamente** componentes existentes num sistema funcional, explicável e reproduzível, com uma metodologia documentada de correlação notícia–impacto. Usar modelos/ferramentas existentes **é** o trabalho de engenharia.
- **Tema:** sistema inteligente de alertas financeiros para investidores de retalho, **XAI-first** (toda a lógica transparente e rastreável). Dois gatilhos: (1) movimento abrupto de mercado (NYSE/NASDAQ) → anomalia estatística → alerta + explicação; (2) nova notícia financeira → alerta + impacto potencial + precedentes históricos. **Núcleo:** motor de correlação notícia–mercado baseado em histórico (FNSPID). **Saída:** alertas via Telegram com evento + explicação + fontes + precedentes.
- **Restrições não negociáveis (§5.2):** apenas APIs gratuitas; foco mercado US (NYSE/NASDAQ); XAI-first; útil a um investidor real; rigor académico. ❌ Sem previsão de preços, sem trading algorítmico, sem APIs pagas, sem conteúdo de enchimento.
- **Disciplina de âmbito (§5.3):** primeiro uma **fatia fina end-to-end**; cada componente começa na versão mais simples e defensável; perguntar antes de adicionar complexidade; cortar opcionais se o prazo apertar.
- **Arquitetura de dados (§5.4):** camada **HISTÓRICA** = FNSPID (`Zihan1004/FNSPID`, CC BY-SA 4.0 — atribuição obrigatória); camada **LIVE** = yfinance + (a confirmar) Finnhub/Alpha Vantage/GNews/RSS.
- **Horizonte:** ~30 sessões (guia flexível, orientado pela qualidade). **Continuidade entre sessões é o requisito nº 1.**

---

## Decisões Confirmadas
- **Variante de Inglês (tese):** **EN-GB** (bloqueada; nunca misturar). [Sessão 0]
- **Idioma docs de aprendizagem/internos:** **PT-PT** (o único toggle do §0). Tese em Inglês. [Sessão 0]
- **Versão de Python fixada:** **3.12** (estabilidade para torch/transformers/sentence-transformers; 3.14 corre risco de faltar wheels). [Sessão 0]
- **Título escolhido:** **T1** — *Explainable Financial Alerts for Retail Investors: Integrating Statistical Anomaly Detection and News–Market Impact Correlation* (EN-GB). [Sessão 2 / D-008]
- **APIs aprovadas:** proposta (Fase C, `docs/free_apis.md`, verificado 2026-06-21) — preços: yfinance (base) + Finnhub (fallback, 60/min); notícias: Finnhub news + RSS (+ GNews/Marketaux opcional); histórico: FNSPID; alertas: Telegram Bot API. Alpha Vantage só ocasional (25/dia).
- **Metodologias de IA por componente:** [APÓS FASE C]
- **Estrutura de capítulos:** [APÓS FASE A]
- **Layout LaTeX:** usar a estrutura/classe nativa do template ISEP (`meia-style.cls`, `authoryear-comp`, `chN/`); o esboço `thesis/chapters/0X_*.tex` do §9 é ilustrativo e será reconciliado na Fase D. [Sessão 0]
- (Racional completo em `progress/DECISIONS.md`.)

---

## Estado LaTeX
- **Escrito:** nada ainda (Fase D cria `thesis/` a partir do template ISEP). Template **analisado** (`docs/analise_template_latex.md`).
- **Em falta:** integração do template em `thesis/`; 7 capítulos; `references.bib`.
- **Achado a tratar na Fase D:** o `Makefile` do template invoca `latexmk -r latexmk.rc` mas o `latexmk.rc` **não existe** — criar mínimo ou ajustar invocação (o CI `xu-cheng/latex-action` não depende dele).
- **Problemas de compilação:** n/a. (LaTeX local disponível: MiKTeX + biber 2.21; CI compila em cada push após Fase D.)

## Estado do Código
- **Implementado:** esqueleto de pacotes `src/` (stubs com docstrings PT-PT); `src/main.py` stub.
- **Em falta:** toda a lógica dos componentes; thin slice.
- **Smoke test da thin slice:** ainda não existe (placeholder `tests/test_smoke.py` a passar).

## Referências Verificadas
- Nenhuma ainda. Protocolo de integridade de citações (§6.4) em vigor: nenhuma entrada no `.bib` sem DOI/id verificado e registado em `docs/citation_log.md`.

---

## Questões em Aberto / À Espera do Aluno (humano-only)
1. **Instalar Python 3.12** — para `scripts/setup_env.sh` criar o venv canónico (até lá, verify corre no Python disponível).
2. **Auth GitHub** — o primeiro `git push` abre login do Git Credential Manager no browser; aprovar (não é preciso `gh`).
3. **Bot Telegram** (@BotFather → token + chat id) → apenas no `.env` local. Necessário antes da thin slice (~Sessão 10).
4. **Chaves de APIs gratuitas** (Finnhub / Alpha Vantage / GNews) → apenas no `.env`, conforme necessário (Fase C).
5. **Política ISEP de uso de IA** — texto exato da declaração de uso de IA na MEIA (confirmar com Prof. Luís Gomes se houver dúvida) — para conformidade com §6.8.
6. **Confirmar conjunto de tickers e janela temporal** do FNSPID (Fase C / data_card).
7. ~~Escolher o título~~ ✅ RESOLVIDO (T1 — D-008). Arquitetura técnica confirmada pelo aluno.

---

## Regras Permanentes (cópia compacta)
**Limites rígidos (§2.2):** nunca expor segredos (só em `.env` gitignored; scan antes de cada commit); nunca fabricar (dados, resultados, **citações** — toda a citação verificada §6.4); nunca operações git destrutivas/irreversíveis sem aviso (sem `--force`, sem reescrita de história publicada, sem `reset --hard` que perca trabalho); nada destrutivo fora do repo; nunca gastar dinheiro (só free tier); nunca automatizar logins em portais de editoras; **pausar em cada gate de fase**.

**Aluno & aprendizagem (§3):** explicar cada conceito em PT-PT antes de usar; o aluno tem de conseguir defender tudo; simplicidade defensável > sofisticação; nada que o aluno não entenda entra na tese.

**Académico (§6):** contextualização com dados 2025–2026; literatura seminal + recente, peer-reviewed primeiro; tabelas comparativas; cada afirmação com fonte, cada decisão técnica com justificação; **cada citação verificada (citation_log.md) — zero fabricação**; uso de IA declarado; datasets/modelos atribuídos.

**DoD (§8) — gate para avançar de fase:** deliverables existem e commitados; `verify.sh` passa (testes + LaTeX compila); cada conceito novo explicado em `learning.md` com nota de defesa; cada citação nova verificada e registada; nenhum segredo em ficheiros versionados; `CLAUDE.md` atualizado com estado e próxima ação.

**Git & continuidade (§12):** branch único `main`, história linear (rebase); começar sessão com pull-rebase; terminar com verify→commit→pull-rebase→push (sem force-push, sem auto-resolver conflitos que possam perder trabalho); dados grandes/modelos nunca versionados; commits descritivos em PT-PT.

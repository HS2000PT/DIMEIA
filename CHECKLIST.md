# CHECKLIST — o que FALTA (só isso)

> Lista viva, mínima de propósito: **apenas o que ainda não está feito.** O histórico completo
> do que já foi construído vive em `progress/SESSIONS.md` (por sessão) e `progress/TRACKER.md`
> (por fase); o estado técnico detalhado em `CLAUDE.md`; o resumo para o júri em
> `RELATORIO_FINAL.md`. Última limpeza: 2026-07-11.

## 🧑 Cliques só teus (ninguém pode fazer por ti)

### Produto ao vivo
- [ ] **Chaves de preços (2026-07-13, corrige os 0 alertas de mercado):** criar contas grátis
      em <https://www.tiingo.com> e <https://polygon.io>, e adicionar 3 segredos no GitHub
      (Settings → Secrets and variables → Actions): `TIINGO_API_KEY`, `POLYGON_API_KEY` e
      `ALPHAVANTAGE_API_KEY` (esta já a tens no .env do outro PC). Porquê: o yfinance está
      bloqueado nos runners do GitHub — foi por isso que NUNCA houve alertas de mercado nem
      resumo diário; a cadeia de fallback nova usa estas fontes. (O Stooq, sem chave, ganhou
      anti-bot e já não serve — testado ao vivo.) Depois: 1 clique em "Run workflow" no
      workflow Alerts num dia útil e confirmar no log `[precos …] servido por …`.
- [ ] **Streamlit: apagar e recriar a app com Python 3.12** (Advanced settings ao criar —
      NÃO é o defeito). Causa confirmada (2026-07-11): em Python 3.14 os pins pandas/numpy
      não têm wheels, a instalação falha em silêncio (~45 min) e a app arranca sem plotly
      no ambiente base da plataforma. Detalhe: `docs/design/deployment.md` (aviso no topo).
- [ ] **Streamlit: Sharing → público** — logo a seguir a recriar; verificar em janela anónima.
- [ ] **VM Oracle Free (para alertas em minutos)** — criar conta + VM e correr
      `bash deploy/setup_vm.sh` (guia passo-a-passo: `docs/design/vm_watch.md`). Até lá, o cron
      do GitHub cobre com latência ~1-2 h. *Testável já no teu PC:*
      `python scripts/run_alerts.py --watch`.
- [ ] **Afixar a mensagem de onboarding no canal** + descrição (textos prontos:
      `docs/design/going_live.md` §1b).

### Académico (bloqueia a submissão)
- [ ] **Leitura final da tese** (`thesis/main.pdf`, 78 pp) — o texto é teu para defender.
- [ ] **Licença do código** com o Prof. Luís Gomes (MIT/Apache; política de IP do ISEP) +
      ficheiro `LICENSE`.
- [ ] **Redação exata da declaração de uso de IA** (MEIA/ISEP) + **data de entrega** — confirmar
      com o Prof. Luís Gomes.
- [ ] Correr `python scripts/post_validate.py` (rotula as decisões reais maturadas do loop de
      pós-validação — repetir de vez em quando enquanto o canal está vivo).

### Opcional
- [ ] Migrar/renomear o repositório (procedimento + trade-offs: `docs/design/migrar_repo.md`;
      a alternativa sem risco é o rename `DIMEIA`→`InvestiGator`).

## 🤖 Pendentes do código (nenhum bloqueia)
- [ ] Confirmar no próximo dia útil (após as chaves de preços): alertas de MERCADO a aparecer
      (intradiário via Finnhub corre agora também no Actions; severidade notable/strong/extreme;
      linha "Sector check"), resumo diário ao fecho, investigação cruzada ("Possible
      explanation"), e a branch `alerts-history` a crescer sem duplicados.
- [ ] ~17/07: confirmar os primeiros casos MATURADOS na KB viva (`live_kb.jsonl` na branch
      alerts-history) e precedentes de 2026 a aparecer nos alertas com "(Xd ago)".
- [ ] ~Agosto: quando a KB viva tiver semanas de casos, definir `news.max_precedent_age_days`
      (proposta: 730) no alerts.yaml — o corte duro de idade dos precedentes.
- [ ] No PC com o dataset FNSPID (691 MB): corrida empírica Platt vs isotonic (a tese justifica
      conceptualmente; a comparação numérica fica como extensão) e, opcional, re-curadoria da
      KB light com peso maior em 2022-23.
- [ ] Polimento futuro (quando quiseres): cobertura `pytest --cov` no README; camada `logging`;
      CLI do Gatilho 2; de-dup de precedentes quase iguais.

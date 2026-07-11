# CHECKLIST — o que FALTA (só isso)

> Lista viva, mínima de propósito: **apenas o que ainda não está feito.** O histórico completo
> do que já foi construído vive em `progress/SESSIONS.md` (por sessão) e `progress/TRACKER.md`
> (por fase); o estado técnico detalhado em `CLAUDE.md`; o resumo para o júri em
> `RELATORIO_FINAL.md`. Última limpeza: 2026-07-11.

## 🧑 Cliques só teus (ninguém pode fazer por ti)

### Produto ao vivo
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
- [ ] Confirmar no próximo dia útil: filtros de qualidade ao vivo (menos alertas, só relevantes),
      resumo diário ao fecho no canal, e a branch `alerts-history` a crescer sem duplicados.
- [ ] Polimento futuro (quando quiseres): cobertura `pytest --cov` no README; camada `logging`;
      CLI do Gatilho 2; de-dup de precedentes quase iguais.
